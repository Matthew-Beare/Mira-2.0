"""Deterministic provider-neutral lifecycle planning for optional MIRA compute workers.

This module composes validated worker state, durable compute-job views, explicit
lifecycle locks, generic power observations and optional deterministic hardware
safety decisions. It returns action requirements only. It does not send WOL,
shutdown a host, mutate worker/job state, kill processes, or bind private hardware.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
import re
from typing import Iterable

from .command_sequencer import ComputeJobView
from .compute_safety import ComputeSafetyDecision, SafetySeverity
from .service_state import WorkerRegistryView


_TOKEN_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_WORKER_AVAILABILITY = frozenset({"ready", "busy", "offline", "draining", "faulted"})
_WORKER_HEALTH = frozenset({"healthy", "degraded", "unknown", "faulted"})
_ACTIVE_JOB_STATES = frozenset({"leased", "running"})


class ComputeLifecycleError(Exception):
    """Raised when lifecycle inputs cannot be reconciled safely."""


class LifecycleIntent(str, Enum):
    STEADY = "steady"
    WAKE = "wake"
    DRAIN = "drain"
    SHUTDOWN = "shutdown"
    SAFETY_RECONCILE = "safety_reconcile"


class WorkerPowerState(str, Enum):
    ON = "on"
    OFF = "off"
    STARTING = "starting"
    STOPPING = "stopping"
    UNKNOWN = "unknown"


class LifecycleJobActionKind(str, Enum):
    FINISH_OR_CHECKPOINT = "finish_or_checkpoint"
    STOP_REQUIRED = "stop_required"


@dataclass(frozen=True)
class LifecycleLocks:
    """Explicit operator/user lifecycle locks; none are inferred from host identity."""

    do_not_wake: bool = False
    do_not_shutdown: bool = False
    maintenance_lock: bool = False
    interactive_lock: bool = False

    def __post_init__(self) -> None:
        for field in (
            "do_not_wake",
            "do_not_shutdown",
            "maintenance_lock",
            "interactive_lock",
        ):
            if not isinstance(getattr(self, field), bool):
                raise ComputeLifecycleError(f"{field} must be boolean")


@dataclass(frozen=True)
class LifecycleJobAction:
    job_id: str
    action: LifecycleJobActionKind
    reason_code: str

    def __post_init__(self) -> None:
        _token(self.job_id, "job_id")
        if not isinstance(self.action, LifecycleJobActionKind):
            raise ComputeLifecycleError("action must be a LifecycleJobActionKind")
        _token(self.reason_code, "reason_code")


@dataclass(frozen=True)
class ComputeLifecycleDecision:
    worker_id: str
    intent: LifecycleIntent
    evaluated_at: str
    power_state: WorkerPowerState
    effective_interactive_lock: bool
    maintenance_lock: bool
    do_not_wake: bool
    do_not_shutdown: bool
    admit_new_work: bool
    request_drain: bool
    stop_workloads: bool
    fault_node: bool
    request_wake: bool
    request_safe_shutdown: bool
    requires_human_action: bool
    blocked_actions: tuple[str, ...]
    reason_codes: tuple[str, ...]
    job_actions: tuple[LifecycleJobAction, ...]

    def __post_init__(self) -> None:
        _token(self.worker_id, "worker_id")
        if not isinstance(self.intent, LifecycleIntent):
            raise ComputeLifecycleError("intent must be a LifecycleIntent")
        _utc(self.evaluated_at, "evaluated_at")
        if not isinstance(self.power_state, WorkerPowerState):
            raise ComputeLifecycleError("power_state must be a WorkerPowerState")
        for field in (
            "effective_interactive_lock",
            "maintenance_lock",
            "do_not_wake",
            "do_not_shutdown",
            "admit_new_work",
            "request_drain",
            "stop_workloads",
            "fault_node",
            "request_wake",
            "request_safe_shutdown",
            "requires_human_action",
        ):
            if not isinstance(getattr(self, field), bool):
                raise ComputeLifecycleError(f"{field} must be boolean")
        if tuple(sorted(set(self.blocked_actions))) != self.blocked_actions:
            raise ComputeLifecycleError("blocked_actions must be sorted and unique")
        if any(not isinstance(value, str) or not value for value in self.blocked_actions):
            raise ComputeLifecycleError("blocked_actions must contain non-empty strings")
        if tuple(sorted(set(self.reason_codes))) != self.reason_codes:
            raise ComputeLifecycleError("reason_codes must be sorted and unique")
        if any(not isinstance(value, str) or not value for value in self.reason_codes):
            raise ComputeLifecycleError("reason_codes must contain non-empty strings")
        if any(not isinstance(action, LifecycleJobAction) for action in self.job_actions):
            raise ComputeLifecycleError("job_actions must contain LifecycleJobAction values")
        if tuple(sorted(self.job_actions, key=lambda item: item.job_id)) != self.job_actions:
            raise ComputeLifecycleError("job_actions must be sorted by job_id")
        if len({action.job_id for action in self.job_actions}) != len(self.job_actions):
            raise ComputeLifecycleError("job_actions must have unique job IDs")
        if self.stop_workloads and not self.request_drain:
            raise ComputeLifecycleError("stop_workloads requires request_drain")
        if self.fault_node and not self.stop_workloads:
            raise ComputeLifecycleError("fault_node requires stop_workloads")
        if self.request_wake and self.power_state != WorkerPowerState.OFF:
            raise ComputeLifecycleError("wake request requires observed off power state")
        if self.request_safe_shutdown and self.power_state != WorkerPowerState.ON:
            raise ComputeLifecycleError("safe shutdown request requires observed on power state")
        if self.request_wake and self.request_safe_shutdown:
            raise ComputeLifecycleError("wake and shutdown cannot be requested together")
        if self.admit_new_work and (
            self.request_drain
            or self.stop_workloads
            or self.fault_node
            or self.request_wake
            or self.request_safe_shutdown
        ):
            raise ComputeLifecycleError(
                "admit_new_work cannot coexist with lifecycle transition requirements"
            )
        if self.requires_human_action and not self.blocked_actions:
            raise ComputeLifecycleError(
                "requires_human_action requires at least one blocked action"
            )


def plan_compute_lifecycle(
    worker: WorkerRegistryView,
    jobs: Iterable[ComputeJobView],
    *,
    intent: LifecycleIntent,
    power_state: WorkerPowerState,
    locks: LifecycleLocks,
    evaluated_at: str,
    safety: ComputeSafetyDecision | None = None,
) -> ComputeLifecycleDecision:
    """Reconcile lifecycle evidence into deterministic action requirements."""

    if not isinstance(worker, WorkerRegistryView):
        raise ComputeLifecycleError("worker must be a WorkerRegistryView")
    if not isinstance(intent, LifecycleIntent):
        raise ComputeLifecycleError("intent must be a LifecycleIntent")
    if not isinstance(power_state, WorkerPowerState):
        raise ComputeLifecycleError("power_state must be a WorkerPowerState")
    if not isinstance(locks, LifecycleLocks):
        raise ComputeLifecycleError("locks must be LifecycleLocks")
    evaluated_dt = _utc(evaluated_at, "evaluated_at")
    _validate_worker(worker)
    material = _materialize_jobs(jobs)
    assigned_active = tuple(
        job
        for job in material
        if job.state in _ACTIVE_JOB_STATES and job.lease_worker_id == worker.worker_id
    )

    if safety is not None:
        if not isinstance(safety, ComputeSafetyDecision):
            raise ComputeLifecycleError("safety must be a ComputeSafetyDecision or None")
        if _utc(safety.evaluated_at, "safety.evaluated_at") > evaluated_dt:
            raise ComputeLifecycleError("safety decision cannot be from the future")
    if intent == LifecycleIntent.SAFETY_RECONCILE and safety is None:
        raise ComputeLifecycleError("safety_reconcile requires a safety decision")

    effective_interactive = bool(worker.interactive_lock or locks.interactive_lock)
    admit_new_work = intent == LifecycleIntent.STEADY
    request_drain = False
    stop_workloads = False
    fault_node = False
    request_wake = False
    request_safe_shutdown = False
    requires_human_action = False
    blocked_actions: set[str] = set()
    reasons: set[str] = set()

    # Existing worker evidence remains authoritative and may itself block admission.
    if worker.availability == "offline":
        admit_new_work = False
        reasons.add("worker_offline")
    elif worker.availability == "draining":
        admit_new_work = False
        request_drain = True
        reasons.add("worker_already_draining")
    elif worker.availability == "faulted":
        admit_new_work = False
        request_drain = True
        stop_workloads = True
        fault_node = True
        reasons.add("worker_availability_faulted")

    if worker.health == "unknown":
        admit_new_work = False
        reasons.add("worker_health_unknown")
    elif worker.health == "faulted":
        admit_new_work = False
        request_drain = True
        stop_workloads = True
        fault_node = True
        reasons.add("worker_health_faulted")
    elif worker.health == "degraded":
        reasons.add("worker_health_degraded")

    # User/operator locks block admission and ordinary use. Safety stop/fault may override
    # interactive convenience but never erases an explicit do-not-shutdown lock.
    if locks.maintenance_lock:
        admit_new_work = False
        request_drain = True
        reasons.add("maintenance_lock_active")
    if effective_interactive:
        admit_new_work = False
        request_drain = True
        reasons.add("interactive_lock_active")

    if intent == LifecycleIntent.DRAIN:
        admit_new_work = False
        request_drain = True
        reasons.add("drain_requested")
    elif intent == LifecycleIntent.SHUTDOWN:
        admit_new_work = False
        request_drain = True
        reasons.add("shutdown_requested")
    elif intent == LifecycleIntent.WAKE:
        admit_new_work = False
        reasons.add("wake_requested")
    elif intent == LifecycleIntent.SAFETY_RECONCILE:
        admit_new_work = False
        reasons.add("safety_reconcile_requested")

    safety_shutdown_required = False
    if safety is not None:
        for code in safety.reason_codes:
            reasons.add(f"safety:{code}")
        reasons.add(f"safety_severity:{safety.aggregate_severity.value}")
        if not safety.response.admit_new_work:
            admit_new_work = False
        request_drain = bool(request_drain or safety.response.request_drain)
        stop_workloads = bool(stop_workloads or safety.response.stop_workloads)
        fault_node = bool(fault_node or safety.response.fault_node)
        safety_shutdown_required = safety.response.require_safe_shutdown

    if stop_workloads:
        request_drain = True
        admit_new_work = False
    if fault_node:
        stop_workloads = True
        request_drain = True
        admit_new_work = False

    # Wake is an eligibility request only. It never sends a packet.
    if intent == LifecycleIntent.WAKE:
        wake_blockers: list[str] = []
        if power_state != WorkerPowerState.OFF:
            wake_blockers.append("power_state_not_off")
        if locks.do_not_wake:
            wake_blockers.append("do_not_wake_lock")
        if locks.maintenance_lock:
            wake_blockers.append("maintenance_lock")
        if effective_interactive:
            wake_blockers.append("interactive_lock")
        if worker.health in {"unknown", "faulted"} or worker.availability == "faulted":
            wake_blockers.append("worker_fault_or_unknown")
        if safety is not None and (
            not safety.response.admit_new_work
            or safety.response.request_drain
            or safety.response.stop_workloads
            or safety.response.fault_node
        ):
            wake_blockers.append("safety_blocks_wake")
        if wake_blockers:
            blocked_actions.add("wake")
            reasons.update(f"wake_blocked:{reason}" for reason in wake_blockers)
            if any(
                reason in {"do_not_wake_lock", "maintenance_lock", "interactive_lock"}
                for reason in wake_blockers
            ):
                requires_human_action = True
        else:
            request_wake = True
            reasons.add("wake_eligible")

    shutdown_requested = intent == LifecycleIntent.SHUTDOWN or safety_shutdown_required
    if shutdown_requested:
        if safety_shutdown_required:
            reasons.add("safe_shutdown_required_by_safety")
        if locks.do_not_shutdown:
            blocked_actions.add("safe_shutdown")
            reasons.add(
                "safe_shutdown_required_but_locked"
                if safety_shutdown_required
                else "shutdown_blocked:do_not_shutdown_lock"
            )
            requires_human_action = True
        elif assigned_active:
            reasons.add(
                "shutdown_waiting_for_workload_stop"
                if stop_workloads
                else "shutdown_waiting_for_active_jobs"
            )
        elif power_state == WorkerPowerState.ON:
            request_safe_shutdown = True
            reasons.add("safe_shutdown_eligible")
        elif power_state == WorkerPowerState.OFF:
            reasons.add("shutdown_not_needed_already_off")
        elif power_state == WorkerPowerState.STOPPING:
            reasons.add("shutdown_already_in_progress")
        else:
            blocked_actions.add("safe_shutdown")
            reasons.add(f"shutdown_blocked:power_state_{power_state.value}")

    job_actions = _job_actions(
        assigned_active,
        stop_workloads=stop_workloads,
        request_drain=request_drain,
    )

    if admit_new_work:
        reasons.add("lifecycle_allows_new_work")
    elif not reasons:
        reasons.add("lifecycle_blocks_new_work")

    return ComputeLifecycleDecision(
        worker_id=worker.worker_id,
        intent=intent,
        evaluated_at=evaluated_at,
        power_state=power_state,
        effective_interactive_lock=effective_interactive,
        maintenance_lock=locks.maintenance_lock,
        do_not_wake=locks.do_not_wake,
        do_not_shutdown=locks.do_not_shutdown,
        admit_new_work=admit_new_work,
        request_drain=request_drain,
        stop_workloads=stop_workloads,
        fault_node=fault_node,
        request_wake=request_wake,
        request_safe_shutdown=request_safe_shutdown,
        requires_human_action=requires_human_action,
        blocked_actions=tuple(sorted(blocked_actions)),
        reason_codes=tuple(sorted(reasons)),
        job_actions=job_actions,
    )


def _job_actions(
    jobs: tuple[ComputeJobView, ...],
    *,
    stop_workloads: bool,
    request_drain: bool,
) -> tuple[LifecycleJobAction, ...]:
    if not jobs or (not stop_workloads and not request_drain):
        return ()
    action = (
        LifecycleJobActionKind.STOP_REQUIRED
        if stop_workloads
        else LifecycleJobActionKind.FINISH_OR_CHECKPOINT
    )
    reason = "safety_or_fault_stop_required" if stop_workloads else "lifecycle_drain_requested"
    return tuple(
        LifecycleJobAction(job_id=job.job_id, action=action, reason_code=reason)
        for job in sorted(jobs, key=lambda value: value.job_id)
    )


def _materialize_jobs(jobs: Iterable[ComputeJobView]) -> tuple[ComputeJobView, ...]:
    if isinstance(jobs, (str, bytes)):
        raise ComputeLifecycleError("jobs must be an iterable of ComputeJobView values")
    try:
        material = tuple(jobs)
    except TypeError as exc:
        raise ComputeLifecycleError(
            "jobs must be an iterable of ComputeJobView values"
        ) from exc
    if any(not isinstance(job, ComputeJobView) for job in material):
        raise ComputeLifecycleError("jobs must contain ComputeJobView values")
    seen: set[str] = set()
    for job in material:
        _token(job.job_id, "job_id")
        if job.job_id in seen:
            raise ComputeLifecycleError(f"duplicate compute job: {job.job_id}")
        seen.add(job.job_id)
        if job.state in _ACTIVE_JOB_STATES and job.lease_worker_id is None:
            raise ComputeLifecycleError(
                f"active compute job lacks lease worker: {job.job_id}"
            )
    return tuple(sorted(material, key=lambda value: value.job_id))


def _validate_worker(worker: WorkerRegistryView) -> None:
    _token(worker.worker_id, "worker_id")
    if worker.availability not in _WORKER_AVAILABILITY:
        raise ComputeLifecycleError("unsupported worker availability state")
    if worker.health not in _WORKER_HEALTH:
        raise ComputeLifecycleError("unsupported worker health state")
    if not isinstance(worker.interactive_lock, bool):
        raise ComputeLifecycleError("worker interactive_lock must be boolean")


def _token(value: object, field: str) -> str:
    if not isinstance(value, str) or not _TOKEN_RE.fullmatch(value):
        raise ComputeLifecycleError(f"{field} must be a bounded token")
    return value


def _utc(value: object, field: str) -> datetime:
    if not isinstance(value, str) or not value or value != value.strip():
        raise ComputeLifecycleError(f"{field} must be a UTC ISO-8601 timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ComputeLifecycleError(
            f"{field} must be a UTC ISO-8601 timestamp"
        ) from exc
    if parsed.tzinfo is None or parsed.utcoffset() != timezone.utc.utcoffset(parsed):
        raise ComputeLifecycleError(f"{field} must use UTC")
    return parsed.astimezone(timezone.utc)
