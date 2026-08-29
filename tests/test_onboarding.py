from __future__ import annotations

import unittest

from mira.onboarding import (
    AnswerConflictError,
    COMPLETION_ORIENTATION,
    InterviewLedgerService,
    OnboardingValidationError,
    QUESTION_IDS,
    QUESTIONS,
    QuestionOrderError,
)
from mira.structured_state import InMemoryStructuredStateAdapter


class InterviewLedgerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.adapter = InMemoryStructuredStateAdapter(
            schema_version="mira-test-v1",
            resource_types=["onboarding_ledger"],
            event_types=["created"],
        )
        self.service = InterviewLedgerService(self.adapter)

    def test_fresh_start_persists_empty_ledger_and_first_question(self) -> None:
        view = self.service.start_or_resume()
        self.assertEqual(view.revision, 1)
        self.assertFalse(view.complete)
        self.assertEqual(view.answers, {})
        self.assertIsNotNone(view.next_question)
        self.assertEqual(view.next_question.question_id, "timezone")

        resumed = self.service.start_or_resume()
        self.assertEqual(resumed.revision, 1)
        self.assertEqual(resumed.next_question.question_id, "timezone")

    def test_exactly_four_canonical_questions_and_no_name_question(self) -> None:
        self.assertEqual(
            QUESTION_IDS,
            ("timezone", "life_pattern", "goals", "appointment_help"),
        )
        combined = " ".join(question.prompt.lower() for question in QUESTIONS)
        self.assertNotIn("rename mira", combined)
        self.assertNotIn("what should i call", combined)
        self.assertNotIn("choose a name", combined)

    def test_answers_advance_in_order_and_resume(self) -> None:
        self.service.start_or_resume()
        first = self.service.answer(
            "timezone",
            "America/New_York",
            idempotency_key="answer-timezone-1",
        )
        self.assertEqual(first.revision, 2)
        self.assertEqual(first.answers["timezone"], {"iana_timezone": "America/New_York"})
        self.assertEqual(first.next_question.question_id, "life_pattern")

        resumed = self.service.start_or_resume()
        self.assertEqual(resumed.revision, 2)
        self.assertEqual(resumed.next_question.question_id, "life_pattern")

    def test_out_of_order_answer_fails(self) -> None:
        self.service.start_or_resume()
        with self.assertRaises(QuestionOrderError):
            self.service.answer(
                "goals",
                "Keep track of projects.",
                idempotency_key="bad-order",
            )

    def test_invalid_timezone_fails(self) -> None:
        self.service.start_or_resume()
        with self.assertRaisesRegex(OnboardingValidationError, "IANA"):
            self.service.answer(
                "timezone",
                "Definitely/The-Moon",
                idempotency_key="bad-timezone",
            )

    def test_repeat_same_answer_is_read_only_replay(self) -> None:
        self.service.start_or_resume()
        first = self.service.answer(
            "timezone",
            "America/New_York",
            idempotency_key="tz-first",
        )
        replay = self.service.answer(
            "timezone",
            "America/New_York",
            idempotency_key="tz-second",
        )
        self.assertEqual(replay.revision, first.revision)
        self.assertTrue(replay.idempotent_replay)

    def test_material_reanswer_requires_explicit_replace(self) -> None:
        self.service.start_or_resume()
        self.service.answer(
            "timezone",
            "America/New_York",
            idempotency_key="tz-first",
        )
        with self.assertRaises(AnswerConflictError):
            self.service.answer(
                "timezone",
                "America/Chicago",
                idempotency_key="tz-change",
            )

        changed = self.service.answer(
            "timezone",
            "America/Chicago",
            idempotency_key="tz-change-explicit",
            replace=True,
        )
        self.assertEqual(changed.answers["timezone"]["iana_timezone"], "America/Chicago")

    def test_appointment_preference_does_not_fake_activation(self) -> None:
        self._answer_first_three()
        view = self.service.answer(
            "appointment_help",
            {"wants_help": True, "calendar_lane": "Google Calendar"},
            idempotency_key="appointments-1",
        )
        appointment = view.answers["appointment_help"]
        self.assertEqual(appointment["calendar_lane_requested"], "google")
        self.assertFalse(appointment["calendar_capability_verified"])
        self.assertFalse(appointment["calendar_projection_active"])
        self.assertFalse(appointment["appointment_service_activated"])

    def test_declining_appointment_help_has_no_calendar_lane(self) -> None:
        self._answer_first_three()
        view = self.service.answer(
            "appointment_help",
            {"wants_help": False, "calendar_lane": None},
            idempotency_key="appointments-no",
        )
        appointment = view.answers["appointment_help"]
        self.assertIsNone(appointment["calendar_lane_requested"])
        self.assertFalse(appointment["appointment_service_activated"])

    def test_completion_only_after_all_four_and_has_orientation(self) -> None:
        self._answer_first_three()
        before = self.service.get()
        self.assertFalse(before.complete)
        self.assertIsNone(before.completion_orientation)

        completed = self.service.answer(
            "appointment_help",
            {"wants_help": True, "calendar_lane": "Apple/iCloud"},
            idempotency_key="appointments-final",
        )
        self.assertTrue(completed.complete)
        self.assertIsNone(completed.next_question)
        self.assertEqual(completed.completion_orientation, COMPLETION_ORIENTATION)
        self.assertIn("continue the interview", completed.completion_orientation)
        self.assertIn("MIRA Studio", completed.completion_orientation)
        self.assertIn("sharing is optional", completed.completion_orientation)

    def test_text_answers_are_trimmed_and_json_compatible(self) -> None:
        self.service.start_or_resume()
        self.service.answer(
            "timezone",
            "America/New_York",
            idempotency_key="tz",
        )
        view = self.service.answer(
            "life_pattern",
            "  I work, study, and manage a household.  ",
            idempotency_key="life",
        )
        self.assertEqual(
            view.answers["life_pattern"],
            {"text": "I work, study, and manage a household."},
        )

    def _answer_first_three(self) -> None:
        self.service.start_or_resume()
        self.service.answer(
            "timezone",
            "America/New_York",
            idempotency_key="tz",
        )
        self.service.answer(
            "life_pattern",
            "I work, study, and manage a household.",
            idempotency_key="life",
        )
        self.service.answer(
            "goals",
            "Remember commitments and keep projects moving.",
            idempotency_key="goals",
        )


if __name__ == "__main__":
    unittest.main()
