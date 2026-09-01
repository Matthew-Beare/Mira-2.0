from __future__ import annotations

import unittest

from mira.runtime_router import (
    ApprovalState,
    RouteOutcome,
    RouteReason,
    RouteRequest,
    RuntimeLaneCandidate,
    RuntimePolicy,
    RuntimeRouterValidationError,
    route_runtime,
)
from mira.service_state import (
    AuthorizationState,
    CapabilityEvidenceState,
    CapabilityGate,
    GateObservation,
    ProviderCapabilitySnapshot,
)


NOW = "2026-09-01T04:00:00Z"
RECENT = "2026-09-01T03:55:00Z"
STALE = "2026-09-01T02:00:00Z"


class RuntimeRouterTests(unittest.TestCase):
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
        provider: str,
        *,
        service: str = "calendar",
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
        lane: str,
        provider: str,
        *,
        priority: int = 100,
        service: str = "calendar",
        snapshot: ProviderCapabilitySnapshot | None = None,
        policy: RuntimePolicy | None = None,
    ) -> RuntimeLaneCandidate:
        return RuntimeLaneCandidate(
            lane_id=lane,
            runtime_id=f"runtime-{lane}",
            capability=snapshot or self.snapshot(provider, service=service),
            policy=policy or self.policy(),
            priority=priority,
        )

    def request(
        self,
        *gates: CapabilityGate,
        required_provider: str | None = None,
        preferred: tuple[str, ...] = (),
        service: str = "calendar",
        data_classification: str = "personal",
    ) -> RouteRequest:
        return RouteRequest(
            operation_id="calendar-operation",
            service_id=service,
            required_gates=tuple(gates),
            data_classification=data_classification,
            required_provider_id=required_provider,
            preferred_provider_ids=preferred,
        )

    def route(
        self,
        request: RouteRequest,
        *candidates: RuntimeLaneCandidate,
    ):
        return route_runtime(
            request,
            candidates,
            now=NOW,
            max_age_seconds=3600,
        )

    def test_selects_single_verified_lane(self) -> None:
        result = self.route(
            self.request(CapabilityGate.READ, CapabilityGate.REMOTE_READBACK),
            self.candidate("google-native", "google"),
        )
        self.assertTrue(result.selected)
        self.assertEqual(result.outcome, RouteOutcome.SELECTED)
        self.assertEqual(result.reason, RouteReason.SELECTED)
        self.assertEqual(result.selected_lane_id, "google-native")
        self.assertEqual(result.selected_provider_id, "google")
        self.assertTrue(result.candidate_decisions[0].eligible)

    def test_read_only_lane_is_rejected_for_write_request(self) -> None:
        read_only = self.snapshot(
            "google",
            gates=(
                self.observation(CapabilityGate.READ),
                self.observation(CapabilityGate.REMOTE_READBACK),
            ),
        )
        result = self.route(
            self.request(CapabilityGate.WRITE, CapabilityGate.REMOTE_READBACK),
            self.candidate("google-read-only", "google", snapshot=read_only),
        )
        self.assertFalse(result.selected)
        self.assertEqual(result.reason, RouteReason.CAPABILITY_BLOCKED)
        self.assertIn(
            "capability_write_evidence_unknown",
            result.candidate_decisions[0].reason_codes,
        )

    def test_write_without_verified_remote_readback_is_rejected(self) -> None:
        no_readback = self.snapshot(
            "google",
            gates=(
                self.observation(CapabilityGate.WRITE),
                self.observation(
                    CapabilityGate.REMOTE_READBACK,
                    CapabilityEvidenceState.FAILED,
                    reason_code="readback_mismatch",
                ),
            ),
        )
        result = self.route(
            self.request(CapabilityGate.WRITE, CapabilityGate.REMOTE_READBACK),
            self.candidate("google-write", "google", snapshot=no_readback),
        )
        self.assertEqual(result.reason, RouteReason.CAPABILITY_BLOCKED)
        self.assertIn(
            "capability_remote_readback_readback_mismatch",
            result.candidate_decisions[0].reason_codes,
        )

    def test_revoked_and_stale_capability_lanes_fail_closed(self) -> None:
        revoked = self.snapshot(
            "google",
            authorization=AuthorizationState.REVOKED,
            gates=(self.observation(CapabilityGate.READ),),
        )
        stale = self.snapshot(
            "microsoft",
            gates=(
                self.observation(CapabilityGate.READ, observed_at=STALE),
            ),
        )
        result = self.route(
            self.request(CapabilityGate.READ),
            self.candidate("google", "google", snapshot=revoked),
            self.candidate("microsoft", "microsoft", snapshot=stale),
        )
        self.assertEqual(result.reason, RouteReason.CAPABILITY_BLOCKED)
        reasons = {
            decision.lane_id: decision.reason_codes
            for decision in result.candidate_decisions
        }
        self.assertIn("capability_connection_reconnect", reasons["google"])
        self.assertIn("capability_read_evidence_stale", reasons["microsoft"])

    def test_policy_denial_blocks_otherwise_capable_lane(self) -> None:
        result = self.route(
            self.request(CapabilityGate.READ),
            self.candidate(
                "google",
                "google",
                policy=self.policy(approval=ApprovalState.DENIED),
            ),
        )
        self.assertEqual(result.reason, RouteReason.POLICY_BLOCKED)
        self.assertEqual(
            result.candidate_decisions[0].reason_codes,
            ("policy_approval_denied",),
        )
        self.assertIsNone(result.candidate_decisions[0].capability_evaluation)

    def test_unapproved_data_classification_blocks_lane(self) -> None:
        result = self.route(
            self.request(
                CapabilityGate.READ,
                data_classification="restricted",
            ),
            self.candidate(
                "google",
                "google",
                policy=self.policy(data_classes=("personal",)),
            ),
        )
        self.assertEqual(result.reason, RouteReason.POLICY_BLOCKED)
        self.assertIn(
            "policy_data_classification_not_allowed",
            result.candidate_decisions[0].reason_codes,
        )

    def test_approval_required_is_not_treated_as_approval(self) -> None:
        result = self.route(
            self.request(CapabilityGate.READ),
            self.candidate(
                "managed",
                "managed-provider",
                policy=self.policy(approval=ApprovalState.REQUIRED),
            ),
        )
        self.assertEqual(result.reason, RouteReason.POLICY_BLOCKED)
        self.assertIn(
            "policy_approval_required",
            result.candidate_decisions[0].reason_codes,
        )

    def test_candidate_order_does_not_change_deterministic_selection(self) -> None:
        higher = self.candidate("lane-b", "google", priority=20)
        lower = self.candidate("lane-a", "google", priority=10)
        request = self.request(CapabilityGate.READ)
        first = self.route(request, higher, lower)
        second = self.route(request, lower, higher)
        self.assertEqual(first.selected_lane_id, "lane-a")
        self.assertEqual(second.selected_lane_id, "lane-a")
        self.assertEqual(first.candidate_decisions, second.candidate_decisions)

    def test_preferred_provider_ranks_eligible_lane_before_numeric_priority(self) -> None:
        google = self.candidate("google", "google", priority=1)
        microsoft = self.candidate("microsoft", "microsoft", priority=100)
        result = self.route(
            self.request(
                CapabilityGate.READ,
                preferred=("microsoft", "google"),
            ),
            google,
            microsoft,
        )
        self.assertEqual(result.selected_provider_id, "microsoft")
        self.assertEqual(result.selected_lane_id, "microsoft")

    def test_explicit_provider_requirement_never_silently_substitutes(self) -> None:
        result = self.route(
            self.request(
                CapabilityGate.READ,
                required_provider="microsoft",
            ),
            self.candidate("google", "google"),
        )
        self.assertFalse(result.selected)
        self.assertEqual(result.reason, RouteReason.REQUIRED_PROVIDER_UNAVAILABLE)
        self.assertIn(
            "required_provider_mismatch",
            result.candidate_decisions[0].reason_codes,
        )

    def test_explicit_provider_present_but_unusable_reports_capability_block(self) -> None:
        revoked = self.snapshot(
            "microsoft",
            authorization=AuthorizationState.REVOKED,
            gates=(self.observation(CapabilityGate.READ),),
        )
        result = self.route(
            self.request(
                CapabilityGate.READ,
                required_provider="microsoft",
                preferred=("microsoft",),
            ),
            self.candidate("microsoft", "microsoft", snapshot=revoked),
            self.candidate("google", "google"),
        )
        self.assertEqual(result.reason, RouteReason.CAPABILITY_BLOCKED)
        self.assertFalse(result.selected)

    def test_invalid_evidence_in_one_lane_does_not_poison_valid_lane(self) -> None:
        future = self.snapshot(
            "broken",
            gates=(
                self.observation(
                    CapabilityGate.READ,
                    observed_at="2026-09-01T04:05:00Z",
                ),
            ),
        )
        result = self.route(
            self.request(CapabilityGate.READ),
            self.candidate("broken", "broken", priority=0, snapshot=future),
            self.candidate("google", "google", priority=100),
        )
        self.assertEqual(result.selected_lane_id, "google")
        decisions = {
            decision.lane_id: decision
            for decision in result.candidate_decisions
        }
        self.assertIn(
            "capability_evidence_invalid",
            decisions["broken"].reason_codes,
        )
        self.assertTrue(decisions["google"].eligible)

    def test_service_mismatch_does_not_poison_matching_lane(self) -> None:
        result = self.route(
            self.request(CapabilityGate.READ, service="calendar"),
            self.candidate("drive", "google", service="drive", priority=0),
            self.candidate("calendar", "google", service="calendar", priority=100),
        )
        self.assertEqual(result.selected_lane_id, "calendar")
        mismatch = next(
            decision
            for decision in result.candidate_decisions
            if decision.lane_id == "drive"
        )
        self.assertEqual(mismatch.reason_codes, ("service_mismatch",))

    def test_empty_candidate_set_fails_closed(self) -> None:
        result = self.route(self.request(CapabilityGate.READ))
        self.assertEqual(result.outcome, RouteOutcome.BLOCKED)
        self.assertEqual(result.reason, RouteReason.NO_CANDIDATES)
        self.assertEqual(result.candidate_decisions, ())

    def test_duplicate_lane_ids_and_duplicate_provider_preferences_are_rejected(self) -> None:
        candidate = self.candidate("same", "google")
        with self.assertRaises(RuntimeRouterValidationError):
            self.route(
                self.request(CapabilityGate.READ),
                candidate,
                candidate,
            )

        with self.assertRaises(RuntimeRouterValidationError):
            self.request(
                CapabilityGate.READ,
                preferred=("google", "google"),
            )

    def test_router_shapes_do_not_contain_credentials_or_tokens(self) -> None:
        request = self.request(CapabilityGate.READ)
        candidate = self.candidate("google", "google")
        for value in (request, candidate, candidate.policy):
            self.assertFalse(hasattr(value, "token"))
            self.assertFalse(hasattr(value, "credentials"))
            self.assertFalse(hasattr(value, "secret"))


if __name__ == "__main__":
    unittest.main()
