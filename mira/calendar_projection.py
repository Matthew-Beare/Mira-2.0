"""Provider-neutral source-linked Calendar projection semantics for MIRA.

The core deliberately does not call Google, Microsoft, Apple, or any other real
Calendar provider. It defines the canonical projection identity, provider-adapter
contract, replay/conflict rules, and exact readback boundary that provider-specific
adapters must satisfy later.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
import hashlib
import json
import re
from typing import Any, Mapping, Protocol, Sequence
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from .structured_state import (
    IdempotencyConflictError,
    NotFoundError,
    ResourceRecord,
    RevisionConflictError,
    StructuredStateAdapter,
    StructuredStateError,
    ValidationError as StoreValidationError,
)


CALENDAR_PROJECTION_RESOURCE_TYPE = "calendar_projection"
CALENDAR_PROJECTION_SCHEMA_VERSION = 2
_TOKEN_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_WS_RE = re.compile(r"\s+")


class CalendarProjectionError(Exception):
    """Base class for Calendar projection failures."""


class CalendarProjectionValidationError(CalendarProjectionError):
    """Raised when requested or persisted projection material is malformed."""


class CalendarProjectionConflictError(CalendarProjectionError):
    """Raised when source/provider/canonical concurrency truth conflicts."""


class CalendarProjectionCapabilityError(CalendarProjectionError):
    """Raised when a selected provider adapter cannot satisfy the core contract."""


class CalendarProjectionReadbackError(CalendarProjectionError):
    """Raised when independent provider or canonical readback does not match."""


class CalendarProjectionIntegrityError(CalendarProjectionError):
    """Raised when persisted canonical projection state is internally inconsistent."""


class CalendarProviderError(Exception):
    """Base class for provider-adapter contract failures."""


class CalendarProviderValidationError(CalendarProviderError):
    """Raised when provider-adapter input is malformed."""


class CalendarProviderNotFoundError(CalendarProviderError):
    """Raised when an exact provider event is missing."""


class CalendarProviderConflictError(CalendarProviderError):
    """Raised when provider version/projection identity conflicts."""


class CalendarProviderIdempotencyConflictError(CalendarProviderError):
    """Raised when one provider idempotency key is reused for different material."""


@dataclass(frozen=True)
class CalendarEventMaterial:
    title: str
    start_at: str
    end_at: str
    timezone: str
    location: str | None = None
    description: str | None = None

    def payload(self) -> dict[str, str | None]:
        return {
            "title": self.title,
            "start_at": self.start_at,
            "end_at": self.end_at,
            "timezone": self.timezone,
            "location": self.location,
            "description": self.description,
        }


@dataclass(frozen=True)
class CalendarProjectionRequest:
    source_resource_type: str
    source_resource_id: str
    source_revision: int
    provider_lane: str
    calendar_ref: str
    event: CalendarEventMaterial


@dataclass(frozen=True)
class CalendarProviderCapability:
    provider_lane: str
    writable: bool
    exact_readback: bool
    stable_projection_key: bool


@dataclass(frozen=True)
class ProviderCalendarEvent:
    provider_lane: str
    calendar_ref: str
    event_id: str
    provider_version: str
    projection_key: str
    event: CalendarEventMaterial


@dataclass(frozen=True)
class ProviderCalendarMutationResult:
    event: ProviderCalendarEvent
    idempotent_replay: bool


class CalendarProjectionAdapter(Protocol):
    """Provider adapter boundary required by the projection core."""

    def capability(self) -> CalendarProviderCapability: ...

    def upsert_event(
        self,
        calendar_ref: str,
        projection_key: str,
        event: CalendarEventMaterial,
        *,
        idempotency_key: str,
        expected_provider_version: str | None,
    ) -> ProviderCalendarMutationResult: ...

    def read_event(self, calendar_ref: str, event_id: str) -> ProviderCalendarEvent: ...


@dataclass(frozen=True)
class CalendarProjectionView:
    projection_id: str
    revision: int
    source_resource_type: str
    source_resource_id: str
    source_revision: int
    provider_lane: str
    calendar_ref: str
    provider_event_id: str
    provider_version: str
    event: CalendarEventMaterial
    desired_sha256: str
    readback_sha256: str
    status: str


@dataclass(frozen=True)
class CalendarProjectionResult:
    status: str
    projection: CalendarProjectionView
    provider_idempotent_replay: bool = False


class CalendarProjectionService:
    """Project normalized source truth through a verified Calendar adapter boundary."""

    def __init__(
        self,
        state: StructuredStateAdapter,
        calendar: CalendarProjectionAdapter,
        *,
        projection_resource_type: str = CALENDAR_PROJECTION_RESOURCE_TYPE,
    ) -> None:
        self._state = state
        self._calendar = calendar
        self._projection_type = _token(
            projection_resource_type, "projection_resource_type"
        )

    def project(
        self,
        request: CalendarProjectionRequest,
        *,
        idempotency_key: str,
    ) -> CalendarProjectionResult:
        normalized = _request(request)
        request_key = _token(idempotency_key, "idempotency_key")
        capability = _capability(self._calendar.capability())
        if capability.provider_lane != normalized.provider_lane:
            raise CalendarProjectionCapabilityError(
                "selected adapter provider_lane does not match projection request"
            )
        if not capability.writable:
            raise CalendarProjectionCapabilityError(
                "selected Calendar adapter does not provide write capability"
            )
        if not capability.exact_readback:
            raise CalendarProjectionCapabilityError(
                "selected Calendar adapter cannot provide exact event readback"
            )
        if not capability.stable_projection_key:
            raise CalendarProjectionCapabilityError(
                "selected Calendar adapter cannot guarantee stable projection-key identity"
            )

        projection_id = _projection_id(normalized)
        desired_sha256 = _event_fingerprint(normalized.event)
        current = self._maybe_projection(projection_id)
        if current is not None:
            _assert_projection_target(current, normalized)
            if normalized.source_revision < current.source_revision:
                raise CalendarProjectionConflictError(
                    "source revision is older than the canonical projection revision"
                )
            if normalized.source_revision == current.source_revision:
                if desired_sha256 != current.desired_sha256:
                    raise CalendarProjectionConflictError(
                        "the same source revision cannot project different event material"
                    )
                provider = self._read_provider(current.calendar_ref, current.provider_event_id)
                _verify_provider_event(
                    provider,
                    request=normalized,
                    projection_key=projection_id,
                    expected_event_id=current.provider_event_id,
                    expected_provider_version=current.provider_version,
                )
                if _event_fingerprint(provider.event) != current.readback_sha256:
                    raise CalendarProjectionReadbackError(
                        "provider event material drifted from canonical verified readback"
                    )
                return CalendarProjectionResult(
                    status="unchanged",
                    projection=current,
                    provider_idempotent_replay=True,
                )

        expected_provider_version = (
            None if current is None else current.provider_version
        )
        provider_key = _derived_token("calprov", request_key)
        try:
            mutation = self._calendar.upsert_event(
                normalized.calendar_ref,
                projection_id,
                normalized.event,
                idempotency_key=provider_key,
                expected_provider_version=expected_provider_version,
            )
        except CalendarProviderIdempotencyConflictError as exc:
            raise CalendarProjectionConflictError(
                "provider idempotency key was reused for different material"
            ) from exc
        except CalendarProviderConflictError as exc:
            raise CalendarProjectionConflictError(str(exc)) from exc
        except CalendarProviderValidationError as exc:
            raise CalendarProjectionValidationError(str(exc)) from exc
        except CalendarProviderError as exc:
            raise CalendarProjectionReadbackError(str(exc)) from exc

        provider = self._read_provider(
            normalized.calendar_ref, mutation.event.event_id
        )
        _verify_provider_event(
            provider,
            request=normalized,
            projection_key=projection_id,
            expected_event_id=mutation.event.event_id,
            expected_provider_version=mutation.event.provider_version,
        )
        readback_sha256 = _event_fingerprint(provider.event)
        if readback_sha256 != desired_sha256:
            raise CalendarProjectionReadbackError(
                "provider readback does not match desired event material"
            )

        payload = _projection_payload(
            projection_id=projection_id,
            request=normalized,
            provider=provider,
            desired_sha256=desired_sha256,
            readback_sha256=readback_sha256,
        )
        expected_revision = 0 if current is None else current.revision
        state_key = _derived_token("calstate", request_key)
        try:
            mutation_result = self._state.upsert(
                self._projection_type,
                projection_id,
                payload,
                idempotency_key=state_key,
                expected_revision=expected_revision,
            )
        except (RevisionConflictError, IdempotencyConflictError) as exc:
            raise CalendarProjectionConflictError(str(exc)) from exc
        except StoreValidationError as exc:
            raise CalendarProjectionValidationError(str(exc)) from exc
        except StructuredStateError as exc:
            raise CalendarProjectionIntegrityError(str(exc)) from exc

        stored = self._read_projection_record(projection_id)
        if stored.payload != mutation_result.record.payload:
            raise CalendarProjectionReadbackError(
                "canonical projection readback differs from persisted mutation result"
            )
        view = _projection_view(stored)
        if view.desired_sha256 != desired_sha256 or view.readback_sha256 != readback_sha256:
            raise CalendarProjectionReadbackError(
                "canonical projection fingerprints do not match verified provider material"
            )
        return CalendarProjectionResult(
            status="created" if current is None else "updated",
            projection=view,
            provider_idempotent_replay=mutation.idempotent_replay,
        )

    def get_projection(self, projection_id: str) -> CalendarProjectionView:
        normalized_id = _token(projection_id, "projection_id")
        return _projection_view(self._read_projection_record(normalized_id))

    def projections_for_source(
        self,
        source_resource_type: str,
        source_resource_id: str,
        *,
        limit: int = 100,
    ) -> tuple[CalendarProjectionView, ...]:
        source_type = _token(source_resource_type, "source_resource_type")
        source_id = _token(source_resource_id, "source_resource_id")
        try:
            records = self._state.query(
                self._projection_type,
                filters={
                    "source_resource_type": source_type,
                    "source_resource_id": source_id,
                },
                limit=limit,
            )
        except StoreValidationError as exc:
            raise CalendarProjectionValidationError(str(exc)) from exc
        except StructuredStateError as exc:
            raise CalendarProjectionIntegrityError(str(exc)) from exc
        return tuple(_projection_view(record) for record in records)

    def _maybe_projection(self, projection_id: str) -> CalendarProjectionView | None:
        try:
            return self.get_projection(projection_id)
        except CalendarProjectionValidationError as exc:
            if "does not exist" in str(exc):
                return None
            raise

    def _read_projection_record(self, projection_id: str) -> ResourceRecord:
        try:
            return self._state.get(self._projection_type, projection_id)
        except NotFoundError as exc:
            raise CalendarProjectionValidationError(str(exc)) from exc
        except StoreValidationError as exc:
            raise CalendarProjectionValidationError(str(exc)) from exc
        except StructuredStateError as exc:
            raise CalendarProjectionIntegrityError(str(exc)) from exc

    def _read_provider(self, calendar_ref: str, event_id: str) -> ProviderCalendarEvent:
        try:
            return self._calendar.read_event(calendar_ref, event_id)
        except CalendarProviderNotFoundError as exc:
            raise CalendarProjectionReadbackError(
                "canonical projection references a missing provider event"
            ) from exc
        except CalendarProviderValidationError as exc:
            raise CalendarProjectionValidationError(str(exc)) from exc
        except CalendarProviderError as exc:
            raise CalendarProjectionReadbackError(str(exc)) from exc


class InMemoryCalendarProjectionAdapter:
    """Deterministic synthetic Calendar adapter for direct contract proof."""

    def __init__(
        self,
        provider_lane: str,
        *,
        writable: bool = True,
        exact_readback: bool = True,
        stable_projection_key: bool = True,
    ) -> None:
        self._provider_lane = _token(provider_lane, "provider_lane")
        self._capability = CalendarProviderCapability(
            provider_lane=self._provider_lane,
            writable=bool(writable),
            exact_readback=bool(exact_readback),
            stable_projection_key=bool(stable_projection_key),
        )
        self._events: dict[tuple[str, str], ProviderCalendarEvent] = {}
        self._projection_index: dict[tuple[str, str], str] = {}
        self._idempotency: dict[str, tuple[str, ProviderCalendarEvent]] = {}
        self.write_count = 0

    def capability(self) -> CalendarProviderCapability:
        return self._capability

    def upsert_event(
        self,
        calendar_ref: str,
        projection_key: str,
        event: CalendarEventMaterial,
        *,
        idempotency_key: str,
        expected_provider_version: str | None,
    ) -> ProviderCalendarMutationResult:
        calendar = _text(calendar_ref, "calendar_ref", 500)
        projection = _token(projection_key, "projection_key")
        normalized_event = _event_material(event)
        key = _token(idempotency_key, "idempotency_key")
        _expected_version(expected_provider_version)
        fingerprint = _fingerprint(
            {
                "calendar_ref": calendar,
                "projection_key": projection,
                "event": normalized_event.payload(),
                "expected_provider_version": expected_provider_version,
            }
        )
        previous = self._idempotency.get(key)
        if previous is not None:
            previous_fingerprint, previous_event = previous
            if previous_fingerprint != fingerprint:
                raise CalendarProviderIdempotencyConflictError(
                    "provider idempotency key was reused for different material"
                )
            return ProviderCalendarMutationResult(
                event=deepcopy(previous_event), idempotent_replay=True
            )

        projection_index = (calendar, projection)
        existing_event_id = self._projection_index.get(projection_index)
        existing = (
            None
            if existing_event_id is None
            else self._events.get((calendar, existing_event_id))
        )
        if existing is None:
            if expected_provider_version is not None:
                raise CalendarProviderConflictError(
                    "provider event is missing for the expected provider version"
                )
            event_id = _derived_token(
                "event", f"{self._provider_lane}|{calendar}|{projection}"
            )
            persisted = ProviderCalendarEvent(
                provider_lane=self._provider_lane,
                calendar_ref=calendar,
                event_id=event_id,
                provider_version="memory:1",
                projection_key=projection,
                event=normalized_event,
            )
            self._events[(calendar, event_id)] = persisted
            self._projection_index[projection_index] = event_id
            self.write_count += 1
        else:
            if expected_provider_version is None:
                if existing.event != normalized_event:
                    raise CalendarProviderConflictError(
                        "stable projection key already exists with different material"
                    )
                persisted = existing
            else:
                if expected_provider_version != existing.provider_version:
                    raise CalendarProviderConflictError(
                        "provider version precondition is stale"
                    )
                if existing.event == normalized_event:
                    persisted = existing
                else:
                    persisted = ProviderCalendarEvent(
                        provider_lane=self._provider_lane,
                        calendar_ref=calendar,
                        event_id=existing.event_id,
                        provider_version=_next_memory_version(existing.provider_version),
                        projection_key=projection,
                        event=normalized_event,
                    )
                    self._events[(calendar, existing.event_id)] = persisted
                    self.write_count += 1
        self._idempotency[key] = (fingerprint, deepcopy(persisted))
        return ProviderCalendarMutationResult(
            event=deepcopy(persisted), idempotent_replay=False
        )

    def read_event(self, calendar_ref: str, event_id: str) -> ProviderCalendarEvent:
        calendar = _text(calendar_ref, "calendar_ref", 500)
        normalized_id = _token(event_id, "event_id")
        try:
            return deepcopy(self._events[(calendar, normalized_id)])
        except KeyError as exc:
            raise CalendarProviderNotFoundError(
                f"provider event does not exist: {calendar}:{normalized_id}"
            ) from exc

    def replace_event_for_test(
        self,
        calendar_ref: str,
        event_id: str,
        event: CalendarEventMaterial,
        *,
        bump_version: bool = True,
    ) -> ProviderCalendarEvent:
        """Synthetic-only helper used to prove independent drift detection."""
        current = self.read_event(calendar_ref, event_id)
        replacement = ProviderCalendarEvent(
            provider_lane=current.provider_lane,
            calendar_ref=current.calendar_ref,
            event_id=current.event_id,
            provider_version=(
                _next_memory_version(current.provider_version)
                if bump_version
                else current.provider_version
            ),
            projection_key=current.projection_key,
            event=_event_material(event),
        )
        self._events[(current.calendar_ref, current.event_id)] = replacement
        return deepcopy(replacement)

    def delete_event_for_test(self, calendar_ref: str, event_id: str) -> None:
        """Synthetic-only helper used to prove missing-provider-event behavior."""
        current = self.read_event(calendar_ref, event_id)
        self._events.pop((current.calendar_ref, current.event_id), None)


def _request(value: CalendarProjectionRequest) -> CalendarProjectionRequest:
    if not isinstance(value, CalendarProjectionRequest):
        raise CalendarProjectionValidationError(
            "request must be a CalendarProjectionRequest"
        )
    source_type = _token(value.source_resource_type, "source_resource_type")
    source_id = _token(value.source_resource_id, "source_resource_id")
    source_revision = _positive_int(value.source_revision, "source_revision")
    provider_lane = _token(value.provider_lane, "provider_lane")
    calendar_ref = _text(value.calendar_ref, "calendar_ref", 500)
    event = _event_material(value.event)
    return CalendarProjectionRequest(
        source_resource_type=source_type,
        source_resource_id=source_id,
        source_revision=source_revision,
        provider_lane=provider_lane,
        calendar_ref=calendar_ref,
        event=event,
    )


def _event_material(value: CalendarEventMaterial) -> CalendarEventMaterial:
    if not isinstance(value, CalendarEventMaterial):
        raise CalendarProjectionValidationError(
            "event must be CalendarEventMaterial"
        )
    title = _text(value.title, "event.title", 500)
    timezone_name = _text(value.timezone, "event.timezone", 128)
    try:
        zone = ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError as exc:
        raise CalendarProjectionValidationError(
            f"event.timezone is not a known IANA timezone: {timezone_name}"
        ) from exc
    start = _aware_datetime(value.start_at, "event.start_at")
    end = _aware_datetime(value.end_at, "event.end_at")
    if end <= start:
        raise CalendarProjectionValidationError(
            "event.end_at must be later than event.start_at"
        )
    if start.astimezone(zone).utcoffset() != start.utcoffset():
        raise CalendarProjectionValidationError(
            "event.start_at offset does not match event.timezone"
        )
    if end.astimezone(zone).utcoffset() != end.utcoffset():
        raise CalendarProjectionValidationError(
            "event.end_at offset does not match event.timezone"
        )
    return CalendarEventMaterial(
        title=title,
        start_at=start.isoformat(),
        end_at=end.isoformat(),
        timezone=timezone_name,
        location=_optional_text(value.location, "event.location", 1000),
        description=_optional_text(value.description, "event.description", 4000),
    )


def _capability(value: CalendarProviderCapability) -> CalendarProviderCapability:
    if not isinstance(value, CalendarProviderCapability):
        raise CalendarProjectionCapabilityError(
            "Calendar adapter capability result is malformed"
        )
    try:
        lane = _token(value.provider_lane, "capability.provider_lane")
    except CalendarProjectionValidationError as exc:
        raise CalendarProjectionCapabilityError(str(exc)) from exc
    if not all(
        isinstance(flag, bool)
        for flag in (value.writable, value.exact_readback, value.stable_projection_key)
    ):
        raise CalendarProjectionCapabilityError(
            "Calendar adapter capability flags must be booleans"
        )
    return CalendarProviderCapability(
        provider_lane=lane,
        writable=value.writable,
        exact_readback=value.exact_readback,
        stable_projection_key=value.stable_projection_key,
    )


def _projection_id(request: CalendarProjectionRequest) -> str:
    material = "|".join(
        (
            request.source_resource_type,
            request.source_resource_id,
            request.provider_lane,
            request.calendar_ref,
        )
    )
    return _derived_token("calproj", material)


def _projection_payload(
    *,
    projection_id: str,
    request: CalendarProjectionRequest,
    provider: ProviderCalendarEvent,
    desired_sha256: str,
    readback_sha256: str,
) -> dict[str, Any]:
    return {
        "schema_version": CALENDAR_PROJECTION_SCHEMA_VERSION,
        "projection_id": projection_id,
        "source_resource_type": request.source_resource_type,
        "source_resource_id": request.source_resource_id,
        "source_revision": request.source_revision,
        "provider_lane": request.provider_lane,
        "calendar_ref": request.calendar_ref,
        "provider_event_id": provider.event_id,
        "provider_version": provider.provider_version,
        "desired_event": request.event.payload(),
        "desired_sha256": desired_sha256,
        "readback_sha256": readback_sha256,
        "status": "verified",
    }


def _projection_view(record: ResourceRecord) -> CalendarProjectionView:
    if record.resource_type != CALENDAR_PROJECTION_RESOURCE_TYPE:
        raise CalendarProjectionIntegrityError(
            "record is not a canonical calendar_projection Resource"
        )
    payload = record.payload
    if not isinstance(payload, Mapping):
        raise CalendarProjectionIntegrityError(
            "calendar_projection payload must be an object"
        )
    try:
        schema_version = payload["schema_version"]
        projection_id = _token(payload["projection_id"], "projection_id")
        source_type = _token(
            payload["source_resource_type"], "source_resource_type"
        )
        source_id = _token(payload["source_resource_id"], "source_resource_id")
        source_revision = _positive_int(payload["source_revision"], "source_revision")
        provider_lane = _token(payload["provider_lane"], "provider_lane")
        calendar_ref = _text(payload["calendar_ref"], "calendar_ref", 500)
        provider_event_id = _token(payload["provider_event_id"], "provider_event_id")
        provider_version = _provider_version_token(
            payload["provider_version"], "provider_version"
        )
        desired_sha256 = _sha256(payload["desired_sha256"], "desired_sha256")
        readback_sha256 = _sha256(payload["readback_sha256"], "readback_sha256")
        status = _text(payload["status"], "status", 64)
        event_raw = payload["desired_event"]
    except KeyError as exc:
        raise CalendarProjectionIntegrityError(
            f"calendar_projection payload missing field: {exc.args[0]}"
        ) from exc
    except CalendarProjectionValidationError as exc:
        raise CalendarProjectionIntegrityError(str(exc)) from exc
    if schema_version != CALENDAR_PROJECTION_SCHEMA_VERSION:
        raise CalendarProjectionIntegrityError(
            "unsupported calendar_projection schema_version"
        )
    if projection_id != record.resource_id:
        raise CalendarProjectionIntegrityError(
            "projection_id does not match canonical Resource identity"
        )
    if status != "verified":
        raise CalendarProjectionIntegrityError(
            "canonical calendar_projection status must be verified"
        )
    if not isinstance(event_raw, Mapping):
        raise CalendarProjectionIntegrityError("desired_event must be an object")
    try:
        event = _event_material(
            CalendarEventMaterial(
                title=event_raw.get("title"),
                start_at=event_raw.get("start_at"),
                end_at=event_raw.get("end_at"),
                timezone=event_raw.get("timezone"),
                location=event_raw.get("location"),
                description=event_raw.get("description"),
            )
        )
    except CalendarProjectionValidationError as exc:
        raise CalendarProjectionIntegrityError(str(exc)) from exc
    calculated = _event_fingerprint(event)
    if desired_sha256 != calculated or readback_sha256 != calculated:
        raise CalendarProjectionIntegrityError(
            "calendar_projection fingerprints do not match desired_event"
        )
    return CalendarProjectionView(
        projection_id=projection_id,
        revision=record.revision,
        source_resource_type=source_type,
        source_resource_id=source_id,
        source_revision=source_revision,
        provider_lane=provider_lane,
        calendar_ref=calendar_ref,
        provider_event_id=provider_event_id,
        provider_version=provider_version,
        event=event,
        desired_sha256=desired_sha256,
        readback_sha256=readback_sha256,
        status=status,
    )


def _assert_projection_target(
    current: CalendarProjectionView, request: CalendarProjectionRequest
) -> None:
    if (
        current.source_resource_type != request.source_resource_type
        or current.source_resource_id != request.source_resource_id
        or current.provider_lane != request.provider_lane
        or current.calendar_ref != request.calendar_ref
    ):
        raise CalendarProjectionIntegrityError(
            "deterministic projection identity collides with different source/target material"
        )


def _verify_provider_event(
    provider: ProviderCalendarEvent,
    *,
    request: CalendarProjectionRequest,
    projection_key: str,
    expected_event_id: str,
    expected_provider_version: str,
) -> None:
    try:
        lane = _token(provider.provider_lane, "provider.provider_lane")
        calendar_ref = _text(provider.calendar_ref, "provider.calendar_ref", 500)
        event_id = _token(provider.event_id, "provider.event_id")
        version = _provider_version_token(
            provider.provider_version, "provider.provider_version"
        )
        provider_projection_key = _token(
            provider.projection_key, "provider.projection_key"
        )
        material = _event_material(provider.event)
    except CalendarProjectionValidationError as exc:
        raise CalendarProjectionReadbackError(str(exc)) from exc
    if lane != request.provider_lane:
        raise CalendarProjectionReadbackError(
            "provider readback lane does not match requested provider lane"
        )
    if calendar_ref != request.calendar_ref:
        raise CalendarProjectionReadbackError(
            "provider readback calendar does not match requested calendar"
        )
    if event_id != expected_event_id:
        raise CalendarProjectionReadbackError(
            "provider readback event identity changed unexpectedly"
        )
    if version != expected_provider_version:
        raise CalendarProjectionReadbackError(
            "provider readback version does not match mutation/canonical evidence"
        )
    if provider_projection_key != projection_key:
        raise CalendarProjectionReadbackError(
            "provider readback projection key does not match canonical projection identity"
        )
    if material != request.event:
        raise CalendarProjectionReadbackError(
            "provider readback event material does not match desired event"
        )


def _event_fingerprint(event: CalendarEventMaterial) -> str:
    return _fingerprint(event.payload())


def _fingerprint(value: object) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()


def _derived_token(prefix: str, material: str) -> str:
    digest = hashlib.sha256(material.encode("utf-8")).hexdigest()[:32]
    return f"{prefix}-{digest}"


def _token(value: Any, field: str) -> str:
    if not isinstance(value, str):
        raise CalendarProjectionValidationError(f"{field} must be text")
    normalized = value.strip()
    if not _TOKEN_RE.fullmatch(normalized):
        raise CalendarProjectionValidationError(
            f"{field} must be a safe token of 1-128 characters"
        )
    return normalized


def _text(value: Any, field: str, maximum: int) -> str:
    if not isinstance(value, str):
        raise CalendarProjectionValidationError(f"{field} must be text")
    normalized = _WS_RE.sub(" ", value).strip()
    if not normalized:
        raise CalendarProjectionValidationError(f"{field} must be non-empty")
    if len(normalized) > maximum:
        raise CalendarProjectionValidationError(
            f"{field} must be at most {maximum} characters"
        )
    return normalized


def _optional_text(value: Any, field: str, maximum: int) -> str | None:
    if value is None:
        return None
    return _text(value, field, maximum)


def _positive_int(value: Any, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise CalendarProjectionValidationError(f"{field} must be a positive integer")
    return value


def _provider_version_token(value: Any, field: str) -> str:
    if not isinstance(value, str):
        raise CalendarProjectionValidationError(f"{field} must be text")
    normalized = value.strip()
    if not normalized:
        raise CalendarProjectionValidationError(f"{field} must be non-empty")
    if len(normalized) > 1024:
        raise CalendarProjectionValidationError(
            f"{field} must be at most 1024 characters"
        )
    return normalized


def _expected_version(value: str | None) -> None:
    if value is None:
        return
    try:
        _provider_version_token(value, "expected_provider_version")
    except CalendarProjectionValidationError as exc:
        raise CalendarProviderValidationError(str(exc)) from exc


def _next_memory_version(value: str) -> str:
    try:
        normalized = _provider_version_token(value, "provider_version")
        prefix, raw = normalized.split(":", 1)
        number = int(raw)
    except (CalendarProjectionValidationError, ValueError) as exc:
        raise CalendarProviderValidationError(
            "in-memory provider version is malformed"
        ) from exc
    if prefix != "memory" or number < 1:
        raise CalendarProviderValidationError(
            "in-memory provider version is malformed"
        )
    return f"memory:{number + 1}"


def _sha256(value: Any, field: str) -> str:
    if not isinstance(value, str) or not _SHA256_RE.fullmatch(value):
        raise CalendarProjectionValidationError(f"{field} must be lowercase SHA-256 hex")
    return value


def _aware_datetime(value: Any, field: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise CalendarProjectionValidationError(
            f"{field} must be an ISO-8601 timestamp with offset"
        )
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError as exc:
        raise CalendarProjectionValidationError(
            f"{field} must be a valid ISO-8601 timestamp"
        ) from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise CalendarProjectionValidationError(
            f"{field} must include an explicit timezone offset"
        )
    return parsed
