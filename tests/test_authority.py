"""Deterministic tests for canonical Authority Registry routing."""

import unittest

from mira.authority import (
    AuthorityBindingNotFoundError,
    AuthorityRegistry,
    AuthoritySchemaError,
    AuthoritySpec,
    AuthorityUnavailableError,
)
from mira.structured_state import (
    InMemoryStructuredStateAdapter,
    RevisionConflictError,
)


class UnhealthyAdapter(InMemoryStructuredStateAdapter):
    def health(self):
        health = super().health()
        return type(health)(
            ok=False,
            adapter=health.adapter,
            schema_version=health.schema_version,
        )


class AuthorityRegistryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.registry_store = InMemoryStructuredStateAdapter(
            schema_version="registry-1",
            resource_types=("authority", "authority_binding"),
            event_types=("registered", "activated"),
        )
        self.registry = AuthorityRegistry(self.registry_store)
        self.data_adapter = InMemoryStructuredStateAdapter(
            schema_version="data-1",
            resource_types=("entity",),
            event_types=("created", "updated"),
        )
        self.spec = AuthoritySpec(
            authority_id="auth-primary",
            adapter_key="memory-primary",
            resource_ref="synthetic-primary",
            namespace="mira2-test",
            failure_domain="process-a",
            owner_id="owner-001",
            schema_version="data-1",
            verified=True,
            enabled=True,
        )

    def register(self, spec=None, key="register-001", expected_revision=0):
        return self.registry.register_authority(
            spec or self.spec,
            idempotency_key=key,
            expected_revision=expected_revision,
        )

    def test_registry_requires_declared_registry_resource_types(self) -> None:
        bad_store = InMemoryStructuredStateAdapter(
            schema_version="1",
            resource_types=("authority",),
            event_types=("registered",),
        )
        with self.assertRaises(AuthoritySchemaError):
            AuthorityRegistry(bad_store)

    def test_registration_persists_exact_metadata_without_activation(self) -> None:
        stored = self.register()
        self.assertEqual(stored.spec, self.spec)
        self.assertEqual(stored.revision, 1)
        self.assertEqual(self.registry.get_authority("auth-primary"), stored)
        with self.assertRaises(AuthorityBindingNotFoundError):
            self.registry.get_binding("tasks")

    def test_activation_is_idempotent_and_routes_one_authority(self) -> None:
        self.register()
        self.registry.register_runtime_adapter("memory-primary", self.data_adapter)
        first = self.registry.activate(
            "tasks",
            "auth-primary",
            idempotency_key="bind-001",
            expected_revision=0,
        )
        replay = self.registry.activate(
            "tasks",
            "auth-primary",
            idempotency_key="bind-001",
            expected_revision=0,
        )
        self.assertEqual(first.revision, 1)
        self.assertEqual(replay, first)
        route = self.registry.resolve("tasks")
        self.assertEqual(route.binding, first)
        self.assertEqual(route.authority.spec, self.spec)
        self.assertIs(route.adapter, self.data_adapter)

    def test_binding_replacement_requires_current_revision(self) -> None:
        self.register()
        second_spec = AuthoritySpec(
            authority_id="auth-secondary",
            adapter_key="memory-secondary",
            resource_ref="synthetic-secondary",
            namespace="mira2-test",
            failure_domain="process-b",
            owner_id="owner-001",
            schema_version="data-1",
            verified=True,
        )
        self.register(second_spec, key="register-002", expected_revision=0)
        self.registry.activate(
            "tasks",
            "auth-primary",
            idempotency_key="bind-001",
            expected_revision=0,
        )
        with self.assertRaises(RevisionConflictError):
            self.registry.activate(
                "tasks",
                "auth-secondary",
                idempotency_key="bind-stale",
                expected_revision=0,
            )
        self.assertEqual(self.registry.get_binding("tasks").authority_id, "auth-primary")

        replaced = self.registry.activate(
            "tasks",
            "auth-secondary",
            idempotency_key="bind-002",
            expected_revision=1,
        )
        self.assertEqual(replaced.authority_id, "auth-secondary")
        self.assertEqual(replaced.revision, 2)

    def test_unverified_or_disabled_authority_cannot_be_activated_or_resolved(self) -> None:
        unverified = AuthoritySpec(
            authority_id="auth-unverified",
            adapter_key=self.spec.adapter_key,
            resource_ref=self.spec.resource_ref,
            namespace=self.spec.namespace,
            failure_domain=self.spec.failure_domain,
            owner_id=self.spec.owner_id,
            schema_version=self.spec.schema_version,
            verified=False,
            enabled=True,
        )
        self.register(unverified, key="register-unverified", expected_revision=0)
        with self.assertRaises(AuthorityUnavailableError):
            self.registry.activate(
                "tasks",
                "auth-unverified",
                idempotency_key="bind-unverified",
                expected_revision=0,
            )

        self.register()
        self.registry.register_runtime_adapter("memory-primary", self.data_adapter)
        self.registry.activate(
            "tasks",
            "auth-primary",
            idempotency_key="bind-001",
            expected_revision=0,
        )
        self.registry.set_enabled(
            "auth-primary",
            False,
            idempotency_key="disable-001",
            expected_revision=1,
        )
        with self.assertRaises(AuthorityUnavailableError):
            self.registry.resolve("tasks")

    def test_runtime_adapter_registration_is_required_but_not_authority(self) -> None:
        self.register()
        self.registry.activate(
            "tasks",
            "auth-primary",
            idempotency_key="bind-001",
            expected_revision=0,
        )
        with self.assertRaises(AuthorityUnavailableError):
            self.registry.resolve("tasks")

        self.registry.register_runtime_adapter("memory-primary", self.data_adapter)
        self.assertEqual(
            self.registry.resolve("tasks").authority.spec.authority_id,
            "auth-primary",
        )
        self.registry.unregister_runtime_adapter("memory-primary")
        with self.assertRaises(AuthorityUnavailableError):
            self.registry.resolve("tasks")

    def test_schema_mismatch_or_unhealthy_adapter_fails_closed(self) -> None:
        self.register()
        self.registry.activate(
            "tasks",
            "auth-primary",
            idempotency_key="bind-001",
            expected_revision=0,
        )
        mismatched = InMemoryStructuredStateAdapter(
            schema_version="wrong",
            resource_types=("entity",),
            event_types=("created",),
        )
        self.registry.register_runtime_adapter("memory-primary", mismatched)
        with self.assertRaises(AuthorityUnavailableError):
            self.registry.resolve("tasks")

        unhealthy = UnhealthyAdapter(
            schema_version="data-1",
            resource_types=("entity",),
            event_types=("created",),
        )
        self.registry.register_runtime_adapter("memory-primary", unhealthy)
        with self.assertRaises(AuthorityUnavailableError):
            self.registry.resolve("tasks")

    def test_failure_isolated_by_data_class(self) -> None:
        self.register()
        second = AuthoritySpec(
            authority_id="auth-second",
            adapter_key="memory-second",
            resource_ref="synthetic-second",
            namespace="mira2-test",
            failure_domain="process-b",
            owner_id="owner-001",
            schema_version="data-1",
            verified=True,
        )
        self.register(second, key="register-002", expected_revision=0)
        self.registry.register_runtime_adapter("memory-primary", self.data_adapter)
        self.registry.activate(
            "tasks",
            "auth-primary",
            idempotency_key="bind-tasks",
            expected_revision=0,
        )
        self.registry.activate(
            "assets",
            "auth-second",
            idempotency_key="bind-assets",
            expected_revision=0,
        )
        self.assertEqual(
            self.registry.resolve("tasks").authority.spec.authority_id,
            "auth-primary",
        )
        with self.assertRaises(AuthorityUnavailableError):
            self.registry.resolve("assets")


if __name__ == "__main__":
    unittest.main()
