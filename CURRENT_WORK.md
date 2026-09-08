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
- **Current status:** implementation and synthetic tests complete on branch; PR #139 draft; CI #522 failed only at work-session alignment because the three authority reviews were collapsed under one heading; metadata corrected here.

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
- Durable compute-job implementation: **complete on branch**.
- Synthetic lifecycle/lease/retry/cancel/preempt/resume/provenance tests: **complete on branch**.
- Active-lease identity collision hardening + regression test: **complete on branch**.
- CI #522 on `9fb435c954c694f5202aaf4c444c2bdef5bcbcdc`: **compile, feature registry, lifecycle and starter distribution passed; work-session alignment failed because this document used a combined authority heading; corrected without product-code change**.
- Exact-head CI after metadata correction: **pending**.
- Merge/post-merge CI: **pending**.
- Live worker/network/model/private deployment evidence: **not claimed and out of scope**.

## Session-start alignment verification — 2026-09-08

### `FEATURES.md`

Reviewed from verified main. `LOCAL-001` and `PROVIDER-001` remain the primary capability/policy anchors; `STORE-001`, `RECOVERY-002`, `API-001` and `DEV-004` remain supporting invariants. The packet adds no second product authority, provider-specific scheduler, or mandatory local-compute dependency.

### `BACKLOG.md`

Reviewed from verified main. `LOCAL-INTEGRATIONS` remains the existing registered work anchor explicitly reprioritized by the product owner for the compute-fabric initiative. This packet continues that registered work instead of inventing an unrelated queue or backlog identity.

### `ROADMAP.md`

Reviewed from verified main. Advanced/self-hosted compute remains optional and downstream of the ordinary Personal baseline. The durable control plane is provider-neutral shared infrastructure and does not make private hardware, local AI, or Advanced onboarding a Standard-path prerequisite.

### Reuse review

`mira/command_sequencer.py` already defines the canonical provider-neutral queued execution boundary with stable command identity, serialization, replay/idempotency behavior and crash-before-acknowledgement recovery. M2-M1-024 extends this shared control-plane surface for durable compute jobs rather than creating a second queue authority.

### Collision/concurrency review

PR #134 changes People Discovery and `project/code_ownership.json`. PR #135 changes Sheets plus ownership-fragment machinery. M2-M1-024 does not modify those paths and reuses an already-owned production module.

### Direction result

ALIGNED

## Exact next action / resume point

1. Run exact-head CI after the authority-heading metadata correction.
2. If CI reaches product tests, fix only concrete failures on this bounded packet.
3. Review final diff and reconcile current remote `main` plus active PR overlap.
4. Mark PR #139 ready and merge only with exact-head green CI using expected-head protection.
5. Read back merged `main` and post-merge CI before claiming integration verification.

## Recovery protocol

Resume from current remote `main`, this branch's `CURRENT_WORK.md`, `docs/work-packets/M2-M1-024.md`, PR #139, the branch head and concurrent PRs. Do not reopen M2-M1-021 through M2-M1-023 unless regression evidence requires it.
