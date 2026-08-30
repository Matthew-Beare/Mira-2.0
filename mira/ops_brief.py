"""Deterministic task-centered Ops Brief composition for Personal MIRA.

This is the first user-visible no-app vertical. It deliberately composes only
canonical task state plus the already-defined optional progressive-discovery
prompt. Missing weather, mail, orders, mileage, calendar, or other services are
omitted rather than fabricated. Composition is distinct from delivery: the
canonical run checkpoint records a composed brief, never claims a notification
or scheduler actually fired.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import date, datetime, time
import hashlib
import json
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from .onboarding import ProgressiveDiscoveryService
from .structured_state import (
    NotFoundError,
    ResourceRecord,
    StructuredStateAdapter,
    ValidationError as StoreValidationError,
)
from .tasks import TaskService, TaskView


OPS_BRIEF_RESOURCE_TYPE = "ops_brief_run"
OPS_BRIEF_SCHEMA_VERSION = 1
OPS_BRIEF_SLOTS = ("am", "pm")


class OpsBriefError(Exception):
    """Base class for Ops Brief failures."""


class OpsBriefValidationError(OpsBriefError):
    """Raised when schedule, state or persisted run data is invalid."""


class OpsBriefNotDueError(OpsBriefError):
    """Raised when a caller asks the clock gate to run outside a canonical slot."""


@dataclass(frozen=True)
class BriefSlot:
    slot: str
    local_date: str
    timezone: str
    scheduled_local: str
    scheduled_utc: str
    run_id: str


@dataclass(frozen=True)
class OpsBriefView:
    run_id: str
    revision: int
    slot: str
    local_date: str
    timezone: str
    context: str | None
    scheduled_local: str
    scheduled_utc: str
    task_ids: tuple[str, ...]
    discovery_topic_id: str | None
    rendered_text: str
    source_fingerprint: str
    status: str
    delivered: bool
    idempotent_replay: bool = False


@dataclass(frozen=True)
class OpsBriefSchedule:
    am_time: time = time(2, 45)
    pm_time: time = time(14, 45)

    def due_slot(self, instant: datetime, timezone_name: str) -> BriefSlot:
        if not isinstance(instant, datetime) or instant.tzinfo is None or instant.utcoffset() is None:
            raise OpsBriefValidationError("instant must be an offset-aware datetime")
        zone = _zone(timezone_name)
        local = instant.astimezone(zone)
        current = time(local.hour, local.minute)
        if current == self.am_time:
            slot = "am"
            scheduled_time = self.am_time
        elif current == self.pm_time:
            slot = "pm"
            scheduled_time = self.pm_time
        else:
            raise OpsBriefNotDueError(
                "instant does not match the canonical 02:45 or 14:45 local Ops Brief slot"
            )
        scheduled_local = datetime.combine(local.date(), scheduled_time, tzinfo=zone)
        return _slot(slot, local.date(), timezone_name, scheduled_local)

    def explicit_slot(self, local_date: str, slot: str, timezone_name: str) -> BriefSlot:
        day = _date(local_date)
        normalized_slot = _slot_name(slot)
        zone = _zone(timezone_name)
        scheduled_time = self.am_time if normalized_slot == "am" else self.pm_time
        scheduled_local = datetime.combine(day, scheduled_time, tzinfo=zone)
        return _slot(normalized_slot, day, timezone_name, scheduled_local)


class OpsBriefService:
    """Compose and checkpoint one immutable brief snapshot per canonical slot."""

    def __init__(
        self,
        adapter: StructuredStateAdapter,
        *,
        schedule: OpsBriefSchedule | None = None,
        task_service: TaskService | None = None,
        discovery_service: ProgressiveDiscoveryService | None = None,
        resource_type: str = OPS_BRIEF_RESOURCE_TYPE,
    ) -> None:
        self._adapter = adapter
        self._schedule = schedule or OpsBriefSchedule()
        self._tasks = task_service or TaskService(adapter)
        self._discovery = discovery_service
        self._resource_type = resource_type

    def compose_due(
        self,
        instant: datetime,
        *,
        timezone_name: str,
        context: str | None = None,
    ) -> OpsBriefView:
        slot = self._schedule.due_slot(instant, timezone_name)
        return self._compose(slot, context=context)

    def compose_slot(
        self,
        local_date: str,
        slot: str,
        *,
        timezone_name: str,
        context: str | None = None,
    ) -> OpsBriefView:
        resolved = self._schedule.explicit_slot(local_date, slot, timezone_name)
        return self._compose(resolved, context=context)

    def get_run(self, run_id: str) -> OpsBriefView:
        try:
            return _run_view(self._adapter.get(self._resource_type, run_id))
        except NotFoundError as exc:
            raise OpsBriefValidationError(f"Ops Brief run {run_id!r} does not exist") from exc

    def _compose(self, slot: BriefSlot, *, context: str | None) -> OpsBriefView:
        # A canonical slot is immutable once composed. Re-running it reads the
        # same checkpoint instead of silently changing history after tasks move.
        try:
            existing = self._adapter.get(self._resource_type, slot.run_id)
        except NotFoundError:
            existing = None
        if existing is not None:
            return _run_view(existing, idempotent_replay=True)

        tasks = self._tasks.active_tasks(context=context)
        discovery_topic_id: str | None = None
        discovery_prompt: str | None = None
        if self._discovery is not None and not self._date_already_has_discovery(slot.local_date):
            discovery = self._discovery.claim_brief_question(
                slot.local_date,
                idempotency_key=f"ops-brief-discovery:{slot.run_id}",
            )
            if (
                discovery.next_topic is not None
                and discovery.last_brief_local_date == slot.local_date
                and discovery.brief_drip_enabled
            ):
                discovery_topic_id = discovery.next_topic.topic_id
                discovery_prompt = discovery.next_topic.prompt

        fingerprint = _source_fingerprint(
            slot=slot,
            context=context,
            tasks=tasks,
            discovery_topic_id=discovery_topic_id,
            discovery_prompt=discovery_prompt,
        )
        rendered = _render(
            slot=slot,
            context=context,
            tasks=tasks,
            discovery_prompt=discovery_prompt,
        )
        payload = {
            "schema_version": OPS_BRIEF_SCHEMA_VERSION,
            "run_id": slot.run_id,
            "slot": slot.slot,
            "local_date": slot.local_date,
            "timezone": slot.timezone,
            "context": _context(context),
            "scheduled_local": slot.scheduled_local,
            "scheduled_utc": slot.scheduled_utc,
            "task_ids": [task.task_id for task in tasks],
            "task_revisions": {task.task_id: task.revision for task in tasks},
            "discovery_topic_id": discovery_topic_id,
            "rendered_text": rendered,
            "source_fingerprint": fingerprint,
            "status": "composed",
            "delivered": False,
        }
        try:
            result = self._adapter.upsert(
                self._resource_type,
                slot.run_id,
                payload,
                idempotency_key=f"compose:{slot.run_id}:{fingerprint[:24]}",
                expected_revision=0,
            )
        except StoreValidationError as exc:
            raise OpsBriefValidationError(str(exc)) from exc
        return _run_view(result.record, idempotent_replay=result.idempotent_replay)

    def _date_already_has_discovery(self, local_date: str) -> bool:
        try:
            runs = self._adapter.query(self._resource_type, limit=1000)
        except StoreValidationError as exc:
            raise OpsBriefValidationError(str(exc)) from exc
        return any(
            run.payload.get("local_date") == local_date
            and run.payload.get("discovery_topic_id") is not None
            for run in runs
        )


def _render(
    *,
    slot: BriefSlot,
    context: str | None,
    tasks: tuple[TaskView, ...],
    discovery_prompt: str | None,
) -> str:
    label = "AM" if slot.slot == "am" else "PM"
    lines = [f"MIRA Ops Brief — {slot.local_date} {label}"]
    normalized_context = _context(context)
    if normalized_context is not None:
        lines.append(f"Context: {normalized_context.upper()}")
    lines.append("")
    lines.append("Tasks")
    if not tasks:
        lines.append("- No active tasks.")
    else:
        day = date.fromisoformat(slot.local_date)
        for task in tasks:
            due = ""
            if task.due_date is not None:
                due_date = date.fromisoformat(task.due_date)
                if due_date < day:
                    due = f" [OVERDUE {task.due_date}]"
                elif due_date == day:
                    due = " [DUE TODAY]"
                else:
                    due = f" [due {task.due_date}]"
            lines.append(
                f"- [{task.priority.upper()}]{due} {task.title}: {task.next_action}"
            )
    if discovery_prompt is not None:
        lines.extend(("", "Optional setup", f"- {discovery_prompt}"))
    return "\n".join(lines).rstrip() + "\n"


def _slot(
    slot: str,
    day: date,
    timezone_name: str,
    scheduled_local: datetime,
) -> BriefSlot:
    normalized_slot = _slot_name(slot)
    timezone = _timezone_name(timezone_name)
    scheduled_utc = scheduled_local.astimezone(ZoneInfo("UTC"))
    return BriefSlot(
        slot=normalized_slot,
        local_date=day.isoformat(),
        timezone=timezone,
        scheduled_local=scheduled_local.isoformat(),
        scheduled_utc=scheduled_utc.isoformat(),
        run_id=f"ops-brief:{day.isoformat()}:{normalized_slot}",
    )


def _run_view(
    record: ResourceRecord,
    *,
    idempotent_replay: bool = False,
) -> OpsBriefView:
    payload = deepcopy(record.payload)
    if payload.get("schema_version") != OPS_BRIEF_SCHEMA_VERSION:
        raise OpsBriefValidationError("unsupported Ops Brief schema version")
    run_id = payload.get("run_id")
    if not isinstance(run_id, str) or run_id != record.resource_id:
        raise OpsBriefValidationError("Ops Brief run identity/readback mismatch")
    slot = _slot_name(payload.get("slot"))
    local_date = _date(payload.get("local_date")).isoformat()
    timezone = _timezone_name(payload.get("timezone"))
    scheduled_local = _timestamp(payload.get("scheduled_local"), "scheduled_local")
    scheduled_utc = _timestamp(payload.get("scheduled_utc"), "scheduled_utc")
    task_ids = payload.get("task_ids")
    if not isinstance(task_ids, list) or not all(isinstance(item, str) for item in task_ids):
        raise OpsBriefValidationError("Ops Brief task_ids must be a text list")
    discovery_topic_id = payload.get("discovery_topic_id")
    if discovery_topic_id is not None and not isinstance(discovery_topic_id, str):
        raise OpsBriefValidationError("discovery_topic_id must be text or null")
    rendered = payload.get("rendered_text")
    fingerprint = payload.get("source_fingerprint")
    if not isinstance(rendered, str) or not rendered.endswith("\n"):
        raise OpsBriefValidationError("rendered_text must be newline-terminated text")
    if not isinstance(fingerprint, str) or len(fingerprint) != 64:
        raise OpsBriefValidationError("source_fingerprint must be SHA-256 hex")
    if payload.get("status") != "composed" or payload.get("delivered") is not False:
        raise OpsBriefValidationError("first Ops Brief vertical only records composed/not-delivered runs")
    expected_run_id = f"ops-brief:{local_date}:{slot}"
    if run_id != expected_run_id:
        raise OpsBriefValidationError("Ops Brief run_id does not match slot/date")
    return OpsBriefView(
        run_id=run_id,
        revision=record.revision,
        slot=slot,
        local_date=local_date,
        timezone=timezone,
        context=_context(payload.get("context")),
        scheduled_local=scheduled_local,
        scheduled_utc=scheduled_utc,
        task_ids=tuple(task_ids),
        discovery_topic_id=discovery_topic_id,
        rendered_text=rendered,
        source_fingerprint=fingerprint,
        status="composed",
        delivered=False,
        idempotent_replay=idempotent_replay,
    )


def _source_fingerprint(
    *,
    slot: BriefSlot,
    context: str | None,
    tasks: tuple[TaskView, ...],
    discovery_topic_id: str | None,
    discovery_prompt: str | None,
) -> str:
    material: dict[str, Any] = {
        "run_id": slot.run_id,
        "timezone": slot.timezone,
        "context": _context(context),
        "tasks": [
            {
                "task_id": task.task_id,
                "revision": task.revision,
                "title": task.title,
                "next_action": task.next_action,
                "priority": task.priority,
                "due_date": task.due_date,
                "context": task.context,
                "parent_task_id": task.parent_task_id,
            }
            for task in tasks
        ],
        "discovery_topic_id": discovery_topic_id,
        "discovery_prompt": discovery_prompt,
    }
    encoded = json.dumps(
        material,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _zone(value: Any) -> ZoneInfo:
    name = _timezone_name(value)
    try:
        return ZoneInfo(name)
    except (ZoneInfoNotFoundError, ValueError) as exc:
        raise OpsBriefValidationError("timezone must be a valid IANA timezone") from exc


def _timezone_name(value: Any) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise OpsBriefValidationError("timezone must be non-empty IANA text")
    return value


def _slot_name(value: Any) -> str:
    if not isinstance(value, str) or value.strip().lower() not in OPS_BRIEF_SLOTS:
        raise OpsBriefValidationError("slot must be am or pm")
    return value.strip().lower()


def _date(value: Any) -> date:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise OpsBriefValidationError("local_date must be YYYY-MM-DD")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise OpsBriefValidationError("local_date must be YYYY-MM-DD") from exc


def _timestamp(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise OpsBriefValidationError(f"{field} must be ISO-8601 text")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise OpsBriefValidationError(f"{field} must be ISO-8601 text") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise OpsBriefValidationError(f"{field} must include a UTC offset")
    return parsed.isoformat()


def _context(value: Any) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise OpsBriefValidationError("context must be text or null")
    return value.strip().lower()


__all__ = [
    "BriefSlot",
    "OPS_BRIEF_RESOURCE_TYPE",
    "OPS_BRIEF_SCHEMA_VERSION",
    "OPS_BRIEF_SLOTS",
    "OpsBriefError",
    "OpsBriefNotDueError",
    "OpsBriefSchedule",
    "OpsBriefService",
    "OpsBriefValidationError",
    "OpsBriefView",
]
