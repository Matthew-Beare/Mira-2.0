from __future__ import annotations

import inspect
import unittest

from mira.people_tracker import (
    CareerInteractionService,
    DEFAULT_TRACKER_PROJECTION,
    PeopleTrackerValidationError,
    interaction_row,
    relationship_columns,
)
from mira.structured_state import InMemoryStructuredStateAdapter


class CareerInteractionServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.adapter = InMemoryStructuredStateAdapter(
            schema_version="mira-career-test-v1",
            resource_types=["career_interaction"],
            event_types=["unused"],
        )
        self.service = CareerInteractionService(self.adapter)

    def test_outbound_message_tracks_contact_and_awaiting_reply(self) -> None:
        recorded = self.service.record(
            "int-001",
            person_id="person-ada",
            company_id="company-acme",
            job_id="job-neteng",
            channel="linkedin",
            direction="outbound",
            kind="message",
            occurred_at="2026-09-07T18:00:00-04:00",
            outcome="sent",
            summary="Asked about the network team and early-career hiring path.",
            follow_up_due="2026-09-12",
            idempotency_key="record-int-001",
        )
        self.assertEqual(recorded.revision, 1)
        summary = self.service.relationship_summary("person-ada")
        self.assertTrue(summary.have_i_contacted_them)
        self.assertFalse(summary.have_they_replied)
        self.assertTrue(summary.awaiting_reply)
        self.assertEqual(summary.relationship_state, "awaiting_reply")
        self.assertEqual(summary.follow_up_due, "2026-09-12")

    def test_inbound_reply_links_to_outbound_and_clears_awaiting_reply(self) -> None:
        self.service.record(
            "int-001",
            person_id="person-ada",
            channel="email",
            direction="outbound",
            kind="email",
            occurred_at="2026-09-07T18:00:00-04:00",
            outcome="sent",
            idempotency_key="record-int-001",
        )
        self.service.record(
            "int-002",
            person_id="person-ada",
            channel="email",
            direction="inbound",
            kind="reply",
            occurred_at="2026-09-08T09:15:00-04:00",
            outcome="replied",
            reply_to_interaction_id="int-001",
            summary="Replied with team context and offered to answer questions.",
            idempotency_key="record-int-002",
        )
        summary = self.service.relationship_summary("person-ada")
        self.assertTrue(summary.have_i_contacted_them)
        self.assertTrue(summary.have_they_replied)
        self.assertFalse(summary.awaiting_reply)
        self.assertEqual(summary.relationship_state, "replied")
        self.assertEqual(summary.last_channel, "email")
        self.assertEqual(summary.interaction_count, 2)

    def test_new_outbound_after_reply_returns_to_awaiting_reply(self) -> None:
        self.service.record(
            "int-001",
            person_id="person-ada",
            channel="linkedin",
            direction="outbound",
            kind="message",
            occurred_at="2026-09-07T18:00:00-04:00",
            outcome="sent",
            idempotency_key="record-int-001",
        )
        self.service.record(
            "int-002",
            person_id="person-ada",
            channel="linkedin",
            direction="inbound",
            kind="reply",
            occurred_at="2026-09-08T09:00:00-04:00",
            outcome="replied",
            reply_to_interaction_id="int-001",
            idempotency_key="record-int-002",
        )
        self.service.record(
            "int-003",
            person_id="person-ada",
            channel="linkedin",
            direction="outbound",
            kind="follow_up",
            occurred_at="2026-09-08T14:00:00-04:00",
            outcome="sent",
            follow_up_due="2026-09-13",
            idempotency_key="record-int-003",
        )
        summary = self.service.relationship_summary("person-ada")
        self.assertTrue(summary.have_they_replied)
        self.assertTrue(summary.awaiting_reply)
        self.assertEqual(summary.relationship_state, "awaiting_reply")

    def test_timezone_normalization_orders_interactions_by_actual_instant(self) -> None:
        self.service.record(
            "int-later",
            person_id="person-ada",
            channel="email",
            direction="outbound",
            kind="message",
            occurred_at="2026-09-08T09:30:00-04:00",
            outcome="sent",
            idempotency_key="later",
        )
        self.service.record(
            "int-earlier",
            person_id="person-ada",
            channel="email",
            direction="inbound",
            kind="reply",
            occurred_at="2026-09-08T14:00:00+01:00",
            outcome="replied",
            idempotency_key="earlier",
        )
        interactions = self.service.for_person("person-ada")
        self.assertEqual([item.interaction_id for item in interactions], ["int-earlier", "int-later"])
        self.assertEqual(interactions[0].occurred_at, "2026-09-08T13:00:00Z")
        self.assertEqual(interactions[1].occurred_at, "2026-09-08T13:30:00Z")

    def test_follow_up_uses_earliest_due_date(self) -> None:
        self.service.record(
            "int-001",
            person_id="person-ada",
            channel="email",
            direction="outbound",
            kind="message",
            occurred_at="2026-09-07T18:00:00-04:00",
            outcome="sent",
            follow_up_due="2026-09-15",
            idempotency_key="record-int-001",
        )
        self.service.record(
            "int-002",
            person_id="person-ada",
            channel="linkedin",
            direction="outbound",
            kind="follow_up",
            occurred_at="2026-09-08T18:00:00-04:00",
            outcome="sent",
            follow_up_due="2026-09-11",
            idempotency_key="record-int-002",
        )
        self.assertEqual(
            self.service.relationship_summary("person-ada").follow_up_due,
            "2026-09-11",
        )

    def test_conversation_and_referral_states_outrank_simple_reply(self) -> None:
        self.service.record(
            "int-001",
            person_id="person-ada",
            channel="phone",
            direction="outbound",
            kind="call",
            occurred_at="2026-09-07T18:00:00-04:00",
            outcome="conversation",
            idempotency_key="record-int-001",
        )
        self.service.record(
            "int-002",
            person_id="person-ada",
            channel="email",
            direction="inbound",
            kind="referral",
            occurred_at="2026-09-08T09:15:00-04:00",
            outcome="referral",
            idempotency_key="record-int-002",
        )
        self.assertEqual(
            self.service.relationship_summary("person-ada").relationship_state,
            "referral",
        )

    def test_record_is_idempotent_for_exact_replay(self) -> None:
        kwargs = dict(
            person_id="person-ada",
            channel="linkedin",
            direction="outbound",
            kind="connection_request",
            occurred_at="2026-09-07T18:00:00-04:00",
            outcome="sent",
            idempotency_key="record-int-001",
        )
        first = self.service.record("int-001", **kwargs)
        second = self.service.record("int-001", **kwargs)
        self.assertFalse(first.idempotent_replay)
        self.assertTrue(second.idempotent_replay)
        self.assertEqual(len(self.service.for_person("person-ada")), 1)

    def test_validation_rejects_invalid_direction_outcome_and_naive_timestamp(self) -> None:
        with self.assertRaises(PeopleTrackerValidationError):
            self.service.record(
                "int-001",
                person_id="person-ada",
                channel="linkedin",
                direction="inbound",
                kind="message",
                occurred_at="2026-09-07T18:00:00-04:00",
                outcome="sent",
                idempotency_key="bad-direction-outcome",
            )
        with self.assertRaises(PeopleTrackerValidationError):
            self.service.record(
                "int-002",
                person_id="person-ada",
                channel="linkedin",
                direction="outbound",
                kind="message",
                occurred_at="2026-09-07T18:00:00",
                outcome="sent",
                idempotency_key="bad-naive-time",
            )

    def test_tracker_projection_contains_relationship_and_interaction_fields(self) -> None:
        self.service.record(
            "int-001",
            person_id="person-ada",
            company_id="company-acme",
            channel="linkedin",
            direction="outbound",
            kind="message",
            occurred_at="2026-09-07T18:00:00-04:00",
            outcome="sent",
            summary="Synthetic public test note.",
            idempotency_key="record-int-001",
        )
        interaction = self.service.for_person("person-ada")[0]
        row = interaction_row(interaction)
        self.assertEqual(len(row), len(DEFAULT_TRACKER_PROJECTION.interactions_headers))
        summary = relationship_columns(self.service.relationship_summary("person-ada"))
        self.assertIn("have_i_contacted_them", summary)
        self.assertIn("have_they_replied", summary)
        self.assertIn("awaiting_reply", summary)
        self.assertIn("relationship_state", DEFAULT_TRACKER_PROJECTION.people_headers)
        self.assertEqual(
            set(DEFAULT_TRACKER_PROJECTION.companies_headers[:2]),
            {"company_id", "company_name"},
        )

    def test_public_api_has_no_outbound_send_or_connect_action(self) -> None:
        public_methods = {
            name
            for name, value in inspect.getmembers(CareerInteractionService, inspect.isfunction)
            if not name.startswith("_")
        }
        forbidden = {"send", "send_message", "send_email", "connect", "post", "comment"}
        self.assertTrue(public_methods.isdisjoint(forbidden))
        self.assertEqual(public_methods, {"record", "for_person", "relationship_summary"})


if __name__ == "__main__":
    unittest.main()
