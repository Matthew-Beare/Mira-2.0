"""Deterministic tests for the M2-M1 canonical command sequencer."""

from __future__ import annotations

from threading import Barrier, Thread
import unittest

from mira.api_core import (
    ApiService,
    AuthenticatedPrincipal,
    CommandEnvelope,
    Grant,
    InMemoryAuditSink,
)
from mira.authority import AuthorityRegistry, AuthoritySpec
from mira.command_sequencer import (
    DuplicateQueuedCommandError,
    InMemoryCommandQueue,
    SerializedCommandWorker,
)
from mira.structured_state import InMemoryStructuredStateAdapter


class CommandSequencerTests(unittest.TestCase):
    def setUp(self) -> None:
        registry_store = InMemoryStructuredStateAdapter(
            schema_version="registry-1",
            resource_types=("authority", "authority_binding"),
            event_types=("registered", "activated"),
        )
        registry = AuthorityRegistry(registry_store)
        self.data = InMemoryStructuredStateAdapter(
            schema_version="data-1",
            resource_types=("entity",),
            event_types=("created", "updated"),
        )
        registry.register_authority(
            AuthoritySpec(
                authority_id="auth-primary",
                adapter_key="memory-primary",
                resource_ref="synthetic-primary",
                namespace="mira2-test",
                failure_domain="process-a",
                owner_id="user-001",
                schema_version="data-1",
                verified=True,
                enabled=True,
            ),
            idempotency_key="register-authority",
            expected_revision=0,
        )
        registry.register_runtime_adapter("memory-primary", self.data)
        registry.activate(
            "entity",
            "auth-primary",
            idempotency_key="bind-entity",
            expected_revision=0,
        )
        self.audit = InMemoryAuditSink()
        self.service = ApiService(
            registry,
            self.audit,
            api_major=1,
            schema_version="mira-api-1",
        )
        self.principal = AuthenticatedPrincipal(
            actor_id="user-001",
            client_id="serialized-worker",
            grants=(
                Grant("entity", "read", "*"),
                Grant("entity", "query", "*"),
                Grant("entity", "upsert", "*"),
                Grant("entity", "append_event", "*"),
            ),
        )
        self.queue = InMemoryCommandQueue()

    def command(self, suffix: str, *, expected_revision: int, state: str) -> CommandEnvelope:
        return CommandEnvelope(
            command_id=f"cmd-{suffix}",
            subject_id="user-001",
            data_class="entity",
            action="upsert",
            api_major=1,
            schema_version="mira-api-1",
            resource_id="entity-001",
            payload={"state": state},
            idempotency_key=f"idem-{suffix}",
            expected_revision=expected_revision,
        )

    def test_same_command_id_cannot_be_queued_twice(self) -> None:
        command = self.command("one", expected_revision=0, state="one")
        self.queue.submit(command)
        with self.assertRaises(DuplicateQueuedCommandError):
            self.queue.submit(command)

    def test_two_stale_commands_are_serialized_so_only_one_can_commit(self) -> None:
        self.queue.submit(self.command("a", expected_revision=0, state="alpha"))
        self.queue.submit(self.command("b", expected_revision=0, state="beta"))
        worker = SerializedCommandWorker(self.service, self.principal, self.queue)
        gate = Barrier(3)
        outcomes = []

        def run_one() -> None:
            gate.wait()
            outcomes.append(worker.process_next())

        threads = [Thread(target=run_one), Thread(target=run_one)]
        for thread in threads:
            thread.start()
        gate.wait()
        for thread in threads:
            thread.join()

        self.assertEqual(sorted(outcome.status for outcome in outcomes), ["failed", "succeeded"])
        entries = self.queue.entries()
        self.assertEqual(entries[0].status, "succeeded")
        self.assertEqual(entries[0].result.record.revision, 1)
        self.assertEqual(entries[1].status, "failed")
        self.assertEqual(entries[1].error_code, "conflict")
        canonical = self.data.get("entity", "entity-001")
        self.assertEqual(canonical.revision, 1)
        self.assertEqual(canonical.payload, {"state": "alpha"})

    def test_crash_after_canonical_success_retries_as_idempotent_replay(self) -> None:
        self.queue.submit(self.command("crash", expected_revision=0, state="created"))
        calls = 0

        def crash_once(entry, result) -> None:
            nonlocal calls
            calls += 1
            if calls == 1:
                raise RuntimeError("synthetic crash after canonical mutation")

        worker = SerializedCommandWorker(
            self.service,
            self.principal,
            self.queue,
            after_execute=crash_once,
        )
        with self.assertRaisesRegex(RuntimeError, "synthetic crash"):
            worker.process_next()

        pending = self.queue.get("cmd-crash")
        self.assertEqual(pending.status, "pending")
        self.assertEqual(pending.attempts, 1)
        self.assertEqual(self.data.get("entity", "entity-001").revision, 1)

        retried = worker.process_next()
        self.assertEqual(retried.status, "succeeded")
        self.assertTrue(retried.result.idempotent_replay)
        self.assertEqual(self.queue.get("cmd-crash").attempts, 2)
        self.assertEqual(self.data.get("entity", "entity-001").revision, 1)

    def test_expected_revision_progresses_across_serialized_commands(self) -> None:
        self.queue.submit(self.command("create", expected_revision=0, state="created"))
        self.queue.submit(self.command("update", expected_revision=1, state="updated"))
        worker = SerializedCommandWorker(self.service, self.principal, self.queue)
        outcomes = worker.process_all()

        self.assertEqual([item.status for item in outcomes], ["succeeded", "succeeded"])
        self.assertEqual(outcomes[0].result.record.revision, 1)
        self.assertEqual(outcomes[1].result.record.revision, 2)
        self.assertEqual(self.data.get("entity", "entity-001").payload, {"state": "updated"})

    def test_authorization_failure_is_terminal_and_does_not_mutate_provider(self) -> None:
        self.queue.submit(
            CommandEnvelope(
                command_id="cmd-other-user",
                subject_id="other-user",
                data_class="entity",
                action="upsert",
                api_major=1,
                schema_version="mira-api-1",
                resource_id="entity-001",
                payload={"state": "forbidden"},
                idempotency_key="idem-other-user",
                expected_revision=0,
            )
        )
        worker = SerializedCommandWorker(self.service, self.principal, self.queue)
        outcome = worker.process_next()
        self.assertEqual(outcome.status, "failed")
        self.assertEqual(outcome.error_code, "authorization_error")
        self.assertEqual(self.queue.get("cmd-other-user").attempts, 1)
        self.assertEqual(self.data.query("entity"), ())


if __name__ == "__main__":
    unittest.main()
