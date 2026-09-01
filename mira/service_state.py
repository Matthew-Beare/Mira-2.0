"""Explicit provider-neutral MIRA service and capability state.

SERVICE-001 requires user intent, recommendation, provider capability/readiness,
and actual activation to remain separate truths. SOURCE-001 / PROVIDER-001 also
require provider authorization, read, write, and exact remote-readback evidence
to remain independent rather than collapsing "OAuth succeeded" into "ready".

This module provides both boundaries without performing provider authorization or
provider I/O itself. Provider adapters report bounded evidence; this module turns
that evidence into deterministic fail-closed connection/readiness decisions.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Iterable

from .structured_state import NotFoundError, ResourceRecord, StructuredStateAdapter


RESOURCE_TYPE = "service_state"
SCHEMA_VERSION = 1

ACTIVATION_STATES = frozenset({"disabled", "requested", "active", "suspended"})
CAPABILITY_STATES = frozenset({"unknown", "unavailable", "available"})
RECOMMENDATION_STATES = frozenset({"none", "suggested"})


class ServiceStateError(Exception):
    """Base error for explicit service-state behavior."""


class ServiceStateValidationError(ServiceStateError):
    """Raised when service state or transition input is malformed."""


class ServiceNotReadyError(ServiceStateError):
    """Raised when activation is attempted without verified readiness."""


class ServiceIntentRequiredError(ServiceStateError):
    """Raised when activation is attempted without explicit user intent."""


class AuthorizationState(str, Enum):
    """Observed provider authorization state, independent of usable capability."""

    UNKNOWN = "unknown"
    REQUIRED = "required"
    AUTHORIZED = "authorized"
    DENIED = "denied"
    EXPIRED = "expired"
    REVOKED = "revoked"
    UNAVAILABLE = "unavailable"


class CapabilityGate(str, Enum):
    """Independent SOURCE-001 gates that must never imply one another."""

    READ = "read"
    WRITE = "write"
    REMOTE_READBACK = "remote_readback"


class CapabilityEvidenceState(str, Enum):
    """State of one observed provider capability gate."""

    UNKNOWN = "unknown"
    UNSUPPORTED = "unsupported"
    DECLARED = "declared"
    VERIFIED = "verified"
    FAILED = "failed"
    PERMISSION_DENIED = "permission_denied"


class ConnectionState(str, Enum):
    """Provider-neutral presentation state for later Connections surfaces."""

    CONNECT = "connect"
    CONNECTED = "connected"
    RECONNECT = "reconnect"
    NEEDS_ATTENTION = "needs_attention"
    UNAVAILABLE = "unavailable"


@dataclass(frozen=True)
class GateObservation:
    gate: CapabilityGate
    state: CapabilityEvidenceState
    observed_at: str
    reason_code: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.gate, CapabilityGate):
            raise ServiceStateValidationError("gate must be a CapabilityGate")
        if not isinstance(self.state, CapabilityEvidenceState):
            raise ServiceStateValidationError(
                "state must be a CapabilityEvidenceState"
            )
        _utc_timestamp(self.observed_at, "observed_at")
        if self.reason_code is not None:
            _token(self.reason_code, "reason_code")


@dataclass(frozen=True)
class ProviderCapabilitySnapshot:
    """Secret-free provider/service capability evidence at one decision boundary."""

    provider_id: str
    service_id: str
    authorization_state: AuthorizationState
    authorization_observed_at: str
    gates: tuple[GateObservation, ...]
    resource_ref: str | None = None
    scopes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _token(self.provider_id, "provider_id")
        _token(self.service_id, "service_id")
        if not isinstance(self.authorization_state, AuthorizationState):
            raise ServiceStateValidationError(
                "authorization_state must be an AuthorizationState"
            )
        _utc_timestamp(self.authorization_observed_at, "authorization_observed_at")
        if not isinstance(self.gates, tuple):
            raise ServiceStateValidationError("gates must be a tuple")
        seen: set[CapabilityGate] = set()
        for observation in self.gates:
            if not isinstance(observation, GateObservation):
                raise ServiceStateValidationError(
                    "gates must contain GateObservation values"
                )
            if observation.gate in seen:
                raise ServiceStateValidationError(
                    f"duplicate gate observation: {observation.gate.value}"
                )
            seen.add(observation.gate)
        if self.resource_ref is not None:
            _text(self.resource_ref, "resource_ref", 512)
        if not isinstance(self.scopes, tuple):
            raise ServiceStateValidationError("scopes must be a tuple")
        normalized_scopes = tuple(sorted({_text(scope, "scope", 512) for scope in self.scopes}))
        if normalized_scopes != self.scopes:
            raise ServiceStateValidationError("scopes must be sorted and unique")


@dataclass(frozen=True)
class GateDecision:
    gate: CapabilityGate
    allowed: bool
    reason_code: str


@dataclass(frozen=True)
class CapabilityEvaluation:
    provider_id: str
    service_id: str
    connection_state: ConnectionState
    decisions: tuple[GateDecision, ...]

    @property
    def ready(self) -> bool:
        return self.connection_state == ConnectionState.CONNECTED and all(
            decision.allowed for decision in self.decisions
        )

    @property
    def blockers(self) -> tuple[str, ...]:
        return tuple(
            sorted(
                {
                    f"provider:{decision.gate.value}:{decision.reason_code}"
                    for decision in self.decisions
                    if not decision.allowed
                }
            )
        )


def evaluate_provider_capability(
    snapshot: ProviderCapabilitySnapshot,
    *,
    required_gates: Iterable[CapabilityGate],
    now: str,
    max_age_seconds: int,
) -> CapabilityEvaluation:
    """Evaluate secret-free provider evidence into deterministic fail-closed state.

    Authorization, declared support, verified operations, and freshness remain
    separate. A provider can therefore be authorized but still not usable.
    """

    if not isinstance(snapshot, ProviderCapabilitySnapshot):
        raise ServiceStateValidationError(
            "snapshot must be a ProviderCapabilitySnapshot"
        )
    required = _required_gates(required_gates)
    now_dt = _utc_timestamp(now, "now")
    if (
        not isinstance(max_age_seconds, int)
        or isinstance(max_age_seconds, bool)
        or max_age_seconds < 1
    ):
        raise ServiceStateValidationError("max_age_seconds must be a positive integer")

    authorization = snapshot.authorization_state
    if authorization == AuthorizationState.UNAVAILABLE:
        return _blocked_evaluation(snapshot, required, ConnectionState.UNAVAILABLE, "authorization_unavailable")
    if authorization in {AuthorizationState.UNKNOWN, AuthorizationState.REQUIRED}:
        return _blocked_evaluation(snapshot, required, ConnectionState.CONNECT, "authorization_required")
    if authorization in {AuthorizationState.EXPIRED, AuthorizationState.REVOKED}:
        return _blocked_evaluation(snapshot, required, ConnectionState.RECONNECT, f"authorization_{authorization.value}")
    if authorization == AuthorizationState.DENIED:
        return _blocked_evaluation(snapshot, required, ConnectionState.NEEDS_ATTENTION, "authorization_denied")
    if authorization != AuthorizationState.AUTHORIZED:
        raise ServiceStateValidationError("unsupported authorization state")

    auth_time = _utc_timestamp(
        snapshot.authorization_observed_at, "authorization_observed_at"
    )
    if _is_stale(auth_time, now_dt, max_age_seconds):
        return _blocked_evaluation(
            snapshot,
            required,
            ConnectionState.NEEDS_ATTENTION,
            "authorization_stale",
        )

    observations = {observation.gate: observation for observation in snapshot.gates}
    decisions: list[GateDecision] = []
    saw_unavailable = False
    for gate in required:
        observation = observations.get(gate)
        if observation is None or observation.state == CapabilityEvidenceState.UNKNOWN:
            decisions.append(GateDecision(gate, False, "evidence_unknown"))
            continue
        if observation.state == CapabilityEvidenceState.UNSUPPORTED:
            decisions.append(GateDecision(gate, False, "unsupported"))
            saw_unavailable = True
            continue
        if observation.state == CapabilityEvidenceState.DECLARED:
            decisions.append(GateDecision(gate, False, "not_verified"))
            continue
        if observation.state == CapabilityEvidenceState.PERMISSION_DENIED:
            decisions.append(GateDecision(gate, False, "permission_denied"))
            continue
        if observation.state == CapabilityEvidenceState.FAILED:
            decisions.append(
                GateDecision(gate, False, observation.reason_code or "verification_failed")
            )
            continue
        if observation.state != CapabilityEvidenceState.VERIFIED:
            raise ServiceStateValidationError("unsupported capability evidence state")
        observed_at = _utc_timestamp(observation.observed_at, "observed_at")
        if _is_stale(observed_at, now_dt, max_age_seconds):
            decisions.append(GateDecision(gate, False, "evidence_stale"))
            continue
        decisions.append(GateDecision(gate, True, "verified"))

    if all(decision.allowed for decision in decisions):
        connection_state = ConnectionState.CONNECTED
    elif saw_unavailable:
        connection_state = ConnectionState.UNAVAILABLE
    else:
        connection_state = ConnectionState.NEEDS_ATTENTION
    return CapabilityEvaluation(
        provider_id=snapshot.provider_id,
        service_id=snapshot.service_id,
        connection_state=connection_state,
        decisions=tuple(decisions),
    )


def _blocked_evaluation(
    snapshot: ProviderCapabilitySnapshot,
    required: tuple[CapabilityGate, ...],
    connection_state: ConnectionState,
    reason_code: str,
) -> CapabilityEvaluation:
    return CapabilityEvaluation(
        provider_id=snapshot.provider_id,
        service_id=snapshot.service_id,
        connection_state=connection_state,
        decisions=tuple(
            GateDecision(gate=gate, allowed=False, reason_code=reason_code)
            for gate in required
        ),
    )


def _required_gates(values: Iterable[CapabilityGate]) -> tuple[CapabilityGate, ...]:
    if isinstance(values, (str, bytes)):
        raise ServiceStateValidationError(
            "required_gates must be a collection of CapabilityGate values"
        )
    try:
        material = tuple(values)
    except TypeError as exc:
        raise ServiceStateValidationError(
            "required_gates must be an iterable of CapabilityGate values"
        ) from exc
    if not material:
        raise ServiceStateValidationError("at least one required gate is required")
    if any(not isinstance(value, CapabilityGate) for value in material):
        raise ServiceStateValidationError(
            "required_gates must contain CapabilityGate values"
        )
    return tuple(sorted(set(material), key=lambda value: value.value))


def _utc_timestamp(value: Any, field: str) -> datetime:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise ServiceStateValidationError(f"{field} must be a UTC ISO-8601 timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ServiceStateValidationError(
            f"{field} must be a UTC ISO-8601 timestamp"
        ) from exc
    if parsed.tzinfo is None or parsed.utcoffset() != timezone.utc.utcoffset(parsed):
        raise ServiceStateValidationError(f"{field} must use UTC")
    return parsed.astimezone(timezone.utc)


def _is_stale(observed_at: datetime, now: datetime, max_age_seconds: int) -> bool:
    if observed_at > now:
        raise ServiceStateValidationError("capability evidence cannot be from the future")
    return (now - observed_at).total_seconds() > max_age_seconds


@dataclass(frozen=True)
class ServiceStateView:
    service_id: str
    revision: int
    activation_state: str
    capability_state: str
    recommendation_state: str
    dependency_blockers: tuple[str, ...]
    suspension_reason: str | None
    idempotent_replay: bool = False

    @property
    def requested_by_user(self) -> bool:
        return self.activation_state in {"requested", "active", "suspended"}

    @property
    def ready(self) -> bool:
        return self.capability_state == "available" and not self.dependency_blockers

    @property
    def effective_active(self) -> bool:
        return self.activation_state == "active" and self.ready


class ServiceStateService:
    """Persist explicit service state through STORE-001-compatible semantics."""

    def __init__(self, adapter: StructuredStateAdapter) -> None:
        self._adapter = adapter

    def ensure(self, service_id: str) -> ServiceStateView:
        service_id = _token(service_id, "service_id")
        try:
            return _view(self._adapter.get(RESOURCE_TYPE, service_id))
        except NotFoundError:
            result = self._adapter.upsert(
                RESOURCE_TYPE,
                service_id,
                _empty_payload(service_id),
                idempotency_key=f"service-state-start:{service_id}",
                expected_revision=0,
            )
            return _view(result.record, idempotent_replay=result.idempotent_replay)

    def get(self, service_id: str) -> ServiceStateView:
        service_id = _token(service_id, "service_id")
        try:
            return _view(self._adapter.get(RESOURCE_TYPE, service_id))
        except NotFoundError as exc:
            raise ServiceStateValidationError(f"unknown service state: {service_id}") from exc

    def request_enable(self, service_id: str, *, idempotency_key: str) -> ServiceStateView:
        def change(payload: dict[str, Any]) -> None:
            if payload["activation_state"] == "active":
                return
            payload["activation_state"] = "requested"
            payload["suspension_reason"] = None

        return self._mutate(service_id, idempotency_key, change)

    def recommend(self, service_id: str, *, idempotency_key: str) -> ServiceStateView:
        def change(payload: dict[str, Any]) -> None:
            payload["recommendation_state"] = "suggested"

        return self._mutate(service_id, idempotency_key, change)

    def clear_recommendation(
        self, service_id: str, *, idempotency_key: str
    ) -> ServiceStateView:
        def change(payload: dict[str, Any]) -> None:
            payload["recommendation_state"] = "none"

        return self._mutate(service_id, idempotency_key, change)

    def set_readiness(
        self,
        service_id: str,
        *,
        capability_state: str,
        dependency_blockers: Iterable[str] = (),
        idempotency_key: str,
    ) -> ServiceStateView:
        capability = _enum(capability_state, CAPABILITY_STATES, "capability_state")
        blockers = _blockers(dependency_blockers)

        def change(payload: dict[str, Any]) -> None:
            payload["capability_state"] = capability
            payload["dependency_blockers"] = list(blockers)
            ready = capability == "available" and not blockers
            if payload["activation_state"] == "active" and not ready:
                payload["activation_state"] = "suspended"
                payload["suspension_reason"] = "readiness_lost"

        return self._mutate(service_id, idempotency_key, change)

    def apply_capability_evaluation(
        self,
        service_id: str,
        *,
        evaluation: CapabilityEvaluation,
        idempotency_key: str,
    ) -> ServiceStateView:
        """Project verified provider readiness without changing user activation intent."""

        service_id = _token(service_id, "service_id")
        if not isinstance(evaluation, CapabilityEvaluation):
            raise ServiceStateValidationError(
                "evaluation must be a CapabilityEvaluation"
            )
        if evaluation.service_id != service_id:
            raise ServiceStateValidationError(
                "capability evaluation service identity mismatch"
            )
        return self.set_readiness(
            service_id,
            capability_state="available" if evaluation.ready else "unavailable",
            dependency_blockers=() if evaluation.ready else evaluation.blockers,
            idempotency_key=idempotency_key,
        )

    def activate(self, service_id: str, *, idempotency_key: str) -> ServiceStateView:
        current = self.ensure(service_id)
        if current.activation_state not in {"requested", "suspended"}:
            raise ServiceIntentRequiredError(
                "service activation requires explicit user request before activation"
            )
        if not current.ready:
            reasons = list(current.dependency_blockers)
            if current.capability_state != "available":
                reasons.insert(0, f"capability:{current.capability_state}")
            detail = ", ".join(reasons) or "readiness unknown"
            raise ServiceNotReadyError(f"service is not ready: {detail}")

        def change(payload: dict[str, Any]) -> None:
            payload["activation_state"] = "active"
            payload["suspension_reason"] = None

        return self._mutate_existing(service_id, idempotency_key, change)

    def disable(self, service_id: str, *, idempotency_key: str) -> ServiceStateView:
        def change(payload: dict[str, Any]) -> None:
            payload["activation_state"] = "disabled"
            payload["suspension_reason"] = None

        return self._mutate(service_id, idempotency_key, change)

    def apply_appointment_onboarding_intent(
        self,
        *,
        wants_help: bool,
        idempotency_key: str,
        service_id: str = "appointments_calendar",
    ) -> ServiceStateView:
        if not isinstance(wants_help, bool):
            raise ServiceStateValidationError("wants_help must be boolean")
        if wants_help:
            return self.request_enable(service_id, idempotency_key=idempotency_key)
        return self.disable(service_id, idempotency_key=idempotency_key)

    def _mutate(
        self,
        service_id: str,
        idempotency_key: str,
        change: Callable[[dict[str, Any]], None],
    ) -> ServiceStateView:
        self.ensure(service_id)
        return self._mutate_existing(service_id, idempotency_key, change)

    def _mutate_existing(
        self,
        service_id: str,
        idempotency_key: str,
        change: Callable[[dict[str, Any]], None],
    ) -> ServiceStateView:
        service_id = _token(service_id, "service_id")
        key = _token(idempotency_key, "idempotency_key")
        record = self._adapter.get(RESOURCE_TYPE, service_id)
        payload = deepcopy(record.payload)
        _validate_payload(payload, expected_service_id=service_id)
        before = deepcopy(payload)
        change(payload)
        _validate_payload(payload, expected_service_id=service_id)
        if payload == before:
            return _view(record, idempotent_replay=True)
        result = self._adapter.upsert(
            RESOURCE_TYPE,
            service_id,
            payload,
            idempotency_key=key,
            expected_revision=record.revision,
        )
        return _view(result.record, idempotent_replay=result.idempotent_replay)


def _empty_payload(service_id: str) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "service_id": service_id,
        "activation_state": "disabled",
        "capability_state": "unknown",
        "recommendation_state": "none",
        "dependency_blockers": [],
        "suspension_reason": None,
    }


def _view(record: ResourceRecord, *, idempotent_replay: bool = False) -> ServiceStateView:
    payload = deepcopy(record.payload)
    _validate_payload(payload, expected_service_id=record.resource_id)
    return ServiceStateView(
        service_id=record.resource_id,
        revision=record.revision,
        activation_state=payload["activation_state"],
        capability_state=payload["capability_state"],
        recommendation_state=payload["recommendation_state"],
        dependency_blockers=tuple(payload["dependency_blockers"]),
        suspension_reason=payload["suspension_reason"],
        idempotent_replay=idempotent_replay,
    )


def _validate_payload(payload: dict[str, Any], *, expected_service_id: str) -> None:
    if not isinstance(payload, dict):
        raise ServiceStateValidationError("service-state payload must be an object")
    if payload.get("schema_version") != SCHEMA_VERSION:
        raise ServiceStateValidationError("unsupported service-state schema version")
    if payload.get("service_id") != expected_service_id:
        raise ServiceStateValidationError("service-state identity/readback mismatch")
    _enum(payload.get("activation_state"), ACTIVATION_STATES, "activation_state")
    _enum(payload.get("capability_state"), CAPABILITY_STATES, "capability_state")
    _enum(
        payload.get("recommendation_state"),
        RECOMMENDATION_STATES,
        "recommendation_state",
    )
    blockers = payload.get("dependency_blockers")
    normalized_blockers = _blockers(blockers if isinstance(blockers, list) else ())
    if list(normalized_blockers) != blockers:
        raise ServiceStateValidationError(
            "dependency_blockers must be a sorted unique list of non-empty tokens"
        )
    suspension_reason = payload.get("suspension_reason")
    if suspension_reason is not None:
        _token(suspension_reason, "suspension_reason")
    if payload["activation_state"] == "active":
        if payload["capability_state"] != "available" or blockers:
            raise ServiceStateValidationError(
                "persisted active service must have verified available capability and no blockers"
            )
    if payload["activation_state"] == "suspended" and suspension_reason is None:
        raise ServiceStateValidationError("suspended service requires suspension_reason")


def _blockers(values: Iterable[str]) -> tuple[str, ...]:
    if isinstance(values, (str, bytes)):
        raise ServiceStateValidationError("dependency_blockers must be a collection of tokens")
    try:
        normalized = tuple(sorted({_token(value, "dependency_blocker") for value in values}))
    except TypeError as exc:
        raise ServiceStateValidationError(
            "dependency_blockers must be an iterable of tokens"
        ) from exc
    return normalized


def _enum(value: Any, allowed: frozenset[str], field: str) -> str:
    token = _token(value, field)
    if token not in allowed:
        raise ServiceStateValidationError(
            f"{field} must be one of: {', '.join(sorted(allowed))}"
        )
    return token


def _text(value: Any, field: str, max_length: int) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise ServiceStateValidationError(f"{field} must be non-empty trimmed text")
    if len(value) > max_length:
        raise ServiceStateValidationError(
            f"{field} must be at most {max_length} characters"
        )
    return value


def _token(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise ServiceStateValidationError(f"{field} must be a non-empty trimmed string")
    if len(value) > 128:
        raise ServiceStateValidationError(f"{field} must be at most 128 characters")
    return value


__all__ = [
    "ACTIVATION_STATES",
    "CAPABILITY_STATES",
    "RECOMMENDATION_STATES",
    "RESOURCE_TYPE",
    "AuthorizationState",
    "CapabilityEvidenceState",
    "CapabilityEvaluation",
    "CapabilityGate",
    "ConnectionState",
    "GateDecision",
    "GateObservation",
    "ProviderCapabilitySnapshot",
    "ServiceIntentRequiredError",
    "ServiceNotReadyError",
    "ServiceStateError",
    "ServiceStateService",
    "ServiceStateValidationError",
    "ServiceStateView",
    "evaluate_provider_capability",
]
