# MIRA 2.0 CURRENT WORK

Git is authoritative. This branch records exactly one active packet. Multiple other packet branches may be active repository-wide at the same time under `docs/CONCURRENT_WORK_POLICY.md`.

## Active packet

### `M2-M1-022` — Compute worker advertisement and identity-proof contract

- **Primary work:** `LOCAL-INTEGRATIONS`.
- **Primary features:** `LOCAL-001`, `PROVIDER-001`.
- **Related invariants/features:** `SOURCE-001`, `RECOVERY-002`, `DEV-004`, `API-001`.
- **Repository:** `Matthew-Beare/Mira-2.0`.
- **Branch:** `work/m2-m1-022-compute-worker-registry`.
- **Base SHA:** `0e1a1ef2d8565beacbdb8e13e8f73c97bc3d43a5`.
- **Packet:** `docs/work-packets/M2-M1-022.md`.
- **Owned implementation surfaces:** `mira/runtime_router.py`, `tests/test_compute_worker_contract.py`, packet doc, this branch's `CURRENT_WORK.md`.
- **Shared/high-contention surfaces:** none modified. PR #134 changes `project/code_ownership.json`; PR #135 changes the ownership validator/fragments and Sheets surfaces. This packet avoids those files.
- **Current status:** active; packet and collision-aware split are recorded. Implementation pending.

## Objective

Add the secret-free worker advertisement, verified identity-proof, heartbeat freshness and runtime-candidate projection contract that the merged M2-M1-021 router needs before a durable worker registry can safely exist.

The packet remains read-only and provider-neutral. It does not persist worker state, perform authentication transport, deploy an agent, expose raw inference/Python/shell, wake/shutdown machines, invent hardware thresholds, or bind private infrastructure.

## Acceptance state

- M2-M1-021 merged to `main`: **verified at `0e1a1ef2d8565beacbdb8e13e8f73c97bc3d43a5`**.
- M2-M1-021 post-merge CI #511: **PASS end-to-end**.
- Concurrent overlap check against PR #134 / #135: **complete**.
- New bounded packet branch: **created from exact verified main**.
- Worker advertisement/identity-proof contract: **pending**.
- Heartbeat freshness fail-closed projection: **pending**.
- Deterministic tests: **pending**.
- Exact-head CI: **pending**.
- Durable STORE-001 worker registry: **not claimed; next child packet**.
- Live worker/provider/device evidence: **not claimed**.

## Session-start alignment verification — 2026-09-08

### `FEATURES.md`

Reviewed from verified `main`. `LOCAL-001` and `PROVIDER-001` require scoped, provider-neutral local/runtime capability behavior; `SOURCE-001`, `RECOVERY-002`, `DEV-004` and `API-001` preserve evidence, recovery, sanitization and bounded-interface constraints.

### `BACKLOG.md`

Reviewed. `LOCAL-INTEGRATIONS` remains the registered work anchor for the product-owner-reprioritized local-compute direction. This packet does not invent an unregistered work item.

### `ROADMAP.md`

Reviewed. Advanced/local compute remains optional and must not become a prerequisite for ordinary Personal MIRA.

### Collision/concurrency review

PR #134 changes People Discovery and the monolithic code-ownership manifest. PR #135 changes Sheets surfaces, the code-ownership validator and ownership fragments. M2-M1-022 avoids all of those paths by extending the already-owned runtime-routing component only.

### Direction result

ALIGNED

## Exact next action / resume point

1. Implement verified identity-proof, worker advertisement and freshness projection in `mira/runtime_router.py`.
2. Add deterministic synthetic tests in `tests/test_compute_worker_contract.py`.
3. Open draft PR and obtain exact-head CI.
4. Re-read `main` and active PRs before merge.

## Recovery protocol

Resume from this file plus `docs/work-packets/M2-M1-022.md`, exact remote branch head and active PR state. M2-M1-021 is complete and merged; do not reopen it unless regression evidence requires it.
