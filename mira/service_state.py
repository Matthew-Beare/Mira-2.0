"""Explicit provider-neutral MIRA service, capability, and worker registry state.

SERVICE-001 requires user intent, recommendation, provider capability/readiness,
and actual activation to remain separate truths. SOURCE-001 / PROVIDER-001 also
require provider authorization, read, write, and exact remote-readback evidence
to remain independent rather than collapsing "OAuth succeeded" into "ready".

This module also owns the durable secret-free compute-worker registry used by the
optional LOCAL-001 compute fabric. It performs no worker authentication transport,
provider I/O, job scheduling, network listening, or private-machine binding.
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

WORKER_RESOURCE_TYPE = "compute_worker"
WORKER_SCHEMA_VERSION = 1

ACTIVATION_STATES = frozenset({"disabled", "requested", "active", "suspended"})
CAPABILITY_STATES = frozenset({"unknown", "unavailable", "available"})
RECOMMENDATION_STATES = frozenset({"none", "suggested"})

WORKER_IDENTITY_STATES = frozenset({"unverified", "verified", "revoked"})
WORKER_RUNTIME_KINDS = frozenset({"hosted", "local"})
WORKER_APPROVAL_STATES = frozenset({"unknown", "required", "approved", "denied"})
WORKER_LOCAL_COMPUTE_MODES = frozenset({"off", "normal", "aggressive"})
WORKER_AVAILABILITY_STATES = frozenset(
    {"ready", "busy", "offline", "draining", "faulted"}
)
WORKER_HEALTH_STATES = frozenset({"healthy", "degraded", "unknown", "faulted"})


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
        normalized_scopes = tuple(
            sorted({_text(scope, "scope", 512) for scope in self.scopes})
        )
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
        raise ServiceStateValidationError(
            "max_age_seconds must be a positive integer"
        )

    authorization = snapshot.authorization_state
    if authorization == AuthorizationState.UNAVAILABLE:
        return _blocked_evaluation(
            snapshot,
            required,
            ConnectionState.UNAVAILABLE,
            "authorization_unavailable",
        )
    if authorization in {AuthorizationState.UNKNOWN, AuthorizationState.REQUIRED}:
        return _blocked_evaluation(
            snapshot, required, ConnectionState.CONNECT, "authorization_required"
        )
    if authorization in {AuthorizationState.EXPIRED, AuthorizationState.REVOKED}:
        return _blocked_evaluation(
            snapshot,
            required,
            ConnectionState.RECONNECT,
            f"authorization_{authorization.value}",
        )
    if authorization == AuthorizationState.DENIED:
        return _blocked_evaluation(
            snapshot,
            required,
            ConnectionState.NEEDS_ATTENTION,
            "authorization_denied",
        )
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

    observations = {
        observation.gate: observation for observation in snapshot.gates
    }
    decisions: list[GateDecision] = []
    saw_unavailable = False
    for gate in required:
        observation = observations.get(gate)
        if (
            observation is None
            or observation.state == CapabilityEvidenceState.UNKNOWN
        ):
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
                GateDecision(
                    gate,
                    False,
                    observation.reason_code or "verification_failed",
                )
            )
            continue
        if observation.state != CapabilityEvidenceState.VERIFIED:
            raise ServiceStateValidationError(
                "unsupported capability evidence state"
            )
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


def _required_gates(
    values: Iterable[CapabilityGate],
) -> tuple[CapabilityGate, ...]:
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
        raise ServiceStateValidationError(
            "at least one required gate is required"
        )
    if any(not isinstance(value, CapabilityGate) for value in material):
        raise ServiceStateValidationError(
            "required_gates must contain CapabilityGate values"
        )
    return tuple(sorted(set(material), key=lambda value: value.value))


def _utc_timestamp(value: Any, field: str) -> datetime:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise ServiceStateValidationError(
            f"{field} must be a UTC ISO-8601 timestamp"
        )
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ServiceStateValidationError(
            f"{field} must be a UTC ISO-8601 timestamp"
        ) from exc
    if (
        parsed.tzinfo is None
        or parsed.utcoffset() != timezone.utc.utcoffset(parsed)
    ):
        raise ServiceStateValidationError(f"{field} must use UTC")
    return parsed.astimezone(timezone.utc)


def _is_stale(
    observed_at: datetime, now: datetime, max_age_seconds: int
) -> bool:
    if observed_at > now:
        raise ServiceStateValidationError(
            "capability evidence cannot be from the future"
        )
    return (now - observed_at).total_seconds() > max_age_seconds


@dataclass(frozen=True)
class WorkerRegistryIdentityEvidence:
    """Secret-free external worker identity evidence accepted by the registry."""

    principal_id: str
    state: str
    verified_at: str

    def __post_init__(self) -> None:
        _token(self.principal_id, "principal_id")
        _enum(self.state, WORKER_IDENTITY_STATES, "identity_state")
        _utc_timestamp(self.verified_at, "identity_verified_at")


@dataclass(frozen=True)
class WorkerRegistryView:
    """Validated durable compute-worker record."""

    worker_id: str
    revision: int
    principal_id: str
    identity_state: str
    identity_verified_at: str
    lane_id: str
    runtime_id: str
    service_id: str
    runtime_kind: str
    runtime_capabilities: tuple[str, ...]
    policy_id: str
    approval_state: str
    allowed_data_classifications: tuple[str, ...]
    local_compute_mode: str
    availability: str
    health: str
    interactive_lock: bool
    priority: int
    load_rank: int
    cost_rank: int
    heartbeat_at: str
    idempotent_replay: bool = False


class WorkerRegistryService:
    """Persist replay-safe, secret-free worker state through STORE-001 semantics."""

    def __init__(self, adapter: StructuredStateAdapter) -> None:
        self._adapter = adapter

    def register(
        self,
        worker_id: str,
        *,
        identity: WorkerRegistryIdentityEvidence,
        lane_id: str,
        runtime_id: str,
        service_id: str,
        runtime_kind: str,
        runtime_capabilities: Iterable[str],
        policy_id: str,
        approval_state: str,
        allowed_data_classifications: Iterable[str],
        local_compute_mode: str,
        availability: str,
        health: str,
        interactive_lock: bool,
        priority: int,
        load_rank: int,
        cost_rank: int,
        heartbeat_at: str,
        now: str,
        idempotency_key: str,
    ) -> WorkerRegistryView:
        worker = _token(worker_id, "worker_id")
        key = _token(idempotency_key, "idempotency_key")
        _verify_worker_identity(
            identity,
            expected_principal_id=identity.principal_id,
            heartbeat_at=heartbeat_at,
            now=now,
        )
        payload = _worker_payload(
            worker_id=worker,
            principal_id=identity.principal_id,
            identity_state=identity.state,
            identity_verified_at=identity.verified_at,
            lane_id=lane_id,
            runtime_id=runtime_id,
            service_id=service_id,
            runtime_kind=runtime_kind,
            runtime_capabilities=runtime_capabilities,
            policy_id=policy_id,
            approval_state=approval_state,
            allowed_data_classifications=allowed_data_classifications,
            local_compute_mode=local_compute_mode,
            availability=availability,
            health=health,
            interactive_lock=interactive_lock,
            priority=priority,
            load_rank=load_rank,
            cost_rank=cost_rank,
            heartbeat_at=heartbeat_at,
        )
        result = self._adapter.upsert(
            WORKER_RESOURCE_TYPE,
            worker,
            payload,
            idempotency_key=key,
            expected_revision=0,
        )
        return _worker_view(
            result.record, idempotent_replay=result.idempotent_replay
        )

    def get(self, worker_id: str) -> WorkerRegistryView:
        worker = _token(worker_id, "worker_id")
        try:
            record = self._adapter.get(WORKER_RESOURCE_TYPE, worker)
        except NotFoundError as exc:
            raise ServiceStateValidationError(
                f"unknown compute worker: {worker}"
            ) from exc
        return _worker_view(record)

    def heartbeat(
        self,
        worker_id: str,
        *,
        identity: WorkerRegistryIdentityEvidence,
        heartbeat_at: str,
        now: str,
        idempotency_key: str,
        runtime_capabilities: Iterable[str] | None = None,
        availability: str | None = None,
        health: str | None = None,
        interactive_lock: bool | None = None,
        load_rank: int | None = None,
    ) -> WorkerRegistryView:
        current = self.get(worker_id)
        _verify_worker_identity(
            identity,
            expected_principal_id=current.principal_id,
            heartbeat_at=heartbeat_at,
            now=now,
        )
        identity_time = _utc_timestamp(
            identity.verified_at, "identity_verified_at"
        )
        prior_identity_time = _utc_timestamp(
            current.identity_verified_at, "identity_verified_at"
        )
        if identity_time < prior_identity_time:
            raise ServiceStateValidationError(
                "worker identity verification time cannot move backwards"
            )
        heartbeat_time = _utc_timestamp(heartbeat_at, "heartbeat_at")
        prior_heartbeat_time = _utc_timestamp(
            current.heartbeat_at, "heartbeat_at"
        )
        if heartbeat_time < prior_heartbeat_time:
            raise ServiceStateValidationError(
                "worker heartbeat time cannot move backwards"
            )

        payload = _worker_payload(
            worker_id=current.worker_id,
            principal_id=current.principal_id,
            identity_state=identity.state,
            identity_verified_at=identity.verified_at,
            lane_id=current.lane_id,
            runtime_id=current.runtime_id,
            service_id=current.service_id,
            runtime_kind=current.runtime_kind,
            runtime_capabilities=(
                current.runtime_capabilities
                if runtime_capabilities is None
                else runtime_capabilities
            ),
            policy_id=current.policy_id,
            approval_state=current.approval_state,
            allowed_data_classifications=current.allowed_data_classifications,
            local_compute_mode=current.local_compute_mode,
            availability=(
                current.availability if availability is None else availability
            ),
            health=current.health if health is None else health,
            interactive_lock=(
                current.interactive_lock
                if interactive_lock is None
                else interactive_lock
            ),
            priority=current.priority,
            load_rank=current.load_rank if load_rank is None else load_rank,
            cost_rank=current.cost_rank,
            heartbeat_at=heartbeat_at,
        )
        result = self._adapter.upsert(
            WORKER_RESOURCE_TYPE,
            current.worker_id,
            payload,
            idempotency_key=_token(idempotency_key, "idempotency_key"),
            expected_revision=current.revision,
        )
        return _worker_view(
            result.record, idempotent_replay=result.idempotent_replay
        )

    def list_workers(self, *, limit: int = 1000) -> tuple[WorkerRegistryView, ...]:
        records = self._adapter.query(WORKER_RESOURCE_TYPE, limit=limit)
        workers = [_worker_view(record) for record in records]
        workers.sort(key=lambda worker: worker.worker_id)
        return tuple(workers)


def _verify_worker_identity(
    identity: WorkerRegistryIdentityEvidence,
    *,
    expected_principal_id: str,
    heartbeat_at: str,
    now: str,
) -> None:
    if not isinstance(identity, WorkerRegistryIdentityEvidence):
        raise ServiceStateValidationError(
            "identity must be a WorkerRegistryIdentityEvidence"
        )
    principal = _token(expected_principal_id, "principal_id")
    if identity.principal_id != principal:
        raise ServiceStateValidationError(
            "worker identity principal mismatch"
        )
    if identity.state != "verified":
        raise ServiceStateValidationError(
            "worker identity must be verified"
        )
    identity_time = _utc_timestamp(
        identity.verified_at, "identity_verified_at"
    )
    heartbeat_time = _utc_timestamp(heartbeat_at, "heartbeat_at")
    now_time = _utc_timestamp(now, "now")
    if identity_time > heartbeat_time:
        raise ServiceStateValidationError(
            "worker heartbeat must not predate identity verification"
        )
    if heartbeat_time > now_time:
        raise ServiceStateValidationError(
            "worker heartbeat cannot be from the future"
        )
    if identity_time > now_time:
        raise ServiceStateValidationError(
            "worker identity evidence cannot be from the future"
        )


def _worker_payload(
    *,
    worker_id: str,
    principal_id: str,
    identity_state: str,
    identity_verified_at: str,
    lane_id: str,
    runtime_id: str,
    service_id: str,
    runtime_kind: str,
    runtime_capabilities: Iterable[str],
    policy_id: str,
    approval_state: str,
    allowed_data_classifications: Iterable[str],
    local_compute_mode: str,
    availability: str,
    health: str,
    interactive_lock: bool,
    priority: int,
    load_rank: int,
    cost_rank: int,
    heartbeat_at: str,
) -> dict[str, Any]:
    capabilities = _worker_tokens(
        runtime_capabilities,
        "runtime_capabilities",
        allow_empty=False,
    )
    data_classes = _worker_tokens(
        allowed_data_classifications,
        "allowed_data_classifications",
        allow_empty=False,
    )
    payload = {
        "schema_version": WORKER_SCHEMA_VERSION,
        "worker_id": _token(worker_id, "worker_id"),
        "principal_id": _token(principal_id, "principal_id"),
        "identity_state": _enum(
            identity_state, WORKER_IDENTITY_STATES, "identity_state"
        ),
        "identity_verified_at": _utc_text(
            identity_verified_at, "identity_verified_at"
        ),
        "lane_id": _token(lane_id, "lane_id"),
        "runtime_id": _token(runtime_id, "runtime_id"),
        "service_id": _token(service_id, "service_id"),
        "runtime_kind": _enum(
            runtime_kind, WORKER_RUNTIME_KINDS, "runtime_kind"
        ),
        "runtime_capabilities": list(capabilities),
        "policy_id": _token(policy_id, "policy_id"),
        "approval_state": _enum(
            approval_state, WORKER_APPROVAL_STATES, "approval_state"
        ),
        "allowed_data_classifications": list(data_classes),
        "local_compute_mode": _enum(
            local_compute_mode,
            WORKER_LOCAL_COMPUTE_MODES,
            "local_compute_mode",
        ),
        "availability": _enum(
            availability,
            WORKER_AVAILABILITY_STATES,
            "availability",
        ),
        "health": _enum(health, WORKER_HEALTH_STATES, "health"),
        "interactive_lock": _bool(interactive_lock, "interactive_lock"),
        "priority": _rank(priority, "priority"),
        "load_rank": _rank(load_rank, "load_rank"),
        "cost_rank": _rank(cost_rank, "cost_rank"),
        "heartbeat_at": _utc_text(heartbeat_at, "heartbeat_at"),
    }
    _validate_worker_payload(payload, expected_worker_id=payload["worker_id"])
    return payload


def _worker_view(
    record: ResourceRecord,
    *,
    idempotent_replay: bool = False,
) -> WorkerRegistryView:
    payload = deepcopy(record.payload)
    _validate_worker_payload(payload, expected_worker_id=record.resource_id)
    return WorkerRegistryView(
        worker_id=record.resource_id,
        revision=record.revision,
        principal_id=payload["principal_id"],
        identity_state=payload["identity_state"],
        identity_verified_at=payload["identity_verified_at"],
        lane_id=payload["lane_id"],
        runtime_id=payload["runtime_id"],
        service_id=payload["service_id"],
        runtime_kind=payload["runtime_kind"],
        runtime_capabilities=tuple(payload["runtime_capabilities"]),
        policy_id=payload["policy_id"],
        approval_state=payload["approval_state"],
        allowed_data_classifications=tuple(
            payload["allowed_data_classifications"]
        ),
        local_compute_mode=payload["local_compute_mode"],
        availability=payload["availability"],
        health=payload["health"],
        interactive_lock=payload["interactive_lock"],
        priority=payload["priority"],
        load_rank=payload["load_rank"],
        cost_rank=payload["cost_rank"],
        heartbeat_at=payload["heartbeat_at"],
        idempotent_replay=idempotent_replay,
    )


def _validate_worker_payload(
    payload: dict[str, Any],
    *,
    expected_worker_id: str,
) -> None:
    if not isinstance(payload, dict):
        raise ServiceStateValidationError(
            "compute-worker payload must be an object"
        )
    expected_keys = {
        "schema_version",
        "worker_id",
        "principal_id",
        "identity_state",
        "identity_verified_at",
        "lane_id",
        "runtime_id",
        "service_id",
        "runtime_kind",
        "runtime_capabilities",
        "policy_id",
        "approval_state",
        "allowed_data_classifications",
        "local_compute_mode",
        "availability",
        "health",
        "interactive_lock",
        "priority",
        "load_rank",
        "cost_rank",
        "heartbeat_at",
    }
    if set(payload) != expected_keys:
        raise ServiceStateValidationError(
            "compute-worker payload fields do not match the supported schema"
        )
    if payload.get("schema_version") != WORKER_SCHEMA_VERSION:
        raise ServiceStateValidationError(
            "unsupported compute-worker schema version"
        )
    if payload.get("worker_id") != expected_worker_id:
        raise ServiceStateValidationError(
            "compute-worker identity/readback mismatch"
        )
    _token(payload["worker_id"], "worker_id")
    _token(payload["principal_id"], "principal_id")
    if (
        _enum(
            payload["identity_state"],
            WORKER_IDENTITY_STATES,
            "identity_state",
        )
        != "verified"
    ):
        raise ServiceStateValidationError(
            "persisted compute worker must have verified identity state"
        )
    identity_time = _utc_timestamp(
        payload["identity_verified_at"], "identity_verified_at"
    )
    _token(payload["lane_id"], "lane_id")
    _token(payload["runtime_id"], "runtime_id")
    _token(payload["service_id"], "service_id")
    _enum(payload["runtime_kind"], WORKER_RUNTIME_KINDS, "runtime_kind")
    capabilities = payload["runtime_capabilities"]
    if not isinstance(capabilities, list):
        raise ServiceStateValidationError(
            "runtime_capabilities must be a sorted unique list"
        )
    if list(
        _worker_tokens(
            capabilities,
            "runtime_capabilities",
            allow_empty=False,
        )
    ) != capabilities:
        raise ServiceStateValidationError(
            "runtime_capabilities must be a sorted unique list"
        )
    _token(payload["policy_id"], "policy_id")
    _enum(
        payload["approval_state"],
        WORKER_APPROVAL_STATES,
        "approval_state",
    )
    data_classes = payload["allowed_data_classifications"]
    if not isinstance(data_classes, list):
        raise ServiceStateValidationError(
            "allowed_data_classifications must be a sorted unique list"
        )
    if list(
        _worker_tokens(
            data_classes,
            "allowed_data_classifications",
            allow_empty=False,
        )
    ) != data_classes:
        raise ServiceStateValidationError(
            "allowed_data_classifications must be a sorted unique list"
        )
    _enum(
        payload["local_compute_mode"],
        WORKER_LOCAL_COMPUTE_MODES,
        "local_compute_mode",
    )
    _enum(
        payload["availability"],
        WORKER_AVAILABILITY_STATES,
        "availability",
    )
    _enum(payload["health"], WORKER_HEALTH_STATES, "health")
    _bool(payload["interactive_lock"], "interactive_lock")
    _rank(payload["priority"], "priority")
    _rank(payload["load_rank"], "load_rank")
    _rank(payload["cost_rank"], "cost_rank")
    heartbeat_time = _utc_timestamp(payload["heartbeat_at"], "heartbeat_at")
    if identity_time > heartbeat_time:
        raise ServiceStateValidationError(
            "persisted worker heartbeat predates identity verification"
        )


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
        return (
            self.capability_state == "available"
            and not self.dependency_blockers
        )

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
            return _view(
                result.record,
                idempotent_replay=result.idempotent_replay,
            )

    def get(self, service_id: str) -> ServiceStateView:
        service_id = _token(service_id, "service_id")
        try:
            return _view(self._adapter.get(RESOURCE_TYPE, service_id))
        except NotFoundError as exc:
            raise ServiceStateValidationError(
                f"unknown service state: {service_id}"
            ) from exc

    def request_enable(
        self, service_id: str, *, idempotency_key: str
    ) -> ServiceStateView:
        def change(payload: dict[str, Any]) -> None:
            if payload["activation_state"] == "active":
                return
            payload["activation_state"] = "requested"
            payload["suspension_reason"] = None

        return self._mutate(service_id, idempotency_key, change)

    def recommend(
        self, service_id: str, *, idempotency_key: str
    ) -> ServiceStateView:
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
        capability = _enum(
            capability_state, CAPABILITY_STATES, "capability_state"
        )
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
            capability_state=(
                "available" if evaluation.ready else "unavailable"
            ),
            dependency_blockers=(
                () if evaluation.ready else evaluation.blockers
            ),
            idempotency_key=idempotency_key,
        )

    def activate(
        self, service_id: str, *, idempotency_key: str
    ) -> ServiceStateView:
        current = self.ensure(service_id)
        if current.activation_state not in {"requested", "suspended"}:
            raise ServiceIntentRequiredError(
                "service activation requires explicit user request before activation"
            )
        if not current.ready:
            reasons = list(current.dependency_blockers)
            if current.capability_state != "available":
                reasons.insert(
                    0, f"capability:{current.capability_state}"
                )
            detail = ", ".join(reasons) or "readiness unknown"
            raise ServiceNotReadyError(
                f"service is not ready: {detail}"
            )

        def change(payload: dict[str, Any]) -> None:
            payload["activation_state"] = "active"
            payload["suspension_reason"] = None

        return self._mutate_existing(
            service_id, idempotency_key, change
        )

    def disable(
        self, service_id: str, *, idempotency_key: str
    ) -> ServiceStateView:
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
            raise ServiceStateValidationError(
                "wants_help must be boolean"
            )
        if wants_help:
            return self.request_enable(
                service_id, idempotency_key=idempotency_key
            )
        return self.disable(
            service_id, idempotency_key=idempotency_key
        )

    def _mutate(
        self,
        service_id: str,
        idempotency_key: str,
        change: Callable[[dict[str, Any]], None],
    ) -> ServiceStateView:
        self.ensure(service_id)
        return self._mutate_existing(
            service_id, idempotency_key, change
        )

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
        _validate_payload(
            payload, expected_service_id=service_id
        )
        before = deepcopy(payload)
        change(payload)
        _validate_payload(
            payload, expected_service_id=service_id
        )
        if payload == before:
            return _view(record, idempotent_replay=True)
        result = self._adapter.upsert(
            RESOURCE_TYPE,
            service_id,
            payload,
            idempotency_key=key,
            expected_revision=record.revision,
        )
        return _view(
            result.record,
            idempotent_replay=result.idempotent_replay,
        )


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


def _view(
    record: ResourceRecord,
    *,
    idempotent_replay: bool = False,
) -> ServiceStateView:
    payload = deepcopy(record.payload)
    _validate_payload(
        payload, expected_service_id=record.resource_id
    )
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


def _validate_payload(
    payload: dict[str, Any],
    *,
    expected_service_id: str,
) -> None:
    if not isinstance(payload, dict):
        raise ServiceStateValidationError(
            "service-state payload must be an object"
        )
    if payload.get("schema_version") != SCHEMA_VERSION:
        raise ServiceStateValidationError(
            "unsupported service-state schema version"
        )
    if payload.get("service_id") != expected_service_id:
        raise ServiceStateValidationError(
            "service-state identity/readback mismatch"
        )
    _enum(
        payload.get("activation_state"),
        ACTIVATION_STATES,
        "activation_state",
    )
    _enum(
        payload.get("capability_state"),
        CAPABILITY_STATES,
        "capability_state",
    )
    _enum(
        payload.get("recommendation_state"),
        RECOMMENDATION_STATES,
        "recommendation_state",
    )
    blockers = payload.get("dependency_blockers")
    normalized_blockers = _blockers(
        blockers if isinstance(blockers, list) else ()
    )
    if list(normalized_blockers) != blockers:
        raise ServiceStateValidationError(
            "dependency_blockers must be a sorted unique list of non-empty tokens"
        )
    suspension_reason = payload.get("suspension_reason")
    if suspension_reason is not None:
        _token(suspension_reason, "suspension_reason")
    if payload["activation_state"] == "active":
        if (
            payload["capability_state"] != "available"
            or blockers
        ):
            raise ServiceStateValidationError(
                "persisted active service must have verified available capability and no blockers"
            )
    if (
        payload["activation_state"] == "suspended"
        and suspension_reason is None
    ):
        raise ServiceStateValidationError(
            "suspended service requires suspension_reason"
        )


def _blockers(values: Iterable[str]) -> tuple[str, ...]:
    if isinstance(values, (str, bytes)):
        raise ServiceStateValidationError(
            "dependency_blockers must be a collection of tokens"
        )
    try:
        normalized = tuple(
            sorted(
                {
                    _token(value, "dependency_blocker")
                    for value in values
                }
            )
        )
    except TypeError as exc:
        raise ServiceStateValidationError(
            "dependency_blockers must be an iterable of tokens"
        ) from exc
    return normalized


def _worker_tokens(
    values: Iterable[str],
    field: str,
    *,
    allow_empty: bool,
) -> tuple[str, ...]:
    if isinstance(values, (str, bytes)):
        raise ServiceStateValidationError(
            f"{field} must be a collection of tokens"
        )
    try:
        material = tuple(values)
    except TypeError as exc:
        raise ServiceStateValidationError(
            f"{field} must be an iterable of tokens"
        ) from exc
    if not material and not allow_empty:
        raise ServiceStateValidationError(
            f"{field} must not be empty"
        )
    normalized = tuple(
        sorted({_token(value, field) for value in material})
    )
    if len(normalized) != len(material):
        raise ServiceStateValidationError(
            f"{field} must not contain duplicates"
        )
    return normalized


def _enum(
    value: Any,
    allowed: frozenset[str],
    field: str,
) -> str:
    token = _token(value, field)
    if token not in allowed:
        raise ServiceStateValidationError(
            f"{field} must be one of: {', '.join(sorted(allowed))}"
        )
    return token


def _bool(value: Any, field: str) -> bool:
    if not isinstance(value, bool):
        raise ServiceStateValidationError(
            f"{field} must be boolean"
        )
    return value


def _rank(value: Any, field: str) -> int:
    if (
        not isinstance(value, int)
        or isinstance(value, bool)
        or not 0 <= value <= 1_000_000
    ):
        raise ServiceStateValidationError(
            f"{field} must be an integer from 0 through 1000000"
        )
    return value


def _utc_text(value: Any, field: str) -> str:
    _utc_timestamp(value, field)
    return value


def _text(value: Any, field: str, max_length: int) -> str:
    if (
        not isinstance(value, str)
        or not value.strip()
        or value != value.strip()
    ):
        raise ServiceStateValidationError(
            f"{field} must be non-empty trimmed text"
        )
    if len(value) > max_length:
        raise ServiceStateValidationError(
            f"{field} must be at most {max_length} characters"
        )
    return value


def _token(value: Any, field: str) -> str:
    if (
        not isinstance(value, str)
        or not value.strip()
        or value != value.strip()
    ):
        raise ServiceStateValidationError(
            f"{field} must be a non-empty trimmed string"
        )
    if len(value) > 128:
        raise ServiceStateValidationError(
            f"{field} must be at most 128 characters"
        )
    return value


__all__ = [
    "ACTIVATION_STATES",
    "CAPABILITY_STATES",
    "RECOMMENDATION_STATES",
    "RESOURCE_TYPE",
    "WORKER_APPROVAL_STATES",
    "WORKER_AVAILABILITY_STATES",
    "WORKER_HEALTH_STATES",
    "WORKER_IDENTITY_STATES",
    "WORKER_LOCAL_COMPUTE_MODES",
    "WORKER_RESOURCE_TYPE",
    "WORKER_RUNTIME_KINDS",
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
    "WorkerRegistryIdentityEvidence",
    "WorkerRegistryService",
    "WorkerRegistryView",
    "evaluate_provider_capability",
]
