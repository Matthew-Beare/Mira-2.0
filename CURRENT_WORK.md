# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active implementation packet and its resume point.

## Completed packet before this branch

### `M2-G1-001A` — Synthetic structured-state adapter core

- **Merged PR:** #37
- **Merge SHA / main readback:** `a6550d6a44bbe8b02285204e9f475f8caa085d95`
- **Post-merge completion checkpoint / this branch start SHA:** `6b9f9c362da2732f938958810b030d007a543ffe`
- **Remote CI:** GitHub Actions run `33209577735`; compile + 11 unit tests passed.
- **Result:** `STORE-ADAPTER-001A` is implemented/test-verified.

## Active packet

### `M2-G1-002` — Canonical Authority Registry core

- **Work ID:** `AUTHORITY-REGISTRY-001`
- **Class:** implementation / foundational prerequisite
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `impl/g1-002-authority-registry`
- **Branch start SHA:** `6b9f9c362da2732f938958810b030d007a543ffe`
- **Activation commit:** `98c9cd8896b66e4621849617d2b2a0c5df155125`
- **Registry implementation:** `33b74fac03c3666c0d0bd6580fd616c16fc7768a`
- **Registry tests:** `beb0278e2b488f6c1121195ba4a5998caeab70f3`
- **Package export update:** `266fab94ffa600a3435d2b5bab23e0614572009e`
- **Status:** implementation complete locally; full suite 19 tests pass; bounded PR/remote CI next.

## Implemented component

Component: **authority-registry**

Owned production surface:
- `mira/authority.py` — persisted Authority metadata, one binding per data class, explicit runtime adapter registration and safe route resolution.
- `mira/__init__.py` — package export surface.

Direct verification:
- `tests/test_authority.py` plus existing structured-state tests.
- existing `.github/workflows/ci.yml` compiles package/tests and runs all stdlib unit tests.

## Implemented semantics

- Authority records use caller-supplied IDs and non-secret adapter/resource/namespace/failure-domain/owner/schema/verification metadata;
- Authority records and bindings persist only through `StructuredStateAdapter`;
- stable one-binding-per-data-class identity enforces one active canonical authority;
- activation/replacement is optimistic-revision checked and inherits structured-state idempotency/replay semantics;
- registration never activates an Authority;
- disabled/unverified Authorities fail closed;
- runtime adapter mount/unmount is explicit and nonauthoritative;
- unregistered, unhealthy or schema-mismatched runtime adapter fails route resolution;
- routing returns exact persisted Authority + binding + mounted adapter;
- one unavailable data-class route does not prevent a healthy unrelated data-class route.

## Verification evidence

Local deterministic full-suite run against the implemented content:
- command: `python -m unittest discover -s tests -v`
- result: **19 tests passed, 0 failures/errors**.

Remote PR CI is pending and is not yet counted as test-verified evidence for this packet.

## Acceptance criteria

1. Stable bounded Authority records. **Implemented/local-test-verified.**
2. Persist through `StructuredStateAdapter` only. **Implemented/local-test-verified.**
3. Exactly one binding per mutable data class; missing binding explicit. **Implemented/local-test-verified.**
4. Optimistic revision + replay-safe activation/replacement. **Implemented/local-test-verified.**
5. Unknown/disabled/unverified/unregistered/unhealthy/schema-mismatched route fails closed. **Implemented/local-test-verified.**
6. Registration never silently activates. **Implemented/local-test-verified.**
7. Runtime adapter registration is explicit and nonauthoritative. **Implemented/local-test-verified.**
8. Resolution returns exact metadata + adapter without credentials. **Implemented.**
9. Deterministic routing/replacement/replay/failure-isolation tests. **8 new tests; 19 total pass locally.**
10. No HTTP/API/provider-specific/cross-person/evidence/Android work. **Satisfied.**

## Exact next action

1. Compare branch to `main`; verify only Authority Registry/test/current-work/package-export files changed.
2. Open bounded PR at exact head and verify server-side changed-file list.
3. Require PR-triggered CI success.
4. Merge exact green head/read back `main`.
5. Checkpoint completion and activate `API-CORE-001` as successor.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture unrelated ideas in BACKLOG unless required for acceptance or explicitly reprioritized.
