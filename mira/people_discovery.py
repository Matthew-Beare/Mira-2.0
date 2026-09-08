"""Provider-neutral People Discovery domain logic for MIRA.

No provider credentials, Google identifiers, browser automation, LinkedIn
scraping, or outbound-contact actions live here. The module converts grounded
provider/public-web observations into canonical career-networking records with
conservative entity resolution, durable provenance, relevant-experience
estimation, and configurable relevance scoring.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import date, datetime, timedelta, timezone
import re
from typing import Iterable, Sequence
from urllib.parse import urlsplit, urlunsplit
from uuid import NAMESPACE_URL, uuid5

TECH_TERMS = (
    "network", "networking", "routing", "switching", "noc", "infrastructure",
    "cloud", "aws", "azure", "linux", "systems", "system administrator",
    "sysadmin", "terraform", "ansible", "kubernetes", "data center",
    "datacenter", "technical support", "support engineer", "network security",
    "security infrastructure", "cisco",
)
TARGET_ROLE_TERMS = (
    "network engineer", "associate network engineer", "junior network engineer",
    "network administrator", "network support engineer", "network technician",
    "noc engineer", "noc technician", "infrastructure engineer",
    "infrastructure support", "systems engineer", "systems administrator",
    "system administrator", "cloud engineer", "cloud support engineer",
    "technical support engineer", "data center engineer", "data center technician",
    "network security engineer",
)
CERT_TERMS = (
    "ccna", "ccnp", "comptia", "aws", "azure", "linux", "red hat", "rhcsa",
    "rhce", "kubernetes", "cka", "ckad", "terraform", "security+", "network+", "a+",
)
EXECUTIVE_TERMS = ("chief ", "ceo", "cfo", "cio", "cto", "coo", "president", "vice president", "vp ")
RECRUITER_TERMS = ("recruiter", "talent acquisition", "technical recruiter")
MANAGER_TERMS = ("network manager", "infrastructure manager", "noc manager", "systems manager", "cloud manager", "hiring manager")
WGU_TERMS = ("western governors university", "wgu")


class PeopleDiscoveryError(Exception):
    """Base People Discovery failure."""


class IdentityConflictError(PeopleDiscoveryError):
    """Automatic identity resolution could not prove a safe merge."""


class ValidationError(PeopleDiscoveryError):
    """Malformed discovery material."""


@dataclass(frozen=True)
class SourceRef:
    source: str
    source_id: str | None
    source_url: str | None
    observed_at: str
    confidence: float
    status: str = "verified"

    def __post_init__(self) -> None:
        _trimmed(self.source, "source")
        if self.source_id is not None:
            _trimmed(self.source_id, "source_id")
        if self.source_url is not None:
            object.__setattr__(self, "source_url", normalize_url(self.source_url))
        _timestamp(self.observed_at)
        if not 0 <= self.confidence <= 1:
            raise ValidationError("confidence must be between 0 and 1")
        if self.status not in {"verified", "inferred", "stale", "conflicting", "human_entered"}:
            raise ValidationError("invalid provenance status")


@dataclass(frozen=True)
class FieldObservation:
    field_name: str
    value: str
    source: SourceRef

    def __post_init__(self) -> None:
        _trimmed(self.field_name, "field_name")
        _trimmed(self.value, "value")


@dataclass(frozen=True)
class EducationRecord:
    school_name: str
    start_date: str | None = None
    end_date: str | None = None
    degree: str | None = None
    field_of_study: str | None = None


@dataclass(frozen=True)
class ExperienceRecord:
    employer: str
    title: str
    start_date: str | None = None
    end_date: str | None = None
    is_current: bool = False


@dataclass(frozen=True)
class CertificationRecord:
    name: str
    organization: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    explicitly_reported: bool = True


@dataclass(frozen=True)
class CandidatePerson:
    provider: str
    provider_person_id: str | None
    full_name: str
    current_title: str
    current_employer: str
    current_location: str | None
    linkedin_url: str | None = None
    public_profile_urls: tuple[str, ...] = ()
    profile_photo_url_or_reference: str | None = None
    education: tuple[EducationRecord, ...] = ()
    experience: tuple[ExperienceRecord, ...] = ()
    certifications: tuple[CertificationRecord, ...] = ()
    skills: tuple[str, ...] = ()
    source_refs: tuple[SourceRef, ...] = ()
    field_observations: tuple[FieldObservation, ...] = ()
    provider_confidence: float = 0.5
    provider_last_verified_at: str | None = None

    def __post_init__(self) -> None:
        for field, value in (("provider", self.provider), ("full_name", self.full_name), ("current_title", self.current_title), ("current_employer", self.current_employer)):
            _trimmed(value, field)
        if self.provider_person_id is not None:
            _trimmed(self.provider_person_id, "provider_person_id")
        if not 0 <= self.provider_confidence <= 1:
            raise ValidationError("provider_confidence must be between 0 and 1")
        if self.linkedin_url:
            object.__setattr__(self, "linkedin_url", normalize_linkedin_url(self.linkedin_url))
        object.__setattr__(self, "public_profile_urls", tuple(sorted({normalize_url(u) for u in self.public_profile_urls if u})))
        if self.profile_photo_url_or_reference:
            value = self.profile_photo_url_or_reference.strip()
            object.__setattr__(self, "profile_photo_url_or_reference", normalize_url(value) if value.startswith(("http://", "https://")) else value)
        if self.provider_last_verified_at:
            _timestamp(self.provider_last_verified_at)


@dataclass(frozen=True)
class DiscoveryTarget:
    company_id: str
    company_name: str
    metro: str
    priority: int = 1
    company_domains: tuple[str, ...] = ()
    target_roles: tuple[str, ...] = TARGET_ROLE_TERMS

    def __post_init__(self) -> None:
        _trimmed(self.company_id, "company_id")
        _trimmed(self.company_name, "company_name")
        _trimmed(self.metro, "metro")
        if not isinstance(self.priority, int) or isinstance(self.priority, bool) or self.priority < 1:
            raise ValidationError("priority must be a positive integer")
        object.__setattr__(self, "company_domains", tuple(sorted({d.strip().lower().removeprefix("www.") for d in self.company_domains if d.strip()})))


@dataclass(frozen=True)
class ScoreWeights:
    wgu: int = 30
    target_employer: int = 24
    exact_target_role: int = 20
    technical_relevance: int = 14
    relevant_certification: int = 9
    target_metro: int = 7
    similar_progression: int = 7
    recent_transition: int = 5
    useful_recruiter_or_manager: int = 5
    executive_penalty: int = 28
    unrelated_penalty: int = 35
    stale_penalty: int = 12
    low_confidence_penalty: int = 18


@dataclass(frozen=True)
class RelevanceScore:
    score: int
    tier: int
    factors: tuple[str, ...]
    penalties: tuple[str, ...]


@dataclass(frozen=True)
class CanonicalPerson:
    person_id: str
    full_name: str
    current_title: str
    current_employer: str
    current_location: str | None
    linkedin_url: str | None
    public_profile_urls: tuple[str, ...]
    profile_photo_url_or_reference: str | None
    previous_employer: str | None
    previous_title: str | None
    estimated_relevant_experience_years: float | None
    relevant_experience_is_estimated: bool
    wgu_connection: str
    certifications: tuple[str, ...]
    relevant_skills_or_keywords: tuple[str, ...]
    why_relevant: str
    discovery_sources: tuple[str, ...]
    source_urls: tuple[str, ...]
    confidence: float
    discovered_at: str
    last_verified_at: str
    priority_score: int
    priority_tier: int
    contact_status: str = "not_contacted"
    last_contact_at: str | None = None
    next_action: str | None = None
    next_action_date: str | None = None
    notes: str | None = None
    provider_ids: tuple[str, ...] = ()
    provenance: tuple[FieldObservation, ...] = ()
    identity_keys: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.contact_status not in {"not_contacted", "contacted", "replied", "conversation", "referral", "do_not_contact", "rejected"}:
            raise ValidationError("invalid contact_status")
        _timestamp(self.discovered_at)
        _timestamp(self.last_verified_at)
        if self.last_contact_at:
            _timestamp(self.last_contact_at)
        if not 0 <= self.confidence <= 1:
            raise ValidationError("confidence must be between 0 and 1")
        if not 0 <= self.priority_score <= 100 or self.priority_tier not in {1, 2, 3, 4, 5}:
            raise ValidationError("invalid priority")


@dataclass(frozen=True)
class DiscoveryResult:
    person: CanonicalPerson
    created: bool
    enriched: bool


def canonicalize_candidate(candidate: CandidatePerson, target: DiscoveryTarget, *, discovered_at: str | None = None, weights: ScoreWeights = ScoreWeights()) -> CanonicalPerson:
    observed_at = discovered_at or _now()
    _timestamp(observed_at)
    score = score_candidate(candidate, target, weights=weights)
    years = estimate_relevant_experience_years(candidate.experience)
    previous = _previous(candidate.experience, candidate.current_employer)
    refs = candidate.source_refs or (SourceRef(candidate.provider, candidate.provider_person_id, candidate.linkedin_url or (candidate.public_profile_urls[0] if candidate.public_profile_urls else None), candidate.provider_last_verified_at or observed_at, candidate.provider_confidence),)
    provenance = candidate.field_observations or _default_observations(candidate, refs[0])
    return CanonicalPerson(
        person_id=stable_person_id(candidate),
        full_name=candidate.full_name,
        current_title=candidate.current_title,
        current_employer=candidate.current_employer,
        current_location=candidate.current_location,
        linkedin_url=candidate.linkedin_url,
        public_profile_urls=candidate.public_profile_urls,
        profile_photo_url_or_reference=candidate.profile_photo_url_or_reference,
        previous_employer=previous.employer if previous else None,
        previous_title=previous.title if previous else None,
        estimated_relevant_experience_years=years,
        relevant_experience_is_estimated=years is not None,
        wgu_connection="Western Governors University / WGU affiliation" if _has_wgu(candidate.education) else "none_observed",
        certifications=tuple(sorted({c.name.strip() for c in candidate.certifications if c.name.strip() and c.explicitly_reported}, key=str.lower)),
        relevant_skills_or_keywords=tuple(sorted({s.strip() for s in candidate.skills if s.strip() and _technical(s)})),
        why_relevant=why_relevant(candidate, target, score, years),
        discovery_sources=tuple(sorted({r.source for r in refs})),
        source_urls=tuple(sorted({r.source_url for r in refs if r.source_url})),
        confidence=max([candidate.provider_confidence, *[r.confidence for r in refs]]),
        discovered_at=observed_at,
        last_verified_at=max((_timestamp(r.observed_at) for r in refs)).isoformat().replace("+00:00", "Z"),
        priority_score=score.score,
        priority_tier=score.tier,
        provider_ids=tuple(sorted({f"{candidate.provider}:{candidate.provider_person_id}"} if candidate.provider_person_id else set())),
        provenance=tuple(provenance),
        identity_keys=identity_keys(candidate),
    )


def upsert_candidate(existing: Sequence[CanonicalPerson], candidate: CandidatePerson, target: DiscoveryTarget, *, observed_at: str | None = None, weights: ScoreWeights = ScoreWeights()) -> tuple[tuple[CanonicalPerson, ...], DiscoveryResult]:
    incoming = canonicalize_candidate(candidate, target, discovered_at=observed_at, weights=weights)
    matches = [person for person in existing if _records_match(person, incoming)]
    if len(matches) > 1:
        raise IdentityConflictError(f"candidate {candidate.full_name!r} matches multiple canonical people")
    if not matches:
        return tuple(existing) + (incoming,), DiscoveryResult(incoming, True, False)
    current = matches[0]
    merged = merge_people(current, incoming)
    output = tuple(merged if p.person_id == current.person_id else p for p in existing)
    return output, DiscoveryResult(merged, False, merged != current)


def merge_people(current: CanonicalPerson, incoming: CanonicalPerson) -> CanonicalPerson:
    _assert_merge_safe(current, incoming)
    provenance = _merge_observations(current.provenance, incoming.provenance)
    resolved = {}
    for field in ("full_name", "current_title", "current_employer", "current_location", "linkedin_url", "profile_photo_url_or_reference"):
        resolved[field] = _resolve_field(field, getattr(current, field), getattr(incoming, field), provenance)
    return replace(
        current,
        full_name=resolved["full_name"], current_title=resolved["current_title"],
        current_employer=resolved["current_employer"], current_location=resolved["current_location"],
        linkedin_url=resolved["linkedin_url"], profile_photo_url_or_reference=resolved["profile_photo_url_or_reference"],
        public_profile_urls=tuple(sorted(set(current.public_profile_urls) | set(incoming.public_profile_urls))),
        previous_employer=incoming.previous_employer or current.previous_employer,
        previous_title=incoming.previous_title or current.previous_title,
        estimated_relevant_experience_years=_max_optional(current.estimated_relevant_experience_years, incoming.estimated_relevant_experience_years),
        relevant_experience_is_estimated=current.relevant_experience_is_estimated or incoming.relevant_experience_is_estimated,
        wgu_connection="Western Governors University / WGU affiliation" if "WGU" in (current.wgu_connection + incoming.wgu_connection).upper() or "WESTERN GOVERNORS" in (current.wgu_connection + incoming.wgu_connection).upper() else current.wgu_connection,
        certifications=tuple(sorted(set(current.certifications) | set(incoming.certifications), key=str.lower)),
        relevant_skills_or_keywords=tuple(sorted(set(current.relevant_skills_or_keywords) | set(incoming.relevant_skills_or_keywords))),
        why_relevant=incoming.why_relevant if incoming.priority_score >= current.priority_score else current.why_relevant,
        discovery_sources=tuple(sorted(set(current.discovery_sources) | set(incoming.discovery_sources))),
        source_urls=tuple(sorted(set(current.source_urls) | set(incoming.source_urls))),
        confidence=max(current.confidence, incoming.confidence),
        last_verified_at=max(current.last_verified_at, incoming.last_verified_at),
        priority_score=max(current.priority_score, incoming.priority_score),
        priority_tier=min(current.priority_tier, incoming.priority_tier),
        provider_ids=tuple(sorted(set(current.provider_ids) | set(incoming.provider_ids))),
        provenance=provenance,
        identity_keys=tuple(sorted(set(current.identity_keys) | set(incoming.identity_keys))),
    )


def score_candidate(candidate: CandidatePerson, target: DiscoveryTarget, *, weights: ScoreWeights = ScoreWeights()) -> RelevanceScore:
    raw = 0; factors: list[str] = []; penalties: list[str] = []
    wgu = _has_wgu(candidate.education)
    employer = _same_org(candidate.current_employer, target.company_name)
    exact_role = _matches_role(candidate.current_title, target.target_roles)
    technical = _technical_strength(candidate)
    cert = any(_contains(c.name, CERT_TERMS) for c in candidate.certifications)
    metro = bool(candidate.current_location and _location_matches(candidate.current_location, target.metro))
    useful_manager = _contains(candidate.current_title, RECRUITER_TERMS + MANAGER_TERMS)
    progression = _similar_progression(candidate.experience)
    recent = _recent_transition(candidate.experience)
    for condition, points, label in (
        (wgu, weights.wgu, "WGU affiliation"), (employer, weights.target_employer, "current target employer"),
        (exact_role, weights.exact_target_role, "target technical role"), (technical, weights.technical_relevance, "networking/cloud/infrastructure relevance"),
        (cert, weights.relevant_certification, "relevant certification"), (metro, weights.target_metro, "target metro"),
        (progression, weights.similar_progression, "similar technical career progression"), (recent, weights.recent_transition, "recent transition into target field"),
        (useful_manager, weights.useful_recruiter_or_manager, "useful recruiting/hiring responsibility"),
    ):
        if condition: raw += points; factors.append(label)
    if _contains(candidate.current_title, EXECUTIVE_TERMS): raw -= weights.executive_penalty; penalties.append("distant executive")
    if not technical and not useful_manager: raw -= weights.unrelated_penalty; penalties.append("weak technical relevance")
    if _is_stale(candidate): raw -= weights.stale_penalty; penalties.append("stale provider observation")
    if candidate.provider_confidence < 0.55: raw -= weights.low_confidence_penalty; penalties.append("low-confidence identity/data match")
    tier = 1 if employer and wgu and technical else 2 if employer and wgu else 3 if employer and technical else 4 if employer and exact_role else 5
    return RelevanceScore(max(0, min(100, raw)), tier, tuple(factors), tuple(penalties))


def why_relevant(candidate: CandidatePerson, target: DiscoveryTarget, score: RelevanceScore, relevant_years: float | None) -> str:
    parts: list[str] = []
    if _has_wgu(candidate.education): parts.append("WGU affiliation")
    parts.append(f"{candidate.current_title} at {candidate.current_employer}")
    certs = [c.name for c in candidate.certifications if c.explicitly_reported and _contains(c.name, CERT_TERMS)]
    if certs: parts.append(", ".join(certs[:3]))
    previous = _previous(candidate.experience, candidate.current_employer)
    if previous and _technical(previous.title): parts.append(f"previously {previous.title} at {previous.employer}")
    if relevant_years is not None: parts.append(f"estimated {relevant_years:.1f} years relevant technical experience")
    if _location_matches(candidate.current_location or "", target.metro): parts.append(f"in {target.metro}")
    return "; ".join(parts) + "."


def estimate_relevant_experience_years(experience: Sequence[ExperienceRecord], *, as_of: date | None = None) -> float | None:
    as_of = as_of or datetime.now(timezone.utc).date()
    intervals: list[tuple[date, date]] = []
    for item in experience:
        if not (_technical(item.title) or _technical(item.employer)): continue
        start = _partial_date(item.start_date, end=False)
        end = as_of if item.is_current or not item.end_date else _partial_date(item.end_date, end=True)
        if start and end and end >= start: intervals.append((start, min(end, as_of)))
    if not intervals: return None
    intervals.sort(); merged: list[list[date]] = []
    for start, end in intervals:
        if not merged or start > merged[-1][1] + timedelta(days=1): merged.append([start, end])
        elif end > merged[-1][1]: merged[-1][1] = end
    days = sum((end - start).days + 1 for start, end in merged)
    return round(days / 365.2425, 1)


def identity_keys(candidate: CandidatePerson) -> tuple[str, ...]:
    keys: set[str] = set()
    if candidate.provider_person_id: keys.add(f"provider:{_norm(candidate.provider)}:{candidate.provider_person_id.strip()}")
    if candidate.linkedin_url: keys.add(f"linkedin:{normalize_linkedin_url(candidate.linkedin_url)}")
    for url in candidate.public_profile_urls: keys.add(f"profile:{normalize_url(url)}")
    keys.add("fallback:" + "|".join((_norm(candidate.full_name), _norm(candidate.current_employer), _norm(candidate.current_location or ""), _norm(candidate.current_title))))
    return tuple(sorted(keys))


def stable_person_id(candidate: CandidatePerson) -> str:
    keys = identity_keys(candidate)
    strong = [k for k in keys if not k.startswith("fallback:")]
    return str(uuid5(NAMESPACE_URL, "mira:career-person:" + (strong[0] if strong else keys[0])))


def normalize_linkedin_url(url: str) -> str:
    normalized = normalize_url(url); parts = urlsplit(normalized)
    host = "www.linkedin.com" if parts.netloc.lower() in {"linkedin.com", "www.linkedin.com"} else parts.netloc.lower()
    return urlunsplit(("https", host, re.sub(r"/+$", "", parts.path), "", ""))


def normalize_url(url: str) -> str:
    if not isinstance(url, str) or not url.strip(): raise ValidationError("URL must be a non-empty string")
    parts = urlsplit(url.strip())
    if parts.scheme not in {"http", "https"} or not parts.netloc: raise ValidationError("URL must use http or https with a host")
    return urlunsplit(("https", parts.netloc.lower(), re.sub(r"/+$", "", parts.path) or "/", "", ""))


def _records_match(current: CanonicalPerson, incoming: CanonicalPerson) -> bool:
    left, right = set(current.identity_keys), set(incoming.identity_keys); shared = left & right
    if any(not k.startswith("fallback:") for k in shared): return True
    if not any(k.startswith("fallback:") for k in shared): return False
    left_strong = {k for k in left if not k.startswith("fallback:")}; right_strong = {k for k in right if not k.startswith("fallback:")}
    if left_strong and right_strong and not left_strong & right_strong: return False
    return min(current.confidence, incoming.confidence) >= 0.80


def _assert_merge_safe(current: CanonicalPerson, incoming: CanonicalPerson) -> None:
    left, right = set(current.identity_keys), set(incoming.identity_keys)
    if not left & right: raise IdentityConflictError("canonical people do not share an identity key")
    for prefix, label in (("linkedin:", "LinkedIn"),):
        a = {k for k in left if k.startswith(prefix)}; b = {k for k in right if k.startswith(prefix)}
        if a and b and a != b: raise IdentityConflictError(f"conflicting {label} identities")
    a = _provider_map(k for k in left if k.startswith("provider:")); b = _provider_map(k for k in right if k.startswith("provider:"))
    for provider in set(a) & set(b):
        if a[provider] != b[provider]: raise IdentityConflictError(f"conflicting {provider} provider identities")


def _provider_map(keys: Iterable[str]) -> dict[str, str]:
    out = {}
    for key in keys:
        _, provider, identifier = key.split(":", 2); out[provider] = identifier
    return out


def _merge_observations(left: Sequence[FieldObservation], right: Sequence[FieldObservation]) -> tuple[FieldObservation, ...]:
    keyed = {(o.field_name, o.value, o.source.source, o.source.source_id, o.source.observed_at): o for o in (*left, *right)}
    values: dict[str, set[str]] = {}
    for o in keyed.values(): values.setdefault(o.field_name, set()).add(_norm(o.value))
    out = [replace(o, source=replace(o.source, status="conflicting")) if len(values[o.field_name]) > 1 and o.source.status == "verified" else o for o in keyed.values()]
    return tuple(sorted(out, key=lambda o: (o.field_name, o.source.observed_at, o.source.source, o.value)))


def _resolve_field(field: str, current: str | None, incoming: str | None, provenance: Sequence[FieldObservation]) -> str | None:
    if not incoming or _norm(incoming) == _norm(current or ""): return current or incoming
    if not current: return incoming
    rank = {"human_entered": 3, "verified": 2, "inferred": 1}
    candidates = [o for o in provenance if o.field_name == field and o.source.status not in {"stale", "conflicting"}]
    candidates.sort(key=lambda o: (rank.get(o.source.status, 0), o.source.confidence, o.source.observed_at), reverse=True)
    if candidates:
        top = candidates[0]; key = (rank.get(top.source.status, 0), top.source.confidence, top.source.observed_at)
        tied = [o for o in candidates if (rank.get(o.source.status, 0), o.source.confidence, o.source.observed_at) == key]
        if len({_norm(o.value) for o in tied}) == 1: return top.value
    return current


def _default_observations(c: CandidatePerson, source: SourceRef) -> tuple[FieldObservation, ...]:
    values = {"full_name": c.full_name, "current_title": c.current_title, "current_employer": c.current_employer, "current_location": c.current_location, "linkedin_url": c.linkedin_url, "profile_photo_url_or_reference": c.profile_photo_url_or_reference}
    return tuple(FieldObservation(k, v, source) for k, v in values.items() if v)


def _has_wgu(education: Sequence[EducationRecord]) -> bool: return any(_contains(e.school_name, WGU_TERMS) for e in education)
def _technical(value: str) -> bool: return _contains(value, TECH_TERMS)
def _technical_strength(c: CandidatePerson) -> bool: return _technical(" ".join((c.current_title, " ".join(c.skills), " ".join(e.title for e in c.experience))))
def _matches_role(title: str, roles: Sequence[str]) -> bool:
    value = _norm(title); return any(_norm(r) in value or value in _norm(r) for r in roles)
def _same_org(a: str, b: str) -> bool:
    a, b = _norm_org(a), _norm_org(b); return a == b or (len(a) >= 4 and len(b) >= 4 and (a in b or b in a))
def _norm_org(value: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"\b(inc|incorporated|llc|ltd|limited|corp|corporation|company|co|technologies|technology)\b", "", _norm(value))).strip()
def _contains(value: str, terms: Sequence[str]) -> bool:
    value = _norm(value); return any(_norm(term) in value for term in terms)
def _norm(value: str) -> str: return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9+#]+", " ", value.lower())).strip()


def _previous(experience: Sequence[ExperienceRecord], employer: str) -> ExperienceRecord | None:
    prior = [e for e in experience if not e.is_current and not _same_org(e.employer, employer)]
    return max(prior, key=lambda e: e.end_date or "") if prior else None


def _similar_progression(experience: Sequence[ExperienceRecord]) -> bool:
    relevant = [e for e in experience if _technical(e.title)]
    return len(relevant) >= 2 and max(_seniority(e.title) for e in relevant) > min(_seniority(e.title) for e in relevant)


def _seniority(title: str) -> int:
    value = _norm(title)
    if any(t in value for t in ("director", "head", "vp", "vice president", "chief")): return 4
    if any(t in value for t in ("manager", "lead", "principal")): return 3
    if any(t in value for t in ("senior", "sr ")): return 2
    if any(t in value for t in ("junior", "jr ", "associate", "technician", "support")): return 0
    return 1


def _recent_transition(experience: Sequence[ExperienceRecord]) -> bool:
    current = [e for e in experience if e.is_current and _technical(e.title)]
    if not current: return False
    start = _partial_date(current[0].start_date, end=False)
    return bool(start and 0 <= (datetime.now(timezone.utc).date() - start).days <= 1096)


def _is_stale(candidate: CandidatePerson) -> bool:
    return bool(candidate.provider_last_verified_at and (datetime.now(timezone.utc) - _timestamp(candidate.provider_last_verified_at)).days > 365)


def _location_matches(location: str, metro: str) -> bool:
    a, b = _norm(location), _norm(metro)
    if not a: return False
    if a in b or b in a: return True
    groups = {
        "austin": ("austin", "round rock", "cedar park", "pflugerville", "georgetown"),
        "research triangle": ("raleigh", "durham", "research triangle", "research triangle park", "rtp", "cary", "morrisville", "chapel hill"),
    }
    return any(anchor in b and any(alias in a for alias in aliases) for anchor, aliases in groups.items())


def _partial_date(value: str | None, *, end: bool) -> date | None:
    if not value: return None
    for fmt in ("%Y-%m-%d", "%Y-%m", "%Y"):
        try: parsed = datetime.strptime(value.strip(), fmt).date()
        except ValueError: continue
        if fmt == "%Y-%m" and end:
            return date(parsed.year, 12, 31) if parsed.month == 12 else date(parsed.year, parsed.month + 1, 1) - timedelta(days=1)
        if fmt == "%Y" and end: return date(parsed.year, 12, 31)
        return parsed
    return None


def _timestamp(value: str) -> datetime:
    if not isinstance(value, str) or not value.strip() or value.strip() != value: raise ValidationError("timestamp must be a trimmed ISO-8601 string")
    try: parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc: raise ValidationError("timestamp must be ISO-8601") from exc
    if parsed.tzinfo is None: raise ValidationError("timestamp must be offset-aware")
    return parsed.astimezone(timezone.utc)


def _trimmed(value: str, field: str) -> str:
    if not isinstance(value, str) or not value or value.strip() != value: raise ValidationError(f"{field} must be a trimmed non-empty string")
    return value


def _now() -> str: return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
def _max_optional(a: float | None, b: float | None) -> float | None: return b if a is None else a if b is None else max(a, b)


__all__ = [
    "CandidatePerson", "CanonicalPerson", "CertificationRecord", "DiscoveryResult",
    "DiscoveryTarget", "EducationRecord", "ExperienceRecord", "FieldObservation",
    "IdentityConflictError", "PeopleDiscoveryError", "RelevanceScore", "ScoreWeights",
    "SourceRef", "ValidationError", "canonicalize_candidate",
    "estimate_relevant_experience_years", "identity_keys", "merge_people",
    "normalize_linkedin_url", "normalize_url", "score_candidate", "stable_person_id",
    "upsert_candidate", "why_relevant",
]
