"""Durable compute-fabric dispatch for bounded MIRA Studio implementation.

This module composes existing authorities. It does not create a second scheduler,
worker registry, runtime router, model selector, worker executor, approval engine,
or source-activation path.

A review-ready Studio draft becomes one durable compute job bound to the exact
controller-owned WorkerManifest digest. Worker choice comes only from durable worker
registry state plus externally supplied provider-capability evidence through the
existing runtime router. The exact submitted job is leased to the exact selected
worker, started, admitted through the M2-M1-042 restricted-runtime gate, and then
completed/failed through the existing durable compute control plane.

No worker success grants merge, push, activation, publication, installation or
feature-share authority.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
import hashlib
import json
import re

from mira.command_sequencer import (
    ComputeJobControlPlane,
    ComputeJobView,
    QueueStateError,
)
from mira.runtime_router import (
    RouteRequest,
    RuntimeKind,
    RuntimeRouteResult,
    WorkerCandidateProjection,
    project_worker_candidate,
    route_runtime,
    worker_registry_view_to_advertisement,
)
from mira.service_state import (
    CapabilityGate,
    ProviderCapabilitySnapshot,
    WorkerRegistryService,
    WorkerRegistryView,
)
from mira.studio_intake import StudioIntakeDraft
from ops.studio_execution_bridge import (
    RestrictedStudioExecutionResult,
    StudioLocalExecutionPolicy,
    manifest_from_review_ready_intake,
    run_review_ready_intake_restricted,
)
from ops.studio_local_worker import StudioWorkerError, WorkerResult
from ops.studio_restricted_runtime import (
    RestrictedRuntimeError,
    RestrictedRuntimePolicy,
    RuntimeIsolationEvidence,
    StudioExecutionPermit,
    manifest_sha256,
)


_TOKEN_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class StudioComputeDispatchError(RuntimeError):
    """Malformed or contradictory trusted Studio dispatch configuration."""


class StudioDispatchOutcome(str, Enum):
    BLOCKED = "blocked"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    REPLAYED_SUCCESS = "replayed_success"


@dataclass(frozen=True)
class StudioComputeDispatchPolicy:
    """Controller-owned durable job/routing/lease policy for local Studio work."""

    operation_id: str
    service_id: str
    data_classification: str
    required_gates: tuple[CapabilityGate, ...]
    required_runtime_capabilities: tuple[str, ...]
    priority: int
    max_attempts: int
    lease_ttl_seconds: int
    max_provider_evidence_age_seconds: int
    max_worker_heartbeat_age_seconds: int

    def __post_init__(self) -> None:
        _token(self.operation_id, "operation_id")
        _token(self.service_id, "service_id")
        _token(self.data_classification, "data_classification")
        if not isinstance(self.required_gates, tuple) or not self.required_gates:
            raise StudioComputeDispatchError("required_gates must be a non-empty tuple")
        if any(not isinstance(gate, CapabilityGate) for gate in self.required_gates):
            raise StudioComputeDispatchError(
                "required_gates must contain CapabilityGate values"
            )
        normalized_gates = tuple(
            sorted(set(self.required_gates), key=lambda gate: gate.value)
        )
        if normalized_gates != self.required_gates:
            raise StudioComputeDispatchError(
                "required_gates must be sorted and unique"
            )
        _sorted_tokens(
            self.required_runtime_capabilities,
            "required_runtime_capabilities",
            allow_empty=False,
        )
        _rank(self.priority, "priority")
        if self.max_attempts != 1:
            raise StudioComputeDispatchError(
                "current Studio local execution requires max_attempts=1 because one "
                "failed worker run consumes its controller-owned Git branch"
            )
        _positive_int(self.lease_ttl_seconds, "lease_ttl_seconds", upper=86_400)
        _positive_int(
            self.max_provider_evidence_age_seconds,
            "max_provider_evidence_age_seconds",
            upper=86_400,
        )
        _positive_int(
            self.max_worker_heartbeat_age_seconds,
            "max_worker_heartbeat_age_seconds",
            upper=86_400,
        )


@dataclass(frozen=True)
class StudioWorkerDispatchStatus:
    """Secret-free projection status for one durable worker considered by dispatch."""

    worker_id: str
    projected: bool
    reason_codes: tuple[str, ...]

    def __post_init__(self) -> None:
        _token(self.worker_id, "worker_id")
        if not isinstance(self.projected, bool):
            raise StudioComputeDispatchError("projected must be boolean")
        _sorted_tokens(self.reason_codes, "reason_codes", allow_empty=True)


@dataclass(frozen=True)
class StudioComputeDispatchResult:
    """Secret-free durable dispatch/lifecycle outcome plus bounded worker evidence."""

    outcome: StudioDispatchOutcome
    reason: str
    job: ComputeJobView
    route: RuntimeRouteResult | None
    worker_statuses: tuple[StudioWorkerDispatchStatus, ...]
    selected_worker_id: str | None
    permit: StudioExecutionPermit | None
    worker_result: WorkerResult | None

    def __post_init__(self) -> None:
        if not isinstance(self.outcome, StudioDispatchOutcome):
            raise StudioComputeDispatchError("outcome must be StudioDispatchOutcome")
        _token(self.reason, "reason")
        if not isinstance(self.job, ComputeJobView):
            raise StudioComputeDispatchError("job must be ComputeJobView")
        if self.route is not None and not isinstance(self.route, RuntimeRouteResult):
            raise StudioComputeDispatchError("route must be RuntimeRouteResult or None")
        if not isinstance(self.worker_statuses, tuple) or any(
            not isinstance(item, StudioWorkerDispatchStatus)
            for item in self.worker_statuses
        ):
            raise StudioComputeDispatchError(
                "worker_statuses must contain StudioWorkerDispatchStatus values"
            )
        if self.selected_worker_id is not None:
            _token(self.selected_worker_id, "selected_worker_id")


def dispatch_review_ready_intake(
    draft: StudioIntakeDraft,
    execution_policy: StudioLocalExecutionPolicy,
    *,
    control_plane: ComputeJobControlPlane,
    worker_registry: WorkerRegistryService,
    provider_capabilities: Mapping[str, ProviderCapabilitySnapshot],
    isolation_evidence: Mapping[str, RuntimeIsolationEvidence],
    dispatch_policy: StudioComputeDispatchPolicy,
    runtime_policy: RestrictedRuntimePolicy,
    clock: Callable[[], str] | None = None,
) -> StudioComputeDispatchResult:
    """Route and execute one exact review-ready Studio job through durable compute.

    Expected blocking conditions return a bounded result without granting execution
    authority. Malformed/contradictory trusted controller configuration raises
    ``StudioComputeDispatchError``. Once a durable lease is started, execution or
    restricted-runtime failures are reconciled to the existing job control plane.
    """

    _validate_dependencies(
        draft=draft,
        execution_policy=execution_policy,
        control_plane=control_plane,
        worker_registry=worker_registry,
        provider_capabilities=provider_capabilities,
        isolation_evidence=isolation_evidence,
        dispatch_policy=dispatch_policy,
        runtime_policy=runtime_policy,
    )
    now_fn = _utc_now if clock is None else clock
    if not callable(now_fn):
        raise StudioComputeDispatchError("clock must be callable")

    manifest = manifest_from_review_ready_intake(draft, execution_policy)
    manifest_digest = manifest_sha256(manifest)
    required_capabilities = tuple(
        sorted(
            set(dispatch_policy.required_runtime_capabilities)
            | set(runtime_policy.required_worker_capabilities)
        )
    )
    job_material = {
        "draft_id": draft.draft_id,
        "manifest_sha256": manifest_digest,
        "operation_id": dispatch_policy.operation_id,
        "service_id": dispatch_policy.service_id,
        "data_classification": dispatch_policy.data_classification,
        "required_capabilities": list(required_capabilities),
        "priority": dispatch_policy.priority,
        "max_attempts": dispatch_policy.max_attempts,
    }
    job_material_sha = _object_sha256(job_material)
    job_id = "studio-job-" + job_material_sha[:48]
    submitted_at = _clock_read(now_fn, "submitted_at")
    job = _ensure_job(
        control_plane,
        job_id=job_id,
        operation_id=dispatch_policy.operation_id,
        service_id=dispatch_policy.service_id,
        data_classification=dispatch_policy.data_classification,
        required_capabilities=required_capabilities,
        input_artifact_id=draft.draft_id,
        input_sha256=manifest_digest,
        priority=dispatch_policy.priority,
        max_attempts=dispatch_policy.max_attempts,
        created_at=submitted_at,
        idempotency_key="studio-submit-" + job_material_sha[:48],
    )

    if job.state == "succeeded":
        return StudioComputeDispatchResult(
            outcome=StudioDispatchOutcome.REPLAYED_SUCCESS,
            reason="already_succeeded",
            job=job,
            route=None,
            worker_statuses=(),
            selected_worker_id=job.result_worker_id,
            permit=None,
            worker_result=None,
        )
    if job.state in {"failed", "cancelled"}:
        return StudioComputeDispatchResult(
            outcome=StudioDispatchOutcome.FAILED,
            reason="already_terminal",
            job=job,
            route=None,
            worker_statuses=(),
            selected_worker_id=job.result_worker_id,
            permit=None,
            worker_result=None,
        )
    if job.state in {"leased", "running", "paused"}:
        return StudioComputeDispatchResult(
            outcome=StudioDispatchOutcome.BLOCKED,
            reason="recovery_required",
            job=job,
            route=None,
            worker_statuses=(),
            selected_worker_id=job.lease_worker_id,
            permit=None,
            worker_result=None,
        )
    if job.state != "queued":
        raise StudioComputeDispatchError(
            f"unsupported durable Studio job state: {job.state}"
        )

    workers = worker_registry.list_workers()
    candidates = []
    statuses: list[StudioWorkerDispatchStatus] = []
    candidate_workers: dict[tuple[str, str], WorkerRegistryView] = {}
    seen_lanes: set[str] = set()

    for worker in workers:
        if worker.runtime_kind != RuntimeKind.LOCAL.value:
            statuses.append(
                StudioWorkerDispatchStatus(
                    worker_id=worker.worker_id,
                    projected=False,
                    reason_codes=("runtime_kind_not_local",),
                )
            )
            continue
        capability = provider_capabilities.get(worker.worker_id)
        if capability is None:
            statuses.append(
                StudioWorkerDispatchStatus(
                    worker_id=worker.worker_id,
                    projected=False,
                    reason_codes=("provider_capability_missing",),
                )
            )
            continue
        if not isinstance(capability, ProviderCapabilitySnapshot):
            raise StudioComputeDispatchError(
                f"provider capability for {worker.worker_id} is malformed"
            )
        try:
            projection = project_worker_candidate(
                worker_registry_view_to_advertisement(worker),
                capability,
                now=submitted_at,
                max_heartbeat_age_seconds=(
                    dispatch_policy.max_worker_heartbeat_age_seconds
                ),
            )
        except Exception as exc:
            raise StudioComputeDispatchError(
                f"worker projection failed closed for {worker.worker_id}"
            ) from exc
        statuses.append(_worker_status(projection))
        if projection.candidate is None:
            continue
        candidate = projection.candidate
        if candidate.lane_id in seen_lanes:
            return StudioComputeDispatchResult(
                outcome=StudioDispatchOutcome.BLOCKED,
                reason="ambiguous_worker_lane",
                job=job,
                route=None,
                worker_statuses=tuple(sorted(statuses, key=lambda item: item.worker_id)),
                selected_worker_id=None,
                permit=None,
                worker_result=None,
            )
        seen_lanes.add(candidate.lane_id)
        key = (candidate.lane_id, candidate.runtime_id)
        if key in candidate_workers:
            return StudioComputeDispatchResult(
                outcome=StudioDispatchOutcome.BLOCKED,
                reason="ambiguous_worker_runtime",
                job=job,
                route=None,
                worker_statuses=tuple(sorted(statuses, key=lambda item: item.worker_id)),
                selected_worker_id=None,
                permit=None,
                worker_result=None,
            )
        candidate_workers[key] = worker
        candidates.append(candidate)

    route = route_runtime(
        RouteRequest(
            operation_id=dispatch_policy.operation_id,
            service_id=dispatch_policy.service_id,
            required_gates=dispatch_policy.required_gates,
            data_classification=dispatch_policy.data_classification,
            required_runtime_capabilities=required_capabilities,
        ),
        tuple(candidates),
        now=submitted_at,
        max_age_seconds=dispatch_policy.max_provider_evidence_age_seconds,
    )
    normalized_statuses = tuple(sorted(statuses, key=lambda item: item.worker_id))
    if not route.selected:
        return StudioComputeDispatchResult(
            outcome=StudioDispatchOutcome.BLOCKED,
            reason=route.reason.value,
            job=job,
            route=route,
            worker_statuses=normalized_statuses,
            selected_worker_id=None,
            permit=None,
            worker_result=None,
        )

    selected_key = (route.selected_lane_id, route.selected_runtime_id)
    selected_worker = candidate_workers.get(selected_key)
    if selected_worker is None:
        return StudioComputeDispatchResult(
            outcome=StudioDispatchOutcome.BLOCKED,
            reason="selected_worker_missing",
            job=job,
            route=route,
            worker_statuses=normalized_statuses,
            selected_worker_id=None,
            permit=None,
            worker_result=None,
        )

    isolation = isolation_evidence.get(selected_worker.worker_id)
    if isolation is None:
        return StudioComputeDispatchResult(
            outcome=StudioDispatchOutcome.BLOCKED,
            reason="isolation_evidence_missing",
            job=job,
            route=route,
            worker_statuses=normalized_statuses,
            selected_worker_id=selected_worker.worker_id,
            permit=None,
            worker_result=None,
        )
    if not isinstance(isolation, RuntimeIsolationEvidence):
        raise StudioComputeDispatchError("selected isolation evidence is malformed")
    if (
        isolation.worker_id != selected_worker.worker_id
        or isolation.principal_id != selected_worker.principal_id
        or isolation.runtime_id != selected_worker.runtime_id
    ):
        return StudioComputeDispatchResult(
            outcome=StudioDispatchOutcome.BLOCKED,
            reason="isolation_identity_mismatch",
            job=job,
            route=route,
            worker_statuses=normalized_statuses,
            selected_worker_id=selected_worker.worker_id,
            permit=None,
            worker_result=None,
        )

    lease_started_at = submitted_at
    lease_expires_at = _add_seconds(
        lease_started_at, dispatch_policy.lease_ttl_seconds
    )
    attempt_number = job.attempts + 1
    lease_material = _object_sha256(
        {
            "job_id": job.job_id,
            "worker_id": selected_worker.worker_id,
            "attempt": attempt_number,
            "manifest_sha256": manifest_digest,
        }
    )
    lease_id = "studio-lease-" + lease_material[:48]
    leased = control_plane.lease_job(
        job.job_id,
        worker_id=selected_worker.worker_id,
        worker_capabilities=selected_worker.runtime_capabilities,
        lease_id=lease_id,
        leased_at=lease_started_at,
        lease_expires_at=lease_expires_at,
        idempotency_key="studio-lease-key-" + lease_material[:40],
    )
    if leased.input_artifact_id != draft.draft_id or leased.input_sha256 != manifest_digest:
        raise StudioComputeDispatchError(
            "durable compute job input no longer matches the exact Studio manifest"
        )

    running = control_plane.start(
        leased.job_id,
        worker_id=selected_worker.worker_id,
        lease_id=lease_id,
        started_at=lease_started_at,
        idempotency_key="studio-start-" + lease_material[:48],
    )

    restricted_result: RestrictedStudioExecutionResult
    try:
        restricted_result = run_review_ready_intake_restricted(
            draft,
            execution_policy,
            job=running,
            worker=selected_worker,
            isolation=isolation,
            runtime_policy=runtime_policy,
            now=lease_started_at,
        )
    except RestrictedRuntimeError:
        failed_at = _clock_read(now_fn, "failed_at")
        failed = _fail_started_job(
            control_plane,
            running,
            worker=selected_worker,
            lease_id=lease_id,
            failed_at=failed_at,
            error_code="restricted_runtime_blocked",
        )
        return StudioComputeDispatchResult(
            outcome=StudioDispatchOutcome.FAILED,
            reason="restricted_runtime_blocked",
            job=failed,
            route=route,
            worker_statuses=normalized_statuses,
            selected_worker_id=selected_worker.worker_id,
            permit=None,
            worker_result=None,
        )
    except (StudioWorkerError, Exception):
        failed_at = _clock_read(now_fn, "failed_at")
        failed = _fail_started_job(
            control_plane,
            running,
            worker=selected_worker,
            lease_id=lease_id,
            failed_at=failed_at,
            error_code="studio_execution_error",
        )
        return StudioComputeDispatchResult(
            outcome=StudioDispatchOutcome.FAILED,
            reason="studio_execution_error",
            job=failed,
            route=route,
            worker_statuses=normalized_statuses,
            selected_worker_id=selected_worker.worker_id,
            permit=None,
            worker_result=None,
        )

    worker_result = restricted_result.worker_result
    if worker_result.status != "ready_for_review" or worker_result.final_candidate_sha is None:
        failed_at = _clock_read(now_fn, "failed_at")
        error_code = _worker_failure_code(worker_result)
        failed = _fail_started_job(
            control_plane,
            running,
            worker=selected_worker,
            lease_id=lease_id,
            failed_at=failed_at,
            error_code=error_code,
        )
        return StudioComputeDispatchResult(
            outcome=StudioDispatchOutcome.FAILED,
            reason=error_code,
            job=failed,
            route=route,
            worker_statuses=normalized_statuses,
            selected_worker_id=selected_worker.worker_id,
            permit=restricted_result.permit,
            worker_result=worker_result,
        )

    result_sha = _object_sha256(worker_result.as_dict())
    completed_at = _clock_read(now_fn, "completed_at")
    try:
        completed = control_plane.complete(
            running.job_id,
            worker_id=selected_worker.worker_id,
            lease_id=lease_id,
            runtime_id=selected_worker.runtime_id,
            result_artifact_id="studio-result-" + result_sha[:48],
            result_sha256=result_sha,
            completed_at=completed_at,
            idempotency_key="studio-complete-" + result_sha[:48],
        )
    except QueueStateError as exc:
        raise StudioComputeDispatchError(
            "Studio worker succeeded but durable completion could not be reconciled"
        ) from exc

    return StudioComputeDispatchResult(
        outcome=StudioDispatchOutcome.SUCCEEDED,
        reason="ready_for_review",
        job=completed,
        route=route,
        worker_statuses=normalized_statuses,
        selected_worker_id=selected_worker.worker_id,
        permit=restricted_result.permit,
        worker_result=worker_result,
    )


def _ensure_job(
    control_plane: ComputeJobControlPlane,
    *,
    job_id: str,
    operation_id: str,
    service_id: str,
    data_classification: str,
    required_capabilities: tuple[str, ...],
    input_artifact_id: str,
    input_sha256: str,
    priority: int,
    max_attempts: int,
    created_at: str,
    idempotency_key: str,
) -> ComputeJobView:
    expected = {
        job.job_id: job for job in control_plane.list_jobs()
    }.get(job_id)
    if expected is None:
        return control_plane.submit(
            job_id,
            operation_id=operation_id,
            service_id=service_id,
            data_classification=data_classification,
            required_capabilities=required_capabilities,
            input_artifact_id=input_artifact_id,
            input_sha256=input_sha256,
            priority=priority,
            max_attempts=max_attempts,
            created_at=created_at,
            idempotency_key=idempotency_key,
        )
    identity = (
        expected.operation_id,
        expected.service_id,
        expected.data_classification,
        expected.required_capabilities,
        expected.input_artifact_id,
        expected.input_sha256,
        expected.priority,
        expected.max_attempts,
    )
    wanted = (
        operation_id,
        service_id,
        data_classification,
        required_capabilities,
        input_artifact_id,
        input_sha256,
        priority,
        max_attempts,
    )
    if identity != wanted:
        raise StudioComputeDispatchError(
            "durable Studio job identity collides with different dispatch material"
        )
    return expected


def _worker_status(projection: WorkerCandidateProjection) -> StudioWorkerDispatchStatus:
    reasons = projection.reason_codes
    if projection.candidate is None and not reasons:
        reasons = ("worker_projection_unavailable",)
    return StudioWorkerDispatchStatus(
        worker_id=projection.worker_id,
        projected=projection.candidate is not None,
        reason_codes=tuple(sorted(set(reasons))),
    )


def _fail_started_job(
    control_plane: ComputeJobControlPlane,
    running: ComputeJobView,
    *,
    worker: WorkerRegistryView,
    lease_id: str,
    failed_at: str,
    error_code: str,
) -> ComputeJobView:
    try:
        return control_plane.fail(
            running.job_id,
            worker_id=worker.worker_id,
            lease_id=lease_id,
            error_code=error_code,
            failed_at=failed_at,
            retryable=False,
            idempotency_key=(
                "studio-fail-"
                + _object_sha256(
                    {
                        "job_id": running.job_id,
                        "attempt": running.attempts,
                        "error_code": error_code,
                    }
                )[:48]
            ),
        )
    except QueueStateError as exc:
        raise StudioComputeDispatchError(
            "Studio execution failed but durable failure could not be reconciled"
        ) from exc


def _worker_failure_code(result: WorkerResult) -> str:
    reason = result.stop_reason.replace("-", "_")
    candidate = "studio_" + reason
    if not _TOKEN_RE.fullmatch(candidate):
        return "studio_worker_blocked"
    return candidate


def _validate_dependencies(
    *,
    draft: StudioIntakeDraft,
    execution_policy: StudioLocalExecutionPolicy,
    control_plane: ComputeJobControlPlane,
    worker_registry: WorkerRegistryService,
    provider_capabilities: Mapping[str, ProviderCapabilitySnapshot],
    isolation_evidence: Mapping[str, RuntimeIsolationEvidence],
    dispatch_policy: StudioComputeDispatchPolicy,
    runtime_policy: RestrictedRuntimePolicy,
) -> None:
    if not isinstance(draft, StudioIntakeDraft):
        raise StudioComputeDispatchError("draft must be StudioIntakeDraft")
    if not isinstance(execution_policy, StudioLocalExecutionPolicy):
        raise StudioComputeDispatchError(
            "execution_policy must be StudioLocalExecutionPolicy"
        )
    if not isinstance(control_plane, ComputeJobControlPlane):
        raise StudioComputeDispatchError(
            "control_plane must be ComputeJobControlPlane"
        )
    if not isinstance(worker_registry, WorkerRegistryService):
        raise StudioComputeDispatchError(
            "worker_registry must be WorkerRegistryService"
        )
    if not isinstance(provider_capabilities, Mapping):
        raise StudioComputeDispatchError("provider_capabilities must be a mapping")
    if not isinstance(isolation_evidence, Mapping):
        raise StudioComputeDispatchError("isolation_evidence must be a mapping")
    if not isinstance(dispatch_policy, StudioComputeDispatchPolicy):
        raise StudioComputeDispatchError(
            "dispatch_policy must be StudioComputeDispatchPolicy"
        )
    if not isinstance(runtime_policy, RestrictedRuntimePolicy):
        raise StudioComputeDispatchError(
            "runtime_policy must be RestrictedRuntimePolicy"
        )
    if runtime_policy.required_operation_id != dispatch_policy.operation_id:
        raise StudioComputeDispatchError(
            "restricted-runtime operation does not match dispatch operation"
        )
    if runtime_policy.required_service_id != dispatch_policy.service_id:
        raise StudioComputeDispatchError(
            "restricted-runtime service does not match dispatch service"
        )
    if not runtime_policy.bind_job_input_to_draft:
        raise StudioComputeDispatchError(
            "Studio dispatch requires restricted runtime to bind job input to draft"
        )
    if runtime_policy.permit_ttl_seconds > dispatch_policy.lease_ttl_seconds:
        raise StudioComputeDispatchError(
            "restricted-runtime permit TTL cannot exceed compute lease TTL"
        )
    minimum_lease = (
        execution_policy.wall_timeout_seconds
        + execution_policy.model_timeout_seconds
        + execution_policy.test_timeout_seconds
        + 60
    )
    if dispatch_policy.lease_ttl_seconds < minimum_lease:
        raise StudioComputeDispatchError(
            "compute lease TTL must cover the bounded Studio worker execution budget"
        )


def _object_sha256(value: object) -> str:
    try:
        payload = json.dumps(
            value,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise StudioComputeDispatchError(
            "dispatch evidence must be canonical JSON data"
        ) from exc
    return hashlib.sha256(payload).hexdigest()


def _clock_read(clock: Callable[[], str], field: str) -> str:
    value = clock()
    parsed = _utc(value, field)
    return parsed.isoformat().replace("+00:00", "Z")


def _add_seconds(value: str, seconds: int) -> str:
    return (
        _utc(value, "lease_started_at") + timedelta(seconds=seconds)
    ).isoformat().replace("+00:00", "Z")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _utc(value: object, field: str) -> datetime:
    if not isinstance(value, str) or not value or value != value.strip():
        raise StudioComputeDispatchError(f"{field} must be a UTC ISO-8601 timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise StudioComputeDispatchError(
            f"{field} must be a UTC ISO-8601 timestamp"
        ) from exc
    if parsed.tzinfo is None or parsed.utcoffset() != timedelta(0):
        raise StudioComputeDispatchError(f"{field} must use UTC")
    return parsed.astimezone(timezone.utc)


def _token(value: object, field: str) -> str:
    if not isinstance(value, str) or not _TOKEN_RE.fullmatch(value):
        raise StudioComputeDispatchError(f"{field} must be a bounded token")
    return value


def _sorted_tokens(
    values: object,
    field: str,
    *,
    allow_empty: bool,
) -> tuple[str, ...]:
    if not isinstance(values, tuple):
        raise StudioComputeDispatchError(f"{field} must be a tuple")
    normalized = tuple(sorted({_token(value, field) for value in values}))
    if normalized != values or (not allow_empty and not normalized):
        raise StudioComputeDispatchError(
            f"{field} must be sorted, unique" + ("" if allow_empty else ", and non-empty")
        )
    return normalized


def _rank(value: object, field: str) -> int:
    if (
        not isinstance(value, int)
        or isinstance(value, bool)
        or value < 0
        or value > 1_000_000
    ):
        raise StudioComputeDispatchError(
            f"{field} must be an integer from 0 through 1000000"
        )
    return value


def _positive_int(value: object, field: str, *, upper: int) -> int:
    if (
        not isinstance(value, int)
        or isinstance(value, bool)
        or value < 1
        or value > upper
    ):
        raise StudioComputeDispatchError(
            f"{field} must be an integer from 1 through {upper}"
        )
    return value


__all__ = [
    "StudioComputeDispatchError",
    "StudioComputeDispatchPolicy",
    "StudioComputeDispatchResult",
    "StudioDispatchOutcome",
    "StudioWorkerDispatchStatus",
    "dispatch_review_ready_intake",
]
