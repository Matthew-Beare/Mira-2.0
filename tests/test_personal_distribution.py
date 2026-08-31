from __future__ import annotations

from dataclasses import replace
import json
import unittest

from mira.personal_distribution import (
    PersonalDistributionError,
    StarterSnapshot,
    build_release_manifest,
    load_blueprint,
    validate_blueprint,
    verify_release_manifest,
    verify_snapshot,
)


class PersonalDistributionTests(unittest.TestCase):
    def test_repository_blueprint_is_valid_and_sanitized(self) -> None:
        blueprint = load_blueprint()
        self.assertEqual(blueprint.distribution_id, "mira-personal-google-workspace-v1")
        self.assertEqual(blueprint.spreadsheet_time_zone, "Etc/UTC")
        self.assertEqual(
            [tab.title for tab in blueprint.tabs],
            ["Metadata", "Resources", "Events", "Idempotency"],
        )
        metadata = dict(next(tab for tab in blueprint.tabs if tab.title == "Metadata").rows)
        self.assertEqual(
            json.loads(metadata["resource_types_json"]),
            [
                "appointment",
                "appointment_provider",
                "authority",
                "authority_binding",
                "asset",
                "entity",
                "identifier",
                "inventory_state",
                "location",
                "onboarding_ledger",
                "ops_brief_run",
                "receipt",
                "service_state",
                "shopping_intent",
                "task",
            ],
        )
        for tab in blueprint.tabs:
            if tab.title != "Metadata":
                self.assertEqual(tab.rows, ())
                self.assertTrue(tab.must_be_empty_after_seed_rows)

    def test_release_manifest_is_byte_for_byte_deterministic(self) -> None:
        source_sha = "a" * 40
        first = build_release_manifest(source_sha)
        second = build_release_manifest(source_sha)
        self.assertEqual(first, second)
        self.assertEqual(first.json_bytes(), second.json_bytes())
        projection = json.loads(first.json_bytes())
        self.assertEqual(projection["source_sha"], source_sha)
        self.assertEqual(len(projection["artifacts"]), 5)
        self.assertEqual(
            [item["path"] for item in projection["artifacts"]],
            sorted(item["path"] for item in projection["artifacts"]),
        )

    def test_release_manifest_verifier_detects_tamper(self) -> None:
        manifest = build_release_manifest("b" * 40).projection()
        verify_release_manifest(manifest)
        tampered = json.loads(json.dumps(manifest))
        tampered["artifacts"][0]["sha256"] = "0" * 64
        with self.assertRaisesRegex(PersonalDistributionError, "does not match"):
            verify_release_manifest(tampered)

    def test_invalid_source_sha_is_rejected(self) -> None:
        with self.assertRaisesRegex(PersonalDistributionError, "source_sha"):
            build_release_manifest("main")

    def test_blueprint_rejects_secret_or_provider_material(self) -> None:
        blueprint = load_blueprint()
        secret = replace(
            blueprint,
            distribution_id="MIRA_BEARER_TOKEN=do-not-ship",
        )
        with self.assertRaisesRegex(PersonalDistributionError, "distribution_id|secret-like"):
            validate_blueprint(secret)

        provider = replace(
            blueprint,
            spreadsheet_title="https://docs.google.com/spreadsheets/d/ABCDEF1234567890",
        )
        with self.assertRaisesRegex(PersonalDistributionError, "title|provider identifier"):
            validate_blueprint(provider)

    def test_blueprint_rejects_dirty_mutable_seed_rows(self) -> None:
        blueprint = load_blueprint()
        resources = next(tab for tab in blueprint.tabs if tab.title == "Resources")
        dirty_resources = replace(
            resources,
            rows=(("entity", "private-user-thing", 1, "{}", "now", "key", "hash"),),
        )
        dirty = replace(
            blueprint,
            tabs=tuple(
                dirty_resources if tab.title == "Resources" else tab
                for tab in blueprint.tabs
            ),
        )
        with self.assertRaisesRegex(PersonalDistributionError, "Resources must contain no seed data"):
            validate_blueprint(dirty)

    def test_snapshot_verifier_accepts_exact_clean_starter(self) -> None:
        blueprint = load_blueprint()
        tabs = {tab.title: (tab.headers,) + tab.rows for tab in blueprint.tabs}
        snapshot = StarterSnapshot(
            title=blueprint.spreadsheet_title,
            time_zone=blueprint.spreadsheet_time_zone,
            tabs=tabs,
        )
        verify_snapshot(snapshot)

    def test_snapshot_verifier_rejects_header_drift_and_inherited_state(self) -> None:
        blueprint = load_blueprint()
        tabs = {tab.title: (tab.headers,) + tab.rows for tab in blueprint.tabs}
        bad_headers = dict(tabs)
        bad_headers["Resources"] = (("wrong",) + tabs["Resources"][0][1:],)
        with self.assertRaisesRegex(PersonalDistributionError, "headers"):
            verify_snapshot(
                StarterSnapshot(
                    title=blueprint.spreadsheet_title,
                    time_zone=blueprint.spreadsheet_time_zone,
                    tabs=bad_headers,
                )
            )

        dirty = dict(tabs)
        dirty["Resources"] = dirty["Resources"] + (
            ("entity", "inherited", 1, "{}", "now", "key", "hash"),
        )
        with self.assertRaisesRegex(PersonalDistributionError, "inherited mutable state"):
            verify_snapshot(
                StarterSnapshot(
                    title=blueprint.spreadsheet_title,
                    time_zone=blueprint.spreadsheet_time_zone,
                    tabs=dirty,
                )
            )

    def test_snapshot_verifier_rejects_metadata_drift(self) -> None:
        blueprint = load_blueprint()
        tabs = {tab.title: (tab.headers,) + tab.rows for tab in blueprint.tabs}
        metadata = list(tabs["Metadata"])
        metadata[1] = ("schema_version", "wrong")
        tabs["Metadata"] = tuple(metadata)
        with self.assertRaisesRegex(PersonalDistributionError, "Metadata"):
            verify_snapshot(
                StarterSnapshot(
                    title=blueprint.spreadsheet_title,
                    time_zone=blueprint.spreadsheet_time_zone,
                    tabs=tabs,
                )
            )


if __name__ == "__main__":
    unittest.main()
