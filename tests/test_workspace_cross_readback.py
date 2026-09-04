"""Shared-writer stock-ChatGPT canonical cross-readback contract tests."""

from __future__ import annotations

from dataclasses import replace
import unittest

from mira.structured_state import ResourceRecord
from mira.workspace_native import (
    WorkspaceIdempotencyRecord,
    WorkspaceReadbackError,
    WorkspaceResourceRow,
    plan_workspace_bootstrap,
    verify_workspace_shared_resource_readback,
    workspace_upsert_fingerprint,
)


class WorkspaceSharedCrossReadbackTests(unittest.TestCase):
    def setUp(self) -> None:
        bootstrap = plan_workspace_bootstrap(
            owner_id="shared-proof-user",
            resource_rows=[],
            idempotency_rows=[],
        )
        self.payload = {"state": "android-updated", "proof": "shared-writer"}
        self.resource_id = "shared-entity-001"
        self.idempotency_key = "android-shared-upsert-001"
        self.expected_revision = 1
        self.revision = 2
        self.request_hash = workspace_upsert_fingerprint(
            "entity",
            self.resource_id,
            self.payload,
            expected_revision=self.expected_revision,
        )
        self.record = ResourceRecord(
            "entity",
            self.resource_id,
            self.payload,
            self.revision,
        )
        self.rows = [
            WorkspaceResourceRow(
                row_number=2,
                record=bootstrap.authority.record,
                last_idempotency_key=bootstrap.authority.idempotency_key,
                request_hash=bootstrap.authority.request_hash,
            ),
            WorkspaceResourceRow(
                row_number=3,
                record=bootstrap.binding.record,
                last_idempotency_key=bootstrap.binding.idempotency_key,
                request_hash=bootstrap.binding.request_hash,
            ),
            WorkspaceResourceRow(
                row_number=4,
                record=self.record,
                last_idempotency_key=self.idempotency_key,
                request_hash=self.request_hash,
            ),
        ]
        self.result = {
            "kind": "upsert",
            "record": {
                "payload": self.payload,
                "resource_id": self.resource_id,
                "resource_type": "entity",
                "revision": self.revision,
            },
        }
        self.idempotency = [
            WorkspaceIdempotencyRecord(
                row_number=4,
                idempotency_key=self.idempotency_key,
                operation="upsert",
                request_hash=self.request_hash,
                result=self.result,
                resource_ref=f"entity/{self.resource_id}",
            )
        ]

    def verify(self, **overrides):
        values = {
            "resource_type": "entity",
            "resource_id": self.resource_id,
            "payload": self.payload,
            "revision": self.revision,
            "expected_revision": self.expected_revision,
            "idempotency_key": self.idempotency_key,
            "resource_rows": self.rows,
            "idempotency_rows": self.idempotency,
            "mutation_mode": "queued_writer",
        }
        values.update(overrides)
        return verify_workspace_shared_resource_readback(**values)

    def test_queued_writer_read_verifies_exact_canonical_android_mutation(self) -> None:
        original_rows = tuple(self.rows)
        original_idempotency = tuple(self.idempotency)

        record = self.verify()

        self.assertEqual(record, self.record)
        self.assertEqual(tuple(self.rows), original_rows)
        self.assertEqual(tuple(self.idempotency), original_idempotency)

    def test_missing_duplicate_or_wrong_canonical_resource_fails_closed(self) -> None:
        without_target = self.rows[:2]
        with self.assertRaisesRegex(WorkspaceReadbackError, "missing or duplicated"):
            self.verify(resource_rows=without_target)

        duplicate = self.rows + [replace(self.rows[2], row_number=5)]
        with self.assertRaisesRegex(WorkspaceReadbackError, "missing or duplicated"):
            self.verify(resource_rows=duplicate)

        wrong_record = ResourceRecord(
            "entity",
            self.resource_id,
            {"state": "stale"},
            self.revision,
        )
        wrong_rows = self.rows[:2] + [replace(self.rows[2], record=wrong_record)]
        with self.assertRaisesRegex(WorkspaceReadbackError, "revision or payload"):
            self.verify(resource_rows=wrong_rows)

    def test_authority_routing_must_be_unique_verified_and_schema_compatible(self) -> None:
        no_binding = [self.rows[0], self.rows[2]]
        with self.assertRaisesRegex(WorkspaceReadbackError, "authority binding"):
            self.verify(resource_rows=no_binding)

        duplicate_binding = self.rows + [replace(self.rows[1], row_number=5)]
        with self.assertRaisesRegex(WorkspaceReadbackError, "authority binding"):
            self.verify(resource_rows=duplicate_binding)

        authority = self.rows[0].record
        disabled_payload = dict(authority.payload)
        disabled_payload["enabled"] = False
        disabled = ResourceRecord(
            authority.resource_type,
            authority.resource_id,
            disabled_payload,
            authority.revision,
        )
        disabled_rows = [replace(self.rows[0], record=disabled), self.rows[1], self.rows[2]]
        with self.assertRaisesRegex(WorkspaceReadbackError, "disabled, unverified, or incompatible"):
            self.verify(resource_rows=disabled_rows)

    def test_resource_and_idempotency_provenance_mismatch_fails_closed(self) -> None:
        wrong_resource_provenance = self.rows[:2] + [
            replace(self.rows[2], request_hash="not-the-shared-request-hash")
        ]
        with self.assertRaisesRegex(WorkspaceReadbackError, "mutation provenance"):
            self.verify(resource_rows=wrong_resource_provenance)

        wrong_idempotency = [
            replace(self.idempotency[0], resource_ref="entity/some-other-resource")
        ]
        with self.assertRaisesRegex(WorkspaceReadbackError, "idempotency provenance"):
            self.verify(idempotency_rows=wrong_idempotency)

        duplicate_idempotency = self.idempotency + [
            replace(self.idempotency[0], row_number=5)
        ]
        with self.assertRaisesRegex(WorkspaceReadbackError, "missing or duplicated"):
            self.verify(idempotency_rows=duplicate_idempotency)

    def test_read_transition_and_mode_validation_fail_closed(self) -> None:
        with self.assertRaisesRegex(WorkspaceReadbackError, "expected upsert transition"):
            self.verify(revision=3)

        with self.assertRaisesRegex(ValueError, "mutation_mode"):
            self.verify(mutation_mode="mystery-writer")


if __name__ == "__main__":
    unittest.main()
