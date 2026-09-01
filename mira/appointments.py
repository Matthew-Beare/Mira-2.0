"""Provider-neutral appointment and provider identity reconciliation for MIRA.

This module consumes already-normalized evidence. It deliberately does not parse
email/images, write Calendar events, schedule reminders, send messages, or infer
medical meaning. Provider identity and appointment-occurrence identity are kept
separate and reconciled only from exact deterministic keys.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
import hashlib
import re
from typing import Any, Mapping, Sequence
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from .structured_state import (
    IdempotencyConflictError,
    IdentityConflictError,
    NotFoundError,
    ResourceRecord,
    RevisionConflictError,
    StructuredStateAdapter,
    StructuredStateError,
    ValidationError as StoreValidationError,
)


PROVIDER_RESOURCE_TYPE = "appointment_provider"
APPOINTMENT_RESOURCE_TYPE = "appointment"
APPOINTMENT_IDENTITY_SCHEMA_VERSION = 1
EVIDENCE_AUTHORITIES = frozenset({"derived", "source", "user_confirmed"})
_AUTHORITY_RANK = {"derived": 0, "source": 1, "user_confirmed": 2}
_TOKEN_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_WS_RE = re.compile(r"\s+")


class AppointmentIdentityError(Exception):
    """Base class for appointment/provider identity failures."""


class AppointmentIdentityValidationError(AppointmentIdentityError):
    """Raised when requested or persisted material is malformed."""


class AppointmentIdentityConflictError(AppointmentIdentityError):
    """Raised when canonical identity, revision, or confirmed truth conflicts."""


class AppointmentIdentityIntegrityError(AppointmentIdentityError):
    """Raised when persisted canonical state is internally inconsistent."""


@dataclass(frozen=True)
class EvidenceRef:
    source_type: str
    source_id: str
    material_sha256: str
    observed_at: str
    authority: str = "source"

    def payload(self) -> dict[str, str]:
        return {
            "source_type": self.source_type,
            "source_id": self.source_id,
            "material_sha256": self.material_sha256,
            "observed_at": self.observed_at,
            "authority": self.authority,
        }

    @property
    def source_key(self) -> str:
        return f"{self.source_type}:{self.source_id}"


@dataclass(frozen=True)
class ProviderCandidate:
    evidence: EvidenceRef
    display_name: str | None = None
    organization: str | None = None
    email: str | None = None
    phone: str | None = None
    specialty_type: str | None = None
    identity_namespace: str | None = None
    identity_value: str | None = None
    canonical_provider_id: str | None = None


@dataclass(frozen=True)
class AppointmentCandidate:
    evidence: EvidenceRef
    provider_id: str
    start_at: str | None = None
    end_at: str | None = None
    timezone: str | None = None
    title: str | None = None
    location: str | None = None
    appointment_type: str | None = None
    identity_namespace: str | None = None
    identity_value: str | None = None
    canonical_appointment_id: str | None = None


@dataclass(frozen=True)
class ProviderView:
    provider_id: str
    revision: int
    identity_keys: tuple[str, ...]
    display_name: str | None
    organization: str | None
    email: str | None
    phone: str | None
    specialty_type: str | None
    field_authority: dict[str, str]
    evidence: tuple[EvidenceRef, ...]


@dataclass(frozen=True)
class AppointmentView:
    appointment_id: str
    revision: int
    identity_keys: tuple[str, ...]
    provider_id: str
    start_at: str | None
    end_at: str | None
    timezone: str | None
    title: str | None
    location: str | None
    appointment_type: str | None
    field_authority: dict[str, str]
    evidence: tuple[EvidenceRef, ...]


@dataclass(frozen=True)
class ProviderReconciliationResult:
    status: str
    provider: ProviderView | None
    reason: str | None = None
    candidate_provider_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class AppointmentReconciliationResult:
    status: str
    appointment: AppointmentView | None
    reason: str | None = None
    candidate_appointment_ids: tuple[str, ...] = ()


class AppointmentIdentityService:
    """Reconcile durable provider and appointment identities from exact evidence."""

    def __init__(
        self,
        adapter: StructuredStateAdapter,
        *,
        provider_resource_type: str = PROVIDER_RESOURCE_TYPE,
        appointment_resource_type: str = APPOINTMENT_RESOURCE_TYPE,
    ) -> None:
        self._adapter = adapter
        self._provider_type = provider_resource_type
        self._appointment_type = appointment_resource_type

    def reconcile_provider(
        self,
        candidate: ProviderCandidate,
        *,
        idempotency_key: str,
    ) -> ProviderReconciliationResult:
        evidence = _evidence(candidate.evidence)
        requested_id = (
            None
            if candidate.canonical_provider_id is None
            else _token(candidate.canonical_provider_id, "canonical_provider_id")
        )
        if requested_id is not None and evidence.authority != "user_confirmed":
            raise AppointmentIdentityValidationError(
                "canonical_provider_id may be supplied only with user_confirmed evidence"
            )
        incoming = {
            "display_name": _optional_text(candidate.display_name, "display_name", 500),
            "organization": _optional_text(candidate.organization, "organization", 500),
            "email": _email(candidate.email),
            "phone": _phone(candidate.phone),
            "specialty_type": _optional_text(candidate.specialty_type, "specialty_type", 500),
        }
        keys = _provider_identity_keys(candidate, incoming)
        providers = self.providers(limit=1000)

        current: ProviderView | None = None
        if requested_id is not None:
            current = self.get_provider(requested_id)
            collisions = _matching_views(providers, keys, exclude_id=requested_id)
            if collisions:
                return ProviderReconciliationResult(
                    status="needs_review",
                    provider=current,
                    reason="confirmed provider identity keys collide with another canonical provider",
                    candidate_provider_ids=tuple(row.provider_id for row in collisions),
                )
        else:
            matches = _matching_views(providers, keys)
            if len(matches) > 1:
                return ProviderReconciliationResult(
                    status="needs_review",
                    provider=None,
                    reason="exact provider evidence matches multiple canonical providers",
                    candidate_provider_ids=tuple(row.provider_id for row in matches),
                )
            if matches:
                current = matches[0]

        if current is None:
            if not keys:
                return ProviderReconciliationResult(
                    status="needs_review",
                    provider=None,
                    reason="provider evidence lacks an exact deterministic identity key",
                )
            provider_id = _deterministic_id("provider", keys[0])
            try:
                existing_by_id = self.get_provider(provider_id)
            except AppointmentIdentityValidationError:
                existing_by_id = None
            if existing_by_id is not None:
                current = existing_by_id
            else:
                payload = _provider_payload(
                    provider_id=provider_id,
                    identity_keys=keys,
                    fields=incoming,
                    field_authority={
                        field: evidence.authority
                        for field, value in incoming.items()
                        if value is not None
                    },
                    evidence=(evidence,),
                )
                created = self._upsert_provider(
                    provider_id,
                    payload,
                    idempotency_key=idempotency_key,
                    expected_revision=0,
                )
                return ProviderReconciliationResult(status="created", provider=created)

        conflict = _evidence_source_conflict(current.evidence, evidence)
        if conflict:
            return ProviderReconciliationResult(
                status="needs_review", provider=current, reason=conflict
            )
        updated_fields, authorities, field_conflict = _merge_fields(
            _provider_fields(current), current.field_authority, incoming, evidence.authority
        )
        if field_conflict:
            return ProviderReconciliationResult(
                status="needs_review", provider=current, reason=field_conflict
            )
        merged_keys = tuple(sorted(set(current.identity_keys).union(keys)))
        new_evidence = _append_evidence(current.evidence, evidence)
        if (
            updated_fields == _provider_fields(current)
            and authorities == current.field_authority
            and merged_keys == current.identity_keys
            and new_evidence == current.evidence
        ):
            return ProviderReconciliationResult(status="replay", provider=current)
        payload = _provider_payload(
            provider_id=current.provider_id,
            identity_keys=merged_keys,
            fields=updated_fields,
            field_authority=authorities,
            evidence=new_evidence,
        )
        updated = self._upsert_provider(
            current.provider_id,
            payload,
            idempotency_key=idempotency_key,
            expected_revision=current.revision,
        )
        return ProviderReconciliationResult(status="updated", provider=updated)

    def reconcile_appointment(
        self,
        candidate: AppointmentCandidate,
        *,
        idempotency_key: str,
    ) -> AppointmentReconciliationResult:
        evidence = _evidence(candidate.evidence)
        requested_id = (
            None
            if candidate.canonical_appointment_id is None
            else _token(candidate.canonical_appointment_id, "canonical_appointment_id")
        )
        if requested_id is not None and evidence.authority != "user_confirmed":
            raise AppointmentIdentityValidationError(
                "canonical_appointment_id may be supplied only with user_confirmed evidence"
            )
        provider_id = _token(candidate.provider_id, "provider_id")
        self.get_provider(provider_id)
        incoming = {
            "provider_id": provider_id,
            "start_at": _optional_timestamp(candidate.start_at, "start_at"),
            "end_at": _optional_timestamp(candidate.end_at, "end_at"),
            "timezone": _optional_timezone(candidate.timezone),
            "title": _optional_text(candidate.title, "title", 1000),
            "location": _optional_text(candidate.location, "location", 1000),
            "appointment_type": _optional_text(candidate.appointment_type, "appointment_type", 500),
        }
        _validate_appointment_timing(incoming)
        keys = _appointment_identity_keys(candidate, incoming)
        appointments = self.appointments(limit=1000)

        current: AppointmentView | None = None
        if requested_id is not None:
            current = self.get_appointment(requested_id)
            collisions = _matching_views(appointments, keys, exclude_id=requested_id)
            if collisions:
                return AppointmentReconciliationResult(
                    status="needs_review",
                    appointment=current,
                    reason="confirmed appointment identity keys collide with another canonical appointment",
                    candidate_appointment_ids=tuple(row.appointment_id for row in collisions),
                )
        else:
            matches = _matching_views(appointments, keys)
            if len(matches) > 1:
                return AppointmentReconciliationResult(
                    status="needs_review",
                    appointment=None,
                    reason="exact appointment evidence matches multiple canonical appointments",
                    candidate_appointment_ids=tuple(row.appointment_id for row in matches),
                )
            if matches:
                current = matches[0]

        if current is None:
            if not keys:
                return AppointmentReconciliationResult(
                    status="needs_review",
                    appointment=None,
                    reason="appointment evidence lacks an explicit identity or provider plus exact start time",
                )
            appointment_id = _deterministic_id("appointment", keys[0])
            try:
                existing_by_id = self.get_appointment(appointment_id)
            except AppointmentIdentityValidationError:
                existing_by_id = None
            if existing_by_id is not None:
                current = existing_by_id
            else:
                payload = _appointment_payload(
                    appointment_id=appointment_id,
                    identity_keys=keys,
                    fields=incoming,
                    field_authority={
                        field: evidence.authority
                        for field, value in incoming.items()
                        if value is not None
                    },
                    evidence=(evidence,),
                )
                created = self._upsert_appointment(
                    appointment_id,
                    payload,
                    idempotency_key=idempotency_key,
                    expected_revision=0,
                )
                return AppointmentReconciliationResult(
                    status="created", appointment=created
                )

        conflict = _evidence_source_conflict(current.evidence, evidence)
        if conflict:
            return AppointmentReconciliationResult(
                status="needs_review", appointment=current, reason=conflict
            )
        updated_fields, authorities, field_conflict = _merge_fields(
            _appointment_fields(current), current.field_authority, incoming, evidence.authority
        )
        if field_conflict:
            return AppointmentReconciliationResult(
                status="needs_review", appointment=current, reason=field_conflict
            )
        _validate_appointment_timing(updated_fields)
        merged_keys = tuple(sorted(set(current.identity_keys).union(keys)))
        new_evidence = _append_evidence(current.evidence, evidence)
        if (
            updated_fields == _appointment_fields(current)
            and authorities == current.field_authority
            and merged_keys == current.identity_keys
            and new_evidence == current.evidence
        ):
            return AppointmentReconciliationResult(status="replay", appointment=current)
        payload = _appointment_payload(
            appointment_id=current.appointment_id,
            identity_keys=merged_keys,
            fields=updated_fields,
            field_authority=authorities,
            evidence=new_evidence,
        )
        updated = self._upsert_appointment(
            current.appointment_id,
            payload,
            idempotency_key=idempotency_key,
            expected_revision=current.revision,
        )
        return AppointmentReconciliationResult(status="updated", appointment=updated)

    def get_provider(self, provider_id: str) -> ProviderView:
        normalized = _token(provider_id, "provider_id")
        try:
            return _provider_view(self._adapter.get(self._provider_type, normalized))
        except NotFoundError as exc:
            raise AppointmentIdentityValidationError(
                f"provider {normalized!r} does not exist"
            ) from exc
        except StoreValidationError as exc:
            raise AppointmentIdentityValidationError(str(exc)) from exc
        except StructuredStateError as exc:
            raise AppointmentIdentityIntegrityError(str(exc)) from exc

    def get_appointment(self, appointment_id: str) -> AppointmentView:
        normalized = _token(appointment_id, "appointment_id")
        try:
            return _appointment_view(self._adapter.get(self._appointment_type, normalized))
        except NotFoundError as exc:
            raise AppointmentIdentityValidationError(
                f"appointment {normalized!r} does not exist"
            ) from exc
        except StoreValidationError as exc:
            raise AppointmentIdentityValidationError(str(exc)) from exc
        except StructuredStateError as exc:
            raise AppointmentIdentityIntegrityError(str(exc)) from exc

    def providers(self, *, limit: int = 100) -> tuple[ProviderView, ...]:
        records = self._query(self._provider_type, limit)
        return tuple(_provider_view(record) for record in records)

    def appointments(self, *, limit: int = 100) -> tuple[AppointmentView, ...]:
        records = self._query(self._appointment_type, limit)
        return tuple(_appointment_view(record) for record in records)

    def _query(self, resource_type: str, limit: int) -> Sequence[ResourceRecord]:
        bounded = _limit(limit)
        try:
            return self._adapter.query(resource_type, limit=bounded)
        except StoreValidationError as exc:
            raise AppointmentIdentityValidationError(str(exc)) from exc
        except StructuredStateError as exc:
            raise AppointmentIdentityIntegrityError(str(exc)) from exc

    def _upsert_provider(
        self,
        provider_id: str,
        payload: Mapping[str, Any],
        *,
        idempotency_key: str,
        expected_revision: int,
    ) -> ProviderView:
        record = self._upsert(
            self._provider_type,
            provider_id,
            payload,
            idempotency_key=idempotency_key,
            expected_revision=expected_revision,
        )
        return _provider_view(record)

    def _upsert_appointment(
        self,
        appointment_id: str,
        payload: Mapping[str, Any],
        *,
        idempotency_key: str,
        expected_revision: int,
    ) -> AppointmentView:
        record = self._upsert(
            self._appointment_type,
            appointment_id,
            payload,
            idempotency_key=idempotency_key,
            expected_revision=expected_revision,
        )
        return _appointment_view(record)

    def _upsert(
        self,
        resource_type: str,
        resource_id: str,
        payload: Mapping[str, Any],
        *,
        idempotency_key: str,
        expected_revision: int,
    ) -> ResourceRecord:
        try:
            result = self._adapter.upsert(
                resource_type,
                resource_id,
                payload,
                idempotency_key=_token(idempotency_key, "idempotency_key"),
                expected_revision=expected_revision,
            )
        except (RevisionConflictError, IdempotencyConflictError, IdentityConflictError) as exc:
            raise AppointmentIdentityConflictError(str(exc)) from exc
        except StoreValidationError as exc:
            raise AppointmentIdentityValidationError(str(exc)) from exc
        except StructuredStateError as exc:
            raise AppointmentIdentityIntegrityError(str(exc)) from exc
        return result.record


def _provider_identity_keys(
    candidate: ProviderCandidate, fields: Mapping[str, str | None]
) -> tuple[str, ...]:
    keys: list[str] = []
    explicit = _explicit_identity(candidate.identity_namespace, candidate.identity_value)
    if explicit is not None:
        keys.append(explicit)
    if fields["email"] is not None:
        keys.append(f"email:{fields['email']}")
    phone_key = _phone_identity(fields["phone"])
    if phone_key is not None:
        keys.append(phone_key)
    if fields["organization"] is not None and fields["display_name"] is not None:
        keys.append(
            "org-name:"
            f"{_normalized_text(fields['organization'])}|{_normalized_text(fields['display_name'])}"
        )
    return tuple(sorted(set(keys)))


def _appointment_identity_keys(
    candidate: AppointmentCandidate, fields: Mapping[str, str | None]
) -> tuple[str, ...]:
    keys: list[str] = []
    explicit = _explicit_identity(candidate.identity_namespace, candidate.identity_value)
    if explicit is not None:
        keys.append(explicit)
    if fields["start_at"] is not None:
        keys.append(f"provider-start:{fields['provider_id']}|{fields['start_at']}")
    return tuple(sorted(set(keys)))


def _explicit_identity(namespace: str | None, value: str | None) -> str | None:
    if namespace is None and value is None:
        return None
    if namespace is None or value is None:
        raise AppointmentIdentityValidationError(
            "identity_namespace and identity_value must be supplied together"
        )
    return f"external:{_token(namespace, 'identity_namespace')}:{_text(value, 'identity_value', 500)}"


def _matching_views(views, keys: tuple[str, ...], exclude_id: str | None = None):
    wanted = set(keys)
    if not wanted:
        return []
    matches = []
    for row in views:
        row_id = getattr(row, "appointment_id", None)
        if row_id is None:
            row_id = getattr(row, "provider_id", None)
        if exclude_id is not None and row_id == exclude_id:
            continue
        if wanted.intersection(row.identity_keys):
            matches.append(row)
    return matches


def _merge_fields(
    current: Mapping[str, str | None],
    current_authority: Mapping[str, str],
    incoming: Mapping[str, str | None],
    incoming_authority: str,
) -> tuple[dict[str, str | None], dict[str, str], str | None]:
    fields = dict(current)
    authorities = dict(current_authority)
    for field, value in incoming.items():
        if value is None:
            continue
        prior = fields.get(field)
        prior_authority = authorities.get(field)
        if prior is None:
            fields[field] = value
            authorities[field] = incoming_authority
            continue
        if prior == value:
            if (
                prior_authority is None
                or _AUTHORITY_RANK[incoming_authority] > _AUTHORITY_RANK[prior_authority]
            ):
                authorities[field] = incoming_authority
            continue
        if (
            prior_authority is None
            or _AUTHORITY_RANK[incoming_authority] > _AUTHORITY_RANK[prior_authority]
        ):
            fields[field] = value
            authorities[field] = incoming_authority
            continue
        if incoming_authority == "user_confirmed" and prior_authority == "user_confirmed":
            raise AppointmentIdentityConflictError(
                f"conflicting user-confirmed values for {field}"
            )
        if _AUTHORITY_RANK[incoming_authority] == _AUTHORITY_RANK[prior_authority]:
            return fields, authorities, f"conflicting equal-authority values for {field}"
    return fields, authorities, None


def _evidence_source_conflict(
    existing: Sequence[EvidenceRef], incoming: EvidenceRef
) -> str | None:
    for prior in existing:
        if (
            prior.source_key == incoming.source_key
            and prior.material_sha256 != incoming.material_sha256
        ):
            return "one immutable evidence source identity was supplied with different material"
    return None


def _append_evidence(
    existing: Sequence[EvidenceRef], incoming: EvidenceRef
) -> tuple[EvidenceRef, ...]:
    if any(prior == incoming for prior in existing):
        return tuple(existing)
    rows = [*existing, incoming]
    rows.sort(
        key=lambda row: (
            row.observed_at,
            row.source_type,
            row.source_id,
            row.material_sha256,
        )
    )
    return tuple(rows)


def _provider_fields(view: ProviderView) -> dict[str, str | None]:
    return {
        "display_name": view.display_name,
        "organization": view.organization,
        "email": view.email,
        "phone": view.phone,
        "specialty_type": view.specialty_type,
    }


def _appointment_fields(view: AppointmentView) -> dict[str, str | None]:
    return {
        "provider_id": view.provider_id,
        "start_at": view.start_at,
        "end_at": view.end_at,
        "timezone": view.timezone,
        "title": view.title,
        "location": view.location,
        "appointment_type": view.appointment_type,
    }


def _provider_payload(
    *,
    provider_id: str,
    identity_keys: Sequence[str],
    fields: Mapping[str, str | None],
    field_authority: Mapping[str, str],
    evidence: Sequence[EvidenceRef],
) -> dict[str, Any]:
    return _canonical_payload(
        identity_field="provider_id",
        identity_value=provider_id,
        identity_keys=identity_keys,
        fields=fields,
        field_authority=field_authority,
        evidence=evidence,
    )


def _appointment_payload(
    *,
    appointment_id: str,
    identity_keys: Sequence[str],
    fields: Mapping[str, str | None],
    field_authority: Mapping[str, str],
    evidence: Sequence[EvidenceRef],
) -> dict[str, Any]:
    return _canonical_payload(
        identity_field="appointment_id",
        identity_value=appointment_id,
        identity_keys=identity_keys,
        fields=fields,
        field_authority=field_authority,
        evidence=evidence,
    )


def _canonical_payload(
    *,
    identity_field: str,
    identity_value: str,
    identity_keys: Sequence[str],
    fields: Mapping[str, str | None],
    field_authority: Mapping[str, str],
    evidence: Sequence[EvidenceRef],
) -> dict[str, Any]:
    canonical_keys = tuple(
        sorted({_text(key, "identity_key", 1000) for key in identity_keys})
    )
    canonical_evidence = tuple(_evidence(item) for item in evidence)
    authorities: dict[str, str] = {}
    for field, authority in field_authority.items():
        if field not in fields or fields[field] is None:
            raise AppointmentIdentityValidationError(
                "field_authority cannot reference a missing field"
            )
        authorities[_text(field, "field_authority field", 128)] = _authority(authority)
    return {
        "schema_version": APPOINTMENT_IDENTITY_SCHEMA_VERSION,
        identity_field: _token(identity_value, identity_field),
        "identity_keys": list(canonical_keys),
        **dict(fields),
        "field_authority": dict(sorted(authorities.items())),
        "evidence": [item.payload() for item in canonical_evidence],
    }


def _provider_view(record: ResourceRecord) -> ProviderView:
    payload = deepcopy(record.payload)
    provider_id, keys, authorities, evidence = _parse_common(
        record, payload, "provider_id"
    )
    fields = {
        "display_name": _optional_text(payload.get("display_name"), "display_name", 500),
        "organization": _optional_text(payload.get("organization"), "organization", 500),
        "email": _email(payload.get("email")),
        "phone": _phone(payload.get("phone")),
        "specialty_type": _optional_text(
            payload.get("specialty_type"), "specialty_type", 500
        ),
    }
    normalized = _provider_payload(
        provider_id=provider_id,
        identity_keys=keys,
        fields=fields,
        field_authority=authorities,
        evidence=evidence,
    )
    if payload != normalized:
        raise AppointmentIdentityIntegrityError(
            "persisted provider payload is noncanonical or malformed"
        )
    return ProviderView(
        provider_id,
        record.revision,
        keys,
        field_authority=authorities,
        evidence=evidence,
        **fields,
    )


def _appointment_view(record: ResourceRecord) -> AppointmentView:
    payload = deepcopy(record.payload)
    appointment_id, keys, authorities, evidence = _parse_common(
        record, payload, "appointment_id"
    )
    extended_timing = "end_at" in payload or "timezone" in payload
    fields = {
        "provider_id": _token(payload.get("provider_id"), "provider_id"),
        "start_at": _optional_timestamp(payload.get("start_at"), "start_at"),
        "end_at": _optional_timestamp(payload.get("end_at"), "end_at"),
        "timezone": _optional_timezone(payload.get("timezone")),
        "title": _optional_text(payload.get("title"), "title", 1000),
        "location": _optional_text(payload.get("location"), "location", 1000),
        "appointment_type": _optional_text(
            payload.get("appointment_type"), "appointment_type", 500
        ),
    }
    _validate_appointment_timing(fields)
    normalized_fields = fields
    if not extended_timing:
        normalized_fields = {
            key: value
            for key, value in fields.items()
            if key not in {"end_at", "timezone"}
        }
    normalized = _appointment_payload(
        appointment_id=appointment_id,
        identity_keys=keys,
        fields=normalized_fields,
        field_authority=authorities,
        evidence=evidence,
    )
    if payload != normalized:
        raise AppointmentIdentityIntegrityError(
            "persisted appointment payload is noncanonical or malformed"
        )
    return AppointmentView(
        appointment_id,
        record.revision,
        keys,
        field_authority=authorities,
        evidence=evidence,
        **fields,
    )


def _parse_common(
    record: ResourceRecord,
    payload: Mapping[str, Any],
    identity_field: str,
) -> tuple[str, tuple[str, ...], dict[str, str], tuple[EvidenceRef, ...]]:
    if payload.get("schema_version") != APPOINTMENT_IDENTITY_SCHEMA_VERSION:
        raise AppointmentIdentityIntegrityError(
            "unsupported appointment-identity schema version"
        )
    identity = _token(payload.get(identity_field), identity_field)
    if identity != record.resource_id:
        raise AppointmentIdentityIntegrityError("canonical identity/readback mismatch")
    raw_keys = payload.get("identity_keys")
    if not isinstance(raw_keys, list):
        raise AppointmentIdentityIntegrityError("identity_keys must be a list")
    keys = tuple(sorted({_text(value, "identity_key", 1000) for value in raw_keys}))
    if not keys:
        raise AppointmentIdentityIntegrityError(
            "canonical identity requires at least one identity key"
        )
    raw_authority = payload.get("field_authority")
    if not isinstance(raw_authority, Mapping):
        raise AppointmentIdentityIntegrityError("field_authority must be an object")
    authorities = {
        _text(field, "field_authority field", 128): _authority(value)
        for field, value in raw_authority.items()
    }
    raw_evidence = payload.get("evidence")
    if not isinstance(raw_evidence, list) or not raw_evidence:
        raise AppointmentIdentityIntegrityError("canonical identity requires evidence")
    evidence = tuple(_evidence(value) for value in raw_evidence)
    return identity, keys, authorities, evidence


def _evidence(value: EvidenceRef | Mapping[str, Any]) -> EvidenceRef:
    material = value.payload() if isinstance(value, EvidenceRef) else dict(value)
    expected = {
        "source_type",
        "source_id",
        "material_sha256",
        "observed_at",
        "authority",
    }
    if set(material) != expected:
        raise AppointmentIdentityValidationError(
            "evidence fields are incomplete or unexpected"
        )
    digest = _text(material["material_sha256"], "material_sha256", 64).lower()
    if not _SHA256_RE.fullmatch(digest):
        raise AppointmentIdentityValidationError(
            "material_sha256 must be a lowercase SHA-256 hex digest"
        )
    return EvidenceRef(
        source_type=_token(material["source_type"], "source_type"),
        source_id=_text(material["source_id"], "source_id", 500),
        material_sha256=digest,
        observed_at=_timestamp(material["observed_at"], "observed_at"),
        authority=_authority(material["authority"]),
    )


def _authority(value: object) -> str:
    if not isinstance(value, str) or value not in EVIDENCE_AUTHORITIES:
        raise AppointmentIdentityValidationError(
            "authority must be one of derived, source, or user_confirmed"
        )
    return value


def _deterministic_id(prefix: str, identity_key: str) -> str:
    digest = hashlib.sha256(identity_key.encode("utf-8")).hexdigest()[:24]
    return f"{prefix}-{digest}"


def _token(value: object, field: str) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise AppointmentIdentityValidationError(
            f"{field} must be a non-empty trimmed string"
        )
    if not _TOKEN_RE.fullmatch(value):
        raise AppointmentIdentityValidationError(
            f"{field} must match {_TOKEN_RE.pattern}"
        )
    return value


def _text(value: object, field: str, max_length: int) -> str:
    if not isinstance(value, str) or not value.strip():
        raise AppointmentIdentityValidationError(f"{field} must be non-empty text")
    trimmed = _WS_RE.sub(" ", value.strip())
    if len(trimmed) > max_length:
        raise AppointmentIdentityValidationError(
            f"{field} must be at most {max_length} characters"
        )
    return trimmed


def _optional_text(value: object, field: str, max_length: int) -> str | None:
    return None if value is None else _text(value, field, max_length)


def _normalized_text(value: str) -> str:
    return _WS_RE.sub(" ", value.strip()).casefold()


def _email(value: object) -> str | None:
    if value is None:
        return None
    text = _text(value, "email", 320).casefold()
    if text.count("@") != 1 or text.startswith("@") or text.endswith("@"):
        raise AppointmentIdentityValidationError("email must contain one non-edge @")
    return text


def _phone(value: object) -> str | None:
    if value is None:
        return None
    return _text(value, "phone", 100)


def _phone_identity(value: str | None) -> str | None:
    if value is None:
        return None
    digits = "".join(ch for ch in value if ch.isdigit())
    if 7 <= len(digits) <= 15 and not re.search(
        r"(?:ext|x)\s*\d", value, re.IGNORECASE
    ):
        return f"phone:{digits}"
    return None


def _timestamp(value: object, field: str) -> str:
    text = _text(value, field, 100)
    raw = text[:-1] + "+00:00" if text.endswith("Z") else text
    try:
        parsed = datetime.fromisoformat(raw)
    except ValueError as exc:
        raise AppointmentIdentityValidationError(
            f"{field} must be valid ISO-8601"
        ) from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise AppointmentIdentityValidationError(
            f"{field} must include a UTC offset"
        )
    return parsed.isoformat()


def _optional_timestamp(value: object, field: str) -> str | None:
    return None if value is None else _timestamp(value, field)


def _optional_timezone(value: object) -> str | None:
    if value is None:
        return None
    name = _text(value, "timezone", 100)
    try:
        ZoneInfo(name)
    except ZoneInfoNotFoundError as exc:
        raise AppointmentIdentityValidationError(
            f"timezone is not a known IANA timezone: {name}"
        ) from exc
    return name


def _validate_appointment_timing(fields: Mapping[str, str | None]) -> None:
    start_at = fields.get("start_at")
    end_at = fields.get("end_at")
    timezone = fields.get("timezone")
    if end_at is not None and start_at is None:
        raise AppointmentIdentityValidationError(
            "end_at cannot be supplied without start_at"
        )
    start = None if start_at is None else datetime.fromisoformat(start_at)
    end = None if end_at is None else datetime.fromisoformat(end_at)
    if start is not None and end is not None and end <= start:
        raise AppointmentIdentityValidationError(
            "end_at must be later than start_at"
        )
    if timezone is None:
        return
    zone = ZoneInfo(timezone)
    if start is not None and start.astimezone(zone).utcoffset() != start.utcoffset():
        raise AppointmentIdentityValidationError(
            "start_at offset does not match timezone"
        )
    if end is not None and end.astimezone(zone).utcoffset() != end.utcoffset():
        raise AppointmentIdentityValidationError(
            "end_at offset does not match timezone"
        )


def _limit(value: object) -> int:
    if (
        not isinstance(value, int)
        or isinstance(value, bool)
        or not 1 <= value <= 1000
    ):
        raise AppointmentIdentityValidationError(
            "limit must be an integer from 1 through 1000"
        )
    return value


__all__ = [
    "APPOINTMENT_IDENTITY_SCHEMA_VERSION",
    "APPOINTMENT_RESOURCE_TYPE",
    "AppointmentCandidate",
    "AppointmentIdentityConflictError",
    "AppointmentIdentityError",
    "AppointmentIdentityIntegrityError",
    "AppointmentIdentityService",
    "AppointmentIdentityValidationError",
    "AppointmentReconciliationResult",
    "AppointmentView",
    "EVIDENCE_AUTHORITIES",
    "EvidenceRef",
    "PROVIDER_RESOURCE_TYPE",
    "ProviderCandidate",
    "ProviderReconciliationResult",
    "ProviderView",
]
