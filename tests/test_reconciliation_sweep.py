import hashlib

import pytest

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


def digest(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def spec(*modules: ModuleSpec, run_key: str | None = None) -> RunSpec:
    return RunSpec.build(
        local_date="2026-09-13",
        timezone="America/New_York",
        slot="am",
        context="road",
        modules=modules,
        run_key=run_key,
    )


def complete(module_id: str, *, fresh: bool = True, rebuild: bool = False) -> ModuleResult:
    return ModuleResult(
        module_id=module_id,
        disposition="complete",
        counts=ReconciliationCounts(discovered=3, matched=2, updated=1),
        sources=(
            SourceStatus(
                source_id=f"{module_id}.source",
                freshness="fresh" if fresh else "unknown",
                coverage="complete",
                cursor="cursor-2",
            ),
        ),
        mutations=(
            MutationReadback(
                mutation_id=f"{module_id}.mutation",
                required=True,
                readback_verified=True,
                readback_fingerprint=digest(f"{module_id}-readback"),
            ),
        ),
        rebuild_verified=rebuild,
        next_cursor="cursor-2",
    )


def test_successful_multi_module_run_and_claim_gate():
    store = MemoryCheckpointStore()
    sweep = ReconciliationSweep(store)
    run = spec(
        ModuleSpec("finance", rebuild_required=True),
        ModuleSpec("mileage", depends_on=("finance",)),
    )
    result = sweep.run(
        run,
        {
            "finance": lambda ctx: complete("finance", rebuild=True),
            "mileage": lambda ctx: complete("mileage"),
        },
        previous_cursors={"finance": "cursor-1"},
    )
    assert result.required_action is False
    assert [item.module_id for item in result.modules] == ["finance", "mileage"]
    assert result.claim_allowed("finance", "reconciled") is True
    assert result.claim_allowed("finance", "current") is True
    assert len(result.checkpoint_fingerprint) == 64


def test_unknown_freshness_allows_reconciled_but_not_current():
    result = ReconciliationSweep(MemoryCheckpointStore()).run(
        spec(ModuleSpec("finance")),
        {"finance": lambda ctx: complete("finance", fresh=False)},
    )
    assert result.claim_allowed("finance", "reconciled") is True
    assert result.claim_allowed("finance", "current") is False
    with pytest.raises(ClaimGateError):
        result.assert_claim("finance", "current")


def test_missing_required_readback_fails_closed_without_raw_detail():
    result = ReconciliationSweep(MemoryCheckpointStore()).run(
        spec(ModuleSpec("finance")),
        {
            "finance": lambda ctx: ModuleResult(
                module_id="finance",
                disposition="complete",
                mutations=(MutationReadback("finance.write", required=True),),
            )
        },
    )
    finance = result.module("finance")
    assert finance.disposition == "blocked"
    assert finance.blocker_code == "module_contract_violation"
    assert result.required_action is True
    assert result.claim_allowed("finance", "updated") is False


def test_required_rebuild_must_be_verified():
    result = ReconciliationSweep(MemoryCheckpointStore()).run(
        spec(ModuleSpec("finance", rebuild_required=True)),
        {"finance": lambda ctx: complete("finance", rebuild=False)},
    )
    assert result.module("finance").blocker_code == "module_contract_violation"


def test_needs_review_is_checkpointed_and_blocks_strong_claims():
    result = ReconciliationSweep(MemoryCheckpointStore()).run(
        spec(ModuleSpec("purchases")),
        {
            "purchases": lambda ctx: ModuleResult(
                module_id="purchases",
                disposition="needs_review",
                counts=ReconciliationCounts(discovered=2, unresolved=1),
                sources=(SourceStatus("mail", "fresh", "complete"),),
                review_item_ids=("purchase.large-001",),
            )
        },
    )
    assert result.required_action is True
    assert result.module("purchases").review_item_ids == ("purchase.large-001",)
    assert result.claim_allowed("purchases", "done") is False


def test_blocked_module_does_not_suppress_independent_healthy_module():
    calls = []
    result = ReconciliationSweep(MemoryCheckpointStore()).run(
        spec(ModuleSpec("mail"), ModuleSpec("calendar", required=False)),
        {
            "mail": lambda ctx: ModuleResult(
                module_id="mail", disposition="blocked", blocker_code="provider_unavailable"
            ),
            "calendar": lambda ctx: (calls.append("calendar") or complete("calendar")),
        },
    )
    assert calls == ["calendar"]
    assert result.module("mail").disposition == "blocked"
    assert result.module("calendar").disposition == "complete"
    assert result.required_action is True


def test_dependency_block_prevents_handler_execution():
    calls = []
    result = ReconciliationSweep(MemoryCheckpointStore()).run(
        spec(ModuleSpec("mail"), ModuleSpec("orders", depends_on=("mail",))),
        {
            "mail": lambda ctx: ModuleResult(
                module_id="mail", disposition="blocked", blocker_code="provider_unavailable"
            ),
            "orders": lambda ctx: calls.append("orders"),
        },
    )
    assert calls == []
    assert result.module("orders").blocker_code == "dependency_not_verified"


def test_handler_exception_is_sanitized():
    secret = "synthetic-private-path-/tmp/foo-token"

    def boom(ctx):
        raise RuntimeError(secret)

    result = ReconciliationSweep(MemoryCheckpointStore()).run(
        spec(ModuleSpec("mail")), {"mail": boom}
    )
    payload = str(result.to_payload())
    assert secret not in payload
    assert result.module("mail").blocker_code == "handler_exception"


def test_duplicate_module_ids_rejected_before_execution():
    with pytest.raises(ManifestError):
        spec(ModuleSpec("mail"), ModuleSpec("mail"))


def test_dependency_cycle_rejected():
    with pytest.raises(ManifestError):
        spec(ModuleSpec("a", depends_on=("b",)), ModuleSpec("b", depends_on=("a",)))


def test_missing_dependency_rejected():
    with pytest.raises(ManifestError):
        spec(ModuleSpec("orders", depends_on=("mail",)))


def test_duplicate_mutation_ids_fail_closed():
    mutation = MutationReadback("finance.write", True, True, digest("readback"))
    result = ReconciliationSweep(MemoryCheckpointStore()).run(
        spec(ModuleSpec("finance")),
        {
            "finance": lambda ctx: ModuleResult(
                module_id="finance",
                disposition="complete",
                mutations=(mutation, mutation),
            )
        },
    )
    assert result.module("finance").blocker_code == "module_contract_violation"


def test_negative_counts_fail_closed():
    result = ReconciliationSweep(MemoryCheckpointStore()).run(
        spec(ModuleSpec("finance")),
        {
            "finance": lambda ctx: ModuleResult(
                module_id="finance",
                disposition="complete",
                counts=ReconciliationCounts(updated=-1),
            )
        },
    )
    assert result.module("finance").blocker_code == "module_contract_violation"


def test_completed_run_replay_does_not_rerun_handler():
    store = MemoryCheckpointStore()
    sweep = ReconciliationSweep(store)
    run = spec(ModuleSpec("finance"))
    calls = []

    def handler(ctx):
        calls.append(ctx.previous_cursor)
        return complete("finance")

    first = sweep.run(run, {"finance": handler}, previous_cursors={"finance": "cursor-1"})
    second = sweep.run(run, {"finance": handler}, previous_cursors={"finance": "cursor-x"})
    assert calls == ["cursor-1"]
    assert first.idempotent_replay is False
    assert second.idempotent_replay is True
    assert second.checkpoint_fingerprint == first.checkpoint_fingerprint


def test_same_run_id_with_different_manifest_conflicts():
    store = MemoryCheckpointStore()
    sweep = ReconciliationSweep(store)
    original = spec(ModuleSpec("finance"))
    sweep.run(original, {"finance": lambda ctx: complete("finance")})
    altered = RunSpec(
        run_id=original.run_id,
        local_date=original.local_date,
        timezone=original.timezone,
        slot=original.slot,
        context=original.context,
        modules=(ModuleSpec("mail"),),
    )
    with pytest.raises(CheckpointConflictError):
        sweep.run(altered, {"mail": lambda ctx: complete("mail")})


def test_not_applicable_is_terminal_without_action_required():
    result = ReconciliationSweep(MemoryCheckpointStore()).run(
        spec(ModuleSpec("weather")),
        {"weather": lambda ctx: ModuleResult("weather", "not_applicable")},
    )
    assert result.required_action is False
    assert result.module("weather").disposition == "not_applicable"
    assert result.claim_allowed("weather", "done") is False


def test_optional_blocker_does_not_force_global_action_required():
    result = ReconciliationSweep(MemoryCheckpointStore()).run(
        spec(ModuleSpec("jobs", required=False)),
        {
            "jobs": lambda ctx: ModuleResult(
                module_id="jobs", disposition="blocked", blocker_code="provider_unavailable"
            )
        },
    )
    assert result.required_action is False
    assert result.module("jobs").disposition == "blocked"


def test_previous_cursor_outside_manifest_is_rejected():
    with pytest.raises(ManifestError):
        ReconciliationSweep(MemoryCheckpointStore()).run(
            spec(ModuleSpec("finance")),
            {"finance": lambda ctx: complete("finance")},
            previous_cursors={"mail": "cursor-1"},
        )


def test_verified_mutation_requires_sha256_fingerprint():
    result = ReconciliationSweep(MemoryCheckpointStore()).run(
        spec(ModuleSpec("finance")),
        {
            "finance": lambda ctx: ModuleResult(
                module_id="finance",
                disposition="complete",
                mutations=(
                    MutationReadback(
                        "finance.write",
                        required=True,
                        readback_verified=True,
                        readback_fingerprint="not-a-digest",
                    ),
                ),
            )
        },
    )
    assert result.module("finance").blocker_code == "module_contract_violation"


def test_run_identity_is_deterministic():
    modules = (ModuleSpec("finance"), ModuleSpec("mileage", depends_on=("finance",)))
    a = spec(*modules)
    b = spec(*modules)
    assert a.run_id == b.run_id
    assert a.manifest_fingerprint == b.manifest_fingerprint


def test_manual_run_key_changes_identity():
    a = spec(ModuleSpec("finance"), run_key="manual-1")
    b = spec(ModuleSpec("finance"), run_key="manual-2")
    assert a.run_id != b.run_id
