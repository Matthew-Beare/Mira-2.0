"""Provider-neutral onboarding and progressive discovery for Personal MIRA.

Minimum Useful Setup remains the deterministic four-question ONBOARD-003 front
door. After those four questions, ONBOARD-004 may continue immediately or use a
bounded one-topic-per-local-day discovery drip. Both ledgers use the existing
STORE-001-compatible ``onboarding_ledger`` resource type and contain no Google
row coordinates, provider IDs, Android assumptions, or silent service activation.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import date
from typing import Any, Mapping
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from .structured_state import (
    NotFoundError,
    ResourceRecord,
    StructuredStateAdapter,
    ValidationError as StoreValidationError,
)


INTERVIEW_ID = "minimum-useful-setup"
DISCOVERY_ID = "progressive-discovery"
LEDGER_RESOURCE_TYPE = "onboarding_ledger"
LEDGER_SCHEMA_VERSION = 1
DISCOVERY_SCHEMA_VERSION = 1
DISCOVERY_BRIEF_TOPIC_LIMIT = 7


class OnboardingError(Exception):
    """Base class for onboarding failures."""


class OnboardingValidationError(OnboardingError):
    """Raised when an onboarding answer or transition is malformed or unsafe."""


class QuestionOrderError(OnboardingError):
    """Raised when an unanswered question is submitted out of canonical order."""


class AnswerConflictError(OnboardingError):
    """Raised when a prior answer would be changed without explicit replacement."""


@dataclass(frozen=True)
class OnboardingQuestion:
    question_id: str
    prompt: str


@dataclass(frozen=True)
class DiscoveryTopic:
    topic_id: str
    prompt: str
    followup_prompt: str | None = None


QUESTIONS = (
    OnboardingQuestion(
        question_id="timezone",
        prompt=(
            "What timezone should MIRA treat as authoritative? "
            "Use an IANA timezone such as America/New_York."
        ),
    ),
    OnboardingQuestion(
        question_id="life_pattern",
        prompt=(
            "What does your normal life look like at a broad level? "
            "Include the work, school, household, caregiving, travel, or other "
            "patterns that materially affect how MIRA should organize things."
        ),
    ),
    OnboardingQuestion(
        question_id="goals",
        prompt=(
            "What are the biggest things you want MIRA to help you remember, "
            "organize, decide, plan, or follow through on?"
        ),
    ),
    OnboardingQuestion(
        question_id="appointment_help",
        prompt=(
            "Do you want MIRA to help capture appointments and reminders? "
            "If yes, which Calendar should be your preferred future sync lane: "
            "Google, Microsoft/Outlook/M365, Apple/iCloud, another calendar, "
            "or manual/no automatic Calendar sync?"
        ),
    ),
)

QUESTION_IDS = tuple(question.question_id for question in QUESTIONS)
_QUESTION_BY_ID = {question.question_id: question for question in QUESTIONS}

DISCOVERY_TOPICS = (
    DiscoveryTopic(
        topic_id="fitness_wellness",
        prompt=(
            "Would you like MIRA to help with fitness, activity, nutrition, or "
            "weight-management goals?"
        ),
        followup_prompt=(
            "What are your goals, and what kind of help do you want from MIRA? "
            "For example: cardio, strength, both, meal or nutrition support, "
            "activity accountability, or weight goals."
        ),
    ),
    DiscoveryTopic(
        topic_id="meals_groceries",
        prompt=(
            "Would you like MIRA to help with recipes, meal planning, pantry or "
            "freezer tracking, or grocery shopping?"
        ),
    ),
    DiscoveryTopic(
        topic_id="household_routines",
        prompt=(
            "Would you like MIRA to help manage household tasks, errands, "
            "maintenance, or recurring routines?"
        ),
    ),
    DiscoveryTopic(
        topic_id="education_study",
        prompt=(
            "Would you like MIRA to help with school, certifications, study "
            "plans, deadlines, or offline preparation?"
        ),
    ),
    DiscoveryTopic(
        topic_id="receipts_assets_inventory",
        prompt=(
            "Would you like MIRA to organize purchases and receipts, warranties "
            "and manuals, vehicles or equipment, or household/shop inventory?"
        ),
    ),
    DiscoveryTopic(
        topic_id="travel_work_tracking",
        prompt=(
            "Would you like MIRA to help with travel, work trips, routes, "
            "mileage, or context-aware planning?"
        ),
    ),
    DiscoveryTopic(
        topic_id="connected_integrations",
        prompt=(
            "Would you like MIRA to use optional connected data sources such as "
            "a smartwatch or activity tracker, smart-home/local services, or "
            "additional provider accounts when supported?"
        ),
    ),
)

DISCOVERY_TOPIC_IDS = tuple(topic.topic_id for topic in DISCOVERY_TOPICS)
_DISCOVERY_BY_ID = {topic.topic_id: topic for topic in DISCOVERY_TOPICS}
_FINAL_TOPIC_STATES = frozenset({"accepted", "declined", "skipped"})

COMPLETION_ORIENTATION = (
    "Minimum Useful Setup is complete. Would you like to continue setup now, "
    "or start using MIRA? If you start using MIRA, MIRA can offer at most one "
    "short discovery topic per local day in an eligible brief for up to seven "
    "topic-days, and you can stop that at any time. You can also ask MIRA at any "
    "time to continue the interview. MIRA Studio is the guided place for adding "
    "or refining bounded preferences and workflows, and sharing is optional. "
    "Nothing is silently enabled or shared merely because setup is complete."
)

_CALENDAR_LANE_ALIASES = {
    "google": "google",
    "google calendar": "google",
    "microsoft": "microsoft",
    "outlook": "microsoft",
    "m365": "microsoft",
    "microsoft 365": "microsoft",
    "microsoft/outlook/m365": "microsoft",
    "apple": "apple",
    "icloud": "apple",
    "apple/icloud": "apple",
    "other": "other",
    "another": "other",
    "manual": "manual",
    "no auto sync": "manual",
    "no automatic sync": "manual",
}

_DISCOVERY_MODE_ALIASES = {
    "continue": "continue_now",
    "continue now": "continue_now",
    "continue setup": "continue_now",
    "continue setup now": "continue_now",
    "continue_now": "continue_now",
    "use mira": "brief_drip",
    "start using mira": "brief_drip",
    "start": "brief_drip",
    "brief drip": "brief_drip",
    "brief_drip": "brief_drip",
}


@dataclass(frozen=True)
class InterviewLedgerView:
    interview_id: str
    revision: int
    status: str
    answers: dict[str, Any]
    next_question: OnboardingQuestion | None
    completion_orientation: str | None
    idempotent_replay: bool = False

    @property
    def complete(self) -> bool:
        return self.status == "complete"


@dataclass(frozen=True)
class DiscoveryLedgerView:
    interview_id: str
    revision: int
    status: str
    mode: str | None
    answers: dict[str, Any]
    topic_states: dict[str, str]
    next_topic: DiscoveryTopic | None
    followup_prompt: str | None
    brief_drip_enabled: bool
    brief_topic_days_used: int
    last_brief_local_date: str | None
    remaining_topic_ids: tuple[str, ...]
    brief_topic_emitted: bool = False
    idempotent_replay: bool = False

    @property
    def complete(self) -> bool:
        return self.status == "complete"


class InterviewLedgerService:
    """Persist and resume ONBOARD-003 over a structured-state adapter."""

    def __init__(
        self,
        adapter: StructuredStateAdapter,
        *,
        resource_type: str = LEDGER_RESOURCE_TYPE,
    ) -> None:
        self._adapter = adapter
        self._resource_type = resource_type

    def start_or_resume(
        self,
        *,
        interview_id: str = INTERVIEW_ID,
        idempotency_key: str | None = None,
    ) -> InterviewLedgerView:
        try:
            record = self._adapter.get(self._resource_type, interview_id)
            return _view(record)
        except NotFoundError:
            payload = _empty_payload(interview_id)
            try:
                result = self._adapter.upsert(
                    self._resource_type,
                    interview_id,
                    payload,
                    idempotency_key=idempotency_key or f"onboarding-start:{interview_id}",
                    expected_revision=0,
                )
            except StoreValidationError as exc:
                raise OnboardingValidationError(str(exc)) from exc
            return _view(result.record, idempotent_replay=result.idempotent_replay)

    def answer(
        self,
        question_id: str,
        answer: Any,
        *,
        interview_id: str = INTERVIEW_ID,
        idempotency_key: str,
        replace: bool = False,
    ) -> InterviewLedgerView:
        if question_id not in _QUESTION_BY_ID:
            raise OnboardingValidationError(f"unknown onboarding question: {question_id}")
        _idempotency_key(idempotency_key)

        current = self.start_or_resume(interview_id=interview_id)
        record = self._adapter.get(self._resource_type, interview_id)
        payload = deepcopy(record.payload)
        answers = payload.get("answers")
        if not isinstance(answers, dict):
            raise OnboardingValidationError("stored Interview Ledger answers are malformed")

        normalized = _normalize_answer(question_id, answer)
        if question_id in answers:
            if answers[question_id] == normalized:
                return _view(record, idempotent_replay=True)
            if not replace:
                raise AnswerConflictError(
                    f"question {question_id} is already answered; explicit replace=True is required"
                )
        else:
            expected_question = (
                None if current.next_question is None else current.next_question.question_id
            )
            if question_id != expected_question:
                raise QuestionOrderError(
                    f"next unanswered question is {expected_question!r}, not {question_id!r}"
                )

        answers[question_id] = normalized
        _refresh_payload_state(payload)

        try:
            result = self._adapter.upsert(
                self._resource_type,
                interview_id,
                payload,
                idempotency_key=idempotency_key.strip(),
                expected_revision=record.revision,
            )
        except StoreValidationError as exc:
            raise OnboardingValidationError(str(exc)) from exc
        return _view(result.record, idempotent_replay=result.idempotent_replay)

    def get(self, *, interview_id: str = INTERVIEW_ID) -> InterviewLedgerView:
        try:
            return _view(self._adapter.get(self._resource_type, interview_id))
        except NotFoundError as exc:
            raise OnboardingValidationError("Interview Ledger has not been started") from exc


class ProgressiveDiscoveryService:
    """Persist optional post-Minimum-Setup discovery using the same resource type."""

    def __init__(
        self,
        adapter: StructuredStateAdapter,
        *,
        resource_type: str = LEDGER_RESOURCE_TYPE,
    ) -> None:
        self._adapter = adapter
        self._resource_type = resource_type
        self._minimum = InterviewLedgerService(adapter, resource_type=resource_type)

    def start_or_resume(
        self,
        *,
        interview_id: str = DISCOVERY_ID,
        idempotency_key: str | None = None,
    ) -> DiscoveryLedgerView:
        minimum = self._minimum.get()
        if not minimum.complete:
            raise OnboardingValidationError(
                "progressive discovery requires completed Minimum Useful Setup"
            )
        try:
            return _discovery_view(self._adapter.get(self._resource_type, interview_id))
        except NotFoundError:
            payload = _empty_discovery_payload(interview_id)
            try:
                result = self._adapter.upsert(
                    self._resource_type,
                    interview_id,
                    payload,
                    idempotency_key=idempotency_key
                    or f"onboarding-discovery-start:{interview_id}",
                    expected_revision=0,
                )
            except StoreValidationError as exc:
                raise OnboardingValidationError(str(exc)) from exc
            return _discovery_view(
                result.record, idempotent_replay=result.idempotent_replay
            )

    def choose_mode(
        self,
        choice: str,
        *,
        idempotency_key: str,
        interview_id: str = DISCOVERY_ID,
    ) -> DiscoveryLedgerView:
        _idempotency_key(idempotency_key)
        if not isinstance(choice, str):
            raise OnboardingValidationError("discovery choice must be text")
        mode = _DISCOVERY_MODE_ALIASES.get(choice.strip().lower())
        if mode is None:
            raise OnboardingValidationError(
                "discovery choice must be continue setup now or start using MIRA"
            )
        current = self.start_or_resume(interview_id=interview_id)
        record = self._adapter.get(self._resource_type, interview_id)
        if current.mode == mode and current.status in {"active", "complete"}:
            return _discovery_view(record, idempotent_replay=True)
        payload = deepcopy(record.payload)
        payload["mode"] = mode
        payload["brief_drip_enabled"] = mode == "brief_drip" and payload["status"] != "complete"
        if payload["status"] != "complete":
            payload["status"] = "active"
        return self._persist_discovery(
            record,
            payload,
            idempotency_key=idempotency_key,
        )

    def next_now(self, *, interview_id: str = DISCOVERY_ID) -> DiscoveryLedgerView:
        view = self.start_or_resume(interview_id=interview_id)
        if view.mode != "continue_now":
            raise OnboardingValidationError(
                "continue-now discovery is not active; choose continue setup now first"
            )
        return view

    def claim_brief_question(
        self,
        local_date: str,
        *,
        idempotency_key: str,
        interview_id: str = DISCOVERY_ID,
    ) -> DiscoveryLedgerView:
        """Claim at most one new discovery topic for one supplied local date."""

        _idempotency_key(idempotency_key)
        normalized_date = _local_date(local_date)
        view = self.start_or_resume(interview_id=interview_id)
        record = self._adapter.get(self._resource_type, interview_id)
        if view.mode != "brief_drip" or not view.brief_drip_enabled:
            return _discovery_view(record, idempotent_replay=True)
        if view.last_brief_local_date == normalized_date:
            return _discovery_view(record, idempotent_replay=True)
        if record.payload.get("current_topic_id") is not None:
            return _discovery_view(record, idempotent_replay=True)
        if view.brief_topic_days_used >= DISCOVERY_BRIEF_TOPIC_LIMIT:
            payload = deepcopy(record.payload)
            payload["brief_drip_enabled"] = False
            payload["status"] = "paused" if view.remaining_topic_ids else "complete"
            return self._persist_discovery(
                record,
                payload,
                idempotency_key=idempotency_key,
            )
        next_topic_id = _first_pending_topic(record.payload)
        if next_topic_id is None:
            payload = deepcopy(record.payload)
            payload["brief_drip_enabled"] = False
            payload["status"] = "complete"
            return self._persist_discovery(
                record,
                payload,
                idempotency_key=idempotency_key,
            )
        payload = deepcopy(record.payload)
        payload["current_topic_id"] = next_topic_id
        payload["last_brief_local_date"] = normalized_date
        payload["brief_topic_days_used"] = int(payload["brief_topic_days_used"]) + 1
        result = self._persist_discovery(
            record,
            payload,
            idempotency_key=idempotency_key,
        )
        return _discovery_view(
            self._adapter.get(self._resource_type, interview_id),
            brief_topic_emitted=True,
            idempotent_replay=result.idempotent_replay,
        )

    def answer_topic(
        self,
        topic_id: str,
        accepted: bool,
        *,
        idempotency_key: str,
        details: str | None = None,
        interview_id: str = DISCOVERY_ID,
    ) -> DiscoveryLedgerView:
        _idempotency_key(idempotency_key)
        topic = _DISCOVERY_BY_ID.get(topic_id)
        if topic is None:
            raise OnboardingValidationError(f"unknown discovery topic: {topic_id}")
        if not isinstance(accepted, bool):
            raise OnboardingValidationError("accepted must be boolean")
        view = self.start_or_resume(interview_id=interview_id)
        record = self._adapter.get(self._resource_type, interview_id)
        payload = deepcopy(record.payload)
        topic_states = payload["topic_states"]
        existing_state = topic_states[topic_id]
        if existing_state in _FINAL_TOPIC_STATES:
            existing = payload["answers"].get(topic_id)
            normalized = _discovery_answer(accepted, details)
            if existing == normalized:
                return _discovery_view(record, idempotent_replay=True)
            raise AnswerConflictError(
                f"discovery topic {topic_id} is already answered"
            )

        expected = payload.get("current_topic_id") or _first_pending_topic(payload)
        if expected != topic_id:
            raise QuestionOrderError(
                f"next discovery topic is {expected!r}, not {topic_id!r}"
            )
        if existing_state == "needs_details":
            raise OnboardingValidationError(
                f"discovery topic {topic_id} requires its follow-up answer"
            )

        payload["answers"][topic_id] = _discovery_answer(accepted, details)
        if accepted and topic.followup_prompt is not None and details is None:
            topic_states[topic_id] = "needs_details"
            payload["current_topic_id"] = topic_id
        else:
            topic_states[topic_id] = "accepted" if accepted else "declined"
            payload["current_topic_id"] = None
        _refresh_discovery_state(payload)
        return self._persist_discovery(
            record,
            payload,
            idempotency_key=idempotency_key,
        )

    def answer_followup(
        self,
        topic_id: str,
        details: str,
        *,
        idempotency_key: str,
        interview_id: str = DISCOVERY_ID,
    ) -> DiscoveryLedgerView:
        _idempotency_key(idempotency_key)
        topic = _DISCOVERY_BY_ID.get(topic_id)
        if topic is None or topic.followup_prompt is None:
            raise OnboardingValidationError(
                f"discovery topic {topic_id} has no follow-up question"
            )
        record = self._adapter.get(self._resource_type, interview_id)
        payload = deepcopy(record.payload)
        if payload.get("current_topic_id") != topic_id or payload["topic_states"].get(topic_id) != "needs_details":
            raise QuestionOrderError(
                f"discovery topic {topic_id} is not awaiting follow-up"
            )
        detail_text = _normalize_text(
            details, field=f"{topic_id}.details", max_length=6000
        )
        payload["answers"][topic_id] = {
            "accepted": True,
            "details": detail_text,
        }
        payload["topic_states"][topic_id] = "accepted"
        payload["current_topic_id"] = None
        _refresh_discovery_state(payload)
        return self._persist_discovery(
            record,
            payload,
            idempotency_key=idempotency_key,
        )

    def skip_topic(
        self,
        topic_id: str,
        *,
        idempotency_key: str,
        interview_id: str = DISCOVERY_ID,
    ) -> DiscoveryLedgerView:
        _idempotency_key(idempotency_key)
        if topic_id not in _DISCOVERY_BY_ID:
            raise OnboardingValidationError(f"unknown discovery topic: {topic_id}")
        record = self._adapter.get(self._resource_type, interview_id)
        payload = deepcopy(record.payload)
        expected = payload.get("current_topic_id") or _first_pending_topic(payload)
        if expected != topic_id:
            raise QuestionOrderError(
                f"next discovery topic is {expected!r}, not {topic_id!r}"
            )
        payload["topic_states"][topic_id] = "skipped"
        payload["answers"][topic_id] = {"skipped": True}
        payload["current_topic_id"] = None
        _refresh_discovery_state(payload)
        return self._persist_discovery(
            record,
            payload,
            idempotency_key=idempotency_key,
        )

    def disable_brief_drip(
        self,
        *,
        idempotency_key: str,
        interview_id: str = DISCOVERY_ID,
    ) -> DiscoveryLedgerView:
        _idempotency_key(idempotency_key)
        record = self._adapter.get(self._resource_type, interview_id)
        payload = deepcopy(record.payload)
        if not payload.get("brief_drip_enabled"):
            return _discovery_view(record, idempotent_replay=True)
        payload["brief_drip_enabled"] = False
        if payload.get("status") != "complete":
            payload["status"] = "paused"
        return self._persist_discovery(
            record,
            payload,
            idempotency_key=idempotency_key,
        )

    def _persist_discovery(
        self,
        record: ResourceRecord,
        payload: dict[str, Any],
        *,
        idempotency_key: str,
    ) -> DiscoveryLedgerView:
        try:
            result = self._adapter.upsert(
                self._resource_type,
                record.resource_id,
                payload,
                idempotency_key=idempotency_key.strip(),
                expected_revision=record.revision,
            )
        except StoreValidationError as exc:
            raise OnboardingValidationError(str(exc)) from exc
        return _discovery_view(
            result.record, idempotent_replay=result.idempotent_replay
        )


def _empty_payload(interview_id: str) -> dict[str, Any]:
    return {
        "schema_version": LEDGER_SCHEMA_VERSION,
        "interview_id": interview_id,
        "status": "in_progress",
        "answers": {},
        "answered_question_ids": [],
        "next_question_id": QUESTION_IDS[0],
        "minimum_useful_setup_complete": False,
    }


def _empty_discovery_payload(interview_id: str) -> dict[str, Any]:
    return {
        "schema_version": DISCOVERY_SCHEMA_VERSION,
        "interview_id": interview_id,
        "status": "choice_pending",
        "mode": None,
        "answers": {},
        "topic_states": {topic_id: "unanswered" for topic_id in DISCOVERY_TOPIC_IDS},
        "current_topic_id": None,
        "brief_drip_enabled": False,
        "brief_topic_days_used": 0,
        "last_brief_local_date": None,
    }


def _normalize_answer(question_id: str, answer: Any) -> Any:
    if question_id == "timezone":
        return _normalize_timezone(answer)
    if question_id == "life_pattern":
        return {"text": _normalize_text(answer, field="life_pattern", max_length=4000)}
    if question_id == "goals":
        return {"text": _normalize_text(answer, field="goals", max_length=6000)}
    if question_id == "appointment_help":
        return _normalize_appointment_preference(answer)
    raise OnboardingValidationError(f"unknown onboarding question: {question_id}")


def _normalize_timezone(answer: Any) -> dict[str, str]:
    value = _normalize_text(answer, field="timezone", max_length=128)
    try:
        ZoneInfo(value)
    except (ZoneInfoNotFoundError, ValueError) as exc:
        raise OnboardingValidationError(
            "timezone must be a valid IANA timezone such as America/New_York"
        ) from exc
    return {"iana_timezone": value}


def _normalize_text(answer: Any, *, field: str, max_length: int) -> str:
    if not isinstance(answer, str):
        raise OnboardingValidationError(f"{field} must be text")
    value = answer.strip()
    if not value:
        raise OnboardingValidationError(f"{field} must not be blank")
    if len(value) > max_length:
        raise OnboardingValidationError(
            f"{field} must be at most {max_length} characters"
        )
    return value


def _normalize_appointment_preference(answer: Any) -> dict[str, Any]:
    if not isinstance(answer, Mapping):
        raise OnboardingValidationError(
            "appointment_help must be a mapping with wants_help and calendar_lane"
        )
    wants_help = answer.get("wants_help")
    if not isinstance(wants_help, bool):
        raise OnboardingValidationError("appointment_help.wants_help must be boolean")

    raw_lane = answer.get("calendar_lane")
    if not wants_help:
        if raw_lane not in (None, "", "none"):
            raise OnboardingValidationError(
                "calendar_lane must be empty when appointment help is declined"
            )
        lane: str | None = None
    else:
        if not isinstance(raw_lane, str) or not raw_lane.strip():
            raise OnboardingValidationError(
                "calendar_lane is required when appointment help is requested"
            )
        lane = _CALENDAR_LANE_ALIASES.get(raw_lane.strip().lower())
        if lane is None:
            raise OnboardingValidationError(
                "calendar_lane must be google, microsoft/outlook/m365, apple/icloud, other, or manual"
            )

    return {
        "wants_help": wants_help,
        "calendar_lane_requested": lane,
        "calendar_capability_verified": False,
        "calendar_projection_active": False,
        "appointment_service_activated": False,
    }


def _discovery_answer(accepted: bool, details: str | None) -> dict[str, Any]:
    result: dict[str, Any] = {"accepted": accepted}
    if details is not None:
        result["details"] = _normalize_text(
            details, field="discovery details", max_length=6000
        )
    return result


def _refresh_payload_state(payload: dict[str, Any]) -> None:
    answers = payload["answers"]
    answered = [question_id for question_id in QUESTION_IDS if question_id in answers]
    next_question_id = next(
        (question_id for question_id in QUESTION_IDS if question_id not in answers),
        None,
    )
    complete = next_question_id is None
    payload["answered_question_ids"] = answered
    payload["next_question_id"] = next_question_id
    payload["minimum_useful_setup_complete"] = complete
    payload["status"] = "complete" if complete else "in_progress"


def _refresh_discovery_state(payload: dict[str, Any]) -> None:
    states = payload["topic_states"]
    if all(states[topic_id] in _FINAL_TOPIC_STATES for topic_id in DISCOVERY_TOPIC_IDS):
        payload["status"] = "complete"
        payload["brief_drip_enabled"] = False
        payload["current_topic_id"] = None
        return
    if (
        payload.get("mode") == "brief_drip"
        and int(payload.get("brief_topic_days_used", 0)) >= DISCOVERY_BRIEF_TOPIC_LIMIT
    ):
        payload["status"] = "paused"
        payload["brief_drip_enabled"] = False
        return
    payload["status"] = "active" if payload.get("mode") is not None else "choice_pending"


def _first_pending_topic(payload: Mapping[str, Any]) -> str | None:
    states = payload.get("topic_states")
    if not isinstance(states, Mapping):
        raise OnboardingValidationError("stored discovery topic states are malformed")
    for topic_id in DISCOVERY_TOPIC_IDS:
        if states.get(topic_id) == "unanswered":
            return topic_id
    return None


def _view(record: ResourceRecord, *, idempotent_replay: bool = False) -> InterviewLedgerView:
    payload = record.payload
    if payload.get("schema_version") != LEDGER_SCHEMA_VERSION:
        raise OnboardingValidationError("unsupported Interview Ledger schema version")
    if payload.get("interview_id") != record.resource_id:
        raise OnboardingValidationError("Interview Ledger identity/readback mismatch")
    answers = payload.get("answers")
    if not isinstance(answers, dict):
        raise OnboardingValidationError("stored Interview Ledger answers are malformed")
    next_question_id = payload.get("next_question_id")
    if next_question_id is None:
        next_question = None
    else:
        next_question = _QUESTION_BY_ID.get(next_question_id)
        if next_question is None:
            raise OnboardingValidationError("stored next_question_id is unknown")
    status = payload.get("status")
    if status not in {"in_progress", "complete"}:
        raise OnboardingValidationError("stored Interview Ledger status is invalid")
    if status == "complete" and next_question is not None:
        raise OnboardingValidationError("completed Interview Ledger still has a next question")
    return InterviewLedgerView(
        interview_id=record.resource_id,
        revision=record.revision,
        status=status,
        answers=deepcopy(answers),
        next_question=next_question,
        completion_orientation=COMPLETION_ORIENTATION if status == "complete" else None,
        idempotent_replay=idempotent_replay,
    )


def _discovery_view(
    record: ResourceRecord,
    *,
    brief_topic_emitted: bool = False,
    idempotent_replay: bool = False,
) -> DiscoveryLedgerView:
    payload = record.payload
    if payload.get("schema_version") != DISCOVERY_SCHEMA_VERSION:
        raise OnboardingValidationError("unsupported discovery ledger schema version")
    if payload.get("interview_id") != record.resource_id:
        raise OnboardingValidationError("discovery ledger identity/readback mismatch")
    status = payload.get("status")
    if status not in {"choice_pending", "active", "paused", "complete"}:
        raise OnboardingValidationError("stored discovery status is invalid")
    mode = payload.get("mode")
    if mode not in {None, "continue_now", "brief_drip"}:
        raise OnboardingValidationError("stored discovery mode is invalid")
    answers = payload.get("answers")
    states = payload.get("topic_states")
    if not isinstance(answers, dict) or not isinstance(states, dict):
        raise OnboardingValidationError("stored discovery state is malformed")
    if set(states) != set(DISCOVERY_TOPIC_IDS):
        raise OnboardingValidationError("stored discovery topic set is incompatible")
    for topic_id, topic_state in states.items():
        if topic_state not in {"unanswered", "needs_details", *tuple(_FINAL_TOPIC_STATES)}:
            raise OnboardingValidationError(
                f"stored discovery topic state is invalid: {topic_id}={topic_state}"
            )
    current_topic_id = payload.get("current_topic_id")
    if current_topic_id is not None and current_topic_id not in _DISCOVERY_BY_ID:
        raise OnboardingValidationError("stored current discovery topic is unknown")
    next_topic_id = current_topic_id or _first_pending_topic(payload)
    next_topic = None if next_topic_id is None else _DISCOVERY_BY_ID[next_topic_id]
    followup_prompt = None
    if current_topic_id is not None and states[current_topic_id] == "needs_details":
        followup_prompt = _DISCOVERY_BY_ID[current_topic_id].followup_prompt
    days_used = payload.get("brief_topic_days_used")
    if not isinstance(days_used, int) or isinstance(days_used, bool) or days_used < 0:
        raise OnboardingValidationError("stored brief_topic_days_used is invalid")
    last_date = payload.get("last_brief_local_date")
    if last_date is not None:
        _local_date(last_date)
    remaining = tuple(
        topic_id
        for topic_id in DISCOVERY_TOPIC_IDS
        if states[topic_id] not in _FINAL_TOPIC_STATES
    )
    return DiscoveryLedgerView(
        interview_id=record.resource_id,
        revision=record.revision,
        status=status,
        mode=mode,
        answers=deepcopy(answers),
        topic_states=deepcopy(states),
        next_topic=next_topic,
        followup_prompt=followup_prompt,
        brief_drip_enabled=payload.get("brief_drip_enabled") is True,
        brief_topic_days_used=days_used,
        last_brief_local_date=last_date,
        remaining_topic_ids=remaining,
        brief_topic_emitted=brief_topic_emitted,
        idempotent_replay=idempotent_replay,
    )


def _idempotency_key(value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise OnboardingValidationError("idempotency_key must be a non-empty string")
    return value.strip()


def _local_date(value: str) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise OnboardingValidationError("local_date must be YYYY-MM-DD")
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise OnboardingValidationError("local_date must be YYYY-MM-DD") from exc
    return parsed.isoformat()


__all__ = [
    "AnswerConflictError",
    "COMPLETION_ORIENTATION",
    "DISCOVERY_BRIEF_TOPIC_LIMIT",
    "DISCOVERY_ID",
    "DISCOVERY_TOPIC_IDS",
    "DISCOVERY_TOPICS",
    "DiscoveryLedgerView",
    "DiscoveryTopic",
    "INTERVIEW_ID",
    "InterviewLedgerService",
    "InterviewLedgerView",
    "LEDGER_RESOURCE_TYPE",
    "OnboardingError",
    "OnboardingQuestion",
    "OnboardingValidationError",
    "ProgressiveDiscoveryService",
    "QUESTION_IDS",
    "QUESTIONS",
    "QuestionOrderError",
]
