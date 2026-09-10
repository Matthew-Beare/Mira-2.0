from __future__ import annotations

import copy
import hashlib
import unittest

from mira.feature_share import (
    FeatureShareError,
    build_feature_share_package,
    inspect_feature_share_import,
    package_from_mapping,
    verify_feature_share_package,
)


OWNER = "private-owner-001"
DIGEST = hashlib.sha256(b"reviewed-source").hexdigest()


def build():
    return build_feature_share_package(
        private_owner_id=OWNER,
        change_id="CHANGE-001",
        source_revision="abc1234",
        reviewed_source_sha256=DIGEST,
        feature_ids=("DEV-004", "STUDIO-001"),
        dependency_ids=("DIST-001", "SOURCE-001"),
        min_runtime_schema=1,
        max_runtime_schema=3,
        artifacts={
            "mira/example.py": "VALUE = 1\n",
            "tests/test_example.py": "def test_example():\n    assert True\n",
        },
    )


class FeatureShareTests(unittest.TestCase):
    def test_roundtrip_is_deterministic_and_hides_owner(self):
        first = build()
        second = build()
        self.assertEqual(first.package_id, second.package_id)
        self.assertEqual(first.canonical_bytes(), second.canonical_bytes())
        encoded = first.canonical_bytes().decode("utf-8")
        self.assertNotIn(OWNER, encoded)
        self.assertEqual(package_from_mapping(first.projection()), first)

    def test_changed_artifact_changes_package_id(self):
        first = build()
        second = build_feature_share_package(
            private_owner_id=OWNER,
            change_id="CHANGE-001",
            source_revision="abc1234",
            reviewed_source_sha256=DIGEST,
            feature_ids=("DEV-004", "STUDIO-001"),
            dependency_ids=("DIST-001", "SOURCE-001"),
            min_runtime_schema=1,
            max_runtime_schema=3,
            artifacts={
                "mira/example.py": "VALUE = 2\n",
                "tests/test_example.py": "def test_example():\n    assert True\n",
            },
        )
        self.assertNotEqual(first.package_id, second.package_id)

    def test_tampered_artifact_digest_fails(self):
        material = copy.deepcopy(build().projection())
        material["artifacts"][0]["content_b64"] = "VkFMVUUgPSA5Cg=="
        with self.assertRaisesRegex(FeatureShareError, "artifact digest mismatch"):
            verify_feature_share_package(material)

    def test_tampered_package_id_fails(self):
        material = copy.deepcopy(build().projection())
        material["package_id"] = "0" * 64
        with self.assertRaisesRegex(FeatureShareError, "package_id"):
            verify_feature_share_package(material)

    def test_duplicate_feature_ids_fail(self):
        with self.assertRaisesRegex(FeatureShareError, "duplicates"):
            build_feature_share_package(
                private_owner_id=OWNER,
                change_id="CHANGE-001",
                source_revision="abc1234",
                reviewed_source_sha256=DIGEST,
                feature_ids=("STUDIO-001", "STUDIO-001"),
                dependency_ids=(),
                min_runtime_schema=1,
                max_runtime_schema=1,
                artifacts={"mira/example.py": "VALUE = 1\n"},
            )

    def test_unsorted_ids_fail(self):
        with self.assertRaisesRegex(FeatureShareError, "sorted"):
            build_feature_share_package(
                private_owner_id=OWNER,
                change_id="CHANGE-001",
                source_revision="abc1234",
                reviewed_source_sha256=DIGEST,
                feature_ids=("STUDIO-001", "DEV-004"),
                dependency_ids=(),
                min_runtime_schema=1,
                max_runtime_schema=1,
                artifacts={"mira/example.py": "VALUE = 1\n"},
            )

    def test_dependency_feature_overlap_fails(self):
        with self.assertRaisesRegex(FeatureShareError, "disjoint"):
            build_feature_share_package(
                private_owner_id=OWNER,
                change_id="CHANGE-001",
                source_revision="abc1234",
                reviewed_source_sha256=DIGEST,
                feature_ids=("STUDIO-001",),
                dependency_ids=("STUDIO-001",),
                min_runtime_schema=1,
                max_runtime_schema=1,
                artifacts={"mira/example.py": "VALUE = 1\n"},
            )

    def test_private_email_in_artifact_fails(self):
        with self.assertRaisesRegex(FeatureShareError, "private/provider-specific"):
            build_feature_share_package(
                private_owner_id=OWNER,
                change_id="CHANGE-001",
                source_revision="abc1234",
                reviewed_source_sha256=DIGEST,
                feature_ids=("STUDIO-001",),
                dependency_ids=(),
                min_runtime_schema=1,
                max_runtime_schema=1,
                artifacts={"README.md": "contact matt@example.com\n"},
            )

    def test_provider_document_id_in_artifact_fails(self):
        with self.assertRaisesRegex(FeatureShareError, "private/provider-specific"):
            build_feature_share_package(
                private_owner_id=OWNER,
                change_id="CHANGE-001",
                source_revision="abc1234",
                reviewed_source_sha256=DIGEST,
                feature_ids=("STUDIO-001",),
                dependency_ids=(),
                min_runtime_schema=1,
                max_runtime_schema=1,
                artifacts={
                    "README.md":
                    "https://docs.google.com/spreadsheets/d/1abcdefghijklmnopqrstuvwxyz0123456789/edit\n"
                },
            )

    def test_secret_marker_in_artifact_fails(self):
        with self.assertRaisesRegex(FeatureShareError, "secret/private"):
            build_feature_share_package(
                private_owner_id=OWNER,
                change_id="CHANGE-001",
                source_revision="abc1234",
                reviewed_source_sha256=DIGEST,
                feature_ids=("STUDIO-001",),
                dependency_ids=(),
                min_runtime_schema=1,
                max_runtime_schema=1,
                artifacts={"config.txt": "client_secret = nope\n"},
            )

    def test_unsafe_path_fails(self):
        with self.assertRaisesRegex(FeatureShareError, "invalid or unsafe"):
            build_feature_share_package(
                private_owner_id=OWNER,
                change_id="CHANGE-001",
                source_revision="abc1234",
                reviewed_source_sha256=DIGEST,
                feature_ids=("STUDIO-001",),
                dependency_ids=(),
                min_runtime_schema=1,
                max_runtime_schema=1,
                artifacts={"../secret.txt": "nope\n"},
            )

    def test_credential_named_path_fails(self):
        with self.assertRaisesRegex(FeatureShareError, "credential"):
            build_feature_share_package(
                private_owner_id=OWNER,
                change_id="CHANGE-001",
                source_revision="abc1234",
                reviewed_source_sha256=DIGEST,
                feature_ids=("STUDIO-001",),
                dependency_ids=(),
                min_runtime_schema=1,
                max_runtime_schema=1,
                artifacts={"config/credentials/data.txt": "nope\n"},
            )

    def test_incompatible_runtime_is_inert_not_ready(self):
        inspection = inspect_feature_share_import(
            build().projection(),
            runtime_schema=4,
            available_feature_ids=("DIST-001", "SOURCE-001"),
        )
        self.assertFalse(inspection.compatible)
        self.assertFalse(inspection.ready_for_review)
        self.assertFalse(inspection.activation_authorized)
        self.assertFalse(inspection.source_mutation_authorized)
        self.assertFalse(inspection.install_authorized)

    def test_missing_dependency_is_reported(self):
        inspection = inspect_feature_share_import(
            build().projection(),
            runtime_schema=2,
            available_feature_ids=("DIST-001",),
        )
        self.assertEqual(inspection.missing_dependencies, ("SOURCE-001",))
        self.assertFalse(inspection.ready_for_review)

    def test_compatible_import_is_only_ready_for_review(self):
        inspection = inspect_feature_share_import(
            build().projection(),
            runtime_schema=2,
            available_feature_ids=("DIST-001", "SOURCE-001"),
        )
        self.assertTrue(inspection.compatible)
        self.assertTrue(inspection.ready_for_review)
        self.assertFalse(inspection.activation_authorized)
        self.assertFalse(inspection.source_mutation_authorized)
        self.assertFalse(inspection.install_authorized)

    def test_existing_feature_is_reported_without_mutation_authority(self):
        inspection = inspect_feature_share_import(
            build().projection(),
            runtime_schema=2,
            available_feature_ids=("DEV-004", "DIST-001", "SOURCE-001"),
        )
        self.assertEqual(inspection.already_present_features, ("DEV-004",))
        self.assertFalse(inspection.activation_authorized)

    def test_authority_smuggling_extra_field_fails(self):
        material = copy.deepcopy(build().projection())
        material["approved"] = True
        with self.assertRaisesRegex(FeatureShareError, "execution authority"):
            package_from_mapping(material)

    def test_authority_smuggling_nested_field_fails(self):
        material = copy.deepcopy(build().projection())
        material["artifacts"][0]["activation"] = True
        with self.assertRaisesRegex(FeatureShareError, "execution authority"):
            package_from_mapping(material)

    def test_extra_schema_field_fails(self):
        material = copy.deepcopy(build().projection())
        material["display_name"] = "Helpful feature"
        with self.assertRaisesRegex(FeatureShareError, "fields do not match schema"):
            package_from_mapping(material)

    def test_invalid_compatibility_range_fails(self):
        with self.assertRaisesRegex(FeatureShareError, "may not exceed"):
            build_feature_share_package(
                private_owner_id=OWNER,
                change_id="CHANGE-001",
                source_revision="abc1234",
                reviewed_source_sha256=DIGEST,
                feature_ids=("STUDIO-001",),
                dependency_ids=(),
                min_runtime_schema=3,
                max_runtime_schema=2,
                artifacts={"mira/example.py": "VALUE = 1\n"},
            )


if __name__ == "__main__":
    unittest.main()
