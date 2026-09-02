# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and exact recovery state.

## Product direction

Default Personal MIRA remains stock ChatGPT + Google Workspace with no external infrastructure prerequisite. When Android or another software writer is enabled, direct independent Google Sheets mutation must stop; commands use the serialized shared command boundary. Ordinary users must not open Apps Script, paste code, manage triggers, copy provider IDs, or understand queued-writer internals merely to enable Android/shared access.

Pre-Android feature growth remains frozen except for this hard shared-writer proof. After this packet reaches its live Google evidence ceiling, start `ANDROID-CLIENT-CORE-001`.

## Session-start alignment verification — 2026-09-02 M2-M1-001 provider-proof handoff

### `FEATURES.md`

- `CLIENT-ANDROID-001`, `API-001`, `AUTH-001`, `STORE-001`, and `RECOVERY-002` still require one safe shared canonical mutation boundary rather than independent read-then-write clients.
- Default Personal remains stock ChatGPT + Personal Google Workspace first. The shipped background canonical runtime legitimately requires full Sheets scope because it reopens the initialized canonical Sheet by ID; optional Calendar/provider scopes remain absent.

### `BACKLOG.md`

- `ANDROID-COMMAND-BOUNDARY-001` remains the active hard prerequisite until a real Google time-driven worker processes a synthetic command and exact Resource/Idempotency/command-result state is read back.
- `ANDROID-CLIENT-CORE-001` remains queued immediately after this proof.
- `HOST-CONNECT-EXEC-001` was completed in M2-M0-029 / PR #90 but its stale backlog row still requires closure reconciliation before this packet closes.

### `ROADMAP.md`

- M2-M1 remains blocked only on live shared-writer provider proof, not on new concurrency architecture or unrelated feature growth.
- Android client implementation follows immediately after this packet closes.

### Direction result

**ALIGNED.** Normal-mode source work for the live Apps Script permission blocker is complete and green. Resume only at the provider-owned existing-project republish/activation/worker proof, using the already-created disposable synthetic proof target and never touching legacy MIRA data.

## Active packet

### `M2-M1-001` — Concurrent canonical command boundary, live Google proof

- **Primary work:** `ANDROID-COMMAND-BOUNDARY-001`
- **Primary features:** `CLIENT-ANDROID-001`, `API-001`
- **Related invariants/features:** `AUTH-001`, `STORE-001`, `RECOVERY-002`, `ONBOARD-006`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Checkpoint branch:** `governance/m1-001-scope-fix-merged-checkpoint`
- **Current green main SHA:** `72c273c7833eb2f0c53efd744c3b60b9a8d4e730`
- **Dependencies:** existing fresh isolated synthetic Google Sheet; already-authorized private maintainer Google identity; existing bound Apps Script project; Apps Script API/provider browser access.

## Objective

Complete the existing queued-writer proof against the one existing disposable Google Workspace target: republish the corrected verified runtime to the already-bound Apps Script project, activate Android/shared access through the ordinary-user menu, enqueue one synthetic API-001 command, observe the real time-driven worker serialize and commit it, and verify exact canonical/idempotency/result readback.

## Live provider evidence already established

A Work-mode session successfully completed the private Google authorization and initial Apps Script publication to the existing disposable M2-M1-001 proof target with exact bound-project/provider HEAD readback. No legacy MIRA data was touched.

Shared-access activation then failed with:

`Exception: Specified permissions are not sufficient to call SpreadsheetApp.openById. Required permission: https://www.googleapis.com/auth/spreadsheets`

That evidence proved publication/binding succeeded and isolated the remaining blocker to a source manifest/runtime mismatch.

## Scope-fix evidence

PR #95 fixed that blocker and is fully merged/green:

- `workspace/apps_script/appsscript.json` now grants `https://www.googleapis.com/auth/spreadsheets` instead of insufficient `spreadsheets.currentonly` and still grants only the required `script.scriptapp` trigger scope beyond it; optional Calendar/provider scopes remain absent.
- `tests/test_apps_script_publication.py` now regression-tests that the shipped `SpreadsheetApp.openById` runtime has the required full Sheets scope and cannot regress to `spreadsheets.currentonly`.
- `mira/workspace_bundle.py` now enforces the same runtime/manifest contract rather than the stale current-Sheet-only invariant.
- The first PR #95 CI run `33595772517` exposed the stale starter-scope invariant.
- The second CI run `33595908558` passed that gate and exposed a missing session-alignment section in the checkpoint.
- Final exact-head PR SHA `e8df4e3eade9aada0561aea26a4d6ed880beaf7b` passed CI `33595975370`, including compile, feature registry, lifecycle ledger, Personal starter distribution, work-session alignment, code ownership, Python unit tests, and Workspace Apps Script tests.
- PR #95 merged only at that expected head. Remote main readback is `72c273c7833eb2f0c53efd744c3b60b9a8d4e730`.
- Post-merge main CI `33596012057` completed successfully.

## Existing disposable proof target constraints

- Use only the already-created fresh disposable M2-M1-001 synthetic Sheet and its already-bound Apps Script project.
- Do **not** rerun the fresh-publication path that creates another Apps Script project.
- Do not create a second Sheet/project merely to avoid updating the existing project.
- Provider Sheet/script IDs, OAuth refresh material, and access tokens remain private session/provider evidence and must never be committed to public Git.
- Legacy MIRA production Sheets, briefs, Calendars, automations, Drive data, and operational state remain protected and must not be fixtures.

Previously verified substrate remains synthetic-only, `Etc/UTC`, with canonical Metadata/Resources/Events/Idempotency state and synthetic same-user Authority owner `m1-live-synthetic-user`. The failed activation occurred before successful queued-writer activation, so live trigger firing and queued command execution are still unverified.

## Acceptance criteria remaining

1. Republish the corrected runtime only to the existing bound Apps Script project and independently verify exact parent binding plus exact provider HEAD readback.
2. Preserve private OAuth/provider identifiers outside public Git.
3. Ordinary-user activation uses `MIRA → Initialize this copy` only if the existing script property is not already persisted, then `MIRA → Enable Android / shared access`; no Apps Script editor/internal-function ritual.
4. Activation creates/validates exactly one one-minute worker trigger before `mutation_mode=queued_writer` becomes authoritative.
5. Activation creates the canonical `Commands` tab and persists queued-writer mode.
6. Submit one synthetic same-user API-001 `entity` upsert with stable command/idempotency IDs and expected revision 0.
7. The actual Google time-driven worker processes the command under `ScriptLock`.
8. Exact readback proves command status `succeeded`, durable result material, Resource revision 1 with exact submitted payload, and matching Idempotency material.
9. No independent direct-native canonical mutation path remains active after queued mode is authoritative.
10. Record only generic/synthetic provider evidence in public Git.
11. Reconcile the stale `HOST-CONNECT-EXEC-001` BACKLOG row before packet closure.
12. Close `ANDROID-COMMAND-BOUNDARY-001` only to the evidence actually demonstrated, then immediately start `ANDROID-CLIENT-CORE-001`.

## Exact next action / resume point

1. Switch only the provider portion back to ChatGPT Work mode because normal mode has no Apps Script API/browser execution surface.
2. In Work, read this `CURRENT_WORK.md` first and verify main `72c273c7833eb2f0c53efd744c3b60b9a8d4e730`.
3. Recover the privately known existing bound Apps Script project from the successful prior Work publication. Do not create a new project.
4. Republish main's corrected runtime using the existing-project publication path (`publish_existing_runtime` / equivalent provider API update), requiring exact parent and exact provider HEAD readback.
5. Activate shared access in the existing disposable Sheet; satisfy any new Google consent caused by the corrected Sheets scope, then verify one trigger + `Commands` + queued mode.
6. Submit the stable synthetic same-user entity command, observe actual scheduler execution, and exact-read Commands/Resources/Idempotency.
7. As soon as provider/browser-only work is finished, explicitly return to normal ChatGPT mode for Git closure, BACKLOG reconciliation, packet closeout, and `ANDROID-CLIENT-CORE-001` startup.

## Recovery protocol

Read this file first, then `FEATURES.md`, `BACKLOG.md`, `ROADMAP.md`, and `PRODUCT_INVARIANTS.md`. Active work is `M2-M1-001` / `ANDROID-COMMAND-BOUNDARY-001`. Source fix PR #95 is merged and post-merge green on main `72c273c7833eb2f0c53efd744c3b60b9a8d4e730`. Normal-mode work is complete to its current capability ceiling. Resume only with the existing-project Google republish/activation/live scheduler proof in Work mode, then return to normal mode for Git closure. Never touch legacy MIRA data or expose provider IDs/OAuth material in public Git.
