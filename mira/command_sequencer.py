"""Serialized API commands plus durable provider-neutral compute-job control."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, replace
from datetime import datetime, timezone
import hashlib
import json
import re
from threading import RLock
from typing import Any, Callable, Iterable

from .api_core import (
    ApiAuthorityError,
    ApiReadbackError,
    ApiService,
    ApiServiceError,
    AuthenticatedPrincipal,
    CommandEnvelope,
    CommandResult,
)
from .structured_state import NotFoundError, ResourceRecord, StructuredStateAdapter


_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_PENDING = "pending"
_SUCCEEDED = "succeeded"
_FAILED = "failed"

COMPUTE_JOB_RESOURCE_TYPE = "compute_job"
COMPUTE_JOB_SCHEMA_VERSION = 1
COMPUTE_JOB_STATES = frozenset(
    {"queued", "leased", "running", "paused", "succeeded", "failed", "cancelled"}
)
COMPUTE_JOB_TERMINAL_STATES = frozenset({"succeeded", "failed", "cancelled"})


class CommandSequencerError(Exception):
    """Base command-sequencer/control-plane error."""


class DuplicateQueuedCommandError(CommandSequencerError):
    """Raised when a command ID is already queued."""


class QueueStateError(CommandSequencerError):
    """Raised for invalid queue/control-plane state."""


@dataclass(frozen=True)
class QueuedCommand:
    envelope: CommandEnvelope
    status: str = _PENDING
    attempts: int = 0
    result: CommandResult | None = None
    error_code: str | None = None
    error_message: str | None = None

    @property
    def command_id(self) -> str:
        return self.envelope.command_id


@dataclass(frozen=True)
class SequencerOutcome:
    command_id: str
    status: str
    result: CommandResult | None = None
    error_code: str | None = None
    error_message: str | None = None


class InMemoryCommandQueue:
    """Deterministic synthetic API-command queue."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._order: list[str] = []
        self._entries: dict[str, QueuedCommand] = {}

    def submit(self, envelope: CommandEnvelope) -> QueuedCommand:
        if not isinstance(envelope, CommandEnvelope):
            raise CommandSequencerError("envelope must be a CommandEnvelope")
        command_id = _command_id(envelope.command_id)
        with self._lock:
            if command_id in self._entries:
                raise DuplicateQueuedCommandError(
                    f"command_id is already queued: {command_id}"
                )
            entry = QueuedCommand(envelope=deepcopy(envelope))
            self._entries[command_id] = entry
            self._order.append(command_id)
            return deepcopy(entry)

    def next_pending(self) -> QueuedCommand | None:
        with self._lock:
            for command_id in self._order:
                entry = self._entries[command_id]
                if entry.status == _PENDING:
                    return deepcopy(entry)
        return None

    def record_attempt(self, command_id: str) -> QueuedCommand:
        command_id = _command_id(command_id)
        with self._lock:
            entry = self._required(command_id)
            if entry.status != _PENDING:
                raise QueueStateError(
                    f"cannot attempt command in state {entry.status}: {command_id}"
                )
            updated = replace(entry, attempts=entry.attempts + 1)
            self._entries[command_id] = updated
            return deepcopy(updated)

    def succeed(self, command_id: str, result: CommandResult) -> QueuedCommand:
        command_id = _command_id(command_id)
        if not isinstance(result, CommandResult):
            raise CommandSequencerError("result must be a CommandResult")
        with self._lock:
            entry = self._required(command_id)
            if entry.status != _PENDING:
                raise QueueStateError(
                    f"cannot succeed command in state {entry.status}: {command_id}"
                )
            if result.command_id != command_id:
                raise QueueStateError("command result identity does not match queued command")
            updated = replace(
                entry,
                status=_SUCCEEDED,
                result=deepcopy(result),
                error_code=None,
                error_message=None,
            )
            self._entries[command_id] = updated
            return deepcopy(updated)

    def fail(self, command_id: str, error: ApiServiceError) -> QueuedCommand:
        command_id = _command_id(command_id)
        if not isinstance(error, ApiServiceError):
            raise CommandSequencerError("error must be an ApiServiceError")
        with self._lock:
            entry = self._required(command_id)
            if entry.status != _PENDING:
                raise QueueStateError(
                    f"cannot fail command in state {entry.status}: {command_id}"
                )
            updated = replace(
                entry,
                status=_FAILED,
                result=None,
                error_code=error.code,
                error_message=error.message,
            )
            self._entries[command_id] = updated
            return deepcopy(updated)

    def get(self, command_id: str) -> QueuedCommand:
        command_id = _command_id(command_id)
        with self._lock:
            return deepcopy(self._required(command_id))

    def entries(self) -> tuple[QueuedCommand, ...]:
        with self._lock:
            return tuple(deepcopy(self._entries[item]) for item in self._order)

    def _required(self, command_id: str) -> QueuedCommand:
        try:
            return self._entries[command_id]
        except KeyError as exc:
            raise QueueStateError(f"unknown command_id: {command_id}") from exc


class SerializedCommandWorker:
    """Execute at most one queued API command under one critical section."""

    def __init__(
        self,
        service: ApiService,
        principal: AuthenticatedPrincipal,
        queue: InMemoryCommandQueue,
        *,
        after_execute: Callable[[QueuedCommand, CommandResult], None] | None = None,
    ) -> None:
        if not isinstance(service, ApiService):
            raise CommandSequencerError("service must be an ApiService")
        if not isinstance(principal, AuthenticatedPrincipal):
            raise CommandSequencerError("principal must be an AuthenticatedPrincipal")
        if not isinstance(queue, InMemoryCommandQueue):
            raise CommandSequencerError("queue must be an InMemoryCommandQueue")
        if after_execute is not None and not callable(after_execute):
            raise CommandSequencerError("after_execute must be callable or None")
        self._service = service
        self._principal = deepcopy(principal)
        self._queue = queue
        self._after_execute = after_execute
        self._lock = RLock()

    def process_next(self) -> SequencerOutcome | None:
        with self._lock:
            entry = self._queue.next_pending()
            if entry is None:
                return None
            entry = self._queue.record_attempt(entry.command_id)
            try:
                result = self._service.execute_command(
                    self._principal,
                    deepcopy(entry.envelope),
                )
            except (ApiAuthorityError, ApiReadbackError):
                raise
            except ApiServiceError as exc:
                failed = self._queue.fail(entry.command_id, exc)
                return SequencerOutcome(
                    command_id=failed.command_id,
                    status=failed.status,
                    error_code=failed.error_code,
                    error_message=failed.error_message,
                )
            if self._after_execute is not None:
                self._after_execute(deepcopy(entry), deepcopy(result))
            succeeded = self._queue.succeed(entry.command_id, result)
            return SequencerOutcome(
                command_id=succeeded.command_id,
                status=succeeded.status,
                result=deepcopy(succeeded.result),
            )

    def process_all(self, *, limit: int = 100) -> tuple[SequencerOutcome, ...]:
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 1000:
            raise CommandSequencerError("limit must be an integer from 1 through 1000")
        outcomes: list[SequencerOutcome] = []
        for _ in range(limit):
            outcome = self.process_next()
            if outcome is None:
                break
            outcomes.append(outcome)
        return tuple(outcomes)


@dataclass(frozen=True)
class ComputeJobView:
    job_id: str
    revision: int
    operation_id: str
    service_id: str
    data_classification: str
    required_capabilities: tuple[str, ...]
    input_artifact_id: str
    input_sha256: str
    priority: int
    max_attempts: int
    state: str
    attempts: int
    created_at: str
    cancel_requested: bool
    lease_worker_id: str | None
    lease_id: str | None
    leased_at: str | None
    lease_expires_at: str | None
    started_at: str | None
    checkpoint_artifact_id: str | None
    checkpoint_sha256: str | None
    error_code: str | None
    result_artifact_id: str | None
    result_sha256: str | None
    result_worker_id: str | None
    result_runtime_id: str | None
    result_attempt: int | None
    finished_at: str | None
    last_transition_key_sha256: str | None
    last_transition_material_sha256: str | None
    idempotent_replay: bool = False

    @property
    def active_lease(self) -> bool:
        return self.state in {"leased", "running"}

    def queue_sort_key(self) -> tuple[int, str, str]:
        return (self.priority, self.created_at, self.job_id)


class ComputeJobControlPlane:
    """STORE-001-backed compute-job lifecycle; it never executes the job itself."""

    def __init__(self, adapter: StructuredStateAdapter) -> None:
        self._adapter = adapter

    def submit(
        self,
        job_id: str,
        *,
        operation_id: str,
        service_id: str,
        data_classification: str,
        required_capabilities: Iterable[str],
        input_artifact_id: str,
        input_sha256: str,
        priority: int,
        max_attempts: int,
        created_at: str,
        idempotency_key: str,
    ) -> ComputeJobView:
        job = _token(job_id, "job_id")
        operation = _token(operation_id, "operation_id")
        service = _token(service_id, "service_id")
        classification = _token(data_classification, "data_classification")
        caps = _tokens(required_capabilities, "required_capabilities", allow_empty=False)
        input_id = _token(input_artifact_id, "input_artifact_id")
        input_hash = _sha256(input_sha256, "input_sha256")
        normalized_priority = _rank(priority, "priority")
        attempts_limit = _positive(max_attempts, "max_attempts")
        created = _utc_text(created_at, "created_at")
        key = _token(idempotency_key, "idempotency_key")
        material = {
            "operation": "submit",
            "job_id": job,
            "operation_id": operation,
            "service_id": service,
            "data_classification": classification,
            "required_capabilities": list(caps),
            "input_artifact_id": input_id,
            "input_sha256": input_hash,
            "priority": normalized_priority,
            "max_attempts": attempts_limit,
            "created_at": created,
        }
        key_hash, material_hash = _transition_receipt(key, material)
        payload = _job_payload(
            job_id=job,
            operation_id=operation,
            service_id=service,
            data_classification=classification,
            required_capabilities=list(caps),
            input_artifact_id=input_id,
            input_sha256=input_hash,
            priority=normalized_priority,
            max_attempts=attempts_limit,
            state="queued",
            attempts=0,
            created_at=created,
            last_transition_key_sha256=key_hash,
            last_transition_material_sha256=material_hash,
        )
        result = self._adapter.upsert(
            COMPUTE_JOB_RESOURCE_TYPE,
            payload["job_id"],
            payload,
            idempotency_key=key,
            expected_revision=0,
        )
        return _job_view(result.record, idempotent_replay=result.idempotent_replay)

    def get(self, job_id: str) -> ComputeJobView:
        try:
            return _job_view(
                self._adapter.get(COMPUTE_JOB_RESOURCE_TYPE, _token(job_id, "job_id"))
            )
        except NotFoundError as exc:
            raise QueueStateError(f"unknown compute job: {job_id}") from exc

    def list_jobs(self, *, limit: int = 1000) -> tuple[ComputeJobView, ...]:
        jobs = [
            _job_view(record)
            for record in self._adapter.query(COMPUTE_JOB_RESOURCE_TYPE, limit=limit)
        ]
        jobs.sort(key=lambda job: job.job_id)
        return tuple(jobs)

    def lease_next(
        self,
        *,
        worker_id: str,
        worker_capabilities: Iterable[str],
        lease_id: str,
        leased_at: str,
        lease_expires_at: str,
        idempotency_key: str,
    ) -> ComputeJobView | None:
        worker = _token(worker_id, "worker_id")
        caps_tuple = _tokens(worker_capabilities, "worker_capabilities", allow_empty=False)
        caps = set(caps_tuple)
        lease = _token(lease_id, "lease_id")
        leased = _utc_text(leased_at, "leased_at")
        expires = _utc_text(lease_expires_at, "lease_expires_at")
        if _utc(expires, "lease_expires_at") <= _utc(leased, "leased_at"):
            raise QueueStateError("lease_expires_at must be after leased_at")
        key = _token(idempotency_key, "idempotency_key")
        material = {
            "operation": "lease_next",
            "worker_id": worker,
            "worker_capabilities": list(caps_tuple),
            "lease_id": lease,
            "leased_at": leased,
            "lease_expires_at": expires,
        }
        jobs = self.list_jobs()
        replay = self._find_transition_replay(jobs, key, material)
        if replay is not None:
            return replay
        for candidate in jobs:
            if candidate.lease_id == lease and candidate.active_lease:
                raise QueueStateError("lease_id is already active with different material")
        eligible = [
            candidate
            for candidate in jobs
            if candidate.state == "queued"
            and not candidate.cancel_requested
            and candidate.attempts < candidate.max_attempts
            and set(candidate.required_capabilities).issubset(caps)
        ]
        if not eligible:
            return None
        selected = min(eligible, key=ComputeJobView.queue_sort_key)
        return self._mutate(
            selected.job_id,
            key,
            material,
            state="leased",
            attempts=selected.attempts + 1,
            lease_worker_id=worker,
            lease_id=lease,
            leased_at=leased,
            lease_expires_at=expires,
            started_at=None,
            error_code=None,
            finished_at=None,
        )

    def lease_job(
        self,
        job_id: str,
        *,
        worker_id: str,
        worker_capabilities: Iterable[str],
        lease_id: str,
        leased_at: str,
        lease_expires_at: str,
        idempotency_key: str,
    ) -> ComputeJobView:
        """Lease one exact queued job to one exact worker.

        Unlike :meth:`lease_next`, this method never selects a different queued job.
        It exists for controller-routed work where another trusted component has
        already selected the worker for this specific durable job.
        """

        current = self.get(job_id)
        worker = _token(worker_id, "worker_id")
        caps_tuple = _tokens(worker_capabilities, "worker_capabilities", allow_empty=False)
        caps = set(caps_tuple)
        lease = _token(lease_id, "lease_id")
        leased = _utc_text(leased_at, "leased_at")
        expires = _utc_text(lease_expires_at, "lease_expires_at")
        if _utc(expires, "lease_expires_at") <= _utc(leased, "leased_at"):
            raise QueueStateError("lease_expires_at must be after leased_at")
        key = _token(idempotency_key, "idempotency_key")
        material = {
            "operation": "lease_job",
            "job_id": current.job_id,
            "worker_id": worker,
            "worker_capabilities": list(caps_tuple),
            "lease_id": lease,
            "leased_at": leased,
            "lease_expires_at": expires,
        }
        replay = _transition_replay(current, key, material)
        if replay is not None:
            return replay
        if current.state != "queued":
            raise QueueStateError(
                f"cannot lease exact compute job in state {current.state}"
            )
        if current.cancel_requested:
            raise QueueStateError("cancel-requested compute job cannot be leased")
        if current.attempts >= current.max_attempts:
            raise QueueStateError("compute job attempt budget is exhausted")
        if not set(current.required_capabilities).issubset(caps):
            raise QueueStateError("worker lacks required compute-job capabilities")
        for candidate in self.list_jobs():
            if (
                candidate.job_id != current.job_id
                and candidate.lease_id == lease
                and candidate.active_lease
            ):
                raise QueueStateError("lease_id is already active with different material")
        return self._mutate(
            current.job_id,
            key,
            material,
            state="leased",
            attempts=current.attempts + 1,
            lease_worker_id=worker,
            lease_id=lease,
            leased_at=leased,
            lease_expires_at=expires,
            started_at=None,
            error_code=None,
            finished_at=None,
        )

    def start(
        self,
        job_id: str,
        *,
        worker_id: str,
        lease_id: str,
        started_at: str,
        idempotency_key: str,
    ) -> ComputeJobView:
        current = self.get(job_id)
        worker = _token(worker_id, "worker_id")
        lease = _token(lease_id, "lease_id")
        started = _utc_text(started_at, "started_at")
        key = _token(idempotency_key, "idempotency_key")
        material = {
            "operation": "start",
            "job_id": current.job_id,
            "worker_id": worker,
            "lease_id": lease,
            "started_at": started,
        }
        replay = _transition_replay(current, key, material)
        if replay is not None:
            return replay
        _lease(current, worker, lease)
        if current.state != "leased":
            raise QueueStateError(f"cannot start compute job in state {current.state}")
        _within_lease(current, started, "started_at")
        return self._mutate(
            current.job_id, key, material, state="running", started_at=started
        )

    def request_cancel(
        self,
        job_id: str,
        *,
        requested_at: str,
        idempotency_key: str,
    ) -> ComputeJobView:
        current = self.get(job_id)
        when = _utc_text(requested_at, "requested_at")
        key = _token(idempotency_key, "idempotency_key")
        material = {
            "operation": "request_cancel",
            "job_id": current.job_id,
            "requested_at": when,
        }
        replay = _transition_replay(current, key, material)
        if replay is not None:
            return replay
        if current.state in {"succeeded", "failed", "cancelled"}:
            raise QueueStateError(f"cannot cancel terminal compute job in state {current.state}")
        if current.cancel_requested:
            raise QueueStateError("cancellation has already been requested")
        if current.state in {"queued", "paused"}:
            return self._mutate(
                current.job_id,
                key,
                material,
                state="cancelled",
                cancel_requested=True,
                lease_worker_id=None,
                lease_id=None,
                leased_at=None,
                lease_expires_at=None,
                started_at=None,
                finished_at=when,
            )
        return self._mutate(current.job_id, key, material, cancel_requested=True)

    def acknowledge_cancel(
        self,
        job_id: str,
        *,
        worker_id: str,
        lease_id: str,
        cancelled_at: str,
        idempotency_key: str,
    ) -> ComputeJobView:
        current = self.get(job_id)
        worker = _token(worker_id, "worker_id")
        lease = _token(lease_id, "lease_id")
        cancelled = _utc_text(cancelled_at, "cancelled_at")
        key = _token(idempotency_key, "idempotency_key")
        material = {
            "operation": "acknowledge_cancel",
            "job_id": current.job_id,
            "worker_id": worker,
            "lease_id": lease,
            "cancelled_at": cancelled,
        }
        replay = _transition_replay(current, key, material)
        if replay is not None:
            return replay
        if current.state == "cancelled":
            raise QueueStateError("compute job is already cancelled")
        _lease(current, worker, lease)
        if not current.cancel_requested:
            raise QueueStateError("cancellation has not been requested")
        _within_lease(current, cancelled, "cancelled_at")
        return self._mutate(
            current.job_id,
            key,
            material,
            state="cancelled",
            lease_worker_id=None,
            lease_id=None,
            leased_at=None,
            lease_expires_at=None,
            started_at=None,
            finished_at=cancelled,
        )

    def pause(
        self,
        job_id: str,
        *,
        worker_id: str,
        lease_id: str,
        checkpoint_artifact_id: str,
        checkpoint_sha256: str,
        paused_at: str,
        idempotency_key: str,
    ) -> ComputeJobView:
        current = self.get(job_id)
        worker = _token(worker_id, "worker_id")
        lease = _token(lease_id, "lease_id")
        checkpoint_id = _token(checkpoint_artifact_id, "checkpoint_artifact_id")
        checkpoint_hash = _sha256(checkpoint_sha256, "checkpoint_sha256")
        paused = _utc_text(paused_at, "paused_at")
        key = _token(idempotency_key, "idempotency_key")
        material = {
            "operation": "pause",
            "job_id": current.job_id,
            "worker_id": worker,
            "lease_id": lease,
            "checkpoint_artifact_id": checkpoint_id,
            "checkpoint_sha256": checkpoint_hash,
            "paused_at": paused,
        }
        replay = _transition_replay(current, key, material)
        if replay is not None:
            return replay
        _lease(current, worker, lease)
        if current.state != "running":
            raise QueueStateError(f"cannot pause compute job in state {current.state}")
        if current.cancel_requested:
            raise QueueStateError("cancel-requested job must acknowledge cancellation")
        _within_lease(current, paused, "paused_at")
        return self._mutate(
            current.job_id,
            key,
            material,
            state="paused",
            lease_worker_id=None,
            lease_id=None,
            leased_at=None,
            lease_expires_at=None,
            started_at=None,
            checkpoint_artifact_id=checkpoint_id,
            checkpoint_sha256=checkpoint_hash,
        )

    def resume(self, job_id: str, *, idempotency_key: str) -> ComputeJobView:
        current = self.get(job_id)
        key = _token(idempotency_key, "idempotency_key")
        material = {"operation": "resume", "job_id": current.job_id}
        replay = _transition_replay(current, key, material)
        if replay is not None:
            return replay
        if current.state != "paused":
            raise QueueStateError(f"cannot resume compute job in state {current.state}")
        return self._mutate(
            current.job_id, key, material, state="queued", error_code=None
        )

    def complete(
        self,
        job_id: str,
        *,
        worker_id: str,
        lease_id: str,
        runtime_id: str,
        result_artifact_id: str,
        result_sha256: str,
        completed_at: str,
        idempotency_key: str,
    ) -> ComputeJobView:
        current = self.get(job_id)
        worker = _token(worker_id, "worker_id")
        lease = _token(lease_id, "lease_id")
        runtime = _token(runtime_id, "runtime_id")
        result_id = _token(result_artifact_id, "result_artifact_id")
        result_hash = _sha256(result_sha256, "result_sha256")
        completed = _utc_text(completed_at, "completed_at")
        key = _token(idempotency_key, "idempotency_key")
        material = {
            "operation": "complete",
            "job_id": current.job_id,
            "worker_id": worker,
            "lease_id": lease,
            "runtime_id": runtime,
            "result_artifact_id": result_id,
            "result_sha256": result_hash,
            "completed_at": completed,
        }
        replay = _transition_replay(current, key, material)
        if replay is not None:
            return replay
        if current.state == "succeeded":
            raise QueueStateError("compute job already has a successful result")
        _lease(current, worker, lease)
        if current.state != "running":
            raise QueueStateError(f"cannot complete compute job in state {current.state}")
        if current.cancel_requested:
            raise QueueStateError("cancel-requested job cannot succeed")
        _within_lease(current, completed, "completed_at")
        return self._mutate(
            current.job_id,
            key,
            material,
            state="succeeded",
            lease_worker_id=None,
            lease_id=None,
            leased_at=None,
            lease_expires_at=None,
            started_at=None,
            result_artifact_id=result_id,
            result_sha256=result_hash,
            result_worker_id=worker,
            result_runtime_id=runtime,
            result_attempt=current.attempts,
            finished_at=completed,
            error_code=None,
        )

    def fail(
        self,
        job_id: str,
        *,
        worker_id: str,
        lease_id: str,
        error_code: str,
        failed_at: str,
        retryable: bool,
        idempotency_key: str,
    ) -> ComputeJobView:
        current = self.get(job_id)
        worker = _token(worker_id, "worker_id")
        lease = _token(lease_id, "lease_id")
        error = _token(error_code, "error_code")
        failed = _utc_text(failed_at, "failed_at")
        if not isinstance(retryable, bool):
            raise QueueStateError("retryable must be boolean")
        key = _token(idempotency_key, "idempotency_key")
        material = {
            "operation": "fail",
            "job_id": current.job_id,
            "worker_id": worker,
            "lease_id": lease,
            "error_code": error,
            "failed_at": failed,
            "retryable": retryable,
        }
        replay = _transition_replay(current, key, material)
        if replay is not None:
            return replay
        _lease(current, worker, lease)
        if current.state not in {"leased", "running"}:
            raise QueueStateError(f"cannot fail compute job in state {current.state}")
        _within_lease(current, failed, "failed_at")
        terminal = not retryable or current.attempts >= current.max_attempts
        state = (
            "cancelled"
            if current.cancel_requested
            else ("failed" if terminal else "queued")
        )
        return self._mutate(
            current.job_id,
            key,
            material,
            state=state,
            lease_worker_id=None,
            lease_id=None,
            leased_at=None,
            lease_expires_at=None,
            started_at=None,
            error_code=error,
            finished_at=failed if state in COMPUTE_JOB_TERMINAL_STATES else None,
        )

    def reap_expired(self, *, now: str) -> tuple[ComputeJobView, ...]:
        now_text = _utc_text(now, "now")
        now_dt = _utc(now_text, "now")
        changed: list[ComputeJobView] = []
        for current in self.list_jobs():
            if not current.active_lease:
                continue
            if _utc(current.lease_expires_at, "lease_expires_at") >= now_dt:
                continue
            state = (
                "cancelled"
                if current.cancel_requested
                else ("failed" if current.attempts >= current.max_attempts else "queued")
            )
            key = f"compute-job-reap:{current.job_id}:{current.lease_id}"
            material = {
                "operation": "reap_expired",
                "job_id": current.job_id,
                "lease_id": current.lease_id,
                "now": now_text,
            }
            changed.append(
                self._mutate(
                    current.job_id,
                    key,
                    material,
                    state=state,
                    lease_worker_id=None,
                    lease_id=None,
                    leased_at=None,
                    lease_expires_at=None,
                    started_at=None,
                    error_code="lease_expired",
                    finished_at=(
                        now_text if state in COMPUTE_JOB_TERMINAL_STATES else None
                    ),
                )
            )
        changed.sort(key=lambda job: job.job_id)
        return tuple(changed)

    def _find_transition_replay(
        self,
        jobs: Iterable[ComputeJobView],
        idempotency_key: str,
        material: dict[str, Any],
    ) -> ComputeJobView | None:
        for job in jobs:
            replay = _transition_replay(job, idempotency_key, material)
            if replay is not None:
                return replay
        return None

    def _mutate(
        self,
        job_id: str,
        idempotency_key: str,
        transition_material: dict[str, Any],
        **changes: Any,
    ) -> ComputeJobView:
        key = _token(idempotency_key, "idempotency_key")
        record = self._adapter.get(
            COMPUTE_JOB_RESOURCE_TYPE, _token(job_id, "job_id")
        )
        current = _job_view(record)
        replay = _transition_replay(current, key, transition_material)
        if replay is not None:
            return replay
        key_hash, material_hash = _transition_receipt(key, transition_material)
        payload = deepcopy(record.payload)
        payload.update(changes)
        payload["last_transition_key_sha256"] = key_hash
        payload["last_transition_material_sha256"] = material_hash
        _validate_job_payload(payload, expected_job_id=record.resource_id)
        result = self._adapter.upsert(
            COMPUTE_JOB_RESOURCE_TYPE,
            record.resource_id,
            payload,
            idempotency_key=key,
            expected_revision=record.revision,
        )
        return _job_view(result.record, idempotent_replay=result.idempotent_replay)


def _job_payload(**base: Any) -> dict[str, Any]:
    payload = {
        "schema_version": COMPUTE_JOB_SCHEMA_VERSION,
        **base,
        "cancel_requested": False,
        "lease_worker_id": None,
        "lease_id": None,
        "leased_at": None,
        "lease_expires_at": None,
        "started_at": None,
        "checkpoint_artifact_id": None,
        "checkpoint_sha256": None,
        "error_code": None,
        "result_artifact_id": None,
        "result_sha256": None,
        "result_worker_id": None,
        "result_runtime_id": None,
        "result_attempt": None,
        "finished_at": None,
    }
    payload.setdefault("last_transition_key_sha256", None)
    payload.setdefault("last_transition_material_sha256", None)
    _validate_job_payload(payload, expected_job_id=payload["job_id"])
    return payload


def _job_view(
    record: ResourceRecord, *, idempotent_replay: bool = False
) -> ComputeJobView:
    p = deepcopy(record.payload)
    _validate_job_payload(p, expected_job_id=record.resource_id)
    return ComputeJobView(
        job_id=record.resource_id,
        revision=record.revision,
        operation_id=p["operation_id"],
        service_id=p["service_id"],
        data_classification=p["data_classification"],
        required_capabilities=tuple(p["required_capabilities"]),
        input_artifact_id=p["input_artifact_id"],
        input_sha256=p["input_sha256"],
        priority=p["priority"],
        max_attempts=p["max_attempts"],
        state=p["state"],
        attempts=p["attempts"],
        created_at=p["created_at"],
        cancel_requested=p["cancel_requested"],
        lease_worker_id=p["lease_worker_id"],
        lease_id=p["lease_id"],
        leased_at=p["leased_at"],
        lease_expires_at=p["lease_expires_at"],
        started_at=p["started_at"],
        checkpoint_artifact_id=p["checkpoint_artifact_id"],
        checkpoint_sha256=p["checkpoint_sha256"],
        error_code=p["error_code"],
        result_artifact_id=p["result_artifact_id"],
        result_sha256=p["result_sha256"],
        result_worker_id=p["result_worker_id"],
        result_runtime_id=p["result_runtime_id"],
        result_attempt=p["result_attempt"],
        finished_at=p["finished_at"],
        last_transition_key_sha256=p["last_transition_key_sha256"],
        last_transition_material_sha256=p["last_transition_material_sha256"],
        idempotent_replay=idempotent_replay,
    )


def _validate_job_payload(p: dict[str, Any], *, expected_job_id: str) -> None:
    expected = {
        "schema_version",
        "job_id",
        "operation_id",
        "service_id",
        "data_classification",
        "required_capabilities",
        "input_artifact_id",
        "input_sha256",
        "priority",
        "max_attempts",
        "state",
        "attempts",
        "created_at",
        "cancel_requested",
        "lease_worker_id",
        "lease_id",
        "leased_at",
        "lease_expires_at",
        "started_at",
        "checkpoint_artifact_id",
        "checkpoint_sha256",
        "error_code",
        "result_artifact_id",
        "result_sha256",
        "result_worker_id",
        "result_runtime_id",
        "result_attempt",
        "finished_at",
        "last_transition_key_sha256",
        "last_transition_material_sha256",
    }
    if not isinstance(p, dict) or set(p) != expected:
        raise QueueStateError("compute-job payload fields do not match the supported schema")
    if p["schema_version"] != COMPUTE_JOB_SCHEMA_VERSION or p["job_id"] != expected_job_id:
        raise QueueStateError("compute-job schema/identity mismatch")
    for field in (
        "job_id",
        "operation_id",
        "service_id",
        "data_classification",
        "input_artifact_id",
    ):
        _token(p[field], field)
    caps = p["required_capabilities"]
    if (
        not isinstance(caps, list)
        or list(_tokens(caps, "required_capabilities", allow_empty=False)) != caps
    ):
        raise QueueStateError("required_capabilities must be a sorted unique list")
    _sha256(p["input_sha256"], "input_sha256")
    _rank(p["priority"], "priority")
    max_attempts = _positive(p["max_attempts"], "max_attempts")
    attempts = _nonnegative(p["attempts"], "attempts")
    if attempts > max_attempts:
        raise QueueStateError("attempts cannot exceed max_attempts")
    state = _state(p["state"])
    created = _utc(p["created_at"], "created_at")
    if not isinstance(p["cancel_requested"], bool):
        raise QueueStateError("cancel_requested must be boolean")
    for field in (
        "lease_worker_id",
        "lease_id",
        "checkpoint_artifact_id",
        "error_code",
        "result_artifact_id",
        "result_worker_id",
        "result_runtime_id",
    ):
        if p[field] is not None:
            _token(p[field], field)
    for field in (
        "checkpoint_sha256",
        "result_sha256",
        "last_transition_key_sha256",
        "last_transition_material_sha256",
    ):
        if p[field] is not None:
            _sha256(p[field], field)
    if (p["last_transition_key_sha256"] is None) != (
        p["last_transition_material_sha256"] is None
    ):
        raise QueueStateError("transition receipt hashes must appear together")
    for field in ("leased_at", "lease_expires_at", "started_at", "finished_at"):
        if p[field] is not None:
            _utc(p[field], field)
    active = state in {"leased", "running"}
    lease_fields = (
        p["lease_worker_id"],
        p["lease_id"],
        p["leased_at"],
        p["lease_expires_at"],
    )
    if active and any(value is None for value in lease_fields):
        raise QueueStateError("active compute job requires complete lease state")
    if not active and any(value is not None for value in lease_fields):
        raise QueueStateError("non-active compute job must not retain lease state")
    if active:
        leased = _utc(p["leased_at"], "leased_at")
        expires = _utc(p["lease_expires_at"], "lease_expires_at")
        if leased < created or expires <= leased:
            raise QueueStateError("invalid lease chronology")
        if state == "running":
            if p["started_at"] is None:
                raise QueueStateError("running compute job requires started_at")
            started = _utc(p["started_at"], "started_at")
            if started < leased or started > expires:
                raise QueueStateError("started_at must fall within active lease")
        elif p["started_at"] is not None:
            raise QueueStateError("leased compute job must not have started_at")
    elif p["started_at"] is not None:
        raise QueueStateError("non-active compute job must not retain started_at")
    if (p["checkpoint_artifact_id"] is None) != (p["checkpoint_sha256"] is None):
        raise QueueStateError("checkpoint ID/hash must appear together")
    result_values = (
        p["result_artifact_id"],
        p["result_sha256"],
        p["result_worker_id"],
        p["result_runtime_id"],
        p["result_attempt"],
    )
    if state == "succeeded":
        if any(value is None for value in result_values) or p["finished_at"] is None:
            raise QueueStateError("succeeded job requires exact result provenance")
        if _positive(p["result_attempt"], "result_attempt") != attempts:
            raise QueueStateError("result_attempt must equal attempts")
    elif any(value is not None for value in result_values):
        raise QueueStateError("only succeeded jobs may retain result provenance")
    if state in COMPUTE_JOB_TERMINAL_STATES:
        if p["finished_at"] is None or _utc(p["finished_at"], "finished_at") < created:
            raise QueueStateError("terminal job requires valid finished_at")
    elif p["finished_at"] is not None:
        raise QueueStateError("non-terminal job must not have finished_at")
    if state == "cancelled" and not p["cancel_requested"]:
        raise QueueStateError("cancelled job must retain cancel_requested=true")
    if state in {"queued", "paused"} and p["cancel_requested"]:
        raise QueueStateError("queued/paused job cannot retain cancel_requested=true")


def _transition_receipt(
    idempotency_key: str, material: dict[str, Any]
) -> tuple[str, str]:
    key = _token(idempotency_key, "idempotency_key")
    try:
        normalized = json.dumps(
            material,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise QueueStateError("transition material must be canonical JSON data") from exc
    return (
        hashlib.sha256(key.encode("utf-8")).hexdigest(),
        hashlib.sha256(normalized.encode("utf-8")).hexdigest(),
    )


def _transition_replay(
    job: ComputeJobView, idempotency_key: str, material: dict[str, Any]
) -> ComputeJobView | None:
    key_hash, material_hash = _transition_receipt(idempotency_key, material)
    if job.last_transition_key_sha256 != key_hash:
        return None
    if job.last_transition_material_sha256 != material_hash:
        raise QueueStateError(
            "idempotency key was already used with different transition material"
        )
    return replace(job, idempotent_replay=True)


def _lease(job: ComputeJobView, worker_id: str, lease_id: str) -> None:
    if not job.active_lease:
        raise QueueStateError(f"compute job has no active lease in state {job.state}")
    if (
        job.lease_worker_id != _token(worker_id, "worker_id")
        or job.lease_id != _token(lease_id, "lease_id")
    ):
        raise QueueStateError("compute-job lease ownership mismatch")


def _within_lease(job: ComputeJobView, value: str, field: str) -> None:
    when = _utc(value, field)
    if (
        when < _utc(job.leased_at, "leased_at")
        or when > _utc(job.lease_expires_at, "lease_expires_at")
    ):
        raise QueueStateError(f"{field} must fall within active lease")


def _command_id(value: object) -> str:
    if not isinstance(value, str) or not _ID_RE.fullmatch(value):
        raise CommandSequencerError("command_id has invalid canonical identity syntax")
    return value


def _token(value: object, field: str) -> str:
    if not isinstance(value, str) or not _ID_RE.fullmatch(value):
        raise QueueStateError(f"{field} has invalid canonical identity syntax")
    return value


def _tokens(values: Iterable[str], field: str, *, allow_empty: bool) -> tuple[str, ...]:
    if isinstance(values, (str, bytes)):
        raise QueueStateError(f"{field} must be a collection of tokens")
    try:
        result = tuple(sorted({_token(value, field) for value in values}))
    except TypeError as exc:
        raise QueueStateError(f"{field} must be iterable") from exc
    if not allow_empty and not result:
        raise QueueStateError(f"{field} must not be empty")
    return result


def _sha256(value: object, field: str) -> str:
    if not isinstance(value, str) or not _SHA256_RE.fullmatch(value):
        raise QueueStateError(f"{field} must be lowercase SHA-256 hex")
    return value


def _rank(value: object, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or not 0 <= value <= 1_000_000:
        raise QueueStateError(f"{field} must be an integer from 0 through 1000000")
    return value


def _positive(value: object, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise QueueStateError(f"{field} must be a positive integer")
    return value


def _nonnegative(value: object, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise QueueStateError(f"{field} must be a non-negative integer")
    return value


def _state(value: object) -> str:
    value = _token(value, "state")
    if value not in COMPUTE_JOB_STATES:
        raise QueueStateError("unsupported compute-job state")
    return value


def _utc(value: object, field: str) -> datetime:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise QueueStateError(f"{field} must be a UTC ISO-8601 timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise QueueStateError(f"{field} must be a UTC ISO-8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() != timezone.utc.utcoffset(parsed):
        raise QueueStateError(f"{field} must use UTC")
    return parsed.astimezone(timezone.utc)


def _utc_text(value: object, field: str) -> str:
    _utc(value, field)
    assert isinstance(value, str)
    return value


__all__ = [
    "COMPUTE_JOB_RESOURCE_TYPE",
    "COMPUTE_JOB_SCHEMA_VERSION",
    "COMPUTE_JOB_STATES",
    "COMPUTE_JOB_TERMINAL_STATES",
    "CommandSequencerError",
    "ComputeJobControlPlane",
    "ComputeJobView",
    "DuplicateQueuedCommandError",
    "InMemoryCommandQueue",
    "QueuedCommand",
    "QueueStateError",
    "SequencerOutcome",
    "SerializedCommandWorker",
]
