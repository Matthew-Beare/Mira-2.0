"""Canonical Authority Registry built on the structured-state contract.

The registry persists authority metadata and one binding per mutable data class.
Runtime adapter objects are mounted explicitly and are never themselves authority.
This module also contains provider-neutral fail-closed evidence policy for mutable
current-state facts and durable-purchase commit readiness. These helpers decide
whether evidence is strong enough to be presented or committed; provider adapters
still perform the actual reads and writes.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from enum import Enum
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


class VerificationStatus(str, Enum):
    """Verification ceiling for a mutable current-state fact."""

    VERIFIED = "verified"
    USER_REPORTED = "user_reported"
    UNVERIFIED = "unverified"


class AuthoritySource(str, Enum):
    """Evidence source classes used by fail-closed mutable-fact policy."""

    CARRIER = "carrier"
    USER = "user"
    VENDOR = "vendor"
    WORKSPACE = "workspace"
    PROVIDER = "provider"


@dataclass(frozen=True)
class MutableFactResult:
    value: str | None
    status: VerificationStatus
    authority: AuthoritySource | None
    reason: str


def resolve_shipment_fact(
    *,
    tracking_number: str | None,
    carrier_lookup_attempted: bool,
    carrier_value: str | None,
    user_value: str | None = None,
    vendor_value: str | None = None,
) -> MutableFactResult:
    """Resolve shipment state without allowing secondary evidence to impersonate carrier state.

    Once a tracking number exists, the live carrier is canonical for ETA,
    progress, exception, out-for-delivery and delivered state. A user statement
    or vendor email can identify the shipment, but cannot be promoted to live
    carrier truth merely because it is newer than a cached projection.
    """

    if not isinstance(carrier_lookup_attempted, bool):
        raise TypeError("carrier_lookup_attempted must be boolean")

    tracking = _clean_optional_text(tracking_number)
    carrier = _clean_optional_text(carrier_value)
    user = _clean_optional_text(user_value)
    vendor = _clean_optional_text(vendor_value)

    if tracking:
        if carrier_lookup_attempted and carrier:
            return MutableFactResult(
                value=carrier,
                status=VerificationStatus.VERIFIED,
                authority=AuthoritySource.CARRIER,
                reason="live carrier readback",
            )
        return MutableFactResult(
            value=None,
            status=VerificationStatus.UNVERIFIED,
            authority=AuthoritySource.CARRIER,
            reason="tracking exists; live carrier readback is required",
        )

    if user:
        return MutableFactResult(
            value=user,
            status=VerificationStatus.USER_REPORTED,
            authority=AuthoritySource.USER,
            reason="no tracking authority is available; value is explicitly user-reported",
        )

    if vendor:
        return MutableFactResult(
            value=vendor,
            status=VerificationStatus.UNVERIFIED,
            authority=AuthoritySource.VENDOR,
            reason="vendor evidence is secondary and no live carrier authority is available",
        )

    return MutableFactResult(
        value=None,
        status=VerificationStatus.UNVERIFIED,
        authority=None,
        reason="no authoritative shipment evidence is available",
    )


class AcquisitionState(str, Enum):
    """Commit readiness for receipt-linked durable purchase ingestion."""

    COMMITTED = "committed"
    NEEDS_REVIEW = "needs_review"
    NOT_INVENTORIED_CONSUMABLE = "not_inventoried_consumable"


@dataclass(frozen=True)
class DurablePurchaseEvidence:
    """Evidence required before a durable owned purchase is fully ingested."""

    consumable: bool
    ownership_confirmed: bool
    receipt_evidence_id: str | None
    archived_receipt_link: str | None
    category: str | None
    canonical_record_id: str | None
    canonical_record_receipt_link: str | None
    readback_confirmed: bool


@dataclass(frozen=True)
class AcquisitionResult:
    state: AcquisitionState
    missing: tuple[str, ...]


def evaluate_durable_purchase(evidence: DurablePurchaseEvidence) -> AcquisitionResult:
    """Require the full evidence -> archive -> inventory -> link -> readback chain.

    Receipt or order email is evidence, not proof that the inventory side effect
    succeeded. Durable non-consumables fail closed until the canonical record is
    linked back to the archived receipt and read back successfully.
    """

    if not isinstance(evidence, DurablePurchaseEvidence):
        raise TypeError("evidence must be DurablePurchaseEvidence")
    if not isinstance(evidence.consumable, bool):
        raise TypeError("consumable must be boolean")
    if not isinstance(evidence.ownership_confirmed, bool):
        raise TypeError("ownership_confirmed must be boolean")
    if not isinstance(evidence.readback_confirmed, bool):
        raise TypeError("readback_confirmed must be boolean")

    if evidence.consumable:
        return AcquisitionResult(
            state=AcquisitionState.NOT_INVENTORIED_CONSUMABLE,
            missing=(),
        )

    receipt_evidence_id = _clean_optional_text(evidence.receipt_evidence_id)
    archived_receipt_link = _clean_optional_text(evidence.archived_receipt_link)
    category = _clean_optional_text(evidence.category)
    canonical_record_id = _clean_optional_text(evidence.canonical_record_id)
    canonical_record_receipt_link = _clean_optional_text(
        evidence.canonical_record_receipt_link
    )

    missing: list[str] = []
    if not evidence.ownership_confirmed:
        missing.append("ownership_confirmed")
    if not receipt_evidence_id:
        missing.append("receipt_evidence_id")
    if not archived_receipt_link:
        missing.append("archived_receipt_link")
    if not category:
        missing.append("category")
    if not canonical_record_id:
        missing.append("canonical_record_id")
    if not canonical_record_receipt_link:
        missing.append("canonical_record_receipt_link")
    if (
        archived_receipt_link
        and canonical_record_receipt_link
        and archived_receipt_link != canonical_record_receipt_link
    ):
        missing.append("receipt_link_readback_mismatch")
    if not evidence.readback_confirmed:
        missing.append("readback_confirmed")

    return AcquisitionResult(
        state=AcquisitionState.COMMITTED if not missing else AcquisitionState.NEEDS_REVIEW,
        missing=tuple(missing),
    )


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


def _clean_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise TypeError("text evidence values must be strings or None")
    stripped = value.strip()
    return stripped or None
