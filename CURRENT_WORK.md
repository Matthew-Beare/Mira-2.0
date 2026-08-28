# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active implementation packet and its resume point.

## Completed packet before this branch

### `M2-G1-002` — Canonical Authority Registry core

- **Merged PR:** #38
- **Merge SHA / main readback:** `a453e54c437a697daa592e51f336a9604dffd8e2`
- **Post-merge completion checkpoint / this branch start SHA:** `1d4d0108408e76a34a1dea4dcef0cb690e5dd96c`
- **Remote CI:** GitHub Actions run `33209898891`; compile + 19 unit tests passed.
- **Result:** `AUTHORITY-REGISTRY-001` is implemented/test-verified.

## Active packet

### `M2-G1-003A` — API service semantics core

- **Work ID:** `API-CORE-001A`
- **Class:** implementation / security-data-integrity prerequisite
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `impl/g1-003a-api-service-core`
- **Branch start SHA:** `1d4d0108408e76a34a1dea4dcef0cb690e5dd96c`
- **Activation commit:** `68628614057c7e779d3968296e737581e76ea979`
- **Service implementation:** `60ebbef6c3489af52676a6a1b4fbf19d2621e425`
- **Deterministic API tests:** `705412977e7c1e9c67147516a84406173c885c10`
- **Package exports:** `50d325d18dfab0945082e02850969d89133093d2`
- **Status:** implementation/test content complete; local full-suite evidence is 30 tests green; bounded PR/remote CI next.

## API umbrella split

`API-CORE-001` remains an umbrella:
1. `API-CORE-001A` — transport-independent service semantics (this packet).
2. `API-CORE-001B` — scoped client/session authentication + HTTP transport (next after 001A).

The umbrella is complete only when both are verified.

## Implemented component

Component: **api-service-core**

Owned production surface:
- `mira/api_core.py` — principal/grant contract, versioned envelopes/results/errors, authorization/preflight, Authority Registry routing, canonical read/write/readback, audit.
- `mira/__init__.py` — package exports.

Direct verification:
- `tests/test_api_core.py` plus existing structured-state and Authority Registry tests.
- existing `.github/workflows/ci.yml` compiles `mira`/`tests` and runs the full stdlib unit suite.

## Implemented semantics

- versioned `QueryEnvelope` and `CommandEnvelope`;
- already-authenticated `AuthenticatedPrincipal` with explicit `Grant` values;
- same-user subject enforcement; cross-person access fails closed;
- exact data-class/action/resource authorization before Authority Registry resolution;
- query requires class-level wildcard permission;
- API-major/schema compatibility preflight before state mutation;
- commands require idempotency keys and carry expected revision;
- canonical operations route only via `AuthorityRegistry.resolve()`;
- upserts use canonical exact read-after-write verification;
- append events use exact event-stream readback verification;
- structured conflicts/validation/not-found/authority failures map to stable API error categories;
- synthetic nonauthoritative audit sink records identities, requested action/resource, authorization decision, outcome, error category and resolved authority.

## Verification evidence

Local full-suite run against the implementation/test content:
- command: `python -m unittest discover -s tests -v`
- result: **30 tests passed, 0 failures/errors**.

Remote PR CI is pending and is not yet counted as packet test-verification evidence.

## Acceptance criteria

1. Versioned query/command envelopes. **Implemented/local-test-verified.**
2. Authenticated-principal/grant contract without token issuance. **Implemented/local-test-verified.**
3. Same-user enforcement / cross-person fail closed. **Implemented/local-test-verified.**
4. Exact resource/action authorization before state access. **Implemented/local-test-verified.**
5. Compatibility/unknown-action preflight before mutation. **Implemented/local-test-verified.**
6. Mandatory command idempotency + expected revision propagation. **Implemented/local-test-verified.**
7. All state routing through Authority Registry. **Implemented/local-test-verified.**
8. Exact read-after-write / event readback. **Implemented/local-test-verified.**
9. Stable conflict/validation/not-found/authority error categories. **Implemented/local-test-verified.**
10. Nonauthoritative audit sink for allowed/denied/failed requests. **Implemented/local-test-verified.**
11. Deterministic API behavior tests. **11 new API tests; 30 total pass locally.**
12. No HTTP/token/provider/Google/Android/evidence/legacy-state work. **Satisfied.**

## Exact next action

1. Compare branch to `main`; expected changed files are `CURRENT_WORK.md`, `mira/__init__.py`, `mira/api_core.py`, `tests/test_api_core.py`.
2. Open bounded PR at exact head and verify server-side changed-file list.
3. Require PR-triggered compile + full unit-suite success.
4. Merge exact green head/read back `main`.
5. Checkpoint completion and activate `M2-G1-003B` for authentication + HTTP transport.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture unrelated ideas in BACKLOG unless required for acceptance or explicitly reprioritized.
