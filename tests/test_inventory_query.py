from __future__ import annotations

from copy import deepcopy
import hashlib
import unittest

from mira.assets import AssetService
from mira.identifiers import IdentifierService
from mira.inventory_location import InventoryLocationService
from mira.inventory_query import (
    InventoryQueryIntegrityError,
    InventoryQueryService,
    InventoryQueryValidationError,
)
from mira.receipts import ReceiptService
from mira.structured_state import InMemoryStructuredStateAdapter


ASSET_A = "11111111-1111-4111-8111-111111111111"
ASSET_B = "22222222-2222-4222-8222-222222222222"
ASSET_C = "33333333-3333-4333-8333-333333333333"
MISSING_ASSET = "99999999-9999-4999-8999-999999999999"


def fp(label: str) -> str:
    return hashlib.sha256(label.encode("utf-8")).hexdigest()


class InventoryQueryServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.adapter = InMemoryStructuredStateAdapter(
            schema_version="mira-test-v1",
            resource_types=[
                "receipt",
                "asset",
                "identifier",
                "location",
                "inventory_state",
            ],
            event_types=["created", "updated"],
        )
        self.receipts = ReceiptService(self.adapter)
        self.assets = AssetService(self.adapter, receipt_service=self.receipts)
        self.identifiers = IdentifierService(self.adapter, asset_service=self.assets)
        self.inventory = InventoryLocationService(
            self.adapter, asset_service=self.assets
        )
        self.query = InventoryQueryService(
            self.adapter,
            asset_service=self.assets,
            identifier_service=self.identifiers,
            inventory_location_service=self.inventory,
        )

        self.site = self.inventory.create_location(
            location_id="loc-site",
            display_name="Synthetic Property",
            kind="site",
            idempotency_key="loc-site-create",
        )
        self.shop = self.inventory.create_location(
            location_id="loc-shop",
            display_name="Shop",
            kind="building",
            parent_location_id=self.site.location_id,
            idempotency_key="loc-shop-create",
        )
        self.shelf_a = self.inventory.create_location(
            location_id="loc-shelf-a",
            display_name="Shelf A",
            kind="shelf",
            parent_location_id=self.shop.location_id,
            idempotency_key="loc-shelf-a-create",
        )
        self.shelf_b = self.inventory.create_location(
            location_id="loc-shelf-b",
            display_name="Shelf B",
            kind="shelf",
            parent_location_id=self.shop.location_id,
            idempotency_key="loc-shelf-b-create",
        )
        self.bench = self.inventory.create_location(
            location_id="loc-bench",
            display_name="Workbench",
            kind="zone",
            parent_location_id=self.shop.location_id,
            idempotency_key="loc-bench-create",
        )

        self.asset_a = self._asset(
            entity_uuid=ASSET_A,
            label="wrench",
            display_name="Zulu Torque Wrench",
        )
        self.asset_b = self._asset(
            entity_uuid=ASSET_B,
            label="hammer",
            display_name="Alpha Dead Blow Hammer",
        )
        self.asset_c = self._asset(
            entity_uuid=ASSET_C,
            label="untracked",
            display_name="Untracked Drill",
        )

        self.identifiers.attach(
            entity_uuid=self.asset_a.entity_uuid,
            identifier_type="model_number",
            namespace="Acme Tools",
            value="WRENCH-42",
            verification_state="verified",
            idempotency_key="identifier-wrench-model",
        )
        self.identifiers.attach(
            entity_uuid=self.asset_a.entity_uuid,
            identifier_type="serial_number",
            namespace="Acme Tools",
            value="SN-A-0001",
            verification_state="observed",
            idempotency_key="identifier-wrench-serial",
        )
        self.identifiers.attach(
            entity_uuid=self.asset_b.entity_uuid,
            identifier_type="model_number",
            namespace="Acme Tools",
            value="HAMMER-9",
            verification_state="verified",
            idempotency_key="identifier-hammer-model",
        )

        self.inventory.track_asset(
            self.asset_a.entity_uuid,
            intended_location_id=self.shelf_a.location_id,
            note="Primary torque tool",
            idempotency_key="track-wrench",
        )
        self.inventory.set_observed_location(
            self.asset_a.entity_uuid,
            location_id=self.bench.location_id,
            observed_at="2026-08-30T18:15:00-04:00",
            idempotency_key="observe-wrench-bench",
        )
        self.inventory.track_asset(
            self.asset_b.entity_uuid,
            intended_location_id=self.shelf_b.location_id,
            idempotency_key="track-hammer",
        )

    def _asset(self, *, entity_uuid: str, label: str, display_name: str):
        receipt = self.receipts.capture(
            merchant="Synthetic Tool Supply",
            purchase_date="2026-08-30",
            currency="USD",
            total_minor=2500,
            order_number=f"ORDER-{label.upper()}",
            lines=[
                {
                    "description": display_name,
                    "quantity": "1",
                    "unit_price_minor": 2500,
                    "line_total_minor": 2500,
                }
            ],
            state="captured",
            source_type="text",
            source_fingerprint=fp(label),
            observed_at="2026-08-30T12:00:00-04:00",
            idempotency_key=f"receipt-{label}",
        ).receipt
        return self.assets.acquire(
            receipt_id=receipt.receipt_id,
            receipt_line_id=receipt.lines[0].line_id,
            acquisition_key="unit-1",
            display_name=display_name,
            tracking_mode="individual",
            quantity=1,
            entity_uuid=entity_uuid,
            note=f"Asset note {label}",
            idempotency_key=f"asset-{label}",
        ).asset

    def test_projection_joins_canonical_identity_provenance_identifiers_and_locations(self) -> None:
        rows = self.query.query(entity_uuid=self.asset_a.entity_uuid)
        self.assertEqual(len(rows), 1)
        item = rows[0]

        self.assertEqual(item.entity_uuid, self.asset_a.entity_uuid)
        self.assertEqual(item.display_name, "Zulu Torque Wrench")
        self.assertEqual(item.tracking_mode, "individual")
        self.assertEqual(item.quantity, 1)
        self.assertEqual(item.asset_revision, self.asset_a.revision)
        self.assertEqual(item.inventory_revision, 2)
        self.assertEqual(item.receipt_id, self.asset_a.acquisition.receipt_id)
        self.assertEqual(item.receipt_line_id, self.asset_a.acquisition.receipt_line_id)
        self.assertEqual(
            [(value.identifier_type, value.source_value) for value in item.identifiers],
            [("model_number", "WRENCH-42"), ("serial_number", "SN-A-0001")],
        )
        self.assertEqual(item.intended_location.location_id, self.shelf_a.location_id)
        self.assertEqual(
            item.intended_location.path_display_names,
            ("Synthetic Property", "Shop", "Shelf A"),
        )
        self.assertEqual(item.observed_location.location_id, self.bench.location_id)
        self.assertEqual(
            item.observed_location.path_display_names,
            ("Synthetic Property", "Shop", "Workbench"),
        )
        self.assertEqual(item.observed_at, "2026-08-30T18:15:00-04:00")
        self.assertEqual(item.asset_note, "Asset note wrench")
        self.assertEqual(item.inventory_note, "Primary torque tool")

    def test_name_entity_identifier_and_location_filters_are_all_canonical(self) -> None:
        self.assertEqual(
            [item.entity_uuid for item in self.query.query(display_name="torque")],
            [self.asset_a.entity_uuid],
        )
        self.assertEqual(
            [
                item.entity_uuid
                for item in self.query.query(
                    identifier_type="model_number",
                    identifier_value="wrench-42",
                    identifier_namespace="acme tools",
                )
            ],
            [self.asset_a.entity_uuid],
        )
        self.assertEqual(
            [
                item.entity_uuid
                for item in self.query.query(
                    intended_location_id=self.shelf_b.location_id
                )
            ],
            [self.asset_b.entity_uuid],
        )
        self.assertEqual(
            [
                item.entity_uuid
                for item in self.query.query(
                    observed_location_id=self.bench.location_id
                )
            ],
            [self.asset_a.entity_uuid],
        )
        self.assertEqual(
            self.query.query(observed_location_id=self.shelf_a.location_id),
            (),
        )

    def test_location_descendant_filter_is_explicit_query_semantics_only(self) -> None:
        exact = self.query.query(intended_location_id=self.shop.location_id)
        self.assertEqual(exact, ())

        descendants = self.query.query(
            intended_location_id=self.shop.location_id,
            include_location_descendants=True,
        )
        self.assertEqual(
            [item.entity_uuid for item in descendants],
            [self.asset_b.entity_uuid, self.asset_a.entity_uuid],
        )
        # Descendant matching did not fabricate an observation for the hammer.
        hammer = descendants[0]
        self.assertIsNone(hammer.observed_location)
        self.assertIsNone(hammer.observed_at)

    def test_untracked_asset_is_not_silently_presented_as_inventory(self) -> None:
        self.assertEqual(self.query.query(entity_uuid=self.asset_c.entity_uuid), ())
        all_rows = self.query.query()
        self.assertNotIn(self.asset_c.entity_uuid, {item.entity_uuid for item in all_rows})

    def test_result_order_and_limit_are_deterministic(self) -> None:
        rows = self.query.query()
        self.assertEqual(
            [item.display_name for item in rows],
            ["Alpha Dead Blow Hammer", "Zulu Torque Wrench"],
        )
        self.assertEqual(
            [item.display_name for item in self.query.query(limit=1)],
            ["Alpha Dead Blow Hammer"],
        )

    def test_bad_filter_material_fails_closed(self) -> None:
        with self.assertRaises(InventoryQueryValidationError):
            self.query.query(display_name="   ")
        with self.assertRaises(InventoryQueryValidationError):
            self.query.query(identifier_type="model_number")
        with self.assertRaises(InventoryQueryValidationError):
            self.query.query(identifier_value="WRENCH-42")
        with self.assertRaisesRegex(InventoryQueryValidationError, "does not exist"):
            self.query.query(intended_location_id="loc-missing")
        with self.assertRaises(InventoryQueryValidationError):
            self.query.query(entity_uuid=MISSING_ASSET)
        with self.assertRaises(InventoryQueryValidationError):
            self.query.query(limit=0)
        with self.assertRaises(InventoryQueryValidationError):
            self.query.query(include_location_descendants=1)

    def test_valid_identifier_with_no_match_returns_empty_not_fabricated_result(self) -> None:
        rows = self.query.query(
            identifier_type="model_number",
            identifier_value="NOT-OWNED",
            identifier_namespace="Acme Tools",
        )
        self.assertEqual(rows, ())

    def test_corrupt_location_cycle_fails_integrity_instead_of_rendering_path(self) -> None:
        current = self.adapter.get("location", self.shop.location_id)
        payload = dict(current.payload)
        payload["parent_location_id"] = self.shelf_a.location_id
        self.adapter.upsert(
            "location",
            self.shop.location_id,
            payload,
            idempotency_key="inject-cycle",
            expected_revision=current.revision,
        )

        with self.assertRaisesRegex(InventoryQueryIntegrityError, "cycle"):
            self.query.query(entity_uuid=self.asset_a.entity_uuid)

    def test_orphan_inventory_state_fails_integrity(self) -> None:
        self.adapter.upsert(
            "inventory_state",
            MISSING_ASSET,
            {
                "schema_version": 1,
                "entity_uuid": MISSING_ASSET,
                "participation_state": "tracked",
                "intended_location_id": None,
                "observed_location_id": None,
                "observed_at": None,
                "note": None,
            },
            idempotency_key="inject-orphan-inventory",
            expected_revision=0,
        )
        with self.assertRaises(InventoryQueryIntegrityError):
            self.query.query()

    def test_query_is_read_only_with_zero_resource_event_or_idempotency_mutation(self) -> None:
        before_records = deepcopy(self.adapter._records)
        before_events = deepcopy(self.adapter._events)
        before_event_ids = deepcopy(self.adapter._event_ids)
        before_stream_revisions = deepcopy(self.adapter._stream_revisions)
        before_idempotency = deepcopy(self.adapter._idempotency)

        rows = self.query.query(
            identifier_type="model_number",
            identifier_value="WRENCH-42",
            identifier_namespace="Acme Tools",
            intended_location_id=self.shop.location_id,
            include_location_descendants=True,
        )
        self.assertEqual([item.entity_uuid for item in rows], [self.asset_a.entity_uuid])

        self.assertEqual(self.adapter._records, before_records)
        self.assertEqual(self.adapter._events, before_events)
        self.assertEqual(self.adapter._event_ids, before_event_ids)
        self.assertEqual(self.adapter._stream_revisions, before_stream_revisions)
        self.assertEqual(self.adapter._idempotency, before_idempotency)


if __name__ == "__main__":
    unittest.main()
