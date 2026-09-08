"""Deterministic trust policy for optional private self-hosted CI.

This module never schedules a runner. It evaluates source provenance and optional
runner-isolation evidence into a secret-free decision receipt. Pull-request/fork
source remains hosted-only; canonical-main source still requires independent
runner isolation before private execution is eligible.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from enum import Enum
import json
from pathlib import Path
import re
from typing import Sequence


_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
_REPOSITORY_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
_BRANCH_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]{0,254}$")
_WORKFLOW_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 ._/-]{0,127}$")
_ALLOWED_TRIGGER_EVENTS = frozenset({"push", "pull_request"})
_ALLOWED_CONCLUSIONS = frozenset(
    {
        "success",
        "failure",
        "cancelled",
        "timed_out",
        "action_required",
        "neutral",
        "skipped",
        "stale",
        "startup_failure",
    }
)


class CiTrustValidationError(ValueError):
    """Raised when trust evidence is malformed rather than merely untrusted."""


class SourceTrust(str, Enum):
    UNTRUSTED = "untrusted"
    TRUSTED_CANONICAL_MAIN = "trusted_canonical_main"


class RunnerDecision(str, Enum):
    BLOCKED = "blocked"
    HOSTED_ONLY = "hosted_only"
    REQUIRES_ISOLATION = "requires_isolation"
    PRIVATE_RUNNER_ELIGIBLE = "private_runner_eligible"


@dataclass(frozen=True)
class WorkflowRunEvidence:
    """Secret-free provenance for one completed upstream CI workflow run."""

    trigger_repository: str
    trigger_event: str
    trigger_branch: str
    source_sha: str
    conclusion: str
    policy_sha: str
    workflow_name: str
    workflow_run_id: int

    def __post_init__(self) -> None:
        _repository(self.trigger_repository, "trigger_repository")
        if self.trigger_event not in _ALLOWED_TRIGGER_EVENTS:
            raise CiTrustValidationError("trigger_event is unsupported")
        _branch(self.trigger_branch, "trigger_branch")
        _sha(self.source_sha, "source_sha")
        if self.conclusion not in _ALLOWED_CONCLUSIONS:
            raise CiTrustValidationError("conclusion is unsupported")
        _sha(self.policy_sha, "policy_sha")
        _workflow(self.workflow_name, "workflow_name")
        _positive_int(self.workflow_run_id, "workflow_run_id")


@dataclass(frozen=True)
class RunnerIsolationEvidence:
    """Secret-free proof that a prospective private runner is constrained."""

    identity_restricted: bool
    workspace_ephemeral: bool
    source_execution_sandboxed: bool
    credentials_injected: bool
    private_network_access: bool

    def __post_init__(self) -> None:
        for field in (
            "identity_restricted",
            "workspace_ephemeral",
            "source_execution_sandboxed",
            "credentials_injected",
            "private_network_access",
        ):
            if not isinstance(getattr(self, field), bool):
                raise CiTrustValidationError(f"{field} must be boolean")


@dataclass(frozen=True)
class CiTrustReceipt:
    schema_version: int
    expected_repository: str
    expected_branch: str
    expected_workflow: str
    trigger_repository: str
    trigger_event: str
    trigger_branch: str
    source_sha: str
    policy_sha: str
    workflow_run_id: int
    source_trust: SourceTrust
    runner_decision: RunnerDecision
    self_hosted_execution_authorized: bool
    requires_isolation: bool
    reason_codes: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "expected_repository": self.expected_repository,
            "expected_branch": self.expected_branch,
            "expected_workflow": self.expected_workflow,
            "trigger_repository": self.trigger_repository,
            "trigger_event": self.trigger_event,
            "trigger_branch": self.trigger_branch,
            "source_sha": self.source_sha,
            "policy_sha": self.policy_sha,
            "workflow_run_id": self.workflow_run_id,
            "source_trust": self.source_trust.value,
            "runner_decision": self.runner_decision.value,
            "self_hosted_execution_authorized": self.self_hosted_execution_authorized,
            "requires_isolation": self.requires_isolation,
            "reason_codes": list(self.reason_codes),
        }

    def to_json(self) -> str:
        return json.dumps(
            self.to_dict(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )


def evaluate_ci_trust(
    evidence: WorkflowRunEvidence,
    *,
    expected_repository: str,
    expected_branch: str = "main",
    expected_workflow: str = "CI",
    isolation: RunnerIsolationEvidence | None = None,
) -> CiTrustReceipt:
    """Evaluate source trust and independent runner isolation."""

    if not isinstance(evidence, WorkflowRunEvidence):
        raise CiTrustValidationError("evidence must be WorkflowRunEvidence")
    expected_repository = _repository(expected_repository, "expected_repository")
    expected_branch = _branch(expected_branch, "expected_branch")
    expected_workflow = _workflow(expected_workflow, "expected_workflow")
    if isolation is not None and not isinstance(isolation, RunnerIsolationEvidence):
        raise CiTrustValidationError("isolation must be RunnerIsolationEvidence or None")

    source_reasons: list[str] = []
    hard_block = False

    if evidence.workflow_name != expected_workflow:
        source_reasons.append("source_workflow_mismatch")
        hard_block = True
    if evidence.conclusion != "success":
        source_reasons.append("source_ci_not_success")
        hard_block = True
    if evidence.trigger_repository != expected_repository:
        source_reasons.append("source_repository_mismatch")
    if evidence.trigger_event != "push":
        source_reasons.append("source_event_not_push")
    if evidence.trigger_branch != expected_branch:
        source_reasons.append("source_branch_mismatch")

    if hard_block:
        return _receipt(
            evidence,
            expected_repository=expected_repository,
            expected_branch=expected_branch,
            expected_workflow=expected_workflow,
            source_trust=SourceTrust.UNTRUSTED,
            runner_decision=RunnerDecision.BLOCKED,
            reasons=source_reasons,
        )

    if source_reasons:
        return _receipt(
            evidence,
            expected_repository=expected_repository,
            expected_branch=expected_branch,
            expected_workflow=expected_workflow,
            source_trust=SourceTrust.UNTRUSTED,
            runner_decision=RunnerDecision.HOSTED_ONLY,
            reasons=source_reasons,
        )

    if isolation is None:
        return _receipt(
            evidence,
            expected_repository=expected_repository,
            expected_branch=expected_branch,
            expected_workflow=expected_workflow,
            source_trust=SourceTrust.TRUSTED_CANONICAL_MAIN,
            runner_decision=RunnerDecision.REQUIRES_ISOLATION,
            reasons=("runner_isolation_missing",),
        )

    isolation_reasons = _isolation_blockers(isolation)
    if isolation_reasons:
        return _receipt(
            evidence,
            expected_repository=expected_repository,
            expected_branch=expected_branch,
            expected_workflow=expected_workflow,
            source_trust=SourceTrust.TRUSTED_CANONICAL_MAIN,
            runner_decision=RunnerDecision.BLOCKED,
            reasons=isolation_reasons,
        )

    return _receipt(
        evidence,
        expected_repository=expected_repository,
        expected_branch=expected_branch,
        expected_workflow=expected_workflow,
        source_trust=SourceTrust.TRUSTED_CANONICAL_MAIN,
        runner_decision=RunnerDecision.PRIVATE_RUNNER_ELIGIBLE,
        reasons=("trusted_source_and_isolation_verified",),
        authorized=True,
    )


def _isolation_blockers(isolation: RunnerIsolationEvidence) -> tuple[str, ...]:
    reasons: list[str] = []
    if not isolation.identity_restricted:
        reasons.append("runner_identity_unrestricted")
    if not isolation.workspace_ephemeral:
        reasons.append("runner_workspace_not_ephemeral")
    if not isolation.source_execution_sandboxed:
        reasons.append("runner_source_not_sandboxed")
    if isolation.credentials_injected:
        reasons.append("runner_credentials_present")
    if isolation.private_network_access:
        reasons.append("runner_private_network_present")
    return tuple(reasons)


def _receipt(
    evidence: WorkflowRunEvidence,
    *,
    expected_repository: str,
    expected_branch: str,
    expected_workflow: str,
    source_trust: SourceTrust,
    runner_decision: RunnerDecision,
    reasons: Sequence[str],
    authorized: bool = False,
) -> CiTrustReceipt:
    return CiTrustReceipt(
        schema_version=1,
        expected_repository=expected_repository,
        expected_branch=expected_branch,
        expected_workflow=expected_workflow,
        trigger_repository=evidence.trigger_repository,
        trigger_event=evidence.trigger_event,
        trigger_branch=evidence.trigger_branch,
        source_sha=evidence.source_sha,
        policy_sha=evidence.policy_sha,
        workflow_run_id=evidence.workflow_run_id,
        source_trust=source_trust,
        runner_decision=runner_decision,
        self_hosted_execution_authorized=authorized,
        requires_isolation=runner_decision == RunnerDecision.REQUIRES_ISOLATION,
        reason_codes=tuple(sorted(set(reasons))),
    )


def _repository(value: object, field: str) -> str:
    if not isinstance(value, str) or not _REPOSITORY_RE.fullmatch(value):
        raise CiTrustValidationError(f"{field} must be owner/repository")
    return value


def _branch(value: object, field: str) -> str:
    if not isinstance(value, str) or not _BRANCH_RE.fullmatch(value):
        raise CiTrustValidationError(f"{field} is invalid")
    return value


def _workflow(value: object, field: str) -> str:
    if not isinstance(value, str) or not _WORKFLOW_RE.fullmatch(value):
        raise CiTrustValidationError(f"{field} is invalid")
    return value


def _sha(value: object, field: str) -> str:
    if not isinstance(value, str) or not _SHA_RE.fullmatch(value):
        raise CiTrustValidationError(f"{field} must be a lowercase 40-character Git SHA")
    return value


def _positive_int(value: object, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise CiTrustValidationError(f"{field} must be a positive integer")
    return value


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="MIRA private-runner trust preflight")
    subparsers = parser.add_subparsers(dest="command", required=True)
    evaluate = subparsers.add_parser(
        "evaluate",
        help="write deterministic source-trust preflight evidence",
    )
    evaluate.add_argument("--expected-repository", required=True)
    evaluate.add_argument("--expected-branch", default="main")
    evaluate.add_argument("--expected-workflow", default="CI")
    evaluate.add_argument("--trigger-repository", required=True)
    evaluate.add_argument("--trigger-event", required=True)
    evaluate.add_argument("--trigger-branch", required=True)
    evaluate.add_argument("--trigger-workflow", required=True)
    evaluate.add_argument("--source-sha", required=True)
    evaluate.add_argument("--conclusion", required=True)
    evaluate.add_argument("--policy-sha", required=True)
    evaluate.add_argument("--workflow-run-id", required=True, type=int)
    evaluate.add_argument("--output", required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    evidence = WorkflowRunEvidence(
        trigger_repository=args.trigger_repository,
        trigger_event=args.trigger_event,
        trigger_branch=args.trigger_branch,
        source_sha=args.source_sha,
        conclusion=args.conclusion,
        policy_sha=args.policy_sha,
        workflow_name=args.trigger_workflow,
        workflow_run_id=args.workflow_run_id,
    )
    receipt = evaluate_ci_trust(
        evidence,
        expected_repository=args.expected_repository,
        expected_branch=args.expected_branch,
        expected_workflow=args.expected_workflow,
        isolation=None,
    )
    output = Path(args.output)
    output.write_text(receipt.to_json() + "\n", encoding="utf-8")
    print(receipt.to_json())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
