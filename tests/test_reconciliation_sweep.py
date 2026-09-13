import hashlib
import unittest

from ops.reconciliation_sweep import (
    CheckpointConflictError,
    ClaimGateError,
    ManifestError,
    MemoryCheckpointStore,
    ModuleResult,
    ModuleSpec,
    MutationReadback,
    ReconciliationCounts,
    ReconciliationSweep,
    RunSpec,
    SourceStatus,
)


def digest(text):
    return hashlib.sha256(text.encode()).hexdigest()


def make_spec(*modules, run_key=None):
    return RunSpec.build(
        local_date="2026-09-13",
        timezone="America/New_York",
        slot="am",
        context="road",
        modules=modules,
        run_key=run_key,
    )


def complete(module_id, *, fresh=True, rebuild=False):
    return ModuleResult(
        module_id=module_id,
        disposition="complete",
        counts=ReconciliationCounts(discovered=3, matched=2, updated=1),
        sources=(SourceStatus(f"{module_id}.source", "fresh" if fresh else "unknown", "complete", "cursor-2"),),
        mutations=(MutationReadback(f"{module_id}.mutation", True, True, digest(f"{module_id}-readback")),),
        rebuild_verified=rebuild,
        next_cursor="cursor-2",
    )


class ReconciliationSweepTests(unittest.TestCase):
    def test_successful_multi_module_run_and_claim_gate(self):
        sweep = ReconciliationSweep(MemoryCheckpointStore())
        run = make_spec(ModuleSpec("finance", rebuild_required=True), ModuleSpec("mileage", depends_on=("finance",)))
        result = sweep.run(
            run,
            {"finance": lambda ctx: complete("finance", rebuild=True), "mileage": lambda ctx: complete("mileage")},
            previous_cursors={"finance": "cursor-1"},
        )
        self.assertFalse(result.required_action)
        self.assertEqual([item.module_id for item in result.modules], ["finance", "mileage"])
        self.assertTrue(result.claim_allowed("finance", "reconciled"))
        self.assertTrue(result.claim_allowed("finance", "current"))
        self.assertEqual(len(result.checkpoint_fingerprint), 64)

    def test_unknown_freshness_allows_reconciled_but_not_current(self):
        result = ReconciliationSweep(MemoryCheckpointStore()).run(
            make_spec(ModuleSpec("finance")), {"finance": lambda ctx: complete("finance", fresh=False)}
        )
        self.assertTrue(result.claim_allowed("finance", "reconciled"))
        self.assertFalse(result.claim_allowed("finance", "current"))
        with self.assertRaises(ClaimGateError):
            result.assert_claim("finance", "current")

    def test_missing_required_readback_fails_closed(self):
        result = ReconciliationSweep(MemoryCheckpointStore()).run(
            make_spec(ModuleSpec("finance")),
            {"finance": lambda ctx: ModuleResult("finance", "complete", mutations=(MutationReadback("finance.write", True),))},
        )
        self.assertEqual(result.module("finance").blocker_code, "module_contract_violation")
        self.assertTrue(result.required_action)
        self.assertFalse(result.claim_allowed("finance", "updated"))

    def test_required_rebuild_must_be_verified(self):
        result = ReconciliationSweep(MemoryCheckpointStore()).run(
            make_spec(ModuleSpec("finance", rebuild_required=True)), {"finance": lambda ctx: complete("finance")}
        )
        self.assertEqual(result.module("finance").blocker_code, "module_contract_violation")

    def test_needs_review_is_checkpointed_and_blocks_strong_claims(self):
        result = ReconciliationSweep(MemoryCheckpointStore()).run(
            make_spec(ModuleSpec("purchases")),
            {"purchases": lambda ctx: ModuleResult(
                "purchases", "needs_review",
                counts=ReconciliationCounts(discovered=2, unresolved=1),
                sources=(SourceStatus("mail", "fresh", "complete"),),
                review_item_ids=("purchase.large-001",),
            )},
        )
        self.assertTrue(result.required_action)
        self.assertEqual(result.module("purchases").review_item_ids, ("purchase.large-001",))
        self.assertFalse(result.claim_allowed("purchases", "done"))

    def test_blocked_module_does_not_suppress_independent_healthy_module(self):
        calls = []
        result = ReconciliationSweep(MemoryCheckpointStore()).run(
            make_spec(ModuleSpec("mail"), ModuleSpec("calendar", required=False)),
            {
                "mail": lambda ctx: ModuleResult("mail", "blocked", blocker_code="provider_unavailable"),
                "calendar": lambda ctx: (calls.append("calendar") or complete("calendar")),
            },
        )
        self.assertEqual(calls, ["calendar"])
        self.assertEqual(result.module("calendar").disposition, "complete")
        self.assertTrue(result.required_action)

    def test_dependency_block_prevents_handler_execution(self):
        calls = []
        result = ReconciliationSweep(MemoryCheckpointStore()).run(
            make_spec(ModuleSpec("mail"), ModuleSpec("orders", depends_on=("mail",))),
            {
                "mail": lambda ctx: ModuleResult("mail", "blocked", blocker_code="provider_unavailable"),
                "orders": lambda ctx: calls.append("orders"),
            },
        )
        self.assertEqual(calls, [])
        self.assertEqual(result.module("orders").blocker_code, "dependency_not_verified")

    def test_handler_exception_is_sanitized(self):
        secret = "synthetic-private-path-/tmp/foo-token"
        def boom(ctx):
            raise RuntimeError(secret)
        result = ReconciliationSweep(MemoryCheckpointStore()).run(make_spec(ModuleSpec("mail")), {"mail": boom})
        self.assertNotIn(secret, str(result.to_payload()))
        self.assertEqual(result.module("mail").blocker_code, "handler_exception")

    def test_duplicate_module_ids_rejected(self):
        with self.assertRaises(ManifestError):
            make_spec(ModuleSpec("mail"), ModuleSpec("mail"))

    def test_dependency_cycle_rejected(self):
        with self.assertRaises(ManifestError):
            make_spec(ModuleSpec("a", depends_on=("b",)), ModuleSpec("b", depends_on=("a",)))

    def test_missing_dependency_rejected(self):
        with self.assertRaises(ManifestError):
            make_spec(ModuleSpec("orders", depends_on=("mail",)))

    def test_duplicate_mutation_ids_fail_closed(self):
        mutation = MutationReadback("finance.write", True, True, digest("readback"))
        result = ReconciliationSweep(MemoryCheckpointStore()).run(
            make_spec(ModuleSpec("finance")),
            {"finance": lambda ctx: ModuleResult("finance", "complete", mutations=(mutation, mutation))},
        )
        self.assertEqual(result.module("finance").blocker_code, "module_contract_violation")

    def test_negative_counts_fail_closed(self):
        result = ReconciliationSweep(MemoryCheckpointStore()).run(
            make_spec(ModuleSpec("finance")),
            {"finance": lambda ctx: ModuleResult("finance", "complete", counts=ReconciliationCounts(updated=-1))},
        )
        self.assertEqual(result.module("finance").blocker_code, "module_contract_violation")

    def test_completed_run_replay_does_not_rerun_handler(self):
        store = MemoryCheckpointStore(); sweep = ReconciliationSweep(store); run = make_spec(ModuleSpec("finance")); calls=[]
        def handler(ctx):
            calls.append(ctx.previous_cursor); return complete("finance")
        first = sweep.run(run, {"finance": handler}, previous_cursors={"finance": "cursor-1"})
        second = sweep.run(run, {"finance": handler}, previous_cursors={"finance": "cursor-x"})
        self.assertEqual(calls, ["cursor-1"])
        self.assertFalse(first.idempotent_replay)
        self.assertTrue(second.idempotent_replay)
        self.assertEqual(second.checkpoint_fingerprint, first.checkpoint_fingerprint)

    def test_same_run_id_with_different_manifest_conflicts(self):
        store=MemoryCheckpointStore(); sweep=ReconciliationSweep(store); original=make_spec(ModuleSpec("finance"))
        sweep.run(original, {"finance": lambda ctx: complete("finance")})
        altered=RunSpec(original.run_id, original.local_date, original.timezone, original.slot, original.context, (ModuleSpec("mail"),))
        with self.assertRaises(CheckpointConflictError):
            sweep.run(altered, {"mail": lambda ctx: complete("mail")})

    def test_not_applicable_is_terminal_without_action_required(self):
        result=ReconciliationSweep(MemoryCheckpointStore()).run(
            make_spec(ModuleSpec("weather")), {"weather": lambda ctx: ModuleResult("weather", "not_applicable")}
        )
        self.assertFalse(result.required_action)
        self.assertFalse(result.claim_allowed("weather", "done"))

    def test_optional_blocker_does_not_force_global_action_required(self):
        result=ReconciliationSweep(MemoryCheckpointStore()).run(
            make_spec(ModuleSpec("jobs", required=False)),
            {"jobs": lambda ctx: ModuleResult("jobs", "blocked", blocker_code="provider_unavailable")},
        )
        self.assertFalse(result.required_action)

    def test_previous_cursor_outside_manifest_is_rejected(self):
        with self.assertRaises(ManifestError):
            ReconciliationSweep(MemoryCheckpointStore()).run(
                make_spec(ModuleSpec("finance")), {"finance": lambda ctx: complete("finance")}, previous_cursors={"mail": "cursor-1"}
            )

    def test_verified_mutation_requires_sha256_fingerprint(self):
        result=ReconciliationSweep(MemoryCheckpointStore()).run(
            make_spec(ModuleSpec("finance")),
            {"finance": lambda ctx: ModuleResult("finance", "complete", mutations=(MutationReadback("finance.write", True, True, "not-a-digest"),))},
        )
        self.assertEqual(result.module("finance").blocker_code, "module_contract_violation")

    def test_run_identity_is_deterministic(self):
        modules=(ModuleSpec("finance"), ModuleSpec("mileage", depends_on=("finance",)))
        a=make_spec(*modules); b=make_spec(*modules)
        self.assertEqual(a.run_id, b.run_id)
        self.assertEqual(a.manifest_fingerprint, b.manifest_fingerprint)

    def test_manual_run_key_changes_identity(self):
        self.assertNotEqual(make_spec(ModuleSpec("finance"), run_key="manual-1").run_id, make_spec(ModuleSpec("finance"), run_key="manual-2").run_id)

    def test_non_text_context_is_rejected_as_manifest_error(self):
        with self.assertRaises(ManifestError):
            RunSpec.build(local_date="2026-09-13", timezone="America/New_York", slot="am", context=42, modules=(ModuleSpec("finance"),))


if __name__ == "__main__":
    unittest.main()
