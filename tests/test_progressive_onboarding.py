from __future__ import annotations

import unittest

from mira.onboarding import (
    COMPLETION_ORIENTATION,
    DISCOVERY_TOPIC_IDS,
    InterviewLedgerService,
    OnboardingValidationError,
    ProgressiveDiscoveryService,
)
from mira.structured_state import InMemoryStructuredStateAdapter


class ProgressiveDiscoveryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.adapter = InMemoryStructuredStateAdapter(
            schema_version="mira-test-v1",
            resource_types=["onboarding_ledger"],
            event_types=["created"],
        )
        self.minimum = InterviewLedgerService(self.adapter)
        self.discovery = ProgressiveDiscoveryService(self.adapter)

    def test_discovery_requires_completed_minimum_setup(self) -> None:
        self.minimum.start_or_resume()
        with self.assertRaisesRegex(OnboardingValidationError, "completed Minimum Useful Setup"):
            self.discovery.start_or_resume()

    def test_completion_orientation_offers_continue_or_use_mira(self) -> None:
        completed = self._complete_minimum()
        self.assertEqual(completed.completion_orientation, COMPLETION_ORIENTATION)
        self.assertIn("continue setup now", COMPLETION_ORIENTATION)
        self.assertIn("start using MIRA", COMPLETION_ORIENTATION)
        self.assertIn("at most one short discovery topic per local day", COMPLETION_ORIENTATION)

    def test_continue_now_starts_with_fitness_then_asks_goals(self) -> None:
        self._complete_minimum()
        started = self.discovery.start_or_resume()
        self.assertEqual(started.status, "choice_pending")
        chosen = self.discovery.choose_mode(
            "continue setup now", idempotency_key="choose-continue"
        )
        self.assertEqual(chosen.mode, "continue_now")
        self.assertEqual(chosen.next_topic.topic_id, "fitness_wellness")

        accepted = self.discovery.answer_topic(
            "fitness_wellness",
            True,
            idempotency_key="fitness-yes",
        )
        self.assertEqual(accepted.topic_states["fitness_wellness"], "needs_details")
        self.assertIn("What are your goals", accepted.followup_prompt)

        goals = self.discovery.answer_followup(
            "fitness_wellness",
            "Build strength, improve cardio, and use activity accountability.",
            idempotency_key="fitness-goals",
        )
        self.assertEqual(goals.topic_states["fitness_wellness"], "accepted")
        self.assertEqual(goals.next_topic.topic_id, "meals_groceries")
        self.assertEqual(
            goals.answers["fitness_wellness"]["details"],
            "Build strength, improve cardio, and use activity accountability.",
        )

    def test_fitness_decline_moves_on_without_followup(self) -> None:
        self._complete_minimum()
        self.discovery.choose_mode("continue", idempotency_key="choose")
        declined = self.discovery.answer_topic(
            "fitness_wellness",
            False,
            idempotency_key="fitness-no",
        )
        self.assertEqual(declined.topic_states["fitness_wellness"], "declined")
        self.assertIsNone(declined.followup_prompt)
        self.assertEqual(declined.next_topic.topic_id, "meals_groceries")

    def test_start_using_mira_emits_at_most_one_topic_per_local_day(self) -> None:
        self._complete_minimum()
        chosen = self.discovery.choose_mode(
            "start using MIRA", idempotency_key="choose-use"
        )
        self.assertTrue(chosen.brief_drip_enabled)

        first = self.discovery.claim_brief_question(
            "2026-08-30", idempotency_key="brief-day-1"
        )
        self.assertTrue(first.brief_topic_emitted)
        self.assertEqual(first.next_topic.topic_id, "fitness_wellness")
        self.assertEqual(first.brief_topic_days_used, 1)

        duplicate = self.discovery.claim_brief_question(
            "2026-08-30", idempotency_key="brief-day-1-again"
        )
        self.assertFalse(duplicate.brief_topic_emitted)
        self.assertEqual(duplicate.brief_topic_days_used, 1)

        # Silence is not an answer and does not advance to a second topic.
        next_day_silence = self.discovery.claim_brief_question(
            "2026-08-31", idempotency_key="brief-day-2-silence"
        )
        self.assertFalse(next_day_silence.brief_topic_emitted)
        self.assertEqual(next_day_silence.next_topic.topic_id, "fitness_wellness")

        self.discovery.skip_topic(
            "fitness_wellness", idempotency_key="skip-fitness"
        )
        second = self.discovery.claim_brief_question(
            "2026-08-31", idempotency_key="brief-day-2"
        )
        self.assertTrue(second.brief_topic_emitted)
        self.assertEqual(second.next_topic.topic_id, "meals_groceries")
        self.assertEqual(second.brief_topic_days_used, 2)

    def test_seven_topic_days_complete_without_deleting_history(self) -> None:
        self._complete_minimum()
        self.discovery.choose_mode("use MIRA", idempotency_key="choose-use")
        for index, topic_id in enumerate(DISCOVERY_TOPIC_IDS, start=1):
            day = f"2026-09-{index:02d}"
            emitted = self.discovery.claim_brief_question(
                day, idempotency_key=f"claim-{index}"
            )
            self.assertTrue(emitted.brief_topic_emitted)
            self.assertEqual(emitted.next_topic.topic_id, topic_id)
            if topic_id == "fitness_wellness":
                self.discovery.answer_topic(
                    topic_id,
                    False,
                    idempotency_key=f"answer-{index}",
                )
            else:
                self.discovery.answer_topic(
                    topic_id,
                    False,
                    idempotency_key=f"answer-{index}",
                )
        finished = self.discovery.start_or_resume()
        self.assertTrue(finished.complete)
        self.assertFalse(finished.brief_drip_enabled)
        self.assertEqual(finished.brief_topic_days_used, 7)
        self.assertEqual(finished.remaining_topic_ids, ())
        self.assertEqual(set(finished.topic_states), set(DISCOVERY_TOPIC_IDS))

    def test_brief_drip_can_be_disabled_and_state_resumes(self) -> None:
        self._complete_minimum()
        self.discovery.choose_mode("start", idempotency_key="choose")
        self.discovery.claim_brief_question(
            "2026-08-30", idempotency_key="claim"
        )
        paused = self.discovery.disable_brief_drip(idempotency_key="disable")
        self.assertEqual(paused.status, "paused")
        self.assertFalse(paused.brief_drip_enabled)

        restarted = ProgressiveDiscoveryService(self.adapter).start_or_resume()
        self.assertEqual(restarted.revision, paused.revision)
        self.assertEqual(restarted.next_topic.topic_id, "fitness_wellness")
        self.assertFalse(restarted.brief_drip_enabled)

        continued = ProgressiveDiscoveryService(self.adapter).choose_mode(
            "continue setup now", idempotency_key="resume-now"
        )
        self.assertEqual(continued.mode, "continue_now")
        self.assertEqual(continued.next_topic.topic_id, "fitness_wellness")

    def _complete_minimum(self):
        self.minimum.start_or_resume()
        self.minimum.answer(
            "timezone", "America/New_York", idempotency_key="tz"
        )
        self.minimum.answer(
            "life_pattern",
            "I work, study, travel, and manage a household.",
            idempotency_key="life",
        )
        self.minimum.answer(
            "goals",
            "Remember commitments, organize life, and keep projects moving.",
            idempotency_key="goals",
        )
        return self.minimum.answer(
            "appointment_help",
            {"wants_help": True, "calendar_lane": "Google"},
            idempotency_key="appointments",
        )


if __name__ == "__main__":
    unittest.main()
