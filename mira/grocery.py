"""Read-only grocery intent versus known-stock reconciliation for Personal MIRA.

Grocery reconciliation composes existing shopping intent with canonical tracked
inventory and observed location truth. It owns no mutable grocery database and
performs no writes. A receipt or acquisition record proves purchase history, not
current stock, and immutable asset acquisition quantity is never presented as
remaining consumable quantity.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Mapping, Sequence

from .inventory_query import (
    InventoryItemProjection,
    InventoryQueryError,
    InventoryQueryService,
)
from .shopping import (
    ShoppingIntentError,
    ShoppingIntentService,
    ShoppingIntentView,
)
from .structured_state import StructuredStateAdapter


GROCERY_STATUSES = frozenset({"needs_to_buy", "known_in_stock", "unresolved"})
_WS_RE = re.compile(r"\s+")


class GroceryReconciliationError(Exception):
    """Base class for grocery reconciliation failures."""


class GroceryReconciliationValidationError(GroceryReconciliationError):
    """Raised when selection, scope, or canonical lookup material is invalid."""


class GroceryReconciliationIntegrityError(GroceryReconciliationError):
    """Raised when required canonical shopping/inventory state is inconsistent."""


@dataclass(frozen=True)
class GroceryReconciliationView:
    intent_id: str
    intent_revision: int
    description: str
    requested_quantity: str
    requested_unit: str | None
    status: str
    reason: str
    match_basis: str | None
    stock_entity_uuid: str | None
    stock_display_name: str | None
    observed_location_id: str | None
    observed_location_path: tuple[str, ...]
    observed_at: str | None
    stock_quantity: None = None
    stock_quantity_known: bool = False

    def sort_key(self) -> tuple[str, str]:
        return (_exact_text(self.description), self.intent_id)


class GroceryReconciliationService:
    """Compose deterministic grocery-vs-stock answers without mutating authority."""

    def __init__(
        self,
        adapter: StructuredStateAdapter,
        *,
        shopping_service: ShoppingIntentService | None = None,
        inventory_query_service: InventoryQueryService | None = None,
    ) -> None:
        self._shopping = shopping_service or ShoppingIntentService(adapter)
        self._inventory = inventory_query_service or InventoryQueryService(adapter)

    def reconcile(
        self,
        *,
        intent_ids: Sequence[str],
        stock_location_id: str,
        entity_uuid_by_intent: Mapping[str, str] | None = None,
        limit: int = 100,
    ) -> tuple[GroceryReconciliationView, ...]:
        """Reconcile explicitly selected active intents against observed stock.

        ``intent_ids`` is the explicit grocery selection boundary. No arbitrary
        shopping intent is auto-classified as grocery. ``stock_location_id`` is
        the canonical location root whose observed descendants count as known
        stock for this query. Exact Entity UUID mappings override name matching;
        otherwise only exact normalized display-name equality is accepted.
        """

        selected_ids = _intent_ids(intent_ids)
        bounded_limit = _limit(limit)
        location_id = _text(stock_location_id, "stock_location_id", 128)
        mappings = _entity_mappings(entity_uuid_by_intent, selected_ids)

        intents = [self._active_intent(intent_id) for intent_id in selected_ids]
        intents.sort(key=ShoppingIntentView.sort_key)

        try:
            stock_pool = self._inventory.query(
                observed_location_id=location_id,
                include_location_descendants=True,
                limit=1000,
            )
        except InventoryQueryError as exc:
            raise GroceryReconciliationValidationError(str(exc)) from exc

        by_exact_name: dict[str, list[InventoryItemProjection]] = {}
        for item in stock_pool:
            by_exact_name.setdefault(_exact_text(item.display_name), []).append(item)
        for matches in by_exact_name.values():
            matches.sort(key=lambda item: item.entity_uuid)

        output: list[GroceryReconciliationView] = []
        for intent in intents:
            explicit_entity = mappings.get(intent.intent_id)
            if explicit_entity is not None:
                output.append(
                    self._reconcile_explicit_entity(
                        intent,
                        entity_uuid=explicit_entity,
                        stock_location_id=location_id,
                    )
                )
                continue

            exact_matches = by_exact_name.get(intent.search_text, [])
            if len(exact_matches) == 1:
                output.append(
                    _result(
                        intent,
                        status="known_in_stock",
                        reason="single_exact_description_observed_in_stock_scope",
                        match_basis="exact_description",
                        stock=exact_matches[0],
                    )
                )
            elif len(exact_matches) > 1:
                output.append(
                    _result(
                        intent,
                        status="unresolved",
                        reason="multiple_exact_description_stock_matches_require_entity_identity",
                        match_basis="exact_description",
                    )
                )
            else:
                output.append(
                    _result(
                        intent,
                        status="needs_to_buy",
                        reason="active_intent_has_no_exact_observed_stock_match",
                        match_basis=None,
                    )
                )

        return tuple(output[:bounded_limit])

    def _active_intent(self, intent_id: str) -> ShoppingIntentView:
        try:
            intent = self._shopping.get(intent_id)
        except ShoppingIntentError as exc:
            raise GroceryReconciliationValidationError(str(exc)) from exc
        if intent.state != "active":
            raise GroceryReconciliationValidationError(
                f"shopping intent {intent.intent_id!r} must be active for grocery reconciliation"
            )
        return intent

    def _reconcile_explicit_entity(
        self,
        intent: ShoppingIntentView,
        *,
        entity_uuid: str,
        stock_location_id: str,
    ) -> GroceryReconciliationView:
        try:
            tracked = self._inventory.query(entity_uuid=entity_uuid, limit=1)
        except InventoryQueryError as exc:
            raise GroceryReconciliationValidationError(str(exc)) from exc

        if not tracked:
            return _result(
                intent,
                status="unresolved",
                reason="explicit_entity_is_not_tracked_inventory",
                match_basis="entity_uuid",
            )

        item = tracked[0]
        if item.observed_location is None:
            return _result(
                intent,
                status="unresolved",
                reason="explicit_entity_has_no_supported_observed_location",
                match_basis="entity_uuid",
                stock=item,
            )

        if stock_location_id in item.observed_location.path_location_ids:
            return _result(
                intent,
                status="known_in_stock",
                reason="explicit_entity_observed_in_stock_scope",
                match_basis="entity_uuid",
                stock=item,
            )

        return _result(
            intent,
            status="needs_to_buy",
            reason="explicit_entity_observed_outside_stock_scope",
            match_basis="entity_uuid",
            stock=item,
        )


def _result(
    intent: ShoppingIntentView,
    *,
    status: str,
    reason: str,
    match_basis: str | None,
    stock: InventoryItemProjection | None = None,
) -> GroceryReconciliationView:
    if status not in GROCERY_STATUSES:
        raise GroceryReconciliationIntegrityError(f"unsupported grocery status: {status}")
    observed = None if stock is None else stock.observed_location
    return GroceryReconciliationView(
        intent_id=intent.intent_id,
        intent_revision=intent.revision,
        description=intent.description,
        requested_quantity=intent.quantity,
        requested_unit=intent.unit,
        status=status,
        reason=reason,
        match_basis=match_basis,
        stock_entity_uuid=None if stock is None else stock.entity_uuid,
        stock_display_name=None if stock is None else stock.display_name,
        observed_location_id=None if observed is None else observed.location_id,
        observed_location_path=(
            () if observed is None else observed.path_display_names
        ),
        observed_at=None if stock is None else stock.observed_at,
        # Deliberately never copy InventoryItemProjection.quantity here. That
        # field is immutable acquisition quantity, not remaining grocery stock.
        stock_quantity=None,
        stock_quantity_known=False,
    )


def _intent_ids(values: Sequence[str]) -> tuple[str, ...]:
    if isinstance(values, (str, bytes)) or not isinstance(values, Sequence):
        raise GroceryReconciliationValidationError(
            "intent_ids must be a non-empty sequence of explicit shopping intent IDs"
        )
    if not 1 <= len(values) <= 1000:
        raise GroceryReconciliationValidationError(
            "intent_ids must contain from 1 through 1000 explicit shopping intent IDs"
        )
    normalized = tuple(_text(value, "intent_id", 128) for value in values)
    if len(set(normalized)) != len(normalized):
        raise GroceryReconciliationValidationError("intent_ids must not contain duplicates")
    return normalized


def _entity_mappings(
    values: Mapping[str, str] | None,
    selected_ids: tuple[str, ...],
) -> dict[str, str]:
    if values is None:
        return {}
    if not isinstance(values, Mapping):
        raise GroceryReconciliationValidationError(
            "entity_uuid_by_intent must be a mapping or null"
        )
    selected = set(selected_ids)
    result: dict[str, str] = {}
    for raw_intent_id, raw_entity_uuid in values.items():
        intent_id = _text(raw_intent_id, "entity mapping intent_id", 128)
        if intent_id not in selected:
            raise GroceryReconciliationValidationError(
                "entity_uuid_by_intent keys must be a subset of selected intent_ids"
            )
        result[intent_id] = _text(raw_entity_uuid, "entity_uuid", 128)
    return result


def _exact_text(value: str) -> str:
    return _WS_RE.sub(" ", value.strip()).casefold()


def _text(value: object, field: str, maximum: int) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise GroceryReconciliationValidationError(
            f"{field} must be non-empty trimmed text"
        )
    if len(value) > maximum:
        raise GroceryReconciliationValidationError(
            f"{field} exceeds maximum length {maximum}"
        )
    return value


def _limit(value: object) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or not 1 <= value <= 1000:
        raise GroceryReconciliationValidationError(
            "limit must be an integer from 1 through 1000"
        )
    return value


__all__ = [
    "GROCERY_STATUSES",
    "GroceryReconciliationError",
    "GroceryReconciliationIntegrityError",
    "GroceryReconciliationService",
    "GroceryReconciliationValidationError",
    "GroceryReconciliationView",
]
