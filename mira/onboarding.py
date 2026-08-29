"""Provider-neutral Minimum Useful Setup for Personal MIRA.

The first useful no-app MIRA needs a deterministic front door, not merely a
working storage substrate. This module implements the four-question ONBOARD-003
contract over STORE-001-compatible structured state. It contains no Google row
coordinates, provider resource IDs, Android assumptions, or silent service
activation.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Mapping
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from .structured_state import (
    NotFoundError,
    ResourceRecord,
    StructuredStateAdapter,
    ValidationError as StoreValidationError,
)


INTERVIEW_ID = "minimum-useful-setup"
LEDGER_RESOURCE_TYPE = "onboarding_ledger"
LEDGER_SCHEMA_VERSION = 1


class OnboardingError(Exception):
    """Base class for Minimum Useful Setup failures."""


class OnboardingValidationError(OnboardingError):
    """Raised when an onboarding answer is malformed or unsafe to persist."""


class QuestionOrderError(OnboardingError):
    """Raised when an unanswered question is submitted out of canonical order."""


class AnswerConflictError(OnboardingError):
    """Raised when a prior answer would be changed without explicit replacement."""


@dataclass(frozen=True)
class OnboardingQuestion:
    question_id: str
    prompt: str


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

COMPLETION_ORIENTATION = (
    "Minimum Useful Setup is complete. You can ask MIRA at any time to continue "
    "the interview with additional questions that improve how MIRA functions for "
    "you. MIRA Studio is the guided place for adding or refining bounded "
    "preferences and workflows, and sharing is optional. Nothing is silently "
    "enabled or shared merely because setup is complete."
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
        if not isinstance(idempotency_key, str) or not idempotency_key.strip():
            raise OnboardingValidationError("idempotency_key must be a non-empty string")

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

    def get(
        self, *, interview_id: str = INTERVIEW_ID
    ) -> InterviewLedgerView:
        try:
            return _view(self._adapter.get(self._resource_type, interview_id))
        except NotFoundError as exc:
            raise OnboardingValidationError("Interview Ledger has not been started") from exc


def _empty_payload(interview_id: str) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "schema_version": LEDGER_SCHEMA_VERSION,
        "interview_id": interview_id,
        "status": "in_progress",
        "answers": {},
        "answered_question_ids": [],
        "next_question_id": QUESTION_IDS[0],
        "minimum_useful_setup_complete": False,
    }
    return payload


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
        alias = raw_lane.strip().lower()
        lane = _CALENDAR_LANE_ALIASES.get(alias)
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


def _view(
    record: ResourceRecord, *, idempotent_replay: bool = False
) -> InterviewLedgerView:
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


__all__ = [
    "AnswerConflictError",
    "COMPLETION_ORIENTATION",
    "INTERVIEW_ID",
    "InterviewLedgerService",
    "InterviewLedgerView",
    "LEDGER_RESOURCE_TYPE",
    "OnboardingError",
    "OnboardingQuestion",
    "OnboardingValidationError",
    "QUESTION_IDS",
    "QUESTIONS",
    "QuestionOrderError",
]
