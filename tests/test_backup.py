"""Direct tests for provider-neutral current-resource backup and isolated restore."""

from dataclasses import replace
import json
import unittest

from mira.backup import (
    EVENT_COVERAGE,
    IDEMPOTENCY_COVERAGE,
    RESOURCE_COVERAGE,
    BackupArtifact,
    BackupIntegrityError,
    BackupService,
    BackupValidationError,
)
from mira.structured_state import (
    InMemoryStructuredStateAdapter,
    MutationResult,
    ResourceRecord,
    SchemaInfo,
)


def _store(*, schema_version: str = "1") -> InMemoryStructuredStateAdapter:
    return InMemoryStructuredStateAdapter(
        schema_version=schema_version,
        resource_types=("entity", "task"),
        event_types=("created", "updated"),
    )


def _seed(store: InMemoryStructuredStateAdapter, *, reverse: bool = False) -> None:
    operations = [
        ("entity", "entity-002", {"name": "Beta"}, "entity-002-r1", 0),
        ("entity", "entity-001", {"name": "Alpha"}, "entity-001-r1", 0),
        ("task", "task-001", {"status": "open"}, "task-001-r1", 0),
    ]
    if reverse:
        operations.reverse()
    for resource_type, resource_id, payload, key, expected in operations:
        store.upsert(
            resource_type,
            resource_id,
            payload,
            idempotency_key=key,
            expected_revision=expected,
        )
    store.upsert(
        "entity",
        "entity-001",
        {"name": "Alpha", "status": "verified"},
        idempotency_key="entity-001-r2",
        expected_revision=1,
    )


class _TrackingAdapter:
    def __init__(self, inner: InMemoryStructuredStateAdapter) -> None:
        self.inner = inner
        self.upsert_calls = 0
        self.event_calls = 0

    def health(self):
        return self.inner.health()

    def schema(self):
        return self.inner.schema()

    def get(self, resource_type, resource_id):
        return self.inner.get(resource_type, resource_id)

    def query(self, resource_type, *, filters=None, limit=100):
        return self.inner.query(resource_type, filters=filters, limit=limit)

    def upsert(self, resource_type, resource_id, payload, *, idempotency_key, expected_revision=None):
        self.upsert_calls += 1
        return self.inner.upsert(
            resource_type,
            resource_id,
            payload,
            idempotency_key=idempotency_key,
            expected_revision=expected_revision,
        )

    def append_event(
        self,
        stream_type,
        stream_id,
        event_type,
        event_id,
        payload,
        *,
        idempotency_key,
        expected_stream_revision=None,
    ):
        self.event_calls += 1
        return self.inner.append_event(
            stream_type,
            stream_id,
            event_type,
            event_id,
            payload,
            idempotency_key=idempotency_key,
            expected_stream_revision=expected_stream_revision,
        )

    def events_for(self, stream_type, stream_id, *, after_revision=0, limit=100):
        return self.inner.events_for(
            stream_type,
            stream_id,
            after_revision=after_revision,
            limit=limit,
        )


class _ReadbackDriftAdapter(_TrackingAdapter):
    """Behaves during writes, then corrupts query readback after restore begins."""

    def query(self, resource_type, *, filters=None, limit=100):
        rows = self.inner.query(resource_type, filters=filters, limit=limit)
        if self.upsert_calls and rows:
            first = rows[0]
            changed = ResourceRecord(
                resource_type=first.resource_type,
                resource_id=first.resource_id,
                payload={**first.payload, "drifted": True},
                revision=first.revision,
            )
            return (changed, *rows[1:])
        return rows


class _ReplayOnlyTarget:
    """Simulates hidden prior restore idempotency despite empty visible Resources."""

    def __init__(self) -> None:
        self.inner = _store()

    def health(self):
        return self.inner.health()

    def schema(self):
        return self.inner.schema()

    def get(self, resource_type, resource_id):
        return self.inner.get(resource_type, resource_id)

    def query(self, resource_type, *, filters=None, limit=100):
        return ()

    def upsert(self, resource_type, resource_id, payload, *, idempotency_key, expected_revision=None):
        return MutationResult(
            record=ResourceRecord(
                resource_type=resource_type,
                resource_id=resource_id,
                payload=dict(payload),
                revision=(expected_revision or 0) + 1,
            ),
            idempotent_replay=True,
        )

    def append_event(self, *args, **kwargs):
        raise AssertionError("restore must not append Events")

    def events_for(self, *args, **kwargs):
        return ()


class _ThousandRowAdapter:
    def schema(self):
        return SchemaInfo(
            schema_version="1",
            resource_types=("entity",),
            event_types=("created",),
        )

    def query(self, resource_type, *, filters=None, limit=100):
        return tuple(
            ResourceRecord(
                resource_type="entity",
                resource_id=f"entity-{index:04d}",
                payload={"index": index},
                revision=1,
            )
            for index in range(1000)
        )


class BackupServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = BackupService()

    def test_export_is_deterministic_and_declares_exact_coverage(self) -> None:
        first = _store()
        second = _store()
        _seed(first)
        _seed(second, reverse=True)

        first.append_event(
            "entity",
            "entity-001",
            "created",
            "event-001",
            {"source": "synthetic"},
            idempotency_key="event-001",
            expected_stream_revision=0,
        )

        artifact_a = self.service.create(first)
        artifact_b = self.service.create(second)

        self.assertEqual(artifact_a.to_json(), artifact_b.to_json())
        self.assertEqual(artifact_a.material_sha256, artifact_b.material_sha256)
        self.assertEqual(artifact_a.resource_count, 3)
        self.assertEqual(artifact_a.resource_coverage, RESOURCE_COVERAGE)
        self.assertEqual(artifact_a.event_coverage, EVENT_COVERAGE)
        self.assertEqual(artifact_a.idempotency_coverage, IDEMPOTENCY_COVERAGE)
        self.assertEqual(
            [(row.resource_type, row.resource_id, row.revision) for row in artifact_a.resources],
            [
                ("entity", "entity-001", 2),
                ("entity", "entity-002", 1),
                ("task", "task-001", 1),
            ],
        )

    def test_backup_creation_performs_zero_source_writes(self) -> None:
        inner = _store()
        _seed(inner)
        inner.append_event(
            "entity",
            "entity-001",
            "created",
            "event-001",
            {},
            idempotency_key="event-001",
            expected_stream_revision=0,
        )
        source = _TrackingAdapter(inner)
        before_resources = {
            resource_type: inner.query(resource_type, limit=1000)
            for resource_type in inner.schema().resource_types
        }
        before_events = inner.events_for("entity", "entity-001")

        self.service.create(source)

        self.assertEqual(source.upsert_calls, 0)
        self.assertEqual(source.event_calls, 0)
        self.assertEqual(
            before_resources,
            {
                resource_type: inner.query(resource_type, limit=1000)
                for resource_type in inner.schema().resource_types
            },
        )
        self.assertEqual(before_events, inner.events_for("entity", "entity-001"))

    def test_empty_target_restore_preserves_current_resource_revision_and_material(self) -> None:
        source = _store()
        _seed(source)
        source.upsert(
            "entity",
            "entity-001",
            {"name": "Alpha", "status": "final"},
            idempotency_key="entity-001-r3",
            expected_revision=2,
        )
        artifact = self.service.create(source)
        target = _store()

        result = self.service.restore(artifact.to_json(), target)

        self.assertEqual(result.restored_resource_count, 3)
        self.assertEqual(result.verified_material_sha256, artifact.material_sha256)
        self.assertEqual(target.get("entity", "entity-001").revision, 3)
        self.assertEqual(
            target.get("entity", "entity-001").payload,
            {"name": "Alpha", "status": "final"},
        )
        self.assertEqual(target.events_for("entity", "entity-001"), ())
        self.assertEqual(self.service.create(target).to_json(), artifact.to_json())

    def test_tampered_digest_and_malformed_artifact_fail_closed(self) -> None:
        source = _store()
        _seed(source)
        artifact = self.service.create(source)
        material = json.loads(artifact.to_json())
        material["resources"][0]["payload"]["tampered"] = True

        with self.assertRaises(BackupIntegrityError):
            self.service.verify(json.dumps(material))
        with self.assertRaises(BackupValidationError):
            self.service.verify("not-json")

        bool_version = json.loads(artifact.to_json())
        bool_version["artifact_version"] = True
        with self.assertRaises(BackupValidationError):
            self.service.verify(json.dumps(bool_version))

    def test_direct_artifact_object_cannot_bypass_sort_or_duplicate_validation(self) -> None:
        source = _store()
        _seed(source)
        artifact = self.service.create(source)

        unsorted = replace(artifact, resources=tuple(reversed(artifact.resources)))
        with self.assertRaises(BackupValidationError):
            self.service.verify(unsorted)

        duplicate = replace(
            artifact,
            resources=(artifact.resources[0], artifact.resources[0], *artifact.resources[1:]),
        )
        with self.assertRaises(BackupValidationError):
            self.service.verify(duplicate)

    def test_incompatible_or_nonempty_restore_target_is_rejected_before_restore(self) -> None:
        source = _store()
        _seed(source)
        artifact = self.service.create(source)

        incompatible = _store(schema_version="2")
        with self.assertRaises(BackupValidationError):
            self.service.restore(artifact, incompatible)
        self.assertEqual(incompatible.query("entity"), ())

        nonempty = _store()
        nonempty.upsert(
            "task",
            "existing-task",
            {"status": "existing"},
            idempotency_key="existing-task",
            expected_revision=0,
        )
        with self.assertRaises(BackupValidationError):
            self.service.restore(artifact, nonempty)
        self.assertEqual(nonempty.get("task", "existing-task").revision, 1)
        self.assertEqual(nonempty.query("entity"), ())

    def test_independent_readback_drift_fails_restore_verification(self) -> None:
        source = _store()
        _seed(source)
        artifact = self.service.create(source)
        target = _ReadbackDriftAdapter(_store())

        with self.assertRaises(BackupIntegrityError):
            self.service.restore(artifact, target)
        self.assertGreater(target.upsert_calls, 0)

    def test_hidden_restore_idempotency_replay_is_rejected_as_not_fresh(self) -> None:
        source = _store()
        _seed(source)
        artifact = self.service.create(source)

        with self.assertRaisesRegex(BackupIntegrityError, "not fresh"):
            self.service.restore(artifact, _ReplayOnlyTarget())

    def test_exact_query_bound_fails_when_export_completeness_cannot_be_proven(self) -> None:
        with self.assertRaisesRegex(BackupIntegrityError, "cannot prove complete export"):
            self.service.create(_ThousandRowAdapter())

    def test_roundtrip_parser_preserves_canonical_json_exactly(self) -> None:
        source = _store()
        _seed(source)
        artifact = self.service.create(source)

        reparsed = BackupArtifact.from_json(artifact.to_json())

        self.assertEqual(reparsed, artifact)
        self.assertEqual(reparsed.to_json(), artifact.to_json())


if __name__ == "__main__":
    unittest.main()
