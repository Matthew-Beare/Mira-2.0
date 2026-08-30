"""Canonical inventory participation and intended/observed physical location state.

Inventory is a projection over an existing physical asset identity. It never
allocates another physical UUID. Locations have their own stable identities,
while an inventory_state resource is keyed exactly by the canonical asset Entity
UUID and keeps intended placement separate from latest supported observation.
Movement-event history and scanner behavior are deliberately outside this module.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, replace
from datetime import datetime
from typing import Any
from uuid import uuid4

from .assets import AssetService, AssetValidationError
from .structured_state import (
    NotFoundError,
    ResourceRecord,
    StructuredStateAdapter,
    ValidationError as StoreValidationError,
)


LOCATION_RESOURCE_TYPE = "location"
INVENTORY_STATE_RESOURCE_TYPE = "inventory_state"
LOCATION_SCHEMA_VERSION = 1
INVENTORY_STATE_SCHEMA_VERSION = 1
LOCATION_KINDS = frozenset(
    {"site", "building", "room", "zone", "aisle", "shelf", "bin", "container", "other"}
)


class InventoryLocationError(Exception):
    """Base class for inventory/location failures."""


class InventoryLocationValidationError(InventoryLocationError):
    """Raised when requested or persisted inventory/location state is malformed."""


class InventoryLocationConflictError(InventoryLocationError):
    """Raised when requested state conflicts with canonical identity/state."""


class InventoryLocationIntegrityError(InventoryLocationError):
    """Raised when persisted canonical hierarchy or references are inconsistent."""


@dataclass(frozen=True)
class LocationView:
    location_id: str
    revision: int
    display_name: str
    kind: str
    parent_location_id: str | None
    note: str | None
    idempotent_replay: bool = False


@dataclass(frozen=True)
class InventoryStateView:
    entity_uuid: str
    revision: int
    participation_state: str
    intended_location_id: str | None
    observed_location_id: str | None
    observed_at: str | None
    note: str | None
    idempotent_replay: bool = False


class InventoryLocationService:
    """Track existing assets and maintain independent intended/observed locations."""

    def __init__(
        self,
        adapter: StructuredStateAdapter,
        *,
        asset_service: AssetService | None = None,
        location_resource_type: str = LOCATION_RESOURCE_TYPE,
        inventory_resource_type: str = INVENTORY_STATE_RESOURCE_TYPE,
    ) -> None:
        self._adapter = adapter
        self._assets = asset_service or AssetService(adapter)
        self._location_resource_type = location_resource_type
        self._inventory_resource_type = inventory_resource_type

    def create_location(
        self,
        *,
        display_name: str,
        kind: str,
        idempotency_key: str,
        location_id: str | None = None,
        parent_location_id: str | None = None,
        note: str | None = None,
    ) -> LocationView:
        key = _text(idempotency_key, "idempotency_key", 128)
        name = _text(display_name, "display_name", 300)
        location_kind = _location_kind(kind)
        parent = _optional_id(parent_location_id, "parent_location_id", 128)
        normalized_note = _optional_text(note, "note", 4000)
        wanted_id = (
            f"location-{uuid4()}"
            if location_id is None
            else _text(location_id, "location_id", 128)
        )
        if parent == wanted_id:
            raise InventoryLocationConflictError("location cannot be its own parent")
        if parent is not None:
            self.get_location(parent)

        try:
            current_record = self._adapter.get(self._location_resource_type, wanted_id)
        except NotFoundError:
            current_record = None
        except StoreValidationError as exc:
            raise InventoryLocationValidationError(str(exc)) from exc

        if current_record is not None:
            current = _location_view(current_record)
            if (
                current.display_name == name
                and current.kind == location_kind
                and current.parent_location_id == parent
                and current.note == normalized_note
            ):
                return replace(current, idempotent_replay=True)
            raise InventoryLocationConflictError(
                "location_id already exists with different canonical material"
            )

        self._assert_parent_chain_safe(location_id=wanted_id, parent_location_id=parent)
        return self._write_location(
            location_id=wanted_id,
            display_name=name,
            kind=location_kind,
            parent_location_id=parent,
            note=normalized_note,
            expected_revision=0,
            idempotency_key=key,
        )

    def get_location(self, location_id: str) -> LocationView:
        wanted = _text(location_id, "location_id", 128)
        try:
            return _location_view(self._adapter.get(self._location_resource_type, wanted))
        except NotFoundError as exc:
            raise InventoryLocationValidationError(
                f"location {wanted!r} does not exist"
            ) from exc
        except StoreValidationError as exc:
            raise InventoryLocationValidationError(str(exc)) from exc

    def update_location(
        self,
        location_id: str,
        *,
        idempotency_key: str,
        display_name: str | None = None,
        kind: str | None = None,
        parent_location_id: str | None | object = None,
        replace_parent: bool = False,
        note: str | None | object = None,
        replace_note: bool = False,
    ) -> LocationView:
        key = _text(idempotency_key, "idempotency_key", 128)
        current = self.get_location(location_id)
        if not isinstance(replace_parent, bool) or not isinstance(replace_note, bool):
            raise InventoryLocationValidationError(
                "replace_parent and replace_note must be boolean"
            )
        name = (
            current.display_name
            if display_name is None
            else _text(display_name, "display_name", 300)
        )
        location_kind = current.kind if kind is None else _location_kind(kind)
        if replace_parent:
            parent = _optional_id(parent_location_id, "parent_location_id", 128)
        else:
            if parent_location_id is not None:
                raise InventoryLocationValidationError(
                    "parent_location_id changes require replace_parent=True"
                )
            parent = current.parent_location_id
        if replace_note:
            normalized_note = _optional_text(note, "note", 4000)
        else:
            if note is not None:
                raise InventoryLocationValidationError(
                    "note changes require replace_note=True"
                )
            normalized_note = current.note

        if parent == current.location_id:
            raise InventoryLocationConflictError("location cannot be its own parent")
        if parent is not None:
            self.get_location(parent)
        self._assert_parent_chain_safe(
            location_id=current.location_id, parent_location_id=parent
        )
        if (
            name == current.display_name
            and location_kind == current.kind
            and parent == current.parent_location_id
            and normalized_note == current.note
        ):
            return replace(current, idempotent_replay=True)
        return self._write_location(
            location_id=current.location_id,
            display_name=name,
            kind=location_kind,
            parent_location_id=parent,
            note=normalized_note,
            expected_revision=current.revision,
            idempotency_key=key,
        )

    def list_locations(self, *, limit: int = 1000) -> tuple[LocationView, ...]:
        _limit(limit)
        try:
            records = self._adapter.query(self._location_resource_type, limit=limit)
        except StoreValidationError as exc:
            raise InventoryLocationValidationError(str(exc)) from exc
        rows = [_location_view(record) for record in records]
        rows.sort(key=lambda item: item.location_id)
        return tuple(rows)

    def track_asset(
        self,
        entity_uuid: str,
        *,
        idempotency_key: str,
        intended_location_id: str | None = None,
        note: str | None = None,
    ) -> InventoryStateView:
        key = _text(idempotency_key, "idempotency_key", 128)
        asset = self._canonical_asset(entity_uuid)
        intended = _optional_id(intended_location_id, "intended_location_id", 128)
        if intended is not None:
            self.get_location(intended)
        normalized_note = _optional_text(note, "note", 4000)

        try:
            current_record = self._adapter.get(
                self._inventory_resource_type, asset.entity_uuid
            )
        except NotFoundError:
            current_record = None
        except StoreValidationError as exc:
            raise InventoryLocationValidationError(str(exc)) from exc

        if current_record is not None:
            current = self._validated_inventory_state(current_record)
            if (
                current.intended_location_id == intended
                and current.note == normalized_note
            ):
                return replace(current, idempotent_replay=True)
            raise InventoryLocationConflictError(
                "asset is already inventory-tracked; use explicit state mutations"
            )

        return self._write_inventory_state(
            entity_uuid=asset.entity_uuid,
            intended_location_id=intended,
            observed_location_id=None,
            observed_at=None,
            note=normalized_note,
            expected_revision=0,
            idempotency_key=key,
        )

    def get_inventory_state(self, entity_uuid: str) -> InventoryStateView:
        asset = self._canonical_asset(entity_uuid)
        try:
            record = self._adapter.get(self._inventory_resource_type, asset.entity_uuid)
        except NotFoundError as exc:
            raise InventoryLocationValidationError(
                f"asset {asset.entity_uuid!r} is not tracked in inventory"
            ) from exc
        except StoreValidationError as exc:
            raise InventoryLocationValidationError(str(exc)) from exc
        return self._validated_inventory_state(record)

    def set_intended_location(
        self,
        entity_uuid: str,
        *,
        location_id: str | None,
        idempotency_key: str,
    ) -> InventoryStateView:
        key = _text(idempotency_key, "idempotency_key", 128)
        current = self.get_inventory_state(entity_uuid)
        intended = _optional_id(location_id, "location_id", 128)
        if intended is not None:
            self.get_location(intended)
        if intended == current.intended_location_id:
            return replace(current, idempotent_replay=True)
        return self._write_inventory_state(
            entity_uuid=current.entity_uuid,
            intended_location_id=intended,
            observed_location_id=current.observed_location_id,
            observed_at=current.observed_at,
            note=current.note,
            expected_revision=current.revision,
            idempotency_key=key,
        )

    def set_observed_location(
        self,
        entity_uuid: str,
        *,
        location_id: str | None,
        idempotency_key: str,
        observed_at: str | None = None,
    ) -> InventoryStateView:
        key = _text(idempotency_key, "idempotency_key", 128)
        current = self.get_inventory_state(entity_uuid)
        observed = _optional_id(location_id, "location_id", 128)
        if observed is None:
            if observed_at is not None:
                raise InventoryLocationValidationError(
                    "observed_at must be null when clearing observed location"
                )
            normalized_time = None
        else:
            self.get_location(observed)
            normalized_time = _observed_at(observed_at)
        if (
            observed == current.observed_location_id
            and normalized_time == current.observed_at
        ):
            return replace(current, idempotent_replay=True)
        return self._write_inventory_state(
            entity_uuid=current.entity_uuid,
            intended_location_id=current.intended_location_id,
            observed_location_id=observed,
            observed_at=normalized_time,
            note=current.note,
            expected_revision=current.revision,
            idempotency_key=key,
        )

    def _canonical_asset(self, entity_uuid: str):
        try:
            return self._assets.get(entity_uuid)
        except AssetValidationError as exc:
            raise InventoryLocationValidationError(str(exc)) from exc

    def _validated_inventory_state(self, record: ResourceRecord) -> InventoryStateView:
        view = _inventory_state_view(record)
        if view.entity_uuid != record.resource_id:
            raise InventoryLocationIntegrityError(
                "inventory state Resource identity does not equal canonical Entity UUID"
            )
        self._canonical_asset(view.entity_uuid)
        for location_id in (
            view.intended_location_id,
            view.observed_location_id,
        ):
            if location_id is not None:
                try:
                    self.get_location(location_id)
                except InventoryLocationValidationError as exc:
                    raise InventoryLocationIntegrityError(
                        "inventory state references a missing/corrupt canonical location"
                    ) from exc
        return view

    def _assert_parent_chain_safe(
        self, *, location_id: str, parent_location_id: str | None
    ) -> None:
        if parent_location_id is None:
            return
        seen = {location_id}
        cursor: str | None = parent_location_id
        while cursor is not None:
            if cursor in seen:
                raise InventoryLocationConflictError(
                    "location parent relationship would create a cycle"
                )
            seen.add(cursor)
            parent = self.get_location(cursor)
            cursor = parent.parent_location_id
            if len(seen) > 1000:
                raise InventoryLocationIntegrityError(
                    "location hierarchy exceeds safe traversal bound"
                )

    def _write_location(
        self,
        *,
        location_id: str,
        display_name: str,
        kind: str,
        parent_location_id: str | None,
        note: str | None,
        expected_revision: int,
        idempotency_key: str,
    ) -> LocationView:
        payload = {
            "schema_version": LOCATION_SCHEMA_VERSION,
            "location_id": location_id,
            "display_name": display_name,
            "kind": kind,
            "parent_location_id": parent_location_id,
            "note": note,
        }
        try:
            result = self._adapter.upsert(
                self._location_resource_type,
                location_id,
                payload,
                idempotency_key=idempotency_key,
                expected_revision=expected_revision,
            )
        except StoreValidationError as exc:
            raise InventoryLocationValidationError(str(exc)) from exc
        return _location_view(result.record, idempotent_replay=result.idempotent_replay)

    def _write_inventory_state(
        self,
        *,
        entity_uuid: str,
        intended_location_id: str | None,
        observed_location_id: str | None,
        observed_at: str | None,
        note: str | None,
        expected_revision: int,
        idempotency_key: str,
    ) -> InventoryStateView:
        payload = {
            "schema_version": INVENTORY_STATE_SCHEMA_VERSION,
            "entity_uuid": entity_uuid,
            "participation_state": "tracked",
            "intended_location_id": intended_location_id,
            "observed_location_id": observed_location_id,
            "observed_at": observed_at,
            "note": note,
        }
        try:
            result = self._adapter.upsert(
                self._inventory_resource_type,
                entity_uuid,
                payload,
                idempotency_key=idempotency_key,
                expected_revision=expected_revision,
            )
        except StoreValidationError as exc:
            raise InventoryLocationValidationError(str(exc)) from exc
        return self._validated_inventory_state(result.record)


def _location_view(
    record: ResourceRecord, *, idempotent_replay: bool = False
) -> LocationView:
    payload = deepcopy(record.payload)
    if payload.get("schema_version") != LOCATION_SCHEMA_VERSION:
        raise InventoryLocationValidationError("unsupported location schema version")
    location_id = _text(payload.get("location_id"), "location_id", 128)
    if location_id != record.resource_id:
        raise InventoryLocationValidationError(
            "location_id does not match Resource identity"
        )
    return LocationView(
        location_id=location_id,
        revision=record.revision,
        display_name=_text(payload.get("display_name"), "display_name", 300),
        kind=_location_kind(payload.get("kind")),
        parent_location_id=_optional_id(
            payload.get("parent_location_id"), "parent_location_id", 128
        ),
        note=_optional_text(payload.get("note"), "note", 4000),
        idempotent_replay=idempotent_replay,
    )


def _inventory_state_view(
    record: ResourceRecord, *, idempotent_replay: bool = False
) -> InventoryStateView:
    payload = deepcopy(record.payload)
    if payload.get("schema_version") != INVENTORY_STATE_SCHEMA_VERSION:
        raise InventoryLocationValidationError(
            "unsupported inventory_state schema version"
        )
    entity_uuid = _text(payload.get("entity_uuid"), "entity_uuid", 128)
    if payload.get("participation_state") != "tracked":
        raise InventoryLocationValidationError(
            "inventory participation_state must be tracked"
        )
    intended = _optional_id(
        payload.get("intended_location_id"), "intended_location_id", 128
    )
    observed = _optional_id(
        payload.get("observed_location_id"), "observed_location_id", 128
    )
    raw_observed_at = payload.get("observed_at")
    if observed is None:
        if raw_observed_at is not None:
            raise InventoryLocationValidationError(
                "observed_at requires an observed_location_id"
            )
        observed_at = None
    else:
        observed_at = _observed_at(raw_observed_at)
    return InventoryStateView(
        entity_uuid=entity_uuid,
        revision=record.revision,
        participation_state="tracked",
        intended_location_id=intended,
        observed_location_id=observed,
        observed_at=observed_at,
        note=_optional_text(payload.get("note"), "note", 4000),
        idempotent_replay=idempotent_replay,
    )


def _location_kind(value: Any) -> str:
    if not isinstance(value, str):
        raise InventoryLocationValidationError("location kind must be text")
    normalized = value.strip().lower()
    if normalized not in LOCATION_KINDS:
        raise InventoryLocationValidationError(
            "location kind must be one of " + ", ".join(sorted(LOCATION_KINDS))
        )
    return normalized


def _observed_at(value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        raise InventoryLocationValidationError(
            "observed_at must be a non-empty offset-aware ISO-8601 timestamp"
        )
    text = value.strip()
    parse_text = text[:-1] + "+00:00" if text.endswith("Z") else text
    try:
        parsed = datetime.fromisoformat(parse_text)
    except ValueError as exc:
        raise InventoryLocationValidationError(
            "observed_at must be valid ISO-8601"
        ) from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise InventoryLocationValidationError(
            "observed_at must include an explicit UTC offset"
        )
    return parsed.isoformat()


def _limit(value: Any) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or not 1 <= value <= 1000:
        raise InventoryLocationValidationError("limit must be an integer from 1 through 1000")
    return value


def _text(value: Any, field: str, maximum: int) -> str:
    if not isinstance(value, str):
        raise InventoryLocationValidationError(f"{field} must be text")
    normalized = value.strip()
    if not normalized:
        raise InventoryLocationValidationError(f"{field} must not be blank")
    if len(normalized) > maximum:
        raise InventoryLocationValidationError(
            f"{field} exceeds maximum length {maximum}"
        )
    return normalized


def _optional_text(value: Any, field: str, maximum: int) -> str | None:
    if value is None:
        return None
    return _text(value, field, maximum)


def _optional_id(value: Any, field: str, maximum: int) -> str | None:
    if value is None:
        return None
    return _text(value, field, maximum)


__all__ = [
    "INVENTORY_STATE_RESOURCE_TYPE",
    "INVENTORY_STATE_SCHEMA_VERSION",
    "LOCATION_KINDS",
    "LOCATION_RESOURCE_TYPE",
    "LOCATION_SCHEMA_VERSION",
    "InventoryLocationConflictError",
    "InventoryLocationError",
    "InventoryLocationIntegrityError",
    "InventoryLocationService",
    "InventoryLocationValidationError",
    "InventoryStateView",
    "LocationView",
]
