from __future__ import annotations

import hashlib
import unittest

from mira.assets import AssetService
from mira.inventory_location import InventoryLocationService
from mira.movement import (
    MOVEMENT_EVENT_TYPE,
    MovementConflictError,
    MovementService,
    MovementValidationError,
)
from mira.receipts import ReceiptService
from mira.structured_state import InMemoryStructuredStateAdapter


ASSET_UUID = "44444444-4444-4444-8444-444444444444"
SECOND_ASSET_UUID = "55555555-5555-4555-8555-555555555555"
MISSING_UUID = "66666666-6666-4666-8666-666666666666"


def fp(label: str) -> str:
    return hashlib.sha256(label.encode("utf-8")).hexdigest()


class ProjectionFailureAdapter:
    """Inject one projection failure before or after the canonical upsert."""

    def __init__(self, delegate, *, fail_after_write: bool) -> None:
        self._delegate = delegate
        self._fail_after_write = fail_after_write
        self._failed = False

    def __getattr__(self, name):
        return getattr(self._delegate, name)

    def upsert(
        self,
        resource_type,
        resource_id,
        payload,
        *,
        idempotency_key,
        expected_revision=None,
    ):
        is_movement_projection = (
            resource_type == "inventory_state"
            and idempotency_key.startswith("movement-state-")
            and not self._failed
        )
        if not is_movement_projection:
            return self._delegate.upsert(
                resource_type,
                resource_id,
                payload,
                idempotency_key=idempotency_key,
                expected_revision=expected_revision,
            )
        self._failed = True
        if self._fail_after_write:
            self._delegate.upsert(
                resource_type,
                resource_id,
                payload,
                idempotency_key=idempotency_key,
                expected_revision=expected_revision,
            )
        raise RuntimeError("synthetic crash around movement projection")


class MovementServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.adapter = InMemoryStructuredStateAdapter(
            schema_version="mira-test-v1",
            resource_types=["receipt", "asset", "location", "inventory_state"],
            event_types=[MOVEMENT_EVENT_TYPE],
        )
        self.receipts = ReceiptService(self.adapter)
        self.assets = AssetService(self.adapter, receipt_service=self.receipts)
        self.inventory = InventoryLocationService(
            self.adapter, asset_service=self.assets
        )
        self.movement = MovementService(
            self.adapter, inventory_service=self.inventory
        )
        self.asset(ASSET_UUID, "primary")
        self.asset(SECOND_ASSET_UUID, "secondary")
        self.inventory.create_location(
            location_id="loc-shop",
            display_name="Synthetic Shop",
            kind="room",
            idempotency_key="location-shop",
        )
        self.inventory.create_location(
            location_id="loc-shelf-a",
            display_name="Shelf A",
            kind="shelf",
            parent_location_id="loc-shop",
            idempotency_key="location-shelf-a",
        )
        self.inventory.create_location(
            location_id="loc-shelf-b",
            display_name="Shelf B",
            kind="shelf",
            parent_location_id="loc-shop",
            idempotency_key="location-shelf-b",
        )
        self.inventory.create_location(
            location_id="loc-bench",
            display_name="Workbench",
            kind="zone",
            parent_location_id="loc-shop",
            idempotency_key="location-bench",
        )
        self.inventory.track_asset(
            ASSET_UUID,
            intended_location_id="loc-shelf-a",
            note="Keep calibration certificate with tool",
            idempotency_key="track-primary",
        )

    def asset(self, entity_uuid: str, label: str):
        receipt = self.receipts.capture(
            merchant="Synthetic Movement Supply",
            purchase_date="2026-08-30",
            currency="USD",
            total_minor=2500,
            order_number=f"ORDER-{label}",
            lines=[
                {
                    "description": f"Synthetic tool {label}",
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

    def observe(
        self,
        *,
        event_id="move-001",
        idempotency_key="movement-001",
        location_id="loc-bench",
        observed_at="2026-08-30T12:00:00-04:00",
        source="explicit_user_observation",
        expected_inventory_revision=1,
        expected_prior_observed_location_id=None,
        expected_prior_observed_at=None,
        note="Placed on bench",
        service=None,
    ):
        target = service or self.movement
        return target.record_observation(
            ASSET_UUID,
            location_id=location_id,
            observed_at=observed_at,
            source=source,
            event_id=event_id,
            idempotency_key=idempotency_key,
            expected_inventory_revision=expected_inventory_revision,
            expected_prior_observed_location_id=expected_prior_observed_location_id,
            expected_prior_observed_at=expected_prior_observed_at,
            note=note,
        )

    def test_records_event_then_projects_observed_state_without_touching_intended(self) -> None:
        result = self.observe()
        self.assertFalse(result.idempotent_replay)
        self.assertFalse(result.recovered_projection)
        self.assertEqual(result.event.stream_revision, 1)
        self.assertEqual(result.event.prior_inventory_revision, 1)
        self.assertEqual(result.event.resulting_inventory_revision, 2)
        self.assertIsNone(result.event.prior_observed_location_id)
        self.assertEqual(result.inventory_state.revision, 2)
        self.assertEqual(result.inventory_state.intended_location_id, "loc-shelf-a")
        self.assertEqual(result.inventory_state.observed_location_id, "loc-bench")
        self.assertEqual(
            result.inventory_state.observed_at,
            "2026-08-30T12:00:00-04:00",
        )
        self.assertEqual(
            result.inventory_state.note,
            "Keep calibration certificate with tool",
        )
        self.assertEqual(len(self.movement.history(ASSET_UUID)), 1)

    def test_exact_replay_adds_no_event_and_no_inventory_revision(self) -> None:
        first = self.observe()
        replay = self.observe()
        self.assertTrue(replay.idempotent_replay)
        self.assertFalse(replay.recovered_projection)
        self.assertEqual(replay.event.event_id, first.event.event_id)
        self.assertEqual(replay.inventory_state.revision, 2)
        self.assertEqual(len(self.movement.history(ASSET_UUID)), 1)

    def test_reusing_event_or_idempotency_identity_for_different_material_fails(self) -> None:
        self.observe()
        with self.assertRaises(MovementConflictError):
            self.observe(location_id="loc-shelf-b")
        with self.assertRaises(MovementConflictError):
            self.observe(
                event_id="move-002",
                idempotency_key="movement-001",
                location_id="loc-shelf-b",
                observed_at="2026-08-30T13:00:00-04:00",
                expected_inventory_revision=2,
                expected_prior_observed_location_id="loc-bench",
                expected_prior_observed_at="2026-08-30T12:00:00-04:00",
            )
        self.assertEqual(len(self.movement.history(ASSET_UUID)), 1)
        self.assertEqual(self.inventory.get_inventory_state(ASSET_UUID).revision, 2)

    def test_stale_revision_and_contradictory_prior_state_fail_before_event(self) -> None:
        with self.assertRaises(MovementConflictError):
            self.observe(expected_inventory_revision=99)
        with self.assertRaises(MovementConflictError):
            self.observe(expected_prior_observed_location_id="loc-shelf-b")
        with self.assertRaises(MovementConflictError):
            self.observe(expected_prior_observed_at="2026-08-30T09:00:00-04:00")
        self.assertEqual(self.movement.history(ASSET_UUID), ())
        self.assertEqual(self.inventory.get_inventory_state(ASSET_UUID).revision, 1)

    def test_unknown_untracked_asset_and_missing_location_fail_closed(self) -> None:
        with self.assertRaises(MovementValidationError):
            self.movement.record_observation(
                MISSING_UUID,
                location_id="loc-bench",
                observed_at="2026-08-30T12:00:00-04:00",
                source="explicit_user_observation",
                event_id="move-missing",
                idempotency_key="movement-missing",
                expected_inventory_revision=1,
            )
        with self.assertRaises(MovementValidationError):
            self.movement.record_observation(
                SECOND_ASSET_UUID,
                location_id="loc-bench",
                observed_at="2026-08-30T12:00:00-04:00",
                source="explicit_user_observation",
                event_id="move-untracked",
                idempotency_key="movement-untracked",
                expected_inventory_revision=1,
            )
        with self.assertRaises(MovementValidationError):
            self.observe(location_id="loc-nowhere")
        self.assertEqual(self.movement.history(ASSET_UUID), ())

    def test_same_location_reobservation_requires_new_later_explicit_event(self) -> None:
        self.observe()
        later = self.observe(
            event_id="move-002",
            idempotency_key="movement-002",
            observed_at="2026-08-30T13:00:00-04:00",
            expected_inventory_revision=2,
            expected_prior_observed_location_id="loc-bench",
            expected_prior_observed_at="2026-08-30T12:00:00-04:00",
            note="Explicitly observed on bench again",
        )
        self.assertEqual(later.inventory_state.revision, 3)
        self.assertEqual(later.inventory_state.observed_location_id, "loc-bench")
        self.assertEqual(len(self.movement.history(ASSET_UUID)), 2)

        with self.assertRaises(MovementConflictError):
            self.observe(
                event_id="move-003",
                idempotency_key="movement-003",
                observed_at="2026-08-30T13:00:00-04:00",
                expected_inventory_revision=3,
                expected_prior_observed_location_id="loc-bench",
                expected_prior_observed_at="2026-08-30T13:00:00-04:00",
            )
        self.assertEqual(len(self.movement.history(ASSET_UUID)), 2)

    def test_history_is_stream_ordered_bounded_and_never_synthesizes_current_state(self) -> None:
        self.assertEqual(self.movement.history(ASSET_UUID), ())
        self.observe()
        self.observe(
            event_id="move-002",
            idempotency_key="movement-002",
            location_id="loc-shelf-b",
            observed_at="2026-08-30T13:00:00-04:00",
            expected_inventory_revision=2,
            expected_prior_observed_location_id="loc-bench",
            expected_prior_observed_at="2026-08-30T12:00:00-04:00",
        )
        self.observe(
            event_id="move-003",
            idempotency_key="movement-003",
            location_id="loc-bench",
            observed_at="2026-08-30T14:00:00-04:00",
            expected_inventory_revision=3,
            expected_prior_observed_location_id="loc-shelf-b",
            expected_prior_observed_at="2026-08-30T13:00:00-04:00",
        )
        self.assertEqual(
            [row.event_id for row in self.movement.history(ASSET_UUID)],
            ["move-001", "move-002", "move-003"],
        )
        self.assertEqual(
            [row.event_id for row in self.movement.history(ASSET_UUID, after_revision=1)],
            ["move-002", "move-003"],
        )
        self.assertEqual(
            [row.event_id for row in self.movement.history(ASSET_UUID, limit=2)],
            ["move-001", "move-002"],
        )

    def test_history_ignores_unrelated_generic_updated_events(self) -> None:
        self.adapter.append_event(
            "inventory_state",
            ASSET_UUID,
            MOVEMENT_EVENT_TYPE,
            "generic-update-001",
            {"event_kind": "inventory_note_changed", "schema_version": 1},
            idempotency_key="generic-update-idempotency",
        )
        self.assertEqual(self.movement.history(ASSET_UUID), ())

        moved = self.observe()
        self.assertEqual(moved.event.stream_revision, 2)
        history = self.movement.history(ASSET_UUID)
        self.assertEqual([row.event_id for row in history], ["move-001"])
        self.assertEqual(history[0].stream_revision, 2)

    def test_crash_after_event_before_projection_recovers_without_duplicate(self) -> None:
        wrapper = ProjectionFailureAdapter(self.adapter, fail_after_write=False)
        service = MovementService(wrapper)
        with self.assertRaisesRegex(RuntimeError, "synthetic crash"):
            self.observe(service=service)
        self.assertEqual(len(service.history(ASSET_UUID)), 1)
        self.assertEqual(self.inventory.get_inventory_state(ASSET_UUID).revision, 1)

        recovered = self.observe(service=service)
        self.assertTrue(recovered.recovered_projection)
        self.assertFalse(recovered.idempotent_replay)
        self.assertEqual(len(service.history(ASSET_UUID)), 1)
        self.assertEqual(self.inventory.get_inventory_state(ASSET_UUID).revision, 2)

    def test_crash_after_projection_before_ack_replays_both_writes_without_duplicates(self) -> None:
        wrapper = ProjectionFailureAdapter(self.adapter, fail_after_write=True)
        service = MovementService(wrapper)
        with self.assertRaisesRegex(RuntimeError, "synthetic crash"):
            self.observe(service=service)
        self.assertEqual(len(service.history(ASSET_UUID)), 1)
        self.assertEqual(self.inventory.get_inventory_state(ASSET_UUID).revision, 2)

        replay = self.observe(service=service)
        self.assertTrue(replay.idempotent_replay)
        self.assertFalse(replay.recovered_projection)
        self.assertEqual(len(service.history(ASSET_UUID)), 1)
        self.assertEqual(self.inventory.get_inventory_state(ASSET_UUID).revision, 2)

    def test_offset_aware_time_is_required_and_z_is_canonicalized(self) -> None:
        with self.assertRaises(MovementValidationError):
            self.observe(observed_at="2026-08-30T12:00:00")
        result = self.observe(observed_at="2026-08-30T16:00:00Z")
        self.assertEqual(result.event.observed_at, "2026-08-30T16:00:00+00:00")
        self.assertEqual(
            result.inventory_state.observed_at,
            "2026-08-30T16:00:00+00:00",
        )


if __name__ == "__main__":
    unittest.main()
