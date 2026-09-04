# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active/recovery packet and exact recovery state.

## Product direction

Default Personal MIRA remains stock ChatGPT + Google Workspace first. Android extends the same canonical reality without becoming a second authority. M2-M1-001 through M2-M1-009 are durably closed. `ANDROID-SYNC` remains partial only because stock ChatGPT has not yet been proven to read an Android-originated canonical mutation back from the same authority; representative-device proof remains a later, separate evidence step.

## Prior-packet recovery verification — 2026-09-04

- Repository: `Matthew-Beare/Mira-2.0`.
- Authoritative `main` before M2-M1-010: `a7238151a08734b51e1ffa3386a5b672a73c46c0`.
- M2-M1-009 final closeout CI: `33900587999` — success on that exact head.
- Remote `main` independently read back the same SHA.
- M2-M1-001 through M2-M1-009 and M2-GOV-012 are durably closed and must not be rerun.

## Session-start alignment verification — 2026-09-04 M2-M1-010

### `FEATURES.md`

- `CLIENT-ANDROID-001` remains `specified+implemented+test_verified+partial`.
- `API-001`, `AUTH-001`, `STORE-001`, and `RECOVERY-002` require one canonical authority, exact verified readback, and client-neutral state semantics.
- Canonical truth must not depend on which client authored a mutation.

### `BACKLOG.md`

- `ANDROID-CLIENT-CORE-001` is partial through M2-M1-009.
- `ANDROID-SYNC` is partial through M2-M1-009: canonical Android read/freshness and deterministic queued mutation are complete; stock-ChatGPT cross-readback remains.
- The next unfinished dependency is stock ChatGPT reading the Android-originated mutation from the same canonical Google-backed authority.

### `ROADMAP.md`

- M2-M1 ordered proof step 7 is stock ChatGPT reading the Android mutation back from the same authority.
- Representative-device proof is step 8 and remains separate unless this packet discovers a hard dependency.

### `PRODUCT_INVARIANTS.md`

- One canonical authority remains authoritative regardless of client origin.
- Default Personal stays stock ChatGPT + Google Workspace first.
- Ordinary-user provider setup must not require copied IDs, developer consoles, scripts, or terminal work.
- Provider/readback evidence must remain truthful; deterministic repository proof cannot be mislabeled as live host/provider proof.

### Direction result

**ALIGNED.** M2-M1-010 is bounded to the stock-ChatGPT cross-readback child of `ANDROID-SYNC`: prove that an Android-shaped queued command is executed by the existing serialized Workspace writer into canonical `Resources`, then the existing stock-ChatGPT Workspace query contract reads that exact canonical revision/payload through the same persisted Authority binding. Do not add a second read engine, broaden Android UI, perform representative-device proof, or touch legacy production state.

## Active packet

### `M2-M1-010` — Stock ChatGPT cross-readback of Android canonical mutation

- **Primary work:** `ANDROID-SYNC`
- **Primary features:** `CLIENT-ANDROID-001`, `API-001`
- **Related invariants/features:** `AUTH-001`, `STORE-001`, `RECOVERY-002`, `DATA-001`, `PROVIDER-002`
- **Related work:** `CHATGPT-API-CLIENT-001`, `CORE-ROUNDTRIP`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Implementation branch:** `work/m2-m1-010-stock-chatgpt-cross-readback`
- **Packet base SHA:** `a7238151a08734b51e1ffa3386a5b672a73c46c0`
- **Activation SHA:** `151bb3e0853fbbbe172ac7df81cb6c3864d0283f`
- **Cross-readback test head:** `e3483a95adbf6dd24e940834486768001c0576ad`
- **Status:** active implementation; first CI blocked only by corrected alignment metadata before test execution

## Objective

Prove client-origin neutrality across the existing default-Personal Google Workspace boundary without inventing new canonical state or a second stock-ChatGPT read path.

The bounded proof must:

1. use the existing `Commands` row shape accepted by `GoogleWorkspaceTransport` / `CommandWorker.gs` as the Android-originated mutation boundary;
2. execute that command through the existing queued writer, not by directly editing canonical `Resources` in the proof;
3. require successful worker canonical readback before treating the mutation as persisted;
4. query the resulting entity through the existing stock-ChatGPT `/v1/query` Workspace read contract in `Code.gs`;
5. resolve the same persisted Authority/Authority-binding records used by the no-app Personal path;
6. return the exact resource type, ID, revision and payload written by the worker;
7. demonstrate that read success is independent of command/client provenance and does not consult Android local cache or the nonauthoritative `Changes` projection;
8. fail closed for missing/duplicate authority or resource identity, stale/failed queued mutation, or malformed provider state;
9. preserve direct-native write prohibition while queued mode is active;
10. distinguish deterministic repository integration evidence from any later live stock-ChatGPT/provider proof.

## Acceptance criteria

1. One deterministic cross-readback integration test/harness exercises both `CommandWorker.gs` and the existing `Code.gs` query path against one shared synthetic Workbook state.
2. The synthetic queued command uses the exact 16-column Android Workspace command protocol and a same-user subject/authority owner.
3. The worker mutates canonical `Resources` and records terminal success/readback through existing production code; the test does not pre-seed the target post-mutation Resource.
4. Stock-ChatGPT query reads the resulting exact canonical record through `/v1/query` and the persisted entity Authority binding.
5. Exact returned revision and canonical payload match the worker's persisted Resource and terminal command result.
6. Query success does not require or inspect `Changes`, Android offline cache, or Android-only state.
7. Queued-mode metadata remains compatible with read queries while direct native mutation remains prohibited.
8. A failed/stale queued command cannot be represented as successful cross-readback evidence.
9. Existing Apps Script, native Workspace, Android, Python, lifecycle and ownership suites remain green.
10. No Work mode, live provider mutation, legacy MIRA production data, historical disposable M2-M1-001 resource, private provider identifier, token, credential, or secret is used for deterministic implementation/test evidence.
11. Before merge, re-read FEATURES/BACKLOG/ROADMAP/invariants and keep representative-device/live-host evidence explicitly separate.
12. Expected-head merge, remote-main readback, post-merge CI, lifecycle reconciliation and final closeout CI are required before durable closure.

## Completed evidence

- M2-M1-009 durably closed on exact main `a7238151a08734b51e1ffa3386a5b672a73c46c0` with final CI `33900587999` green.
- Fresh canonical lifecycle review identifies stock-ChatGPT cross-readback as M2-M1 step 7 and the next unfinished dependency.
- `workspace/apps_script/Code.gs` already resolves canonical reads through persisted `authority_binding` + verified/enabled Google Sheets Authority and reads `Resources`; it does not use Android cache or Changes.
- `workspace/apps_script/CommandWorker.gs` already owns queued-mode canonical mutation, same-user authority validation, exact readback and Changes projection.
- Queued-writer activation stores `mutation_mode=queued_writer`; the stock-ChatGPT schema/read contract continues to use `writer_model=single_writer`, so queued mutation does not inherently invalidate read queries.
- Existing `workspace_read.test.js` proves exact canonical query behavior for persisted Resources, but does not yet prove a Resource created/updated by the queued Android/shared-client writer can be read by that same query path.
- `android_cross_readback.test.js` now adds the missing shared-runtime proof without changing production code.
- First PR CI `33901154860` stopped at Work-session alignment before Apps Script tests because `CHATGPT-API-CLIENT-001` and `CORE-ROUNDTRIP` were incorrectly placed in the feature-only `Related invariants/features` field; this checkpoint corrects only that taxonomy and preserves them as related work.

## Explicitly deferred

- Live Android Google authorization and physical-device mutation execution.
- Live stock-ChatGPT/provider cross-readback, unless deterministic work is green and this packet reaches a genuinely narrow live acceptance ceiling.
- Representative-device proof.
- User-facing conflict-resolution UI and broad Connections/app-shell polish.
- Release signing/distribution, notifications/TTS, capture paths, unrelated providers, and legacy-data migration.

## Session-end alignment verification — pending

### `FEATURES.md`

Pending final evidence review. `CLIENT-ANDROID-001` must not be promoted solely by deterministic cross-readback.

### `BACKLOG.md`

Pending final lifecycle review. `ANDROID-SYNC` may become complete only if the packet's accepted cross-readback evidence ceiling is actually satisfied; live/device evidence gaps must remain separately truthful.

### `ROADMAP.md`

Pending final confirmation of step 7 evidence and whether representative-device proof remains step 8.

### Direction result

**PENDING IMPLEMENTATION + EXACT-HEAD CI.**

## Exact next action / resume point

1. Run CI again after the alignment-field correction.
2. If the cross-readback Apps Script integration test reaches execution, repair only packet-scoped failures.
3. Change production code only if that integration test exposes a real contract incompatibility.
4. Re-read canonical lifecycle authorities before merge.
5. Do not use Work mode until deterministic cross-readback implementation/tests are green and a narrow live provider/host acceptance proof genuinely remains.

## Recovery protocol

Read this file first. Verify branch `work/m2-m1-010-stock-chatgpt-cross-readback` against base `a7238151a08734b51e1ffa3386a5b672a73c46c0`. Resume from CI after the alignment taxonomy correction. Do not rerun M2-M1-001 through M2-M1-009 and do not absorb representative-device proof without a hard dependency.