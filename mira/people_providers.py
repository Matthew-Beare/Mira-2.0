"""Replaceable People Discovery provider adapters for MIRA.

The first concrete adapter targets People Data Labs Person Search. Credentials are
injected at runtime, query volume is explicitly bounded, and the adapter exposes
search only. It contains no email, LinkedIn messaging, connection, posting or other
outbound-contact capability.

Public source and tests contain no provider key, live person data or private tracker
identifiers.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from typing import Callable, Mapping, Protocol, Sequence
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .people_discovery import (
    CandidatePerson,
    CertificationRecord,
    DiscoveryTarget,
    EducationRecord,
    ExperienceRecord,
    SourceRef,
)


PDL_PERSON_SEARCH_URL = "https://api.peopledatalabs.com/v5/person/search"
PDL_SANDBOX_PERSON_SEARCH_URL = "https://sandbox.api.peopledatalabs.com/v5/person/search"
PDL_MAX_API_SIZE = 100
WGU_SCHOOL_NAME = "western governors university"


class PeopleProviderError(Exception):
    """Base discovery-provider failure."""


class PeopleProviderValidationError(PeopleProviderError):
    """Malformed provider configuration or response."""


class PeopleProviderBudgetError(PeopleProviderError):
    """A request would exceed the configured bounded discovery budget."""


class PeopleProviderTransportError(PeopleProviderError):
    """Provider HTTP request failed or returned unusable data."""


class DiscoveryProvider(Protocol):
    def discover(self, target: DiscoveryTarget, *, limit: int = 10) -> tuple[CandidatePerson, ...]: ...


@dataclass(frozen=True)
class DiscoveryBudget:
    """Per-run guardrail for credit-consuming person-search calls."""

    max_records: int = 15
    max_requests: int = 2
    wgu_first_records: int = 5

    def __post_init__(self) -> None:
        for field, value in (
            ("max_records", self.max_records),
            ("max_requests", self.max_requests),
            ("wgu_first_records", self.wgu_first_records),
        ):
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                raise PeopleProviderValidationError(f"{field} must be a non-negative integer")
        if self.max_records < 1:
            raise PeopleProviderValidationError("max_records must be at least 1")
        if self.max_requests < 1:
            raise PeopleProviderValidationError("max_requests must be at least 1")
        if self.wgu_first_records > self.max_records:
            raise PeopleProviderValidationError("wgu_first_records cannot exceed max_records")


@dataclass(frozen=True)
class ProviderRunStats:
    requests: int
    returned_records: int
    unique_candidates: int


HttpGet = Callable[[str, Mapping[str, str], float], Mapping[str, object]]
Clock = Callable[[], datetime]


class PeopleDataLabsProvider:
    """Credit-aware PDL Person Search adapter with WGU-first discovery.

    PDL Person Search does not return an enrichment likelihood score. The configured
    ``source_confidence`` therefore describes MIRA's confidence that a field was
    observed from this provider response, not a PDL identity-match likelihood.
    """

    def __init__(
        self,
        *,
        api_key_provider: Callable[[], str],
        budget: DiscoveryBudget = DiscoveryBudget(),
        endpoint: str = PDL_PERSON_SEARCH_URL,
        timeout_seconds: float = 15.0,
        source_confidence: float = 0.8,
        http_get: HttpGet | None = None,
        clock: Clock | None = None,
    ) -> None:
        if not callable(api_key_provider):
            raise PeopleProviderValidationError("api_key_provider must be callable")
        if not isinstance(timeout_seconds, (int, float)) or isinstance(timeout_seconds, bool) or timeout_seconds <= 0:
            raise PeopleProviderValidationError("timeout_seconds must be greater than zero")
        if not isinstance(source_confidence, (int, float)) or isinstance(source_confidence, bool):
            raise PeopleProviderValidationError("source_confidence must be numeric")
        if not 0 <= float(source_confidence) <= 1:
            raise PeopleProviderValidationError("source_confidence must be between 0 and 1")
        if not isinstance(endpoint, str) or not endpoint.startswith("https://"):
            raise PeopleProviderValidationError("endpoint must be an https URL")
        self._api_key_provider = api_key_provider
        self._budget = budget
        self._endpoint = endpoint
        self._timeout_seconds = float(timeout_seconds)
        self._source_confidence = float(source_confidence)
        self._http_get = http_get or _stdlib_get_json
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._last_run_stats = ProviderRunStats(0, 0, 0)

    @property
    def last_run_stats(self) -> ProviderRunStats:
        return self._last_run_stats

    def discover(self, target: DiscoveryTarget, *, limit: int = 10) -> tuple[CandidatePerson, ...]:
        requested = _bounded_limit(limit, self._budget.max_records)
        observed_at = _utc_timestamp(self._clock())
        candidates: list[CandidatePerson] = []
        seen: set[str] = set()
        requests = 0
        returned = 0

        wgu_size = min(requested, self._budget.wgu_first_records)
        if wgu_size and requests < self._budget.max_requests:
            payload = self._search(target, size=wgu_size, require_wgu=True)
            requests += 1
            data = _response_data(payload)
            returned += len(data)
            _extend_unique(candidates, seen, data, observed_at, self._source_confidence)

        remaining = requested - len(candidates)
        if remaining > 0 and requests < self._budget.max_requests:
            payload = self._search(target, size=remaining, require_wgu=False)
            requests += 1
            data = _response_data(payload)
            returned += len(data)
            _extend_unique(candidates, seen, data, observed_at, self._source_confidence)

        self._last_run_stats = ProviderRunStats(
            requests=requests,
            returned_records=returned,
            unique_candidates=len(candidates[:requested]),
        )
        return tuple(candidates[:requested])

    def build_query(self, target: DiscoveryTarget, *, require_wgu: bool) -> Mapping[str, object]:
        """Return the exact Elasticsearch query body used for a bounded search."""

        must: list[Mapping[str, object]] = [
            {"match": {"job_company_name": target.company_name.strip().lower()}},
        ]
        if require_wgu:
            must.append({"match": {"education.school.name": WGU_SCHOOL_NAME}})

        should: list[Mapping[str, object]] = []
        if target.metro.strip():
            location = target.metro.strip().lower()
            should.extend(
                (
                    {"match": {"location_name": location}},
                    {"match": {"location_metro": location}},
                )
            )
        for role in target.target_roles:
            if role.strip():
                should.append({"match": {"job_title.text": role.strip().lower()}})

        query: dict[str, object] = {"bool": {"must": must}}
        if should:
            query["bool"]["should"] = should  # type: ignore[index]
            if not require_wgu:
                query["bool"]["minimum_should_match"] = 1  # type: ignore[index]
        return {"query": query}

    def _search(self, target: DiscoveryTarget, *, size: int, require_wgu: bool) -> Mapping[str, object]:
        if size < 1 or size > min(PDL_MAX_API_SIZE, self._budget.max_records):
            raise PeopleProviderBudgetError("search size exceeds configured budget")
        key = self._api_key_provider()
        if not isinstance(key, str) or not key.strip():
            raise PeopleProviderValidationError("People Data Labs API key is unavailable")
        query = self.build_query(target, require_wgu=require_wgu)
        params = urlencode(
            {
                "query": json.dumps(query, separators=(",", ":"), sort_keys=True),
                "size": str(size),
            }
        )
        url = f"{self._endpoint}?{params}"
        headers = {"X-Api-Key": key.strip(), "Accept": "application/json"}
        payload = self._http_get(url, headers, self._timeout_seconds)
        if not isinstance(payload, Mapping):
            raise PeopleProviderTransportError("PDL response must be a JSON object")
        status = payload.get("status")
        if status != 200:
            raise PeopleProviderTransportError(f"PDL Person Search returned status {status!r}")
        return payload


def pdl_record_to_candidate(
    record: Mapping[str, object],
    *,
    observed_at: str,
    source_confidence: float,
) -> CandidatePerson | None:
    """Normalize one PDL Person record without inventing missing required facts."""

    provider_id = _string(record.get("id"))
    full_name = _string(record.get("full_name"))
    current_title = _string(record.get("job_title"))
    current_employer = _string(record.get("job_company_name"))
    if not (provider_id and full_name and current_title and current_employer):
        return None

    linkedin_url = _string(record.get("linkedin_url"))
    public_urls = tuple(
        value
        for value in (
            _string(record.get("github_url")),
            _string(record.get("facebook_url")),
            _string(record.get("twitter_url")),
        )
        if value
    )
    education = tuple(_education(item) for item in _mapping_list(record.get("education")))
    experience = tuple(_experience(item) for item in _mapping_list(record.get("experience")))
    certifications = tuple(
        _certification(item) for item in _mapping_list(record.get("certifications"))
    )
    skills = tuple(value for value in _string_list(record.get("skills")) if value)
    source = SourceRef(
        source="people_data_labs",
        source_id=provider_id,
        source_url=linkedin_url,
        observed_at=observed_at,
        confidence=source_confidence,
        status="verified",
    )
    return CandidatePerson(
        provider="people_data_labs",
        provider_person_id=provider_id,
        full_name=full_name,
        current_title=current_title,
        current_employer=current_employer,
        current_location=_string(record.get("location_name")),
        linkedin_url=linkedin_url,
        public_profile_urls=public_urls,
        profile_photo_url_or_reference=_string(record.get("profile_pic_url")),
        education=education,
        experience=experience,
        certifications=certifications,
        skills=skills,
        source_refs=(source,),
        provider_confidence=source_confidence,
        provider_last_verified_at=observed_at,
    )


def _extend_unique(
    output: list[CandidatePerson],
    seen: set[str],
    records: Sequence[Mapping[str, object]],
    observed_at: str,
    source_confidence: float,
) -> None:
    for record in records:
        candidate = pdl_record_to_candidate(
            record,
            observed_at=observed_at,
            source_confidence=source_confidence,
        )
        if candidate is None:
            continue
        key = candidate.provider_person_id or candidate.linkedin_url or (
            f"{candidate.full_name}|{candidate.current_employer}|{candidate.current_title}"
        )
        if key in seen:
            continue
        seen.add(key)
        output.append(candidate)


def _response_data(payload: Mapping[str, object]) -> tuple[Mapping[str, object], ...]:
    raw = payload.get("data", [])
    if not isinstance(raw, list):
        raise PeopleProviderTransportError("PDL response data must be a list")
    output: list[Mapping[str, object]] = []
    for item in raw:
        if not isinstance(item, Mapping):
            raise PeopleProviderTransportError("PDL response contains a non-object person record")
        output.append(item)
    return tuple(output)


def _education(item: Mapping[str, object]) -> EducationRecord:
    school = item.get("school") if isinstance(item.get("school"), Mapping) else {}
    degrees = _string_list(item.get("degrees"))
    majors = _string_list(item.get("majors"))
    return EducationRecord(
        school_name=_string(school.get("name")) or "unknown school",
        start_date=_string(item.get("start_date")),
        end_date=_string(item.get("end_date")),
        degree=degrees[0] if degrees else None,
        field_of_study=majors[0] if majors else None,
    )


def _experience(item: Mapping[str, object]) -> ExperienceRecord:
    company = item.get("company") if isinstance(item.get("company"), Mapping) else {}
    title = item.get("title") if isinstance(item.get("title"), Mapping) else {}
    return ExperienceRecord(
        employer=_string(company.get("name")) or "unknown employer",
        title=_string(title.get("name")) or "unknown title",
        start_date=_string(item.get("start_date")),
        end_date=_string(item.get("end_date")),
        is_current=bool(item.get("is_primary")),
    )


def _certification(item: Mapping[str, object]) -> CertificationRecord:
    return CertificationRecord(
        name=_string(item.get("name")) or "unknown certification",
        organization=_string(item.get("organization")),
        start_date=_string(item.get("start_date")),
        end_date=_string(item.get("end_date")),
        explicitly_reported=True,
    )


def _mapping_list(value: object) -> tuple[Mapping[str, object], ...]:
    if not isinstance(value, list):
        return ()
    return tuple(item for item in value if isinstance(item, Mapping))


def _string_list(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ()
    return tuple(item.strip() for item in value if isinstance(item, str) and item.strip())


def _string(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    text = value.strip()
    return text or None


def _bounded_limit(value: int, maximum: int) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise PeopleProviderValidationError("limit must be a positive integer")
    if value > maximum:
        raise PeopleProviderBudgetError(
            f"requested {value} records exceeds configured max_records={maximum}"
        )
    return value


def _utc_timestamp(value: datetime) -> str:
    if value.tzinfo is None or value.utcoffset() is None:
        raise PeopleProviderValidationError("clock must return a timezone-aware datetime")
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _stdlib_get_json(url: str, headers: Mapping[str, str], timeout: float) -> Mapping[str, object]:
    request = Request(url, method="GET", headers=dict(headers))
    try:
        with urlopen(request, timeout=timeout) as response:  # noqa: S310 - fixed https endpoint by construction
            raw = response.read().decode("utf-8")
    except HTTPError as exc:
        raise PeopleProviderTransportError(f"PDL HTTP error {exc.code}") from exc
    except URLError as exc:
        raise PeopleProviderTransportError("PDL request failed") from exc
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise PeopleProviderTransportError("PDL response was not valid JSON") from exc
    if not isinstance(payload, Mapping):
        raise PeopleProviderTransportError("PDL response must be a JSON object")
    return payload
