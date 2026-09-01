from __future__ import annotations

import unittest

from mira.provider_onboarding import (
    ConnectionCommand,
    ConnectionEffectScope,
    ConnectionIntent,
    ConnectionNextAction,
    ConnectionSurface,
    ConnectionSurfaceKind,
    NativeFlowChannel,
    ProviderOnboardingValidationError,
    plan_provider_connection,
)
from mira.runtime_router import ApprovalState, RuntimeLaneCandidate, RuntimePolicy
from mira.service_state import (
    AuthorizationState,
    CapabilityEvidenceState,
    CapabilityGate,
    ConnectionState,
    GateObservation,
    ProviderCapabilitySnapshot,
)


NOW = "2026-09-01T05:30:00Z"
RECENT = "2026-09-01T05:25:00Z"
STALE = "2026-09-01T03:00:00Z"


class ProviderOnboardingTests(unittest.TestCase):
    def observation(
        self,
        gate: CapabilityGate,
        state: CapabilityEvidenceState = CapabilityEvidenceState.VERIFIED,
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

    def snapshot(
        self,
        provider: str = "google",
        service: str = "calendar",
        *,
        authorization: AuthorizationState = AuthorizationState.AUTHORIZED,
        authorization_observed_at: str = RECENT,
        gates: tuple[GateObservation, ...] | None = None,
    ) -> ProviderCapabilitySnapshot:
        if gates is None:
            gates = (
                self.observation(CapabilityGate.READ),
                self.observation(CapabilityGate.WRITE),
                self.observation(CapabilityGate.REMOTE_READBACK),
            )
        return ProviderCapabilitySnapshot(
            provider_id=provider,
            service_id=service,
            authorization_state=authorization,
            authorization_observed_at=authorization_observed_at,
            gates=gates,
            resource_ref=f"synthetic:{provider}:{service}",
            scopes=(f"{service}.synthetic",),
        )

    def policy(
        self,
        *,
        approval: ApprovalState = ApprovalState.APPROVED,
        data_classes: tuple[str, ...] = ("personal",),
        policy_id: str = "personal-default",
    ) -> RuntimePolicy:
        return RuntimePolicy(
            policy_id=policy_id,
            approval_state=approval,
            allowed_data_classifications=data_classes,
        )

    def candidate(
        self,
        lane: str = "google-native-calendar",
        *,
        provider: str = "google",
        service: str = "calendar",
        snapshot: ProviderCapabilitySnapshot | None = None,
        policy: RuntimePolicy | None = None,
        priority: int = 100,
    ) -> RuntimeLaneCandidate:
        return RuntimeLaneCandidate(
            lane_id=lane,
            runtime_id=f"runtime-{lane}",
            capability=snapshot or self.snapshot(provider, service),
            policy=policy or self.policy(),
            priority=priority,
        )

    def intent(
        self,
        *,
        provider: str = "google",
        service: str = "calendar",
        gates: tuple[CapabilityGate, ...] = (
            CapabilityGate.READ,
            CapabilityGate.WRITE,
            CapabilityGate.REMOTE_READBACK,
        ),
        data_classification: str = "personal",
    ) -> ConnectionIntent:
        return ConnectionIntent(
            provider_id=provider,
            service_id=service,
            required_gates=gates,
            data_classification=data_classification,
        )

    def product_surface(self) -> ConnectionSurface:
        return ConnectionSurface(
            kind=ConnectionSurfaceKind.PRODUCT_OWNED,
            authorization_flow=NativeFlowChannel.PROVIDER_NATIVE,
            disconnect_flow=NativeFlowChannel.PROVIDER_NATIVE,
        )

    def host_surface(self) -> ConnectionSurface:
        return ConnectionSurface(
            kind=ConnectionSurfaceKind.HOST_CONTROLLED,
            authorization_flow=NativeFlowChannel.HOST_NATIVE,
            disconnect_flow=NativeFlowChannel.HOST_NATIVE,
        )

    def plan(
        self,
        snapshot: ProviderCapabilitySnapshot,
        *,
        surface: ConnectionSurface | None = None,
        command: ConnectionCommand = ConnectionCommand.INSPECT,
        policy: RuntimePolicy | None = None,
        intent: ConnectionIntent | None = None,
        lane: str = "google-native-calendar",
        extra_candidates: tuple[RuntimeLaneCandidate, ...] = (),
    ):
        primary = self.candidate(
            lane,
            provider=snapshot.provider_id,
            service=snapshot.service_id,
            snapshot=snapshot,
            policy=policy,
        )
        return plan_provider_connection(
            intent or self.intent(
                provider=snapshot.provider_id,
                service=snapshot.service_id,
            ),
            surface or self.product_surface(),
            (primary,) + extra_candidates,
            command=command,
            now=NOW,
            max_age_seconds=3600,
        )

    def test_fresh_product_owned_connection_exposes_connect_and_native_auth(self) -> None:
        snapshot = self.snapshot(
            authorization=AuthorizationState.REQUIRED,
            gates=(),
        )
        inspect = self.plan(snapshot)
        self.assertEqual(inspect.connection_state, ConnectionState.CONNECT)
        self.assertEqual(inspect.available_commands, (ConnectionCommand.CONNECT,))
        self.assertEqual(inspect.next_action, ConnectionNextAction.NONE)

        connect = self.plan(snapshot, command=ConnectionCommand.CONNECT)
        self.assertEqual(
            connect.next_action,
            ConnectionNextAction.START_NATIVE_AUTHORIZATION,
        )
        self.assertEqual(connect.flow_channel, NativeFlowChannel.PROVIDER_NATIVE)
        self.assertEqual(connect.effect_scope, ConnectionEffectScope.NONE)
        self.assertNotIn(ConnectionCommand.DISCONNECT, connect.available_commands)

    def test_host_controlled_connection_uses_host_native_flow_not_custom_ui_promise(self) -> None:
        snapshot = self.snapshot(
            authorization=AuthorizationState.REQUIRED,
            gates=(),
        )
        connect = self.plan(
            snapshot,
            surface=self.host_surface(),
            command=ConnectionCommand.CONNECT,
        )
        self.assertEqual(connect.surface_kind, ConnectionSurfaceKind.HOST_CONTROLLED)
        self.assertEqual(connect.flow_channel, NativeFlowChannel.HOST_NATIVE)
        self.assertEqual(
            connect.next_action,
            ConnectionNextAction.START_NATIVE_AUTHORIZATION,
        )

    def test_authorized_but_unverified_runs_automatic_verification_before_connected(self) -> None:
        snapshot = self.snapshot(
            gates=(
                self.observation(
                    CapabilityGate.READ,
                    CapabilityEvidenceState.DECLARED,
                ),
                self.observation(
                    CapabilityGate.WRITE,
                    CapabilityEvidenceState.DECLARED,
                ),
                self.observation(
                    CapabilityGate.REMOTE_READBACK,
                    CapabilityEvidenceState.UNKNOWN,
                ),
            ),
        )
        plan = self.plan(snapshot)
        self.assertEqual(plan.connection_state, ConnectionState.NEEDS_ATTENTION)
        self.assertEqual(
            plan.next_action,
            ConnectionNextAction.VERIFY_CAPABILITIES,
        )
        self.assertIn("verification_required", plan.reason_codes)
        self.assertFalse(plan.connected)

    def test_fully_verified_and_routable_is_connected(self) -> None:
        plan = self.plan(self.snapshot())
        self.assertTrue(plan.connected)
        self.assertEqual(plan.connection_state, ConnectionState.CONNECTED)
        self.assertEqual(plan.next_action, ConnectionNextAction.NONE)
        self.assertEqual(plan.selected_lane_id, "google-native-calendar")
        self.assertEqual(
            plan.available_commands,
            (ConnectionCommand.DISCONNECT,),
        )

    def test_expired_or_revoked_authorization_exposes_reconnect(self) -> None:
        for authorization in (AuthorizationState.EXPIRED, AuthorizationState.REVOKED):
            with self.subTest(authorization=authorization):
                snapshot = self.snapshot(
                    authorization=authorization,
                    gates=(),
                )
                inspect = self.plan(snapshot)
                self.assertEqual(inspect.connection_state, ConnectionState.RECONNECT)
                self.assertIn(ConnectionCommand.RECONNECT, inspect.available_commands)

                reconnect = self.plan(
                    snapshot,
                    command=ConnectionCommand.RECONNECT,
                )
                self.assertEqual(
                    reconnect.next_action,
                    ConnectionNextAction.START_NATIVE_REAUTHORIZATION,
                )
                self.assertEqual(
                    reconnect.flow_channel,
                    NativeFlowChannel.PROVIDER_NATIVE,
                )

    def test_permission_or_verification_failure_needs_attention_without_fake_retry_success(self) -> None:
        snapshot = self.snapshot(
            gates=(
                self.observation(CapabilityGate.READ),
                self.observation(
                    CapabilityGate.WRITE,
                    CapabilityEvidenceState.PERMISSION_DENIED,
                ),
                self.observation(
                    CapabilityGate.REMOTE_READBACK,
                    CapabilityEvidenceState.FAILED,
                    reason_code="readback_mismatch",
                ),
            ),
        )
        plan = self.plan(snapshot)
        self.assertEqual(plan.connection_state, ConnectionState.NEEDS_ATTENTION)
        self.assertEqual(plan.next_action, ConnectionNextAction.REPORT_BLOCKER)
        self.assertFalse(plan.connected)
        self.assertIn(
            "capability_write_permission_denied",
            plan.reason_codes,
        )

    def test_unsupported_required_capability_is_unavailable(self) -> None:
        snapshot = self.snapshot(
            gates=(
                self.observation(CapabilityGate.READ),
                self.observation(
                    CapabilityGate.WRITE,
                    CapabilityEvidenceState.UNSUPPORTED,
                ),
                self.observation(CapabilityGate.REMOTE_READBACK),
            ),
        )
        plan = self.plan(snapshot)
        self.assertEqual(plan.connection_state, ConnectionState.UNAVAILABLE)
        self.assertEqual(plan.next_action, ConnectionNextAction.REPORT_BLOCKER)
        self.assertFalse(plan.connected)

    def test_policy_approval_required_is_needs_attention_and_denial_is_unavailable(self) -> None:
        required = self.plan(
            self.snapshot(),
            policy=self.policy(approval=ApprovalState.REQUIRED),
        )
        self.assertEqual(required.connection_state, ConnectionState.NEEDS_ATTENTION)
        self.assertEqual(required.next_action, ConnectionNextAction.REPORT_BLOCKER)
        self.assertIn("policy_approval_required", required.reason_codes)

        denied = self.plan(
            self.snapshot(),
            policy=self.policy(approval=ApprovalState.DENIED),
        )
        self.assertEqual(denied.connection_state, ConnectionState.UNAVAILABLE)
        self.assertEqual(denied.next_action, ConnectionNextAction.REPORT_BLOCKER)
        self.assertIn("policy_approval_denied", denied.reason_codes)

    def test_data_classification_block_is_unavailable_even_if_provider_is_connected(self) -> None:
        plan = self.plan(
            self.snapshot(),
            policy=self.policy(data_classes=("personal",)),
            intent=self.intent(data_classification="restricted"),
        )
        self.assertEqual(plan.connection_state, ConnectionState.UNAVAILABLE)
        self.assertFalse(plan.connected)
        self.assertIn(
            "policy_data_classification_not_allowed",
            plan.reason_codes,
        )
        self.assertIn(ConnectionCommand.DISCONNECT, plan.available_commands)

    def test_authorization_denied_can_offer_connect_retry_without_claiming_connected(self) -> None:
        snapshot = self.snapshot(
            authorization=AuthorizationState.DENIED,
            gates=(),
        )
        inspect = self.plan(snapshot)
        self.assertEqual(inspect.connection_state, ConnectionState.NEEDS_ATTENTION)
        self.assertEqual(inspect.available_commands, (ConnectionCommand.CONNECT,))

        retry = self.plan(snapshot, command=ConnectionCommand.CONNECT)
        self.assertEqual(
            retry.next_action,
            ConnectionNextAction.START_NATIVE_AUTHORIZATION,
        )
        self.assertFalse(retry.connected)

    def test_disconnect_is_connection_only_and_never_provider_data_deletion(self) -> None:
        plan = self.plan(
            self.snapshot(),
            command=ConnectionCommand.DISCONNECT,
        )
        self.assertEqual(
            plan.next_action,
            ConnectionNextAction.START_NATIVE_DISCONNECT,
        )
        self.assertEqual(plan.flow_channel, NativeFlowChannel.PROVIDER_NATIVE)
        self.assertEqual(plan.effect_scope, ConnectionEffectScope.CONNECTION_ONLY)
        self.assertIn("disconnect_connection_only", plan.reason_codes)
        self.assertNotIn("delete", " ".join(plan.reason_codes))

    def test_host_disconnect_uses_native_host_account_management(self) -> None:
        plan = self.plan(
            self.snapshot(),
            surface=self.host_surface(),
            command=ConnectionCommand.DISCONNECT,
        )
        self.assertEqual(
            plan.next_action,
            ConnectionNextAction.START_NATIVE_DISCONNECT,
        )
        self.assertEqual(plan.flow_channel, NativeFlowChannel.HOST_NATIVE)
        self.assertEqual(plan.effect_scope, ConnectionEffectScope.CONNECTION_ONLY)

    def test_no_native_authorization_flow_is_honestly_unavailable_not_manual_setup(self) -> None:
        unavailable_surface = ConnectionSurface(
            kind=ConnectionSurfaceKind.HOST_CONTROLLED,
            authorization_flow=NativeFlowChannel.UNAVAILABLE,
            disconnect_flow=NativeFlowChannel.UNAVAILABLE,
        )
        snapshot = self.snapshot(
            authorization=AuthorizationState.REQUIRED,
            gates=(),
        )
        plan = self.plan(snapshot, surface=unavailable_surface)
        self.assertEqual(plan.connection_state, ConnectionState.UNAVAILABLE)
        self.assertEqual(plan.next_action, ConnectionNextAction.REPORT_BLOCKER)
        self.assertIn(
            "surface_native_authorization_unavailable",
            plan.reason_codes,
        )
        self.assertEqual(plan.available_commands, ())

    def test_hard_provider_target_never_substitutes_another_valid_provider(self) -> None:
        google_missing = self.snapshot(
            provider="microsoft",
            service="calendar",
        )
        result = plan_provider_connection(
            self.intent(provider="google"),
            self.product_surface(),
            (
                self.candidate(
                    "microsoft-calendar",
                    provider="microsoft",
                    service="calendar",
                    snapshot=google_missing,
                ),
            ),
            now=NOW,
            max_age_seconds=3600,
        )
        self.assertEqual(result.connection_state, ConnectionState.UNAVAILABLE)
        self.assertIsNone(result.selected_lane_id)
        self.assertIn("route_required_provider_unavailable", result.reason_codes)

    def test_broken_unrelated_lane_does_not_poison_selected_target(self) -> None:
        broken = self.snapshot(
            provider="microsoft",
            service="calendar",
            gates=(
                self.observation(
                    CapabilityGate.READ,
                    observed_at="2026-09-01T05:35:00Z",
                ),
            ),
        )
        unrelated = self.candidate(
            "microsoft-broken",
            provider="microsoft",
            service="calendar",
            snapshot=broken,
            priority=0,
        )
        plan = self.plan(
            self.snapshot(),
            extra_candidates=(unrelated,),
        )
        self.assertEqual(plan.connection_state, ConnectionState.CONNECTED)
        self.assertEqual(plan.selected_lane_id, "google-native-calendar")
        self.assertNotIn("capability_evidence_invalid", plan.reason_codes)

    def test_stale_verified_evidence_is_reverified_automatically(self) -> None:
        stale = self.snapshot(
            gates=(
                self.observation(CapabilityGate.READ, observed_at=STALE),
                self.observation(CapabilityGate.WRITE, observed_at=STALE),
                self.observation(CapabilityGate.REMOTE_READBACK, observed_at=STALE),
            ),
        )
        plan = self.plan(stale)
        self.assertEqual(plan.connection_state, ConnectionState.NEEDS_ATTENTION)
        self.assertEqual(plan.next_action, ConnectionNextAction.VERIFY_CAPABILITIES)

    def test_surface_channel_must_match_surface_kind(self) -> None:
        with self.assertRaises(ProviderOnboardingValidationError):
            ConnectionSurface(
                kind=ConnectionSurfaceKind.HOST_CONTROLLED,
                authorization_flow=NativeFlowChannel.PROVIDER_NATIVE,
                disconnect_flow=NativeFlowChannel.HOST_NATIVE,
            )

        with self.assertRaises(ProviderOnboardingValidationError):
            ConnectionSurface(
                kind=ConnectionSurfaceKind.PRODUCT_OWNED,
                authorization_flow=NativeFlowChannel.PROVIDER_NATIVE,
                disconnect_flow=NativeFlowChannel.HOST_NATIVE,
            )

    def test_public_contract_has_no_manual_setup_or_activation_action(self) -> None:
        action_values = {action.value for action in ConnectionNextAction}
        self.assertFalse(any("manual" in value for value in action_values))
        self.assertFalse(any("script" in value for value in action_values))
        self.assertFalse(any("terminal" in value for value in action_values))
        self.assertFalse(any("activate_service" in value for value in action_values))


if __name__ == "__main__":
    unittest.main()
