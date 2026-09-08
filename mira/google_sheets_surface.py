"""Render provider-neutral MIRA Sheets control definitions into Google batchUpdate plans.

This module is intentionally a request planner, not a provider client. It turns a
validated ``ProjectionDefinition`` into deterministic Google Sheets API request
shapes for headers, native tables, validation, technical-column protection,
visibility, and developer metadata. Runtime spreadsheet IDs remain outside public
feature manifests and provider execution/readback stays in the caller.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Mapping, Sequence

from .sheets_control import (
    ColumnKind,
    ColumnSpec,
    ProjectionDefinition,
    ProjectionValidationError,
)


_TABLE_NAME_RE = re.compile(r"[^A-Za-z0-9_]+")


@dataclass(frozen=True)
class GoogleSheetSurfacePlan:
    sheet_id: int
    max_data_rows: int
    table_name: str | None
    metadata: tuple[tuple[str, str], ...]
    requests: tuple[Mapping[str, object], ...]

    def __post_init__(self) -> None:
        _sheet_id(self.sheet_id)
        _row_count(self.max_data_rows)
        if self.table_name is not None:
            _table_name(self.table_name)
        object.__setattr__(self, "metadata", tuple(self.metadata))
        object.__setattr__(self, "requests", tuple(self.requests))


def build_surface_plan(
    definition: ProjectionDefinition,
    *,
    sheet_id: int,
    max_data_rows: int = 1000,
    table_name: str | None = None,
    technical_protection: str = "warning",
    protection_editor_emails: Sequence[str] = (),
) -> GoogleSheetSurfacePlan:
    """Create one deterministic Sheets ``batchUpdate`` plan.

    ``max_data_rows`` reserves an operational region for validation/protection/table
    behavior; it is not a claim that those rows currently contain canonical data.

    Technical protection defaults to ``warning`` because a reusable public feature
    cannot know the private owner's/editor identities. ``restrict`` is allowed only
    when explicit runtime editor emails are supplied by the caller.
    """

    if not isinstance(definition, ProjectionDefinition):
        raise ProjectionValidationError("definition must be a ProjectionDefinition")
    _sheet_id(sheet_id)
    _row_count(max_data_rows)
    if technical_protection not in {"warning", "restrict"}:
        raise ProjectionValidationError(
            "technical_protection must be 'warning' or 'restrict'"
        )
    editors = tuple(_email(value) for value in protection_editor_emails)
    if technical_protection == "restrict" and not editors:
        raise ProjectionValidationError(
            "restricted technical protection requires at least one runtime editor email"
        )

    width = len(definition.columns) + len(definition.technical_column_keys)
    body_end_row = max_data_rows + 1
    technical_start = len(definition.columns)
    metadata = (
        ("mira.feature_id", definition.feature_id),
        ("mira.projection_id", definition.projection_id),
        ("mira.schema_version", str(definition.schema_version)),
        ("mira.projection_role", definition.role.value),
    )

    requests: list[dict[str, object]] = [
        _header_request(definition, sheet_id=sheet_id),
        {
            "updateSheetProperties": {
                "properties": {
                    "sheetId": sheet_id,
                    "gridProperties": {
                        "frozenRowCount": definition.presentation.freeze_header_rows
                    },
                },
                "fields": "gridProperties.frozenRowCount",
            }
        },
        {
            "repeatCell": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": 0,
                    "endRowIndex": 1,
                    "startColumnIndex": 0,
                    "endColumnIndex": width,
                },
                "cell": {
                    "userEnteredFormat": {
                        "textFormat": {"bold": True},
                        "wrapStrategy": "WRAP",
                    }
                },
                "fields": "userEnteredFormat(textFormat.bold,wrapStrategy)",
            }
        },
    ]

    for index, column in enumerate(definition.columns):
        validation = _validation_rule(column)
        if column.editable and validation is not None:
            requests.append(
                {
                    "setDataValidation": {
                        "range": {
                            "sheetId": sheet_id,
                            "startRowIndex": 1,
                            "endRowIndex": body_end_row,
                            "startColumnIndex": index,
                            "endColumnIndex": index + 1,
                        },
                        "rule": validation,
                    }
                }
            )

    for key, value in metadata:
        requests.append(
            {
                "createDeveloperMetadata": {
                    "developerMetadata": {
                        "metadataKey": key,
                        "metadataValue": value,
                        "visibility": "DOCUMENT",
                        "location": {"sheetId": sheet_id},
                    }
                }
            }
        )

    if definition.presentation.hide_technical_columns:
        requests.append(
            {
                "updateDimensionProperties": {
                    "range": {
                        "sheetId": sheet_id,
                        "dimension": "COLUMNS",
                        "startIndex": technical_start,
                        "endIndex": width,
                    },
                    "properties": {"hiddenByUser": True},
                    "fields": "hiddenByUser",
                }
            }
        )

    if definition.presentation.protect_technical_columns:
        protected_range: dict[str, object] = {
            "range": {
                "sheetId": sheet_id,
                "startRowIndex": 0,
                "endRowIndex": body_end_row,
                "startColumnIndex": technical_start,
                "endColumnIndex": width,
            },
            "description": (
                "MIRA technical identity/revision/readback columns. "
                "Do not edit directly."
            ),
        }
        if technical_protection == "warning":
            protected_range["warningOnly"] = True
        else:
            protected_range["warningOnly"] = False
            protected_range["editors"] = {"users": list(editors)}
        requests.append({"addProtectedRange": {"protectedRange": protected_range}})

    resolved_table_name: str | None = None
    if definition.presentation.use_native_table:
        resolved_table_name = _table_name(
            table_name or f"mira_{definition.projection_id}"
        )
        requests.append(
            {
                "addTable": {
                    "table": {
                        "name": resolved_table_name,
                        "range": {
                            "sheetId": sheet_id,
                            "startRowIndex": 0,
                            "endRowIndex": body_end_row,
                            "startColumnIndex": 0,
                            "endColumnIndex": width,
                        },
                        "columnProperties": [
                            _table_column(column)
                            for column in definition.columns
                        ]
                        + _technical_table_columns(),
                    }
                }
            }
        )

    return GoogleSheetSurfacePlan(
        sheet_id=sheet_id,
        max_data_rows=max_data_rows,
        table_name=resolved_table_name,
        metadata=metadata,
        requests=tuple(requests),
    )


def _header_request(
    definition: ProjectionDefinition, *, sheet_id: int
) -> dict[str, object]:
    return {
        "updateCells": {
            "start": {"sheetId": sheet_id, "rowIndex": 0, "columnIndex": 0},
            "rows": [
                {
                    "values": [
                        {"userEnteredValue": {"stringValue": header}}
                        for header in definition.headers
                    ]
                }
            ],
            "fields": "userEnteredValue",
        }
    }


def _validation_rule(column: ColumnSpec) -> dict[str, object] | None:
    if column.kind is ColumnKind.ENUM:
        return {
            "condition": {
                "type": "ONE_OF_LIST",
                "values": [
                    {"userEnteredValue": value}
                    for value in column.allowed_values
                ],
            },
            "strict": True,
            "showCustomUi": True,
        }
    if column.kind is ColumnKind.BOOLEAN:
        return {
            "condition": {"type": "BOOLEAN"},
            "strict": True,
            "showCustomUi": True,
        }
    if column.kind is ColumnKind.DATE:
        return {
            "condition": {"type": "DATE_IS_VALID"},
            "strict": True,
            "showCustomUi": True,
        }
    return None


def _table_column(column: ColumnSpec) -> dict[str, object]:
    return {
        "name": column.label,
        "columnType": _table_column_type(column.kind),
    }


def _technical_table_columns() -> list[dict[str, object]]:
    return [
        {"name": "MIRA Row ID", "columnType": "TEXT"},
        {"name": "MIRROR Revision", "columnType": "DOUBLE"},
        {"name": "MIRA Read At", "columnType": "DATE_TIME"},
        {"name": "Reconciliation State", "columnType": "TEXT"},
    ]


def _table_column_type(kind: ColumnKind) -> str:
    if kind in {ColumnKind.INTEGER, ColumnKind.NUMBER}:
        return "DOUBLE"
    if kind is ColumnKind.DATE:
        return "DATE"
    if kind is ColumnKind.TIMESTAMP:
        return "DATE_TIME"
    if kind is ColumnKind.BOOLEAN:
        return "BOOLEAN"
    return "TEXT"


def _table_name(value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ProjectionValidationError("table_name must be a non-empty string")
    name = _TABLE_NAME_RE.sub("_", value.strip())
    name = re.sub(r"_+", "_", name).strip("_")
    if not name:
        raise ProjectionValidationError("table_name contains no usable characters")
    if name[0].isdigit():
        name = "mira_" + name
    if len(name) > 80:
        name = name[:80].rstrip("_")
    return name


def _sheet_id(value: object) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ProjectionValidationError("sheet_id must be a non-negative integer")
    return value


def _row_count(value: object) -> int:
    if (
        not isinstance(value, int)
        or isinstance(value, bool)
        or value < 1
        or value > 100_000
    ):
        raise ProjectionValidationError(
            "max_data_rows must be an integer between 1 and 100000"
        )
    return value


def _email(value: object) -> str:
    if not isinstance(value, str) or value != value.strip():
        raise ProjectionValidationError("protection editor email must be trimmed")
    local, separator, domain = value.partition("@")
    if not separator or not local or "." not in domain or domain.startswith("."):
        raise ProjectionValidationError("invalid protection editor email")
    return value


__all__ = ["GoogleSheetSurfacePlan", "build_surface_plan"]
