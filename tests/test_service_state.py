from __future__ import annotations

import unittest

from mira.service_state import (
    AuthorizationState,
    CapabilityEvidenceState,
    CapabilityGate,
    ConnectionState,
    GateObservation,
    ProviderCapabilitySnapshot,
    ServiceIntentRequiredError,
    ServiceNotReadyError,
    ServiceStateService,
    ServiceStateValidationError,
    evaluate_provider_capability,
)
from mira.structured_state import InMemoryStructuredStateAdapter


NOW = "2026-08-31T22:00:00Z"
RECENT = "2026-08-31T21:55:00Z"
STALE = "2026-08-31T20:00:00Z"


class ProviderCapabilityGateTests(unittest.TestCase):
    def snapshot(
        self,
        *,
        authorization: AuthorizationState = AuthorizationState.AUTHORIZED,
        authorization_observed_at: str = RECENT,
        gates: tuple[GateObservation, ...] = (),
    ) -> ProviderCapabilitySnapshot:
        return ProviderCapabilitySnapshot(
            provider_id="google",
            service_id="appointments_calendar",
            authorization_state=authorization,
            authorization_observed_at=authorization_observed_at,
            gates=gates,
            resource_ref="calendar:synthetic-test",
            scopes=("calendar.events",),
        )

    def gate(
        self,
        gate: CapabilityGate,
        state: CapabilityEvidenceState,
        *,
        observed_at: str = RECENT,
        reason_code: str | None = None,
    ) -> GateObservation:
        return GateObservation(
            gate=gate,
            state=state,
            observed_at=observed_at,
            reason_code=reason_code,
        )

    def evaluate(
        self,
        snapshot: ProviderCapabilitySnapshot,
        *gates: CapabilityGate,
    ):
        return evaluate_provider_capability(
            snapshot,
            required_gates=gates,
            now=NOW,
            max_age_seconds=3600,
        )

    def test_authorization_required_routes_to_connect_without_claiming_capability(self) -> None:
        result = self.evaluate(
            self.snapshot(authorization=AuthorizationState.REQUIRED),
            CapabilityGate.READ,
        )
        self.assertEqual(result.connection_state, ConnectionState.CONNECT)
        self.assertFalse(result.ready)
        self.assertEqual(result.decisions[0].reason_code, "authorization_required")

    def test_authorized_but_declared_only_is_not_connected(self) -> None:
        result = self.evaluate(
            self.snapshot(
                gates=(
                    self.gate(
                        CapabilityGate.READ,
                        CapabilityEvidenceState.DECLARED,
                    ),
                )
            ),
            CapabilityGate.READ,
        )
        self.assertEqual(result.connection_state, ConnectionState.NEEDS_ATTENTION)
        self.assertFalse(result.ready)
        self.assertEqual(result.decisions[0].reason_code, "not_verified")

    def test_read_write_and_readback_are_independent_gates(self) -> None:
        result = self.evaluate(
            self.snapshot(
                gates=(
                    self.gate(CapabilityGate.READ, CapabilityEvidenceState.VERIFIED),
                    self.gate(CapabilityGate.WRITE, CapabilityEvidenceState.DECLARED),
                    self.gate(
                        CapabilityGate.REMOTE_READBACK,
                        CapabilityEvidenceState.VERIFIED,
                    ),
                )
            ),
            CapabilityGate.READ,
            CapabilityGate.WRITE,
            CapabilityGate.REMOTE_READBACK,
        )
        decisions = {decision.gate: decision for decision in result.decisions}
        self.assertTrue(decisions[CapabilityGate.READ].allowed)
        self.assertFalse(decisions[CapabilityGate.WRITE].allowed)
        self.assertTrue(decisions[CapabilityGate.REMOTE_READBACK].allowed)
        self.assertFalse(result.ready)

    def test_verified_required_gates_produce_connected(self) -> None:
        result = self.evaluate(
            self.snapshot(
                gates=(
                    self.gate(CapabilityGate.READ, CapabilityEvidenceState.VERIFIED),
                    self.gate(
                        CapabilityGate.REMOTE_READBACK,
                        CapabilityEvidenceState.VERIFIED,
                    ),
                )
            ),
            CapabilityGate.READ,
            CapabilityGate.REMOTE_READBACK,
        )
        self.assertEqual(result.connection_state, ConnectionState.CONNECTED)
        self.assertTrue(result.ready)
        self.assertEqual(result.blockers, ())

    def test_write_verified_but_readback_failed_is_not_ready(self) -> None:
        result = self.evaluate(
            self.snapshot(
                gates=(
                    self.gate(CapabilityGate.WRITE, CapabilityEvidenceState.VERIFIED),
                    self.gate(
                        CapabilityGate.REMOTE_READBACK,
                        CapabilityEvidenceState.FAILED,
                        reason_code="provider_readback_mismatch",
                    ),
                )
            ),
            CapabilityGate.WRITE,
            CapabilityGate.REMOTE_READBACK,
        )
        self.assertEqual(result.connection_state, ConnectionState.NEEDS_ATTENTION)
        self.assertFalse(result.ready)
        self.assertIn(
            "provider:remote_readback:provider_readback_mismatch",
            result.blockers,
        )

    def test_revoked_and_expired_authorization_route_to_reconnect(self) -> None:
        for authorization in (AuthorizationState.REVOKED, AuthorizationState.EXPIRED):
            with self.subTest(authorization=authorization):
                result = self.evaluate(
                    self.snapshot(authorization=authorization),
                    CapabilityGate.READ,
                )
                self.assertEqual(result.connection_state, ConnectionState.RECONNECT)
                self.assertFalse(result.ready)

    def test_permission_denied_needs_attention_and_unsupported_is_unavailable(self) -> None:
        denied = self.evaluate(
            self.snapshot(
                gates=(
                    self.gate(
                        CapabilityGate.READ,
                        CapabilityEvidenceState.PERMISSION_DENIED,
                    ),
                )
            ),
            CapabilityGate.READ,
        )
        self.assertEqual(denied.connection_state, ConnectionState.NEEDS_ATTENTION)
        self.assertEqual(denied.decisions[0].reason_code, "permission_denied")

        unsupported = self.evaluate(
            self.snapshot(
                gates=(
                    self.gate(
                        CapabilityGate.WRITE,
                        CapabilityEvidenceState.UNSUPPORTED,
                    ),
                )
            ),
            CapabilityGate.WRITE,
        )
        self.assertEqual(unsupported.connection_state, ConnectionState.UNAVAILABLE)
        self.assertEqual(unsupported.decisions[0].reason_code, "unsupported")

    def test_stale_authorization_and_gate_evidence_fail_closed(self) -> None:
        stale_auth = self.evaluate(
            self.snapshot(authorization_observed_at=STALE),
            CapabilityGate.READ,
        )
        self.assertEqual(stale_auth.connection_state, ConnectionState.NEEDS_ATTENTION)
        self.assertEqual(stale_auth.decisions[0].reason_code, "authorization_stale")

        stale_gate = self.evaluate(
            self.snapshot(
                gates=(
                    self.gate(
                        CapabilityGate.READ,
                        CapabilityEvidenceState.VERIFIED,
                        observed_at=STALE,
                    ),
                )
            ),
            CapabilityGate.READ,
        )
        self.assertEqual(stale_gate.connection_state, ConnectionState.NEEDS_ATTENTION)
        self.assertEqual(stale_gate.decisions[0].reason_code, "evidence_stale")

    def test_duplicate_gate_evidence_and_future_evidence_are_rejected(self) -> None:
        with self.assertRaises(ServiceStateValidationError):
            self.snapshot(
                gates=(
                    self.gate(CapabilityGate.READ, CapabilityEvidenceState.VERIFIED),
                    self.gate(CapabilityGate.READ, CapabilityEvidenceState.VERIFIED),
                )
            )

        future = self.snapshot(
            gates=(
                self.gate(
                    CapabilityGate.READ,
                    CapabilityEvidenceState.VERIFIED,
                    observed_at="2026-08-31T22:05:00Z",
                ),
            )
        )
        with self.assertRaises(ServiceStateValidationError):
            self.evaluate(future, CapabilityGate.READ)

    def test_snapshot_contains_no_credential_or_token_payload_field(self) -> None:
        snapshot = self.snapshot()
        self.assertFalse(hasattr(snapshot, "token"))
        self.assertFalse(hasattr(snapshot, "credentials"))
        self.assertFalse(hasattr(snapshot, "secret"))


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

    def test_capability_evaluation_updates_readiness_but_not_user_intent(self) -> None:
        snapshot = ProviderCapabilitySnapshot(
            provider_id="google",
            service_id="appointments_calendar",
            authorization_state=AuthorizationState.AUTHORIZED,
            authorization_observed_at=RECENT,
            gates=(
                GateObservation(
                    gate=CapabilityGate.READ,
                    state=CapabilityEvidenceState.VERIFIED,
                    observed_at=RECENT,
                ),
                GateObservation(
                    gate=CapabilityGate.REMOTE_READBACK,
                    state=CapabilityEvidenceState.VERIFIED,
                    observed_at=RECENT,
                ),
            ),
        )
        evaluation = evaluate_provider_capability(
            snapshot,
            required_gates=(CapabilityGate.READ, CapabilityGate.REMOTE_READBACK),
            now=NOW,
            max_age_seconds=3600,
        )
        view = self.service.apply_capability_evaluation(
            "appointments_calendar",
            evaluation=evaluation,
            idempotency_key="capability-ready",
        )
        self.assertEqual(view.capability_state, "available")
        self.assertEqual(view.activation_state, "disabled")
        self.assertTrue(view.ready)
        self.assertFalse(view.effective_active)

    def test_capability_evaluation_service_identity_mismatch_fails_closed(self) -> None:
        snapshot = ProviderCapabilitySnapshot(
            provider_id="google",
            service_id="appointments_calendar",
            authorization_state=AuthorizationState.REQUIRED,
            authorization_observed_at=RECENT,
            gates=(),
        )
        evaluation = evaluate_provider_capability(
            snapshot,
            required_gates=(CapabilityGate.READ,),
            now=NOW,
            max_age_seconds=3600,
        )
        with self.assertRaises(ServiceStateValidationError):
            self.service.apply_capability_evaluation(
                "email_triage",
                evaluation=evaluation,
                idempotency_key="wrong-service",
            )


if __name__ == "__main__":
    unittest.main()
