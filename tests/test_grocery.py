from __future__ import annotations

from copy import deepcopy
import hashlib
import unittest

from mira.assets import AssetService
from mira.grocery import (
    GroceryReconciliationService,
    GroceryReconciliationValidationError,
)
from mira.inventory_location import InventoryLocationService
from mira.inventory_query import InventoryQueryService
from mira.receipts import ReceiptService
from mira.shopping import ShoppingIntentService
from mira.structured_state import InMemoryStructuredStateAdapter


MILK = "11111111-1111-4111-8111-111111111111"
PEAS = "22222222-2222-4222-8222-222222222222"
SAUCE_A = "33333333-3333-4333-8333-333333333333"
SAUCE_B = "44444444-4444-4444-8444-444444444444"
PAPER = "55555555-5555-4555-8555-555555555555"
OATS = "66666666-6666-4666-8666-666666666666"
RICE = "77777777-7777-4777-8777-777777777777"


def fp(label: str) -> str:
    return hashlib.sha256(label.encode("utf-8")).hexdigest()


class GroceryReconciliationServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.adapter = InMemoryStructuredStateAdapter(
            schema_version="mira-test-v1",
            resource_types=[
                "receipt",
                "asset",
                "identifier",
                "location",
                "inventory_state",
                "shopping_intent",
            ],
            event_types=["created", "updated"],
        )
        self.receipts = ReceiptService(self.adapter)
        self.assets = AssetService(self.adapter, receipt_service=self.receipts)
        self.inventory = InventoryLocationService(
            self.adapter, asset_service=self.assets
        )
        self.inventory_query = InventoryQueryService(
            self.adapter,
            asset_service=self.assets,
            inventory_location_service=self.inventory,
        )
        self.shopping = ShoppingIntentService(
            self.adapter, receipt_service=self.receipts
        )
        self.grocery = GroceryReconciliationService(
            self.adapter,
            shopping_service=self.shopping,
            inventory_query_service=self.inventory_query,
        )

        self.site = self.inventory.create_location(
            location_id="loc-site",
            display_name="Synthetic Home",
            kind="site",
            idempotency_key="loc-site",
        )
        self.kitchen = self.inventory.create_location(
            location_id="loc-kitchen",
            display_name="Kitchen",
            kind="room",
            parent_location_id=self.site.location_id,
            idempotency_key="loc-kitchen",
        )
        self.pantry = self.inventory.create_location(
            location_id="loc-pantry",
            display_name="Pantry",
            kind="zone",
            parent_location_id=self.kitchen.location_id,
            idempotency_key="loc-pantry",
        )
        self.freezer = self.inventory.create_location(
            location_id="loc-freezer",
            display_name="Freezer",
            kind="container",
            parent_location_id=self.kitchen.location_id,
            idempotency_key="loc-freezer",
        )
        self.garage = self.inventory.create_location(
            location_id="loc-garage",
            display_name="Garage",
            kind="room",
            parent_location_id=self.site.location_id,
            idempotency_key="loc-garage",
        )

        self.milk = self._asset(
            entity_uuid=MILK,
            label="milk",
            display_name="Whole Milk",
            quantity=12,
            tracking_mode="lot",
        )
        self.peas = self._asset(
            entity_uuid=PEAS,
            label="peas",
            display_name="Frozen Peas",
        )
        self.sauce_a = self._asset(
            entity_uuid=SAUCE_A,
            label="sauce-a",
            display_name="Tomato Sauce",
        )
        self.sauce_b = self._asset(
            entity_uuid=SAUCE_B,
            label="sauce-b",
            display_name="Tomato Sauce",
        )
        self.paper = self._asset(
            entity_uuid=PAPER,
            label="paper",
            display_name="Paper Towels",
        )
        self.oats = self._asset(
            entity_uuid=OATS,
            label="oats",
            display_name="Oatmeal",
        )
        self.rice = self._asset(
            entity_uuid=RICE,
            label="rice",
            display_name="Rice",
        )

        self._track_observed(self.milk.entity_uuid, self.pantry.location_id, "milk")
        self._track_observed(self.peas.entity_uuid, self.freezer.location_id, "peas")
        self._track_observed(self.sauce_a.entity_uuid, self.pantry.location_id, "sauce-a")
        self._track_observed(self.sauce_b.entity_uuid, self.pantry.location_id, "sauce-b")
        self._track_observed(self.paper.entity_uuid, self.garage.location_id, "paper")
        self.inventory.track_asset(
            self.oats.entity_uuid,
            intended_location_id=self.pantry.location_id,
            idempotency_key="track-oats",
        )
        # Rice has durable purchase + asset history but is intentionally untracked.

    def _asset(
        self,
        *,
        entity_uuid: str,
        label: str,
        display_name: str,
        quantity: int = 1,
        tracking_mode: str = "individual",
    ):
        receipt = self.receipts.capture(
            merchant="Synthetic Grocery Supply",
            purchase_date="2026-08-30",
            currency="USD",
            total_minor=500 * quantity,
            order_number=f"ORDER-{label.upper()}",
            lines=[
                {
                    "description": display_name,
                    "quantity": str(quantity),
                    "unit_price_minor": 500,
                    "line_total_minor": 500 * quantity,
                }
            ],
            state="captured",
            source_type="text",
            source_fingerprint=fp(label),
            observed_at="2026-08-30T08:00:00-04:00",
            idempotency_key=f"receipt-{label}",
        ).receipt
        return self.assets.acquire(
            receipt_id=receipt.receipt_id,
            receipt_line_id=receipt.lines[0].line_id,
            acquisition_key="lot-1" if tracking_mode == "lot" else "unit-1",
            display_name=display_name,
            tracking_mode=tracking_mode,
            quantity=quantity,
            entity_uuid=entity_uuid,
            idempotency_key=f"asset-{label}",
        ).asset

    def _track_observed(self, entity_uuid: str, location_id: str, label: str) -> None:
        self.inventory.track_asset(
            entity_uuid,
            intended_location_id=location_id,
            idempotency_key=f"track-{label}",
        )
        self.inventory.set_observed_location(
            entity_uuid,
            location_id=location_id,
            observed_at="2026-08-30T09:00:00-04:00",
            idempotency_key=f"observe-{label}",
        )

    def _intent(
        self,
        intent_id: str,
        description: str,
        *,
        quantity: str = "1",
        unit: str | None = None,
        created_at: str = "2026-08-30T10:00:00-04:00",
    ):
        return self.shopping.create(
            intent_id,
            description=description,
            quantity=quantity,
            unit=unit,
            created_at=created_at,
            idempotency_key=f"create-{intent_id}",
        )

    def test_single_exact_observed_name_is_known_stock_but_quantity_remains_unknown(self) -> None:
        intent = self._intent("grocery-milk", "Whole Milk", quantity="1", unit="gallon")
        rows = self.grocery.reconcile(
            intent_ids=[intent.intent_id],
            stock_location_id=self.kitchen.location_id,
        )
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row.status, "known_in_stock")
        self.assertEqual(row.reason, "single_exact_description_observed_in_stock_scope")
        self.assertEqual(row.match_basis, "exact_description")
        self.assertEqual(row.stock_entity_uuid, MILK)
        self.assertEqual(row.observed_location_id, self.pantry.location_id)
        self.assertEqual(
            row.observed_location_path,
            ("Synthetic Home", "Kitchen", "Pantry"),
        )
        self.assertEqual(row.requested_quantity, "1")
        self.assertEqual(row.requested_unit, "gallon")
        # The asset was acquired as a lot of 12. That is deliberately not stock quantity.
        self.assertEqual(self.milk.quantity, 12)
        self.assertIsNone(row.stock_quantity)
        self.assertFalse(row.stock_quantity_known)

    def test_active_intent_with_no_exact_observed_stock_match_stays_needs_to_buy(self) -> None:
        intent = self._intent("grocery-bananas", "Bananas")
        row = self.grocery.reconcile(
            intent_ids=[intent.intent_id],
            stock_location_id=self.kitchen.location_id,
        )[0]
        self.assertEqual(row.status, "needs_to_buy")
        self.assertEqual(row.reason, "active_intent_has_no_exact_observed_stock_match")
        self.assertIsNone(row.stock_entity_uuid)
        self.assertEqual(self.shopping.get(intent.intent_id).state, "active")

    def test_multiple_exact_observed_names_are_unresolved_until_entity_identity_is_supplied(self) -> None:
        intent = self._intent("grocery-sauce", "Tomato Sauce")
        ambiguous = self.grocery.reconcile(
            intent_ids=[intent.intent_id],
            stock_location_id=self.pantry.location_id,
        )[0]
        self.assertEqual(ambiguous.status, "unresolved")
        self.assertEqual(
            ambiguous.reason,
            "multiple_exact_description_stock_matches_require_entity_identity",
        )
        self.assertIsNone(ambiguous.stock_entity_uuid)

        resolved = self.grocery.reconcile(
            intent_ids=[intent.intent_id],
            stock_location_id=self.pantry.location_id,
            entity_uuid_by_intent={intent.intent_id: SAUCE_B},
        )[0]
        self.assertEqual(resolved.status, "known_in_stock")
        self.assertEqual(resolved.match_basis, "entity_uuid")
        self.assertEqual(resolved.stock_entity_uuid, SAUCE_B)

    def test_explicit_entity_outside_stock_scope_is_needs_to_buy(self) -> None:
        intent = self._intent("grocery-paper", "Paper Towels")
        row = self.grocery.reconcile(
            intent_ids=[intent.intent_id],
            stock_location_id=self.kitchen.location_id,
            entity_uuid_by_intent={intent.intent_id: PAPER},
        )[0]
        self.assertEqual(row.status, "needs_to_buy")
        self.assertEqual(row.reason, "explicit_entity_observed_outside_stock_scope")
        self.assertEqual(row.observed_location_id, self.garage.location_id)

    def test_explicit_tracked_entity_without_observation_is_unresolved(self) -> None:
        intent = self._intent("grocery-oats", "Oatmeal")
        row = self.grocery.reconcile(
            intent_ids=[intent.intent_id],
            stock_location_id=self.pantry.location_id,
            entity_uuid_by_intent={intent.intent_id: OATS},
        )[0]
        self.assertEqual(row.status, "unresolved")
        self.assertEqual(
            row.reason, "explicit_entity_has_no_supported_observed_location"
        )
        self.assertEqual(row.stock_entity_uuid, OATS)
        self.assertIsNone(row.observed_location_id)

    def test_explicit_untracked_entity_is_unresolved(self) -> None:
        intent = self._intent("grocery-rice", "Rice")
        row = self.grocery.reconcile(
            intent_ids=[intent.intent_id],
            stock_location_id=self.pantry.location_id,
            entity_uuid_by_intent={intent.intent_id: RICE},
        )[0]
        self.assertEqual(row.status, "unresolved")
        self.assertEqual(row.reason, "explicit_entity_is_not_tracked_inventory")
        self.assertIsNone(row.stock_entity_uuid)

    def test_location_scope_uses_observed_descendants_not_intended_location(self) -> None:
        peas = self._intent("grocery-peas", "Frozen Peas")
        kitchen = self.grocery.reconcile(
            intent_ids=[peas.intent_id],
            stock_location_id=self.kitchen.location_id,
        )[0]
        pantry_only = self.grocery.reconcile(
            intent_ids=[peas.intent_id],
            stock_location_id=self.pantry.location_id,
        )[0]
        self.assertEqual(kitchen.status, "known_in_stock")
        self.assertEqual(kitchen.observed_location_id, self.freezer.location_id)
        self.assertEqual(pantry_only.status, "needs_to_buy")

    def test_fuzzy_and_substring_names_never_auto_match(self) -> None:
        intent = self._intent("grocery-fuzzy-milk", "Milk")
        row = self.grocery.reconcile(
            intent_ids=[intent.intent_id],
            stock_location_id=self.kitchen.location_id,
        )[0]
        self.assertEqual(row.status, "needs_to_buy")
        self.assertIsNone(row.match_basis)

    def test_purchase_and_asset_history_without_tracked_observation_does_not_prove_stock(self) -> None:
        intent = self._intent("grocery-rice-history", "Rice")
        self.assertEqual(self.assets.get(RICE).display_name, "Rice")
        row = self.grocery.reconcile(
            intent_ids=[intent.intent_id],
            stock_location_id=self.kitchen.location_id,
        )[0]
        self.assertEqual(row.status, "needs_to_buy")
        self.assertIsNone(row.stock_entity_uuid)

    def test_selection_mapping_scope_and_terminal_validation_fail_closed(self) -> None:
        active = self._intent("grocery-active", "Bananas")
        cancelled = self._intent("grocery-cancelled", "Apples")
        self.shopping.cancel(
            cancelled.intent_id,
            cancelled_at="2026-08-30T11:00:00-04:00",
            idempotency_key="cancel-grocery-cancelled",
        )

        with self.assertRaises(GroceryReconciliationValidationError):
            self.grocery.reconcile(intent_ids=[], stock_location_id=self.pantry.location_id)
        with self.assertRaises(GroceryReconciliationValidationError):
            self.grocery.reconcile(
                intent_ids=[active.intent_id, active.intent_id],
                stock_location_id=self.pantry.location_id,
            )
        with self.assertRaisesRegex(GroceryReconciliationValidationError, "must be active"):
            self.grocery.reconcile(
                intent_ids=[cancelled.intent_id],
                stock_location_id=self.pantry.location_id,
            )
        with self.assertRaises(GroceryReconciliationValidationError):
            self.grocery.reconcile(
                intent_ids=[active.intent_id],
                stock_location_id="loc-does-not-exist",
            )
        with self.assertRaises(GroceryReconciliationValidationError):
            self.grocery.reconcile(
                intent_ids=[active.intent_id],
                stock_location_id=self.pantry.location_id,
                entity_uuid_by_intent={"not-selected": MILK},
            )
        with self.assertRaises(GroceryReconciliationValidationError):
            self.grocery.reconcile(
                intent_ids=[active.intent_id],
                stock_location_id=self.pantry.location_id,
                limit=0,
            )

    def test_result_order_and_limit_are_deterministic_not_input_order(self) -> None:
        late = self._intent(
            "grocery-late",
            "Bananas",
            created_at="2026-08-30T10:02:00-04:00",
        )
        early = self._intent(
            "grocery-early",
            "Whole Milk",
            created_at="2026-08-30T10:00:00-04:00",
        )
        middle = self._intent(
            "grocery-middle",
            "Frozen Peas",
            created_at="2026-08-30T10:01:00-04:00",
        )
        rows = self.grocery.reconcile(
            intent_ids=[late.intent_id, early.intent_id, middle.intent_id],
            stock_location_id=self.kitchen.location_id,
            limit=2,
        )
        self.assertEqual([row.intent_id for row in rows], [early.intent_id, middle.intent_id])

    def test_reconciliation_is_zero_write_across_all_canonical_state(self) -> None:
        milk = self._intent("grocery-zero-milk", "Whole Milk")
        bananas = self._intent(
            "grocery-zero-bananas",
            "Bananas",
            created_at="2026-08-30T10:01:00-04:00",
        )
        before_records = deepcopy(self.adapter._records)
        before_events = deepcopy(self.adapter._events)
        before_event_ids = deepcopy(self.adapter._event_ids)
        before_stream_revisions = deepcopy(self.adapter._stream_revisions)
        before_idempotency = deepcopy(self.adapter._idempotency)

        rows = self.grocery.reconcile(
            intent_ids=[bananas.intent_id, milk.intent_id],
            stock_location_id=self.kitchen.location_id,
        )
        self.assertEqual(
            [(row.intent_id, row.status) for row in rows],
            [
                (milk.intent_id, "known_in_stock"),
                (bananas.intent_id, "needs_to_buy"),
            ],
        )
        self.assertEqual(self.adapter._records, before_records)
        self.assertEqual(self.adapter._events, before_events)
        self.assertEqual(self.adapter._event_ids, before_event_ids)
        self.assertEqual(self.adapter._stream_revisions, before_stream_revisions)
        self.assertEqual(self.adapter._idempotency, before_idempotency)


if __name__ == "__main__":
    unittest.main()
