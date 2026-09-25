"""Executable Personal MIRA orchestration over canonical service state.

MIRA-SKILL-001 is the product glue above service composition. It must not treat
implemented code, green CI, provider authorization, or user intent as equivalent
to an executable service.

This module deliberately starts with one real customer path: the Personal Ops
Brief. The briefs service must be explicitly requested, dependency-ready, and
explicitly activated before orchestration calls the canonical OpsBriefService.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable

from .ops_brief import OpsBriefService, OpsBriefView
from .service_composition import (
    DependencyEvidence,
    ServiceComposer,
    ServiceCompositionValidationError,
    personal_service_bundle,
)
from .service_state import (
    ServiceStateService,
    ServiceStateValidationError,
    ServiceStateView,
)
from .structured_state import StructuredStateAdapter


class MiraOrchestrationError(Exception):
    """Base error for Personal MIRA orchestration."""


class MiraServiceNotExecutableError(MiraOrchestrationError):
    """Raised when a requested service is not currently executable."""

    def __init__(self, status: "ServiceExecutionStatus") -> None:
        self.status = status
        detail = ", ".join(status.blockers) or "service is not executable"
        super().__init__(f"{status.service_id} is not executable: {detail}")


@dataclass(frozen=True)
class ServiceExecutionStatus:
    """One truthful user-facing service execution decision."""

    service_id: str
    activation_state: str
    capability_state: str
    ready: bool
    effective_active: bool
    blockers: tuple[str, ...]


class PersonalMiraOrchestrator:
    """Execute supported Personal MIRA behaviors through canonical service gates."""

    def __init__(
        self,
        adapter: StructuredStateAdapter,
        *,
        ops_brief_service: OpsBriefService | None = None,
    ) -> None:
        self._state = ServiceStateService(adapter)
        self._composer = ServiceComposer(self._state)
        self._ops_brief = ops_brief_service or OpsBriefService(adapter)

    def request_service(
        self,
        service_id: str,
        *,
        idempotency_key: str,
    ) -> ServiceExecutionStatus:
        """Persist explicit user intent without claiming the service is active."""

        spec = personal_service_bundle(service_id)
        state = self._state.request_enable(
            spec.service_id,
            idempotency_key=idempotency_key,
        )
        return _status_from_state(state)

    def refresh_service_readiness(
        self,
        service_id: str,
        *,
        capability_available: bool,
        dependency_evidence: Iterable[DependencyEvidence],
        idempotency_key: str,
    ) -> ServiceExecutionStatus:
        """Project verified capability/dependency evidence into service readiness."""

        spec = personal_service_bundle(service_id)
        composed = self._composer.compose(
            spec,
            capability_available=capability_available,
            dependency_evidence=dependency_evidence,
            idempotency_key=idempotency_key,
        )
        blockers = list(composed.blockers)
        if composed.activation_state != "active":
            blockers.append(f"activation:{composed.activation_state}")
        return ServiceExecutionStatus(
            service_id=composed.service_id,
            activation_state=composed.activation_state,
            capability_state=composed.capability_state,
            ready=composed.ready,
            effective_active=composed.effective_active,
            blockers=tuple(blockers),
        )

    def activate_service(
        self,
        service_id: str,
        *,
        idempotency_key: str,
    ) -> ServiceExecutionStatus:
        """Explicitly activate a requested service only after readiness is true."""

        spec = personal_service_bundle(service_id)
        state = self._state.activate(
            spec.service_id,
            idempotency_key=idempotency_key,
        )
        return _status_from_state(state)

    def service_status(self, service_id: str) -> ServiceExecutionStatus:
        """Read current persisted service truth without mutating it."""

        spec = personal_service_bundle(service_id)
        try:
            state = self._state.get(spec.service_id)
        except ServiceStateValidationError as exc:
            raise MiraOrchestrationError(
                f"canonical service state is unavailable for {spec.service_id}"
            ) from exc
        return _status_from_state(state)

    def run_ops_brief(
        self,
        local_date: str,
        slot: str,
        *,
        timezone_name: str,
        context: str | None = None,
    ) -> OpsBriefView:
        """Execute one explicit canonical Ops Brief slot when briefs is active."""

        self._require_executable("briefs")
        return self._ops_brief.compose_slot(
            local_date,
            slot,
            timezone_name=timezone_name,
            context=context,
        )

    def run_due_ops_brief(
        self,
        instant: datetime,
        *,
        timezone_name: str,
        context: str | None = None,
    ) -> OpsBriefView:
        """Execute the canonical due-slot path when briefs is active."""

        self._require_executable("briefs")
        return self._ops_brief.compose_due(
            instant,
            timezone_name=timezone_name,
            context=context,
        )

    def _require_executable(self, service_id: str) -> ServiceExecutionStatus:
        try:
            status = self.service_status(service_id)
        except MiraOrchestrationError as exc:
            missing = ServiceExecutionStatus(
                service_id=service_id,
                activation_state="missing",
                capability_state="unknown",
                ready=False,
                effective_active=False,
                blockers=("service_state:unavailable",),
            )
            raise MiraServiceNotExecutableError(missing) from exc
        if not status.effective_active:
            raise MiraServiceNotExecutableError(status)
        return status


def _status_from_state(state: ServiceStateView) -> ServiceExecutionStatus:
    blockers = list(state.dependency_blockers)
    if state.capability_state != "available":
        blockers.insert(0, f"capability:{state.capability_state}")
    if state.activation_state != "active":
        blockers.append(f"activation:{state.activation_state}")
    return ServiceExecutionStatus(
        service_id=state.service_id,
        activation_state=state.activation_state,
        capability_state=state.capability_state,
        ready=state.ready,
        effective_active=state.effective_active,
        blockers=tuple(blockers),
    )


__all__ = [
    "MiraOrchestrationError",
    "MiraServiceNotExecutableError",
    "PersonalMiraOrchestrator",
    "ServiceExecutionStatus",
]
