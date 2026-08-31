"""Provider-neutral appointment evidence intake and reconciliation for MIRA.

This module accepts already-observed evidence references plus a structured extraction
result. It does not fetch Gmail, perform OCR/model extraction, schedule reminders,
send messages, or infer medical meaning. Canonical provider/appointment identity is
delegated to ``AppointmentIdentityService`` and Calendar projection remains a gated
downstream side effect.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import hashlib
import re
from typing import Mapping

from .appointments import (
    APPOINTMENT_RESOURCE_TYPE,
    EVIDENCE_AUTHORITIES,
    AppointmentCandidate,
    AppointmentIdentityError,
    AppointmentIdentityService,
    AppointmentReconciliationResult,
    AppointmentView,
    EvidenceRef,
    ProviderCandidate,
    ProviderReconciliationResult,
    ProviderView,
)
from .calendar_projection import (
    CalendarEventMaterial,
    CalendarProjectionError,
    CalendarProjectionRequest,
    CalendarProjectionResult,
    CalendarProjectionService,
)
from .service_state import ServiceStateView


ALLOWED_APPOINTMENT_SOURCE_TYPES = frozenset({"email", "image", "text"})
ESSENTIAL_CONFIDENCE = 0.90
OPTIONAL_CONFIDENCE = 0.80
APPOINTMENT_SERVICE_ID = "appointments_calendar"
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_WS_RE = re.compile(r"\s+")


class AppointmentIntakeError(Exception):
    """Base class for appointment-intake failures."""


class AppointmentIntakeValidationError(AppointmentIntakeError):
    """Raised when evidence/extraction/orchestration input is malformed."""


@dataclass(frozen=True)
class AppointmentExtraction:
    """Structured facts extracted from one authorized evidence observation."""

    provider_display_name: str | None = None
    provider_organization: str | None = None
    provider_email: str | None = None
    provider_phone: str | None = None
    provider_specialty_type: str | None = None
    provider_identity_namespace: str | None = None
    provider_identity_value: str | None = None
    canonical_provider_id: str | None = None
    appointment_start_at: str | None = None
    appointment_end_at: str | None = None
    appointment_timezone: str | None = None
    appointment_title: str | None = None
    appointment_location: str | None = None
    appointment_type: str | None = None
    appointment_identity_namespace: str | None = None
    appointment_identity_value: str | None = None
    canonical_appointment_id: str | None = None
    confidence: Mapping[str, float] | None = None


@dataclass(frozen=True)
class CalendarProjectionTarget:
    provider_lane: str
    calendar_ref: str


@dataclass(frozen=True)
class AppointmentIntakeResult:
    status: str
    provider_result: ProviderReconciliationResult | None
    appointment_result: AppointmentReconciliationResult | None
    review_reasons: tuple[str, ...] = ()
    omitted_low_confidence_fields: tuple[str, ...] = ()
    projection_status: str = "not_requested"
    projection_result: CalendarProjectionResult | None = None
    projection_error: str | None = None

    @property
    def provider(self) -> ProviderView | None:
        return None if self.provider_result is None else self.provider_result.provider

    @property
    def appointment(self) -> AppointmentView | None:
        return (
            None
            if self.appointment_result is None
            else self.appointment_result.appointment
        )


class AppointmentIntakeService:
    """Validate extracted evidence, reconcile canonical identity, and gate projection."""

    def __init__(
        self,
        identity: AppointmentIdentityService,
        *,
        calendar_projection: CalendarProjectionService | None = None,
    ) -> None:
        self._identity = identity
        self._calendar_projection = calendar_projection

    def intake(
        self,
        evidence: EvidenceRef,
        extraction: AppointmentExtraction,
        *,
        idempotency_key: str,
        service_state: ServiceStateView | None = None,
        projection_target: CalendarProjectionTarget | None = None,
    ) -> AppointmentIntakeResult:
        normalized_evidence = _evidence(evidence)
        key = _token(idempotency_key, "idempotency_key")
        accepted, omitted = _accepted_extraction(normalized_evidence, extraction)

        review = _preflight_identity(accepted, normalized_evidence)
        if review:
            return AppointmentIntakeResult(
                status="needs_review",
                provider_result=None,
                appointment_result=None,
                review_reasons=tuple(review),
                omitted_low_confidence_fields=omitted,
                projection_status=_suppressed_projection_status(projection_target),
            )

        provider_candidate = ProviderCandidate(
            evidence=normalized_evidence,
            display_name=accepted.get("provider_display_name"),
            organization=accepted.get("provider_organization"),
            email=accepted.get("provider_email"),
            phone=accepted.get("provider_phone"),
            specialty_type=accepted.get("provider_specialty_type"),
            identity_namespace=accepted.get("provider_identity_namespace"),
            identity_value=accepted.get("provider_identity_value"),
            canonical_provider_id=accepted.get("canonical_provider_id"),
        )
        try:
            provider_result = self._identity.reconcile_provider(
                provider_candidate,
                idempotency_key=_derived_key("appt-intake-provider", key),
            )
        except AppointmentIdentityError as exc:
            raise AppointmentIntakeValidationError(str(exc)) from exc
        if provider_result.status == "needs_review" or provider_result.provider is None:
            reason = provider_result.reason or "provider reconciliation requires review"
            return AppointmentIntakeResult(
                status="needs_review",
                provider_result=provider_result,
                appointment_result=None,
                review_reasons=(reason,),
                omitted_low_confidence_fields=omitted,
                projection_status=_suppressed_projection_status(projection_target),
            )

        appointment_candidate = AppointmentCandidate(
            evidence=normalized_evidence,
            provider_id=provider_result.provider.provider_id,
            start_at=accepted.get("appointment_start_at"),
            end_at=accepted.get("appointment_end_at"),
            timezone=accepted.get("appointment_timezone"),
            title=accepted.get("appointment_title"),
            location=accepted.get("appointment_location"),
            appointment_type=accepted.get("appointment_type"),
            identity_namespace=accepted.get("appointment_identity_namespace"),
            identity_value=accepted.get("appointment_identity_value"),
            canonical_appointment_id=accepted.get("canonical_appointment_id"),
        )
        try:
            appointment_result = self._identity.reconcile_appointment(
                appointment_candidate,
                idempotency_key=_derived_key("appt-intake-appointment", key),
            )
        except AppointmentIdentityError as exc:
            raise AppointmentIntakeValidationError(str(exc)) from exc
        if appointment_result.status == "needs_review" or appointment_result.appointment is None:
            reason = appointment_result.reason or "appointment reconciliation requires review"
            return AppointmentIntakeResult(
                status="needs_review",
                provider_result=provider_result,
                appointment_result=appointment_result,
                review_reasons=(reason,),
                omitted_low_confidence_fields=omitted,
                projection_status=_suppressed_projection_status(projection_target),
            )

        projection_status, projection_result, projection_error = self._project_if_ready(
            provider_result.provider,
            appointment_result.appointment,
            service_state=service_state,
            projection_target=projection_target,
            idempotency_key=key,
        )
        return AppointmentIntakeResult(
            status="reconciled",
            provider_result=provider_result,
            appointment_result=appointment_result,
            omitted_low_confidence_fields=omitted,
            projection_status=projection_status,
            projection_result=projection_result,
            projection_error=projection_error,
        )

    def _project_if_ready(
        self,
        provider: ProviderView,
        appointment: AppointmentView,
        *,
        service_state: ServiceStateView | None,
        projection_target: CalendarProjectionTarget | None,
        idempotency_key: str,
    ) -> tuple[str, CalendarProjectionResult | None, str | None]:
        if projection_target is None:
            return "not_requested", None, None
        target = _projection_target(projection_target)
        if service_state is None:
            return "service_inactive", None, None
        if service_state.service_id != APPOINTMENT_SERVICE_ID:
            raise AppointmentIntakeValidationError(
                f"service_state must describe {APPOINTMENT_SERVICE_ID!r}"
            )
        if not service_state.effective_active:
            return "service_inactive", None, None
        if self._calendar_projection is None:
            return "projection_unavailable", None, "Calendar projection dependency is unavailable"
        if (
            appointment.start_at is None
            or appointment.end_at is None
            or appointment.timezone is None
        ):
            return (
                "timing_needs_review",
                None,
                "Calendar projection requires exact start_at, end_at, and IANA timezone",
            )

        event = CalendarEventMaterial(
            title=_calendar_title(provider, appointment),
            start_at=appointment.start_at,
            end_at=appointment.end_at,
            timezone=appointment.timezone,
            location=appointment.location,
            description=None,
        )
        request = CalendarProjectionRequest(
            source_resource_type=APPOINTMENT_RESOURCE_TYPE,
            source_resource_id=appointment.appointment_id,
            source_revision=appointment.revision,
            provider_lane=target.provider_lane,
            calendar_ref=target.calendar_ref,
            event=event,
        )
        try:
            result = self._calendar_projection.project(
                request,
                idempotency_key=_derived_key("appt-intake-calendar", idempotency_key),
            )
        except CalendarProjectionError as exc:
            return "projection_failed", None, str(exc)
        return "projected", result, None


_FIELD_THRESHOLDS = {
    "provider_display_name": ESSENTIAL_CONFIDENCE,
    "provider_organization": ESSENTIAL_CONFIDENCE,
    "provider_email": ESSENTIAL_CONFIDENCE,
    "provider_phone": ESSENTIAL_CONFIDENCE,
    "provider_specialty_type": OPTIONAL_CONFIDENCE,
    "provider_identity_namespace": ESSENTIAL_CONFIDENCE,
    "provider_identity_value": ESSENTIAL_CONFIDENCE,
    "canonical_provider_id": ESSENTIAL_CONFIDENCE,
    "appointment_start_at": ESSENTIAL_CONFIDENCE,
    "appointment_end_at": ESSENTIAL_CONFIDENCE,
    "appointment_timezone": ESSENTIAL_CONFIDENCE,
    "appointment_title": OPTIONAL_CONFIDENCE,
    "appointment_location": OPTIONAL_CONFIDENCE,
    "appointment_type": OPTIONAL_CONFIDENCE,
    "appointment_identity_namespace": ESSENTIAL_CONFIDENCE,
    "appointment_identity_value": ESSENTIAL_CONFIDENCE,
    "canonical_appointment_id": ESSENTIAL_CONFIDENCE,
}


def _accepted_extraction(
    evidence: EvidenceRef,
    extraction: AppointmentExtraction,
) -> tuple[dict[str, str | None], tuple[str, ...]]:
    if not isinstance(extraction, AppointmentExtraction):
        raise AppointmentIntakeValidationError(
            "extraction must be AppointmentExtraction"
        )
    raw = {field: getattr(extraction, field) for field in _FIELD_THRESHOLDS}
    confidence = {} if extraction.confidence is None else dict(extraction.confidence)
    unknown = sorted(set(confidence) - set(_FIELD_THRESHOLDS))
    if unknown:
        raise AppointmentIntakeValidationError(
            "confidence contains unknown extraction fields: " + ", ".join(unknown)
        )
    normalized_confidence = {
        field: _confidence(value, field) for field, value in confidence.items()
    }
    accepted: dict[str, str | None] = {}
    omitted: list[str] = []
    for field, value in raw.items():
        if value is None:
            accepted[field] = None
            continue
        if not isinstance(value, str) or not value.strip():
            raise AppointmentIntakeValidationError(
                f"{field} must be non-empty text when supplied"
            )
        normalized_value = _WS_RE.sub(" ", value.strip())
        if evidence.authority == "user_confirmed":
            accepted[field] = normalized_value
            continue
        if field not in normalized_confidence:
            raise AppointmentIntakeValidationError(
                f"confidence is required for extracted field {field}"
            )
        if normalized_confidence[field] < _FIELD_THRESHOLDS[field]:
            accepted[field] = None
            omitted.append(field)
        else:
            accepted[field] = normalized_value
    if evidence.authority != "user_confirmed":
        unused = sorted(set(normalized_confidence) - {field for field, value in raw.items() if value is not None})
        if unused:
            raise AppointmentIntakeValidationError(
                "confidence supplied for missing extraction fields: " + ", ".join(unused)
            )
    return accepted, tuple(sorted(omitted))


def _preflight_identity(
    values: Mapping[str, str | None], evidence: EvidenceRef
) -> list[str]:
    reasons: list[str] = []
    if values["canonical_provider_id"] is not None and evidence.authority != "user_confirmed":
        raise AppointmentIntakeValidationError(
            "canonical_provider_id requires user_confirmed evidence"
        )
    if values["canonical_appointment_id"] is not None and evidence.authority != "user_confirmed":
        raise AppointmentIntakeValidationError(
            "canonical_appointment_id requires user_confirmed evidence"
        )

    provider_pair = _pair_state(
        values["provider_identity_namespace"], values["provider_identity_value"]
    )
    if provider_pair == "partial":
        reasons.append("provider identity namespace/value is incomplete or low-confidence")
    provider_exact = (
        values["canonical_provider_id"] is not None
        or provider_pair == "complete"
        or values["provider_email"] is not None
        or _exact_phone(values["provider_phone"])
        or (
            values["provider_organization"] is not None
            and values["provider_display_name"] is not None
        )
    )
    if not provider_exact:
        reasons.append("provider evidence lacks a high-confidence exact identity key")

    appointment_pair = _pair_state(
        values["appointment_identity_namespace"],
        values["appointment_identity_value"],
    )
    if appointment_pair == "partial":
        reasons.append("appointment identity namespace/value is incomplete or low-confidence")
    appointment_exact = (
        values["canonical_appointment_id"] is not None
        or appointment_pair == "complete"
        or values["appointment_start_at"] is not None
    )
    if not appointment_exact:
        reasons.append(
            "appointment occurrence lacks a high-confidence exact start time or explicit identity"
        )
    return reasons


def _evidence(value: EvidenceRef) -> EvidenceRef:
    if not isinstance(value, EvidenceRef):
        raise AppointmentIntakeValidationError("evidence must be EvidenceRef")
    if value.source_type not in ALLOWED_APPOINTMENT_SOURCE_TYPES:
        raise AppointmentIntakeValidationError(
            "appointment evidence source_type must be email, image, or text"
        )
    source_id = _text(value.source_id, "source_id", 500)
    digest = _text(value.material_sha256, "material_sha256", 64).lower()
    if not _SHA256_RE.fullmatch(digest):
        raise AppointmentIntakeValidationError(
            "material_sha256 must be a lowercase SHA-256 hex digest"
        )
    observed_at = _timestamp(value.observed_at, "observed_at")
    if value.authority not in EVIDENCE_AUTHORITIES:
        raise AppointmentIntakeValidationError(
            "authority must be derived, source, or user_confirmed"
        )
    return EvidenceRef(
        source_type=value.source_type,
        source_id=source_id,
        material_sha256=digest,
        observed_at=observed_at,
        authority=value.authority,
    )


def _projection_target(value: CalendarProjectionTarget) -> CalendarProjectionTarget:
    if not isinstance(value, CalendarProjectionTarget):
        raise AppointmentIntakeValidationError(
            "projection_target must be CalendarProjectionTarget"
        )
    return CalendarProjectionTarget(
        provider_lane=_token(value.provider_lane, "provider_lane"),
        calendar_ref=_text(value.calendar_ref, "calendar_ref", 500),
    )


def _calendar_title(provider: ProviderView, appointment: AppointmentView) -> str:
    if appointment.title:
        return appointment.title
    if appointment.appointment_type:
        return appointment.appointment_type
    if provider.specialty_type:
        return f"{provider.specialty_type} appointment"
    if provider.display_name:
        return f"Appointment with {provider.display_name}"
    if provider.organization:
        return f"Appointment with {provider.organization}"
    return "Appointment"


def _suppressed_projection_status(
    projection_target: CalendarProjectionTarget | None,
) -> str:
    return "not_requested" if projection_target is None else "not_reconciled"


def _pair_state(left: str | None, right: str | None) -> str:
    if left is None and right is None:
        return "absent"
    if left is None or right is None:
        return "partial"
    return "complete"


def _exact_phone(value: str | None) -> bool:
    if value is None or re.search(r"(?:ext|x)\s*\d", value, re.IGNORECASE):
        return False
    digits = "".join(ch for ch in value if ch.isdigit())
    return 7 <= len(digits) <= 15


def _confidence(value: object, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise AppointmentIntakeValidationError(
            f"confidence for {field} must be a number from 0 through 1"
        )
    number = float(value)
    if not 0.0 <= number <= 1.0:
        raise AppointmentIntakeValidationError(
            f"confidence for {field} must be from 0 through 1"
        )
    return number


def _derived_key(prefix: str, logical_key: str) -> str:
    digest = hashlib.sha256(f"{prefix}|{logical_key}".encode("utf-8")).hexdigest()[:40]
    return f"{prefix}-{digest}"


def _token(value: object, field: str) -> str:
    text = _text(value, field, 128)
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,127}", text):
        raise AppointmentIntakeValidationError(f"{field} contains invalid characters")
    return text


def _text(value: object, field: str, max_length: int) -> str:
    if not isinstance(value, str) or not value.strip():
        raise AppointmentIntakeValidationError(f"{field} must be non-empty text")
    text = _WS_RE.sub(" ", value.strip())
    if len(text) > max_length:
        raise AppointmentIntakeValidationError(
            f"{field} must be at most {max_length} characters"
        )
    return text


def _timestamp(value: object, field: str) -> str:
    text = _text(value, field, 100)
    raw = text[:-1] + "+00:00" if text.endswith("Z") else text
    try:
        parsed = datetime.fromisoformat(raw)
    except ValueError as exc:
        raise AppointmentIntakeValidationError(
            f"{field} must be valid ISO-8601"
        ) from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise AppointmentIntakeValidationError(
            f"{field} must include a UTC offset"
        )
    return parsed.isoformat()


__all__ = [
    "ALLOWED_APPOINTMENT_SOURCE_TYPES",
    "APPOINTMENT_SERVICE_ID",
    "ESSENTIAL_CONFIDENCE",
    "OPTIONAL_CONFIDENCE",
    "AppointmentExtraction",
    "AppointmentIntakeError",
    "AppointmentIntakeResult",
    "AppointmentIntakeService",
    "AppointmentIntakeValidationError",
    "CalendarProjectionTarget",
]
