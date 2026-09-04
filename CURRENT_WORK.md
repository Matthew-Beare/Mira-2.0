# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active/recovery packet and exact recovery state.

## Product direction

Default Personal MIRA remains stock ChatGPT + Google Workspace first. Android extends the same canonical reality without becoming a second authority. M2-M1-001 through M2-M1-009 are durably closed. M2-M1-010 has completed the bounded deterministic `ANDROID-SYNC` cross-client contract: an Android-shaped queued mutation becomes canonical Workspace state and the existing stock-ChatGPT query path reads that exact state through the same Authority. Live Android authorization/device execution, conflict UI and representative-device evidence remain separate and must not be inferred from this packet.

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
- `ANDROID-SYNC` was partial through M2-M1-009 because stock-ChatGPT cross-readback remained after canonical Android read/freshness and deterministic queued mutation.
- Lifecycle reconciliation now records `ANDROID-SYNC` complete at deterministic integration evidence in M2-M1-010 while retaining live provider/device, conflict-UI and representative-device gaps under `ANDROID-CLIENT-CORE-001`.

### `ROADMAP.md`

- M2-M1 ordered proof step 7 was stock ChatGPT reading the Android mutation back from the same authority.
- Step 7 is now complete in M2-M1-010 / PR #110 at deterministic integration evidence.
- Representative-device proof remains step 8 and is separate work subject to fresh dependency ranking after durable closeout.

### `PRODUCT_INVARIANTS.md`

- One canonical authority remains authoritative regardless of client origin.
- Default Personal stays stock ChatGPT + Google Workspace first.
- Ordinary-user provider setup must not require copied IDs, developer consoles, scripts, or terminal work.
- Provider/readback evidence must remain truthful; deterministic repository proof cannot be mislabeled as live host/provider proof.

### Direction result

**ALIGNED.** M2-M1-010 was bounded to the stock-ChatGPT cross-readback child of `ANDROID-SYNC`: prove that an Android-shaped queued command is executed by the existing serialized Workspace writer into canonical `Resources`, then the existing stock-ChatGPT Workspace query contract reads that exact canonical revision/payload through the same persisted Authority binding. No second read engine, Android UI expansion, representative-device proof, or legacy production state was included.

## Active packet

### `M2-M1-010` — Stock ChatGPT cross-readback of Android canonical mutation

- **Primary work:** `ANDROID-SYNC`
- **Primary features:** `CLIENT-ANDROID-001`, `API-001`
- **Related invariants/features:** `AUTH-001`, `STORE-001`, `RECOVERY-002`, `DATA-001`, `PROVIDER-002`
- **Related work:** `CHATGPT-API-CLIENT-001`, `CORE-ROUNDTRIP`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Packet base SHA:** `a7238151a08734b51e1ffa3386a5b672a73c46c0`
- **Implementation branch:** `work/m2-m1-010-stock-chatgpt-cross-readback`
- **Final implementation/evidence head:** `d49f136511734762b4e8b4c827d1cc929898e774`
- **Final implementation exact-head CI:** `33901584522` — success
- **Implementation PR:** #110 — merged with expected-head protection
- **Implementation merge SHA:** `9e2314ee1e653291ecb857c6faa126f603fcd33d`
- **Implementation post-merge CI:** `33902636268` — success on exact merge SHA
- **Lifecycle branch:** `work/m2-m1-010-lifecycle-closeout`
- **Lifecycle PR:** #112 — merged with expected-head protection
- **Lifecycle exact-head:** `e396efeb0f8ce470290e08a45cf4cab79179b5c3`
- **Lifecycle exact-head CI:** `33903302798` — success
- **Lifecycle merge SHA:** `c83e418ea29ce151ff373db96dcbe0db875fe423`
- **Lifecycle post-merge CI:** `33903459412` — success on exact lifecycle merge SHA
- **Final closeout branch:** `work/m2-m1-010-final-closeout`
- **Current head:** this CURRENT_WORK-only closeout checkpoint; recovery must read back the branch/PR exact head before merge rather than reconstruct it from chat
- **Dependencies:** M2-M1-001 through M2-M1-009 complete; implementation and lifecycle merge chains above verified green
- **Blockers:** none known for final Git closeout
- **Status:** **COMPLETE AT BOUNDED DETERMINISTIC INTEGRATION EVIDENCE CEILING; final Git closure checkpoint active until its exact-head CI, expected-head merge, remote-main readback and post-merge CI succeed**

## Objective result

**COMPLETE AT THE BOUNDED DETERMINISTIC INTEGRATION EVIDENCE CEILING.**

No new production read path was required. The existing queued writer and existing stock-ChatGPT Workspace query path already compose correctly over the same canonical Authority.

1. `android_cross_readback.test.js` loads production `Code.gs` and `CommandWorker.gs` into one shared synthetic Workbook runtime.
2. The target canonical Resource is absent before the command; the test does not pre-seed the post-mutation state.
3. The test submits the exact Android Workspace queued-command shape with same-user subject, API/schema, idempotency identity and expected revision.
4. `miraProcessCommandQueue()` executes the command through the serialized worker and produces terminal `succeeded` with `readback_verified=true` and the canonical record.
5. The persisted Resource exactly matches the worker terminal result.
6. The primary test deletes the nonauthoritative `Changes` projection after worker success and before stock-ChatGPT readback.
7. Existing `doPost(.../v1/query...)` resolves the persisted entity Authority binding and returns the exact canonical resource ID, revision and payload from `Resources`.
8. The query result and worker terminal canonical record are exact matches, proving client-origin neutrality at the canonical-state contract.
9. Queued-writer mode remains compatible with stock-ChatGPT canonical reads.
10. A stale Android-shaped command fails with conflict, does not mutate canonical state, and stock ChatGPT continues to read the prior canonical revision.

## Completed evidence

- M2-M1-009 durably closed on exact main `a7238151a08734b51e1ffa3386a5b672a73c46c0` with CI `33900587999` green.
- `Code.gs` already resolves canonical reads through persisted `authority_binding` + verified/enabled Google Sheets Authority and reads `Resources`; it does not use Android cache or `Changes` as authority.
- `CommandWorker.gs` already owns queued-mode canonical mutation, same-user authority validation, exact readback and nonauthoritative `Changes` projection.
- `tests/apps_script/android_cross_readback.test.js` supplies the missing shared-runtime integration evidence; no production source changed.
- Final implementation head `d49f136511734762b4e8b4c827d1cc929898e774` passed exact-head CI `33901584522`.
- PR #110 merged only with that exact expected head at `9e2314ee1e653291ecb857c6faa126f603fcd33d`; remote `main` read back that exact SHA; post-merge CI `33902636268` succeeded on it.
- A concurrently opened duplicate PR #111 was detected and closed unmerged; PR #110 remained the authoritative production-path integration proof.
- Lifecycle reconciliation changed only the intended M2-M1-010 status material in `BACKLOG.md` and `ROADMAP.md` plus this recovery record.
- Lifecycle head `e396efeb0f8ce470290e08a45cf4cab79179b5c3` passed exact-head CI `33903302798`.
- PR #112 merged only with that exact expected head at `c83e418ea29ce151ff373db96dcbe0db875fe423`; remote `main` independently read back that exact SHA.
- Lifecycle post-merge CI `33903459412` succeeded on exact `main` SHA `c83e418ea29ce151ff373db96dcbe0db875fe423`.
- `BACKLOG.md` records `ANDROID-SYNC` complete at deterministic integration evidence while `ANDROID-CLIENT-CORE-001` remains partial for live provider/device, conflict UI and representative-device evidence.
- `ROADMAP.md` records M2-M1 step 7 complete and leaves representative-device proof as step 8 subject to fresh dependency ranking.
- No Work mode, live provider mutation, legacy MIRA production data, historical disposable M2-M1-001 resource, private provider identifier, token, credential, or secret was used.

## Acceptance criteria result

1. Shared deterministic worker + stock-ChatGPT query integration harness — **satisfied**.
2. Android queued-command protocol and same-user subject — **satisfied**.
3. Worker creates the target canonical Resource and terminal verified result through production code — **satisfied**.
4. Existing stock-ChatGPT `/v1/query` reads the result through persisted Authority binding — **satisfied**.
5. Exact revision/payload matches worker terminal result and canonical Resource — **satisfied**.
6. Query independence from `Changes`/Android cache — **satisfied**.
7. Queued mutation mode remains read-compatible; no second read engine — **satisfied**.
8. Failed stale command cannot masquerade as cross-readback success — **satisfied**.
9. Existing repository suites remain green — **satisfied through implementation and lifecycle post-merge CI**.
10. Zero Work/live-provider/legacy/private-state usage — **satisfied**.
11. FEATURES/BACKLOG/ROADMAP/invariant alignment — **satisfied**.
12. Expected-head implementation merge, remote-main readback and implementation post-merge CI — **satisfied**.
13. BACKLOG/ROADMAP lifecycle reconciliation, exact-head CI, expected-head merge, remote-main readback and post-merge CI — **satisfied**.
14. Final CURRENT_WORK closure checkpoint — **this checkpoint; durable closure becomes effective only after this checkpoint itself passes exact-head CI, expected-head merge, remote-main readback and post-merge CI**.

## Explicitly deferred

- Live Android Google authorization and physical-device mutation execution.
- Live provider/host cross-readback using an actual Android device-originated command.
- Representative-device proof.
- User-facing conflict-resolution UI and broad Connections/app-shell polish.
- Release signing/distribution, notifications/TTS, capture paths, unrelated providers, and legacy-data migration.

## Session-end alignment verification — 2026-09-04 M2-M1-010 final closeout

### `FEATURES.md`

`CLIENT-ANDROID-001` remains partial. M2-M1-010 completes the deterministic cross-client functional contract but does not prove live Android authorization/device behavior, conflict UI, or representative-device delivery.

### `BACKLOG.md`

`ANDROID-SYNC` is complete at deterministic integration evidence in M2-M1-010 / PR #110. `ANDROID-CLIENT-CORE-001` remains partial through M2-M1-010 because live provider/device, conflict-UI and representative-device evidence remain unfinished.

### `ROADMAP.md`

M2-M1 step 7 is complete at deterministic integration evidence. Step 8 representative-device proof remains candidate next work within M2-M1, but a fresh post-closeout dependency review must decide whether a higher-priority blocker outranks it.

### `PRODUCT_INVARIANTS.md`

One-authority semantics, client-origin neutrality, nonauthoritative `Changes`/cache state, default Personal Google path, ordinary-user setup expectations, evidence honesty and legacy-data protection remain preserved.

### Direction result

**ALIGNED.** M2-M1-010 is complete at its bounded evidence ceiling without falsely claiming live Android/provider/device evidence. No further M2-M1-010 implementation, provider proof, or lifecycle reconciliation is required if this final checkpoint's merge/readback/CI conditions are satisfied.

## Exact next action / resume point

1. Read back `work/m2-m1-010-final-closeout` exact head and verify the branch differs from `c83e418ea29ce151ff373db96dcbe0db875fe423` only in `CURRENT_WORK.md`.
2. Open a CURRENT_WORK-only final closeout PR.
3. Require exact-head CI and merge only with exact expected-head SHA if green.
4. Independently read back remote `main` at the final closeout merge SHA and require post-merge CI on that exact SHA.
5. **Once all four conditions above are green, M2-M1-010 is durably closed. Do not create another M2-M1-010 closeout commit.**
6. Then re-read `CURRENT_WORK.md`, `FEATURES.md`, `BACKLOG.md`, `ROADMAP.md`, and `PRODUCT_INVARIANTS.md` from exact remote `main` and select exactly one next bounded packet by current dependency/risk/value ranking. Representative-device proof is a candidate, not an automatic selection.

## Recovery protocol

Read this file first and inspect its Git context. If this file is on remote `main` and the commit containing it has successful post-merge CI, treat M2-M1-010 as **durably closed** and do not rerun any M2-M1-010 implementation, lifecycle, or provider proof. If it is still on `work/m2-m1-010-final-closeout`, resume only the exact-head CI/expected-head merge/remote-main readback/post-merge CI sequence above. After durable closure, perform a fresh canonical dependency review before opening the next packet. Do not use Work mode for this closeout.
