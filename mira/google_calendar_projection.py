"""Google Calendar adapter for MIRA's provider-neutral Calendar projection core.

This module contains no credentials and performs no network I/O by itself. A caller
must inject a Google Calendar transport and a durable idempotency store. The adapter
uses deterministic Google event IDs, private extended properties, and opaque ETag
versions so retries and conditional updates remain safe across process restarts.

Live provider verification belongs to a separate packet with an isolated MIRA test
Calendar; protected personal/legacy Calendars are never development fixtures.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import hashlib
import json
import re
from typing import Any, Mapping, Protocol
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from .calendar_projection import (
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


GOOGLE_PROVIDER_LANE = "google"
_PRIVATE_PROJECTION_KEY = "miraProjectionKey"
_PRIVATE_IDEMPOTENCY_KEY = "miraIdempotencyKey"
_PRIVATE_REQUEST_HASH = "miraRequestHash"
_GOOGLE_EVENT_ID_RE = re.compile(r"^[0-9a-v]{5,1024}$")
_SAFE_KEY_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_WRITABLE_ACCESS_ROLES = frozenset({"owner", "writer"})


class GoogleCalendarTransportError(Exception):
    """Base class for injected Google transport failures."""


class GoogleCalendarTransportNotFoundError(GoogleCalendarTransportError):
    """Raised when an exact Calendar or event is absent."""


class GoogleCalendarTransportConflictError(GoogleCalendarTransportError):
    """Raised for stale ETag / conditional-write conflicts."""


class GoogleCalendarTransportPermissionError(GoogleCalendarTransportError):
    """Raised when the authenticated principal lacks required access."""


class GoogleCalendarTransport(Protocol):
    """Minimal Google Calendar API seam required by this adapter.

    A real implementation should map ``patch_event(..., if_match_etag=...)`` to a
    conditional Google Calendar event patch using HTTP ``If-Match`` and should avoid
    attendee notifications unless product policy explicitly authorizes them.
    """

    def calendar_access_role(self, calendar_ref: str) -> str: ...

    def get_event(self, calendar_ref: str, event_id: str) -> Mapping[str, Any]: ...

    def insert_event(
        self,
        calendar_ref: str,
        event_id: str,
        body: Mapping[str, Any],
    ) -> Mapping[str, Any]: ...

    def patch_event(
        self,
        calendar_ref: str,
        event_id: str,
        body: Mapping[str, Any],
        *,
        if_match_etag: str,
    ) -> Mapping[str, Any]: ...


@dataclass(frozen=True)
class CalendarProviderIdempotencyRecord:
    idempotency_key: str
    request_sha256: str
    calendar_ref: str
    event_id: str
    provider_version: str


class CalendarProviderIdempotencyStore(Protocol):
    """Durable replay history for external Calendar mutations."""

    def get(self, idempotency_key: str) -> CalendarProviderIdempotencyRecord | None: ...

    def put(self, record: CalendarProviderIdempotencyRecord) -> None: ...


class InMemoryCalendarProviderIdempotencyStore:
    """Synthetic deterministic ledger used only for direct adapter verification."""

    def __init__(self) -> None:
        self._records: dict[str, CalendarProviderIdempotencyRecord] = {}

    def get(self, idempotency_key: str) -> CalendarProviderIdempotencyRecord | None:
        return self._records.get(idempotency_key)

    def put(self, record: CalendarProviderIdempotencyRecord) -> None:
        existing = self._records.get(record.idempotency_key)
        if existing is not None and existing != record:
            if existing.request_sha256 != record.request_sha256:
                raise CalendarProviderIdempotencyConflictError(
                    "provider idempotency key was reused for different material"
                )
            raise CalendarProviderConflictError(
                "provider idempotency replay record changed unexpectedly"
            )
        self._records[record.idempotency_key] = record


class GoogleCalendarProjectionAdapter(CalendarProjectionAdapter):
    """Google-specific projection adapter over injected transport and durable replay state."""

    def __init__(
        self,
        transport: GoogleCalendarTransport,
        idempotency: CalendarProviderIdempotencyStore,
        *,
        write_enabled: bool = True,
    ) -> None:
        self._transport = transport
        self._idempotency = idempotency
        self._write_enabled = bool(write_enabled)

    def capability(self) -> CalendarProviderCapability:
        return CalendarProviderCapability(
            provider_lane=GOOGLE_PROVIDER_LANE,
            writable=self._write_enabled,
            exact_readback=True,
            stable_projection_key=True,
        )

    def upsert_event(
        self,
        calendar_ref: str,
        projection_key: str,
        event: CalendarEventMaterial,
        *,
        idempotency_key: str,
        expected_provider_version: str | None,
    ) -> ProviderCalendarMutationResult:
        if not self._write_enabled:
            raise CalendarProviderValidationError("Google Calendar writes are disabled")
        calendar = _text(calendar_ref, "calendar_ref", 500)
        projection = _safe_key(projection_key, "projection_key")
        idem_key = _safe_key(idempotency_key, "idempotency_key")
        expected_version = _optional_etag(expected_provider_version)
        desired = _event(event)
        self._require_writable_calendar(calendar)

        event_id = google_event_id(projection)
        request_sha = _request_sha256(
            calendar_ref=calendar,
            projection_key=projection,
            event=desired,
            expected_provider_version=expected_version,
        )

        prior = self._idempotency.get(idem_key)
        if prior is not None:
            if prior.request_sha256 != request_sha:
                raise CalendarProviderIdempotencyConflictError(
                    "provider idempotency key was reused for different material"
                )
            if prior.calendar_ref != calendar or prior.event_id != event_id:
                raise CalendarProviderConflictError(
                    "provider idempotency replay points to a different Calendar event"
                )
            current = self._read_exact(calendar, event_id)
            _require_managed_identity(current, projection)
            return ProviderCalendarMutationResult(
                event=current,
                idempotent_replay=True,
            )

        existing_raw = self._get_optional(calendar, event_id)
        if existing_raw is None:
            if expected_version is not None:
                raise CalendarProviderConflictError(
                    "Google Calendar event is missing for the expected ETag"
                )
            body = _google_body(
                event_id=event_id,
                projection_key=projection,
                idempotency_key=idem_key,
                request_sha256=request_sha,
                event=desired,
                include_id=True,
            )
            try:
                created_raw = self._transport.insert_event(calendar, event_id, body)
            except GoogleCalendarTransportConflictError:
                # A previous attempt may have committed the deterministic event ID
                # before the client observed success. Resolve by exact readback.
                created_raw = self._get_required(calendar, event_id)
            except GoogleCalendarTransportPermissionError as exc:
                raise CalendarProviderValidationError(
                    "Google Calendar write permission was denied"
                ) from exc
            except GoogleCalendarTransportError as exc:
                raise CalendarProviderError(str(exc)) from exc
            created = _provider_event(calendar, created_raw)
            _require_managed_identity(created, projection)
            _require_retry_metadata(created_raw, idem_key, request_sha)
            if created.event != desired:
                raise CalendarProviderError(
                    "Google Calendar insert readback differs from requested event material"
                )
            self._remember(idem_key, request_sha, created)
            return ProviderCalendarMutationResult(
                event=created,
                idempotent_replay=False,
            )

        existing = _provider_event(calendar, existing_raw)
        _require_managed_identity(existing, projection)
        retry_matches = _retry_metadata_matches(existing_raw, idem_key, request_sha)
        if retry_matches:
            if existing.event != desired:
                raise CalendarProviderConflictError(
                    "Google Calendar retry metadata matches but event material differs"
                )
            self._remember(idem_key, request_sha, existing)
            return ProviderCalendarMutationResult(
                event=existing,
                idempotent_replay=True,
            )

        if expected_version is None:
            if existing.event != desired:
                raise CalendarProviderConflictError(
                    "deterministic Google event ID already exists with different material"
                )
            # Existing compatible event from an earlier crash predating replay-ledger
            # persistence. Claim it only if its MIRA projection identity is exact.
            self._remember(idem_key, request_sha, existing)
            return ProviderCalendarMutationResult(
                event=existing,
                idempotent_replay=True,
            )

        if existing.provider_version != expected_version:
            raise CalendarProviderConflictError(
                "Google Calendar ETag precondition is stale"
            )
        if existing.event == desired:
            self._remember(idem_key, request_sha, existing)
            return ProviderCalendarMutationResult(
                event=existing,
                idempotent_replay=True,
            )

        patch = _google_body(
            event_id=event_id,
            projection_key=projection,
            idempotency_key=idem_key,
            request_sha256=request_sha,
            event=desired,
            include_id=False,
        )
        try:
            updated_raw = self._transport.patch_event(
                calendar,
                event_id,
                patch,
                if_match_etag=existing.provider_version,
            )
        except GoogleCalendarTransportConflictError as exc:
            latest = self._get_optional(calendar, event_id)
            if latest is not None and _retry_metadata_matches(
                latest, idem_key, request_sha
            ):
                replayed = _provider_event(calendar, latest)
                _require_managed_identity(replayed, projection)
                if replayed.event != desired:
                    raise CalendarProviderConflictError(
                        "Google Calendar update retry metadata matches but material differs"
                    ) from exc
                self._remember(idem_key, request_sha, replayed)
                return ProviderCalendarMutationResult(
                    event=replayed,
                    idempotent_replay=True,
                )
            raise CalendarProviderConflictError(
                "Google Calendar ETag changed during conditional update"
            ) from exc
        except GoogleCalendarTransportPermissionError as exc:
            raise CalendarProviderValidationError(
                "Google Calendar write permission was denied"
            ) from exc
        except GoogleCalendarTransportError as exc:
            raise CalendarProviderError(str(exc)) from exc

        updated = _provider_event(calendar, updated_raw)
        _require_managed_identity(updated, projection)
        _require_retry_metadata(updated_raw, idem_key, request_sha)
        if updated.event != desired:
            raise CalendarProviderError(
                "Google Calendar update readback differs from requested event material"
            )
        self._remember(idem_key, request_sha, updated)
        return ProviderCalendarMutationResult(
            event=updated,
            idempotent_replay=False,
        )

    def read_event(self, calendar_ref: str, event_id: str) -> ProviderCalendarEvent:
        calendar = _text(calendar_ref, "calendar_ref", 500)
        normalized_id = _google_event_id(event_id)
        return self._read_exact(calendar, normalized_id)

    def _require_writable_calendar(self, calendar_ref: str) -> None:
        try:
            role = self._transport.calendar_access_role(calendar_ref)
        except GoogleCalendarTransportNotFoundError as exc:
            raise CalendarProviderValidationError(
                "Google Calendar target does not exist or is not visible"
            ) from exc
        except GoogleCalendarTransportPermissionError as exc:
            raise CalendarProviderValidationError(
                "Google Calendar access could not be verified"
            ) from exc
        except GoogleCalendarTransportError as exc:
            raise CalendarProviderError(str(exc)) from exc
        if role not in _WRITABLE_ACCESS_ROLES:
            raise CalendarProviderValidationError(
                "Google Calendar target must provide owner or writer access for exact private-metadata readback"
            )

    def _get_optional(self, calendar_ref: str, event_id: str) -> Mapping[str, Any] | None:
        try:
            return self._transport.get_event(calendar_ref, event_id)
        except GoogleCalendarTransportNotFoundError:
            return None
        except GoogleCalendarTransportPermissionError as exc:
            raise CalendarProviderValidationError(
                "Google Calendar event read permission was denied"
            ) from exc
        except GoogleCalendarTransportError as exc:
            raise CalendarProviderError(str(exc)) from exc

    def _get_required(self, calendar_ref: str, event_id: str) -> Mapping[str, Any]:
        raw = self._get_optional(calendar_ref, event_id)
        if raw is None:
            raise CalendarProviderNotFoundError(
                f"Google Calendar event does not exist: {calendar_ref}:{event_id}"
            )
        return raw

    def _read_exact(self, calendar_ref: str, event_id: str) -> ProviderCalendarEvent:
        return _provider_event(calendar_ref, self._get_required(calendar_ref, event_id))

    def _remember(
        self,
        idempotency_key: str,
        request_sha256: str,
        event: ProviderCalendarEvent,
    ) -> None:
        record = CalendarProviderIdempotencyRecord(
            idempotency_key=idempotency_key,
            request_sha256=request_sha256,
            calendar_ref=event.calendar_ref,
            event_id=event.event_id,
            provider_version=event.provider_version,
        )
        try:
            self._idempotency.put(record)
        except (CalendarProviderIdempotencyConflictError, CalendarProviderConflictError):
            raise
        except Exception as exc:
            raise CalendarProviderError(
                "provider idempotency ledger could not persist replay evidence"
            ) from exc


def google_event_id(projection_key: str) -> str:
    """Return a deterministic Google-valid event ID for one projection identity.

    Google permits caller-specified event IDs using base32hex characters. Lowercase
    hexadecimal is a subset of that alphabet, so the stable ``mira`` prefix plus a
    SHA-256 hex digest is valid while remaining provider-opaque.
    """

    projection = _safe_key(projection_key, "projection_key")
    candidate = "mira" + hashlib.sha256(projection.encode("utf-8")).hexdigest()[:48]
    return _google_event_id(candidate)


def _google_body(
    *,
    event_id: str,
    projection_key: str,
    idempotency_key: str,
    request_sha256: str,
    event: CalendarEventMaterial,
    include_id: bool,
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "summary": event.title,
        "description": event.description,
        "location": event.location,
        "start": {"dateTime": event.start_at, "timeZone": event.timezone},
        "end": {"dateTime": event.end_at, "timeZone": event.timezone},
        "extendedProperties": {
            "private": {
                _PRIVATE_PROJECTION_KEY: projection_key,
                _PRIVATE_IDEMPOTENCY_KEY: idempotency_key,
                _PRIVATE_REQUEST_HASH: request_sha256,
            }
        },
    }
    if include_id:
        body["id"] = event_id
    return body


def _provider_event(calendar_ref: str, raw: Mapping[str, Any]) -> ProviderCalendarEvent:
    if not isinstance(raw, Mapping):
        raise CalendarProviderValidationError("Google Calendar event must be an object")
    event_id = _google_event_id(raw.get("id"))
    etag = _etag(raw.get("etag"))
    projection_key = _private_properties(raw).get(_PRIVATE_PROJECTION_KEY)
    projection = _safe_key(projection_key, "Google private projection key")
    summary = _text(raw.get("summary"), "Google event summary", 500)
    start_raw = _mapping(raw.get("start"), "Google event start")
    end_raw = _mapping(raw.get("end"), "Google event end")
    timezone = _text(start_raw.get("timeZone"), "Google event start.timeZone", 128)
    end_timezone = _text(end_raw.get("timeZone"), "Google event end.timeZone", 128)
    if timezone != end_timezone:
        raise CalendarProviderValidationError(
            "Google event start/end time zones do not match"
        )
    start_at = _normalize_google_datetime(
        start_raw.get("dateTime"), timezone, "Google event start.dateTime"
    )
    end_at = _normalize_google_datetime(
        end_raw.get("dateTime"), timezone, "Google event end.dateTime"
    )
    return ProviderCalendarEvent(
        provider_lane=GOOGLE_PROVIDER_LANE,
        calendar_ref=_text(calendar_ref, "calendar_ref", 500),
        event_id=event_id,
        provider_version=etag,
        projection_key=projection,
        event=CalendarEventMaterial(
            title=summary,
            start_at=start_at,
            end_at=end_at,
            timezone=timezone,
            location=_optional_text(raw.get("location"), "Google event location", 1000),
            description=_optional_text(
                raw.get("description"), "Google event description", 4000
            ),
        ),
    )


def _require_managed_identity(event: ProviderCalendarEvent, projection_key: str) -> None:
    if event.event_id != google_event_id(projection_key):
        raise CalendarProviderConflictError(
            "Google event ID does not match deterministic MIRA projection identity"
        )
    if event.projection_key != projection_key:
        raise CalendarProviderConflictError(
            "Google event private projection metadata does not match MIRA identity"
        )


def _request_sha256(
    *,
    calendar_ref: str,
    projection_key: str,
    event: CalendarEventMaterial,
    expected_provider_version: str | None,
) -> str:
    return hashlib.sha256(
        json.dumps(
            {
                "calendar_ref": calendar_ref,
                "projection_key": projection_key,
                "event": event.payload(),
                "expected_provider_version": expected_provider_version,
            },
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()


def _private_properties(raw: Mapping[str, Any]) -> Mapping[str, Any]:
    extended = raw.get("extendedProperties")
    if not isinstance(extended, Mapping):
        raise CalendarProviderValidationError(
            "Google event lacks MIRA private extended properties"
        )
    private = extended.get("private")
    if not isinstance(private, Mapping):
        raise CalendarProviderValidationError(
            "Google event lacks MIRA private extended properties"
        )
    return private


def _retry_metadata_matches(
    raw: Mapping[str, Any], idempotency_key: str, request_sha256: str
) -> bool:
    private = _private_properties(raw)
    return (
        private.get(_PRIVATE_IDEMPOTENCY_KEY) == idempotency_key
        and private.get(_PRIVATE_REQUEST_HASH) == request_sha256
    )


def _require_retry_metadata(
    raw: Mapping[str, Any], idempotency_key: str, request_sha256: str
) -> None:
    if not _retry_metadata_matches(raw, idempotency_key, request_sha256):
        raise CalendarProviderError(
            "Google event readback lacks exact MIRA idempotency metadata"
        )


def _event(value: CalendarEventMaterial) -> CalendarEventMaterial:
    if not isinstance(value, CalendarEventMaterial):
        raise CalendarProviderValidationError("event must be CalendarEventMaterial")
    title = _text(value.title, "event.title", 500)
    timezone = _text(value.timezone, "event.timezone", 128)
    try:
        zone = ZoneInfo(timezone)
    except ZoneInfoNotFoundError as exc:
        raise CalendarProviderValidationError(
            f"event.timezone is not a known IANA timezone: {timezone}"
        ) from exc
    start = _aware_datetime(value.start_at, "event.start_at").astimezone(zone)
    end = _aware_datetime(value.end_at, "event.end_at").astimezone(zone)
    if end <= start:
        raise CalendarProviderValidationError(
            "event.end_at must be later than event.start_at"
        )
    return CalendarEventMaterial(
        title=title,
        start_at=start.isoformat(),
        end_at=end.isoformat(),
        timezone=timezone,
        location=_optional_text(value.location, "event.location", 1000),
        description=_optional_text(value.description, "event.description", 4000),
    )


def _normalize_google_datetime(value: Any, timezone: str, field: str) -> str:
    parsed = _aware_datetime(value, field)
    try:
        zone = ZoneInfo(timezone)
    except ZoneInfoNotFoundError as exc:
        raise CalendarProviderValidationError(
            f"Google event timeZone is not a known IANA timezone: {timezone}"
        ) from exc
    return parsed.astimezone(zone).isoformat()


def _aware_datetime(value: Any, field: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise CalendarProviderValidationError(
            f"{field} must be an ISO-8601 timestamp with offset"
        )
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError as exc:
        raise CalendarProviderValidationError(
            f"{field} must be a valid ISO-8601 timestamp"
        ) from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise CalendarProviderValidationError(
            f"{field} must include an explicit timezone offset"
        )
    return parsed


def _mapping(value: Any, field: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise CalendarProviderValidationError(f"{field} must be an object")
    return value


def _text(value: Any, field: str, maximum: int) -> str:
    if not isinstance(value, str):
        raise CalendarProviderValidationError(f"{field} must be text")
    normalized = value.strip()
    if not normalized:
        raise CalendarProviderValidationError(f"{field} must be non-empty")
    if len(normalized) > maximum or "\r" in normalized or "\n" in normalized:
        raise CalendarProviderValidationError(
            f"{field} must be single-line text of at most {maximum} characters"
        )
    return normalized


def _optional_text(value: Any, field: str, maximum: int) -> str | None:
    if value is None:
        return None
    return _text(value, field, maximum)


def _safe_key(value: Any, field: str) -> str:
    if not isinstance(value, str) or not _SAFE_KEY_RE.fullmatch(value.strip()):
        raise CalendarProviderValidationError(
            f"{field} must be a safe token of 1-128 characters"
        )
    return value.strip()


def _google_event_id(value: Any) -> str:
    if not isinstance(value, str) or not _GOOGLE_EVENT_ID_RE.fullmatch(value):
        raise CalendarProviderValidationError(
            "Google Calendar event ID must be 5-1024 base32hex characters"
        )
    return value


def _etag(value: Any) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise CalendarProviderValidationError("Google Calendar event ETag must be non-empty text")
    if len(value) > 1024 or "\r" in value or "\n" in value:
        raise CalendarProviderValidationError("Google Calendar event ETag is malformed")
    return value


def _optional_etag(value: Any) -> str | None:
    if value is None:
        return None
    return _etag(value)


def _sha256(value: Any, field: str) -> str:
    if not isinstance(value, str) or not _SHA256_RE.fullmatch(value):
        raise CalendarProviderValidationError(f"{field} must be lowercase SHA-256 hex")
    return value
