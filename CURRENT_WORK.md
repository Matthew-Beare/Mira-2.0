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
- **Owned implementation surfaces:** `mira/service_state.py`, `mira/runtime_router.py`, `tests/test_compute_worker_registry.py`, packet doc, this branch's `CURRENT_WORK.md`.
- **Shared/high-contention surfaces:** none modified. PR #134 changes the monolithic ownership manifest; PR #135 changes ownership-fragment machinery and Sheets surfaces. This packet reuses already-owned production modules.
- **Current status:** active; exact verified base and bounded persistence objective recorded. Implementation pending.

## Objective

Persist secret-free worker registration and heartbeat state over STORE-001-compatible structured state with replay-safe mutations, optimistic revisions, exact readback, immutable principal binding and deterministic query semantics. Feed validated durable worker state into the M2-M1-022 projection contract without turning the registry into an authentication provider, provider-capability authority, scheduler, network listener or power controller.

## Acceptance state

- M2-M1-021 routing foundation: **merged + post-merge CI verified**.
- M2-M1-022 worker evidence/projection contract: **merged at `36cfc28d128c46078fa1bb082e32695a23e7f64a`; post-merge CI #517 PASS end-to-end**.
- Concurrent overlap check against PR #134 / #135: **complete**.
- M2-M1-023 branch: **created from exact verified main**.
- Dedicated STORE-001 compute-worker resource: **pending**.
- Replay-safe registration and exact readback: **pending**.
- Principal-bound heartbeat/update with optimistic revisions: **pending**.
- Deterministic query/list: **pending**.
- Runtime-router durable-view projection: **pending**.
- Exact-head CI: **pending**.
- Live worker/network/provider/private deployment evidence: **not claimed**.

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

1. Extend `mira/service_state.py` with a dedicated compute-worker resource/service without importing `runtime_router`.
2. Add a runtime-router conversion from validated registry view to the existing worker-advertisement projection contract.
3. Add deterministic synthetic STORE-001 tests in `tests/test_compute_worker_registry.py`.
4. Open a draft PR and obtain exact-head CI.
5. Reconcile current `main` and concurrent PRs before merge.

## Recovery protocol

Resume from this file plus `docs/work-packets/M2-M1-023.md`, exact remote branch head and active PR state. M2-M1-021 and M2-M1-022 are complete and merged; do not reopen them unless regression evidence requires it.
