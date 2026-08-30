"""Canonical namespaced product/device identifiers for Personal MIRA.

Identifiers enrich an existing physical asset UUID; they never become the asset
identity. Exact source values are retained separately from deterministic search
normalization. Product-level identifiers may legitimately describe many assets,
while serial-level identifiers fail closed when reused across physical entities.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, replace
import hashlib
import json
import re
import unicodedata
from typing import Any

from .assets import AssetService, AssetValidationError, AssetView
from .structured_state import (
    NotFoundError,
    ResourceRecord,
    StructuredStateAdapter,
    ValidationError as StoreValidationError,
)


IDENTIFIER_RESOURCE_TYPE = "identifier"
IDENTIFIER_SCHEMA_VERSION = 1
IDENTIFIER_TYPES = frozenset(
    {
        "gtin8",
        "upc_a",
        "ean13",
        "gtin14",
        "merchant_sku",
        "manufacturer_part_number",
        "model_number",
        "serial_number",
        "imei",
        "mac",
    }
)
NAMESPACED_TYPES = frozenset(
    {
        "merchant_sku",
        "manufacturer_part_number",
        "model_number",
        "serial_number",
    }
)
SERIAL_LEVEL_TYPES = frozenset({"serial_number", "imei", "mac"})
VERIFICATION_STATES = frozenset({"observed", "verified"})


class IdentifierError(Exception):
    """Base class for canonical identifier failures."""


class IdentifierValidationError(IdentifierError):
    """Raised when identifier input or persisted state is malformed."""


class IdentifierConflictError(IdentifierError):
    """Raised when canonical identifier identity conflicts with requested state."""


class IdentifierIntegrityError(IdentifierError):
    """Raised when persisted identifier state violates identity invariants."""


@dataclass(frozen=True)
class IdentifierView:
    identifier_id: str
    revision: int
    entity_uuid: str
    identifier_type: str
    namespace: str | None
    namespace_key: str | None
    source_value: str
    normalized_value: str
    verification_state: str
    note: str | None
    idempotent_replay: bool = False


@dataclass(frozen=True)
class IdentifierAttachResult:
    identifier: IdentifierView
    outcome: str  # created | verified | replay


class IdentifierService:
    """Attach validated canonical identifiers to existing immutable assets."""

    def __init__(
        self,
        adapter: StructuredStateAdapter,
        *,
        asset_service: AssetService | None = None,
        resource_type: str = IDENTIFIER_RESOURCE_TYPE,
    ) -> None:
        self._adapter = adapter
        self._assets = asset_service or AssetService(adapter)
        self._resource_type = resource_type

    def attach(
        self,
        *,
        entity_uuid: str,
        identifier_type: str,
        value: str,
        idempotency_key: str,
        namespace: str | None = None,
        verification_state: str = "observed",
        note: str | None = None,
    ) -> IdentifierAttachResult:
        """Attach one identifier without changing the underlying asset identity."""

        key = _text(idempotency_key, "idempotency_key", 128)
        kind = _identifier_type(identifier_type)
        exact_value = _source_value(value)
        display_namespace, namespace_key = _namespace(kind, namespace)
        normalized_value = _normalized_value(kind, exact_value)
        state = _verification_state(verification_state)
        normalized_note = _optional_text(note, "note", 4000)

        try:
            asset = self._assets.get(entity_uuid)
        except AssetValidationError as exc:
            raise IdentifierValidationError(str(exc)) from exc

        all_identifiers = self._all_views()
        if kind in SERIAL_LEVEL_TYPES:
            collisions = [
                item
                for item in all_identifiers
                if item.identifier_type == kind
                and item.namespace_key == namespace_key
                and item.normalized_value == normalized_value
                and item.entity_uuid != asset.entity_uuid
            ]
            if collisions:
                raise IdentifierConflictError(
                    "serial-level identifier is already attached to another Entity UUID"
                )

        identifier_id = _identifier_id(
            entity_uuid=asset.entity_uuid,
            identifier_type=kind,
            namespace_key=namespace_key,
            normalized_value=normalized_value,
        )
        try:
            current_record = self._adapter.get(self._resource_type, identifier_id)
        except NotFoundError:
            current_record = None
        except StoreValidationError as exc:
            raise IdentifierValidationError(str(exc)) from exc

        if current_record is not None:
            current = _view(current_record)
            _assert_same_identity(
                current,
                entity_uuid=asset.entity_uuid,
                identifier_type=kind,
                namespace_key=namespace_key,
                normalized_value=normalized_value,
            )
            if current.source_value != exact_value or current.namespace != display_namespace:
                raise IdentifierConflictError(
                    "identifier replay conflicts with the canonical exact source value or namespace"
                )
            if current.note != normalized_note:
                raise IdentifierConflictError(
                    "identifier replay cannot silently replace the canonical note"
                )
            if current.verification_state == "verified" or state == current.verification_state:
                return IdentifierAttachResult(
                    identifier=replace(current, idempotent_replay=True), outcome="replay"
                )
            upgraded = self._write(
                identifier_id=identifier_id,
                entity_uuid=asset.entity_uuid,
                identifier_type=kind,
                namespace=display_namespace,
                namespace_key=namespace_key,
                source_value=exact_value,
                normalized_value=normalized_value,
                verification_state="verified",
                note=normalized_note,
                expected_revision=current.revision,
                idempotency_key=key,
            )
            return IdentifierAttachResult(identifier=upgraded, outcome="verified")

        created = self._write(
            identifier_id=identifier_id,
            entity_uuid=asset.entity_uuid,
            identifier_type=kind,
            namespace=display_namespace,
            namespace_key=namespace_key,
            source_value=exact_value,
            normalized_value=normalized_value,
            verification_state=state,
            note=normalized_note,
            expected_revision=0,
            idempotency_key=key,
        )
        return IdentifierAttachResult(identifier=created, outcome="created")

    def get(self, identifier_id: str) -> IdentifierView:
        wanted = _text(identifier_id, "identifier_id", 128)
        try:
            return _view(self._adapter.get(self._resource_type, wanted))
        except NotFoundError as exc:
            raise IdentifierValidationError(f"identifier {wanted!r} does not exist") from exc
        except StoreValidationError as exc:
            raise IdentifierValidationError(str(exc)) from exc

    def query(
        self,
        *,
        entity_uuid: str | None = None,
        identifier_type: str | None = None,
        value: str | None = None,
        namespace: str | None = None,
        limit: int = 100,
    ) -> tuple[IdentifierView, ...]:
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 1000:
            raise IdentifierValidationError("limit must be an integer from 1 through 1000")

        wanted_entity: str | None = None
        if entity_uuid is not None:
            try:
                wanted_entity = self._assets.get(entity_uuid).entity_uuid
            except AssetValidationError as exc:
                raise IdentifierValidationError(str(exc)) from exc

        wanted_type = None if identifier_type is None else _identifier_type(identifier_type)
        if value is not None and wanted_type is None:
            raise IdentifierValidationError("identifier_type is required when filtering by value")

        wanted_namespace_key: str | None | object = _UNSET
        if wanted_type is not None:
            _, wanted_namespace_key = _namespace(wanted_type, namespace)
        elif namespace is not None:
            raise IdentifierValidationError(
                "identifier_type is required when filtering by namespace"
            )

        wanted_value = None
        if value is not None:
            wanted_value = _normalized_value(wanted_type, _source_value(value))

        rows: list[IdentifierView] = []
        for item in self._all_views():
            if wanted_entity is not None and item.entity_uuid != wanted_entity:
                continue
            if wanted_type is not None and item.identifier_type != wanted_type:
                continue
            if wanted_namespace_key is not _UNSET and item.namespace_key != wanted_namespace_key:
                continue
            if wanted_value is not None and item.normalized_value != wanted_value:
                continue
            rows.append(item)
        rows.sort(
            key=lambda item: (
                item.identifier_type,
                item.namespace_key or "",
                item.normalized_value,
                item.entity_uuid,
                item.identifier_id,
            )
        )
        return tuple(rows[:limit])

    def lookup_assets(
        self,
        *,
        identifier_type: str,
        value: str,
        namespace: str | None = None,
        limit: int = 100,
    ) -> tuple[AssetView, ...]:
        identifiers = self.query(
            identifier_type=identifier_type,
            value=value,
            namespace=namespace,
            limit=limit,
        )
        assets: dict[str, AssetView] = {}
        for item in identifiers:
            try:
                assets[item.entity_uuid] = self._assets.get(item.entity_uuid)
            except AssetValidationError as exc:
                raise IdentifierIntegrityError(
                    "identifier references an asset that cannot be read canonically"
                ) from exc
        return tuple(assets[key] for key in sorted(assets))

    def _write(
        self,
        *,
        identifier_id: str,
        entity_uuid: str,
        identifier_type: str,
        namespace: str | None,
        namespace_key: str | None,
        source_value: str,
        normalized_value: str,
        verification_state: str,
        note: str | None,
        expected_revision: int,
        idempotency_key: str,
    ) -> IdentifierView:
        payload = {
            "schema_version": IDENTIFIER_SCHEMA_VERSION,
            "identifier_id": identifier_id,
            "entity_uuid": entity_uuid,
            "identifier_type": identifier_type,
            "namespace": namespace,
            "namespace_key": namespace_key,
            "source_value": source_value,
            "normalized_value": normalized_value,
            "verification_state": verification_state,
            "note": note,
        }
        try:
            result = self._adapter.upsert(
                self._resource_type,
                identifier_id,
                payload,
                idempotency_key=idempotency_key,
                expected_revision=expected_revision,
            )
        except StoreValidationError as exc:
            raise IdentifierValidationError(str(exc)) from exc
        return _view(result.record, idempotent_replay=result.idempotent_replay)

    def _all_views(self) -> tuple[IdentifierView, ...]:
        try:
            records = self._adapter.query(self._resource_type, limit=1000)
        except StoreValidationError as exc:
            raise IdentifierValidationError(str(exc)) from exc
        return tuple(_view(record) for record in records)


_UNSET = object()


def _view(record: ResourceRecord, *, idempotent_replay: bool = False) -> IdentifierView:
    payload = deepcopy(record.payload)
    if payload.get("schema_version") != IDENTIFIER_SCHEMA_VERSION:
        raise IdentifierValidationError("unsupported identifier schema version")
    identifier_id = _text(payload.get("identifier_id"), "identifier_id", 128)
    if identifier_id != record.resource_id:
        raise IdentifierValidationError("identifier_id does not match Resource identity")
    entity_uuid = _canonical_entity_uuid(payload.get("entity_uuid"))
    kind = _identifier_type(payload.get("identifier_type"))
    namespace, namespace_key = _namespace(kind, payload.get("namespace"))
    stored_namespace_key = payload.get("namespace_key")
    if stored_namespace_key != namespace_key:
        raise IdentifierValidationError("identifier namespace_key does not match namespace")
    source_value = _source_value(payload.get("source_value"))
    normalized_value = _normalized_value(kind, source_value)
    if payload.get("normalized_value") != normalized_value:
        raise IdentifierValidationError(
            "identifier normalized_value does not match source value/type"
        )
    expected_id = _identifier_id(
        entity_uuid=entity_uuid,
        identifier_type=kind,
        namespace_key=namespace_key,
        normalized_value=normalized_value,
    )
    if expected_id != identifier_id:
        raise IdentifierValidationError("identifier Resource identity is not deterministic")
    state = _verification_state(payload.get("verification_state"))
    note = _optional_text(payload.get("note"), "note", 4000)
    return IdentifierView(
        identifier_id=identifier_id,
        revision=record.revision,
        entity_uuid=entity_uuid,
        identifier_type=kind,
        namespace=namespace,
        namespace_key=namespace_key,
        source_value=source_value,
        normalized_value=normalized_value,
        verification_state=state,
        note=note,
        idempotent_replay=idempotent_replay,
    )


def _assert_same_identity(
    current: IdentifierView,
    *,
    entity_uuid: str,
    identifier_type: str,
    namespace_key: str | None,
    normalized_value: str,
) -> None:
    if (
        current.entity_uuid != entity_uuid
        or current.identifier_type != identifier_type
        or current.namespace_key != namespace_key
        or current.normalized_value != normalized_value
    ):
        raise IdentifierIntegrityError(
            "deterministic identifier Resource ID resolves conflicting canonical material"
        )


def _identifier_id(
    *,
    entity_uuid: str,
    identifier_type: str,
    namespace_key: str | None,
    normalized_value: str,
) -> str:
    material = {
        "entity_uuid": entity_uuid,
        "identifier_type": identifier_type,
        "namespace_key": namespace_key,
        "normalized_value": normalized_value,
    }
    digest = hashlib.sha256(
        json.dumps(
            material,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()
    return f"identifier-{digest[:32]}"


def _identifier_type(value: Any) -> str:
    if not isinstance(value, str):
        raise IdentifierValidationError("identifier_type must be text")
    normalized = value.strip().lower()
    if normalized not in IDENTIFIER_TYPES:
        raise IdentifierValidationError(
            "identifier_type must be one of " + ", ".join(sorted(IDENTIFIER_TYPES))
        )
    return normalized


def _namespace(kind: str, value: Any) -> tuple[str | None, str | None]:
    if kind in NAMESPACED_TYPES:
        display = _text(value, "namespace", 300)
        return display, _normalize_local(display)
    if value is not None:
        raise IdentifierValidationError(
            f"{kind} is a global identifier type and must not invent a local namespace"
        )
    return None, None


def _source_value(value: Any) -> str:
    return _text(value, "value", 500)


def _normalized_value(kind: str, source_value: str) -> str:
    if kind == "gtin8":
        return _gtin(source_value, 8, "GTIN-8")
    if kind == "upc_a":
        return _gtin(source_value, 12, "UPC-A")
    if kind == "ean13":
        return _gtin(source_value, 13, "EAN-13")
    if kind == "gtin14":
        return _gtin(source_value, 14, "GTIN-14")
    if kind == "imei":
        if not re.fullmatch(r"\d{15}", source_value):
            raise IdentifierValidationError("IMEI must contain exactly 15 digits")
        if not _luhn_valid(source_value):
            raise IdentifierValidationError("IMEI fails Luhn validation")
        return source_value
    if kind == "mac":
        return _mac(source_value)
    return _normalize_local(source_value)


def _gtin(source_value: str, length: int, label: str) -> str:
    if not re.fullmatch(rf"\d{{{length}}}", source_value):
        raise IdentifierValidationError(
            f"{label} must contain exactly {length} digits"
        )
    body = source_value[:-1]
    weighted = 0
    for index, character in enumerate(reversed(body)):
        weighted += int(character) * (3 if index % 2 == 0 else 1)
    expected = (10 - (weighted % 10)) % 10
    if expected != int(source_value[-1]):
        raise IdentifierValidationError(f"{label} check digit is invalid")
    return source_value


def _luhn_valid(digits: str) -> bool:
    total = 0
    for index, character in enumerate(digits):
        value = int(character)
        if index % 2 == 1:  # 15-digit IMEI: double positions 2,4,...,14.
            value *= 2
            if value > 9:
                value -= 9
        total += value
    return total % 10 == 0


def _mac(source_value: str) -> str:
    patterns = (
        r"[0-9A-Fa-f]{12}",
        r"(?:[0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}",
        r"(?:[0-9A-Fa-f]{2}-){5}[0-9A-Fa-f]{2}",
        r"(?:[0-9A-Fa-f]{4}\.){2}[0-9A-Fa-f]{4}",
    )
    if not any(re.fullmatch(pattern, source_value) for pattern in patterns):
        raise IdentifierValidationError(
            "MAC must be 12 hexadecimal digits in compact, colon, hyphen, or Cisco-dot form"
        )
    return re.sub(r"[:.\-]", "", source_value).upper()


def _normalize_local(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value)
    normalized = " ".join(normalized.strip().split()).casefold()
    if not normalized:
        raise IdentifierValidationError("normalized identifier/namespace cannot be blank")
    return normalized


def _verification_state(value: Any) -> str:
    if not isinstance(value, str):
        raise IdentifierValidationError("verification_state must be text")
    normalized = value.strip().lower()
    if normalized not in VERIFICATION_STATES:
        raise IdentifierValidationError(
            "verification_state must be observed or verified"
        )
    return normalized


def _canonical_entity_uuid(value: Any) -> str:
    # AssetService.get performs full canonical RFC-4122 validation before writes.
    if not isinstance(value, str) or not value.strip():
        raise IdentifierValidationError("entity_uuid must be non-empty text")
    normalized = value.strip().lower()
    if not re.fullmatch(
        r"[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}",
        normalized,
    ):
        raise IdentifierValidationError("entity_uuid must be a canonical RFC 4122 UUID")
    return normalized


def _text(value: Any, field: str, maximum: int) -> str:
    if not isinstance(value, str):
        raise IdentifierValidationError(f"{field} must be text")
    normalized = value.strip()
    if not normalized:
        raise IdentifierValidationError(f"{field} must not be blank")
    if len(normalized) > maximum:
        raise IdentifierValidationError(f"{field} exceeds maximum length {maximum}")
    return normalized


def _optional_text(value: Any, field: str, maximum: int) -> str | None:
    if value is None:
        return None
    return _text(value, field, maximum)


__all__ = [
    "IDENTIFIER_RESOURCE_TYPE",
    "IDENTIFIER_SCHEMA_VERSION",
    "IDENTIFIER_TYPES",
    "IdentifierAttachResult",
    "IdentifierConflictError",
    "IdentifierError",
    "IdentifierIntegrityError",
    "IdentifierService",
    "IdentifierValidationError",
    "IdentifierView",
]
