"""Deterministic tests for the synthetic structured-state adapter."""

import unittest

from mira.structured_state import (
    IdempotencyConflictError,
    IdentityConflictError,
    InMemoryStructuredStateAdapter,
    NotFoundError,
    RevisionConflictError,
    ValidationError,
)


class InMemoryStructuredStateAdapterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.store = InMemoryStructuredStateAdapter(
            schema_version="1",
            resource_types=("entity", "task"),
            event_types=("created", "updated"),
        )

    def test_health_and_schema_are_explicit(self) -> None:
        health = self.store.health()
        self.assertTrue(health.ok)
        self.assertEqual(health.adapter, "memory")
        self.assertEqual(health.schema_version, "1")
        schema = self.store.schema()
        self.assertEqual(schema.resource_types, ("entity", "task"))
        self.assertEqual(schema.event_types, ("created", "updated"))

    def test_create_read_update_and_monotonic_revision(self) -> None:
        created = self.store.upsert(
            "entity",
            "entity-001",
            {"name": "Alpha", "nested": {"count": 1}},
            idempotency_key="create-001",
            expected_revision=0,
        )
        self.assertFalse(created.idempotent_replay)
        self.assertEqual(created.record.revision, 1)
        self.assertEqual(self.store.get("entity", "entity-001"), created.record)

        updated = self.store.upsert(
            "entity",
            "entity-001",
            {"name": "Beta"},
            idempotency_key="update-001",
            expected_revision=1,
        )
        self.assertEqual(updated.record.revision, 2)
        self.assertEqual(self.store.get("entity", "entity-001"), updated.record)

    def test_readback_is_isolated_from_caller_mutation(self) -> None:
        payload = {"name": "Alpha", "tags": ["one"]}
        result = self.store.upsert(
            "entity", "entity-001", payload, idempotency_key="create-001"
        )
        payload["tags"].append("caller-change")
        result.record.payload["tags"].append("returned-object-change")
        readback = self.store.get("entity", "entity-001")
        self.assertEqual(readback.payload, {"name": "Alpha", "tags": ["one"]})

    def test_exact_idempotent_replay_does_not_mutate_again(self) -> None:
        first = self.store.upsert(
            "entity",
            "entity-001",
            {"name": "Alpha"},
            idempotency_key="same-key",
            expected_revision=0,
        )
        second = self.store.upsert(
            "entity",
            "entity-001",
            {"name": "Alpha"},
            idempotency_key="same-key",
            expected_revision=0,
        )
        self.assertFalse(first.idempotent_replay)
        self.assertTrue(second.idempotent_replay)
        self.assertEqual(second.record.revision, 1)
        self.assertEqual(self.store.get("entity", "entity-001").revision, 1)

    def test_idempotency_key_reuse_with_different_input_fails_closed(self) -> None:
        self.store.upsert(
            "entity", "entity-001", {"name": "Alpha"}, idempotency_key="same-key"
        )
        with self.assertRaises(IdempotencyConflictError):
            self.store.upsert(
                "entity", "entity-001", {"name": "Beta"}, idempotency_key="same-key"
            )
        self.assertEqual(self.store.get("entity", "entity-001").payload["name"], "Alpha")

    def test_stale_revision_leaves_state_unchanged(self) -> None:
        self.store.upsert(
            "entity",
            "entity-001",
            {"name": "Alpha"},
            idempotency_key="create-001",
            expected_revision=0,
        )
        with self.assertRaises(RevisionConflictError):
            self.store.upsert(
                "entity",
                "entity-001",
                {"name": "Stale"},
                idempotency_key="stale-001",
                expected_revision=0,
            )
        readback = self.store.get("entity", "entity-001")
        self.assertEqual(readback.revision, 1)
        self.assertEqual(readback.payload["name"], "Alpha")

    def test_bounded_query_filters_and_sorts(self) -> None:
        self.store.upsert(
            "task", "task-002", {"status": "open"}, idempotency_key="task-002"
        )
        self.store.upsert(
            "task", "task-001", {"status": "open"}, idempotency_key="task-001"
        )
        self.store.upsert(
            "task", "task-003", {"status": "done"}, idempotency_key="task-003"
        )
        rows = self.store.query("task", filters={"status": "open"}, limit=2)
        self.assertEqual([row.resource_id for row in rows], ["task-001", "task-002"])
        with self.assertRaises(ValidationError):
            self.store.query("task", limit=0)

    def test_unknown_resource_and_invalid_payload_fail_closed(self) -> None:
        with self.assertRaises(ValidationError):
            self.store.upsert(
                "unknown", "x-001", {"x": 1}, idempotency_key="bad-resource"
            )
        with self.assertRaises(ValidationError):
            self.store.upsert(
                "entity",
                "entity-001",
                {"bad": {1, 2}},
                idempotency_key="bad-payload",
            )
        with self.assertRaises(NotFoundError):
            self.store.get("entity", "missing")

    def test_event_append_replay_conflict_and_ordered_readback(self) -> None:
        first = self.store.append_event(
            "entity",
            "entity-001",
            "created",
            "event-001",
            {"source": "synthetic"},
            idempotency_key="event-key-001",
            expected_stream_revision=0,
        )
        replay = self.store.append_event(
            "entity",
            "entity-001",
            "created",
            "event-001",
            {"source": "synthetic"},
            idempotency_key="event-key-001",
            expected_stream_revision=0,
        )
        self.assertFalse(first.idempotent_replay)
        self.assertTrue(replay.idempotent_replay)
        self.assertEqual(replay.event.stream_revision, 1)

        second = self.store.append_event(
            "entity",
            "entity-001",
            "updated",
            "event-002",
            {"field": "name"},
            idempotency_key="event-key-002",
            expected_stream_revision=1,
        )
        self.assertEqual(second.event.stream_revision, 2)
        events = self.store.events_for("entity", "entity-001", after_revision=0)
        self.assertEqual([event.event_id for event in events], ["event-001", "event-002"])

        with self.assertRaises(RevisionConflictError):
            self.store.append_event(
                "entity",
                "entity-001",
                "updated",
                "event-003",
                {"field": "status"},
                idempotency_key="event-key-003",
                expected_stream_revision=1,
            )
        self.assertEqual(len(self.store.events_for("entity", "entity-001")), 2)

    def test_duplicate_event_identity_with_new_idempotency_key_fails(self) -> None:
        self.store.append_event(
            "entity",
            "entity-001",
            "created",
            "event-001",
            {},
            idempotency_key="event-key-001",
        )
        with self.assertRaises(IdentityConflictError):
            self.store.append_event(
                "entity",
                "entity-001",
                "created",
                "event-001",
                {},
                idempotency_key="event-key-002",
            )

    def test_unknown_event_type_fails_closed(self) -> None:
        with self.assertRaises(ValidationError):
            self.store.append_event(
                "entity",
                "entity-001",
                "invented",
                "event-001",
                {},
                idempotency_key="event-key-001",
            )


if __name__ == "__main__":
    unittest.main()
