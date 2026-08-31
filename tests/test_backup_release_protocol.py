"""Regression guards for the no-app backup/restore integrity contract."""

import unittest

from mira.workspace_bundle import (
    WorkspaceBundleError,
    load_workspace_bundle,
    validate_workspace_bundle,
)


class BackupReleaseProtocolTests(unittest.TestCase):
    def setUp(self) -> None:
        self.bundle = load_workspace_bundle()
        self.protocol = self.bundle.file("MIRA_NO_APP_INSTRUCTIONS.md")

    def _replace_and_reject(self, old: str, new: str) -> None:
        self.assertIn(old, self.protocol)
        files = dict(self.bundle.files)
        files["MIRA_NO_APP_INSTRUCTIONS.md"] = self.protocol.replace(old, new)
        with self.assertRaisesRegex(WorkspaceBundleError, "contract clauses"):
            validate_workspace_bundle(files)

    def test_repository_protocol_contains_backup_restore_integrity_boundaries(self) -> None:
        required = (
            "## Canonical current-Resource backup and isolated restore",
            "A MIRA backup artifact is a **nonauthoritative snapshot**",
            "complete_current_resources_under_query_bound",
            "not_exported_interface_not_enumerable",
            "Creating the backup is read-only.",
            "Restore only into a genuinely fresh, isolated, schema-compatible target authority.",
            "A restore-key replay on the supposedly fresh target is evidence that the target is not fresh; fail closed.",
            "Restore-generated provider timestamps, request hashes",
            "Verified restore requires exact schema, Resource identity, payload, revision",
            "does **not** prove Event-history recovery",
            "Backup and authority migration remain separate.",
            "**snapshot created**",
            "**restore verified**",
        )
        for marker in required:
            with self.subTest(marker=marker):
                self.assertIn(marker, self.protocol)

    def test_bundle_rejects_backup_source_write_regression(self) -> None:
        self._replace_and_reject(
            "Creating the backup is read-only.",
            "Creating the backup may normalize or update source rows.",
        )

    def test_bundle_rejects_recycled_restore_target_regression(self) -> None:
        self._replace_and_reject(
            "Restore only into a genuinely fresh, isolated, schema-compatible target authority.",
            "Restore may reuse any compatible target authority.",
        )

    def test_bundle_rejects_event_history_overclaim(self) -> None:
        self._replace_and_reject(
            "does **not** prove Event-history recovery",
            "proves complete Event-history recovery",
        )

    def test_bundle_rejects_coverage_declaration_regression(self) -> None:
        self._replace_and_reject(
            "not_exported_interface_not_enumerable",
            "complete_event_and_idempotency_history",
        )

    def test_bundle_rejects_backup_authority_cutover_regression(self) -> None:
        self._replace_and_reject(
            "Backup and authority migration remain separate.",
            "A verified backup may automatically switch canonical authority.",
        )

    def test_bundle_rejects_restore_replay_as_fresh_regression(self) -> None:
        self._replace_and_reject(
            "A restore-key replay on the supposedly fresh target is evidence that the target is not fresh; fail closed.",
            "A restore-key replay confirms the fresh target is safe to reuse.",
        )


if __name__ == "__main__":
    unittest.main()
