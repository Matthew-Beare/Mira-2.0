# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and the exact recovery point.

## Product deployment invariant

Default Personal MIRA remains **Google Workspace first, zero infrastructure**. Stock ChatGPT may use the official same-user Google Drive/Sheets connection for the single-writer Personal lane. That convenience must not be generalized into unsafe multi-writer state mutation.

The Android milestone therefore adds a stronger shared execution boundary only where concurrency requires it. Provider-neutral `API-001`, `AUTH-001` and `STORE-001` remain canonical; no client becomes an independent authority and no dual writable masters are permitted.

## Completed predecessor

### `M2-M0-006` — Google Workspace zero-infrastructure first run

- **Status:** complete and remotely verified.
- PR #50 merge `e412405a475d1423edaac821d7a99481e4a6eb4b`; CI `33243206658` green.
- PR #51 merge `641a7ce412bd0de46500c229910e52cb35a90bcc`; CI `33243533206` green.
- PR #52 merge `07d79c3a72cc906e93316e213e282919a1fcc4ff`; CI `33243840207` green.
- Closeout PR #53 merge `983444bf697a58a42c4482859d4fe7f0c17fb454`; CI `33274016785` green.
- Proven Personal path: clean Workspace copy → Authority/binding bootstrap → stock ChatGPT native Google create/read/replay/mutate/readback with exact provider verification.
- Truth boundary: native read-then-write Sheets mutation is single-writer only; it is not distributed compare-and-swap.

### Preserved onboarding contract

`ONBOARD-003`/`ONBOARD-004` remain preserved in Git and audited legacy source: four-question kickoff, resumable Interview Ledger, current AI-use/friction discovery, and evidence-first reuse of accessible conversation/files/connected sources. Full MIRA 2.0 interview runtime is still queued under `FIRSTBOOT-CORE-001` / `DISCOVERY-CORE-001`; this packet does not silently absorb it.

## Preserved advanced deployment work

### `M2-M0-005` — Cloud Run credential + live Google deployment proof

- Related work: `API-DEPLOYMENT-001B`.
- Paused/deprioritized as a Personal-baseline prerequisite; reusable candidate for stronger shared execution.
- PR #48 merged `acb37af4aa378e8128d8591406859fe954af3474`; CI `33217543700` green.
- PR #49 merged `3332081054d691eca646c1d7bb274d22096f1c62`; CI `33218561781` green.
- Pre-pivot checkpoint: `c392b9b829fab989be8856c9272294c9907e409e`.
- No live Cloud Run evidence is claimed.

## Active packet

### `M2-M1-001` — Concurrent canonical command boundary

- **Primary work:** first bounded slice of `ANDROID-CLIENT-CORE-001`
- **Related features:** `CLIENT-ANDROID-001`, `API-001`, `AUTH-001`, `STORE-001`, `RECOVERY-002`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `integration/m1-001-concurrent-boundary`
- **Base SHA:** `983444bf697a58a42c4482859d4fe7f0c17fb454`
- **Status:** active architecture/contract packet; no Android UI or live canonical mutation yet.

## Objective

Select and prove the smallest stronger execution boundary that allows stock ChatGPT and a future Android client to submit canonical commands without racing direct Google Sheets read-then-write operations. The selected boundary must serialize or transactionally reject conflicting mutations, preserve MIRA's existing idempotency/revision/readback semantics, and keep Google Workspace as a valid Personal authority rather than forcing a product-model rewrite.

This packet is deliberately **not** “build the Android app.” It establishes the safe command/mutation seam Android will depend on.

## Candidate boundary set

Evaluate only credible minimal candidates:

1. **Existing managed API / Cloud Run profile** — reuse the already-implemented `API-001` managed runtime and single-instance Google adapter path, adding whatever stronger concurrency semantics are actually required rather than rebuilding the product model.
2. **Google-native serialized command worker** — a Workspace-side command inbox/worker is viable only if official Google behavior proves API-written commands can be processed reliably, authenticated clients cannot bypass the single writer, latency/recovery are acceptable, and the worker can provide deterministic command result/readback semantics.

Do not select a design because it sounds elegant. Provider behavior must be verified from current authoritative documentation and backed by deterministic tests.

## Acceptance criteria

1. **No direct multi-writer Sheets mutation.** ChatGPT native connector and Android may not both independently perform canonical read-then-write mutations.
2. **One canonical mutation sequencer.** Every Android-era write reaches one execution boundary that owns revision/idempotency conflict decisions before the provider mutation.
3. **Existing semantics preserved.** `API-001` command envelope, Authority routing, `STORE-001` revision/idempotency behavior and exact provider readback remain canonical.
4. **Same-user authentication is explicit.** Stock ChatGPT and Android each have a supported authentication path; no secret is embedded in prompts, Sheet cells, public Git or URL query parameters.
5. **Replay safety.** Same command/idempotency material returns the original result without duplicate provider mutation.
6. **Conflict safety.** Two commands based on the same stale revision cannot both succeed.
7. **Restart/retry safety.** Boundary restart or client retry cannot silently duplicate a successful command.
8. **No dual writable masters.** The Personal native Sheets path must be placed in read-only/client-command mode when the stronger Android boundary becomes active for mutation.
9. **Provider portability.** Google Sheets remains behind `STORE-001`; selection must not make Android depend on spreadsheet row coordinates or Google-specific schema.
10. **Synthetic first.** Prove the command/concurrency contract with deterministic tests before any live Android or production-provider writes.
11. **Legacy preservation.** No legacy MIRA production artifact is used as a fixture or modified.
12. **Bounded scope.** No Android UI, notifications/TTS, camera/NFC/BLE, Gmail/Calendar fan-out, full onboarding port or Cloud Run live deployment unless required to prove the selected command boundary.

## Decision evidence required

For each candidate, record:
- client authentication feasibility for stock ChatGPT and Android;
- whether API-originated writes trigger/queue Google-side execution as assumed;
- concurrency/locking/transaction guarantees;
- command latency and retry behavior;
- restart/recovery semantics;
- provider readback capability;
- operational burden for an ordinary Personal user;
- whether the design preserves the M2-M0 no-infrastructure baseline for users who do not enable Android.

Reject any candidate whose correctness depends on undocumented trigger behavior, best-effort polling being mistaken for a transaction, or two independent writers “probably not colliding.”

## Exact next action

1. Verify current official Google Apps Script trigger/LockService/web-app behavior relevant to API-written command queues and concurrent executions.
2. Re-read the existing managed runtime/Cloud Run implementation and tests from main.
3. Write a bounded architecture decision plus deterministic concurrency contract tests for the selected execution seam.
4. Do not touch live provider state until those tests are green.
5. Update `BACKLOG.md` only if the evidence changes dependency ordering or splits `ANDROID-CLIENT-CORE-001` further.

## Recovery protocol

Read this file first. Verify main contains M2-M0 closeout merge `983444bf697a58a42c4482859d4fe7f0c17fb454` or a descendant. Continue only `M2-M1-001` on `integration/m1-001-concurrent-boundary`. Preserve M2-M0 Personal native Google proof as single-writer evidence; do not reinterpret it as safe Android concurrency. Preserve the Cloud Run checkpoint without claiming live proof. Keep provider IDs, secrets, personal data and live row contents out of public Git.
