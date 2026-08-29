"""Deterministic native Google Workspace protocol for Personal MIRA.

Stock ChatGPT can use its authenticated Google Drive/Sheets connection directly
for the zero-infrastructure Personal lane. This module defines the durable
single-writer bootstrap/preflight/mutation/readback semantics that the
orchestration layer must follow so direct connector writes remain compatible
with AUTH-001 and STORE-001.

It contains no spreadsheet IDs, account data, credentials, or connector calls.
It produces runtime batchUpdate request shapes from already-grounded sheet IDs
and freshly read provider state.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import re
from typing import Any, Mapping, Sequence

from .structured_state import (
    IdempotencyConflictError,
    IdentityConflictError,
    ResourceRecord,
    RevisionConflictError,
    StructuredStateError,
    ValidationError,
)


_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_PERSONAL_AUTHORITY_ID = "google-sheets-personal"
_PERSONAL_BINDING_ID = "binding-entity"
_PERSONAL_DATA_CLASS = "entity"
_PERSONAL_SCHEMA_VERSION = "mira-structured-state-v1"


class WorkspaceReadbackError(StructuredStateError):
    """Raised when native Google provider readback differs from the plan."""


class WorkspaceBootstrapError(StructuredStateError):
    """Raised when a copied Workspace starter cannot be safely initialized."""


@dataclass(frozen=True)
class WorkspaceIdempotencyRecord:
    """Persisted idempotency state read from the MIRROR Idempotency tab."""

    row_number: int
    idempotency_key: str
    operation: str
    request_hash: str
    result: Mapping[str, Any]
    resource_ref: str

    def __post_init__(self) -> None:
        _positive_row(self.row_number, "row_number")
        _token(self.idempotency_key, "idempotency_key")
        _token(self.operation, "operation")
        _token(self.request_hash, "request_hash")
        _token(self.resource_ref, "resource_ref")
        _normalize_mapping(self.result, "result")


@dataclass(frozen=True)
class WorkspaceUpsertPlan:
    """One canonical upsert decision after resource/idempotency preflight."""

    record: ResourceRecord
    idempotency_key: str
    request_hash: str
    expected_revision: int
    resource_row_number: int | None
    result: Mapping[str, Any]
    idempotent_replay: bool = False

    def batch_update_requests(
        self,
        *,
        resources_sheet_id: int,
        idempotency_sheet_id: int,
        timestamp: str,
    ) -> tuple[dict[str, object], ...]:
        """Materialize one atomic Sheets batchUpdate request list.

        Replay plans intentionally materialize no writes.
        """

        if self.idempotent_replay:
            return ()
        _sheet_id(resources_sheet_id, "resources_sheet_id")
        _sheet_id(idempotency_sheet_id, "idempotency_sheet_id")
        when = _token(timestamp, "timestamp")

        resource_values = (
            self.record.resource_type,
            self.record.resource_id,
            self.record.revision,
            _json_text(self.record.payload),
            when,
            self.idempotency_key,
            self.request_hash,
        )
        resource_cells = [_cell(value) for value in resource_values]
        if self.resource_row_number is None:
            resource_request: dict[str, object] = {
                "appendCells": {
                    "sheetId": resources_sheet_id,
                    "rows": [{"values": resource_cells}],
                    "fields": "userEnteredValue",
                }
            }
        else:
            row_number = _positive_row(self.resource_row_number, "resource_row_number")
            resource_request = {
                "updateCells": {
                    "range": {
                        "sheetId": resources_sheet_id,
                        "startRowIndex": row_number - 1,
                        "endRowIndex": row_number,
                        "startColumnIndex": 0,
                        "endColumnIndex": len(resource_cells),
                    },
                    "rows": [{"values": resource_cells}],
                    "fields": "userEnteredValue",
                }
            }

        idempotency_values = (
            self.idempotency_key,
            "upsert",
            self.request_hash,
            _json_text(self.result),
            when,
            f"{self.record.resource_type}/{self.record.resource_id}",
        )
        return (
            resource_request,
            {
                "appendCells": {
                    "sheetId": idempotency_sheet_id,
                    "rows": [{"values": [_cell(value) for value in idempotency_values]}],
                    "fields": "userEnteredValue",
                }
            },
        )


@dataclass(frozen=True)
class WorkspaceBootstrapPlan:
    """Atomic Authority + entity-binding initialization for one copied starter."""

    authority: WorkspaceUpsertPlan
    binding: WorkspaceUpsertPlan

    @property
    def idempotent_replay(self) -> bool:
        return self.authority.idempotent_replay and self.binding.idempotent_replay

    def batch_update_requests(
        self,
        *,
        resources_sheet_id: int,
        idempotency_sheet_id: int,
        timestamp: str,
    ) -> tuple[dict[str, object], ...]:
        """Return zero requests on replay or one four-request atomic bootstrap."""

        authority_requests = self.authority.batch_update_requests(
            resources_sheet_id=resources_sheet_id,
            idempotency_sheet_id=idempotency_sheet_id,
            timestamp=timestamp,
        )
        binding_requests = self.binding.batch_update_requests(
            resources_sheet_id=resources_sheet_id,
            idempotency_sheet_id=idempotency_sheet_id,
            timestamp=timestamp,
        )
        if bool(authority_requests) != bool(binding_requests):
            raise WorkspaceBootstrapError(
                "Workspace bootstrap is partially persisted; refuse non-atomic repair"
            )
        return authority_requests + binding_requests


def plan_workspace_bootstrap(
    *,
    owner_id: str,
    resource_rows: Sequence[tuple[int, ResourceRecord]],
    idempotency_rows: Sequence[WorkspaceIdempotencyRecord],
) -> WorkspaceBootstrapPlan:
    """Plan first-run Personal Authority state for a clean copied Sheet.

    Initialization is all-new or all-replay. A partial/conflicting bootstrap
    fails closed so a copied starter never silently invents a second authority.
    """

    owner = _identifier(owner_id, "owner_id")
    expected_binding_payload = {
        "authority_id": _PERSONAL_AUTHORITY_ID,
        "data_class": _PERSONAL_DATA_CLASS,
    }
    conflicting_bindings = [
        record
        for _, record in resource_rows
        if record.resource_type == "authority_binding"
        and record.payload.get("data_class") == _PERSONAL_DATA_CLASS
        and (
            record.resource_id != _PERSONAL_BINDING_ID
            or dict(record.payload) != expected_binding_payload
        )
    ]
    if conflicting_bindings:
        raise WorkspaceBootstrapError(
            "entity data class is already bound to a different persisted authority"
        )

    authority_payload = {
        "adapter_key": "google-sheets",
        "authority_id": _PERSONAL_AUTHORITY_ID,
        "enabled": True,
        "failure_domain": "google-sheets-personal",
        "namespace": "mira-personal",
        "owner_id": owner,
        "resource_ref": "runtime:google-structured-state",
        "schema_version": _PERSONAL_SCHEMA_VERSION,
        "verified": True,
    }
    authority = plan_workspace_upsert(
        "authority",
        _PERSONAL_AUTHORITY_ID,
        authority_payload,
        idempotency_key="bootstrap-authority-google-sheets-personal",
        expected_revision=0,
        resource_rows=resource_rows,
        idempotency_rows=idempotency_rows,
    )
    binding = plan_workspace_upsert(
        "authority_binding",
        _PERSONAL_BINDING_ID,
        expected_binding_payload,
        idempotency_key="bootstrap-binding-entity",
        expected_revision=0,
        resource_rows=resource_rows,
        idempotency_rows=idempotency_rows,
    )
    if authority.idempotent_replay != binding.idempotent_replay:
        raise WorkspaceBootstrapError(
            "Workspace bootstrap is partially persisted; refuse non-atomic repair"
        )
    if authority.idempotent_replay:
        if authority.record.payload.get("owner_id") != owner:
            raise WorkspaceBootstrapError(
                "persisted Personal authority belongs to a different owner identity"
            )
    return WorkspaceBootstrapPlan(authority=authority, binding=binding)


def verify_workspace_bootstrap_readback(
    plan: WorkspaceBootstrapPlan,
    *,
    resource_rows: Sequence[tuple[int, ResourceRecord]],
    idempotency_rows: Sequence[WorkspaceIdempotencyRecord],
) -> None:
    """Require exact provider readback for both bootstrap records."""

    verify_workspace_upsert_readback(
        plan.authority,
        resource_rows=resource_rows,
        idempotency_rows=idempotency_rows,
    )
    verify_workspace_upsert_readback(
        plan.binding,
        resource_rows=resource_rows,
        idempotency_rows=idempotency_rows,
    )


def plan_workspace_upsert(
    resource_type: str,
    resource_id: str,
    payload: Mapping[str, Any],
    *,
    idempotency_key: str,
    expected_revision: int,
    resource_rows: Sequence[tuple[int, ResourceRecord]],
    idempotency_rows: Sequence[WorkspaceIdempotencyRecord],
) -> WorkspaceUpsertPlan:
    """Plan a replay-safe single-writer upsert from freshly read Google state."""

    resource_type = _token(resource_type, "resource_type")
    resource_id = _identifier(resource_id, "resource_id")
    key = _token(idempotency_key, "idempotency_key")
    if not isinstance(expected_revision, int) or isinstance(expected_revision, bool) or expected_revision < 0:
        raise ValidationError("expected_revision must be a non-negative integer")
    normalized_payload = _normalize_mapping(payload, "payload")
    request_hash = workspace_upsert_fingerprint(
        resource_type,
        resource_id,
        normalized_payload,
        expected_revision=expected_revision,
    )

    matching_idempotency = [row for row in idempotency_rows if row.idempotency_key == key]
    if len(matching_idempotency) > 1:
        raise IdempotencyConflictError(f"duplicate persisted idempotency key: {key}")
    if matching_idempotency:
        stored = matching_idempotency[0]
        if stored.operation != "upsert":
            raise IdempotencyConflictError(
                "idempotency key was already used for a different operation"
            )
        if stored.request_hash != request_hash:
            raise IdempotencyConflictError(
                "idempotency key was already used for different material input"
            )
        result = _normalize_mapping(stored.result, "idempotency result")
        if result.get("kind") != "upsert":
            raise IdempotencyConflictError("persisted idempotency result has wrong operation")
        record = _record_from_result(result)
        return WorkspaceUpsertPlan(
            record=record,
            idempotency_key=key,
            request_hash=request_hash,
            expected_revision=expected_revision,
            resource_row_number=None,
            result=result,
            idempotent_replay=True,
        )

    matching_resources = [
        (row_number, record)
        for row_number, record in resource_rows
        if record.resource_type == resource_type and record.resource_id == resource_id
    ]
    if len(matching_resources) > 1:
        raise IdentityConflictError(
            f"duplicate persisted resource identity: {resource_type}:{resource_id}"
        )
    current = matching_resources[0] if matching_resources else None
    current_revision = 0 if current is None else current[1].revision
    if expected_revision != current_revision:
        raise RevisionConflictError(
            f"expected revision {expected_revision}, current revision is {current_revision}"
        )

    record = ResourceRecord(
        resource_type=resource_type,
        resource_id=resource_id,
        payload=normalized_payload,
        revision=current_revision + 1,
    )
    result = {
        "kind": "upsert",
        "record": {
            "payload": dict(record.payload),
            "resource_id": record.resource_id,
            "resource_type": record.resource_type,
            "revision": record.revision,
        },
    }
    return WorkspaceUpsertPlan(
        record=record,
        idempotency_key=key,
        request_hash=request_hash,
        expected_revision=expected_revision,
        resource_row_number=None if current is None else current[0],
        result=result,
        idempotent_replay=False,
    )


def workspace_upsert_fingerprint(
    resource_type: str,
    resource_id: str,
    payload: Mapping[str, Any],
    *,
    expected_revision: int,
) -> str:
    """Return the exact STORE-001 Google-adapter upsert request hash."""

    material = {
        "operation": "upsert",
        "resource_type": _token(resource_type, "resource_type"),
        "resource_id": _identifier(resource_id, "resource_id"),
        "payload": _normalize_mapping(payload, "payload"),
        "expected_revision": expected_revision,
    }
    return hashlib.sha256(_json_text(material).encode("utf-8")).hexdigest()


def verify_workspace_upsert_readback(
    plan: WorkspaceUpsertPlan,
    *,
    resource_rows: Sequence[tuple[int, ResourceRecord]],
    idempotency_rows: Sequence[WorkspaceIdempotencyRecord],
) -> None:
    """Require exact post-write resource and idempotency provider readback."""

    resources = [
        record
        for _, record in resource_rows
        if record.resource_type == plan.record.resource_type
        and record.resource_id == plan.record.resource_id
    ]
    if resources != [plan.record]:
        raise WorkspaceReadbackError("Google Workspace resource readback mismatch")

    rows = [row for row in idempotency_rows if row.idempotency_key == plan.idempotency_key]
    if len(rows) != 1:
        raise WorkspaceReadbackError("Google Workspace idempotency readback mismatch")
    stored = rows[0]
    if (
        stored.operation != "upsert"
        or stored.request_hash != plan.request_hash
        or _normalize_mapping(stored.result, "idempotency result")
        != _normalize_mapping(plan.result, "planned result")
        or stored.resource_ref != f"{plan.record.resource_type}/{plan.record.resource_id}"
    ):
        raise WorkspaceReadbackError("Google Workspace idempotency material mismatch")


def _record_from_result(result: Mapping[str, Any]) -> ResourceRecord:
    raw = result.get("record")
    if not isinstance(raw, Mapping):
        raise IdempotencyConflictError("persisted idempotency result has no record")
    try:
        resource_type = _token(raw["resource_type"], "resource_type")
        resource_id = _identifier(raw["resource_id"], "resource_id")
        revision = raw["revision"]
        payload = _normalize_mapping(raw["payload"], "payload")
    except KeyError as exc:
        raise IdempotencyConflictError("persisted idempotency record is incomplete") from exc
    if not isinstance(revision, int) or isinstance(revision, bool) or revision < 1:
        raise IdempotencyConflictError("persisted idempotency revision is invalid")
    return ResourceRecord(resource_type, resource_id, payload, revision)


def _normalize_mapping(value: Mapping[str, Any], field: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ValidationError(f"{field} must be a mapping")
    try:
        return json.loads(_json_text(dict(value)))
    except (TypeError, ValueError) as exc:
        raise ValidationError(f"{field} must contain JSON-compatible values") from exc


def _json_text(value: object) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def _token(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise ValidationError(f"{field} must be a non-empty trimmed string")
    if len(value) > 128:
        raise ValidationError(f"{field} must be at most 128 characters")
    return value


def _identifier(value: object, field: str) -> str:
    normalized = _token(value, field)
    if not _ID_RE.fullmatch(normalized):
        raise ValidationError(f"{field} has invalid canonical identity syntax")
    return normalized


def _positive_row(value: object, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 2:
        raise ValidationError(f"{field} must be an integer >= 2")
    return value


def _sheet_id(value: object, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ValidationError(f"{field} must be a non-negative integer")
    return value


def _cell(value: object) -> dict[str, object]:
    if isinstance(value, bool):
        return {"userEnteredValue": {"boolValue": value}}
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return {"userEnteredValue": {"numberValue": value}}
    if isinstance(value, str):
        return {"userEnteredValue": {"stringValue": value}}
    raise ValidationError(f"unsupported Google Sheets cell value type: {type(value).__name__}")


__all__ = [
    "WorkspaceBootstrapError",
    "WorkspaceBootstrapPlan",
    "WorkspaceIdempotencyRecord",
    "WorkspaceReadbackError",
    "WorkspaceUpsertPlan",
    "plan_workspace_bootstrap",
    "plan_workspace_upsert",
    "verify_workspace_bootstrap_readback",
    "verify_workspace_upsert_readback",
    "workspace_upsert_fingerprint",
]
