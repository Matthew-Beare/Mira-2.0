"""Deterministic policy-only hardware safety for optional MIRA compute workers.

Thresholds and shutdown eligibility are explicit configuration. This module does
not discover sensors, infer hardware limits, mutate worker state, execute jobs,
stop processes, call private management APIs, or power off machines. It converts
validated sensor policy plus observations into immutable response requirements
for later lifecycle executors.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
import math
import re
from typing import Iterable


_TOKEN_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_UNIT_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._%°/:-]{0,31}$")


class ComputeSafetyError(Exception):
    """Raised when safety policy/evidence cannot be evaluated safely."""


class SensorDirection(str, Enum):
    HIGH_IS_BAD = "high_is_bad"
    LOW_IS_BAD = "low_is_bad"


class SensorEvidenceState(str, Enum):
    FRESH = "fresh"
    MISSING = "missing"
    STALE = "stale"
    UNIT_MISMATCH = "unit_mismatch"


class SafetySeverity(str, Enum):
    NORMAL = "normal"
    WARNING = "warning"
    CRITICAL = "critical"
    SENSOR_FAULT = "sensor_fault"


_SEVERITY_RANK = {
    SafetySeverity.NORMAL: 0,
    SafetySeverity.WARNING: 1,
    SafetySeverity.CRITICAL: 2,
    SafetySeverity.SENSOR_FAULT: 3,
}


@dataclass(frozen=True)
class SensorSafetyPolicy:
    """Explicit configured safety limits for one required scalar sensor."""

    sensor_id: str
    unit: str
    direction: SensorDirection
    warning_threshold: float
    critical_threshold: float
    max_age_seconds: int

    def __post_init__(self) -> None:
        _token(self.sensor_id, "sensor_id")
        _unit(self.unit, "unit")
        if not isinstance(self.direction, SensorDirection):
            raise ComputeSafetyError("direction must be a SensorDirection")
        warning = _finite(self.warning_threshold, "warning_threshold")
        critical = _finite(self.critical_threshold, "critical_threshold")
        object.__setattr__(self, "warning_threshold", warning)
        object.__setattr__(self, "critical_threshold", critical)
        _positive_int(self.max_age_seconds, "max_age_seconds")
        if self.direction == SensorDirection.HIGH_IS_BAD and not warning < critical:
            raise ComputeSafetyError(
                "high_is_bad warning_threshold must be below critical_threshold"
            )
        if self.direction == SensorDirection.LOW_IS_BAD and not warning > critical:
            raise ComputeSafetyError(
                "low_is_bad warning_threshold must be above critical_threshold"
            )


@dataclass(frozen=True)
class ComputeSafetyPolicy:
    """Node-level deterministic safety configuration; values are never inferred."""

    policy_id: str
    sensors: tuple[SensorSafetyPolicy, ...]
    safe_shutdown_on_critical: bool
    safe_shutdown_on_sensor_fault: bool

    def __post_init__(self) -> None:
        _token(self.policy_id, "policy_id")
        if not isinstance(self.sensors, tuple) or not self.sensors:
            raise ComputeSafetyError("sensors must be a non-empty tuple")
        if any(not isinstance(sensor, SensorSafetyPolicy) for sensor in self.sensors):
            raise ComputeSafetyError("sensors must contain SensorSafetyPolicy values")
        sensor_ids = [sensor.sensor_id for sensor in self.sensors]
        if len(set(sensor_ids)) != len(sensor_ids):
            raise ComputeSafetyError("sensor policy IDs must be unique")
        if not isinstance(self.safe_shutdown_on_critical, bool):
            raise ComputeSafetyError("safe_shutdown_on_critical must be boolean")
        if not isinstance(self.safe_shutdown_on_sensor_fault, bool):
            raise ComputeSafetyError("safe_shutdown_on_sensor_fault must be boolean")
        object.__setattr__(
            self,
            "sensors",
            tuple(sorted(self.sensors, key=lambda sensor: sensor.sensor_id)),
        )


@dataclass(frozen=True)
class SensorObservation:
    """One provider-neutral scalar sensor observation."""

    sensor_id: str
    value: float
    unit: str
    observed_at: str

    def __post_init__(self) -> None:
        _token(self.sensor_id, "sensor_id")
        object.__setattr__(self, "value", _finite(self.value, "value"))
        _unit(self.unit, "unit")
        _utc(self.observed_at, "observed_at")


@dataclass(frozen=True)
class SensorSafetyResult:
    sensor_id: str
    unit: str
    direction: SensorDirection
    warning_threshold: float
    critical_threshold: float
    max_age_seconds: int
    evidence_state: SensorEvidenceState
    severity: SafetySeverity
    reason_code: str
    observed_value: float | None
    observed_at: str | None
    age_seconds: float | None

    def __post_init__(self) -> None:
        _token(self.sensor_id, "sensor_id")
        _unit(self.unit, "unit")
        if not isinstance(self.direction, SensorDirection):
            raise ComputeSafetyError("result direction must be a SensorDirection")
        _finite(self.warning_threshold, "warning_threshold")
        _finite(self.critical_threshold, "critical_threshold")
        _positive_int(self.max_age_seconds, "max_age_seconds")
        if not isinstance(self.evidence_state, SensorEvidenceState):
            raise ComputeSafetyError(
                "result evidence_state must be a SensorEvidenceState"
            )
        if not isinstance(self.severity, SafetySeverity):
            raise ComputeSafetyError("result severity must be a SafetySeverity")
        _token(self.reason_code, "reason_code")
        if self.observed_value is not None:
            _finite(self.observed_value, "observed_value")
        if self.observed_at is not None:
            _utc(self.observed_at, "observed_at")
        if self.age_seconds is not None:
            age = _finite(self.age_seconds, "age_seconds")
            if age < 0:
                raise ComputeSafetyError("age_seconds must be non-negative")
            object.__setattr__(self, "age_seconds", age)


@dataclass(frozen=True)
class SafetyResponseRequirements:
    """Requirements for a later executor; this object performs no side effects."""

    admit_new_work: bool
    request_drain: bool
    stop_workloads: bool
    fault_node: bool
    require_safe_shutdown: bool

    def __post_init__(self) -> None:
        for field in (
            "admit_new_work",
            "request_drain",
            "stop_workloads",
            "fault_node",
            "require_safe_shutdown",
        ):
            if not isinstance(getattr(self, field), bool):
                raise ComputeSafetyError(f"{field} must be boolean")
        if self.admit_new_work and (
            self.request_drain or self.stop_workloads or self.fault_node
        ):
            raise ComputeSafetyError(
                "admit_new_work cannot coexist with drain/stop/fault requirements"
            )
        if self.stop_workloads and not self.request_drain:
            raise ComputeSafetyError("stop_workloads requires request_drain")
        if self.fault_node and not self.stop_workloads:
            raise ComputeSafetyError("fault_node requires stop_workloads")
        if self.require_safe_shutdown and not self.fault_node:
            raise ComputeSafetyError("safe shutdown requires node fault state")


@dataclass(frozen=True)
class ComputeSafetyDecision:
    policy_id: str
    evaluated_at: str
    aggregate_severity: SafetySeverity
    reason_codes: tuple[str, ...]
    sensors: tuple[SensorSafetyResult, ...]
    response: SafetyResponseRequirements

    def __post_init__(self) -> None:
        _token(self.policy_id, "policy_id")
        _utc(self.evaluated_at, "evaluated_at")
        if not isinstance(self.aggregate_severity, SafetySeverity):
            raise ComputeSafetyError(
                "aggregate_severity must be a SafetySeverity"
            )
        if not isinstance(self.reason_codes, tuple):
            raise ComputeSafetyError("reason_codes must be a tuple")
        if any(not isinstance(reason, str) or not reason for reason in self.reason_codes):
            raise ComputeSafetyError("reason_codes must contain non-empty strings")
        if tuple(sorted(set(self.reason_codes))) != self.reason_codes:
            raise ComputeSafetyError("reason_codes must be sorted and unique")
        if not isinstance(self.sensors, tuple) or not self.sensors:
            raise ComputeSafetyError("sensors must be a non-empty tuple")
        if any(not isinstance(sensor, SensorSafetyResult) for sensor in self.sensors):
            raise ComputeSafetyError("sensors must contain SensorSafetyResult values")
        if tuple(sorted(self.sensors, key=lambda sensor: sensor.sensor_id)) != self.sensors:
            raise ComputeSafetyError("sensor results must be sorted by sensor_id")
        if not isinstance(self.response, SafetyResponseRequirements):
            raise ComputeSafetyError(
                "response must be a SafetyResponseRequirements value"
            )


def evaluate_compute_safety(
    policy: ComputeSafetyPolicy,
    observations: Iterable[SensorObservation],
    *,
    now: str,
) -> ComputeSafetyDecision:
    """Evaluate configured safety evidence into deterministic response requirements."""

    if not isinstance(policy, ComputeSafetyPolicy):
        raise ComputeSafetyError("policy must be a ComputeSafetyPolicy")
    now_dt = _utc(now, "now")
    material = _materialize_observations(observations)
    observation_by_id: dict[str, SensorObservation] = {}
    for observation in material:
        if observation.sensor_id in observation_by_id:
            raise ComputeSafetyError(
                f"duplicate sensor observation: {observation.sensor_id}"
            )
        observation_by_id[observation.sensor_id] = observation

    results: list[SensorSafetyResult] = []
    for sensor in policy.sensors:
        observation = observation_by_id.get(sensor.sensor_id)
        results.append(_evaluate_sensor(sensor, observation, now_dt))

    ordered_results = tuple(sorted(results, key=lambda result: result.sensor_id))
    aggregate = max(
        (result.severity for result in ordered_results),
        key=lambda severity: _SEVERITY_RANK[severity],
    )
    reason_codes = tuple(
        sorted(
            {
                f"sensor:{result.sensor_id}:{result.reason_code}"
                for result in ordered_results
                if result.severity != SafetySeverity.NORMAL
            }
        )
    )
    has_warning = any(
        result.severity == SafetySeverity.WARNING for result in ordered_results
    )
    has_critical = any(
        result.severity == SafetySeverity.CRITICAL for result in ordered_results
    )
    has_sensor_fault = any(
        result.severity == SafetySeverity.SENSOR_FAULT for result in ordered_results
    )
    response = _response_requirements(
        policy,
        has_warning=has_warning,
        has_critical=has_critical,
        has_sensor_fault=has_sensor_fault,
    )
    return ComputeSafetyDecision(
        policy_id=policy.policy_id,
        evaluated_at=now,
        aggregate_severity=aggregate,
        reason_codes=reason_codes,
        sensors=ordered_results,
        response=response,
    )


def _evaluate_sensor(
    policy: SensorSafetyPolicy,
    observation: SensorObservation | None,
    now: datetime,
) -> SensorSafetyResult:
    if observation is None:
        return _sensor_result(
            policy,
            evidence_state=SensorEvidenceState.MISSING,
            severity=SafetySeverity.SENSOR_FAULT,
            reason_code="sensor_missing",
            observation=None,
            age_seconds=None,
        )

    observed_at = _utc(observation.observed_at, "observed_at")
    if observed_at > now:
        raise ComputeSafetyError(
            f"sensor observation cannot be from the future: {policy.sensor_id}"
        )
    age_seconds = (now - observed_at).total_seconds()
    if observation.unit != policy.unit:
        return _sensor_result(
            policy,
            evidence_state=SensorEvidenceState.UNIT_MISMATCH,
            severity=SafetySeverity.SENSOR_FAULT,
            reason_code="sensor_unit_mismatch",
            observation=observation,
            age_seconds=age_seconds,
        )
    if age_seconds > policy.max_age_seconds:
        return _sensor_result(
            policy,
            evidence_state=SensorEvidenceState.STALE,
            severity=SafetySeverity.SENSOR_FAULT,
            reason_code="sensor_stale",
            observation=observation,
            age_seconds=age_seconds,
        )

    severity, reason_code = _threshold_severity(policy, observation.value)
    return _sensor_result(
        policy,
        evidence_state=SensorEvidenceState.FRESH,
        severity=severity,
        reason_code=reason_code,
        observation=observation,
        age_seconds=age_seconds,
    )


def _threshold_severity(
    policy: SensorSafetyPolicy,
    value: float,
) -> tuple[SafetySeverity, str]:
    if policy.direction == SensorDirection.HIGH_IS_BAD:
        if value >= policy.critical_threshold:
            return SafetySeverity.CRITICAL, "critical_threshold_crossed"
        if value >= policy.warning_threshold:
            return SafetySeverity.WARNING, "warning_threshold_crossed"
        return SafetySeverity.NORMAL, "within_configured_limits"
    if policy.direction == SensorDirection.LOW_IS_BAD:
        if value <= policy.critical_threshold:
            return SafetySeverity.CRITICAL, "critical_threshold_crossed"
        if value <= policy.warning_threshold:
            return SafetySeverity.WARNING, "warning_threshold_crossed"
        return SafetySeverity.NORMAL, "within_configured_limits"
    raise ComputeSafetyError("unsupported sensor direction")


def _sensor_result(
    policy: SensorSafetyPolicy,
    *,
    evidence_state: SensorEvidenceState,
    severity: SafetySeverity,
    reason_code: str,
    observation: SensorObservation | None,
    age_seconds: float | None,
) -> SensorSafetyResult:
    return SensorSafetyResult(
        sensor_id=policy.sensor_id,
        unit=policy.unit,
        direction=policy.direction,
        warning_threshold=policy.warning_threshold,
        critical_threshold=policy.critical_threshold,
        max_age_seconds=policy.max_age_seconds,
        evidence_state=evidence_state,
        severity=severity,
        reason_code=reason_code,
        observed_value=None if observation is None else observation.value,
        observed_at=None if observation is None else observation.observed_at,
        age_seconds=age_seconds,
    )


def _response_requirements(
    policy: ComputeSafetyPolicy,
    *,
    has_warning: bool,
    has_critical: bool,
    has_sensor_fault: bool,
) -> SafetyResponseRequirements:
    stop_class = has_critical or has_sensor_fault
    drain = has_warning or stop_class
    safe_shutdown = (
        has_critical and policy.safe_shutdown_on_critical
    ) or (
        has_sensor_fault and policy.safe_shutdown_on_sensor_fault
    )
    return SafetyResponseRequirements(
        admit_new_work=not drain,
        request_drain=drain,
        stop_workloads=stop_class,
        fault_node=stop_class,
        require_safe_shutdown=safe_shutdown,
    )


def _materialize_observations(
    observations: Iterable[SensorObservation],
) -> tuple[SensorObservation, ...]:
    if isinstance(observations, (str, bytes)):
        raise ComputeSafetyError("observations must be an iterable of SensorObservation")
    try:
        material = tuple(observations)
    except TypeError as exc:
        raise ComputeSafetyError("observations must be iterable") from exc
    if any(not isinstance(item, SensorObservation) for item in material):
        raise ComputeSafetyError(
            "observations must contain SensorObservation values"
        )
    return material


def _token(value: object, field: str) -> str:
    if not isinstance(value, str) or not _TOKEN_RE.fullmatch(value):
        raise ComputeSafetyError(f"{field} must match {_TOKEN_RE.pattern}")
    return value


def _unit(value: object, field: str) -> str:
    if not isinstance(value, str) or not _UNIT_RE.fullmatch(value):
        raise ComputeSafetyError(f"{field} must match {_UNIT_RE.pattern}")
    return value


def _finite(value: object, field: str) -> float:
    if (
        not isinstance(value, (int, float))
        or isinstance(value, bool)
        or not math.isfinite(float(value))
    ):
        raise ComputeSafetyError(f"{field} must be a finite number")
    return float(value)


def _positive_int(value: object, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise ComputeSafetyError(f"{field} must be a positive integer")
    return value


def _utc(value: object, field: str) -> datetime:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise ComputeSafetyError(f"{field} must be a UTC ISO-8601 timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ComputeSafetyError(
            f"{field} must be a UTC ISO-8601 timestamp"
        ) from exc
    if parsed.tzinfo is None or parsed.utcoffset() != timezone.utc.utcoffset(parsed):
        raise ComputeSafetyError(f"{field} must use UTC")
    return parsed.astimezone(timezone.utc)
