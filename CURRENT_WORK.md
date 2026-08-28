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
- **Status:** activated; integration proof next.

## Objective

Prove the assembled MIRA 2.0 stack end-to-end without external provider state: separate synthetic registry and canonical data stores, Authority Registry, API service, scoped session auth and WSGI HTTP transport must create, read, update, replay and reject conflicting mutation for one canonical entity with exact readback and audit evidence.

## Acceptance criteria

1. Distinct registry/canonical stores, one verified Authority, one explicit data-class binding.
2. HTTPS command creates canonical entity through full WSGI/API/registry/adapter stack.
3. HTTPS query reads the same entity.
4. Expected-revision update mutates same entity and increments revision once.
5. Exact replay returns replay=true without another revision increment.
6. Same idempotency key + different material input returns 409 with no state change.
7. Stale expected revision returns 409 with no state change.
8. Missing/invalid bearer cannot mutate state.
9. Audit identifies exact actor/client/action/resource/outcome/Authority for successful and failed authorized requests.
10. Direct canonical-store readback exactly equals final HTTP representation.
11. Full repository CI passes.
12. No Google/provider/deployment/Android/evidence-store/legacy production state.

## Exact next action

1. Add a single integration test file using real merged layers.
2. Verify the complete create/read/update/replay/conflict/readback sequence plus auth isolation/audit.
3. Open bounded PR and require full GitHub CI green.
4. Merge/read back main.
5. Then activate early repository growth gates before provider/client fan-out.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture unrelated ideas in BACKLOG unless required for acceptance or explicitly reprioritized.
