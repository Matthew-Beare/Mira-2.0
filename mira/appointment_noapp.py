"""Direct stock-ChatGPT appointment capture planning for Personal MIRA.

This module bridges direct user text/image evidence into the provider-neutral
appointment intake core and the existing native Google Workspace mutation
contract. It performs no Gmail fetching, OCR/model execution, provider writes,
Calendar authorization, reminders, outbound contact, or medical inference.

The runtime/model supplies a structured ``AppointmentExtraction``. This module
owns deterministic source provenance, fail-closed clarification, canonical
snapshot reconciliation, Personal authority-binding preflight, native Workspace
upsert planning, and exact readback verification.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, fields
import hashlib
import json
import re
from typing import Any, Mapping, Sequence

from .appointment_intake import (
    AppointmentExtraction,
    AppointmentIntakeResult,
    AppointmentIntakeService,
    CalendarProjectionTarget,
)
from .appointments import (
    APPOINTMENT_RESOURCE_TYPE,
    PROVIDER_RESOURCE_TYPE,
    AppointmentIdentityService,
    EvidenceRef,
)
from .calendar_projection import CalendarProjectionService
from .service_state import ServiceStateView
from .structured_state import (
    HealthStatus,
    IdempotencyConflictError,
    IdentityConflictError,
    MutationResult,
    NotFoundError,
    ResourceRecord,
    RevisionConflictError,
    SchemaInfo,
    ValidationError,
)
from .workspace_native import (
    WorkspaceIdempotencyRecord,
    WorkspaceReadbackError,
    WorkspaceUpsertPlan,
    plan_workspace_upsert,
    verify_workspace_upsert_readback,
)


PERSONAL_AUTHORITY_ID = "google-sheets-personal"
PERSONAL_SCHEMA_VERSION = "mira-structured-state-v1"
DIRECT_SOURCE_TYPES = frozenset({"text", "image"})
FINGERPRINT_EXACT_TEXT = "exact_text_sha256"
FINGERPRINT_RAW_IMAGE = "raw_file_sha256"
FINGERPRINT_DERIVED_EXTRACTION = "normalized_extraction_sha256_v1"
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_WS_RE = re.compile(r"\s+")

_REQUIRED_BINDINGS = (
    (PROVIDER_RESOURCE_TYPE, "binding-appointment-provider"),
    (APPOINTMENT_RESOURCE_TYPE, "binding-appointment"),
    ("calendar_projection", "binding-calendar-projection"),
)


class AppointmentNoAppError(Exception):
    """Base class for direct no-app appointment planning failures."""


class AppointmentNoAppValidationError(AppointmentNoAppError):
    """Raised when direct evidence or provider-readback input is malformed."""


class AppointmentNoAppIntegrityError(AppointmentNoAppError):
    """Raised when persisted Workspace state contradicts canonical invariants."""


@dataclass(frozen=True)
class DirectAppointmentEvidence:
    """Runtime-visible direct evidence without copying raw material into state."""

    source_type: str
    source_ref: str
    observed_at: str
    authority: str = "source"
    text_material: str | None = None
    raw_file_sha256: str | None = None


@dataclass(frozen=True)
class DirectEvidenceObservation:
    evidence: EvidenceRef
    source_ref: str
    fingerprint_basis: str


@dataclass(frozen=True)
class SnapshotMutation:
    resource_type: str
    resource_id: str
    payload: Mapping[str, Any]
    idempotency_key: str
    expected_revision: int
    result_record: ResourceRecord


@dataclass(frozen=True)
class AppointmentBindingPlan:
    """Missing Personal appointment data-class bindings to add atomically."""

    plans: tuple[WorkspaceUpsertPlan, ...]

    @property
    def idempotent_replay(self) -> bool:
        return not self.plans

    def batch_update_requests(
        self,
        *,
        resources_sheet_id: int,
        idempotency_sheet_id: int,
        timestamp: str,
    ) -> tuple[dict[str, object], ...]:
        requests: list[dict[str, object]] = []
        for plan in self.plans:
            requests.extend(
                plan.batch_update_requests(
                    resources_sheet_id=resources_sheet_id,
                    idempotency_sheet_id=idempotency_sheet_id,
                    timestamp=timestamp,
                )
            )
        return tuple(requests)


@dataclass(frozen=True)
class DirectAppointmentPlan:
    """One direct evidence result plus exact native Workspace mutations."""

    observation: DirectEvidenceObservation
    intake_result: AppointmentIntakeResult
    workspace_plans: tuple[WorkspaceUpsertPlan, ...]
    review_question: str | None = None

    @property
    def needs_review(self) -> bool:
        return self.intake_result.status == "needs_review"

    @property
    def idempotent_replay(self) -> bool:
        return not self.workspace_plans

    def batch_update_requests(
        self,
        *,
        resources_sheet_id: int,
        idempotency_sheet_id: int,
        timestamp: str,
    ) -> tuple[dict[str, object], ...]:
        requests: list[dict[str, object]] = []
        for plan in self.workspace_plans:
            requests.extend(
                plan.batch_update_requests(
                    resources_sheet_id=resources_sheet_id,
                    idempotency_sheet_id=idempotency_sheet_id,
                    timestamp=timestamp,
                )
            )
        return tuple(requests)


def build_direct_evidence(
    source: DirectAppointmentEvidence,
    extraction: AppointmentExtraction,
) -> DirectEvidenceObservation:
    """Build provenance-honest ``EvidenceRef`` material for direct input.

    Text fingerprints hash exact user-provided text. Image fingerprints use a
    verified raw-file SHA-256 only when the runtime actually supplies one;
    otherwise they hash normalized extraction material and label that basis in
    the stable source identity instead of pretending image bytes were hashed.
    """

    if not isinstance(source, DirectAppointmentEvidence):
        raise AppointmentNoAppValidationError(
            "source must be DirectAppointmentEvidence"
        )
    if not isinstance(extraction, AppointmentExtraction):
        raise AppointmentNoAppValidationError(
            "extraction must be AppointmentExtraction"
        )
    source_type = _token(source.source_type, "source_type")
    if source_type not in DIRECT_SOURCE_TYPES:
        raise AppointmentNoAppValidationError(
            "direct appointment source_type must be text or image"
        )
    source_ref = _text(source.source_ref, "source_ref", 400)
    observed_at = _text(source.observed_at, "observed_at", 100)
    authority = _token(source.authority, "authority")

    if source_type == "text":
        if source.raw_file_sha256 is not None:
            raise AppointmentNoAppValidationError(
                "text evidence cannot declare raw_file_sha256"
            )
        if not isinstance(source.text_material, str) or not source.text_material:
            raise AppointmentNoAppValidationError(
                "text evidence requires exact non-empty text_material"
            )
        digest = hashlib.sha256(source.text_material.encode("utf-8")).hexdigest()
        basis = FINGERPRINT_EXACT_TEXT
    else:
        if source.text_material is not None:
            raise AppointmentNoAppValidationError(
                "image evidence must not copy image/OCR text into text_material"
            )
        if source.raw_file_sha256 is not None:
            digest = _sha256(source.raw_file_sha256, "raw_file_sha256")
            basis = FINGERPRINT_RAW_IMAGE
        else:
            digest = hashlib.sha256(
                _canonical_json(_extraction_material(extraction)).encode("utf-8")
            ).hexdigest()
            basis = FINGERPRINT_DERIVED_EXTRACTION

    source_id = f"{source_ref}|fingerprint_basis={basis}"
    if len(source_id) > 500:
        raise AppointmentNoAppValidationError(
            "source_ref is too long after fingerprint-basis annotation"
        )
    return DirectEvidenceObservation(
        evidence=EvidenceRef(
            source_type=source_type,
            source_id=source_id,
            material_sha256=digest,
            observed_at=observed_at,
            authority=authority,
        ),
        source_ref=source_ref,
        fingerprint_basis=basis,
    )


def plan_appointment_workspace_bindings(
    *,
    resource_rows: Sequence[tuple[int, ResourceRecord]],
    idempotency_rows: Sequence[WorkspaceIdempotencyRecord],
) -> AppointmentBindingPlan:
    """Plan missing appointment bindings after validating Personal authority.

    Historic first-run entity bootstrap remains untouched. This function is a
    backward-compatible enrichment step for clean or existing Personal state.
    Exact existing bindings are replay/no-write; conflicting or duplicated
    routing fails closed.
    """

    rows = tuple(resource_rows)
    authority_rows = [
        record
        for _, record in rows
        if record.resource_type == "authority"
        and record.resource_id == PERSONAL_AUTHORITY_ID
    ]
    if len(authority_rows) != 1:
        raise AppointmentNoAppIntegrityError(
            "Personal Google authority must exist exactly once before appointment binding"
        )
    authority = authority_rows[0]
    if (
        authority.payload.get("adapter_key") != "google-sheets"
        or authority.payload.get("enabled") is not True
        or authority.payload.get("verified") is not True
        or authority.payload.get("schema_version") != PERSONAL_SCHEMA_VERSION
    ):
        raise AppointmentNoAppIntegrityError(
            "Personal Google authority is not enabled, verified, schema-compatible google-sheets"
        )

    plans: list[WorkspaceUpsertPlan] = []
    for data_class, binding_id in _REQUIRED_BINDINGS:
        expected_payload = {
            "authority_id": PERSONAL_AUTHORITY_ID,
            "data_class": data_class,
        }
        matching = [
            record
            for _, record in rows
            if record.resource_type == "authority_binding"
            and record.payload.get("data_class") == data_class
        ]
        if len(matching) > 1:
            raise AppointmentNoAppIntegrityError(
                f"duplicate authority bindings for {data_class}"
            )
        if matching:
            current = matching[0]
            if current.resource_id != binding_id or dict(current.payload) != expected_payload:
                raise AppointmentNoAppIntegrityError(
                    f"{data_class} is bound to conflicting canonical authority state"
                )
            continue

        plan = plan_workspace_upsert(
            "authority_binding",
            binding_id,
            expected_payload,
            idempotency_key=f"bootstrap-binding-{data_class.replace('_', '-')}",
            expected_revision=0,
            resource_rows=rows,
            idempotency_rows=idempotency_rows,
        )
        if plan.idempotent_replay:
            raise AppointmentNoAppIntegrityError(
                f"{data_class} binding idempotency exists without its Resource row"
            )
        plans.append(plan)
    return AppointmentBindingPlan(plans=tuple(plans))


def verify_appointment_workspace_bindings(
    *, resource_rows: Sequence[tuple[int, ResourceRecord]]
) -> None:
    """Require exact post-write routing readback for appointment data classes."""

    rows = tuple(resource_rows)
    for data_class, binding_id in _REQUIRED_BINDINGS:
        matches = [
            record
            for _, record in rows
            if record.resource_type == "authority_binding"
            and record.payload.get("data_class") == data_class
        ]
        expected = {
            "authority_id": PERSONAL_AUTHORITY_ID,
            "data_class": data_class,
        }
        if (
            len(matches) != 1
            or matches[0].resource_id != binding_id
            or dict(matches[0].payload) != expected
        ):
            raise WorkspaceReadbackError(
                f"appointment authority binding readback mismatch for {data_class}"
            )


def plan_direct_appointment_intake(
    source: DirectAppointmentEvidence,
    extraction: AppointmentExtraction,
    *,
    logical_key: str,
    resource_rows: Sequence[tuple[int, ResourceRecord]],
    idempotency_rows: Sequence[WorkspaceIdempotencyRecord],
    service_state: ServiceStateView | None = None,
    projection_target: CalendarProjectionTarget | None = None,
    calendar_projection: CalendarProjectionService | None = None,
) -> DirectAppointmentPlan:
    """Dry-run real CAL-005/CAL-008 logic and produce native Workspace plans."""

    key = _token(logical_key, "logical_key")
    observation = build_direct_evidence(source, extraction)
    snapshot = _PlanningSnapshotAdapter(
        record
        for _, record in resource_rows
        if record.resource_type in {PROVIDER_RESOURCE_TYPE, APPOINTMENT_RESOURCE_TYPE}
    )
    identity = AppointmentIdentityService(snapshot)
    intake = AppointmentIntakeService(
        identity, calendar_projection=calendar_projection
    )
    result = intake.intake(
        observation.evidence,
        extraction,
        idempotency_key=key,
        service_state=service_state,
        projection_target=projection_target,
    )

    native_plans: list[WorkspaceUpsertPlan] = []
    rows = tuple(resource_rows)
    for mutation in snapshot.mutations:
        plan = plan_workspace_upsert(
            mutation.resource_type,
            mutation.resource_id,
            mutation.payload,
            idempotency_key=mutation.idempotency_key,
            expected_revision=mutation.expected_revision,
            resource_rows=rows,
            idempotency_rows=idempotency_rows,
        )
        if plan.record != mutation.result_record:
            raise AppointmentNoAppIntegrityError(
                "native Workspace plan differs from canonical intake reconciliation result"
            )
        native_plans.append(plan)

    question = None
    if result.status == "needs_review":
        question = _review_question(result)
    return DirectAppointmentPlan(
        observation=observation,
        intake_result=result,
        workspace_plans=tuple(native_plans),
        review_question=question,
    )


def verify_direct_appointment_readback(
    plan: DirectAppointmentPlan,
    *,
    resource_rows: Sequence[tuple[int, ResourceRecord]],
    idempotency_rows: Sequence[WorkspaceIdempotencyRecord],
) -> None:
    """Require exact native Google Resource + idempotency readback for every write."""

    if not isinstance(plan, DirectAppointmentPlan):
        raise AppointmentNoAppValidationError("plan must be DirectAppointmentPlan")
    for native_plan in plan.workspace_plans:
        verify_workspace_upsert_readback(
            native_plan,
            resource_rows=resource_rows,
            idempotency_rows=idempotency_rows,
        )


class _PlanningSnapshotAdapter:
    """In-process snapshot used only to run canonical reconciliation dry-runs."""

    def __init__(self, records) -> None:
        self._records: dict[tuple[str, str], ResourceRecord] = {}
        self._idempotency: dict[str, tuple[str, MutationResult]] = {}
        self._mutations: list[SnapshotMutation] = []
        for record in records:
            if not isinstance(record, ResourceRecord):
                raise AppointmentNoAppValidationError(
                    "resource_rows must contain ResourceRecord values"
                )
            key = (record.resource_type, record.resource_id)
            if key in self._records:
                raise IdentityConflictError(
                    f"duplicate persisted resource identity: {record.resource_type}:{record.resource_id}"
                )
            self._records[key] = deepcopy(record)

    @property
    def mutations(self) -> tuple[SnapshotMutation, ...]:
        return tuple(self._mutations)

    def health(self) -> HealthStatus:
        return HealthStatus(
            ok=True,
            adapter="appointment-noapp-snapshot",
            schema_version=PERSONAL_SCHEMA_VERSION,
        )

    def schema(self) -> SchemaInfo:
        return SchemaInfo(
            schema_version=PERSONAL_SCHEMA_VERSION,
            resource_types=(APPOINTMENT_RESOURCE_TYPE, PROVIDER_RESOURCE_TYPE),
            event_types=(),
        )

    def get(self, resource_type: str, resource_id: str) -> ResourceRecord:
        try:
            return deepcopy(self._records[(resource_type, resource_id)])
        except KeyError as exc:
            raise NotFoundError(
                f"{resource_type}:{resource_id} does not exist"
            ) from exc

    def query(
        self,
        resource_type: str,
        *,
        filters: Mapping[str, Any] | None = None,
        limit: int = 100,
    ) -> tuple[ResourceRecord, ...]:
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 1000:
            raise ValidationError("limit must be an integer from 1 through 1000")
        wanted = {} if filters is None else dict(filters)
        rows = [
            record
            for (candidate_type, _), record in self._records.items()
            if candidate_type == resource_type
            and all(record.payload.get(key) == value for key, value in wanted.items())
        ]
        rows.sort(key=lambda record: record.resource_id)
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
        if expected_revision is None:
            raise ValidationError(
                "appointment no-app snapshot requires explicit expected_revision"
            )
        normalized = json.loads(_canonical_json(dict(payload)))
        fingerprint = hashlib.sha256(
            _canonical_json(
                {
                    "operation": "upsert",
                    "resource_type": resource_type,
                    "resource_id": resource_id,
                    "payload": normalized,
                    "expected_revision": expected_revision,
                }
            ).encode("utf-8")
        ).hexdigest()
        if idempotency_key in self._idempotency:
            stored_hash, stored_result = self._idempotency[idempotency_key]
            if stored_hash != fingerprint:
                raise IdempotencyConflictError(
                    "snapshot idempotency key reused for different material"
                )
            return MutationResult(
                record=deepcopy(stored_result.record), idempotent_replay=True
            )

        current = self._records.get((resource_type, resource_id))
        current_revision = 0 if current is None else current.revision
        if current_revision != expected_revision:
            raise RevisionConflictError(
                f"expected revision {expected_revision}, current revision is {current_revision}"
            )
        record = ResourceRecord(
            resource_type=resource_type,
            resource_id=resource_id,
            payload=deepcopy(normalized),
            revision=current_revision + 1,
        )
        self._records[(resource_type, resource_id)] = record
        result = MutationResult(record=deepcopy(record), idempotent_replay=False)
        self._idempotency[idempotency_key] = (fingerprint, result)
        self._mutations.append(
            SnapshotMutation(
                resource_type=resource_type,
                resource_id=resource_id,
                payload=deepcopy(normalized),
                idempotency_key=idempotency_key,
                expected_revision=expected_revision,
                result_record=deepcopy(record),
            )
        )
        return result

    def append_event(self, *args, **kwargs):
        raise ValidationError("appointment no-app snapshot does not append events")

    def events_for(self, *args, **kwargs):
        return ()


def _extraction_material(extraction: AppointmentExtraction) -> dict[str, object]:
    material: dict[str, object] = {}
    for field in fields(AppointmentExtraction):
        value = getattr(extraction, field.name)
        if isinstance(value, Mapping):
            material[field.name] = {
                str(key): value[key] for key in sorted(value, key=str)
            }
        else:
            material[field.name] = value
    return material


def _review_question(result: AppointmentIntakeResult) -> str:
    reasons = " ".join(result.review_reasons).lower()
    if "source" in reasons and ("different" in reasons or "conflict" in reasons):
        return (
            "This source was already recorded with different appointment details. "
            "Which version should MIRA treat as correct?"
        )
    if "multiple canonical providers" in reasons or "multiple canonical provider" in reasons:
        return "I found more than one exact provider match. Which provider is this appointment with?"
    if "provider" in reasons and (
        "identity" in reasons or "exact" in reasons or "incomplete" in reasons
    ):
        return (
            "Which provider or clinic is this appointment with? Please include a provider "
            "email, phone number, or exact organization and provider name."
        )
    if "multiple canonical appointments" in reasons or "multiple canonical appointment" in reasons:
        return "I found more than one exact matching appointment. Which occurrence should I update?"
    if "start time" in reasons or "occurrence" in reasons:
        return "What is the exact appointment date and time, including timezone?"
    reason = result.review_reasons[0] if result.review_reasons else "appointment details are ambiguous"
    return f"I need one clarification before saving this appointment: {reason}"


def _canonical_json(value: object) -> str:
    try:
        return json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise AppointmentNoAppValidationError(
            "appointment material must be JSON-compatible"
        ) from exc


def _text(value: object, field: str, max_length: int) -> str:
    if not isinstance(value, str) or not value.strip():
        raise AppointmentNoAppValidationError(f"{field} must be non-empty text")
    text = _WS_RE.sub(" ", value.strip())
    if len(text) > max_length:
        raise AppointmentNoAppValidationError(
            f"{field} must be at most {max_length} characters"
        )
    return text


def _token(value: object, field: str) -> str:
    text = _text(value, field, 128)
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,127}", text):
        raise AppointmentNoAppValidationError(f"{field} contains invalid characters")
    return text


def _sha256(value: object, field: str) -> str:
    text = _text(value, field, 64).lower()
    if not _SHA256_RE.fullmatch(text):
        raise AppointmentNoAppValidationError(
            f"{field} must be a lowercase SHA-256 hex digest"
        )
    return text


__all__ = [
    "AppointmentBindingPlan",
    "AppointmentNoAppError",
    "AppointmentNoAppIntegrityError",
    "AppointmentNoAppValidationError",
    "DirectAppointmentEvidence",
    "DirectAppointmentPlan",
    "DirectEvidenceObservation",
    "FINGERPRINT_DERIVED_EXTRACTION",
    "FINGERPRINT_EXACT_TEXT",
    "FINGERPRINT_RAW_IMAGE",
    "build_direct_evidence",
    "plan_appointment_workspace_bindings",
    "plan_direct_appointment_intake",
    "verify_appointment_workspace_bindings",
    "verify_direct_appointment_readback",
]
