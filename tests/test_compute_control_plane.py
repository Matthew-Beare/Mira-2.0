from __future__ import annotations

import unittest

from mira.command_sequencer import (
    COMPUTE_JOB_RESOURCE_TYPE,
    ComputeJobControlPlane,
    QueueStateError,
)
from mira.structured_state import InMemoryStructuredStateAdapter


T0 = "2026-09-08T10:00:00Z"
T1 = "2026-09-08T10:01:00Z"
T2 = "2026-09-08T10:02:00Z"
T3 = "2026-09-08T10:03:00Z"
T4 = "2026-09-08T10:04:00Z"
T5 = "2026-09-08T10:05:00Z"
T6 = "2026-09-08T10:06:00Z"
H1 = "1" * 64
H2 = "2" * 64
H3 = "3" * 64


class ComputeControlPlaneTests(unittest.TestCase):
    def setUp(self) -> None:
        self.adapter = InMemoryStructuredStateAdapter(
            schema_version="1",
            resource_types=(COMPUTE_JOB_RESOURCE_TYPE,),
            event_types=("compute_job_test_event",),
        )
        self.control = ComputeJobControlPlane(self.adapter)

    def submit(
        self,
        job_id: str = "job-a",
        *,
        priority: int = 100,
        caps: tuple[str, ...] = ("coding",),
        max_attempts: int = 3,
        created_at: str = T0,
        key: str | None = None,
    ):
        return self.control.submit(
            job_id,
            operation_id=f"op-{job_id}",
            service_id="compute",
            data_classification="personal",
            required_capabilities=caps,
            input_artifact_id=f"input-{job_id}",
            input_sha256=H1,
            priority=priority,
            max_attempts=max_attempts,
            created_at=created_at,
            idempotency_key=key or f"submit-{job_id}",
        )

    def lease(
        self,
        *,
        worker: str = "worker-a",
        caps: tuple[str, ...] = ("coding", "python"),
        lease_id: str = "lease-a",
        leased_at: str = T1,
        expires_at: str = T5,
        key: str = "lease-key",
    ):
        return self.control.lease_next(
            worker_id=worker,
            worker_capabilities=caps,
            lease_id=lease_id,
            leased_at=leased_at,
            lease_expires_at=expires_at,
            idempotency_key=key,
        )

    def test_submit_is_durable_and_exact_retry_is_idempotent(self) -> None:
        first = self.submit()
        second = self.submit()
        self.assertEqual(first.state, "queued")
        self.assertEqual(first.revision, 1)
        self.assertTrue(second.idempotent_replay)
        self.assertEqual(second.revision, 1)
        self.assertEqual(self.control.get("job-a").input_sha256, H1)

    def test_lease_selection_is_priority_then_time_then_id_and_capability_filtered(self) -> None:
        self.submit("job-low", priority=50, caps=("gpu",), created_at=T0)
        self.submit("job-b", priority=10, created_at=T1)
        self.submit("job-a", priority=10, created_at=T1)
        leased = self.lease(caps=("coding",), lease_id="lease-priority")
        self.assertIsNotNone(leased)
        self.assertEqual(leased.job_id, "job-a")
        self.assertEqual(leased.state, "leased")
        self.assertEqual(leased.attempts, 1)
        self.assertEqual(self.control.get("job-low").state, "queued")

    def test_exact_lease_retry_does_not_increment_attempt_twice(self) -> None:
        self.submit()
        first = self.lease()
        second = self.lease()
        self.assertEqual(first.attempts, 1)
        self.assertTrue(second.idempotent_replay)
        self.assertEqual(second.attempts, 1)
        self.assertEqual(second.revision, first.revision)

    def test_lease_replay_binds_capability_material(self) -> None:
        self.submit()
        self.lease(caps=("coding", "python"), key="lease-material")
        with self.assertRaises(QueueStateError):
            self.lease(caps=("coding",), key="lease-material")

    def test_active_lease_id_cannot_be_reused_with_different_material(self) -> None:
        self.submit("job-a")
        self.submit("job-b")
        first = self.lease(lease_id="lease-shared", key="lease-first")
        self.assertEqual(first.job_id, "job-a")
        with self.assertRaises(QueueStateError):
            self.control.lease_next(
                worker_id="worker-b",
                worker_capabilities=("coding",),
                lease_id="lease-shared",
                leased_at=T2,
                lease_expires_at=T6,
                idempotency_key="lease-second",
            )
        self.assertEqual(self.control.get("job-b").state, "queued")
        self.assertEqual(self.control.get("job-b").attempts, 0)

    def test_only_matching_active_lease_can_start_and_complete(self) -> None:
        self.submit()
        leased = self.lease()
        self.assertIsNotNone(leased)
        with self.assertRaises(QueueStateError):
            self.control.start(
                "job-a",
                worker_id="worker-b",
                lease_id="lease-a",
                started_at=T2,
                idempotency_key="bad-start",
            )
        running = self.control.start(
            "job-a",
            worker_id="worker-a",
            lease_id="lease-a",
            started_at=T2,
            idempotency_key="start-a",
        )
        self.assertEqual(running.state, "running")
        with self.assertRaises(QueueStateError):
            self.control.complete(
                "job-a",
                worker_id="worker-a",
                lease_id="wrong-lease",
                runtime_id="runtime-a",
                result_artifact_id="result-a",
                result_sha256=H2,
                completed_at=T3,
                idempotency_key="bad-complete",
            )

    def test_completion_records_exact_result_provenance_and_replays(self) -> None:
        self.submit()
        self.lease()
        self.control.start(
            "job-a",
            worker_id="worker-a",
            lease_id="lease-a",
            started_at=T2,
            idempotency_key="start-a",
        )
        first = self.control.complete(
            "job-a",
            worker_id="worker-a",
            lease_id="lease-a",
            runtime_id="runtime-a",
            result_artifact_id="result-a",
            result_sha256=H2,
            completed_at=T3,
            idempotency_key="complete-a",
        )
        self.assertEqual(first.state, "succeeded")
        self.assertEqual(first.result_worker_id, "worker-a")
        self.assertEqual(first.result_runtime_id, "runtime-a")
        self.assertEqual(first.result_artifact_id, "result-a")
        self.assertEqual(first.result_sha256, H2)
        self.assertEqual(first.result_attempt, 1)
        self.assertIsNone(first.lease_id)
        replay = self.control.complete(
            "job-a",
            worker_id="worker-a",
            lease_id="lease-a",
            runtime_id="runtime-a",
            result_artifact_id="result-a",
            result_sha256=H2,
            completed_at=T3,
            idempotency_key="complete-a",
        )
        self.assertTrue(replay.idempotent_replay)

    def test_pause_resume_preserves_checkpoint_and_allows_new_lease(self) -> None:
        self.submit()
        self.lease()
        self.control.start(
            "job-a",
            worker_id="worker-a",
            lease_id="lease-a",
            started_at=T2,
            idempotency_key="start-a",
        )
        paused = self.control.pause(
            "job-a",
            worker_id="worker-a",
            lease_id="lease-a",
            checkpoint_artifact_id="checkpoint-a",
            checkpoint_sha256=H3,
            paused_at=T3,
            idempotency_key="pause-a",
        )
        self.assertEqual(paused.state, "paused")
        self.assertEqual(paused.checkpoint_artifact_id, "checkpoint-a")
        self.assertIsNone(paused.lease_id)
        resumed = self.control.resume("job-a", idempotency_key="resume-a")
        self.assertEqual(resumed.state, "queued")
        self.assertEqual(resumed.checkpoint_sha256, H3)
        leased_again = self.lease(
            lease_id="lease-b",
            leased_at=T4,
            expires_at=T6,
            key="lease-b-key",
        )
        self.assertIsNotNone(leased_again)
        self.assertEqual(leased_again.job_id, "job-a")
        self.assertEqual(leased_again.attempts, 2)
        self.assertEqual(leased_again.checkpoint_artifact_id, "checkpoint-a")

    def test_pause_replay_binds_paused_at(self) -> None:
        self.submit()
        self.lease()
        self.control.start(
            "job-a",
            worker_id="worker-a",
            lease_id="lease-a",
            started_at=T2,
            idempotency_key="start-a",
        )
        first = self.control.pause(
            "job-a",
            worker_id="worker-a",
            lease_id="lease-a",
            checkpoint_artifact_id="checkpoint-a",
            checkpoint_sha256=H3,
            paused_at=T3,
            idempotency_key="pause-material",
        )
        replay = self.control.pause(
            "job-a",
            worker_id="worker-a",
            lease_id="lease-a",
            checkpoint_artifact_id="checkpoint-a",
            checkpoint_sha256=H3,
            paused_at=T3,
            idempotency_key="pause-material",
        )
        self.assertTrue(replay.idempotent_replay)
        self.assertEqual(replay.revision, first.revision)
        with self.assertRaises(QueueStateError):
            self.control.pause(
                "job-a",
                worker_id="worker-a",
                lease_id="lease-a",
                checkpoint_artifact_id="checkpoint-a",
                checkpoint_sha256=H3,
                paused_at=T4,
                idempotency_key="pause-material",
            )

    def test_queued_cancel_is_terminal_and_active_cancel_requires_ack(self) -> None:
        self.submit("job-queued")
        cancelled = self.control.request_cancel(
            "job-queued", requested_at=T1, idempotency_key="cancel-queued"
        )
        self.assertEqual(cancelled.state, "cancelled")
        self.assertTrue(cancelled.cancel_requested)

        self.submit("job-active")
        active = self.control.lease_next(
            worker_id="worker-a",
            worker_capabilities=("coding",),
            lease_id="lease-active",
            leased_at=T1,
            lease_expires_at=T5,
            idempotency_key="lease-active-key",
        )
        self.assertIsNotNone(active)
        requested = self.control.request_cancel(
            "job-active", requested_at=T2, idempotency_key="cancel-active"
        )
        self.assertEqual(requested.state, "leased")
        self.assertTrue(requested.cancel_requested)
        with self.assertRaises(QueueStateError):
            self.control.complete(
                "job-active",
                worker_id="worker-a",
                lease_id="lease-active",
                runtime_id="runtime-a",
                result_artifact_id="result-active",
                result_sha256=H2,
                completed_at=T3,
                idempotency_key="complete-after-cancel",
            )
        acked = self.control.acknowledge_cancel(
            "job-active",
            worker_id="worker-a",
            lease_id="lease-active",
            cancelled_at=T3,
            idempotency_key="ack-cancel",
        )
        self.assertEqual(acked.state, "cancelled")
        self.assertIsNone(acked.lease_id)

    def test_cancel_request_and_ack_replay_bind_timestamps(self) -> None:
        self.submit()
        self.lease()
        first = self.control.request_cancel(
            "job-a", requested_at=T2, idempotency_key="cancel-material"
        )
        replay = self.control.request_cancel(
            "job-a", requested_at=T2, idempotency_key="cancel-material"
        )
        self.assertTrue(replay.idempotent_replay)
        self.assertEqual(replay.revision, first.revision)
        with self.assertRaises(QueueStateError):
            self.control.request_cancel(
                "job-a", requested_at=T3, idempotency_key="cancel-material"
            )
        ack = self.control.acknowledge_cancel(
            "job-a",
            worker_id="worker-a",
            lease_id="lease-a",
            cancelled_at=T3,
            idempotency_key="ack-material",
        )
        ack_replay = self.control.acknowledge_cancel(
            "job-a",
            worker_id="worker-a",
            lease_id="lease-a",
            cancelled_at=T3,
            idempotency_key="ack-material",
        )
        self.assertTrue(ack_replay.idempotent_replay)
        self.assertEqual(ack_replay.revision, ack.revision)
        with self.assertRaises(QueueStateError):
            self.control.acknowledge_cancel(
                "job-a",
                worker_id="worker-a",
                lease_id="lease-a",
                cancelled_at=T4,
                idempotency_key="ack-material",
            )

    def test_retryable_failure_requeues_until_attempt_budget_is_exhausted(self) -> None:
        self.submit(max_attempts=2)
        self.lease(lease_id="lease-1", key="lease-1-key")
        retried = self.control.fail(
            "job-a",
            worker_id="worker-a",
            lease_id="lease-1",
            error_code="worker_error",
            failed_at=T2,
            retryable=True,
            idempotency_key="fail-1",
        )
        self.assertEqual(retried.state, "queued")
        self.assertEqual(retried.attempts, 1)
        second = self.lease(
            lease_id="lease-2",
            leased_at=T3,
            expires_at=T5,
            key="lease-2-key",
        )
        self.assertEqual(second.attempts, 2)
        failed = self.control.fail(
            "job-a",
            worker_id="worker-a",
            lease_id="lease-2",
            error_code="worker_error",
            failed_at=T4,
            retryable=True,
            idempotency_key="fail-2",
        )
        self.assertEqual(failed.state, "failed")
        self.assertEqual(failed.finished_at, T4)

    def test_retryable_failure_exact_replay_survives_requeue(self) -> None:
        self.submit(max_attempts=2)
        self.lease(lease_id="lease-1", key="lease-1-key")
        first = self.control.fail(
            "job-a",
            worker_id="worker-a",
            lease_id="lease-1",
            error_code="worker_error",
            failed_at=T2,
            retryable=True,
            idempotency_key="fail-material",
        )
        self.assertEqual(first.state, "queued")
        replay = self.control.fail(
            "job-a",
            worker_id="worker-a",
            lease_id="lease-1",
            error_code="worker_error",
            failed_at=T2,
            retryable=True,
            idempotency_key="fail-material",
        )
        self.assertTrue(replay.idempotent_replay)
        self.assertEqual(replay.revision, first.revision)
        with self.assertRaises(QueueStateError):
            self.control.fail(
                "job-a",
                worker_id="worker-a",
                lease_id="lease-1",
                error_code="worker_error",
                failed_at=T3,
                retryable=True,
                idempotency_key="fail-material",
            )

    def test_expired_lease_requeues_or_fails_at_attempt_limit(self) -> None:
        self.submit("job-retry", max_attempts=2)
        self.submit("job-terminal", max_attempts=1, priority=1)
        first = self.control.lease_next(
            worker_id="worker-a",
            worker_capabilities=("coding",),
            lease_id="lease-terminal",
            leased_at=T1,
            lease_expires_at=T2,
            idempotency_key="lease-terminal-key",
        )
        self.assertEqual(first.job_id, "job-terminal")
        changed = self.control.reap_expired(now=T3)
        self.assertEqual(changed[0].state, "failed")
        second = self.control.lease_next(
            worker_id="worker-a",
            worker_capabilities=("coding",),
            lease_id="lease-retry",
            leased_at=T3,
            lease_expires_at=T4,
            idempotency_key="lease-retry-key",
        )
        self.assertEqual(second.job_id, "job-retry")
        changed = self.control.reap_expired(now=T5)
        self.assertEqual(changed[0].job_id, "job-retry")
        self.assertEqual(changed[0].state, "queued")
        self.assertEqual(changed[0].error_code, "lease_expired")

    def test_injected_private_or_unknown_schema_field_fails_readback(self) -> None:
        self.submit()
        record = self.adapter.get(COMPUTE_JOB_RESOURCE_TYPE, "job-a")
        payload = dict(record.payload)
        payload["hostname"] = "private-host"
        self.adapter.upsert(
            COMPUTE_JOB_RESOURCE_TYPE,
            "job-a",
            payload,
            idempotency_key="inject-private",
            expected_revision=record.revision,
        )
        with self.assertRaises(QueueStateError):
            self.control.get("job-a")

    def test_submission_shape_contains_no_raw_execution_or_private_binding_fields(self) -> None:
        self.submit()
        payload = self.adapter.get(COMPUTE_JOB_RESOURCE_TYPE, "job-a").payload
        forbidden = {
            "prompt",
            "output",
            "hostname",
            "ip_address",
            "mac_address",
            "credentials",
            "token",
            "secret",
            "idempotency_key",
            "shell_command",
            "python_code",
            "inference_endpoint",
            "model_path",
        }
        self.assertTrue(forbidden.isdisjoint(payload))


if __name__ == "__main__":
    unittest.main()
