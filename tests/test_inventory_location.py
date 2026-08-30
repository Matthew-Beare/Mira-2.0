from __future__ import annotations

import hashlib
import unittest

from mira.assets import AssetService
from mira.inventory_location import (
    InventoryLocationConflictError,
    InventoryLocationIntegrityError,
    InventoryLocationService,
    InventoryLocationValidationError,
)
from mira.receipts import ReceiptService
from mira.structured_state import InMemoryStructuredStateAdapter


ASSET_UUID = "44444444-4444-4444-8444-444444444444"
SECOND_ASSET_UUID = "55555555-5555-4555-8555-555555555555"


def fp(label: str) -> str:
    return hashlib.sha256(label.encode("utf-8")).hexdigest()


class InventoryLocationServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.adapter = InMemoryStructuredStateAdapter(
            schema_version="mira-test-v1",
            resource_types=["receipt", "asset", "location", "inventory_state"],
            event_types=["created", "updated"],
        )
        self.receipts = ReceiptService(self.adapter)
        self.assets = AssetService(self.adapter, receipt_service=self.receipts)
        self.locations = InventoryLocationService(
            self.adapter, asset_service=self.assets
        )

    def asset(self, entity_uuid: str = ASSET_UUID, label: str = "asset"):
        receipt = self.receipts.capture(
            merchant="Synthetic Inventory Supply",
            purchase_date="2026-08-30",
            currency="USD",
            total_minor=2500,
            order_number=f"ORDER-{label}",
            lines=[
                {
                    "description": "Synthetic tracked tool",
                    "quantity": "1",
                    "unit_price_minor": 2500,
                    "line_total_minor": 2500,
                }
            ],
            state="captured",
            source_type="text",
            source_fingerprint=fp(label),
            observed_at="2026-08-30T08:00:00-04:00",
            idempotency_key=f"receipt-{label}",
        ).receipt
        return self.assets.acquire(
            receipt_id=receipt.receipt_id,
            receipt_line_id=receipt.lines[0].line_id,
            acquisition_key="unit-1",
            display_name=f"Synthetic tool {label}",
            tracking_mode="individual",
            quantity=1,
            entity_uuid=entity_uuid,
            idempotency_key=f"asset-{label}",
        ).asset

    def hierarchy(self):
        site = self.locations.create_location(
            location_id="loc-site",
            display_name="Synthetic Site",
            kind="site",
            idempotency_key="loc-site-create",
        )
        room = self.locations.create_location(
            location_id="loc-room",
            display_name="Synthetic Shop",
            kind="room",
            parent_location_id=site.location_id,
            idempotency_key="loc-room-create",
        )
        shelf = self.locations.create_location(
            location_id="loc-shelf",
            display_name="Shelf A",
            kind="shelf",
            parent_location_id=room.location_id,
            idempotency_key="loc-shelf-create",
        )
        bench = self.locations.create_location(
            location_id="loc-bench",
            display_name="Work Bench",
            kind="zone",
            parent_location_id=room.location_id,
            idempotency_key="loc-bench-create",
        )
        return site, room, shelf, bench

    def test_inventory_participation_reuses_asset_uuid_as_resource_identity(self) -> None:
        asset = self.asset()
        state = self.locations.track_asset(
            asset.entity_uuid,
            idempotency_key="track-asset",
            note="Tracked inventory projection",
        )
        self.assertEqual(state.entity_uuid, asset.entity_uuid)
        self.assertEqual(state.revision, 1)
        self.assertEqual(state.participation_state, "tracked")
        record = self.adapter.get("inventory_state", asset.entity_uuid)
        self.assertEqual(record.resource_id, asset.entity_uuid)
        self.assertEqual(record.payload["entity_uuid"], asset.entity_uuid)
        self.assertEqual(len(self.adapter.query("inventory_state", limit=10)), 1)

    def test_tracking_unknown_asset_fails_closed(self) -> None:
        with self.assertRaisesRegex(InventoryLocationValidationError, "does not exist"):
            self.locations.track_asset(
                ASSET_UUID,
                idempotency_key="track-missing",
            )
        self.assertEqual(self.adapter.query("inventory_state", limit=10), ())

    def test_location_hierarchy_and_exact_replay(self) -> None:
        site, room, shelf, _ = self.hierarchy()
        self.assertIsNone(site.parent_location_id)
        self.assertEqual(room.parent_location_id, site.location_id)
        self.assertEqual(shelf.parent_location_id, room.location_id)
        replay = self.locations.create_location(
            location_id="loc-shelf",
            display_name="Shelf A",
            kind="shelf",
            parent_location_id="loc-room",
            idempotency_key="different-logical-key",
        )
        self.assertTrue(replay.idempotent_replay)
        self.assertEqual(replay.revision, 1)
        self.assertEqual(
            [item.location_id for item in self.locations.list_locations()],
            ["loc-bench", "loc-room", "loc-shelf", "loc-site"],
        )

    def test_missing_parent_self_parent_and_cycles_fail_closed(self) -> None:
        with self.assertRaisesRegex(InventoryLocationValidationError, "does not exist"):
            self.locations.create_location(
                location_id="loc-child",
                display_name="Child",
                kind="bin",
                parent_location_id="loc-missing",
                idempotency_key="missing-parent",
            )
        with self.assertRaises(InventoryLocationConflictError):
            self.locations.create_location(
                location_id="loc-self",
                display_name="Self",
                kind="bin",
                parent_location_id="loc-self",
                idempotency_key="self-parent",
            )

        site, room, shelf, _ = self.hierarchy()
        with self.assertRaisesRegex(InventoryLocationConflictError, "cycle"):
            self.locations.update_location(
                site.location_id,
                parent_location_id=shelf.location_id,
                replace_parent=True,
                idempotency_key="cycle-site-under-shelf",
            )
        self.assertIsNone(self.locations.get_location(site.location_id).parent_location_id)
        self.assertEqual(
            self.locations.get_location(room.location_id).parent_location_id,
            site.location_id,
        )

    def test_location_rename_and_reparent_preserve_stable_location_id(self) -> None:
        site, room, shelf, bench = self.hierarchy()
        changed = self.locations.update_location(
            shelf.location_id,
            display_name="Shelf Alpha",
            parent_location_id=bench.location_id,
            replace_parent=True,
            idempotency_key="rename-reparent-shelf",
        )
        self.assertEqual(changed.location_id, shelf.location_id)
        self.assertEqual(changed.revision, 2)
        self.assertEqual(changed.display_name, "Shelf Alpha")
        self.assertEqual(changed.parent_location_id, bench.location_id)
        self.assertEqual(self.locations.get_location(site.location_id).revision, 1)
        self.assertEqual(self.locations.get_location(room.location_id).revision, 1)

    def test_intended_and_observed_locations_change_independently(self) -> None:
        asset = self.asset()
        _, _, shelf, bench = self.hierarchy()
        tracked = self.locations.track_asset(
            asset.entity_uuid,
            intended_location_id=shelf.location_id,
            idempotency_key="track-with-home",
        )
        self.assertEqual(tracked.intended_location_id, shelf.location_id)
        self.assertIsNone(tracked.observed_location_id)
        self.assertIsNone(tracked.observed_at)

        observed = self.locations.set_observed_location(
            asset.entity_uuid,
            location_id=bench.location_id,
            observed_at="2026-08-30T12:34:56-04:00",
            idempotency_key="observe-on-bench",
        )
        self.assertEqual(observed.revision, 2)
        self.assertEqual(observed.intended_location_id, shelf.location_id)
        self.assertEqual(observed.observed_location_id, bench.location_id)
        self.assertEqual(observed.observed_at, "2026-08-30T12:34:56-04:00")

        new_home = self.locations.set_intended_location(
            asset.entity_uuid,
            location_id=bench.location_id,
            idempotency_key="change-home-to-bench",
        )
        self.assertEqual(new_home.revision, 3)
        self.assertEqual(new_home.intended_location_id, bench.location_id)
        self.assertEqual(new_home.observed_location_id, bench.location_id)
        self.assertEqual(new_home.observed_at, observed.observed_at)

    def test_observed_location_requires_offset_aware_timestamp(self) -> None:
        asset = self.asset()
        _, _, _, bench = self.hierarchy()
        self.locations.track_asset(asset.entity_uuid, idempotency_key="track")
        for value in (None, "", "2026-08-30T12:00:00"):
            with self.subTest(value=value):
                with self.assertRaises(InventoryLocationValidationError):
                    self.locations.set_observed_location(
                        asset.entity_uuid,
                        location_id=bench.location_id,
                        observed_at=value,
                        idempotency_key=f"bad-observed-{value}",
                    )
        good = self.locations.set_observed_location(
            asset.entity_uuid,
            location_id=bench.location_id,
            observed_at="2026-08-30T16:00:00Z",
            idempotency_key="good-z-observation",
        )
        self.assertEqual(good.observed_at, "2026-08-30T16:00:00+00:00")

    def test_clearing_intended_and_observed_state_does_not_cross_clear(self) -> None:
        asset = self.asset()
        _, _, shelf, bench = self.hierarchy()
        self.locations.track_asset(
            asset.entity_uuid,
            intended_location_id=shelf.location_id,
            idempotency_key="track",
        )
        self.locations.set_observed_location(
            asset.entity_uuid,
            location_id=bench.location_id,
            observed_at="2026-08-30T12:00:00-04:00",
            idempotency_key="observe",
        )
        no_home = self.locations.set_intended_location(
            asset.entity_uuid,
            location_id=None,
            idempotency_key="clear-home",
        )
        self.assertIsNone(no_home.intended_location_id)
        self.assertEqual(no_home.observed_location_id, bench.location_id)
        self.assertEqual(no_home.observed_at, "2026-08-30T12:00:00-04:00")

        no_observation = self.locations.set_observed_location(
            asset.entity_uuid,
            location_id=None,
            observed_at=None,
            idempotency_key="clear-observed",
        )
        self.assertIsNone(no_observation.intended_location_id)
        self.assertIsNone(no_observation.observed_location_id)
        self.assertIsNone(no_observation.observed_at)

    def test_missing_location_references_fail_closed(self) -> None:
        asset = self.asset()
        self.locations.track_asset(asset.entity_uuid, idempotency_key="track")
        with self.assertRaisesRegex(InventoryLocationValidationError, "does not exist"):
            self.locations.set_intended_location(
                asset.entity_uuid,
                location_id="loc-missing",
                idempotency_key="missing-home",
            )
        with self.assertRaisesRegex(InventoryLocationValidationError, "does not exist"):
            self.locations.set_observed_location(
                asset.entity_uuid,
                location_id="loc-missing",
                observed_at="2026-08-30T12:00:00-04:00",
                idempotency_key="missing-observed",
            )

    def test_corrupt_inventory_identity_or_location_reference_fails_integrity(self) -> None:
        asset = self.asset()
        _, _, shelf, _ = self.hierarchy()
        state = self.locations.track_asset(
            asset.entity_uuid,
            intended_location_id=shelf.location_id,
            idempotency_key="track",
        )
        payload = dict(self.adapter.get("inventory_state", asset.entity_uuid).payload)
        payload["entity_uuid"] = SECOND_ASSET_UUID
        self.adapter.upsert(
            "inventory_state",
            asset.entity_uuid,
            payload,
            idempotency_key="corrupt-uuid",
            expected_revision=state.revision,
        )
        with self.assertRaises(InventoryLocationIntegrityError):
            self.locations.get_inventory_state(asset.entity_uuid)

    def test_inventory_location_mutations_do_not_change_asset_or_create_side_effects(self) -> None:
        asset = self.asset()
        original_payload = dict(self.adapter.get("asset", asset.entity_uuid).payload)
        _, _, shelf, bench = self.hierarchy()
        self.locations.track_asset(
            asset.entity_uuid,
            intended_location_id=shelf.location_id,
            idempotency_key="track",
        )
        self.locations.set_observed_location(
            asset.entity_uuid,
            location_id=bench.location_id,
            observed_at="2026-08-30T12:00:00-04:00",
            idempotency_key="observe",
        )
        asset_after = self.adapter.get("asset", asset.entity_uuid)
        self.assertEqual(asset_after.revision, asset.revision)
        self.assertEqual(asset_after.payload, original_payload)
        inventory_payload = self.adapter.get("inventory_state", asset.entity_uuid).payload
        for forbidden in (
            "movement_event",
            "scan_id",
            "barcode_action",
            "installed_on",
            "fitment",
            "par_level",
            "grocery_stock",
        ):
            self.assertNotIn(forbidden, inventory_payload)


if __name__ == "__main__":
    unittest.main()
