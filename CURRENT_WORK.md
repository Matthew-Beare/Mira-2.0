# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active implementation packet and its resume point.

## Completed packet before this branch

### `M2-G0-010` — Final dependency graph and implementation ranking closeout

- **Merged PR:** #36
- **Merge SHA / main readback:** `a7d3e947ac71803c3c19777668c0ea79d844463f`
- **Post-merge completion checkpoint / this branch start SHA:** `15b8842e9058cf09b5b8294ff10ceac22a3d5422`
- **Result:** G0 is complete; M2-M0/M2-M1 critical path is acyclic and ranked.

## Active packet

### `M2-G1-001A` — Synthetic structured-state adapter core

- **Work ID:** `STORE-ADAPTER-001A`
- **Class:** implementation / foundational prerequisite
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `impl/g1-001a-structured-state-adapter`
- **Branch start SHA:** `15b8842e9058cf09b5b8294ff10ceac22a3d5422`
- **Status:** activated; repository layout inspection and implementation next.

## Objective

Implement the provider-neutral structured-state contract and deterministic in-memory synthetic adapter used by later Authority Registry and API work. This packet deliberately excludes Google/provider/network/evidence-store behavior.

## Acceptance criteria

1. Bounded interface for health/schema, exact read, bounded query, idempotent upsert and append-event behavior.
2. Stable caller-supplied canonical IDs; replay never invents competing identities.
3. Monotonic revisions and exact material readback after mutation.
4. Same idempotency key + same material request returns the prior result without another mutation.
5. Same idempotency key + different material request fails closed.
6. Stale expected revision fails explicitly and leaves state unchanged.
7. Invalid/unknown resource or envelope fails explicitly rather than permissively writing arbitrary state.
8. Deterministic tests cover create/read/query/update/replay/conflict/append-event/readback.
9. No Google/provider/network/evidence-store work, credentials or legacy production state.
10. Bounded production ownership and tests; one coherent PR.

## Scope guard

Allowed:
- structured-state interface/types/errors;
- deterministic in-memory adapter;
- synthetic tests;
- minimal packaging/test configuration required to run those tests;
- packet evidence updates.

Excluded:
- Authority Registry implementation;
- HTTP/FastAPI/API runtime;
- Google/SQL/provider adapters;
- evidence/document storage;
- Android code;
- legacy production data or credentials.

## Exact next action

1. Inspect repository directories, Python/test conventions and baseline CI configuration.
2. Choose the smallest coherent module/test paths.
3. Implement the interface, errors and in-memory adapter.
4. Add deterministic tests for every acceptance behavior.
5. Run applicable repository tests/gates; fix failures without expanding scope.
6. Record evidence in BACKLOG/CURRENT_WORK and bounded PR/merge/readback.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture unrelated ideas in BACKLOG unless required for acceptance or explicitly reprioritized.
