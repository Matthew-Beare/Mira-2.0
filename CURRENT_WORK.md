# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active/recovery packet and exact recovery state.

## Prior-packet closure verification — 2026-09-04

- Repository: `Matthew-Beare/Mira-2.0`.
- M2-M1-009 closeout commit: `a7238151a08734b51e1ffa3386a5b672a73c46c0`.
- Remote `main` independently read back at that exact SHA.
- Exact-head CI: `33900587999` — success.
- M2-M1-001 through M2-M1-009 are durably closed at their recorded bounded evidence ceilings and must not be rerun.

## Session-start alignment verification — 2026-09-04 M2-M1-010

### `FEATURES.md`

- `CLIENT-ANDROID-001` remains `specified+implemented+test_verified+partial`; deterministic Android mutation exists, but the shared-state vertical is not complete until stock ChatGPT reads that mutation from the same canonical authority.
- `API-001`, `AUTH-001`, and `STORE-001` preserve one-authority semantics, exact canonical identity/revision/payload truth, and verified readback.
- `RECOVERY-002` requires failure isolation and explicit dependency boundaries. `DATA-001` protects legacy production state.

### `BACKLOG.md`

- `ANDROID-CLIENT-CORE-001` remains partial through M2-M1-009.
- `ANDROID-SYNC` is the active vertical and remains partial only because stock-ChatGPT cross-readback is unfinished after canonical Android read/freshness and deterministic queued mutation were completed.
- Representative-device proof, conflict UI, notifications/TTS, capture, and release work are separate later evidence/work.

### `ROADMAP.md`

- M2-M1 ordered proof steps 1 through 6 are complete at their bounded evidence ceilings.
- Step 7, stock ChatGPT reading the Android mutation from the same canonical authority, is explicitly next.
- Step 8 representative-device proof remains separate and later.

### `PRODUCT_INVARIANTS.md`

- Stock ChatGPT must read current canonical mutable state from the verified Workspace authority rather than chat history, memory, `Commands`, or the `Changes` projection.
- Shared `queued_writer` mode disables direct native mutation but must not disable canonical reads.
- Exact authority routing and provider/readback truth remain mandatory; transport/projection evidence cannot become a second authority.
- No legacy MIRA production resource may be used as a test fixture.

### Direction result

**ALIGNED.** The next dependency-correct bounded outcome is a deterministic stock-ChatGPT cross-readback contract for a shared-writer mutation. It must verify the exact canonical `Resources` state and matching mutation provenance without duplicating the queued writer, permitting direct writes in `queued_writer` mode, or treating `Changes`/`Commands` as canonical truth.

## Active packet

### `M2-M1-010` — Deterministic stock-ChatGPT cross-readback

- **Primary work:** `ANDROID-SYNC`
- **Primary features:** `CLIENT-ANDROID-001`, `API-001`
- **Preserved invariants/features:** `AUTH-001`, `STORE-001`, `RECOVERY-002`, `DATA-001`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `work/m2-m1-010-chatgpt-cross-readback`
- **Packet base SHA:** `a7238151a08734b51e1ffa3386a5b672a73c46c0`
- **Current head:** packet checkpoint commit created from the base; read back branch head before implementation and update this field at the next checkpoint
- **Dependencies:** completed M2-M1-009 deterministic queued mutation; existing stock-ChatGPT native Workspace read semantics; canonical Authority/structured-state contracts
- **Blockers:** none known for deterministic repository proof
- **Status:** active

## Objective

Add one bounded deterministic stock-ChatGPT/native Workspace cross-readback surface that proves an expected shared-writer upsert is present in the same canonical authority Android uses.

The verifier must read canonical `Resources` material, resolve the exact `authority_binding` and verified/enabled Google Sheets authority, and tie the target Resource revision/payload to its persisted idempotency provenance. `queued_writer` must remain readable but non-writable from the stock-ChatGPT native lane.

This packet does not execute a live Android or Google provider mutation. It establishes the protocol/test contract required before any narrow live cross-client acceptance proof.

## Feature alignment

### User-visible behavior enabled

After Android has applied a queued canonical mutation, stock ChatGPT can deterministically read the exact same canonical resource and establish that its identity, revision, payload, authority routing, idempotency key, request fingerprint, result, and resource reference agree with the persisted canonical mutation evidence.

### Preserved behavior/invariants

- exactly one writable canonical authority per mutable data class;
- `Resources` is canonical state; `Commands` is an inbox and `Changes` is a reconnect projection, neither is canonical state;
- `queued_writer` prevents direct stock-ChatGPT native mutation;
- canonical reads remain possible in `queued_writer` mode;
- exact readback is required before claiming shared-state convergence;
- no provider identifier, credential, account identity, private user data, or legacy production state is committed;
- provider-neutral API/Authority/store semantics remain independent of Android and Google transport details.

### Intentionally deferred

- live Android Google authorization/provider-device execution;
- live stock-ChatGPT/Google cross-client provider proof until deterministic protocol/tests are green;
- representative-device proof;
- conflict-resolution UI;
- notifications/TTS, capture paths, signing/distribution, and unrelated providers.

## Acceptance criteria

1. Add a bounded native Workspace cross-readback verifier rather than a second mutation/execution engine.
2. Cross-readback accepts `queued_writer` as a readable mode while existing direct-mutation guards continue to reject writes in that mode.
3. Resolve exactly one target canonical Resource by stable `(resource_type, resource_id)` identity; missing or duplicate identity fails closed.
4. Resolve exactly one matching `authority_binding` and exactly one referenced `authority`; authority must be enabled, verified, `adapter_key=google-sheets`, and schema-compatible.
5. Require exact expected resource revision and normalized payload.
6. Require the Resource row's persisted `last_idempotency_key` and `request_hash` to match the expected logical Android/shared-writer upsert.
7. Require exactly one matching Idempotency row with operation `upsert`, exact request hash, exact canonical upsert result, and exact `resource_ref`.
8. Compute/verify request fingerprint using the existing STORE-001 Workspace upsert fingerprint contract; do not invent a second hash contract.
9. The cross-readback surface performs zero mutations and consumes no `Changes` projection as authority.
10. Tests cover success in `queued_writer`, missing/duplicate/wrong resource material, authority-routing failures, and idempotency/provenance mismatch.
11. Existing direct mutation-mode tests remain green and still prove queued mode rejects native writes.
12. Production code ownership/direct-verification metadata remains valid if production files are changed.
13. Existing repository CI and alignment gates pass on the exact implementation head.
14. Before merge/closeout, repeat FEATURES/BACKLOG/ROADMAP/invariant alignment; do not falsely complete representative-device or live-provider evidence.
15. Merge only with expected-head verification, then require exact remote-main readback and post-merge CI before durable closure.

## Completed evidence

- M2-M1-009 durable closure verified on exact remote main `a7238151a08734b51e1ffa3386a5b672a73c46c0` with CI `33900587999` success.
- Session-start semantic alignment completed against `FEATURES.md`, `BACKLOG.md`, `ROADMAP.md`, `PRODUCT_INVARIANTS.md`, and `project/WORK_PACKET_POLICY.md` at that exact base SHA.
- Branch `work/m2-m1-010-chatgpt-cross-readback` created exactly from the verified base SHA.

## Exact next action / resume point

1. Read back the branch head after this packet checkpoint.
2. Implement the smallest deterministic cross-readback verifier in the existing stock-ChatGPT native Workspace component.
3. Add direct tests for shared-writer success and fail-closed authority/resource/idempotency mismatches without touching live provider state.
4. Update production ownership metadata only if needed by the touched production surface.
5. Run/obtain exact-head CI and continue only while green.

## Recovery protocol

Read this file first, then verify branch `work/m2-m1-010-chatgpt-cross-readback` and its exact head. Do not rerun M2-M1-001 through M2-M1-009. Do not enter Work mode or touch live Google provider resources unless this packet's deterministic protocol/test work is green and `CURRENT_WORK.md` has been advanced to a narrow live acceptance proof step.
