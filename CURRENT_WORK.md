# MIRA 2.0 CURRENT WORK

Git is authoritative. This file records the completed structured-state packet and exact successor.

## Completed packet

### `M2-G1-001A` — Synthetic structured-state adapter core

- **Work ID:** `STORE-ADAPTER-001A`
- **Merged PR:** #37
- **Merge SHA / main readback:** `a6550d6a44bbe8b02285204e9f475f8caa085d95`
- **Branch:** `impl/g1-001a-structured-state-adapter`
- **Branch start SHA:** `15b8842e9058cf09b5b8294ff10ceac22a3d5422`
- **Implementation head / CI-verified PR head:** `c66deb591f47979e45e819c75a4eca830e390cbd`
- **GitHub Actions run:** `33209577735`
- **Remote verification:** compile succeeded; `python -m unittest discover -s tests -v` succeeded with **11 tests, 0 failures/errors**.
- **Result:** provider-neutral structured-state Protocol, deterministic in-memory synthetic adapter, caller-supplied stable IDs, monotonic revisions, exact readback, bounded query, mandatory idempotency/replay protection, stale-revision conflict handling, append-only event streams and fail-closed validation are implemented/test-verified.
- **Scope proof:** no Google/provider/network/evidence-store/Authority Registry/API/Android behavior or protected legacy production state was touched.

## Selected successor

### `M2-G1-002` — Canonical Authority Registry core

- **Work ID:** `AUTHORITY-REGISTRY-001`
- **Class:** implementation / foundational prerequisite
- **Planned branch:** `impl/g1-002-authority-registry`
- **Dependency satisfied:** `STORE-ADAPTER-001A` is merged and test-verified.
- **Objective:** implement a canonical persisted registry that binds each mutable data class to exactly one active authority and resolves that authority through an explicitly registered structured-state adapter.

### Acceptance criteria

1. Define stable Authority records with caller-supplied Authority IDs and bounded adapter/resource/namespace/failure-domain/owner/schema/verification metadata.
2. Persist Authority records and data-class bindings through `StructuredStateAdapter`; registry has no second mutable backing store.
3. Each mutable data class resolves to exactly one active Authority binding; missing binding fails explicitly.
4. Activating/replacing a binding requires optimistic expected revision and is replay-safe/idempotent.
5. Unknown, disabled, unverified or runtime-unregistered authority/adapter cannot resolve as healthy canonical authority.
6. Registering an Authority never silently activates it for a data class.
7. Runtime adapter registration is explicit and separate from persisted Authority metadata; possessing an adapter object grants no data-class authority by itself.
8. Routing returns the exact Authority metadata plus the registered adapter without exposing provider/database credentials.
9. Deterministic tests prove registration/readback, activation, one-authority routing, replacement conflict, replay, disabled/unverified/unregistered failure and failure isolation.
10. No HTTP/API, Google/provider-specific adapter, cross-person permission, evidence-store or Android work.

## Exact next action

1. Create `impl/g1-002-authority-registry` from this exact main checkpoint.
2. Activate `M2-G1-002` in branch `CURRENT_WORK.md`.
3. Implement the registry over the merged structured-state adapter.
4. Extend tests and existing CI only within packet scope.
5. PR/CI/merge/readback, then advance to `API-CORE-001`.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture unrelated ideas in BACKLOG unless required for acceptance or explicitly reprioritized.
