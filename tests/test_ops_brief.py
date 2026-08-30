from __future__ import annotations

from datetime import datetime, timezone
import unittest

from mira.onboarding import InterviewLedgerService, ProgressiveDiscoveryService
from mira.ops_brief import OpsBriefNotDueError, OpsBriefService
from mira.structured_state import InMemoryStructuredStateAdapter
from mira.tasks import TaskService


class OpsBriefServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.adapter = InMemoryStructuredStateAdapter(
            schema_version="mira-test-v1",
            resource_types=["task", "ops_brief_run", "onboarding_ledger"],
            event_types=["created"],
        )
        self.tasks = TaskService(self.adapter)
        self.briefs = OpsBriefService(self.adapter, task_service=self.tasks)

    def test_clock_gate_is_dst_safe_and_run_ids_are_deterministic(self) -> None:
        am = self.briefs.compose_due(
            datetime(2026, 8, 30, 6, 45, tzinfo=timezone.utc),
            timezone_name="America/New_York",
        )
        self.assertEqual(am.run_id, "ops-brief:2026-08-30:am")
        self.assertEqual(am.scheduled_local, "2026-08-30T02:45:00-04:00")
        self.assertEqual(am.scheduled_utc, "2026-08-30T06:45:00+00:00")
        self.assertFalse(am.delivered)

        pm = self.briefs.compose_due(
            datetime(2026, 8, 30, 18, 45, tzinfo=timezone.utc),
            timezone_name="America/New_York",
        )
        self.assertEqual(pm.run_id, "ops-brief:2026-08-30:pm")
        self.assertEqual(pm.scheduled_local, "2026-08-30T14:45:00-04:00")

        with self.assertRaises(OpsBriefNotDueError):
            self.briefs.compose_due(
                datetime(2026, 8, 30, 18, 44, tzinfo=timezone.utc),
                timezone_name="America/New_York",
            )

    def test_task_brief_orders_priority_and_due_and_uses_one_action_per_line(self) -> None:
        self.tasks.create(
            "medium",
            title="Put away laundry",
            next_action="Put the clean laundry in the closet.",
            priority="medium",
            context="home",
            idempotency_key="create-medium",
        )
        self.tasks.create(
            "high-later",
            title="Replace air filter",
            next_action="Install the replacement filter.",
            priority="high",
            due_date="2026-09-02",
            context="home",
            idempotency_key="create-high-later",
        )
        self.tasks.create(
            "high-overdue",
            title="Order lug nuts",
            next_action="Place the order for the selected lug nuts.",
            priority="high",
            due_date="2026-08-28",
            idempotency_key="create-high-overdue",
        )
        self.tasks.create(
            "road-only",
            title="Road task",
            next_action="Do the road-only thing.",
            priority="high",
            context="road",
            idempotency_key="create-road",
        )

        brief = self.briefs.compose_slot(
            "2026-08-30",
            "am",
            timezone_name="America/New_York",
            context="home",
        )
        lines = brief.rendered_text.splitlines()
        action_lines = [line for line in lines if line.startswith("- [")]
        self.assertEqual(
            action_lines,
            [
                "- [HIGH] [OVERDUE 2026-08-28] Order lug nuts: Place the order for the selected lug nuts.",
                "- [HIGH] [due 2026-09-02] Replace air filter: Install the replacement filter.",
                "- [MEDIUM] Put away laundry: Put the clean laundry in the closet.",
            ],
        )
        self.assertNotIn("Road task", brief.rendered_text)
        self.assertEqual(
            brief.task_ids, ("high-overdue", "high-later", "medium")
        )

    def test_completed_task_is_preserved_but_removed_from_future_brief(self) -> None:
        self.tasks.create(
            "done-later",
            title="Finish the thing",
            next_action="Finish it.",
            priority="high",
            idempotency_key="create-done-later",
        )
        first = self.briefs.compose_slot(
            "2026-08-30", "am", timezone_name="America/New_York"
        )
        self.assertIn("Finish the thing", first.rendered_text)

        self.tasks.complete(
            "done-later",
            completed_at="2026-08-30T10:00:00-04:00",
            idempotency_key="complete-done-later",
        )
        second = self.briefs.compose_slot(
            "2026-08-30", "pm", timezone_name="America/New_York"
        )
        self.assertNotIn("Finish the thing", second.rendered_text)
        self.assertEqual(self.tasks.get("done-later").state, "completed")

    def test_same_run_is_immutable_replay_even_if_task_changes_after_composition(self) -> None:
        self.tasks.create(
            "immutable",
            title="Original title",
            next_action="Do the original action.",
            idempotency_key="create-immutable",
        )
        first = self.briefs.compose_slot(
            "2026-08-30", "am", timezone_name="America/New_York"
        )
        self.tasks.update(
            "immutable",
            title="Changed title",
            next_action="Do the changed action.",
            idempotency_key="update-immutable",
        )
        replay = self.briefs.compose_slot(
            "2026-08-30", "am", timezone_name="America/New_York"
        )
        self.assertTrue(replay.idempotent_replay)
        self.assertEqual(replay.rendered_text, first.rendered_text)
        self.assertIn("Original title", replay.rendered_text)
        self.assertNotIn("Changed title", replay.rendered_text)

        later = self.briefs.compose_slot(
            "2026-08-30", "pm", timezone_name="America/New_York"
        )
        self.assertIn("Changed title", later.rendered_text)

    def test_empty_optional_sections_are_omitted_not_fabricated(self) -> None:
        brief = self.briefs.compose_slot(
            "2026-08-30", "am", timezone_name="America/New_York"
        )
        self.assertIn("- No active tasks.", brief.rendered_text)
        for unavailable in ("Weather", "Orders", "Email", "Calendar", "Mileage"):
            self.assertNotIn(unavailable, brief.rendered_text)

    def test_progressive_discovery_can_appear_once_in_one_daily_brief(self) -> None:
        interview = InterviewLedgerService(self.adapter)
        interview.start_or_resume()
        interview.answer("timezone", "America/New_York", idempotency_key="tz")
        interview.answer(
            "life_pattern",
            "I work, study, travel, and manage a household.",
            idempotency_key="life",
        )
        interview.answer(
            "goals",
            "Keep commitments and projects organized.",
            idempotency_key="goals",
        )
        interview.answer(
            "appointment_help",
            {"wants_help": False, "calendar_lane": None},
            idempotency_key="appointments",
        )
        discovery = ProgressiveDiscoveryService(self.adapter)
        discovery.choose_mode("start using MIRA", idempotency_key="choose-drip")
        briefs = OpsBriefService(
            self.adapter,
            task_service=self.tasks,
            discovery_service=discovery,
        )

        am = briefs.compose_slot(
            "2026-08-30", "am", timezone_name="America/New_York"
        )
        self.assertEqual(am.discovery_topic_id, "fitness_wellness")
        self.assertIn("fitness, activity, nutrition", am.rendered_text)

        pm = briefs.compose_slot(
            "2026-08-30", "pm", timezone_name="America/New_York"
        )
        self.assertIsNone(pm.discovery_topic_id)
        self.assertNotIn("Optional setup", pm.rendered_text)

        state = discovery.start_or_resume()
        self.assertEqual(state.topic_states["fitness_wellness"], "unanswered")
        self.assertEqual(state.brief_topic_days_used, 1)


if __name__ == "__main__":
    unittest.main()
