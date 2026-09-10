"""Fail-closed execution boundary for explicitly approved MIRA Studio changes.

The module composes M2-M1-032 approval evidence with SOURCE-001 capability truth.
Provider/source mutation is injected through ``StudioSourceAdapter``. Core logic
never chooses a source lane, constructs provider commands, stores credentials, or
silently activates/rolls back a change.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from hashlib import sha256
import json
import re
from typing import Protocol

from .service_state import CapabilityEvaluation, CapabilityGate
from .studio_competition import StudioActivationPlan

_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
_DIGEST_RE = re.compile(r"^[0-9a-f]{64}$")
_TOKEN_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,255}$")


class StudioActivationExecutionError(Exception):
    """Raised when execution-contract material is malformed or contradictory."""


class StudioExecutionStatus(str, Enum):
    APPLIED = "applied"
    ALREADY_APPLIED = "already_applied"
    ROLLED_BACK = "rolled_back"
    BLOCKED = "blocked"
    RECOVERY_REQUIRED = "recovery_required"


class MutationDisposition(str, Enum):
    NOT_ATTEMPTED = "not_attempted"
    PERFORMED = "performed"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class StudioSourceTarget:
    provider_id: str
    service_id: str
    target_ref: str

    def __post_init__(self) -> None:
        _token(self.provider_id, "provider_id")
        _token(self.service_id, "service_id")
        _token(self.target_ref, "target_ref")


@dataclass(frozen=True)
class StudioSourceState:
    revision_sha: str
    source_sha256: str
    state_sha256: str

    def __post_init__(self) -> None:
        _git_sha(self.revision_sha, "revision_sha")
        _digest(self.source_sha256, "source_sha256")
        _digest(self.state_sha256, "state_sha256")


@dataclass(frozen=True)
class StudioSourceMutationResult:
    revision_sha: str
    source_sha256: str
    state_sha256: str
    evidence_sha256: str

    def __post_init__(self) -> None:
        _git_sha(self.revision_sha, "revision_sha")
        _digest(self.source_sha256, "source_sha256")
        _digest(self.state_sha256, "state_sha256")
        _digest(self.evidence_sha256, "evidence_sha256")


class StudioSourceAdapter(Protocol):
    """Injected source-lane adapter. Core passes only approved, bounded material."""

    def read_state(self, target: StudioSourceTarget) -> StudioSourceState: ...

    def apply_activation(
        self,
        target: StudioSourceTarget,
        *,
        change_id: str,
        expected_revision_sha: str,
        proposed_revision_sha: str,
        proposed_source_sha256: str,
    ) -> StudioSourceMutationResult: ...

    def apply_rollback(
        self,
        target: StudioSourceTarget,
        *,
        change_id: str,
        expected_revision_sha: str,
        prior_revision_id: str,
        prior_state_sha256: str,
    ) -> StudioSourceMutationResult: ...


@dataclass(frozen=True)
class StudioActivationReceipt:
    status: StudioExecutionStatus
    reason_code: str
    packet_id: str
    work_id: str
    change_id: str
    approver_id: str
    target: StudioSourceTarget
    base_sha: str
    proposed_sha: str
    approved_source_sha256: str
    applied_revision_sha: str | None
    applied_state_sha256: str | None
    adapter_evidence_sha256: str | None
    mutation_disposition: MutationDisposition

    def __post_init__(self) -> None:
        if not isinstance(self.status, StudioExecutionStatus):
            raise StudioActivationExecutionError("invalid activation status")
        for field, value in (
            ("reason_code", self.reason_code),
            ("packet_id", self.packet_id),
            ("work_id", self.work_id),
            ("change_id", self.change_id),
            ("approver_id", self.approver_id),
        ):
            _token(value, field)
        if not isinstance(self.target, StudioSourceTarget):
            raise StudioActivationExecutionError("target must be StudioSourceTarget")
        _git_sha(self.base_sha, "base_sha")
        _git_sha(self.proposed_sha, "proposed_sha")
        _digest(self.approved_source_sha256, "approved_source_sha256")
        _optional_git_sha(self.applied_revision_sha, "applied_revision_sha")
        _optional_digest(self.applied_state_sha256, "applied_state_sha256")
        _optional_digest(self.adapter_evidence_sha256, "adapter_evidence_sha256")
        if not isinstance(self.mutation_disposition, MutationDisposition):
            raise StudioActivationExecutionError("invalid mutation_disposition")
        self._validate_state_machine()

    def _validate_state_machine(self) -> None:
        applied = (
            self.applied_revision_sha is not None
            and self.applied_state_sha256 is not None
        )
        evidence = self.adapter_evidence_sha256 is not None
        if self.status == StudioExecutionStatus.APPLIED:
            if (
                self.mutation_disposition != MutationDisposition.PERFORMED
                or not applied
                or not evidence
            ):
                raise StudioActivationExecutionError(
                    "APPLIED requires performed mutation evidence"
                )
        elif self.status == StudioExecutionStatus.ALREADY_APPLIED:
            if (
                self.mutation_disposition != MutationDisposition.NOT_ATTEMPTED
                or not applied
            ):
                raise StudioActivationExecutionError(
                    "ALREADY_APPLIED requires verified zero-write state"
                )
        elif self.status == StudioExecutionStatus.BLOCKED:
            if (
                self.mutation_disposition != MutationDisposition.NOT_ATTEMPTED
                or applied
                or evidence
            ):
                raise StudioActivationExecutionError(
                    "BLOCKED cannot carry mutation evidence"
                )
        elif self.status == StudioExecutionStatus.RECOVERY_REQUIRED:
            if self.mutation_disposition == MutationDisposition.NOT_ATTEMPTED:
                raise StudioActivationExecutionError(
                    "RECOVERY_REQUIRED requires performed or unknown mutation"
                )
            if (
                self.mutation_disposition == MutationDisposition.PERFORMED
                and (not applied or not evidence)
            ):
                raise StudioActivationExecutionError(
                    "performed recovery requires mutation evidence"
                )
        else:
            raise StudioActivationExecutionError(
                "rollback-only status in activation receipt"
            )

    @property
    def receipt_sha256(self) -> str:
        return _receipt_digest(
            {
                "status": self.status.value,
                "reason_code": self.reason_code,
                "packet_id": self.packet_id,
                "work_id": self.work_id,
                "change_id": self.change_id,
                "approver_id": self.approver_id,
                "target": _target_payload(self.target),
                "base_sha": self.base_sha,
                "proposed_sha": self.proposed_sha,
                "approved_source_sha256": self.approved_source_sha256,
                "applied_revision_sha": self.applied_revision_sha,
                "applied_state_sha256": self.applied_state_sha256,
                "adapter_evidence_sha256": self.adapter_evidence_sha256,
                "mutation_disposition": self.mutation_disposition.value,
            }
        )


@dataclass(frozen=True)
class StudioRollbackReceipt:
    status: StudioExecutionStatus
    reason_code: str
    packet_id: str
    work_id: str
    change_id: str
    target: StudioSourceTarget
    from_revision_sha: str
    rollback_revision_id: str
    rollback_state_sha256: str
    resulting_revision_sha: str | None
    adapter_evidence_sha256: str | None
    mutation_disposition: MutationDisposition

    def __post_init__(self) -> None:
        if self.status not in {
            StudioExecutionStatus.ROLLED_BACK,
            StudioExecutionStatus.BLOCKED,
            StudioExecutionStatus.RECOVERY_REQUIRED,
        }:
            raise StudioActivationExecutionError("invalid rollback status")
        for field, value in (
            ("reason_code", self.reason_code),
            ("packet_id", self.packet_id),
            ("work_id", self.work_id),
            ("change_id", self.change_id),
            ("rollback_revision_id", self.rollback_revision_id),
        ):
            _token(value, field)
        if not isinstance(self.target, StudioSourceTarget):
            raise StudioActivationExecutionError("target must be StudioSourceTarget")
        _git_sha(self.from_revision_sha, "from_revision_sha")
        _digest(self.rollback_state_sha256, "rollback_state_sha256")
        _optional_git_sha(self.resulting_revision_sha, "resulting_revision_sha")
        _optional_digest(self.adapter_evidence_sha256, "adapter_evidence_sha256")
        if not isinstance(self.mutation_disposition, MutationDisposition):
            raise StudioActivationExecutionError("invalid mutation_disposition")
        result = self.resulting_revision_sha is not None
        evidence = self.adapter_evidence_sha256 is not None
        if self.status == StudioExecutionStatus.ROLLED_BACK:
            if (
                self.mutation_disposition != MutationDisposition.PERFORMED
                or not result
                or not evidence
            ):
                raise StudioActivationExecutionError(
                    "ROLLED_BACK requires performed mutation evidence"
                )
        elif self.status == StudioExecutionStatus.BLOCKED:
            if (
                self.mutation_disposition != MutationDisposition.NOT_ATTEMPTED
                or result
                or evidence
            ):
                raise StudioActivationExecutionError(
                    "BLOCKED rollback cannot carry mutation evidence"
                )
        elif self.mutation_disposition == MutationDisposition.NOT_ATTEMPTED:
            raise StudioActivationExecutionError(
                "RECOVERY_REQUIRED rollback requires performed or unknown mutation"
            )
        elif (
            self.mutation_disposition == MutationDisposition.PERFORMED
            and (not result or not evidence)
        ):
            raise StudioActivationExecutionError(
                "performed rollback recovery requires mutation evidence"
            )

    @property
    def receipt_sha256(self) -> str:
        return _receipt_digest(
            {
                "status": self.status.value,
                "reason_code": self.reason_code,
                "packet_id": self.packet_id,
                "work_id": self.work_id,
                "change_id": self.change_id,
                "target": _target_payload(self.target),
                "from_revision_sha": self.from_revision_sha,
                "rollback_revision_id": self.rollback_revision_id,
                "rollback_state_sha256": self.rollback_state_sha256,
                "resulting_revision_sha": self.resulting_revision_sha,
                "adapter_evidence_sha256": self.adapter_evidence_sha256,
                "mutation_disposition": self.mutation_disposition.value,
            }
        )


def execute_studio_activation(
    plan: StudioActivationPlan,
    target: StudioSourceTarget,
    capability: CapabilityEvaluation,
    adapter: StudioSourceAdapter,
    *,
    prior_receipt: StudioActivationReceipt | None = None,
) -> StudioActivationReceipt:
    """Apply one approved Studio plan, succeeding only after exact remote readback."""

    _require_plan_target(plan, target)
    blocker = _capability_blocker(capability, target)
    if blocker:
        return _activation_receipt(
            plan,
            target,
            StudioExecutionStatus.BLOCKED,
            blocker,
            MutationDisposition.NOT_ATTEMPTED,
        )
    if prior_receipt is not None:
        _require_matching_receipt(prior_receipt, plan, target)

    try:
        current = adapter.read_state(target)
    except Exception:
        return _activation_receipt(
            plan,
            target,
            StudioExecutionStatus.BLOCKED,
            "preflight_read_failed",
            MutationDisposition.NOT_ATTEMPTED,
        )
    if not isinstance(current, StudioSourceState):
        return _activation_receipt(
            plan,
            target,
            StudioExecutionStatus.BLOCKED,
            "preflight_invalid_state",
            MutationDisposition.NOT_ATTEMPTED,
        )

    if prior_receipt is not None and _matches_prior_receipt(current, prior_receipt):
        return StudioActivationReceipt(
            status=StudioExecutionStatus.ALREADY_APPLIED,
            reason_code="verified_replay",
            packet_id=plan.packet_id,
            work_id=plan.work_id,
            change_id=plan.change_id,
            approver_id=plan.approver_id,
            target=target,
            base_sha=plan.base_sha,
            proposed_sha=plan.proposed_sha,
            approved_source_sha256=plan.source_sha256,
            applied_revision_sha=current.revision_sha,
            applied_state_sha256=current.state_sha256,
            adapter_evidence_sha256=prior_receipt.adapter_evidence_sha256,
            mutation_disposition=MutationDisposition.NOT_ATTEMPTED,
        )

    if current.revision_sha != plan.base_sha:
        return _activation_receipt(
            plan,
            target,
            StudioExecutionStatus.BLOCKED,
            "preflight_revision_mismatch",
            MutationDisposition.NOT_ATTEMPTED,
        )
    if current.state_sha256 != plan.rollback_state_sha256:
        return _activation_receipt(
            plan,
            target,
            StudioExecutionStatus.BLOCKED,
            "preflight_state_mismatch",
            MutationDisposition.NOT_ATTEMPTED,
        )

    try:
        mutation = adapter.apply_activation(
            target,
            change_id=plan.change_id,
            expected_revision_sha=current.revision_sha,
            proposed_revision_sha=plan.proposed_sha,
            proposed_source_sha256=plan.source_sha256,
        )
    except Exception:
        return _activation_receipt(
            plan,
            target,
            StudioExecutionStatus.RECOVERY_REQUIRED,
            "activation_write_outcome_unknown",
            MutationDisposition.UNKNOWN,
        )
    if not isinstance(mutation, StudioSourceMutationResult):
        return _activation_receipt(
            plan,
            target,
            StudioExecutionStatus.RECOVERY_REQUIRED,
            "activation_invalid_mutation_result",
            MutationDisposition.UNKNOWN,
        )
    if mutation.revision_sha == current.revision_sha:
        return _activation_receipt(
            plan,
            target,
            StudioExecutionStatus.RECOVERY_REQUIRED,
            "mutation_revision_unchanged",
            MutationDisposition.PERFORMED,
            mutation,
        )
    if mutation.source_sha256 != plan.source_sha256:
        return _activation_receipt(
            plan,
            target,
            StudioExecutionStatus.RECOVERY_REQUIRED,
            "mutation_source_mismatch",
            MutationDisposition.PERFORMED,
            mutation,
        )

    try:
        readback = adapter.read_state(target)
    except Exception:
        return _activation_receipt(
            plan,
            target,
            StudioExecutionStatus.RECOVERY_REQUIRED,
            "activation_readback_failed",
            MutationDisposition.PERFORMED,
            mutation,
        )
    if not isinstance(readback, StudioSourceState):
        return _activation_receipt(
            plan,
            target,
            StudioExecutionStatus.RECOVERY_REQUIRED,
            "activation_invalid_readback",
            MutationDisposition.PERFORMED,
            mutation,
        )
    if not _state_matches_mutation(readback, mutation):
        return _activation_receipt(
            plan,
            target,
            StudioExecutionStatus.RECOVERY_REQUIRED,
            "activation_readback_mismatch",
            MutationDisposition.PERFORMED,
            mutation,
        )

    return _activation_receipt(
        plan,
        target,
        StudioExecutionStatus.APPLIED,
        "applied_and_verified",
        MutationDisposition.PERFORMED,
        mutation,
    )


def execute_studio_rollback(
    plan: StudioActivationPlan,
    activation_receipt: StudioActivationReceipt,
    target: StudioSourceTarget,
    capability: CapabilityEvaluation,
    adapter: StudioSourceAdapter,
) -> StudioRollbackReceipt:
    """Explicitly roll back a verified activation to its recorded prior-state anchor."""

    _require_plan_target(plan, target)
    _require_matching_receipt(activation_receipt, plan, target)
    if activation_receipt.status not in {
        StudioExecutionStatus.APPLIED,
        StudioExecutionStatus.ALREADY_APPLIED,
    }:
        raise StudioActivationExecutionError(
            "rollback requires successful activation receipt"
        )
    assert activation_receipt.applied_revision_sha is not None
    assert activation_receipt.applied_state_sha256 is not None

    blocker = _capability_blocker(capability, target)
    if blocker:
        return _rollback_receipt(
            plan,
            activation_receipt,
            target,
            StudioExecutionStatus.BLOCKED,
            blocker,
            MutationDisposition.NOT_ATTEMPTED,
        )

    try:
        current = adapter.read_state(target)
    except Exception:
        return _rollback_receipt(
            plan,
            activation_receipt,
            target,
            StudioExecutionStatus.BLOCKED,
            "rollback_preflight_read_failed",
            MutationDisposition.NOT_ATTEMPTED,
        )
    if not isinstance(current, StudioSourceState):
        return _rollback_receipt(
            plan,
            activation_receipt,
            target,
            StudioExecutionStatus.BLOCKED,
            "rollback_preflight_invalid_state",
            MutationDisposition.NOT_ATTEMPTED,
        )
    if (
        current.revision_sha != activation_receipt.applied_revision_sha
        or current.source_sha256 != plan.source_sha256
        or current.state_sha256 != activation_receipt.applied_state_sha256
    ):
        return _rollback_receipt(
            plan,
            activation_receipt,
            target,
            StudioExecutionStatus.BLOCKED,
            "rollback_preflight_mismatch",
            MutationDisposition.NOT_ATTEMPTED,
        )

    try:
        mutation = adapter.apply_rollback(
            target,
            change_id=plan.change_id,
            expected_revision_sha=current.revision_sha,
            prior_revision_id=plan.rollback_revision_id,
            prior_state_sha256=plan.rollback_state_sha256,
        )
    except Exception:
        return _rollback_receipt(
            plan,
            activation_receipt,
            target,
            StudioExecutionStatus.RECOVERY_REQUIRED,
            "rollback_write_outcome_unknown",
            MutationDisposition.UNKNOWN,
        )
    if not isinstance(mutation, StudioSourceMutationResult):
        return _rollback_receipt(
            plan,
            activation_receipt,
            target,
            StudioExecutionStatus.RECOVERY_REQUIRED,
            "rollback_invalid_mutation_result",
            MutationDisposition.UNKNOWN,
        )
    if mutation.revision_sha == current.revision_sha:
        return _rollback_receipt(
            plan,
            activation_receipt,
            target,
            StudioExecutionStatus.RECOVERY_REQUIRED,
            "rollback_revision_unchanged",
            MutationDisposition.PERFORMED,
            mutation,
        )
    if mutation.state_sha256 != plan.rollback_state_sha256:
        return _rollback_receipt(
            plan,
            activation_receipt,
            target,
            StudioExecutionStatus.RECOVERY_REQUIRED,
            "rollback_state_mismatch",
            MutationDisposition.PERFORMED,
            mutation,
        )

    try:
        readback = adapter.read_state(target)
    except Exception:
        return _rollback_receipt(
            plan,
            activation_receipt,
            target,
            StudioExecutionStatus.RECOVERY_REQUIRED,
            "rollback_readback_failed",
            MutationDisposition.PERFORMED,
            mutation,
        )
    if not isinstance(readback, StudioSourceState):
        return _rollback_receipt(
            plan,
            activation_receipt,
            target,
            StudioExecutionStatus.RECOVERY_REQUIRED,
            "rollback_invalid_readback",
            MutationDisposition.PERFORMED,
            mutation,
        )
    if not _state_matches_mutation(readback, mutation):
        return _rollback_receipt(
            plan,
            activation_receipt,
            target,
            StudioExecutionStatus.RECOVERY_REQUIRED,
            "rollback_readback_mismatch",
            MutationDisposition.PERFORMED,
            mutation,
        )

    return _rollback_receipt(
        plan,
        activation_receipt,
        target,
        StudioExecutionStatus.ROLLED_BACK,
        "rolled_back_and_verified",
        MutationDisposition.PERFORMED,
        mutation,
    )


def _capability_blocker(
    capability: CapabilityEvaluation,
    target: StudioSourceTarget,
) -> str | None:
    if not isinstance(capability, CapabilityEvaluation):
        raise StudioActivationExecutionError(
            "capability must be CapabilityEvaluation"
        )
    if capability.provider_id != target.provider_id:
        return "capability_provider_mismatch"
    if capability.service_id != target.service_id:
        return "capability_service_mismatch"
    for gate in (
        CapabilityGate.READ,
        CapabilityGate.WRITE,
        CapabilityGate.REMOTE_READBACK,
    ):
        matches = tuple(
            decision for decision in capability.decisions if decision.gate == gate
        )
        if not matches:
            return f"capability_{gate.value}_missing"
        if len(matches) != 1:
            return f"capability_{gate.value}_ambiguous"
        if not matches[0].allowed:
            return f"capability_{gate.value}_{matches[0].reason_code}"
    if not capability.ready:
        return "capability_not_ready"
    return None


def _require_plan_target(
    plan: StudioActivationPlan,
    target: StudioSourceTarget,
) -> None:
    if not isinstance(plan, StudioActivationPlan):
        raise StudioActivationExecutionError("plan must be StudioActivationPlan")
    if not isinstance(target, StudioSourceTarget):
        raise StudioActivationExecutionError("target must be StudioSourceTarget")


def _require_matching_receipt(
    receipt: StudioActivationReceipt,
    plan: StudioActivationPlan,
    target: StudioSourceTarget,
) -> None:
    if not isinstance(receipt, StudioActivationReceipt):
        raise StudioActivationExecutionError(
            "prior receipt must be StudioActivationReceipt"
        )
    if (
        receipt.packet_id,
        receipt.work_id,
        receipt.change_id,
        receipt.approver_id,
        receipt.base_sha,
        receipt.proposed_sha,
        receipt.approved_source_sha256,
        receipt.target,
    ) != (
        plan.packet_id,
        plan.work_id,
        plan.change_id,
        plan.approver_id,
        plan.base_sha,
        plan.proposed_sha,
        plan.source_sha256,
        target,
    ):
        raise StudioActivationExecutionError(
            "activation receipt does not match plan and target"
        )


def _matches_prior_receipt(
    current: StudioSourceState,
    receipt: StudioActivationReceipt,
) -> bool:
    return (
        receipt.status
        in {StudioExecutionStatus.APPLIED, StudioExecutionStatus.ALREADY_APPLIED}
        and receipt.applied_revision_sha is not None
        and receipt.applied_state_sha256 is not None
        and current.revision_sha == receipt.applied_revision_sha
        and current.source_sha256 == receipt.approved_source_sha256
        and current.state_sha256 == receipt.applied_state_sha256
    )


def _state_matches_mutation(
    state: StudioSourceState,
    mutation: StudioSourceMutationResult,
) -> bool:
    return (
        state.revision_sha == mutation.revision_sha
        and state.source_sha256 == mutation.source_sha256
        and state.state_sha256 == mutation.state_sha256
    )


def _activation_receipt(
    plan: StudioActivationPlan,
    target: StudioSourceTarget,
    status: StudioExecutionStatus,
    reason: str,
    disposition: MutationDisposition,
    mutation: StudioSourceMutationResult | None = None,
) -> StudioActivationReceipt:
    return StudioActivationReceipt(
        status=status,
        reason_code=reason,
        packet_id=plan.packet_id,
        work_id=plan.work_id,
        change_id=plan.change_id,
        approver_id=plan.approver_id,
        target=target,
        base_sha=plan.base_sha,
        proposed_sha=plan.proposed_sha,
        approved_source_sha256=plan.source_sha256,
        applied_revision_sha=mutation.revision_sha if mutation else None,
        applied_state_sha256=mutation.state_sha256 if mutation else None,
        adapter_evidence_sha256=mutation.evidence_sha256 if mutation else None,
        mutation_disposition=disposition,
    )


def _rollback_receipt(
    plan: StudioActivationPlan,
    activation: StudioActivationReceipt,
    target: StudioSourceTarget,
    status: StudioExecutionStatus,
    reason: str,
    disposition: MutationDisposition,
    mutation: StudioSourceMutationResult | None = None,
) -> StudioRollbackReceipt:
    assert activation.applied_revision_sha is not None
    return StudioRollbackReceipt(
        status=status,
        reason_code=reason,
        packet_id=plan.packet_id,
        work_id=plan.work_id,
        change_id=plan.change_id,
        target=target,
        from_revision_sha=activation.applied_revision_sha,
        rollback_revision_id=plan.rollback_revision_id,
        rollback_state_sha256=plan.rollback_state_sha256,
        resulting_revision_sha=mutation.revision_sha if mutation else None,
        adapter_evidence_sha256=mutation.evidence_sha256 if mutation else None,
        mutation_disposition=disposition,
    )


def _target_payload(target: StudioSourceTarget) -> dict[str, str]:
    return {
        "provider_id": target.provider_id,
        "service_id": target.service_id,
        "target_ref": target.target_ref,
    }


def _receipt_digest(payload: dict[str, object]) -> str:
    material = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    return sha256(material).hexdigest()


def _token(value: str, field: str) -> None:
    if not isinstance(value, str) or _TOKEN_RE.fullmatch(value) is None:
        raise StudioActivationExecutionError(f"{field} must be a stable token")


def _git_sha(value: str, field: str) -> None:
    if not isinstance(value, str) or _SHA_RE.fullmatch(value) is None:
        raise StudioActivationExecutionError(
            f"{field} must be a lowercase Git SHA-1"
        )


def _digest(value: str, field: str) -> None:
    if not isinstance(value, str) or _DIGEST_RE.fullmatch(value) is None:
        raise StudioActivationExecutionError(f"{field} must be a lowercase SHA-256")


def _optional_git_sha(value: str | None, field: str) -> None:
    if value is not None:
        _git_sha(value, field)


def _optional_digest(value: str | None, field: str) -> None:
    if value is not None:
        _digest(value, field)
