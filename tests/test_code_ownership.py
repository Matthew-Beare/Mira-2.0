"""Tests for production component ownership and direct verification coverage."""

from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from mira.code_ownership import CodeOwnershipError, validate_repository


FEATURES = """# FEATURES

## Feature index

`ID | Title | requirement | evidence | deps`

- `CORE-001` | Core | required | specified | -
- `DEV-006` | Ownership | required | specified | -
"""

BACKLOG = """# BACKLOG

| Work ID | Class | Work | Dependencies | Status |
|---|---|---|---|---|
| `WORK-001` | PREREQUISITE | Example work | - | queued |
"""


class RepositoryFixture:
    def __init__(self) -> None:
        self.temp = TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "mira").mkdir()
        (self.root / "tests").mkdir()
        (self.root / "project").mkdir()
        (self.root / "FEATURES.md").write_text(FEATURES, encoding="utf-8")
        (self.root / "BACKLOG.md").write_text(BACKLOG, encoding="utf-8")
        (self.root / "mira" / "example.py").write_text("VALUE = 1\n", encoding="utf-8")
        (self.root / "tests" / "test_example.py").write_text(
            "from mira.example import VALUE\n", encoding="utf-8"
        )
        self.manifest = {
            "schema_version": 1,
            "production_roots": [
                {"path": "mira", "profile": "python", "suffixes": [".py"]}
            ],
            "components": [
                {
                    "id": "example",
                    "responsibility": "Own the example production module.",
                    "why_separate": "Keeps this fixture component bounded and independently verifiable.",
                    "owned_paths": ["mira/example.py"],
                    "feature_ids": ["CORE-001"],
                    "work_ids": ["WORK-001"],
                    "verification": ["tests/test_example.py"],
                }
            ],
        }
        self.write_manifest()

    def write_manifest(self) -> None:
        (self.root / "project" / "code_ownership.json").write_text(
            json.dumps(self.manifest, indent=2) + "\n", encoding="utf-8"
        )

    def validate(self):
        return validate_repository(repository_root=self.root)

    def close(self) -> None:
        self.temp.cleanup()


class CodeOwnershipTests(unittest.TestCase):
    def fixture(self) -> RepositoryFixture:
        fixture = RepositoryFixture()
        self.addCleanup(fixture.close)
        return fixture

    def test_minimal_repository_is_valid(self) -> None:
        fixture = self.fixture()
        report = fixture.validate()
        self.assertEqual(report.component_count, 1)
        self.assertEqual(report.production_artifact_count, 1)

    def test_rejects_unowned_production_artifact(self) -> None:
        fixture = self.fixture()
        (fixture.root / "mira" / "orphan.py").write_text("ORPHAN = True\n", encoding="utf-8")
        with self.assertRaisesRegex(CodeOwnershipError, "unowned production artifacts: mira/orphan.py"):
            fixture.validate()

    def test_rejects_overlapping_ownership(self) -> None:
        fixture = self.fixture()
        duplicate = dict(fixture.manifest["components"][0])
        duplicate["id"] = "duplicate"
        fixture.manifest["components"].append(duplicate)
        fixture.write_manifest()
        with self.assertRaisesRegex(CodeOwnershipError, "overlapping owners"):
            fixture.validate()

    def test_rejects_missing_owned_path(self) -> None:
        fixture = self.fixture()
        fixture.manifest["components"][0]["owned_paths"] = ["mira/missing.py"]
        fixture.write_manifest()
        with self.assertRaisesRegex(CodeOwnershipError, "owned path does not exist"):
            fixture.validate()

    def test_rejects_owned_path_outside_production_root(self) -> None:
        fixture = self.fixture()
        (fixture.root / "other").mkdir()
        (fixture.root / "other" / "outside.py").write_text("VALUE = 2\n", encoding="utf-8")
        fixture.manifest["components"][0]["owned_paths"] = ["other/outside.py"]
        fixture.write_manifest()
        with self.assertRaisesRegex(CodeOwnershipError, "outside production roots"):
            fixture.validate()

    def test_rejects_unknown_feature_reference(self) -> None:
        fixture = self.fixture()
        fixture.manifest["components"][0]["feature_ids"] = ["MISSING-001"]
        fixture.write_manifest()
        with self.assertRaisesRegex(CodeOwnershipError, "unknown feature ID MISSING-001"):
            fixture.validate()

    def test_rejects_unknown_work_reference(self) -> None:
        fixture = self.fixture()
        fixture.manifest["components"][0]["work_ids"] = ["MISSING-WORK"]
        fixture.write_manifest()
        with self.assertRaisesRegex(CodeOwnershipError, "unknown work ID MISSING-WORK"):
            fixture.validate()

    def test_rejects_missing_verification_path(self) -> None:
        fixture = self.fixture()
        fixture.manifest["components"][0]["verification"] = ["tests/test_missing.py"]
        fixture.write_manifest()
        with self.assertRaisesRegex(CodeOwnershipError, "verification path does not exist"):
            fixture.validate()

    def test_rejects_verification_that_does_not_import_owned_module(self) -> None:
        fixture = self.fixture()
        (fixture.root / "tests" / "test_example.py").write_text(
            "import unittest\n", encoding="utf-8"
        )
        with self.assertRaisesRegex(CodeOwnershipError, "no direct Python verification import"):
            fixture.validate()

    def test_real_repository_manifest_is_valid(self) -> None:
        report = validate_repository(repository_root=Path("."))
        self.assertGreaterEqual(report.component_count, 5)
        self.assertGreaterEqual(report.production_artifact_count, 7)


if __name__ == "__main__":
    unittest.main()
