"""Tests for the canonical MIRA feature registry projection."""

from __future__ import annotations

import json
from pathlib import Path
import unittest

from mira.feature_registry import FeatureRegistryError, parse_registry_bytes


HEADER = """# MIRA 2.0 FEATURES

## Feature index

`ID | Title | requirement | evidence | deps`

"""


def source(*rows: str, trailing: str = "") -> bytes:
    body = HEADER + "\n".join(rows)
    if trailing:
        body += "\n\n## Mapping\n\n" + trailing
    return (body + "\n").encode("utf-8")


class FeatureRegistryTests(unittest.TestCase):
    def test_parses_only_feature_index_and_preserves_authored_ids(self) -> None:
        registry = parse_registry_bytes(
            source(
                "- `CORE-001` | Core | required | specified | -",
                "- `API-001` | API | required | specified | CORE-001",
                trailing="- `FAKE-999` | mapping prose only",
            )
        )
        self.assertEqual([item.feature_id for item in registry.features], ["API-001", "CORE-001"])
        self.assertEqual(registry.feature_map()["API-001"].dependencies, ("CORE-001",))

    def test_rejects_malformed_feature_row(self) -> None:
        with self.assertRaisesRegex(FeatureRegistryError, "malformed feature row"):
            parse_registry_bytes(source("- `CORE-001` | missing fields"))

    def test_rejects_duplicate_feature_id(self) -> None:
        with self.assertRaisesRegex(FeatureRegistryError, "duplicate stable feature ID"):
            parse_registry_bytes(
                source(
                    "- `CORE-001` | One | required | specified | -",
                    "- `CORE-001` | Two | required | specified | -",
                )
            )

    def test_rejects_invalid_feature_id(self) -> None:
        with self.assertRaisesRegex(FeatureRegistryError, "invalid stable feature ID"):
            parse_registry_bytes(source("- `core-one` | Bad | required | specified | -"))

    def test_rejects_unknown_dependency(self) -> None:
        with self.assertRaisesRegex(FeatureRegistryError, "unknown feature ID MISSING-001"):
            parse_registry_bytes(
                source("- `CORE-001` | Core | required | specified | MISSING-001")
            )

    def test_rejects_self_dependency(self) -> None:
        with self.assertRaisesRegex(FeatureRegistryError, "cannot depend on itself"):
            parse_registry_bytes(
                source("- `CORE-001` | Core | required | specified | CORE-001")
            )

    def test_rejects_duplicate_dependency(self) -> None:
        with self.assertRaisesRegex(FeatureRegistryError, "repeats a dependency"):
            parse_registry_bytes(
                source(
                    "- `CORE-001` | Core | required | specified | -",
                    "- `API-001` | API | required | specified | CORE-001,CORE-001",
                )
            )

    def test_reports_deterministic_cycle_path(self) -> None:
        raw = source(
            "- `AAA-001` | A | required | specified | BBB-001",
            "- `BBB-001` | B | required | specified | CCC-001",
            "- `CCC-001` | C | required | specified | AAA-001",
        )
        with self.assertRaisesRegex(
            FeatureRegistryError,
            r"feature dependency cycle: AAA-001 -> BBB-001 -> CCC-001 -> AAA-001",
        ):
            parse_registry_bytes(raw)

    def test_projection_is_deterministic_and_source_bound(self) -> None:
        raw = source(
            "- `CORE-001` | Core | required | specified | -",
            "- `API-001` | API | required | test_verified | CORE-001",
        )
        first = parse_registry_bytes(raw, source_path="FEATURES.md")
        second = parse_registry_bytes(raw, source_path="FEATURES.md")
        self.assertEqual(first.json_bytes(), second.json_bytes())
        projection = json.loads(first.json_bytes())
        self.assertEqual(projection["schema_version"], 1)
        self.assertEqual(projection["source"]["path"], "FEATURES.md")
        self.assertEqual(len(projection["source"]["sha256"]), 64)
        self.assertEqual([item["id"] for item in projection["features"]], ["API-001", "CORE-001"])

    def test_real_repository_feature_registry_is_valid(self) -> None:
        raw = Path("FEATURES.md").read_bytes()
        registry = parse_registry_bytes(raw, source_path="FEATURES.md")
        self.assertGreater(len(registry.features), 50)
        self.assertIn("API-001", registry.feature_map())
        self.assertIn("CLIENT-ANDROID-001", registry.feature_map())


if __name__ == "__main__":
    unittest.main()
