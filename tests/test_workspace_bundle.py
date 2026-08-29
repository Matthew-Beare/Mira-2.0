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
