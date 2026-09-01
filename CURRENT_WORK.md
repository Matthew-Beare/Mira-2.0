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

**ALIGNED.** Resume the existing `M2-M1-001` packet. The ordinary-user activation defect is now merged; next prove a maintainer-only Apps Script publication seam, then use a fresh isolated published Sheet to execute one real queued-worker command end-to-end. Do not touch legacy production state.

## Active packet

### `M2-M1-001` — Concurrent canonical command boundary, live Google proof

- **Primary work:** `ANDROID-COMMAND-BOUNDARY-001`
- **Primary features:** `CLIENT-ANDROID-001`, `API-001`
- **Related invariants/features:** `AUTH-001`, `STORE-001`, `RECOVERY-002`, `ONBOARD-006`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `integration/m1-001-apps-script-publication`
- **Base/main SHA:** `b6b7455422608dc0308f1e8634c33c2e7291e7d0`
- **Prior implementation:** PR #54 provider-neutral sequencer; PR #55 Workspace `Commands` inbox + `ScriptLock` worker; PR #91 ordinary-user shared-access activation surface.
- **Dependencies:** isolated synthetic Google Workspace substrate; verified bound Apps Script publication containing current repository runtime.
- **Current blocker:** this ChatGPT host's connected Google Drive/Sheets surface does not expose Apps Script project publication or arbitrary custom-function invocation. A maintainer-only Apps Script API publisher is being implemented so the release process can bind verified Git content to a disposable/official starter without exporting developer work to the Personal user.

## Objective

Prove the existing queued-writer architecture against a fresh isolated Google Workspace copy using an ordinary-user activation path: publish the verified bound runtime, enable Android/shared access without Apps Script-editor work, enqueue a synthetic API-001 command, observe the real time-driven worker serialize and commit it, and verify exact canonical/idempotency/result readback.

## Acceptance criteria

1. Use only a fresh isolated synthetic Sheet; legacy MIRA production Sheets, briefs, Calendars, automations, and user operational data are not fixtures.
2. The verified bound Apps Script release exposes `MIRA → Enable Android / shared access`; no normal user opens Apps Script or manually runs `miraEnableQueuedWriter()`.
3. Maintainer publication uses an explicit Google Apps Script API boundary with credentials external to Git, binds the project to the exact intended Sheet, replaces complete HEAD runtime content, and exact-reads it back before success.
4. Publication must not persist or log access tokens, provider IDs, or user/private state into the public repository.
5. Activation creates/validates exactly one one-minute worker trigger before persisted `mutation_mode=queued_writer` becomes authoritative.
6. Activation creates the canonical `Commands` transport tab and persists queued-writer mode.
7. Submit one synthetic same-user API-001 `entity` upsert command through the authenticated Google Sheet surface with stable command/idempotency IDs and expected revision 0.
8. The actual Google time-driven worker processes the pending command under `ScriptLock`.
9. Success is recorded only after exact Resource + Idempotency readback; the new entity is revision 1 and matches submitted payload/material.
10. Re-reading the command shows a durable succeeded result rather than assuming scheduler execution.
11. No independent direct-native canonical mutation path remains active after queued mode is authoritative.
12. Record only generic/synthetic provider evidence in public Git.
13. Exact-head CI, expected-head merge, remote readback, and post-merge CI are required for source changes.
14. Reconcile the stale M2-M0-029 `HOST-CONNECT-EXEC-001` BACKLOG row before packet closure.
15. After live proof, mark `ANDROID-COMMAND-BOUNDARY-001` only to the evidence actually demonstrated and start `ANDROID-CLIENT-CORE-001`.

## Completed evidence in this resumed packet

### Ordinary-user activation surface

PR #91 merged at `b6b7455422608dc0308f1e8634c33c2e7291e7d0` after exact-head CI `33547638096` passed. Post-merge main CI `33547715540` passed. `Code.gs` now exposes `MIRA → Enable Android / shared access` through `miraEnableQueuedWriterFromMenu()`, delegating to the already-tested worker activation while keeping internal queued-writer jargon out of the menu. Regression coverage is durable in both Python and Apps Script tests.

### Live isolated substrate prepared

A fresh copy was created from a post-PR-55 Personal proof Sheet:

- title: `MIRA M2-M1-001 Live Queued Writer Proof - 2026-09-01 - NOT A STARTER`
- Google Sheet ID is intentionally not committed to public Git; it remains session/provider evidence only.
- metadata readback proves `environment=mira_2_sandbox`, `data_policy=synthetic_only`, `adapter_contract=STORE-001`, `writer_model=single_writer`.
- canonical Authority is verified/enabled and owned by synthetic subject `synthetic-no-app-user`; `entity` binding exists.
- before activation the copy has Metadata, Resources, Events, and Idempotency tabs and no Commands tab, as expected.

This copy still contains the older bound script and therefore is evidence/substrate only; it is not the corrected live-worker proof target.

## Apps Script publication seam

Current Google documentation confirms the Apps Script API can create a script project bound to a Drive parent via `projects.create(parentId=...)`, replace HEAD content with `projects.updateContent`, and retrieve project content for exact readback. The release seam is maintainer-only and does not change ordinary-user onboarding.

Current branch work:

- `ops/publish_apps_script.py` loads only the default shared runtime (`Code.gs`, `CommandWorker.gs`, `appsscript.json`), canonicalizes the manifest, validates provider IDs, creates a bound project for the explicitly supplied Sheet, replaces HEAD content, and exact-compares provider content readback before reporting success.
- a short-lived Apps Script OAuth access token is accepted only from process environment, never as a CLI argument or repository material;
- provider error bodies are bounded and the tool emits no success identifiers;
- `tests/test_apps_script_publication.py` covers exact create/update/readback sequencing, wrong-parent rejection, provider drift, invalid runtime material, and pre-provider input rejection.

Live Apps Script API publication remains unverified until an authorized maintainer execution surface is available. The current ChatGPT Google connector intentionally does not expose its OAuth token to this publisher.

## Evidence ceiling so far

- Provider-neutral serialized command semantics: test-verified.
- Workspace worker implementation and fake-Apps-Script execution: test-verified in PR #55.
- Ordinary-user shared-access activation surface: merged/test-verified in PR #91; post-merge main green.
- Fresh isolated Google Sheet substrate and canonical metadata/Authority readback: live provider-readback verified.
- Maintainer Apps Script publication protocol: implemented on current branch; CI/merge pending.
- Actual Apps Script API publication, trigger creation/firing, and queued command execution: **not yet live-verified**.

## Exact next action / resume point

1. Run exact-head CI for the Apps Script publisher and merge only if green; verify post-merge main.
2. Resolve an authorized maintainer execution surface for the Apps Script API without exposing a user/provider token to Git or ordinary-user setup. Prefer a product/release-owned authorization flow over manual developer-console work.
3. Create a fresh isolated Google Sheet and publish the verified bound runtime to it using the new publisher; exact-read back the provider script content.
4. Surface the one unavoidable user action only if the host cannot invoke the custom Sheet menu itself: **MIRA → Enable Android / shared access**.
5. Read back Commands + Metadata, submit one synthetic entity command, and verify actual worker result/Resource/Idempotency state.
6. Reconcile BACKLOG lifecycle evidence, close `ANDROID-COMMAND-BOUNDARY-001`, then start `ANDROID-CLIENT-CORE-001`.

## Recovery protocol

Read this file first, then `FEATURES.md`, `BACKLOG.md`, `ROADMAP.md`, and `PRODUCT_INVARIANTS.md`. Active work is `M2-M1-001` / `ANDROID-COMMAND-BOUNDARY-001` on `integration/m1-001-apps-script-publication`, based on green main `b6b7455422608dc0308f1e8634c33c2e7291e7d0`. PR #91 already fixed and merged the missing Personal activation control. Resume at exact-head CI for the maintainer-only Apps Script publication seam, then obtain a safe authorized execution surface and perform the fresh isolated live worker proof. Do not make an ordinary user open Apps Script or paste/run code.
