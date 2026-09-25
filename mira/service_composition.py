"""Dependency-derived service composition for MIRA Personal services.

SERVICE-001 owns explicit user intent and activation truth. SERVICE-002 requires
service bundles to derive readiness from verified dependencies without silently
turning capability, recommendation, or successful tests into activation.

This module is intentionally provider-neutral. Callers supply bounded dependency
evidence produced by the appropriate runtime/provider gates. The composer only
projects that evidence into the existing ServiceStateService and returns one
truthful execution view.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .service_state import ServiceStateService, ServiceStateView


class ServiceCompositionError(Exception):
    """Base error for service composition."""


class ServiceCompositionValidationError(ServiceCompositionError):
    """Raised when a service bundle or dependency evidence is malformed."""


def _token(value: object, field: str) -> str:
    if (
        not isinstance(value, str)
        or not value.strip()
        or value != value.strip()
        or len(value) > 128
    ):
        raise ServiceCompositionValidationError(
            f"{field} must be non-empty trimmed text up to 128 characters"
        )
    return value


@dataclass(frozen=True)
class DependencyEvidence:
    """One dependency decision at the service-composition boundary.

    ready=True means the dependency was already verified by its owning boundary.
    ready=False requires a concrete reason code. Missing evidence is represented
    by omitting the dependency; composition then fails closed as unknown.
    """

    dependency_id: str
    ready: bool
    reason_code: str | None = None

    def __post_init__(self) -> None:
        _token(self.dependency_id, "dependency_id")
        if not isinstance(self.ready, bool):
            raise ServiceCompositionValidationError("ready must be boolean")
        if self.ready:
            if self.reason_code is not None:
                raise ServiceCompositionValidationError(
                    "ready dependency evidence must not carry a failure reason"
                )
        else:
            _token(self.reason_code, "reason_code")


@dataclass(frozen=True)
class ServiceBundleSpec:
    """Canonical dependency contract for one activatable service bundle."""

    service_id: str
    dependency_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _token(self.service_id, "service_id")
        if not isinstance(self.dependency_ids, tuple):
            raise ServiceCompositionValidationError(
                "dependency_ids must be a sorted unique tuple"
            )
        normalized = tuple(
            sorted({_token(value, "dependency_id") for value in self.dependency_ids})
        )
        if normalized != self.dependency_ids:
            raise ServiceCompositionValidationError(
                "dependency_ids must be a sorted unique tuple"
            )


PERSONAL_SERVICE_BUNDLES = (
    ServiceBundleSpec(
        service_id="briefs",
        dependency_ids=(
            "OPS-001",
            "OPS-003",
            "OPS-004",
            "RECOVERY-001",
            "RECOVERY-002",
        ),
    ),
)
_PERSONAL_SERVICE_BUNDLE_MAP = {
    bundle.service_id: bundle for bundle in PERSONAL_SERVICE_BUNDLES
}


def personal_service_bundle(service_id: str) -> ServiceBundleSpec:
    """Return one canonical Personal service bundle contract."""

    normalized = _token(service_id, "service_id")
    try:
        return _PERSONAL_SERVICE_BUNDLE_MAP[normalized]
    except KeyError as exc:
        raise ServiceCompositionValidationError(
            f"unknown Personal service bundle: {normalized}"
        ) from exc


@dataclass(frozen=True)
class ServiceCompositionView:
    """Read-only composed truth returned to orchestration/client layers."""

    service_id: str
    revision: int
    activation_state: str
    capability_state: str
    ready: bool
    effective_active: bool
    blockers: tuple[str, ...]
    dependency_ids: tuple[str, ...]
    idempotent_replay: bool


class ServiceComposer:
    """Project verified dependency evidence into SERVICE-001 state.

    Composition never calls activate. Explicit user intent plus a separate
    activation action remain mandatory even when every dependency is ready.
    """

    def __init__(self, service_state: ServiceStateService) -> None:
        if not isinstance(service_state, ServiceStateService):
            raise ServiceCompositionValidationError(
                "service_state must be a ServiceStateService"
            )
        self._service_state = service_state

    def compose(
        self,
        spec: ServiceBundleSpec,
        *,
        capability_available: bool,
        dependency_evidence: Iterable[DependencyEvidence] = (),
        idempotency_key: str,
    ) -> ServiceCompositionView:
        if not isinstance(spec, ServiceBundleSpec):
            raise ServiceCompositionValidationError(
                "spec must be a ServiceBundleSpec"
            )
        if not isinstance(capability_available, bool):
            raise ServiceCompositionValidationError(
                "capability_available must be boolean"
            )
        key = _token(idempotency_key, "idempotency_key")
        evidence = _evidence_map(dependency_evidence)

        declared = set(spec.dependency_ids)
        extra = tuple(sorted(set(evidence).difference(declared)))
        if extra:
            raise ServiceCompositionValidationError(
                "dependency evidence was supplied for undeclared dependencies: "
                + ", ".join(extra)
            )

        blockers: list[str] = []
        for dependency_id in spec.dependency_ids:
            observation = evidence.get(dependency_id)
            if observation is None:
                blockers.append(f"dependency:{dependency_id}:unknown")
            elif not observation.ready:
                blockers.append(
                    f"dependency:{dependency_id}:{observation.reason_code}"
                )

        state = self._service_state.set_readiness(
            spec.service_id,
            capability_state="available" if capability_available else "unavailable",
            dependency_blockers=tuple(blockers),
            idempotency_key=key,
        )
        return _composition_view(spec, state)

    def current(self, spec: ServiceBundleSpec) -> ServiceCompositionView:
        """Return current persisted service truth without changing readiness."""

        if not isinstance(spec, ServiceBundleSpec):
            raise ServiceCompositionValidationError(
                "spec must be a ServiceBundleSpec"
            )
        state = self._service_state.get(spec.service_id)
        return _composition_view(spec, state)


def _composition_view(
    spec: ServiceBundleSpec,
    state: ServiceStateView,
) -> ServiceCompositionView:
    blockers = list(state.dependency_blockers)
    if state.capability_state != "available":
        blockers.insert(0, f"capability:{state.capability_state}")
    return ServiceCompositionView(
        service_id=state.service_id,
        revision=state.revision,
        activation_state=state.activation_state,
        capability_state=state.capability_state,
        ready=state.ready,
        effective_active=state.effective_active,
        blockers=tuple(blockers),
        dependency_ids=spec.dependency_ids,
        idempotent_replay=state.idempotent_replay,
    )


def _evidence_map(
    values: Iterable[DependencyEvidence],
) -> dict[str, DependencyEvidence]:
    if isinstance(values, (str, bytes)):
        raise ServiceCompositionValidationError(
            "dependency_evidence must be an iterable of DependencyEvidence values"
        )
    try:
        material = tuple(values)
    except TypeError as exc:
        raise ServiceCompositionValidationError(
            "dependency_evidence must be iterable"
        ) from exc

    result: dict[str, DependencyEvidence] = {}
    for item in material:
        if not isinstance(item, DependencyEvidence):
            raise ServiceCompositionValidationError(
                "dependency_evidence must contain DependencyEvidence values"
            )
        if item.dependency_id in result:
            raise ServiceCompositionValidationError(
                f"duplicate dependency evidence: {item.dependency_id}"
            )
        result[item.dependency_id] = item
    return result


__all__ = [
    "DependencyEvidence",
    "PERSONAL_SERVICE_BUNDLES",
    "ServiceBundleSpec",
    "ServiceComposer",
    "ServiceCompositionError",
    "ServiceCompositionValidationError",
    "ServiceCompositionView",
    "personal_service_bundle",
]
