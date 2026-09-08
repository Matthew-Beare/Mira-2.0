"""Google Sheets projection for canonical MIRA career state.

The spreadsheet is a human-readable projection and bounded input surface, not a
second canonical authority. Rows are keyed by stable canonical IDs, reruns replace
the matching row instead of appending duplicates, and every mutation is followed by
exact readback.

This module reuses the repository's existing ``SheetsGateway`` / ``SheetRowMutation``
contract. It does not contain Google credentials, spreadsheet IDs, provider keys,
private person data, or outbound-contact actions.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Protocol, Sequence

from .google_sheets_store import SheetRowMutation
from .people_discovery import CanonicalPerson, DiscoveryTarget
from .people_tracker import (
    DEFAULT_TRACKER_PROJECTION,
    InteractionView,
    RelationshipSummary,
    TrackerProjection,
    interaction_row,
)


class PeopleSheetProjectionError(Exception):
    """Career tracker projection/readback could not be proven."""


class TrackerSheetsGateway(Protocol):
    def read_range(self, a1_range: str) -> Sequence[Sequence[object]]: ...

    def apply_mutations(self, mutations: Sequence[SheetRowMutation]) -> None: ...


@dataclass(frozen=True)
class CareerJobProjection:
    job_id: str
    company_id: str
    title: str
    location: str
    url: str
    status: str
    discovered_at: str
    applied_at: str | None = None
    notes: str | None = None


@dataclass(frozen=True)
class ProjectionWriteResult:
    tab: str
    row_id: str
    row_number: int
    created: bool
    changed: bool
    exact_readback: bool


class PeopleTrackerSheetProjector:
    """Stable-ID upsert/readback for COMPANIES/PEOPLE/INTERACTIONS/JOBS."""

    def __init__(
        self,
        gateway: TrackerSheetsGateway,
        *,
        projection: TrackerProjection = DEFAULT_TRACKER_PROJECTION,
        row_limit: int = 5000,
    ) -> None:
        if not isinstance(row_limit, int) or isinstance(row_limit, bool) or row_limit < 2:
            raise PeopleSheetProjectionError("row_limit must be an integer >= 2")
        self._gateway = gateway
        self._projection = projection
        self._row_limit = row_limit

    def bootstrap_headers(self) -> None:
        for tab, headers in self._tabs():
            self._ensure_header(tab, headers)

    def upsert_company(
        self,
        target: DiscoveryTarget,
        *,
        career_url: str | None = None,
        notes: str | None = None,
    ) -> ProjectionWriteResult:
        row = (
            target.company_id,
            target.company_name,
            target.metro,
            target.priority,
            career_url or "",
            notes or "",
        )
        return self._upsert("COMPANIES", self._projection.companies_headers, row)

    def upsert_person(
        self,
        person: CanonicalPerson,
        relationship: RelationshipSummary,
    ) -> ProjectionWriteResult:
        if person.person_id != relationship.person_id:
            raise PeopleSheetProjectionError(
                "person and relationship summaries refer to different canonical IDs"
            )
        profile_url = person.linkedin_url or (
            person.public_profile_urls[0] if person.public_profile_urls else ""
        )
        row = (
            person.person_id,
            person.full_name,
            person.current_title,
            person.current_employer,
            person.current_location or "",
            profile_url,
            person.profile_photo_url_or_reference or "",
            person.previous_employer or "",
            person.previous_title or "",
            person.estimated_relevant_experience_years
            if person.estimated_relevant_experience_years is not None
            else "",
            person.wgu_connection,
            "; ".join(person.certifications),
            "; ".join(person.relevant_skills_or_keywords),
            person.why_relevant,
            person.priority_score,
            person.priority_tier,
            relationship.relationship_state,
            relationship.have_i_contacted_them,
            relationship.have_they_replied,
            relationship.awaiting_reply,
            relationship.last_interaction_at or "",
            relationship.last_channel or "",
            relationship.follow_up_due or "",
            person.last_verified_at,
            person.confidence,
            person.notes or "",
        )
        return self._upsert("PEOPLE", self._projection.people_headers, row)

    def upsert_interaction(self, interaction: InteractionView) -> ProjectionWriteResult:
        return self._upsert(
            "INTERACTIONS",
            self._projection.interactions_headers,
            interaction_row(interaction),
        )

    def upsert_job(self, job: CareerJobProjection) -> ProjectionWriteResult:
        row = (
            job.job_id,
            job.company_id,
            job.title,
            job.location,
            job.url,
            job.status,
            job.discovered_at,
            job.applied_at or "",
            job.notes or "",
        )
        return self._upsert("JOBS", self._projection.jobs_headers, row)

    def read_row(self, tab: str, row_id: str) -> tuple[object, ...] | None:
        headers = self._headers(tab)
        rows = self._read_table(tab, headers)
        matches = [row for _, row in rows if str(row[0]) == row_id]
        if len(matches) > 1:
            raise PeopleSheetProjectionError(
                f"duplicate stable ID {row_id!r} in tracker tab {tab}"
            )
        return matches[0] if matches else None

    def _upsert(
        self,
        tab: str,
        headers: tuple[str, ...],
        row: tuple[object, ...],
    ) -> ProjectionWriteResult:
        if len(row) != len(headers):
            raise PeopleSheetProjectionError(
                f"{tab} row width {len(row)} does not match header width {len(headers)}"
            )
        row_id = str(row[0]).strip()
        if not row_id:
            raise PeopleSheetProjectionError(f"{tab} stable row ID must not be empty")
        self._ensure_header(tab, headers)
        existing = [item for item in self._read_table(tab, headers) if str(item[1][0]) == row_id]
        if len(existing) > 1:
            raise PeopleSheetProjectionError(
                f"duplicate stable ID {row_id!r} in tracker tab {tab}"
            )
        if existing and existing[0][1] == row:
            return ProjectionWriteResult(
                tab=tab,
                row_id=row_id,
                row_number=existing[0][0],
                created=False,
                changed=False,
                exact_readback=True,
            )

        row_number = existing[0][0] if existing else None
        self._gateway.apply_mutations(
            (SheetRowMutation(tab=tab, values=row, row_number=row_number),)
        )
        readback = self.read_row(tab, row_id)
        if readback != row:
            raise PeopleSheetProjectionError(
                f"{tab} exact readback mismatch for stable ID {row_id!r}"
            )
        if row_number is None:
            table = self._read_table(tab, headers)
            matched_numbers = [number for number, values in table if str(values[0]) == row_id]
            if len(matched_numbers) != 1:
                raise PeopleSheetProjectionError(
                    f"{tab} could not prove one row after append for {row_id!r}"
                )
            row_number = matched_numbers[0]
        return ProjectionWriteResult(
            tab=tab,
            row_id=row_id,
            row_number=row_number,
            created=not bool(existing),
            changed=True,
            exact_readback=True,
        )

    def _ensure_header(self, tab: str, headers: tuple[str, ...]) -> None:
        rows = tuple(tuple(row) for row in self._gateway.read_range(self._range(tab)))
        if not rows:
            self._gateway.apply_mutations(
                (SheetRowMutation(tab=tab, values=headers, row_number=None),)
            )
            rows = tuple(tuple(row) for row in self._gateway.read_range(self._range(tab)))
        if not rows:
            raise PeopleSheetProjectionError(f"tracker tab {tab} remains empty after bootstrap")
        actual = tuple(str(value) for value in rows[0])
        if actual != headers:
            raise PeopleSheetProjectionError(
                f"tracker tab {tab} header mismatch: {actual!r}"
            )

    def _read_table(
        self, tab: str, headers: tuple[str, ...]
    ) -> tuple[tuple[int, tuple[object, ...]], ...]:
        rows = tuple(tuple(row) for row in self._gateway.read_range(self._range(tab)))
        if not rows:
            raise PeopleSheetProjectionError(f"tracker tab {tab} is empty")
        actual = tuple(str(value) for value in rows[0])
        if actual != headers:
            raise PeopleSheetProjectionError(
                f"tracker tab {tab} header mismatch: {actual!r}"
            )
        width = len(headers)
        output: list[tuple[int, tuple[object, ...]]] = []
        for row_number, raw in enumerate(rows[1:], start=2):
            if not raw or all(value in (None, "") for value in raw):
                continue
            if len(raw) > width:
                raise PeopleSheetProjectionError(
                    f"tracker tab {tab} row {row_number} is wider than its schema"
                )
            output.append((row_number, raw + ("",) * (width - len(raw))))
        return tuple(output)

    def _headers(self, tab: str) -> tuple[str, ...]:
        mapping: Mapping[str, tuple[str, ...]] = dict(self._tabs())
        try:
            return mapping[tab]
        except KeyError as exc:
            raise PeopleSheetProjectionError(f"unknown career tracker tab: {tab}") from exc

    def _tabs(self) -> tuple[tuple[str, tuple[str, ...]], ...]:
        return (
            ("COMPANIES", self._projection.companies_headers),
            ("PEOPLE", self._projection.people_headers),
            ("INTERACTIONS", self._projection.interactions_headers),
            ("JOBS", self._projection.jobs_headers),
        )

    def _range(self, tab: str) -> str:
        # ZZ comfortably covers the bounded tracker schemas while retaining the
        # generic repository Sheets gateway and avoiding a duplicate HTTP client.
        return f"{tab}!A1:ZZ{self._row_limit}"
