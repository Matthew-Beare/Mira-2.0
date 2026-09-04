# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active/recovery packet and exact recovery state.

## Product direction

Default Personal MIRA remains stock ChatGPT + Google Workspace first. Android extends the same canonical reality without becoming a second authority. M2-M1-001 through M2-M1-009 are durably closed. M2-M1-010 now has deterministic integration evidence for the final functional `ANDROID-SYNC` cross-client contract: an Android-shaped queued mutation becomes canonical Workspace state and the existing stock-ChatGPT query path reads that exact state through the same Authority. Live Android authorization/device execution and representative-device evidence remain separate and must not be inferred from this packet.

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

- `ANDROID-CLIENT-CORE-001` was partial through M2-M1-009.
- `ANDROID-SYNC` was partial through M2-M1-009: canonical Android read/freshness and deterministic queued mutation were complete; stock-ChatGPT cross-readback remained.
- Stock ChatGPT reading the Android-originated mutation from the same canonical Google-backed authority was the next unfinished dependency.

### `ROADMAP.md`

- M2-M1 ordered proof step 7 was stock ChatGPT reading the Android mutation back from the same authority.
- Representative-device proof was step 8 and remained separate unless this packet discovered a hard dependency.

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
- **Integration-test SHA:** `e3483a95adbf6dd24e940834486768001c0576ad`
- **Alignment-fix SHA:** `f7bfbda6aed92349f2ea6f8d4def695f37574cc3`
- **Green integration CI:** `33901335696` — success on exact `f7bfbda6aed92349f2ea6f8d4def695f37574cc3`
- **PR:** #110 — open and mergeable before this evidence checkpoint
- **Status:** implementation/test evidence complete; this checkpoint requires exact-head CI before expected-head merge

## Objective result

**COMPLETE AT THE BOUNDED DETERMINISTIC INTEGRATION EVIDENCE CEILING.**

No new production read path was required. The existing queued writer and existing stock-ChatGPT Workspace query path already compose correctly over the same canonical Authority.

1. `android_cross_readback.test.js` loads both production `Code.gs` and `CommandWorker.gs` into one shared synthetic Workbook runtime.
2. The target canonical Resource is absent before the command; the test does not pre-seed the post-mutation state.
3. The test submits the exact 16-column Android Workspace command shape with same-user subject, API/schema, idempotency identity and expected revision.
4. `miraProcessCommandQueue()` executes the command through the serialized worker and produces terminal `succeeded` with `readback_verified=true` and the canonical record.
5. The persisted Resource exactly matches the worker terminal result.
6. The primary test deletes the nonauthoritative `Changes` projection after worker success and before stock-ChatGPT readback.
7. Existing `doPost(.../v1/query...)` then resolves the persisted entity Authority binding and returns the exact canonical resource ID, revision and payload from `Resources`.
8. The query result and worker terminal canonical record are exact matches, proving client-origin neutrality at the canonical-state contract.
9. A second test confirms `mutation_mode=queued_writer` remains compatible with the existing stock-ChatGPT read contract.
10. A stale Android-shaped command fails with conflict, does not mutate canonical state, and the stock-ChatGPT query continues to return the prior canonical revision rather than the rejected Android payload.

## Completed evidence

- M2-M1-009 durably closed on exact main `a7238151a08734b51e1ffa3386a5b672a73c46c0` with final CI `33900587999` green.
- Fresh canonical lifecycle review identified stock-ChatGPT cross-readback as M2-M1 step 7 and the next unfinished dependency.
- `Code.gs` already resolves canonical reads through persisted `authority_binding` + verified/enabled Google Sheets Authority and reads `Resources`; it does not use Android cache or Changes.
- `CommandWorker.gs` already owns queued-mode canonical mutation, same-user authority validation, exact readback and Changes projection.
- Queued-writer activation stores `mutation_mode=queued_writer`; the stock-ChatGPT schema/read contract continues to use `writer_model=single_writer`, so queued mutation does not invalidate reads.
- New test-only file `tests/apps_script/android_cross_readback.test.js` supplies the missing shared-runtime integration evidence; no production source changed.
- First PR CI `33901154860` correctly stopped at Work-session alignment before test execution because two backlog work IDs were accidentally placed in the feature-only `Related invariants/features` field. No implementation/test code changed in response.
- Checkpoint `f7bfbda6aed92349f2ea6f8d4def695f37574cc3` corrected only that taxonomy by retaining `AUTH-001`, `STORE-001`, `RECOVERY-002`, `DATA-001`, and `PROVIDER-002` as related features and moving `CHATGPT-API-CLIENT-001` / `CORE-ROUNDTRIP` to a separate related-work field.
- Corrected exact-head CI `33901335696` is completely green: compile, feature registry, product lifecycle, starter distribution, work-session alignment, code ownership, Android unit tests, Python unit tests and Workspace Apps Script tests all passed.
- Pre-merge re-read of `FEATURES.md`, `BACKLOG.md`, `ROADMAP.md`, and `PRODUCT_INVARIANTS.md` still aligns with the bounded result: deterministic cross-readback satisfies M2-M1 step 7, while live Android/provider/device and representative-device evidence remain separate.
- No Work mode, live provider mutation, legacy MIRA production data, historical disposable M2-M1-001 resource, private provider identifier, token, credential, or secret was used.

## Acceptance criteria result

1. Shared deterministic worker + stock-ChatGPT query integration harness — **satisfied**.
2. Exact 16-column Android Workspace command protocol and same-user subject — **satisfied**.
3. Worker creates the target canonical Resource and terminal verified result through production code — **satisfied**.
4. Existing stock-ChatGPT `/v1/query` reads the result through persisted Authority binding — **satisfied**.
5. Exact revision/payload matches worker terminal result and canonical Resource — **satisfied**.
6. Query independence from Changes/Android cache — **satisfied; primary test removes Changes before read**.
7. Queued mutation mode remains read-compatible; no second read engine — **satisfied**.
8. Failed stale command cannot masquerade as cross-readback success — **satisfied**.
9. Existing repository suites remain green — **satisfied on CI `33901335696`**.
10. Zero Work/live-provider/legacy/private-state usage — **satisfied**.
11. Pre-merge FEATURES/BACKLOG/ROADMAP/invariant alignment re-read — **satisfied**.
12. Expected-head merge, remote-main readback, post-merge CI, lifecycle reconciliation and final closeout CI — **pending**.

## Explicitly deferred

- Live Android Google authorization and physical-device mutation execution.
- Live provider/host cross-readback using an actual Android device-originated command; this belongs with representative-device/live-evidence work rather than being fabricated from deterministic tests.
- Representative-device proof.
- User-facing conflict-resolution UI and broad Connections/app-shell polish.
- Release signing/distribution, notifications/TTS, capture paths, unrelated providers, and legacy-data migration.

## Session-end alignment verification — 2026-09-04 M2-M1-010 pre-merge

### `FEATURES.md`

`CLIENT-ANDROID-001` remains partial. M2-M1-010 adds deterministic cross-client integration evidence but does not prove live Android authorization/device behavior or representative-device delivery.

### `BACKLOG.md`

The accepted `ANDROID-SYNC` functional contract is now satisfied at deterministic integration evidence: Android-shaped queued mutation reaches canonical Workspace state and the stock-ChatGPT query contract reads that exact state from the same Authority. `ANDROID-CLIENT-CORE-001` remains partial because its live provider/device, conflict-UI and representative-device evidence gaps remain.

### `ROADMAP.md`

M2-M1 step 7 is satisfied at deterministic integration evidence. Step 8 representative-device proof remains next within the Android milestone unless fresh dependency ranking selects a higher-priority release blocker after this packet closes.

### `PRODUCT_INVARIANTS.md`

One-authority semantics, client-origin neutrality, nonauthoritative Changes/cache state, default Personal Google path, ordinary-user setup expectations, evidence honesty and legacy-data protection remain preserved.

### Direction result

**ALIGNED.** The packet required no production read implementation because the existing canonical read contract already composes correctly with queued Android/shared-client mutation. This is a test/evidence completion, not permission to claim live Android/provider/device behavior.

## Exact next action / resume point

1. Require exact-head CI on this evidence checkpoint.
2. Re-read PR #110 head/mergeability and merge only with exact expected-head SHA if CI is green.
3. Independently read back remote `main` at the merge SHA and require post-merge CI.
4. Reconcile BACKLOG/ROADMAP lifecycle so `ANDROID-SYNC` records deterministic integration completion while `ANDROID-CLIENT-CORE-001` / `CLIENT-ANDROID-001` retain live/device gaps.
5. Write final CURRENT_WORK closeout and require exact-head CI/readback before durable closure.
6. Do not use Work mode for lifecycle closeout. Any later representative-device/live-provider packet must be separately bounded and may use Work only when its deterministic prerequisites are green.

## Recovery protocol

Read this file first. Verify PR #110 exact head and CI. Resume from expected-head merge after this checkpoint passes exact-head CI. Do not rerun M2-M1-001 through M2-M1-009, do not add production read code without new failing evidence, and do not collapse representative-device/live-provider proof into this deterministic packet.