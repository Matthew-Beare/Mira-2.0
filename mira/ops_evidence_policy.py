"""Fail-closed authority rules for mutable Ops facts and durable purchase ingestion.

This module is intentionally provider-neutral. It decides whether evidence is
strong enough to be presented or committed; provider adapters perform the
actual reads and writes.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class VerificationStatus(str, Enum):
    VERIFIED = "verified"
    USER_REPORTED = "user_reported"
    UNVERIFIED = "unverified"


class AuthoritySource(str, Enum):
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
    """Resolve shipment state without letting secondary evidence impersonate carrier state.

    Once a tracking number exists, the live carrier is canonical for ETA,
    progress, exception, out-for-delivery and delivered state. A user statement
    or vendor email may help identify the shipment, but cannot be promoted to
    live carrier truth merely because it is newer than a cached projection.
    """

    tracking = _clean(tracking_number)
    carrier = _clean(carrier_value)
    user = _clean(user_value)
    vendor = _clean(vendor_value)

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

    A receipt/order email is evidence, not proof that the inventory side effect
    succeeded. Durable non-consumables fail closed until the canonical record is
    linked back to the archived receipt and read back successfully.
    """

    if not isinstance(evidence, DurablePurchaseEvidence):
        raise TypeError("evidence must be DurablePurchaseEvidence")

    if evidence.consumable:
        return AcquisitionResult(
            state=AcquisitionState.NOT_INVENTORIED_CONSUMABLE,
            missing=(),
        )

    missing: list[str] = []
    if not evidence.ownership_confirmed:
        missing.append("ownership_confirmed")
    if not _clean(evidence.receipt_evidence_id):
        missing.append("receipt_evidence_id")
    if not _clean(evidence.archived_receipt_link):
        missing.append("archived_receipt_link")
    if not _clean(evidence.category):
        missing.append("category")
    if not _clean(evidence.canonical_record_id):
        missing.append("canonical_record_id")
    if not _clean(evidence.canonical_record_receipt_link):
        missing.append("canonical_record_receipt_link")
    if (
        _clean(evidence.archived_receipt_link)
        and _clean(evidence.canonical_record_receipt_link)
        and _clean(evidence.archived_receipt_link)
        != _clean(evidence.canonical_record_receipt_link)
    ):
        missing.append("receipt_link_readback_mismatch")
    if not evidence.readback_confirmed:
        missing.append("readback_confirmed")

    return AcquisitionResult(
        state=AcquisitionState.COMMITTED if not missing else AcquisitionState.NEEDS_REVIEW,
        missing=tuple(missing),
    )


def _clean(value: str | None) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise TypeError("text evidence values must be strings or None")
    stripped = value.strip()
    return stripped or None


__all__ = [
    "AcquisitionResult",
    "AcquisitionState",
    "AuthoritySource",
    "DurablePurchaseEvidence",
    "MutableFactResult",
    "VerificationStatus",
    "evaluate_durable_purchase",
    "resolve_shipment_fact",
]
