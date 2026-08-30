"""Direct verification for the Google Workspace first-run bundle."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from mira.workspace_bundle import (
    WorkspaceBundleError,
    load_workspace_bundle,
    validate_workspace_bundle,
)


class WorkspaceBundleTests(unittest.TestCase):
    def test_repository_bundle_loads_and_declares_browser_initializer(self) -> None:
        bundle = load_workspace_bundle()
        code = bundle.file("Code.gs")
        self.assertIn("MIRA_SPREADSHEET_ID", code)
        self.assertIn("SpreadsheetApp.getActiveSpreadsheet", code)
        self.assertIn("SpreadsheetApp.openById", code)
        self.assertIn("/v1/health", code)
        self.assertIn("/v1/schema", code)
        self.assertIn("/v1/query", code)
        self.assertIn("/v1/commands", code)
        self.assertIn("not_implemented", code)

    def test_repository_bundle_contains_complete_no_app_protocol(self) -> None:
        bundle = load_workspace_bundle()
        protocol = bundle.file("MIRA_NO_APP_INSTRUCTIONS.md")
        self.assertIn("Replace the existing Personal MIRA operating-instruction block", protocol)
        self.assertIn("Never ask the user to rename MIRA.", protocol)
        self.assertIn("Chat history, model memory, Git", protocol)
        self.assertIn("Every mutable data class used by MIRA must resolve", protocol)
        self.assertIn("authority_binding/binding-onboarding-ledger", protocol)
        self.assertIn("authority_binding/binding-service-state", protocol)
        self.assertIn("authority_binding/binding-receipt", protocol)
        self.assertIn("authority_binding/binding-asset", protocol)
        self.assertIn("authority_binding/binding-identifier", protocol)
        self.assertIn("resource id: `google-sheets-personal`", protocol)
        self.assertIn("resource id: `minimum-useful-setup`", protocol)
        self.assertIn("`timezone`", protocol)
        self.assertIn("`life_pattern`", protocol)
        self.assertIn("`goals`", protocol)
        self.assertIn("`appointment_help`", protocol)
        self.assertIn("## Canonical receipts and purchase history", protocol)
        self.assertIn("canonical resource type is `receipt`", protocol)
        self.assertIn("integer minor units", protocol)
        self.assertIn("Exact source-fingerprint replay", protocol)
        self.assertIn("Receipt capture does **not** automatically create or mutate an asset", protocol)
        self.assertIn("## Canonical physical assets and receipt-linked acquisition", protocol)
        self.assertIn("canonical resource type is `asset`", protocol)
        self.assertIn("immutable RFC 4122 Entity UUID", protocol)
        self.assertIn("Receipt capture never automatically creates assets.", protocol)
        self.assertIn("`tracking_mode=individual` requires asset quantity exactly `1`", protocol)
        self.assertIn("Asset acquisition alone therefore never claims an item is installed on a vehicle", protocol)
        self.assertIn("## Canonical asset identifiers and lookup", protocol)
        self.assertIn("canonical resource type is `identifier`", protocol)
        self.assertIn("Leading zeroes are preserved.", protocol)
        self.assertIn("serial-level collision-protected identifiers", protocol)
        self.assertIn("identifiers cannot manufacture physical assets.", protocol)
        self.assertIn("Identifier attachment alone never infers fitment", protocol)
        self.assertIn("`calendar_capability_verified`: false", protocol)
        self.assertIn("service_state/appointments_calendar", protocol)
        self.assertIn("`activation_state` to `requested`", protocol)
        self.assertIn("Do **not** mark the service active.", protocol)
        self.assertIn("SHA-256", protocol)
        self.assertIn("expected_revision", protocol)
        self.assertIn("exact provider readback", protocol)
        self.assertIn("must not require Cloud Run", protocol)
        self.assertIn("Microsoft/Outlook/M365", protocol)
        self.assertIn("Apple/iCloud", protocol)

    def test_bundle_rejects_missing_no_app_contract_clause(self) -> None:
        bundle = load_workspace_bundle()
        files = dict(bundle.files)
        files["MIRA_NO_APP_INSTRUCTIONS.md"] = files[
            "MIRA_NO_APP_INSTRUCTIONS.md"
        ].replace("Do **not** mark the service active.", "")
        with self.assertRaisesRegex(WorkspaceBundleError, "contract clauses"):
            validate_workspace_bundle(files)

    def test_bundle_rejects_missing_authority_binding_clause(self) -> None:
        bundle = load_workspace_bundle()
        files = dict(bundle.files)
        files["MIRA_NO_APP_INSTRUCTIONS.md"] = files[
            "MIRA_NO_APP_INSTRUCTIONS.md"
        ].replace("authority_binding/binding-service-state", "authority_binding/missing")
        with self.assertRaisesRegex(WorkspaceBundleError, "contract clauses"):
            validate_workspace_bundle(files)

    def test_bundle_rejects_missing_receipt_safety_clause(self) -> None:
        bundle = load_workspace_bundle()
        files = dict(bundle.files)
        files["MIRA_NO_APP_INSTRUCTIONS.md"] = files[
            "MIRA_NO_APP_INSTRUCTIONS.md"
        ].replace(
            "Receipt capture does **not** automatically create or mutate an asset",
            "Receipt capture may create an asset",
        )
        with self.assertRaisesRegex(WorkspaceBundleError, "contract clauses"):
            validate_workspace_bundle(files)

    def test_bundle_rejects_missing_asset_identity_clause(self) -> None:
        bundle = load_workspace_bundle()
        files = dict(bundle.files)
        files["MIRA_NO_APP_INSTRUCTIONS.md"] = files[
            "MIRA_NO_APP_INSTRUCTIONS.md"
        ].replace("immutable RFC 4122 Entity UUID", "mutable asset identifier")
        with self.assertRaisesRegex(WorkspaceBundleError, "contract clauses"):
            validate_workspace_bundle(files)

    def test_bundle_rejects_missing_asset_side_effect_clause(self) -> None:
        bundle = load_workspace_bundle()
        files = dict(bundle.files)
        files["MIRA_NO_APP_INSTRUCTIONS.md"] = files[
            "MIRA_NO_APP_INSTRUCTIONS.md"
        ].replace(
            "Asset acquisition alone therefore never claims an item is installed on a vehicle",
            "Asset acquisition may imply installation",
        )
        with self.assertRaisesRegex(WorkspaceBundleError, "contract clauses"):
            validate_workspace_bundle(files)

    def test_bundle_rejects_missing_identifier_binding_clause(self) -> None:
        bundle = load_workspace_bundle()
        files = dict(bundle.files)
        files["MIRA_NO_APP_INSTRUCTIONS.md"] = files[
            "MIRA_NO_APP_INSTRUCTIONS.md"
        ].replace("authority_binding/binding-identifier", "authority_binding/missing-identifier")
        with self.assertRaisesRegex(WorkspaceBundleError, "contract clauses"):
            validate_workspace_bundle(files)

    def test_bundle_rejects_missing_identifier_collision_clause(self) -> None:
        bundle = load_workspace_bundle()
        files = dict(bundle.files)
        files["MIRA_NO_APP_INSTRUCTIONS.md"] = files[
            "MIRA_NO_APP_INSTRUCTIONS.md"
        ].replace(
            "`serial_number`, `imei`, and `mac` are serial-level collision-protected identifiers.",
            "Serial identifiers may be reused.",
        )
        with self.assertRaisesRegex(WorkspaceBundleError, "contract clauses"):
            validate_workspace_bundle(files)

    def test_bundle_rejects_identifier_side_effect_regression(self) -> None:
        bundle = load_workspace_bundle()
        files = dict(bundle.files)
        files["MIRA_NO_APP_INSTRUCTIONS.md"] = files[
            "MIRA_NO_APP_INSTRUCTIONS.md"
        ].replace(
            "Identifier attachment alone never infers fitment",
            "Identifier attachment may infer fitment",
        )
        with self.assertRaisesRegex(WorkspaceBundleError, "contract clauses"):
            validate_workspace_bundle(files)

    def test_bundle_rejects_provider_identifiers(self) -> None:
        bundle = load_workspace_bundle()
        files = dict(bundle.files)
        files["README.md"] += "\nAKfycb12345678901234567890\n"
        with self.assertRaisesRegex(WorkspaceBundleError, "provider identifier"):
            validate_workspace_bundle(files)

    def test_bundle_rejects_secret_markers(self) -> None:
        bundle = load_workspace_bundle()
        files = dict(bundle.files)
        files["README.md"] += "\n-----BEGIN PRIVATE KEY-----\n"
        with self.assertRaisesRegex(WorkspaceBundleError, "secret material"):
            validate_workspace_bundle(files)

    def test_missing_file_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "Code.gs").write_text("function onOpen() {}", encoding="utf-8")
            with self.assertRaisesRegex(WorkspaceBundleError, "missing Workspace bundle file"):
                load_workspace_bundle(root)


if __name__ == "__main__":
    unittest.main()
