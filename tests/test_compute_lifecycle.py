import dataclasses
import unittest

from mira.command_sequencer import ComputeJobView
from mira.compute_lifecycle import (
    ComputeLifecycleError,
    LifecycleIntent,
    LifecycleJobActionKind,
    LifecycleLocks,
    WorkerPowerState,
    plan_compute_lifecycle,
)
from mira.compute_safety import (
    ComputeSafetyPolicy,
    SensorDirection,
    SensorObservation,
    SensorSafetyPolicy,
    evaluate_compute_safety,
)
from mira.service_state import WorkerRegistryView


NOW = "2026-09-09T05:00:00Z"
SAFETY_NOW = "2026-09-09T04:59:30Z"


def worker(
    *,
    worker_id: str = "worker-a",
    availability: str = "ready",
    health: str = "healthy",
    interactive_lock: bool = False,
) -> WorkerRegistryView:
    return WorkerRegistryView(
        worker_id=worker_id,
        revision=1,
        principal_id="principal-a",
        identity_state="verified",
        identity_verified_at="2026-09-09T04:50:00Z",
        lane_id="lane-a",
        runtime_id="runtime-a",
        service_id="compute-service",
        runtime_kind="local",
        runtime_capabilities=("python_compute",),
        policy_id="policy-a",
        approval_state="approved",
        allowed_data_classifications=("internal",),
        local_compute_mode="normal",
        availability=availability,
        health=health,
        interactive_lock=interactive_lock,
        priority=1,
        load_rank=0,
        cost_rank=0,
        heartbeat_at="2026-09-09T04:59:00Z",
    )


def job(
    job_id: str,
    *,
    state: str = "running",
    lease_worker_id: str | None = "worker-a",
) -> ComputeJobView:
    active = state in {"leased", "running"}
    terminal = state in {"succeeded", "failed", "cancelled"}
    return ComputeJobView(
        job_id=job_id,
        revision=1,
        operation_id="operation-a",
        service_id="compute-service",
        data_classification="internal",
        required_capabilities=("python_compute",),
        input_artifact_id="artifact-in",
        input_sha256="a" * 64,
        priority=1,
        max_attempts=3,
        state=state,
        attempts=1 if active or terminal else 0,
        created_at="2026-09-09T04:40:00Z",
        cancel_requested=False,
        lease_worker_id=lease_worker_id if active else None,
        lease_id="lease-a" if active else None,
        leased_at="2026-09-09T04:55:00Z" if active else None,
        lease_expires_at="2026-09-09T05:10:00Z" if active else None,
        started_at="2026-09-09T04:56:00Z" if state == "running" else None,
        checkpoint_artifact_id=None,
        checkpoint_sha256=None,
        error_code="synthetic_failure" if state == "failed" else None,
        result_artifact_id="artifact-out" if state == "succeeded" else None,
        result_sha256="b" * 64 if state == "succeeded" else None,
        result_worker_id="worker-a" if state == "succeeded" else None,
        result_runtime_id="runtime-a" if state == "succeeded" else None,
        result_attempt=1 if state == "succeeded" else None,
        finished_at="2026-09-09T04:58:00Z" if terminal else None,
        last_transition_key_sha256=None,
        last_transition_material_sha256=None,
    )


def safety(
    value: float | None,
    *,
    shutdown_critical: bool = False,
    shutdown_fault: bool = False,
):
    policy = ComputeSafetyPolicy(
        policy_id="safety-policy",
        sensors=(
            SensorSafetyPolicy(
                sensor_id="thermal_core",
                unit="degC",
                direction=SensorDirection.HIGH_IS_BAD,
                warning_threshold=70.0,
                critical_threshold=80.0,
                max_age_seconds=60,
            ),
        ),
        safe_shutdown_on_critical=shutdown_critical,
        safe_shutdown_on_sensor_fault=shutdown_fault,
    )
    observations = (
        ()
        if value is None
        else (
            SensorObservation(
                sensor_id="thermal_core",
                value=value,
                unit="degC",
                observed_at="2026-09-09T04:59:15Z",
            ),
        )
    )
    return evaluate_compute_safety(policy, observations, now=SAFETY_NOW)


class ComputeLifecycleTests(unittest.TestCase):
    def test_steady_healthy_worker_allows_new_work(self) -> None:
        decision = plan_compute_lifecycle(
            worker(),
            (),
            intent=LifecycleIntent.STEADY,
            power_state=WorkerPowerState.ON,
            locks=LifecycleLocks(),
            evaluated_at=NOW,
        )
        self.assertTrue(decision.admit_new_work)
        self.assertFalse(decision.request_drain)
        self.assertFalse(decision.stop_workloads)
        self.assertFalse(decision.fault_node)
        self.assertFalse(decision.request_wake)
        self.assertFalse(decision.request_safe_shutdown)
        self.assertIn("lifecycle_allows_new_work", decision.reason_codes)

    def test_registry_interactive_lock_requests_graceful_drain(self) -> None:
        decision = plan_compute_lifecycle(
            worker(interactive_lock=True),
            (job("job-b"), job("job-a")),
            intent=LifecycleIntent.STEADY,
            power_state=WorkerPowerState.ON,
            locks=LifecycleLocks(),
            evaluated_at=NOW,
        )
        self.assertFalse(decision.admit_new_work)
        self.assertTrue(decision.effective_interactive_lock)
        self.assertTrue(decision.request_drain)
        self.assertFalse(decision.stop_workloads)
        self.assertEqual([item.job_id for item in decision.job_actions], ["job-a", "job-b"])
        self.assertTrue(
            all(
                item.action == LifecycleJobActionKind.FINISH_OR_CHECKPOINT
                for item in decision.job_actions
            )
        )

    def test_explicit_interactive_lock_composes_with_registry_state(self) -> None:
        decision = plan_compute_lifecycle(
            worker(interactive_lock=False),
            (job("job-a"),),
            intent=LifecycleIntent.STEADY,
            power_state=WorkerPowerState.ON,
            locks=LifecycleLocks(interactive_lock=True),
            evaluated_at=NOW,
        )
        self.assertTrue(decision.effective_interactive_lock)
        self.assertTrue(decision.request_drain)

    def test_maintenance_lock_blocks_wake_and_requires_resolution(self) -> None:
        decision = plan_compute_lifecycle(
            worker(availability="offline"),
            (),
            intent=LifecycleIntent.WAKE,
            power_state=WorkerPowerState.OFF,
            locks=LifecycleLocks(maintenance_lock=True),
            evaluated_at=NOW,
        )
        self.assertFalse(decision.request_wake)
        self.assertIn("wake", decision.blocked_actions)
        self.assertTrue(decision.requires_human_action)
        self.assertIn("wake_blocked:maintenance_lock", decision.reason_codes)

    def test_do_not_wake_blocks_explicit_wake(self) -> None:
        decision = plan_compute_lifecycle(
            worker(availability="offline"),
            (),
            intent=LifecycleIntent.WAKE,
            power_state=WorkerPowerState.OFF,
            locks=LifecycleLocks(do_not_wake=True),
            evaluated_at=NOW,
        )
        self.assertFalse(decision.request_wake)
        self.assertEqual(decision.blocked_actions, ("wake",))
        self.assertTrue(decision.requires_human_action)

    def test_offline_off_worker_can_be_wake_eligible(self) -> None:
        decision = plan_compute_lifecycle(
            worker(availability="offline", health="healthy"),
            (),
            intent=LifecycleIntent.WAKE,
            power_state=WorkerPowerState.OFF,
            locks=LifecycleLocks(),
            evaluated_at=NOW,
        )
        self.assertTrue(decision.request_wake)
        self.assertIn("wake_eligible", decision.reason_codes)
        self.assertFalse(decision.requires_human_action)

    def test_warning_safety_blocks_wake(self) -> None:
        decision = plan_compute_lifecycle(
            worker(availability="offline"),
            (),
            intent=LifecycleIntent.WAKE,
            power_state=WorkerPowerState.OFF,
            locks=LifecycleLocks(),
            evaluated_at=NOW,
            safety=safety(75.0),
        )
        self.assertFalse(decision.request_wake)
        self.assertIn("wake", decision.blocked_actions)
        self.assertIn("wake_blocked:safety_blocks_wake", decision.reason_codes)

    def test_graceful_shutdown_waits_for_active_job(self) -> None:
        decision = plan_compute_lifecycle(
            worker(),
            (job("job-a"),),
            intent=LifecycleIntent.SHUTDOWN,
            power_state=WorkerPowerState.ON,
            locks=LifecycleLocks(),
            evaluated_at=NOW,
        )
        self.assertTrue(decision.request_drain)
        self.assertFalse(decision.stop_workloads)
        self.assertFalse(decision.request_safe_shutdown)
        self.assertEqual(
            decision.job_actions[0].action,
            LifecycleJobActionKind.FINISH_OR_CHECKPOINT,
        )
        self.assertIn("shutdown_waiting_for_active_jobs", decision.reason_codes)

    def test_graceful_shutdown_requests_power_action_after_jobs_clear(self) -> None:
        decision = plan_compute_lifecycle(
            worker(),
            (),
            intent=LifecycleIntent.SHUTDOWN,
            power_state=WorkerPowerState.ON,
            locks=LifecycleLocks(),
            evaluated_at=NOW,
        )
        self.assertTrue(decision.request_drain)
        self.assertTrue(decision.request_safe_shutdown)
        self.assertFalse(decision.job_actions)
        self.assertIn("safe_shutdown_eligible", decision.reason_codes)

    def test_do_not_shutdown_blocks_ordinary_shutdown(self) -> None:
        decision = plan_compute_lifecycle(
            worker(),
            (),
            intent=LifecycleIntent.SHUTDOWN,
            power_state=WorkerPowerState.ON,
            locks=LifecycleLocks(do_not_shutdown=True),
            evaluated_at=NOW,
        )
        self.assertFalse(decision.request_safe_shutdown)
        self.assertEqual(decision.blocked_actions, ("safe_shutdown",))
        self.assertTrue(decision.requires_human_action)
        self.assertIn("shutdown_blocked:do_not_shutdown_lock", decision.reason_codes)

    def test_critical_safety_overrides_interactive_convenience_for_stop(self) -> None:
        decision = plan_compute_lifecycle(
            worker(interactive_lock=True),
            (job("job-a"),),
            intent=LifecycleIntent.SAFETY_RECONCILE,
            power_state=WorkerPowerState.ON,
            locks=LifecycleLocks(maintenance_lock=True),
            evaluated_at=NOW,
            safety=safety(85.0),
        )
        self.assertFalse(decision.admit_new_work)
        self.assertTrue(decision.request_drain)
        self.assertTrue(decision.stop_workloads)
        self.assertTrue(decision.fault_node)
        self.assertEqual(
            decision.job_actions[0].action,
            LifecycleJobActionKind.STOP_REQUIRED,
        )
        self.assertIn("interactive_lock_active", decision.reason_codes)
        self.assertIn("maintenance_lock_active", decision.reason_codes)

    def test_do_not_shutdown_preserves_critical_shutdown_requirement_as_blocked(self) -> None:
        decision = plan_compute_lifecycle(
            worker(),
            (job("job-a"),),
            intent=LifecycleIntent.SAFETY_RECONCILE,
            power_state=WorkerPowerState.ON,
            locks=LifecycleLocks(do_not_shutdown=True),
            evaluated_at=NOW,
            safety=safety(85.0, shutdown_critical=True),
        )
        self.assertTrue(decision.stop_workloads)
        self.assertTrue(decision.fault_node)
        self.assertFalse(decision.request_safe_shutdown)
        self.assertIn("safe_shutdown", decision.blocked_actions)
        self.assertTrue(decision.requires_human_action)
        self.assertIn("safe_shutdown_required_but_locked", decision.reason_codes)

    def test_safety_shutdown_requests_power_action_only_after_assigned_jobs_clear(self) -> None:
        active = plan_compute_lifecycle(
            worker(),
            (job("job-a"),),
            intent=LifecycleIntent.SAFETY_RECONCILE,
            power_state=WorkerPowerState.ON,
            locks=LifecycleLocks(),
            evaluated_at=NOW,
            safety=safety(85.0, shutdown_critical=True),
        )
        self.assertFalse(active.request_safe_shutdown)
        self.assertIn("shutdown_waiting_for_workload_stop", active.reason_codes)

        clear = plan_compute_lifecycle(
            worker(),
            (),
            intent=LifecycleIntent.SAFETY_RECONCILE,
            power_state=WorkerPowerState.ON,
            locks=LifecycleLocks(),
            evaluated_at=NOW,
            safety=safety(85.0, shutdown_critical=True),
        )
        self.assertTrue(clear.request_safe_shutdown)

    def test_missing_required_sensor_can_drive_fault_shutdown(self) -> None:
        decision = plan_compute_lifecycle(
            worker(),
            (),
            intent=LifecycleIntent.SAFETY_RECONCILE,
            power_state=WorkerPowerState.ON,
            locks=LifecycleLocks(),
            evaluated_at=NOW,
            safety=safety(None, shutdown_fault=True),
        )
        self.assertTrue(decision.stop_workloads)
        self.assertTrue(decision.fault_node)
        self.assertTrue(decision.request_safe_shutdown)
        self.assertIn("safety_severity:sensor_fault", decision.reason_codes)

    def test_other_worker_and_terminal_jobs_do_not_block_target_shutdown(self) -> None:
        jobs = (
            job("other-active", lease_worker_id="worker-b"),
            job("done", state="succeeded"),
        )
        decision = plan_compute_lifecycle(
            worker(),
            jobs,
            intent=LifecycleIntent.SHUTDOWN,
            power_state=WorkerPowerState.ON,
            locks=LifecycleLocks(),
            evaluated_at=NOW,
        )
        self.assertTrue(decision.request_safe_shutdown)
        self.assertEqual(decision.job_actions, ())

    def test_job_input_order_does_not_change_decision(self) -> None:
        left = plan_compute_lifecycle(
            worker(interactive_lock=True),
            (job("job-b"), job("job-a")),
            intent=LifecycleIntent.STEADY,
            power_state=WorkerPowerState.ON,
            locks=LifecycleLocks(),
            evaluated_at=NOW,
        )
        right = plan_compute_lifecycle(
            worker(interactive_lock=True),
            (job("job-a"), job("job-b")),
            intent=LifecycleIntent.STEADY,
            power_state=WorkerPowerState.ON,
            locks=LifecycleLocks(),
            evaluated_at=NOW,
        )
        self.assertEqual(left, right)

    def test_duplicate_job_ids_fail_closed(self) -> None:
        with self.assertRaisesRegex(ComputeLifecycleError, "duplicate compute job"):
            plan_compute_lifecycle(
                worker(),
                (job("job-a"), job("job-a")),
                intent=LifecycleIntent.DRAIN,
                power_state=WorkerPowerState.ON,
                locks=LifecycleLocks(),
                evaluated_at=NOW,
            )

    def test_active_job_without_lease_worker_fails_closed(self) -> None:
        with self.assertRaisesRegex(ComputeLifecycleError, "lacks lease worker"):
            plan_compute_lifecycle(
                worker(),
                (job("job-a", lease_worker_id=None),),
                intent=LifecycleIntent.DRAIN,
                power_state=WorkerPowerState.ON,
                locks=LifecycleLocks(),
                evaluated_at=NOW,
            )

    def test_safety_reconcile_requires_safety_decision(self) -> None:
        with self.assertRaisesRegex(ComputeLifecycleError, "requires a safety decision"):
            plan_compute_lifecycle(
                worker(),
                (),
                intent=LifecycleIntent.SAFETY_RECONCILE,
                power_state=WorkerPowerState.ON,
                locks=LifecycleLocks(),
                evaluated_at=NOW,
            )

    def test_future_safety_decision_fails_closed(self) -> None:
        future = evaluate_compute_safety(
            ComputeSafetyPolicy(
                policy_id="future-policy",
                sensors=(
                    SensorSafetyPolicy(
                        sensor_id="thermal_core",
                        unit="degC",
                        direction=SensorDirection.HIGH_IS_BAD,
                        warning_threshold=70.0,
                        critical_threshold=80.0,
                        max_age_seconds=60,
                    ),
                ),
                safe_shutdown_on_critical=False,
                safe_shutdown_on_sensor_fault=False,
            ),
            (
                SensorObservation(
                    sensor_id="thermal_core",
                    value=60.0,
                    unit="degC",
                    observed_at="2026-09-09T05:00:15Z",
                ),
            ),
            now="2026-09-09T05:00:30Z",
        )
        with self.assertRaisesRegex(ComputeLifecycleError, "cannot be from the future"):
            plan_compute_lifecycle(
                worker(),
                (),
                intent=LifecycleIntent.STEADY,
                power_state=WorkerPowerState.ON,
                locks=LifecycleLocks(),
                evaluated_at=NOW,
                safety=future,
            )

    def test_unknown_power_state_blocks_shutdown_without_inventing_action(self) -> None:
        decision = plan_compute_lifecycle(
            worker(),
            (),
            intent=LifecycleIntent.SHUTDOWN,
            power_state=WorkerPowerState.UNKNOWN,
            locks=LifecycleLocks(),
            evaluated_at=NOW,
        )
        self.assertFalse(decision.request_safe_shutdown)
        self.assertIn("safe_shutdown", decision.blocked_actions)
        self.assertIn("shutdown_blocked:power_state_unknown", decision.reason_codes)

    def test_public_decision_shape_contains_no_private_execution_fields(self) -> None:
        decision = plan_compute_lifecycle(
            worker(),
            (),
            intent=LifecycleIntent.STEADY,
            power_state=WorkerPowerState.ON,
            locks=LifecycleLocks(),
            evaluated_at=NOW,
            safety=safety(60.0),
        )
        material = dataclasses.asdict(decision)
        serialized_keys = " ".join(material.keys()).lower()
        for forbidden in (
            "hostname",
            "ip_address",
            "mac_address",
            "credential",
            "private_key",
            "shell_command",
            "shutdown_command",
            "wol_packet",
            "model_path",
            "provider_resource",
        ):
            self.assertNotIn(forbidden, serialized_keys)

    def test_invalid_non_enum_intent_and_power_state_are_rejected(self) -> None:
        with self.assertRaisesRegex(ComputeLifecycleError, "LifecycleIntent"):
            plan_compute_lifecycle(
                worker(),
                (),
                intent="steady",  # type: ignore[arg-type]
                power_state=WorkerPowerState.ON,
                locks=LifecycleLocks(),
                evaluated_at=NOW,
            )
        with self.assertRaisesRegex(ComputeLifecycleError, "WorkerPowerState"):
            plan_compute_lifecycle(
                worker(),
                (),
                intent=LifecycleIntent.STEADY,
                power_state="on",  # type: ignore[arg-type]
                locks=LifecycleLocks(),
                evaluated_at=NOW,
            )


if __name__ == "__main__":
    unittest.main()
