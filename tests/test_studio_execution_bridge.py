from __future__ import annotations

import json
import sys
import unittest

from mira.studio_competition import StudioChangeKind
from mira.studio_intake import (
    StudioIntakeDraft,
    StudioIntakeNextAction,
)
from ops.studio_execution_bridge import (
    StudioLocalExecutionPolicy,
    manifest_from_review_ready_intake,
)
from ops.studio_local_worker import StudioWorkerError


class StudioExecutionBridgeTests(unittest.TestCase):
    def draft(self, *, ready: bool = True) -> StudioIntakeDraft:
        questions = () if ready else ("Which account may be changed?",)
        blockers = () if ready else (
            "clarification_required:Which account may be changed?",
        )
        return StudioIntakeDraft(
            draft_id="intake-" + ("a" * 64),
            registry_sha256="b" * 64,
            raw_request="Build the requested workflow without touching production data.",
            kind=StudioChangeKind.WORKFLOW,
            desired_outcome="Create a bounded workflow implementation.",
            feature_ids=("STUDIO-001",),
            dependency_ids=("AUTH-001",),
            explicit_constraints=("Do not touch production data.",),
            assumptions=("A local coding worker is available.",),
            unresolved_questions=questions,
            blockers=blockers,
            review_ready=ready,
            next_action=(
                StudioIntakeNextAction.REVIEW_DRAFT
                if ready
                else StudioIntakeNextAction.CLARIFY_WITH_CUSTOMER
            ),
        )

    def policy(self, *, endpoint: str = "http://127.0.0.1:1234/v1"):
        return StudioLocalExecutionPolicy(
            repo_path="/synthetic/repo",
            base_sha="c" * 40,
            branch_name="studio/synthetic-change",
            allowed_paths=("mira/example.py",),
            test_argv=(sys.executable, "-m", "unittest", "tests.test_example"),
            model_base_url=endpoint,
            model="local-coding-model",
            max_rounds=4,
            wall_timeout_seconds=600,
            test_timeout_seconds=90,
            model_timeout_seconds=120,
        )

    def test_review_ready_intake_binds_to_controller_policy(self):
        draft = self.draft()
        policy = self.policy()
        manifest = manifest_from_review_ready_intake(draft, policy)

        self.assertEqual(manifest.draft_id, draft.draft_id)
        self.assertEqual(manifest.repo_path, policy.repo_path)
        self.assertEqual(manifest.base_sha, policy.base_sha)
        self.assertEqual(manifest.branch_name, policy.branch_name)
        self.assertEqual(manifest.allowed_paths, policy.allowed_paths)
        self.assertEqual(manifest.test_argv, policy.test_argv)
        self.assertEqual(manifest.model_base_url, policy.model_base_url)
        self.assertEqual(manifest.model, policy.model)
        self.assertEqual(manifest.max_rounds, 4)

        objective = json.loads(manifest.objective)
        self.assertEqual(objective["customer_request"], draft.raw_request)
        self.assertEqual(objective["desired_outcome"], draft.desired_outcome)
        self.assertEqual(
            objective["explicit_customer_constraints"],
            ["Do not touch production data."],
        )
        self.assertEqual(
            objective["model_assumptions"],
            ["A local coding worker is available."],
        )
        self.assertEqual(objective["feature_ids"], ["STUDIO-001"])
        self.assertEqual(objective["dependency_ids"], ["AUTH-001"])
        self.assertEqual(
            objective["intake_projection_sha256"], draft.projection_sha256
        )

    def test_unresolved_customer_question_cannot_enter_execution(self):
        with self.assertRaisesRegex(StudioWorkerError, "review-ready"):
            manifest_from_review_ready_intake(self.draft(ready=False), self.policy())

    def test_execution_policy_cannot_bypass_loopback_gate(self):
        with self.assertRaisesRegex(StudioWorkerError, "loopback"):
            manifest_from_review_ready_intake(
                self.draft(), self.policy(endpoint="https://example.com/v1")
            )

    def test_bridge_does_not_grant_activation_or_merge_authority(self):
        manifest = manifest_from_review_ready_intake(self.draft(), self.policy())
        self.assertFalse(hasattr(manifest, "merge_authorized"))
        self.assertFalse(hasattr(manifest, "activation_authorized"))
        self.assertFalse(hasattr(manifest, "push_authorized"))


if __name__ == "__main__":
    unittest.main()
