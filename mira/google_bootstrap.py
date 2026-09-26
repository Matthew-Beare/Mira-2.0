"""Deterministic Personal Google bootstrap planning and verification.

GOOGLE-BOOTSTRAP-001 is deliberately secret-free and side-effect free here.  It
turns selected Workspace services into an explicit blueprint and verifies fresh
provider capability evidence without treating OAuth, declared scopes, or a
successful plan as proof that a service is usable.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping

from .service_state import (
    CapabilityEvaluation,
    CapabilityGate,
    ConnectionState,
    ProviderCapabilitySnapshot,
    evaluate_provider_capability,
)


class GoogleBootstrapError(ValueError):
    """Raised when a Google bootstrap blueprint or proof is malformed."""


@dataclass(frozen=True)
class GoogleServiceBlueprint:
    service_id: str
    required_gates: tuple[CapabilityGate, ...]
    data_classification: str


@dataclass(frozen=True)
class GoogleBootstrapPlan:
    provider_id: str
    services: tuple[GoogleServiceBlueprint, ...]


@dataclass(frozen=True)
class GoogleServiceVerification:
    service_id: str
    ready: bool
    connection_state: ConnectionState
    blockers: tuple[str, ...]
    resource_ref: str | None


@dataclass(frozen=True)
class GoogleBootstrapVerification:
    provider_id: str
    ready: bool
    services: tuple[GoogleServiceVerification, ...]


_SERVICE_BLUEPRINTS = {
    "calendar": GoogleServiceBlueprint(
        "calendar",
        (CapabilityGate.READ, CapabilityGate.WRITE, CapabilityGate.REMOTE_READBACK),
        "personal",
    ),
    "gmail": GoogleServiceBlueprint(
        "gmail",
        (CapabilityGate.READ,),
        "personal",
    ),
    "sheets": GoogleServiceBlueprint(
        "sheets",
        (CapabilityGate.READ, CapabilityGate.WRITE, CapabilityGate.REMOTE_READBACK),
        "personal",
    ),
}


def plan_personal_google_bootstrap(
    selected_services: Iterable[str],
) -> GoogleBootstrapPlan:
    """Return a canonical, deterministic plan for explicitly selected services."""

    if isinstance(selected_services, (str, bytes)):
        raise GoogleBootstrapError("selected_services must be a collection")
    try:
        selected = tuple(selected_services)
    except TypeError as exc:
        raise GoogleBootstrapError("selected_services must be iterable") from exc
    if not selected:
        raise GoogleBootstrapError("at least one Google service must be selected")
    if any(not isinstance(value, str) or value != value.strip() or not value for value in selected):
        raise GoogleBootstrapError("service ids must be non-empty trimmed text")
    unknown = sorted(set(selected) - set(_SERVICE_BLUEPRINTS))
    if unknown:
        raise GoogleBootstrapError("unsupported Google services: " + ", ".join(unknown))
    services = tuple(_SERVICE_BLUEPRINTS[name] for name in sorted(set(selected)))
    return GoogleBootstrapPlan(provider_id="google", services=services)


def verify_personal_google_bootstrap(
    plan: GoogleBootstrapPlan,
    snapshots: Mapping[str, ProviderCapabilitySnapshot],
    *,
    now: str,
    max_age_seconds: int,
) -> GoogleBootstrapVerification:
    """Verify every planned service independently and fail closed on missing proof."""

    if not isinstance(plan, GoogleBootstrapPlan) or plan.provider_id != "google":
        raise GoogleBootstrapError("plan must be a Personal Google bootstrap plan")
    if not isinstance(snapshots, Mapping):
        raise GoogleBootstrapError("snapshots must be a service-id mapping")

    results = []
    for service in plan.services:
        snapshot = snapshots.get(service.service_id)
        if snapshot is None:
            results.append(
                GoogleServiceVerification(
                    service_id=service.service_id,
                    ready=False,
                    connection_state=ConnectionState.NEEDS_ATTENTION,
                    blockers=("provider:evidence:missing",),
                    resource_ref=None,
                )
            )
            continue
        if not isinstance(snapshot, ProviderCapabilitySnapshot):
            raise GoogleBootstrapError(
                f"snapshot for {service.service_id} must be ProviderCapabilitySnapshot"
            )
        if snapshot.provider_id != "google" or snapshot.service_id != service.service_id:
            raise GoogleBootstrapError(
                f"snapshot identity mismatch for {service.service_id}"
            )
        evaluation: CapabilityEvaluation = evaluate_provider_capability(
            snapshot,
            required_gates=service.required_gates,
            now=now,
            max_age_seconds=max_age_seconds,
        )
        results.append(
            GoogleServiceVerification(
                service_id=service.service_id,
                ready=evaluation.ready,
                connection_state=evaluation.connection_state,
                blockers=evaluation.blockers,
                resource_ref=snapshot.resource_ref,
            )
        )

    services = tuple(results)
    return GoogleBootstrapVerification(
        provider_id="google",
        ready=bool(services) and all(service.ready for service in services),
        services=services,
    )


__all__ = [
    "GoogleBootstrapError",
    "GoogleBootstrapPlan",
    "GoogleBootstrapVerification",
    "GoogleServiceBlueprint",
    "GoogleServiceVerification",
    "plan_personal_google_bootstrap",
    "verify_personal_google_bootstrap",
]
