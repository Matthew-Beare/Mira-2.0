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
- **Current status:** implementation, replay hardening and adversarial synthetic tests complete on branch; PR #139 remains draft; CI #526 passed end-to-end on hardened implementation head `8916fd5476ffc85c8f97e6ef9c50ac21b4024964`; documentation closeout requires one final exact-head CI before merge.

## Objective

Add a provider-neutral, STORE-001-backed durable compute-job control plane by extending the existing canonical queue/sequencer boundary rather than creating a duplicate scheduler. Jobs must support stable identity, secret-free task requirements, deterministic priority, bounded attempts, worker leases, replay-safe state transitions, cancellation, pause/preempt/resume checkpoints, lease-expiry recovery and exact result provenance.

This packet does not execute jobs, authenticate workers, expose network/raw shell/Python/inference services, choose or bind private machines, control power, load models, invent hardware thresholds, run self-hosted CI or claim live worker evidence.

## Acceptance state

- M2-M1-021 routing foundation: **merged + post-merge CI verified**.
- M2-M1-022 worker identity/advertisement contract: **merged + post-merge CI verified**.
- M2-M1-023 durable worker registry: **merged at `9d7dc7b392e389b3bbcd746fd2b52d61bd8f149a`; post-merge CI #521 PASS**.
- M2-M1-024 ID/branch collision check: **complete; no prior PR or branch existed**.
- Current concurrent PR review: **#134 and #135 remain open drafts and are now non-mergeable against newer main; this packet does not overlap their files**.
- Existing shared queue/sequencer inspection: **complete; `mira/command_sequencer.py` reused rather than creating a duplicate scheduler**.
- Durable compute-job implementation: **complete on branch**.
- Synthetic lifecycle/lease/retry/cancel/preempt/resume/provenance tests: **complete on branch**.
- Active-lease identity collision hardening + regression test: **complete on branch**.
- STORE-001 test-harness correction: **complete; empty event registry replaced with valid synthetic event type**.
- Transition replay hardening: **complete; durable SHA-256 receipt hashes bind idempotency identity to canonical transition material without persisting raw keys**.
- Adversarial replay coverage: **complete; lease capability material, pause/cancel timestamps, cancellation acknowledgement and fail-after-requeue exact retry are covered**.
- CI #522: **failed only at work-session alignment; authority headings corrected**.
- CI #523: **reached Python tests and exposed the invalid synthetic STORE-001 event registry**.
- CI #524: **PASS end-to-end after harness correction**.
- CI #526 on hardened implementation head `8916fd5476ffc85c8f97e6ef9c50ac21b4024964`: **PASS end-to-end, including Python adversarial replay tests and all repository gates**.
- Documentation closeout exact-head CI: **pending**.
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

PR #134 changes People Discovery and `project/code_ownership.json`. PR #135 changes Sheets plus ownership-fragment machinery. Both remain draft and currently non-mergeable against newer main. M2-M1-024 does not modify their paths and reuses an already-owned production module.

### Direction result

ALIGNED

## Exact next action / resume point

1. Run final exact-head CI after this documentation closeout and packet evidence update.
2. Re-read remote `main`, PR #139 head/mergeability and changed-file overlap.
3. Mark PR #139 ready and merge only if exact-head CI is green, using expected-head protection.
4. Read back merged `main` and verify post-merge CI before claiming integration verification.
5. After M2-M1-024 closes, select the next dependency-ranked compute-fabric child packet from current Git state rather than chat history.

## Recovery protocol

Resume from current remote `main`, this branch's `CURRENT_WORK.md`, `docs/work-packets/M2-M1-024.md`, PR #139, the branch head and concurrent PRs. Do not reopen M2-M1-021 through M2-M1-023 unless regression evidence requires it.
