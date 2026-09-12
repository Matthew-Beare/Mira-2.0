from __future__ import annotations

import unittest

from mira.command_sequencer import (
    COMPUTE_JOB_RESOURCE_TYPE,
    ComputeJobControlPlane,
    QueueStateError,
)
from mira.structured_state import InMemoryStructuredStateAdapter


T0 = "2026-09-12T21:00:00Z"
T1 = "2026-09-12T21:01:00Z"
T2 = "2026-09-12T21:02:00Z"
T3 = "2026-09-12T21:03:00Z"
T4 = "2026-09-12T21:04:00Z"
H1 = "1" * 64


class ExactComputeJobLeaseTests(unittest.TestCase):
    def setUp(self) -> None:
        adapter = InMemoryStructuredStateAdapter(
            schema_version="1",
            resource_types=(COMPUTE_JOB_RESOURCE_TYPE,),
            event_types=("compute_job_test_event",),
        )
        self.control = ComputeJobControlPlane(adapter)

    def submit(
        self,
        job_id: str,
        *,
        priority: int = 100,
        caps: tuple[str, ...] = ("coding",),
        max_attempts: int = 3,
        created_at: str = T0,
    ):
        return self.control.submit(
            job_id,
            operation_id="studio_implement",
            service_id="ai-runtime",
            data_classification="private_source",
            required_capabilities=caps,
            input_artifact_id=f"input-{job_id}",
            input_sha256=H1,
            priority=priority,
            max_attempts=max_attempts,
            created_at=created_at,
            idempotency_key=f"submit-{job_id}",
        )

    def lease_exact(
        self,
        job_id: str,
        *,
        worker: str = "worker-a",
        caps: tuple[str, ...] = ("coding", "local_model"),
        lease_id: str = "lease-a",
        leased_at: str = T1,
        expires_at: str = T4,
        key: str = "lease-exact",
    ):
        return self.control.lease_job(
            job_id,
            worker_id=worker,
            worker_capabilities=caps,
            lease_id=lease_id,
            leased_at=leased_at,
            lease_expires_at=expires_at,
            idempotency_key=key,
        )

    def test_exact_lease_never_consumes_higher_ranked_other_job(self) -> None:
        self.submit("job-other", priority=1, created_at=T0)
        self.submit("job-studio", priority=100, created_at=T1)

        leased = self.lease_exact("job-studio")

        self.assertEqual(leased.job_id, "job-studio")
        self.assertEqual(leased.state, "leased")
        self.assertEqual(leased.attempts, 1)
        other = self.control.get("job-other")
        self.assertEqual(other.state, "queued")
        self.assertEqual(other.attempts, 0)

    def test_exact_retry_is_idempotent_and_does_not_increment_attempts(self) -> None:
        self.submit("job-studio")
        first = self.lease_exact("job-studio")
        replay = self.lease_exact("job-studio")

        self.assertTrue(replay.idempotent_replay)
        self.assertEqual(replay.revision, first.revision)
        self.assertEqual(replay.attempts, 1)

    def test_reused_idempotency_key_with_changed_material_fails_closed(self) -> None:
        self.submit("job-studio")
        self.lease_exact("job-studio", caps=("coding", "local_model"))

        with self.assertRaisesRegex(QueueStateError, "different transition material"):
            self.lease_exact("job-studio", caps=("coding",))

    def test_missing_worker_capability_rejects_without_mutation(self) -> None:
        self.submit("job-studio", caps=("coding", "local_model"))

        with self.assertRaisesRegex(QueueStateError, "lacks required"):
            self.lease_exact("job-studio", caps=("coding",))

        current = self.control.get("job-studio")
        self.assertEqual(current.state, "queued")
        self.assertEqual(current.attempts, 0)

    def test_active_lease_id_collision_on_another_job_fails_closed(self) -> None:
        self.submit("job-a")
        self.submit("job-b")
        self.lease_exact("job-a", lease_id="lease-shared", key="lease-a")

        with self.assertRaisesRegex(QueueStateError, "lease_id is already active"):
            self.lease_exact(
                "job-b",
                worker="worker-b",
                lease_id="lease-shared",
                key="lease-b",
            )

        current = self.control.get("job-b")
        self.assertEqual(current.state, "queued")
        self.assertEqual(current.attempts, 0)

    def test_cancelled_nonqueued_and_exhausted_jobs_cannot_be_exact_leased(self) -> None:
        self.submit("job-cancelled")
        self.control.request_cancel(
            "job-cancelled",
            requested_at=T1,
            idempotency_key="cancel-job",
        )
        with self.assertRaisesRegex(QueueStateError, "state cancelled"):
            self.lease_exact("job-cancelled", key="lease-cancelled")

        self.submit("job-running")
        self.lease_exact("job-running", key="lease-running")
        self.control.start(
            "job-running",
            worker_id="worker-a",
            lease_id="lease-a",
            started_at=T2,
            idempotency_key="start-running",
        )
        with self.assertRaisesRegex(QueueStateError, "state running"):
            self.lease_exact("job-running", key="lease-running-again")

        self.submit("job-exhausted", max_attempts=1)
        self.lease_exact(
            "job-exhausted",
            lease_id="lease-exhausted-1",
            key="lease-exhausted-1",
        )
        self.control.fail(
            "job-exhausted",
            worker_id="worker-a",
            lease_id="lease-exhausted-1",
            error_code="worker_error",
            failed_at=T2,
            retryable=True,
            idempotency_key="fail-exhausted",
        )
        with self.assertRaisesRegex(QueueStateError, "state failed"):
            self.lease_exact(
                "job-exhausted",
                lease_id="lease-exhausted-2",
                key="lease-exhausted-2",
            )

    def test_invalid_lease_interval_rejects_before_mutation(self) -> None:
        self.submit("job-studio")
        with self.assertRaisesRegex(QueueStateError, "must be after"):
            self.lease_exact(
                "job-studio",
                leased_at=T3,
                expires_at=T2,
            )
        current = self.control.get("job-studio")
        self.assertEqual(current.state, "queued")
        self.assertEqual(current.attempts, 0)


if __name__ == "__main__":
    unittest.main()
