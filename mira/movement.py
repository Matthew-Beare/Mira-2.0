"""Replay-safe explicit inventory observation and movement history.

This module records explicit physical observations as canonical append-only events and
projects the resulting observed location onto the existing inventory_state resource.
The event append intentionally happens before the projection write. Both writes have
stable idempotency identities so an interrupted operation can be replayed without
creating duplicate history or an extra inventory-state revision.

The current Personal Google path is single-writer. This module therefore does not claim
a distributed transaction across the event and resource writes. If unrelated concurrent
mutation violates that boundary between the two writes, recovery fails closed rather
than overwriting newer canonical state.

STORE-001 keeps provider event types generic (created/updated). Movement semantics are
therefore identified by typed payload material instead of adding a provider-specific
schema event type. Identifier recognition, barcode/QR/NFC/BLE capture, container
propagation, intended-location changes, par/grocery behavior and Android client behavior
are outside this module.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import hashlib
from typing import Any

from .inventory_location import (
    INVENTORY_STATE_RESOURCE_TYPE,
    INVENTORY_STATE_SCHEMA_VERSION,
    InventoryLocationError,
    InventoryLocationService,
    InventoryStateView,
)
from .structured_state import (
    EventRecord,
    IdempotencyConflictError,
    IdentityConflictError,
    ResourceRecord,
    RevisionConflictError,
    StructuredStateAdapter,
    StructuredStateError,
    ValidationError as StoreValidationError,
)


MOVEMENT_EVENT_TYPE = "updated"
MOVEMENT_EVENT_KIND = "inventory_observation"
MOVEMENT_SCHEMA_VERSION = 1


class MovementError(Exception):
    """Base class for explicit inventory movement/observation failures."""


class MovementValidationError(MovementError):
    """Raised when requested movement material is malformed or references invalid state."""


class MovementConflictError(MovementError):
    """Raised when replay, revision, or prior-state material conflicts with canonical truth."""


class MovementIntegrityError(MovementError):
    """Raised when persisted movement history and projected state cannot reconcile."""


@dataclass(frozen=True)
class MovementEventView:
    event_id: str
    entity_uuid: str
    stream_revision: int
    observed_location_id: str
    observed_at: str
    source: str
    note: str | None
    prior_inventory_revision: int
    prior_observed_location_id: str | None
    prior_observed_at: str | None
    prior_intended_location_id: str | None
    prior_inventory_note: str | None
    resulting_inventory_revision: int
    idempotent_replay: bool = False


@dataclass(frozen=True)
class MovementResult:
    event: MovementEventView
    inventory_state: InventoryStateView
    current_inventory_state: InventoryStateView
    idempotent_replay: bool
    recovered_projection: bool


_UNSET = object()


class MovementService:
    """Record explicit observations and maintain a replay-safe observed-state projection."""

    def __init__(
        self,
        adapter: StructuredStateAdapter,
        *,
        inventory_service: InventoryLocationService | None = None,
    ) -> None:
        self._adapter = adapter
        self._inventory = inventory_service or InventoryLocationService(adapter)

    def record_observation(
        self,
        entity_uuid: str,
        *,
        location_id: str,
        observed_at: str,
        source: str,
        event_id: str,
        idempotency_key: str,
        expected_inventory_revision: int,
        expected_prior_observed_location_id: str | None | object = _UNSET,
        expected_prior_observed_at: str | None | object = _UNSET,
        note: str | None = None,
    ) -> MovementResult:
        """Record one explicit physical observation and project latest observed state.

        ``event_id`` and ``idempotency_key`` identify the logical operation independently
        from the asset UUID. Exact replay uses the persisted event material, allowing a
        prior event-first / projection-second interruption to converge safely.
        """

        asset_id = _text(entity_uuid, "entity_uuid", 128)
        destination = _text(location_id, "location_id", 128)
        timestamp = _timestamp(observed_at, "observed_at")
        source_value = _text(source, "source", 128)
        movement_id = _text(event_id, "event_id", 128)
        replay_key = _text(idempotency_key, "idempotency_key", 128)
        expected_revision = _nonnegative_int(
            expected_inventory_revision, "expected_inventory_revision"
        )
        normalized_note = _optional_text(note, "note", 4000)

        try:
            current = self._inventory.get_inventory_state(asset_id)
            self._inventory.get_location(destination)
        except InventoryLocationError as exc:
            raise MovementValidationError(str(exc)) from exc

        prior_location_expectation = _normalize_optional_expectation(
            expected_prior_observed_location_id,
            "expected_prior_observed_location_id",
            timestamp=False,
        )
        prior_time_expectation = _normalize_optional_expectation(
            expected_prior_observed_at,
            "expected_prior_observed_at",
            timestamp=True,
        )

        existing = self._find_event(asset_id, movement_id)
        if existing is not None:
            view = _event_view(existing)
            self._assert_replay_material(
                view,
                destination=destination,
                observed_at=timestamp,
                source=source_value,
                note=normalized_note,
                expected_inventory_revision=expected_revision,
                expected_prior_location=prior_location_expectation,
                expected_prior_time=prior_time_expectation,
            )
            try:
                replayed = self._adapter.append_event(
                    INVENTORY_STATE_RESOURCE_TYPE,
                    asset_id,
                    MOVEMENT_EVENT_TYPE,
                    movement_id,
                    existing.payload,
                    idempotency_key=replay_key,
                    expected_stream_revision=None,
                )
            except (
                IdempotencyConflictError,
                IdentityConflictError,
                RevisionConflictError,
            ) as exc:
                raise MovementConflictError(str(exc)) from exc
            except StoreValidationError as exc:
                raise MovementValidationError(str(exc)) from exc
            except StructuredStateError as exc:
                raise MovementIntegrityError(str(exc)) from exc
            if not replayed.idempotent_replay:
                raise MovementIntegrityError(
                    "existing movement event did not resolve as an idempotent replay"
                )
            return self._project_event(
                _event_view(replayed.event, idempotent_replay=True),
                event_existed=True,
            )

        self._assert_new_preconditions(
            current,
            expected_inventory_revision=expected_revision,
            expected_prior_location=prior_location_expectation,
            expected_prior_time=prior_time_expectation,
            observed_at=timestamp,
        )

        payload = {
            "schema_version": MOVEMENT_SCHEMA_VERSION,
            "event_kind": MOVEMENT_EVENT_KIND,
            "event_id": movement_id,
            "entity_uuid": asset_id,
            "observed_location_id": destination,
            "observed_at": timestamp,
            "source": source_value,
            "note": normalized_note,
            "prior_inventory_revision": current.revision,
            "prior_observed_location_id": current.observed_location_id,
            "prior_observed_at": current.observed_at,
            "prior_intended_location_id": current.intended_location_id,
            "prior_inventory_note": current.note,
            "resulting_inventory_revision": current.revision + 1,
        }
        try:
            appended = self._adapter.append_event(
                INVENTORY_STATE_RESOURCE_TYPE,
                asset_id,
                MOVEMENT_EVENT_TYPE,
                movement_id,
                payload,
                idempotency_key=replay_key,
                expected_stream_revision=None,
            )
        except (
            IdempotencyConflictError,
            IdentityConflictError,
            RevisionConflictError,
        ) as exc:
            raise MovementConflictError(str(exc)) from exc
        except StoreValidationError as exc:
            raise MovementValidationError(str(exc)) from exc
        except StructuredStateError as exc:
            raise MovementIntegrityError(str(exc)) from exc

        return self._project_event(
            _event_view(appended.event, idempotent_replay=appended.idempotent_replay),
            event_existed=appended.idempotent_replay,
        )

    def history(
        self,
        entity_uuid: str,
        *,
        after_revision: int = 0,
        limit: int = 100,
    ) -> tuple[MovementEventView, ...]:
        asset_id = _text(entity_uuid, "entity_uuid", 128)
        after = _nonnegative_int(after_revision, "after_revision")
        bounded_limit = _limit(limit)
        try:
            self._inventory.get_inventory_state(asset_id)
            raw = self._adapter.events_for(
                INVENTORY_STATE_RESOURCE_TYPE,
                asset_id,
                after_revision=after,
                limit=1000,
            )
        except InventoryLocationError as exc:
            raise MovementValidationError(str(exc)) from exc
        except StoreValidationError as exc:
            raise MovementValidationError(str(exc)) from exc
        except StructuredStateError as exc:
            raise MovementIntegrityError(str(exc)) from exc
        rows = [
            _event_view(event)
            for event in raw
            if event.event_type == MOVEMENT_EVENT_TYPE
            and event.payload.get("event_kind") == MOVEMENT_EVENT_KIND
        ]
        rows.sort(key=lambda item: item.stream_revision)
        return tuple(rows[:bounded_limit])

    def _find_event(self, entity_uuid: str, event_id: str) -> EventRecord | None:
        try:
            rows = self._adapter.events_for(
                INVENTORY_STATE_RESOURCE_TYPE,
                entity_uuid,
                after_revision=0,
                limit=1000,
            )
        except StoreValidationError as exc:
            raise MovementValidationError(str(exc)) from exc
        except StructuredStateError as exc:
            raise MovementIntegrityError(str(exc)) from exc
        matches = [event for event in rows if event.event_id == event_id]
        if len(matches) > 1:
            raise MovementIntegrityError("movement stream contains duplicate event identity")
        return matches[0] if matches else None

    def _assert_new_preconditions(
        self,
        current: InventoryStateView,
        *,
        expected_inventory_revision: int,
        expected_prior_location: str | None | object,
        expected_prior_time: str | None | object,
        observed_at: str,
    ) -> None:
        if current.revision != expected_inventory_revision:
            raise MovementConflictError(
                f"expected inventory revision {expected_inventory_revision}, "
                f"current revision is {current.revision}"
            )
        if (
            expected_prior_location is not _UNSET
            and current.observed_location_id != expected_prior_location
        ):
            raise MovementConflictError(
                "claimed prior observed location does not match canonical inventory state"
            )
        if expected_prior_time is not _UNSET and current.observed_at != expected_prior_time:
            raise MovementConflictError(
                "claimed prior observed timestamp does not match canonical inventory state"
            )
        if current.observed_at is not None:
            prior = datetime.fromisoformat(current.observed_at)
            proposed = datetime.fromisoformat(observed_at)
            if proposed <= prior:
                raise MovementConflictError(
                    "new observation time must be later than the latest canonical observation"
                )

    def _assert_replay_material(
        self,
        event: MovementEventView,
        *,
        destination: str,
        observed_at: str,
        source: str,
        note: str | None,
        expected_inventory_revision: int,
        expected_prior_location: str | None | object,
        expected_prior_time: str | None | object,
    ) -> None:
        if (
            event.observed_location_id != destination
            or event.observed_at != observed_at
            or event.source != source
            or event.note != note
            or event.prior_inventory_revision != expected_inventory_revision
        ):
            raise MovementConflictError(
                "movement event identity was already used for different material input"
            )
        if (
            expected_prior_location is not _UNSET
            and event.prior_observed_location_id != expected_prior_location
        ):
            raise MovementConflictError(
                "replayed prior observed location conflicts with persisted movement event"
            )
        if (
            expected_prior_time is not _UNSET
            and event.prior_observed_at != expected_prior_time
        ):
            raise MovementConflictError(
                "replayed prior observed timestamp conflicts with persisted movement event"
            )

    def _project_event(
        self,
        event: MovementEventView,
        *,
        event_existed: bool,
    ) -> MovementResult:
        payload = {
            "schema_version": INVENTORY_STATE_SCHEMA_VERSION,
            "entity_uuid": event.entity_uuid,
            "participation_state": "tracked",
            "intended_location_id": event.prior_intended_location_id,
            "observed_location_id": event.observed_location_id,
            "observed_at": event.observed_at,
            "note": event.prior_inventory_note,
        }
        state_key = _projection_key(event.event_id)
        try:
            projected = self._adapter.upsert(
                INVENTORY_STATE_RESOURCE_TYPE,
                event.entity_uuid,
                payload,
                idempotency_key=state_key,
                expected_revision=event.prior_inventory_revision,
            )
        except (
            RevisionConflictError,
            IdempotencyConflictError,
            IdentityConflictError,
        ) as exc:
            raise MovementConflictError(
                "movement event exists but observed-state projection conflicts with canonical state: "
                + str(exc)
            ) from exc
        except StoreValidationError as exc:
            raise MovementValidationError(str(exc)) from exc
        except StructuredStateError as exc:
            raise MovementIntegrityError(str(exc)) from exc

        projected_view = _inventory_view(
            projected.record,
            idempotent_replay=projected.idempotent_replay,
        )
        if (
            projected_view.revision != event.resulting_inventory_revision
            or projected_view.intended_location_id != event.prior_intended_location_id
            or projected_view.observed_location_id != event.observed_location_id
            or projected_view.observed_at != event.observed_at
            or projected_view.note != event.prior_inventory_note
        ):
            raise MovementIntegrityError(
                "persisted movement projection does not match movement event material"
            )

        try:
            current = self._inventory.get_inventory_state(event.entity_uuid)
        except InventoryLocationError as exc:
            raise MovementIntegrityError(str(exc)) from exc
        if current.revision < projected_view.revision:
            raise MovementIntegrityError(
                "movement projection readback is older than the persisted projection result"
            )
        if current.revision == projected_view.revision and not _same_inventory_state(
            current, projected_view
        ):
            raise MovementIntegrityError(
                "movement projection exact readback differs at the same revision"
            )
        if current.revision > projected_view.revision and not projected.idempotent_replay:
            raise MovementIntegrityError(
                "canonical inventory advanced unexpectedly during movement projection"
            )

        recovered = event_existed and not projected.idempotent_replay
        return MovementResult(
            event=event,
            inventory_state=projected_view,
            current_inventory_state=current,
            idempotent_replay=event.idempotent_replay and projected.idempotent_replay,
            recovered_projection=recovered,
        )


def _event_view(event: EventRecord, *, idempotent_replay: bool = False) -> MovementEventView:
    if event.event_type != MOVEMENT_EVENT_TYPE:
        raise MovementIntegrityError("event is not canonical inventory movement history")
    payload = dict(event.payload)
    if payload.get("event_kind") != MOVEMENT_EVENT_KIND:
        raise MovementIntegrityError("event payload is not an inventory observation")
    if payload.get("schema_version") != MOVEMENT_SCHEMA_VERSION:
        raise MovementIntegrityError("unsupported movement event schema version")
    event_id = _text(payload.get("event_id"), "event_id", 128)
    entity_uuid = _text(payload.get("entity_uuid"), "entity_uuid", 128)
    if event_id != event.event_id:
        raise MovementIntegrityError("movement event_id does not match Event identity")
    if entity_uuid != event.stream_id or event.stream_type != INVENTORY_STATE_RESOURCE_TYPE:
        raise MovementIntegrityError("movement event stream does not match canonical asset identity")
    prior_revision = _nonnegative_int(
        payload.get("prior_inventory_revision"), "prior_inventory_revision"
    )
    resulting_revision = _positive_int(
        payload.get("resulting_inventory_revision"), "resulting_inventory_revision"
    )
    if resulting_revision != prior_revision + 1:
        raise MovementIntegrityError(
            "movement resulting inventory revision must follow prior revision by one"
        )
    prior_observed_location = _optional_text(
        payload.get("prior_observed_location_id"), "prior_observed_location_id", 128
    )
    raw_prior_time = payload.get("prior_observed_at")
    if prior_observed_location is None:
        if raw_prior_time is not None:
            raise MovementIntegrityError(
                "movement prior observed timestamp requires prior observed location"
            )
        prior_time = None
    else:
        prior_time = _timestamp(raw_prior_time, "prior_observed_at")
    return MovementEventView(
        event_id=event_id,
        entity_uuid=entity_uuid,
        stream_revision=_positive_int(event.stream_revision, "stream_revision"),
        observed_location_id=_text(
            payload.get("observed_location_id"), "observed_location_id", 128
        ),
        observed_at=_timestamp(payload.get("observed_at"), "observed_at"),
        source=_text(payload.get("source"), "source", 128),
        note=_optional_text(payload.get("note"), "note", 4000),
        prior_inventory_revision=prior_revision,
        prior_observed_location_id=prior_observed_location,
        prior_observed_at=prior_time,
        prior_intended_location_id=_optional_text(
            payload.get("prior_intended_location_id"), "prior_intended_location_id", 128
        ),
        prior_inventory_note=_optional_text(
            payload.get("prior_inventory_note"), "prior_inventory_note", 4000
        ),
        resulting_inventory_revision=resulting_revision,
        idempotent_replay=idempotent_replay,
    )


def _inventory_view(
    record: ResourceRecord,
    *,
    idempotent_replay: bool,
) -> InventoryStateView:
    if record.resource_type != INVENTORY_STATE_RESOURCE_TYPE:
        raise MovementIntegrityError("movement projection returned wrong Resource type")
    payload = dict(record.payload)
    if payload.get("schema_version") != INVENTORY_STATE_SCHEMA_VERSION:
        raise MovementIntegrityError("movement projection returned unsupported inventory schema")
    if payload.get("entity_uuid") != record.resource_id:
        raise MovementIntegrityError("movement projection changed canonical asset identity")
    if payload.get("participation_state") != "tracked":
        raise MovementIntegrityError("movement projection changed inventory participation")
    observed_location = _optional_text(
        payload.get("observed_location_id"), "observed_location_id", 128
    )
    raw_time = payload.get("observed_at")
    if observed_location is None or raw_time is None:
        raise MovementIntegrityError("movement projection must contain an observed location/time")
    return InventoryStateView(
        entity_uuid=_text(payload.get("entity_uuid"), "entity_uuid", 128),
        revision=_positive_int(record.revision, "revision"),
        participation_state="tracked",
        intended_location_id=_optional_text(
            payload.get("intended_location_id"), "intended_location_id", 128
        ),
        observed_location_id=observed_location,
        observed_at=_timestamp(raw_time, "observed_at"),
        note=_optional_text(payload.get("note"), "note", 4000),
        idempotent_replay=idempotent_replay,
    )


def _same_inventory_state(left: InventoryStateView, right: InventoryStateView) -> bool:
    return (
        left.entity_uuid == right.entity_uuid
        and left.revision == right.revision
        and left.participation_state == right.participation_state
        and left.intended_location_id == right.intended_location_id
        and left.observed_location_id == right.observed_location_id
        and left.observed_at == right.observed_at
        and left.note == right.note
    )


def _projection_key(event_id: str) -> str:
    digest = hashlib.sha256(event_id.encode("utf-8")).hexdigest()
    return f"movement-state-{digest[:40]}"


def _normalize_optional_expectation(
    value: str | None | object,
    field: str,
    *,
    timestamp: bool,
) -> str | None | object:
    if value is _UNSET or value is None:
        return value
    return _timestamp(value, field) if timestamp else _text(value, field, 128)


def _timestamp(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise MovementValidationError(
            f"{field} must be a non-empty offset-aware ISO-8601 timestamp"
        )
    text = value.strip()
    parse_text = text[:-1] + "+00:00" if text.endswith("Z") else text
    try:
        parsed = datetime.fromisoformat(parse_text)
    except ValueError as exc:
        raise MovementValidationError(f"{field} must be valid ISO-8601") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise MovementValidationError(f"{field} must include an explicit UTC offset")
    return parsed.isoformat()


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


def _nonnegative_int(value: Any, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise MovementValidationError(f"{field} must be a non-negative integer")
    return value


def _positive_int(value: Any, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise MovementIntegrityError(f"{field} must be a positive integer")
    return value


def _limit(value: Any) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or not 1 <= value <= 1000:
        raise MovementValidationError("limit must be an integer from 1 through 1000")
    return value


__all__ = [
    "MOVEMENT_EVENT_KIND",
    "MOVEMENT_EVENT_TYPE",
    "MOVEMENT_SCHEMA_VERSION",
    "MovementConflictError",
    "MovementError",
    "MovementEventView",
    "MovementIntegrityError",
    "MovementResult",
    "MovementService",
    "MovementValidationError",
]
