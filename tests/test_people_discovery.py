from __future__ import annotations

from datetime import date
import unittest

from mira.people_discovery import (
    CandidatePerson,
    CertificationRecord,
    DiscoveryTarget,
    EducationRecord,
    ExperienceRecord,
    SourceRef,
    canonicalize_candidate,
    estimate_relevant_experience_years,
    identity_keys,
    normalize_linkedin_url,
    score_candidate,
    stable_person_id,
    upsert_candidate,
)


class PeopleDiscoveryCoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.target = DiscoveryTarget(
            company_id="company-acme",
            company_name="Acme Networks",
            metro="Austin, Texas",
            target_roles=("network engineer", "cloud engineer"),
        )
        self.observed_at = "2026-09-08T03:00:00Z"

    def test_wgu_target_employer_technical_candidate_is_tier_one(self) -> None:
        candidate = self._candidate(
            provider="provider-a",
            provider_id="a-1",
            linkedin="https://linkedin.com/in/ada-synthetic/",
            name="Ada Synthetic",
            title="Network Engineer",
            employer="Acme Networks",
            wgu=True,
        )
        score = score_candidate(candidate, self.target)
        self.assertEqual(score.tier, 1)
        self.assertIn("WGU affiliation", score.factors)
        self.assertIn("current target employer", score.factors)
        self.assertIn("networking/cloud/infrastructure relevance", score.factors)
        self.assertGreaterEqual(score.score, 70)

    def test_unrelated_executive_is_penalized_not_promoted_by_company_alone(self) -> None:
        candidate = self._candidate(
            provider="provider-a",
            provider_id="a-2",
            linkedin="https://linkedin.com/in/executive-synthetic",
            name="Executive Synthetic",
            title="Chief Marketing Officer",
            employer="Acme Networks",
            wgu=False,
            skills=("marketing",),
            certifications=(),
        )
        score = score_candidate(candidate, self.target)
        self.assertIn("distant executive", score.penalties)
        self.assertIn("weak technical relevance", score.penalties)
        self.assertEqual(score.tier, 5)
        self.assertLess(score.score, 30)

    def test_same_linkedin_identity_is_stable_across_replaceable_providers(self) -> None:
        first = self._candidate(
            provider="provider-a",
            provider_id="a-1",
            linkedin="https://linkedin.com/in/ada-synthetic/",
            name="Ada Synthetic",
            title="Network Engineer",
            employer="Acme Networks",
            wgu=True,
        )
        second = self._candidate(
            provider="provider-b",
            provider_id="b-9",
            linkedin="https://www.linkedin.com/in/ada-synthetic",
            name="Ada Synthetic",
            title="Network Engineer",
            employer="Acme Networks",
            wgu=True,
        )
        self.assertEqual(stable_person_id(first), stable_person_id(second))
        self.assertIn(
            "linkedin:https://www.linkedin.com/in/ada-synthetic",
            identity_keys(first),
        )

    def test_repeated_discovery_enriches_same_person_without_duplicate_row(self) -> None:
        first = self._candidate(
            provider="provider-a",
            provider_id="a-1",
            linkedin="https://linkedin.com/in/ada-synthetic",
            name="Ada Synthetic",
            title="Network Engineer",
            employer="Acme Networks",
            wgu=True,
            certifications=(CertificationRecord("CCNA", "Cisco"),),
            skills=("routing", "switching"),
        )
        records, result = upsert_candidate(
            (), first, self.target, observed_at=self.observed_at
        )
        self.assertTrue(result.created)
        self.assertEqual(len(records), 1)

        enriched = self._candidate(
            provider="provider-b",
            provider_id="b-9",
            linkedin="https://www.linkedin.com/in/ada-synthetic",
            name="Ada Synthetic",
            title="Network Engineer",
            employer="Acme Networks",
            wgu=True,
            certifications=(
                CertificationRecord("CCNA", "Cisco"),
                CertificationRecord("RHCSA", "Red Hat"),
            ),
            skills=("routing", "switching", "linux", "ansible"),
        )
        records, result = upsert_candidate(
            records,
            enriched,
            self.target,
            observed_at="2026-09-09T03:00:00Z",
        )
        self.assertFalse(result.created)
        self.assertTrue(result.enriched)
        self.assertEqual(len(records), 1)
        self.assertEqual(set(records[0].certifications), {"CCNA", "RHCSA"})
        self.assertEqual(
            set(records[0].provider_ids),
            {"provider-a:a-1", "provider-b:b-9"},
        )

    def test_same_fallback_facts_with_conflicting_strong_ids_fail_closed_as_separate_people(self) -> None:
        first = self._candidate(
            provider="provider-a",
            provider_id="a-1",
            linkedin="https://linkedin.com/in/ada-one",
            name="Ada Synthetic",
            title="Network Engineer",
            employer="Acme Networks",
            wgu=True,
        )
        second = self._candidate(
            provider="provider-b",
            provider_id="b-2",
            linkedin="https://linkedin.com/in/ada-two",
            name="Ada Synthetic",
            title="Network Engineer",
            employer="Acme Networks",
            wgu=True,
        )
        records, _ = upsert_candidate((), first, self.target, observed_at=self.observed_at)
        records, second_result = upsert_candidate(
            records,
            second,
            self.target,
            observed_at="2026-09-09T03:00:00Z",
        )
        self.assertTrue(second_result.created)
        self.assertEqual(len(records), 2)

    def test_relevant_experience_merges_overlapping_intervals(self) -> None:
        years = estimate_relevant_experience_years(
            (
                ExperienceRecord(
                    employer="Synthetic ISP",
                    title="Network Technician",
                    start_date="2023-01",
                    end_date="2024-12",
                ),
                ExperienceRecord(
                    employer="Synthetic Cloud Co",
                    title="Cloud Support Engineer",
                    start_date="2024-06",
                    end_date=None,
                    is_current=True,
                ),
            ),
            as_of=date(2026, 1, 1),
        )
        self.assertIsNotNone(years)
        assert years is not None
        self.assertGreater(years, 2.9)
        self.assertLess(years, 3.1)

    def test_canonical_record_preserves_provenance_and_explains_relevance(self) -> None:
        source = SourceRef(
            source="synthetic_provider",
            source_id="synthetic-1",
            source_url="https://example.com/profiles/synthetic-1",
            observed_at=self.observed_at,
            confidence=0.9,
        )
        candidate = self._candidate(
            provider="synthetic_provider",
            provider_id="synthetic-1",
            linkedin="https://linkedin.com/in/ada-synthetic",
            name="Ada Synthetic",
            title="Network Engineer",
            employer="Acme Networks",
            wgu=True,
            source_refs=(source,),
        )
        person = canonicalize_candidate(
            candidate,
            self.target,
            discovered_at=self.observed_at,
        )
        self.assertEqual(person.discovery_sources, ("synthetic_provider",))
        self.assertEqual(person.source_urls, ("https://example.com/profiles/synthetic-1",))
        self.assertEqual(person.confidence, 0.9)
        self.assertIn("WGU affiliation", person.why_relevant)
        self.assertIn("Network Engineer at Acme Networks", person.why_relevant)
        self.assertTrue(person.provenance)

    def test_linkedin_normalization_removes_query_and_trailing_slash(self) -> None:
        self.assertEqual(
            normalize_linkedin_url(
                "http://linkedin.com/in/ada-synthetic/?trk=synthetic"
            ),
            "https://www.linkedin.com/in/ada-synthetic",
        )

    def _candidate(
        self,
        *,
        provider: str,
        provider_id: str,
        linkedin: str,
        name: str,
        title: str,
        employer: str,
        wgu: bool,
        skills: tuple[str, ...] = ("routing", "switching", "linux"),
        certifications: tuple[CertificationRecord, ...] = (
            CertificationRecord("CCNA", "Cisco"),
        ),
        source_refs: tuple[SourceRef, ...] = (),
    ) -> CandidatePerson:
        education = (
            EducationRecord(
                school_name=(
                    "Western Governors University" if wgu else "Synthetic State University"
                ),
                start_date="2023",
                end_date="2026",
                degree="bachelors",
                field_of_study="information technology",
            ),
        )
        experience = (
            ExperienceRecord(
                employer="Synthetic ISP",
                title="Network Technician",
                start_date="2023-01",
                end_date="2024-12",
            ),
            ExperienceRecord(
                employer=employer,
                title=title,
                start_date="2025-01",
                end_date=None,
                is_current=True,
            ),
        )
        return CandidatePerson(
            provider=provider,
            provider_person_id=provider_id,
            full_name=name,
            current_title=title,
            current_employer=employer,
            current_location="Austin, Texas, United States",
            linkedin_url=linkedin,
            education=education,
            experience=experience,
            certifications=certifications,
            skills=skills,
            source_refs=source_refs,
            provider_confidence=0.9,
            provider_last_verified_at=self.observed_at,
        )


if __name__ == "__main__":
    unittest.main()
