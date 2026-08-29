"""Mutation-mode guard tests for the Personal native Workspace client."""

import unittest

from mira.structured_state import ValidationError
from mira.workspace_native import (
    WorkspaceQueuedWriterRequiredError,
    plan_workspace_upsert,
)


class WorkspaceMutationModeTests(unittest.TestCase):
    def plan(self, **overrides):
        values = {
            "resource_type": "entity",
            "resource_id": "entity-queued-001",
            "payload": {"state": "created"},
            "idempotency_key": "idem-queued-001",
            "expected_revision": 0,
            "resource_rows": [],
            "idempotency_rows": [],
        }
        values.update(overrides)
        return plan_workspace_upsert(**values)

    def test_direct_single_writer_mode_remains_default_for_personal_lane(self) -> None:
        plan = self.plan()
        self.assertEqual(plan.record.revision, 1)
        self.assertFalse(plan.idempotent_replay)

    def test_queued_writer_mode_refuses_direct_native_mutation(self) -> None:
        with self.assertRaisesRegex(
            WorkspaceQueuedWriterRequiredError,
            "canonical command inbox",
        ):
            self.plan(mutation_mode="queued_writer")

    def test_unknown_mutation_mode_fails_validation(self) -> None:
        with self.assertRaisesRegex(ValidationError, "mutation_mode"):
            self.plan(mutation_mode="mystery-writer")


if __name__ == "__main__":
    unittest.main()
