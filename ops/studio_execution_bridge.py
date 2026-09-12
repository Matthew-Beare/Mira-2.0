"""Trusted bridge from review-ready Studio intake to the local worker manifest.

Customer intent remains customer intent. Technical execution policy remains owned by
MIRA's trusted controller. This bridge binds the two without asking the customer to
copy Git SHAs, paths, test commands, model endpoints, or worker budgets by hand.
"""

from __future__ import annotations

from dataclasses import dataclass
import json

from mira.studio_intake import (
    StudioIntakeDraft,
    StudioIntakeNextAction,
)
from ops.studio_local_worker import StudioWorkerError, WorkerManifest


@dataclass(frozen=True)
class StudioLocalExecutionPolicy:
    """Controller-owned execution details for one bounded local implementation."""

    repo_path: str
    base_sha: str
    branch_name: str
    allowed_paths: tuple[str, ...]
    test_argv: tuple[str, ...]
    model_base_url: str
    model: str
    max_rounds: int = 3
    wall_timeout_seconds: int = 900
    test_timeout_seconds: int = 180
    model_timeout_seconds: int = 180


def manifest_from_review_ready_intake(
    draft: StudioIntakeDraft,
    policy: StudioLocalExecutionPolicy,
) -> WorkerManifest:
    """Bind one review-ready intake to trusted execution policy.

    The intake cannot choose repository authority, mutable paths, tests, model
    endpoint, model identity, or budgets. Conversely, the execution policy cannot
    rewrite the customer's request, constraints, assumptions, or feature scope.
    """

    if not isinstance(draft, StudioIntakeDraft):
        raise StudioWorkerError("draft must be a StudioIntakeDraft")
    if not isinstance(policy, StudioLocalExecutionPolicy):
        raise StudioWorkerError("policy must be a StudioLocalExecutionPolicy")
    if (
        not draft.review_ready
        or draft.next_action is not StudioIntakeNextAction.REVIEW_DRAFT
        or draft.unresolved_questions
        or draft.blockers
    ):
        raise StudioWorkerError(
            "Studio intake must be review-ready before local implementation"
        )

    objective = json.dumps(
        {
            "customer_request": draft.raw_request,
            "desired_outcome": draft.desired_outcome,
            "explicit_customer_constraints": list(draft.explicit_constraints),
            "model_assumptions": list(draft.assumptions),
            "feature_ids": list(draft.feature_ids),
            "dependency_ids": list(draft.dependency_ids),
            "intake_projection_sha256": draft.projection_sha256,
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )

    manifest = WorkerManifest(
        draft_id=draft.draft_id,
        objective=objective,
        repo_path=policy.repo_path,
        base_sha=policy.base_sha,
        branch_name=policy.branch_name,
        allowed_paths=policy.allowed_paths,
        test_argv=policy.test_argv,
        model_base_url=policy.model_base_url,
        model=policy.model,
        max_rounds=policy.max_rounds,
        wall_timeout_seconds=policy.wall_timeout_seconds,
        test_timeout_seconds=policy.test_timeout_seconds,
        model_timeout_seconds=policy.model_timeout_seconds,
    )
    manifest.validate()
    return manifest
