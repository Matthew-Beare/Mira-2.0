import pytest

from mira.structured_state import InMemoryStructuredStateAdapter
from ops.reconciliation_checkpoint_store import StructuredCheckpointStore
from ops.reconciliation_sweep import (
    ModuleResult,
    ModuleSpec,
    ReconciliationError,
    ReconciliationSweep,
    RunSpec,
)


def adapter():
    return InMemoryStructuredStateAdapter(
        schema_version="v1",
        resource_types=("reconciliation_run",),
        event_types=("noop",),
    )


def test_structured_checkpoint_survives_new_sweep_instance_and_replays():
    state = adapter()
    spec = RunSpec.build(
        local_date="2026-09-13",
        timezone="America/New_York",
        slot="am",
        modules=(ModuleSpec("finance"),),
    )
    calls = []
    first = ReconciliationSweep(StructuredCheckpointStore(state)).run(
        spec,
        {"finance": lambda ctx: (calls.append(1) or ModuleResult("finance", "complete"))},
    )
    second = ReconciliationSweep(StructuredCheckpointStore(state)).run(
        spec,
        {"finance": lambda ctx: (calls.append(2) or ModuleResult("finance", "complete"))},
    )
    assert calls == [1]
    assert second.idempotent_replay is True
    assert second.checkpoint_fingerprint == first.checkpoint_fingerprint


def test_structured_checkpoint_payload_tamper_fails_readback():
    state = adapter()
    store = StructuredCheckpointStore(state)
    spec = RunSpec.build(
        local_date="2026-09-13",
        timezone="America/New_York",
        slot="pm",
        modules=(ModuleSpec("finance"),),
    )
    ReconciliationSweep(store).run(
        spec, {"finance": lambda ctx: ModuleResult("finance", "complete")}
    )
    record = state.get("reconciliation_run", spec.run_id)
    corrupt = dict(record.payload)
    corrupt["required_action"] = True
    state.upsert(
        "reconciliation_run",
        spec.run_id,
        corrupt,
        idempotency_key="synthetic-tamper",
        expected_revision=record.revision,
    )
    with pytest.raises(ReconciliationError):
        StructuredCheckpointStore(state).get(spec.run_id)
