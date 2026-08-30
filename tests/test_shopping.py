from __future__ import annotations

import hashlib
import unittest

from mira.receipts import ReceiptService
from mira.shopping import (
    SHOPPING_INTENT_RESOURCE_TYPE,
    ShoppingIntentConflictError,
    ShoppingIntentIntegrityError,
    ShoppingIntentService,
    ShoppingIntentTransitionError,
    ShoppingIntentValidationError,
)
from mira.structured_state import InMemoryStructuredStateAdapter, ResourceRecord


def fp(label: str) -> str:
    return hashlib.sha256(label.encode("utf-8")).hexdigest()


class ShoppingIntentServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.adapter = InMemoryStructuredStateAdapter(
            schema_version="mira-test-v1",
            resource_types=["receipt", SHOPPING_INTENT_RESOURCE_TYPE],
            event_types=["created", "updated"],
        )
        self.receipts = ReceiptService(self.adapter)
        self.shopping = ShoppingIntentService(
            self.adapter, receipt_service=self.receipts
        )
        captured = self.receipts.capture(
            merchant="Synthetic Supply",
            purchase_date="2026-08-30",
            currency="USD",
            total_minor=12500,
            lines=[
                {
                    "description": "Torque wrench",
                    "quantity": "1",
                    "unit_price_minor": 10000,
                    "line_total_minor": 10000,
                },
                {
                    "description": "Socket set",
                    "quantity": "1",
                    "unit_price_minor": 2500,
                    "line_total_minor": 2500,
                },
            ],
            state="captured",
            source_type="text",
            source_fingerprint=fp("captured"),
            observed_at="2026-08-30T08:00:00-04:00",
            idempotency_key="receipt-captured",
        ).receipt
        self.receipt = captured
        self.receipt_line_id = captured.lines[0].line_id
        self.review_receipt = self.receipts.capture(
            merchant="Synthetic Review Supply",
            purchase_date="2026-08-30",
            currency="USD",
            total_minor=999,
            state="needs_review",
            source_type="text",
            source_fingerprint=fp("review"),
            observed_at="2026-08-30T08:05:00-04:00",
            idempotency_key="receipt-review",
        ).receipt

    def create(self, intent_id: str = "shop-001", **overrides):
        values = {
            "description": "Torque wrench",
            "quantity": "1",
            "unit": "each",
            "note": "Buy before next service",
            "created_at": "2026-08-30T09:00:00-04:00",
            "idempotency_key": f"create-{intent_id}",
        }
        values.update(overrides)
        return self.shopping.create(intent_id, **values)

    def test_create_read_and_exact_create_replay(self) -> None:
        first = self.create()
        replay = self.create()
        self.assertEqual(first.intent_id, "shop-001")
        self.assertEqual(first.revision, 1)
        self.assertEqual(first.description, "Torque wrench")
        self.assertEqual(first.search_text, "torque wrench")
        self.assertEqual(first.quantity, "1")
        self.assertEqual(first.state, "active")
        self.assertIsNone(first.reconciliation)
        self.assertTrue(replay.idempotent_replay)
        self.assertEqual(replay.revision, 1)

    def test_create_conflicting_idempotency_material_fails(self) -> None:
        self.create()
        with self.assertRaises(ShoppingIntentConflictError):
            self.create(description="Different item")
        self.assertEqual(self.shopping.get("shop-001").description, "Torque wrench")

    def test_active_update_is_revisioned_and_exact_semantic_replay_is_zero_write(self) -> None:
        self.create()
        updated = self.shopping.update(
            "shop-001",
            description="3/8 torque wrench",
            quantity="1.0",
            updated_at="2026-08-30T10:00:00-04:00",
            idempotency_key="update-shop-001",
        )
        self.assertEqual(updated.revision, 2)
        self.assertEqual(updated.description, "3/8 torque wrench")
        self.assertEqual(updated.quantity, "1")
        replay = self.shopping.update(
            "shop-001",
            description="3/8 torque wrench",
            quantity="1",
            updated_at="2026-08-30T10:00:00-04:00",
            idempotency_key="update-shop-001",
        )
        self.assertTrue(replay.idempotent_replay)
        self.assertEqual(replay.revision, 2)

    def test_query_filters_and_orders_deterministically_before_limit(self) -> None:
        self.create("shop-b", description="Brake fluid", created_at="2026-08-30T09:01:00-04:00")
        self.create("shop-a", description="Brake pads", created_at="2026-08-30T09:00:00-04:00")
        self.create("shop-c", description="Oil filter", created_at="2026-08-30T09:02:00-04:00")
        self.shopping.cancel(
            "shop-b",
            cancelled_at="2026-08-30T10:00:00-04:00",
            idempotency_key="cancel-shop-b",
        )
        active = self.shopping.query(state="active")
        self.assertEqual([row.intent_id for row in active], ["shop-a", "shop-c"])
        brake = self.shopping.query(description="BRAKE")
        self.assertEqual([row.intent_id for row in brake], ["shop-a", "shop-b"])
        self.assertEqual(self.shopping.query(intent_id="shop-c")[0].description, "Oil filter")
        self.assertEqual([row.intent_id for row in self.shopping.query(limit=2)], ["shop-a", "shop-c"])

    def test_receipt_existence_never_auto_fulfills_active_intent(self) -> None:
        intent = self.create()
        self.assertEqual(intent.state, "active")
        self.assertEqual(self.shopping.get("shop-001").state, "active")
        self.assertIsNone(self.shopping.get("shop-001").reconciliation)

    def test_explicit_line_fulfillment_records_receipt_provenance_only(self) -> None:
        self.create()
        receipt_before = self.receipts.get(self.receipt.receipt_id)
        fulfilled = self.shopping.fulfill_from_receipt(
            "shop-001",
            receipt_id=self.receipt.receipt_id,
            receipt_line_id=self.receipt_line_id,
            reconciled_at="2026-08-30T11:00:00-04:00",
            idempotency_key="fulfill-shop-001",
        )
        receipt_after = self.receipts.get(self.receipt.receipt_id)
        self.assertEqual(fulfilled.state, "fulfilled")
        self.assertEqual(fulfilled.revision, 2)
        self.assertEqual(fulfilled.fulfilled_at, "2026-08-30T11:00:00-04:00")
        self.assertIsNotNone(fulfilled.reconciliation)
        self.assertEqual(fulfilled.reconciliation.receipt_id, self.receipt.receipt_id)
        self.assertEqual(fulfilled.reconciliation.receipt_line_id, self.receipt_line_id)
        self.assertEqual(fulfilled.reconciliation.receipt_revision, receipt_before.revision)
        self.assertEqual(receipt_before, receipt_after)
        self.assertEqual(
            tuple(self.adapter.query(SHOPPING_INTENT_RESOURCE_TYPE, limit=100))[0].revision,
            2,
        )

    def test_receipt_level_fulfillment_is_supported_when_explicit(self) -> None:
        self.create()
        fulfilled = self.shopping.fulfill_from_receipt(
            "shop-001",
            receipt_id=self.receipt.receipt_id,
            reconciled_at="2026-08-30T11:00:00-04:00",
            idempotency_key="fulfill-shop-001",
        )
        self.assertIsNone(fulfilled.reconciliation.receipt_line_id)

    def test_fulfillment_requires_captured_receipt_and_exact_line(self) -> None:
        self.create()
        with self.assertRaises(ShoppingIntentValidationError):
            self.shopping.fulfill_from_receipt(
                "shop-001",
                receipt_id=self.review_receipt.receipt_id,
                reconciled_at="2026-08-30T11:00:00-04:00",
                idempotency_key="fulfill-review",
            )
        with self.assertRaises(ShoppingIntentValidationError):
            self.shopping.fulfill_from_receipt(
                "shop-001",
                receipt_id=self.receipt.receipt_id,
                receipt_line_id="line-does-not-exist",
                reconciled_at="2026-08-30T11:00:00-04:00",
                idempotency_key="fulfill-missing-line",
            )
        with self.assertRaises(ShoppingIntentValidationError):
            self.shopping.fulfill_from_receipt(
                "shop-001",
                receipt_id="receipt-does-not-exist",
                reconciled_at="2026-08-30T11:00:00-04:00",
                idempotency_key="fulfill-missing-receipt",
            )
        self.assertEqual(self.shopping.get("shop-001").state, "active")

    def test_cancellation_is_not_fulfillment_and_terminal_states_do_not_reopen(self) -> None:
        self.create()
        cancelled = self.shopping.cancel(
            "shop-001",
            cancelled_at="2026-08-30T11:00:00-04:00",
            idempotency_key="cancel-shop-001",
        )
        self.assertEqual(cancelled.state, "cancelled")
        self.assertIsNone(cancelled.fulfilled_at)
        self.assertIsNone(cancelled.reconciliation)
        with self.assertRaises(ShoppingIntentTransitionError):
            self.shopping.fulfill_from_receipt(
                "shop-001",
                receipt_id=self.receipt.receipt_id,
                reconciled_at="2026-08-30T12:00:00-04:00",
                idempotency_key="fulfill-cancelled",
            )
        with self.assertRaises(ShoppingIntentTransitionError):
            self.shopping.update(
                "shop-001",
                description="Reopened behind our backs",
                updated_at="2026-08-30T12:00:00-04:00",
                idempotency_key="update-cancelled",
            )

    def test_fulfillment_replay_is_zero_write_and_conflicting_reconciliation_fails(self) -> None:
        self.create()
        first = self.shopping.fulfill_from_receipt(
            "shop-001",
            receipt_id=self.receipt.receipt_id,
            receipt_line_id=self.receipt_line_id,
            reconciled_at="2026-08-30T11:00:00-04:00",
            idempotency_key="fulfill-shop-001",
        )
        replay = self.shopping.fulfill_from_receipt(
            "shop-001",
            receipt_id=self.receipt.receipt_id,
            receipt_line_id=self.receipt_line_id,
            reconciled_at="2026-08-30T11:00:00-04:00",
            idempotency_key="fulfill-shop-001",
        )
        self.assertEqual(first.revision, 2)
        self.assertTrue(replay.idempotent_replay)
        self.assertEqual(replay.revision, 2)
        with self.assertRaises(ShoppingIntentTransitionError):
            self.shopping.fulfill_from_receipt(
                "shop-001",
                receipt_id=self.receipt.receipt_id,
                receipt_line_id=self.receipt.lines[1].line_id,
                reconciled_at="2026-08-30T11:00:00-04:00",
                idempotency_key="fulfill-shop-001-other",
            )

    def test_receipt_later_revision_does_not_rewrite_historical_reconciliation(self) -> None:
        self.create()
        fulfilled = self.shopping.fulfill_from_receipt(
            "shop-001",
            receipt_id=self.receipt.receipt_id,
            receipt_line_id=self.receipt_line_id,
            reconciled_at="2026-08-30T11:00:00-04:00",
            idempotency_key="fulfill-shop-001",
        )
        observed_revision = fulfilled.reconciliation.receipt_revision
        corrected = self.receipts.correct(
            self.receipt.receipt_id,
            user_note="Later receipt note",
            idempotency_key="receipt-correction",
        )
        self.assertGreater(corrected.revision, observed_revision)
        reread = self.shopping.get("shop-001")
        self.assertEqual(reread.reconciliation.receipt_revision, observed_revision)

    def test_timestamp_quantity_and_query_validation_fail_closed(self) -> None:
        with self.assertRaises(ShoppingIntentValidationError):
            self.create(quantity=0)
        with self.assertRaises(ShoppingIntentValidationError):
            self.create(created_at="2026-08-30T09:00:00")
        self.create()
        with self.assertRaises(ShoppingIntentTransitionError):
            self.shopping.cancel(
                "shop-001",
                cancelled_at="2026-08-30T09:00:00-04:00",
                idempotency_key="cancel-not-later",
            )
        with self.assertRaises(ShoppingIntentValidationError):
            self.shopping.query(limit=0)
        with self.assertRaises(ShoppingIntentValidationError):
            self.shopping.query(state="bought-ish")

    def test_corrupt_persisted_identity_fails_integrity(self) -> None:
        self.create()
        self.adapter._records[(SHOPPING_INTENT_RESOURCE_TYPE, "shop-001")] = ResourceRecord(
            resource_type=SHOPPING_INTENT_RESOURCE_TYPE,
            resource_id="shop-001",
            payload={
                **self.adapter._records[(SHOPPING_INTENT_RESOURCE_TYPE, "shop-001")].payload,
                "intent_id": "shop-other",
            },
            revision=1,
        )
        with self.assertRaises(ShoppingIntentIntegrityError):
            self.shopping.get("shop-001")


if __name__ == "__main__":
    unittest.main()
