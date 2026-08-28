"""Deterministic contract tests for the Google Sheets structured-state adapter."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import json
import unittest
from unittest.mock import patch

from mira.google_sheets_store import (
    GoogleSheetsRestGateway,
    GoogleSheetsStructuredStateAdapter,
    SheetRowMutation,
)
from mira.structured_state import (
    IdempotencyConflictError,
    IdentityConflictError,
    NotFoundError,
    RevisionConflictError,
    ValidationError,
)


class FakeSheetsGateway:
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
            "Resources": [
                [
                    "resource_type",
                    "resource_id",
                    "revision",
                    "payload_json",
                    "updated_at",
                    "last_idempotency_key",
                    "request_hash",
                ]
            ],
            "Events": [
                [
                    "event_type",
                    "event_id",
                    "stream_type",
                    "stream_id",
                    "stream_revision",
                    "payload_json",
                    "occurred_at",
                    "idempotency_key",
                ]
            ],
            "Idempotency": [
                [
                    "idempotency_key",
                    "operation",
                    "request_hash",
                    "result_json",
                    "created_at",
                    "resource_ref",
                ]
            ],
        }
        self.batches: list[tuple[SheetRowMutation, ...]] = []

    def read_range(self, a1_range: str):
        tab = a1_range.split("!", 1)[0]
        return tuple(tuple(row) for row in self.tables[tab])

    def apply_mutations(self, mutations):
        staged = deepcopy(self.tables)
        for mutation in mutations:
            table = staged[mutation.tab]
            row = list(mutation.values)
            if mutation.row_number is None:
                table.append(row)
            else:
                table[mutation.row_number - 1] = row
        self.tables = staged
        self.batches.append(tuple(mutations))


class GoogleSheetsStructuredStateAdapterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.gateway = FakeSheetsGateway()
        self.adapter = GoogleSheetsStructuredStateAdapter(
            self.gateway,
            clock=lambda: datetime(2026, 8, 28, 12, 0, tzinfo=timezone.utc),
        )

    def test_health_and_schema_are_provider_backed(self) -> None:
        health = self.adapter.health()
        self.assertTrue(health.ok)
        self.assertEqual(health.adapter, "google-sheets")
        schema = self.adapter.schema()
        self.assertEqual(schema.schema_version, "mira-structured-state-v1")
        self.assertEqual(schema.resource_types, ("entity",))
        self.assertEqual(schema.event_types, ("created", "updated"))

    def test_create_read_query_update_replay_and_conflicts(self) -> None:
        created = self.adapter.upsert(
            "entity",
            "entity-002",
            {"name": "Beta", "group": "test"},
            idempotency_key="create-002",
            expected_revision=0,
        )
        self.assertFalse(created.idempotent_replay)
        self.assertEqual(created.record.revision, 1)
        self.assertEqual(self.adapter.get("entity", "entity-002"), created.record)
        self.assertEqual(
            self.adapter.query("entity", filters={"group": "test"}),
            (created.record,),
        )

        updated = self.adapter.upsert(
            "entity",
            "entity-002",
            {"name": "Gamma", "group": "test"},
            idempotency_key="update-002",
            expected_revision=1,
        )
        self.assertEqual(updated.record.revision, 2)
        self.assertEqual(len(self.gateway.batches), 2)

        replay = self.adapter.upsert(
            "entity",
            "entity-002",
            {"name": "Gamma", "group": "test"},
            idempotency_key="update-002",
            expected_revision=1,
        )
        self.assertTrue(replay.idempotent_replay)
        self.assertEqual(replay.record, updated.record)
        self.assertEqual(len(self.gateway.batches), 2)

        with self.assertRaises(IdempotencyConflictError):
            self.adapter.upsert(
                "entity",
                "entity-002",
                {"name": "Different"},
                idempotency_key="update-002",
                expected_revision=2,
            )
        with self.assertRaises(RevisionConflictError):
            self.adapter.upsert(
                "entity",
                "entity-002",
                {"name": "Stale"},
                idempotency_key="stale-002",
                expected_revision=1,
            )
        self.assertEqual(self.adapter.get("entity", "entity-002").payload["name"], "Gamma")

    def test_append_events_replay_and_ordered_readback(self) -> None:
        first = self.adapter.append_event(
            "entity",
            "entity-002",
            "created",
            "event-002-a",
            {"source": "test"},
            idempotency_key="event-key-a",
            expected_stream_revision=0,
        )
        second = self.adapter.append_event(
            "entity",
            "entity-002",
            "updated",
            "event-002-b",
            {"field": "name"},
            idempotency_key="event-key-b",
            expected_stream_revision=1,
        )
        self.assertEqual(first.event.stream_revision, 1)
        self.assertEqual(second.event.stream_revision, 2)
        self.assertEqual(
            [event.event_id for event in self.adapter.events_for("entity", "entity-002")],
            ["event-002-a", "event-002-b"],
        )
        replay = self.adapter.append_event(
            "entity",
            "entity-002",
            "updated",
            "event-002-b",
            {"field": "name"},
            idempotency_key="event-key-b",
            expected_stream_revision=1,
        )
        self.assertTrue(replay.idempotent_replay)
        self.assertEqual(replay.event, second.event)
        with self.assertRaises(IdentityConflictError):
            self.adapter.append_event(
                "entity",
                "entity-002",
                "updated",
                "event-002-b",
                {"field": "other"},
                idempotency_key="event-key-c",
                expected_stream_revision=2,
            )

    def test_fail_closed_validation_and_not_found(self) -> None:
        with self.assertRaises(ValidationError):
            self.adapter.query("unknown")
        with self.assertRaises(ValidationError):
            self.adapter.upsert("entity", "bad id", {}, idempotency_key="key")
        with self.assertRaises(NotFoundError):
            self.adapter.get("entity", "missing")

    def test_duplicate_persisted_identity_fails_closed(self) -> None:
        row = [
            "entity",
            "dup-001",
            1,
            '{"name":"A"}',
            "2026-08-28T12:00:00Z",
            "key-a",
            "hash-a",
        ]
        self.gateway.tables["Resources"].append(row)
        self.gateway.tables["Resources"].append(list(row))
        with self.assertRaises(IdentityConflictError):
            self.adapter.get("entity", "dup-001")

    def test_writer_model_is_explicit_capability_boundary(self) -> None:
        self.gateway.tables["Metadata"][-1][1] = "distributed"
        self.assertFalse(self.adapter.health().ok)
        with self.assertRaisesRegex(ValidationError, "writer_model=single_writer"):
            self.adapter.schema()


class _FakeHttpResponse:
    def __init__(self, payload):
        self.payload = json.dumps(payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return self.payload


class GoogleSheetsRestGatewayTests(unittest.TestCase):
    def test_read_range_uses_bearer_and_unformatted_values(self) -> None:
        seen = []

        def fake_urlopen(request, timeout):
            seen.append((request, timeout))
            return _FakeHttpResponse({"values": [["a", 1]]})

        gateway = GoogleSheetsRestGateway(
            spreadsheet_id="sheet-123",
            access_token_provider=lambda: "secret-token",
        )
        with patch("mira.google_sheets_store.urlopen", side_effect=fake_urlopen):
            rows = gateway.read_range("Resources!A1:B2")
        self.assertEqual(rows, (("a", 1),))
        request, timeout = seen[0]
        self.assertEqual(request.get_header("Authorization"), "Bearer secret-token")
        self.assertIn("valueRenderOption=UNFORMATTED_VALUE", request.full_url)
        self.assertGreater(timeout, 0)

    def test_apply_mutations_builds_single_atomic_batch(self) -> None:
        responses = [
            _FakeHttpResponse(
                {
                    "sheets": [
                        {"properties": {"sheetId": 10, "title": "Resources"}},
                        {"properties": {"sheetId": 20, "title": "Idempotency"}},
                    ]
                }
            ),
            _FakeHttpResponse({}),
        ]
        seen = []

        def fake_urlopen(request, timeout):
            seen.append(request)
            return responses.pop(0)

        gateway = GoogleSheetsRestGateway(
            spreadsheet_id="sheet-123",
            access_token_provider=lambda: "token",
        )
        with patch("mira.google_sheets_store.urlopen", side_effect=fake_urlopen):
            gateway.apply_mutations(
                [
                    SheetRowMutation("Resources", ("entity", "a", 2), row_number=2),
                    SheetRowMutation("Idempotency", ("key", "upsert", "hash")),
                ]
            )
        self.assertEqual(len(seen), 2)
        body = json.loads(seen[1].data.decode("utf-8"))
        self.assertEqual(len(body["requests"]), 2)
        self.assertIn("updateCells", body["requests"][0])
        self.assertIn("appendCells", body["requests"][1])


if __name__ == "__main__":
    unittest.main()
