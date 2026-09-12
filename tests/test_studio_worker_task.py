from __future__ import annotations

from dataclasses import replace
import json
import unittest

from mira.studio_competition import StudioChangeKind
from mira.studio_intake import StudioIntakeDraft, StudioIntakeNextAction
from ops.studio_execution_bridge import (
    StudioLocalExecutionPolicy,
    manifest_from_review_ready_intake,
)
from ops.studio_worker_task import (
    PortableStudioExecutionPolicy,
    PortableStudioWorkerTask,
    StudioModelPrivateBinding,
    StudioSourcePrivateBinding,
    StudioWorkerPrivateBindings,
    StudioWorkerTaskError,
    bind_portable_task,
    portable_task_from_review_ready_intake,
)


BASE_SHA = "b" * 40


class StudioWorkerTaskTests(unittest.TestCase):
    def draft(self, **changes) -> StudioIntakeDraft:
        values = {
            "draft_id": "intake-" + ("a" * 64),
            "registry_sha256": "c" * 64,
            "raw_request": "Implement the bounded Studio workflow I described.",
            "kind": StudioChangeKind.WORKFLOW,
            "desired_outcome": "Produce a tested reviewable candidate.",
            "feature_ids": ("STUDIO-001",),
            "dependency_ids": ("DEV-004", "LOCAL-001"),
            "explicit_constraints": ("Do not activate the candidate.",),
            "assumptions": ("An eligible local worker may be available.",),
            "unresolved_questions": (),
            "blockers": (),
            "review_ready": True,
            "next_action": StudioIntakeNextAction.REVIEW_DRAFT,
        }
        values.update(changes)
        return StudioIntakeDraft(**values)

    def policy(self, **changes) -> PortableStudioExecutionPolicy:
        values = {
            "source_binding_id": "source-mira-canonical",
            "base_sha": BASE_SHA,
            "branch_name": "studio/task-candidate",
            "allowed_paths": ("mira/example.py",),
            "test_argv": ("python", "-m", "unittest", "tests.test_example"),
            "model_profile_id": "coding-general",
            "max_rounds": 3,
            "wall_timeout_seconds": 600,
            "test_timeout_seconds": 120,
            "model_timeout_seconds": 180,
        }
        values.update(changes)
        return PortableStudioExecutionPolicy(**values)

    def bindings(self, **changes) -> StudioWorkerPrivateBindings:
        values = {
            "sources": (
                StudioSourcePrivateBinding(
                    source_binding_id="source-mira-canonical",
                    repo_path="/private/runtime/mira",
                ),
            ),
            "models": (
                StudioModelPrivateBinding(
                    model_profile_id="coding-general",
                    model_base_url="http://127.0.0.1:1234/v1",
                    model="concrete-private-model",
                ),
            ),
        }
        values.update(changes)
        return StudioWorkerPrivateBindings(**values)

    def task(self, **policy_changes) -> PortableStudioWorkerTask:
        return portable_task_from_review_ready_intake(
            self.draft(), self.policy(**policy_changes)
        )

    def test_review_ready_intake_projects_to_deterministic_portable_task(self):
        first = self.task()
        second = self.task()
        self.assertEqual(first, second)
        self.assertEqual(first.sha256, second.sha256)
        self.assertEqual(len(first.sha256), 64)
        payload = json.loads(first.canonical_bytes())
        self.assertEqual(payload["draft_id"], self.draft().draft_id)
        self.assertEqual(payload["source_binding_id"], "source-mira-canonical")
        self.assertEqual(payload["model_profile_id"], "coding-general")

    def test_portable_task_contains_no_physical_worker_binding_material(self):
        task = self.task()
        encoded = task.canonical_bytes().decode("utf-8")
        forbidden_keys = (
            '"repo_path"',
            '"model_base_url"',
            '"model"',
            '"hostname"',
            '"ip_address"',
            '"credential"',
            '"token"',
        )
        for value in forbidden_keys:
            with self.subTest(value=value):
                self.assertNotIn(value, encoded)
        self.assertNotIn("/private/runtime/mira", encoded)
        self.assertNotIn("127.0.0.1:1234", encoded)
        self.assertNotIn("concrete-private-model", encoded)

    def test_private_binding_repr_does_not_disclose_binding_values(self):
        bindings = self.bindings()
        rendered = repr(bindings)
        self.assertNotIn("/private/runtime/mira", rendered)
        self.assertNotIn("127.0.0.1:1234", rendered)
        self.assertNotIn("concrete-private-model", rendered)

    def test_binding_produces_existing_valid_worker_manifest_without_semantic_drift(self):
        draft = self.draft()
        task = portable_task_from_review_ready_intake(draft, self.policy())
        manifest = bind_portable_task(task, self.bindings())

        self.assertEqual(manifest.draft_id, task.draft_id)
        self.assertEqual(manifest.objective, task.objective)
        self.assertEqual(manifest.repo_path, "/private/runtime/mira")
        self.assertEqual(manifest.base_sha, BASE_SHA)
        self.assertEqual(manifest.branch_name, "studio/task-candidate")
        self.assertEqual(manifest.allowed_paths, ("mira/example.py",))
        self.assertEqual(manifest.test_argv, self.policy().test_argv)
        self.assertEqual(manifest.model_base_url, "http://127.0.0.1:1234/v1")
        self.assertEqual(manifest.model, "concrete-private-model")
        self.assertEqual(manifest.max_rounds, 3)
        self.assertEqual(manifest.wall_timeout_seconds, 600)
        manifest.validate()

        legacy_manifest = manifest_from_review_ready_intake(
            draft,
            StudioLocalExecutionPolicy(
                repo_path="/private/runtime/mira",
                base_sha=BASE_SHA,
                branch_name="studio/task-candidate",
                allowed_paths=("mira/example.py",),
                test_argv=self.policy().test_argv,
                model_base_url="http://127.0.0.1:1234/v1",
                model="concrete-private-model",
                max_rounds=3,
                wall_timeout_seconds=600,
                test_timeout_seconds=120,
                model_timeout_seconds=180,
            ),
        )
        self.assertEqual(manifest.objective, legacy_manifest.objective)

    def test_task_hash_binds_every_portable_execution_dimension(self):
        original = self.task()
        variants = (
            replace(original, branch_name="studio/other-candidate"),
            replace(original, model_profile_id="coding-review"),
            replace(original, max_rounds=4),
            replace(original, test_argv=("python", "-m", "unittest", "other")),
        )
        for variant in variants:
            with self.subTest(variant=variant):
                variant.validate()
                self.assertNotEqual(original.sha256, variant.sha256)

    def test_unready_intake_cannot_become_portable_execution_task(self):
        drafts = (
            self.draft(
                unresolved_questions=("Clarify behavior",),
                review_ready=False,
                next_action=StudioIntakeNextAction.CLARIFY_WITH_CUSTOMER,
            ),
            self.draft(
                blockers=("blocked",),
                review_ready=False,
                next_action=StudioIntakeNextAction.CLARIFY_WITH_CUSTOMER,
            ),
        )
        for draft in drafts:
            with self.subTest(draft=draft):
                with self.assertRaisesRegex(StudioWorkerTaskError, "review-ready"):
                    portable_task_from_review_ready_intake(draft, self.policy())

    def test_portable_policy_rejects_unsafe_or_noncanonical_controller_material(self):
        invalid = (
            self.policy(base_sha="not-a-sha"),
            self.policy(branch_name="../escape"),
            self.policy(allowed_paths=("../escape.py",)),
            self.policy(allowed_paths=("z.py", "a.py")),
            self.policy(allowed_paths=("mira/example.py", "mira/example.py")),
            self.policy(test_argv=()),
            self.policy(source_binding_id="bad binding"),
            self.policy(model_profile_id="bad/profile"),
            self.policy(max_rounds=0),
        )
        for policy in invalid:
            with self.subTest(policy=policy):
                with self.assertRaises(StudioWorkerTaskError):
                    policy.validate()

    def test_missing_or_duplicate_private_bindings_fail_closed(self):
        task = self.task()
        missing_source = StudioWorkerPrivateBindings(
            sources=(
                StudioSourcePrivateBinding("other-source", "/private/other"),
            ),
            models=self.bindings().models,
        )
        with self.assertRaisesRegex(StudioWorkerTaskError, "source binding"):
            bind_portable_task(task, missing_source)

        missing_model = StudioWorkerPrivateBindings(
            sources=self.bindings().sources,
            models=(
                StudioModelPrivateBinding(
                    "other-model", "http://127.0.0.1:1234/v1", "other"
                ),
            ),
        )
        with self.assertRaisesRegex(StudioWorkerTaskError, "model profile"):
            bind_portable_task(task, missing_model)

        duplicate_source = StudioWorkerPrivateBindings(
            sources=(
                StudioSourcePrivateBinding(
                    "source-mira-canonical", "/private/a"
                ),
                StudioSourcePrivateBinding(
                    "source-mira-canonical", "/private/b"
                ),
            ),
            models=self.bindings().models,
        )
        with self.assertRaisesRegex(StudioWorkerTaskError, "duplicate source"):
            bind_portable_task(task, duplicate_source)

        duplicate_model = StudioWorkerPrivateBindings(
            sources=self.bindings().sources,
            models=(
                StudioModelPrivateBinding(
                    "coding-general", "http://127.0.0.1:1234/v1", "a"
                ),
                StudioModelPrivateBinding(
                    "coding-general", "http://127.0.0.1:4321/v1", "b"
                ),
            ),
        )
        with self.assertRaisesRegex(StudioWorkerTaskError, "duplicate model"):
            bind_portable_task(task, duplicate_model)

    def test_non_loopback_private_model_binding_is_rejected_by_existing_manifest_gate(self):
        bindings = StudioWorkerPrivateBindings(
            sources=self.bindings().sources,
            models=(
                StudioModelPrivateBinding(
                    "coding-general",
                    "https://example.com/v1",
                    "concrete-private-model",
                ),
            ),
        )
        with self.assertRaisesRegex(StudioWorkerTaskError, "loopback"):
            bind_portable_task(self.task(), bindings)

    def test_private_bindings_cannot_rewrite_portable_controller_policy(self):
        task = self.task()
        bindings = StudioWorkerPrivateBindings(
            sources=(
                StudioSourcePrivateBinding(
                    task.source_binding_id, "/another/private/source"
                ),
            ),
            models=(
                StudioModelPrivateBinding(
                    task.model_profile_id,
                    "http://localhost:9999/v1",
                    "another-concrete-model",
                ),
            ),
        )
        manifest = bind_portable_task(task, bindings)
        self.assertEqual(manifest.objective, task.objective)
        self.assertEqual(manifest.base_sha, task.base_sha)
        self.assertEqual(manifest.branch_name, task.branch_name)
        self.assertEqual(manifest.allowed_paths, task.allowed_paths)
        self.assertEqual(manifest.test_argv, task.test_argv)
        self.assertEqual(manifest.max_rounds, task.max_rounds)
        self.assertEqual(manifest.repo_path, "/another/private/source")
        self.assertEqual(manifest.model, "another-concrete-model")


if __name__ == "__main__":
    unittest.main()
