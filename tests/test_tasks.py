from __future__ import annotations

import unittest

from mira.structured_state import InMemoryStructuredStateAdapter
from mira.tasks import TaskService, TaskTransitionError, TaskValidationError


class TaskServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.adapter = InMemoryStructuredStateAdapter(
            schema_version="mira-test-v1",
            resource_types=["task"],
            event_types=["created"],
        )
        self.tasks = TaskService(self.adapter)

    def test_create_read_update_and_explicit_completion_preserve_history(self) -> None:
        created = self.tasks.create(
            "task-air-filter",
            title="Change air filter",
            next_action="Buy the replacement filter.",
            priority="medium",
            due_date="2026-08-30",
            context="home",
            idempotency_key="create-air-filter",
        )
        self.assertEqual(created.revision, 1)
        self.assertTrue(created.active)

        updated = self.tasks.update(
            "task-air-filter",
            next_action="Install the replacement filter.",
            priority="high",
            idempotency_key="update-air-filter",
        )
        self.assertEqual(updated.revision, 2)
        self.assertEqual(updated.next_action, "Install the replacement filter.")
        self.assertEqual(updated.priority, "high")

        completed = self.tasks.complete(
            "task-air-filter",
            completed_at="2026-08-30T18:00:00-04:00",
            idempotency_key="complete-air-filter",
        )
        self.assertEqual(completed.revision, 3)
        self.assertEqual(completed.state, "completed")
        self.assertFalse(completed.active)
        self.assertEqual(self.tasks.active_tasks(context="home"), ())

        all_tasks = self.tasks.all_tasks()
        self.assertEqual(len(all_tasks), 1)
        self.assertEqual(all_tasks[0].state, "completed")
        self.assertEqual(all_tasks[0].completed_at, "2026-08-30T18:00:00-04:00")

    def test_completion_is_not_inferred_and_completed_task_requires_reopen_to_edit(self) -> None:
        self.tasks.create(
            "task-laundry",
            title="Put away laundry",
            next_action="Put the clean laundry in the closet.",
            idempotency_key="create-laundry",
        )
        self.assertEqual(self.tasks.get("task-laundry").state, "open")
        self.tasks.complete(
            "task-laundry",
            completed_at="2026-08-30T09:00:00-04:00",
            idempotency_key="complete-laundry",
        )
        with self.assertRaisesRegex(TaskTransitionError, "reopen"):
            self.tasks.update(
                "task-laundry",
                next_action="This must not silently edit history.",
                idempotency_key="bad-edit",
            )
        reopened = self.tasks.reopen(
            "task-laundry", idempotency_key="reopen-laundry"
        )
        self.assertEqual(reopened.state, "open")
        self.assertIsNone(reopened.completed_at)
        self.assertEqual(reopened.revision, 3)

    def test_cancelled_task_is_preserved_but_not_active(self) -> None:
        self.tasks.create(
            "task-old-order",
            title="Order old part",
            next_action="Place the obsolete order.",
            idempotency_key="create-old-order",
        )
        cancelled = self.tasks.cancel(
            "task-old-order", idempotency_key="cancel-old-order"
        )
        self.assertEqual(cancelled.state, "cancelled")
        self.assertEqual(self.tasks.active_tasks(), ())
        self.assertEqual(self.tasks.all_tasks()[0].state, "cancelled")

    def test_active_tasks_filter_context_and_sort_priority_due_then_id(self) -> None:
        cases = (
            ("low", "Low", "low", None, None),
            ("high-later", "High later", "high", "2026-09-10", None),
            ("high-soon", "High soon", "high", "2026-08-30", "home"),
            ("medium", "Medium", "medium", None, "road"),
            ("high-any", "High no due", "high", None, None),
        )
        for task_id, title, priority, due, context in cases:
            self.tasks.create(
                task_id,
                title=title,
                next_action=f"Do {title.lower()}.",
                priority=priority,
                due_date=due,
                context=context,
                idempotency_key=f"create-{task_id}",
            )
        self.assertEqual(
            [task.task_id for task in self.tasks.active_tasks()],
            ["high-soon", "high-later", "high-any", "medium", "low"],
        )
        self.assertEqual(
            [task.task_id for task in self.tasks.active_tasks(context="home")],
            ["high-soon", "high-later", "high-any", "low"],
        )
        self.assertEqual(
            [task.task_id for task in self.tasks.active_tasks(context="road")],
            ["high-later", "high-any", "medium", "low"],
        )

    def test_validation_rejects_blank_action_invalid_priority_self_parent_and_naive_completion(self) -> None:
        with self.assertRaises(TaskValidationError):
            self.tasks.create(
                "bad",
                title="Bad",
                next_action=" ",
                idempotency_key="bad-action",
            )
        with self.assertRaises(TaskValidationError):
            self.tasks.create(
                "bad2",
                title="Bad",
                next_action="Do it.",
                priority="urgent",
                idempotency_key="bad-priority",
            )
        with self.assertRaises(TaskValidationError):
            self.tasks.create(
                "self-parent",
                title="Bad",
                next_action="Do it.",
                parent_task_id="self-parent",
                idempotency_key="bad-parent",
            )
        self.tasks.create(
            "needs-time",
            title="Needs timestamp",
            next_action="Finish it.",
            idempotency_key="create-needs-time",
        )
        with self.assertRaises(TaskValidationError):
            self.tasks.complete(
                "needs-time",
                completed_at="2026-08-30T09:00:00",
                idempotency_key="naive-time",
            )


if __name__ == "__main__":
    unittest.main()
