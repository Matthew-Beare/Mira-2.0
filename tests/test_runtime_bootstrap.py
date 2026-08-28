"""Tests for fail-closed persisted Authority runtime bootstrap."""

from dataclasses import replace
import unittest

from mira.authority import AuthorityRegistry, AuthoritySpec
from mira.runtime_bootstrap import (
    RuntimeBootstrapMismatchError,
    bootstrap_runtime_authority,
)
from mira.structured_state import InMemoryStructuredStateAdapter


class RuntimeBootstrapTests(unittest.TestCase):
    def setUp(self) -> None:
        self.store = InMemoryStructuredStateAdapter(
            schema_version="mira-structured-state-v1",
            resource_types=("authority", "authority_binding", "entity"),
            event_types=("created", "updated"),
        )
        self.registry = AuthorityRegistry(self.store)
        self.spec = AuthoritySpec(
            authority_id="google-sheets-m0",
            adapter_key="google-sheets",
            resource_ref="runtime:google-structured-state",
            namespace="mira-2-sandbox",
            failure_domain="google-sheets-sandbox",
            owner_id="m0-synthetic-user",
            schema_version="mira-structured-state-v1",
            verified=True,
            enabled=True,
        )

    def bootstrap(self):
        return bootstrap_runtime_authority(
            self.registry,
            spec=self.spec,
            data_class="entity",
            adapter=self.store,
        )

    def test_first_boot_creates_authority_binding_and_resolves_adapter(self) -> None:
        result = self.bootstrap()
        self.assertTrue(result.authority_created)
        self.assertTrue(result.binding_created)
        self.assertEqual(result.route.authority.spec, self.spec)
        self.assertEqual(result.route.binding.authority_id, self.spec.authority_id)
        self.assertIs(result.route.adapter, self.store)
        self.assertEqual(result.route.authority.revision, 1)
        self.assertEqual(result.route.binding.revision, 1)

    def test_restart_is_read_only_after_route_exists(self) -> None:
        first = self.bootstrap()
        authority_before = self.store.get("authority", self.spec.authority_id)
        binding_before = self.store.get("authority_binding", "binding-entity")

        restarted_registry = AuthorityRegistry(self.store)
        second = bootstrap_runtime_authority(
            restarted_registry,
            spec=self.spec,
            data_class="entity",
            adapter=self.store,
        )

        self.assertTrue(first.authority_created)
        self.assertTrue(first.binding_created)
        self.assertFalse(second.authority_created)
        self.assertFalse(second.binding_created)
        self.assertEqual(
            self.store.get("authority", self.spec.authority_id), authority_before
        )
        self.assertEqual(
            self.store.get("authority_binding", "binding-entity"), binding_before
        )
        self.assertIs(second.route.adapter, self.store)

    def test_existing_materially_different_authority_fails_without_rewrite(self) -> None:
        different = replace(self.spec, resource_ref="runtime:unexpected-store")
        stored = self.registry.register_authority(
            different,
            idempotency_key="preexisting-authority",
            expected_revision=0,
        )

        with self.assertRaises(RuntimeBootstrapMismatchError):
            self.bootstrap()

        self.assertEqual(self.registry.get_authority(self.spec.authority_id), stored)
        self.assertEqual(self.store.query("authority_binding"), ())

    def test_existing_different_binding_fails_before_any_new_persistent_write(self) -> None:
        other = replace(
            self.spec,
            authority_id="other-authority",
            adapter_key="other-adapter",
            resource_ref="runtime:other-store",
        )
        self.registry.register_authority(
            other,
            idempotency_key="preexisting-other-authority",
            expected_revision=0,
        )
        binding = self.registry.activate(
            "entity",
            other.authority_id,
            idempotency_key="preexisting-binding",
            expected_revision=0,
        )

        with self.assertRaises(RuntimeBootstrapMismatchError):
            self.bootstrap()

        self.assertEqual(self.registry.get_binding("entity"), binding)
        self.assertEqual(
            self.store.query("authority", filters={"authority_id": self.spec.authority_id}),
            (),
        )

    def test_existing_matching_authority_only_creates_missing_binding(self) -> None:
        authority = self.registry.register_authority(
            self.spec,
            idempotency_key="preexisting-authority",
            expected_revision=0,
        )
        result = self.bootstrap()
        self.assertFalse(result.authority_created)
        self.assertTrue(result.binding_created)
        self.assertEqual(result.route.authority, authority)
        self.assertEqual(result.route.binding.revision, 1)


if __name__ == "__main__":
    unittest.main()
