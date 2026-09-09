"""Deterministic evidence planning for competitive MIRA Studio development.

This module does not create Git branches, invoke models/providers, execute tests,
schedule private runners, merge code, or activate features. It validates supplied
packet/candidate/verification/critique evidence and, only after explicit reviewer
selection, emits an immutable integration plan bound to one exact candidate SHA.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import re
from typing import Iterable


_TOKEN_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_BRANCH_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]{0,191}$")
_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
_DIGEST_RE = re.compile(r"^[0-9a-f]{64}$")


class StudioCompetitionError(Exception):
    """Raised when competitive-development evidence is malformed or ambiguous."""


class VerificationOutcome(str, Enum):
    PASSED = "passed"
    FAILED = "failed"


class CritiqueSeverity(str, Enum):
    BLOCKING = "blocking"
    NON_BLOCKING = "non_blocking"


class CritiqueResolution(str, Enum):
    OPEN = "open"
    RESOLVED = "resolved"
    ACCEPTED_RISK = "accepted_risk"


@dataclass(frozen=True)
class StudioWorkSpec:
    packet_id: str
    work_id: str
    base_sha: str
    feature_ids: tuple[str, ...]
    acceptance_criteria: tuple[str, ...]
    required_verification_suites: tuple[str, ...]
    require_independent_critique: bool

    def __post_init__(self) -> None:
        _token(self.packet_id, "packet_id")
        _token(self.work_id, "work_id")
        _sha(self.base_sha, "base_sha")
        _sorted_tokens(self.feature_ids, "feature_ids", allow_empty=False)
        _sorted_tokens(
            self.acceptance_criteria, "acceptance_criteria", allow_empty=False
        )
        _sorted_tokens(
            self.required_verification_suites,
            "required_verification_suites",
            allow_empty=False,
        )
        if not isinstance(self.require_independent_critique, bool):
            raise StudioCompetitionError(
                "require_independent_critique must be boolean"
            )


@dataclass(frozen=True)
class StudioCandidate:
    candidate_id: str
    producer_id: str
    branch: str
    base_sha: str
    head_sha: str
    acceptance_criteria: tuple[str, ...]
    source_sha256: str

    def __post_init__(self) -> None:
        _token(self.candidate_id, "candidate_id")
        _token(self.producer_id, "producer_id")
        _branch(self.branch)
        _sha(self.base_sha, "base_sha")
        _sha(self.head_sha, "head_sha")
        if self.head_sha == self.base_sha:
            raise StudioCompetitionError("candidate head_sha must differ from base_sha")
        _sorted_tokens(
            self.acceptance_criteria, "acceptance_criteria", allow_empty=False
        )
        _digest(self.source_sha256, "source_sha256")


@dataclass(frozen=True)
class VerificationEvidence:
    candidate_id: str
    head_sha: str
    suite_id: str
    outcome: VerificationOutcome
    evidence_sha256: str

    def __post_init__(self) -> None:
        _token(self.candidate_id, "candidate_id")
        _sha(self.head_sha, "head_sha")
        _token(self.suite_id, "suite_id")
        if not isinstance(self.outcome, VerificationOutcome):
            raise StudioCompetitionError(
                "verification outcome must be a VerificationOutcome"
            )
        _digest(self.evidence_sha256, "evidence_sha256")


@dataclass(frozen=True)
class CritiqueEvidence:
    target_candidate_id: str
    target_head_sha: str
    critic_id: str
    finding_id: str
    severity: CritiqueSeverity
    resolution: CritiqueResolution
    evidence_sha256: str

    def __post_init__(self) -> None:
        _token(self.target_candidate_id, "target_candidate_id")
        _sha(self.target_head_sha, "target_head_sha")
        _token(self.critic_id, "critic_id")
        _token(self.finding_id, "finding_id")
        if not isinstance(self.severity, CritiqueSeverity):
            raise StudioCompetitionError("severity must be a CritiqueSeverity")
        if not isinstance(self.resolution, CritiqueResolution):
            raise StudioCompetitionError("resolution must be a CritiqueResolution")
        _digest(self.evidence_sha256, "evidence_sha256")


@dataclass(frozen=True)
class ReviewerSelection:
    reviewer_id: str
    candidate_id: str
    head_sha: str

    def __post_init__(self) -> None:
        _token(self.reviewer_id, "reviewer_id")
        _token(self.candidate_id, "candidate_id")
        _sha(self.head_sha, "head_sha")


@dataclass(frozen=True)
class CandidateEvaluation:
    candidate_id: str
    producer_id: str
    branch: str
    head_sha: str
    integration_ready: bool
    blockers: tuple[str, ...]
    verified_suite_ids: tuple[str, ...]
    critique_finding_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        _token(self.candidate_id, "candidate_id")
        _token(self.producer_id, "producer_id")
        _branch(self.branch)
        _sha(self.head_sha, "head_sha")
        if not isinstance(self.integration_ready, bool):
            raise StudioCompetitionError("integration_ready must be boolean")
        _sorted_tokens(self.blockers, "blockers", allow_empty=True)
        _sorted_tokens(
            self.verified_suite_ids, "verified_suite_ids", allow_empty=True
        )
        _sorted_tokens(
            self.critique_finding_ids, "critique_finding_ids", allow_empty=True
        )
        if self.integration_ready != (not self.blockers):
            raise StudioCompetitionError(
                "integration_ready must exactly reflect blocker absence"
            )


@dataclass(frozen=True)
class IntegrationPlan:
    reviewer_id: str
    candidate_id: str
    producer_id: str
    branch: str
    base_sha: str
    head_sha: str
    source_sha256: str
    verification_evidence_sha256s: tuple[str, ...]
    critique_evidence_sha256s: tuple[str, ...]

    def __post_init__(self) -> None:
        _token(self.reviewer_id, "reviewer_id")
        _token(self.candidate_id, "candidate_id")
        _token(self.producer_id, "producer_id")
        _branch(self.branch)
        _sha(self.base_sha, "base_sha")
        _sha(self.head_sha, "head_sha")
        _digest(self.source_sha256, "source_sha256")
        _sorted_digests(
            self.verification_evidence_sha256s,
            "verification_evidence_sha256s",
        )
        _sorted_digests(
            self.critique_evidence_sha256s,
            "critique_evidence_sha256s",
        )


@dataclass(frozen=True)
class StudioCompetitionDecision:
    packet_id: str
    work_id: str
    base_sha: str
    evaluations: tuple[CandidateEvaluation, ...]
    eligible_candidate_ids: tuple[str, ...]
    integration_plan: IntegrationPlan | None

    def __post_init__(self) -> None:
        _token(self.packet_id, "packet_id")
        _token(self.work_id, "work_id")
        _sha(self.base_sha, "base_sha")
        if not isinstance(self.evaluations, tuple) or not self.evaluations:
            raise StudioCompetitionError("evaluations must be a non-empty tuple")
        if any(
            not isinstance(item, CandidateEvaluation) for item in self.evaluations
        ):
            raise StudioCompetitionError(
                "evaluations must contain CandidateEvaluation values"
            )
        if tuple(sorted(self.evaluations, key=lambda item: item.candidate_id)) != self.evaluations:
            raise StudioCompetitionError("evaluations must be sorted by candidate_id")
        _sorted_tokens(
            self.eligible_candidate_ids,
            "eligible_candidate_ids",
            allow_empty=True,
        )
        expected = tuple(
            item.candidate_id for item in self.evaluations if item.integration_ready
        )
        if expected != self.eligible_candidate_ids:
            raise StudioCompetitionError(
                "eligible_candidate_ids must exactly match integration-ready evaluations"
            )
        if self.integration_plan is not None:
            if not isinstance(self.integration_plan, IntegrationPlan):
                raise StudioCompetitionError(
                    "integration_plan must be an IntegrationPlan or None"
                )
            if self.integration_plan.candidate_id not in self.eligible_candidate_ids:
                raise StudioCompetitionError(
                    "integration plan candidate must be integration-ready"
                )


def evaluate_studio_competition(
    spec: StudioWorkSpec,
    candidates: Iterable[StudioCandidate],
    verifications: Iterable[VerificationEvidence],
    critiques: Iterable[CritiqueEvidence],
    *,
    reviewer_selection: ReviewerSelection | None = None,
) -> StudioCompetitionDecision:
    """Evaluate exact candidate evidence without executing or ranking candidates."""

    if not isinstance(spec, StudioWorkSpec):
        raise StudioCompetitionError("spec must be a StudioWorkSpec")
    candidate_items = _materialize(candidates, StudioCandidate, "candidates")
    verification_items = _materialize(
        verifications, VerificationEvidence, "verifications", allow_empty=True
    )
    critique_items = _materialize(
        critiques, CritiqueEvidence, "critiques", allow_empty=True
    )
    if reviewer_selection is not None and not isinstance(
        reviewer_selection, ReviewerSelection
    ):
        raise StudioCompetitionError(
            "reviewer_selection must be a ReviewerSelection or None"
        )

    candidate_by_id: dict[str, StudioCandidate] = {}
    branch_owner: dict[str, str] = {}
    for candidate in candidate_items:
        if candidate.candidate_id in candidate_by_id:
            raise StudioCompetitionError(
                f"duplicate candidate_id: {candidate.candidate_id}"
            )
        if candidate.branch in branch_owner:
            raise StudioCompetitionError(
                f"candidate branches must be unique: {candidate.branch}"
            )
        candidate_by_id[candidate.candidate_id] = candidate
        branch_owner[candidate.branch] = candidate.candidate_id

    _reject_unknown_evidence(candidate_by_id, verification_items, critique_items)

    evaluations = tuple(
        _evaluate_candidate(
            spec,
            candidate,
            verification_items,
            critique_items,
        )
        for candidate in sorted(candidate_items, key=lambda item: item.candidate_id)
    )
    eligible = tuple(
        item.candidate_id for item in evaluations if item.integration_ready
    )
    plan = _integration_plan(
        spec,
        candidate_by_id,
        evaluations,
        verification_items,
        critique_items,
        reviewer_selection,
    )
    return StudioCompetitionDecision(
        packet_id=spec.packet_id,
        work_id=spec.work_id,
        base_sha=spec.base_sha,
        evaluations=evaluations,
        eligible_candidate_ids=eligible,
        integration_plan=plan,
    )


def _evaluate_candidate(
    spec: StudioWorkSpec,
    candidate: StudioCandidate,
    verifications: tuple[VerificationEvidence, ...],
    critiques: tuple[CritiqueEvidence, ...],
) -> CandidateEvaluation:
    blockers: set[str] = set()
    verified_suites: set[str] = set()

    if candidate.base_sha != spec.base_sha:
        blockers.add("candidate:base_sha_mismatch")

    missing_criteria = set(spec.acceptance_criteria) - set(candidate.acceptance_criteria)
    for criterion in missing_criteria:
        blockers.add(f"acceptance:{criterion}:missing")

    for suite_id in spec.required_verification_suites:
        evidence = tuple(
            item
            for item in verifications
            if item.candidate_id == candidate.candidate_id
            and item.suite_id == suite_id
        )
        if not evidence:
            blockers.add(f"verification:{suite_id}:missing")
            continue
        if len(evidence) != 1:
            blockers.add(f"verification:{suite_id}:duplicate")
            continue
        item = evidence[0]
        if item.head_sha != candidate.head_sha:
            blockers.add(f"verification:{suite_id}:head_mismatch")
            continue
        if item.outcome != VerificationOutcome.PASSED:
            blockers.add(f"verification:{suite_id}:failed")
            continue
        verified_suites.add(suite_id)

    candidate_critiques = tuple(
        item
        for item in critiques
        if item.target_candidate_id == candidate.candidate_id
    )
    finding_counts: dict[str, int] = {}
    for critique in candidate_critiques:
        finding_counts[critique.finding_id] = finding_counts.get(critique.finding_id, 0) + 1
    for finding_id, count in finding_counts.items():
        if count > 1:
            blockers.add(f"critique:{finding_id}:duplicate")

    active_critiques: list[CritiqueEvidence] = []
    for critique in candidate_critiques:
        if critique.target_head_sha != candidate.head_sha:
            blockers.add(f"critique:{critique.finding_id}:head_mismatch")
            continue
        if finding_counts[critique.finding_id] > 1:
            continue
        active_critiques.append(critique)
        if (
            critique.severity == CritiqueSeverity.BLOCKING
            and critique.resolution == CritiqueResolution.OPEN
        ):
            blockers.add(f"critique:{critique.finding_id}:open_blocking")

    if spec.require_independent_critique and not any(
        critique.critic_id != candidate.producer_id for critique in active_critiques
    ):
        blockers.add("critique:independent_required")

    blocker_tuple = tuple(sorted(blockers))
    return CandidateEvaluation(
        candidate_id=candidate.candidate_id,
        producer_id=candidate.producer_id,
        branch=candidate.branch,
        head_sha=candidate.head_sha,
        integration_ready=not blocker_tuple,
        blockers=blocker_tuple,
        verified_suite_ids=tuple(sorted(verified_suites)),
        critique_finding_ids=tuple(
            sorted(critique.finding_id for critique in active_critiques)
        ),
    )


def _integration_plan(
    spec: StudioWorkSpec,
    candidate_by_id: dict[str, StudioCandidate],
    evaluations: tuple[CandidateEvaluation, ...],
    verifications: tuple[VerificationEvidence, ...],
    critiques: tuple[CritiqueEvidence, ...],
    selection: ReviewerSelection | None,
) -> IntegrationPlan | None:
    if selection is None:
        return None
    try:
        candidate = candidate_by_id[selection.candidate_id]
    except KeyError as exc:
        raise StudioCompetitionError(
            f"reviewer selected unknown candidate: {selection.candidate_id}"
        ) from exc
    if selection.head_sha != candidate.head_sha:
        raise StudioCompetitionError(
            "reviewer selection head_sha does not match current candidate head"
        )
    evaluation = next(
        item for item in evaluations if item.candidate_id == candidate.candidate_id
    )
    if not evaluation.integration_ready:
        raise StudioCompetitionError(
            "reviewer selection must target an integration-ready candidate"
        )

    required_suites = set(spec.required_verification_suites)
    verification_digests = tuple(
        sorted(
            item.evidence_sha256
            for item in verifications
            if item.candidate_id == candidate.candidate_id
            and item.head_sha == candidate.head_sha
            and item.suite_id in required_suites
            and item.outcome == VerificationOutcome.PASSED
        )
    )
    critique_digests = tuple(
        sorted(
            item.evidence_sha256
            for item in critiques
            if item.target_candidate_id == candidate.candidate_id
            and item.target_head_sha == candidate.head_sha
        )
    )
    return IntegrationPlan(
        reviewer_id=selection.reviewer_id,
        candidate_id=candidate.candidate_id,
        producer_id=candidate.producer_id,
        branch=candidate.branch,
        base_sha=candidate.base_sha,
        head_sha=candidate.head_sha,
        source_sha256=candidate.source_sha256,
        verification_evidence_sha256s=verification_digests,
        critique_evidence_sha256s=critique_digests,
    )


def _reject_unknown_evidence(
    candidates: dict[str, StudioCandidate],
    verifications: tuple[VerificationEvidence, ...],
    critiques: tuple[CritiqueEvidence, ...],
) -> None:
    known = set(candidates)
    for item in verifications:
        if item.candidate_id not in known:
            raise StudioCompetitionError(
                f"verification references unknown candidate: {item.candidate_id}"
            )
    for item in critiques:
        if item.target_candidate_id not in known:
            raise StudioCompetitionError(
                f"critique references unknown candidate: {item.target_candidate_id}"
            )


def _materialize(
    values: Iterable[object],
    expected_type: type,
    field: str,
    *,
    allow_empty: bool = False,
) -> tuple:
    if isinstance(values, (str, bytes)):
        raise StudioCompetitionError(f"{field} must be an iterable of objects")
    try:
        material = tuple(values)
    except TypeError as exc:
        raise StudioCompetitionError(
            f"{field} must be an iterable of objects"
        ) from exc
    if not material and not allow_empty:
        raise StudioCompetitionError(f"{field} must not be empty")
    if any(not isinstance(item, expected_type) for item in material):
        raise StudioCompetitionError(
            f"{field} must contain {expected_type.__name__} values"
        )
    return material


def _token(value: str, field: str) -> str:
    if not isinstance(value, str) or not _TOKEN_RE.fullmatch(value):
        raise StudioCompetitionError(f"{field} must be a valid logical token")
    return value


def _branch(value: str) -> str:
    if (
        not isinstance(value, str)
        or not _BRANCH_RE.fullmatch(value)
        or ".." in value
        or "//" in value
        or value.endswith(("/", "."))
    ):
        raise StudioCompetitionError("branch must be a safe logical Git branch name")
    return value


def _sha(value: str, field: str) -> str:
    if not isinstance(value, str) or not _SHA_RE.fullmatch(value):
        raise StudioCompetitionError(f"{field} must be a lowercase 40-char Git SHA")
    return value


def _digest(value: str, field: str) -> str:
    if not isinstance(value, str) or not _DIGEST_RE.fullmatch(value):
        raise StudioCompetitionError(f"{field} must be a lowercase SHA-256 digest")
    return value


def _sorted_tokens(
    values: tuple[str, ...], field: str, *, allow_empty: bool
) -> tuple[str, ...]:
    if not isinstance(values, tuple):
        raise StudioCompetitionError(f"{field} must be a tuple")
    if not values and not allow_empty:
        raise StudioCompetitionError(f"{field} must not be empty")
    normalized = tuple(_token(value, field) for value in values)
    if tuple(sorted(set(normalized))) != normalized:
        raise StudioCompetitionError(f"{field} must be sorted and unique")
    return normalized


def _sorted_digests(values: tuple[str, ...], field: str) -> tuple[str, ...]:
    if not isinstance(values, tuple):
        raise StudioCompetitionError(f"{field} must be a tuple")
    normalized = tuple(_digest(value, field) for value in values)
    if tuple(sorted(normalized)) != normalized:
        raise StudioCompetitionError(f"{field} must be sorted")
    return normalized
