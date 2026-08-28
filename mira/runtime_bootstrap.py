"""Fail-closed runtime bootstrap for persisted canonical Authority routing.

The bootstrap is intentionally provider-neutral. It reconciles one desired
AuthoritySpec and one data-class binding against an AuthorityRegistry without
overwriting unexpected persisted routing metadata.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib

from .authority import (
    AuthorityBinding,
    AuthorityBindingNotFoundError,
    AuthorityNotFoundError,
    AuthorityRegistry,
    AuthorityRegistryError,
    AuthorityRoute,
    AuthoritySpec,
    StoredAuthority,
)
from .structured_state import StructuredStateAdapter


_MAX_IDEMPOTENCY_KEY_LENGTH = 128


class RuntimeBootstrapError(AuthorityRegistryError):
    """Base class for runtime bootstrap failures."""


class RuntimeBootstrapMismatchError(RuntimeBootstrapError):
    """Raised when persisted routing metadata differs from desired startup state."""


@dataclass(frozen=True)
class RuntimeBootstrapResult:
    """Verified bootstrap outcome and whether persistent records were created."""

    route: AuthorityRoute
    authority_created: bool
    binding_created: bool


def bootstrap_runtime_authority(
    registry: AuthorityRegistry,
    *,
    spec: AuthoritySpec,
    data_class: str,
    adapter: StructuredStateAdapter,
) -> RuntimeBootstrapResult:
    """Ensure one persisted route exists, then mount and resolve its runtime adapter.

    Existing metadata is inspected before any persistent write. A materially
    different Authority or binding is a startup error, not an invitation to
    rewrite canonical routing. Missing records are created with deterministic
    idempotency keys and revision-zero preconditions.
    """

    existing_authority = _get_authority_if_present(registry, spec.authority_id)
    existing_binding = _get_binding_if_present(registry, data_class)

    if existing_authority is not None and existing_authority.spec != spec:
        raise RuntimeBootstrapMismatchError(
            f"persisted authority metadata differs for {spec.authority_id}"
        )
    if existing_binding is not None and existing_binding.authority_id != spec.authority_id:
        raise RuntimeBootstrapMismatchError(
            f"persisted binding for {data_class} points to "
            f"{existing_binding.authority_id}, expected {spec.authority_id}"
        )

    authority_created = existing_authority is None
    binding_created = existing_binding is None

    if existing_authority is None:
        existing_authority = registry.register_authority(
            spec,
            idempotency_key=_bootstrap_idempotency_key("authority", spec.authority_id),
            expected_revision=0,
        )

    if existing_binding is None:
        existing_binding = registry.activate(
            data_class,
            spec.authority_id,
            idempotency_key=_bootstrap_idempotency_key("binding", data_class),
            expected_revision=0,
        )

    registry.register_runtime_adapter(spec.adapter_key, adapter)
    route = registry.resolve(data_class)
    return RuntimeBootstrapResult(
        route=route,
        authority_created=authority_created,
        binding_created=binding_created,
    )


def _get_authority_if_present(
    registry: AuthorityRegistry, authority_id: str
) -> StoredAuthority | None:
    try:
        return registry.get_authority(authority_id)
    except AuthorityNotFoundError:
        return None


def _get_binding_if_present(
    registry: AuthorityRegistry, data_class: str
) -> AuthorityBinding | None:
    try:
        return registry.get_binding(data_class)
    except AuthorityBindingNotFoundError:
        return None


def _bootstrap_idempotency_key(kind: str, identity: str) -> str:
    candidate = f"bootstrap-{kind}-{identity}"
    if len(candidate) <= _MAX_IDEMPOTENCY_KEY_LENGTH:
        return candidate
    digest = hashlib.sha256(identity.encode("utf-8")).hexdigest()
    return f"bootstrap-{kind}-sha256-{digest}"
