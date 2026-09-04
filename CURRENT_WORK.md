# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active/recovery packet and exact recovery state.

## Product direction

Default Personal MIRA remains stock ChatGPT + Google Workspace first. Android extends the same canonical reality and must not become a second authority. Google authorization/network details live behind a replaceable provider module; provider-neutral client state, reconnect orchestration and row-transport semantics remain in `:core`.

M2-M1-001 through M2-M1-006 and M2-GOV-012 are durably closed. M2-M1-007 remains active only for reconciliation/merge/closeout after duplicate concurrent implementations were discovered.

## Prior-packet / remote-main verification — 2026-09-04

- Repository: `Matthew-Beare/Mira-2.0`.
- PR #106 merged the first M2-M1-007 product implementation to `main` at `f6d38ee9398bc473425f33b6fe97fb5fb0ae4b35`.
- Post-merge CI `33826483012` succeeded on that exact main SHA.
- Duplicate PR #105 is closed unmerged; its branch is salvage/history only and must not be merged.
- Reconciliation PR #107 is the only active M2-M1-007 implementation path.

## Session-start alignment verification — reconciliation checkpoint

### `FEATURES.md`

- `CLIENT-ANDROID-001` remains partial and requires provider-neutral shared client semantics, protected credentials, replay-safe sync and evidence-based capability truth.
- `PROVIDER-002` requires ordinary-user native connection, unavoidable provider consent only, automated post-consent verification/binding and no copied provider IDs or technical setup.
- `PROVIDER-003` preserves deterministic Personal Google verification without promoting Google details into universal client semantics.

### `BACKLOG.md`

- `ANDROID-CLIENT-CORE-001` remains partial; provider binding is one prerequisite beneath the later `ANDROID-SYNC` vertical.
- `ANDROID-SYNC` remains unstarted and is explicitly outside this packet.
- The duplicate implementation is an integrity repair within M2-M1-007, not a new work item.

### `ROADMAP.md`

- M2-M1 still requires exactly one Android connection/transport path into the same canonical Personal Workspace, followed later by canonical read, mutation, stock-ChatGPT cross-readback and representative-device proof.
- Two parallel Google provider stacks would violate that direction and increase provider coupling.

### `PRODUCT_INVARIANTS.md`

- Provider consent is not readiness.
- Ordinary users must never copy IDs/scopes/tokens or perform developer setup.
- Provider-specific details must not become canonical product semantics or a dependency of unrelated provider-neutral core behavior.
- No legacy MIRA production state may be used as a development fixture.

### Direction result

**ALIGNED.** Preserve the stronger product behavior from merged PR #106, keep one production provider stack only, and salvage PR #105's provider-module separation, privacy, multi-module ownership/CI and HTTP hardening without expanding into `ANDROID-SYNC` or UI work.

## Active packet

### `M2-M1-007` — Android Google authorization and Workspace binding reconciliation

- **Primary work:** `ANDROID-CLIENT-CORE-001`
- **Primary features:** `CLIENT-ANDROID-001`, `PROVIDER-002`, `PROVIDER-003`
- **Related invariants/features:** `AUTH-001`, `STORE-001`, `API-001`, `RECOVERY-002`, `DATA-001`, `SOURCE-001`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `work/m2-m1-007-provider-module-reconcile`
- **Base/main SHA:** `f6d38ee9398bc473425f33b6fe97fb5fb0ae4b35`
- **Source implementation:** merged PR #106
- **Salvage reference:** closed PR #105 / head `51d2203a6f951ae0bd8ef50b4e5ab3e596c2fa16`
- **Reconciliation PR:** #107
- **Last exact green reconciliation head:** `dedc830f8d5f29a29cef537f34b16ed5fb050ef6`
- **Exact reconciliation CI:** `33829763913` — success
- **Status:** merge candidate after this final evidence checkpoint passes exact-head CI

## Reconciliation result

**IMPLEMENTED AND TEST-VERIFIED.** Exactly one Google provider stack now remains on the reconciliation branch.

Preserved from PR #106:

1. Google Identity Services Picker flow with exact `drive.file` scope and explicit revoke support.
2. Drive file metadata verification: selected ID, Google-Sheet MIME type, Trash state, edit capability and display name.
3. Clean-starter Metadata verification including `environment=mira_2_personal_clean` and `data_policy=clean_starter_only`.
4. Honest `direct_single_writer` versus verified `queued_writer` readiness.
5. Fresh-token revalidation of a token-free binding without requiring the user to select the same Sheet again.
6. Bounded Commands/Changes gateway and explicit provider failure mapping.

Strengthened from PR #105:

1. Google SDK/network code moved to `android-client/google-workspace`; `:core` no longer depends on Google Play Services or carries the provider-only INTERNET permission.
2. Token-bearing Picker grants are opaque outside the provider package; token and raw provider ID are excluded from string/log surfaces.
3. Fresh reconnect consumes the stored non-secret binding and a new Google `AuthorizationResult` entirely inside the provider module, reconstructing `GoogleWorkspaceTransport` without exposing the token to UI/app code.
4. HTTP reads are size/row/cell bounded; nested provider cell material fails closed; Commands append accepts exactly 16 primitive cells and makes one POST attempt only.
5. Provider error bodies are never included in normalized errors; `HttpURLConnection` disconnects in a `finally` path.
6. Android ownership governance supports multiple explicit production roots and rejects unowned provider source or overlapping roots.
7. CI executes both `:core:testDebugUnitTest` and `:google-workspace:testDebugUnitTest`.

## Completed evidence

- PR #106 main merge `f6d38ee9398bc473425f33b6fe97fb5fb0ae4b35` passed post-merge CI `33826483012`.
- PR #105 duplicate is closed unmerged and was not merged into current main.
- PR #107 branch deletes the three Google provider production classes and their three tests from `:core`, then provides exactly three corresponding production classes/tests under `:google-workspace`.
- `android-client/core/build.gradle.kts` no longer depends on `play-services-auth`; the Google provider module owns `play-services-auth:21.6.0`.
- `android-client/core/src/main/AndroidManifest.xml` no longer declares INTERNET; the provider module declares it.
- Direct tests cover exact scope/picker material, token bounds/opacity, file identity/type/editability, clean-starter metadata, direct-vs-queued readiness, header drift, provider failures, token-private revalidation, REST request boundaries, primitive-only rows, oversized responses, no error-body leakage, no arbitrary tables, one-attempt ambiguous append behavior and readiness/grant matching.
- First reconciliation head `55350fe9c1ae6aec0d649687444c95338716b3a5` passed CI `33829526201` before token-private reconnect refinement.
- Exact refined head `dedc830f8d5f29a29cef537f34b16ed5fb050ef6` passed CI `33829763913`, including compile, feature registry, lifecycle, Personal starter distribution, work-session alignment, multi-module ownership, both Android modules, Python tests and Workspace Apps Script tests.
- No Work mode, live provider mutation, historical proof resource, private provider identifier, secret, or legacy MIRA production fixture was used.

## Acceptance criteria result

1. Exactly one Google provider implementation — **satisfied on PR #107 branch**.
2. Provider-neutral `:core` with no Google SDK/provider-only INTERNET requirement — **satisfied**.
3. Dedicated `:google-workspace` owns GIS authorization/revoke, Picker parsing, verification/readiness/revalidation and REST — **satisfied**.
4. PR #106 product behavior preserved — **satisfied**.
5. Token/provider identity privacy surface hardened — **satisfied**.
6. REST bounded/fail-closed/no hidden retry — **satisfied**.
7. Multi-module ownership and CI — **satisfied and green**.
8. Zero live provider/Work/legacy-state scope — **satisfied**.
9. Exact-head CI before reconciliation merge — **satisfied on `dedc830f...`; this evidence commit requires its own final exact-head CI**.
10. Merge/main readback/post-merge lifecycle closeout — **pending only**.

## Explicitly deferred

- Full `ANDROID-SYNC` canonical read/mutation/cross-ChatGPT proof.
- Broad Connections UI polish and conflict UI.
- Durable connection-state serialization/presentation details beyond the token-free provider binding contract.
- Representative physical-device proof and release signing/distribution.
- Gmail, Calendar, Contacts, Microsoft, Apple/iCloud, Airtable, finance and other provider adapters.
- Integration recommendation engine under `PROVIDER-004`.

## Session-end alignment verification — 2026-09-04 M2-M1-007 reconciliation

### `FEATURES.md`

`CLIENT-ANDROID-001` remains partial. The reconciliation adds implementation/test evidence for the Google provider binding prerequisite but does not complete the Android feature because `ANDROID-SYNC`, conflict UX and representative-device proof remain unfinished. Final feature evidence wording will be reconciled only after PR #107 is actually merged.

### `BACKLOG.md`

`ANDROID-CLIENT-CORE-001` remains partial and `ANDROID-SYNC` remains next. The canonical backlog still says partial through M2-M1-006 because durable M2-M1-007 evidence requires the reconciliation merge and post-merge CI first; the closeout checkpoint must advance it to partial through M2-M1-007.

### `ROADMAP.md`

The implementation satisfies the provider-binding prerequisite only. The roadmap must be reconciled after merge to record M2-M1-001 through M2-M1-007 complete while leaving canonical Android read/mutation/cross-readback/device proof unfinished.

### `PRODUCT_INVARIANTS.md`

Ordinary-user connection, least privilege, provider-owned unavoidable UI only, automatic post-consent verification, provider consent not equaling readiness, provider-neutral core, no second authority and legacy-data protection are all preserved.

### Direction result

**ALIGNED.** PR #107 resolves the duplicate implementation without adding a second product path or expanding packet scope. Final lifecycle text is intentionally deferred until merged evidence exists.

## Exact next action / resume point

1. Require exact-head CI on this final evidence commit.
2. Verify PR #107 remains mergeable and contains only the reconciliation/provider-module/governance/checkpoint scope.
3. Merge #107 with expected-head protection after exact green CI.
4. Read back remote `main` and verify post-merge CI.
5. On the final closeout checkpoint, reconcile `FEATURES.md`, `BACKLOG.md`, and `ROADMAP.md` to M2-M1-007 complete-at-packet-evidence-ceiling while leaving `CLIENT-ANDROID-001` / `ANDROID-CLIENT-CORE-001` partial and `ANDROID-SYNC` next.
6. Record final duplicate-resolution evidence in this file and require final exact-head CI plus remote-main readback.
7. Do not use Work mode; no live-provider-only blocker is required to close this deterministic provider-binding packet.

## Recovery protocol

Read this file first. PR #105 is closed salvage only. PR #106 is merged product-behavior source. PR #107 is the sole active reconciliation path. Resume only final CI → expected-head merge → post-merge CI → canonical lifecycle closeout. Do not create another Google provider implementation and do not rerun M2-M1-001 through M2-M1-006.
