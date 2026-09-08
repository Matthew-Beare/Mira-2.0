from __future__ import annotations

import unittest

from mira.runtime_router import (
    ApprovalState,
    LocalComputeMode,
    RouteReason,
    RouteRequest,
    RuntimeAvailability,
    RuntimeHealth,
    RuntimeKind,
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


NOW = "2026-09-08T05:30:00Z"
RECENT = "2026-09-08T05:25:00Z"


class ComputeRoutingTests(unittest.TestCase):
    def snapshot(self, provider: str) -> ProviderCapabilitySnapshot:
        return ProviderCapabilitySnapshot(
            provider_id=provider,
            service_id="ai-runtime",
            authorization_state=AuthorizationState.AUTHORIZED,
            authorization_observed_at=RECENT,
            gates=(
                GateObservation(
                    gate=CapabilityGate.READ,
                    state=CapabilityEvidenceState.VERIFIED,
                    observed_at=RECENT,
                ),
            ),
            resource_ref=f"synthetic:{provider}:ai-runtime",
            scopes=("ai-runtime.synthetic",),
        )

    def policy(
        self,
        mode: LocalComputeMode = LocalComputeMode.NORMAL,
        *,
        approval: ApprovalState = ApprovalState.APPROVED,
        data_classes: tuple[str, ...] = ("personal",),
    ) -> RuntimePolicy:
        return RuntimePolicy(
            policy_id=f"compute-{mode.value}",
            approval_state=approval,
            allowed_data_classifications=data_classes,
            local_compute_mode=mode,
        )

    def candidate(
        self,
        lane: str,
        provider: str,
        *,
        kind: RuntimeKind = RuntimeKind.HOSTED,
        mode: LocalComputeMode = LocalComputeMode.NORMAL,
        capabilities: tuple[str, ...] = ("coding", "python"),
        availability: RuntimeAvailability = RuntimeAvailability.READY,
        health: RuntimeHealth = RuntimeHealth.HEALTHY,
        interactive_lock: bool = False,
        priority: int = 100,
        load_rank: int = 0,
        cost_rank: int = 100,
        policy: RuntimePolicy | None = None,
    ) -> RuntimeLaneCandidate:
        return RuntimeLaneCandidate(
            lane_id=lane,
            runtime_id=f"runtime-{lane}",
            capability=self.snapshot(provider),
            policy=policy or self.policy(mode),
            priority=priority,
            runtime_kind=kind,
            runtime_capabilities=capabilities,
            availability=availability,
            health=health,
            interactive_lock=interactive_lock,
            load_rank=load_rank,
            cost_rank=cost_rank,
        )

    def request(
        self,
        *,
        capabilities: tuple[str, ...] = ("coding",),
        preferred: tuple[str, ...] = (),
        data_classification: str = "personal",
    ) -> RouteRequest:
        return RouteRequest(
            operation_id="studio-code-task",
            service_id="ai-runtime",
            required_gates=(CapabilityGate.READ,),
            data_classification=data_classification,
            preferred_provider_ids=preferred,
            required_runtime_capabilities=capabilities,
        )

    def route(self, *candidates: RuntimeLaneCandidate, request: RouteRequest | None = None):
        return route_runtime(
            request or self.request(),
            candidates,
            now=NOW,
            max_age_seconds=3600,
        )

    def test_off_mode_blocks_local_worker_even_when_present_and_cheapest(self) -> None:
        local = self.candidate(
            "local",
            "local-provider",
            kind=RuntimeKind.LOCAL,
            mode=LocalComputeMode.OFF,
            priority=0,
            cost_rank=0,
        )
        hosted = self.candidate(
            "hosted",
            "hosted-provider",
            priority=100,
            cost_rank=100,
        )
        result = self.route(local, hosted)
        self.assertEqual(result.selected_lane_id, "hosted")
        local_decision = next(
            decision for decision in result.candidate_decisions if decision.lane_id == "local"
        )
        self.assertIn("policy_local_compute_off", local_decision.reason_codes)

    def test_normal_mode_does_not_create_implicit_local_bias(self) -> None:
        local = self.candidate(
            "local",
            "local-provider",
            kind=RuntimeKind.LOCAL,
            priority=100,
        )
        hosted = self.candidate(
            "hosted",
            "hosted-provider",
            priority=10,
        )
        self.assertEqual(self.route(local, hosted).selected_lane_id, "hosted")

    def test_aggressive_mode_prefers_eligible_local_worker(self) -> None:
        local = self.candidate(
            "local",
            "local-provider",
            kind=RuntimeKind.LOCAL,
            mode=LocalComputeMode.AGGRESSIVE,
            priority=500,
            cost_rank=500,
        )
        hosted = self.candidate(
            "hosted",
            "hosted-provider",
            priority=1,
            cost_rank=1,
        )
        self.assertEqual(self.route(hosted, local).selected_lane_id, "local")

    def test_explicit_provider_preference_beats_aggressive_local_bias(self) -> None:
        local = self.candidate(
            "local",
            "local-provider",
            kind=RuntimeKind.LOCAL,
            mode=LocalComputeMode.AGGRESSIVE,
        )
        hosted = self.candidate("hosted", "hosted-provider")
        result = self.route(
            local,
            hosted,
            request=self.request(preferred=("hosted-provider", "local-provider")),
        )
        self.assertEqual(result.selected_lane_id, "hosted")

    def test_required_runtime_capability_is_fail_closed(self) -> None:
        local = self.candidate(
            "local",
            "local-provider",
            kind=RuntimeKind.LOCAL,
            capabilities=("python",),
        )
        hosted = self.candidate(
            "hosted",
            "hosted-provider",
            capabilities=("coding", "python"),
        )
        result = self.route(
            local,
            hosted,
            request=self.request(capabilities=("coding", "python")),
        )
        self.assertEqual(result.selected_lane_id, "hosted")
        local_decision = next(
            decision for decision in result.candidate_decisions if decision.lane_id == "local"
        )
        self.assertIn("capability_runtime_missing_coding", local_decision.reason_codes)

    def test_local_unavailable_or_unsafe_states_are_not_selected(self) -> None:
        cases = (
            (
                {"availability": RuntimeAvailability.OFFLINE},
                "capability_runtime_availability_offline",
            ),
            (
                {"availability": RuntimeAvailability.DRAINING},
                "capability_runtime_availability_draining",
            ),
            (
                {"availability": RuntimeAvailability.FAULTED},
                "capability_runtime_availability_faulted",
            ),
            ({"health": RuntimeHealth.UNKNOWN}, "capability_runtime_health_unknown"),
            ({"health": RuntimeHealth.FAULTED}, "capability_runtime_health_faulted"),
        )
        for overrides, expected_reason in cases:
            with self.subTest(expected_reason=expected_reason):
                local = self.candidate(
                    "local",
                    "local-provider",
                    kind=RuntimeKind.LOCAL,
                    **overrides,
                )
                result = self.route(local)
                self.assertFalse(result.selected)
                self.assertEqual(result.reason, RouteReason.CAPABILITY_BLOCKED)
                self.assertIn(expected_reason, result.candidate_decisions[0].reason_codes)

    def test_interactive_lock_wins_over_aggressive_compute_mode(self) -> None:
        local = self.candidate(
            "local",
            "local-provider",
            kind=RuntimeKind.LOCAL,
            mode=LocalComputeMode.AGGRESSIVE,
            interactive_lock=True,
        )
        hosted = self.candidate("hosted", "hosted-provider")
        result = self.route(local, hosted)
        self.assertEqual(result.selected_lane_id, "hosted")
        local_decision = next(
            decision for decision in result.candidate_decisions if decision.lane_id == "local"
        )
        self.assertIn("policy_interactive_lock", local_decision.reason_codes)

    def test_data_policy_still_blocks_local_compute_before_selection(self) -> None:
        local = self.candidate(
            "local",
            "local-provider",
            kind=RuntimeKind.LOCAL,
            mode=LocalComputeMode.AGGRESSIVE,
            policy=self.policy(
                LocalComputeMode.AGGRESSIVE,
                data_classes=("personal",),
            ),
        )
        result = self.route(
            local,
            request=self.request(data_classification="restricted"),
        )
        self.assertFalse(result.selected)
        self.assertEqual(result.reason, RouteReason.POLICY_BLOCKED)
        self.assertIn(
            "policy_data_classification_not_allowed",
            result.candidate_decisions[0].reason_codes,
        )

    def test_normal_ranking_considers_health_availability_priority_load_and_cost(self) -> None:
        degraded = self.candidate(
            "degraded",
            "local-a",
            kind=RuntimeKind.LOCAL,
            health=RuntimeHealth.DEGRADED,
            priority=0,
        )
        busy = self.candidate(
            "busy",
            "local-b",
            kind=RuntimeKind.LOCAL,
            availability=RuntimeAvailability.BUSY,
            priority=0,
        )
        high_load = self.candidate(
            "high-load",
            "local-c",
            kind=RuntimeKind.LOCAL,
            priority=10,
            load_rank=20,
            cost_rank=1,
        )
        low_load = self.candidate(
            "low-load",
            "local-d",
            kind=RuntimeKind.LOCAL,
            priority=10,
            load_rank=5,
            cost_rank=100,
        )
        self.assertEqual(
            self.route(degraded, busy, high_load, low_load).selected_lane_id,
            "low-load",
        )

        cheap = self.candidate(
            "cheap",
            "local-e",
            kind=RuntimeKind.LOCAL,
            priority=10,
            load_rank=5,
            cost_rank=1,
        )
        expensive = self.candidate(
            "expensive",
            "local-f",
            kind=RuntimeKind.LOCAL,
            priority=10,
            load_rank=5,
            cost_rank=50,
        )
        self.assertEqual(self.route(expensive, cheap).selected_lane_id, "cheap")

    def test_candidate_input_order_does_not_change_result(self) -> None:
        local_a = self.candidate(
            "local-a",
            "local-provider-a",
            kind=RuntimeKind.LOCAL,
            priority=10,
            load_rank=5,
        )
        local_b = self.candidate(
            "local-b",
            "local-provider-b",
            kind=RuntimeKind.LOCAL,
            priority=10,
            load_rank=5,
        )
        first = self.route(local_b, local_a)
        second = self.route(local_a, local_b)
        self.assertEqual(first.selected_lane_id, "local-a")
        self.assertEqual(second.selected_lane_id, "local-a")
        self.assertEqual(first.candidate_decisions, second.candidate_decisions)

    def test_execution_metadata_validation_and_secret_free_shape(self) -> None:
        with self.assertRaises(RuntimeRouterValidationError):
            self.candidate("bad", "local-provider", load_rank=-1)
        with self.assertRaises(RuntimeRouterValidationError):
            self.candidate(
                "bad-lock",
                "local-provider",
                interactive_lock=1,  # type: ignore[arg-type]
            )
        with self.assertRaises(RuntimeRouterValidationError):
            self.policy("aggressive")  # type: ignore[arg-type]

        candidate = self.candidate(
            "local",
            "local-provider",
            kind=RuntimeKind.LOCAL,
        )
        request = self.request()
        for value in (candidate, candidate.policy, request):
            for forbidden in (
                "token",
                "credentials",
                "secret",
                "hostname",
                "ip_address",
                "shell_endpoint",
                "model_path",
            ):
                self.assertFalse(hasattr(value, forbidden))


if __name__ == "__main__":
    unittest.main()
