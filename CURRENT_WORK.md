# MIRA 2.0 CURRENT WORK

Git is authoritative. This branch records exactly one active packet. Multiple other packet branches may be active repository-wide at the same time under `docs/CONCURRENT_WORK_POLICY.md`.

## Active packet

### `M2-M1-023` — Durable compute worker registry

- **Primary work:** `LOCAL-INTEGRATIONS`.
- **Primary features:** `LOCAL-001`, `PROVIDER-001`.
- **Related invariants/features:** `STORE-001`, `SOURCE-001`, `RECOVERY-002`, `DEV-004`, `API-001`.
- **Repository:** `Matthew-Beare/Mira-2.0`.
- **Branch:** `work/m2-m1-023-durable-worker-registry`.
- **Base SHA:** `36cfc28d128c46078fa1bb082e32695a23e7f64a`.
- **Packet:** `docs/work-packets/M2-M1-023.md`.
- **PR:** `#138`.
- **Owned implementation surfaces:** `mira/service_state.py`, `mira/runtime_router.py`, `tests/test_compute_worker_registry.py`, packet doc, this branch's `CURRENT_WORK.md`.
- **Shared/high-contention surfaces:** none modified. PR #134 changes the monolithic ownership manifest; PR #135 changes ownership-fragment machinery and Sheets surfaces. This packet reuses already-owned production modules.
- **Current status:** implementation complete on branch; CI #518 passed end-to-end on `61ebe9b597cadd7bc71304d5f994409dc6fd7b2e`. This closeout checkpoint changes the head and therefore requires one final exact-head CI before merge.

## Objective

Persist secret-free worker registration and heartbeat state over STORE-001-compatible structured state with replay-safe mutations, optimistic revisions, exact readback, immutable principal binding and deterministic query semantics. Feed validated durable worker state into the M2-M1-022 projection contract without turning the registry into an authentication provider, provider-capability authority, scheduler, network listener or power controller.

## Acceptance state

- M2-M1-021 routing foundation: **merged + post-merge CI verified**.
- M2-M1-022 worker evidence/projection contract: **merged at `36cfc28d128c46078fa1bb082e32695a23e7f64a`; post-merge CI #517 PASS end-to-end**.
- Concurrent overlap check against PR #134 / #135: **complete at packet start; final reconciliation still required before merge**.
- M2-M1-023 branch: **created from exact verified main**.
- Dedicated STORE-001 `compute_worker` resource/schema: **implemented**.
- Replay-safe registration and exact readback: **implemented + test-verified**.
- Principal-bound heartbeat/update with optimistic revisions: **implemented + test-verified**.
- Exact heartbeat retry: **replay-safe no-op/readback implemented after review found that recomputing the newer expected revision would otherwise change the STORE-001 idempotency fingerprint**.
- Reused heartbeat idempotency key with changed material: **fails closed through STORE-001; test-verified**.
- Immutable principal binding and verified-identity-only persistence: **implemented + test-verified**.
- Monotonic identity/heartbeat chronology: **implemented + test-verified**.
- Deterministic query/list ordering: **implemented + test-verified**.
- Strict secret-free persisted schema: **implemented + test-verified; unsupported/private extra fields fail readback validation**.
- Runtime-router durable-view projection: **implemented + test-verified via `worker_registry_view_to_advertisement`**.
- Provider capability authority separation: **preserved; externally supplied `ProviderCapabilitySnapshot` remains required**.
- Stale durable heartbeat fail-closed behavior: **test-verified through existing projection/router path**.
- CI #518 on `61ebe9b597cadd7bc71304d5f994409dc6fd7b2e`: **PASS end-to-end: compile, feature registry, lifecycle, starter distribution, work-session alignment, code ownership, Android proof/provenance/retention, Python unit tests and Workspace Apps Script tests**.
- Final exact-head CI after this documentation checkpoint: **pending**.
- Current-main reconciliation / PR #138 merge/readback: **pending final exact-head green**.
- Live worker/network/provider/private deployment evidence: **not claimed and out of scope**.

## Session-start alignment verification — 2026-09-08

### `FEATURES.md`

Reviewed from verified `main` `36cfc28d128c46078fa1bb082e32695a23e7f64a`. `LOCAL-001`, `PROVIDER-001`, `STORE-001`, `SOURCE-001`, `RECOVERY-002`, `DEV-004` and `API-001` support durable, provider-neutral, evidence-first and sanitizable worker state.

### `BACKLOG.md`

Reviewed. `LOCAL-INTEGRATIONS` remains the registered work anchor for the explicitly reprioritized local-compute direction.

### `ROADMAP.md`

Reviewed. Advanced/local compute remains optional and must not become an ordinary Personal prerequisite.

### Collision/concurrency review

PR #134 owns People Discovery plus `project/code_ownership.json`. PR #135 owns Sheets plus code-ownership validator/fragment changes. M2-M1-023 avoids those files by implementing the registry inside the already-owned service-state boundary and adding only a router conversion in the already-owned runtime-router boundary.

### Direction result

ALIGNED

## Exact next action / resume point

1. Update `docs/work-packets/M2-M1-023.md` with the implementation/CI evidence from head `61ebe9b597cadd7bc71304d5f994409dc6fd7b2e`.
2. Obtain one final exact-head CI for the documentation closeout head.
3. Re-read current remote `main`, PR #138 head/mergeability, and active overlapping PRs.
4. If the final head remains non-destructive and CI is green, mark PR #138 ready and merge using the exact expected head SHA.
5. Read back merged `main` and post-merge CI. Record the evidence ceiling as durable registry implementation/integration verified only; do not claim live worker transport, queue, power control, model runtime or private deployment.
6. Select the next compute-fabric child packet by dependency/integrity ranking from the M2-M1-021 decomposition.

## Recovery protocol

Resume from this file plus `docs/work-packets/M2-M1-023.md`, exact remote branch head, PR #138 and active PR state. M2-M1-021 and M2-M1-022 are complete and merged; do not reopen them unless regression evidence requires it.
