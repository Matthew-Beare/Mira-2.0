from __future__ import annotations

import unittest
from unittest.mock import patch

from mira.command_sequencer import ComputeJobView
from mira.service_state import WorkerRegistryView
from ops.studio_local_worker import WorkerManifest
from ops.studio_restricted_runtime import (
    RestrictedRuntimeError,
    RestrictedRuntimePolicy,
    RuntimeIsolationEvidence,
    issue_execution_permit,
    manifest_sha256,
    run_authorized_manifest,
    validate_execution_permit,
)


NOW = "2026-09-12T20:30:00Z"
DRAFT_ID = "intake-" + ("a" * 64)


class StudioRestrictedRuntimeTests(unittest.TestCase):
    def manifest(self, **changes) -> WorkerManifest:
        values = {
            "draft_id": DRAFT_ID,
            "objective": "Implement one bounded reviewed Studio change.",
            "repo_path": "/srv/mira/source",
            "base_sha": "b" * 40,
            "branch_name": "studio/restricted-candidate",
            "allowed_paths": ("mira/example.py",),
            "test_argv": ("python", "-m", "unittest", "tests.test_example"),
            "model_base_url": "http://127.0.0.1:1234/v1",
            "model": "local-profile",
            "max_rounds": 3,
            "wall_timeout_seconds": 900,
            "test_timeout_seconds": 180,
            "model_timeout_seconds": 180,
        }
        values.update(changes)
        return WorkerManifest(**values)

    def job(self, **changes) -> ComputeJobView:
        values = {
            "job_id": "job-studio-1",
            "revision": 4,
            "operation_id": "studio_implement",
            "service_id": "mira_studio",
            "data_classification": "private_source",
            "required_capabilities": ("code_edit", "local_model"),
            "input_artifact_id": DRAFT_ID,
            "input_sha256": "1" * 64,
            "priority": 10,
            "max_attempts": 3,
            "state": "leased",
            "attempts": 1,
            "created_at": "2026-09-12T20:00:00Z",
            "cancel_requested": False,
            "lease_worker_id": "worker-local-1",
            "lease_id": "lease-1",
            "leased_at": "2026-09-12T20:29:00Z",
            "lease_expires_at": "2026-09-12T20:40:00Z",
            "started_at": None,
            "checkpoint_artifact_id": None,
            "checkpoint_sha256": None,
            "error_code": None,
            "result_artifact_id": None,
            "result_sha256": None,
            "result_worker_id": None,
            "result_runtime_id": None,
            "result_attempt": None,
            "finished_at": None,
            "last_transition_key_sha256": "2" * 64,
            "last_transition_material_sha256": "3" * 64,
            "idempotent_replay": False,
        }
        values.update(changes)
        return ComputeJobView(**values)

    def worker(self, **changes) -> WorkerRegistryView:
        values = {
            "worker_id": "worker-local-1",
            "revision": 7,
            "principal_id": "principal-local-1",
            "identity_state": "verified",
            "identity_verified_at": "2026-09-12T20:20:00Z",
            "lane_id": "lane-home",
            "runtime_id": "runtime-studio-1",
            "service_id": "compute",
            "runtime_kind": "local",
            "runtime_capabilities": (
                "code_edit",
                "local_model",
                "restricted_runtime",
            ),
            "policy_id": "compute-home",
            "approval_state": "approved",
            "allowed_data_classifications": ("private_source",),
            "local_compute_mode": "normal",
            "availability": "busy",
            "health": "healthy",
            "interactive_lock": False,
            "priority": 10,
            "load_rank": 1,
            "cost_rank": 1,
            "heartbeat_at": "2026-09-12T20:30:00Z",
            "idempotent_replay": False,
        }
        values.update(changes)
        return WorkerRegistryView(**values)

    def isolation(self, **changes) -> RuntimeIsolationEvidence:
        values = {
            "worker_id": "worker-local-1",
            "principal_id": "principal-local-1",
            "runtime_id": "runtime-studio-1",
            "observed_at": "2026-09-12T20:30:00Z",
            "attestation_kind": "trusted_host_policy",
            "restricted_identity": True,
            "filesystem_isolation": True,
            "process_tree_containment": True,
            "credential_isolation": True,
            "resource_limits_enforced": True,
            "network_mode": "loopback_only",
            "provenance_sha256": "4" * 64,
        }
        values.update(changes)
        return RuntimeIsolationEvidence(**values)

    def policy(self, **changes) -> RestrictedRuntimePolicy:
        values = {
            "policy_id": "studio-restricted-v1",
            "required_operation_id": "studio_implement",
            "required_service_id": "mira_studio",
            "required_worker_capabilities": ("restricted_runtime",),
            "allowed_attestation_kinds": ("trusted_host_policy",),
            "max_evidence_age_seconds": 60,
            "max_worker_heartbeat_age_seconds": 60,
            "permit_ttl_seconds": 120,
            "required_network_mode": "loopback_only",
            "bind_job_input_to_draft": True,
        }
        values.update(changes)
        return RestrictedRuntimePolicy(**values)

    def permit(self):
        return issue_execution_permit(
            manifest=self.manifest(),
            job=self.job(),
            worker=self.worker(),
            isolation=self.isolation(),
            policy=self.policy(),
            now=NOW,
        )

    def test_permit_binds_exact_manifest_policy_and_lease_context(self):
        permit = self.permit()
        self.assertEqual(permit.manifest_sha256, manifest_sha256(self.manifest()))
        self.assertEqual(len(permit.policy_sha256), 64)
        self.assertEqual(permit.job_id, "job-studio-1")
        self.assertEqual(permit.lease_id, "lease-1")
        self.assertEqual(permit.worker_id, "worker-local-1")
        self.assertEqual(permit.runtime_id, "runtime-studio-1")
        self.assertEqual(permit.draft_id, DRAFT_ID)
        self.assertEqual(permit.expires_at, "2026-09-12T20:32:00Z")

        validate_execution_permit(
            permit=permit,
            manifest=self.manifest(),
            job=self.job(),
            worker=self.worker(),
            isolation=self.isolation(),
            policy=self.policy(),
            now="2026-09-12T20:31:00Z",
        )

    def test_newer_heartbeat_does_not_invalidate_unchanged_permit(self):
        permit = self.permit()
        validate_execution_permit(
            permit=permit,
            manifest=self.manifest(),
            job=self.job(),
            worker=self.worker(revision=8, heartbeat_at="2026-09-12T20:30:30Z"),
            isolation=self.isolation(observed_at="2026-09-12T20:30:30Z"),
            policy=self.policy(),
            now="2026-09-12T20:31:00Z",
        )

    def test_manifest_change_invalidates_permit_before_worker_entry(self):
        permit = self.permit()
        changed = self.manifest(test_argv=("python", "-m", "unittest", "different"))
        with patch("ops.studio_restricted_runtime.run_manifest") as runner:
            with self.assertRaisesRegex(RestrictedRuntimeError, "manifest"):
                run_authorized_manifest(
                    permit=permit,
                    manifest=changed,
                    job=self.job(),
                    worker=self.worker(),
                    isolation=self.isolation(),
                    policy=self.policy(),
                    now="2026-09-12T20:31:00Z",
                )
        runner.assert_not_called()

    def test_policy_change_invalidates_permit_before_worker_entry(self):
        permit = self.permit()
        changed_policy = self.policy(permit_ttl_seconds=60)
        with patch("ops.studio_restricted_runtime.run_manifest") as runner:
            with self.assertRaisesRegex(RestrictedRuntimeError, "policy_sha256|policy"):
                run_authorized_manifest(
                    permit=permit,
                    manifest=self.manifest(),
                    job=self.job(),
                    worker=self.worker(),
                    isolation=self.isolation(),
                    policy=changed_policy,
                    now="2026-09-12T20:30:30Z",
                )
        runner.assert_not_called()

    def test_expired_permit_is_rejected_before_worker_entry(self):
        permit = self.permit()
        with patch("ops.studio_restricted_runtime.run_manifest") as runner:
            with self.assertRaisesRegex(RestrictedRuntimeError, "expired"):
                run_authorized_manifest(
                    permit=permit,
                    manifest=self.manifest(),
                    job=self.job(),
                    worker=self.worker(heartbeat_at="2026-09-12T20:32:01Z"),
                    isolation=self.isolation(observed_at="2026-09-12T20:32:01Z"),
                    policy=self.policy(),
                    now="2026-09-12T20:32:01Z",
                )
        runner.assert_not_called()

    def test_worker_lease_identity_and_runtime_evidence_must_agree(self):
        cases = (
            (self.job(lease_worker_id="other-worker"), self.worker(), self.isolation(), "different worker"),
            (self.job(), self.worker(principal_id="other-principal"), self.isolation(), "principal"),
            (self.job(), self.worker(runtime_id="runtime-other"), self.isolation(), "runtime"),
        )
        for job, worker, isolation, message in cases:
            with self.subTest(message=message):
                with self.assertRaisesRegex(RestrictedRuntimeError, message):
                    issue_execution_permit(
                        manifest=self.manifest(),
                        job=job,
                        worker=worker,
                        isolation=isolation,
                        policy=self.policy(),
                        now=NOW,
                    )

    def test_cancel_expiry_health_approval_and_interactive_lock_fail_closed(self):
        cases = (
            (self.job(cancel_requested=True), self.worker(), "cancel"),
            (self.job(lease_expires_at=NOW), self.worker(), "expired"),
            (self.job(), self.worker(health="degraded"), "healthy"),
            (self.job(), self.worker(approval_state="required"), "approved"),
            (self.job(), self.worker(interactive_lock=True), "interactive"),
            (self.job(), self.worker(local_compute_mode="off"), "off"),
        )
        for job, worker, message in cases:
            with self.subTest(message=message):
                with self.assertRaisesRegex(RestrictedRuntimeError, message):
                    issue_execution_permit(
                        manifest=self.manifest(),
                        job=job,
                        worker=worker,
                        isolation=self.isolation(),
                        policy=self.policy(),
                        now=NOW,
                    )

    def test_worker_identity_and_heartbeat_must_be_current(self):
        cases = (
            (self.worker(heartbeat_at="2026-09-12T20:28:59Z"), "heartbeat is stale"),
            (self.worker(heartbeat_at="2026-09-12T20:30:01Z"), "heartbeat cannot be from the future"),
            (
                self.worker(identity_verified_at="2026-09-12T20:29:45Z", heartbeat_at="2026-09-12T20:29:30Z"),
                "predates identity",
            ),
            (
                self.worker(identity_verified_at="2026-09-12T20:30:01Z", heartbeat_at="2026-09-12T20:30:01Z"),
                "identity verification cannot be from the future",
            ),
        )
        for worker, message in cases:
            with self.subTest(message=message):
                with self.assertRaisesRegex(RestrictedRuntimeError, message):
                    issue_execution_permit(
                        manifest=self.manifest(),
                        job=self.job(),
                        worker=worker,
                        isolation=self.isolation(),
                        policy=self.policy(),
                        now=NOW,
                    )

    def test_data_classification_and_capabilities_fail_closed(self):
        cases = (
            (
                self.job(data_classification="secret"),
                self.worker(),
                self.policy(),
                "classification",
            ),
            (
                self.job(required_capabilities=("code_edit", "gpu")),
                self.worker(),
                self.policy(),
                "job capabilities",
            ),
            (
                self.job(),
                self.worker(runtime_capabilities=("code_edit", "local_model")),
                self.policy(),
                "restricted-runtime capabilities",
            ),
        )
        for job, worker, policy, message in cases:
            with self.subTest(message=message):
                with self.assertRaisesRegex(RestrictedRuntimeError, message):
                    issue_execution_permit(
                        manifest=self.manifest(),
                        job=job,
                        worker=worker,
                        isolation=self.isolation(),
                        policy=policy,
                        now=NOW,
                    )

    def test_isolation_must_be_fresh_trusted_and_complete(self):
        cases = (
            (self.isolation(observed_at="2026-09-12T20:28:44Z"), self.policy(), "stale"),
            (self.isolation(observed_at="2026-09-12T20:30:01Z"), self.policy(), "future"),
            (self.isolation(attestation_kind="self_report"), self.policy(), "attestation"),
            (self.isolation(restricted_identity=False), self.policy(), "restricted_identity"),
            (self.isolation(filesystem_isolation=False), self.policy(), "filesystem_isolation"),
            (self.isolation(process_tree_containment=False), self.policy(), "process_tree_containment"),
            (self.isolation(credential_isolation=False), self.policy(), "credential_isolation"),
            (self.isolation(resource_limits_enforced=False), self.policy(), "resource_limits_enforced"),
            (self.isolation(network_mode="none"), self.policy(), "network"),
        )
        for isolation, policy, message in cases:
            with self.subTest(message=message):
                with self.assertRaisesRegex(RestrictedRuntimeError, message):
                    issue_execution_permit(
                        manifest=self.manifest(),
                        job=self.job(),
                        worker=self.worker(),
                        isolation=isolation,
                        policy=policy,
                        now=NOW,
                    )

    def test_job_input_must_bind_to_reviewed_draft_when_policy_requires_it(self):
        with self.assertRaisesRegex(RestrictedRuntimeError, "draft"):
            issue_execution_permit(
                manifest=self.manifest(),
                job=self.job(input_artifact_id="other-input"),
                worker=self.worker(),
                isolation=self.isolation(),
                policy=self.policy(),
                now=NOW,
            )

    def test_permit_contains_no_private_endpoint_path_or_credentials(self):
        permit = self.permit()
        text = repr(permit)
        self.assertNotIn("/srv/mira/source", text)
        self.assertNotIn("127.0.0.1", text)
        self.assertNotIn("local-profile", text)
        self.assertNotIn("test_example", text)
        self.assertNotIn("token", text.lower())
        self.assertNotIn("password", text.lower())

    def test_authorized_entry_calls_lower_worker_only_after_revalidation(self):
        permit = self.permit()
        sentinel = object()
        with patch("ops.studio_restricted_runtime.run_manifest", return_value=sentinel) as runner:
            result = run_authorized_manifest(
                permit=permit,
                manifest=self.manifest(),
                job=self.job(),
                worker=self.worker(),
                isolation=self.isolation(),
                policy=self.policy(),
                now="2026-09-12T20:31:00Z",
            )
        self.assertIs(result, sentinel)
        runner.assert_called_once_with(self.manifest())


if __name__ == "__main__":
    unittest.main()
