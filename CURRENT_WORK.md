# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and exact recovery state.

## Product direction

Default Personal MIRA remains stock ChatGPT + Google Workspace with no external infrastructure prerequisite. When Android or another software writer is enabled, direct independent Google Sheets mutation must stop; commands use the serialized shared command boundary. Ordinary users must not open Apps Script, paste code, manage triggers, copy provider IDs, or understand queued-writer internals merely to enable Android/shared access.

Pre-Android feature growth remains frozen except for this hard shared-writer proof. After this packet reaches its live Google evidence ceiling, start `ANDROID-CLIENT-CORE-001`.

## Session-start alignment verification — 2026-09-01 M2-M1-001 resume

### `FEATURES.md`

- `CLIENT-ANDROID-001`, `API-001`, `AUTH-001`, `STORE-001`, and `RECOVERY-002` require one safe shared canonical mutation boundary rather than independent read-then-write clients.
- Default Personal setup remains no-terminal/no-developer-console when software can provide an ordinary-user control.

### `BACKLOG.md`

- `ANDROID-COMMAND-BOUNDARY-001` is partial: provider-neutral sequencer and synthetic Workspace worker proof are complete in PRs #54/#55; live isolated Google worker proof remains pending.
- `ANDROID-CLIENT-CORE-001` is queued immediately after this live proof.
- `HOST-CONNECT-EXEC-001` was implemented/live-host-proven in M2-M0-029 / PR #90, but its BACKLOG status row still requires closure reconciliation. That bookkeeping does not change the technical critical path and must be corrected before this packet closes.

### `ROADMAP.md`

- M2-M1 is blocked on live shared-writer proof, not on inventing another concurrency architecture.
- Android client implementation follows this packet; unrelated provider expansion remains deferred.

### Direction result

**ALIGNED.** Resume the existing `M2-M1-001` packet. Fix the newly discovered ordinary-user activation blocker, publish that verified bound-script release into an isolated starter/proof substrate, then prove one real Google worker command end-to-end. Do not touch legacy production state.

## Active packet

### `M2-M1-001` — Concurrent canonical command boundary, live Google proof

- **Primary work:** `ANDROID-COMMAND-BOUNDARY-001`
- **Primary features:** `CLIENT-ANDROID-001`, `API-001`
- **Related invariants/features:** `AUTH-001`, `STORE-001`, `RECOVERY-002`, `ONBOARD-006`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `integration/m1-001-live-worker-proof`
- **Base/main SHA:** `2be8ccefd8ada72dc31bfd2f4df1c560ca22f483`
- **Prior implementation:** PR #54 provider-neutral sequencer; PR #55 Workspace `Commands` inbox + `ScriptLock` worker, both merged/test-verified.
- **Current branch evidence:** `Code.gs` now exposes `MIRA → Enable Android / shared access` through a wrapper around the existing `miraEnableQueuedWriter()`; direct tests guard the ordinary-user surface.
- **Dependencies:** isolated synthetic Google Workspace substrate; verified bound Apps Script release containing the current branch changes.
- **Current blocker:** Git source changes do not automatically update an already-copied bound Apps Script project. The current Google connector can copy/read/write Sheet cells but cannot publish bound Apps Script source or invoke custom Apps Script functions. Live proof therefore requires a release/publication seam before the one-click user activation can be exercised against the corrected bundle.

## Objective

Prove the existing queued-writer architecture against a fresh isolated Google Workspace copy using an ordinary-user activation path: enable Android/shared access without Apps Script-editor work, enqueue a synthetic API-001 command, observe the real time-driven worker serialize and commit it, and verify exact canonical/idempotency/result readback.

## Acceptance criteria

1. Use only a fresh isolated synthetic Sheet; legacy MIRA production Sheets, briefs, Calendars, automations, and user operational data are not fixtures.
2. The verified bound Apps Script release exposes `MIRA → Enable Android / shared access`; no normal user opens Apps Script or manually runs `miraEnableQueuedWriter()`.
3. Activation creates/validates exactly one one-minute worker trigger before persisted `mutation_mode=queued_writer` becomes authoritative.
4. Activation creates the canonical `Commands` transport tab and persists queued-writer mode.
5. Submit one synthetic same-user API-001 `entity` upsert command through the authenticated Google Sheet surface with stable command/idempotency IDs and expected revision 0.
6. The actual Google time-driven worker processes the pending command under `ScriptLock`.
7. Success is recorded only after exact Resource + Idempotency readback; the new entity is revision 1 and matches submitted payload/material.
8. Re-reading the command shows a durable succeeded result rather than assuming scheduler execution.
9. No independent direct-native canonical mutation path remains active after queued mode is authoritative.
10. Record only generic/synthetic provider evidence in public Git.
11. Exact-head CI, expected-head merge, remote readback, and post-merge CI are required for source changes.
12. Reconcile the stale M2-M0-029 `HOST-CONNECT-EXEC-001` BACKLOG row before packet closure.
13. After live proof, mark `ANDROID-COMMAND-BOUNDARY-001` only to the evidence actually demonstrated and start `ANDROID-CLIENT-CORE-001`.

## Live isolated substrate prepared

A fresh copy was created from a post-PR-55 Personal proof Sheet:

- title: `MIRA M2-M1-001 Live Queued Writer Proof - 2026-09-01 - NOT A STARTER`
- Google Sheet ID is intentionally not committed to public Git; it remains session/provider evidence only.
- metadata readback proves `environment=mira_2_sandbox`, `data_policy=synthetic_only`, `adapter_contract=STORE-001`, `writer_model=single_writer`.
- canonical Authority is verified/enabled and owned by synthetic subject `synthetic-no-app-user`; `entity` binding exists.
- before activation the copy has Metadata, Resources, Events, and Idempotency tabs and no Commands tab, as expected.

## Newly discovered blocker and fix

`CommandWorker.gs` already implemented `miraEnableQueuedWriter()`, but `Code.gs` exposed only `MIRA → Initialize this copy`. That meant a live activation required opening the Apps Script editor and running an internal function manually, violating the ordinary-user Personal contract.

The branch now adds a user-facing `MIRA → Enable Android / shared access` menu action through `miraEnableQueuedWriterFromMenu()`, which delegates to the already-tested worker activation and keeps internal queued-writer terminology out of the menu. `tests/test_shared_access_menu_contract.py` prevents regression.

The remaining issue is release publication: changing Git cannot mutate an existing bound Apps Script project, and the connected Google Drive/Sheets surface currently lacks an Apps Script source/publication action. Do not export this maintainer problem to an ordinary user by asking them to paste or run script code.

## Evidence ceiling so far

- Provider-neutral serialized command semantics: test-verified.
- Workspace worker implementation and fake-Apps-Script execution: test-verified in PR #55.
- Fresh isolated Google Sheet substrate and canonical metadata/Authority readback: live provider-readback verified.
- Ordinary-user activation UI fix: implemented on current branch; CI/merge pending.
- Actual Google Apps Script trigger creation/firing and queued command execution: **not yet live-verified**.

## Exact next action / resume point

1. Run CI for the shared-access menu/regression changes and merge only when green.
2. Identify or implement the bounded maintainer/template publication seam needed to place the verified bound Apps Script release into an isolated Google starter without ordinary-user script editing; reuse an existing stable work ID if present, otherwise record the hard dependency explicitly before adding one.
3. Create/copy a fresh isolated proof Sheet from that verified published release.
4. Surface the one unavoidable user action only if the host cannot invoke the custom Sheet menu itself: **MIRA → Enable Android / shared access**.
5. Read back Commands + Metadata, submit one synthetic entity command, and verify actual worker result/Resource/Idempotency state.
6. Reconcile BACKLOG lifecycle evidence, close `ANDROID-COMMAND-BOUNDARY-001`, then start `ANDROID-CLIENT-CORE-001`.

## Recovery protocol

Read this file first, then `FEATURES.md`, `BACKLOG.md`, `ROADMAP.md`, and `PRODUCT_INVARIANTS.md`. Active work is resumed `M2-M1-001` / `ANDROID-COMMAND-BOUNDARY-001` on `integration/m1-001-live-worker-proof`, based on main `2be8ccefd8ada72dc31bfd2f4df1c560ca22f483`. The immediate code defect is the missing ordinary-user shared-access activation control; its fix and regression test are on this branch. The hard remaining live-proof dependency is publishing the corrected bound Apps Script release into an isolated Google proof substrate without making the ordinary user do developer work.
