"""Provider-neutral capability and policy routing for MIRA.

This module is deliberately read-only. It consumes SOURCE-001 capability evidence
from :mod:`mira.service_state` plus explicit policy/approval inputs and selects at
most one eligible provider/runtime lane. It performs no provider authorization,
discovery, provider I/O, canonical-state mutation, worker wake/shutdown, job
execution, or MIRA service activation.

PROVIDER-001 requires routing from observed evidence rather than provider branding
or a successful consent screen. LOCAL-001 additionally requires local execution to
remain policy-gated, capability-driven, and free of assumed LAN trust. Consequently,
every requested operation carries its own capability requirements and every
candidate is evaluated independently.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
import re
from typing import Iterable

from .service_state import (
    CapabilityEvaluation,
    CapabilityGate,
    ProviderCapabilitySnapshot,
    ServiceStateValidationError,
    evaluate_provider_capability,
)


class RuntimeRouterError(Exception):
    """Base error for deterministic runtime-routing validation failures."""


class RuntimeRouterValidationError(RuntimeRouterError):
    """Raised when route request/candidate material is malformed."""


class ApprovalState(str, Enum):
    """Explicit policy approval state for one runtime lane."""

    UNKNOWN = "unknown"
    REQUIRED = "required"
    APPROVED = "approved"
    DENIED = "denied"


class RuntimeKind(str, Enum):
    """Generic execution location without naming a provider or private machine."""

    HOSTED = "hosted"
    LOCAL = "local"


class LocalComputeMode(str, Enum):
    """User policy for optional local execution."""

    OFF = "off"
    NORMAL = "normal"
    AGGRESSIVE = "aggressive"


class RuntimeAvailability(str, Enum):
    """Observed schedulability state for one runtime lane."""

    READY = "ready"
    BUSY = "busy"
    OFFLINE = "offline"
    DRAINING = "draining"
    FAULTED = "faulted"


class RuntimeHealth(str, Enum):
    """Observed health state used by deterministic fail-closed routing."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"
    FAULTED = "faulted"


class WorkerIdentityState(str, Enum):
    """Result of an external worker-authentication boundary."""

    UNVERIFIED = "unverified"
    VERIFIED = "verified"
    REVOKED = "revoked"


class RouteOutcome(str, Enum):
    """Top-level routing result."""

    SELECTED = "selected"
    BLOCKED = "blocked"


class RouteReason(str, Enum):
    """Bounded machine-readable top-level routing reasons."""

    SELECTED = "selected"
    NO_CANDIDATES = "no_candidates"
    REQUIRED_PROVIDER_UNAVAILABLE = "required_provider_unavailable"
    POLICY_BLOCKED = "policy_blocked"
    CAPABILITY_BLOCKED = "capability_blocked"
    NO_ELIGIBLE_LANE = "no_eligible_lane"


@dataclass(frozen=True)
class WorkerIdentityProof:
    """Secret-free result from an external authenticated worker boundary.

    The proof deliberately contains no credential or transport material. A later
    worker agent/transport may use mTLS or another authenticated mechanism, but it
    must reduce that ceremony to this bounded evidence before routing code sees it.
    """

    principal_id: str
    state: WorkerIdentityState
    verified_at: str

    def __post_init__(self) -> None:
        _token(self.principal_id, "principal_id")
        if not isinstance(self.state, WorkerIdentityState):
            raise RuntimeRouterValidationError(
                "state must be a WorkerIdentityState"
            )
        _utc_timestamp(self.verified_at, "verified_at")


@dataclass(frozen=True)
class RuntimePolicy:
    """Explicit policy material supplied to the router for one candidate lane.

    ``allowed_data_classifications`` is intentionally opaque/provider-neutral. A
    policy layer may define classifications such as ``personal`` or ``restricted``
    without making those names universal product semantics in this router.

    ``local_compute_mode`` affects only candidates whose ``runtime_kind`` is
    ``LOCAL``. Worker presence never overrides ``OFF``.
    """

    policy_id: str
    approval_state: ApprovalState
    allowed_data_classifications: tuple[str, ...]
    local_compute_mode: LocalComputeMode = LocalComputeMode.NORMAL

    def __post_init__(self) -> None:
        _token(self.policy_id, "policy_id")
        if not isinstance(self.approval_state, ApprovalState):
            raise RuntimeRouterValidationError(
                "approval_state must be an ApprovalState"
            )
        normalized = _sorted_tokens(
            self.allowed_data_classifications,
            "allowed_data_classifications",
        )
        object.__setattr__(self, "allowed_data_classifications", normalized)
        if not isinstance(self.local_compute_mode, LocalComputeMode):
            raise RuntimeRouterValidationError(
                "local_compute_mode must be a LocalComputeMode"
            )


@dataclass(frozen=True)
class WorkerAdvertisement:
    """Secret-free worker execution evidence before router-candidate projection.

    Private bindings such as hostnames, IP addresses, device serials, model paths,
    shell endpoints, or credentials are intentionally absent. ``identity`` is the
    result of an external authentication boundary, not authentication material.
    ``principal_id`` is the opaque principal this worker expects that proof to bind.
    """

    worker_id: str
    principal_id: str
    identity: WorkerIdentityProof
    lane_id: str
    runtime_id: str
    service_id: str
    runtime_kind: RuntimeKind
    runtime_capabilities: tuple[str, ...]
    policy: RuntimePolicy
    availability: RuntimeAvailability
    health: RuntimeHealth
    interactive_lock: bool
    priority: int
    load_rank: int
    cost_rank: int
    heartbeat_at: str

    def __post_init__(self) -> None:
        _token(self.worker_id, "worker_id")
        _token(self.principal_id, "principal_id")
        if not isinstance(self.identity, WorkerIdentityProof):
            raise RuntimeRouterValidationError(
                "identity must be a WorkerIdentityProof"
            )
        _token(self.lane_id, "lane_id")
        _token(self.runtime_id, "runtime_id")
        _token(self.service_id, "service_id")
        if not isinstance(self.runtime_kind, RuntimeKind):
            raise RuntimeRouterValidationError(
                "runtime_kind must be a RuntimeKind"
            )
        capabilities = _sorted_tokens(
            self.runtime_capabilities,
            "runtime_capabilities",
        )
        object.__setattr__(self, "runtime_capabilities", capabilities)
        if not isinstance(self.policy, RuntimePolicy):
            raise RuntimeRouterValidationError("policy must be a RuntimePolicy")
        if not isinstance(self.availability, RuntimeAvailability):
            raise RuntimeRouterValidationError(
                "availability must be a RuntimeAvailability"
            )
        if not isinstance(self.health, RuntimeHealth):
            raise RuntimeRouterValidationError("health must be a RuntimeHealth")
        if not isinstance(self.interactive_lock, bool):
            raise RuntimeRouterValidationError("interactive_lock must be boolean")
        _rank(self.priority, "priority")
        _rank(self.load_rank, "load_rank")
        _rank(self.cost_rank, "cost_rank")
        _utc_timestamp(self.heartbeat_at, "heartbeat_at")


@dataclass(frozen=True)
class RuntimeLaneCandidate:
    """One concrete provider/runtime lane that may satisfy a route request.

    The execution metadata is secret-free decision material. It deliberately does
    not contain a hostname, IP address, credential, model secret, shell endpoint,
    or provider access token. Later worker registries/adapters resolve private
    runtime bindings outside this read-only router.
    """

    lane_id: str
    runtime_id: str
    capability: ProviderCapabilitySnapshot
    policy: RuntimePolicy
    priority: int = 100
    runtime_kind: RuntimeKind = RuntimeKind.HOSTED
    runtime_capabilities: tuple[str, ...] = ()
    availability: RuntimeAvailability = RuntimeAvailability.READY
    health: RuntimeHealth = RuntimeHealth.HEALTHY
    interactive_lock: bool = False
    load_rank: int = 0
    cost_rank: int = 100

    def __post_init__(self) -> None:
        _token(self.lane_id, "lane_id")
        _token(self.runtime_id, "runtime_id")
        if not isinstance(self.capability, ProviderCapabilitySnapshot):
            raise RuntimeRouterValidationError(
                "capability must be a ProviderCapabilitySnapshot"
            )
        if not isinstance(self.policy, RuntimePolicy):
            raise RuntimeRouterValidationError("policy must be a RuntimePolicy")
        _rank(self.priority, "priority")
        if not isinstance(self.runtime_kind, RuntimeKind):
            raise RuntimeRouterValidationError("runtime_kind must be a RuntimeKind")
        capabilities = _sorted_tokens(
            self.runtime_capabilities,
            "runtime_capabilities",
        )
        object.__setattr__(self, "runtime_capabilities", capabilities)
        if not isinstance(self.availability, RuntimeAvailability):
            raise RuntimeRouterValidationError(
                "availability must be a RuntimeAvailability"
            )
        if not isinstance(self.health, RuntimeHealth):
            raise RuntimeRouterValidationError("health must be a RuntimeHealth")
        if not isinstance(self.interactive_lock, bool):
            raise RuntimeRouterValidationError("interactive_lock must be boolean")
        _rank(self.load_rank, "load_rank")
        _rank(self.cost_rank, "cost_rank")


@dataclass(frozen=True)
class WorkerCandidateProjection:
    """Result of converting one authenticated worker advertisement to a lane."""

    worker_id: str
    identity_verified: bool
    heartbeat_fresh: bool
    reason_codes: tuple[str, ...]
    candidate: RuntimeLaneCandidate | None


@dataclass(frozen=True)
class RouteRequest:
    """One provider-backed operation with explicit capability requirements."""

    operation_id: str
    service_id: str
    required_gates: tuple[CapabilityGate, ...]
    data_classification: str
    required_provider_id: str | None = None
    preferred_provider_ids: tuple[str, ...] = ()
    required_runtime_capabilities: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _token(self.operation_id, "operation_id")
        _token(self.service_id, "service_id")
        _token(self.data_classification, "data_classification")
        gates = _gates(self.required_gates)
        object.__setattr__(self, "required_gates", gates)
        if self.required_provider_id is not None:
            _token(self.required_provider_id, "required_provider_id")
        preferences = _ordered_unique_tokens(
            self.preferred_provider_ids,
            "preferred_provider_ids",
        )
        object.__setattr__(self, "preferred_provider_ids", preferences)
        runtime_capabilities = _sorted_tokens(
            self.required_runtime_capabilities,
            "required_runtime_capabilities",
        )
        object.__setattr__(
            self,
            "required_runtime_capabilities",
            runtime_capabilities,
        )


@dataclass(frozen=True)
class CandidateRouteDecision:
    """Independent eligibility result for one candidate lane."""

    lane_id: str
    runtime_id: str
    provider_id: str
    service_id: str
    policy_id: str
    eligible: bool
    reason_codes: tuple[str, ...]
    capability_evaluation: CapabilityEvaluation | None


@dataclass(frozen=True)
class RuntimeRouteResult:
    """Deterministic route selection or fail-closed result."""

    outcome: RouteOutcome
    reason: RouteReason
    selected_lane_id: str | None
    selected_runtime_id: str | None
    selected_provider_id: str | None
    candidate_decisions: tuple[CandidateRouteDecision, ...]

    @property
    def selected(self) -> bool:
        return self.outcome == RouteOutcome.SELECTED


def project_worker_candidate(
    advertisement: WorkerAdvertisement,
    capability: ProviderCapabilitySnapshot,
    *,
    now: str,
    max_heartbeat_age_seconds: int,
) -> WorkerCandidateProjection:
    """Project authenticated worker evidence into the existing runtime router.

    Authentication transport remains outside this module. A non-verified identity
    or a proof for the wrong principal never creates a candidate. A stale heartbeat
    does create an explicit fail-closed candidate so the router reports ordinary
    unavailable/unknown worker reasons rather than accidentally reusing the last
    healthy state.
    """

    if not isinstance(advertisement, WorkerAdvertisement):
        raise RuntimeRouterValidationError(
            "advertisement must be a WorkerAdvertisement"
        )
    if not isinstance(capability, ProviderCapabilitySnapshot):
        raise RuntimeRouterValidationError(
            "capability must be a ProviderCapabilitySnapshot"
        )
    if (
        not isinstance(max_heartbeat_age_seconds, int)
        or isinstance(max_heartbeat_age_seconds, bool)
        or max_heartbeat_age_seconds < 1
    ):
        raise RuntimeRouterValidationError(
            "max_heartbeat_age_seconds must be a positive integer"
        )
    if capability.service_id != advertisement.service_id:
        raise RuntimeRouterValidationError(
            "worker advertisement service identity does not match provider capability"
        )

    now_dt = _utc_timestamp(now, "now")
    heartbeat_dt = _utc_timestamp(advertisement.heartbeat_at, "heartbeat_at")
    identity_dt = _utc_timestamp(
        advertisement.identity.verified_at,
        "verified_at",
    )
    if heartbeat_dt > now_dt:
        raise RuntimeRouterValidationError("worker heartbeat cannot be from the future")
    if identity_dt > now_dt:
        raise RuntimeRouterValidationError(
            "worker identity evidence cannot be from the future"
        )
    if identity_dt > heartbeat_dt:
        raise RuntimeRouterValidationError(
            "worker heartbeat must not predate its identity verification"
        )

    heartbeat_fresh = (
        now_dt - heartbeat_dt
    ).total_seconds() <= max_heartbeat_age_seconds
    reasons: list[str] = []

    if advertisement.identity.principal_id != advertisement.principal_id:
        reasons.append("worker_identity_principal_mismatch")
    if advertisement.identity.state is not WorkerIdentityState.VERIFIED:
        reasons.append(
            f"worker_identity_{advertisement.identity.state.value}"
        )
    identity_verified = not reasons
    if not identity_verified:
        return WorkerCandidateProjection(
            worker_id=advertisement.worker_id,
            identity_verified=False,
            heartbeat_fresh=heartbeat_fresh,
            reason_codes=tuple(sorted(reasons)),
            candidate=None,
        )

    availability = advertisement.availability
    health = advertisement.health
    if not heartbeat_fresh:
        reasons.append("worker_heartbeat_stale")
        availability = RuntimeAvailability.OFFLINE
        health = RuntimeHealth.UNKNOWN

    candidate = RuntimeLaneCandidate(
        lane_id=advertisement.lane_id,
        runtime_id=advertisement.runtime_id,
        capability=capability,
        policy=advertisement.policy,
        priority=advertisement.priority,
        runtime_kind=advertisement.runtime_kind,
        runtime_capabilities=advertisement.runtime_capabilities,
        availability=availability,
        health=health,
        interactive_lock=advertisement.interactive_lock,
        load_rank=advertisement.load_rank,
        cost_rank=advertisement.cost_rank,
    )
    return WorkerCandidateProjection(
        worker_id=advertisement.worker_id,
        identity_verified=True,
        heartbeat_fresh=heartbeat_fresh,
        reason_codes=tuple(sorted(reasons)),
        candidate=candidate,
    )


def route_runtime(
    request: RouteRequest,
    candidates: Iterable[RuntimeLaneCandidate],
    *,
    now: str,
    max_age_seconds: int,
) -> RuntimeRouteResult:
    """Select one eligible runtime lane or fail closed with bounded reasons.

    Candidate failures are isolated. Invalid/stale capability evidence in one lane
    is recorded against that lane and does not prevent an independently valid lane
    from being selected.
    """

    if not isinstance(request, RouteRequest):
        raise RuntimeRouterValidationError("request must be a RouteRequest")
    if (
        not isinstance(max_age_seconds, int)
        or isinstance(max_age_seconds, bool)
        or max_age_seconds < 1
    ):
        raise RuntimeRouterValidationError(
            "max_age_seconds must be a positive integer"
        )
    _utc_timestamp(now, "now")

    material = _candidates(candidates)
    if not material:
        return RuntimeRouteResult(
            outcome=RouteOutcome.BLOCKED,
            reason=RouteReason.NO_CANDIDATES,
            selected_lane_id=None,
            selected_runtime_id=None,
            selected_provider_id=None,
            candidate_decisions=(),
        )

    ordered_candidates = tuple(sorted(material, key=lambda item: item.lane_id))
    decisions = tuple(
        _evaluate_candidate(
            request,
            candidate,
            now=now,
            max_age_seconds=max_age_seconds,
        )
        for candidate in ordered_candidates
    )

    eligible = [
        (candidate, decision)
        for candidate, decision in zip(ordered_candidates, decisions)
        if decision.eligible
    ]
    if eligible:
        candidate, _ = min(
            eligible,
            key=lambda pair: _selection_rank(request, pair[0]),
        )
        return RuntimeRouteResult(
            outcome=RouteOutcome.SELECTED,
            reason=RouteReason.SELECTED,
            selected_lane_id=candidate.lane_id,
            selected_runtime_id=candidate.runtime_id,
            selected_provider_id=candidate.capability.provider_id,
            candidate_decisions=decisions,
        )

    if request.required_provider_id is not None:
        required_present = any(
            candidate.capability.service_id == request.service_id
            and candidate.capability.provider_id == request.required_provider_id
            for candidate in material
        )
        if not required_present:
            reason = RouteReason.REQUIRED_PROVIDER_UNAVAILABLE
        else:
            reason = _blocked_reason(decisions, request=request)
    else:
        reason = _blocked_reason(decisions, request=request)

    return RuntimeRouteResult(
        outcome=RouteOutcome.BLOCKED,
        reason=reason,
        selected_lane_id=None,
        selected_runtime_id=None,
        selected_provider_id=None,
        candidate_decisions=decisions,
    )


def _evaluate_candidate(
    request: RouteRequest,
    candidate: RuntimeLaneCandidate,
    *,
    now: str,
    max_age_seconds: int,
) -> CandidateRouteDecision:
    snapshot = candidate.capability
    reasons: list[str] = []

    if snapshot.service_id != request.service_id:
        reasons.append("service_mismatch")
    if (
        request.required_provider_id is not None
        and snapshot.provider_id != request.required_provider_id
    ):
        reasons.append("required_provider_mismatch")
    if reasons:
        return _candidate_decision(candidate, reasons, None)

    policy_reasons = _policy_reasons(request, candidate)
    if policy_reasons:
        return _candidate_decision(candidate, policy_reasons, None)

    runtime_reasons = _runtime_reasons(request, candidate)
    if runtime_reasons:
        return _candidate_decision(candidate, runtime_reasons, None)

    try:
        evaluation = evaluate_provider_capability(
            snapshot,
            required_gates=request.required_gates,
            now=now,
            max_age_seconds=max_age_seconds,
        )
    except ServiceStateValidationError:
        return _candidate_decision(
            candidate,
            ["capability_evidence_invalid"],
            None,
        )

    if evaluation.ready:
        return _candidate_decision(candidate, (), evaluation)

    capability_reasons = [
        f"capability_connection_{evaluation.connection_state.value}"
    ]
    capability_reasons.extend(
        f"capability_{decision.gate.value}_{decision.reason_code}"
        for decision in evaluation.decisions
        if not decision.allowed
    )
    return _candidate_decision(candidate, capability_reasons, evaluation)


def _policy_reasons(
    request: RouteRequest,
    candidate: RuntimeLaneCandidate,
) -> list[str]:
    policy = candidate.policy
    reasons: list[str] = []
    if policy.approval_state in {ApprovalState.UNKNOWN, ApprovalState.REQUIRED}:
        reasons.append("policy_approval_required")
    elif policy.approval_state == ApprovalState.DENIED:
        reasons.append("policy_approval_denied")
    elif policy.approval_state != ApprovalState.APPROVED:
        raise RuntimeRouterValidationError("unsupported approval state")

    if request.data_classification not in policy.allowed_data_classifications:
        reasons.append("policy_data_classification_not_allowed")

    if candidate.runtime_kind is RuntimeKind.LOCAL:
        if policy.local_compute_mode is LocalComputeMode.OFF:
            reasons.append("policy_local_compute_off")
        if candidate.interactive_lock:
            reasons.append("policy_interactive_lock")
    return reasons


def _runtime_reasons(
    request: RouteRequest,
    candidate: RuntimeLaneCandidate,
) -> list[str]:
    reasons: list[str] = []
    if candidate.runtime_kind is RuntimeKind.LOCAL:
        if candidate.availability in {
            RuntimeAvailability.OFFLINE,
            RuntimeAvailability.DRAINING,
            RuntimeAvailability.FAULTED,
        }:
            reasons.append(
                f"capability_runtime_availability_{candidate.availability.value}"
            )
        if candidate.health in {RuntimeHealth.UNKNOWN, RuntimeHealth.FAULTED}:
            reasons.append(f"capability_runtime_health_{candidate.health.value}")

    available = set(candidate.runtime_capabilities)
    for capability in request.required_runtime_capabilities:
        if capability not in available:
            reasons.append(
                "capability_runtime_missing_" + _reason_fragment(capability)
            )
    return reasons


def _candidate_decision(
    candidate: RuntimeLaneCandidate,
    reasons: Iterable[str],
    evaluation: CapabilityEvaluation | None,
) -> CandidateRouteDecision:
    normalized_reasons = tuple(
        sorted({_token(reason, "reason_code") for reason in reasons})
    )
    return CandidateRouteDecision(
        lane_id=candidate.lane_id,
        runtime_id=candidate.runtime_id,
        provider_id=candidate.capability.provider_id,
        service_id=candidate.capability.service_id,
        policy_id=candidate.policy.policy_id,
        eligible=not normalized_reasons,
        reason_codes=normalized_reasons,
        capability_evaluation=evaluation,
    )


def _blocked_reason(
    decisions: tuple[CandidateRouteDecision, ...],
    *,
    request: RouteRequest,
) -> RouteReason:
    relevant = [
        decision
        for decision in decisions
        if decision.service_id == request.service_id
        and (
            request.required_provider_id is None
            or decision.provider_id == request.required_provider_id
        )
    ]
    if not relevant:
        return (
            RouteReason.REQUIRED_PROVIDER_UNAVAILABLE
            if request.required_provider_id is not None
            else RouteReason.NO_ELIGIBLE_LANE
        )

    families: set[str] = set()
    for decision in relevant:
        for reason in decision.reason_codes:
            if reason.startswith("policy_"):
                families.add("policy")
            elif reason.startswith("capability_"):
                families.add("capability")
            else:
                families.add("other")
    if families == {"policy"}:
        return RouteReason.POLICY_BLOCKED
    if families == {"capability"}:
        return RouteReason.CAPABILITY_BLOCKED
    return RouteReason.NO_ELIGIBLE_LANE


def _selection_rank(
    request: RouteRequest,
    candidate: RuntimeLaneCandidate,
) -> tuple[int, int, int, int, int, int, int, str, str]:
    if request.preferred_provider_ids:
        try:
            preference = request.preferred_provider_ids.index(
                candidate.capability.provider_id
            )
        except ValueError:
            preference = len(request.preferred_provider_ids)
    else:
        preference = 0

    aggressive_local_rank = 1
    if (
        candidate.runtime_kind is RuntimeKind.LOCAL
        and candidate.policy.local_compute_mode is LocalComputeMode.AGGRESSIVE
    ):
        aggressive_local_rank = 0

    health_rank = 0 if candidate.health is RuntimeHealth.HEALTHY else 1
    availability_rank = (
        0 if candidate.availability is RuntimeAvailability.READY else 1
    )
    return (
        preference,
        aggressive_local_rank,
        health_rank,
        availability_rank,
        candidate.priority,
        candidate.load_rank,
        candidate.cost_rank,
        candidate.lane_id,
        candidate.runtime_id,
    )


def _candidates(values: Iterable[RuntimeLaneCandidate]) -> tuple[RuntimeLaneCandidate, ...]:
    if isinstance(values, (str, bytes)):
        raise RuntimeRouterValidationError(
            "candidates must be a collection of RuntimeLaneCandidate values"
        )
    try:
        material = tuple(values)
    except TypeError as exc:
        raise RuntimeRouterValidationError(
            "candidates must be an iterable of RuntimeLaneCandidate values"
        ) from exc
    if any(not isinstance(value, RuntimeLaneCandidate) for value in material):
        raise RuntimeRouterValidationError(
            "candidates must contain RuntimeLaneCandidate values"
        )
    lane_ids = [candidate.lane_id for candidate in material]
    if len(set(lane_ids)) != len(lane_ids):
        raise RuntimeRouterValidationError("candidate lane_id values must be unique")
    return material


def _gates(values: tuple[CapabilityGate, ...]) -> tuple[CapabilityGate, ...]:
    if not isinstance(values, tuple) or not values:
        raise RuntimeRouterValidationError(
            "required_gates must be a non-empty tuple of CapabilityGate values"
        )
    if any(not isinstance(value, CapabilityGate) for value in values):
        raise RuntimeRouterValidationError(
            "required_gates must contain CapabilityGate values"
        )
    return tuple(sorted(set(values), key=lambda value: value.value))


def _sorted_tokens(values: tuple[str, ...], field: str) -> tuple[str, ...]:
    if not isinstance(values, tuple):
        raise RuntimeRouterValidationError(f"{field} must be a tuple")
    return tuple(sorted({_token(value, field) for value in values}))


def _ordered_unique_tokens(values: tuple[str, ...], field: str) -> tuple[str, ...]:
    if not isinstance(values, tuple):
        raise RuntimeRouterValidationError(f"{field} must be a tuple")
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        token = _token(value, field)
        if token in seen:
            raise RuntimeRouterValidationError(f"{field} contains duplicates")
        seen.add(token)
        result.append(token)
    return tuple(result)


def _rank(value: object, field: str) -> int:
    if (
        not isinstance(value, int)
        or isinstance(value, bool)
        or not 0 <= value <= 1_000_000
    ):
        raise RuntimeRouterValidationError(
            f"{field} must be an integer from 0 through 1000000"
        )
    return value


def _reason_fragment(value: str) -> str:
    fragment = re.sub(r"[^A-Za-z0-9]+", "_", value).strip("_").lower()
    if not fragment:
        raise RuntimeRouterValidationError(
            "runtime capability must contain a reason-code-safe character"
        )
    return fragment[:80]


def _utc_timestamp(value: object, field: str) -> datetime:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise RuntimeRouterValidationError(
            f"{field} must be a UTC ISO-8601 timestamp"
        )
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise RuntimeRouterValidationError(
            f"{field} must be a UTC ISO-8601 timestamp"
        ) from exc
    if parsed.tzinfo is None or parsed.utcoffset() != timezone.utc.utcoffset(parsed):
        raise RuntimeRouterValidationError(f"{field} must use UTC")
    return parsed.astimezone(timezone.utc)


def _token(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise RuntimeRouterValidationError(f"{field} must be non-empty trimmed text")
    if len(value) > 128:
        raise RuntimeRouterValidationError(f"{field} must be at most 128 characters")
    return value


__all__ = [
    "ApprovalState",
    "CandidateRouteDecision",
    "LocalComputeMode",
    "RouteOutcome",
    "RouteReason",
    "RouteRequest",
    "RuntimeAvailability",
    "RuntimeHealth",
    "RuntimeKind",
    "RuntimeLaneCandidate",
    "RuntimePolicy",
    "RuntimeRouteResult",
    "RuntimeRouterError",
    "RuntimeRouterValidationError",
    "WorkerAdvertisement",
    "WorkerCandidateProjection",
    "WorkerIdentityProof",
    "WorkerIdentityState",
    "project_worker_candidate",
    "route_runtime",
]
