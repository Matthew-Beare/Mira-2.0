"""Deterministic user-facing lifecycle surface for MIRA Studio.

This module composes already-reviewed Studio evidence into truthful product state.
It does not invoke models, create branches, choose providers, call source/share
adapters, install imports, activate behavior, or infer approval. Execution remains
owned by the lower-level Studio activation and feature-share boundaries.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from hashlib import sha256
import json
import re
from typing import Any, Iterable, Mapping

from .feature_share import ImportInspection, inspect_feature_share_import
from .studio_activation import (
    MutationDisposition,
    StudioActivationReceipt,
    StudioExecutionStatus,
    StudioRollbackReceipt,
)
from .studio_competition import (
    StudioActivationApproval,
    StudioActivationPlan,
    StudioChangeContract,
    StudioChangeKind,
    StudioCompetitionDecision,
    StudioPreviewEvidence,
    StudioRollbackAnchor,
    StudioStagedChangeDecision,
    StudioTestEvidence,
    evaluate_staged_change,
)


_TOKEN_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,255}$")
_FEATURE_ID_RE = re.compile(r"^[A-Z][A-Z0-9-]{1,79}$")
_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
_DIGEST_RE = re.compile(r"^[0-9a-f]{64}$")
_MAX_OBJECTIVE_LENGTH = 2000


class StudioSurfaceError(ValueError):
    """Raised when Studio surface material is malformed or contradictory."""


class StudioSurfacePhase(str, Enum):
    DRAFT = "draft"
    REVIEW_BLOCKED = "review_blocked"
    AWAITING_APPROVAL = "awaiting_approval"
    READY_TO_ACTIVATE = "ready_to_activate"
    ACTIVATION_BLOCKED = "activation_blocked"
    ACTIVATION_RECOVERY_REQUIRED = "activation_recovery_required"
    ACTIVE = "active"
    ROLLBACK_BLOCKED = "rollback_blocked"
    ROLLBACK_RECOVERY_REQUIRED = "rollback_recovery_required"
    ROLLED_BACK = "rolled_back"
    IMPORT_REVIEW_REQUIRED = "import_review_required"
    IMPORT_BLOCKED = "import_blocked"


class StudioNextAction(str, Enum):
    PROVIDE_REVIEW_EVIDENCE = "provide_review_evidence"
    RESOLVE_REVIEW_BLOCKERS = "resolve_review_blockers"
    REVIEW_AND_APPROVE = "review_and_approve"
    ACTIVATE_APPROVED_CHANGE = "activate_approved_change"
    RESOLVE_ACTIVATION_BLOCKER = "resolve_activation_blocker"
    RECONCILE_ACTIVATION_STATE = "reconcile_activation_state"
    RESOLVE_ROLLBACK_BLOCKER = "resolve_rollback_blocker"
    RECONCILE_ROLLBACK_STATE = "reconcile_rollback_state"
    REVIEW_IMPORT = "review_import"
    RESOLVE_IMPORT_BLOCKERS = "resolve_import_blockers"
    NONE_REQUIRED = "none_required"


@dataclass(frozen=True)
class StudioSession:
    """One bounded user-visible Studio change request."""

    session_id: str
    packet_id: str
    work_id: str
    change_id: str
    kind: StudioChangeKind
    objective: str
    feature_ids: tuple[str, ...]
    dependency_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for field, value in (
            ("session_id", self.session_id),
            ("packet_id", self.packet_id),
            ("work_id", self.work_id),
            ("change_id", self.change_id),
        ):
            _token(value, field)
        if not isinstance(self.kind, StudioChangeKind):
            raise StudioSurfaceError("kind must be a StudioChangeKind")
        _objective(self.objective)
        _feature_ids(self.feature_ids, "feature_ids", required=True)
        _feature_ids(self.dependency_ids, "dependency_ids", required=False)
        if set(self.feature_ids) & set(self.dependency_ids):
            raise StudioSurfaceError(
                "feature_ids and dependency_ids must describe distinct roles"
            )


@dataclass(frozen=True)
class StudioSurface:
    """Pure projection of one local Studio change's user-visible lifecycle state."""

    session_id: str
    packet_id: str
    work_id: str
    change_id: str
    kind: StudioChangeKind
    objective: str
    phase: StudioSurfacePhase
    next_action: StudioNextAction
    proposed_sha: str | None
    source_sha256: str | None
    preview_sha256: str | None
    review_ready: bool
    activation_approved: bool
    activation_verified: bool
    rollback_available: bool
    share_review_available: bool
    blockers: tuple[str, ...]
    verified_suite_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        for field, value in (
            ("session_id", self.session_id),
            ("packet_id", self.packet_id),
            ("work_id", self.work_id),
            ("change_id", self.change_id),
        ):
            _token(value, field)
        if not isinstance(self.kind, StudioChangeKind):
            raise StudioSurfaceError("kind must be a StudioChangeKind")
        _objective(self.objective)
        if not isinstance(self.phase, StudioSurfacePhase):
            raise StudioSurfaceError("phase must be a StudioSurfacePhase")
        if not isinstance(self.next_action, StudioNextAction):
            raise StudioSurfaceError("next_action must be a StudioNextAction")
        _optional_sha(self.proposed_sha, "proposed_sha")
        _optional_digest(self.source_sha256, "source_sha256")
        _optional_digest(self.preview_sha256, "preview_sha256")
        for field, value in (
            ("review_ready", self.review_ready),
            ("activation_approved", self.activation_approved),
            ("activation_verified", self.activation_verified),
            ("rollback_available", self.rollback_available),
            ("share_review_available", self.share_review_available),
        ):
            if not isinstance(value, bool):
                raise StudioSurfaceError(f"{field} must be boolean")
        _sorted_tokens(self.blockers, "blockers")
        _sorted_tokens(self.verified_suite_ids, "verified_suite_ids")
        if self.activation_approved and not self.review_ready:
            raise StudioSurfaceError("activation approval requires review-ready evidence")
        if self.activation_verified and not self.activation_approved:
            raise StudioSurfaceError("verified activation requires explicit approval")
        if self.rollback_available and not self.activation_verified:
            raise StudioSurfaceError("rollback availability requires verified activation")
        if self.share_review_available and not self.activation_verified:
            raise StudioSurfaceError("share review requires verified active source")

    @property
    def surface_sha256(self) -> str:
        return _projection_digest(
            {
                "session_id": self.session_id,
                "packet_id": self.packet_id,
                "work_id": self.work_id,
                "change_id": self.change_id,
                "kind": self.kind.value,
                "objective": self.objective,
                "phase": self.phase.value,
                "next_action": self.next_action.value,
                "proposed_sha": self.proposed_sha,
                "source_sha256": self.source_sha256,
                "preview_sha256": self.preview_sha256,
                "review_ready": self.review_ready,
                "activation_approved": self.activation_approved,
                "activation_verified": self.activation_verified,
                "rollback_available": self.rollback_available,
                "share_review_available": self.share_review_available,
                "blockers": list(self.blockers),
                "verified_suite_ids": list(self.verified_suite_ids),
            }
        )


@dataclass(frozen=True)
class StudioReviewResult:
    """Reviewed staged-change evidence plus its user-facing projection."""

    session: StudioSession
    contract: StudioChangeContract
    decision: StudioStagedChangeDecision
    surface: StudioSurface

    def __post_init__(self) -> None:
        if not isinstance(self.session, StudioSession):
            raise StudioSurfaceError("session must be a StudioSession")
        if not isinstance(self.contract, StudioChangeContract):
            raise StudioSurfaceError("contract must be a StudioChangeContract")
        if not isinstance(self.decision, StudioStagedChangeDecision):
            raise StudioSurfaceError("decision must be a StudioStagedChangeDecision")
        if not isinstance(self.surface, StudioSurface):
            raise StudioSurfaceError("surface must be a StudioSurface")
        _require_session_contract(self.session, self.contract)
        if self.decision.change_id != self.contract.change_id:
            raise StudioSurfaceError("decision change_id does not match contract")
        if self.decision.proposed_sha != self.contract.proposed_sha:
            raise StudioSurfaceError("decision proposed_sha does not match contract")
        if self.surface.session_id != self.session.session_id:
            raise StudioSurfaceError("surface session_id does not match review session")
        if self.surface.surface_sha256 != _surface_from_decision(
            self.session, self.contract, self.decision, self.surface.preview_sha256
        ).surface_sha256:
            raise StudioSurfaceError("surface does not match staged-change decision")

    @property
    def activation_plan(self) -> StudioActivationPlan | None:
        return self.decision.activation_plan


@dataclass(frozen=True)
class StudioImportSurface:
    """Inert review projection for one sanitized imported feature package."""

    package_id: str
    phase: StudioSurfacePhase
    next_action: StudioNextAction
    compatible: bool
    missing_dependencies: tuple[str, ...]
    already_present_features: tuple[str, ...]
    ready_for_review: bool
    activation_authorized: bool = False
    source_mutation_authorized: bool = False
    install_authorized: bool = False

    def __post_init__(self) -> None:
        _digest(self.package_id, "package_id")
        if self.phase not in {
            StudioSurfacePhase.IMPORT_REVIEW_REQUIRED,
            StudioSurfacePhase.IMPORT_BLOCKED,
        }:
            raise StudioSurfaceError("import surface must use an import phase")
        if self.next_action not in {
            StudioNextAction.REVIEW_IMPORT,
            StudioNextAction.RESOLVE_IMPORT_BLOCKERS,
        }:
            raise StudioSurfaceError("import surface has invalid next action")
        for field, value in (
            ("compatible", self.compatible),
            ("ready_for_review", self.ready_for_review),
            ("activation_authorized", self.activation_authorized),
            ("source_mutation_authorized", self.source_mutation_authorized),
            ("install_authorized", self.install_authorized),
        ):
            if not isinstance(value, bool):
                raise StudioSurfaceError(f"{field} must be boolean")
        _feature_ids(
            self.missing_dependencies, "missing_dependencies", required=False
        )
        _feature_ids(
            self.already_present_features,
            "already_present_features",
            required=False,
        )
        if (
            self.activation_authorized
            or self.source_mutation_authorized
            or self.install_authorized
        ):
            raise StudioSurfaceError("import review cannot carry execution authority")
        expected_ready = self.compatible and not self.missing_dependencies
        if self.ready_for_review != expected_ready:
            raise StudioSurfaceError(
                "ready_for_review must reflect compatibility and dependencies"
            )

    @property
    def surface_sha256(self) -> str:
        return _projection_digest(
            {
                "package_id": self.package_id,
                "phase": self.phase.value,
                "next_action": self.next_action.value,
                "compatible": self.compatible,
                "missing_dependencies": list(self.missing_dependencies),
                "already_present_features": list(self.already_present_features),
                "ready_for_review": self.ready_for_review,
                "activation_authorized": self.activation_authorized,
                "source_mutation_authorized": self.source_mutation_authorized,
                "install_authorized": self.install_authorized,
            }
        )


def project_studio_draft(session: StudioSession) -> StudioSurface:
    """Project a newly stated Studio intent before reviewed implementation evidence."""

    if not isinstance(session, StudioSession):
        raise StudioSurfaceError("session must be a StudioSession")
    return StudioSurface(
        session_id=session.session_id,
        packet_id=session.packet_id,
        work_id=session.work_id,
        change_id=session.change_id,
        kind=session.kind,
        objective=session.objective,
        phase=StudioSurfacePhase.DRAFT,
        next_action=StudioNextAction.PROVIDE_REVIEW_EVIDENCE,
        proposed_sha=None,
        source_sha256=None,
        preview_sha256=None,
        review_ready=False,
        activation_approved=False,
        activation_verified=False,
        rollback_available=False,
        share_review_available=False,
        blockers=(),
        verified_suite_ids=(),
    )


def review_studio_change(
    session: StudioSession,
    competition_decision: StudioCompetitionDecision,
    contract: StudioChangeContract,
    preview: StudioPreviewEvidence,
    tests: Iterable[StudioTestEvidence],
    rollback: StudioRollbackAnchor | None,
    *,
    approval: StudioActivationApproval | None = None,
) -> StudioReviewResult:
    """Evaluate one reviewed candidate and project its next user-visible action."""

    if not isinstance(session, StudioSession):
        raise StudioSurfaceError("session must be a StudioSession")
    _require_session_contract(session, contract)
    if not isinstance(preview, StudioPreviewEvidence):
        raise StudioSurfaceError("preview must be StudioPreviewEvidence")

    decision = evaluate_staged_change(
        competition_decision,
        contract,
        preview,
        tests,
        rollback,
        approval=approval,
    )
    surface = _surface_from_decision(
        session,
        contract,
        decision,
        preview.preview_sha256,
    )
    return StudioReviewResult(
        session=session,
        contract=contract,
        decision=decision,
        surface=surface,
    )


def project_activation_receipt(
    review: StudioReviewResult,
    receipt: StudioActivationReceipt,
) -> StudioSurface:
    """Project verified activation execution evidence without executing a mutation."""

    if not isinstance(review, StudioReviewResult):
        raise StudioSurfaceError("review must be a StudioReviewResult")
    if not isinstance(receipt, StudioActivationReceipt):
        raise StudioSurfaceError("receipt must be a StudioActivationReceipt")
    plan = review.activation_plan
    if plan is None:
        raise StudioSurfaceError("activation receipt requires an approval-bound plan")
    _require_activation_receipt(plan, receipt)

    if receipt.status in {
        StudioExecutionStatus.APPLIED,
        StudioExecutionStatus.ALREADY_APPLIED,
    }:
        phase = StudioSurfacePhase.ACTIVE
        action = StudioNextAction.NONE_REQUIRED
        blockers: tuple[str, ...] = ()
        verified = True
        rollback_available = True
        share_review_available = True
    elif receipt.status == StudioExecutionStatus.BLOCKED:
        phase = StudioSurfacePhase.ACTIVATION_BLOCKED
        action = StudioNextAction.RESOLVE_ACTIVATION_BLOCKER
        blockers = (f"activation:{receipt.reason_code}",)
        verified = False
        rollback_available = False
        share_review_available = False
    elif receipt.status == StudioExecutionStatus.RECOVERY_REQUIRED:
        phase = StudioSurfacePhase.ACTIVATION_RECOVERY_REQUIRED
        action = StudioNextAction.RECONCILE_ACTIVATION_STATE
        blockers = (f"activation:{receipt.reason_code}",)
        verified = False
        rollback_available = False
        share_review_available = False
    else:
        raise StudioSurfaceError("activation receipt carries non-activation status")

    return _surface(
        review,
        phase=phase,
        next_action=action,
        activation_verified=verified,
        rollback_available=rollback_available,
        share_review_available=share_review_available,
        blockers=blockers,
    )


def project_rollback_receipt(
    review: StudioReviewResult,
    activation_receipt: StudioActivationReceipt,
    rollback_receipt: StudioRollbackReceipt,
) -> StudioSurface:
    """Project explicit rollback evidence after a verified activation."""

    if not isinstance(review, StudioReviewResult):
        raise StudioSurfaceError("review must be a StudioReviewResult")
    if not isinstance(activation_receipt, StudioActivationReceipt):
        raise StudioSurfaceError(
            "activation_receipt must be a StudioActivationReceipt"
        )
    if not isinstance(rollback_receipt, StudioRollbackReceipt):
        raise StudioSurfaceError("rollback_receipt must be a StudioRollbackReceipt")
    plan = review.activation_plan
    if plan is None:
        raise StudioSurfaceError("rollback projection requires an approval-bound plan")
    _require_activation_receipt(plan, activation_receipt)
    if activation_receipt.status not in {
        StudioExecutionStatus.APPLIED,
        StudioExecutionStatus.ALREADY_APPLIED,
    }:
        raise StudioSurfaceError("rollback requires a verified successful activation")
    _require_rollback_receipt(plan, activation_receipt, rollback_receipt)

    if rollback_receipt.status == StudioExecutionStatus.ROLLED_BACK:
        return _surface(
            review,
            phase=StudioSurfacePhase.ROLLED_BACK,
            next_action=StudioNextAction.NONE_REQUIRED,
            activation_verified=False,
            rollback_available=False,
            share_review_available=False,
            blockers=(),
        )
    if rollback_receipt.status == StudioExecutionStatus.BLOCKED:
        return _surface(
            review,
            phase=StudioSurfacePhase.ROLLBACK_BLOCKED,
            next_action=StudioNextAction.RESOLVE_ROLLBACK_BLOCKER,
            activation_verified=True,
            rollback_available=True,
            share_review_available=False,
            blockers=(f"rollback:{rollback_receipt.reason_code}",),
        )
    if rollback_receipt.status == StudioExecutionStatus.RECOVERY_REQUIRED:
        return _surface(
            review,
            phase=StudioSurfacePhase.ROLLBACK_RECOVERY_REQUIRED,
            next_action=StudioNextAction.RECONCILE_ROLLBACK_STATE,
            activation_verified=False,
            rollback_available=False,
            share_review_available=False,
            blockers=(f"rollback:{rollback_receipt.reason_code}",),
        )
    raise StudioSurfaceError("rollback receipt carries non-rollback status")


def inspect_studio_import(
    material: Mapping[str, Any],
    *,
    runtime_schema: int,
    available_feature_ids: Iterable[str],
) -> StudioImportSurface:
    """Inspect sanitized shared material as inert review-only input."""

    inspection = inspect_feature_share_import(
        material,
        runtime_schema=runtime_schema,
        available_feature_ids=available_feature_ids,
    )
    _require_inert_import(inspection)
    if inspection.ready_for_review:
        phase = StudioSurfacePhase.IMPORT_REVIEW_REQUIRED
        action = StudioNextAction.REVIEW_IMPORT
    else:
        phase = StudioSurfacePhase.IMPORT_BLOCKED
        action = StudioNextAction.RESOLVE_IMPORT_BLOCKERS
    return StudioImportSurface(
        package_id=inspection.package_id,
        phase=phase,
        next_action=action,
        compatible=inspection.compatible,
        missing_dependencies=inspection.missing_dependencies,
        already_present_features=inspection.already_present_features,
        ready_for_review=inspection.ready_for_review,
        activation_authorized=False,
        source_mutation_authorized=False,
        install_authorized=False,
    )


def _surface_from_decision(
    session: StudioSession,
    contract: StudioChangeContract,
    decision: StudioStagedChangeDecision,
    preview_sha256: str | None,
) -> StudioSurface:
    if decision.blockers:
        phase = StudioSurfacePhase.REVIEW_BLOCKED
        action = StudioNextAction.RESOLVE_REVIEW_BLOCKERS
        approved = False
    elif decision.activation_plan is None:
        phase = StudioSurfacePhase.AWAITING_APPROVAL
        action = StudioNextAction.REVIEW_AND_APPROVE
        approved = False
    else:
        phase = StudioSurfacePhase.READY_TO_ACTIVATE
        action = StudioNextAction.ACTIVATE_APPROVED_CHANGE
        approved = True
    return StudioSurface(
        session_id=session.session_id,
        packet_id=session.packet_id,
        work_id=session.work_id,
        change_id=session.change_id,
        kind=session.kind,
        objective=session.objective,
        phase=phase,
        next_action=action,
        proposed_sha=contract.proposed_sha,
        source_sha256=contract.source_sha256,
        preview_sha256=preview_sha256,
        review_ready=decision.review_ready,
        activation_approved=approved,
        activation_verified=False,
        rollback_available=False,
        share_review_available=False,
        blockers=decision.blockers,
        verified_suite_ids=decision.verified_suite_ids,
    )


def _surface(
    review: StudioReviewResult,
    *,
    phase: StudioSurfacePhase,
    next_action: StudioNextAction,
    activation_verified: bool,
    rollback_available: bool,
    share_review_available: bool,
    blockers: tuple[str, ...],
) -> StudioSurface:
    decision = review.decision
    plan = decision.activation_plan
    if plan is None:
        raise StudioSurfaceError("execution projection requires activation plan")
    return StudioSurface(
        session_id=review.session.session_id,
        packet_id=review.session.packet_id,
        work_id=review.session.work_id,
        change_id=review.session.change_id,
        kind=review.session.kind,
        objective=review.session.objective,
        phase=phase,
        next_action=next_action,
        proposed_sha=review.contract.proposed_sha,
        source_sha256=review.contract.source_sha256,
        preview_sha256=plan.preview_sha256,
        review_ready=True,
        activation_approved=True,
        activation_verified=activation_verified,
        rollback_available=rollback_available,
        share_review_available=share_review_available,
        blockers=tuple(sorted(blockers)),
        verified_suite_ids=decision.verified_suite_ids,
    )


def _require_session_contract(
    session: StudioSession,
    contract: StudioChangeContract,
) -> None:
    if not isinstance(contract, StudioChangeContract):
        raise StudioSurfaceError("contract must be a StudioChangeContract")
    if session.packet_id != contract.packet_id:
        raise StudioSurfaceError("session packet_id does not match contract")
    if session.work_id != contract.work_id:
        raise StudioSurfaceError("session work_id does not match contract")
    if session.change_id != contract.change_id:
        raise StudioSurfaceError("session change_id does not match contract")
    if session.kind != contract.kind:
        raise StudioSurfaceError("session change kind does not match contract")
    if session.feature_ids != contract.feature_ids:
        raise StudioSurfaceError("session feature_ids do not match contract")


def _require_activation_receipt(
    plan: StudioActivationPlan,
    receipt: StudioActivationReceipt,
) -> None:
    expected = (
        ("packet_id", receipt.packet_id, plan.packet_id),
        ("work_id", receipt.work_id, plan.work_id),
        ("change_id", receipt.change_id, plan.change_id),
        ("approver_id", receipt.approver_id, plan.approver_id),
        ("base_sha", receipt.base_sha, plan.base_sha),
        ("proposed_sha", receipt.proposed_sha, plan.proposed_sha),
        (
            "approved_source_sha256",
            receipt.approved_source_sha256,
            plan.source_sha256,
        ),
    )
    for field, actual, wanted in expected:
        if actual != wanted:
            raise StudioSurfaceError(
                f"activation receipt {field} does not match approved plan"
            )
    if (
        receipt.status in {
            StudioExecutionStatus.APPLIED,
            StudioExecutionStatus.ALREADY_APPLIED,
        }
        and receipt.mutation_disposition == MutationDisposition.UNKNOWN
    ):
        raise StudioSurfaceError("successful activation cannot have unknown outcome")


def _require_rollback_receipt(
    plan: StudioActivationPlan,
    activation: StudioActivationReceipt,
    rollback: StudioRollbackReceipt,
) -> None:
    for field, actual, wanted in (
        ("packet_id", rollback.packet_id, plan.packet_id),
        ("work_id", rollback.work_id, plan.work_id),
        ("change_id", rollback.change_id, plan.change_id),
        ("target", rollback.target, activation.target),
        (
            "from_revision_sha",
            rollback.from_revision_sha,
            activation.applied_revision_sha,
        ),
        ("rollback_revision_id", rollback.rollback_revision_id, plan.rollback_revision_id),
        (
            "rollback_state_sha256",
            rollback.rollback_state_sha256,
            plan.rollback_state_sha256,
        ),
    ):
        if actual != wanted:
            raise StudioSurfaceError(
                f"rollback receipt {field} does not match approved activation"
            )


def _require_inert_import(inspection: ImportInspection) -> None:
    if not isinstance(inspection, ImportInspection):
        raise StudioSurfaceError("import inspection must be ImportInspection")
    if (
        inspection.activation_authorized
        or inspection.source_mutation_authorized
        or inspection.install_authorized
    ):
        raise StudioSurfaceError("import inspection must remain inert")


def _token(value: str, field: str) -> str:
    if not isinstance(value, str) or not _TOKEN_RE.fullmatch(value):
        raise StudioSurfaceError(f"{field} must be a valid logical token")
    return value


def _objective(value: str) -> str:
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or len(value) > _MAX_OBJECTIVE_LENGTH
        or any(ord(char) < 32 and char not in "\n\t" for char in value)
    ):
        raise StudioSurfaceError("objective must be bounded, trimmed human-readable text")
    return value


def _feature_ids(
    values: tuple[str, ...],
    field: str,
    *,
    required: bool,
) -> tuple[str, ...]:
    if not isinstance(values, tuple):
        raise StudioSurfaceError(f"{field} must be a tuple")
    if required and not values:
        raise StudioSurfaceError(f"{field} must not be empty")
    for value in values:
        if not isinstance(value, str) or not _FEATURE_ID_RE.fullmatch(value):
            raise StudioSurfaceError(f"{field} must contain canonical MIRA IDs")
    if tuple(sorted(set(values))) != values:
        raise StudioSurfaceError(f"{field} must be sorted and unique")
    return values


def _sorted_tokens(values: tuple[str, ...], field: str) -> tuple[str, ...]:
    if not isinstance(values, tuple):
        raise StudioSurfaceError(f"{field} must be a tuple")
    normalized = tuple(_token(value, field) for value in values)
    if tuple(sorted(set(normalized))) != normalized:
        raise StudioSurfaceError(f"{field} must be sorted and unique")
    return normalized


def _optional_sha(value: str | None, field: str) -> None:
    if value is not None and (not isinstance(value, str) or not _SHA_RE.fullmatch(value)):
        raise StudioSurfaceError(f"{field} must be a lowercase 40-char Git SHA or None")


def _optional_digest(value: str | None, field: str) -> None:
    if value is not None:
        _digest(value, field)


def _digest(value: str, field: str) -> str:
    if not isinstance(value, str) or not _DIGEST_RE.fullmatch(value):
        raise StudioSurfaceError(f"{field} must be a lowercase SHA-256 digest")
    return value


def _projection_digest(material: Mapping[str, object]) -> str:
    encoded = json.dumps(
        material,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return sha256(encoded).hexdigest()
