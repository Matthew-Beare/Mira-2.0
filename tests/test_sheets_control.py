"""Deterministic tests for the shared Sheets operational control-surface core."""

from __future__ import annotations

import json
import unittest

from mira.sheets_control import (
    ColumnKind,
    ColumnSpec,
    EditSubmission,
    FeatureSheetManifest,
    PresentationSpec,
    ProjectionDefinition,
    ProjectionRecord,
    ProjectionRole,
    ProjectionValidationError,
    ReconciliationStatus,
    SheetRuntimeBinding,
    reconcile_edit,
    validate_public_manifest,
)


class SheetsControlTests(unittest.TestCase):
    def test_controlled_edit_produces_revision_bound_plan(self) -> None:
        definition = self._people_definition()
        current = ProjectionRecord(
            row_id="person-001",
            values={
                "name": "Ada Example",
                "employer": "Synthetic Networks",
                "profile_url": "https://example.invalid/ada",
                "next_action": "",
                "relationship_status": "not_contacted",
            },
            read_at="2026-09-08T12:00:00Z",
            canonical_revision=3,
        )
        submission = EditSubmission(
            row_id="person-001",
            base_revision=3,
            changes={"relationship_status": "contacted"},
            submitted_at="2026-09-08T12:05:00Z",
        )

        result = reconcile_edit(definition, current, submission)

        self.assertEqual(result.status, ReconciliationStatus.READY)
        self.assertIsNotNone(result.plan)
        assert result.plan is not None
        self.assertEqual(result.plan.expected_revision, 3)
        self.assertEqual(result.plan.resource_id, "person-001")
        self.assertEqual(
            dict(result.plan.changes), {"relationship_status": "contacted"}
        )
        self.assertEqual(
            result.plan.provenance_source, "google_sheets_controlled_edit"
        )

    def test_stale_edit_fails_closed_as_conflict(self) -> None:
        definition = self._people_definition()
        current = ProjectionRecord(
            row_id="person-001",
            values={
                "name": "Ada Example",
                "employer": "Synthetic Networks",
                "profile_url": "",
                "next_action": "",
                "relationship_status": "not_contacted",
            },
            read_at="2026-09-08T12:00:00Z",
            canonical_revision=4,
        )
        submission = EditSubmission(
            row_id="person-001",
            base_revision=3,
            changes={"relationship_status": "contacted"},
            submitted_at="2026-09-08T12:05:00Z",
        )

        result = reconcile_edit(definition, current, submission)

        self.assertEqual(result.status, ReconciliationStatus.CONFLICT)
        self.assertIsNone(result.plan)
        self.assertIn("MIRROR revision changed", result.errors[0])

    def test_read_only_and_prototype_surfaces_cannot_write_mirror(self) -> None:
        read_only = ProjectionDefinition(
            projection_id="ops_status",
            feature_id="OBS-001",
            title="MIRA Operations",
            role=ProjectionRole.CANONICAL_READ_ONLY,
            columns=(ColumnSpec("packet", "Packet"),),
            canonical_resource_type="work_packet",
        )
        read_only_record = ProjectionRecord(
            row_id="packet-001",
            values={"packet": "M2-M1-020"},
            read_at="2026-09-08T12:00:00Z",
            canonical_revision=1,
        )
        read_only_edit = EditSubmission(
            row_id="packet-001",
            base_revision=1,
            changes={"packet": "fake"},
            submitted_at="2026-09-08T12:05:00Z",
        )
        self.assertEqual(
            reconcile_edit(read_only, read_only_record, read_only_edit).status,
            ReconciliationStatus.INVALID,
        )

        prototype = ProjectionDefinition(
            projection_id="prototype_fields",
            feature_id="SHEETS-PROTOTYPE-001",
            title="Prototype Fields",
            role=ProjectionRole.TEMPORARY_PROTOTYPE,
            columns=(ColumnSpec("idea", "Idea", editable=True),),
        )
        prototype_record = ProjectionRecord(
            row_id="proto-001",
            values={"idea": "Try this"},
            read_at="2026-09-08T12:00:00Z",
        )
        prototype_edit = EditSubmission(
            row_id="proto-001",
            base_revision=1,
            changes={"idea": "Try that"},
            submitted_at="2026-09-08T12:05:00Z",
        )
        result = reconcile_edit(prototype, prototype_record, prototype_edit)
        self.assertEqual(result.status, ReconciliationStatus.INVALID)
        self.assertEqual(
            prototype.public_manifest()["role"],
            "temporary_non_authoritative_prototype",
        )

    def test_disallowed_and_invalid_user_fields_are_rejected(self) -> None:
        definition = self._people_definition()
        current = ProjectionRecord(
            row_id="person-001",
            values={
                "name": "Ada Example",
                "employer": "Synthetic Networks",
                "profile_url": "",
                "next_action": "",
                "relationship_status": "not_contacted",
            },
            read_at="2026-09-08T12:00:00Z",
            canonical_revision=1,
        )
        submission = EditSubmission(
            row_id="person-001",
            base_revision=1,
            changes={
                "relationship_status": "invented_status",
                "employer": "Human tries to overwrite provider truth",
                "__mira_revision": 999,
            },
            submitted_at="2026-09-08T12:05:00Z",
        )

        result = reconcile_edit(definition, current, submission)

        self.assertEqual(result.status, ReconciliationStatus.INVALID)
        self.assertIsNone(result.plan)
        self.assertTrue(any("relationship_status" in error for error in result.errors))
        self.assertTrue(any("employer" in error for error in result.errors))
        self.assertTrue(any("__mira_revision" in error for error in result.errors))

    def test_identical_edit_produces_zero_write_plan(self) -> None:
        definition = self._people_definition()
        current = ProjectionRecord(
            row_id="person-001",
            values={
                "name": "Ada Example",
                "employer": "Synthetic Networks",
                "profile_url": "",
                "next_action": "Follow up Friday",
                "relationship_status": "contacted",
            },
            read_at="2026-09-08T12:00:00Z",
            canonical_revision=7,
        )
        submission = EditSubmission(
            row_id="person-001",
            base_revision=7,
            changes={"next_action": "Follow up Friday"},
            submitted_at="2026-09-08T12:05:00Z",
        )

        result = reconcile_edit(definition, current, submission)

        self.assertEqual(result.status, ReconciliationStatus.NO_CHANGE)
        self.assertIsNone(result.plan)

    def test_two_domains_share_one_contract_and_finance_dimensions_stay_distinct(self) -> None:
        people = self._people_definition()
        finance = ProjectionDefinition(
            projection_id="finance_transactions",
            feature_id="FIN-OPS-001",
            title="Finance Transactions",
            role=ProjectionRole.CONTROLLED_EDITABLE,
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
            canonical_resource_type="finance_transaction",
            writeback_action="classify_transaction",
            presentation=PresentationSpec(
                filterable_columns=("drawdown_category", "necessity"),
                slicer_columns=("drawdown_category", "necessity"),
                conditional_status_columns=("necessity",),
            ),
        )
        finance_record = ProjectionRecord(
            row_id="transaction-001",
            values={
                "merchant": "Synthetic Fuel",
                "amount": 42.0,
                "drawdown_category": "core",
                "necessity": "necessary",
            },
            read_at="2026-09-08T12:00:00Z",
            canonical_revision=2,
        )
        finance_edit = EditSubmission(
            row_id="transaction-001",
            base_revision=2,
            changes={
                "drawdown_category": "discretionary",
                "necessity": "unnecessary",
            },
            submitted_at="2026-09-08T12:05:00Z",
        )

        result = reconcile_edit(finance, finance_record, finance_edit)

        self.assertEqual(
            set(finance.editable_columns), {"drawdown_category", "necessity"}
        )
        self.assertEqual(result.status, ReconciliationStatus.READY)
        assert result.plan is not None
        self.assertEqual(
            dict(result.plan.changes),
            {
                "drawdown_category": "discretionary",
                "necessity": "unnecessary",
            },
        )
        self.assertEqual(people.role, finance.role)

    def test_feature_manifest_is_sanitized_and_runtime_binding_is_separate(self) -> None:
        definition = self._people_definition()
        feature = FeatureSheetManifest(
            feature_id="CAREER-PEOPLE-001",
            version=1,
            projections=(definition,),
            dependencies=("CAREER-001",),
            required_capabilities=("google_sheets.read", "google_sheets.write"),
        )
        binding = SheetRuntimeBinding(
            projection_id="career_people",
            spreadsheet_id="private-runtime-spreadsheet-id",
            sheet_title="People",
        )

        public_manifest = feature.public_manifest()

        self.assertEqual(validate_public_manifest(public_manifest), ())
        self.assertNotIn(binding.spreadsheet_id, json.dumps(public_manifest))
        self.assertNotIn("spreadsheet_id", public_manifest)

    def test_public_manifest_validator_rejects_private_runtime_keys(self) -> None:
        errors = validate_public_manifest(
            {
                "feature_id": "SYNTHETIC-001",
                "runtime": {
                    "spreadsheet_id": "private",
                    "api_key": "also-private",
                },
            }
        )
        self.assertEqual(len(errors), 2)

    def test_presentation_columns_must_exist(self) -> None:
        with self.assertRaisesRegex(
            ProjectionValidationError, "references unknown columns"
        ):
            ProjectionDefinition(
                projection_id="bad_projection",
                feature_id="SHEETS-001",
                title="Bad Projection",
                role=ProjectionRole.CANONICAL_READ_ONLY,
                columns=(ColumnSpec("name", "Name"),),
                canonical_resource_type="entity",
                presentation=PresentationSpec(filterable_columns=("missing",)),
            )

    @staticmethod
    def _people_definition() -> ProjectionDefinition:
        return ProjectionDefinition(
            projection_id="career_people",
            feature_id="CAREER-PEOPLE-001",
            title="People Discovery",
            role=ProjectionRole.CONTROLLED_EDITABLE,
            canonical_resource_type="career_person",
            writeback_action="career_person_edit",
            columns=(
                ColumnSpec("name", "Name", required=True),
                ColumnSpec("employer", "Employer", required=True),
                ColumnSpec("profile_url", "Profile", kind=ColumnKind.URL),
                ColumnSpec("next_action", "Next Action", editable=True),
                ColumnSpec(
                    "relationship_status",
                    "Relationship Status",
                    kind=ColumnKind.ENUM,
                    editable=True,
                    allowed_values=(
                        "not_contacted",
                        "contacted",
                        "replied",
                        "conversation",
                    ),
                ),
            ),
            presentation=PresentationSpec(
                filterable_columns=("employer", "relationship_status"),
                slicer_columns=("relationship_status",),
                hyperlink_columns=("profile_url",),
                conditional_status_columns=("relationship_status",),
            ),
        )


if __name__ == "__main__":
    unittest.main()
