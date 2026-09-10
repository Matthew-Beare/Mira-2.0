import dataclasses
import unittest

from mira.service_state import (
    CapabilityEvaluation,
    CapabilityGate,
    ConnectionState,
    GateDecision,
)
from mira.studio_competition import StudioActivationPlan, StudioChangeKind
from mira.studio_activation import (
    MutationDisposition,
    StudioActivationExecutionError,
    StudioActivationReceipt,
    StudioExecutionStatus,
    StudioRollbackReceipt,
    StudioSourceMutationResult,
    StudioSourceState,
    StudioSourceTarget,
    execute_studio_activation,
    execute_studio_rollback,
)

BASE = "1" * 40
PROPOSED = "2" * 40
APPLIED = "3" * 40
ROLLED = "4" * 40
OTHER = "5" * 40
SOURCE = "a" * 64
BASE_SOURCE = "b" * 64
BASE_STATE = "c" * 64
APPLIED_STATE = "d" * 64
ROLLBACK_SOURCE = "e" * 64
WRITE_EVIDENCE = "f" * 64
ROLLBACK_EVIDENCE = "1" * 64
UPSTREAM = "2" * 64
TEST_EVIDENCE = "3" * 64
PREVIEW = "4" * 64
APPROVAL = "5" * 64
ROLLBACK_ANCHOR_EVIDENCE = "6" * 64


def plan(**changes):
    values = dict(
        approver_id="operator",
        change_id="studio-change-1",
        packet_id="M2-M1-033",
        work_id="SKILL-BUILDER-001",
        kind=StudioChangeKind.FEATURE,
        base_sha=BASE,
        proposed_sha=PROPOSED,
        source_sha256=SOURCE,
        preview_sha256=PREVIEW,
        upstream_evidence_sha256s=(UPSTREAM,),
        test_evidence_sha256s=(TEST_EVIDENCE,),
        rollback_revision_id="prior-revision-1",
        rollback_state_sha256=BASE_STATE,
        rollback_evidence_sha256=ROLLBACK_ANCHOR_EVIDENCE,
        approval_evidence_sha256=APPROVAL,
    )
    values.update(changes)
    return StudioActivationPlan(**values)


def target(**changes):
    values = dict(
        provider_id="source-provider",
        service_id="source-service",
        target_ref="refs/heads/main",
    )
    values.update(changes)
    return StudioSourceTarget(**values)


def capability(*, deny=None, omit=None, extra_false=False, provider_id=None, service_id=None):
    deny = set(deny or ())
    omit = set(omit or ())
    decisions = []
    for gate in (
        CapabilityGate.READ,
        CapabilityGate.WRITE,
        CapabilityGate.REMOTE_READBACK,
    ):
        if gate in omit:
            continue
        allowed = gate not in deny
        decisions.append(
            GateDecision(
                gate=gate,
                allowed=allowed,
                reason_code="verified" if allowed else "permission_denied",
            )
        )
    if extra_false:
        decisions.append(
            GateDecision(
                gate=CapabilityGate.READ,
                allowed=False,
                reason_code="stale_duplicate",
            )
        )
    return CapabilityEvaluation(
        provider_id=provider_id or "source-provider",
        service_id=service_id or "source-service",
        connection_state=(
            ConnectionState.CONNECTED
            if not deny and not omit and not extra_false
            else ConnectionState.NEEDS_ATTENTION
        ),
        decisions=tuple(decisions),
    )


def source_state(revision=BASE, source=BASE_SOURCE, state=BASE_STATE):
    return StudioSourceState(
        revision_sha=revision,
        source_sha256=source,
        state_sha256=state,
    )


def activation_result(
    revision=APPLIED,
    source=SOURCE,
    state=APPLIED_STATE,
    evidence=WRITE_EVIDENCE,
):
    return StudioSourceMutationResult(
        revision_sha=revision,
        source_sha256=source,
        state_sha256=state,
        evidence_sha256=evidence,
    )


def rollback_result(
    revision=ROLLED,
    source=ROLLBACK_SOURCE,
    state=BASE_STATE,
    evidence=ROLLBACK_EVIDENCE,
):
    return StudioSourceMutationResult(
        revision_sha=revision,
        source_sha256=source,
        state_sha256=state,
        evidence_sha256=evidence,
    )


class FakeAdapter:
    def __init__(
        self,
        *,
        reads=(),
        activation=None,
        rollback=None,
        activation_error=False,
        rollback_error=False,
    ):
        self.reads = list(reads)
        self.activation = activation
        self.rollback = rollback
        self.activation_error = activation_error
        self.rollback_error = rollback_error
        self.read_count = 0
        self.activation_calls = []
        self.rollback_calls = []

    def read_state(self, target_value):
        self.read_count += 1
        if not self.reads:
            raise RuntimeError("no read queued")
        value = self.reads.pop(0)
        if isinstance(value, Exception):
            raise value
        return value

    def apply_activation(self, target_value, **kwargs):
        self.activation_calls.append((target_value, kwargs))
        if self.activation_error:
            raise RuntimeError("write transport failed")
        return self.activation

    def apply_rollback(self, target_value, **kwargs):
        self.rollback_calls.append((target_value, kwargs))
        if self.rollback_error:
            raise RuntimeError("rollback transport failed")
        return self.rollback


def successful_activation_receipt(**changes):
    values = dict(
        status=StudioExecutionStatus.APPLIED,
        reason_code="applied_and_verified",
        packet_id="M2-M1-033",
        work_id="SKILL-BUILDER-001",
        change_id="studio-change-1",
        approver_id="operator",
        target=target(),
        base_sha=BASE,
        proposed_sha=PROPOSED,
        approved_source_sha256=SOURCE,
        applied_revision_sha=APPLIED,
        applied_state_sha256=APPLIED_STATE,
        adapter_evidence_sha256=WRITE_EVIDENCE,
        mutation_disposition=MutationDisposition.PERFORMED,
    )
    values.update(changes)
    return StudioActivationReceipt(**values)


class StudioActivationTests(unittest.TestCase):
    def test_activation_success_requires_exact_preflight_write_and_remote_readback(self):
        mutation = activation_result()
        adapter = FakeAdapter(
            reads=(
                source_state(),
                source_state(APPLIED, SOURCE, APPLIED_STATE),
            ),
            activation=mutation,
        )
        receipt = execute_studio_activation(plan(), target(), capability(), adapter)

        self.assertEqual(receipt.status, StudioExecutionStatus.APPLIED)
        self.assertEqual(receipt.reason_code, "applied_and_verified")
        self.assertEqual(receipt.mutation_disposition, MutationDisposition.PERFORMED)
        self.assertEqual(receipt.applied_revision_sha, APPLIED)
        self.assertEqual(receipt.applied_state_sha256, APPLIED_STATE)
        self.assertEqual(receipt.adapter_evidence_sha256, WRITE_EVIDENCE)
        self.assertEqual(len(adapter.activation_calls), 1)
        called_target, kwargs = adapter.activation_calls[0]
        self.assertEqual(called_target, target())
        self.assertEqual(
            kwargs,
            {
                "change_id": "studio-change-1",
                "expected_revision_sha": BASE,
                "proposed_revision_sha": PROPOSED,
                "proposed_source_sha256": SOURCE,
            },
        )
        self.assertEqual(adapter.read_count, 2)
        self.assertEqual(receipt.receipt_sha256, receipt.receipt_sha256)

    def test_read_write_and_remote_readback_capabilities_are_all_required(self):
        for denied_gate in (
            CapabilityGate.READ,
            CapabilityGate.WRITE,
            CapabilityGate.REMOTE_READBACK,
        ):
            with self.subTest(denied_gate=denied_gate):
                adapter = FakeAdapter()
                receipt = execute_studio_activation(
                    plan(), target(), capability(deny=(denied_gate,)), adapter
                )
                self.assertEqual(receipt.status, StudioExecutionStatus.BLOCKED)
                self.assertEqual(
                    receipt.mutation_disposition, MutationDisposition.NOT_ATTEMPTED
                )
                self.assertIn(denied_gate.value, receipt.reason_code)
                self.assertEqual(adapter.read_count, 0)
                self.assertEqual(adapter.activation_calls, [])

        adapter = FakeAdapter()
        receipt = execute_studio_activation(
            plan(),
            target(),
            capability(omit=(CapabilityGate.REMOTE_READBACK,)),
            adapter,
        )
        self.assertEqual(receipt.status, StudioExecutionStatus.BLOCKED)
        self.assertEqual(receipt.reason_code, "capability_remote_readback_missing")

    def test_capability_and_source_target_identity_must_match(self):
        for cap in (
            capability(provider_id="other-provider"),
            capability(service_id="other-service"),
        ):
            adapter = FakeAdapter()
            receipt = execute_studio_activation(plan(), target(), cap, adapter)
            self.assertEqual(receipt.status, StudioExecutionStatus.BLOCKED)
            self.assertEqual(adapter.read_count, 0)
            self.assertEqual(adapter.activation_calls, [])

    def test_duplicate_required_gate_is_ambiguous_and_blocked(self):
        adapter = FakeAdapter()
        receipt = execute_studio_activation(
            plan(), target(), capability(extra_false=True), adapter
        )
        self.assertEqual(receipt.status, StudioExecutionStatus.BLOCKED)
        self.assertEqual(receipt.reason_code, "capability_read_ambiguous")
        self.assertEqual(adapter.read_count, 0)

    def test_stale_preflight_revision_or_state_blocks_without_mutation(self):
        cases = (
            (source_state(OTHER, BASE_SOURCE, BASE_STATE), "preflight_revision_mismatch"),
            (source_state(BASE, BASE_SOURCE, "7" * 64), "preflight_state_mismatch"),
        )
        for preflight, reason in cases:
            with self.subTest(reason=reason):
                adapter = FakeAdapter(reads=(preflight,))
                receipt = execute_studio_activation(plan(), target(), capability(), adapter)
                self.assertEqual(receipt.status, StudioExecutionStatus.BLOCKED)
                self.assertEqual(receipt.reason_code, reason)
                self.assertEqual(
                    receipt.mutation_disposition, MutationDisposition.NOT_ATTEMPTED
                )
                self.assertEqual(adapter.activation_calls, [])

    def test_invalid_preflight_adapter_state_blocks_without_mutation(self):
        adapter = FakeAdapter(reads=(object(),))
        receipt = execute_studio_activation(plan(), target(), capability(), adapter)
        self.assertEqual(receipt.status, StudioExecutionStatus.BLOCKED)
        self.assertEqual(receipt.reason_code, "preflight_invalid_state")
        self.assertEqual(adapter.activation_calls, [])

    def test_activation_write_exception_is_recovery_required_with_unknown_outcome(self):
        adapter = FakeAdapter(
            reads=(source_state(),),
            activation_error=True,
        )
        receipt = execute_studio_activation(plan(), target(), capability(), adapter)
        self.assertEqual(receipt.status, StudioExecutionStatus.RECOVERY_REQUIRED)
        self.assertEqual(receipt.reason_code, "activation_write_outcome_unknown")
        self.assertEqual(receipt.mutation_disposition, MutationDisposition.UNKNOWN)
        self.assertIsNone(receipt.applied_revision_sha)

    def test_invalid_or_unchanged_activation_result_is_recovery_required(self):
        cases = (
            (object(), "activation_invalid_mutation_result", MutationDisposition.UNKNOWN),
            (
                activation_result(revision=BASE),
                "mutation_revision_unchanged",
                MutationDisposition.PERFORMED,
            ),
        )
        for result, reason, disposition in cases:
            with self.subTest(reason=reason):
                adapter = FakeAdapter(reads=(source_state(),), activation=result)
                receipt = execute_studio_activation(plan(), target(), capability(), adapter)
                self.assertEqual(receipt.status, StudioExecutionStatus.RECOVERY_REQUIRED)
                self.assertEqual(receipt.reason_code, reason)
                self.assertEqual(receipt.mutation_disposition, disposition)

    def test_activation_source_or_remote_readback_mismatch_is_not_success(self):
        wrong_source = activation_result(source="8" * 64)
        adapter = FakeAdapter(reads=(source_state(),), activation=wrong_source)
        receipt = execute_studio_activation(plan(), target(), capability(), adapter)
        self.assertEqual(receipt.status, StudioExecutionStatus.RECOVERY_REQUIRED)
        self.assertEqual(receipt.reason_code, "mutation_source_mismatch")
        self.assertEqual(receipt.mutation_disposition, MutationDisposition.PERFORMED)

        mutation = activation_result()
        adapter = FakeAdapter(
            reads=(source_state(), source_state(APPLIED, SOURCE, "9" * 64)),
            activation=mutation,
        )
        receipt = execute_studio_activation(plan(), target(), capability(), adapter)
        self.assertEqual(receipt.status, StudioExecutionStatus.RECOVERY_REQUIRED)
        self.assertEqual(receipt.reason_code, "activation_readback_mismatch")
        self.assertEqual(receipt.mutation_disposition, MutationDisposition.PERFORMED)

    def test_activation_readback_failure_or_invalid_shape_requires_recovery(self):
        mutation = activation_result()
        for readback, reason in (
            (RuntimeError("remote read failed"), "activation_readback_failed"),
            (object(), "activation_invalid_readback"),
        ):
            with self.subTest(reason=reason):
                adapter = FakeAdapter(
                    reads=(source_state(), readback),
                    activation=mutation,
                )
                receipt = execute_studio_activation(
                    plan(), target(), capability(), adapter
                )
                self.assertEqual(receipt.status, StudioExecutionStatus.RECOVERY_REQUIRED)
                self.assertEqual(receipt.reason_code, reason)
                self.assertEqual(
                    receipt.mutation_disposition, MutationDisposition.PERFORMED
                )

    def test_verified_activation_replay_is_zero_write(self):
        prior = successful_activation_receipt()
        adapter = FakeAdapter(
            reads=(source_state(APPLIED, SOURCE, APPLIED_STATE),),
        )
        replay = execute_studio_activation(
            plan(), target(), capability(), adapter, prior_receipt=prior
        )
        self.assertEqual(replay.status, StudioExecutionStatus.ALREADY_APPLIED)
        self.assertEqual(replay.reason_code, "verified_replay")
        self.assertEqual(replay.mutation_disposition, MutationDisposition.NOT_ATTEMPTED)
        self.assertEqual(adapter.activation_calls, [])
        self.assertEqual(replay.applied_revision_sha, APPLIED)

    def test_prior_receipt_cannot_be_relabelled_to_another_plan_or_target(self):
        adapter = FakeAdapter()
        with self.assertRaises(StudioActivationExecutionError):
            execute_studio_activation(
                plan(),
                target(),
                capability(),
                adapter,
                prior_receipt=successful_activation_receipt(change_id="other-change"),
            )
        with self.assertRaises(StudioActivationExecutionError):
            execute_studio_activation(
                plan(),
                target(),
                capability(),
                adapter,
                prior_receipt=successful_activation_receipt(
                    target=target(target_ref="refs/heads/other")
                ),
            )

    def test_explicit_rollback_requires_exact_applied_state_and_exact_readback(self):
        active = successful_activation_receipt()
        mutation = rollback_result()
        adapter = FakeAdapter(
            reads=(
                source_state(APPLIED, SOURCE, APPLIED_STATE),
                source_state(ROLLED, ROLLBACK_SOURCE, BASE_STATE),
            ),
            rollback=mutation,
        )
        receipt = execute_studio_rollback(
            plan(), active, target(), capability(), adapter
        )
        self.assertEqual(receipt.status, StudioExecutionStatus.ROLLED_BACK)
        self.assertEqual(receipt.reason_code, "rolled_back_and_verified")
        self.assertEqual(receipt.mutation_disposition, MutationDisposition.PERFORMED)
        self.assertEqual(receipt.resulting_revision_sha, ROLLED)
        self.assertEqual(len(adapter.rollback_calls), 1)
        called_target, kwargs = adapter.rollback_calls[0]
        self.assertEqual(called_target, target())
        self.assertEqual(
            kwargs,
            {
                "change_id": "studio-change-1",
                "expected_revision_sha": APPLIED,
                "prior_revision_id": "prior-revision-1",
                "prior_state_sha256": BASE_STATE,
            },
        )
        self.assertEqual(receipt.receipt_sha256, receipt.receipt_sha256)

    def test_rollback_stale_current_state_blocks_zero_mutation(self):
        active = successful_activation_receipt()
        adapter = FakeAdapter(
            reads=(source_state(OTHER, SOURCE, APPLIED_STATE),),
        )
        receipt = execute_studio_rollback(
            plan(), active, target(), capability(), adapter
        )
        self.assertEqual(receipt.status, StudioExecutionStatus.BLOCKED)
        self.assertEqual(receipt.reason_code, "rollback_preflight_mismatch")
        self.assertEqual(receipt.mutation_disposition, MutationDisposition.NOT_ATTEMPTED)
        self.assertEqual(adapter.rollback_calls, [])

    def test_rollback_write_exception_is_recovery_required_unknown(self):
        active = successful_activation_receipt()
        adapter = FakeAdapter(
            reads=(source_state(APPLIED, SOURCE, APPLIED_STATE),),
            rollback_error=True,
        )
        receipt = execute_studio_rollback(
            plan(), active, target(), capability(), adapter
        )
        self.assertEqual(receipt.status, StudioExecutionStatus.RECOVERY_REQUIRED)
        self.assertEqual(receipt.reason_code, "rollback_write_outcome_unknown")
        self.assertEqual(receipt.mutation_disposition, MutationDisposition.UNKNOWN)

    def test_rollback_invalid_unchanged_or_wrong_state_result_requires_recovery(self):
        active = successful_activation_receipt()
        cases = (
            (object(), "rollback_invalid_mutation_result", MutationDisposition.UNKNOWN),
            (
                rollback_result(revision=APPLIED),
                "rollback_revision_unchanged",
                MutationDisposition.PERFORMED,
            ),
            (
                rollback_result(state="7" * 64),
                "rollback_state_mismatch",
                MutationDisposition.PERFORMED,
            ),
        )
        for result, reason, disposition in cases:
            with self.subTest(reason=reason):
                adapter = FakeAdapter(
                    reads=(source_state(APPLIED, SOURCE, APPLIED_STATE),),
                    rollback=result,
                )
                receipt = execute_studio_rollback(
                    plan(), active, target(), capability(), adapter
                )
                self.assertEqual(receipt.status, StudioExecutionStatus.RECOVERY_REQUIRED)
                self.assertEqual(receipt.reason_code, reason)
                self.assertEqual(receipt.mutation_disposition, disposition)

    def test_rollback_readback_failure_invalid_or_mismatch_requires_recovery(self):
        active = successful_activation_receipt()
        mutation = rollback_result()
        cases = (
            (RuntimeError("read failed"), "rollback_readback_failed"),
            (object(), "rollback_invalid_readback"),
            (
                source_state(ROLLED, ROLLBACK_SOURCE, "8" * 64),
                "rollback_readback_mismatch",
            ),
        )
        for readback, reason in cases:
            with self.subTest(reason=reason):
                adapter = FakeAdapter(
                    reads=(
                        source_state(APPLIED, SOURCE, APPLIED_STATE),
                        readback,
                    ),
                    rollback=mutation,
                )
                receipt = execute_studio_rollback(
                    plan(), active, target(), capability(), adapter
                )
                self.assertEqual(receipt.status, StudioExecutionStatus.RECOVERY_REQUIRED)
                self.assertEqual(receipt.reason_code, reason)
                self.assertEqual(
                    receipt.mutation_disposition, MutationDisposition.PERFORMED
                )

    def test_rollback_requires_successful_matching_activation_receipt(self):
        blocked = StudioActivationReceipt(
            status=StudioExecutionStatus.BLOCKED,
            reason_code="blocked",
            packet_id="M2-M1-033",
            work_id="SKILL-BUILDER-001",
            change_id="studio-change-1",
            approver_id="operator",
            target=target(),
            base_sha=BASE,
            proposed_sha=PROPOSED,
            approved_source_sha256=SOURCE,
            applied_revision_sha=None,
            applied_state_sha256=None,
            adapter_evidence_sha256=None,
            mutation_disposition=MutationDisposition.NOT_ATTEMPTED,
        )
        with self.assertRaises(StudioActivationExecutionError):
            execute_studio_rollback(
                plan(), blocked, target(), capability(), FakeAdapter()
            )

    def test_receipt_state_machine_rejects_false_success_and_false_clean_failure(self):
        base_values = dict(
            reason_code="x",
            packet_id="M2-M1-033",
            work_id="SKILL-BUILDER-001",
            change_id="studio-change-1",
            approver_id="operator",
            target=target(),
            base_sha=BASE,
            proposed_sha=PROPOSED,
            approved_source_sha256=SOURCE,
            applied_revision_sha=None,
            applied_state_sha256=None,
            adapter_evidence_sha256=None,
        )
        with self.assertRaises(StudioActivationExecutionError):
            StudioActivationReceipt(
                status=StudioExecutionStatus.APPLIED,
                mutation_disposition=MutationDisposition.NOT_ATTEMPTED,
                **base_values,
            )
        with self.assertRaises(StudioActivationExecutionError):
            StudioActivationReceipt(
                status=StudioExecutionStatus.RECOVERY_REQUIRED,
                mutation_disposition=MutationDisposition.NOT_ATTEMPTED,
                **base_values,
            )

    def test_public_execution_contract_is_secret_and_executor_agnostic(self):
        forbidden = {
            "credential",
            "credentials",
            "token",
            "secret",
            "provider_endpoint",
            "endpoint",
            "hostname",
            "host",
            "ip",
            "mac",
            "shell",
            "command",
            "runner_label",
            "model_path",
        }
        for cls in (
            StudioSourceTarget,
            StudioSourceState,
            StudioSourceMutationResult,
            StudioActivationReceipt,
            StudioRollbackReceipt,
        ):
            names = {field.name for field in dataclasses.fields(cls)}
            self.assertTrue(forbidden.isdisjoint(names), (cls.__name__, names))


if __name__ == "__main__":
    unittest.main()
