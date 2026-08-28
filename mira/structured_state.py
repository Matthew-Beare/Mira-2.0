"""Provider-neutral structured mutable-state contract and synthetic memory adapter.

This module intentionally contains no provider, network, database, evidence-store,
or product-domain policy. It defines the deterministic mutation/readback semantics
required by later MIRROR authority and API layers.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
import hashlib
import json
import re
from typing import Any, Mapping, Protocol, Sequence


_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")


class StructuredStateError(Exception):
    """Base class for structured-state contract failures."""


class ValidationError(StructuredStateError):
    """Raised when an operation is outside the declared adapter schema."""


class NotFoundError(StructuredStateError):
    """Raised when an exact requested record does not exist."""


class RevisionConflictError(StructuredStateError):
    """Raised when optimistic revision preconditions are stale or impossible."""


class IdempotencyConflictError(StructuredStateError):
    """Raised when an idempotency key is reused for different material input."""


class IdentityConflictError(StructuredStateError):
    """Raised when a caller-supplied canonical identity collides."""


@dataclass(frozen=True)
class HealthStatus:
    ok: bool
    adapter: str
    schema_version: str


@dataclass(frozen=True)
class SchemaInfo:
    schema_version: str
    resource_types: tuple[str, ...]
    event_types: tuple[str, ...]


@dataclass(frozen=True)
class ResourceRecord:
    resource_type: str
    resource_id: str
    payload: dict[str, Any]
    revision: int


@dataclass(frozen=True)
class MutationResult:
    record: ResourceRecord
    idempotent_replay: bool


@dataclass(frozen=True)
class EventRecord:
    event_id: str
    stream_type: str
    stream_id: str
    event_type: str
    payload: dict[str, Any]
    stream_revision: int


@dataclass(frozen=True)
class EventMutationResult:
    event: EventRecord
    idempotent_replay: bool


class StructuredStateAdapter(Protocol):
    """Bounded interface consumed by later Authority Registry/API layers."""

    def health(self) -> HealthStatus: ...

    def schema(self) -> SchemaInfo: ...

    def get(self, resource_type: str, resource_id: str) -> ResourceRecord: ...

    def query(
        self,
        resource_type: str,
        *,
        filters: Mapping[str, Any] | None = None,
        limit: int = 100,
    ) -> Sequence[ResourceRecord]: ...

    def upsert(
        self,
        resource_type: str,
        resource_id: str,
        payload: Mapping[str, Any],
        *,
        idempotency_key: str,
        expected_revision: int | None = None,
    ) -> MutationResult: ...

    def append_event(
        self,
        stream_type: str,
        stream_id: str,
        event_type: str,
        event_id: str,
        payload: Mapping[str, Any],
        *,
        idempotency_key: str,
        expected_stream_revision: int | None = None,
    ) -> EventMutationResult: ...

    def events_for(
        self,
        stream_type: str,
        stream_id: str,
        *,
        after_revision: int = 0,
        limit: int = 100,
    ) -> Sequence[EventRecord]: ...


class InMemoryStructuredStateAdapter:
    """Deterministic synthetic adapter with exact readback and replay protection."""

    def __init__(
        self,
        *,
        schema_version: str,
        resource_types: Sequence[str],
        event_types: Sequence[str],
    ) -> None:
        self._schema_version = _validate_token(schema_version, "schema_version")
        self._resource_types = _validated_type_set(resource_types, "resource_types")
        self._event_types = _validated_type_set(event_types, "event_types")
        self._records: dict[tuple[str, str], ResourceRecord] = {}
        self._events: list[EventRecord] = []
        self._event_ids: dict[str, EventRecord] = {}
        self._stream_revisions: dict[tuple[str, str], int] = {}
        self._idempotency: dict[str, tuple[str, object]] = {}

    def health(self) -> HealthStatus:
        return HealthStatus(ok=True, adapter="memory", schema_version=self._schema_version)

    def schema(self) -> SchemaInfo:
        return SchemaInfo(
            schema_version=self._schema_version,
            resource_types=tuple(sorted(self._resource_types)),
            event_types=tuple(sorted(self._event_types)),
        )

    def get(self, resource_type: str, resource_id: str) -> ResourceRecord:
        self._validate_resource_identity(resource_type, resource_id)
        try:
            return deepcopy(self._records[(resource_type, resource_id)])
        except KeyError as exc:
            raise NotFoundError(f"{resource_type}:{resource_id} does not exist") from exc

    def query(
        self,
        resource_type: str,
        *,
        filters: Mapping[str, Any] | None = None,
        limit: int = 100,
    ) -> tuple[ResourceRecord, ...]:
        self._validate_resource_type(resource_type)
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 1000:
            raise ValidationError("limit must be an integer from 1 through 1000")
        normalized_filters = _normalize_mapping(filters or {}, "filters")
        rows = [
            record
            for (candidate_type, _), record in self._records.items()
            if candidate_type == resource_type
            and all(record.payload.get(key) == value for key, value in normalized_filters.items())
        ]
        rows.sort(key=lambda row: row.resource_id)
        return tuple(deepcopy(rows[:limit]))

    def upsert(
        self,
        resource_type: str,
        resource_id: str,
        payload: Mapping[str, Any],
        *,
        idempotency_key: str,
        expected_revision: int | None = None,
    ) -> MutationResult:
        self._validate_resource_identity(resource_type, resource_id)
        normalized_payload = _normalize_mapping(payload, "payload")
        normalized_key = _validate_token(idempotency_key, "idempotency_key")
        _validate_expected_revision(expected_revision, "expected_revision")

        fingerprint = _fingerprint(
            {
                "operation": "upsert",
                "resource_type": resource_type,
                "resource_id": resource_id,
                "payload": normalized_payload,
                "expected_revision": expected_revision,
            }
        )
        replay = self._replay(normalized_key, fingerprint, MutationResult)
        if replay is not None:
            return MutationResult(record=deepcopy(replay.record), idempotent_replay=True)

        current = self._records.get((resource_type, resource_id))
        current_revision = 0 if current is None else current.revision
        if expected_revision is not None and expected_revision != current_revision:
            raise RevisionConflictError(
                f"expected revision {expected_revision}, current revision is {current_revision}"
            )

        record = ResourceRecord(
            resource_type=resource_type,
            resource_id=resource_id,
            payload=deepcopy(normalized_payload),
            revision=current_revision + 1,
        )
        self._records[(resource_type, resource_id)] = record
        result = MutationResult(record=deepcopy(record), idempotent_replay=False)
        self._remember(normalized_key, fingerprint, result)
        return result

    def append_event(
        self,
        stream_type: str,
        stream_id: str,
        event_type: str,
        event_id: str,
        payload: Mapping[str, Any],
        *,
        idempotency_key: str,
        expected_stream_revision: int | None = None,
    ) -> EventMutationResult:
        self._validate_resource_identity(stream_type, stream_id)
        if event_type not in self._event_types:
            raise ValidationError(f"unknown event type: {event_type}")
        normalized_event_id = _validate_id(event_id, "event_id")
        normalized_payload = _normalize_mapping(payload, "payload")
        normalized_key = _validate_token(idempotency_key, "idempotency_key")
        _validate_expected_revision(expected_stream_revision, "expected_stream_revision")

        fingerprint = _fingerprint(
            {
                "operation": "append_event",
                "stream_type": stream_type,
                "stream_id": stream_id,
                "event_type": event_type,
                "event_id": normalized_event_id,
                "payload": normalized_payload,
                "expected_stream_revision": expected_stream_revision,
            }
        )
        replay = self._replay(normalized_key, fingerprint, EventMutationResult)
        if replay is not None:
            return EventMutationResult(event=deepcopy(replay.event), idempotent_replay=True)

        if normalized_event_id in self._event_ids:
            raise IdentityConflictError(f"event_id already exists: {normalized_event_id}")

        stream_key = (stream_type, stream_id)
        current_revision = self._stream_revisions.get(stream_key, 0)
        if (
            expected_stream_revision is not None
            and expected_stream_revision != current_revision
        ):
            raise RevisionConflictError(
                "expected stream revision "
                f"{expected_stream_revision}, current revision is {current_revision}"
            )

        event = EventRecord(
            event_id=normalized_event_id,
            stream_type=stream_type,
            stream_id=stream_id,
            event_type=event_type,
            payload=deepcopy(normalized_payload),
            stream_revision=current_revision + 1,
        )
        self._events.append(event)
        self._event_ids[normalized_event_id] = event
        self._stream_revisions[stream_key] = event.stream_revision
        result = EventMutationResult(event=deepcopy(event), idempotent_replay=False)
        self._remember(normalized_key, fingerprint, result)
        return result

    def events_for(
        self,
        stream_type: str,
        stream_id: str,
        *,
        after_revision: int = 0,
        limit: int = 100,
    ) -> tuple[EventRecord, ...]:
        """Return a bounded ordered event stream for deterministic readback/tests."""
        self._validate_resource_identity(stream_type, stream_id)
        if not isinstance(after_revision, int) or isinstance(after_revision, bool) or after_revision < 0:
            raise ValidationError("after_revision must be a non-negative integer")
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 1000:
            raise ValidationError("limit must be an integer from 1 through 1000")
        rows = [
            event
            for event in self._events
            if event.stream_type == stream_type
            and event.stream_id == stream_id
            and event.stream_revision > after_revision
        ]
        rows.sort(key=lambda event: event.stream_revision)
        return tuple(deepcopy(rows[:limit]))

    def _validate_resource_type(self, resource_type: str) -> None:
        if resource_type not in self._resource_types:
            raise ValidationError(f"unknown resource type: {resource_type}")

    def _validate_resource_identity(self, resource_type: str, resource_id: str) -> None:
        self._validate_resource_type(resource_type)
        _validate_id(resource_id, "resource_id")

    def _replay(self, key: str, fingerprint: str, result_type: type) -> object | None:
        prior = self._idempotency.get(key)
        if prior is None:
            return None
        prior_fingerprint, prior_result = prior
        if prior_fingerprint != fingerprint:
            raise IdempotencyConflictError(
                "idempotency key was already used for different material input"
            )
        if not isinstance(prior_result, result_type):
            raise IdempotencyConflictError(
                "idempotency key was already used for a different operation"
            )
        return deepcopy(prior_result)

    def _remember(self, key: str, fingerprint: str, result: object) -> None:
        self._idempotency[key] = (fingerprint, deepcopy(result))


def _validated_type_set(values: Sequence[str], field: str) -> frozenset[str]:
    if isinstance(values, (str, bytes)) or not values:
        raise ValidationError(f"{field} must be a non-empty sequence")
    normalized = frozenset(_validate_token(value, field) for value in values)
    if len(normalized) != len(values):
        raise ValidationError(f"{field} must not contain duplicates")
    return normalized


def _validate_token(value: str, field: str) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise ValidationError(f"{field} must be a non-empty trimmed string")
    if len(value) > 128:
        raise ValidationError(f"{field} must be at most 128 characters")
    return value


def _validate_id(value: str, field: str) -> str:
    normalized = _validate_token(value, field)
    if not _ID_RE.fullmatch(normalized):
        raise ValidationError(
            f"{field} must match {_ID_RE.pattern} for deterministic canonical identity"
        )
    return normalized


def _validate_expected_revision(value: int | None, field: str) -> None:
    if value is None:
        return
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ValidationError(f"{field} must be a non-negative integer or None")


def _normalize_mapping(value: Mapping[str, Any], field: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ValidationError(f"{field} must be a mapping")
    normalized = deepcopy(dict(value))
    try:
        encoded = json.dumps(
            normalized,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise ValidationError(f"{field} must contain JSON-compatible values") from exc
    return json.loads(encoded)


def _fingerprint(material: Mapping[str, Any]) -> str:
    encoded = json.dumps(
        material,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()
