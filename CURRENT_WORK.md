# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and exact recovery state.

## Product direction

Default Personal MIRA remains stock ChatGPT + Google Workspace with no external infrastructure prerequisite. When Android or another software writer is enabled, direct independent Google Sheets mutation must stop; commands use the serialized shared command boundary. Ordinary users must not open Apps Script, paste code, manage triggers, copy provider IDs, or understand queued-writer internals merely to enable Android/shared access.

Pre-Android feature growth remains frozen except for this hard shared-writer proof. After this packet reaches its live Google evidence ceiling, start `ANDROID-CLIENT-CORE-001`.

## Active packet

### `M2-M1-001` — Concurrent canonical command boundary, live Google proof

- **Primary work:** `ANDROID-COMMAND-BOUNDARY-001`
- **Primary features:** `CLIENT-ANDROID-001`, `API-001`
- **Related invariants/features:** `AUTH-001`, `STORE-001`, `RECOVERY-002`, `ONBOARD-006`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `fix/m1-001-apps-script-spreadsheet-scope`
- **Base/main SHA:** `019b205fb2c3c405e8c5ba33f1c81d43dcf44e60`
- **Dependencies:** existing fresh isolated synthetic Google Sheet; existing private maintainer Google authorization; Apps Script API availability.

## Objective

Prove the existing queued-writer architecture against the existing fresh isolated Google Workspace proof target using the ordinary-user activation path: publish the verified bound runtime, initialize the copy, enable Android/shared access without Apps Script-editor work, enqueue one synthetic API-001 command, observe the real time-driven worker serialize and commit it, and verify exact canonical/idempotency/result readback.

## New live provider evidence — 2026-09-02

Work-mode provider authorization and Apps Script publication succeeded against the existing disposable M2-M1-001 proof target with exact provider readback. No legacy MIRA data was touched.

The subsequent ordinary-user shared-access activation failed with the provider error:

`Exception: Specified permissions are not sufficient to call SpreadsheetApp.openById. Required permission: https://www.googleapis.com/auth/spreadsheets`

Source inspection confirms the failure is a runtime/manifest contract mismatch rather than an authorization or binding failure:

- `workspace/apps_script/Code.gs` persists the bound spreadsheet ID in script properties during `miraInitializeCopy()` and `miraSpreadsheet_()` later reopens that exact spreadsheet with `SpreadsheetApp.openById(id)` so background/time-driven executions remain bound to the canonical Sheet.
- `workspace/apps_script/appsscript.json` currently declares only `https://www.googleapis.com/auth/spreadsheets.currentonly` plus `https://www.googleapis.com/auth/script.scriptapp`.
- `spreadsheets.currentonly` is insufficient for `SpreadsheetApp.openById`; the runtime therefore requires `https://www.googleapis.com/auth/spreadsheets`.
- The earlier Apps Script publication proof remains valid: publication, exact bound-project parent verification, and exact provider HEAD readback succeeded before activation reached this runtime permission boundary.

This is the current active acceptance blocker and outranks unrelated feature work under green-before-growth.

## Acceptance criteria

1. Use only the existing fresh isolated synthetic Sheet for this proof; legacy MIRA production Sheets, briefs, Calendars, automations, and user operational data are not fixtures.
2. The verified bound Apps Script release exposes `MIRA → Initialize this copy` and `MIRA → Enable Android / shared access`; no normal user opens Apps Script or manually runs an internal function.
3. Maintainer publication uses explicit Apps Script API operations with credentials external to Git, binds to the exact requested Sheet, and independently reads back `Project.parentId` before content mutation.
4. Publication replaces the complete approved runtime and exact-reads provider HEAD before success.
5. OAuth refresh material and ephemeral access tokens are never committed, emitted as workflow outputs, or printed by release tooling.
6. Republish for this defect fix targets only the already-created disposable proof Sheet; do not create or bind a second proof target.
7. Manifest scopes must authorize the APIs actually used by the runtime, including `SpreadsheetApp.openById`, while remaining no broader than required by this implementation.
8. Activation creates/validates exactly one one-minute worker trigger before persisted `mutation_mode=queued_writer` becomes authoritative.
9. Activation creates the canonical `Commands` transport tab and persists queued-writer mode.
10. Submit one synthetic same-user API-001 `entity` upsert command with stable command/idempotency IDs and expected revision 0.
11. The actual Google time-driven worker processes the pending command under `ScriptLock`.
12. Success is recorded only after exact Resource + Idempotency readback; the new entity is revision 1 and matches submitted material.
13. Re-reading the command shows a durable succeeded result rather than assuming scheduler execution.
14. No independent direct-native canonical mutation path remains active after queued mode is authoritative.
15. Record only generic/synthetic provider evidence in public Git; provider IDs and OAuth material remain private session/release evidence.
16. Exact-head CI, expected-head merge, remote readback, and post-merge CI are required for source changes.
17. Reconcile the stale M2-M0-029 `HOST-CONNECT-EXEC-001` BACKLOG row before packet closure.
18. After live proof, mark `ANDROID-COMMAND-BOUNDARY-001` only to the evidence actually demonstrated and start `ANDROID-CLIENT-CORE-001`.

## Completed evidence

### Shared writer and activation

- PR #54: provider-neutral serialized command sequencer.
- PR #55: Workspace `Commands` inbox + `ScriptLock` worker, synthetic/fake-provider verified.
- PR #91 merged at `b6b7455422608dc0308f1e8634c33c2e7291e7d0`; exact-head CI `33547638096` and post-merge CI `33547715540` green. `Code.gs` exposes ordinary-user initialization and shared-access activation through the Sheet `MIRA` menu.

### Apps Script publication and private release authorization

- PR #92 merged at `bbea10ce0a4d52b3ddbe330621c9e5af37d9d5a9`; post-merge CI `33548158788` green. Direct Apps Script create/binding/content exact-readback protocol is test-verified.
- PR #93 merged at `f40e4801634a4da0450e3c94a7bbaad97137e14f`; exact-head CI `33550835232` green and post-merge CI `33550883206` green.
- PR #94 merged into green main at `019b205fb2c3c405e8c5ba33f1c81d43dcf44e60`; it checkpointed the fresh disposable live Google proof target without exposing provider IDs.
- 2026-09-02 Work-mode execution established the private Google authorization, published the runtime to that existing disposable proof target, independently verified the bound project/provider content, and then exposed the `openById` scope mismatch during activation.

### Fresh live Google proof target

The existing disposable Google Sheet remains the only allowed live target for this packet. Its provider ID and OAuth material remain private and are intentionally not recorded in public Git.

Previously verified substrate remains:

- isolated synthetic M2-M1 proof data only;
- timezone `Etc/UTC`;
- `Metadata`, `Resources`, `Events`, and `Idempotency` tabs before successful queued-writer activation;
- Metadata declares `schema_version=mira-structured-state-v1`, `environment=mira_2_sandbox`, `data_policy=synthetic_only`, `adapter_contract=STORE-001`, and `writer_model=single_writer`;
- Resources contains one verified/enabled synthetic Google Sheets Authority plus the synthetic `entity` Authority binding;
- Authority owner is `m1-live-synthetic-user`;
- no legacy production data is present.

## Evidence ceiling

- Provider-neutral serialized command semantics: test-verified.
- Workspace worker implementation: test-verified.
- Ordinary-user initialization/shared-access menu surface: merged/test-verified.
- Apps Script direct publication protocol: merged/test-verified.
- Private authorization and publication to the existing disposable proof target: **live provider verified**.
- Exact bound-project/provider HEAD readback: **live provider verified**.
- Shared-access activation: **live attempted and blocked specifically by manifest scope mismatch**.
- Trigger creation/firing and queued command execution: **not yet live-verified**.

## Exact next action / resume point

1. On `fix/m1-001-apps-script-spreadsheet-scope`, replace `spreadsheets.currentonly` with the full `https://www.googleapis.com/auth/spreadsheets` scope because the shipped runtime explicitly requires `SpreadsheetApp.openById` for background canonical access.
2. Add/adjust tests so the manifest contract fails if `openById` is present without full spreadsheet scope, while continuing to require the trigger-management scope.
3. Run the repository test gates and exact-head CI; merge only expected head after green.
4. Republish the corrected approved runtime only to the existing disposable proof target and exact-read provider HEAD again. Do not create a new Sheet/project target.
5. Re-run ordinary-user initialization if the script property was not already persisted, then `MIRA → Enable Android / shared access`; verify exactly one one-minute trigger, `Commands`, and `mutation_mode=queued_writer`.
6. Submit the stable synthetic same-user entity upsert, observe the actual scheduler worker, and exact-read `Commands`, `Resources`, and `Idempotency` proving durable succeeded result, revision 1, exact payload, and idempotency material.
7. Reconcile stale `HOST-CONNECT-EXEC-001` BACKLOG state, close this packet to the actual evidence ceiling, and immediately start `ANDROID-CLIENT-CORE-001`.

## Recovery protocol

Read this file first, then `FEATURES.md`, `BACKLOG.md`, `ROADMAP.md`, and `PRODUCT_INVARIANTS.md`. Active work is `M2-M1-001` / `ANDROID-COMMAND-BOUNDARY-001` on `fix/m1-001-apps-script-spreadsheet-scope`, based on green main `019b205fb2c3c405e8c5ba33f1c81d43dcf44e60`. Private authorization and Apps Script publication to the one existing disposable proof target are live-verified. Resume at the manifest/runtime scope fix for `SpreadsheetApp.openById`, then CI/merge, republish only to that target, activate queued writer, and prove one real scheduler-processed command. Never touch legacy MIRA data or expose provider IDs/OAuth material in public Git.
