"""Canonical provider-neutral task state for Personal MIRA.

Tasks are durable MIRROR resources, not chat-memory checklist items. Completion
is an explicit state transition and never deletes history. The service depends
only on STORE-001-compatible structured state so the same semantics can run on
the no-app Google path and later providers without redefining task truth.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import date, datetime
import re
from typing import Any, Mapping

from .structured_state import (
    NotFoundError,
    ResourceRecord,
    StructuredStateAdapter,
    ValidationError as StoreValidationError,
)


TASK_RESOURCE_TYPE = "task"
TASK_SCHEMA_VERSION = 1
TASK_STATES = frozenset({"open", "completed", "cancelled"})
TASK_PRIORITIES = ("high", "medium", "low")
_PRIORITY_RANK = {value: index for index, value in enumerate(TASK_PRIORITIES)}
_TOKEN_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")


class TaskError(Exception):
    """Base class for task-domain failures."""


class TaskValidationError(TaskError):
    """Raised when task input or persisted state is malformed."""


class TaskTransitionError(TaskError):
    """Raised when a requested task-state transition is invalid."""


@dataclass(frozen=True)
class TaskView:
    task_id: str
    revision: int
    title: str
    next_action: str
    priority: str
    state: str
    due_date: str | None
    context: str | None
    parent_task_id: str | None
    completed_at: str | None
    idempotent_replay: bool = False

    @property
    def active(self) -> bool:
        return self.state == "open"

    def sort_key(self) -> tuple[int, int, str, str]:
        due_rank = 1 if self.due_date is None else 0
        due_value = self.due_date or "9999-12-31"
        return (_PRIORITY_RANK[self.priority], due_rank, due_value, self.task_id)


class TaskService:
    """Create, revise and explicitly transition canonical task resources."""

    def __init__(
        self,
        adapter: StructuredStateAdapter,
        *,
        resource_type: str = TASK_RESOURCE_TYPE,
    ) -> None:
        self._adapter = adapter
        self._resource_type = resource_type

    def create(
        self,
        task_id: str,
        *,
        title: str,
        next_action: str,
        priority: str = "medium",
        due_date: str | None = None,
        context: str | None = None,
        parent_task_id: str | None = None,
        idempotency_key: str,
    ) -> TaskView:
        task = _task_id(task_id)
        payload = _payload(
            task_id=task,
            title=title,
            next_action=next_action,
            priority=priority,
            state="open",
            due_date=due_date,
            context=context,
            parent_task_id=parent_task_id,
            completed_at=None,
        )
        try:
            result = self._adapter.upsert(
                self._resource_type,
                task,
                payload,
                idempotency_key=_token(idempotency_key, "idempotency_key"),
                expected_revision=0,
            )
        except StoreValidationError as exc:
            raise TaskValidationError(str(exc)) from exc
        return _view(result.record, idempotent_replay=result.idempotent_replay)

    def get(self, task_id: str) -> TaskView:
        try:
            return _view(self._adapter.get(self._resource_type, _task_id(task_id)))
        except NotFoundError as exc:
            raise TaskValidationError(f"task {task_id!r} does not exist") from exc

    def update(
        self,
        task_id: str,
        *,
        idempotency_key: str,
        title: str | None = None,
        next_action: str | None = None,
        priority: str | None = None,
        due_date: str | None | object = ...,
        context: str | None | object = ...,
        parent_task_id: str | None | object = ...,
    ) -> TaskView:
        current = self.get(task_id)
        if current.state != "open":
            raise TaskTransitionError("only open tasks can be edited; reopen first")
        payload = _payload(
            task_id=current.task_id,
            title=current.title if title is None else title,
            next_action=current.next_action if next_action is None else next_action,
            priority=current.priority if priority is None else priority,
            state=current.state,
            due_date=current.due_date if due_date is ... else due_date,
            context=current.context if context is ... else context,
            parent_task_id=current.parent_task_id if parent_task_id is ... else parent_task_id,
            completed_at=None,
        )
        return self._replace(current, payload, idempotency_key=idempotency_key)

    def complete(
        self,
        task_id: str,
        *,
        completed_at: str,
        idempotency_key: str,
    ) -> TaskView:
        current = self.get(task_id)
        when = _timestamp(completed_at, "completed_at")
        if current.state == "completed":
            if current.completed_at == when:
                return current
            raise TaskTransitionError("task is already completed at a different time")
        if current.state != "open":
            raise TaskTransitionError("only open tasks can be completed")
        payload = _payload(
            task_id=current.task_id,
            title=current.title,
            next_action=current.next_action,
            priority=current.priority,
            state="completed",
            due_date=current.due_date,
            context=current.context,
            parent_task_id=current.parent_task_id,
            completed_at=when,
        )
        return self._replace(current, payload, idempotency_key=idempotency_key)

    def cancel(
        self,
        task_id: str,
        *,
        idempotency_key: str,
    ) -> TaskView:
        current = self.get(task_id)
        if current.state == "cancelled":
            return current
        if current.state != "open":
            raise TaskTransitionError("only open tasks can be cancelled")
        payload = _payload(
            task_id=current.task_id,
            title=current.title,
            next_action=current.next_action,
            priority=current.priority,
            state="cancelled",
            due_date=current.due_date,
            context=current.context,
            parent_task_id=current.parent_task_id,
            completed_at=None,
        )
        return self._replace(current, payload, idempotency_key=idempotency_key)

    def reopen(
        self,
        task_id: str,
        *,
        idempotency_key: str,
    ) -> TaskView:
        current = self.get(task_id)
        if current.state == "open":
            return current
        payload = _payload(
            task_id=current.task_id,
            title=current.title,
            next_action=current.next_action,
            priority=current.priority,
            state="open",
            due_date=current.due_date,
            context=current.context,
            parent_task_id=current.parent_task_id,
            completed_at=None,
        )
        return self._replace(current, payload, idempotency_key=idempotency_key)

    def active_tasks(
        self,
        *,
        context: str | None = None,
        limit: int = 1000,
    ) -> tuple[TaskView, ...]:
        requested_context = _optional_context(context)
        try:
            records = self._adapter.query(self._resource_type, limit=limit)
        except StoreValidationError as exc:
            raise TaskValidationError(str(exc)) from exc
        tasks = [_view(record) for record in records]
        active = [task for task in tasks if task.state == "open"]
        if requested_context is not None:
            active = [
                task
                for task in active
                if task.context is None or task.context == requested_context
            ]
        active.sort(key=TaskView.sort_key)
        return tuple(active)

    def all_tasks(self, *, limit: int = 1000) -> tuple[TaskView, ...]:
        try:
            records = self._adapter.query(self._resource_type, limit=limit)
        except StoreValidationError as exc:
            raise TaskValidationError(str(exc)) from exc
        return tuple(_view(record) for record in records)

    def _replace(
        self,
        current: TaskView,
        payload: Mapping[str, Any],
        *,
        idempotency_key: str,
    ) -> TaskView:
        try:
            result = self._adapter.upsert(
                self._resource_type,
                current.task_id,
                payload,
                idempotency_key=_token(idempotency_key, "idempotency_key"),
                expected_revision=current.revision,
            )
        except StoreValidationError as exc:
            raise TaskValidationError(str(exc)) from exc
        return _view(result.record, idempotent_replay=result.idempotent_replay)


def _payload(
    *,
    task_id: str,
    title: str,
    next_action: str,
    priority: str,
    state: str,
    due_date: str | None,
    context: str | None,
    parent_task_id: str | None,
    completed_at: str | None,
) -> dict[str, Any]:
    task = _task_id(task_id)
    normalized_state = _state(state)
    when = None if completed_at is None else _timestamp(completed_at, "completed_at")
    if normalized_state == "completed" and when is None:
        raise TaskValidationError("completed tasks require completed_at")
    if normalized_state != "completed" and when is not None:
        raise TaskValidationError("only completed tasks may have completed_at")
    parent = None if parent_task_id is None else _task_id(parent_task_id)
    if parent == task:
        raise TaskValidationError("task cannot be its own parent")
    return {
        "schema_version": TASK_SCHEMA_VERSION,
        "task_id": task,
        "title": _text(title, "title", max_length=500),
        "next_action": _text(next_action, "next_action", max_length=1000),
        "priority": _priority(priority),
        "state": normalized_state,
        "due_date": _optional_date(due_date),
        "context": _optional_context(context),
        "parent_task_id": parent,
        "completed_at": when,
    }


def _view(record: ResourceRecord, *, idempotent_replay: bool = False) -> TaskView:
    payload = deepcopy(record.payload)
    if payload.get("schema_version") != TASK_SCHEMA_VERSION:
        raise TaskValidationError("unsupported task schema version")
    task_id = _task_id(payload.get("task_id"))
    if task_id != record.resource_id:
        raise TaskValidationError("task identity/readback mismatch")
    normalized = _payload(
        task_id=task_id,
        title=payload.get("title"),
        next_action=payload.get("next_action"),
        priority=payload.get("priority"),
        state=payload.get("state"),
        due_date=payload.get("due_date"),
        context=payload.get("context"),
        parent_task_id=payload.get("parent_task_id"),
        completed_at=payload.get("completed_at"),
    )
    return TaskView(
        task_id=task_id,
        revision=record.revision,
        title=normalized["title"],
        next_action=normalized["next_action"],
        priority=normalized["priority"],
        state=normalized["state"],
        due_date=normalized["due_date"],
        context=normalized["context"],
        parent_task_id=normalized["parent_task_id"],
        completed_at=normalized["completed_at"],
        idempotent_replay=idempotent_replay,
    )


def _task_id(value: Any) -> str:
    return _token(value, "task_id")


def _token(value: Any, field: str) -> str:
    if not isinstance(value, str) or not _TOKEN_RE.fullmatch(value.strip()):
        raise TaskValidationError(f"{field} must be a stable token")
    return value.strip()


def _text(value: Any, field: str, *, max_length: int) -> str:
    if not isinstance(value, str):
        raise TaskValidationError(f"{field} must be text")
    text = value.strip()
    if not text:
        raise TaskValidationError(f"{field} must not be blank")
    if len(text) > max_length:
        raise TaskValidationError(f"{field} must be at most {max_length} characters")
    return text


def _priority(value: Any) -> str:
    if not isinstance(value, str) or value.strip().lower() not in _PRIORITY_RANK:
        raise TaskValidationError("priority must be high, medium, or low")
    return value.strip().lower()


def _state(value: Any) -> str:
    if not isinstance(value, str) or value.strip().lower() not in TASK_STATES:
        raise TaskValidationError("state must be open, completed, or cancelled")
    return value.strip().lower()


def _optional_date(value: Any) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise TaskValidationError("due_date must be YYYY-MM-DD or null")
    try:
        return date.fromisoformat(value).isoformat()
    except ValueError as exc:
        raise TaskValidationError("due_date must be YYYY-MM-DD or null") from exc


def _optional_context(value: Any) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise TaskValidationError("context must be text or null")
    normalized = value.strip().lower()
    if not normalized:
        raise TaskValidationError("context must not be blank")
    if not _TOKEN_RE.fullmatch(normalized):
        raise TaskValidationError("context must be a stable token")
    return normalized


def _timestamp(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise TaskValidationError(f"{field} must be an ISO-8601 timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise TaskValidationError(f"{field} must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise TaskValidationError(f"{field} must include a UTC offset")
    return parsed.isoformat()


__all__ = [
    "TASK_PRIORITIES",
    "TASK_RESOURCE_TYPE",
    "TASK_SCHEMA_VERSION",
    "TASK_STATES",
    "TaskError",
    "TaskService",
    "TaskTransitionError",
    "TaskValidationError",
    "TaskView",
]
