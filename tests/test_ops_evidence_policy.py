from mira.authority import (
    AcquisitionState,
    AuthoritySource,
    DurablePurchaseEvidence,
    VerificationStatus,
    evaluate_durable_purchase,
    resolve_shipment_fact,
)


def test_tracking_number_requires_live_carrier_even_when_user_supplies_eta() -> None:
    result = resolve_shipment_fact(
        tracking_number="9400000000000000000000",
        carrier_lookup_attempted=False,
        carrier_value=None,
        user_value="Monday",
        vendor_value="Tuesday",
    )
    assert result.status is VerificationStatus.UNVERIFIED
    assert result.authority is AuthoritySource.CARRIER
    assert result.value is None


def test_live_carrier_readback_wins_over_conflicting_user_or_vendor_values() -> None:
    result = resolve_shipment_fact(
        tracking_number="9400000000000000000000",
        carrier_lookup_attempted=True,
        carrier_value="Saturday",
        user_value="Monday",
        vendor_value="Tuesday",
    )
    assert result.status is VerificationStatus.VERIFIED
    assert result.authority is AuthoritySource.CARRIER
    assert result.value == "Saturday"


def test_durable_purchase_does_not_commit_from_receipt_email_alone() -> None:
    result = evaluate_durable_purchase(
        DurablePurchaseEvidence(
            consumable=False,
            ownership_confirmed=True,
            receipt_evidence_id="receipt:synthetic:1",
            archived_receipt_link=None,
            category="Tools",
            canonical_record_id=None,
            canonical_record_receipt_link=None,
            readback_confirmed=False,
        )
    )
    assert result.state is AcquisitionState.NEEDS_REVIEW
    assert "archived_receipt_link" in result.missing
    assert "canonical_record_id" in result.missing
    assert "readback_confirmed" in result.missing


def test_durable_purchase_requires_same_receipt_link_on_canonical_record() -> None:
    result = evaluate_durable_purchase(
        DurablePurchaseEvidence(
            consumable=False,
            ownership_confirmed=True,
            receipt_evidence_id="receipt:synthetic:2",
            archived_receipt_link="https://drive.example/receipt-a",
            category="Electronics",
            canonical_record_id="asset:synthetic:2",
            canonical_record_receipt_link="https://drive.example/receipt-b",
            readback_confirmed=True,
        )
    )
    assert result.state is AcquisitionState.NEEDS_REVIEW
    assert "receipt_link_readback_mismatch" in result.missing


def test_durable_purchase_commits_only_after_full_readback_chain() -> None:
    link = "https://drive.example/receipt-c"
    result = evaluate_durable_purchase(
        DurablePurchaseEvidence(
            consumable=False,
            ownership_confirmed=True,
            receipt_evidence_id="receipt:synthetic:3",
            archived_receipt_link=link,
            category="Tools",
            canonical_record_id="tool:synthetic:3",
            canonical_record_receipt_link=link,
            readback_confirmed=True,
        )
    )
    assert result.state is AcquisitionState.COMMITTED
    assert result.missing == ()


def test_consumable_is_not_forced_into_inventory() -> None:
    result = evaluate_durable_purchase(
        DurablePurchaseEvidence(
            consumable=True,
            ownership_confirmed=True,
            receipt_evidence_id="receipt:synthetic:4",
            archived_receipt_link=None,
            category="Groceries",
            canonical_record_id=None,
            canonical_record_receipt_link=None,
            readback_confirmed=False,
        )
    )
    assert result.state is AcquisitionState.NOT_INVENTORIED_CONSUMABLE
    assert result.missing == ()
