# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active/recovery packet and exact recovery state.

## Product direction

Default Personal MIRA remains stock ChatGPT + Google Workspace first. Android extends the same canonical reality without becoming a second authority. M2-M1-001 through M2-M1-008 are durably closed. M2-M1-009 is the bounded Android canonical-mutation child of `ANDROID-SYNC`; stock-ChatGPT cross-readback remains separate next proof work.

## Prior-packet recovery verification — 2026-09-04

- Repository: `Matthew-Beare/Mira-2.0`.
- Authoritative `main`: `fbef838a0ef7e60d2aec3a4943227d589cca0827`.
- M2-M1-008 final closeout CI: `33839865147` — success on that exact head.
- Remote `main` independently read back the same SHA.
- M2-M1-001 through M2-M1-008 and M2-GOV-012 are durably closed and must not be rerun.

## Session-start alignment verification — 2026-09-04 M2-M1-009

### `FEATURES.md`

- `CLIENT-ANDROID-001` remains `specified+implemented+test_verified+partial`.
- `API-001`, `AUTH-001`, `STORE-001`, and `RECOVERY-002` require replay-safe mutation, exact verified canonical readback, and one-authority semantics.
- Android local queue/cache state is never canonical authority.

### `BACKLOG.md`

- `ANDROID-CLIENT-CORE-001` is partial through M2-M1-008.
- `ANDROID-SYNC` is partial through M2-M1-008: canonical Android read/freshness is complete; Android mutation and stock-ChatGPT cross-readback remain.
- The next unfinished dependency is Android canonical mutation through the existing queued writer.

### `ROADMAP.md`

- M2-M1 ordered proof step 6 is Android mutation through the shared queued execution boundary.
- Stock-ChatGPT cross-readback is step 7 and remains separate from this packet.
- Representative-device proof remains later.

### Direction result

**ALIGNED.** Implement one provider-neutral Android mutation surface that durably enqueues an exact upsert intent before provider I/O, drives the existing queued transport/reconnect contract, and reports applied success only after verified canonical readback and local acknowledgement. Do not implement stock-ChatGPT cross-readback, conflict UI, app-shell polish, release signing, or live provider/device proof in this packet.

## Active packet

### `M2-M1-009` — Canonical Android mutation through queued writer

- **Primary work:** `ANDROID-SYNC`
- **Primary features:** `CLIENT-ANDROID-001`, `API-001`
- **Related invariants/features:** `AUTH-001`, `STORE-001`, `RECOVERY-002`, `DATA-001`, `PROVIDER-002`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `work/m2-m1-009-canonical-mutation`
- **Base SHA:** `fbef838a0ef7e60d2aec3a4943227d589cca0827`
- **Implementation head before this evidence checkpoint:** `902b8ccb5cfc71a0e050667464b3a0cf2609e2dd`
- **Implementation CI:** `33840525676` — success on exact implementation head
- **PR:** #109 — open and mergeable
- **Status:** merge candidate after this evidence checkpoint passes exact-head CI

## Objective result

**IMPLEMENTED AND TEST-VERIFIED AT THE BOUNDED REPOSITORY EVIDENCE CEILING.**

`CanonicalResourceMutator` composes the already-verified encrypted queue, `ReconnectCoordinator`, and transport contract without adding a second mutation engine.

1. Caller-supplied stable command and idempotency identities are preserved exactly.
2. Exact upsert intent is durably enqueued before any transport/provider I/O.
3. Exact pending retry does not duplicate the local queue.
4. Exact acknowledged replay returns converged canonical state without provider I/O.
5. FIFO blocking is distinguished from the requested command itself waiting remotely.
6. Remote conflict/failure and transport/protocol/local failure remain explicit and do not become success.
7. `APPLIED` requires the exact command to resolve to the store's durable `ALREADY_ACKNOWLEDGED` disposition plus a cached canonical snapshot whose revision is newer than `expected_revision`.
8. Command success remains `APPLIED` even if the later general Changes refresh fails, because acknowledgement already followed verified command readback.
9. Unsupported append-event/null-revision shapes fail before enqueue or provider I/O.
10. Core remains provider-neutral and owns no token, spreadsheet ID, account identity, URL, or provider SDK.

## Completed evidence

- Branch `work/m2-m1-009-canonical-mutation` was created exactly from verified main `fbef838a0ef7e60d2aec3a4943227d589cca0827`.
- `CanonicalResourceMutator.java` adds the single bounded mutation façade in Android `:core`.
- Direct `CanonicalResourceMutatorTest` coverage includes durable enqueue-before-I/O, verified applied success, exact acknowledged replay/no provider I/O, pending retry convergence, stale-revision remote failure preservation, transport failure preservation, earlier FIFO blocking, command success despite later Changes-refresh failure, unverified-success fail-closed behavior, missing/invalid cached result evidence, and unsupported command shapes.
- Existing `ReconnectCoordinatorTest` continues to prove crash-after-verified-success-before-ack retry convergence and exact replay ordering.
- Android ownership now assigns the new production source to `android-client-canonical-resource-mutator` with direct JVM verification.
- Compare from base through implementation head contains only `CURRENT_WORK.md`, the new mutator production/test files, and Android ownership metadata.
- Exact implementation head `902b8ccb5cfc71a0e050667464b3a0cf2609e2dd` passed CI `33840525676`, including compile, feature registry, product lifecycle, starter distribution, work-session alignment, code ownership, both Android modules, Python tests, and Workspace Apps Script tests.
- PR #109 is mergeable.
- No Work mode, live Google provider access/mutation, historical proof resource, legacy MIRA production state, private provider identifier, token, credential, or secret was used.

## Acceptance criteria result

1. Bounded provider-neutral mutation façade, no duplicated execution engine — **satisfied**.
2. Stable caller-owned command/idempotency identities — **satisfied**.
3. Durable enqueue before provider I/O and exact replay semantics — **satisfied**.
4. Already-acknowledged convergence requires verified cached result evidence — **satisfied**.
5. Remote pending preserves queue — **satisfied**.
6. Transport failure preserves queue — **satisfied**.
7. Remote stale-revision/failure remains explicit and unacknowledged — **satisfied**.
8. `APPLIED` requires acknowledgement produced by verified canonical readback plus newer cached canonical revision — **satisfied**.
9. Crash/retry convergence — **preserved and test-verified by existing coordinator tests plus exact mutator replay tests**.
10. Exact canonical class/ID/revision/payload returned only from cached canonical snapshot after acknowledgement — **satisfied**.
11. Existing repository suites and ownership gates — **green on `33840525676`**.
12. Zero Work/live-provider/legacy/private-state scope — **satisfied**.
13. End-of-packet authority alignment — **satisfied below**.
14. Final evidence-head CI, expected-head merge, remote-main readback, post-merge CI, lifecycle reconciliation and final closeout CI — **pending closeout only**.

## Explicitly deferred

- Stock ChatGPT reading the Android mutation back from the same canonical authority.
- Live Android Google authorization/provider-device execution evidence.
- User-facing conflict-resolution UI.
- Broad Connections/app-shell polish.
- Representative-device proof, signing/distribution, notifications/TTS, capture paths, and unrelated providers.

## Session-end alignment verification — 2026-09-04 M2-M1-009

### `FEATURES.md`

`CLIENT-ANDROID-001` remains partial. M2-M1-009 adds deterministic canonical-mutation implementation/test evidence only; it does not prove the cross-client shared-state vertical or representative-device behavior.

### `BACKLOG.md`

`ANDROID-SYNC` must remain partial after M2-M1-009. Canonical Android read/freshness and deterministic mutation are implemented/test-verified; stock-ChatGPT cross-readback remains unfinished. `ANDROID-CLIENT-CORE-001` remains partial because live provider/device evidence, conflict UI and representative-device proof remain open.

### `ROADMAP.md`

M2-M1 step 6 is satisfied at deterministic repository evidence once PR #109 merges. Step 7, stock ChatGPT reading the Android mutation from the same authority, remains next. Step 8 representative-device proof remains later.

### Direction result

**ALIGNED.** This packet completes only the deterministic Android mutation child. It does not falsely complete `ANDROID-SYNC`, move app/release work forward, or alter provider/integration priorities.

## Exact next action / resume point

1. Require exact-head CI on this final evidence checkpoint.
2. Re-read PR #109 scope/mergeability and expected head.
3. Merge with expected-head protection only after green CI.
4. Independently read back remote `main` and require post-merge CI on the exact merge SHA.
5. Reconcile `BACKLOG.md` and `ROADMAP.md` to record M2-M1-009 mutation evidence while leaving `ANDROID-SYNC` partial; `FEATURES.md` should remain partial unless evidence genuinely changes.
6. Write final `CURRENT_WORK` closeout and require exact-head CI plus matching remote-main readback.
7. Then select the next packet from canonical dependency/value order; current expected next M2-M1 child is stock-ChatGPT cross-readback from the same authority.
8. Do not use Work mode until deterministic work is green and a narrow live-provider/device proof genuinely remains.

## Recovery protocol

Read this file first. Resume from final evidence-head CI for PR #109. Do not rerun M2-M1-001 through M2-M1-008, and do not absorb stock-ChatGPT cross-readback or app/release work into M2-M1-009.
