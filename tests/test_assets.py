from __future__ import annotations

import hashlib
import unittest
from uuid import UUID

from mira.assets import (
    AssetConflictError,
    AssetIntegrityError,
    AssetService,
    AssetValidationError,
)
from mira.receipts import ReceiptService
from mira.structured_state import InMemoryStructuredStateAdapter


UUID_ONE = "11111111-1111-4111-8111-111111111111"
UUID_TWO = "22222222-2222-4222-8222-222222222222"
UUID_THREE = "33333333-3333-4333-8333-333333333333"


def fp(label: str) -> str:
    return hashlib.sha256(label.encode("utf-8")).hexdigest()


class AssetServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.adapter = InMemoryStructuredStateAdapter(
            schema_version="mira-test-v1",
            resource_types=["receipt", "asset"],
            event_types=["created"],
        )
        self.receipts = ReceiptService(self.adapter)
        self.assets = AssetService(self.adapter, receipt_service=self.receipts)

    def receipt(self, label: str = "purchase", *, quantity: str = "1", state: str = "captured"):
        return self.receipts.capture(
            merchant="Synthetic Tool Supply",
            purchase_date="2026-08-29",
            currency="USD",
            total_minor=5000,
            order_number=f"ORDER-{label}",
            lines=[
                {
                    "description": "Synthetic wrench",
                    "quantity": quantity,
                    "unit_price_minor": 5000,
                    "line_total_minor": 5000,
                }
            ],
            state=state,
            source_type="email",
            source_fingerprint=fp(label),
            observed_at="2026-08-29T12:00:00-04:00",
            idempotency_key=f"receipt-{label}",
        ).receipt

    def test_acquire_individual_uses_immutable_rfc4122_uuid_and_receipt_line(self) -> None:
        receipt = self.receipt()
        line_id = receipt.lines[0].line_id
        result = self.assets.acquire(
            receipt_id=receipt.receipt_id,
            receipt_line_id=line_id,
            acquisition_key="unit-1",
            display_name="Synthetic wrench",
            tracking_mode="individual",
            quantity=1,
            entity_uuid=UUID_ONE,
            idempotency_key="asset-unit-1",
        )
        asset = result.asset
        self.assertEqual(result.outcome, "created")
        self.assertEqual(asset.entity_uuid, UUID_ONE)
        self.assertEqual(UUID(asset.entity_uuid).version, 4)
        self.assertEqual(asset.revision, 1)
        self.assertEqual(asset.tracking_mode, "individual")
        self.assertEqual(asset.quantity, 1)
        self.assertEqual(asset.acquisition.receipt_id, receipt.receipt_id)
        self.assertEqual(asset.acquisition.receipt_line_id, line_id)
        self.assertEqual(asset.acquisition.receipt_revision, receipt.revision)
        self.assertTrue(asset.acquisition.source_identity.startswith("receipt-acquisition:"))
        self.assertEqual(self.assets.get(UUID_ONE), asset)

    def test_auto_allocated_uuid_is_rfc4122_and_replay_preserves_it(self) -> None:
        receipt = self.receipt("auto")
        first = self.assets.acquire(
            receipt_id=receipt.receipt_id,
            receipt_line_id=receipt.lines[0].line_id,
            acquisition_key="unit-1",
            display_name="Auto UUID wrench",
            tracking_mode="individual",
            quantity=1,
            idempotency_key="auto-first",
        )
        parsed = UUID(first.asset.entity_uuid)
        self.assertEqual(parsed.variant, UUID(UUID_ONE).variant)

        replay = self.assets.acquire(
            receipt_id=receipt.receipt_id,
            receipt_line_id=receipt.lines[0].line_id,
            acquisition_key="unit-1",
            display_name="Auto UUID wrench",
            tracking_mode="individual",
            quantity=1,
            idempotency_key="auto-second-logical-key",
        )
        self.assertEqual(replay.outcome, "replay")
        self.assertEqual(replay.asset.entity_uuid, first.asset.entity_uuid)
        self.assertEqual(replay.asset.revision, 1)
        self.assertTrue(replay.asset.idempotent_replay)
        self.assertEqual(len(self.assets.query()), 1)

    def test_same_source_can_enrich_attributes_without_replacing_uuid(self) -> None:
        receipt = self.receipt("enrich")
        line_id = receipt.lines[0].line_id
        first = self.assets.acquire(
            receipt_id=receipt.receipt_id,
            receipt_line_id=line_id,
            acquisition_key="unit-1",
            display_name="Wrench",
            tracking_mode="individual",
            quantity=1,
            entity_uuid=UUID_ONE,
            idempotency_key="enrich-create",
        )
        enriched = self.assets.acquire(
            receipt_id=receipt.receipt_id,
            receipt_line_id=line_id,
            acquisition_key="unit-1",
            display_name="Synthetic 10 mm wrench",
            tracking_mode="individual",
            quantity=1,
            note="Bench tool",
            idempotency_key="enrich-recapture",
        )
        self.assertEqual(enriched.outcome, "enriched")
        self.assertEqual(enriched.asset.entity_uuid, first.asset.entity_uuid)
        self.assertEqual(enriched.asset.revision, 2)
        self.assertEqual(enriched.asset.display_name, "Synthetic 10 mm wrench")
        self.assertEqual(enriched.asset.note, "Bench tool")
        self.assertEqual(enriched.asset.acquisition.source_identity, first.asset.acquisition.source_identity)

    def test_replayed_source_cannot_replace_uuid_or_quantity_mode(self) -> None:
        receipt = self.receipt("conflict", quantity="2")
        line_id = receipt.lines[0].line_id
        self.assets.acquire(
            receipt_id=receipt.receipt_id,
            receipt_line_id=line_id,
            acquisition_key="unit-1",
            display_name="Wrench one",
            tracking_mode="individual",
            quantity=1,
            entity_uuid=UUID_ONE,
            idempotency_key="conflict-create",
        )
        with self.assertRaises(AssetConflictError):
            self.assets.acquire(
                receipt_id=receipt.receipt_id,
                receipt_line_id=line_id,
                acquisition_key="unit-1",
                display_name="Wrench one",
                tracking_mode="individual",
                quantity=1,
                entity_uuid=UUID_TWO,
                idempotency_key="replace-uuid",
            )
        with self.assertRaises(AssetConflictError):
            self.assets.acquire(
                receipt_id=receipt.receipt_id,
                receipt_line_id=line_id,
                acquisition_key="unit-1",
                display_name="Wrench lot",
                tracking_mode="lot",
                quantity=2,
                idempotency_key="replace-mode",
            )
        self.assertEqual(self.assets.get(UUID_ONE).revision, 1)

    def test_individual_quantity_must_be_one_and_lot_can_group_units(self) -> None:
        receipt = self.receipt("quantity", quantity="4")
        line_id = receipt.lines[0].line_id
        with self.assertRaises(AssetValidationError):
            self.assets.acquire(
                receipt_id=receipt.receipt_id,
                receipt_line_id=line_id,
                acquisition_key="bad-individual",
                display_name="Four wrenches",
                tracking_mode="individual",
                quantity=4,
                idempotency_key="bad-individual",
            )
        lot = self.assets.acquire(
            receipt_id=receipt.receipt_id,
            receipt_line_id=line_id,
            acquisition_key="lot-1",
            display_name="Wrench lot",
            tracking_mode="lot",
            quantity=4,
            entity_uuid=UUID_ONE,
            idempotency_key="lot-create",
        )
        self.assertEqual(lot.asset.tracking_mode, "lot")
        self.assertEqual(lot.asset.quantity, 4)

    def test_line_capacity_prevents_more_assets_than_purchased(self) -> None:
        receipt = self.receipt("capacity", quantity="2")
        line_id = receipt.lines[0].line_id
        for acquisition_key, entity_uuid in (("unit-1", UUID_ONE), ("unit-2", UUID_TWO)):
            self.assets.acquire(
                receipt_id=receipt.receipt_id,
                receipt_line_id=line_id,
                acquisition_key=acquisition_key,
                display_name=acquisition_key,
                tracking_mode="individual",
                quantity=1,
                entity_uuid=entity_uuid,
                idempotency_key=f"create-{acquisition_key}",
            )
        with self.assertRaises(AssetConflictError):
            self.assets.acquire(
                receipt_id=receipt.receipt_id,
                receipt_line_id=line_id,
                acquisition_key="unit-3",
                display_name="Impossible third wrench",
                tracking_mode="individual",
                quantity=1,
                entity_uuid=UUID_THREE,
                idempotency_key="create-unit-3",
            )
        self.assertEqual(len(self.assets.query(receipt_line_id=line_id)), 2)

    def test_missing_or_unreviewed_receipt_and_missing_line_fail_closed(self) -> None:
        with self.assertRaises(AssetValidationError):
            self.assets.acquire(
                receipt_id="receipt-does-not-exist",
                acquisition_key="unit-1",
                display_name="No source",
                tracking_mode="individual",
                quantity=1,
                idempotency_key="missing-receipt",
            )

        review = self.receipt("review", state="needs_review")
        with self.assertRaisesRegex(AssetValidationError, "captured receipt"):
            self.assets.acquire(
                receipt_id=review.receipt_id,
                acquisition_key="unit-1",
                display_name="Unverified wrench",
                tracking_mode="individual",
                quantity=1,
                idempotency_key="review-receipt",
            )

        receipt = self.receipt("missing-line")
        with self.assertRaisesRegex(AssetValidationError, "exactly one line"):
            self.assets.acquire(
                receipt_id=receipt.receipt_id,
                receipt_line_id="line-deadbeefdeadbeef",
                acquisition_key="unit-1",
                display_name="Wrong line",
                tracking_mode="individual",
                quantity=1,
                idempotency_key="missing-line",
            )

    def test_fractional_receipt_line_cannot_become_discrete_asset_units(self) -> None:
        receipt = self.receipt("fractional", quantity="1.5")
        with self.assertRaisesRegex(AssetValidationError, "whole-unit"):
            self.assets.acquire(
                receipt_id=receipt.receipt_id,
                receipt_line_id=receipt.lines[0].line_id,
                acquisition_key="fractional",
                display_name="Fractional material",
                tracking_mode="lot",
                quantity=1,
                idempotency_key="fractional-acquire",
            )

    def test_receipt_correction_does_not_change_asset_uuid(self) -> None:
        receipt = self.receipt("correction")
        asset = self.assets.acquire(
            receipt_id=receipt.receipt_id,
            receipt_line_id=receipt.lines[0].line_id,
            acquisition_key="unit-1",
            display_name="Wrench",
            tracking_mode="individual",
            quantity=1,
            entity_uuid=UUID_ONE,
            idempotency_key="asset-before-correction",
        ).asset
        corrected = self.receipts.correct(
            receipt.receipt_id,
            merchant="Synthetic Tool Supply Incorporated",
            idempotency_key="correct-receipt-merchant",
        )
        self.assertEqual(corrected.receipt_id, receipt.receipt_id)
        after = self.assets.get(asset.entity_uuid)
        self.assertEqual(after.entity_uuid, UUID_ONE)
        self.assertEqual(after.revision, 1)
        self.assertEqual(after.acquisition.receipt_id, corrected.receipt_id)

        replay = self.assets.acquire(
            receipt_id=corrected.receipt_id,
            receipt_line_id=corrected.lines[0].line_id,
            acquisition_key="unit-1",
            display_name="Wrench",
            tracking_mode="individual",
            quantity=1,
            idempotency_key="asset-after-correction",
        )
        self.assertEqual(replay.asset.entity_uuid, UUID_ONE)
        self.assertEqual(replay.outcome, "replay")

    def test_enrich_changes_attributes_only_and_requires_explicit_note_replace(self) -> None:
        receipt = self.receipt("explicit-enrich")
        asset = self.assets.acquire(
            receipt_id=receipt.receipt_id,
            acquisition_key="receipt-level-unit",
            display_name="Original name",
            tracking_mode="individual",
            quantity=1,
            entity_uuid=UUID_ONE,
            note="Original note",
            idempotency_key="explicit-create",
        ).asset
        with self.assertRaisesRegex(AssetValidationError, "replace_note"):
            self.assets.enrich(
                asset.entity_uuid,
                note="Silent overwrite",
                idempotency_key="silent-note",
            )
        changed = self.assets.enrich(
            asset.entity_uuid,
            display_name="Better name",
            note="Reviewed note",
            replace_note=True,
            idempotency_key="explicit-enrich",
        )
        self.assertEqual(changed.entity_uuid, UUID_ONE)
        self.assertEqual(changed.revision, 2)
        self.assertEqual(changed.display_name, "Better name")
        self.assertEqual(changed.note, "Reviewed note")
        self.assertEqual(changed.acquisition, asset.acquisition)

    def test_query_is_bounded_and_asset_payload_has_no_downstream_side_effect_state(self) -> None:
        receipt = self.receipt("query", quantity="2")
        line_id = receipt.lines[0].line_id
        for name, key, entity_uuid in (
            ("Alpha wrench", "unit-1", UUID_ONE),
            ("Beta wrench", "unit-2", UUID_TWO),
        ):
            self.assets.acquire(
                receipt_id=receipt.receipt_id,
                receipt_line_id=line_id,
                acquisition_key=key,
                display_name=name,
                tracking_mode="individual",
                quantity=1,
                entity_uuid=entity_uuid,
                idempotency_key=f"query-{key}",
            )
        self.assertEqual(
            [item.entity_uuid for item in self.assets.query(display_name="beta")],
            [UUID_TWO],
        )
        self.assertEqual(len(self.assets.query(receipt_id=receipt.receipt_id)), 2)
        payload = self.adapter.get("asset", UUID_ONE).payload
        for forbidden in (
            "installed_on",
            "assigned_to",
            "fitment",
            "identifiers",
            "serial_number",
            "location",
            "inventory_location",
            "warranty",
            "maintenance",
        ):
            self.assertNotIn(forbidden, payload)

    def test_duplicate_persisted_source_identity_fails_integrity_check(self) -> None:
        receipt = self.receipt("duplicate-source", quantity="2")
        line_id = receipt.lines[0].line_id
        first = self.assets.acquire(
            receipt_id=receipt.receipt_id,
            receipt_line_id=line_id,
            acquisition_key="unit-1",
            display_name="First",
            tracking_mode="individual",
            quantity=1,
            entity_uuid=UUID_ONE,
            idempotency_key="first-source",
        ).asset
        duplicate_payload = dict(self.adapter.get("asset", UUID_ONE).payload)
        duplicate_payload["entity_uuid"] = UUID_TWO
        self.adapter.upsert(
            "asset",
            UUID_TWO,
            duplicate_payload,
            idempotency_key="corrupt-duplicate-source",
            expected_revision=0,
        )
        with self.assertRaises(AssetIntegrityError):
            self.assets.acquire(
                receipt_id=receipt.receipt_id,
                receipt_line_id=line_id,
                acquisition_key=first.acquisition.acquisition_key,
                display_name="First",
                tracking_mode="individual",
                quantity=1,
                idempotency_key="detect-corruption",
            )


if __name__ == "__main__":
    unittest.main()
