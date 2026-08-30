"""Canonical physical asset acquisition for Personal MIRA.

Asset identity is deliberately independent from receipts, names, locations,
fitment, identifiers, inventory projections, and backend storage. Each physical
asset (or intentionally grouped lot) receives one immutable RFC 4122 UUID.
Receipts provide acquisition provenance; they never become the asset identity.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, replace
from decimal import Decimal, InvalidOperation
import hashlib
import json
from typing import Any, Sequence
from uuid import RFC_4122, UUID, uuid4

from .receipts import ReceiptLine, ReceiptService, ReceiptValidationError
from .structured_state import (
    NotFoundError,
    ResourceRecord,
    StructuredStateAdapter,
    ValidationError as StoreValidationError,
)


ASSET_RESOURCE_TYPE = "asset"
ASSET_SCHEMA_VERSION = 1
ASSET_TRACKING_MODES = frozenset({"individual", "lot"})


class AssetError(Exception):
    """Base class for canonical asset failures."""


class AssetValidationError(AssetError):
    """Raised when an asset/acquisition input or persisted record is malformed."""


class AssetConflictError(AssetError):
    """Raised when source identity contradicts canonical asset state."""


class AssetIntegrityError(AssetError):
    """Raised when persisted canonical asset identity is internally inconsistent."""


@dataclass(frozen=True)
class AssetAcquisition:
    source_type: str
    source_identity: str
    receipt_id: str
    receipt_line_id: str | None
    receipt_revision: int
    acquisition_key: str

    def payload(self) -> dict[str, Any]:
        return {
            "source_type": self.source_type,
            "source_identity": self.source_identity,
            "receipt_id": self.receipt_id,
            "receipt_line_id": self.receipt_line_id,
            "receipt_revision": self.receipt_revision,
            "acquisition_key": self.acquisition_key,
        }


@dataclass(frozen=True)
class AssetView:
    entity_uuid: str
    revision: int
    display_name: str
    tracking_mode: str
    quantity: int
    acquisition: AssetAcquisition
    note: str | None
    idempotent_replay: bool = False


@dataclass(frozen=True)
class AssetAcquisitionResult:
    asset: AssetView
    outcome: str  # created | enriched | replay


class AssetService:
    """Create and enrich immutable receipt-linked physical asset identities."""

    def __init__(
        self,
        adapter: StructuredStateAdapter,
        *,
        receipt_service: ReceiptService | None = None,
        resource_type: str = ASSET_RESOURCE_TYPE,
    ) -> None:
        self._adapter = adapter
        self._receipts = receipt_service or ReceiptService(adapter)
        self._resource_type = resource_type

    def acquire(
        self,
        *,
        receipt_id: str,
        acquisition_key: str,
        display_name: str,
        tracking_mode: str,
        quantity: int,
        idempotency_key: str,
        receipt_line_id: str | None = None,
        entity_uuid: str | None = None,
        note: str | None = None,
    ) -> AssetAcquisitionResult:
        """Acquire one individual or intentionally grouped lot from a receipt.

        ``acquisition_key`` is stable source identity within the selected receipt
        or receipt line. For multiple individually tracked units from one receipt
        line, callers use distinct stable keys (for example ``unit-1`` and
        ``unit-2``). Replaying one key always resolves the same Entity UUID.
        """

        key = _text(idempotency_key, "idempotency_key", 128)
        acquisition_key_value = _text(acquisition_key, "acquisition_key", 128)
        name = _text(display_name, "display_name", 500)
        mode = _tracking_mode(tracking_mode)
        count = _quantity(quantity, mode)
        normalized_note = _optional_text(note, "note", 4000)
        requested_uuid = None if entity_uuid is None else _entity_uuid(entity_uuid)

        try:
            receipt = self._receipts.get(receipt_id)
        except ReceiptValidationError as exc:
            raise AssetValidationError(str(exc)) from exc
        if receipt.state != "captured":
            raise AssetValidationError(
                "asset acquisition requires a canonical captured receipt, not needs_review evidence"
            )

        line = _receipt_line(receipt.lines, receipt_line_id)
        if line is not None:
            purchased_units = _integral_receipt_quantity(line)
            if count > purchased_units:
                raise AssetValidationError(
                    "asset quantity exceeds the canonical receipt-line quantity"
                )

        source_identity = _source_identity(
            receipt_id=receipt.receipt_id,
            receipt_line_id=None if line is None else line.line_id,
            acquisition_key=acquisition_key_value,
        )
        acquisition = AssetAcquisition(
            source_type="receipt",
            source_identity=source_identity,
            receipt_id=receipt.receipt_id,
            receipt_line_id=None if line is None else line.line_id,
            receipt_revision=receipt.revision,
            acquisition_key=acquisition_key_value,
        )

        existing = self._all_views()
        source_matches = [
            asset for asset in existing if asset.acquisition.source_identity == source_identity
        ]
        if len(source_matches) > 1:
            raise AssetIntegrityError(
                "one acquisition source identity is attached to multiple Entity UUIDs"
            )
        if source_matches:
            current = source_matches[0]
            _assert_acquisition_compatible(
                current,
                acquisition=acquisition,
                tracking_mode=mode,
                quantity=count,
                requested_uuid=requested_uuid,
            )
            if current.display_name == name and current.note == normalized_note:
                return AssetAcquisitionResult(
                    asset=replace(current, idempotent_replay=True), outcome="replay"
                )
            enriched = self._write(
                current.entity_uuid,
                display_name=name,
                tracking_mode=current.tracking_mode,
                quantity=current.quantity,
                acquisition=replace(
                    current.acquisition,
                    receipt_revision=max(
                        current.acquisition.receipt_revision, acquisition.receipt_revision
                    ),
                ),
                note=normalized_note,
                expected_revision=current.revision,
                idempotency_key=key,
            )
            return AssetAcquisitionResult(asset=enriched, outcome="enriched")

        if line is not None:
            self._validate_line_capacity(
                existing,
                receipt_id=receipt.receipt_id,
                receipt_line_id=line.line_id,
                purchased_units=_integral_receipt_quantity(line),
                proposed_quantity=count,
            )

        allocated_uuid = requested_uuid or str(uuid4())
        try:
            prior_uuid = self._adapter.get(self._resource_type, allocated_uuid)
        except NotFoundError:
            prior_uuid = None
        except StoreValidationError as exc:
            raise AssetValidationError(str(exc)) from exc
        if prior_uuid is not None:
            raise AssetConflictError(
                "requested/allocated Entity UUID already belongs to another canonical asset"
            )

        created = self._write(
            allocated_uuid,
            display_name=name,
            tracking_mode=mode,
            quantity=count,
            acquisition=acquisition,
            note=normalized_note,
            expected_revision=0,
            idempotency_key=key,
        )
        return AssetAcquisitionResult(asset=created, outcome="created")

    def get(self, entity_uuid: str) -> AssetView:
        normalized = _entity_uuid(entity_uuid)
        try:
            return _view(self._adapter.get(self._resource_type, normalized))
        except NotFoundError as exc:
            raise AssetValidationError(f"asset {normalized!r} does not exist") from exc
        except StoreValidationError as exc:
            raise AssetValidationError(str(exc)) from exc

    def enrich(
        self,
        entity_uuid: str,
        *,
        idempotency_key: str,
        display_name: str | None = None,
        note: str | None | object = None,
        replace_note: bool = False,
    ) -> AssetView:
        """Change nonidentity attributes without replacing acquisition or UUID."""

        key = _text(idempotency_key, "idempotency_key", 128)
        if not isinstance(replace_note, bool):
            raise AssetValidationError("replace_note must be boolean")
        current = self.get(entity_uuid)
        name = current.display_name if display_name is None else _text(
            display_name, "display_name", 500
        )
        if replace_note:
            normalized_note = _optional_text(note, "note", 4000)
        else:
            if note is not None:
                raise AssetValidationError(
                    "note changes require replace_note=True so existing notes are not silently overwritten"
                )
            normalized_note = current.note
        if name == current.display_name and normalized_note == current.note:
            return replace(current, idempotent_replay=True)
        return self._write(
            current.entity_uuid,
            display_name=name,
            tracking_mode=current.tracking_mode,
            quantity=current.quantity,
            acquisition=current.acquisition,
            note=normalized_note,
            expected_revision=current.revision,
            idempotency_key=key,
        )

    def query(
        self,
        *,
        receipt_id: str | None = None,
        receipt_line_id: str | None = None,
        display_name: str | None = None,
        limit: int = 100,
    ) -> tuple[AssetView, ...]:
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 1000:
            raise AssetValidationError("limit must be an integer from 1 through 1000")
        wanted_receipt = None if receipt_id is None else _text(
            receipt_id, "receipt_id", 128
        )
        wanted_line = None if receipt_line_id is None else _text(
            receipt_line_id, "receipt_line_id", 128
        )
        wanted_name = None if display_name is None else _text(
            display_name, "display_name", 500
        ).casefold()
        rows = []
        for asset in self._all_views():
            if wanted_receipt is not None and asset.acquisition.receipt_id != wanted_receipt:
                continue
            if wanted_line is not None and asset.acquisition.receipt_line_id != wanted_line:
                continue
            if wanted_name is not None and wanted_name not in asset.display_name.casefold():
                continue
            rows.append(asset)
        rows.sort(key=lambda item: item.entity_uuid)
        return tuple(rows[:limit])

    def _validate_line_capacity(
        self,
        existing: Sequence[AssetView],
        *,
        receipt_id: str,
        receipt_line_id: str,
        purchased_units: int,
        proposed_quantity: int,
    ) -> None:
        used = sum(
            asset.quantity
            for asset in existing
            if asset.acquisition.receipt_id == receipt_id
            and asset.acquisition.receipt_line_id == receipt_line_id
        )
        if used + proposed_quantity > purchased_units:
            raise AssetConflictError(
                "asset acquisitions would exceed the canonical receipt-line quantity"
            )

    def _write(
        self,
        entity_uuid: str,
        *,
        display_name: str,
        tracking_mode: str,
        quantity: int,
        acquisition: AssetAcquisition,
        note: str | None,
        expected_revision: int,
        idempotency_key: str,
    ) -> AssetView:
        payload = {
            "schema_version": ASSET_SCHEMA_VERSION,
            "entity_uuid": entity_uuid,
            "display_name": display_name,
            "tracking_mode": tracking_mode,
            "quantity": quantity,
            "acquisition": acquisition.payload(),
            "note": note,
        }
        try:
            result = self._adapter.upsert(
                self._resource_type,
                entity_uuid,
                payload,
                idempotency_key=idempotency_key,
                expected_revision=expected_revision,
            )
        except StoreValidationError as exc:
            raise AssetValidationError(str(exc)) from exc
        return _view(result.record, idempotent_replay=result.idempotent_replay)

    def _all_views(self) -> tuple[AssetView, ...]:
        try:
            records = self._adapter.query(self._resource_type, limit=1000)
        except StoreValidationError as exc:
            raise AssetValidationError(str(exc)) from exc
        return tuple(_view(record) for record in records)


def _assert_acquisition_compatible(
    current: AssetView,
    *,
    acquisition: AssetAcquisition,
    tracking_mode: str,
    quantity: int,
    requested_uuid: str | None,
) -> None:
    if requested_uuid is not None and requested_uuid != current.entity_uuid:
        raise AssetConflictError(
            "replayed acquisition source cannot replace the canonical Entity UUID"
        )
    current_source = current.acquisition
    if (
        current_source.receipt_id != acquisition.receipt_id
        or current_source.receipt_line_id != acquisition.receipt_line_id
        or current_source.acquisition_key != acquisition.acquisition_key
        or current.tracking_mode != tracking_mode
        or current.quantity != quantity
    ):
        raise AssetConflictError(
            "replayed acquisition source conflicts with canonical asset acquisition facts"
        )


def _view(record: ResourceRecord, *, idempotent_replay: bool = False) -> AssetView:
    payload = deepcopy(record.payload)
    if payload.get("schema_version") != ASSET_SCHEMA_VERSION:
        raise AssetValidationError("unsupported asset schema version")
    entity_uuid = _entity_uuid(payload.get("entity_uuid"))
    if entity_uuid != record.resource_id:
        raise AssetValidationError("asset Entity UUID does not match Resource identity")
    display_name = _text(payload.get("display_name"), "display_name", 500)
    mode = _tracking_mode(payload.get("tracking_mode"))
    quantity = _quantity(payload.get("quantity"), mode)
    note = _optional_text(payload.get("note"), "note", 4000)

    raw_acquisition = payload.get("acquisition")
    if not isinstance(raw_acquisition, dict):
        raise AssetValidationError("asset acquisition must be an object")
    if raw_acquisition.get("source_type") != "receipt":
        raise AssetValidationError("first asset-acquisition slice supports receipt provenance only")
    source_identity = _text(
        raw_acquisition.get("source_identity"), "source_identity", 128
    )
    receipt_id = _text(raw_acquisition.get("receipt_id"), "receipt_id", 128)
    receipt_line_id = _optional_text(
        raw_acquisition.get("receipt_line_id"), "receipt_line_id", 128
    )
    receipt_revision = raw_acquisition.get("receipt_revision")
    if (
        not isinstance(receipt_revision, int)
        or isinstance(receipt_revision, bool)
        or receipt_revision < 1
    ):
        raise AssetValidationError("receipt_revision must be a positive integer")
    acquisition_key = _text(
        raw_acquisition.get("acquisition_key"), "acquisition_key", 128
    )
    expected_source = _source_identity(
        receipt_id=receipt_id,
        receipt_line_id=receipt_line_id,
        acquisition_key=acquisition_key,
    )
    if source_identity != expected_source:
        raise AssetValidationError("asset source_identity does not match acquisition provenance")

    return AssetView(
        entity_uuid=entity_uuid,
        revision=record.revision,
        display_name=display_name,
        tracking_mode=mode,
        quantity=quantity,
        acquisition=AssetAcquisition(
            source_type="receipt",
            source_identity=source_identity,
            receipt_id=receipt_id,
            receipt_line_id=receipt_line_id,
            receipt_revision=receipt_revision,
            acquisition_key=acquisition_key,
        ),
        note=note,
        idempotent_replay=idempotent_replay,
    )


def _receipt_line(
    lines: Sequence[ReceiptLine], receipt_line_id: str | None
) -> ReceiptLine | None:
    if receipt_line_id is None:
        return None
    wanted = _text(receipt_line_id, "receipt_line_id", 128)
    matches = [line for line in lines if line.line_id == wanted]
    if len(matches) != 1:
        raise AssetValidationError(
            "receipt_line_id must resolve to exactly one line on the canonical receipt"
        )
    return matches[0]


def _integral_receipt_quantity(line: ReceiptLine) -> int:
    try:
        value = Decimal(line.quantity)
    except InvalidOperation as exc:
        raise AssetValidationError("receipt-line quantity is not a valid decimal") from exc
    integral = value.to_integral_value()
    if value != integral or integral < 1:
        raise AssetValidationError(
            "asset acquisition from a receipt line requires a positive whole-unit quantity"
        )
    return int(integral)


def _source_identity(
    *, receipt_id: str, receipt_line_id: str | None, acquisition_key: str
) -> str:
    material = {
        "source_type": "receipt",
        "receipt_id": receipt_id,
        "receipt_line_id": receipt_line_id,
        "acquisition_key": acquisition_key,
    }
    encoded = json.dumps(
        material,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return "receipt-acquisition:" + hashlib.sha256(encoded).hexdigest()


def _entity_uuid(value: Any) -> str:
    if not isinstance(value, str) or value != value.strip() or not value:
        raise AssetValidationError("Entity UUID must be canonical RFC 4122 text")
    try:
        parsed = UUID(value)
    except (ValueError, AttributeError) as exc:
        raise AssetValidationError("Entity UUID must be valid RFC 4122 UUID text") from exc
    if parsed.variant != RFC_4122:
        raise AssetValidationError("Entity UUID must use the RFC 4122 variant")
    canonical = str(parsed)
    if value != canonical:
        raise AssetValidationError(
            "Entity UUID must use canonical lowercase hyphenated RFC 4122 text"
        )
    return canonical


def _tracking_mode(value: Any) -> str:
    if not isinstance(value, str) or value.strip().lower() not in ASSET_TRACKING_MODES:
        raise AssetValidationError("tracking_mode must be individual or lot")
    return value.strip().lower()


def _quantity(value: Any, mode: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise AssetValidationError("asset quantity must be a positive integer")
    if value > 1_000_000:
        raise AssetValidationError("asset quantity is unreasonably large")
    if mode == "individual" and value != 1:
        raise AssetValidationError("individual asset tracking requires quantity exactly 1")
    return value


def _text(value: Any, field: str, max_length: int) -> str:
    if not isinstance(value, str):
        raise AssetValidationError(f"{field} must be text")
    normalized = value.strip()
    if not normalized or normalized != value:
        raise AssetValidationError(f"{field} must be non-empty trimmed text")
    if len(normalized) > max_length:
        raise AssetValidationError(f"{field} must be at most {max_length} characters")
    return normalized


def _optional_text(value: Any, field: str, max_length: int) -> str | None:
    if value is None:
        return None
    return _text(value, field, max_length)


__all__ = [
    "ASSET_RESOURCE_TYPE",
    "ASSET_SCHEMA_VERSION",
    "ASSET_TRACKING_MODES",
    "AssetAcquisition",
    "AssetAcquisitionResult",
    "AssetConflictError",
    "AssetError",
    "AssetIntegrityError",
    "AssetService",
    "AssetValidationError",
    "AssetView",
]
