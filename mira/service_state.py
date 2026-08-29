"""Explicit provider-neutral MIRA service state.

SERVICE-001 requires user intent, recommendation, capability/readiness, and
actual activation to remain separate truths. This module provides the smallest
finite state machine needed after first boot without pulling in full service
composition or provider-specific behavior.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Callable, Iterable

from .structured_state import NotFoundError, ResourceRecord, StructuredStateAdapter


RESOURCE_TYPE = "service_state"
SCHEMA_VERSION = 1

ACTIVATION_STATES = frozenset({"disabled", "requested", "active", "suspended"})
CAPABILITY_STATES = frozenset({"unknown", "unavailable", "available"})
RECOMMENDATION_STATES = frozenset({"none", "suggested"})


class ServiceStateError(Exception):
    """Base error for explicit service-state behavior."""


class ServiceStateValidationError(ServiceStateError):
    """Raised when service state or transition input is malformed."""


class ServiceNotReadyError(ServiceStateError):
    """Raised when activation is attempted without verified readiness."""


class ServiceIntentRequiredError(ServiceStateError):
    """Raised when activation is attempted without explicit user intent."""


@dataclass(frozen=True)
class ServiceStateView:
    service_id: str
    revision: int
    activation_state: str
    capability_state: str
    recommendation_state: str
    dependency_blockers: tuple[str, ...]
    suspension_reason: str | None
    idempotent_replay: bool = False

    @property
    def requested_by_user(self) -> bool:
        return self.activation_state in {"requested", "active", "suspended"}

    @property
    def ready(self) -> bool:
        return self.capability_state == "available" and not self.dependency_blockers

    @property
    def effective_active(self) -> bool:
        return self.activation_state == "active" and self.ready


class ServiceStateService:
    """Persist explicit service state through STORE-001-compatible semantics."""

    def __init__(self, adapter: StructuredStateAdapter) -> None:
        self._adapter = adapter

    def ensure(self, service_id: str) -> ServiceStateView:
        service_id = _token(service_id, "service_id")
        try:
            return _view(self._adapter.get(RESOURCE_TYPE, service_id))
        except NotFoundError:
            result = self._adapter.upsert(
                RESOURCE_TYPE,
                service_id,
                _empty_payload(service_id),
                idempotency_key=f"service-state-start:{service_id}",
                expected_revision=0,
            )
            return _view(result.record, idempotent_replay=result.idempotent_replay)

    def get(self, service_id: str) -> ServiceStateView:
        service_id = _token(service_id, "service_id")
        try:
            return _view(self._adapter.get(RESOURCE_TYPE, service_id))
        except NotFoundError as exc:
            raise ServiceStateValidationError(f"unknown service state: {service_id}") from exc

    def request_enable(self, service_id: str, *, idempotency_key: str) -> ServiceStateView:
        def change(payload: dict[str, Any]) -> None:
            if payload["activation_state"] == "active":
                return
            payload["activation_state"] = "requested"
            payload["suspension_reason"] = None

        return self._mutate(service_id, idempotency_key, change)

    def recommend(self, service_id: str, *, idempotency_key: str) -> ServiceStateView:
        def change(payload: dict[str, Any]) -> None:
            payload["recommendation_state"] = "suggested"

        return self._mutate(service_id, idempotency_key, change)

    def clear_recommendation(
        self, service_id: str, *, idempotency_key: str
    ) -> ServiceStateView:
        def change(payload: dict[str, Any]) -> None:
            payload["recommendation_state"] = "none"

        return self._mutate(service_id, idempotency_key, change)

    def set_readiness(
        self,
        service_id: str,
        *,
        capability_state: str,
        dependency_blockers: Iterable[str] = (),
        idempotency_key: str,
    ) -> ServiceStateView:
        capability = _enum(capability_state, CAPABILITY_STATES, "capability_state")
        blockers = _blockers(dependency_blockers)

        def change(payload: dict[str, Any]) -> None:
            payload["capability_state"] = capability
            payload["dependency_blockers"] = list(blockers)
            ready = capability == "available" and not blockers
            if payload["activation_state"] == "active" and not ready:
                payload["activation_state"] = "suspended"
                payload["suspension_reason"] = "readiness_lost"

        return self._mutate(service_id, idempotency_key, change)

    def activate(self, service_id: str, *, idempotency_key: str) -> ServiceStateView:
        current = self.ensure(service_id)
        if current.activation_state not in {"requested", "suspended"}:
            raise ServiceIntentRequiredError(
                "service activation requires explicit user request before activation"
            )
        if not current.ready:
            reasons = list(current.dependency_blockers)
            if current.capability_state != "available":
                reasons.insert(0, f"capability:{current.capability_state}")
            detail = ", ".join(reasons) or "readiness unknown"
            raise ServiceNotReadyError(f"service is not ready: {detail}")

        def change(payload: dict[str, Any]) -> None:
            payload["activation_state"] = "active"
            payload["suspension_reason"] = None

        return self._mutate_existing(service_id, idempotency_key, change)

    def disable(self, service_id: str, *, idempotency_key: str) -> ServiceStateView:
        def change(payload: dict[str, Any]) -> None:
            payload["activation_state"] = "disabled"
            payload["suspension_reason"] = None

        return self._mutate(service_id, idempotency_key, change)

    def apply_appointment_onboarding_intent(
        self,
        *,
        wants_help: bool,
        idempotency_key: str,
        service_id: str = "appointments_calendar",
    ) -> ServiceStateView:
        if not isinstance(wants_help, bool):
            raise ServiceStateValidationError("wants_help must be boolean")
        if wants_help:
            return self.request_enable(service_id, idempotency_key=idempotency_key)
        return self.disable(service_id, idempotency_key=idempotency_key)

    def _mutate(
        self,
        service_id: str,
        idempotency_key: str,
        change: Callable[[dict[str, Any]], None],
    ) -> ServiceStateView:
        self.ensure(service_id)
        return self._mutate_existing(service_id, idempotency_key, change)

    def _mutate_existing(
        self,
        service_id: str,
        idempotency_key: str,
        change: Callable[[dict[str, Any]], None],
    ) -> ServiceStateView:
        service_id = _token(service_id, "service_id")
        key = _token(idempotency_key, "idempotency_key")
        record = self._adapter.get(RESOURCE_TYPE, service_id)
        payload = deepcopy(record.payload)
        _validate_payload(payload, expected_service_id=service_id)
        before = deepcopy(payload)
        change(payload)
        _validate_payload(payload, expected_service_id=service_id)
        if payload == before:
            return _view(record, idempotent_replay=True)
        result = self._adapter.upsert(
            RESOURCE_TYPE,
            service_id,
            payload,
            idempotency_key=key,
            expected_revision=record.revision,
        )
        return _view(result.record, idempotent_replay=result.idempotent_replay)


def _empty_payload(service_id: str) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "service_id": service_id,
        "activation_state": "disabled",
        "capability_state": "unknown",
        "recommendation_state": "none",
        "dependency_blockers": [],
        "suspension_reason": None,
    }


def _view(record: ResourceRecord, *, idempotent_replay: bool = False) -> ServiceStateView:
    payload = deepcopy(record.payload)
    _validate_payload(payload, expected_service_id=record.resource_id)
    return ServiceStateView(
        service_id=record.resource_id,
        revision=record.revision,
        activation_state=payload["activation_state"],
        capability_state=payload["capability_state"],
        recommendation_state=payload["recommendation_state"],
        dependency_blockers=tuple(payload["dependency_blockers"]),
        suspension_reason=payload["suspension_reason"],
        idempotent_replay=idempotent_replay,
    )


def _validate_payload(payload: dict[str, Any], *, expected_service_id: str) -> None:
    if not isinstance(payload, dict):
        raise ServiceStateValidationError("service-state payload must be an object")
    if payload.get("schema_version") != SCHEMA_VERSION:
        raise ServiceStateValidationError("unsupported service-state schema version")
    if payload.get("service_id") != expected_service_id:
        raise ServiceStateValidationError("service-state identity/readback mismatch")
    _enum(payload.get("activation_state"), ACTIVATION_STATES, "activation_state")
    _enum(payload.get("capability_state"), CAPABILITY_STATES, "capability_state")
    _enum(
        payload.get("recommendation_state"),
        RECOMMENDATION_STATES,
        "recommendation_state",
    )
    blockers = payload.get("dependency_blockers")
    normalized_blockers = _blockers(blockers if isinstance(blockers, list) else ())
    if list(normalized_blockers) != blockers:
        raise ServiceStateValidationError(
            "dependency_blockers must be a sorted unique list of non-empty tokens"
        )
    suspension_reason = payload.get("suspension_reason")
    if suspension_reason is not None:
        _token(suspension_reason, "suspension_reason")
    if payload["activation_state"] == "active":
        if payload["capability_state"] != "available" or blockers:
            raise ServiceStateValidationError(
                "persisted active service must have verified available capability and no blockers"
            )
    if payload["activation_state"] == "suspended" and suspension_reason is None:
        raise ServiceStateValidationError("suspended service requires suspension_reason")


def _blockers(values: Iterable[str]) -> tuple[str, ...]:
    if isinstance(values, (str, bytes)):
        raise ServiceStateValidationError("dependency_blockers must be a collection of tokens")
    try:
        normalized = tuple(sorted({_token(value, "dependency_blocker") for value in values}))
    except TypeError as exc:
        raise ServiceStateValidationError(
            "dependency_blockers must be an iterable of tokens"
        ) from exc
    return normalized


def _enum(value: Any, allowed: frozenset[str], field: str) -> str:
    token = _token(value, field)
    if token not in allowed:
        raise ServiceStateValidationError(
            f"{field} must be one of: {', '.join(sorted(allowed))}"
        )
    return token


def _token(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise ServiceStateValidationError(f"{field} must be a non-empty trimmed string")
    if len(value) > 128:
        raise ServiceStateValidationError(f"{field} must be at most 128 characters")
    return value


__all__ = [
    "ACTIVATION_STATES",
    "CAPABILITY_STATES",
    "RECOMMENDATION_STATES",
    "RESOURCE_TYPE",
    "ServiceIntentRequiredError",
    "ServiceNotReadyError",
    "ServiceStateError",
    "ServiceStateService",
    "ServiceStateValidationError",
    "ServiceStateView",
]
