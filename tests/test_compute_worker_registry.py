from __future__ import annotations

from dataclasses import replace
import unittest

from mira.runtime_router import (
    RouteReason,
    RouteRequest,
    RuntimeAvailability,
    RuntimeHealth,
    RuntimeRouterValidationError,
    project_worker_candidate,
    route_runtime,
    worker_registry_view_to_advertisement,
)
from mira.service_state import (
    AuthorizationState,
    CapabilityEvidenceState,
    CapabilityGate,
    GateObservation,
    ProviderCapabilitySnapshot,
    ServiceStateValidationError,
    WORKER_RESOURCE_TYPE,
    WorkerRegistryIdentityEvidence,
    WorkerRegistryService,
)
from mira.structured_state import (
    IdempotencyConflictError,
    InMemoryStructuredStateAdapter,
    RevisionConflictError,
)


NOW = "2026-09-08T08:10:00Z"
REGISTER_IDENTITY_AT = "2026-09-08T08:00:00Z"
REGISTER_HEARTBEAT_AT = "2026-09-08T08:00:30Z"
HEARTBEAT_IDENTITY_AT = "2026-09-08T08:01:00Z"
HEARTBEAT_AT = "2026-09-08T08:01:30Z"
HEARTBEAT_2_IDENTITY_AT = "2026-09-08T08:02:00Z"
HEARTBEAT_2_AT = "2026-09-08T08:02:30Z"
ROUTE_IDENTITY_AT = "2026-09-08T08:09:00Z"
ROUTE_HEARTBEAT_AT = "2026-09-08T08:09:30Z"
STALE_IDENTITY_AT = "2026-09-08T07:00:00Z"
STALE_HEARTBEAT_AT = "2026-09-08T07:00:30Z"
PROVIDER_OBSERVED_AT = "2026-09-08T08:09:40Z"


class ComputeWorkerRegistryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.adapter = InMemoryStructuredStateAdapter(
            schema_version="worker-registry-test-v1",
            resource_types=(WORKER_RESOURCE_TYPE,),
            event_types=("synthetic-worker-event",),
        )
        self.registry = WorkerRegistryService(self.adapter)

    def identity(
        self,
        *,
        principal_id: str = "principal-a",
        verified_at: str = REGISTER_IDENTITY_AT,
        state: str = "verified",
    ) -> WorkerRegistryIdentityEvidence:
        return WorkerRegistryIdentityEvidence(
            principal_id=principal_id,
            state=state,
            verified_at=verified_at,
        )

    def register(
        self,
        *,
        worker_id: str = "worker-a",
        principal_id: str = "principal-a",
        identity_at: str = REGISTER_IDENTITY_AT,
        heartbeat_at: str = REGISTER_HEARTBEAT_AT,
        idempotency_key: str = "register-worker-a",
    ):
        return self.registry.register(
            worker_id,
            identity=self.identity(
                principal_id=principal_id,
                verified_at=identity_at,
            ),
            lane_id=f"lane-{worker_id}",
            runtime_id=f"runtime-{worker_id}",
            service_id="ai-runtime",
            runtime_kind="local",
            runtime_capabilities=("python", "coding"),
            policy_id="worker-policy",
            approval_state="approved",
            allowed_data_classifications=("personal",),
            local_compute_mode="normal",
            availability="ready",
            health="healthy",
            interactive_lock=False,
            priority=10,
            load_rank=5,
            cost_rank=1,
            heartbeat_at=heartbeat_at,
            now=NOW,
            idempotency_key=idempotency_key,
        )

    def capability(self) -> ProviderCapabilitySnapshot:
        return ProviderCapabilitySnapshot(
            provider_id="synthetic-local-runtime",
            service_id="ai-runtime",
            authorization_state=AuthorizationState.AUTHORIZED,
            authorization_observed_at=PROVIDER_OBSERVED_AT,
            gates=(
                GateObservation(
                    gate=CapabilityGate.READ,
                    state=CapabilityEvidenceState.VERIFIED,
                    observed_at=PROVIDER_OBSERVED_AT,
                ),
            ),
            resource_ref="synthetic:local-runtime",
            scopes=("ai-runtime.synthetic",),
        )

    def request(self) -> RouteRequest:
        return RouteRequest(
            operation_id="durable-worker-route-test",
            service_id="ai-runtime",
            required_gates=(CapabilityGate.READ,),
            data_classification="personal",
            required_runtime_capabilities=("coding",),
        )

    def test_register_replay_and_exact_readback(self) -> None:
        first = self.register()
        replay = self.register()
        readback = self.registry.get("worker-a")

        self.assertEqual(first.revision, 1)
        self.assertFalse(first.idempotent_replay)
        self.assertEqual(replay.revision, 1)
        self.assertTrue(replay.idempotent_replay)
        self.assertEqual(readback.worker_id, first.worker_id)
        self.assertEqual(readback.principal_id, first.principal_id)
        self.assertEqual(readback.runtime_capabilities, ("coding", "python"))
        self.assertEqual(readback.revision, first.revision)

    def test_second_registration_with_new_key_conflicts_revision(self) -> None:
        self.register()
        with self.assertRaises(RevisionConflictError):
            self.register(idempotency_key="register-worker-a-again")

    def test_heartbeat_updates_only_mutable_execution_state(self) -> None:
        registered = self.register()
        updated = self.registry.heartbeat(
            "worker-a",
            identity=self.identity(verified_at=HEARTBEAT_IDENTITY_AT),
            heartbeat_at=HEARTBEAT_AT,
            now=NOW,
            idempotency_key="heartbeat-worker-a-1",
            runtime_capabilities=("coding", "python", "testing"),
            availability="busy",
            health="degraded",
            interactive_lock=True,
            load_rank=20,
        )

        self.assertEqual(updated.revision, 2)
        self.assertEqual(updated.principal_id, registered.principal_id)
        self.assertEqual(updated.lane_id, registered.lane_id)
        self.assertEqual(updated.runtime_id, registered.runtime_id)
        self.assertEqual(updated.service_id, registered.service_id)
        self.assertEqual(updated.policy_id, registered.policy_id)
        self.assertEqual(updated.priority, registered.priority)
        self.assertEqual(updated.cost_rank, registered.cost_rank)
        self.assertEqual(updated.runtime_capabilities, ("coding", "python", "testing"))
        self.assertEqual(updated.availability, "busy")
        self.assertEqual(updated.health, "degraded")
        self.assertTrue(updated.interactive_lock)
        self.assertEqual(updated.load_rank, 20)

    def test_exact_heartbeat_retry_is_replay_safe(self) -> None:
        self.register()
        kwargs = dict(
            identity=self.identity(verified_at=HEARTBEAT_IDENTITY_AT),
            heartbeat_at=HEARTBEAT_AT,
            now=NOW,
            idempotency_key="heartbeat-worker-a-replay",
            availability="busy",
            load_rank=9,
        )
        first = self.registry.heartbeat("worker-a", **kwargs)
        replay = self.registry.heartbeat("worker-a", **kwargs)

        self.assertEqual(first.revision, 2)
        self.assertFalse(first.idempotent_replay)
        self.assertEqual(replay.revision, first.revision)
        self.assertTrue(replay.idempotent_replay)

    def test_reused_heartbeat_key_with_changed_material_conflicts(self) -> None:
        self.register()
        key = "heartbeat-worker-a-conflict"
        self.registry.heartbeat(
            "worker-a",
            identity=self.identity(verified_at=HEARTBEAT_IDENTITY_AT),
            heartbeat_at=HEARTBEAT_AT,
            now=NOW,
            idempotency_key=key,
            load_rank=7,
        )
        with self.assertRaises(IdempotencyConflictError):
            self.registry.heartbeat(
                "worker-a",
                identity=self.identity(verified_at=HEARTBEAT_2_IDENTITY_AT),
                heartbeat_at=HEARTBEAT_2_AT,
                now=NOW,
                idempotency_key=key,
                load_rank=8,
            )

    def test_wrong_principal_and_backward_times_fail_closed(self) -> None:
        self.register()
        with self.assertRaises(ServiceStateValidationError):
            self.registry.heartbeat(
                "worker-a",
                identity=self.identity(
                    principal_id="principal-b",
                    verified_at=HEARTBEAT_IDENTITY_AT,
                ),
                heartbeat_at=HEARTBEAT_AT,
                now=NOW,
                idempotency_key="heartbeat-wrong-principal",
            )

        with self.assertRaises(ServiceStateValidationError):
            self.registry.heartbeat(
                "worker-a",
                identity=self.identity(verified_at=REGISTER_IDENTITY_AT),
                heartbeat_at="2026-09-08T07:59:59Z",
                now=NOW,
                idempotency_key="heartbeat-backwards",
            )

    def test_unverified_or_revoked_identity_cannot_be_persisted(self) -> None:
        for state in ("unverified", "revoked"):
            with self.subTest(state=state):
                with self.assertRaises(ServiceStateValidationError):
                    self.registry.register(
                        f"worker-{state}",
                        identity=self.identity(state=state),
                        lane_id=f"lane-{state}",
                        runtime_id=f"runtime-{state}",
                        service_id="ai-runtime",
                        runtime_kind="local",
                        runtime_capabilities=("coding",),
                        policy_id="worker-policy",
                        approval_state="approved",
                        allowed_data_classifications=("personal",),
                        local_compute_mode="normal",
                        availability="ready",
                        health="healthy",
                        interactive_lock=False,
                        priority=10,
                        load_rank=0,
                        cost_rank=1,
                        heartbeat_at=REGISTER_HEARTBEAT_AT,
                        now=NOW,
                        idempotency_key=f"register-{state}",
                    )

    def test_list_workers_is_deterministic(self) -> None:
        self.register(
            worker_id="worker-b",
            principal_id="principal-b",
            idempotency_key="register-b",
        )
        self.register(
            worker_id="worker-a",
            principal_id="principal-a",
            idempotency_key="register-a",
        )
        self.assertEqual(
            tuple(worker.worker_id for worker in self.registry.list_workers()),
            ("worker-a", "worker-b"),
        )

    def test_registry_view_projects_through_existing_router(self) -> None:
        view = self.register(
            identity_at=ROUTE_IDENTITY_AT,
            heartbeat_at=ROUTE_HEARTBEAT_AT,
        )
        advertisement = worker_registry_view_to_advertisement(view)
        projection = project_worker_candidate(
            advertisement,
            self.capability(),
            now=NOW,
            max_heartbeat_age_seconds=120,
        )

        self.assertTrue(projection.identity_verified)
        self.assertTrue(projection.heartbeat_fresh)
        self.assertIsNotNone(projection.candidate)
        result = route_runtime(
            self.request(),
            (projection.candidate,),  # type: ignore[arg-type]
            now=NOW,
            max_age_seconds=120,
        )
        self.assertTrue(result.selected)
        self.assertEqual(result.selected_lane_id, "lane-worker-a")

    def test_stale_registry_heartbeat_fails_closed_through_projection(self) -> None:
        view = self.register(
            identity_at=STALE_IDENTITY_AT,
            heartbeat_at=STALE_HEARTBEAT_AT,
        )
        projection = project_worker_candidate(
            worker_registry_view_to_advertisement(view),
            self.capability(),
            now=NOW,
            max_heartbeat_age_seconds=120,
        )

        self.assertTrue(projection.identity_verified)
        self.assertFalse(projection.heartbeat_fresh)
        self.assertEqual(
            projection.candidate.availability,  # type: ignore[union-attr]
            RuntimeAvailability.OFFLINE,
        )
        self.assertEqual(
            projection.candidate.health,  # type: ignore[union-attr]
            RuntimeHealth.UNKNOWN,
        )
        result = route_runtime(
            self.request(),
            (projection.candidate,),  # type: ignore[arg-type]
            now=NOW,
            max_age_seconds=120,
        )
        self.assertFalse(result.selected)
        self.assertEqual(result.reason, RouteReason.CAPABILITY_BLOCKED)

    def test_strict_readback_rejects_private_extra_fields(self) -> None:
        view = self.register()
        record = self.adapter.get(WORKER_RESOURCE_TYPE, view.worker_id)
        payload = dict(record.payload)
        payload["hostname"] = "private-host"
        self.adapter.upsert(
            WORKER_RESOURCE_TYPE,
            view.worker_id,
            payload,
            idempotency_key="inject-private-field",
            expected_revision=record.revision,
        )
        with self.assertRaises(ServiceStateValidationError):
            self.registry.get(view.worker_id)

    def test_router_bridge_fails_closed_on_invalid_registry_enum(self) -> None:
        view = self.register()
        invalid = replace(view, runtime_kind="teleport")
        with self.assertRaises(RuntimeRouterValidationError):
            worker_registry_view_to_advertisement(invalid)


if __name__ == "__main__":
    unittest.main()
