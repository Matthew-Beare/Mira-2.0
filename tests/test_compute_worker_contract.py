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
    RuntimePolicy,
    RuntimeRouterValidationError,
    WorkerAdvertisement,
    WorkerCandidateProjection,
    WorkerIdentityProof,
    WorkerIdentityState,
    project_worker_candidate,
    route_runtime,
)
from mira.service_state import (
    AuthorizationState,
    CapabilityEvidenceState,
    CapabilityGate,
    GateObservation,
    ProviderCapabilitySnapshot,
)


NOW = "2026-09-08T06:30:00Z"
RECENT = "2026-09-08T06:29:30Z"
STALE = "2026-09-08T06:20:00Z"
FUTURE = "2026-09-08T06:31:00Z"


class ComputeWorkerContractTests(unittest.TestCase):
    def proof(
        self,
        state: WorkerIdentityState = WorkerIdentityState.VERIFIED,
        *,
        verified_at: str = RECENT,
    ) -> WorkerIdentityProof:
        return WorkerIdentityProof(
            principal_id="principal-synthetic-a",
            state=state,
            verified_at=verified_at,
        )

    def policy(
        self,
        *,
        mode: LocalComputeMode = LocalComputeMode.NORMAL,
        approval: ApprovalState = ApprovalState.APPROVED,
    ) -> RuntimePolicy:
        return RuntimePolicy(
            policy_id="worker-policy-synthetic",
            approval_state=approval,
            allowed_data_classifications=("personal",),
            local_compute_mode=mode,
        )

    def advertisement(
        self,
        *,
        identity: WorkerIdentityProof | None = None,
        heartbeat_at: str = RECENT,
        mode: LocalComputeMode = LocalComputeMode.NORMAL,
        availability: RuntimeAvailability = RuntimeAvailability.READY,
        health: RuntimeHealth = RuntimeHealth.HEALTHY,
        interactive_lock: bool = False,
    ) -> WorkerAdvertisement:
        return WorkerAdvertisement(
            worker_id="worker-synthetic-a",
            identity=identity or self.proof(),
            lane_id="local-worker-a",
            runtime_id="runtime-worker-a",
            service_id="ai-runtime",
            runtime_kind=RuntimeKind.LOCAL,
            runtime_capabilities=("python", "coding"),
            policy=self.policy(mode=mode),
            availability=availability,
            health=health,
            interactive_lock=interactive_lock,
            priority=10,
            load_rank=5,
            cost_rank=1,
            heartbeat_at=heartbeat_at,
        )

    def capability(self, *, service_id: str = "ai-runtime") -> ProviderCapabilitySnapshot:
        return ProviderCapabilitySnapshot(
            provider_id="synthetic-local-runtime",
            service_id=service_id,
            authorization_state=AuthorizationState.AUTHORIZED,
            authorization_observed_at=RECENT,
            gates=(
                GateObservation(
                    gate=CapabilityGate.READ,
                    state=CapabilityEvidenceState.VERIFIED,
                    observed_at=RECENT,
                ),
            ),
            resource_ref="synthetic:local-runtime",
            scopes=("ai-runtime.synthetic",),
        )

    def request(self) -> RouteRequest:
        return RouteRequest(
            operation_id="worker-contract-test",
            service_id="ai-runtime",
            required_gates=(CapabilityGate.READ,),
            data_classification="personal",
            required_runtime_capabilities=("coding",),
        )

    def project(
        self,
        advertisement: WorkerAdvertisement | None = None,
        capability: ProviderCapabilitySnapshot | None = None,
    ) -> WorkerCandidateProjection:
        return project_worker_candidate(
            advertisement or self.advertisement(),
            capability or self.capability(),
            now=NOW,
            max_heartbeat_age_seconds=120,
        )

    def test_verified_fresh_worker_projects_to_existing_router_and_is_selected(self) -> None:
        projection = self.project()
        self.assertTrue(projection.identity_verified)
        self.assertTrue(projection.heartbeat_fresh)
        self.assertEqual(projection.reason_codes, ())
        self.assertIsNotNone(projection.candidate)

        result = route_runtime(
            self.request(),
            (projection.candidate,),  # type: ignore[arg-type]
            now=NOW,
            max_age_seconds=120,
        )
        self.assertTrue(result.selected)
        self.assertEqual(result.selected_lane_id, "local-worker-a")
        self.assertEqual(result.selected_runtime_id, "runtime-worker-a")

    def test_unverified_and_revoked_identity_never_produce_routable_candidate(self) -> None:
        for state in (WorkerIdentityState.UNVERIFIED, WorkerIdentityState.REVOKED):
            with self.subTest(state=state):
                projection = self.project(
                    self.advertisement(identity=self.proof(state))
                )
                self.assertFalse(projection.identity_verified)
                self.assertIsNone(projection.candidate)
                self.assertIn(
                    f"worker_identity_{state.value}",
                    projection.reason_codes,
                )

    def test_stale_heartbeat_projects_fail_closed_without_mutating_advertisement(self) -> None:
        advertisement = self.advertisement(heartbeat_at=STALE)
        projection = self.project(advertisement)
        self.assertTrue(projection.identity_verified)
        self.assertFalse(projection.heartbeat_fresh)
        self.assertIn("worker_heartbeat_stale", projection.reason_codes)
        self.assertIsNotNone(projection.candidate)
        self.assertEqual(
            projection.candidate.availability,  # type: ignore[union-attr]
            RuntimeAvailability.OFFLINE,
        )
        self.assertEqual(
            projection.candidate.health,  # type: ignore[union-attr]
            RuntimeHealth.UNKNOWN,
        )
        self.assertEqual(advertisement.availability, RuntimeAvailability.READY)
        self.assertEqual(advertisement.health, RuntimeHealth.HEALTHY)

        result = route_runtime(
            self.request(),
            (projection.candidate,),  # type: ignore[arg-type]
            now=NOW,
            max_age_seconds=120,
        )
        self.assertFalse(result.selected)
        self.assertEqual(result.reason, RouteReason.CAPABILITY_BLOCKED)
        self.assertIn(
            "capability_runtime_availability_offline",
            result.candidate_decisions[0].reason_codes,
        )
        self.assertIn(
            "capability_runtime_health_unknown",
            result.candidate_decisions[0].reason_codes,
        )

    def test_future_heartbeat_and_identity_proof_after_heartbeat_are_rejected(self) -> None:
        with self.assertRaises(RuntimeRouterValidationError):
            self.project(self.advertisement(heartbeat_at=FUTURE))

        with self.assertRaises(RuntimeRouterValidationError):
            self.project(
                self.advertisement(
                    identity=self.proof(verified_at=NOW),
                    heartbeat_at=RECENT,
                )
            )

    def test_provider_capability_service_must_match_worker_service(self) -> None:
        with self.assertRaises(RuntimeRouterValidationError):
            self.project(capability=self.capability(service_id="calendar"))

    def test_existing_local_compute_off_policy_still_wins_after_projection(self) -> None:
        projection = self.project(
            self.advertisement(mode=LocalComputeMode.OFF)
        )
        self.assertIsNotNone(projection.candidate)
        result = route_runtime(
            self.request(),
            (projection.candidate,),  # type: ignore[arg-type]
            now=NOW,
            max_age_seconds=120,
        )
        self.assertFalse(result.selected)
        self.assertEqual(result.reason, RouteReason.POLICY_BLOCKED)
        self.assertIn(
            "policy_local_compute_off",
            result.candidate_decisions[0].reason_codes,
        )

    def test_interactive_lock_still_wins_after_projection(self) -> None:
        projection = self.project(
            self.advertisement(interactive_lock=True)
        )
        self.assertIsNotNone(projection.candidate)
        result = route_runtime(
            self.request(),
            (projection.candidate,),  # type: ignore[arg-type]
            now=NOW,
            max_age_seconds=120,
        )
        self.assertFalse(result.selected)
        self.assertEqual(result.reason, RouteReason.POLICY_BLOCKED)
        self.assertIn(
            "policy_interactive_lock",
            result.candidate_decisions[0].reason_codes,
        )

    def test_projection_is_deterministic_and_secret_free(self) -> None:
        advertisement = self.advertisement()
        capability = self.capability()
        first = self.project(advertisement, capability)
        second = self.project(advertisement, capability)
        self.assertEqual(first, second)

        forbidden = (
            "token",
            "credentials",
            "secret",
            "hostname",
            "ip_address",
            "mac_address",
            "serial_number",
            "shell_endpoint",
            "python_endpoint",
            "inference_endpoint",
            "model_path",
        )
        for value in (
            advertisement,
            advertisement.identity,
            first,
            first.candidate,
        ):
            for field in forbidden:
                self.assertFalse(hasattr(value, field))

    def test_projection_validation_fails_closed(self) -> None:
        with self.assertRaises(RuntimeRouterValidationError):
            project_worker_candidate(
                self.advertisement(),
                self.capability(),
                now=NOW,
                max_heartbeat_age_seconds=0,
            )
        with self.assertRaises(RuntimeRouterValidationError):
            WorkerIdentityProof(
                principal_id="principal",
                state="verified",  # type: ignore[arg-type]
                verified_at=RECENT,
            )


if __name__ == "__main__":
    unittest.main()
