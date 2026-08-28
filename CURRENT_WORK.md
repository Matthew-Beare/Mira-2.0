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
- **Activation commit:** `188730f279b10eb155915e685abf82c26203d8de`
- **Package export commit:** `5f43f54e1b91ba918d59a9d92e6dcfb932977ecc`
- **Structured-state implementation:** `192f6eaa78d806f35fa6e3b2c671da009a21bf14`
- **Deterministic tests:** `30177b198ed45261df544f80b291e25a0532d8fb`
- **Minimal CI gate:** `8737b7aa849bc21e42e756e498f0a29dbb22dc0e`
- **Status:** implementation complete locally; 11 deterministic unit tests pass; remote PR CI and final evidence normalization next.

## Implemented component

Component: **structured-state**

Owned production surface:
- `mira/structured_state.py` — provider-neutral structured mutable-state contract, deterministic in-memory adapter, contract errors/types.
- `mira/__init__.py` — package export surface for this component.

Direct verification:
- `tests/test_structured_state.py`
- `.github/workflows/ci.yml` compiles `mira`/`tests` and runs stdlib `unittest` on Python 3.12.

No third-party runtime dependencies were introduced.

## Implemented semantics

- explicit health/schema contract with declared resource/event types;
- exact read with defensive readback copies;
- bounded deterministic query with exact payload filters and hard limit bounds;
- caller-supplied stable canonical resource/event IDs;
- monotonic resource revisions and event stream revisions;
- mandatory mutation idempotency keys;
- exact replay returns prior result without another mutation;
- material idempotency-key reuse fails closed;
- optimistic stale-revision mutation fails without changing state;
- duplicate event identity fails closed;
- append-only ordered event-stream readback;
- invalid/unknown resource/event types and non-JSON payloads fail explicitly.

## Verification evidence

Local deterministic run against the exact committed implementation/test content:
- command: `python -m unittest discover -s tests -v`
- result: **11 tests passed, 0 failures/errors**.

Remote GitHub CI is not yet evidence until a PR-triggered run succeeds.

## Acceptance criteria

1. Bounded interface for health/schema, exact read, bounded query, idempotent upsert and append-event behavior. **Implemented/local-test-verified.**
2. Stable caller-supplied canonical IDs; replay never invents competing identities. **Implemented/local-test-verified.**
3. Monotonic revisions and exact material readback after mutation. **Implemented/local-test-verified.**
4. Same idempotency key + same material request returns prior result without another mutation. **Implemented/local-test-verified.**
5. Same idempotency key + different material request fails closed. **Implemented/local-test-verified.**
6. Stale expected revision fails explicitly and leaves state unchanged. **Implemented/local-test-verified.**
7. Invalid/unknown resource or envelope fails explicitly. **Implemented/local-test-verified.**
8. Deterministic tests cover create/read/query/update/replay/conflict/append-event/readback. **11 tests pass locally.**
9. No Google/provider/network/evidence-store work, credentials or legacy production state. **Satisfied.**
10. Bounded production ownership and tests; one coherent PR. **Component/test ownership recorded; PR pending.**

## Scope guard

No Authority Registry, HTTP/API, Google/SQL provider, evidence-store, Android, credential or legacy-production behavior was added.

## Exact next action

1. Compare branch to `main` and verify only packet-scoped product/test/CI/current-work files changed.
2. Open bounded implementation PR at the exact head.
3. Verify PR file list and PR-triggered CI.
4. If CI passes, update `BACKLOG.md` and this file with remote test evidence and next packet selection.
5. Merge exact verified head/read back `main`.
6. Activate `AUTHORITY-REGISTRY-001` as the next dependency-ranked implementation packet.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture unrelated ideas in BACKLOG unless required for acceptance or explicitly reprioritized.
