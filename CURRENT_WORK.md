# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active verification packet and its resume point.

## Completed packet before this branch

### `M2-G1-003B` — Scoped client authentication and HTTP transport

- **Merged PR:** #40
- **Merge SHA / main readback:** `247de3c0e30415f93c7bba65d141ca17f706571f`
- **Post-merge completion checkpoint / this branch start SHA:** `e32d7ee0093aedf70dcec7ca87746a6c726c35e0`
- **Remote CI:** GitHub Actions run `33210581967`; compile + full unit suite passed.
- **Result:** `API-CORE-001A` + `API-CORE-001B` are implemented/test-verified; `API-CORE-001` is complete for the synthetic same-user boundary.

## Active packet

### `M2-G1-004` — Synthetic HTTP roundtrip integration proof

- **Work ID:** `CORE-SYNTHETIC-ROUNDTRIP`
- **Class:** integration verification / prerequisite
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `verify/g1-004-synthetic-roundtrip`
- **Branch start SHA:** `e32d7ee0093aedf70dcec7ca87746a6c726c35e0`
- **Activation commit:** `5d00a353d76f5cd87f745a8baf906ff30a8457de`
- **Integration proof commit:** `c09f63c88b04d133b3088fc55534b3d137282410`
- **Status:** real-layer integration proof committed; bounded PR and full remote CI next.

## Integration proof content

`tests/test_synthetic_roundtrip.py` assembles the actual merged layers:
- distinct in-memory registry store;
- distinct canonical entity store;
- real `AuthorityRegistry` with one verified Authority and explicit `entity` binding;
- real `ApiService` and audit sink;
- real scoped `InMemorySessionStore` bearer credential;
- real `WsgiApiApp` HTTPS request boundary.

The test executes through HTTP rather than calling the canonical adapter directly for mutations.

## Proof sequence

1. Unauthenticated create returns 401 and canonical state/audit remain empty.
2. Authenticated HTTP create returns exact Authority, revision 1 and verified readback.
3. HTTP query returns that same canonical record.
4. Expected-revision HTTP update mutates the same identity to revision 2.
5. Exact replay of the update returns `idempotent_replay=true` and canonical revision remains 2.
6. Same replay key with changed material input returns 409 and state remains revision 2/Beta.
7. Separate stale-revision command returns 409 and state remains unchanged.
8. Final HTTP query exactly equals direct canonical-store dataclass readback.
9. Audit rows for successful and failed authorized mutations carry exact actor/client/resource/Authority and stable outcomes/error codes.
10. Invalid bearer cannot create state or service audit records.

## Acceptance criteria status before CI

1. Distinct registry/canonical stores + explicit Authority binding. **Implemented.**
2. Full HTTPS create. **Test-covered.**
3. Full HTTPS read. **Test-covered.**
4. Same-identity expected-revision update. **Test-covered.**
5. Replay does not increment revision. **Test-covered.**
6. Material idempotency conflict leaves state unchanged. **Test-covered.**
7. Stale revision leaves state unchanged. **Test-covered.**
8. Invalid bearer cannot mutate. **Test-covered.**
9. Exact audit evidence. **Test-covered.**
10. Direct canonical readback equals HTTP representation. **Test-covered.**
11. Full repository CI. **Pending.**
12. No provider/deployment/Google/Android/evidence/legacy state. **Satisfied.**

## Exact next action

1. Compare branch to `main`; expected changed files are only `CURRENT_WORK.md` and `tests/test_synthetic_roundtrip.py`.
2. Open bounded verification PR and verify exact file list.
3. Require full PR-triggered CI green.
4. Merge exact verified head/read back `main`.
5. Checkpoint `CORE-SYNTHETIC-ROUNDTRIP` integration verification.
6. Activate early repository growth gates before provider/client fan-out.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture unrelated ideas in BACKLOG unless required for acceptance or explicitly reprioritized.
