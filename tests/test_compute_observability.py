import unittest

from mira.command_sequencer import ComputeJobView
from mira.compute_observability import (
    ComputeObservabilityError,
    build_compute_observability,
    grafana_compute_panel_plan,
)
from mira.service_state import WorkerRegistryView


NOW = "2026-09-09T04:30:00Z"
HASH_A = "a" * 64
HASH_B = "b" * 64


def worker(
    worker_id: str,
    *,
    runtime_kind: str = "local",
    availability: str = "ready",
    health: str = "healthy",
    identity_state: str = "verified",
    local_compute_mode: str = "normal",
    interactive_lock: bool = False,
    heartbeat_at: str = "2026-09-09T04:29:30Z",
    principal_id: str = "principal-secret-looking",
    runtime_id: str = "runtime-secret-looking",
) -> WorkerRegistryView:
    return WorkerRegistryView(
        worker_id=worker_id,
        revision=1,
        principal_id=principal_id,
        identity_state=identity_state,
        identity_verified_at="2026-09-09T04:00:00Z",
        lane_id="lane-private-looking",
        runtime_id=runtime_id,
        service_id="compute",
        runtime_kind=runtime_kind,
        runtime_capabilities=("python",),
        policy_id="policy-normal",
        approval_state="approved",
        allowed_data_classifications=("private",),
        local_compute_mode=local_compute_mode,
        availability=availability,
        health=health,
        interactive_lock=interactive_lock,
        priority=1,
        load_rank=1,
        cost_rank=1,
        heartbeat_at=heartbeat_at,
    )


def job(
    job_id: str,
    *,
    state: str = "queued",
    attempts: int = 0,
    max_attempts: int = 3,
    created_at: str = "2026-09-09T04:20:00Z",
    started_at: str | None = None,
    finished_at: str | None = None,
    result_worker_id: str | None = None,
    result_runtime_id: str | None = None,
    result_attempt: int | None = None,
) -> ComputeJobView:
    return ComputeJobView(
        job_id=job_id,
        revision=1,
        operation_id="operation-private-looking",
        service_id="compute",
        data_classification="private",
        required_capabilities=("python",),
        input_artifact_id="artifact-private-looking",
        input_sha256=HASH_A,
        priority=1,
        max_attempts=max_attempts,
        state=state,
        attempts=attempts,
        created_at=created_at,
        cancel_requested=False,
        lease_worker_id=None,
        lease_id=None,
        leased_at=None,
        lease_expires_at=None,
        started_at=started_at,
        checkpoint_artifact_id=None,
        checkpoint_sha256=None,
        error_code="synthetic_failure" if state == "failed" else None,
        result_artifact_id="result-private-looking" if state == "succeeded" else None,
        result_sha256=HASH_B if state == "succeeded" else None,
        result_worker_id=result_worker_id,
        result_runtime_id=result_runtime_id,
        result_attempt=result_attempt,
        finished_at=finished_at,
        last_transition_key_sha256=None,
        last_transition_material_sha256=None,
    )


def samples(snapshot, name: str):
    return tuple(sample for sample in snapshot.samples if sample.name == name)


def sample_map(snapshot, name: str):
    return {dict(sample.labels).__repr__(): sample.value for sample in samples(snapshot, name)}


class ComputeObservabilityTests(unittest.TestCase):
    def test_projection_is_deterministic_and_secret_free(self):
        workers_a = (
            worker("worker-private-alpha", runtime_kind="local"),
            worker(
                "worker-private-beta",
                runtime_kind="hosted",
                availability="busy",
                health="degraded",
                heartbeat_at="2026-09-09T04:28:00Z",
                principal_id="principal-private-beta",
                runtime_id="runtime-private-beta",
            ),
        )
        jobs_a = (
            job("job-private-queued"),
            job(
                "job-private-succeeded",
                state="succeeded",
                attempts=1,
                created_at="2026-09-09T04:10:00Z",
                started_at="2026-09-09T04:11:00Z",
                finished_at="2026-09-09T04:20:00Z",
                result_worker_id="worker-private-alpha",
                result_runtime_id="runtime-private-alpha",
                result_attempt=1,
            ),
        )
        first = build_compute_observability(workers_a, jobs_a, now=NOW)
        second = build_compute_observability(
            tuple(reversed(workers_a)), tuple(reversed(jobs_a)), now=NOW
        )
        self.assertEqual(first.samples, second.samples)
        self.assertEqual(first.render_prometheus(), second.render_prometheus())

        text = first.render_prometheus()
        for forbidden in (
            "worker-private-alpha",
            "worker-private-beta",
            "job-private-queued",
            "job-private-succeeded",
            "principal-private-beta",
            "runtime-private-beta",
            "runtime-private-alpha",
            "artifact-private-looking",
            "operation-private-looking",
            "lane-private-looking",
        ):
            self.assertNotIn(forbidden, text)

    def test_worker_freshness_and_bounded_state_aggregation(self):
        snapshot = build_compute_observability(
            (
                worker("local-fresh", heartbeat_at="2026-09-09T04:29:30Z"),
                worker(
                    "local-stale",
                    heartbeat_at="2026-09-09T04:26:00Z",
                    availability="offline",
                    health="unknown",
                    interactive_lock=True,
                ),
                worker(
                    "hosted-fresh",
                    runtime_kind="hosted",
                    heartbeat_at="2026-09-09T04:29:00Z",
                ),
            ),
            (),
            now=NOW,
            heartbeat_stale_after_seconds=120,
        )
        heartbeat = {
            tuple(sample.labels): sample.value
            for sample in samples(snapshot, "mira_compute_worker_heartbeat_age_seconds")
        }
        self.assertEqual(
            heartbeat[(("runtime_kind", "local"), ("statistic", "max"))], 240.0
        )
        self.assertEqual(
            heartbeat[(("runtime_kind", "hosted"), ("statistic", "max"))], 60.0
        )
        stale = {
            tuple(sample.labels): sample.value
            for sample in samples(snapshot, "mira_compute_stale_worker_count")
        }
        self.assertEqual(stale[(("runtime_kind", "local"),)], 1.0)
        self.assertEqual(stale[(("runtime_kind", "hosted"),)], 0.0)

        worker_counts = {
            tuple(sample.labels): sample.value
            for sample in samples(snapshot, "mira_compute_worker_count")
        }
        self.assertEqual(sum(worker_counts.values()), 3.0)
        locked_local = [
            labels
            for labels in worker_counts
            if ("runtime_kind", "local") in labels
            and ("interactive_lock", "true") in labels
        ]
        self.assertEqual(len(locked_local), 1)

    def test_future_heartbeat_fails_closed(self):
        with self.assertRaisesRegex(
            ComputeObservabilityError, "heartbeat_at cannot be from the future"
        ):
            build_compute_observability(
                (worker("future", heartbeat_at="2026-09-09T04:30:01Z"),),
                (),
                now=NOW,
            )

    def test_job_lifecycle_queue_age_attempts_and_runtime_reconciliation(self):
        workers = (
            worker("local-worker", runtime_kind="local"),
            worker("hosted-worker", runtime_kind="hosted"),
        )
        jobs = (
            job(
                "queued-old",
                state="queued",
                attempts=0,
                created_at="2026-09-09T04:00:00Z",
            ),
            job(
                "running",
                state="running",
                attempts=2,
                created_at="2026-09-09T04:05:00Z",
                started_at="2026-09-09T04:06:00Z",
            ),
            job(
                "success-local",
                state="succeeded",
                attempts=1,
                created_at="2026-09-09T04:00:00Z",
                started_at="2026-09-09T04:05:00Z",
                finished_at="2026-09-09T04:15:00Z",
                result_worker_id="local-worker",
                result_runtime_id="runtime-local",
                result_attempt=1,
            ),
            job(
                "failed-hosted",
                state="failed",
                attempts=2,
                created_at="2026-09-09T04:10:00Z",
                started_at="2026-09-09T04:11:00Z",
                finished_at="2026-09-09T04:25:00Z",
                result_worker_id="hosted-worker",
                result_runtime_id="runtime-hosted",
                result_attempt=2,
            ),
            job(
                "cancelled-unknown",
                state="cancelled",
                attempts=0,
                created_at="2026-09-09T04:12:00Z",
                finished_at="2026-09-09T04:22:00Z",
            ),
        )
        snapshot = build_compute_observability(workers, jobs, now=NOW)

        counts = {
            dict(sample.labels)["state"]: sample.value
            for sample in samples(snapshot, "mira_compute_job_count")
        }
        self.assertEqual(counts["queued"], 1.0)
        self.assertEqual(counts["running"], 1.0)
        self.assertEqual(counts["succeeded"], 1.0)
        self.assertEqual(counts["failed"], 1.0)
        self.assertEqual(counts["cancelled"], 1.0)
        self.assertEqual(counts["leased"], 0.0)
        self.assertEqual(counts["paused"], 0.0)

        attempts = {
            dict(sample.labels)["state"]: sample.value
            for sample in samples(snapshot, "mira_compute_job_attempt_count")
        }
        self.assertEqual(attempts["running"], 2.0)
        self.assertEqual(attempts["failed"], 2.0)

        queue_age = samples(snapshot, "mira_compute_queued_job_age_seconds")
        self.assertEqual(len(queue_age), 1)
        self.assertEqual(queue_age[0].value, 1800.0)

        durations = {
            (dict(sample.labels)["state"], dict(sample.labels)["statistic"]): sample.value
            for sample in samples(snapshot, "mira_compute_job_lifecycle_duration_seconds")
        }
        self.assertEqual(durations[("succeeded", "count")], 1.0)
        self.assertEqual(durations[("succeeded", "sum")], 900.0)
        self.assertEqual(durations[("succeeded", "max")], 900.0)
        self.assertEqual(durations[("failed", "sum")], 900.0)
        self.assertEqual(durations[("cancelled", "sum")], 600.0)

        terminal = {
            (dict(sample.labels)["state"], dict(sample.labels)["runtime_kind"]): sample.value
            for sample in samples(snapshot, "mira_compute_terminal_job_count")
        }
        self.assertEqual(terminal[("succeeded", "local")], 1.0)
        self.assertEqual(terminal[("failed", "hosted")], 1.0)
        self.assertEqual(terminal[("cancelled", "unknown")], 1.0)

    def test_unknown_result_worker_does_not_invent_runtime_identity(self):
        snapshot = build_compute_observability(
            (),
            (
                job(
                    "success-orphan",
                    state="succeeded",
                    attempts=1,
                    created_at="2026-09-09T04:00:00Z",
                    started_at="2026-09-09T04:01:00Z",
                    finished_at="2026-09-09T04:02:00Z",
                    result_worker_id="missing-worker",
                    result_runtime_id="private-runtime-name",
                    result_attempt=1,
                ),
            ),
            now=NOW,
        )
        terminal = {
            (dict(sample.labels)["state"], dict(sample.labels)["runtime_kind"]): sample.value
            for sample in samples(snapshot, "mira_compute_terminal_job_count")
        }
        self.assertEqual(terminal[("succeeded", "unknown")], 1.0)
        self.assertEqual(terminal[("succeeded", "local")], 0.0)
        self.assertEqual(terminal[("succeeded", "hosted")], 0.0)
        self.assertNotIn("private-runtime-name", snapshot.render_prometheus())

    def test_invalid_lifecycle_material_fails_closed(self):
        cases = (
            job(
                "terminal-missing-finish",
                state="failed",
                attempts=1,
                created_at="2026-09-09T04:00:00Z",
                started_at="2026-09-09T04:01:00Z",
                finished_at=None,
            ),
            job(
                "finish-before-start",
                state="failed",
                attempts=1,
                created_at="2026-09-09T04:00:00Z",
                started_at="2026-09-09T04:10:00Z",
                finished_at="2026-09-09T04:05:00Z",
            ),
            job(
                "future-created",
                state="queued",
                created_at="2026-09-09T04:31:00Z",
            ),
        )
        for bad_job in cases:
            with self.subTest(job=bad_job.job_id):
                with self.assertRaises(ComputeObservabilityError):
                    build_compute_observability((), (bad_job,), now=NOW)

    def test_duplicate_stable_ids_fail_closed(self):
        duplicate_worker = worker("duplicate-worker")
        with self.assertRaisesRegex(ComputeObservabilityError, "duplicate worker_id"):
            build_compute_observability(
                (duplicate_worker, duplicate_worker), (), now=NOW
            )
        duplicate_job = job("duplicate-job")
        with self.assertRaisesRegex(ComputeObservabilityError, "duplicate job_id"):
            build_compute_observability((), (duplicate_job, duplicate_job), now=NOW)

    def test_prometheus_output_has_stable_family_order(self):
        snapshot = build_compute_observability(
            (worker("one"),),
            (job("queued"),),
            now=NOW,
        )
        text = snapshot.render_prometheus()
        family_positions = [
            text.index("# HELP mira_compute_worker_count"),
            text.index("# HELP mira_compute_worker_heartbeat_age_seconds"),
            text.index("# HELP mira_compute_stale_worker_count"),
            text.index("# HELP mira_compute_job_count"),
            text.index("# HELP mira_compute_job_attempt_count"),
            text.index("# HELP mira_compute_queued_job_age_seconds"),
            text.index("# HELP mira_compute_job_lifecycle_duration_seconds"),
            text.index("# HELP mira_compute_terminal_job_count"),
        ]
        self.assertEqual(family_positions, sorted(family_positions))
        self.assertTrue(text.endswith("\n"))

    def test_grafana_plan_is_stable_read_only_and_identifier_free(self):
        first = grafana_compute_panel_plan()
        second = grafana_compute_panel_plan()
        self.assertEqual(first, second)
        self.assertGreaterEqual(len(first), 8)
        material = "\n".join(
            f"{panel.title}\n{panel.promql}\n{panel.description}" for panel in first
        )
        for forbidden in (
            "worker_id",
            "job_id",
            "principal_id",
            "runtime_id",
            "hostname",
            "address",
            "credential",
            "secret",
        ):
            self.assertNotIn(forbidden, material.lower())
        self.assertTrue(all("mira_compute_" in panel.promql for panel in first))


if __name__ == "__main__":
    unittest.main()
