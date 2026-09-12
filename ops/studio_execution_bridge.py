"""Trusted bridge from review-ready Studio intake to bounded local execution.

Customer intent remains customer intent. Technical execution policy remains owned by
MIRA's trusted controller. This bridge binds the two without asking the customer to
copy Git SHAs, paths, test commands, model endpoints, worker budgets, compute leases,
or runtime-isolation details by hand.
"""

from __future__ import annotations

from dataclasses import dataclass

from mira.command_sequencer import ComputeJobView
from mira.service_state import WorkerRegistryView
from mira.studio_intake import StudioIntakeDraft
from ops.studio_local_worker import StudioWorkerError, WorkerManifest, WorkerResult
from ops.studio_restricted_runtime import (
    RestrictedRuntimePolicy,
    RuntimeIsolationEvidence,
    StudioExecutionPermit,
    issue_execution_permit,
    run_authorized_manifest,
)
from ops.studio_worker_task import (
    StudioWorkerTaskError,
    objective_from_review_ready_intake,
)


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


@dataclass(frozen=True)
class RestrictedStudioExecutionResult:
    """Admission receipt plus lower-worker evidence for one restricted run."""

    permit: StudioExecutionPermit
    worker_result: WorkerResult


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
    try:
        objective = objective_from_review_ready_intake(draft)
    except StudioWorkerTaskError as exc:
        raise StudioWorkerError(str(exc)) from exc

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


def run_review_ready_intake_restricted(
    draft: StudioIntakeDraft,
    execution_policy: StudioLocalExecutionPolicy,
    *,
    job: ComputeJobView,
    worker: WorkerRegistryView,
    isolation: RuntimeIsolationEvidence,
    runtime_policy: RestrictedRuntimePolicy,
    now: str,
) -> RestrictedStudioExecutionResult:
    """Execute one review-ready intake only after restricted-runtime admission.

    This is the controller-facing safe path. The durable compute job must already
    hold a live lease for the exact worker. Worker identity, approval, capability,
    data-classification policy, health/locks and trusted host-isolation evidence
    are revalidated immediately before the lower Studio worker is entered.
    """

    manifest = manifest_from_review_ready_intake(draft, execution_policy)
    permit = issue_execution_permit(
        manifest=manifest,
        job=job,
        worker=worker,
        isolation=isolation,
        policy=runtime_policy,
        now=now,
    )
    worker_result = run_authorized_manifest(
        permit=permit,
        manifest=manifest,
        job=job,
        worker=worker,
        isolation=isolation,
        policy=runtime_policy,
        now=now,
    )
    return RestrictedStudioExecutionResult(
        permit=permit,
        worker_result=worker_result,
    )