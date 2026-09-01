"""Ordinary-user provider connection orchestration for MIRA.

This module is deliberately a pure planning layer. It consumes existing SOURCE-001
capability evidence and PROVIDER-001 runtime routing truth, then determines the
honest connection presentation and next step for either a product-owned client or
a host-controlled client such as stock ChatGPT.

It performs no provider authorization, plugin installation, provider discovery,
provider I/O, durable state mutation, or MIRA service activation. In particular,
a successful install or consent screen is never treated as Connected until the
required capability gates are freshly verified and the runtime router selects an
eligible lane.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .runtime_router import (
    RouteReason,
    RouteRequest,
    RuntimeLaneCandidate,
    RuntimeRouteResult,
    RuntimeRouterValidationError,
    route_runtime,
)
from .service_state import (
    AuthorizationState,
    CapabilityEvaluation,
    CapabilityGate,
    ConnectionState,
)


class ProviderOnboardingError(Exception):
    """Base error for provider-connection orchestration."""


class ProviderOnboardingValidationError(ProviderOnboardingError):
    """Raised when connection-planning input is malformed."""


class ConnectionSurfaceKind(str, Enum):
    """Who controls the connection user interface."""

    PRODUCT_OWNED = "product_owned"
    HOST_CONTROLLED = "host_controlled"


class NativeFlowChannel(str, Enum):
    """Supported native route for unavoidable connection/account ceremony."""

    PROVIDER_NATIVE = "provider_native"
    HOST_NATIVE = "host_native"
    UNAVAILABLE = "unavailable"


class ConnectionCommand(str, Enum):
    """Explicit user/surface command. INSPECT is read-only presentation."""

    INSPECT = "inspect"
    CONNECT = "connect"
    RECONNECT = "reconnect"
    DISCONNECT = "disconnect"


class ConnectionNextAction(str, Enum):
    """Bounded next action emitted by the planner."""

    NONE = "none"
    START_NATIVE_CONNECTION_FLOW = "start_native_connection_flow"
    START_NATIVE_RECONNECTION_FLOW = "start_native_reconnection_flow"
    VERIFY_CAPABILITIES = "verify_capabilities"
    START_NATIVE_DISCONNECT = "start_native_disconnect"
    REPORT_BLOCKER = "report_blocker"


class ConnectionEffectScope(str, Enum):
    """Requested downstream effect; the planner itself remains read-only."""

    NONE = "none"
    CONNECTION_ONLY = "connection_only"


@dataclass(frozen=True)
class ConnectionSurface:
    """Client/host ability to launch native connection-management flows.

    For a host-controlled surface such as stock ChatGPT, ``HOST_NATIVE`` means the
    host owns the supported discovery/install/enable/connect/account-consent flow.
    The planner intentionally does not split those host implementation details
    into user-visible manual steps.
    """

    kind: ConnectionSurfaceKind
    authorization_flow: NativeFlowChannel
    disconnect_flow: NativeFlowChannel

    def __post_init__(self) -> None:
        if not isinstance(self.kind, ConnectionSurfaceKind):
            raise ProviderOnboardingValidationError(
                "kind must be a ConnectionSurfaceKind"
            )
        if not isinstance(self.authorization_flow, NativeFlowChannel):
            raise ProviderOnboardingValidationError(
                "authorization_flow must be a NativeFlowChannel"
            )
        if not isinstance(self.disconnect_flow, NativeFlowChannel):
            raise ProviderOnboardingValidationError(
                "disconnect_flow must be a NativeFlowChannel"
            )
        allowed = (
            {NativeFlowChannel.PROVIDER_NATIVE, NativeFlowChannel.UNAVAILABLE}
            if self.kind == ConnectionSurfaceKind.PRODUCT_OWNED
            else {NativeFlowChannel.HOST_NATIVE, NativeFlowChannel.UNAVAILABLE}
        )
        if self.authorization_flow not in allowed:
            raise ProviderOnboardingValidationError(
                "authorization flow does not match the selected connection surface"
            )
        if self.disconnect_flow not in allowed:
            raise ProviderOnboardingValidationError(
                "disconnect flow does not match the selected connection surface"
            )


@dataclass(frozen=True)
class ConnectionIntent:
    """Explicit user-recognizable provider/service connection target."""

    provider_id: str
    service_id: str
    required_gates: tuple[CapabilityGate, ...]
    data_classification: str

    def __post_init__(self) -> None:
        _token(self.provider_id, "provider_id")
        _token(self.service_id, "service_id")
        _token(self.data_classification, "data_classification")
        if not isinstance(self.required_gates, tuple) or not self.required_gates:
            raise ProviderOnboardingValidationError(
                "required_gates must be a non-empty tuple"
            )
        if any(not isinstance(gate, CapabilityGate) for gate in self.required_gates):
            raise ProviderOnboardingValidationError(
                "required_gates must contain CapabilityGate values"
            )
        object.__setattr__(
            self,
            "required_gates",
            tuple(sorted(set(self.required_gates), key=lambda gate: gate.value)),
        )


@dataclass(frozen=True)
class ConnectionPlan:
    """Read-only connection presentation and next-step plan."""

    provider_id: str
    service_id: str
    surface_kind: ConnectionSurfaceKind
    connection_state: ConnectionState
    available_commands: tuple[ConnectionCommand, ...]
    requested_command: ConnectionCommand
    next_action: ConnectionNextAction
    flow_channel: NativeFlowChannel | None
    effect_scope: ConnectionEffectScope
    reason_codes: tuple[str, ...]
    selected_lane_id: str | None
    selected_runtime_id: str | None

    @property
    def connected(self) -> bool:
        return self.connection_state == ConnectionState.CONNECTED


_STATE_PRECEDENCE = {
    ConnectionState.RECONNECT: 0,
    ConnectionState.CONNECT: 1,
    ConnectionState.NEEDS_ATTENTION: 2,
    ConnectionState.UNAVAILABLE: 3,
    ConnectionState.CONNECTED: 4,
}

_RECOVERABLE_VERIFICATION_REASONS = frozenset(
    {
        "authorization_stale",
        "evidence_unknown",
        "not_verified",
        "evidence_stale",
    }
)


def plan_provider_connection(
    intent: ConnectionIntent,
    surface: ConnectionSurface,
    candidates: Iterable[RuntimeLaneCandidate],
    *,
    command: ConnectionCommand = ConnectionCommand.INSPECT,
    now: str,
    max_age_seconds: int,
) -> ConnectionPlan:
    """Plan one provider/service connection without performing side effects."""

    if not isinstance(intent, ConnectionIntent):
        raise ProviderOnboardingValidationError("intent must be a ConnectionIntent")
    if not isinstance(surface, ConnectionSurface):
        raise ProviderOnboardingValidationError("surface must be a ConnectionSurface")
    if not isinstance(command, ConnectionCommand):
        raise ProviderOnboardingValidationError("command must be a ConnectionCommand")

    material = _candidate_tuple(candidates)
    route_request = RouteRequest(
        operation_id=f"connection:{intent.service_id}",
        service_id=intent.service_id,
        required_gates=intent.required_gates,
        data_classification=intent.data_classification,
        required_provider_id=intent.provider_id,
    )
    try:
        route = route_runtime(
            route_request,
            material,
            now=now,
            max_age_seconds=max_age_seconds,
        )
    except RuntimeRouterValidationError as exc:
        raise ProviderOnboardingValidationError(str(exc)) from exc

    relevant_candidates = tuple(
        candidate
        for candidate in material
        if candidate.capability.provider_id == intent.provider_id
        and candidate.capability.service_id == intent.service_id
    )
    relevant_decisions = tuple(
        decision
        for decision in route.candidate_decisions
        if decision.provider_id == intent.provider_id
        and decision.service_id == intent.service_id
    )

    state = _presentation_state(route, relevant_decisions)
    reason_codes = _reason_codes(route, relevant_decisions)
    authorized_states = tuple(
        candidate.capability.authorization_state for candidate in relevant_candidates
    )

    # A client that cannot launch the required unavoidable native connection
    # ceremony must not advertise a dead Connect/Reconnect control as usable.
    if state in {ConnectionState.CONNECT, ConnectionState.RECONNECT}:
        if surface.authorization_flow == NativeFlowChannel.UNAVAILABLE:
            state = ConnectionState.UNAVAILABLE
            reason_codes = _merge_reasons(
                reason_codes,
                ("surface_native_connection_unavailable",),
            )

    available = _available_commands(
        state,
        relevant_decisions=relevant_decisions,
        authorization_states=authorized_states,
        disconnect_available=(surface.disconnect_flow != NativeFlowChannel.UNAVAILABLE),
    )

    next_action = ConnectionNextAction.NONE
    flow_channel: NativeFlowChannel | None = None
    effect_scope = ConnectionEffectScope.NONE

    if command == ConnectionCommand.INSPECT:
        if state == ConnectionState.NEEDS_ATTENTION:
            if _can_auto_verify(relevant_decisions):
                next_action = ConnectionNextAction.VERIFY_CAPABILITIES
                reason_codes = _merge_reasons(reason_codes, ("verification_required",))
            else:
                next_action = ConnectionNextAction.REPORT_BLOCKER
        elif state == ConnectionState.UNAVAILABLE:
            next_action = ConnectionNextAction.REPORT_BLOCKER

    elif command == ConnectionCommand.CONNECT:
        if state == ConnectionState.CONNECTED:
            reason_codes = _merge_reasons(reason_codes, ("already_connected",))
        elif state == ConnectionState.CONNECT or _authorization_denied(relevant_decisions):
            if surface.authorization_flow == NativeFlowChannel.UNAVAILABLE:
                next_action = ConnectionNextAction.REPORT_BLOCKER
                state = ConnectionState.UNAVAILABLE
                reason_codes = _merge_reasons(
                    reason_codes,
                    ("surface_native_connection_unavailable",),
                )
            else:
                next_action = ConnectionNextAction.START_NATIVE_CONNECTION_FLOW
                flow_channel = surface.authorization_flow
                reason_codes = _merge_reasons(
                    reason_codes,
                    (
                        "host_native_discover_install_connect"
                        if surface.authorization_flow == NativeFlowChannel.HOST_NATIVE
                        else "provider_native_connect"
                    ,),
                )
        else:
            next_action = ConnectionNextAction.REPORT_BLOCKER
            reason_codes = _merge_reasons(reason_codes, ("connect_not_applicable",))

    elif command == ConnectionCommand.RECONNECT:
        if state == ConnectionState.CONNECTED:
            reason_codes = _merge_reasons(reason_codes, ("already_connected",))
        elif state == ConnectionState.RECONNECT:
            if surface.authorization_flow == NativeFlowChannel.UNAVAILABLE:
                next_action = ConnectionNextAction.REPORT_BLOCKER
                state = ConnectionState.UNAVAILABLE
                reason_codes = _merge_reasons(
                    reason_codes,
                    ("surface_native_connection_unavailable",),
                )
            else:
                next_action = ConnectionNextAction.START_NATIVE_RECONNECTION_FLOW
                flow_channel = surface.authorization_flow
                reason_codes = _merge_reasons(
                    reason_codes,
                    (
                        "host_native_reconnect"
                        if surface.authorization_flow == NativeFlowChannel.HOST_NATIVE
                        else "provider_native_reconnect"
                    ,),
                )
        else:
            next_action = ConnectionNextAction.REPORT_BLOCKER
            reason_codes = _merge_reasons(reason_codes, ("reconnect_not_applicable",))

    elif command == ConnectionCommand.DISCONNECT:
        if ConnectionCommand.DISCONNECT not in available:
            next_action = ConnectionNextAction.REPORT_BLOCKER
            reason_codes = _merge_reasons(reason_codes, ("disconnect_not_available",))
        else:
            next_action = ConnectionNextAction.START_NATIVE_DISCONNECT
            flow_channel = surface.disconnect_flow
            effect_scope = ConnectionEffectScope.CONNECTION_ONLY
            reason_codes = _merge_reasons(reason_codes, ("disconnect_connection_only",))

    selected_lane_id = route.selected_lane_id if route.selected else None
    selected_runtime_id = route.selected_runtime_id if route.selected else None

    return ConnectionPlan(
        provider_id=intent.provider_id,
        service_id=intent.service_id,
        surface_kind=surface.kind,
        connection_state=state,
        available_commands=available,
        requested_command=command,
        next_action=next_action,
        flow_channel=flow_channel,
        effect_scope=effect_scope,
        reason_codes=reason_codes,
        selected_lane_id=selected_lane_id,
        selected_runtime_id=selected_runtime_id,
    )


def _presentation_state(
    route: RuntimeRouteResult,
    decisions: tuple[object, ...],
) -> ConnectionState:
    if route.selected:
        return ConnectionState.CONNECTED
    if route.reason in {RouteReason.NO_CANDIDATES, RouteReason.REQUIRED_PROVIDER_UNAVAILABLE}:
        return ConnectionState.UNAVAILABLE

    evaluations = tuple(
        decision.capability_evaluation
        for decision in decisions
        if getattr(decision, "capability_evaluation", None) is not None
    )
    actionable = tuple(
        evaluation.connection_state
        for evaluation in evaluations
        if isinstance(evaluation, CapabilityEvaluation)
        and evaluation.connection_state != ConnectionState.CONNECTED
    )
    if actionable:
        return min(actionable, key=lambda state: _STATE_PRECEDENCE[state])

    policy_reasons = {
        reason
        for decision in decisions
        for reason in getattr(decision, "reason_codes", ())
        if reason.startswith("policy_")
    }
    if "policy_approval_required" in policy_reasons:
        return ConnectionState.NEEDS_ATTENTION
    if policy_reasons:
        return ConnectionState.UNAVAILABLE
    return ConnectionState.NEEDS_ATTENTION


def _available_commands(
    state: ConnectionState,
    *,
    relevant_decisions: tuple[object, ...],
    authorization_states: tuple[AuthorizationState, ...],
    disconnect_available: bool,
) -> tuple[ConnectionCommand, ...]:
    commands: list[ConnectionCommand] = []
    if state == ConnectionState.CONNECT:
        commands.append(ConnectionCommand.CONNECT)
    elif state == ConnectionState.RECONNECT:
        commands.append(ConnectionCommand.RECONNECT)
    elif state == ConnectionState.NEEDS_ATTENTION and _authorization_denied(relevant_decisions):
        commands.append(ConnectionCommand.CONNECT)

    can_disconnect = any(
        state_value
        in {
            AuthorizationState.AUTHORIZED,
            AuthorizationState.EXPIRED,
            AuthorizationState.REVOKED,
        }
        for state_value in authorization_states
    )
    if can_disconnect and disconnect_available:
        commands.append(ConnectionCommand.DISCONNECT)
    return tuple(commands)


def _can_auto_verify(decisions: tuple[object, ...]) -> bool:
    saw_evaluation = False
    saw_blocker = False
    for decision in decisions:
        evaluation = getattr(decision, "capability_evaluation", None)
        if not isinstance(evaluation, CapabilityEvaluation):
            continue
        saw_evaluation = True
        for gate in evaluation.decisions:
            if gate.allowed:
                continue
            saw_blocker = True
            if gate.reason_code not in _RECOVERABLE_VERIFICATION_REASONS:
                return False
    return saw_evaluation and saw_blocker


def _authorization_denied(decisions: tuple[object, ...]) -> bool:
    for decision in decisions:
        evaluation = getattr(decision, "capability_evaluation", None)
        if not isinstance(evaluation, CapabilityEvaluation):
            continue
        if any(
            gate.reason_code == "authorization_denied"
            for gate in evaluation.decisions
        ):
            return True
    return False


def _reason_codes(
    route: RuntimeRouteResult,
    decisions: tuple[object, ...],
) -> tuple[str, ...]:
    reasons = {f"route_{route.reason.value}"}
    for decision in decisions:
        reasons.update(getattr(decision, "reason_codes", ()))
    return tuple(sorted(reasons))


def _merge_reasons(
    existing: tuple[str, ...],
    additional: Iterable[str],
) -> tuple[str, ...]:
    return tuple(
        sorted(set(existing).union(_token(value, "reason_code") for value in additional))
    )


def _candidate_tuple(
    candidates: Iterable[RuntimeLaneCandidate],
) -> tuple[RuntimeLaneCandidate, ...]:
    if isinstance(candidates, (str, bytes)):
        raise ProviderOnboardingValidationError(
            "candidates must be a collection of RuntimeLaneCandidate values"
        )
    try:
        material = tuple(candidates)
    except TypeError as exc:
        raise ProviderOnboardingValidationError(
            "candidates must be an iterable of RuntimeLaneCandidate values"
        ) from exc
    if any(not isinstance(candidate, RuntimeLaneCandidate) for candidate in material):
        raise ProviderOnboardingValidationError(
            "candidates must contain RuntimeLaneCandidate values"
        )
    return material


def _token(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise ProviderOnboardingValidationError(
            f"{field} must be non-empty trimmed text"
        )
    if len(value) > 128:
        raise ProviderOnboardingValidationError(
            f"{field} must be at most 128 characters"
        )
    return value


__all__ = [
    "ConnectionCommand",
    "ConnectionEffectScope",
    "ConnectionIntent",
    "ConnectionNextAction",
    "ConnectionPlan",
    "ConnectionSurface",
    "ConnectionSurfaceKind",
    "NativeFlowChannel",
    "ProviderOnboardingError",
    "ProviderOnboardingValidationError",
    "plan_provider_connection",
]
