"""Tests for the Android production ownership governance gate."""

from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from project.android_code_ownership import (
    AndroidCodeOwnershipError,
    validate_repository,
)


FEATURES = """# FEATURES

## Feature index

`ID | Title | requirement | evidence | deps`

- `API-001` | API | required | specified | -
- `CLIENT-ANDROID-001` | Android client | required | specified | API-001
- `RECOVERY-002` | Recovery | required | specified | -
"""

BACKLOG = """# BACKLOG

| Work ID | Class | Work | Dependencies | Status |
|---|---|---|---|---|
| `ANDROID-CLIENT-CORE-001` | PREREQUISITE | Android client core | CLIENT-ANDROID-001 | queued |
"""


class AndroidOwnershipFixture:
    def __init__(self) -> None:
        self.temp = TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.main = self.root / "android-client/core/src/main/java/com/example"
        self.tests = self.root / "android-client/core/src/test/java/com/example"
        self.project = self.root / "project"
        self.main.mkdir(parents=True)
        self.tests.mkdir(parents=True)
        self.project.mkdir(parents=True)
        (self.root / "FEATURES.md").write_text(FEATURES, encoding="utf-8")
        (self.root / "BACKLOG.md").write_text(BACKLOG, encoding="utf-8")
        self.source_path = "android-client/core/src/main/java/com/example/Vault.java"
        self.test_path = "android-client/core/src/test/java/com/example/VaultTest.java"
        (self.root / self.source_path).write_text(
            "package com.example; public final class Vault {}\n",
            encoding="utf-8",
        )
        (self.root / self.test_path).write_text(
            "package com.example; public final class VaultTest { Vault value; }\n",
            encoding="utf-8",
        )
        self.manifest = {
            "schema_version": 1,
            "production_root": "android-client/core/src/main/java",
            "suffixes": [".java"],
            "components": [
                {
                    "id": "android-vault",
                    "responsibility": "Own Android credential protection.",
                    "why_separate": "Keep native secret storage bounded.",
                    "owned_paths": [self.source_path],
                    "feature_ids": ["CLIENT-ANDROID-001", "API-001", "RECOVERY-002"],
                    "work_ids": ["ANDROID-CLIENT-CORE-001"],
                    "verification": [self.test_path],
                }
            ],
        }
        self.write_manifest()

    def write_manifest(self) -> None:
        (self.project / "android_code_ownership.json").write_text(
            json.dumps(self.manifest, indent=2) + "\n",
            encoding="utf-8",
        )

    def validate(self):
        return validate_repository(repository_root=self.root)

    def close(self) -> None:
        self.temp.cleanup()


class AndroidCodeOwnershipTests(unittest.TestCase):
    def fixture(self) -> AndroidOwnershipFixture:
        fixture = AndroidOwnershipFixture()
        self.addCleanup(fixture.close)
        return fixture

    def test_minimal_android_component_is_valid(self) -> None:
        fixture = self.fixture()
        self.assertEqual(fixture.validate(), (1, 1))

    def test_rejects_unowned_android_source(self) -> None:
        fixture = self.fixture()
        (fixture.main / "Orphan.java").write_text(
            "package com.example; final class Orphan {}\n",
            encoding="utf-8",
        )
        with self.assertRaisesRegex(
            AndroidCodeOwnershipError,
            "unowned Android production artifacts",
        ):
            fixture.validate()

    def test_rejects_java_test_without_direct_class_reference(self) -> None:
        fixture = self.fixture()
        (fixture.root / fixture.test_path).write_text(
            "package com.example; public final class VaultTest {}\n".replace("VaultTest", "SecurityTest"),
            encoding="utf-8",
        )
        with self.assertRaisesRegex(
            AndroidCodeOwnershipError,
            "no direct Java verification reference",
        ):
            fixture.validate()

    def test_rejects_unknown_feature_reference(self) -> None:
        fixture = self.fixture()
        fixture.manifest["components"][0]["feature_ids"] = ["MISSING-001"]
        fixture.write_manifest()
        with self.assertRaisesRegex(AndroidCodeOwnershipError, "unknown feature IDs"):
            fixture.validate()

    def test_rejects_overlapping_android_ownership(self) -> None:
        fixture = self.fixture()
        duplicate = dict(fixture.manifest["components"][0])
        duplicate["id"] = "duplicate-vault"
        fixture.manifest["components"].append(duplicate)
        fixture.write_manifest()
        with self.assertRaisesRegex(AndroidCodeOwnershipError, "overlapping owners"):
            fixture.validate()

    def test_real_repository_android_manifest_is_valid(self) -> None:
        components, artifacts = validate_repository(repository_root=Path("."))
        self.assertGreaterEqual(components, 1)
        self.assertGreaterEqual(artifacts, 1)


if __name__ == "__main__":
    unittest.main()
