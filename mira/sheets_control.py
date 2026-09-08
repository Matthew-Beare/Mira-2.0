"""Provider-neutral Google Sheets operational control-surface contracts.

Sheets is a human-facing projection, review, correction, reconciliation and
prototyping surface over MIRROR. This module deliberately contains no
spreadsheet IDs, Google credentials, provider calls, or domain business rules.

Controlled edits are converted into revision-bound write-back plans. A caller
must execute those plans through the canonical MIRA authority path and verify
post-write readback; this module never mutates canonical state itself.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from enum import Enum
import json
import math
import re
from types import MappingProxyType
from typing import Mapping
from urllib.parse import urlsplit


_TOKEN_RE = re.compile(r"^[A-Za-z][A-Za-z0-9._:-]{0,127}$")
_COLUMN_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]{0,63}$")
_TECHNICAL_KEYS = frozenset(
    {
        "__mira_row_id",
        "__mira_revision",
        "__mira_read_at",
        "__mira_reconciliation_state",
    }
)


class SheetsControlError(Exception):
    """Base error for invalid Sheets control-surface definitions."""


class ProjectionValidationError(SheetsControlError):
    """Raised when a projection definition or record is malformed."""


class ProjectionRole(str, Enum):
    CANONICAL_READ_ONLY = "canonical_read_only_projection"
    CONTROLLED_EDITABLE = "controlled_editable_projection"
    DERIVED_ANALYTICAL = "derived_analytical_view"
    TEMPORARY_PROTOTYPE = "temporary_non_authoritative_prototype"
    RECONCILIATION_QUEUE = "reconciliation_queue"
    GENERATED_DASHBOARD = "generated_dashboard"


class ColumnKind(str, Enum):
    STRING = "string"
    INTEGER = "integer"
    NUMBER = "number"
    BOOLEAN = "boolean"
    DATE = "date"
    TIMESTAMP = "timestamp"
    URL = "url"
    ENUM = "enum"
    JSON = "json"


class ReconciliationStatus(str, Enum):
    READY = "ready"
    NO_CHANGE = "no_change"
    CONFLICT = "conflict"
    INVALID = "invalid"


@dataclass(frozen=True)
class ColumnSpec:
    key: str
    label: str
    kind: ColumnKind = ColumnKind.STRING
    editable: bool = False
    required: bool = False
    allowed_values: tuple[str, ...] = ()
    sensitive: bool = False

    def __post_init__(self) -> None:
        _column_key(self.key, "column key")
        _text(self.label, "column label")
        if self.key in _TECHNICAL_KEYS:
            raise ProjectionValidationError(
                f"{self.key} is reserved for MIRA technical projection state"
            )
        if not isinstance(self.kind, ColumnKind):
            try:
                object.__setattr__(self, "kind", ColumnKind(self.kind))
            except (TypeError, ValueError) as exc:
                raise ProjectionValidationError("invalid column kind") from exc
        values = tuple(_text(value, "allowed value") for value in self.allowed_values)
        if len(values) != len(set(values)):
            raise ProjectionValidationError("allowed_values must not contain duplicates")
        object.__setattr__(self, "allowed_values", values)
        if self.kind is ColumnKind.ENUM and not values:
            raise ProjectionValidationError("enum column requires allowed_values")
        if self.kind is not ColumnKind.ENUM and values:
            raise ProjectionValidationError(
                "allowed_values is only valid for enum columns"
            )

    def validate(self, value: object) -> str | None:
        """Return an error message for a user value, otherwise None."""
        if value is None or value == "":
            return "value is required" if self.required else None
        if self.kind is ColumnKind.STRING:
            return None if isinstance(value, str) else "value must be a string"
        if self.kind is ColumnKind.INTEGER:
            return (
                None
                if isinstance(value, int) and not isinstance(value, bool)
                else "value must be an integer"
            )
        if self.kind is ColumnKind.NUMBER:
            if (
                isinstance(value, (int, float))
                and not isinstance(value, bool)
                and math.isfinite(float(value))
            ):
                return None
            return "value must be a finite number"
        if self.kind is ColumnKind.BOOLEAN:
            return None if isinstance(value, bool) else "value must be a boolean"
        if self.kind is ColumnKind.DATE:
            if not isinstance(value, str):
                return "value must be an ISO date string"
            try:
                date.fromisoformat(value)
            except ValueError:
                return "value must be an ISO date string"
            return None
        if self.kind is ColumnKind.TIMESTAMP:
            return _timestamp_error(value)
        if self.kind is ColumnKind.URL:
            if not isinstance(value, str):
                return "value must be an http/https URL"
            parts = urlsplit(value.strip())
            return (
                None
                if value == value.strip()
                and parts.scheme in {"http", "https"}
                and bool(parts.netloc)
                else "value must be an http/https URL"
            )
        if self.kind is ColumnKind.ENUM:
            return (
                None
                if isinstance(value, str) and value in self.allowed_values
                else "value must be one of: " + ", ".join(self.allowed_values)
            )
        if self.kind is ColumnKind.JSON:
            try:
                json.dumps(value, allow_nan=False, sort_keys=True)
            except (TypeError, ValueError):
                return "value must be JSON-compatible"
            return None
        return "unsupported column kind"


@dataclass(frozen=True)
class PresentationSpec:
    """Provider-neutral hints for a rich Google Sheets renderer."""

    use_native_table: bool = True
    freeze_header_rows: int = 1
    filterable_columns: tuple[str, ...] = ()
    slicer_columns: tuple[str, ...] = ()
    group_by_columns: tuple[str, ...] = ()
    hyperlink_columns: tuple[str, ...] = ()
    conditional_status_columns: tuple[str, ...] = ()
    protect_technical_columns: bool = True
    hide_technical_columns: bool = True

    def __post_init__(self) -> None:
        if (
            not isinstance(self.freeze_header_rows, int)
            or isinstance(self.freeze_header_rows, bool)
            or self.freeze_header_rows < 0
            or self.freeze_header_rows > 10
        ):
            raise ProjectionValidationError(
                "freeze_header_rows must be an integer between 0 and 10"
            )
        for field_name in (
            "filterable_columns",
            "slicer_columns",
            "group_by_columns",
            "hyperlink_columns",
            "conditional_status_columns",
        ):
            values = tuple(
                _column_key(value, field_name) for value in getattr(self, field_name)
            )
            if len(values) != len(set(values)):
                raise ProjectionValidationError(f"{field_name} contains duplicates")
            object.__setattr__(self, field_name, values)


@dataclass(frozen=True)
class ProjectionDefinition:
    projection_id: str
    feature_id: str
    title: str
    role: ProjectionRole
    columns: tuple[ColumnSpec, ...]
    schema_version: int = 1
    canonical_resource_type: str | None = None
    writeback_action: str | None = None
    presentation: PresentationSpec = field(default_factory=PresentationSpec)

    def __post_init__(self) -> None:
        _token(self.projection_id, "projection_id")
        _token(self.feature_id, "feature_id")
        _text(self.title, "title")
        if not isinstance(self.role, ProjectionRole):
            try:
                object.__setattr__(self, "role", ProjectionRole(self.role))
            except (TypeError, ValueError) as exc:
                raise ProjectionValidationError("invalid projection role") from exc
        if (
            not isinstance(self.schema_version, int)
            or isinstance(self.schema_version, bool)
            or self.schema_version < 1
        ):
            raise ProjectionValidationError("schema_version must be a positive integer")
        columns = tuple(self.columns)
        if not columns:
            raise ProjectionValidationError("projection requires at least one column")
        if not all(isinstance(column, ColumnSpec) for column in columns):
            raise ProjectionValidationError("columns must contain ColumnSpec values")
        keys = [column.key for column in columns]
        if len(keys) != len(set(keys)):
            raise ProjectionValidationError("projection column keys must be unique")
        object.__setattr__(self, "columns", columns)

        if self.canonical_resource_type is not None:
            _token(self.canonical_resource_type, "canonical_resource_type")
        if self.writeback_action is not None:
            _token(self.writeback_action, "writeback_action")

        editable = tuple(column for column in columns if column.editable)
        if self.role in {
            ProjectionRole.CANONICAL_READ_ONLY,
            ProjectionRole.DERIVED_ANALYTICAL,
            ProjectionRole.GENERATED_DASHBOARD,
        } and editable:
            raise ProjectionValidationError(
                f"{self.role.value} cannot contain editable columns"
            )
        if self.role in {
            ProjectionRole.CONTROLLED_EDITABLE,
            ProjectionRole.RECONCILIATION_QUEUE,
        }:
            if not editable:
                raise ProjectionValidationError(
                    f"{self.role.value} requires at least one editable column"
                )
            if self.canonical_resource_type is None or self.writeback_action is None:
                raise ProjectionValidationError(
                    f"{self.role.value} requires canonical_resource_type and writeback_action"
                )
        elif self.writeback_action is not None:
            raise ProjectionValidationError(
                "writeback_action is only valid for controlled edit/reconciliation roles"
            )

        known = set(keys)
        for field_name in (
            "filterable_columns",
            "slicer_columns",
            "group_by_columns",
            "hyperlink_columns",
            "conditional_status_columns",
        ):
            unknown = set(getattr(self.presentation, field_name)) - known
            if unknown:
                raise ProjectionValidationError(
                    f"{field_name} references unknown columns: {', '.join(sorted(unknown))}"
                )

    @property
    def editable_columns(self) -> tuple[str, ...]:
        return tuple(column.key for column in self.columns if column.editable)

    @property
    def technical_column_keys(self) -> tuple[str, ...]:
        return (
            "__mira_row_id",
            "__mira_revision",
            "__mira_read_at",
            "__mira_reconciliation_state",
        )

    @property
    def headers(self) -> tuple[str, ...]:
        return tuple(column.label for column in self.columns) + (
            "MIRA Row ID",
            "MIRROR Revision",
            "MIRA Read At",
            "Reconciliation State",
        )

    def column(self, key: str) -> ColumnSpec | None:
        return next((column for column in self.columns if column.key == key), None)

    def public_manifest(self) -> dict[str, object]:
        """Return schema/presentation metadata; runtime bindings and row data are absent."""
        return {
            "projection_id": self.projection_id,
            "feature_id": self.feature_id,
            "title": self.title,
            "role": self.role.value,
            "schema_version": self.schema_version,
            "canonical_resource_type": self.canonical_resource_type,
            "writeback_action": self.writeback_action,
            "columns": [
                {
                    "key": column.key,
                    "label": column.label,
                    "kind": column.kind.value,
                    "editable": column.editable,
                    "required": column.required,
                    "allowed_values": list(column.allowed_values),
                    "sensitive": column.sensitive,
                }
                for column in self.columns
            ],
            "presentation": {
                "use_native_table": self.presentation.use_native_table,
                "freeze_header_rows": self.presentation.freeze_header_rows,
                "filterable_columns": list(self.presentation.filterable_columns),
                "slicer_columns": list(self.presentation.slicer_columns),
                "group_by_columns": list(self.presentation.group_by_columns),
                "hyperlink_columns": list(self.presentation.hyperlink_columns),
                "conditional_status_columns": list(
                    self.presentation.conditional_status_columns
                ),
                "protect_technical_columns": self.presentation.protect_technical_columns,
                "hide_technical_columns": self.presentation.hide_technical_columns,
            },
        }


@dataclass(frozen=True)
class FeatureSheetManifest:
    feature_id: str
    version: int
    projections: tuple[ProjectionDefinition, ...]
    dependencies: tuple[str, ...] = ()
    required_capabilities: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _token(self.feature_id, "feature_id")
        if (
            not isinstance(self.version, int)
            or isinstance(self.version, bool)
            or self.version < 1
        ):
            raise ProjectionValidationError("version must be a positive integer")
        projections = tuple(self.projections)
        if not projections:
            raise ProjectionValidationError("feature manifest requires projections")
        if any(item.feature_id != self.feature_id for item in projections):
            raise ProjectionValidationError(
                "every projection must belong to the manifest feature_id"
            )
        ids = [item.projection_id for item in projections]
        if len(ids) != len(set(ids)):
            raise ProjectionValidationError("projection IDs must be unique")
        object.__setattr__(self, "projections", projections)
        for field_name in ("dependencies", "required_capabilities"):
            values = tuple(_token(value, field_name) for value in getattr(self, field_name))
            if len(values) != len(set(values)):
                raise ProjectionValidationError(f"{field_name} contains duplicates")
            object.__setattr__(self, field_name, values)

    def public_manifest(self) -> dict[str, object]:
        return {
            "feature_id": self.feature_id,
            "version": self.version,
            "dependencies": list(self.dependencies),
            "required_capabilities": list(self.required_capabilities),
            "projections": [item.public_manifest() for item in self.projections],
        }


@dataclass(frozen=True)
class SheetRuntimeBinding:
    """Private runtime binding. Values from this object never enter public manifests."""

    projection_id: str
    spreadsheet_id: str
    sheet_title: str

    def __post_init__(self) -> None:
        _token(self.projection_id, "projection_id")
        _text(self.spreadsheet_id, "spreadsheet_id")
        _text(self.sheet_title, "sheet_title")


@dataclass(frozen=True)
class ProjectionRecord:
    row_id: str
    values: Mapping[str, object]
    read_at: str
    canonical_revision: int | None = None
    reconciliation_state: str = "clean"
    provenance: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _token(self.row_id, "row_id")
        if _timestamp_error(self.read_at) is not None:
            raise ProjectionValidationError("read_at must be an offset-aware ISO timestamp")
        if self.canonical_revision is not None and (
            not isinstance(self.canonical_revision, int)
            or isinstance(self.canonical_revision, bool)
            or self.canonical_revision < 1
        ):
            raise ProjectionValidationError(
                "canonical_revision must be a positive integer or None"
            )
        _token(self.reconciliation_state, "reconciliation_state")
        object.__setattr__(self, "values", MappingProxyType(dict(self.values)))
        object.__setattr__(
            self,
            "provenance",
            MappingProxyType(
                {
                    _column_key(key, "provenance field"): _text(value, "provenance value")
                    for key, value in self.provenance.items()
                }
            ),
        )

    def render(self, definition: ProjectionDefinition) -> tuple[object, ...]:
        errors = validate_projection_record(definition, self)
        if errors:
            raise ProjectionValidationError("; ".join(errors))
        return tuple(self.values.get(column.key, "") for column in definition.columns) + (
            self.row_id,
            self.canonical_revision if self.canonical_revision is not None else "",
            self.read_at,
            self.reconciliation_state,
        )


@dataclass(frozen=True)
class EditSubmission:
    row_id: str
    base_revision: int
    changes: Mapping[str, object]
    submitted_at: str
    actor_ref: str = "same_user"

    def __post_init__(self) -> None:
        _token(self.row_id, "row_id")
        if (
            not isinstance(self.base_revision, int)
            or isinstance(self.base_revision, bool)
            or self.base_revision < 1
        ):
            raise ProjectionValidationError("base_revision must be a positive integer")
        if not isinstance(self.changes, Mapping) or not self.changes:
            raise ProjectionValidationError("changes must be a non-empty mapping")
        if _timestamp_error(self.submitted_at) is not None:
            raise ProjectionValidationError(
                "submitted_at must be an offset-aware ISO timestamp"
            )
        _token(self.actor_ref, "actor_ref")
        object.__setattr__(self, "changes", MappingProxyType(dict(self.changes)))


@dataclass(frozen=True)
class WriteBackPlan:
    projection_id: str
    feature_id: str
    canonical_resource_type: str
    resource_id: str
    operation: str
    expected_revision: int
    changes: Mapping[str, object]
    submitted_at: str
    actor_ref: str
    provenance_source: str = "google_sheets_controlled_edit"

    def __post_init__(self) -> None:
        object.__setattr__(self, "changes", MappingProxyType(dict(self.changes)))


@dataclass(frozen=True)
class EditReconciliation:
    status: ReconciliationStatus
    plan: WriteBackPlan | None = None
    errors: tuple[str, ...] = ()


def validate_projection_record(
    definition: ProjectionDefinition, record: ProjectionRecord
) -> tuple[str, ...]:
    errors: list[str] = []
    known = {column.key for column in definition.columns}
    unknown = set(record.values) - known
    if unknown:
        errors.append("unknown projection fields: " + ", ".join(sorted(unknown)))
    for column in definition.columns:
        value = record.values.get(column.key)
        error = column.validate(value)
        if error:
            errors.append(f"{column.key}: {error}")
    if definition.role in {
        ProjectionRole.CANONICAL_READ_ONLY,
        ProjectionRole.CONTROLLED_EDITABLE,
        ProjectionRole.RECONCILIATION_QUEUE,
    } and record.canonical_revision is None:
        errors.append(f"{definition.role.value} requires canonical_revision")
    return tuple(errors)


def reconcile_edit(
    definition: ProjectionDefinition,
    current: ProjectionRecord,
    submission: EditSubmission,
) -> EditReconciliation:
    """Validate a human edit and produce a canonical revision-bound write plan."""
    if definition.role not in {
        ProjectionRole.CONTROLLED_EDITABLE,
        ProjectionRole.RECONCILIATION_QUEUE,
    }:
        return EditReconciliation(
            ReconciliationStatus.INVALID,
            errors=("projection role does not permit canonical write-back",),
        )
    if submission.row_id != current.row_id:
        return EditReconciliation(
            ReconciliationStatus.INVALID,
            errors=("submitted row identity does not match projected row",),
        )
    record_errors = validate_projection_record(definition, current)
    if record_errors:
        return EditReconciliation(ReconciliationStatus.INVALID, errors=record_errors)
    if current.canonical_revision != submission.base_revision:
        return EditReconciliation(
            ReconciliationStatus.CONFLICT,
            errors=(
                "MIRROR revision changed since this row was read; refresh and reconcile",
            ),
        )

    accepted: dict[str, object] = {}
    errors: list[str] = []
    for key, value in submission.changes.items():
        if key in _TECHNICAL_KEYS:
            errors.append(f"{key}: technical projection state is not user-editable")
            continue
        column = definition.column(key)
        if column is None:
            errors.append(f"{key}: unknown projection field")
            continue
        if not column.editable:
            errors.append(f"{key}: field is read-only")
            continue
        error = column.validate(value)
        if error:
            errors.append(f"{key}: {error}")
            continue
        if current.values.get(key) != value:
            accepted[key] = value

    if errors:
        return EditReconciliation(
            ReconciliationStatus.INVALID, errors=tuple(errors)
        )
    if not accepted:
        return EditReconciliation(ReconciliationStatus.NO_CHANGE)

    assert definition.canonical_resource_type is not None
    assert definition.writeback_action is not None
    return EditReconciliation(
        ReconciliationStatus.READY,
        plan=WriteBackPlan(
            projection_id=definition.projection_id,
            feature_id=definition.feature_id,
            canonical_resource_type=definition.canonical_resource_type,
            resource_id=current.row_id,
            operation=definition.writeback_action,
            expected_revision=submission.base_revision,
            changes=accepted,
            submitted_at=submission.submitted_at,
            actor_ref=submission.actor_ref,
        ),
    )


def validate_public_manifest(manifest: Mapping[str, object]) -> tuple[str, ...]:
    """Reject runtime-binding/private-value keys from a public feature package."""
    forbidden_fragments = (
        "spreadsheet_id",
        "drive_id",
        "account_id",
        "credential",
        "access_token",
        "refresh_token",
        "api_key",
        "private_value",
    )
    errors: list[str] = []

    def walk(value: object, path: str) -> None:
        if isinstance(value, Mapping):
            for key, item in value.items():
                key_text = str(key)
                normalized = key_text.lower()
                if any(fragment in normalized for fragment in forbidden_fragments):
                    errors.append(f"{path}{key_text}: forbidden private/runtime key")
                walk(item, f"{path}{key_text}.")
        elif isinstance(value, (list, tuple)):
            for index, item in enumerate(value):
                walk(item, f"{path}[{index}].")

    walk(manifest, "")
    return tuple(errors)


def _token(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not _TOKEN_RE.fullmatch(value):
        raise ProjectionValidationError(
            f"{field_name} must match {_TOKEN_RE.pattern}"
        )
    return value


def _column_key(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not _COLUMN_RE.fullmatch(value):
        raise ProjectionValidationError(
            f"{field_name} must match {_COLUMN_RE.pattern}"
        )
    return value


def _text(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise ProjectionValidationError(
            f"{field_name} must be a non-empty trimmed string"
        )
    return value


def _timestamp_error(value: object) -> str | None:
    if not isinstance(value, str) or not value or value != value.strip():
        return "value must be an offset-aware ISO timestamp"
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return "value must be an offset-aware ISO timestamp"
    if parsed.tzinfo is None:
        return "value must be an offset-aware ISO timestamp"
    parsed.astimezone(timezone.utc)
    return None


__all__ = [
    "ColumnKind",
    "ColumnSpec",
    "EditReconciliation",
    "EditSubmission",
    "FeatureSheetManifest",
    "PresentationSpec",
    "ProjectionDefinition",
    "ProjectionRecord",
    "ProjectionRole",
    "ProjectionValidationError",
    "ReconciliationStatus",
    "SheetRuntimeBinding",
    "SheetsControlError",
    "WriteBackPlan",
    "reconcile_edit",
    "validate_projection_record",
    "validate_public_manifest",
]
