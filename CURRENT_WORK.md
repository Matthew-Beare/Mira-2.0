# MIRA 2.0 CURRENT WORK

Git is authoritative. This branch records exactly one active packet. Multiple other packet branches may be active repository-wide at the same time under `docs/CONCURRENT_WORK_POLICY.md`.

## Active packet

### `M2-M1-024` — Durable compute control plane

- **Primary work:** `LOCAL-INTEGRATIONS`.
- **Primary features:** `LOCAL-001`, `PROVIDER-001`.
- **Related invariants/features:** `STORE-001`, `RECOVERY-002`, `API-001`, `DEV-004`.
- **Repository:** `Matthew-Beare/Mira-2.0`.
- **Branch:** `work/m2-m1-024-durable-compute-control-plane`.
- **Base SHA:** `9d7dc7b392e389b3bbcd746fd2b52d61bd8f149a`.
- **Packet:** `docs/work-packets/M2-M1-024.md`.
- **Owned implementation surfaces:** `mira/command_sequencer.py`, `tests/test_compute_control_plane.py`, packet doc, this branch's `CURRENT_WORK.md`.
- **Shared/high-contention surfaces:** none modified. PR #134 owns People Discovery plus the monolithic ownership manifest; PR #135 owns Sheets and ownership-fragment machinery.
- **Current status:** packet active; implementation in progress.

## Objective

Add a provider-neutral, STORE-001-backed durable compute-job control plane by extending the existing canonical queue/sequencer boundary rather than creating a duplicate scheduler. Jobs must support stable identity, secret-free task requirements, deterministic priority, bounded attempts, worker leases, replay-safe state transitions, cancellation, pause/preempt/resume checkpoints, lease-expiry recovery and exact result provenance.

This packet does not execute jobs, authenticate workers, expose network/raw shell/Python/inference services, choose or bind private machines, control power, load models, invent hardware thresholds, run self-hosted CI or claim live worker evidence.

## Acceptance state

- M2-M1-021 routing foundation: **merged + post-merge CI verified**.
- M2-M1-022 worker identity/advertisement contract: **merged + post-merge CI verified**.
- M2-M1-023 durable worker registry: **merged at `9d7dc7b392e389b3bbcd746fd2b52d61bd8f149a`; post-merge CI #521 PASS**.
- M2-M1-024 ID/branch collision check: **complete; no prior PR or branch exists**.
- Current concurrent PR review: **#134 and #135 remain open; this packet avoids their files**.
- Existing shared queue/sequencer inspection: **complete; `mira/command_sequencer.py` selected for reuse**.
- Durable compute-job implementation: **in progress**.
- Synthetic lifecycle/lease/retry/cancel/preempt/resume/provenance tests: **pending**.
- Exact-head CI: **pending**.
- Merge/post-merge CI: **pending**.
- Live worker/network/model/private deployment evidence: **not claimed and out of scope**.

## Session-start alignment verification — 2026-09-08

### `FEATURES.md` / `BACKLOG.md` / `ROADMAP.md`

Prior compute-fabric packets verified `LOCAL-001`, `PROVIDER-001`, `STORE-001`, `RECOVERY-002`, `API-001` and `DEV-004` as the existing policy/authority anchors. `LOCAL-INTEGRATIONS` remains the explicitly reprioritized registered work anchor. Advanced/local compute remains optional and cannot become a Standard-path prerequisite.

### Reuse review

`mira/command_sequencer.py` already defines the canonical provider-neutral queued execution boundary with stable command identity, serialization, replay/idempotency behavior and crash-before-acknowledgement recovery. M2-M1-024 extends this shared control-plane surface for durable compute jobs rather than creating a second queue authority.

### Collision/concurrency review

PR #134 changes People Discovery and `project/code_ownership.json`. PR #135 changes Sheets plus ownership-fragment machinery. M2-M1-024 does not modify those paths and reuses an already-owned production module.

### Direction result

ALIGNED

## Exact next action / resume point

1. Implement the durable compute-job state machine in `mira/command_sequencer.py` without changing existing serialized API-command semantics.
2. Add deterministic synthetic tests in `tests/test_compute_control_plane.py`.
3. Open a draft PR and run exact-head CI.
4. Review any CI or semantic failures, fix them on the same bounded packet, then reconcile current `main` and active PR overlap before merge.
5. Merge only with exact-head green CI and read back post-merge `main`/CI.

## Recovery protocol

Resume from current remote `main`, this branch's `CURRENT_WORK.md`, `docs/work-packets/M2-M1-024.md`, the branch head and any open PR created for this packet. Do not reopen M2-M1-021 through M2-M1-023 unless regression evidence requires it.
