"""Stock-ChatGPT Google Calendar adapter for the default Personal MIRA lane.

This adapter deliberately models the capability exposed by the native Google
Calendar connector rather than pretending it has provider features it does not.
The native update surface does not expose an atomic ETag/If-Match precondition,
so this lane is same-user/single-writer only. It performs an exact provider
preflight before update and exact provider readback after every mutation.

Stable projection identity is retained in a small MIRA marker appended to the
description of events MIRA creates. Canonical MIRA state remains authoritative
for the exact provider event ID after successful create/readback. The marker is
used for lost-create-ack recovery only; MIRA never searches by title/time and
silently guesses which human event is its projection.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
import hashlib
import json
import re
from typing import Protocol, Sequence

from .calendar_projection import (
    CALENDAR_PROJECTION_RESOURCE_TYPE,
    CalendarEventMaterial,
    CalendarProjectionAdapter,
    CalendarProviderCapability,
    CalendarProviderConflictError,
    CalendarProviderError,
    CalendarProviderIdempotencyConflictError,
    CalendarProviderNotFoundError,
    CalendarProviderValidationError,
    ProviderCalendarEvent,
    ProviderCalendarMutationResult,
)
from .structured_state import NotFoundError, StructuredStateAdapter, StructuredStateError


GOOGLE_NATIVE_PROVIDER_LANE = "google"
GOOGLE_NATIVE_PROTECTION_MODE = "single_writer_preflight_non_atomic"
_MIRA_MARKER_PREFIX = "MIRA-PROJECTION-ID:"
_TOKEN_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")


@dataclass(frozen=True)
class NativeGoogleCalendarEvent:
    """Normalized event shape returned by the stock Google Calendar connector."""

    event_id: str
    title: str
    start_at: str
    end_at: str
    timezone: str
    location: str | None = None
    description: str | None = None


@dataclass(frozen=True)
class NativeGoogleCalendarWrite:
    """Exact safe write material for a MIRA-managed native Calendar event."""

    title: str
    start_at: str
    end_at: str
    timezone: str
    location: str | None
    description: str
    attendees: tuple[str, ...] = ()
    add_google_meet: bool = False
    self_attendance: str = "omit"


class NativeGoogleCalendarConnector(Protocol):
    """Small connector contract corresponding to stock ChatGPT Calendar actions."""

    def search_events(
        self,
        calendar_ref: str,
        *,
        query: str,
        time_min: str,
        time_max: str,
    ) -> Sequence[NativeGoogleCalendarEvent]: ...

    def create_event(
        self,
        calendar_ref: str,
        write: NativeGoogleCalendarWrite,
    ) -> NativeGoogleCalendarEvent: ...

    def update_event(
        self,
        calendar_ref: str,
        event_id: str,
        write: NativeGoogleCalendarWrite,
    ) -> NativeGoogleCalendarEvent: ...

    def read_event(
        self,
        calendar_ref: str,
        event_id: str,
    ) -> NativeGoogleCalendarEvent: ...


class GoogleCalendarNativeSingleWriterAdapter(CalendarProjectionAdapter):
    """Native Google connector adapter with explicit non-atomic update semantics."""

    protection_mode = GOOGLE_NATIVE_PROTECTION_MODE

    def __init__(
        self,
        connector: NativeGoogleCalendarConnector,
        state: StructuredStateAdapter,
        *,
        projection_resource_type: str = CALENDAR_PROJECTION_RESOURCE_TYPE,
    ) -> None:
        self._connector = connector
        self._state = state
        self._projection_type = _token(
            projection_resource_type, "projection_resource_type"
        )

    def capability(self) -> CalendarProviderCapability:
        return CalendarProviderCapability(
            provider_lane=GOOGLE_NATIVE_PROVIDER_LANE,
            writable=True,
            exact_readback=True,
            stable_projection_key=True,
        )

    def capability_evidence(self) -> dict[str, object]:
        """Human/audit-readable evidence boundary for the native connector lane."""
        return {
            "provider_lane": GOOGLE_NATIVE_PROVIDER_LANE,
            "writable": True,
            "exact_readback": True,
            "stable_projection_key": True,
            "update_protection": GOOGLE_NATIVE_PROTECTION_MODE,
            "atomic_provider_version_precondition": False,
            "supported_writer_model": "single_writer",
            "ordinary_user_activation": "plain_language_intent_plus_provider_consent",
        }

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
        idem = _token(idempotency_key, "idempotency_key")
        desired = _event(event)
        marker = _marker(projection)

        if expected_provider_version is None:
            existing = self._recover_create(calendar, projection, desired)
            if existing is not None:
                return ProviderCalendarMutationResult(
                    event=existing,
                    idempotent_replay=True,
                )
            write = _write(desired, projection)
            try:
                created = self._connector.create_event(calendar, write)
            except Exception as exc:
                # A provider/tool failure can occur after Google committed the event.
                # Search once for the exact projection marker before returning the
                # failure. If exactly one exact event exists, recover it; otherwise
                # fail closed so a later retry cannot blindly create a duplicate.
                recovered = self._recover_create(calendar, projection, desired)
                if recovered is not None:
                    return ProviderCalendarMutationResult(
                        event=recovered,
                        idempotent_replay=True,
                    )
                raise CalendarProviderError(
                    "native Google Calendar create acknowledgement could not be verified"
                ) from exc
            provider = self._provider_event(calendar, created, projection)
            _require_material(provider.event, desired)
            verified = self.read_event(calendar, provider.event_id)
            _require_same_provider(provider, verified)
            return ProviderCalendarMutationResult(
                event=verified,
                idempotent_replay=False,
            )

        expected_version = _provider_version(expected_provider_version)
        projection_state = self._projection_state(projection)
        if projection_state["calendar_ref"] != calendar:
            raise CalendarProviderConflictError(
                "canonical projection Calendar changed unexpectedly"
            )
        event_id = projection_state["provider_event_id"]
        if projection_state["provider_version"] != expected_version:
            raise CalendarProviderConflictError(
                "canonical provider version does not match requested precondition"
            )

        current = self.read_event(calendar, event_id)
        if current.provider_version != expected_version:
            raise CalendarProviderConflictError(
                "provider event changed since MIRA's last verified readback"
            )
        if current.projection_key != projection:
            raise CalendarProviderConflictError(
                "provider event no longer carries the canonical MIRA projection marker"
            )
        if current.event == desired:
            return ProviderCalendarMutationResult(
                event=current,
                idempotent_replay=True,
            )

        # The stock connector exposes no If-Match/ETag argument. The exact read
        # above is therefore a single-writer preflight, not an atomic compare-and-
        # swap guarantee. This is acceptable only in the Personal single-writer
        # lane and must never be promoted to Android/shared-writer safety.
        try:
            updated = self._connector.update_event(
                calendar,
                event_id,
                _write(desired, projection),
            )
        except Exception as exc:
            raise CalendarProviderError(
                "native Google Calendar update acknowledgement could not be verified"
            ) from exc
        provider = self._provider_event(calendar, updated, projection)
        if provider.event_id != event_id:
            raise CalendarProviderConflictError(
                "native Google Calendar update changed provider event identity"
            )
        _require_material(provider.event, desired)
        verified = self.read_event(calendar, event_id)
        _require_same_provider(provider, verified)
        return ProviderCalendarMutationResult(
            event=verified,
            idempotent_replay=False,
        )

    def read_event(self, calendar_ref: str, event_id: str) -> ProviderCalendarEvent:
        calendar = _text(calendar_ref, "calendar_ref", 500)
        normalized_event_id = _token(event_id, "event_id")
        try:
            raw = self._connector.read_event(calendar, normalized_event_id)
        except Exception as exc:
            raise CalendarProviderNotFoundError(
                f"native Google Calendar event does not exist: {calendar}:{normalized_event_id}"
            ) from exc
        projection = _projection_from_description(raw.description)
        if projection is None:
            raise CalendarProviderConflictError(
                "native Google Calendar event is missing its MIRA projection marker"
            )
        provider = self._provider_event(calendar, raw, projection)
        if provider.event_id != normalized_event_id:
            raise CalendarProviderConflictError(
                "native Google Calendar readback returned a different event identity"
            )
        return provider

    def _recover_create(
        self,
        calendar_ref: str,
        projection_key: str,
        desired: CalendarEventMaterial,
    ) -> ProviderCalendarEvent | None:
        time_min, time_max = _search_window(desired)
        marker = _marker(projection_key)
        try:
            candidates = tuple(
                self._connector.search_events(
                    calendar_ref,
                    query=marker,
                    time_min=time_min,
                    time_max=time_max,
                )
            )
        except Exception as exc:
            raise CalendarProviderError(
                "native Google Calendar projection recovery search failed"
            ) from exc
        exact: list[ProviderCalendarEvent] = []
        for raw in candidates:
            if _projection_from_description(raw.description) != projection_key:
                continue
            provider = self._provider_event(calendar_ref, raw, projection_key)
            if provider.event == desired:
                exact.append(provider)
        if len(exact) > 1:
            raise CalendarProviderConflictError(
                "multiple native Google Calendar events carry the same MIRA projection identity"
            )
        if len(exact) == 1:
            return self.read_event(calendar_ref, exact[0].event_id)
        # If candidates exist with the marker but material differs, the identity is
        # already occupied and must not be reused for a second provider event.
        marker_matches = [
            raw
            for raw in candidates
            if _projection_from_description(raw.description) == projection_key
        ]
        if marker_matches:
            raise CalendarProviderConflictError(
                "MIRA projection identity already exists with different provider material"
            )
        return None

    def _projection_state(self, projection_key: str) -> dict[str, str]:
        try:
            record = self._state.get(self._projection_type, projection_key)
        except NotFoundError as exc:
            raise CalendarProviderConflictError(
                "canonical projection state is missing for native provider update"
            ) from exc
        except StructuredStateError as exc:
            raise CalendarProviderError(
                "canonical projection state could not be read for native provider update"
            ) from exc
        payload = record.payload
        try:
            calendar_ref = _text(payload["calendar_ref"], "calendar_ref", 500)
            event_id = _token(payload["provider_event_id"], "provider_event_id")
            version = _provider_version(payload["provider_version"])
        except (KeyError, TypeError, CalendarProviderValidationError) as exc:
            raise CalendarProviderError(
                "canonical projection state is malformed for native provider update"
            ) from exc
        return {
            "calendar_ref": calendar_ref,
            "provider_event_id": event_id,
            "provider_version": version,
        }

    @staticmethod
    def _provider_event(
        calendar_ref: str,
        raw: NativeGoogleCalendarEvent,
        projection_key: str,
    ) -> ProviderCalendarEvent:
        raw_event_id = _token(raw.event_id, "provider.event_id")
        projection = _token(projection_key, "provider.projection_key")
        material = _event_from_raw(raw, projection)
        version = _raw_event_version(raw)
        return ProviderCalendarEvent(
            provider_lane=GOOGLE_NATIVE_PROVIDER_LANE,
            calendar_ref=calendar_ref,
            event_id=raw_event_id,
            provider_version=version,
            projection_key=projection,
            event=material,
        )


def _write(event: CalendarEventMaterial, projection_key: str) -> NativeGoogleCalendarWrite:
    return NativeGoogleCalendarWrite(
        title=event.title,
        start_at=event.start_at,
        end_at=event.end_at,
        timezone=event.timezone,
        location=event.location,
        description=_description_with_marker(event.description, projection_key),
    )


def _event_from_raw(
    raw: NativeGoogleCalendarEvent,
    projection_key: str,
) -> CalendarEventMaterial:
    marker = _projection_from_description(raw.description)
    if marker != projection_key:
        raise CalendarProviderConflictError(
            "native Google Calendar event projection marker does not match canonical identity"
        )
    return CalendarEventMaterial(
        title=_text(raw.title, "provider.title", 500),
        start_at=_text(raw.start_at, "provider.start_at", 128),
        end_at=_text(raw.end_at, "provider.end_at", 128),
        timezone=_text(raw.timezone, "provider.timezone", 128),
        location=_optional_text(raw.location, "provider.location", 1000),
        description=_description_without_marker(raw.description),
    )


def _event(value: CalendarEventMaterial) -> CalendarEventMaterial:
    if not isinstance(value, CalendarEventMaterial):
        raise CalendarProviderValidationError("event must be CalendarEventMaterial")
    return CalendarEventMaterial(
        title=_text(value.title, "event.title", 500),
        start_at=_text(value.start_at, "event.start_at", 128),
        end_at=_text(value.end_at, "event.end_at", 128),
        timezone=_text(value.timezone, "event.timezone", 128),
        location=_optional_text(value.location, "event.location", 1000),
        description=_optional_text(value.description, "event.description", 4000),
    )


def _description_with_marker(description: str | None, projection_key: str) -> str:
    projection = _token(projection_key, "projection_key")
    marker = _marker(projection)
    base = "" if description is None else description.strip()
    if _MIRA_MARKER_PREFIX in base:
        raise CalendarProviderValidationError(
            "event description cannot contain a MIRA projection marker"
        )
    return marker if not base else f"{base}\n\n{marker}"


def _description_without_marker(description: str | None) -> str | None:
    if description is None:
        return None
    text = description.strip()
    projection = _projection_from_description(text)
    if projection is None:
        raise CalendarProviderConflictError(
            "native Google Calendar event is missing its MIRA projection marker"
        )
    marker = _marker(projection)
    if text == marker:
        return None
    suffix = "\n\n" + marker
    if not text.endswith(suffix):
        raise CalendarProviderConflictError(
            "native Google Calendar projection marker is not in the expected trailing position"
        )
    base = text[: -len(suffix)].rstrip()
    return base or None


def _projection_from_description(description: str | None) -> str | None:
    if not isinstance(description, str) or not description.strip():
        return None
    lines = [line.strip() for line in description.strip().splitlines()]
    matches = [
        line[len(_MIRA_MARKER_PREFIX) :].strip()
        for line in lines
        if line.startswith(_MIRA_MARKER_PREFIX)
    ]
    if not matches:
        return None
    if len(matches) != 1:
        raise CalendarProviderConflictError(
            "native Google Calendar event has duplicate MIRA projection markers"
        )
    return _token(matches[0], "provider.projection_key")


def _marker(projection_key: str) -> str:
    return _MIRA_MARKER_PREFIX + _token(projection_key, "projection_key")


def _raw_event_version(raw: NativeGoogleCalendarEvent) -> str:
    material = {
        "event_id": raw.event_id,
        "title": raw.title,
        "start_at": raw.start_at,
        "end_at": raw.end_at,
        "timezone": raw.timezone,
        "location": raw.location,
        "description": raw.description,
    }
    digest = hashlib.sha256(
        json.dumps(
            material,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()
    return "native:" + digest


def _provider_version(value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CalendarProviderValidationError(
            "expected_provider_version must be non-empty text"
        )
    normalized = value.strip()
    if len(normalized) > 1024:
        raise CalendarProviderValidationError(
            "expected_provider_version is too long"
        )
    return normalized


def _search_window(event: CalendarEventMaterial) -> tuple[str, str]:
    try:
        start = datetime.fromisoformat(event.start_at.replace("Z", "+00:00"))
        end = datetime.fromisoformat(event.end_at.replace("Z", "+00:00"))
    except ValueError as exc:
        raise CalendarProviderValidationError(
            "event timestamps must be valid ISO-8601 values"
        ) from exc
    if start.tzinfo is None or end.tzinfo is None:
        raise CalendarProviderValidationError(
            "event timestamps must include timezone offsets"
        )
    return (
        (start - timedelta(days=1)).isoformat(),
        (end + timedelta(days=1)).isoformat(),
    )


def _require_material(actual: CalendarEventMaterial, expected: CalendarEventMaterial) -> None:
    if actual != expected:
        raise CalendarProviderConflictError(
            "native Google Calendar readback material does not match desired MIRA event"
        )


def _require_same_provider(
    first: ProviderCalendarEvent,
    second: ProviderCalendarEvent,
) -> None:
    if first != second:
        raise CalendarProviderConflictError(
            "native Google Calendar independent readback differs from mutation acknowledgement"
        )


def _token(value: object, field: str) -> str:
    if not isinstance(value, str):
        raise CalendarProviderValidationError(f"{field} must be text")
    normalized = value.strip()
    if not _TOKEN_RE.fullmatch(normalized):
        raise CalendarProviderValidationError(
            f"{field} must be a safe token of 1-128 characters"
        )
    return normalized


def _text(value: object, field: str, maximum: int) -> str:
    if not isinstance(value, str):
        raise CalendarProviderValidationError(f"{field} must be text")
    normalized = " ".join(value.split()).strip()
    if not normalized:
        raise CalendarProviderValidationError(f"{field} must be non-empty")
    if len(normalized) > maximum:
        raise CalendarProviderValidationError(
            f"{field} must be at most {maximum} characters"
        )
    return normalized


def _optional_text(value: object, field: str, maximum: int) -> str | None:
    if value is None:
        return None
    return _text(value, field, maximum)


__all__ = [
    "GOOGLE_NATIVE_PROTECTION_MODE",
    "GOOGLE_NATIVE_PROVIDER_LANE",
    "GoogleCalendarNativeSingleWriterAdapter",
    "NativeGoogleCalendarConnector",
    "NativeGoogleCalendarEvent",
    "NativeGoogleCalendarWrite",
]
