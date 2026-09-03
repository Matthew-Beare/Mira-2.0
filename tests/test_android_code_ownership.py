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
        self.provider_main = (
            self.root / "android-client/provider/src/main/java/com/example/provider"
        )
        self.tests = self.root / "android-client/core/src/test/java/com/example"
        self.provider_tests = (
            self.root / "android-client/provider/src/test/java/com/example/provider"
        )
        self.project = self.root / "project"
        self.main.mkdir(parents=True)
        self.provider_main.mkdir(parents=True)
        self.tests.mkdir(parents=True)
        self.provider_tests.mkdir(parents=True)
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

    def add_provider_component(self) -> tuple[str, str]:
        source_path = (
            "android-client/provider/src/main/java/com/example/provider/Bridge.java"
        )
        test_path = (
            "android-client/provider/src/test/java/com/example/provider/BridgeTest.java"
        )
        (self.root / source_path).write_text(
            "package com.example.provider; public final class Bridge {}\n",
            encoding="utf-8",
        )
        (self.root / test_path).write_text(
            "package com.example.provider; public final class BridgeTest { Bridge value; }\n",
            encoding="utf-8",
        )
        self.manifest.pop("production_root", None)
        self.manifest["production_roots"] = [
            "android-client/core/src/main/java",
            "android-client/provider/src/main/java",
        ]
        self.manifest["components"].append(
            {
                "id": "android-provider-bridge",
                "responsibility": "Own provider-specific Android bridge behavior.",
                "why_separate": "Keep provider SDK code outside provider-neutral core.",
                "owned_paths": [source_path],
                "feature_ids": ["CLIENT-ANDROID-001", "API-001", "RECOVERY-002"],
                "work_ids": ["ANDROID-CLIENT-CORE-001"],
                "verification": [test_path],
            }
        )
        self.write_manifest()
        return source_path, test_path

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

    def test_multiple_android_module_roots_are_valid(self) -> None:
        fixture = self.fixture()
        fixture.add_provider_component()
        self.assertEqual(fixture.validate(), (2, 2))

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

    def test_rejects_unowned_source_in_secondary_module(self) -> None:
        fixture = self.fixture()
        fixture.add_provider_component()
        (fixture.provider_main / "OrphanProvider.java").write_text(
            "package com.example.provider; final class OrphanProvider {}\n",
            encoding="utf-8",
        )
        with self.assertRaisesRegex(
            AndroidCodeOwnershipError,
            "unowned Android production artifacts",
        ):
            fixture.validate()

    def test_rejects_root_and_roots_together(self) -> None:
        fixture = self.fixture()
        fixture.manifest["production_roots"] = ["android-client/core/src/main/java"]
        fixture.write_manifest()
        with self.assertRaisesRegex(
            AndroidCodeOwnershipError,
            "production_root or production_roots",
        ):
            fixture.validate()

    def test_rejects_overlapping_roots(self) -> None:
        fixture = self.fixture()
        fixture.manifest.pop("production_root")
        fixture.manifest["production_roots"] = [
            "android-client/core/src/main/java",
            "android-client/core/src/main/java/com/example",
        ]
        fixture.write_manifest()
        with self.assertRaisesRegex(AndroidCodeOwnershipError, "must not overlap"):
            fixture.validate()

    def test_rejects_java_test_without_direct_class_reference(self) -> None:
        fixture = self.fixture()
        (fixture.root / fixture.test_path).write_text(
            "package com.example; public final class SecurityTest {}\n",
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
