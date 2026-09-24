from __future__ import annotations

import unittest

from mira.service_composition import (
    DependencyEvidence,
    ServiceBundleSpec,
    ServiceComposer,
    ServiceCompositionValidationError,
)
from mira.service_state import ServiceStateService
from mira.structured_state import InMemoryStructuredStateAdapter


BRIEFS = ServiceBundleSpec(
    service_id="briefs",
    dependency_ids=(
        "OPS-001",
        "OPS-003",
        "OPS-004",
        "RECOVERY-001",
        "RECOVERY-002",
    ),
)


def ready_dependencies(*dependency_ids: str) -> tuple[DependencyEvidence, ...]:
    return tuple(
        DependencyEvidence(dependency_id=dependency_id, ready=True)
        for dependency_id in dependency_ids
    )


class ServiceComposerTests(unittest.TestCase):
    def setUp(self) -> None:
        adapter = InMemoryStructuredStateAdapter(
            schema_version="mira-test-v1",
            resource_types=["service_state"],
            event_types=["created"],
        )
        self.state = ServiceStateService(adapter)
        self.composer = ServiceComposer(self.state)

    def test_verified_bundle_becomes_ready_but_never_silently_activates(self) -> None:
        requested = self.state.request_enable(
            "briefs", idempotency_key="request-briefs"
        )
        self.assertEqual(requested.activation_state, "requested")

        composed = self.composer.compose(
            BRIEFS,
            capability_available=True,
            dependency_evidence=ready_dependencies(*BRIEFS.dependency_ids),
            idempotency_key="compose-ready-briefs",
        )

        self.assertTrue(composed.ready)
        self.assertFalse(composed.effective_active)
        self.assertEqual(composed.activation_state, "requested")
        self.assertEqual(composed.blockers, ())

        activated = self.state.activate(
            "briefs", idempotency_key="explicit-activate-briefs"
        )
        self.assertTrue(activated.effective_active)

    def test_missing_dependency_fails_closed_as_unknown(self) -> None:
        evidence = ready_dependencies(
            "OPS-001",
            "OPS-003",
            "RECOVERY-001",
            "RECOVERY-002",
        )
        composed = self.composer.compose(
            BRIEFS,
            capability_available=True,
            dependency_evidence=evidence,
            idempotency_key="compose-missing-dependency",
        )

        self.assertFalse(composed.ready)
        self.assertIn("dependency:OPS-004:unknown", composed.blockers)

    def test_explicit_dependency_failure_is_preserved(self) -> None:
        evidence = [
            DependencyEvidence(
                dependency_id=dependency_id,
                ready=dependency_id != "OPS-004",
                reason_code=(
                    "delivery_runtime_unverified"
                    if dependency_id == "OPS-004"
                    else None
                ),
            )
            for dependency_id in BRIEFS.dependency_ids
        ]

        composed = self.composer.compose(
            BRIEFS,
            capability_available=True,
            dependency_evidence=evidence,
            idempotency_key="compose-blocked-delivery",
        )

        self.assertFalse(composed.ready)
        self.assertEqual(
            composed.blockers,
            ("dependency:OPS-004:delivery_runtime_unverified",),
        )

    def test_capability_failure_is_independent_from_dependency_truth(self) -> None:
        composed = self.composer.compose(
            BRIEFS,
            capability_available=False,
            dependency_evidence=ready_dependencies(*BRIEFS.dependency_ids),
            idempotency_key="compose-capability-unavailable",
        )

        self.assertFalse(composed.ready)
        self.assertEqual(composed.blockers, ("capability:unavailable",))

    def test_readiness_loss_suspends_previously_active_service(self) -> None:
        self.state.request_enable("briefs", idempotency_key="request")
        self.composer.compose(
            BRIEFS,
            capability_available=True,
            dependency_evidence=ready_dependencies(*BRIEFS.dependency_ids),
            idempotency_key="ready",
        )
        self.state.activate("briefs", idempotency_key="activate")

        degraded = self.composer.compose(
            BRIEFS,
            capability_available=True,
            dependency_evidence=(
                *ready_dependencies("OPS-001", "OPS-003", "OPS-004", "RECOVERY-001"),
                DependencyEvidence(
                    dependency_id="RECOVERY-002",
                    ready=False,
                    reason_code="dependency_failure_isolation_unverified",
                ),
            ),
            idempotency_key="degrade",
        )

        self.assertEqual(degraded.activation_state, "suspended")
        self.assertFalse(degraded.effective_active)
        self.assertIn(
            "dependency:RECOVERY-002:dependency_failure_isolation_unverified",
            degraded.blockers,
        )

    def test_repeat_same_composition_is_read_only_replay(self) -> None:
        first = self.composer.compose(
            BRIEFS,
            capability_available=True,
            dependency_evidence=ready_dependencies(*BRIEFS.dependency_ids),
            idempotency_key="first",
        )
        repeated = self.composer.compose(
            BRIEFS,
            capability_available=True,
            dependency_evidence=ready_dependencies(*BRIEFS.dependency_ids),
            idempotency_key="second",
        )

        self.assertEqual(repeated.revision, first.revision)
        self.assertTrue(repeated.idempotent_replay)

    def test_undeclared_or_duplicate_dependency_evidence_is_rejected(self) -> None:
        with self.assertRaises(ServiceCompositionValidationError):
            self.composer.compose(
                BRIEFS,
                capability_available=True,
                dependency_evidence=(
                    DependencyEvidence("OPS-001", True),
                    DependencyEvidence("OPS-001", True),
                ),
                idempotency_key="duplicate",
            )

        with self.assertRaises(ServiceCompositionValidationError):
            self.composer.compose(
                BRIEFS,
                capability_available=True,
                dependency_evidence=(
                    DependencyEvidence("NOT-DECLARED", True),
                ),
                idempotency_key="extra",
            )

    def test_bundle_contract_must_be_sorted_and_unique(self) -> None:
        with self.assertRaises(ServiceCompositionValidationError):
            ServiceBundleSpec(
                service_id="briefs",
                dependency_ids=("OPS-004", "OPS-003"),
            )


if __name__ == "__main__":
    unittest.main()
