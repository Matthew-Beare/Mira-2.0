"""Replay-safe canonical inventory movement and observation history.

Movement history is an immutable STORE-001 event stream over the existing
``inventory_state/<Entity UUID>`` identity.  The current inventory-state row is a
projection of the latest movement event, not a second history authority.  Events
are appended before projection updates so an interrupted write can be repaired by
replaying the same logical movement without duplicating history.

Barcode/QR/camera capture is deliberately outside this module.  Future capture
clients may feed the same canonical actions after resolving their evidence.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime
import hashlib
import json
from typing import Any

from .identifiers import (
    IdentifierIntegrityError,
    IdentifierService,
    IdentifierValidationError,
)
from .inventory_location import (
    InventoryLocationConflictError,
    InventoryLocationIntegrityError,
    InventoryLocationService,
    InventoryLocationValidationError,
    InventoryStateView,
)
from .structured_state import (
    EventRecord,
    IdempotencyConflictError,
    IdentityConflictError,
    RevisionConflictError,
    StructuredStateAdapter,
    ValidationError as StoreValidationError,
)


MOVEMENT_EVENT_TYPE = "inventory_movement"
MOVEMENT_SCHEMA_VERSION = 1
MOVEMENT_ACTIONS = frozenset({"observed", "moved", "scan_in", "scan_out"})
MOVEMENT_SOURCE_TYPES = frozenset(
    {"manual", "user_text", "barcode_scan", "qr_scan", "system"}
)


class MovementError(Exception):
    """Base class for canonical movement failures."""


class MovementValidationError(MovementError):
    """Raised when requested movement material is malformed or unresolved."""


class MovementConflictError(MovementError):
    """Raised when movement material conflicts with current/canonical state."""


class MovementIntegrityError(MovementError):
    """Raised when persisted movement history violates canonical invariants."""


@dataclass(frozen=True)
class MovementView:
    event_id: str
    stream_revision: int
    entity_uuid: str
    action: str
    from_location_id: str | None
    to_location_id: str | None
    occurred_at: str
    source_type: str
    source_ref: str | None
    note: str | None
    idempotent_replay: bool = False


@dataclass(frozen=True)
class MovementResult:
    movement: MovementView
    inventory_state: InventoryStateView
    outcome: str  # recorded | replay_reconciled


class InventoryMovementService:
    """Append immutable movement facts and reconcile latest observed state."""

    def __init__(
        self,
        adapter: StructuredStateAdapter,
        *,
        inventory_service: InventoryLocationService | None = None,
        identifier_service: IdentifierService | None = None,
        event_type: str = MOVEMENT_EVENT_TYPE,
    ) -> None:
        self._adapter = adapter
        self._inventory = inventory_service or InventoryLocationService(adapter)
        self._identifiers = identifier_service or IdentifierService(adapter)
        self._event_type = event_type

    def record(
        self,
        *,
        action: str,
        occurred_at: str,
        idempotency_key: str,
        entity_uuid: str | None = None,
        identifier_type: str | None = None,
        identifier_value: str | None = None,
        identifier_namespace: str | None = None,
        from_location_id: str | None = None,
        to_location_id: str | None = None,
        source_type: str = "manual",
        source_ref: str | None = None,
        note: str | None = None,
    ) -> MovementResult:
        """Record one logical movement/observation and reconcile its projection.

        The immutable event is written first.  If projection update subsequently
        fails, replaying the same logical request finds the existing event and
        repairs the projection from the latest canonical event without appending a
        duplicate.
        """

        key = _text(idempotency_key, "idempotency_key", 128)
        movement_action = _action(action)
        event_time = _occurred_at(occurred_at)
        source = _source_type(source_type)
        source_reference = _optional_text(source_ref, "source_ref", 500)
        normalized_note = _optional_text(note, "note", 4000)
        explicit_from = _optional_id(from_location_id, "from_location_id")
        destination = _optional_id(to_location_id, "to_location_id")

        entity, current = self._resolve_tracked_entity(
            entity_uuid=entity_uuid,
            identifier_type=identifier_type,
            identifier_value=identifier_value,
            identifier_namespace=identifier_namespace,
        )
        event_id = _event_id(entity, key)
        stream_events = self._stream_events(entity)
        prior = next((event for event in stream_events if event.event_id == event_id), None)
        if prior is not None:
            movement = _movement_view(prior, idempotent_replay=True)
            self._assert_replay_matches(
                movement,
                action=movement_action,
                occurred_at=event_time,
                explicit_from=explicit_from,
                destination=destination,
                source_type=source,
                source_ref=source_reference,
                note=normalized_note,
            )
            projected = self._reconcile_latest_projection(entity)
            return MovementResult(
                movement=movement,
                inventory_state=projected,
                outcome="replay_reconciled",
            )

        resolved_from, resolved_to = self._resolve_locations_for_new_event(
            action=movement_action,
            current=current,
            explicit_from=explicit_from,
            destination=destination,
        )
        payload = {
            "schema_version": MOVEMENT_SCHEMA_VERSION,
            "entity_uuid": entity,
            "action": movement_action,
            "from_location_id": resolved_from,
            "to_location_id": resolved_to,
            "occurred_at": event_time,
            "source_type": source,
            "source_ref": source_reference,
            "note": normalized_note,
        }
        expected_stream_revision = stream_events[-1].stream_revision if stream_events else 0
        try:
            result = self._adapter.append_event(
                "inventory_state",
                entity,
                self._event_type,
                event_id,
                payload,
                idempotency_key=key,
                expected_stream_revision=expected_stream_revision,
            )
        except RevisionConflictError as exc:
            raise MovementConflictError(str(exc)) from exc
        except (IdempotencyConflictError, IdentityConflictError) as exc:
            raise MovementConflictError(str(exc)) from exc
        except StoreValidationError as exc:
            raise MovementValidationError(str(exc)) from exc

        movement = _movement_view(
            result.event,
            idempotent_replay=result.idempotent_replay,
        )
        projected = self._reconcile_latest_projection(entity)
        return MovementResult(
            movement=movement,
            inventory_state=projected,
            outcome="replay_reconciled" if result.idempotent_replay else "recorded",
        )

    def history(
        self,
        *,
        entity_uuid: str | None = None,
        identifier_type: str | None = None,
        identifier_value: str | None = None,
        identifier_namespace: str | None = None,
        after_revision: int = 0,
        limit: int = 100,
    ) -> tuple[MovementView, ...]:
        if not isinstance(after_revision, int) or isinstance(after_revision, bool) or after_revision < 0:
            raise MovementValidationError("after_revision must be a non-negative integer")
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 1000:
            raise MovementValidationError("limit must be an integer from 1 through 1000")
        entity, _ = self._resolve_tracked_entity(
            entity_uuid=entity_uuid,
            identifier_type=identifier_type,
            identifier_value=identifier_value,
            identifier_namespace=identifier_namespace,
        )
        rows = [
            _movement_view(event)
            for event in self._stream_events(entity)
            if event.event_type == self._event_type and event.stream_revision > after_revision
        ]
        return tuple(rows[:limit])

    def reconcile(self, entity_uuid: str) -> InventoryStateView:
        """Repair the current observed-state projection from latest movement history."""

        entity, _ = self._resolve_tracked_entity(
            entity_uuid=entity_uuid,
            identifier_type=None,
            identifier_value=None,
            identifier_namespace=None,
        )
        return self._reconcile_latest_projection(entity)

    def _resolve_tracked_entity(
        self,
        *,
        entity_uuid: str | None,
        identifier_type: str | None,
        identifier_value: str | None,
        identifier_namespace: str | None,
    ) -> tuple[str, InventoryStateView]:
        direct = entity_uuid is not None
        identifier_requested = any(
            value is not None
            for value in (identifier_type, identifier_value, identifier_namespace)
        )
        if direct == identifier_requested:
            raise MovementValidationError(
                "provide exactly one asset resolution path: entity_uuid or identifier"
            )

        if direct:
            if not isinstance(entity_uuid, str):
                raise MovementValidationError("entity_uuid must be text")
            resolved_entity = entity_uuid
        else:
            if identifier_type is None or identifier_value is None:
                raise MovementValidationError(
                    "identifier_type and identifier_value are required for identifier resolution"
                )
            try:
                assets = self._identifiers.lookup_assets(
                    identifier_type=identifier_type,
                    value=identifier_value,
                    namespace=identifier_namespace,
                    limit=2,
                )
            except IdentifierIntegrityError as exc:
                raise MovementIntegrityError(str(exc)) from exc
            except IdentifierValidationError as exc:
                raise MovementValidationError(str(exc)) from exc
            if not assets:
                raise MovementValidationError("identifier resolves no canonical asset")
            if len(assets) != 1:
                raise MovementConflictError(
                    "identifier is ambiguous across multiple canonical assets"
                )
            resolved_entity = assets[0].entity_uuid

        try:
            state = self._inventory.get_inventory_state(resolved_entity)
        except InventoryLocationIntegrityError as exc:
            raise MovementIntegrityError(str(exc)) from exc
        except InventoryLocationValidationError as exc:
            raise MovementValidationError(str(exc)) from exc
        return state.entity_uuid, state

    def _resolve_locations_for_new_event(
        self,
        *,
        action: str,
        current: InventoryStateView,
        explicit_from: str | None,
        destination: str | None,
    ) -> tuple[str | None, str | None]:
        if explicit_from is not None:
            self._get_location(explicit_from)
        if destination is not None:
            self._get_location(destination)

        if action == "observed":
            if explicit_from is not None:
                raise MovementValidationError(
                    "observed action does not accept a claimed from_location_id"
                )
            if destination is None:
                raise MovementValidationError("observed action requires to_location_id")
            return None, destination

        if action in {"moved", "scan_in"}:
            if destination is None:
                raise MovementValidationError(f"{action} action requires to_location_id")
            current_from = current.observed_location_id
            if explicit_from is not None:
                if current_from is None:
                    raise MovementConflictError(
                        "cannot claim a source location when current observed location is unknown"
                    )
                if explicit_from != current_from:
                    raise MovementConflictError(
                        "claimed from_location_id does not match current observed location"
                    )
            return current_from, destination

        if destination is not None:
            raise MovementValidationError("scan_out action must not set to_location_id")
        current_from = current.observed_location_id
        if current_from is None:
            raise MovementConflictError(
                "scan_out requires a known current observed location"
            )
        if explicit_from is not None and explicit_from != current_from:
            raise MovementConflictError(
                "claimed from_location_id does not match current observed location"
            )
        return current_from, None

    def _get_location(self, location_id: str) -> None:
        try:
            self._inventory.get_location(location_id)
        except InventoryLocationIntegrityError as exc:
            raise MovementIntegrityError(str(exc)) from exc
        except InventoryLocationValidationError as exc:
            raise MovementValidationError(str(exc)) from exc

    def _stream_events(self, entity_uuid: str) -> tuple[EventRecord, ...]:
        rows: list[EventRecord] = []
        after = 0
        for _ in range(100):
            try:
                page = tuple(
                    self._adapter.events_for(
                        "inventory_state",
                        entity_uuid,
                        after_revision=after,
                        limit=1000,
                    )
                )
            except StoreValidationError as exc:
                raise MovementValidationError(str(exc)) from exc
            if not page:
                break
            rows.extend(page)
            after = page[-1].stream_revision
            if len(page) < 1000:
                break
        else:
            raise MovementIntegrityError("movement stream exceeds safe traversal bound")
        rows.sort(key=lambda event: event.stream_revision)
        seen_ids: set[str] = set()
        previous_revision = 0
        for event in rows:
            if event.event_id in seen_ids:
                raise MovementIntegrityError("duplicate movement-stream event identity")
            if event.stream_revision <= previous_revision:
                raise MovementIntegrityError("movement stream revisions are not strictly ordered")
            seen_ids.add(event.event_id)
            previous_revision = event.stream_revision
        return tuple(rows)

    def _reconcile_latest_projection(self, entity_uuid: str) -> InventoryStateView:
        current = self._inventory_state(entity_uuid)
        movements = [
            _movement_view(event)
            for event in self._stream_events(entity_uuid)
            if event.event_type == self._event_type
        ]
        if not movements:
            return current
        latest = movements[-1]
        if latest.action == "scan_out":
            desired_location = None
            desired_time = None
        else:
            if latest.to_location_id is None:
                raise MovementIntegrityError(
                    "latest non-scan-out movement has no destination location"
                )
            desired_location = latest.to_location_id
            desired_time = latest.occurred_at

        if (
            current.observed_location_id == desired_location
            and current.observed_at == desired_time
        ):
            return current
        try:
            return self._inventory.set_observed_location(
                entity_uuid,
                location_id=desired_location,
                observed_at=desired_time,
                idempotency_key=_projection_key(latest.event_id),
            )
        except InventoryLocationConflictError as exc:
            raise MovementConflictError(str(exc)) from exc
        except InventoryLocationIntegrityError as exc:
            raise MovementIntegrityError(str(exc)) from exc
        except InventoryLocationValidationError as exc:
            raise MovementValidationError(str(exc)) from exc

    def _inventory_state(self, entity_uuid: str) -> InventoryStateView:
        try:
            return self._inventory.get_inventory_state(entity_uuid)
        except InventoryLocationIntegrityError as exc:
            raise MovementIntegrityError(str(exc)) from exc
        except InventoryLocationValidationError as exc:
            raise MovementValidationError(str(exc)) from exc

    @staticmethod
    def _assert_replay_matches(
        movement: MovementView,
        *,
        action: str,
        occurred_at: str,
        explicit_from: str | None,
        destination: str | None,
        source_type: str,
        source_ref: str | None,
        note: str | None,
    ) -> None:
        if movement.action != action or movement.occurred_at != occurred_at:
            raise MovementConflictError(
                "movement replay conflicts with canonical action or occurrence time"
            )
        if explicit_from is not None and movement.from_location_id != explicit_from:
            raise MovementConflictError(
                "movement replay conflicts with canonical source location"
            )
        if movement.to_location_id != destination:
            raise MovementConflictError(
                "movement replay conflicts with canonical destination location"
            )
        if (
            movement.source_type != source_type
            or movement.source_ref != source_ref
            or movement.note != note
        ):
            raise MovementConflictError(
                "movement replay conflicts with canonical source metadata or note"
            )


def _movement_view(
    event: EventRecord,
    *,
    idempotent_replay: bool = False,
) -> MovementView:
    if event.event_type != MOVEMENT_EVENT_TYPE:
        raise MovementValidationError("event is not a canonical inventory movement")
    payload = dict(event.payload)
    if payload.get("schema_version") != MOVEMENT_SCHEMA_VERSION:
        raise MovementValidationError("unsupported movement schema version")
    entity_uuid = _text(payload.get("entity_uuid"), "entity_uuid", 128)
    if event.stream_type != "inventory_state" or event.stream_id != entity_uuid:
        raise MovementIntegrityError(
            "movement stream identity does not match canonical Entity UUID"
        )
    action = _action(payload.get("action"))
    source = _source_type(payload.get("source_type"))
    from_location = _optional_id(payload.get("from_location_id"), "from_location_id")
    to_location = _optional_id(payload.get("to_location_id"), "to_location_id")
    occurred = _occurred_at(payload.get("occurred_at"))
    if action == "scan_out":
        if from_location is None or to_location is not None:
            raise MovementIntegrityError("scan_out movement payload is malformed")
    elif action == "observed":
        if from_location is not None or to_location is None:
            raise MovementIntegrityError("observed movement payload is malformed")
    elif to_location is None:
        raise MovementIntegrityError(f"{action} movement payload lacks destination")
    return MovementView(
        event_id=event.event_id,
        stream_revision=event.stream_revision,
        entity_uuid=entity_uuid,
        action=action,
        from_location_id=from_location,
        to_location_id=to_location,
        occurred_at=occurred,
        source_type=source,
        source_ref=_optional_text(payload.get("source_ref"), "source_ref", 500),
        note=_optional_text(payload.get("note"), "note", 4000),
        idempotent_replay=idempotent_replay,
    )


def _event_id(entity_uuid: str, logical_key: str) -> str:
    encoded = json.dumps(
        {"entity_uuid": entity_uuid, "logical_key": logical_key},
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return "movement-" + hashlib.sha256(encoded).hexdigest()[:32]


def _projection_key(event_id: str) -> str:
    return "movement-projection-" + hashlib.sha256(event_id.encode("utf-8")).hexdigest()


def _action(value: Any) -> str:
    if not isinstance(value, str):
        raise MovementValidationError("action must be text")
    normalized = value.strip().lower()
    if normalized not in MOVEMENT_ACTIONS:
        raise MovementValidationError(
            "action must be one of " + ", ".join(sorted(MOVEMENT_ACTIONS))
        )
    return normalized


def _source_type(value: Any) -> str:
    if not isinstance(value, str):
        raise MovementValidationError("source_type must be text")
    normalized = value.strip().lower()
    if normalized not in MOVEMENT_SOURCE_TYPES:
        raise MovementValidationError(
            "source_type must be one of " + ", ".join(sorted(MOVEMENT_SOURCE_TYPES))
        )
    return normalized


def _occurred_at(value: Any) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise MovementValidationError("occurred_at must be non-empty trimmed text")
    candidate = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError as exc:
        raise MovementValidationError("occurred_at must be valid ISO 8601") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise MovementValidationError("occurred_at must include an explicit UTC offset")
    return parsed.isoformat()


def _optional_id(value: Any, field: str) -> str | None:
    if value is None:
        return None
    return _text(value, field, 128)


def _text(value: Any, field: str, maximum: int) -> str:
    if not isinstance(value, str):
        raise MovementValidationError(f"{field} must be text")
    normalized = value.strip()
    if not normalized:
        raise MovementValidationError(f"{field} must not be blank")
    if len(normalized) > maximum:
        raise MovementValidationError(f"{field} exceeds maximum length {maximum}")
    return normalized


def _optional_text(value: Any, field: str, maximum: int) -> str | None:
    if value is None:
        return None
    return _text(value, field, maximum)


__all__ = [
    "MOVEMENT_ACTIONS",
    "MOVEMENT_EVENT_TYPE",
    "MOVEMENT_SCHEMA_VERSION",
    "MOVEMENT_SOURCE_TYPES",
    "InventoryMovementService",
    "MovementConflictError",
    "MovementError",
    "MovementIntegrityError",
    "MovementResult",
    "MovementValidationError",
    "MovementView",
]
