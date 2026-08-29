"""Serialized canonical command execution for multi-client MIRA surfaces.

M2-M0 proved that stock ChatGPT can safely mutate Google-backed MIRROR state
when it is the only writer.  M2-M1 introduces Android, so clients must stop
performing independent read-then-write mutations and submit commands to one
sequencer instead.

This module is deliberately provider-neutral.  It defines the durable command
queue/worker semantics that a Google Workspace worker or managed API boundary
must preserve: one command executes at a time, API-001 remains authoritative,
retries use the existing idempotency contract, stale revisions fail closed, and
a crash after canonical mutation but before queue acknowledgement is safe to
retry.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, replace
import re
from threading import RLock
from typing import Callable

from .api_core import (
    ApiAuthorityError,
    ApiReadbackError,
    ApiService,
    ApiServiceError,
    AuthenticatedPrincipal,
    CommandEnvelope,
    CommandResult,
)


_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_PENDING = "pending"
_SUCCEEDED = "succeeded"
_FAILED = "failed"


class CommandSequencerError(Exception):
    """Base command-sequencer state error."""


class DuplicateQueuedCommandError(CommandSequencerError):
    """Raised when the queue already contains a command ID."""


class QueueStateError(CommandSequencerError):
    """Raised when an illegal queue-state transition is requested."""


@dataclass(frozen=True)
class QueuedCommand:
    """Durable queue projection for one API-001 command."""

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
    """One worker attempt outcome."""

    command_id: str
    status: str
    result: CommandResult | None = None
    error_code: str | None = None
    error_message: str | None = None


class InMemoryCommandQueue:
    """Deterministic synthetic queue used to prove sequencer semantics.

    Real transports may persist queue rows elsewhere.  They must preserve these
    state transitions and stable command identity rather than inventing a second
    command model.
    """

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
    """Execute queued API-001 commands through exactly one critical section.

    The lock represents the one canonical mutation sequencer.  A concrete
    Google Workspace implementation maps this boundary to Apps Script
    ``LockService.getScriptLock()``; a managed deployment may map it to a
    platform-level one-instance/one-request execution guarantee.

    ``after_execute`` is a fault-injection seam.  If it raises after the
    canonical mutation succeeds, the queue entry deliberately remains pending.
    The next attempt re-executes the same API command and must resolve through
    canonical idempotency rather than duplicating the provider mutation.
    """

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
        """Process at most one pending command under the sequencer lock."""

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
                # Provider/readback failures remain pending.  The durable
                # idempotency key makes a later retry safe even if the provider
                # mutation happened before the failure became visible.
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


def _command_id(value: object) -> str:
    if not isinstance(value, str) or not _ID_RE.fullmatch(value):
        raise CommandSequencerError("command_id has invalid canonical identity syntax")
    return value


__all__ = [
    "CommandSequencerError",
    "DuplicateQueuedCommandError",
    "InMemoryCommandQueue",
    "QueuedCommand",
    "QueueStateError",
    "SequencerOutcome",
    "SerializedCommandWorker",
]
