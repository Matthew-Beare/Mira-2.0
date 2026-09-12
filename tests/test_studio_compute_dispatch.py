from __future__ import annotations

import unittest
from unittest.mock import patch

from mira.command_sequencer import (
    COMPUTE_JOB_RESOURCE_TYPE,
    ComputeJobControlPlane,
)
from mira.service_state import (
    AuthorizationState,
    CapabilityEvidenceState,
    CapabilityGate,
    GateObservation,
    ProviderCapabilitySnapshot,
    WORKER_RESOURCE_TYPE,
    WorkerRegistryIdentityEvidence,
    WorkerRegistryService,
)
from mira.structured_state import InMemoryStructuredStateAdapter
from mira.studio_competition import StudioChangeKind
from mira.studio_intake import StudioIntakeDraft, StudioIntakeNextAction
from ops.studio_compute_dispatch import (
    StudioComputeDispatchError,
    StudioComputeDispatchPolicy,
    StudioDispatchOutcome,
    dispatch_review_ready_intake,
)
from ops.studio_execution_bridge import (
    RestrictedStudioExecutionResult,
    StudioLocalExecutionPolicy,
    manifest_from_review_ready_intake,
)
from ops.studio_local_worker import (
    StudioWorkerError,
    TestEvidence,
    WorkerResult,
)
from ops.studio_restricted_runtime import (
    RestrictedRuntimePolicy,
    RuntimeIsolationEvidence,
    StudioExecutionPermit,
    manifest_sha256,
)


NOW = "2026-09-12T21:30:00Z"
STALE = "2026-09-12T21:20:00Z"
BASE_SHA = "b" * 40
PROVENANCE = "4" * 64


class StudioComputeDispatchTests(unittest.TestCase):
    def setUp(self) -> None:
        adapter = InMemoryStructuredStateAdapter(
            schema_version="1",
            resource_types=(COMPUTE_JOB_RESOURCE_TYPE, WORKER_RESOURCE_TYPE),
            event_types=("studio_dispatch_test_event",),
        )
        self.control = ComputeJobControlPlane(adapter)
        self.registry = WorkerRegistryService(adapter)

    def draft(self) -> StudioIntakeDraft:
        return StudioIntakeDraft(
            draft_id="intake-" + ("a" * 64),
            registry_sha256="b" * 64,
            raw_request="Implement one bounded synthetic Studio change.",
            kind=StudioChangeKind.WORKFLOW,
            desired_outcome="Produce a reviewed candidate implementation.",
            feature_ids=("STUDIO-001",),
            dependency_ids=("LOCAL-001",),
            explicit_constraints=("Do not activate the candidate.",),
            assumptions=("An eligible local worker may be available.",),
            unresolved_questions=(),
            blockers=(),
            review_ready=True,
            next_action=StudioIntakeNextAction.REVIEW_DRAFT,
        )

    def execution_policy(self) -> StudioLocalExecutionPolicy:
        return StudioLocalExecutionPolicy(
            repo_path="/synthetic/repo",
            base_sha=BASE_SHA,
            branch_name="studio/synthetic-dispatch",
            allowed_paths=("mira/example.py",),
            test_argv=("python", "-m", "unittest", "tests.test_example"),
            model_base_url="http://127.0.0.1:1234/v1",
            model="local-synthetic-model",
            max_rounds=2,
            wall_timeout_seconds=60,
            test_timeout_seconds=10,
            model_timeout_seconds=10,
        )

    def dispatch_policy(self, **changes) -> StudioComputeDispatchPolicy:
        values = {
            "operation_id": "studio_implement",
            "service_id": "ai-runtime",
            "data_classification": "private_source",
            "required_gates": (CapabilityGate.READ,),
            "required_runtime_capabilities": ("coding", "local_model"),
            "priority": 20,
            "max_attempts": 1,
            "lease_ttl_seconds": 180,
            "max_provider_evidence_age_seconds": 120,
            "max_worker_heartbeat_age_seconds": 120,
        }
        values.update(changes)
        return StudioComputeDispatchPolicy(**values)

    def runtime_policy(self, **changes) -> RestrictedRuntimePolicy:
        values = {
            "policy_id": "studio-restricted-v1",
            "required_operation_id": "studio_implement",
            "required_service_id": "ai-runtime",
            "required_worker_capabilities": ("restricted_runtime",),
            "allowed_attestation_kinds": ("trusted_host_policy",),
            "max_evidence_age_seconds": 120,
            "max_worker_heartbeat_age_seconds": 120,
            "permit_ttl_seconds": 60,
            "required_network_mode": "loopback_only",
            "bind_job_input_to_draft": True,
        }
        values.update(changes)
        return RestrictedRuntimePolicy(**values)

    def register_worker(
        self,
        worker_id: str,
        *,
        lane_id: str | None = None,
        runtime_id: str | None = None,
        priority: int = 10,
        mode: str = "normal",
        health: str = "healthy",
        availability: str = "ready",
        interactive_lock: bool = False,
        heartbeat_at: str = NOW,
        caps: tuple[str, ...] = ("coding", "local_model", "restricted_runtime"),
    ):
        lane = lane_id or f"lane-{worker_id}"
        runtime = runtime_id or f"runtime-{worker_id}"
        return self.registry.register(
            worker_id,
            identity=WorkerRegistryIdentityEvidence(
                principal_id=f"principal-{worker_id}",
                state="verified",
                verified_at=heartbeat_at,
            ),
            lane_id=lane,
            runtime_id=runtime,
            service_id="ai-runtime",
            runtime_kind="local",
            runtime_capabilities=caps,
            policy_id=f"policy-{worker_id}",
            approval_state="approved",
            allowed_data_classifications=("private_source",),
            local_compute_mode=mode,
            availability=availability,
            health=health,
            interactive_lock=interactive_lock,
            priority=priority,
            load_rank=0,
            cost_rank=0,
            heartbeat_at=heartbeat_at,
            now=NOW,
            idempotency_key=f"register-{worker_id}",
        )

    def capability(
        self,
        worker_id: str,
        *,
        state: CapabilityEvidenceState = CapabilityEvidenceState.VERIFIED,
    ) -> ProviderCapabilitySnapshot:
        return ProviderCapabilitySnapshot(
            provider_id=f"provider-{worker_id}",
            service_id="ai-runtime",
            authorization_state=AuthorizationState.AUTHORIZED,
            authorization_observed_at=NOW,
            gates=(
                GateObservation(
                    gate=CapabilityGate.READ,
                    state=state,
                    observed_at=NOW,
                ),
            ),
            resource_ref=f"synthetic:{worker_id}",
            scopes=("synthetic.read",),
        )

    def isolation(self, worker_id: str, *, runtime_id: str | None = None):
        return RuntimeIsolationEvidence(
            worker_id=worker_id,
            principal_id=f"principal-{worker_id}",
            runtime_id=runtime_id or f"runtime-{worker_id}",
            observed_at=NOW,
            attestation_kind="trusted_host_policy",
            restricted_identity=True,
            filesystem_isolation=True,
            process_tree_containment=True,
            credential_isolation=True,
            resource_limits_enforced=True,
            network_mode="loopback_only",
            provenance_sha256=PROVENANCE,
        )

    def worker_result(self, *, ready: bool = True) -> WorkerResult:
        baseline = TestEvidence(
            candidate_sha=BASE_SHA,
            returncode=0,
            timed_out=False,
            duration_ms=1,
            stdout="",
            stderr="",
        )
        return WorkerResult(
            run_id="studio-synthetic-run",
            draft_id=self.draft().draft_id,
            source_repo="/synthetic/private/repo",
            base_sha=BASE_SHA,
            branch_name="studio/synthetic-dispatch",
            worktree_path="/synthetic/private/worktree",
            evidence_path="/synthetic/private/evidence",
            status="ready_for_review" if ready else "blocked",
            stop_reason="tests_passed" if ready else "stagnation",
            baseline_test=baseline,
            rounds=(),
            final_candidate_sha=("c" * 40) if ready else None,
        )

    def restricted_result(self, job, worker, *, ready: bool = True):
        permit = StudioExecutionPermit(
            permit_id="1" * 64,
            policy_id="studio-restricted-v1",
            policy_sha256="2" * 64,
            job_id=job.job_id,
            lease_id=job.lease_id,
            worker_id=worker.worker_id,
            principal_id=worker.principal_id,
            runtime_id=worker.runtime_id,
            draft_id=self.draft().draft_id,
            manifest_sha256=job.input_sha256,
            isolation_provenance_sha256=PROVENANCE,
            attestation_kind="trusted_host_policy",
            issued_at=NOW,
            expires_at="2026-09-12T21:31:00Z",
        )
        return RestrictedStudioExecutionResult(
            permit=permit,
            worker_result=self.worker_result(ready=ready),
        )

    def dispatch(self, *, capabilities, isolations, **kwargs):
        return dispatch_review_ready_intake(
            self.draft(),
            self.execution_policy(),
            control_plane=self.control,
            worker_registry=self.registry,
            provider_capabilities=capabilities,
            isolation_evidence=isolations,
            dispatch_policy=kwargs.pop("dispatch_policy", self.dispatch_policy()),
            runtime_policy=kwargs.pop("runtime_policy", self.runtime_policy()),
            clock=lambda: NOW,
            **kwargs,
        )

    def test_success_routes_exact_job_starts_and_completes_with_worker_provenance(self):
        self.register_worker("worker-a", priority=20)
        selected = self.register_worker("worker-b", priority=5)

        self.control.submit(
            "unrelated-higher-ranked-job",
            operation_id="other",
            service_id="ai-runtime",
            data_classification="private_source",
            required_capabilities=("coding",),
            input_artifact_id="unrelated-input",
            input_sha256="9" * 64,
            priority=0,
            max_attempts=3,
            created_at=NOW,
            idempotency_key="submit-unrelated",
        )

        capabilities = {
            "worker-a": self.capability("worker-a"),
            "worker-b": self.capability("worker-b"),
        }
        isolations = {
            "worker-a": self.isolation("worker-a"),
            "worker-b": self.isolation("worker-b"),
        }

        def execute(draft, execution_policy, **call):
            self.assertEqual(call["job"].state, "running")
            self.assertEqual(call["job"].lease_worker_id, "worker-b")
            self.assertEqual(call["worker"].worker_id, "worker-b")
            return self.restricted_result(call["job"], call["worker"], ready=True)

        with patch(
            "ops.studio_compute_dispatch.run_review_ready_intake_restricted",
            side_effect=execute,
        ) as runner:
            result = self.dispatch(capabilities=capabilities, isolations=isolations)

        self.assertEqual(result.outcome, StudioDispatchOutcome.SUCCEEDED)
        self.assertEqual(result.selected_worker_id, "worker-b")
        self.assertEqual(result.job.state, "succeeded")
        self.assertEqual(result.job.result_worker_id, "worker-b")
        self.assertEqual(result.job.result_runtime_id, selected.runtime_id)
        manifest = manifest_from_review_ready_intake(
            self.draft(), self.execution_policy()
        )
        self.assertEqual(result.job.input_artifact_id, self.draft().draft_id)
        self.assertEqual(result.job.input_sha256, manifest_sha256(manifest))
        self.assertEqual(
            self.control.get("unrelated-higher-ranked-job").state,
            "queued",
        )
        runner.assert_called_once()

    def test_successful_dispatch_replay_does_not_execute_or_increment_again(self):
        worker = self.register_worker("worker-a")
        capabilities = {"worker-a": self.capability("worker-a")}
        isolations = {"worker-a": self.isolation("worker-a")}

        with patch(
            "ops.studio_compute_dispatch.run_review_ready_intake_restricted",
            return_value=self.restricted_result(
                type("Job", (), {
                    "job_id": "placeholder",
                    "lease_id": "placeholder",
                    "input_sha256": "3" * 64,
                })(),
                worker,
            ),
        ) as runner:
            def realish(draft, execution_policy, **call):
                return self.restricted_result(call["job"], call["worker"])
            runner.side_effect = realish
            first = self.dispatch(capabilities=capabilities, isolations=isolations)
            runner.reset_mock()
            second = self.dispatch(capabilities=capabilities, isolations=isolations)

        self.assertEqual(first.outcome, StudioDispatchOutcome.SUCCEEDED)
        self.assertEqual(second.outcome, StudioDispatchOutcome.REPLAYED_SUCCESS)
        self.assertEqual(second.job.revision, first.job.revision)
        self.assertEqual(second.job.attempts, 1)
        runner.assert_not_called()

    def test_local_compute_off_blocks_before_lease_or_execution(self):
        self.register_worker("worker-a", mode="off")
        with patch(
            "ops.studio_compute_dispatch.run_review_ready_intake_restricted"
        ) as runner:
            result = self.dispatch(
                capabilities={"worker-a": self.capability("worker-a")},
                isolations={"worker-a": self.isolation("worker-a")},
            )
        self.assertEqual(result.outcome, StudioDispatchOutcome.BLOCKED)
        self.assertEqual(result.reason, "policy_blocked")
        self.assertEqual(result.job.state, "queued")
        self.assertEqual(result.job.attempts, 0)
        runner.assert_not_called()

    def test_stale_worker_blocks_before_lease_or_execution(self):
        self.register_worker("worker-a", heartbeat_at=STALE)
        policy = self.dispatch_policy(max_worker_heartbeat_age_seconds=60)
        with patch(
            "ops.studio_compute_dispatch.run_review_ready_intake_restricted"
        ) as runner:
            result = self.dispatch(
                capabilities={"worker-a": self.capability("worker-a")},
                isolations={"worker-a": self.isolation("worker-a")},
                dispatch_policy=policy,
            )
        self.assertEqual(result.outcome, StudioDispatchOutcome.BLOCKED)
        self.assertEqual(result.reason, "capability_blocked")
        self.assertEqual(result.job.attempts, 0)
        runner.assert_not_called()

    def test_missing_provider_or_isolation_evidence_blocks_without_attempt(self):
        self.register_worker("worker-a")
        missing_provider = self.dispatch(capabilities={}, isolations={})
        self.assertEqual(missing_provider.outcome, StudioDispatchOutcome.BLOCKED)
        self.assertEqual(missing_provider.reason, "no_candidates")
        self.assertEqual(missing_provider.job.attempts, 0)

        missing_isolation = self.dispatch(
            capabilities={"worker-a": self.capability("worker-a")},
            isolations={},
        )
        self.assertEqual(missing_isolation.outcome, StudioDispatchOutcome.BLOCKED)
        self.assertEqual(missing_isolation.reason, "isolation_evidence_missing")
        self.assertEqual(missing_isolation.job.attempts, 0)

    def test_ambiguous_durable_lane_mapping_fails_closed_before_lease(self):
        self.register_worker("worker-a", lane_id="shared-lane", runtime_id="runtime-a")
        self.register_worker("worker-b", lane_id="shared-lane", runtime_id="runtime-b")
        result = self.dispatch(
            capabilities={
                "worker-a": self.capability("worker-a"),
                "worker-b": self.capability("worker-b"),
            },
            isolations={
                "worker-a": self.isolation("worker-a", runtime_id="runtime-a"),
                "worker-b": self.isolation("worker-b", runtime_id="runtime-b"),
            },
        )
        self.assertEqual(result.outcome, StudioDispatchOutcome.BLOCKED)
        self.assertEqual(result.reason, "ambiguous_worker_lane")
        self.assertEqual(result.job.attempts, 0)

    def test_worker_blocked_result_is_durably_failed_not_completed(self):
        worker = self.register_worker("worker-a")
        with patch(
            "ops.studio_compute_dispatch.run_review_ready_intake_restricted",
            side_effect=lambda draft, execution_policy, **call: self.restricted_result(
                call["job"], call["worker"], ready=False
            ),
        ):
            result = self.dispatch(
                capabilities={"worker-a": self.capability("worker-a")},
                isolations={"worker-a": self.isolation("worker-a")},
            )
        self.assertEqual(result.outcome, StudioDispatchOutcome.FAILED)
        self.assertEqual(result.reason, "studio_stagnation")
        self.assertEqual(result.job.state, "failed")
        self.assertEqual(result.job.error_code, "studio_stagnation")
        self.assertIsNone(result.job.result_artifact_id)
        self.assertEqual(result.selected_worker_id, worker.worker_id)

    def test_worker_exception_is_durably_failed_without_raw_error_persistence(self):
        self.register_worker("worker-a")
        with patch(
            "ops.studio_compute_dispatch.run_review_ready_intake_restricted",
            side_effect=StudioWorkerError("synthetic private path /do/not/store"),
        ):
            result = self.dispatch(
                capabilities={"worker-a": self.capability("worker-a")},
                isolations={"worker-a": self.isolation("worker-a")},
            )
        self.assertEqual(result.outcome, StudioDispatchOutcome.FAILED)
        self.assertEqual(result.reason, "studio_execution_error")
        self.assertEqual(result.job.state, "failed")
        self.assertEqual(result.job.error_code, "studio_execution_error")
        self.assertNotIn("private", repr(result.job))

    def test_dispatch_and_restricted_runtime_policy_must_align(self):
        self.register_worker("worker-a")
        with self.assertRaisesRegex(StudioComputeDispatchError, "service"):
            self.dispatch(
                capabilities={"worker-a": self.capability("worker-a")},
                isolations={"worker-a": self.isolation("worker-a")},
                runtime_policy=self.runtime_policy(required_service_id="other-service"),
            )

    def test_current_local_worker_retry_budget_is_deliberately_one_attempt(self):
        with self.assertRaisesRegex(StudioComputeDispatchError, "max_attempts=1"):
            self.dispatch_policy(max_attempts=2)


if __name__ == "__main__":
    unittest.main()
