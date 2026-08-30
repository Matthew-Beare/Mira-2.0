from __future__ import annotations

import hashlib
import unittest

from mira.assets import AssetService
from mira.identifiers import (
    IdentifierConflictError,
    IdentifierService,
    IdentifierValidationError,
)
from mira.receipts import ReceiptService
from mira.structured_state import InMemoryStructuredStateAdapter


UUID_ONE = "11111111-1111-4111-8111-111111111111"
UUID_TWO = "22222222-2222-4222-8222-222222222222"


def fp(label: str) -> str:
    return hashlib.sha256(label.encode("utf-8")).hexdigest()


class IdentifierServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.adapter = InMemoryStructuredStateAdapter(
            schema_version="mira-test-v1",
            resource_types=["receipt", "asset", "identifier"],
            event_types=["created", "updated"],
        )
        self.receipts = ReceiptService(self.adapter)
        self.assets = AssetService(self.adapter, receipt_service=self.receipts)
        self.identifiers = IdentifierService(self.adapter, asset_service=self.assets)
        receipt = self.receipts.capture(
            merchant="Synthetic Identifier Supply",
            purchase_date="2026-08-30",
            currency="USD",
            total_minor=5000,
            order_number="IDENT-ORDER-1",
            lines=[
                {
                    "description": "Synthetic device",
                    "quantity": "2",
                    "unit_price_minor": 2500,
                    "line_total_minor": 5000,
                }
            ],
            state="captured",
            source_type="text",
            source_fingerprint=fp("identifier-receipt"),
            observed_at="2026-08-30T00:00:00-04:00",
            idempotency_key="identifier-receipt",
        ).receipt
        line_id = receipt.lines[0].line_id
        self.assets.acquire(
            receipt_id=receipt.receipt_id,
            receipt_line_id=line_id,
            acquisition_key="unit-1",
            display_name="Synthetic device one",
            tracking_mode="individual",
            quantity=1,
            entity_uuid=UUID_ONE,
            idempotency_key="asset-one",
        )
        self.assets.acquire(
            receipt_id=receipt.receipt_id,
            receipt_line_id=line_id,
            acquisition_key="unit-2",
            display_name="Synthetic device two",
            tracking_mode="individual",
            quantity=1,
            entity_uuid=UUID_TWO,
            idempotency_key="asset-two",
        )

    def test_valid_gtin_variants_preserve_digits_and_leading_zeroes(self) -> None:
        cases = (
            ("gtin8", "96385074"),
            ("upc_a", "036000291452"),
            ("ean13", "4006381333931"),
            ("gtin14", "00012345600012"),
        )
        for index, (kind, value) in enumerate(cases):
            with self.subTest(kind=kind):
                result = self.identifiers.attach(
                    entity_uuid=UUID_ONE,
                    identifier_type=kind,
                    value=value,
                    idempotency_key=f"gtin-{index}",
                )
                item = result.identifier
                self.assertEqual(item.source_value, value)
                self.assertEqual(item.normalized_value, value)
                self.assertIsNone(item.namespace)
                self.assertIsNone(item.namespace_key)
        upc = self.identifiers.query(identifier_type="upc_a", value="036000291452")
        self.assertEqual(len(upc), 1)
        self.assertTrue(upc[0].normalized_value.startswith("0"))

    def test_invalid_gtin_check_digit_fails_closed(self) -> None:
        for kind, value in (
            ("gtin8", "96385075"),
            ("upc_a", "036000291453"),
            ("ean13", "4006381333932"),
            ("gtin14", "00012345600013"),
        ):
            with self.subTest(kind=kind):
                with self.assertRaisesRegex(IdentifierValidationError, "check digit"):
                    self.identifiers.attach(
                        entity_uuid=UUID_ONE,
                        identifier_type=kind,
                        value=value,
                        idempotency_key=f"bad-{kind}",
                    )

    def test_imei_and_mac_validation_and_normalization(self) -> None:
        imei = self.identifiers.attach(
            entity_uuid=UUID_ONE,
            identifier_type="imei",
            value="490154203237518",
            idempotency_key="imei-good",
        ).identifier
        self.assertEqual(imei.normalized_value, "490154203237518")
        with self.assertRaisesRegex(IdentifierValidationError, "Luhn"):
            self.identifiers.attach(
                entity_uuid=UUID_ONE,
                identifier_type="imei",
                value="490154203237519",
                idempotency_key="imei-bad",
            )

        mac = self.identifiers.attach(
            entity_uuid=UUID_ONE,
            identifier_type="mac",
            value="aa:bb:cc:dd:ee:ff",
            idempotency_key="mac-good",
        ).identifier
        self.assertEqual(mac.source_value, "aa:bb:cc:dd:ee:ff")
        self.assertEqual(mac.normalized_value, "AABBCCDDEEFF")
        with self.assertRaisesRegex(IdentifierValidationError, "MAC"):
            self.identifiers.attach(
                entity_uuid=UUID_ONE,
                identifier_type="mac",
                value="aa:bb:cc:dd:ee:gg",
                idempotency_key="mac-bad",
            )

    def test_namespaced_local_identifiers_require_explicit_namespace(self) -> None:
        for kind in (
            "merchant_sku",
            "manufacturer_part_number",
            "model_number",
            "serial_number",
        ):
            with self.subTest(kind=kind):
                with self.assertRaisesRegex(IdentifierValidationError, "namespace"):
                    self.identifiers.attach(
                        entity_uuid=UUID_ONE,
                        identifier_type=kind,
                        value="ABC-123",
                        idempotency_key=f"missing-ns-{kind}",
                    )

        item = self.identifiers.attach(
            entity_uuid=UUID_ONE,
            identifier_type="manufacturer_part_number",
            namespace="Synthetic Tool Co",
            value="AbC-123",
            idempotency_key="mpn-good",
        ).identifier
        self.assertEqual(item.namespace, "Synthetic Tool Co")
        self.assertEqual(item.namespace_key, "synthetic tool co")
        self.assertEqual(item.source_value, "AbC-123")
        self.assertEqual(item.normalized_value, "abc-123")

    def test_global_identifier_rejects_invented_local_namespace(self) -> None:
        with self.assertRaisesRegex(IdentifierValidationError, "global identifier"):
            self.identifiers.attach(
                entity_uuid=UUID_ONE,
                identifier_type="upc_a",
                value="036000291452",
                namespace="Some Merchant",
                idempotency_key="bad-global-namespace",
            )

    def test_same_asset_replay_is_zero_write_and_verification_upgrade_is_one_revision(self) -> None:
        first = self.identifiers.attach(
            entity_uuid=UUID_ONE,
            identifier_type="serial_number",
            namespace="Synthetic Tool Co",
            value="SN-001",
            verification_state="observed",
            idempotency_key="serial-observed",
        )
        replay = self.identifiers.attach(
            entity_uuid=UUID_ONE,
            identifier_type="serial_number",
            namespace="Synthetic Tool Co",
            value="SN-001",
            verification_state="observed",
            idempotency_key="serial-observed-replay",
        )
        self.assertEqual(first.identifier.identifier_id, replay.identifier.identifier_id)
        self.assertEqual(replay.outcome, "replay")
        self.assertEqual(replay.identifier.revision, 1)
        self.assertTrue(replay.identifier.idempotent_replay)

        verified = self.identifiers.attach(
            entity_uuid=UUID_ONE,
            identifier_type="serial_number",
            namespace="Synthetic Tool Co",
            value="SN-001",
            verification_state="verified",
            idempotency_key="serial-verified",
        )
        self.assertEqual(verified.outcome, "verified")
        self.assertEqual(verified.identifier.identifier_id, first.identifier.identifier_id)
        self.assertEqual(verified.identifier.revision, 2)
        self.assertEqual(verified.identifier.verification_state, "verified")

        later_observed = self.identifiers.attach(
            entity_uuid=UUID_ONE,
            identifier_type="serial_number",
            namespace="Synthetic Tool Co",
            value="SN-001",
            verification_state="observed",
            idempotency_key="serial-downgrade-attempt",
        )
        self.assertEqual(later_observed.outcome, "replay")
        self.assertEqual(later_observed.identifier.revision, 2)
        self.assertEqual(later_observed.identifier.verification_state, "verified")

    def test_source_format_variant_does_not_silently_rewrite_exact_value(self) -> None:
        self.identifiers.attach(
            entity_uuid=UUID_ONE,
            identifier_type="mac",
            value="aa:bb:cc:dd:ee:ff",
            idempotency_key="mac-source-first",
        )
        with self.assertRaisesRegex(IdentifierConflictError, "exact source value"):
            self.identifiers.attach(
                entity_uuid=UUID_ONE,
                identifier_type="mac",
                value="AA-BB-CC-DD-EE-FF",
                idempotency_key="mac-source-variant",
            )
        current = self.identifiers.query(
            identifier_type="mac", value="AA.BB.CC.DD.EE.FF".replace(".", "")
        )
        self.assertEqual(len(current), 1)
        self.assertEqual(current[0].source_value, "aa:bb:cc:dd:ee:ff")

    def test_product_identifier_can_link_to_multiple_assets_and_lookup_both(self) -> None:
        for entity_uuid, key in ((UUID_ONE, "upc-one"), (UUID_TWO, "upc-two")):
            self.identifiers.attach(
                entity_uuid=entity_uuid,
                identifier_type="upc_a",
                value="036000291452",
                idempotency_key=key,
            )
        rows = self.identifiers.query(identifier_type="upc_a", value="036000291452")
        self.assertEqual([item.entity_uuid for item in rows], [UUID_ONE, UUID_TWO])
        assets = self.identifiers.lookup_assets(
            identifier_type="upc_a", value="036000291452"
        )
        self.assertEqual([asset.entity_uuid for asset in assets], [UUID_ONE, UUID_TWO])

    def test_serial_level_identifier_cannot_link_to_two_assets(self) -> None:
        self.identifiers.attach(
            entity_uuid=UUID_ONE,
            identifier_type="serial_number",
            namespace="Synthetic Tool Co",
            value="SN-UNIQUE-1",
            idempotency_key="serial-one",
        )
        with self.assertRaisesRegex(IdentifierConflictError, "another Entity UUID"):
            self.identifiers.attach(
                entity_uuid=UUID_TWO,
                identifier_type="serial_number",
                namespace=" synthetic   tool co ",
                value="sn-unique-1",
                idempotency_key="serial-two",
            )

        self.identifiers.attach(
            entity_uuid=UUID_ONE,
            identifier_type="mac",
            value="00:11:22:33:44:55",
            idempotency_key="mac-one",
        )
        with self.assertRaises(IdentifierConflictError):
            self.identifiers.attach(
                entity_uuid=UUID_TWO,
                identifier_type="mac",
                value="0011.2233.4455",
                idempotency_key="mac-two",
            )

    def test_missing_asset_fails_closed_and_identifier_does_not_create_asset(self) -> None:
        missing = "33333333-3333-4333-8333-333333333333"
        with self.assertRaisesRegex(IdentifierValidationError, "does not exist"):
            self.identifiers.attach(
                entity_uuid=missing,
                identifier_type="upc_a",
                value="036000291452",
                idempotency_key="missing-asset",
            )
        self.assertEqual(len(self.assets.query()), 2)
        self.assertEqual(len(self.identifiers.query()), 0)

    def test_query_requires_type_for_value_or_namespace(self) -> None:
        with self.assertRaisesRegex(IdentifierValidationError, "identifier_type"):
            self.identifiers.query(value="036000291452")
        with self.assertRaisesRegex(IdentifierValidationError, "identifier_type"):
            self.identifiers.query(namespace="Synthetic Tool Co")

    def test_identifier_payload_and_asset_payload_preserve_side_effect_boundary(self) -> None:
        item = self.identifiers.attach(
            entity_uuid=UUID_ONE,
            identifier_type="model_number",
            namespace="Synthetic Tool Co",
            value="MODEL-42",
            idempotency_key="model-side-effect",
        ).identifier
        identifier_payload = self.adapter.get("identifier", item.identifier_id).payload
        asset_payload = self.adapter.get("asset", UUID_ONE).payload
        self.assertNotIn("identifiers", asset_payload)
        for forbidden in (
            "fitment",
            "assigned_to",
            "installed_on",
            "location",
            "movement",
            "inventory_location",
            "warranty",
            "maintenance",
            "ocr",
        ):
            self.assertNotIn(forbidden, identifier_payload)
            self.assertNotIn(forbidden, asset_payload)


if __name__ == "__main__":
    unittest.main()
