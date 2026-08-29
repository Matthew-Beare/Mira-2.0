from __future__ import annotations

import unittest

from mira.service_state import (
    ServiceIntentRequiredError,
    ServiceNotReadyError,
    ServiceStateService,
)
from mira.structured_state import InMemoryStructuredStateAdapter


class ServiceStateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.adapter = InMemoryStructuredStateAdapter(
            schema_version="mira-test-v1",
            resource_types=["service_state"],
            event_types=["created"],
        )
        self.service = ServiceStateService(self.adapter)

    def test_fresh_state_is_disabled_unknown_and_not_active(self) -> None:
        view = self.service.ensure("briefs")
        self.assertEqual(view.revision, 1)
        self.assertEqual(view.activation_state, "disabled")
        self.assertEqual(view.capability_state, "unknown")
        self.assertEqual(view.recommendation_state, "none")
        self.assertFalse(view.requested_by_user)
        self.assertFalse(view.ready)
        self.assertFalse(view.effective_active)

    def test_request_does_not_activate(self) -> None:
        view = self.service.request_enable("briefs", idempotency_key="request-briefs")
        self.assertEqual(view.activation_state, "requested")
        self.assertTrue(view.requested_by_user)
        self.assertFalse(view.effective_active)

    def test_recommendation_does_not_request_or_activate(self) -> None:
        view = self.service.recommend("briefs", idempotency_key="recommend-briefs")
        self.assertEqual(view.recommendation_state, "suggested")
        self.assertEqual(view.activation_state, "disabled")
        self.assertFalse(view.requested_by_user)
        self.assertFalse(view.effective_active)

    def test_activation_requires_user_intent(self) -> None:
        self.service.ensure("briefs")
        self.service.set_readiness(
            "briefs",
            capability_state="available",
            idempotency_key="ready-briefs",
        )
        with self.assertRaises(ServiceIntentRequiredError):
            self.service.activate("briefs", idempotency_key="activate-without-request")

    def test_activation_fails_closed_when_not_ready(self) -> None:
        self.service.request_enable("appointments_calendar", idempotency_key="request-appts")
        with self.assertRaises(ServiceNotReadyError):
            self.service.activate(
                "appointments_calendar", idempotency_key="activate-appts-too-early"
            )

        blocked = self.service.set_readiness(
            "appointments_calendar",
            capability_state="available",
            dependency_blockers=["calendar_provider_readback"],
            idempotency_key="blocked-appts",
        )
        self.assertFalse(blocked.ready)
        with self.assertRaises(ServiceNotReadyError):
            self.service.activate(
                "appointments_calendar", idempotency_key="activate-appts-blocked"
            )

    def test_successful_activation_requires_ready_requested_state(self) -> None:
        self.service.request_enable("briefs", idempotency_key="request")
        ready = self.service.set_readiness(
            "briefs",
            capability_state="available",
            idempotency_key="ready",
        )
        self.assertTrue(ready.ready)
        self.assertFalse(ready.effective_active)

        active = self.service.activate("briefs", idempotency_key="activate")
        self.assertEqual(active.activation_state, "active")
        self.assertTrue(active.ready)
        self.assertTrue(active.effective_active)

    def test_readiness_loss_suspends_active_and_never_auto_reactivates(self) -> None:
        self.service.request_enable("briefs", idempotency_key="request")
        self.service.set_readiness(
            "briefs", capability_state="available", idempotency_key="ready"
        )
        self.service.activate("briefs", idempotency_key="activate")

        suspended = self.service.set_readiness(
            "briefs",
            capability_state="unavailable",
            dependency_blockers=["provider_unavailable"],
            idempotency_key="lost-readiness",
        )
        self.assertEqual(suspended.activation_state, "suspended")
        self.assertEqual(suspended.suspension_reason, "readiness_lost")
        self.assertFalse(suspended.effective_active)

        recovered = self.service.set_readiness(
            "briefs", capability_state="available", idempotency_key="ready-again"
        )
        self.assertTrue(recovered.ready)
        self.assertEqual(recovered.activation_state, "suspended")
        self.assertFalse(recovered.effective_active)

        resumed = self.service.activate("briefs", idempotency_key="explicit-resume")
        self.assertTrue(resumed.effective_active)

    def test_disable_preserves_resource_identity(self) -> None:
        self.service.request_enable("briefs", idempotency_key="request")
        before = self.service.get("briefs")
        disabled = self.service.disable("briefs", idempotency_key="disable")
        self.assertEqual(disabled.service_id, before.service_id)
        self.assertGreater(disabled.revision, before.revision)
        self.assertEqual(disabled.activation_state, "disabled")
        self.assertFalse(disabled.requested_by_user)

    def test_repeating_same_transition_is_read_only_replay(self) -> None:
        first = self.service.request_enable("briefs", idempotency_key="request-1")
        repeat = self.service.request_enable("briefs", idempotency_key="request-2")
        self.assertEqual(repeat.revision, first.revision)
        self.assertTrue(repeat.idempotent_replay)

    def test_onboarding_appointment_intent_requests_but_does_not_activate(self) -> None:
        view = self.service.apply_appointment_onboarding_intent(
            wants_help=True,
            idempotency_key="onboarding-appts",
        )
        self.assertEqual(view.service_id, "appointments_calendar")
        self.assertEqual(view.activation_state, "requested")
        self.assertEqual(view.capability_state, "unknown")
        self.assertFalse(view.ready)
        self.assertFalse(view.effective_active)

    def test_onboarding_decline_leaves_service_disabled(self) -> None:
        view = self.service.apply_appointment_onboarding_intent(
            wants_help=False,
            idempotency_key="onboarding-no-appts",
        )
        self.assertEqual(view.activation_state, "disabled")
        self.assertFalse(view.requested_by_user)
        self.assertFalse(view.effective_active)


if __name__ == "__main__":
    unittest.main()
