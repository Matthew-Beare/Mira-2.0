"""Capability-based model profiles and explicit benchmark evidence for MIRA compute.

Public MIRA code intentionally supplies no model-family dependencies, benchmark
thresholds, hardware bindings, model paths, or private runtime endpoints. This
module only evaluates explicit sanitizable profile facts and benchmark evidence
against explicit task/policy requirements. It does not load or execute a model.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
import math
import re
from typing import Iterable


_TOKEN_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_UNIT_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._%/:-]{0,31}$")
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class ModelProfileError(Exception):
    """Raised when model-profile or benchmark evidence is malformed/ambiguous."""


class BenchmarkComparator(str, Enum):
    AT_LEAST = "at_least"
    AT_MOST = "at_most"


class BenchmarkEvidenceKind(str, Enum):
    MEASURED = "measured"
    IMPORTED = "imported"
    SYNTHETIC = "synthetic"


@dataclass(frozen=True)
class ModelProfile:
    """Sanitizable logical model/runtime facts; no private deployment binding."""

    profile_id: str
    runtime_id: str
    artifact_id: str
    artifact_sha256: str
    capabilities: tuple[str, ...]
    context_window_tokens: int
    max_output_tokens: int

    def __post_init__(self) -> None:
        _token(self.profile_id, "profile_id")
        _token(self.runtime_id, "runtime_id")
        _token(self.artifact_id, "artifact_id")
        _sha256(self.artifact_sha256, "artifact_sha256")
        _sorted_tokens(self.capabilities, "capabilities", allow_empty=False)
        context = _positive_int(self.context_window_tokens, "context_window_tokens")
        output = _positive_int(self.max_output_tokens, "max_output_tokens")
        if output > context:
            raise ModelProfileError(
                "max_output_tokens cannot exceed context_window_tokens"
            )


@dataclass(frozen=True)
class BenchmarkObservation:
    """One explicit benchmark metric observation with provenance digest."""

    profile_id: str
    benchmark_id: str
    benchmark_version: str
    capability_id: str
    metric_id: str
    value: float
    unit: str
    observed_at: str
    sample_count: int
    evidence_kind: BenchmarkEvidenceKind
    provenance_sha256: str

    def __post_init__(self) -> None:
        _token(self.profile_id, "profile_id")
        _token(self.benchmark_id, "benchmark_id")
        _token(self.benchmark_version, "benchmark_version")
        _token(self.capability_id, "capability_id")
        _token(self.metric_id, "metric_id")
        object.__setattr__(self, "value", _finite(self.value, "value"))
        _unit(self.unit, "unit")
        _utc(self.observed_at, "observed_at")
        _positive_int(self.sample_count, "sample_count")
        if not isinstance(self.evidence_kind, BenchmarkEvidenceKind):
            raise ModelProfileError(
                "evidence_kind must be a BenchmarkEvidenceKind"
            )
        _sha256(self.provenance_sha256, "provenance_sha256")

    def key(self) -> tuple[str, str, str, str, str]:
        return (
            self.profile_id,
            self.benchmark_id,
            self.benchmark_version,
            self.capability_id,
            self.metric_id,
        )


@dataclass(frozen=True)
class BenchmarkRequirement:
    """Explicit policy threshold over one exact benchmark metric identity."""

    benchmark_id: str
    benchmark_version: str
    capability_id: str
    metric_id: str
    comparator: BenchmarkComparator
    threshold: float
    unit: str
    max_age_seconds: int
    allowed_evidence_kinds: tuple[BenchmarkEvidenceKind, ...]

    def __post_init__(self) -> None:
        _token(self.benchmark_id, "benchmark_id")
        _token(self.benchmark_version, "benchmark_version")
        _token(self.capability_id, "capability_id")
        _token(self.metric_id, "metric_id")
        if not isinstance(self.comparator, BenchmarkComparator):
            raise ModelProfileError("comparator must be a BenchmarkComparator")
        object.__setattr__(self, "threshold", _finite(self.threshold, "threshold"))
        _unit(self.unit, "unit")
        _positive_int(self.max_age_seconds, "max_age_seconds")
        if not isinstance(self.allowed_evidence_kinds, tuple) or not self.allowed_evidence_kinds:
            raise ModelProfileError(
                "allowed_evidence_kinds must be a non-empty tuple"
            )
        if any(
            not isinstance(kind, BenchmarkEvidenceKind)
            for kind in self.allowed_evidence_kinds
        ):
            raise ModelProfileError(
                "allowed_evidence_kinds must contain BenchmarkEvidenceKind values"
            )
        canonical = tuple(
            sorted(set(self.allowed_evidence_kinds), key=lambda kind: kind.value)
        )
        if canonical != self.allowed_evidence_kinds:
            raise ModelProfileError(
                "allowed_evidence_kinds must be sorted and unique"
            )

    def key(self) -> tuple[str, str, str, str]:
        return (
            self.benchmark_id,
            self.benchmark_version,
            self.capability_id,
            self.metric_id,
        )


@dataclass(frozen=True)
class ModelSelectionRequest:
    """Explicit model-level requirements; no implicit benchmark policy exists."""

    required_capabilities: tuple[str, ...]
    min_context_window_tokens: int
    min_max_output_tokens: int
    benchmark_requirements: tuple[BenchmarkRequirement, ...] = ()
    preferred_profile_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        capabilities = _sorted_tokens(
            self.required_capabilities,
            "required_capabilities",
            allow_empty=False,
        )
        context = _positive_int(
            self.min_context_window_tokens,
            "min_context_window_tokens",
        )
        output = _positive_int(self.min_max_output_tokens, "min_max_output_tokens")
        if output > context:
            raise ModelProfileError(
                "min_max_output_tokens cannot exceed min_context_window_tokens"
            )
        if not isinstance(self.benchmark_requirements, tuple):
            raise ModelProfileError("benchmark_requirements must be a tuple")
        if any(
            not isinstance(requirement, BenchmarkRequirement)
            for requirement in self.benchmark_requirements
        ):
            raise ModelProfileError(
                "benchmark_requirements must contain BenchmarkRequirement values"
            )
        requirement_keys = [
            requirement.key() for requirement in self.benchmark_requirements
        ]
        if len(set(requirement_keys)) != len(requirement_keys):
            raise ModelProfileError("benchmark requirement keys must be unique")
        canonical_requirements = tuple(
            sorted(self.benchmark_requirements, key=lambda requirement: requirement.key())
        )
        if canonical_requirements != self.benchmark_requirements:
            raise ModelProfileError(
                "benchmark_requirements must be sorted by benchmark identity"
            )
        capability_set = set(capabilities)
        for requirement in self.benchmark_requirements:
            if requirement.capability_id not in capability_set:
                raise ModelProfileError(
                    "benchmark requirement capability must also be required"
                )
        if not isinstance(self.preferred_profile_ids, tuple):
            raise ModelProfileError("preferred_profile_ids must be a tuple")
        for profile_id in self.preferred_profile_ids:
            _token(profile_id, "preferred_profile_id")
        if len(set(self.preferred_profile_ids)) != len(self.preferred_profile_ids):
            raise ModelProfileError("preferred_profile_ids must be unique")


@dataclass(frozen=True)
class ModelProfileEvaluation:
    profile_id: str
    eligible: bool
    blocker_reason_codes: tuple[str, ...]

    def __post_init__(self) -> None:
        _token(self.profile_id, "profile_id")
        if not isinstance(self.eligible, bool):
            raise ModelProfileError("eligible must be boolean")
        if tuple(sorted(set(self.blocker_reason_codes))) != self.blocker_reason_codes:
            raise ModelProfileError(
                "blocker_reason_codes must be sorted and unique"
            )
        if any(
            not isinstance(reason, str) or not reason
            for reason in self.blocker_reason_codes
        ):
            raise ModelProfileError(
                "blocker_reason_codes must contain non-empty strings"
            )
        if self.eligible and self.blocker_reason_codes:
            raise ModelProfileError("eligible profile cannot contain blockers")
        if not self.eligible and not self.blocker_reason_codes:
            raise ModelProfileError("ineligible profile must contain blockers")


@dataclass(frozen=True)
class ModelSelectionDecision:
    evaluated_at: str
    selected_profile_id: str | None
    selection_reason_code: str
    evaluations: tuple[ModelProfileEvaluation, ...]

    def __post_init__(self) -> None:
        _utc(self.evaluated_at, "evaluated_at")
        if self.selected_profile_id is not None:
            _token(self.selected_profile_id, "selected_profile_id")
        _token(self.selection_reason_code, "selection_reason_code")
        if not isinstance(self.evaluations, tuple) or not self.evaluations:
            raise ModelProfileError("evaluations must be a non-empty tuple")
        if any(
            not isinstance(evaluation, ModelProfileEvaluation)
            for evaluation in self.evaluations
        ):
            raise ModelProfileError(
                "evaluations must contain ModelProfileEvaluation values"
            )
        if tuple(
            sorted(self.evaluations, key=lambda evaluation: evaluation.profile_id)
        ) != self.evaluations:
            raise ModelProfileError("evaluations must be sorted by profile_id")
        if len({evaluation.profile_id for evaluation in self.evaluations}) != len(
            self.evaluations
        ):
            raise ModelProfileError("evaluations must have unique profile IDs")
        eligible_ids = {
            evaluation.profile_id
            for evaluation in self.evaluations
            if evaluation.eligible
        }
        if self.selected_profile_id is None and eligible_ids:
            raise ModelProfileError(
                "selected_profile_id is required when eligible profiles exist"
            )
        if self.selected_profile_id is not None and self.selected_profile_id not in eligible_ids:
            raise ModelProfileError("selected profile must be eligible")


def evaluate_model_profiles(
    profiles: Iterable[ModelProfile],
    observations: Iterable[BenchmarkObservation],
    request: ModelSelectionRequest,
    *,
    now: str,
) -> ModelSelectionDecision:
    """Evaluate explicit model facts/evidence without inventing quality thresholds."""

    if not isinstance(request, ModelSelectionRequest):
        raise ModelProfileError("request must be a ModelSelectionRequest")
    now_dt = _utc(now, "now")
    profile_values = _materialize_profiles(profiles)
    observation_values = _materialize_observations(observations)
    observation_by_key = {observation.key(): observation for observation in observation_values}

    evaluations = tuple(
        _evaluate_profile(
            profile,
            observation_by_key,
            request,
            now_dt,
        )
        for profile in profile_values
    )
    eligible_ids = {
        evaluation.profile_id for evaluation in evaluations if evaluation.eligible
    }
    selected: str | None = None
    reason = "no_eligible_profile"
    for preferred in request.preferred_profile_ids:
        if preferred in eligible_ids:
            selected = preferred
            reason = "preferred_profile_eligible"
            break
    if selected is None and eligible_ids:
        selected = min(eligible_ids)
        reason = "stable_profile_id_tiebreak"
    return ModelSelectionDecision(
        evaluated_at=now,
        selected_profile_id=selected,
        selection_reason_code=reason,
        evaluations=evaluations,
    )


def _evaluate_profile(
    profile: ModelProfile,
    observations: dict[tuple[str, str, str, str, str], BenchmarkObservation],
    request: ModelSelectionRequest,
    now: datetime,
) -> ModelProfileEvaluation:
    blockers: set[str] = set()
    profile_capabilities = set(profile.capabilities)
    for capability in request.required_capabilities:
        if capability not in profile_capabilities:
            blockers.add(f"capability_missing:{capability}")
    if profile.context_window_tokens < request.min_context_window_tokens:
        blockers.add("context_window_below_minimum")
    if profile.max_output_tokens < request.min_max_output_tokens:
        blockers.add("max_output_below_minimum")

    for requirement in request.benchmark_requirements:
        prefix = (
            f"benchmark:{requirement.benchmark_id}:"
            f"{requirement.metric_id}"
        )
        if requirement.capability_id not in profile_capabilities:
            blockers.add(f"{prefix}:capability_missing")
            continue
        key = (
            profile.profile_id,
            requirement.benchmark_id,
            requirement.benchmark_version,
            requirement.capability_id,
            requirement.metric_id,
        )
        observation = observations.get(key)
        if observation is None:
            blockers.add(f"{prefix}:evidence_missing")
            continue
        if observation.unit != requirement.unit:
            blockers.add(f"{prefix}:unit_mismatch")
            continue
        if observation.evidence_kind not in requirement.allowed_evidence_kinds:
            blockers.add(f"{prefix}:evidence_kind_disallowed")
            continue
        observed_at = _utc(observation.observed_at, "observed_at")
        if observed_at > now:
            blockers.add(f"{prefix}:evidence_from_future")
            continue
        age_seconds = (now - observed_at).total_seconds()
        if age_seconds > requirement.max_age_seconds:
            blockers.add(f"{prefix}:evidence_stale")
            continue
        if not _threshold_satisfied(observation.value, requirement):
            blockers.add(f"{prefix}:threshold_not_met")

    ordered = tuple(sorted(blockers))
    return ModelProfileEvaluation(
        profile_id=profile.profile_id,
        eligible=not ordered,
        blocker_reason_codes=ordered,
    )


def _threshold_satisfied(value: float, requirement: BenchmarkRequirement) -> bool:
    if requirement.comparator == BenchmarkComparator.AT_LEAST:
        return value >= requirement.threshold
    if requirement.comparator == BenchmarkComparator.AT_MOST:
        return value <= requirement.threshold
    raise ModelProfileError("unsupported benchmark comparator")


def _materialize_profiles(profiles: Iterable[ModelProfile]) -> tuple[ModelProfile, ...]:
    if isinstance(profiles, (str, bytes)):
        raise ModelProfileError("profiles must be an iterable of ModelProfile values")
    try:
        material = tuple(profiles)
    except TypeError as exc:
        raise ModelProfileError(
            "profiles must be an iterable of ModelProfile values"
        ) from exc
    if not material:
        raise ModelProfileError("at least one model profile is required")
    if any(not isinstance(profile, ModelProfile) for profile in material):
        raise ModelProfileError("profiles must contain ModelProfile values")
    if len({profile.profile_id for profile in material}) != len(material):
        raise ModelProfileError("profile IDs must be unique")
    return tuple(sorted(material, key=lambda profile: profile.profile_id))


def _materialize_observations(
    observations: Iterable[BenchmarkObservation],
) -> tuple[BenchmarkObservation, ...]:
    if isinstance(observations, (str, bytes)):
        raise ModelProfileError(
            "observations must be an iterable of BenchmarkObservation values"
        )
    try:
        material = tuple(observations)
    except TypeError as exc:
        raise ModelProfileError(
            "observations must be an iterable of BenchmarkObservation values"
        ) from exc
    if any(not isinstance(observation, BenchmarkObservation) for observation in material):
        raise ModelProfileError(
            "observations must contain BenchmarkObservation values"
        )
    keys = [observation.key() for observation in material]
    if len(set(keys)) != len(keys):
        raise ModelProfileError("benchmark observation keys must be unique")
    return tuple(sorted(material, key=lambda observation: observation.key()))


def _sorted_tokens(
    values: object,
    field: str,
    *,
    allow_empty: bool,
) -> tuple[str, ...]:
    if not isinstance(values, tuple):
        raise ModelProfileError(f"{field} must be a tuple")
    normalized = tuple(_token(value, field) for value in values)
    if not allow_empty and not normalized:
        raise ModelProfileError(f"{field} must not be empty")
    if tuple(sorted(set(normalized))) != normalized:
        raise ModelProfileError(f"{field} must be sorted and unique")
    return normalized


def _token(value: object, field: str) -> str:
    if not isinstance(value, str) or not _TOKEN_RE.fullmatch(value):
        raise ModelProfileError(f"{field} must be a bounded token")
    return value


def _unit(value: object, field: str) -> str:
    if not isinstance(value, str) or not _UNIT_RE.fullmatch(value):
        raise ModelProfileError(f"{field} must be a bounded unit token")
    return value


def _sha256(value: object, field: str) -> str:
    if not isinstance(value, str) or not _SHA256_RE.fullmatch(value):
        raise ModelProfileError(f"{field} must be a lowercase SHA-256 digest")
    return value


def _finite(value: object, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ModelProfileError(f"{field} must be numeric")
    result = float(value)
    if not math.isfinite(result):
        raise ModelProfileError(f"{field} must be finite")
    return result


def _positive_int(value: object, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise ModelProfileError(f"{field} must be a positive integer")
    return value


def _utc(value: object, field: str) -> datetime:
    if not isinstance(value, str) or not value or value != value.strip():
        raise ModelProfileError(f"{field} must be a UTC ISO-8601 timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ModelProfileError(
            f"{field} must be a UTC ISO-8601 timestamp"
        ) from exc
    if parsed.tzinfo is None or parsed.utcoffset() != timezone.utc.utcoffset(parsed):
        raise ModelProfileError(f"{field} must use UTC")
    return parsed.astimezone(timezone.utc)
