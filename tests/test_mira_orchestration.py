from __future__ import annotations

from pathlib import Path
import unittest

from mira.orchestration import (
    MiraServiceNotExecutableError,
    PersonalMiraOrchestrator,
)
from mira.service_composition import DependencyEvidence, personal_service_bundle
from mira.structured_state import InMemoryStructuredStateAdapter
from mira.tasks import TaskService


BRIEFS = personal_service_bundle("briefs")


def ready_brief_dependencies() -> tuple[DependencyEvidence, ...]:
    return tuple(
        DependencyEvidence(dependency_id=dependency_id, ready=True)
        for dependency_id in BRIEFS.dependency_ids
    )


class PersonalMiraOrchestratorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.adapter = InMemoryStructuredStateAdapter(
            schema_version="mira-test-v1",
            resource_types=["service_state", "task", "ops_brief_run"],
            event_types=["created", "updated"],
        )
        self.orchestrator = PersonalMiraOrchestrator(self.adapter)
        self.tasks = TaskService(self.adapter)

    def make_briefs_ready(self) -> None:
        self.orchestrator.request_service(
            "briefs",
            idempotency_key="request-briefs",
        )
        self.orchestrator.refresh_service_readiness(
            "briefs",
            capability_available=True,
            dependency_evidence=ready_brief_dependencies(),
            idempotency_key="ready-briefs",
        )

    def test_disabled_service_cannot_execute_or_write_a_brief(self) -> None:
        with self.assertRaises(MiraServiceNotExecutableError) as caught:
            self.orchestrator.run_ops_brief(
                "2026-09-25",
                "pm",
                timezone_name="America/New_York",
            )

        self.assertEqual(caught.exception.status.activation_state, "missing")
        self.assertEqual(
            self.adapter.query("ops_brief_run", limit=1000),
            (),
        )

    def test_requested_and_ready_still_requires_explicit_activation(self) -> None:
        self.make_briefs_ready()

        status = self.orchestrator.service_status("briefs")
        self.assertTrue(status.ready)
        self.assertFalse(status.effective_active)
        self.assertIn("activation:requested", status.blockers)

        with self.assertRaises(MiraServiceNotExecutableError):
            self.orchestrator.run_ops_brief(
                "2026-09-25",
                "pm",
                timezone_name="America/New_York",
            )

    def test_active_briefs_service_executes_real_canonical_brief_path(self) -> None:
        self.make_briefs_ready()
        activated = self.orchestrator.activate_service(
            "briefs",
            idempotency_key="activate-briefs",
        )
        self.assertTrue(activated.effective_active)

        self.tasks.create(
            "task-change-filter",
            title="Change shop air filter",
            next_action="Install the spare filter",
            priority="high",
            context="home",
            idempotency_key="create-filter-task",
        )

        brief = self.orchestrator.run_ops_brief(
            "2026-09-25",
            "pm",
            timezone_name="America/New_York",
            context="home",
        )

        self.assertEqual(brief.status, "composed")
        self.assertFalse(brief.delivered)
        self.assertIn("MIRA Ops Brief", brief.rendered_text)
        self.assertIn("Change shop air filter", brief.rendered_text)
        self.assertIn("Install the spare filter", brief.rendered_text)
        persisted = self.adapter.get("ops_brief_run", brief.run_id)
        self.assertEqual(persisted.resource_id, brief.run_id)

    def test_same_slot_replays_same_canonical_run(self) -> None:
        self.make_briefs_ready()
        self.orchestrator.activate_service(
            "briefs",
            idempotency_key="activate-briefs",
        )

        first = self.orchestrator.run_ops_brief(
            "2026-09-25",
            "pm",
            timezone_name="America/New_York",
        )
        second = self.orchestrator.run_ops_brief(
            "2026-09-25",
            "pm",
            timezone_name="America/New_York",
        )

        self.assertEqual(second.run_id, first.run_id)
        self.assertEqual(second.rendered_text, first.rendered_text)
        self.assertTrue(second.idempotent_replay)
        self.assertEqual(len(self.adapter.query("ops_brief_run", limit=1000)), 1)

    def test_readiness_loss_suspends_and_blocks_execution(self) -> None:
        self.make_briefs_ready()
        self.orchestrator.activate_service(
            "briefs",
            idempotency_key="activate-briefs",
        )

        evidence = tuple(
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
        )
        degraded = self.orchestrator.refresh_service_readiness(
            "briefs",
            capability_available=True,
            dependency_evidence=evidence,
            idempotency_key="degrade-briefs",
        )

        self.assertEqual(degraded.activation_state, "suspended")
        self.assertFalse(degraded.effective_active)
        self.assertIn(
            "dependency:OPS-004:delivery_runtime_unverified",
            degraded.blockers,
        )
        with self.assertRaises(MiraServiceNotExecutableError):
            self.orchestrator.run_ops_brief(
                "2026-09-25",
                "pm",
                timezone_name="America/New_York",
            )

    def test_missing_dependency_evidence_fails_closed(self) -> None:
        self.orchestrator.request_service(
            "briefs",
            idempotency_key="request-briefs",
        )
        partial = tuple(
            DependencyEvidence(dependency_id=dependency_id, ready=True)
            for dependency_id in BRIEFS.dependency_ids
            if dependency_id != "RECOVERY-002"
        )
        status = self.orchestrator.refresh_service_readiness(
            "briefs",
            capability_available=True,
            dependency_evidence=partial,
            idempotency_key="partial-briefs",
        )

        self.assertFalse(status.ready)
        self.assertIn("dependency:RECOVERY-002:unknown", status.blockers)

    def test_shipped_no_app_instructions_require_same_execution_gate(self) -> None:
        instructions = Path(
            "workspace/apps_script/MIRA_NO_APP_INSTRUCTIONS.md"
        ).read_text(encoding="utf-8")
        required = (
            "## Orchestration execution gate",
            "service_state/briefs",
            "activation_state=active",
            "capability_state=available",
            "OPS-001",
            "OPS-003",
            "OPS-004",
            "RECOVERY-001",
            "RECOVERY-002",
            "composition is not delivery",
        )
        for phrase in required:
            self.assertIn(phrase, instructions)


if __name__ == "__main__":
    unittest.main()
