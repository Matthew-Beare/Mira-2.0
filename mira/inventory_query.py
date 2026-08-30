"""Read-only canonical inventory projection for Personal MIRA.

This module joins existing canonical asset, identifier, inventory-state, and
location resources for bounded user-facing queries. It does not own mutable
inventory truth and never writes movement, observation, fitment, par, grocery,
scanner, or Android state.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .assets import AssetService, AssetValidationError, AssetView
from .identifiers import (
    IdentifierService,
    IdentifierValidationError,
    IdentifierView,
)
from .inventory_location import (
    INVENTORY_STATE_RESOURCE_TYPE,
    InventoryLocationError,
    InventoryLocationIntegrityError,
    InventoryLocationService,
    InventoryLocationValidationError,
    InventoryStateView,
    LocationView,
)
from .structured_state import (
    StructuredStateAdapter,
    ValidationError as StoreValidationError,
)


class InventoryQueryError(Exception):
    """Base class for inventory-query failures."""


class InventoryQueryValidationError(InventoryQueryError):
    """Raised when a query/filter is malformed or names unknown filter state."""


class InventoryQueryIntegrityError(InventoryQueryError):
    """Raised when canonical inventory projection material is inconsistent."""


@dataclass(frozen=True)
class InventoryIdentifierProjection:
    identifier_id: str
    identifier_type: str
    namespace: str | None
    source_value: str
    normalized_value: str
    verification_state: str


@dataclass(frozen=True)
class InventoryLocationProjection:
    location_id: str
    display_name: str
    kind: str
    path_location_ids: tuple[str, ...]
    path_display_names: tuple[str, ...]


@dataclass(frozen=True)
class InventoryItemProjection:
    entity_uuid: str
    display_name: str
    tracking_mode: str
    quantity: int
    asset_revision: int
    inventory_revision: int
    receipt_id: str
    receipt_line_id: str | None
    identifiers: tuple[InventoryIdentifierProjection, ...]
    intended_location: InventoryLocationProjection | None
    observed_location: InventoryLocationProjection | None
    observed_at: str | None
    asset_note: str | None
    inventory_note: str | None


class InventoryQueryService:
    """Compose deterministic read-only inventory answers from canonical state."""

    def __init__(
        self,
        adapter: StructuredStateAdapter,
        *,
        asset_service: AssetService | None = None,
        identifier_service: IdentifierService | None = None,
        inventory_location_service: InventoryLocationService | None = None,
        inventory_resource_type: str = INVENTORY_STATE_RESOURCE_TYPE,
    ) -> None:
        self._adapter = adapter
        self._assets = asset_service or AssetService(adapter)
        self._identifiers = identifier_service or IdentifierService(
            adapter, asset_service=self._assets
        )
        self._inventory = inventory_location_service or InventoryLocationService(
            adapter, asset_service=self._assets
        )
        self._inventory_resource_type = inventory_resource_type

    def query(
        self,
        *,
        entity_uuid: str | None = None,
        display_name: str | None = None,
        identifier_type: str | None = None,
        identifier_value: str | None = None,
        identifier_namespace: str | None = None,
        intended_location_id: str | None = None,
        observed_location_id: str | None = None,
        include_location_descendants: bool = False,
        limit: int = 100,
    ) -> tuple[InventoryItemProjection, ...]:
        """Return tracked canonical inventory matching all supplied filters.

        Location filters are exact by default. When
        ``include_location_descendants`` is true, a tracked item's referenced
        location may equal the requested location or be below it in the current
        canonical hierarchy. This is query semantics only; it never implies that
        movement of a container moved an item's observation state.
        """

        wanted_limit = _limit(limit)
        if not isinstance(include_location_descendants, bool):
            raise InventoryQueryValidationError(
                "include_location_descendants must be boolean"
            )

        wanted_entity: str | None = None
        if entity_uuid is not None:
            try:
                wanted_entity = self._assets.get(entity_uuid).entity_uuid
            except AssetValidationError as exc:
                raise InventoryQueryValidationError(str(exc)) from exc

        wanted_name = None
        if display_name is not None:
            wanted_name = _text(display_name, "display_name", 500).casefold()

        identifier_filter_used = any(
            value is not None
            for value in (identifier_type, identifier_value, identifier_namespace)
        )
        identifier_entities: set[str] | None = None
        if identifier_filter_used:
            if identifier_type is None or identifier_value is None:
                raise InventoryQueryValidationError(
                    "identifier_type and identifier_value are required together"
                )
            try:
                identifier_entities = {
                    asset.entity_uuid
                    for asset in self._identifiers.lookup_assets(
                        identifier_type=identifier_type,
                        value=identifier_value,
                        namespace=identifier_namespace,
                        limit=1000,
                    )
                }
            except IdentifierValidationError as exc:
                raise InventoryQueryValidationError(str(exc)) from exc
            except Exception as exc:
                # Identifier integrity errors are canonical-data failures, not a
                # reason to silently return a partial inventory projection.
                if isinstance(exc, InventoryQueryError):
                    raise
                raise InventoryQueryIntegrityError(str(exc)) from exc

        location_map = self._location_map()
        wanted_intended = self._validated_filter_location(
            intended_location_id, location_map
        )
        wanted_observed = self._validated_filter_location(
            observed_location_id, location_map
        )

        try:
            inventory_records = self._adapter.query(
                self._inventory_resource_type, limit=1000
            )
        except StoreValidationError as exc:
            raise InventoryQueryValidationError(str(exc)) from exc

        rows: list[InventoryItemProjection] = []
        seen_entity_ids: set[str] = set()
        for record in inventory_records:
            if record.resource_id in seen_entity_ids:
                raise InventoryQueryIntegrityError(
                    "duplicate inventory Resource identity encountered"
                )
            seen_entity_ids.add(record.resource_id)

            try:
                state = self._inventory.get_inventory_state(record.resource_id)
                asset = self._assets.get(state.entity_uuid)
            except InventoryLocationIntegrityError as exc:
                raise InventoryQueryIntegrityError(str(exc)) from exc
            except (InventoryLocationValidationError, AssetValidationError) as exc:
                raise InventoryQueryIntegrityError(
                    "tracked inventory references canonical asset/location state that cannot be resolved"
                ) from exc
            except InventoryLocationError as exc:
                raise InventoryQueryIntegrityError(str(exc)) from exc

            if wanted_entity is not None and asset.entity_uuid != wanted_entity:
                continue
            if wanted_name is not None and wanted_name not in asset.display_name.casefold():
                continue
            if identifier_entities is not None and asset.entity_uuid not in identifier_entities:
                continue
            if not self._location_matches(
                state.intended_location_id,
                wanted_intended,
                include_descendants=include_location_descendants,
                locations=location_map,
            ):
                continue
            if not self._location_matches(
                state.observed_location_id,
                wanted_observed,
                include_descendants=include_location_descendants,
                locations=location_map,
            ):
                continue

            rows.append(self._project(asset, state, location_map))

        rows.sort(key=lambda item: (item.display_name.casefold(), item.entity_uuid))
        return tuple(rows[:wanted_limit])

    def _project(
        self,
        asset: AssetView,
        state: InventoryStateView,
        locations: dict[str, LocationView],
    ) -> InventoryItemProjection:
        try:
            identifiers = self._identifiers.query(
                entity_uuid=asset.entity_uuid, limit=1000
            )
        except IdentifierValidationError as exc:
            raise InventoryQueryIntegrityError(
                "canonical identifiers for tracked asset cannot be resolved"
            ) from exc
        except Exception as exc:
            raise InventoryQueryIntegrityError(str(exc)) from exc

        return InventoryItemProjection(
            entity_uuid=asset.entity_uuid,
            display_name=asset.display_name,
            tracking_mode=asset.tracking_mode,
            quantity=asset.quantity,
            asset_revision=asset.revision,
            inventory_revision=state.revision,
            receipt_id=asset.acquisition.receipt_id,
            receipt_line_id=asset.acquisition.receipt_line_id,
            identifiers=tuple(_identifier_projection(item) for item in identifiers),
            intended_location=self._location_projection(
                state.intended_location_id, locations
            ),
            observed_location=self._location_projection(
                state.observed_location_id, locations
            ),
            observed_at=state.observed_at,
            asset_note=asset.note,
            inventory_note=state.note,
        )

    def _location_map(self) -> dict[str, LocationView]:
        try:
            rows = self._inventory.list_locations(limit=1000)
        except InventoryLocationError as exc:
            raise InventoryQueryIntegrityError(str(exc)) from exc
        locations = {row.location_id: row for row in rows}
        if len(locations) != len(rows):
            raise InventoryQueryIntegrityError(
                "duplicate canonical location identity encountered"
            )
        return locations

    def _validated_filter_location(
        self,
        location_id: str | None,
        locations: dict[str, LocationView],
    ) -> str | None:
        if location_id is None:
            return None
        wanted = _text(location_id, "location_id", 128)
        if wanted not in locations:
            raise InventoryQueryValidationError(
                f"location {wanted!r} does not exist"
            )
        # Validate its parent chain even for exact filters so a corrupt hierarchy
        # cannot be accepted merely because descendant matching was disabled.
        self._location_projection(wanted, locations)
        return wanted

    def _location_matches(
        self,
        candidate_location_id: str | None,
        wanted_location_id: str | None,
        *,
        include_descendants: bool,
        locations: dict[str, LocationView],
    ) -> bool:
        if wanted_location_id is None:
            return True
        if candidate_location_id is None:
            return False
        if candidate_location_id not in locations:
            raise InventoryQueryIntegrityError(
                "inventory state references a missing canonical location"
            )
        if not include_descendants:
            return candidate_location_id == wanted_location_id

        cursor: str | None = candidate_location_id
        seen: set[str] = set()
        while cursor is not None:
            if cursor in seen:
                raise InventoryQueryIntegrityError(
                    "canonical location hierarchy contains a cycle"
                )
            seen.add(cursor)
            if cursor == wanted_location_id:
                return True
            try:
                cursor = locations[cursor].parent_location_id
            except KeyError as exc:
                raise InventoryQueryIntegrityError(
                    "canonical location hierarchy references a missing parent"
                ) from exc
            if len(seen) > 1000:
                raise InventoryQueryIntegrityError(
                    "canonical location hierarchy exceeds safe traversal bound"
                )
        return False

    def _location_projection(
        self,
        location_id: str | None,
        locations: dict[str, LocationView],
    ) -> InventoryLocationProjection | None:
        if location_id is None:
            return None
        path: list[LocationView] = []
        cursor: str | None = location_id
        seen: set[str] = set()
        while cursor is not None:
            if cursor in seen:
                raise InventoryQueryIntegrityError(
                    "canonical location hierarchy contains a cycle"
                )
            seen.add(cursor)
            try:
                location = locations[cursor]
            except KeyError as exc:
                raise InventoryQueryIntegrityError(
                    "canonical location hierarchy references a missing location"
                ) from exc
            path.append(location)
            cursor = location.parent_location_id
            if len(seen) > 1000:
                raise InventoryQueryIntegrityError(
                    "canonical location hierarchy exceeds safe traversal bound"
                )
        path.reverse()
        leaf = path[-1]
        return InventoryLocationProjection(
            location_id=leaf.location_id,
            display_name=leaf.display_name,
            kind=leaf.kind,
            path_location_ids=tuple(item.location_id for item in path),
            path_display_names=tuple(item.display_name for item in path),
        )


def _identifier_projection(item: IdentifierView) -> InventoryIdentifierProjection:
    return InventoryIdentifierProjection(
        identifier_id=item.identifier_id,
        identifier_type=item.identifier_type,
        namespace=item.namespace,
        source_value=item.source_value,
        normalized_value=item.normalized_value,
        verification_state=item.verification_state,
    )


def _limit(value: Any) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or not 1 <= value <= 1000:
        raise InventoryQueryValidationError(
            "limit must be an integer from 1 through 1000"
        )
    return value


def _text(value: Any, field: str, maximum: int) -> str:
    if not isinstance(value, str):
        raise InventoryQueryValidationError(f"{field} must be text")
    normalized = value.strip()
    if not normalized:
        raise InventoryQueryValidationError(f"{field} must not be blank")
    if len(normalized) > maximum:
        raise InventoryQueryValidationError(
            f"{field} exceeds maximum length {maximum}"
        )
    return normalized


__all__ = [
    "InventoryIdentifierProjection",
    "InventoryItemProjection",
    "InventoryLocationProjection",
    "InventoryQueryError",
    "InventoryQueryIntegrityError",
    "InventoryQueryService",
    "InventoryQueryValidationError",
]
