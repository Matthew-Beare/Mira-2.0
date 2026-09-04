# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active/recovery packet and exact recovery state.

## Product direction

Default Personal MIRA remains stock ChatGPT + Google Workspace first. Android extends the same canonical reality without becoming a second authority. M2-M1-001 through M2-M1-008 are durably closed. M2-M1-009 has completed the deterministic Android canonical-mutation child of `ANDROID-SYNC`; stock-ChatGPT cross-readback from the same authority is the next shared-state proof. `ANDROID-SYNC` and `CLIENT-ANDROID-001` remain partial until their remaining evidence is genuinely satisfied.

## Prior-packet recovery verification — 2026-09-04

- Repository: `Matthew-Beare/Mira-2.0`.
- M2-M1-008 final closeout head: `fbef838a0ef7e60d2aec3a4943227d589cca0827`.
- M2-M1-008 final closeout CI: `33839865147` — success on that exact head.
- M2-M1-001 through M2-M1-008 and M2-GOV-012 are durably closed and must not be rerun.

## Session-start alignment verification — 2026-09-04 M2-M1-009

### `FEATURES.md`

- `CLIENT-ANDROID-001` remained `specified+implemented+test_verified+partial`.
- `API-001`, `AUTH-001`, `STORE-001`, and `RECOVERY-002` require replay-safe mutation, exact verified canonical readback, and one-authority semantics.
- Android local queue/cache state is never canonical authority.

### `BACKLOG.md`

- `ANDROID-CLIENT-CORE-001` was partial through M2-M1-008.
- `ANDROID-SYNC` was partial through M2-M1-008: canonical Android read/freshness was complete; Android mutation and stock-ChatGPT cross-readback remained.
- Android canonical mutation through the existing queued writer was the next unfinished dependency.

### `ROADMAP.md`

- M2-M1 ordered proof step 6 was Android mutation through the shared queued execution boundary.
- Stock-ChatGPT cross-readback was step 7 and remained separate from this packet.
- Representative-device proof remained later.

### Direction result

**ALIGNED.** M2-M1-009 was bounded to one provider-neutral Android mutation surface that durably enqueues an exact upsert intent before provider I/O, drives the existing queued transport/reconnect contract, and reports applied success only after verified canonical readback and local acknowledgement. Stock-ChatGPT cross-readback, conflict UI, app-shell polish, release signing, and live provider/device proof were explicitly excluded.

## Active packet

### `M2-M1-009` — Canonical Android mutation through queued writer

- **Primary work:** `ANDROID-SYNC`
- **Primary features:** `CLIENT-ANDROID-001`, `API-001`
- **Related invariants/features:** `AUTH-001`, `STORE-001`, `RECOVERY-002`, `DATA-001`, `PROVIDER-002`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Implementation branch:** `work/m2-m1-009-canonical-mutation`
- **Packet base SHA:** `fbef838a0ef7e60d2aec3a4943227d589cca0827`
- **Implementation head:** `902b8ccb5cfc71a0e050667464b3a0cf2609e2dd`
- **Implementation CI:** `33840525676` — success
- **Final PR head:** `65f7d8c833f6b885b5a4d954f0b6bfc235fb94fd`
- **Final PR-head CI:** `33840744737` — success
- **PR:** #109 — merged
- **Merge SHA:** `3ad36e2b72ee442e0fb42ad5b4f7c8ab7166e3aa`
- **Post-merge CI:** `33840853846` — success on exact merge SHA
- **Backlog lifecycle commit:** `4b7cde25c665e48c680d227d83c059b53b740028`
- **Roadmap lifecycle commit:** `883cd74a08f88dea2a8a93b4eaca7614278513f9`
- **Status:** complete at bounded repository evidence ceiling; this closeout commit still requires exact-head CI and matching remote-main readback before durable closure

## Objective result

**COMPLETE AT THE BOUNDED REPOSITORY EVIDENCE CEILING.**

`CanonicalResourceMutator` composes the already-verified encrypted queue, `ReconnectCoordinator`, and transport contract without adding a second mutation engine.

1. Caller-supplied stable command and idempotency identities are preserved exactly.
2. Exact upsert intent is durably enqueued before any transport/provider I/O.
3. Exact pending retry does not duplicate the local queue.
4. Exact acknowledged replay returns converged canonical state without provider I/O.
5. FIFO blocking is distinguished from the requested command itself waiting remotely.
6. Remote conflict/failure and transport/protocol/local failure remain explicit and do not become success.
7. `APPLIED` requires the exact command to resolve to the store's durable acknowledged disposition plus a cached canonical snapshot whose revision is newer than `expected_revision`.
8. Command success remains `APPLIED` even if the later general Changes refresh fails, because acknowledgement already followed verified command readback.
9. Unsupported append-event/null-revision shapes fail before enqueue or provider I/O.
10. Core remains provider-neutral and owns no token, spreadsheet ID, account identity, URL, or provider SDK.

## Completed evidence

- Branch `work/m2-m1-009-canonical-mutation` was created exactly from verified main `fbef838a0ef7e60d2aec3a4943227d589cca0827`.
- `CanonicalResourceMutator.java` adds the single bounded mutation façade in Android `:core`.
- Direct `CanonicalResourceMutatorTest` coverage includes durable enqueue-before-I/O, verified applied success, exact acknowledged replay/no provider I/O, pending retry convergence, stale-revision remote failure preservation, transport failure preservation, earlier FIFO blocking, command success despite later Changes-refresh failure, unverified-success fail-closed behavior, missing/invalid cached result evidence, and unsupported command shapes.
- Existing `ReconnectCoordinatorTest` continues to prove crash-after-verified-success-before-ack retry convergence and exact replay ordering.
- Android ownership assigns the production source to `android-client-canonical-resource-mutator` with direct JVM verification.
- Exact implementation head `902b8ccb5cfc71a0e050667464b3a0cf2609e2dd` passed CI `33840525676`.
- Final PR head `65f7d8c833f6b885b5a4d954f0b6bfc235fb94fd` passed CI `33840744737`.
- PR #109 merged with expected-head protection at `3ad36e2b72ee442e0fb42ad5b4f7c8ab7166e3aa`.
- Remote `main` independently read back that exact merge SHA before lifecycle commits.
- Post-merge CI `33840853846` succeeded on the exact merge SHA.
- A malformed first BACKLOG lifecycle replacement at `829c97004eb0908d5916f67fdb607b4dc7d13c90` was rejected by compare verification because it omitted unrelated historical tail lines. It was immediately neutralized by compensating commit `600f7def40a3f307a500c16642ddff714d624fd7`; compare from the clean merge SHA through that recovery head showed zero file differences.
- The safe BACKLOG retry `4b7cde25c665e48c680d227d83c059b53b740028` changes only four intended M2-M1 lifecycle lines: `ANDROID-CLIENT-CORE-001`, `ANDROID-SYNC`, the Android lifecycle summary, and the M2-M1 dependency finding.
- ROADMAP lifecycle commit `883cd74a08f88dea2a8a93b4eaca7614278513f9` changes only four intended M2-M1 status/ordered-proof lines: M2-M1-001 through M2-M1-009 are complete at their bounded ceilings, mutation step 6 is complete, cross-readback step 7 is next, and representative-device proof remains later.
- `FEATURES.md` correctly remains partial for `CLIENT-ANDROID-001`; no false feature completion was recorded.
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
9. Crash/retry convergence — **satisfied by existing coordinator evidence plus mutator replay tests**.
10. Exact canonical class/ID/revision/payload returned only from cached canonical snapshot after acknowledgement — **satisfied**.
11. Existing repository suites and ownership gates — **satisfied on both PR-head CIs and post-merge CI**.
12. Zero Work/live-provider/legacy/private-state scope — **satisfied**.
13. End-of-packet FEATURES/BACKLOG/ROADMAP/invariant alignment — **satisfied**.
14. Expected-head merge, remote-main readback and post-merge CI — **satisfied**.
15. Final closeout exact-head CI and matching remote-main readback — **pending only**.

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

`ANDROID-CLIENT-CORE-001` is partial through M2-M1-009. `ANDROID-SYNC` is also partial through M2-M1-009: canonical Android read/freshness and deterministic queued mutation are complete; stock-ChatGPT cross-readback remains unfinished.

### `ROADMAP.md`

M2-M1 step 6, Android mutation through the shared queued boundary, is complete in M2-M1-009 / PR #109 at merged/test-verified evidence. Step 7, stock ChatGPT reading that mutation from the same authority, is next. Step 8 representative-device proof remains later.

### `PRODUCT_INVARIANTS.md`

One-authority semantics, nonauthoritative encrypted Android state, exact verified readback before applied success, provider-neutral core, intent-first provider setup, and legacy-data protection remain preserved.

### Direction result

**ALIGNED.** M2-M1-009 completes only the deterministic Android mutation child. It does not falsely complete `ANDROID-SYNC`, promote `CLIENT-ANDROID-001`, absorb cross-readback, or move UI/release/device work forward.

## Exact next action / resume point

1. Require exact-head CI on this closeout commit and independently read back remote `main` at the same SHA.
2. Once both are green, treat M2-M1-009 as durably closed.
3. Re-read `CURRENT_WORK.md`, `FEATURES.md`, `BACKLOG.md`, `ROADMAP.md`, and `PRODUCT_INVARIANTS.md` from that exact main state.
4. Open exactly one next bounded packet for stock-ChatGPT cross-readback of the Android mutation from the same canonical authority.
5. Keep representative-device proof separate unless fresh dependency review proves it is required for that cross-readback packet.
6. Do not use Work mode until deterministic cross-readback protocol/test work is green and a narrow live provider acceptance proof genuinely remains.

## Recovery protocol

Read this file first. Verify remote `main` plus this closeout commit's exact-head CI. If both are green, M2-M1-009 is durably closed and the next dependency-correct packet is stock-ChatGPT cross-readback from the same authority. Do not rerun M2-M1-001 through M2-M1-009.