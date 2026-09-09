"""Read-only aggregate observability for the optional MIRA compute fabric.

OBS-001 requires operational telemetry to remain a projection rather than a
mutable-state authority. This module consumes the existing secret-free worker
registry and durable compute-job views, validates the time/state material needed
for observation, and emits deterministic aggregate Prometheus text plus a stable
Grafana-compatible PromQL panel plan.

Stable worker/job/principal/runtime identifiers are used only for internal
reconciliation and are deliberately excluded from metric labels and dashboard
queries. This module performs no persistence, worker I/O, job execution, scrape
serving, alerting, sensor reads, or hardware-safety decisions.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
import math
import re
from typing import Iterable

from .command_sequencer import (
    COMPUTE_JOB_STATES,
    COMPUTE_JOB_TERMINAL_STATES,
    ComputeJobView,
)
from .service_state import (
    WORKER_AVAILABILITY_STATES,
    WORKER_HEALTH_STATES,
    WORKER_IDENTITY_STATES,
    WORKER_LOCAL_COMPUTE_MODES,
    WORKER_RUNTIME_KINDS,
    WorkerRegistryView,
)


_PROM_NAME_RE = re.compile(r"^[A-Za-z_:][A-Za-z0-9_:]*$")
_PROM_LABEL_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_RESULT_RUNTIME_KINDS = frozenset({"local", "hosted", "unknown"})


class ComputeObservabilityError(Exception):
    """Raised when source observation material cannot be projected safely."""


@dataclass(frozen=True)
class MetricFamilySpec:
    name: str
    help_text: str
    metric_type: str = "gauge"

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not _PROM_NAME_RE.fullmatch(self.name):
            raise ComputeObservabilityError("metric family name is invalid")
        if (
            not isinstance(self.help_text, str)
            or not self.help_text
            or "\n" in self.help_text
        ):
            raise ComputeObservabilityError("metric help_text must be one non-empty line")
        if self.metric_type != "gauge":
            raise ComputeObservabilityError("compute observability currently emits gauges only")


@dataclass(frozen=True)
class MetricSample:
    name: str
    labels: tuple[tuple[str, str], ...]
    value: float

    def __post_init__(self) -> None:
        if self.name not in METRIC_FAMILIES:
            raise ComputeObservabilityError(f"unknown metric family: {self.name}")
        if not isinstance(self.labels, tuple):
            raise ComputeObservabilityError("metric labels must be a tuple")
        normalized: list[tuple[str, str]] = []
        seen: set[str] = set()
        for item in self.labels:
            if (
                not isinstance(item, tuple)
                or len(item) != 2
                or not isinstance(item[0], str)
                or not isinstance(item[1], str)
            ):
                raise ComputeObservabilityError("metric labels must contain string pairs")
            key, value = item
            if not _PROM_LABEL_RE.fullmatch(key):
                raise ComputeObservabilityError(f"invalid metric label name: {key}")
            if key in seen:
                raise ComputeObservabilityError(f"duplicate metric label name: {key}")
            seen.add(key)
            normalized.append((key, value))
        normalized.sort()
        object.__setattr__(self, "labels", tuple(normalized))
        if (
            not isinstance(self.value, (int, float))
            or isinstance(self.value, bool)
            or not math.isfinite(float(self.value))
            or float(self.value) < 0
        ):
            raise ComputeObservabilityError("metric value must be finite and non-negative")
        object.__setattr__(self, "value", float(self.value))


@dataclass(frozen=True)
class GrafanaPanelQuery:
    title: str
    promql: str
    unit: str
    description: str

    def __post_init__(self) -> None:
        for field in ("title", "promql", "unit", "description"):
            value = getattr(self, field)
            if not isinstance(value, str) or not value.strip() or value != value.strip():
                raise ComputeObservabilityError(f"Grafana panel {field} is invalid")


@dataclass(frozen=True)
class ComputeObservabilitySnapshot:
    observed_at: str
    heartbeat_stale_after_seconds: int
    samples: tuple[MetricSample, ...]

    def __post_init__(self) -> None:
        _utc(self.observed_at, "observed_at")
        _positive_seconds(
            self.heartbeat_stale_after_seconds,
            "heartbeat_stale_after_seconds",
        )
        if not isinstance(self.samples, tuple):
            raise ComputeObservabilityError("samples must be a tuple")
        if any(not isinstance(sample, MetricSample) for sample in self.samples):
            raise ComputeObservabilityError("samples must contain MetricSample values")
        ordered = tuple(sorted(self.samples, key=_sample_sort_key))
        object.__setattr__(self, "samples", ordered)

    def render_prometheus(self) -> str:
        """Render deterministic Prometheus text exposition for this snapshot."""

        by_family: dict[str, list[MetricSample]] = defaultdict(list)
        for sample in self.samples:
            by_family[sample.name].append(sample)

        lines: list[str] = []
        for name in METRIC_ORDER:
            samples = by_family.get(name)
            if not samples:
                continue
            family = METRIC_FAMILIES[name]
            lines.append(f"# HELP {name} {family.help_text}")
            lines.append(f"# TYPE {name} {family.metric_type}")
            for sample in sorted(samples, key=_sample_sort_key):
                lines.append(_render_sample(sample))
        return "\n".join(lines) + ("\n" if lines else "")


METRIC_ORDER = (
    "mira_compute_worker_count",
    "mira_compute_worker_heartbeat_age_seconds",
    "mira_compute_stale_worker_count",
    "mira_compute_job_count",
    "mira_compute_job_attempt_count",
    "mira_compute_queued_job_age_seconds",
    "mira_compute_job_lifecycle_duration_seconds",
    "mira_compute_terminal_job_count",
)

METRIC_FAMILIES = {
    "mira_compute_worker_count": MetricFamilySpec(
        "mira_compute_worker_count",
        "Current compute worker count by bounded worker state.",
    ),
    "mira_compute_worker_heartbeat_age_seconds": MetricFamilySpec(
        "mira_compute_worker_heartbeat_age_seconds",
        "Maximum observed worker heartbeat age by runtime kind.",
    ),
    "mira_compute_stale_worker_count": MetricFamilySpec(
        "mira_compute_stale_worker_count",
        "Current count of workers whose heartbeat exceeds the configured freshness window.",
    ),
    "mira_compute_job_count": MetricFamilySpec(
        "mira_compute_job_count",
        "Current compute job count by durable lifecycle state.",
    ),
    "mira_compute_job_attempt_count": MetricFamilySpec(
        "mira_compute_job_attempt_count",
        "Current summed compute job attempts by durable lifecycle state.",
    ),
    "mira_compute_queued_job_age_seconds": MetricFamilySpec(
        "mira_compute_queued_job_age_seconds",
        "Maximum current age of queued compute jobs.",
    ),
    "mira_compute_job_lifecycle_duration_seconds": MetricFamilySpec(
        "mira_compute_job_lifecycle_duration_seconds",
        "Terminal compute job wall-clock lifecycle duration aggregates by terminal state.",
    ),
    "mira_compute_terminal_job_count": MetricFamilySpec(
        "mira_compute_terminal_job_count",
        "Terminal compute job count by state and reconciled local, hosted, or unknown runtime kind.",
    ),
}


_GRAFANA_PANELS = (
    GrafanaPanelQuery(
        title="Compute workers",
        promql="sum(mira_compute_worker_count)",
        unit="short",
        description="Total currently observed compute workers.",
    ),
    GrafanaPanelQuery(
        title="Ready workers",
        promql='sum(mira_compute_worker_count{availability="ready"})',
        unit="short",
        description="Workers currently advertising ready availability.",
    ),
    GrafanaPanelQuery(
        title="Faulted workers",
        promql='sum(mira_compute_worker_count{health="faulted"})',
        unit="short",
        description="Workers currently advertising faulted health.",
    ),
    GrafanaPanelQuery(
        title="Stale worker heartbeats",
        promql="sum(mira_compute_stale_worker_count)",
        unit="short",
        description="Workers beyond the configured heartbeat freshness window.",
    ),
    GrafanaPanelQuery(
        title="Jobs by state",
        promql="sum by (state) (mira_compute_job_count)",
        unit="short",
        description="Durable compute jobs grouped by lifecycle state.",
    ),
    GrafanaPanelQuery(
        title="Oldest queued job",
        promql='max(mira_compute_queued_job_age_seconds{statistic="max"})',
        unit="s",
        description="Maximum current queue age in seconds.",
    ),
    GrafanaPanelQuery(
        title="Failed jobs",
        promql='sum(mira_compute_job_count{state="failed"})',
        unit="short",
        description="Current durable failed-job count.",
    ),
    GrafanaPanelQuery(
        title="Terminal jobs by runtime kind",
        promql="sum by (runtime_kind,state) (mira_compute_terminal_job_count)",
        unit="short",
        description="Terminal outcomes reconciled to local, hosted, or unknown execution kind.",
    ),
)


def grafana_compute_panel_plan() -> tuple[GrafanaPanelQuery, ...]:
    """Return a stable read-only query plan suitable for Grafana Prometheus panels."""

    return _GRAFANA_PANELS


def build_compute_observability(
    workers: Iterable[WorkerRegistryView],
    jobs: Iterable[ComputeJobView],
    *,
    now: str,
    heartbeat_stale_after_seconds: int = 120,
) -> ComputeObservabilitySnapshot:
    """Project worker/job truth into aggregate secret-free telemetry."""

    now_dt = _utc(now, "now")
    stale_after = _positive_seconds(
        heartbeat_stale_after_seconds,
        "heartbeat_stale_after_seconds",
    )
    worker_values = _materialize(workers, WorkerRegistryView, "workers")
    job_values = _materialize(jobs, ComputeJobView, "jobs")

    worker_ids: set[str] = set()
    worker_runtime_by_id: dict[str, str] = {}
    worker_counts: Counter[tuple[str, str, str, str, str, str]] = Counter()
    heartbeat_ages: dict[str, list[float]] = defaultdict(list)
    stale_workers: Counter[str] = Counter()

    for worker in worker_values:
        if worker.worker_id in worker_ids:
            raise ComputeObservabilityError(f"duplicate worker_id: {worker.worker_id}")
        worker_ids.add(worker.worker_id)
        runtime_kind = _enum(worker.runtime_kind, WORKER_RUNTIME_KINDS, "worker runtime_kind")
        availability = _enum(
            worker.availability,
            WORKER_AVAILABILITY_STATES,
            "worker availability",
        )
        health = _enum(worker.health, WORKER_HEALTH_STATES, "worker health")
        identity_state = _enum(
            worker.identity_state,
            WORKER_IDENTITY_STATES,
            "worker identity_state",
        )
        compute_mode = _enum(
            worker.local_compute_mode,
            WORKER_LOCAL_COMPUTE_MODES,
            "worker local_compute_mode",
        )
        if not isinstance(worker.interactive_lock, bool):
            raise ComputeObservabilityError("worker interactive_lock must be boolean")
        heartbeat = _utc(worker.heartbeat_at, "worker heartbeat_at")
        if heartbeat > now_dt:
            raise ComputeObservabilityError("worker heartbeat_at cannot be from the future")
        age = (now_dt - heartbeat).total_seconds()
        worker_runtime_by_id[worker.worker_id] = runtime_kind
        worker_counts[
            (
                runtime_kind,
                availability,
                health,
                identity_state,
                compute_mode,
                "true" if worker.interactive_lock else "false",
            )
        ] += 1
        heartbeat_ages[runtime_kind].append(age)
        if age > stale_after:
            stale_workers[runtime_kind] += 1

    job_ids: set[str] = set()
    job_counts: Counter[str] = Counter()
    job_attempts: Counter[str] = Counter()
    queued_ages: list[float] = []
    terminal_durations: dict[str, list[float]] = defaultdict(list)
    terminal_runtime_counts: Counter[tuple[str, str]] = Counter()

    for job in job_values:
        if job.job_id in job_ids:
            raise ComputeObservabilityError(f"duplicate job_id: {job.job_id}")
        job_ids.add(job.job_id)
        state = _enum(job.state, COMPUTE_JOB_STATES, "job state")
        if (
            not isinstance(job.attempts, int)
            or isinstance(job.attempts, bool)
            or job.attempts < 0
        ):
            raise ComputeObservabilityError("job attempts must be a non-negative integer")
        if (
            not isinstance(job.max_attempts, int)
            or isinstance(job.max_attempts, bool)
            or job.max_attempts < 1
            or job.attempts > job.max_attempts
        ):
            raise ComputeObservabilityError("job max_attempts/attempts are inconsistent")
        created = _utc(job.created_at, "job created_at")
        if created > now_dt:
            raise ComputeObservabilityError("job created_at cannot be from the future")
        started = _optional_utc(job.started_at, "job started_at")
        finished = _optional_utc(job.finished_at, "job finished_at")
        if started is not None:
            if started < created or started > now_dt:
                raise ComputeObservabilityError("job started_at is outside valid lifecycle bounds")
        if finished is not None:
            if finished < created or finished > now_dt:
                raise ComputeObservabilityError("job finished_at is outside valid lifecycle bounds")
            if started is not None and finished < started:
                raise ComputeObservabilityError("job finished_at cannot precede started_at")

        job_counts[state] += 1
        job_attempts[state] += job.attempts
        if state == "queued":
            queued_ages.append((now_dt - created).total_seconds())

        if state in COMPUTE_JOB_TERMINAL_STATES:
            if finished is None:
                raise ComputeObservabilityError(
                    f"terminal job {job.job_id} is missing finished_at"
                )
            terminal_durations[state].append((finished - created).total_seconds())
            runtime_kind = "unknown"
            if job.result_worker_id is not None:
                runtime_kind = worker_runtime_by_id.get(job.result_worker_id, "unknown")
            if runtime_kind not in _RESULT_RUNTIME_KINDS:
                raise ComputeObservabilityError("derived terminal runtime kind is invalid")
            terminal_runtime_counts[(state, runtime_kind)] += 1

    samples: list[MetricSample] = []
    for dimensions, count in sorted(worker_counts.items()):
        runtime_kind, availability, health, identity_state, compute_mode, locked = dimensions
        samples.append(
            MetricSample(
                name="mira_compute_worker_count",
                labels=(
                    ("runtime_kind", runtime_kind),
                    ("availability", availability),
                    ("health", health),
                    ("identity_state", identity_state),
                    ("compute_mode", compute_mode),
                    ("interactive_lock", locked),
                ),
                value=count,
            )
        )
    for runtime_kind, ages in sorted(heartbeat_ages.items()):
        samples.append(
            MetricSample(
                name="mira_compute_worker_heartbeat_age_seconds",
                labels=(("runtime_kind", runtime_kind), ("statistic", "max")),
                value=max(ages),
            )
        )
        samples.append(
            MetricSample(
                name="mira_compute_stale_worker_count",
                labels=(("runtime_kind", runtime_kind),),
                value=stale_workers[runtime_kind],
            )
        )
    for state in sorted(COMPUTE_JOB_STATES):
        samples.append(
            MetricSample(
                name="mira_compute_job_count",
                labels=(("state", state),),
                value=job_counts[state],
            )
        )
        samples.append(
            MetricSample(
                name="mira_compute_job_attempt_count",
                labels=(("state", state),),
                value=job_attempts[state],
            )
        )
    samples.append(
        MetricSample(
            name="mira_compute_queued_job_age_seconds",
            labels=(("statistic", "max"),),
            value=max(queued_ages, default=0.0),
        )
    )
    for state in sorted(COMPUTE_JOB_TERMINAL_STATES):
        durations = terminal_durations[state]
        aggregates = {
            "count": float(len(durations)),
            "sum": float(sum(durations)),
            "max": float(max(durations, default=0.0)),
        }
        for statistic, value in sorted(aggregates.items()):
            samples.append(
                MetricSample(
                    name="mira_compute_job_lifecycle_duration_seconds",
                    labels=(("state", state), ("statistic", statistic)),
                    value=value,
                )
            )
        for runtime_kind in sorted(_RESULT_RUNTIME_KINDS):
            samples.append(
                MetricSample(
                    name="mira_compute_terminal_job_count",
                    labels=(("state", state), ("runtime_kind", runtime_kind)),
                    value=terminal_runtime_counts[(state, runtime_kind)],
                )
            )

    return ComputeObservabilitySnapshot(
        observed_at=now,
        heartbeat_stale_after_seconds=stale_after,
        samples=tuple(samples),
    )


def _materialize(values: Iterable[object], expected_type: type, field: str) -> tuple:
    if isinstance(values, (str, bytes)):
        raise ComputeObservabilityError(f"{field} must be an iterable of views")
    try:
        material = tuple(values)
    except TypeError as exc:
        raise ComputeObservabilityError(f"{field} must be iterable") from exc
    if any(not isinstance(value, expected_type) for value in material):
        raise ComputeObservabilityError(
            f"{field} must contain {expected_type.__name__} values"
        )
    return material


def _enum(value: object, allowed: frozenset[str], field: str) -> str:
    if not isinstance(value, str) or value not in allowed:
        raise ComputeObservabilityError(f"{field} is invalid")
    return value


def _positive_seconds(value: object, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise ComputeObservabilityError(f"{field} must be a positive integer")
    return value


def _utc(value: object, field: str) -> datetime:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise ComputeObservabilityError(f"{field} must be a UTC ISO-8601 timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ComputeObservabilityError(
            f"{field} must be a UTC ISO-8601 timestamp"
        ) from exc
    if parsed.tzinfo is None or parsed.utcoffset() != timezone.utc.utcoffset(parsed):
        raise ComputeObservabilityError(f"{field} must use UTC")
    return parsed.astimezone(timezone.utc)


def _optional_utc(value: object, field: str) -> datetime | None:
    if value is None:
        return None
    return _utc(value, field)


def _sample_sort_key(sample: MetricSample) -> tuple:
    return (METRIC_ORDER.index(sample.name), sample.labels, sample.value)


def _escape_label(value: str) -> str:
    return value.replace("\\", "\\\\").replace("\n", "\\n").replace('"', '\\"')


def _format_number(value: float) -> str:
    if value.is_integer():
        return str(int(value))
    return format(value, ".15g")


def _render_sample(sample: MetricSample) -> str:
    labels = ""
    if sample.labels:
        material = ",".join(
            f'{name}="{_escape_label(value)}"' for name, value in sample.labels
        )
        labels = "{" + material + "}"
    return f"{sample.name}{labels} {_format_number(sample.value)}"
