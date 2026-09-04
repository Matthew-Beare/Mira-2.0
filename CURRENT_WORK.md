# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active/recovery packet and exact recovery state.

## Product direction

Default Personal MIRA remains stock ChatGPT + Google Workspace first. Android extends the same canonical reality without becoming a second authority. M2-M1-001 through M2-M1-008 are durably closed. The next dependency-correct Android shared-state slice is canonical mutation through the already-verified queued writer; stock-ChatGPT cross-readback remains separate unless a hard implementation dependency emerges.

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
- Stock-ChatGPT cross-readback is step 7 and remains separate from this packet unless implementation proves it is a hard dependency.
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
- **Status:** active implementation

## Objective

Provide the smallest safe Android canonical mutation façade over the already-verified offline queue, `ReconnectCoordinator`, and `GoogleWorkspaceTransport` semantics.

The façade must:

1. accept one exact caller-supplied command identity/idempotency identity and upsert material;
2. durably enqueue the command before any provider/transport call;
3. preserve exact replay semantics for already-pending and already-acknowledged commands;
4. drive only the existing queued-writer path, never direct canonical provider mutation;
5. preserve pending state when the remote worker is still pending or transport fails;
6. treat remote failure/protocol/local failure explicitly and never fabricate success;
7. report applied success only when the existing coordinator has verified canonical readback, stored the verified snapshot, and acknowledged the exact local command;
8. return the resulting exact canonical cached snapshot only after that terminal verified success;
9. preserve crash/retry convergence, FIFO ordering, revision conflict behavior, and nonauthoritative local-cache semantics;
10. remain provider-neutral in `:core` with zero new provider SDK/token/resource-ID ownership.

## Acceptance criteria

1. One bounded mutation façade exists in Android `:core`; it does not duplicate transport/reconnect logic.
2. Caller supplies stable `command_id` and `idempotency_key`; retry does not generate new identities.
3. Durable enqueue occurs before transport I/O and exact duplicate enqueue is idempotent.
4. A command already acknowledged with identical material returns converged applied state without re-enqueueing or provider mutation when the verified cached result is present; missing result evidence fails closed rather than inventing success.
5. Remote `PENDING` leaves the command pending and returns a waiting state.
6. Transport failure leaves the command pending and returns an explicit transport failure.
7. Remote failed/stale-revision result is explicit and does not acknowledge the local command.
8. Terminal `SUCCEEDED` cannot be exposed as applied unless canonical readback is verified, the snapshot is persisted, and the local command is acknowledged.
9. Crash/retry after remote success but before local acknowledgement converges through existing idempotent remote reconciliation without duplicate canonical mutation.
10. Exact resulting resource class/ID/revision/payload is returned only from the verified local canonical snapshot after acknowledgement.
11. Existing reconnect, read-freshness, Workspace transport, offline-state, Android ownership, Python, and Apps Script tests remain green.
12. No Work mode, live provider mutation, legacy production state, historical proof resource, private provider identifier, token, or credential is used for deterministic implementation/test evidence.
13. End-of-packet FEATURES/BACKLOG/ROADMAP/invariant alignment is recorded before merge.
14. Exact-head CI, expected-head merge, remote-main readback, post-merge CI, lifecycle reconciliation, and final closeout CI are required before durable closure.

## Completed evidence

- M2-M1-008 closed at `fbef838a0ef7e60d2aec3a4943227d589cca0827` with final CI `33839865147` green.
- Fresh authority review confirms mutation is the next M2-M1 roadmap step and `ANDROID-SYNC` remains partial.
- `OfflineSyncStateStore` already provides durable FIFO enqueue, exact-material duplicate detection, acknowledgement tombstones, monotonic snapshots, and replay suppression.
- `ReconnectCoordinator` already enforces FIFO command reconciliation, pending/failure preservation, verified snapshots before acknowledgement, crash/retry convergence, and explicit failure states.
- `GoogleWorkspaceTransport.reconcileCommand` already preserves the Commands inbox contract, ambiguous-append reread convergence, exact-material duplicate validation, and terminal canonical readback parsing.
- No existing canonical mutation façade was found; this packet composes the proven seams rather than adding another execution engine.

## Explicitly deferred

- Stock ChatGPT reading the Android mutation back from the same canonical authority.
- Live Android Google authorization/provider-device execution evidence.
- User-facing conflict-resolution UI.
- Broad Connections/app-shell polish.
- Representative-device proof, signing/distribution, notifications/TTS, capture paths, and unrelated providers.

## Session-end alignment verification — pending

### `FEATURES.md`

Pending final implementation/evidence review.

### `BACKLOG.md`

Pending final lifecycle review; `ANDROID-SYNC` must remain partial unless stock-ChatGPT cross-readback is also genuinely proven.

### `ROADMAP.md`

Pending final confirmation that mutation step 6 is satisfied while step 7 cross-readback remains next.

### Direction result

**PENDING IMPLEMENTATION + EXACT-HEAD CI.**

## Exact next action / resume point

1. Inspect existing direct tests for `OfflineSyncStateStore`, `ReconnectCoordinator`, and `GoogleWorkspaceTransport` to reuse their proven semantics without duplication.
2. Implement the smallest provider-neutral canonical mutation façade and direct JVM tests.
3. Add ownership metadata only if new production source requires it.
4. Run/open clean CI and repair only packet-scoped failures.
5. Do not use Work mode until deterministic mutation implementation/tests are green and a narrow live provider/device acceptance proof genuinely remains.

## Recovery protocol

Read this file first. Verify branch `work/m2-m1-009-canonical-mutation` against base `fbef838a0ef7e60d2aec3a4943227d589cca0827`. Resume from the mutation façade direct-test implementation. Do not rerun M2-M1-001 through M2-M1-008 and do not absorb stock-ChatGPT cross-readback without a hard dependency.
