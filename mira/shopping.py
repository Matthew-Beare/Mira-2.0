"""Canonical shopping intent and explicit receipt reconciliation for Personal MIRA.

Shopping intent answers what the user still intends to obtain. It is deliberately
separate from canonical receipt/purchase history: the existence of a receipt never
silently fulfills an intent, and fulfilling an intent never mutates the receipt or
creates downstream asset, inventory, fitment, order, spending, par, or grocery state.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, replace
from datetime import datetime
from decimal import Decimal, InvalidOperation
import re
from typing import Any, Mapping

from .receipts import ReceiptError, ReceiptService, ReceiptView
from .structured_state import (
    IdempotencyConflictError,
    IdentityConflictError,
    NotFoundError,
    ResourceRecord,
    RevisionConflictError,
    StructuredStateAdapter,
    StructuredStateError,
    ValidationError as StoreValidationError,
)


SHOPPING_INTENT_RESOURCE_TYPE = "shopping_intent"
SHOPPING_INTENT_SCHEMA_VERSION = 1
SHOPPING_INTENT_STATES = frozenset({"active", "fulfilled", "cancelled"})
_STATE_RANK = {"active": 0, "fulfilled": 1, "cancelled": 2}
_TOKEN_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_WS_RE = re.compile(r"\s+")
_UNSET = object()


class ShoppingIntentError(Exception):
    """Base class for shopping-intent failures."""


class ShoppingIntentValidationError(ShoppingIntentError):
    """Raised when requested or persisted shopping-intent material is malformed."""


class ShoppingIntentTransitionError(ShoppingIntentError):
    """Raised when an explicit lifecycle transition is not allowed."""


class ShoppingIntentConflictError(ShoppingIntentError):
    """Raised when revision, identity, or replay material conflicts."""


class ShoppingIntentIntegrityError(ShoppingIntentError):
    """Raised when persisted canonical state cannot be reconciled safely."""


@dataclass(frozen=True)
class ReceiptReconciliation:
    receipt_id: str
    receipt_line_id: str | None
    receipt_revision: int
    reconciled_at: str

    def payload(self) -> dict[str, Any]:
        return {
            "receipt_id": self.receipt_id,
            "receipt_line_id": self.receipt_line_id,
            "receipt_revision": self.receipt_revision,
            "reconciled_at": self.reconciled_at,
        }


@dataclass(frozen=True)
class ShoppingIntentView:
    intent_id: str
    revision: int
    description: str
    search_text: str
    quantity: str
    unit: str | None
    note: str | None
    state: str
    created_at: str
    updated_at: str
    fulfilled_at: str | None
    cancelled_at: str | None
    reconciliation: ReceiptReconciliation | None
    idempotent_replay: bool = False

    @property
    def active(self) -> bool:
        return self.state == "active"

    def sort_key(self) -> tuple[int, str, str, str]:
        return (_STATE_RANK[self.state], self.created_at, self.search_text, self.intent_id)


class ShoppingIntentService:
    """Create, query, revise, cancel, and explicitly reconcile shopping intent."""

    def __init__(
        self,
        adapter: StructuredStateAdapter,
        *,
        receipt_service: ReceiptService | None = None,
        resource_type: str = SHOPPING_INTENT_RESOURCE_TYPE,
    ) -> None:
        self._adapter = adapter
        self._receipts = receipt_service or ReceiptService(adapter)
        self._resource_type = resource_type

    def create(
        self,
        intent_id: str,
        *,
        description: str,
        quantity: object,
        created_at: str,
        idempotency_key: str,
        unit: str | None = None,
        note: str | None = None,
    ) -> ShoppingIntentView:
        intent = _intent_id(intent_id)
        when = _timestamp(created_at, "created_at")
        payload = _payload(
            intent_id=intent,
            description=description,
            quantity=quantity,
            unit=unit,
            note=note,
            state="active",
            created_at=when,
            updated_at=when,
            fulfilled_at=None,
            cancelled_at=None,
            reconciliation=None,
        )
        return self._upsert(
            intent,
            payload,
            idempotency_key=idempotency_key,
            expected_revision=0,
        )

    def get(self, intent_id: str) -> ShoppingIntentView:
        normalized = _intent_id(intent_id)
        try:
            return _view(self._adapter.get(self._resource_type, normalized))
        except NotFoundError as exc:
            raise ShoppingIntentValidationError(
                f"shopping intent {normalized!r} does not exist"
            ) from exc
        except StoreValidationError as exc:
            raise ShoppingIntentValidationError(str(exc)) from exc
        except StructuredStateError as exc:
            raise ShoppingIntentIntegrityError(str(exc)) from exc

    def update(
        self,
        intent_id: str,
        *,
        updated_at: str,
        idempotency_key: str,
        description: str | object = _UNSET,
        quantity: object = _UNSET,
        unit: str | None | object = _UNSET,
        note: str | None | object = _UNSET,
    ) -> ShoppingIntentView:
        current = self.get(intent_id)
        if current.state != "active":
            raise ShoppingIntentTransitionError(
                "only active shopping intent can be edited"
            )
        when = _timestamp(updated_at, "updated_at")
        desired_description = (
            current.description
            if description is _UNSET
            else _display_text(description, "description", 1000)
        )
        desired_quantity = current.quantity if quantity is _UNSET else _quantity(quantity)
        desired_unit = (
            current.unit if unit is _UNSET else _optional_text(unit, "unit", 128)
        )
        desired_note = (
            current.note if note is _UNSET else _optional_text(note, "note", 4000)
        )
        if when == current.updated_at:
            if (
                desired_description == current.description
                and desired_quantity == current.quantity
                and desired_unit == current.unit
                and desired_note == current.note
            ):
                return replace(current, idempotent_replay=True)
            raise ShoppingIntentTransitionError(
                "updated_at matches current state but requested shopping material differs"
            )
        _strictly_later(when, current.updated_at, "updated_at")
        payload = _payload(
            intent_id=current.intent_id,
            description=desired_description,
            quantity=desired_quantity,
            unit=desired_unit,
            note=desired_note,
            state="active",
            created_at=current.created_at,
            updated_at=when,
            fulfilled_at=None,
            cancelled_at=None,
            reconciliation=None,
        )
        return self._upsert(
            current.intent_id,
            payload,
            idempotency_key=idempotency_key,
            expected_revision=current.revision,
        )

    def cancel(
        self,
        intent_id: str,
        *,
        cancelled_at: str,
        idempotency_key: str,
    ) -> ShoppingIntentView:
        current = self.get(intent_id)
        when = _timestamp(cancelled_at, "cancelled_at")
        if current.state == "cancelled":
            if current.cancelled_at == when:
                return replace(current, idempotent_replay=True)
            raise ShoppingIntentTransitionError(
                "shopping intent is already cancelled at a different time"
            )
        if current.state != "active":
            raise ShoppingIntentTransitionError(
                "only active shopping intent can be cancelled"
            )
        _strictly_later(when, current.updated_at, "cancelled_at")
        payload = _payload(
            intent_id=current.intent_id,
            description=current.description,
            quantity=current.quantity,
            unit=current.unit,
            note=current.note,
            state="cancelled",
            created_at=current.created_at,
            updated_at=when,
            fulfilled_at=None,
            cancelled_at=when,
            reconciliation=None,
        )
        return self._upsert(
            current.intent_id,
            payload,
            idempotency_key=idempotency_key,
            expected_revision=current.revision,
        )

    def fulfill_from_receipt(
        self,
        intent_id: str,
        *,
        receipt_id: str,
        reconciled_at: str,
        idempotency_key: str,
        receipt_line_id: str | None = None,
    ) -> ShoppingIntentView:
        current = self.get(intent_id)
        when = _timestamp(reconciled_at, "reconciled_at")
        requested_receipt_id = _token(receipt_id, "receipt_id")
        requested_line_id = (
            None
            if receipt_line_id is None
            else _token(receipt_line_id, "receipt_line_id")
        )
        if current.state == "fulfilled":
            prior = current.reconciliation
            if (
                prior is not None
                and prior.receipt_id == requested_receipt_id
                and prior.receipt_line_id == requested_line_id
                and prior.reconciled_at == when
                and current.fulfilled_at == when
            ):
                return replace(current, idempotent_replay=True)
            raise ShoppingIntentTransitionError(
                "shopping intent is already fulfilled from different receipt material"
            )
        if current.state != "active":
            raise ShoppingIntentTransitionError(
                "only active shopping intent can be fulfilled"
            )
        _strictly_later(when, current.updated_at, "reconciled_at")
        receipt, line_id = self._validated_receipt_target(
            requested_receipt_id, requested_line_id
        )
        reconciliation = ReceiptReconciliation(
            receipt_id=receipt.receipt_id,
            receipt_line_id=line_id,
            receipt_revision=receipt.revision,
            reconciled_at=when,
        )
        payload = _payload(
            intent_id=current.intent_id,
            description=current.description,
            quantity=current.quantity,
            unit=current.unit,
            note=current.note,
            state="fulfilled",
            created_at=current.created_at,
            updated_at=when,
            fulfilled_at=when,
            cancelled_at=None,
            reconciliation=reconciliation,
        )
        return self._upsert(
            current.intent_id,
            payload,
            idempotency_key=idempotency_key,
            expected_revision=current.revision,
        )

    def query(
        self,
        *,
        intent_id: str | None = None,
        state: str | None = None,
        description: str | None = None,
        limit: int = 100,
    ) -> tuple[ShoppingIntentView, ...]:
        bounded_limit = _limit(limit)
        wanted_id = None if intent_id is None else _intent_id(intent_id)
        wanted_state = None if state is None else _state(state)
        wanted_text = None if description is None else _search_text(description, "description")
        try:
            records = self._adapter.query(self._resource_type, limit=1000)
        except StoreValidationError as exc:
            raise ShoppingIntentValidationError(str(exc)) from exc
        except StructuredStateError as exc:
            raise ShoppingIntentIntegrityError(str(exc)) from exc
        rows = [_view(record) for record in records]
        filtered = []
        for row in rows:
            if wanted_id is not None and row.intent_id != wanted_id:
                continue
            if wanted_state is not None and row.state != wanted_state:
                continue
            if wanted_text is not None and wanted_text not in row.search_text:
                continue
            filtered.append(row)
        filtered.sort(key=ShoppingIntentView.sort_key)
        return tuple(filtered[:bounded_limit])

    def active_intents(self, *, limit: int = 100) -> tuple[ShoppingIntentView, ...]:
        return self.query(state="active", limit=limit)

    def _validated_receipt_target(
        self, receipt_id: str, receipt_line_id: str | None
    ) -> tuple[ReceiptView, str | None]:
        try:
            receipt = self._receipts.get(receipt_id)
        except ReceiptError as exc:
            raise ShoppingIntentValidationError(str(exc)) from exc
        if receipt.state != "captured":
            raise ShoppingIntentValidationError(
                "shopping fulfillment requires a canonical captured receipt, not review-only evidence"
            )
        if receipt_line_id is None:
            return receipt, None
        matches = [line for line in receipt.lines if line.line_id == receipt_line_id]
        if len(matches) != 1:
            raise ShoppingIntentValidationError(
                "receipt_line_id does not resolve to exactly one line on the canonical receipt"
            )
        return receipt, receipt_line_id

    def _upsert(
        self,
        intent_id: str,
        payload: Mapping[str, Any],
        *,
        idempotency_key: str,
        expected_revision: int,
    ) -> ShoppingIntentView:
        try:
            result = self._adapter.upsert(
                self._resource_type,
                intent_id,
                payload,
                idempotency_key=_token(idempotency_key, "idempotency_key"),
                expected_revision=expected_revision,
            )
        except (RevisionConflictError, IdempotencyConflictError, IdentityConflictError) as exc:
            raise ShoppingIntentConflictError(str(exc)) from exc
        except StoreValidationError as exc:
            raise ShoppingIntentValidationError(str(exc)) from exc
        except StructuredStateError as exc:
            raise ShoppingIntentIntegrityError(str(exc)) from exc
        return _view(result.record, idempotent_replay=result.idempotent_replay)


def _payload(
    *,
    intent_id: str,
    description: object,
    quantity: object,
    unit: object,
    note: object,
    state: object,
    created_at: object,
    updated_at: object,
    fulfilled_at: object,
    cancelled_at: object,
    reconciliation: ReceiptReconciliation | Mapping[str, Any] | None,
) -> dict[str, Any]:
    intent = _intent_id(intent_id)
    display = _display_text(description, "description", 1000)
    search = _search_text(display, "description")
    qty = _quantity(quantity)
    normalized_unit = _optional_text(unit, "unit", 128)
    normalized_note = _optional_text(note, "note", 4000)
    normalized_state = _state(state)
    created = _timestamp(created_at, "created_at")
    updated = _timestamp(updated_at, "updated_at")
    if _instant(updated) < _instant(created):
        raise ShoppingIntentValidationError("updated_at must not precede created_at")
    fulfilled = None if fulfilled_at is None else _timestamp(fulfilled_at, "fulfilled_at")
    cancelled = None if cancelled_at is None else _timestamp(cancelled_at, "cancelled_at")
    rec = _reconciliation(reconciliation)

    if normalized_state == "active":
        if fulfilled is not None or cancelled is not None or rec is not None:
            raise ShoppingIntentValidationError(
                "active shopping intent cannot contain terminal lifecycle material"
            )
    elif normalized_state == "fulfilled":
        if fulfilled is None or cancelled is not None or rec is None:
            raise ShoppingIntentValidationError(
                "fulfilled shopping intent requires fulfilled_at and receipt reconciliation only"
            )
        if fulfilled != updated or rec.reconciled_at != fulfilled:
            raise ShoppingIntentValidationError(
                "fulfilled lifecycle timestamps must equal the reconciliation timestamp"
            )
    elif normalized_state == "cancelled":
        if cancelled is None or fulfilled is not None or rec is not None:
            raise ShoppingIntentValidationError(
                "cancelled shopping intent requires cancelled_at and no receipt reconciliation"
            )
        if cancelled != updated:
            raise ShoppingIntentValidationError(
                "cancelled_at must equal updated_at for the cancellation transition"
            )

    return {
        "schema_version": SHOPPING_INTENT_SCHEMA_VERSION,
        "intent_id": intent,
        "description": display,
        "search_text": search,
        "quantity": qty,
        "unit": normalized_unit,
        "note": normalized_note,
        "state": normalized_state,
        "created_at": created,
        "updated_at": updated,
        "fulfilled_at": fulfilled,
        "cancelled_at": cancelled,
        "reconciliation": None if rec is None else rec.payload(),
    }


def _view(
    record: ResourceRecord, *, idempotent_replay: bool = False
) -> ShoppingIntentView:
    payload = deepcopy(record.payload)
    if payload.get("schema_version") != SHOPPING_INTENT_SCHEMA_VERSION:
        raise ShoppingIntentIntegrityError("unsupported shopping-intent schema version")
    intent_id = _intent_id(payload.get("intent_id"))
    if intent_id != record.resource_id:
        raise ShoppingIntentIntegrityError("shopping-intent identity/readback mismatch")
    try:
        normalized = _payload(
            intent_id=intent_id,
            description=payload.get("description"),
            quantity=payload.get("quantity"),
            unit=payload.get("unit"),
            note=payload.get("note"),
            state=payload.get("state"),
            created_at=payload.get("created_at"),
            updated_at=payload.get("updated_at"),
            fulfilled_at=payload.get("fulfilled_at"),
            cancelled_at=payload.get("cancelled_at"),
            reconciliation=payload.get("reconciliation"),
        )
    except ShoppingIntentValidationError as exc:
        raise ShoppingIntentIntegrityError(str(exc)) from exc
    if payload != normalized:
        raise ShoppingIntentIntegrityError(
            "persisted shopping-intent payload is noncanonical or malformed"
        )
    reconciliation = _reconciliation(normalized["reconciliation"])
    return ShoppingIntentView(
        intent_id=intent_id,
        revision=record.revision,
        description=normalized["description"],
        search_text=normalized["search_text"],
        quantity=normalized["quantity"],
        unit=normalized["unit"],
        note=normalized["note"],
        state=normalized["state"],
        created_at=normalized["created_at"],
        updated_at=normalized["updated_at"],
        fulfilled_at=normalized["fulfilled_at"],
        cancelled_at=normalized["cancelled_at"],
        reconciliation=reconciliation,
        idempotent_replay=idempotent_replay,
    )


def _reconciliation(
    value: ReceiptReconciliation | Mapping[str, Any] | None,
) -> ReceiptReconciliation | None:
    if value is None:
        return None
    if isinstance(value, ReceiptReconciliation):
        material = value.payload()
    elif isinstance(value, Mapping):
        material = dict(value)
    else:
        raise ShoppingIntentValidationError("reconciliation must be an object or null")
    expected = {"receipt_id", "receipt_line_id", "receipt_revision", "reconciled_at"}
    if set(material) != expected:
        raise ShoppingIntentValidationError(
            "reconciliation fields are incomplete or unexpected"
        )
    receipt_id = _token(material["receipt_id"], "receipt_id")
    line_id = (
        None
        if material["receipt_line_id"] is None
        else _token(material["receipt_line_id"], "receipt_line_id")
    )
    revision = material["receipt_revision"]
    if not isinstance(revision, int) or isinstance(revision, bool) or revision < 1:
        raise ShoppingIntentValidationError("receipt_revision must be a positive integer")
    when = _timestamp(material["reconciled_at"], "reconciled_at")
    return ReceiptReconciliation(
        receipt_id=receipt_id,
        receipt_line_id=line_id,
        receipt_revision=revision,
        reconciled_at=when,
    )


def _intent_id(value: object) -> str:
    return _token(value, "intent_id")


def _token(value: object, field: str) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise ShoppingIntentValidationError(f"{field} must be a non-empty trimmed string")
    if not _TOKEN_RE.fullmatch(value):
        raise ShoppingIntentValidationError(
            f"{field} must match {_TOKEN_RE.pattern}"
        )
    return value


def _display_text(value: object, field: str, max_length: int) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ShoppingIntentValidationError(f"{field} must be non-empty text")
    trimmed = value.strip()
    if len(trimmed) > max_length:
        raise ShoppingIntentValidationError(
            f"{field} must be at most {max_length} characters"
        )
    return trimmed


def _optional_text(value: object, field: str, max_length: int) -> str | None:
    if value is None:
        return None
    return _display_text(value, field, max_length)


def _search_text(value: object, field: str) -> str:
    display = _display_text(value, field, 1000)
    return _WS_RE.sub(" ", display).casefold()


def _quantity(value: object) -> str:
    if isinstance(value, bool):
        raise ShoppingIntentValidationError("quantity must be a positive decimal value")
    try:
        decimal = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise ShoppingIntentValidationError(
            "quantity must be a positive decimal value"
        ) from exc
    if not decimal.is_finite() or decimal <= 0:
        raise ShoppingIntentValidationError("quantity must be greater than zero")
    normalized = decimal.normalize()
    text = format(normalized, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text


def _state(value: object) -> str:
    if not isinstance(value, str) or value not in SHOPPING_INTENT_STATES:
        raise ShoppingIntentValidationError(
            "state must be one of active, fulfilled, or cancelled"
        )
    return value


def _timestamp(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise ShoppingIntentValidationError(
            f"{field} must be a non-empty trimmed ISO-8601 timestamp"
        )
    raw = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(raw)
    except ValueError as exc:
        raise ShoppingIntentValidationError(
            f"{field} must be a valid ISO-8601 timestamp"
        ) from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ShoppingIntentValidationError(f"{field} must include a UTC offset")
    return parsed.isoformat()


def _instant(value: str) -> datetime:
    return datetime.fromisoformat(value)


def _strictly_later(candidate: str, prior: str, field: str) -> None:
    if _instant(candidate) <= _instant(prior):
        raise ShoppingIntentTransitionError(
            f"{field} must be later than the current shopping-intent timestamp"
        )


def _limit(value: object) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or not 1 <= value <= 1000:
        raise ShoppingIntentValidationError("limit must be an integer from 1 through 1000")
    return value


__all__ = [
    "ReceiptReconciliation",
    "SHOPPING_INTENT_RESOURCE_TYPE",
    "SHOPPING_INTENT_SCHEMA_VERSION",
    "SHOPPING_INTENT_STATES",
    "ShoppingIntentConflictError",
    "ShoppingIntentError",
    "ShoppingIntentIntegrityError",
    "ShoppingIntentService",
    "ShoppingIntentTransitionError",
    "ShoppingIntentValidationError",
    "ShoppingIntentView",
]
