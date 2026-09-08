"""Deterministic tests for Google Sheets control-surface request planning."""

from __future__ import annotations

import unittest

from mira.google_sheets_surface import build_surface_plan
from mira.sheets_control import (
    ColumnKind,
    ColumnSpec,
    PresentationSpec,
    ProjectionDefinition,
    ProjectionRole,
    ProjectionValidationError,
)


class GoogleSheetsSurfaceTests(unittest.TestCase):
    def test_controlled_surface_contains_table_metadata_validation_and_technical_guards(self) -> None:
        definition = ProjectionDefinition(
            projection_id="finance_transactions",
            feature_id="FIN-OPS-001",
            title="Finance Transactions",
            role=ProjectionRole.CONTROLLED_EDITABLE,
            canonical_resource_type="finance_transaction",
            writeback_action="classify_transaction",
            columns=(
                ColumnSpec("merchant", "Merchant"),
                ColumnSpec("amount", "Amount", kind=ColumnKind.NUMBER),
                ColumnSpec(
                    "drawdown_category",
                    "Drawdown Category",
                    kind=ColumnKind.ENUM,
                    editable=True,
                    allowed_values=("core", "reserve", "discretionary"),
                ),
                ColumnSpec(
                    "necessity",
                    "Necessary vs Unnecessary",
                    kind=ColumnKind.ENUM,
                    editable=True,
                    allowed_values=("necessary", "unnecessary"),
                ),
            ),
            presentation=PresentationSpec(
                filterable_columns=("drawdown_category", "necessity"),
                slicer_columns=("drawdown_category", "necessity"),
            ),
        )

        plan = build_surface_plan(definition, sheet_id=123, max_data_rows=500)
        requests = list(plan.requests)

        self.assertEqual(plan.table_name, "mira_finance_transactions")
        self.assertEqual(plan.sheet_id, 123)
        self.assertEqual(
            dict(plan.metadata),
            {
                "mira.feature_id": "FIN-OPS-001",
                "mira.projection_id": "finance_transactions",
                "mira.schema_version": "1",
                "mira.projection_role": "controlled_editable_projection",
            },
        )

        header = requests[0]["updateCells"]
        values = header["rows"][0]["values"]
        self.assertEqual(len(values), 8)
        self.assertEqual(
            values[0]["userEnteredValue"]["stringValue"], "Merchant"
        )
        self.assertEqual(
            values[-1]["userEnteredValue"]["stringValue"],
            "Reconciliation State",
        )

        validation_requests = [
            request["setDataValidation"]
            for request in requests
            if "setDataValidation" in request
        ]
        self.assertEqual(len(validation_requests), 2)
        allowed = {
            value["userEnteredValue"]
            for value in validation_requests[0]["rule"]["condition"]["values"]
        }
        self.assertEqual(allowed, {"core", "reserve", "discretionary"})
        self.assertTrue(validation_requests[0]["rule"]["strict"])

        metadata_requests = [
            request["createDeveloperMetadata"]
            for request in requests
            if "createDeveloperMetadata" in request
        ]
        self.assertEqual(len(metadata_requests), 4)
        self.assertTrue(
            all(
                item["developerMetadata"]["location"] == {"sheetId": 123}
                for item in metadata_requests
            )
        )

        hidden = next(
            request["updateDimensionProperties"]
            for request in requests
            if "updateDimensionProperties" in request
        )
        self.assertEqual(hidden["range"]["startIndex"], 4)
        self.assertEqual(hidden["range"]["endIndex"], 8)
        self.assertTrue(hidden["properties"]["hiddenByUser"])

        protected = next(
            request["addProtectedRange"]["protectedRange"]
            for request in requests
            if "addProtectedRange" in request
        )
        self.assertTrue(protected["warningOnly"])
        self.assertEqual(protected["range"]["startColumnIndex"], 4)

        table = next(
            request["addTable"]["table"]
            for request in requests
            if "addTable" in request
        )
        self.assertEqual(table["name"], "mira_finance_transactions")
        self.assertEqual(table["range"]["endRowIndex"], 501)
        self.assertEqual(
            [column["columnType"] for column in table["columnProperties"][:4]],
            ["TEXT", "DOUBLE", "TEXT", "TEXT"],
        )
        self.assertEqual(
            [column["columnType"] for column in table["columnProperties"][-4:]],
            ["TEXT", "DOUBLE", "DATE_TIME", "TEXT"],
        )

    def test_read_only_surface_adds_no_user_validation(self) -> None:
        definition = ProjectionDefinition(
            projection_id="mira_ops",
            feature_id="OBS-001",
            title="MIRA Operations",
            role=ProjectionRole.CANONICAL_READ_ONLY,
            canonical_resource_type="work_packet",
            columns=(
                ColumnSpec("packet", "Packet"),
                ColumnSpec("status", "Status", kind=ColumnKind.STRING),
            ),
        )

        plan = build_surface_plan(definition, sheet_id=0, max_data_rows=25)

        self.assertFalse(any("setDataValidation" in item for item in plan.requests))
        self.assertTrue(any("addTable" in item for item in plan.requests))

    def test_boolean_and_date_edit_validation_maps_to_google_conditions(self) -> None:
        definition = ProjectionDefinition(
            projection_id="editable_dates",
            feature_id="SHEETS-001",
            title="Editable Dates",
            role=ProjectionRole.CONTROLLED_EDITABLE,
            canonical_resource_type="synthetic",
            writeback_action="synthetic_edit",
            columns=(
                ColumnSpec("flag", "Flag", kind=ColumnKind.BOOLEAN, editable=True),
                ColumnSpec("due", "Due", kind=ColumnKind.DATE, editable=True),
            ),
        )

        plan = build_surface_plan(definition, sheet_id=1)
        condition_types = [
            item["setDataValidation"]["rule"]["condition"]["type"]
            for item in plan.requests
            if "setDataValidation" in item
        ]

        self.assertEqual(condition_types, ["BOOLEAN", "DATE_IS_VALID"])

    def test_restricted_technical_columns_require_runtime_editors(self) -> None:
        definition = self._minimal_editable_definition()
        with self.assertRaisesRegex(
            ProjectionValidationError,
            "requires at least one runtime editor email",
        ):
            build_surface_plan(
                definition,
                sheet_id=10,
                technical_protection="restrict",
            )

        plan = build_surface_plan(
            definition,
            sheet_id=10,
            technical_protection="restrict",
            protection_editor_emails=("owner@example.com",),
        )
        protected = next(
            request["addProtectedRange"]["protectedRange"]
            for request in plan.requests
            if "addProtectedRange" in request
        )
        self.assertFalse(protected["warningOnly"])
        self.assertEqual(protected["editors"]["users"], ["owner@example.com"])

    def test_native_table_can_be_disabled(self) -> None:
        definition = ProjectionDefinition(
            projection_id="prototype",
            feature_id="SHEETS-PROTOTYPE-001",
            title="Prototype",
            role=ProjectionRole.TEMPORARY_PROTOTYPE,
            columns=(ColumnSpec("idea", "Idea", editable=True),),
            presentation=PresentationSpec(use_native_table=False),
        )

        plan = build_surface_plan(definition, sheet_id=2)

        self.assertIsNone(plan.table_name)
        self.assertFalse(any("addTable" in item for item in plan.requests))

    def test_table_name_is_deterministically_sanitized(self) -> None:
        plan = build_surface_plan(
            self._minimal_editable_definition(),
            sheet_id=3,
            table_name="2026 finance / intake!",
        )
        self.assertEqual(plan.table_name, "mira_2026_finance_intake")

    def test_invalid_row_reservation_fails_closed(self) -> None:
        with self.assertRaisesRegex(ProjectionValidationError, "max_data_rows"):
            build_surface_plan(
                self._minimal_editable_definition(),
                sheet_id=3,
                max_data_rows=0,
            )

    @staticmethod
    def _minimal_editable_definition() -> ProjectionDefinition:
        return ProjectionDefinition(
            projection_id="synthetic_editable",
            feature_id="SHEETS-001",
            title="Synthetic Editable",
            role=ProjectionRole.CONTROLLED_EDITABLE,
            canonical_resource_type="synthetic",
            writeback_action="synthetic_edit",
            columns=(ColumnSpec("note", "Note", editable=True),),
        )


if __name__ == "__main__":
    unittest.main()
