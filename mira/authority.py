"""Canonical Authority Registry built on the structured-state contract.

The registry persists authority metadata and one binding per mutable data class.
Runtime adapter objects are mounted explicitly and are never themselves authority.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
import re
from typing import Mapping

from .structured_state import (
    NotFoundError,
    StructuredStateAdapter,
)


_DATA_CLASS_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,95}$")
_REQUIRED_REGISTRY_RESOURCE_TYPES = frozenset({"authority", "authority_binding"})


class AuthorityRegistryError(Exception):
    """Base class for Authority Registry failures."""


class AuthorityNotFoundError(AuthorityRegistryError):
    """Raised when persisted Authority metadata does not exist."""


class AuthorityBindingNotFoundError(AuthorityRegistryError):
    """Raised when a data class has no canonical Authority binding."""


class AuthorityUnavailableError(AuthorityRegistryError):
    """Raised when a bound Authority cannot safely serve canonical state."""


class AuthoritySchemaError(AuthorityRegistryError):
    """Raised when registry or adapter schema metadata is incompatible."""


@dataclass(frozen=True)
class AuthoritySpec:
    """Persisted non-secret metadata describing one candidate Authority."""

    authority_id: str
    adapter_key: str
    resource_ref: str
    namespace: str
    failure_domain: str
    owner_id: str
    schema_version: str
    verified: bool
    enabled: bool = True


@dataclass(frozen=True)
class StoredAuthority:
    spec: AuthoritySpec
    revision: int


@dataclass(frozen=True)
class AuthorityBinding:
    data_class: str
    authority_id: str
    revision: int


@dataclass(frozen=True)
class AuthorityRoute:
    """Resolved canonical route: exact persisted metadata plus mounted adapter."""

    authority: StoredAuthority
    binding: AuthorityBinding
    adapter: StructuredStateAdapter


class AuthorityRegistry:
    """Persisted one-authority-per-data-class routing with explicit adapter mounts."""

    def __init__(self, registry_store: StructuredStateAdapter) -> None:
        schema = registry_store.schema()
        missing = _REQUIRED_REGISTRY_RESOURCE_TYPES.difference(schema.resource_types)
        if missing:
            raise AuthoritySchemaError(
                "registry store is missing required resource types: "
                + ", ".join(sorted(missing))
            )
        self._store = registry_store
        self._runtime_adapters: dict[str, StructuredStateAdapter] = {}

    def register_runtime_adapter(
        self, adapter_key: str, adapter: StructuredStateAdapter
    ) -> None:
        key = _validate_token(adapter_key, "adapter_key")
        self._runtime_adapters[key] = adapter

    def unregister_runtime_adapter(self, adapter_key: str) -> None:
        key = _validate_token(adapter_key, "adapter_key")
        self._runtime_adapters.pop(key, None)

    def register_authority(
        self,
        spec: AuthoritySpec,
        *,
        idempotency_key: str,
        expected_revision: int | None = None,
    ) -> StoredAuthority:
        validated = _validate_spec(spec)
        result = self._store.upsert(
            "authority",
            validated.authority_id,
            asdict(validated),
            idempotency_key=idempotency_key,
            expected_revision=expected_revision,
        )
        return StoredAuthority(
            spec=_parse_spec(result.record.payload),
            revision=result.record.revision,
        )

    def get_authority(self, authority_id: str) -> StoredAuthority:
        authority_id = _validate_token(authority_id, "authority_id")
        try:
            record = self._store.get("authority", authority_id)
        except NotFoundError as exc:
            raise AuthorityNotFoundError(f"unknown authority: {authority_id}") from exc
        return StoredAuthority(spec=_parse_spec(record.payload), revision=record.revision)

    def activate(
        self,
        data_class: str,
        authority_id: str,
        *,
        idempotency_key: str,
        expected_revision: int | None,
    ) -> AuthorityBinding:
        data_class = _validate_data_class(data_class)
        authority = self.get_authority(authority_id)
        _require_eligible(authority.spec)
        binding_payload = {
            "data_class": data_class,
            "authority_id": authority.spec.authority_id,
        }
        result = self._store.upsert(
            "authority_binding",
            _binding_id(data_class),
            binding_payload,
            idempotency_key=idempotency_key,
            expected_revision=expected_revision,
        )
        return _parse_binding(result.record.payload, result.record.revision)

    def get_binding(self, data_class: str) -> AuthorityBinding:
        data_class = _validate_data_class(data_class)
        try:
            record = self._store.get("authority_binding", _binding_id(data_class))
        except NotFoundError as exc:
            raise AuthorityBindingNotFoundError(
                f"no canonical authority is bound for data class: {data_class}"
            ) from exc
        binding = _parse_binding(record.payload, record.revision)
        if binding.data_class != data_class:
            raise AuthoritySchemaError("binding data class does not match its stable identity")
        return binding

    def resolve(self, data_class: str) -> AuthorityRoute:
        binding = self.get_binding(data_class)
        authority = self.get_authority(binding.authority_id)
        _require_eligible(authority.spec)

        adapter = self._runtime_adapters.get(authority.spec.adapter_key)
        if adapter is None:
            raise AuthorityUnavailableError(
                f"adapter is not registered at runtime: {authority.spec.adapter_key}"
            )

        try:
            health = adapter.health()
            schema = adapter.schema()
        except Exception as exc:
            raise AuthorityUnavailableError(
                f"adapter capability check failed: {authority.spec.adapter_key}"
            ) from exc

        if not health.ok:
            raise AuthorityUnavailableError(
                f"adapter is unhealthy: {authority.spec.adapter_key}"
            )

        if schema.schema_version != authority.spec.schema_version:
            raise AuthorityUnavailableError(
                "adapter schema version does not match verified authority metadata"
            )

        return AuthorityRoute(
            authority=authority,
            binding=binding,
            adapter=adapter,
        )

    def set_enabled(
        self,
        authority_id: str,
        enabled: bool,
        *,
        idempotency_key: str,
        expected_revision: int,
    ) -> StoredAuthority:
        if not isinstance(enabled, bool):
            raise AuthorityRegistryError("enabled must be boolean")
        current = self.get_authority(authority_id)
        revised = replace(current.spec, enabled=enabled)
        return self.register_authority(
            revised,
            idempotency_key=idempotency_key,
            expected_revision=expected_revision,
        )


def _validate_spec(spec: AuthoritySpec) -> AuthoritySpec:
    if not isinstance(spec, AuthoritySpec):
        raise AuthorityRegistryError("spec must be an AuthoritySpec")
    if not isinstance(spec.verified, bool) or not isinstance(spec.enabled, bool):
        raise AuthorityRegistryError("verified and enabled must be boolean")
    return AuthoritySpec(
        authority_id=_validate_token(spec.authority_id, "authority_id"),
        adapter_key=_validate_token(spec.adapter_key, "adapter_key"),
        resource_ref=_validate_token(spec.resource_ref, "resource_ref"),
        namespace=_validate_token(spec.namespace, "namespace"),
        failure_domain=_validate_token(spec.failure_domain, "failure_domain"),
        owner_id=_validate_token(spec.owner_id, "owner_id"),
        schema_version=_validate_token(spec.schema_version, "schema_version"),
        verified=spec.verified,
        enabled=spec.enabled,
    )


def _parse_spec(payload: Mapping[str, object]) -> AuthoritySpec:
    try:
        return _validate_spec(
            AuthoritySpec(
                authority_id=payload["authority_id"],
                adapter_key=payload["adapter_key"],
                resource_ref=payload["resource_ref"],
                namespace=payload["namespace"],
                failure_domain=payload["failure_domain"],
                owner_id=payload["owner_id"],
                schema_version=payload["schema_version"],
                verified=payload["verified"],
                enabled=payload["enabled"],
            )
        )
    except (KeyError, TypeError, AuthorityRegistryError) as exc:
        raise AuthoritySchemaError("persisted Authority metadata is invalid") from exc


def _parse_binding(payload: Mapping[str, object], revision: int) -> AuthorityBinding:
    try:
        data_class = _validate_data_class(payload["data_class"])
        authority_id = _validate_token(payload["authority_id"], "authority_id")
    except (KeyError, TypeError, AuthorityRegistryError) as exc:
        raise AuthoritySchemaError("persisted Authority binding is invalid") from exc
    return AuthorityBinding(
        data_class=data_class,
        authority_id=authority_id,
        revision=revision,
    )


def _require_eligible(spec: AuthoritySpec) -> None:
    if not spec.enabled:
        raise AuthorityUnavailableError(f"authority is disabled: {spec.authority_id}")
    if not spec.verified:
        raise AuthorityUnavailableError(f"authority is not verified: {spec.authority_id}")


def _validate_data_class(value: object) -> str:
    if not isinstance(value, str) or not _DATA_CLASS_RE.fullmatch(value):
        raise AuthorityRegistryError(f"data_class must match {_DATA_CLASS_RE.pattern}")
    return value


def _binding_id(data_class: str) -> str:
    return f"binding-{data_class}"


def _validate_token(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise AuthorityRegistryError(f"{field} must be a non-empty trimmed string")
    if len(value) > 128:
        raise AuthorityRegistryError(f"{field} must be at most 128 characters")
    return value
