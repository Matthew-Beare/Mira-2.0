from __future__ import annotations

import unittest

from mira.people_discovery import CanonicalPerson, DiscoveryTarget
from mira.people_sheet_projection import (
    CareerJobProjection,
    PeopleSheetProjectionError,
    PeopleTrackerSheetProjector,
)
from mira.people_tracker import InteractionView, RelationshipSummary


class FakeTrackerGateway:
    def __init__(self) -> None:
        self.tabs: dict[str, list[list[object]]] = {
            "COMPANIES": [],
            "PEOPLE": [],
            "INTERACTIONS": [],
            "JOBS": [],
        }
        self.mutations = 0

    def read_range(self, a1_range: str):
        tab = a1_range.split("!", 1)[0]
        if tab not in self.tabs:
            raise AssertionError(f"unexpected tab: {tab}")
        return tuple(tuple(row) for row in self.tabs[tab])

    def apply_mutations(self, mutations):
        for mutation in mutations:
            self.mutations += 1
            rows = self.tabs[mutation.tab]
            values = list(mutation.values)
            if mutation.row_number is None:
                rows.append(values)
                continue
            index = mutation.row_number - 1
            while len(rows) <= index:
                rows.append([])
            rows[index] = values


class PeopleTrackerSheetProjectorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.gateway = FakeTrackerGateway()
        self.projector = PeopleTrackerSheetProjector(self.gateway)
        self.target = DiscoveryTarget(
            company_id="company-acme",
            company_name="Acme Networks",
            metro="Austin, Texas",
            priority=1,
        )

    def test_bootstrap_creates_exact_headers_in_existing_empty_tabs(self) -> None:
        self.projector.bootstrap_headers()
        self.assertEqual(self.gateway.tabs["COMPANIES"][0][0], "company_id")
        self.assertEqual(self.gateway.tabs["PEOPLE"][0][0], "person_id")
        self.assertEqual(self.gateway.tabs["INTERACTIONS"][0][0], "interaction_id")
        self.assertEqual(self.gateway.tabs["JOBS"][0][0], "job_id")

    def test_company_rerun_is_zero_write_when_material_state_is_identical(self) -> None:
        first = self.projector.upsert_company(
            self.target,
            career_url="https://example.com/careers",
            notes="Synthetic test company.",
        )
        after_first = self.gateway.mutations
        second = self.projector.upsert_company(
            self.target,
            career_url="https://example.com/careers",
            notes="Synthetic test company.",
        )
        self.assertTrue(first.created)
        self.assertTrue(first.changed)
        self.assertFalse(second.created)
        self.assertFalse(second.changed)
        self.assertEqual(self.gateway.mutations, after_first)
        self.assertEqual(len(self.gateway.tabs["COMPANIES"]), 2)

    def test_same_person_id_replaces_existing_projection_instead_of_duplicating(self) -> None:
        person = self._person(score=92)
        relationship = self._relationship(
            state="not_contacted",
            contacted=False,
            replied=False,
            awaiting=False,
        )
        first = self.projector.upsert_person(person, relationship)
        updated_relationship = self._relationship(
            state="awaiting_reply",
            contacted=True,
            replied=False,
            awaiting=True,
        )
        second = self.projector.upsert_person(person, updated_relationship)
        self.assertTrue(first.created)
        self.assertFalse(second.created)
        self.assertTrue(second.changed)
        self.assertEqual(first.row_number, second.row_number)
        self.assertEqual(len(self.gateway.tabs["PEOPLE"]), 2)
        row = self.projector.read_row("PEOPLE", "person-ada")
        assert row is not None
        headers = self.gateway.tabs["PEOPLE"][0]
        values = dict(zip(headers, row))
        self.assertTrue(values["have_i_contacted_them"])
        self.assertFalse(values["have_they_replied"])
        self.assertTrue(values["awaiting_reply"])
        self.assertEqual(values["relationship_state"], "awaiting_reply")

    def test_interaction_and_job_rows_preserve_cross_links_and_exact_readback(self) -> None:
        interaction = InteractionView(
            interaction_id="int-001",
            revision=1,
            person_id="person-ada",
            company_id="company-acme",
            job_id="job-001",
            channel="linkedin",
            direction="outbound",
            kind="message",
            occurred_at="2026-09-08T13:00:00Z",
            outcome="sent",
            summary="Synthetic outreach note.",
            source_ref=None,
            reply_to_interaction_id=None,
            follow_up_due="2026-09-12",
        )
        job = CareerJobProjection(
            job_id="job-001",
            company_id="company-acme",
            title="Network Engineer",
            location="Austin, Texas",
            url="https://example.com/jobs/job-001",
            status="target",
            discovered_at="2026-09-08T13:00:00Z",
        )
        interaction_result = self.projector.upsert_interaction(interaction)
        job_result = self.projector.upsert_job(job)
        self.assertTrue(interaction_result.exact_readback)
        self.assertTrue(job_result.exact_readback)
        self.assertEqual(
            self.projector.read_row("INTERACTIONS", "int-001")[1:4],
            ("person-ada", "company-acme", "job-001"),
        )
        self.assertEqual(
            self.projector.read_row("JOBS", "job-001")[1],
            "company-acme",
        )

    def test_duplicate_stable_ids_fail_closed(self) -> None:
        self.projector.bootstrap_headers()
        header = self.gateway.tabs["COMPANIES"][0]
        row = ["company-acme", "Acme Networks", "Austin, Texas", 1, "", ""]
        self.assertEqual(len(header), len(row))
        self.gateway.tabs["COMPANIES"].extend([row.copy(), row.copy()])
        with self.assertRaises(PeopleSheetProjectionError):
            self.projector.read_row("COMPANIES", "company-acme")

    def test_person_relationship_id_mismatch_fails_closed(self) -> None:
        with self.assertRaises(PeopleSheetProjectionError):
            self.projector.upsert_person(
                self._person(score=92),
                RelationshipSummary(
                    person_id="person-other",
                    relationship_state="not_contacted",
                    have_i_contacted_them=False,
                    have_they_replied=False,
                    awaiting_reply=False,
                    interaction_count=0,
                    last_interaction_at=None,
                    last_outbound_at=None,
                    last_inbound_at=None,
                    last_channel=None,
                    follow_up_due=None,
                ),
            )

    @staticmethod
    def _person(*, score: int) -> CanonicalPerson:
        return CanonicalPerson(
            person_id="person-ada",
            full_name="Ada Synthetic",
            current_title="Network Engineer",
            current_employer="Acme Networks",
            current_location="Austin, Texas",
            linkedin_url="https://www.linkedin.com/in/ada-synthetic",
            public_profile_urls=(),
            profile_photo_url_or_reference="",
            previous_employer="Synthetic ISP",
            previous_title="Network Technician",
            estimated_relevant_experience_years=3.5,
            relevant_experience_is_estimated=True,
            wgu_connection="Western Governors University / WGU affiliation",
            certifications=("CCNA",),
            relevant_skills_or_keywords=("routing", "switching"),
            why_relevant="WGU affiliation; target employer; network role.",
            discovery_sources=("synthetic_provider",),
            source_urls=("https://example.com/source/ada",),
            confidence=0.9,
            discovered_at="2026-09-08T13:00:00Z",
            last_verified_at="2026-09-08T13:00:00Z",
            priority_score=score,
            priority_tier=1,
            notes="Synthetic test person.",
            provider_ids=("synthetic_provider:ada",),
            identity_keys=("linkedin:https://www.linkedin.com/in/ada-synthetic",),
        )

    @staticmethod
    def _relationship(
        *,
        state: str,
        contacted: bool,
        replied: bool,
        awaiting: bool,
    ) -> RelationshipSummary:
        return RelationshipSummary(
            person_id="person-ada",
            relationship_state=state,
            have_i_contacted_them=contacted,
            have_they_replied=replied,
            awaiting_reply=awaiting,
            interaction_count=1 if contacted else 0,
            last_interaction_at="2026-09-08T13:00:00Z" if contacted else None,
            last_outbound_at="2026-09-08T13:00:00Z" if contacted else None,
            last_inbound_at=None,
            last_channel="linkedin" if contacted else None,
            follow_up_due="2026-09-12" if awaiting else None,
        )


if __name__ == "__main__":
    unittest.main()
