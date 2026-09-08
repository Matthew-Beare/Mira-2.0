from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from project.ci_trust import (
    CiTrustValidationError,
    RunnerDecision,
    RunnerIsolationEvidence,
    SourceTrust,
    WorkflowRunEvidence,
    evaluate_ci_trust,
    main,
)


REPOSITORY = "Matthew-Beare/Mira-2.0"
SOURCE_SHA = "a" * 40
POLICY_SHA = "b" * 40


class CiTrustTests(unittest.TestCase):
    def evidence(self, **overrides) -> WorkflowRunEvidence:
        values = {
            "trigger_repository": REPOSITORY,
            "trigger_event": "push",
            "trigger_branch": "main",
            "source_sha": SOURCE_SHA,
            "conclusion": "success",
            "policy_sha": POLICY_SHA,
            "workflow_name": "CI",
            "workflow_run_id": 42,
        }
        values.update(overrides)
        return WorkflowRunEvidence(**values)

    def safe_isolation(self) -> RunnerIsolationEvidence:
        return RunnerIsolationEvidence(
            identity_restricted=True,
            workspace_ephemeral=True,
            source_execution_sandboxed=True,
            credentials_injected=False,
            private_network_access=False,
        )

    def test_successful_canonical_main_still_requires_runner_isolation(self) -> None:
        receipt = evaluate_ci_trust(
            self.evidence(),
            expected_repository=REPOSITORY,
        )
        self.assertEqual(receipt.source_trust, SourceTrust.TRUSTED_CANONICAL_MAIN)
        self.assertEqual(receipt.runner_decision, RunnerDecision.REQUIRES_ISOLATION)
        self.assertTrue(receipt.requires_isolation)
        self.assertFalse(receipt.self_hosted_execution_authorized)
        self.assertEqual(receipt.reason_codes, ("runner_isolation_missing",))

    def test_safe_isolation_allows_only_already_trusted_main_source(self) -> None:
        receipt = evaluate_ci_trust(
            self.evidence(),
            expected_repository=REPOSITORY,
            isolation=self.safe_isolation(),
        )
        self.assertEqual(
            receipt.runner_decision,
            RunnerDecision.PRIVATE_RUNNER_ELIGIBLE,
        )
        self.assertTrue(receipt.self_hosted_execution_authorized)
        self.assertFalse(receipt.requires_isolation)

    def test_same_repository_pull_request_remains_hosted_only(self) -> None:
        receipt = evaluate_ci_trust(
            self.evidence(
                trigger_event="pull_request",
                trigger_branch="feature/test",
            ),
            expected_repository=REPOSITORY,
            isolation=self.safe_isolation(),
        )
        self.assertEqual(receipt.source_trust, SourceTrust.UNTRUSTED)
        self.assertEqual(receipt.runner_decision, RunnerDecision.HOSTED_ONLY)
        self.assertFalse(receipt.self_hosted_execution_authorized)
        self.assertIn("source_event_not_push", receipt.reason_codes)

    def test_fork_pull_request_remains_hosted_only_even_with_safe_isolation(self) -> None:
        receipt = evaluate_ci_trust(
            self.evidence(
                trigger_repository="someone-else/Mira-2.0",
                trigger_event="pull_request",
                trigger_branch="feature/test",
            ),
            expected_repository=REPOSITORY,
            isolation=self.safe_isolation(),
        )
        self.assertEqual(receipt.runner_decision, RunnerDecision.HOSTED_ONLY)
        self.assertFalse(receipt.self_hosted_execution_authorized)
        self.assertIn("source_repository_mismatch", receipt.reason_codes)

    def test_noncanonical_branch_push_remains_hosted_only(self) -> None:
        receipt = evaluate_ci_trust(
            self.evidence(trigger_branch="development"),
            expected_repository=REPOSITORY,
            isolation=self.safe_isolation(),
        )
        self.assertEqual(receipt.runner_decision, RunnerDecision.HOSTED_ONLY)
        self.assertIn("source_branch_mismatch", receipt.reason_codes)

    def test_failed_ci_or_wrong_workflow_is_blocked(self) -> None:
        for evidence in (
            self.evidence(conclusion="failure"),
            self.evidence(workflow_name="Other Workflow"),
        ):
            with self.subTest(evidence=evidence):
                receipt = evaluate_ci_trust(
                    evidence,
                    expected_repository=REPOSITORY,
                    isolation=self.safe_isolation(),
                )
                self.assertEqual(receipt.runner_decision, RunnerDecision.BLOCKED)
                self.assertFalse(receipt.self_hosted_execution_authorized)

    def test_each_unsafe_isolation_dimension_blocks_trusted_source(self) -> None:
        variants = (
            RunnerIsolationEvidence(False, True, True, False, False),
            RunnerIsolationEvidence(True, False, True, False, False),
            RunnerIsolationEvidence(True, True, False, False, False),
            RunnerIsolationEvidence(True, True, True, True, False),
            RunnerIsolationEvidence(True, True, True, False, True),
        )
        for isolation in variants:
            with self.subTest(isolation=isolation):
                receipt = evaluate_ci_trust(
                    self.evidence(),
                    expected_repository=REPOSITORY,
                    isolation=isolation,
                )
                self.assertEqual(receipt.runner_decision, RunnerDecision.BLOCKED)
                self.assertFalse(receipt.self_hosted_execution_authorized)

    def test_isolation_cannot_upgrade_untrusted_source(self) -> None:
        receipt = evaluate_ci_trust(
            self.evidence(
                trigger_event="pull_request",
                trigger_branch="feature/test",
            ),
            expected_repository=REPOSITORY,
            isolation=self.safe_isolation(),
        )
        self.assertNotEqual(
            receipt.runner_decision,
            RunnerDecision.PRIVATE_RUNNER_ELIGIBLE,
        )
        self.assertFalse(receipt.self_hosted_execution_authorized)

    def test_malformed_provenance_fails_closed(self) -> None:
        with self.assertRaises(CiTrustValidationError):
            self.evidence(source_sha="not-a-sha")
        with self.assertRaises(CiTrustValidationError):
            self.evidence(workflow_run_id=0)
        with self.assertRaises(CiTrustValidationError):
            RunnerIsolationEvidence(
                identity_restricted="yes",  # type: ignore[arg-type]
                workspace_ephemeral=True,
                source_execution_sandboxed=True,
                credentials_injected=False,
                private_network_access=False,
            )

    def test_receipt_serialization_is_deterministic_and_secret_free(self) -> None:
        first = evaluate_ci_trust(
            self.evidence(),
            expected_repository=REPOSITORY,
        )
        second = evaluate_ci_trust(
            self.evidence(),
            expected_repository=REPOSITORY,
        )
        self.assertEqual(first.to_json(), second.to_json())
        payload = json.loads(first.to_json())
        forbidden = {
            "token",
            "credential",
            "secret",
            "hostname",
            "ip_address",
            "mac_address",
            "runner_label",
            "private_key",
        }
        self.assertTrue(forbidden.isdisjoint(payload))

    def test_cli_preflight_never_authorizes_without_isolation_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "receipt.json"
            result = main(
                [
                    "evaluate",
                    "--expected-repository",
                    REPOSITORY,
                    "--expected-branch",
                    "main",
                    "--expected-workflow",
                    "CI",
                    "--trigger-repository",
                    REPOSITORY,
                    "--trigger-event",
                    "push",
                    "--trigger-branch",
                    "main",
                    "--trigger-workflow",
                    "CI",
                    "--source-sha",
                    SOURCE_SHA,
                    "--conclusion",
                    "success",
                    "--policy-sha",
                    POLICY_SHA,
                    "--workflow-run-id",
                    "42",
                    "--output",
                    str(output),
                ]
            )
            self.assertEqual(result, 0)
            receipt = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(receipt["runner_decision"], "requires_isolation")
            self.assertFalse(receipt["self_hosted_execution_authorized"])

    def test_preflight_workflow_is_hosted_read_only_and_never_executes_candidate_source(self) -> None:
        workflow = Path(".github/workflows/trusted-runner-gate.yml").read_text(
            encoding="utf-8"
        )
        lowered = workflow.lower()
        self.assertIn('workflows: ["CI"]', workflow)
        self.assertIn("workflow_run:", workflow)
        self.assertIn("runs-on: ubuntu-latest", workflow)
        self.assertIn("permissions:\n  contents: read", workflow)
        self.assertIn(
            "ref: ${{ github.event.repository.default_branch }}",
            workflow,
        )
        self.assertIn("persist-credentials: false", workflow)
        self.assertIn("python -m project.ci_trust evaluate", workflow)
        self.assertIn("POLICY_SHA=\"$(git rev-parse HEAD)\"", workflow)
        self.assertNotIn("self-hosted", lowered)
        self.assertNotIn("pull_request_target", lowered)
        self.assertNotIn("${{ secrets.", workflow)
        self.assertNotIn(
            "ref: ${{ github.event.workflow_run.head_sha }}",
            workflow,
        )


if __name__ == "__main__":
    unittest.main()
