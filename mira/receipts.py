"""Canonical receipt intake and purchase-history state for Personal MIRA.

A receipt is structured purchase truth derived from one or more authorized
evidence observations. Raw email bodies, images, PDFs, and attachments remain in
their source/evidence provider; this module stores only normalized facts and
provenance metadata. New evidence may enrich unknown facts, but it never silently
rewrites contradictory canonical purchase facts.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
import hashlib
import json
import re
from typing import Any, Mapping, Sequence

from .structured_state import (
    NotFoundError,
    ResourceRecord,
    StructuredStateAdapter,
    ValidationError as StoreValidationError,
)


RECEIPT_RESOURCE_TYPE = "receipt"
RECEIPT_SCHEMA_VERSION = 1
RECEIPT_STATES = frozenset({"captured", "needs_review"})
RECEIPT_SOURCE_TYPES = frozenset({"email", "image", "text"})

_CURRENCY_RE = re.compile(r"^[A-Z]{3}$")
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_RECEIPT_ID_RE = re.compile(r"^receipt-[0-9a-f]{24}$")
_LINE_ID_RE = re.compile(r"^line-[0-9a-f]{16}$")
_WS_RE = re.compile(r"\s+")
_UNSET = object()


class ReceiptError(Exception):
    """Base class for receipt-domain failures."""


class ReceiptValidationError(ReceiptError):
    """Raised when receipt/evidence input or persisted state is malformed."""


class ReceiptConflictError(ReceiptError):
    """Raised when evidence contradicts an existing canonical receipt."""


class ReceiptAmbiguityError(ReceiptError):
    """Raised when more than one canonical receipt is a plausible match."""


class ReceiptIntegrityError(ReceiptError):
    """Raised when persisted receipt state violates uniqueness/integrity rules."""


@dataclass(frozen=True)
class ReceiptEvidence:
    source_type: str
    source_fingerprint: str
    source_ref: str | None
    observed_at: str

    def payload(self) -> dict[str, Any]:
        return {
            "source_type": self.source_type,
            "source_fingerprint": self.source_fingerprint,
            "source_ref": self.source_ref,
            "observed_at": self.observed_at,
        }


@dataclass(frozen=True)
class ReceiptLine:
    line_id: str
    description: str
    quantity: str
    unit_price_minor: int | None
    line_total_minor: int | None

    def payload(self) -> dict[str, Any]:
        return {
            "line_id": self.line_id,
            "description": self.description,
            "quantity": self.quantity,
            "unit_price_minor": self.unit_price_minor,
            "line_total_minor": self.line_total_minor,
        }

    def semantic_payload(self) -> dict[str, Any]:
        result = self.payload()
        result.pop("line_id")
        return result


@dataclass(frozen=True)
class ReceiptView:
    receipt_id: str
    revision: int
    merchant: str
    merchant_key: str
    order_number: str | None
    purchase_date: str
    currency: str
    total_minor: int
    subtotal_minor: int | None
    tax_minor: int | None
    shipping_minor: int | None
    discount_minor: int | None
    lines: tuple[ReceiptLine, ...]
    state: str
    evidence: tuple[ReceiptEvidence, ...]
    user_note: str | None
    idempotent_replay: bool = False


@dataclass(frozen=True)
class ReceiptCaptureResult:
    receipt: ReceiptView
    outcome: str  # created | merged | replay


@dataclass(frozen=True)
class _NormalizedReceipt:
    merchant: str
    merchant_key: str
    order_number: str | None
    order_key: str | None
    purchase_date: str
    currency: str
    total_minor: int
    subtotal_minor: int | None
    tax_minor: int | None
    shipping_minor: int | None
    discount_minor: int | None
    lines: tuple[ReceiptLine, ...]
    state: str
    user_note: str | None

    def core_match_key(self) -> tuple[str, str, str, int]:
        return (self.merchant_key, self.purchase_date, self.currency, self.total_minor)

    def facts_payload(self) -> dict[str, Any]:
        return {
            "merchant": self.merchant,
            "merchant_key": self.merchant_key,
            "order_number": self.order_number,
            "purchase_date": self.purchase_date,
            "currency": self.currency,
            "total_minor": self.total_minor,
            "subtotal_minor": self.subtotal_minor,
            "tax_minor": self.tax_minor,
            "shipping_minor": self.shipping_minor,
            "discount_minor": self.discount_minor,
            "lines": [line.payload() for line in self.lines],
            "state": self.state,
            "user_note": self.user_note,
        }


class ReceiptService:
    """Capture, reconcile, correct, read, and search canonical receipts."""

    def __init__(
        self,
        adapter: StructuredStateAdapter,
        *,
        resource_type: str = RECEIPT_RESOURCE_TYPE,
    ) -> None:
        self._adapter = adapter
        self._resource_type = resource_type

    def capture(
        self,
        *,
        merchant: str,
        purchase_date: str,
        currency: str,
        total_minor: int,
        source_type: str,
        source_fingerprint: str,
        observed_at: str,
        idempotency_key: str,
        source_ref: str | None = None,
        order_number: str | None = None,
        subtotal_minor: int | None = None,
        tax_minor: int | None = None,
        shipping_minor: int | None = None,
        discount_minor: int | None = None,
        lines: Sequence[Mapping[str, Any]] | None = None,
        state: str = "captured",
        user_note: str | None = None,
        distinct_transaction: bool = False,
    ) -> ReceiptCaptureResult:
        """Capture one normalized evidence observation into canonical receipt truth.

        ``distinct_transaction=True`` is an explicit operator/user assertion that
        a transaction matching merchant/date/currency/total is nevertheless a
        separate purchase. Exact source-fingerprint replay can never be bypassed.
        """

        if not isinstance(distinct_transaction, bool):
            raise ReceiptValidationError("distinct_transaction must be boolean")
        key = _idempotency_key(idempotency_key)
        normalized = _normalize_receipt(
            merchant=merchant,
            purchase_date=purchase_date,
            currency=currency,
            total_minor=total_minor,
            order_number=order_number,
            subtotal_minor=subtotal_minor,
            tax_minor=tax_minor,
            shipping_minor=shipping_minor,
            discount_minor=discount_minor,
            lines=lines or (),
            state=state,
            user_note=user_note,
        )
        observation = _evidence(
            source_type=source_type,
            source_fingerprint=source_fingerprint,
            source_ref=source_ref,
            observed_at=observed_at,
        )
        existing = self._all_views()

        fingerprint_matches = [
            receipt
            for receipt in existing
            if any(
                item.source_fingerprint == observation.source_fingerprint
                for item in receipt.evidence
            )
        ]
        if len(fingerprint_matches) > 1:
            raise ReceiptIntegrityError(
                "source fingerprint is attached to more than one canonical receipt"
            )
        if fingerprint_matches:
            current = fingerprint_matches[0]
            _assert_evidence_compatible(current, normalized)
            return ReceiptCaptureResult(receipt=current, outcome="replay")

        if not distinct_transaction:
            candidates = _correlation_candidates(existing, normalized)
            if len(candidates) > 1:
                raise ReceiptAmbiguityError(
                    "multiple canonical receipts match this transaction; explicit resolution is required"
                )
            if len(candidates) == 1:
                merged = self._merge_evidence(
                    candidates[0], normalized, observation, idempotency_key=key
                )
                return ReceiptCaptureResult(receipt=merged, outcome="merged")

        receipt_id = _initial_receipt_id(normalized, observation.source_fingerprint)
        try:
            prior_same_id = self._adapter.get(self._resource_type, receipt_id)
        except NotFoundError:
            prior_same_id = None
        except StoreValidationError as exc:
            raise ReceiptValidationError(str(exc)) from exc
        if prior_same_id is not None:
            # A cryptographic-prefix collision or deliberately repeated distinct
            # capture must never overwrite an existing receipt identity.
            raise ReceiptIntegrityError(
                f"derived receipt identity already exists: {receipt_id}"
            )

        payload = _receipt_payload(receipt_id, normalized, (observation,))
        try:
            result = self._adapter.upsert(
                self._resource_type,
                receipt_id,
                payload,
                idempotency_key=key,
                expected_revision=0,
            )
        except StoreValidationError as exc:
            raise ReceiptValidationError(str(exc)) from exc
        return ReceiptCaptureResult(
            receipt=_view(result.record, idempotent_replay=result.idempotent_replay),
            outcome="replay" if result.idempotent_replay else "created",
        )

    def get(self, receipt_id: str) -> ReceiptView:
        normalized_id = _receipt_id(receipt_id)
        try:
            return _view(self._adapter.get(self._resource_type, normalized_id))
        except NotFoundError as exc:
            raise ReceiptValidationError(f"receipt {normalized_id!r} does not exist") from exc
        except StoreValidationError as exc:
            raise ReceiptValidationError(str(exc)) from exc

    def correct(
        self,
        receipt_id: str,
        *,
        idempotency_key: str,
        merchant: str | object = _UNSET,
        purchase_date: str | object = _UNSET,
        currency: str | object = _UNSET,
        total_minor: int | object = _UNSET,
        order_number: str | None | object = _UNSET,
        subtotal_minor: int | None | object = _UNSET,
        tax_minor: int | None | object = _UNSET,
        shipping_minor: int | None | object = _UNSET,
        discount_minor: int | None | object = _UNSET,
        lines: Sequence[Mapping[str, Any]] | object = _UNSET,
        state: str | object = _UNSET,
        user_note: str | None | object = _UNSET,
    ) -> ReceiptView:
        """Explicitly correct facts while preserving the stable receipt identity."""

        current = self.get(receipt_id)
        normalized = _normalize_receipt(
            merchant=current.merchant if merchant is _UNSET else merchant,
            purchase_date=current.purchase_date if purchase_date is _UNSET else purchase_date,
            currency=current.currency if currency is _UNSET else currency,
            total_minor=current.total_minor if total_minor is _UNSET else total_minor,
            order_number=current.order_number if order_number is _UNSET else order_number,
            subtotal_minor=current.subtotal_minor if subtotal_minor is _UNSET else subtotal_minor,
            tax_minor=current.tax_minor if tax_minor is _UNSET else tax_minor,
            shipping_minor=current.shipping_minor if shipping_minor is _UNSET else shipping_minor,
            discount_minor=current.discount_minor if discount_minor is _UNSET else discount_minor,
            lines=(
                [line.semantic_payload() for line in current.lines]
                if lines is _UNSET
                else lines
            ),
            state=current.state if state is _UNSET else state,
            user_note=current.user_note if user_note is _UNSET else user_note,
        )
        payload = _receipt_payload(current.receipt_id, normalized, current.evidence)
        try:
            result = self._adapter.upsert(
                self._resource_type,
                current.receipt_id,
                payload,
                idempotency_key=_idempotency_key(idempotency_key),
                expected_revision=current.revision,
            )
        except StoreValidationError as exc:
            raise ReceiptValidationError(str(exc)) from exc
        return _view(result.record, idempotent_replay=result.idempotent_replay)

    def history(
        self,
        *,
        receipt_id: str | None = None,
        merchant: str | None = None,
        order_number: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        limit: int = 100,
    ) -> tuple[ReceiptView, ...]:
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 1000:
            raise ReceiptValidationError("limit must be an integer from 1 through 1000")
        start = None if start_date is None else _purchase_date(start_date)
        end = None if end_date is None else _purchase_date(end_date)
        if start is not None and end is not None and start > end:
            raise ReceiptValidationError("start_date must not be after end_date")
        merchant_key = None if merchant is None else _merchant(merchant)[1]
        order_key = None if order_number is None else _order_number(order_number)[1]
        wanted_id = None if receipt_id is None else _receipt_id(receipt_id)

        rows = self._all_views()
        filtered: list[ReceiptView] = []
        for row in rows:
            if wanted_id is not None and row.receipt_id != wanted_id:
                continue
            if merchant_key is not None and merchant_key not in row.merchant_key:
                continue
            if order_key is not None:
                if row.order_number is None or _order_number(row.order_number)[1] != order_key:
                    continue
            if start is not None and row.purchase_date < start:
                continue
            if end is not None and row.purchase_date > end:
                continue
            filtered.append(row)
        filtered.sort(
            key=lambda item: (-date.fromisoformat(item.purchase_date).toordinal(), item.receipt_id)
        )
        return tuple(filtered[:limit])

    def _merge_evidence(
        self,
        current: ReceiptView,
        incoming: _NormalizedReceipt,
        observation: ReceiptEvidence,
        *,
        idempotency_key: str,
    ) -> ReceiptView:
        merged = _merge_compatible_facts(current, incoming)
        evidence = tuple(
            sorted((*current.evidence, observation), key=lambda item: item.source_fingerprint)
        )
        payload = _receipt_payload(current.receipt_id, merged, evidence)
        try:
            result = self._adapter.upsert(
                self._resource_type,
                current.receipt_id,
                payload,
                idempotency_key=idempotency_key,
                expected_revision=current.revision,
            )
        except StoreValidationError as exc:
            raise ReceiptValidationError(str(exc)) from exc
        return _view(result.record, idempotent_replay=result.idempotent_replay)

    def _all_views(self) -> tuple[ReceiptView, ...]:
        try:
            records = self._adapter.query(self._resource_type, limit=1000)
        except StoreValidationError as exc:
            raise ReceiptValidationError(str(exc)) from exc
        return tuple(_view(record) for record in records)


def _correlation_candidates(
    receipts: Sequence[ReceiptView], incoming: _NormalizedReceipt
) -> list[ReceiptView]:
    if incoming.order_key is not None:
        return [
            receipt
            for receipt in receipts
            if receipt.merchant_key == incoming.merchant_key
            and receipt.order_number is not None
            and _order_number(receipt.order_number)[1] == incoming.order_key
        ]
    key = incoming.core_match_key()
    return [
        receipt
        for receipt in receipts
        if (
            receipt.merchant_key,
            receipt.purchase_date,
            receipt.currency,
            receipt.total_minor,
        )
        == key
    ]


def _assert_evidence_compatible(current: ReceiptView, incoming: _NormalizedReceipt) -> None:
    _merge_compatible_facts(current, incoming)


def _merge_compatible_facts(
    current: ReceiptView, incoming: _NormalizedReceipt
) -> _NormalizedReceipt:
    if current.merchant_key != incoming.merchant_key:
        raise ReceiptConflictError("receipt evidence conflicts on merchant")
    if current.purchase_date != incoming.purchase_date:
        raise ReceiptConflictError("receipt evidence conflicts on purchase_date")
    if current.currency != incoming.currency:
        raise ReceiptConflictError("receipt evidence conflicts on currency")
    if current.total_minor != incoming.total_minor:
        raise ReceiptConflictError("receipt evidence conflicts on total_minor")

    current_order_key = (
        None if current.order_number is None else _order_number(current.order_number)[1]
    )
    if (
        current_order_key is not None
        and incoming.order_key is not None
        and current_order_key != incoming.order_key
    ):
        raise ReceiptConflictError("receipt evidence conflicts on order_number")
    order_number = current.order_number or incoming.order_number

    subtotal = _merge_optional_money(
        current.subtotal_minor, incoming.subtotal_minor, "subtotal_minor"
    )
    tax = _merge_optional_money(current.tax_minor, incoming.tax_minor, "tax_minor")
    shipping = _merge_optional_money(
        current.shipping_minor, incoming.shipping_minor, "shipping_minor"
    )
    discount = _merge_optional_money(
        current.discount_minor, incoming.discount_minor, "discount_minor"
    )

    current_semantic = [line.semantic_payload() for line in current.lines]
    incoming_semantic = [line.semantic_payload() for line in incoming.lines]
    if current_semantic and incoming_semantic and current_semantic != incoming_semantic:
        raise ReceiptConflictError("receipt evidence conflicts on line items")
    lines = current.lines or incoming.lines

    if current.state != incoming.state:
        # Evidence capture may not silently change review state. Use explicit
        # correction/review action for that transition.
        raise ReceiptConflictError("receipt evidence conflicts on receipt state")
    if (
        current.user_note is not None
        and incoming.user_note is not None
        and current.user_note != incoming.user_note
    ):
        raise ReceiptConflictError("receipt evidence conflicts on user note")
    user_note = current.user_note or incoming.user_note

    return _NormalizedReceipt(
        merchant=current.merchant,
        merchant_key=current.merchant_key,
        order_number=order_number,
        order_key=None if order_number is None else _order_number(order_number)[1],
        purchase_date=current.purchase_date,
        currency=current.currency,
        total_minor=current.total_minor,
        subtotal_minor=subtotal,
        tax_minor=tax,
        shipping_minor=shipping,
        discount_minor=discount,
        lines=tuple(lines),
        state=current.state,
        user_note=user_note,
    )


def _merge_optional_money(current: int | None, incoming: int | None, field: str) -> int | None:
    if current is not None and incoming is not None and current != incoming:
        raise ReceiptConflictError(f"receipt evidence conflicts on {field}")
    return current if current is not None else incoming


def _normalize_receipt(
    *,
    merchant: Any,
    purchase_date: Any,
    currency: Any,
    total_minor: Any,
    order_number: Any,
    subtotal_minor: Any,
    tax_minor: Any,
    shipping_minor: Any,
    discount_minor: Any,
    lines: Sequence[Mapping[str, Any]],
    state: Any,
    user_note: Any,
) -> _NormalizedReceipt:
    merchant_display, merchant_key = _merchant(merchant)
    order_display, order_key = _order_number(order_number)
    normalized_currency = _currency(currency)
    normalized_lines = _lines(lines)
    normalized_state = _state(state)
    return _NormalizedReceipt(
        merchant=merchant_display,
        merchant_key=merchant_key,
        order_number=order_display,
        order_key=order_key,
        purchase_date=_purchase_date(purchase_date),
        currency=normalized_currency,
        total_minor=_money(total_minor, "total_minor", required=True),
        subtotal_minor=_money(subtotal_minor, "subtotal_minor"),
        tax_minor=_money(tax_minor, "tax_minor"),
        shipping_minor=_money(shipping_minor, "shipping_minor"),
        discount_minor=_money(discount_minor, "discount_minor"),
        lines=normalized_lines,
        state=normalized_state,
        user_note=_optional_text(user_note, "user_note", 4000),
    )


def _receipt_payload(
    receipt_id: str,
    facts: _NormalizedReceipt,
    evidence: Sequence[ReceiptEvidence],
) -> dict[str, Any]:
    return {
        "schema_version": RECEIPT_SCHEMA_VERSION,
        "receipt_id": receipt_id,
        **facts.facts_payload(),
        "evidence": [item.payload() for item in sorted(evidence, key=lambda item: item.source_fingerprint)],
    }


def _view(record: ResourceRecord, *, idempotent_replay: bool = False) -> ReceiptView:
    payload = deepcopy(record.payload)
    if payload.get("schema_version") != RECEIPT_SCHEMA_VERSION:
        raise ReceiptValidationError("unsupported receipt schema version")
    receipt_id = _receipt_id(payload.get("receipt_id"))
    if receipt_id != record.resource_id:
        raise ReceiptValidationError("receipt identity/readback mismatch")
    facts = _normalize_receipt(
        merchant=payload.get("merchant"),
        purchase_date=payload.get("purchase_date"),
        currency=payload.get("currency"),
        total_minor=payload.get("total_minor"),
        order_number=payload.get("order_number"),
        subtotal_minor=payload.get("subtotal_minor"),
        tax_minor=payload.get("tax_minor"),
        shipping_minor=payload.get("shipping_minor"),
        discount_minor=payload.get("discount_minor"),
        lines=payload.get("lines") if isinstance(payload.get("lines"), list) else (),
        state=payload.get("state"),
        user_note=payload.get("user_note"),
    )
    if payload.get("merchant_key") != facts.merchant_key:
        raise ReceiptValidationError("stored merchant_key does not match normalized merchant")
    raw_evidence = payload.get("evidence")
    if not isinstance(raw_evidence, list) or not raw_evidence:
        raise ReceiptValidationError("receipt must contain at least one evidence observation")
    evidence = tuple(
        _evidence(
            source_type=item.get("source_type") if isinstance(item, Mapping) else None,
            source_fingerprint=(
                item.get("source_fingerprint") if isinstance(item, Mapping) else None
            ),
            source_ref=item.get("source_ref") if isinstance(item, Mapping) else None,
            observed_at=item.get("observed_at") if isinstance(item, Mapping) else None,
        )
        for item in raw_evidence
    )
    fingerprints = [item.source_fingerprint for item in evidence]
    if len(fingerprints) != len(set(fingerprints)):
        raise ReceiptValidationError("receipt evidence contains duplicate fingerprints")
    if fingerprints != sorted(fingerprints):
        raise ReceiptValidationError("receipt evidence must be sorted by fingerprint")
    return ReceiptView(
        receipt_id=receipt_id,
        revision=record.revision,
        merchant=facts.merchant,
        merchant_key=facts.merchant_key,
        order_number=facts.order_number,
        purchase_date=facts.purchase_date,
        currency=facts.currency,
        total_minor=facts.total_minor,
        subtotal_minor=facts.subtotal_minor,
        tax_minor=facts.tax_minor,
        shipping_minor=facts.shipping_minor,
        discount_minor=facts.discount_minor,
        lines=facts.lines,
        state=facts.state,
        evidence=evidence,
        user_note=facts.user_note,
        idempotent_replay=idempotent_replay,
    )


def _initial_receipt_id(facts: _NormalizedReceipt, source_fingerprint: str) -> str:
    material = {
        "merchant_key": facts.merchant_key,
        "order_key": facts.order_key,
        "purchase_date": facts.purchase_date,
        "currency": facts.currency,
        "total_minor": facts.total_minor,
        "source_fingerprint": source_fingerprint,
    }
    digest = hashlib.sha256(_canonical_json(material)).hexdigest()
    return f"receipt-{digest[:24]}"


def _lines(values: Sequence[Mapping[str, Any]]) -> tuple[ReceiptLine, ...]:
    if isinstance(values, (str, bytes)) or not isinstance(values, Sequence):
        raise ReceiptValidationError("lines must be a sequence of mappings")
    output: list[ReceiptLine] = []
    occurrences: dict[str, int] = {}
    for item in values:
        if not isinstance(item, Mapping):
            raise ReceiptValidationError("each receipt line must be a mapping")
        semantic = {
            "description": _required_text(item.get("description"), "line.description", 1000),
            "quantity": _quantity(item.get("quantity", "1")),
            "unit_price_minor": _money(item.get("unit_price_minor"), "line.unit_price_minor"),
            "line_total_minor": _money(item.get("line_total_minor"), "line.line_total_minor"),
        }
        base = hashlib.sha256(_canonical_json(semantic)).hexdigest()
        occurrence = occurrences.get(base, 0) + 1
        occurrences[base] = occurrence
        line_digest = hashlib.sha256(
            _canonical_json({"base": base, "occurrence": occurrence})
        ).hexdigest()
        output.append(
            ReceiptLine(
                line_id=f"line-{line_digest[:16]}",
                description=semantic["description"],
                quantity=semantic["quantity"],
                unit_price_minor=semantic["unit_price_minor"],
                line_total_minor=semantic["line_total_minor"],
            )
        )
    return tuple(output)


def _evidence(
    *,
    source_type: Any,
    source_fingerprint: Any,
    source_ref: Any,
    observed_at: Any,
) -> ReceiptEvidence:
    if not isinstance(source_type, str) or source_type.strip().lower() not in RECEIPT_SOURCE_TYPES:
        raise ReceiptValidationError("source_type must be email, image, or text")
    source = source_type.strip().lower()
    if not isinstance(source_fingerprint, str) or not _SHA256_RE.fullmatch(source_fingerprint):
        raise ReceiptValidationError("source_fingerprint must be lowercase SHA-256 hex")
    return ReceiptEvidence(
        source_type=source,
        source_fingerprint=source_fingerprint,
        source_ref=_optional_text(source_ref, "source_ref", 2000),
        observed_at=_timestamp(observed_at, "observed_at"),
    )


def _merchant(value: Any) -> tuple[str, str]:
    display = _required_text(value, "merchant", 500)
    display = _WS_RE.sub(" ", display)
    return display, display.casefold()


def _order_number(value: Any) -> tuple[str | None, str | None]:
    if value is None:
        return None, None
    display = _required_text(value, "order_number", 256)
    display = _WS_RE.sub(" ", display)
    return display, display.casefold()


def _currency(value: Any) -> str:
    if not isinstance(value, str):
        raise ReceiptValidationError("currency must be three-letter text")
    normalized = value.strip().upper()
    if not _CURRENCY_RE.fullmatch(normalized):
        raise ReceiptValidationError("currency must be exactly three ASCII letters")
    return normalized


def _money(value: Any, field: str, *, required: bool = False) -> int | None:
    if value is None and not required:
        return None
    if not isinstance(value, int) or isinstance(value, bool):
        raise ReceiptValidationError(f"{field} must be integer minor units")
    if value < 0:
        raise ReceiptValidationError(f"{field} must be non-negative")
    return value


def _quantity(value: Any) -> str:
    if isinstance(value, bool) or isinstance(value, float) or not isinstance(value, (str, int)):
        raise ReceiptValidationError("line.quantity must be a decimal string or integer, never float")
    text = str(value).strip()
    if not text:
        raise ReceiptValidationError("line.quantity must not be blank")
    try:
        number = Decimal(text)
    except InvalidOperation as exc:
        raise ReceiptValidationError("line.quantity must be a finite decimal") from exc
    if not number.is_finite() or number < 0:
        raise ReceiptValidationError("line.quantity must be finite and non-negative")
    if number == 0:
        return "0"
    normalized = format(number.normalize(), "f")
    return normalized.rstrip("0").rstrip(".") if "." in normalized else normalized


def _state(value: Any) -> str:
    if not isinstance(value, str) or value.strip().lower() not in RECEIPT_STATES:
        raise ReceiptValidationError("receipt state must be captured or needs_review")
    return value.strip().lower()


def _purchase_date(value: Any) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise ReceiptValidationError("purchase_date must be YYYY-MM-DD")
    try:
        return date.fromisoformat(value).isoformat()
    except ValueError as exc:
        raise ReceiptValidationError("purchase_date must be YYYY-MM-DD") from exc


def _timestamp(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise ReceiptValidationError(f"{field} must be an offset-aware ISO-8601 timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ReceiptValidationError(f"{field} must be an offset-aware ISO-8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ReceiptValidationError(f"{field} must include a UTC offset")
    return parsed.isoformat()


def _required_text(value: Any, field: str, max_length: int) -> str:
    if not isinstance(value, str):
        raise ReceiptValidationError(f"{field} must be text")
    normalized = value.strip()
    if not normalized:
        raise ReceiptValidationError(f"{field} must not be blank")
    if len(normalized) > max_length:
        raise ReceiptValidationError(f"{field} must be at most {max_length} characters")
    return normalized


def _optional_text(value: Any, field: str, max_length: int) -> str | None:
    if value is None:
        return None
    return _required_text(value, field, max_length)


def _idempotency_key(value: Any) -> str:
    return _required_text(value, "idempotency_key", 128)


def _receipt_id(value: Any) -> str:
    if not isinstance(value, str) or not _RECEIPT_ID_RE.fullmatch(value):
        raise ReceiptValidationError("receipt_id is not a canonical MIRA receipt ID")
    return value


def _canonical_json(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


__all__ = [
    "RECEIPT_RESOURCE_TYPE",
    "RECEIPT_SCHEMA_VERSION",
    "RECEIPT_SOURCE_TYPES",
    "RECEIPT_STATES",
    "ReceiptAmbiguityError",
    "ReceiptCaptureResult",
    "ReceiptConflictError",
    "ReceiptError",
    "ReceiptEvidence",
    "ReceiptIntegrityError",
    "ReceiptLine",
    "ReceiptService",
    "ReceiptValidationError",
    "ReceiptView",
]
