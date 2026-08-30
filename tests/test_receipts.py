from __future__ import annotations

import hashlib
import unittest

from mira.receipts import (
    ReceiptAmbiguityError,
    ReceiptConflictError,
    ReceiptService,
    ReceiptValidationError,
)
from mira.structured_state import InMemoryStructuredStateAdapter


def fp(label: str) -> str:
    return hashlib.sha256(label.encode("utf-8")).hexdigest()


class ReceiptServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.adapter = InMemoryStructuredStateAdapter(
            schema_version="mira-test-v1",
            resource_types=["receipt"],
            event_types=["created"],
        )
        self.receipts = ReceiptService(self.adapter)

    def capture(self, label: str, **overrides):
        material = {
            "merchant": "Example Hardware",
            "purchase_date": "2026-08-29",
            "currency": "USD",
            "total_minor": 2599,
            "source_type": "email",
            "source_fingerprint": fp(label),
            "observed_at": "2026-08-29T14:15:00-04:00",
            "idempotency_key": f"capture-{label}",
        }
        material.update(overrides)
        return self.receipts.capture(**material)

    def test_email_capture_uses_exact_money_and_stable_line_identity(self) -> None:
        result = self.capture(
            "email-1",
            order_number="ORD-100",
            subtotal_minor=2399,
            tax_minor=200,
            lines=[
                {
                    "description": "  Socket set  ",
                    "quantity": "1.00",
                    "unit_price_minor": 2399,
                    "line_total_minor": 2399,
                },
                {
                    "description": "Shop rag",
                    "quantity": 2,
                    "unit_price_minor": 0,
                    "line_total_minor": 0,
                },
            ],
            source_ref="gmail:synthetic-message-1",
        )
        receipt = result.receipt
        self.assertEqual(result.outcome, "created")
        self.assertEqual(receipt.revision, 1)
        self.assertEqual(receipt.currency, "USD")
        self.assertEqual(receipt.total_minor, 2599)
        self.assertEqual(receipt.lines[0].description, "Socket set")
        self.assertEqual(receipt.lines[0].quantity, "1")
        self.assertEqual(receipt.lines[1].quantity, "2")
        self.assertTrue(receipt.lines[0].line_id.startswith("line-"))
        self.assertEqual(receipt.evidence[0].source_type, "email")
        self.assertEqual(receipt.evidence[0].source_ref, "gmail:synthetic-message-1")

        readback = self.receipts.get(receipt.receipt_id)
        self.assertEqual(readback.receipt_id, receipt.receipt_id)
        self.assertEqual(readback.lines, receipt.lines)
        self.assertEqual(readback.total_minor, 2599)

    def test_exact_source_replay_is_zero_write_when_facts_agree(self) -> None:
        first = self.capture("same-source", order_number="A-1")
        replay = self.receipts.capture(
            merchant="Example Hardware",
            purchase_date="2026-08-29",
            currency="usd",
            total_minor=2599,
            order_number="A-1",
            source_type="email",
            source_fingerprint=fp("same-source"),
            observed_at="2026-08-29T14:15:00-04:00",
            idempotency_key="different-logical-key",
        )
        self.assertEqual(replay.outcome, "replay")
        self.assertEqual(replay.receipt.receipt_id, first.receipt.receipt_id)
        self.assertEqual(replay.receipt.revision, 1)
        self.assertEqual(len(replay.receipt.evidence), 1)

    def test_exact_source_conflict_fails_closed(self) -> None:
        self.capture("conflict-source", order_number="A-2")
        with self.assertRaises(ReceiptConflictError):
            self.receipts.capture(
                merchant="Example Hardware",
                purchase_date="2026-08-29",
                currency="USD",
                total_minor=9999,
                order_number="A-2",
                source_type="email",
                source_fingerprint=fp("conflict-source"),
                observed_at="2026-08-29T14:15:00-04:00",
                idempotency_key="conflicting-recapture",
            )
        self.assertEqual(len(self.receipts.history()), 1)
        self.assertEqual(self.receipts.history()[0].total_minor, 2599)

    def test_second_source_merges_into_same_order_and_can_fill_unknown_facts(self) -> None:
        first = self.capture("order-email", order_number=" PO-42 ")
        merged = self.receipts.capture(
            merchant="example hardware",
            purchase_date="2026-08-29",
            currency="USD",
            total_minor=2599,
            order_number="po-42",
            tax_minor=200,
            subtotal_minor=2399,
            lines=[
                {
                    "description": "Socket set",
                    "quantity": "1",
                    "line_total_minor": 2399,
                }
            ],
            source_type="image",
            source_fingerprint=fp("order-image"),
            source_ref="upload:synthetic-receipt-photo",
            observed_at="2026-08-29T15:00:00-04:00",
            idempotency_key="merge-order-image",
        )
        self.assertEqual(merged.outcome, "merged")
        self.assertEqual(merged.receipt.receipt_id, first.receipt.receipt_id)
        self.assertEqual(merged.receipt.revision, 2)
        self.assertEqual(merged.receipt.tax_minor, 200)
        self.assertEqual(merged.receipt.subtotal_minor, 2399)
        self.assertEqual(len(merged.receipt.lines), 1)
        self.assertEqual(
            {item.source_type for item in merged.receipt.evidence}, {"email", "image"}
        )

    def test_matching_order_with_conflicting_facts_does_not_overwrite(self) -> None:
        first = self.capture("order-source-a", order_number="ORD-X")
        with self.assertRaises(ReceiptConflictError):
            self.receipts.capture(
                merchant="Example Hardware",
                purchase_date="2026-08-29",
                currency="USD",
                total_minor=2600,
                order_number="ord-x",
                source_type="image",
                source_fingerprint=fp("order-source-b"),
                observed_at="2026-08-29T15:00:00-04:00",
                idempotency_key="conflicting-order-source",
            )
        current = self.receipts.get(first.receipt.receipt_id)
        self.assertEqual(current.total_minor, 2599)
        self.assertEqual(current.revision, 1)
        self.assertEqual(len(current.evidence), 1)

    def test_same_core_transaction_can_be_explicitly_kept_distinct_and_then_is_ambiguous(self) -> None:
        first = self.capture("same-core-one")
        second = self.capture(
            "same-core-two",
            distinct_transaction=True,
            source_type="text",
            observed_at="2026-08-29T16:00:00-04:00",
        )
        self.assertNotEqual(first.receipt.receipt_id, second.receipt.receipt_id)
        self.assertEqual(len(self.receipts.history()), 2)

        with self.assertRaises(ReceiptAmbiguityError):
            self.capture(
                "same-core-third",
                source_type="image",
                observed_at="2026-08-29T17:00:00-04:00",
            )
        self.assertEqual(len(self.receipts.history()), 2)

    def test_explicit_correction_preserves_receipt_identity_and_evidence(self) -> None:
        first = self.capture("correction", order_number="BAD-1")
        corrected = self.receipts.correct(
            first.receipt.receipt_id,
            merchant="Example Hardware & Supply",
            order_number="GOOD-1",
            total_minor=2699,
            user_note="Corrected from the original source after explicit review.",
            idempotency_key="correct-receipt",
        )
        self.assertEqual(corrected.receipt_id, first.receipt.receipt_id)
        self.assertEqual(corrected.revision, 2)
        self.assertEqual(corrected.merchant, "Example Hardware & Supply")
        self.assertEqual(corrected.order_number, "GOOD-1")
        self.assertEqual(corrected.total_minor, 2699)
        self.assertEqual(corrected.evidence, first.receipt.evidence)

        replay = self.receipts.correct(
            first.receipt.receipt_id,
            merchant="Example Hardware & Supply",
            order_number="GOOD-1",
            total_minor=2699,
            user_note="Corrected from the original source after explicit review.",
            idempotency_key="correct-receipt",
        )
        self.assertTrue(replay.idempotent_replay)
        self.assertEqual(replay.revision, 2)

    def test_history_filters_and_orders_newest_first(self) -> None:
        older = self.capture(
            "older",
            merchant="Alpha Store",
            purchase_date="2026-08-01",
            order_number="A-100",
            total_minor=1000,
        ).receipt
        newer = self.capture(
            "newer",
            merchant="Alpha Store East",
            purchase_date="2026-08-30",
            order_number="A-200",
            total_minor=2000,
        ).receipt
        middle = self.capture(
            "middle",
            merchant="Beta Store",
            purchase_date="2026-08-15",
            order_number="B-100",
            total_minor=3000,
        ).receipt

        self.assertEqual(
            [row.receipt_id for row in self.receipts.history()],
            [newer.receipt_id, middle.receipt_id, older.receipt_id],
        )
        self.assertEqual(
            [row.receipt_id for row in self.receipts.history(merchant="alpha")],
            [newer.receipt_id, older.receipt_id],
        )
        self.assertEqual(
            [row.receipt_id for row in self.receipts.history(order_number="a-100")],
            [older.receipt_id],
        )
        self.assertEqual(
            [
                row.receipt_id
                for row in self.receipts.history(
                    start_date="2026-08-10", end_date="2026-08-20"
                )
            ],
            [middle.receipt_id],
        )
        self.assertEqual(
            [row.receipt_id for row in self.receipts.history(receipt_id=newer.receipt_id)],
            [newer.receipt_id],
        )

    def test_float_money_and_invalid_quantities_are_rejected(self) -> None:
        with self.assertRaises(ReceiptValidationError):
            self.capture("float-money", total_minor=25.99)
        with self.assertRaises(ReceiptValidationError):
            self.capture(
                "float-quantity",
                lines=[{"description": "Thing", "quantity": 1.5}],
            )
        with self.assertRaises(ReceiptValidationError):
            self.capture(
                "negative-quantity",
                lines=[{"description": "Thing", "quantity": "-1"}],
            )
        with self.assertRaises(ReceiptValidationError):
            self.capture(
                "nan-quantity",
                lines=[{"description": "Thing", "quantity": "NaN"}],
            )

    def test_text_source_is_first_class_and_raw_source_content_is_not_required(self) -> None:
        result = self.capture(
            "user-text",
            source_type="text",
            source_ref=None,
            observed_at="2026-08-29T18:00:00-04:00",
            user_note="User stated the purchase details directly.",
        )
        self.assertEqual(result.receipt.evidence[0].source_type, "text")
        payload = self.adapter.get("receipt", result.receipt.receipt_id).payload
        self.assertNotIn("raw_email", payload)
        self.assertNotIn("raw_image", payload)
        self.assertNotIn("raw_text", payload)


if __name__ == "__main__":
    unittest.main()
