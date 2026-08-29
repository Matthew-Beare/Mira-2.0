"""Contract tests for the native stock-ChatGPT Google Workspace path."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import json
import unittest

from mira.google_sheets_store import GoogleSheetsStructuredStateAdapter
from mira.structured_state import (
    IdempotencyConflictError,
    IdentityConflictError,
    ResourceRecord,
    RevisionConflictError,
)
from mira.workspace_native import (
    WorkspaceIdempotencyRecord,
    WorkspaceReadbackError,
    plan_workspace_upsert,
    verify_workspace_upsert_readback,
    workspace_upsert_fingerprint,
)


class _Gateway:
    def __init__(self) -> None:
        self.tables = {
            "Metadata": [
                ["Key", "Value"],
                ["schema_version", "mira-structured-state-v1"],
                ["store_role", "synthetic_google_structured_state"],
                ["environment", "mira_2_sandbox"],
                ["data_policy", "synthetic_only"],
                ["adapter_contract", "STORE-001"],
                ["resource_types_json", '["entity"]'],
                ["event_types_json", '["created","updated"]'],
                ["writer_model", "single_writer"],
            ],
            "Resources": [[
                "resource_type", "resource_id", "revision", "payload_json",
                "updated_at", "last_idempotency_key", "request_hash",
            ]],
            "Events": [[
                "event_type", "event_id", "stream_type", "stream_id",
                "stream_revision", "payload_json", "occurred_at", "idempotency_key",
            ]],
            "Idempotency": [[
                "idempotency_key", "operation", "request_hash", "result_json",
                "created_at", "resource_ref",
            ]],
        }
        self.batches = []

    def read_range(self, a1_range: str):
        return tuple(tuple(row) for row in self.tables[a1_range.split("!", 1)[0]])

    def apply_mutations(self, mutations):
        staged = deepcopy(self.tables)
        for mutation in mutations:
            row = list(mutation.values)
            if mutation.row_number is None:
                staged[mutation.tab].append(row)
            else:
                staged[mutation.tab][mutation.row_number - 1] = row
        self.tables = staged
        self.batches.append(tuple(mutations))


def _resource_rows(gateway: _Gateway):
    rows = []
    for number, row in enumerate(gateway.tables["Resources"][1:], start=2):
        rows.append((
            number,
            ResourceRecord(
                resource_type=row[0],
                resource_id=row[1],
                revision=int(row[2]),
                payload=json.loads(row[3]),
            ),
        ))
    return rows


def _idempotency_rows(gateway: _Gateway):
    rows = []
    for number, row in enumerate(gateway.tables["Idempotency"][1:], start=2):
        rows.append(WorkspaceIdempotencyRecord(
            row_number=number,
            idempotency_key=row[0],
            operation=row[1],
            request_hash=row[2],
            result=json.loads(row[3]),
            resource_ref=row[5],
        ))
    return rows


class WorkspaceNativeProtocolTests(unittest.TestCase):
    def setUp(self) -> None:
        self.gateway = _Gateway()
        self.adapter = GoogleSheetsStructuredStateAdapter(
            self.gateway,
            clock=lambda: datetime(2026, 8, 29, 8, 34, tzinfo=timezone.utc),
        )

    def test_fingerprint_matches_live_native_proof_and_google_adapter(self) -> None:
        payload = {"proof": "native-google-action", "state": "created"}
        fingerprint = workspace_upsert_fingerprint(
            "entity", "workspace-native-001", payload, expected_revision=0
        )
        self.assertEqual(
            fingerprint,
            "5e738a8828ab0541f35256e0535c44ebb6d5b40db6af0fa8793bff439e5189db",
        )
        self.adapter.upsert(
            "entity",
            "workspace-native-001",
            payload,
            idempotency_key="workspace-native-create-001",
            expected_revision=0,
        )
        self.assertEqual(self.gateway.tables["Resources"][1][6], fingerprint)
        self.assertEqual(self.gateway.tables["Idempotency"][1][2], fingerprint)

    def test_create_plan_matches_adapter_material_and_atomic_batch_shape(self) -> None:
        payload = {"proof": "native-google-action", "state": "created"}
        plan = plan_workspace_upsert(
            "entity",
            "workspace-native-001",
            payload,
            idempotency_key="workspace-native-create-001",
            expected_revision=0,
            resource_rows=[],
            idempotency_rows=[],
        )
        requests = plan.batch_update_requests(
            resources_sheet_id=101,
            idempotency_sheet_id=202,
            timestamp="2026-08-29T08:34:00Z",
        )
        self.assertEqual(len(requests), 2)
        self.assertIn("appendCells", requests[0])
        self.assertIn("appendCells", requests[1])
        resource_values = [
            cell["userEnteredValue"].get("stringValue", cell["userEnteredValue"].get("numberValue"))
            for cell in requests[0]["appendCells"]["rows"][0]["values"]
        ]
        idempotency_values = [
            cell["userEnteredValue"].get("stringValue", cell["userEnteredValue"].get("numberValue"))
            for cell in requests[1]["appendCells"]["rows"][0]["values"]
        ]

        self.adapter.upsert(
            "entity",
            "workspace-native-001",
            payload,
            idempotency_key="workspace-native-create-001",
            expected_revision=0,
        )
        self.assertEqual(resource_values, self.gateway.tables["Resources"][1])
        self.assertEqual(idempotency_values, self.gateway.tables["Idempotency"][1])

    def test_update_plan_targets_existing_row_and_increments_revision(self) -> None:
        current = ResourceRecord(
            "entity",
            "workspace-native-001",
            {"proof": "native-google-action", "state": "created"},
            1,
        )
        plan = plan_workspace_upsert(
            "entity",
            "workspace-native-001",
            {"proof": "native-google-action", "state": "updated"},
            idempotency_key="workspace-native-update-001",
            expected_revision=1,
            resource_rows=[(6, current)],
            idempotency_rows=[],
        )
        self.assertEqual(plan.record.revision, 2)
        requests = plan.batch_update_requests(
            resources_sheet_id=101,
            idempotency_sheet_id=202,
            timestamp="2026-08-29T08:38:00Z",
        )
        update = requests[0]["updateCells"]
        self.assertEqual(update["range"]["startRowIndex"], 5)
        self.assertEqual(update["range"]["endRowIndex"], 6)
        self.assertIn("appendCells", requests[1])

    def test_matching_idempotency_is_read_only_replay(self) -> None:
        payload = {"proof": "native-google-action", "state": "created"}
        first = plan_workspace_upsert(
            "entity",
            "workspace-native-001",
            payload,
            idempotency_key="workspace-native-create-001",
            expected_revision=0,
            resource_rows=[],
            idempotency_rows=[],
        )
        persisted = WorkspaceIdempotencyRecord(
            row_number=8,
            idempotency_key=first.idempotency_key,
            operation="upsert",
            request_hash=first.request_hash,
            result=first.result,
            resource_ref="entity/workspace-native-001",
        )
        replay = plan_workspace_upsert(
            "entity",
            "workspace-native-001",
            payload,
            idempotency_key="workspace-native-create-001",
            expected_revision=0,
            resource_rows=[(6, ResourceRecord("entity", "workspace-native-001", payload, 2))],
            idempotency_rows=[persisted],
        )
        self.assertTrue(replay.idempotent_replay)
        self.assertEqual(replay.batch_update_requests(
            resources_sheet_id=101,
            idempotency_sheet_id=202,
            timestamp="2026-08-29T08:40:00Z",
        ), ())
        self.assertEqual(replay.record.revision, 1)

    def test_same_key_different_material_fails_closed(self) -> None:
        stored = WorkspaceIdempotencyRecord(
            row_number=8,
            idempotency_key="key-1",
            operation="upsert",
            request_hash="different-hash",
            result={"kind": "upsert", "record": {
                "resource_type": "entity",
                "resource_id": "entity-1",
                "payload": {"state": "old"},
                "revision": 1,
            }},
            resource_ref="entity/entity-1",
        )
        with self.assertRaises(IdempotencyConflictError):
            plan_workspace_upsert(
                "entity",
                "entity-1",
                {"state": "new"},
                idempotency_key="key-1",
                expected_revision=0,
                resource_rows=[],
                idempotency_rows=[stored],
            )

    def test_stale_revision_and_duplicate_identity_fail_closed(self) -> None:
        current = ResourceRecord("entity", "entity-1", {"state": "current"}, 2)
        with self.assertRaises(RevisionConflictError):
            plan_workspace_upsert(
                "entity",
                "entity-1",
                {"state": "stale"},
                idempotency_key="stale-key",
                expected_revision=1,
                resource_rows=[(2, current)],
                idempotency_rows=[],
            )
        with self.assertRaises(IdentityConflictError):
            plan_workspace_upsert(
                "entity",
                "entity-1",
                {"state": "next"},
                idempotency_key="next-key",
                expected_revision=2,
                resource_rows=[(2, current), (3, current)],
                idempotency_rows=[],
            )

    def test_exact_readback_is_required(self) -> None:
        plan = plan_workspace_upsert(
            "entity",
            "entity-1",
            {"state": "created"},
            idempotency_key="create-key",
            expected_revision=0,
            resource_rows=[],
            idempotency_rows=[],
        )
        idem = WorkspaceIdempotencyRecord(
            row_number=2,
            idempotency_key=plan.idempotency_key,
            operation="upsert",
            request_hash=plan.request_hash,
            result=plan.result,
            resource_ref="entity/entity-1",
        )
        verify_workspace_upsert_readback(
            plan,
            resource_rows=[(2, plan.record)],
            idempotency_rows=[idem],
        )
        with self.assertRaises(WorkspaceReadbackError):
            verify_workspace_upsert_readback(
                plan,
                resource_rows=[(2, ResourceRecord("entity", "entity-1", {"state": "wrong"}, 1))],
                idempotency_rows=[idem],
            )


if __name__ == "__main__":
    unittest.main()
