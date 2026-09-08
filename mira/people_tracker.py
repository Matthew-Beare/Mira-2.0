"""Canonical career relationship tracking and tracker projection for MIRA.

This module records observed/manual relationship events such as LinkedIn messages,
email replies, calls and meetings. It deliberately contains no send/connect/post
capability. Outbound actions are performed by the human; MIRA records what happened,
derives reply/follow-up state and projects canonical state into a human-readable
tracker.

Provider credentials, live spreadsheet IDs, private message bodies and third-party
person data do not belong in public source control. Public tests use synthetic data.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
import re
from typing import Any, Mapping, Sequence

from .structured_state import (
    StructuredStateAdapter,
    ValidationError as StoreValidationError,
)


INTERACTION_RESOURCE_TYPE = "career_interaction"
INTERACTION_SCHEMA_VERSION = 1

CHANNELS = frozenset({"linkedin", "email", "phone", "video", "in_person", "other"})
DIRECTIONS = frozenset({"outbound", "inbound"})
KINDS = frozenset(
    {
        "connection_request",
        "message",
        "email",
        "reply",
        "call",
        "meeting",
        "follow_up",
        "referral",
        "note",
        "other",
    }
)
OUTCOMES = frozenset(
    {
        "sent",
        "received",
        "accepted",
        "replied",
        "conversation",
        "referral",
        "declined",
        "no_reply",
        "closed",
        "other",
    }
)
RELATIONSHIP_STATES = frozenset(
    {
        "not_contacted",
        "contacted",
        "awaiting_reply",
        "replied",
        "conversation",
        "referral",
        "closed",
    }
)

_TOKEN_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")


class PeopleTrackerError(Exception):
    """Base career tracker failure."""


class PeopleTrackerValidationError(PeopleTrackerError):
    """Raised when observed interaction data is malformed."""


@dataclass(frozen=True)
class InteractionView:
    interaction_id: str
    revision: int
    person_id: str
    company_id: str | None
    job_id: str | None
    channel: str
    direction: str
    kind: str
    occurred_at: str
    outcome: str
    summary: str | None
    source_ref: str | None
    reply_to_interaction_id: str | None
    follow_up_due: str | None
    idempotent_replay: bool = False


@dataclass(frozen=True)
class RelationshipSummary:
    person_id: str
    relationship_state: str
    have_i_contacted_them: bool
    have_they_replied: bool
    awaiting_reply: bool
    interaction_count: int
    last_interaction_at: str | None
    last_outbound_at: str | None
    last_inbound_at: str | None
    last_channel: str | None
    follow_up_due: str | None

    def __post_init__(self) -> None:
        if self.relationship_state not in RELATIONSHIP_STATES:
            raise PeopleTrackerValidationError("invalid relationship_state")


@dataclass(frozen=True)
class TrackerProjection:
    """Provider-neutral rows for the human-readable Google tracker."""

    companies_headers: tuple[str, ...]
    people_headers: tuple[str, ...]
    interactions_headers: tuple[str, ...]
    jobs_headers: tuple[str, ...]


DEFAULT_TRACKER_PROJECTION = TrackerProjection(
    companies_headers=(
        "company_id",
        "company_name",
        "market",
        "priority",
        "career_url",
        "notes",
    ),
    people_headers=(
        "person_id",
        "full_name",
        "current_title",
        "current_employer",
        "location",
        "linkedin_or_profile_url",
        "profile_photo_reference",
        "previous_employer",
        "previous_title",
        "relevant_experience_years",
        "wgu_connection",
        "certifications",
        "skills_keywords",
        "why_relevant",
        "priority_score",
        "priority_tier",
        "relationship_state",
        "have_i_contacted_them",
        "have_they_replied",
        "awaiting_reply",
        "last_interaction_at",
        "last_channel",
        "follow_up_due",
        "last_verified_at",
        "confidence",
        "notes",
    ),
    interactions_headers=(
        "interaction_id",
        "person_id",
        "company_id",
        "job_id",
        "channel",
        "direction",
        "kind",
        "occurred_at",
        "outcome",
        "summary",
        "source_ref",
        "reply_to_interaction_id",
        "follow_up_due",
    ),
    jobs_headers=(
        "job_id",
        "company_id",
        "title",
        "location",
        "url",
        "status",
        "discovered_at",
        "applied_at",
        "notes",
    ),
)


class CareerInteractionService:
    """Append-only canonical relationship facts over STORE-001 structured state.

    An interaction is an observed/manual fact. Corrections are represented by a new
    interaction or a future explicit correction event; this service does not silently
    rewrite relationship history and exposes no outbound messaging action.
    """

    def __init__(
        self,
        adapter: StructuredStateAdapter,
        *,
        resource_type: str = INTERACTION_RESOURCE_TYPE,
    ) -> None:
        self._adapter = adapter
        self._resource_type = resource_type

    def record(
        self,
        interaction_id: str,
        *,
        person_id: str,
        channel: str,
        direction: str,
        kind: str,
        occurred_at: str,
        outcome: str,
        idempotency_key: str,
        company_id: str | None = None,
        job_id: str | None = None,
        summary: str | None = None,
        source_ref: str | None = None,
        reply_to_interaction_id: str | None = None,
        follow_up_due: str | None = None,
    ) -> InteractionView:
        interaction = _token(interaction_id, "interaction_id")
        person = _token(person_id, "person_id")
        payload = _payload(
            interaction_id=interaction,
            person_id=person,
            company_id=_optional_token(company_id, "company_id"),
            job_id=_optional_token(job_id, "job_id"),
            channel=_enum(channel, CHANNELS, "channel"),
            direction=_enum(direction, DIRECTIONS, "direction"),
            kind=_enum(kind, KINDS, "kind"),
            occurred_at=_timestamp(occurred_at, "occurred_at"),
            outcome=_enum(outcome, OUTCOMES, "outcome"),
            summary=_optional_text(summary, "summary", max_length=1000),
            source_ref=_optional_text(source_ref, "source_ref", max_length=500),
            reply_to_interaction_id=_optional_token(
                reply_to_interaction_id, "reply_to_interaction_id"
            ),
            follow_up_due=_optional_date(follow_up_due, "follow_up_due"),
        )
        if payload["reply_to_interaction_id"] == interaction:
            raise PeopleTrackerValidationError("an interaction cannot reply to itself")
        if payload["direction"] == "inbound" and payload["outcome"] == "sent":
            raise PeopleTrackerValidationError("inbound interaction cannot have sent outcome")
        if payload["direction"] == "outbound" and payload["outcome"] == "received":
            raise PeopleTrackerValidationError("outbound interaction cannot have received outcome")
        try:
            result = self._adapter.upsert(
                self._resource_type,
                interaction,
                payload,
                idempotency_key=_token(idempotency_key, "idempotency_key"),
                expected_revision=0,
            )
        except StoreValidationError as exc:
            raise PeopleTrackerValidationError(str(exc)) from exc
        return _view(result.record, idempotent_replay=result.idempotent_replay)

    def for_person(self, person_id: str, *, limit: int = 1000) -> tuple[InteractionView, ...]:
        person = _token(person_id, "person_id")
        try:
            records = self._adapter.query(
                self._resource_type,
                filters={"person_id": person},
                limit=limit,
            )
        except StoreValidationError as exc:
            raise PeopleTrackerValidationError(str(exc)) from exc
        interactions = [_view(record) for record in records]
        interactions.sort(key=lambda item: (item.occurred_at, item.interaction_id))
        return tuple(interactions)

    def relationship_summary(self, person_id: str) -> RelationshipSummary:
        person = _token(person_id, "person_id")
        interactions = self.for_person(person)
        if not interactions:
            return RelationshipSummary(
                person_id=person,
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
            )

        outbound = [item for item in interactions if item.direction == "outbound"]
        inbound = [item for item in interactions if item.direction == "inbound"]
        have_i_contacted = bool(outbound)
        have_they_replied = _has_reply(interactions, outbound)
        last_outbound = outbound[-1] if outbound else None
        last_inbound = inbound[-1] if inbound else None
        awaiting_reply = bool(
            last_outbound
            and not _has_inbound_after(inbound, last_outbound.occurred_at)
            and last_outbound.outcome not in {"closed", "declined"}
        )
        state = _relationship_state(interactions, have_i_contacted, have_they_replied, awaiting_reply)
        follow_up_due = _next_follow_up(interactions)
        last = interactions[-1]
        return RelationshipSummary(
            person_id=person,
            relationship_state=state,
            have_i_contacted_them=have_i_contacted,
            have_they_replied=have_they_replied,
            awaiting_reply=awaiting_reply,
            interaction_count=len(interactions),
            last_interaction_at=last.occurred_at,
            last_outbound_at=last_outbound.occurred_at if last_outbound else None,
            last_inbound_at=last_inbound.occurred_at if last_inbound else None,
            last_channel=last.channel,
            follow_up_due=follow_up_due,
        )


def interaction_row(interaction: InteractionView) -> tuple[object, ...]:
    """Render one canonical interaction into the INTERACTIONS tracker tab."""

    return (
        interaction.interaction_id,
        interaction.person_id,
        interaction.company_id or "",
        interaction.job_id or "",
        interaction.channel,
        interaction.direction,
        interaction.kind,
        interaction.occurred_at,
        interaction.outcome,
        interaction.summary or "",
        interaction.source_ref or "",
        interaction.reply_to_interaction_id or "",
        interaction.follow_up_due or "",
    )


def relationship_columns(summary: RelationshipSummary) -> Mapping[str, object]:
    """Columns projected into PEOPLE without making the sheet a second authority."""

    return {
        "relationship_state": summary.relationship_state,
        "have_i_contacted_them": summary.have_i_contacted_them,
        "have_they_replied": summary.have_they_replied,
        "awaiting_reply": summary.awaiting_reply,
        "last_interaction_at": summary.last_interaction_at or "",
        "last_channel": summary.last_channel or "",
        "follow_up_due": summary.follow_up_due or "",
    }


def _payload(**values: object) -> dict[str, object]:
    return {"schema_version": INTERACTION_SCHEMA_VERSION, **values}


def _view(record: Any, *, idempotent_replay: bool = False) -> InteractionView:
    payload = record.payload
    if payload.get("schema_version") != INTERACTION_SCHEMA_VERSION:
        raise PeopleTrackerValidationError("unsupported career interaction schema_version")
    required = (
        "interaction_id",
        "person_id",
        "channel",
        "direction",
        "kind",
        "occurred_at",
        "outcome",
    )
    if any(key not in payload for key in required):
        raise PeopleTrackerValidationError("persisted career interaction is incomplete")
    return InteractionView(
        interaction_id=_token(str(payload["interaction_id"]), "interaction_id"),
        revision=record.revision,
        person_id=_token(str(payload["person_id"]), "person_id"),
        company_id=_optional_token(payload.get("company_id"), "company_id"),
        job_id=_optional_token(payload.get("job_id"), "job_id"),
        channel=_enum(str(payload["channel"]), CHANNELS, "channel"),
        direction=_enum(str(payload["direction"]), DIRECTIONS, "direction"),
        kind=_enum(str(payload["kind"]), KINDS, "kind"),
        occurred_at=_timestamp(str(payload["occurred_at"]), "occurred_at"),
        outcome=_enum(str(payload["outcome"]), OUTCOMES, "outcome"),
        summary=_optional_text(payload.get("summary"), "summary", max_length=1000),
        source_ref=_optional_text(payload.get("source_ref"), "source_ref", max_length=500),
        reply_to_interaction_id=_optional_token(
            payload.get("reply_to_interaction_id"), "reply_to_interaction_id"
        ),
        follow_up_due=_optional_date(payload.get("follow_up_due"), "follow_up_due"),
        idempotent_replay=idempotent_replay,
    )


def _has_reply(interactions: Sequence[InteractionView], outbound: Sequence[InteractionView]) -> bool:
    outbound_ids = {item.interaction_id for item in outbound}
    for item in interactions:
        if item.direction != "inbound":
            continue
        if item.reply_to_interaction_id in outbound_ids:
            return True
        if item.kind == "reply" or item.outcome in {"replied", "conversation", "referral"}:
            return True
    return False


def _has_inbound_after(inbound: Sequence[InteractionView], occurred_at: str) -> bool:
    return any(item.occurred_at >= occurred_at for item in inbound)


def _relationship_state(
    interactions: Sequence[InteractionView],
    have_i_contacted: bool,
    have_they_replied: bool,
    awaiting_reply: bool,
) -> str:
    outcomes = {item.outcome for item in interactions}
    if "referral" in outcomes:
        return "referral"
    if "conversation" in outcomes:
        return "conversation"
    if interactions[-1].outcome in {"closed", "declined"}:
        return "closed"
    if have_they_replied:
        return "replied"
    if awaiting_reply:
        return "awaiting_reply"
    if have_i_contacted:
        return "contacted"
    return "not_contacted"


def _next_follow_up(interactions: Sequence[InteractionView]) -> str | None:
    dated = [item.follow_up_due for item in interactions if item.follow_up_due]
    return max(dated) if dated else None


def _enum(value: object, allowed: frozenset[str], field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise PeopleTrackerValidationError(f"{field} must be a non-empty string")
    normalized = value.strip().lower()
    if normalized not in allowed:
        raise PeopleTrackerValidationError(f"invalid {field}: {value!r}")
    return normalized


def _token(value: object, field: str) -> str:
    if not isinstance(value, str) or not _TOKEN_RE.fullmatch(value.strip()):
        raise PeopleTrackerValidationError(f"{field} must be a stable token")
    return value.strip()


def _optional_token(value: object, field: str) -> str | None:
    if value is None or value == "":
        return None
    return _token(value, field)


def _optional_text(value: object, field: str, *, max_length: int) -> str | None:
    if value is None or value == "":
        return None
    if not isinstance(value, str):
        raise PeopleTrackerValidationError(f"{field} must be text")
    text = value.strip()
    if not text:
        return None
    if len(text) > max_length:
        raise PeopleTrackerValidationError(f"{field} exceeds {max_length} characters")
    return text


def _timestamp(value: str, field: str) -> str:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise PeopleTrackerValidationError(f"{field} must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise PeopleTrackerValidationError(f"{field} must include a timezone")
    return parsed.isoformat()


def _optional_date(value: object, field: str) -> str | None:
    if value is None or value == "":
        return None
    if not isinstance(value, str):
        raise PeopleTrackerValidationError(f"{field} must be YYYY-MM-DD")
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise PeopleTrackerValidationError(f"{field} must be YYYY-MM-DD") from exc
    return parsed.isoformat()
