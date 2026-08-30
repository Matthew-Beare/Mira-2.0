from __future__ import annotations

import hashlib
import unittest

from mira.assets import AssetService
from mira.identifiers import IdentifierService
from mira.inventory_location import (
    InventoryLocationService,
    InventoryLocationValidationError,
)
from mira.inventory_movement import (
    InventoryMovementService,
    MovementConflictError,
    MovementIntegrityError,
    MovementValidationError,
)
from mira.receipts import ReceiptService
from mira.structured_state import InMemoryStructuredStateAdapter


UUID_ONE = "11111111-1111-4111-8111-111111111111"
UUID_TWO = "22222222-2222-4222-8222-222222222222"


def fp(label: str) -> str:
    return hashlib.sha256(label.encode("utf-8")).hexdigest()


class FailOnceProjectionService(InventoryLocationService):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fail_next_projection = True

    def set_observed_location(self, *args, **kwargs):
        if self.fail_next_projection:
            self.fail_next_projection = False
            raise InventoryLocationValidationError("synthetic projection interruption")
        return super().set_observed_location(*args, **kwargs)


class InventoryMovementServiceTests(unittest.TestCase):
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
            event_types=["created", "inventory_movement", "updated"],
        )
        self.receipts = ReceiptService(self.adapter)
        self.assets = AssetService(self.adapter, receipt_service=self.receipts)
        self.identifiers = IdentifierService(self.adapter, asset_service=self.assets)
        self.inventory = InventoryLocationService(
            self.adapter,
            asset_service=self.assets,
        )
        self.movements = InventoryMovementService(
            self.adapter,
            inventory_service=self.inventory,
            identifier_service=self.identifiers,
        )
        self._create_assets()
        self._create_locations()
        self.inventory.track_asset(
            UUID_ONE,
            intended_location_id="loc-shelf-a",
            idempotency_key="track-one",
        )
        self.inventory.track_asset(
            UUID_TWO,
            intended_location_id="loc-shelf-a",
            idempotency_key="track-two",
        )
        self.identifiers.attach(
            entity_uuid=UUID_ONE,
            identifier_type="serial_number",
            namespace="Synthetic Tool Co",
            value="SN-001",
            idempotency_key="serial-one",
        )
        for entity_uuid, key in ((UUID_ONE, "upc-one"), (UUID_TWO, "upc-two")):
            self.identifiers.attach(
                entity_uuid=entity_uuid,
                identifier_type="upc_a",
                value="036000291452",
                idempotency_key=key,
            )

    def _create_assets(self) -> None:
        receipt = self.receipts.capture(
            merchant="Synthetic Movement Supply",
            purchase_date="2026-08-30",
            currency="USD",
            total_minor=5000,
            order_number="MOVE-ORDER-1",
            lines=[
                {
                    "description": "Synthetic movement tool",
                    "quantity": "2",
                    "unit_price_minor": 2500,
                    "line_total_minor": 5000,
                }
            ],
            state="captured",
            source_type="text",
            source_fingerprint=fp("movement-receipt"),
            observed_at="2026-08-30T08:00:00-04:00",
            idempotency_key="movement-receipt",
        ).receipt
        line_id = receipt.lines[0].line_id
        for entity_uuid, acquisition_key, label in (
            (UUID_ONE, "unit-1", "one"),
            (UUID_TWO, "unit-2", "two"),
        ):
            self.assets.acquire(
                receipt_id=receipt.receipt_id,
                receipt_line_id=line_id,
                acquisition_key=acquisition_key,
                display_name=f"Synthetic movement tool {label}",
                tracking_mode="individual",
                quantity=1,
                entity_uuid=entity_uuid,
                idempotency_key=f"asset-{label}",
            )

    def _create_locations(self) -> None:
        self.inventory.create_location(
            location_id="loc-shop",
            display_name="Synthetic Shop",
            kind="room",
            idempotency_key="loc-shop",
        )
        for location_id, display_name, kind in (
            ("loc-shelf-a", "Shelf A", "shelf"),
            ("loc-shelf-b", "Shelf B", "shelf"),
            ("loc-bench", "Workbench", "zone"),
        ):
            self.inventory.create_location(
                location_id=location_id,
                display_name=display_name,
                kind=kind,
                parent_location_id="loc-shop",
                idempotency_key=f"create-{location_id}",
            )

    def test_observation_appends_history_and_preserves_intended_home(self) -> None:
        result = self.movements.record(
            entity_uuid=UUID_ONE,
            action="observed",
            to_location_id="loc-bench",
            occurred_at="2026-08-30T12:00:00-04:00",
            idempotency_key="observe-bench",
            source_type="user_text",
        )
        self.assertEqual(result.outcome, "recorded")
        self.assertEqual(result.movement.stream_revision, 1)
        self.assertEqual(result.movement.to_location_id, "loc-bench")
        self.assertEqual(result.inventory_state.intended_location_id, "loc-shelf-a")
        self.assertEqual(result.inventory_state.observed_location_id, "loc-bench")
        self.assertEqual(result.inventory_state.observed_at, "2026-08-30T12:00:00-04:00")
        history = self.movements.history(entity_uuid=UUID_ONE)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0].event_id, result.movement.event_id)

    def test_moved_event_uses_known_source_and_updates_only_observed_state(self) -> None:
        self.movements.record(
            entity_uuid=UUID_ONE,
            action="observed",
            to_location_id="loc-bench",
            occurred_at="2026-08-30T12:00:00-04:00",
            idempotency_key="observe-first",
        )
        moved = self.movements.record(
            entity_uuid=UUID_ONE,
            action="moved",
            from_location_id="loc-bench",
            to_location_id="loc-shelf-b",
            occurred_at="2026-08-30T12:10:00-04:00",
            idempotency_key="move-to-shelf-b",
        )
        self.assertEqual(moved.movement.stream_revision, 2)
        self.assertEqual(moved.movement.from_location_id, "loc-bench")
        self.assertEqual(moved.movement.to_location_id, "loc-shelf-b")
        self.assertEqual(moved.inventory_state.observed_location_id, "loc-shelf-b")
        self.assertEqual(moved.inventory_state.intended_location_id, "loc-shelf-a")

    def test_unique_identifier_resolves_asset_but_product_identifier_ambiguity_fails(self) -> None:
        by_serial = self.movements.record(
            identifier_type="serial_number",
            identifier_namespace="Synthetic Tool Co",
            identifier_value="SN-001",
            action="observed",
            to_location_id="loc-bench",
            occurred_at="2026-08-30T12:00:00-04:00",
            idempotency_key="serial-observe",
        )
        self.assertEqual(by_serial.movement.entity_uuid, UUID_ONE)

        with self.assertRaisesRegex(MovementConflictError, "ambiguous"):
            self.movements.record(
                identifier_type="upc_a",
                identifier_value="036000291452",
                action="observed",
                to_location_id="loc-bench",
                occurred_at="2026-08-30T12:01:00-04:00",
                idempotency_key="ambiguous-upc",
            )
        self.assertEqual(len(self.movements.history(entity_uuid=UUID_TWO)), 0)

    def test_exact_replay_is_zero_event_write(self) -> None:
        first = self.movements.record(
            entity_uuid=UUID_ONE,
            action="observed",
            to_location_id="loc-bench",
            occurred_at="2026-08-30T12:00:00-04:00",
            idempotency_key="same-observation",
            source_ref="chat-message-synthetic-1",
        )
        replay = self.movements.record(
            entity_uuid=UUID_ONE,
            action="observed",
            to_location_id="loc-bench",
            occurred_at="2026-08-30T12:00:00-04:00",
            idempotency_key="same-observation",
            source_ref="chat-message-synthetic-1",
        )
        self.assertEqual(first.movement.event_id, replay.movement.event_id)
        self.assertEqual(replay.outcome, "replay_reconciled")
        self.assertTrue(replay.movement.idempotent_replay)
        self.assertEqual(len(self.movements.history(entity_uuid=UUID_ONE)), 1)
        self.assertEqual(replay.inventory_state.revision, first.inventory_state.revision)

    def test_replay_with_changed_material_fails_closed(self) -> None:
        self.movements.record(
            entity_uuid=UUID_ONE,
            action="observed",
            to_location_id="loc-bench",
            occurred_at="2026-08-30T12:00:00-04:00",
            idempotency_key="conflicting-replay",
        )
        with self.assertRaisesRegex(MovementConflictError, "destination"):
            self.movements.record(
                entity_uuid=UUID_ONE,
                action="observed",
                to_location_id="loc-shelf-b",
                occurred_at="2026-08-30T12:00:00-04:00",
                idempotency_key="conflicting-replay",
            )
        self.assertEqual(len(self.movements.history(entity_uuid=UUID_ONE)), 1)

    def test_interrupted_projection_is_repaired_by_replay_without_duplicate_event(self) -> None:
        fail_inventory = FailOnceProjectionService(
            self.adapter,
            asset_service=self.assets,
        )
        failing = InventoryMovementService(
            self.adapter,
            inventory_service=fail_inventory,
            identifier_service=self.identifiers,
        )
        with self.assertRaisesRegex(MovementValidationError, "synthetic projection interruption"):
            failing.record(
                entity_uuid=UUID_ONE,
                action="observed",
                to_location_id="loc-bench",
                occurred_at="2026-08-30T12:00:00-04:00",
                idempotency_key="crash-after-event",
            )
        self.assertEqual(len(self.movements.history(entity_uuid=UUID_ONE)), 1)
        before = self.inventory.get_inventory_state(UUID_ONE)
        self.assertIsNone(before.observed_location_id)

        repaired = self.movements.record(
            entity_uuid=UUID_ONE,
            action="observed",
            to_location_id="loc-bench",
            occurred_at="2026-08-30T12:00:00-04:00",
            idempotency_key="crash-after-event",
        )
        self.assertEqual(repaired.outcome, "replay_reconciled")
        self.assertEqual(len(self.movements.history(entity_uuid=UUID_ONE)), 1)
        self.assertEqual(repaired.inventory_state.observed_location_id, "loc-bench")
        self.assertEqual(repaired.inventory_state.intended_location_id, "loc-shelf-a")

    def test_scan_in_and_scan_out_share_core_without_capture_ui(self) -> None:
        scan_in = self.movements.record(
            entity_uuid=UUID_ONE,
            action="scan_in",
            to_location_id="loc-bench",
            occurred_at="2026-08-30T12:00:00-04:00",
            idempotency_key="scan-in-bench",
            source_type="barcode_scan",
            source_ref="synthetic-scanner-evidence",
        )
        self.assertEqual(scan_in.inventory_state.observed_location_id, "loc-bench")
        self.assertEqual(scan_in.inventory_state.intended_location_id, "loc-shelf-a")

        scan_out = self.movements.record(
            entity_uuid=UUID_ONE,
            action="scan_out",
            from_location_id="loc-bench",
            occurred_at="2026-08-30T12:05:00-04:00",
            idempotency_key="scan-out-bench",
            source_type="barcode_scan",
            source_ref="synthetic-scanner-evidence-2",
        )
        self.assertEqual(scan_out.movement.from_location_id, "loc-bench")
        self.assertIsNone(scan_out.movement.to_location_id)
        self.assertIsNone(scan_out.inventory_state.observed_location_id)
        self.assertIsNone(scan_out.inventory_state.observed_at)
        self.assertEqual(scan_out.inventory_state.intended_location_id, "loc-shelf-a")
        self.assertEqual(
            [item.action for item in self.movements.history(entity_uuid=UUID_ONE)],
            ["scan_in", "scan_out"],
        )

    def test_scan_out_requires_known_current_source_and_source_claim_must_match(self) -> None:
        with self.assertRaisesRegex(MovementConflictError, "known current observed"):
            self.movements.record(
                entity_uuid=UUID_ONE,
                action="scan_out",
                occurred_at="2026-08-30T12:00:00-04:00",
                idempotency_key="scan-out-nowhere",
            )
        self.movements.record(
            entity_uuid=UUID_ONE,
            action="observed",
            to_location_id="loc-bench",
            occurred_at="2026-08-30T12:01:00-04:00",
            idempotency_key="observe-for-source-check",
        )
        with self.assertRaisesRegex(MovementConflictError, "does not match"):
            self.movements.record(
                entity_uuid=UUID_ONE,
                action="moved",
                from_location_id="loc-shelf-b",
                to_location_id="loc-shelf-a",
                occurred_at="2026-08-30T12:02:00-04:00",
                idempotency_key="wrong-source",
            )
        self.assertEqual(len(self.movements.history(entity_uuid=UUID_ONE)), 1)

    def test_occurrence_time_and_location_validation_fail_before_history_write(self) -> None:
        with self.assertRaisesRegex(MovementValidationError, "explicit UTC offset"):
            self.movements.record(
                entity_uuid=UUID_ONE,
                action="observed",
                to_location_id="loc-bench",
                occurred_at="2026-08-30T12:00:00",
                idempotency_key="naive-time",
            )
        with self.assertRaisesRegex(MovementValidationError, "does not exist"):
            self.movements.record(
                entity_uuid=UUID_ONE,
                action="observed",
                to_location_id="loc-missing",
                occurred_at="2026-08-30T12:00:00-04:00",
                idempotency_key="missing-location",
            )
        self.assertEqual(len(self.movements.history(entity_uuid=UUID_ONE)), 0)

    def test_history_is_stream_ordered_and_bounded(self) -> None:
        for index, location in enumerate(("loc-bench", "loc-shelf-b", "loc-bench"), start=1):
            self.movements.record(
                entity_uuid=UUID_ONE,
                action="observed",
                to_location_id=location,
                occurred_at=f"2026-08-30T12:0{index}:00-04:00",
                idempotency_key=f"ordered-{index}",
            )
        history = self.movements.history(entity_uuid=UUID_ONE)
        self.assertEqual([row.stream_revision for row in history], [1, 2, 3])
        self.assertEqual(
            [row.stream_revision for row in self.movements.history(entity_uuid=UUID_ONE, after_revision=1)],
            [2, 3],
        )
        self.assertEqual(len(self.movements.history(entity_uuid=UUID_ONE, limit=2)), 2)

    def test_movement_does_not_mutate_asset_or_identifier_identity(self) -> None:
        asset_before = self.adapter.get("asset", UUID_ONE)
        identifiers_before = tuple(self.adapter.query("identifier", filters={"entity_uuid": UUID_ONE}, limit=100))
        result = self.movements.record(
            entity_uuid=UUID_ONE,
            action="moved",
            to_location_id="loc-bench",
            occurred_at="2026-08-30T12:00:00Z",
            idempotency_key="side-effect-check",
        )
        self.assertEqual(result.inventory_state.intended_location_id, "loc-shelf-a")
        self.assertEqual(self.adapter.get("asset", UUID_ONE), asset_before)
        self.assertEqual(
            tuple(self.adapter.query("identifier", filters={"entity_uuid": UUID_ONE}, limit=100)),
            identifiers_before,
        )

    def test_malformed_persisted_movement_fails_integrity(self) -> None:
        self.adapter.append_event(
            "inventory_state",
            UUID_ONE,
            "inventory_movement",
            "movement-corrupt",
            {
                "schema_version": 1,
                "entity_uuid": UUID_TWO,
                "action": "observed",
                "from_location_id": None,
                "to_location_id": "loc-bench",
                "occurred_at": "2026-08-30T12:00:00-04:00",
                "source_type": "manual",
                "source_ref": None,
                "note": None,
            },
            idempotency_key="corrupt-event",
            expected_stream_revision=0,
        )
        with self.assertRaisesRegex(MovementIntegrityError, "stream identity"):
            self.movements.history(entity_uuid=UUID_ONE)


if __name__ == "__main__":
    unittest.main()
