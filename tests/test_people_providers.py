from __future__ import annotations

from datetime import datetime, timezone
import inspect
import json
import unittest
from urllib.parse import parse_qs, urlsplit

from mira.people_discovery import DiscoveryTarget
from mira.people_providers import (
    DiscoveryBudget,
    PeopleDataLabsProvider,
    PeopleProviderBudgetError,
    PeopleProviderTransportError,
    PeopleProviderValidationError,
    pdl_record_to_candidate,
)


class PeopleDataLabsProviderTests(unittest.TestCase):
    def setUp(self) -> None:
        self.target = DiscoveryTarget(
            company_id="company-acme",
            company_name="Acme Networks",
            metro="Austin, Texas",
            target_roles=("network engineer", "cloud engineer"),
        )

    def test_query_is_company_scoped_and_wgu_first(self) -> None:
        provider = PeopleDataLabsProvider(api_key_provider=lambda: "synthetic-key")
        wgu = provider.build_query(self.target, require_wgu=True)
        must = wgu["query"]["bool"]["must"]
        self.assertIn({"match": {"job_company_name": "acme networks"}}, must)
        self.assertIn(
            {"match": {"education.school.name": "western governors university"}},
            must,
        )
        self.assertIn(
            {"match": {"job_title.text": "network engineer"}},
            wgu["query"]["bool"]["should"],
        )
        fallback = provider.build_query(self.target, require_wgu=False)
        self.assertEqual(fallback["query"]["bool"]["minimum_should_match"], 1)

    def test_discovery_is_credit_bounded_and_deduplicates_between_phases(self) -> None:
        calls: list[tuple[str, dict[str, str], float]] = []

        def fake_get(url: str, headers: dict[str, str], timeout: float):
            calls.append((url, headers, timeout))
            query = json.loads(parse_qs(urlsplit(url).query)["query"][0])
            must = query["query"]["bool"]["must"]
            is_wgu = any("education.school.name" in item.get("match", {}) for item in must)
            duplicate = self._person("pdl-1", "Ada Synthetic", "Network Engineer")
            if is_wgu:
                return {"status": 200, "total": 1, "data": [duplicate]}
            return {
                "status": 200,
                "total": 2,
                "data": [
                    duplicate,
                    self._person("pdl-2", "Grace Synthetic", "Cloud Engineer"),
                ],
            }

        provider = PeopleDataLabsProvider(
            api_key_provider=lambda: "synthetic-key",
            budget=DiscoveryBudget(max_records=4, max_requests=2, wgu_first_records=2),
            http_get=fake_get,
            clock=lambda: datetime(2026, 9, 8, 3, 0, tzinfo=timezone.utc),
        )
        candidates = provider.discover(self.target, limit=3)
        self.assertEqual([candidate.provider_person_id for candidate in candidates], ["pdl-1", "pdl-2"])
        self.assertEqual(provider.last_run_stats.requests, 2)
        self.assertEqual(provider.last_run_stats.returned_records, 3)
        self.assertEqual(provider.last_run_stats.unique_candidates, 2)
        self.assertEqual(len(calls), 2)
        self.assertTrue(all(call[1]["X-Api-Key"] == "synthetic-key" for call in calls))
        sizes = [int(parse_qs(urlsplit(call[0]).query)["size"][0]) for call in calls]
        self.assertEqual(sizes, [2, 2])

    def test_response_normalization_preserves_grounded_resume_fields(self) -> None:
        candidate = pdl_record_to_candidate(
            self._person("pdl-1", "Ada Synthetic", "Network Engineer"),
            observed_at="2026-09-08T03:00:00Z",
            source_confidence=0.8,
        )
        self.assertIsNotNone(candidate)
        assert candidate is not None
        self.assertEqual(candidate.provider, "people_data_labs")
        self.assertEqual(candidate.current_employer, "acme networks")
        self.assertEqual(candidate.education[0].school_name, "western governors university")
        self.assertEqual(candidate.experience[0].employer, "acme networks")
        self.assertTrue(candidate.experience[0].is_current)
        self.assertEqual(candidate.certifications[0].name, "ccna")
        self.assertIn("routing", candidate.skills)
        self.assertEqual(candidate.source_refs[0].source_id, "pdl-1")

    def test_missing_required_identity_or_job_facts_are_skipped_not_invented(self) -> None:
        incomplete = self._person("pdl-1", "Ada Synthetic", "Network Engineer")
        incomplete.pop("job_company_name")
        self.assertIsNone(
            pdl_record_to_candidate(
                incomplete,
                observed_at="2026-09-08T03:00:00Z",
                source_confidence=0.8,
            )
        )

    def test_budget_and_key_validation_fail_closed(self) -> None:
        provider = PeopleDataLabsProvider(
            api_key_provider=lambda: "synthetic-key",
            budget=DiscoveryBudget(max_records=3, max_requests=1, wgu_first_records=3),
            http_get=lambda *_: {"status": 200, "total": 0, "data": []},
        )
        with self.assertRaises(PeopleProviderBudgetError):
            provider.discover(self.target, limit=4)

        missing_key = PeopleDataLabsProvider(
            api_key_provider=lambda: " ",
            http_get=lambda *_: {"status": 200, "total": 0, "data": []},
        )
        with self.assertRaises(PeopleProviderValidationError):
            missing_key.discover(self.target, limit=1)

    def test_non_success_provider_status_is_not_treated_as_empty_success(self) -> None:
        provider = PeopleDataLabsProvider(
            api_key_provider=lambda: "synthetic-key",
            http_get=lambda *_: {"status": 429, "error": {"message": "synthetic limit"}},
        )
        with self.assertRaises(PeopleProviderTransportError):
            provider.discover(self.target, limit=1)

    def test_provider_public_api_has_no_outbound_contact_actions(self) -> None:
        public_methods = {
            name
            for name, value in inspect.getmembers(PeopleDataLabsProvider, inspect.isfunction)
            if not name.startswith("_")
        }
        forbidden = {
            "send",
            "send_message",
            "send_email",
            "connect",
            "post",
            "comment",
            "invite",
        }
        self.assertTrue(public_methods.isdisjoint(forbidden))
        self.assertEqual(public_methods, {"build_query", "discover"})

    @staticmethod
    def _person(person_id: str, full_name: str, job_title: str) -> dict[str, object]:
        return {
            "id": person_id,
            "full_name": full_name,
            "job_title": job_title,
            "job_company_name": "acme networks",
            "location_name": "austin, texas, united states",
            "linkedin_url": f"https://www.linkedin.com/in/{person_id}",
            "education": [
                {
                    "school": {"name": "western governors university"},
                    "degrees": ["bachelors"],
                    "majors": ["information technology"],
                    "start_date": "2023",
                    "end_date": "2026",
                }
            ],
            "experience": [
                {
                    "company": {"name": "acme networks"},
                    "title": {"name": job_title.lower()},
                    "start_date": "2025-01",
                    "end_date": None,
                    "is_primary": True,
                }
            ],
            "certifications": [
                {
                    "name": "ccna",
                    "organization": "cisco",
                    "start_date": "2025-06",
                    "end_date": None,
                }
            ],
            "skills": ["routing", "switching", "linux"],
        }


if __name__ == "__main__":
    unittest.main()
