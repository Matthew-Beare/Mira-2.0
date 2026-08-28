"""Deterministic tests for transport-independent API service semantics."""

import unittest

from mira.api_core import (
    ApiAuthorizationError,
    ApiCompatibilityError,
    ApiConflictError,
    ApiReadbackError,
    ApiService,
    ApiValidationError,
    AuthenticatedPrincipal,
    CommandEnvelope,
    Grant,
    InMemoryAuditSink,
    QueryEnvelope,
)
from mira.authority import AuthorityRegistry, AuthoritySpec
from mira.structured_state import InMemoryStructuredStateAdapter


class CorruptingReadbackAdapter(InMemoryStructuredStateAdapter):
    """Test double that corrupts readback only after a successful mutation."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.corrupt = False

    def upsert(self, *args, **kwargs):
        result = super().upsert(*args, **kwargs)
        self.corrupt = True
        return result

    def get(self, resource_type, resource_id):
        record = super().get(resource_type, resource_id)
        if not self.corrupt:
            return record
        return type(record)(
            resource_type=record.resource_type,
            resource_id=record.resource_id,
            payload={**record.payload, "corrupt": True},
            revision=record.revision,
        )


class ApiServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.registry_store = InMemoryStructuredStateAdapter(
            schema_version="registry-1",
            resource_types=("authority", "authority_binding"),
            event_types=("registered", "activated"),
        )
        self.registry = AuthorityRegistry(self.registry_store)
        self.data = InMemoryStructuredStateAdapter(
            schema_version="data-1",
            resource_types=("entity",),
            event_types=("created", "updated"),
        )
        spec = AuthoritySpec(
            authority_id="auth-primary",
            adapter_key="memory-primary",
            resource_ref="synthetic-primary",
            namespace="mira2-test",
            failure_domain="process-a",
            owner_id="user-001",
            schema_version="data-1",
            verified=True,
            enabled=True,
        )
        self.registry.register_authority(
            spec,
            idempotency_key="register-authority",
            expected_revision=0,
        )
        self.registry.register_runtime_adapter("memory-primary", self.data)
        self.registry.activate(
            "entity",
            "auth-primary",
            idempotency_key="bind-entity",
            expected_revision=0,
        )
        self.audit = InMemoryAuditSink()
        self.service = ApiService(
            self.registry,
            self.audit,
            api_major=1,
            schema_version="mira-api-1",
        )
        self.principal = AuthenticatedPrincipal(
            actor_id="user-001",
            client_id="client-001",
            grants=(
                Grant("entity", "read", "*"),
                Grant("entity", "query", "*"),
                Grant("entity", "upsert", "*"),
                Grant("entity", "append_event", "*"),
            ),
        )

    def command(self, **overrides):
        values = {
            "command_id": "cmd-001",
            "subject_id": "user-001",
            "data_class": "entity",
            "action": "upsert",
            "api_major": 1,
            "schema_version": "mira-api-1",
            "resource_id": "entity-001",
            "payload": {"name": "Alpha"},
            "idempotency_key": "idem-001",
            "expected_revision": 0,
        }
        values.update(overrides)
        return CommandEnvelope(**values)

    def query(self, **overrides):
        values = {
            "request_id": "qry-001",
            "subject_id": "user-001",
            "data_class": "entity",
            "action": "read",
            "api_major": 1,
            "schema_version": "mira-api-1",
            "resource_id": "entity-001",
        }
        values.update(overrides)
        return QueryEnvelope(**values)

    def test_upsert_readback_and_exact_replay(self) -> None:
        first = self.service.execute_command(self.principal, self.command())
        second = self.service.execute_command(self.principal, self.command())
        self.assertTrue(first.readback_verified)
        self.assertFalse(first.idempotent_replay)
        self.assertTrue(second.idempotent_replay)
        self.assertEqual(first.record, second.record)
        self.assertEqual(first.record.revision, 1)

        read = self.service.execute_query(self.principal, self.query())
        self.assertEqual(read.authority_id, "auth-primary")
        self.assertEqual(read.items, (first.record,))

    def test_bounded_query_requires_class_level_grant(self) -> None:
        self.service.execute_command(
            self.principal,
            self.command(command_id="cmd-a", resource_id="entity-002", idempotency_key="idem-a"),
        )
        query = QueryEnvelope(
            request_id="qry-list",
            subject_id="user-001",
            data_class="entity",
            action="query",
            api_major=1,
            schema_version="mira-api-1",
            filters={"name": "Alpha"},
            limit=10,
        )
        result = self.service.execute_query(self.principal, query)
        self.assertEqual([item.resource_id for item in result.items], ["entity-002"])

        narrow = AuthenticatedPrincipal(
            actor_id="user-001",
            client_id="client-narrow",
            grants=(Grant("entity", "read", "entity-002"),),
        )
        with self.assertRaises(ApiAuthorizationError):
            self.service.execute_query(narrow, query)

    def test_exact_resource_authorization_denies_other_resource(self) -> None:
        narrow = AuthenticatedPrincipal(
            actor_id="user-001",
            client_id="client-narrow",
            grants=(Grant("entity", "upsert", "entity-allowed"),),
        )
        with self.assertRaises(ApiAuthorizationError):
            self.service.execute_command(
                narrow,
                self.command(resource_id="entity-denied", idempotency_key="denied-key"),
            )
        self.assertEqual(self.audit.events()[-1].outcome, "denied")
        self.assertEqual(self.audit.events()[-1].authorization, "denied")

    def test_cross_person_request_fails_before_state_mutation(self) -> None:
        with self.assertRaises(ApiAuthorizationError):
            self.service.execute_command(
                self.principal,
                self.command(subject_id="user-002", idempotency_key="cross-person"),
            )
        self.assertEqual(self.data.query("entity"), ())
        self.assertEqual(self.audit.events()[-1].error_code, "authorization_error")

    def test_compatibility_failure_prevents_mutation(self) -> None:
        with self.assertRaises(ApiCompatibilityError):
            self.service.execute_command(
                self.principal,
                self.command(api_major=2, idempotency_key="wrong-version"),
            )
        self.assertEqual(self.data.query("entity"), ())
        event = self.audit.events()[-1]
        self.assertEqual(event.authorization, "not_evaluated")
        self.assertEqual(event.error_code, "compatibility_error")

    def test_revision_conflict_maps_to_stable_api_conflict(self) -> None:
        self.service.execute_command(self.principal, self.command())
        with self.assertRaises(ApiConflictError):
            self.service.execute_command(
                self.principal,
                self.command(
                    command_id="cmd-stale",
                    payload={"name": "Stale"},
                    idempotency_key="stale-key",
                    expected_revision=0,
                ),
            )
        readback = self.data.get("entity", "entity-001")
        self.assertEqual(readback.payload, {"name": "Alpha"})
        self.assertEqual(readback.revision, 1)
        self.assertEqual(self.audit.events()[-1].error_code, "conflict")

    def test_idempotency_key_reuse_maps_to_conflict(self) -> None:
        self.service.execute_command(self.principal, self.command())
        with self.assertRaises(ApiConflictError):
            self.service.execute_command(
                self.principal,
                self.command(
                    command_id="cmd-changed",
                    payload={"name": "Beta"},
                    idempotency_key="idem-001",
                    expected_revision=1,
                ),
            )
        self.assertEqual(self.data.get("entity", "entity-001").payload["name"], "Alpha")

    def test_append_event_is_read_back_and_replay_safe(self) -> None:
        envelope = self.command(
            command_id="cmd-event",
            action="append_event",
            payload={"source": "api"},
            idempotency_key="event-key",
            expected_revision=0,
            event_id="event-001",
            event_type="created",
        )
        first = self.service.execute_command(self.principal, envelope)
        replay = self.service.execute_command(self.principal, envelope)
        self.assertTrue(first.readback_verified)
        self.assertFalse(first.idempotent_replay)
        self.assertTrue(replay.idempotent_replay)
        self.assertEqual(replay.event, first.event)
        self.assertEqual(len(self.data.events_for("entity", "entity-001")), 1)

    def test_malformed_action_and_missing_idempotency_fail_preflight(self) -> None:
        with self.assertRaises(ApiValidationError):
            self.service.execute_command(
                self.principal,
                self.command(action="delete", idempotency_key="delete-key"),
            )
        with self.assertRaises(ApiValidationError):
            self.service.execute_command(
                self.principal,
                self.command(command_id="cmd-empty", idempotency_key=""),
            )
        self.assertEqual(self.data.query("entity"), ())

    def test_exact_readback_mismatch_fails_explicitly(self) -> None:
        registry_store = InMemoryStructuredStateAdapter(
            schema_version="registry-1",
            resource_types=("authority", "authority_binding"),
            event_types=("registered", "activated"),
        )
        registry = AuthorityRegistry(registry_store)
        corrupt = CorruptingReadbackAdapter(
            schema_version="data-1",
            resource_types=("entity",),
            event_types=("created",),
        )
        registry.register_authority(
            AuthoritySpec(
                authority_id="auth-corrupt",
                adapter_key="corrupt",
                resource_ref="synthetic-corrupt",
                namespace="mira2-test",
                failure_domain="process-c",
                owner_id="user-001",
                schema_version="data-1",
                verified=True,
            ),
            idempotency_key="register-corrupt",
            expected_revision=0,
        )
        registry.register_runtime_adapter("corrupt", corrupt)
        registry.activate(
            "entity",
            "auth-corrupt",
            idempotency_key="bind-corrupt",
            expected_revision=0,
        )
        audit = InMemoryAuditSink()
        service = ApiService(registry, audit, api_major=1, schema_version="mira-api-1")
        with self.assertRaises(ApiReadbackError):
            service.execute_command(self.principal, self.command())
        self.assertEqual(audit.events()[-1].error_code, "readback_error")

    def test_success_audit_contains_exact_identity_action_and_authority(self) -> None:
        self.service.execute_command(self.principal, self.command())
        event = self.audit.events()[-1]
        self.assertEqual(event.request_id, "cmd-001")
        self.assertEqual(event.actor_id, "user-001")
        self.assertEqual(event.client_id, "client-001")
        self.assertEqual(event.subject_id, "user-001")
        self.assertEqual(event.data_class, "entity")
        self.assertEqual(event.action, "upsert")
        self.assertEqual(event.resource_id, "entity-001")
        self.assertEqual(event.authorization, "allowed")
        self.assertEqual(event.outcome, "success")
        self.assertEqual(event.authority_id, "auth-primary")
        self.assertIsNone(event.error_code)


if __name__ == "__main__":
    unittest.main()
