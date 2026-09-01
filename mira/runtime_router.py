"""Provider-neutral capability and policy routing for MIRA.

This module is deliberately read-only. It consumes SOURCE-001 capability evidence
from :mod:`mira.service_state` plus explicit policy/approval inputs and selects at
most one eligible provider/runtime lane. It performs no provider authorization,
discovery, provider I/O, canonical-state mutation, or MIRA service activation.

PROVIDER-001 requires routing from observed evidence rather than provider branding
or a successful consent screen. Consequently, every requested operation carries
its own required capability gates and every candidate is evaluated independently.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
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
class RuntimePolicy:
    """Explicit policy material supplied to the router for one candidate lane.

    ``allowed_data_classifications`` is intentionally opaque/provider-neutral. A
    policy layer may define classifications such as ``personal`` or ``restricted``
    without making those names universal product semantics in this router.
    """

    policy_id: str
    approval_state: ApprovalState
    allowed_data_classifications: tuple[str, ...]

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


@dataclass(frozen=True)
class RuntimeLaneCandidate:
    """One concrete provider/runtime lane that may satisfy a route request."""

    lane_id: str
    runtime_id: str
    capability: ProviderCapabilitySnapshot
    policy: RuntimePolicy
    priority: int = 100

    def __post_init__(self) -> None:
        _token(self.lane_id, "lane_id")
        _token(self.runtime_id, "runtime_id")
        if not isinstance(self.capability, ProviderCapabilitySnapshot):
            raise RuntimeRouterValidationError(
                "capability must be a ProviderCapabilitySnapshot"
            )
        if not isinstance(self.policy, RuntimePolicy):
            raise RuntimeRouterValidationError("policy must be a RuntimePolicy")
        if (
            not isinstance(self.priority, int)
            or isinstance(self.priority, bool)
            or not 0 <= self.priority <= 1_000_000
        ):
            raise RuntimeRouterValidationError(
                "priority must be an integer from 0 through 1000000"
            )


@dataclass(frozen=True)
class RouteRequest:
    """One provider-backed operation with explicit capability requirements."""

    operation_id: str
    service_id: str
    required_gates: tuple[CapabilityGate, ...]
    data_classification: str
    required_provider_id: str | None = None
    preferred_provider_ids: tuple[str, ...] = ()

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

    policy_reasons = _policy_reasons(request, candidate.policy)
    if policy_reasons:
        return _candidate_decision(candidate, policy_reasons, None)

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


def _policy_reasons(request: RouteRequest, policy: RuntimePolicy) -> list[str]:
    reasons: list[str] = []
    if policy.approval_state in {ApprovalState.UNKNOWN, ApprovalState.REQUIRED}:
        reasons.append("policy_approval_required")
    elif policy.approval_state == ApprovalState.DENIED:
        reasons.append("policy_approval_denied")
    elif policy.approval_state != ApprovalState.APPROVED:
        raise RuntimeRouterValidationError("unsupported approval state")

    if request.data_classification not in policy.allowed_data_classifications:
        reasons.append("policy_data_classification_not_allowed")
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
) -> tuple[int, int, str, str]:
    if request.preferred_provider_ids:
        try:
            preference = request.preferred_provider_ids.index(
                candidate.capability.provider_id
            )
        except ValueError:
            preference = len(request.preferred_provider_ids)
    else:
        preference = 0
    return (preference, candidate.priority, candidate.lane_id, candidate.runtime_id)


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
    "RouteOutcome",
    "RouteReason",
    "RouteRequest",
    "RuntimeLaneCandidate",
    "RuntimePolicy",
    "RuntimeRouteResult",
    "RuntimeRouterError",
    "RuntimeRouterValidationError",
    "route_runtime",
]
