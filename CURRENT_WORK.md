# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and exact recovery state.

## Product direction

Default Personal MIRA remains stock ChatGPT + Google Workspace with no external infrastructure prerequisite. When Android or another software writer is enabled, direct independent Google Sheets mutation must stop; commands use the serialized shared command boundary. Ordinary users must not open Apps Script, paste code, manage triggers, copy provider IDs, or understand queued-writer internals merely to enable Android/shared access.

Pre-Android feature growth remains frozen except for this hard shared-writer proof. After this packet reaches its live Google evidence ceiling, start `ANDROID-CLIENT-CORE-001`.

## Session-start alignment verification — 2026-09-01 M2-M1-001 release-auth resume

### `FEATURES.md`

- `CLIENT-ANDROID-001`, `API-001`, `AUTH-001`, `STORE-001`, and `RECOVERY-002` require one safe shared canonical mutation boundary rather than independent read-then-write clients.
- Default Personal setup remains no-terminal/no-developer-console when software can provide an ordinary-user control.

### `BACKLOG.md`

- `ANDROID-COMMAND-BOUNDARY-001` remains partial: provider-neutral sequencer, Workspace worker, ordinary-user activation surface, and maintainer publication protocol are test/integration verified; live isolated Google trigger/worker proof remains pending.
- `ANDROID-CLIENT-CORE-001` is queued immediately after this live proof.
- `HOST-CONNECT-EXEC-001` was implemented/live-host-proven in M2-M0-029 / PR #90, but its stale BACKLOG status row still requires closure reconciliation before this packet closes.

### `ROADMAP.md`

- M2-M1 is blocked on live shared-writer proof, not on another concurrency architecture.
- Android client implementation follows this packet; unrelated provider expansion remains deferred.

### Direction result

**ALIGNED.** Resume `M2-M1-001`. Complete a private maintainer authorization/release lane, then use a fresh isolated Sheet to prove one real queued-worker command end-to-end. Do not touch legacy production state.

## Active packet

### `M2-M1-001` — Concurrent canonical command boundary, live Google proof

- **Primary work:** `ANDROID-COMMAND-BOUNDARY-001`
- **Primary features:** `CLIENT-ANDROID-001`, `API-001`
- **Related invariants/features:** `AUTH-001`, `STORE-001`, `RECOVERY-002`, `ONBOARD-006`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `integration/m1-001-clasp-release`
- **Base/main SHA:** `bbea10ce0a4d52b3ddbe330621c9e5af37d9d5a9`
- **Prior implementation:** PR #54 provider-neutral sequencer; PR #55 Workspace `Commands` inbox + `ScriptLock` worker; PR #91 ordinary-user shared-access activation surface; PR #92 direct Apps Script publication seam.
- **Dependencies:** fresh isolated synthetic Google Sheet; one private maintainer Google authorization credential; Apps Script API availability.
- **Current blocker:** live Google authorization has not yet been granted to the maintainer release identity. This ChatGPT host's Google connector does not expose its OAuth token or Apps Script project actions, so the release credential must be established once through a provider-native Google authorization flow and stored privately outside Git.

## Objective

Prove the existing queued-writer architecture against a fresh isolated Google Workspace copy using an ordinary-user activation path: privately publish the verified bound runtime, enable Android/shared access without Apps Script-editor work, enqueue a synthetic API-001 command, observe the real time-driven worker serialize and commit it, and verify exact canonical/idempotency/result readback.

## Acceptance criteria

1. Use only a fresh isolated synthetic Sheet; legacy MIRA production Sheets, briefs, Calendars, automations, and user operational data are not fixtures.
2. The verified bound Apps Script release exposes `MIRA → Enable Android / shared access`; no normal user opens Apps Script or manually runs an internal function.
3. Maintainer publication uses explicit Apps Script API operations with credentials external to Git, binds to the exact requested Sheet, and independently reads back `Project.parentId` before content mutation.
4. Publication replaces the complete approved runtime and exact-reads provider HEAD before success.
5. OAuth refresh material and ephemeral access tokens are never committed, emitted as workflow outputs, or printed by release tooling.
6. The release workflow requires an explicit fresh/disposable target confirmation so an accidental rerun cannot silently be treated as an upgrade path.
7. Activation creates/validates exactly one one-minute worker trigger before persisted `mutation_mode=queued_writer` becomes authoritative.
8. Activation creates the canonical `Commands` transport tab and persists queued-writer mode.
9. Submit one synthetic same-user API-001 `entity` upsert command with stable command/idempotency IDs and expected revision 0.
10. The actual Google time-driven worker processes the pending command under `ScriptLock`.
11. Success is recorded only after exact Resource + Idempotency readback; the new entity is revision 1 and matches submitted material.
12. Re-reading the command shows a durable succeeded result rather than assuming scheduler execution.
13. No independent direct-native canonical mutation path remains active after queued mode is authoritative.
14. Record only generic/synthetic provider evidence in public Git.
15. Exact-head CI, expected-head merge, remote readback, and post-merge CI are required for source changes.
16. Reconcile the stale M2-M0-029 `HOST-CONNECT-EXEC-001` BACKLOG row before packet closure.
17. After live proof, mark `ANDROID-COMMAND-BOUNDARY-001` only to the evidence actually demonstrated and start `ANDROID-CLIENT-CORE-001`.

## Completed evidence

### Shared writer and activation

- PR #54: provider-neutral serialized command sequencer.
- PR #55: Workspace `Commands` inbox + `ScriptLock` worker, synthetic/fake-provider verified.
- PR #91 merged at `b6b7455422608dc0308f1e8634c33c2e7291e7d0`; exact-head CI `33547638096` and post-merge CI `33547715540` green. `Code.gs` now exposes `MIRA → Enable Android / shared access` through the tested worker activation wrapper.

### Apps Script publication seam

- PR #92 merged at `bbea10ce0a4d52b3ddbe330621c9e5af37d9d5a9`; post-merge CI `33548158788` green.
- `ops/publish_apps_script.py` creates a project with Apps Script `projects.create(parentId=...)`, reads `projects.get` to verify the exact parent, replaces complete HEAD with `projects.updateContent`, and exact-reads content back.
- Current branch extends the publisher to consume private clasp 3.x refresh credentials, exchange them for an ephemeral access token without persisting/printing the token, and update a known script only after parent readback.
- Current branch replaces the earlier clasp-heavy deployment draft with `.github/workflows/publish-personal-apps-script.yml`, a fail-closed fresh-release workflow that reads two private secrets (`MIRA_CLASPRC_JSON`, `MIRA_PERSONAL_STARTER_SHEET_ID`), requires explicit fresh-target confirmation, and delegates all provider mutation/readback to the tested Python publisher.
- Current Google/clasp source review found and removed a bad assumption in the first workflow draft: `clasp create-script --parentId` can bind via the Apps Script API but its current JSON output does not populate `parentId` on that path. Binding is therefore verified independently through `projects.get`, not inferred from CLI output.

## Existing live substrate evidence

A prior disposable proof Sheet exists and has synthetic-only canonical metadata/Authority readback, but it contains an older bound script and is not the final live-worker proof target. The final proof must use a fresh isolated Sheet receiving the corrected runtime.

## Evidence ceiling

- Provider-neutral serialized command semantics: test-verified.
- Workspace worker implementation: test-verified.
- Ordinary-user shared-access activation surface: merged/test-verified.
- Apps Script direct publication protocol: merged/test-verified.
- Private refresh-credential release path: implemented on current branch; CI/merge pending.
- Actual authorized Apps Script API publication, trigger creation/firing, and queued command execution: **not yet live-verified**.

## Exact next action / resume point

1. Open a PR for `integration/m1-001-clasp-release`, run exact-head CI, fix any gate failures, and merge only when green; verify post-merge main.
2. Establish the one-time private maintainer Google authorization credential without exposing OAuth material to Git or ordinary-user setup.
3. Create a fresh isolated synthetic Sheet, privately configure the release secrets, dispatch `Publish Fresh Personal Apps Script` once, and verify successful project parent/content readback.
4. Open the fresh Sheet and invoke the only unavoidable ordinary-user-style action if the host cannot invoke the custom menu itself: `MIRA → Enable Android / shared access`.
5. Read back Commands + Metadata, submit one synthetic entity command, and verify actual worker result/Resource/Idempotency state.
6. Reconcile BACKLOG lifecycle evidence, close `ANDROID-COMMAND-BOUNDARY-001`, then start `ANDROID-CLIENT-CORE-001`.

## Recovery protocol

Read this file first, then `FEATURES.md`, `BACKLOG.md`, `ROADMAP.md`, and `PRODUCT_INVARIANTS.md`. Active work is `M2-M1-001` / `ANDROID-COMMAND-BOUNDARY-001` on `integration/m1-001-clasp-release`, based on green main `bbea10ce0a4d52b3ddbe330621c9e5af37d9d5a9`. Resume at PR/CI for the private refresh-credential Apps Script release workflow. After merge, the next hard boundary is the one-time maintainer Google consent required before the fresh isolated live worker proof. Never export Apps Script editing, trigger setup, copied provider IDs, or release credentials to ordinary Personal users.
