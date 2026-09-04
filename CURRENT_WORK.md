# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active/recovery packet and exact recovery state.

## Product direction

Default Personal MIRA remains stock ChatGPT + Google Workspace first. Android extends the same canonical MIRROR authority and shared queued-writer semantics; it never becomes a second writable master. Ordinary users must get a native Connect flow, unavoidable provider consent/resource selection only, automatic post-consent verification/binding, and no copied provider IDs, Apps Script editor, developer console, terminal, or hidden setup ritual.

## Prior-packet recovery verification — 2026-09-03

- Repository: `Matthew-Beare/Mira-2.0`.
- Authoritative `main` before this packet: `290b78518947f060e06a11d9141faf0c5d64d4e5`.
- M2-GOV-012 final closeout CI: `33731858470` — success on that exact head.
- Remote `main` independently read back the same SHA.
- M2-M1-001 through M2-M1-006 and M2-GOV-012 are durably closed and must not be rerun.
- Existing historical disposable provider proof resources remain protected and were not needed for this packet.

## Session-start alignment verification — 2026-09-03 M2-M1-007

### `FEATURES.md`

- `CLIENT-ANDROID-001` requires an Android client adapter over shared API semantics, protected credentials, offline replay-safe sync and evidence-based capabilities.
- `PROVIDER-002` requires native ordinary-user Connect semantics, automated post-consent discovery/binding/verification, no avoidable technical setup, and exact resource readback.
- `API-001`, `AUTH-001`, `STORE-001` and `RECOVERY-002` preserve one canonical authority, exact command/readback semantics and failure isolation.

### `BACKLOG.md`

- `ANDROID-CLIENT-CORE-001` was partial through M2-M1-006 at packet start. Enrollment/session trust, protected credentials, encrypted offline state, reconnect orchestration and the default-Personal Workspace row transport were already merged/test-verified.
- The next unfinished client-core dependency was real Google provider authorization/network binding plus automatic safe Workspace resource selection/binding.
- `ANDROID-SYNC` remained blocked until the client could reach the verified shared Workspace transport through a real authorized gateway.

### `ROADMAP.md`

- M2-M1 requires Android to read/mutate the same Personal canonical state and later prove stock ChatGPT reads the Android mutation back.
- Broad notification/capture/release polish remains after the shared-state proof unless it becomes a hard dependency.

### `PRODUCT_INVARIANTS.md`

- Android must use the same Connect/Connected/Reconnect/Needs-attention/Disconnect semantics as other MIRA clients.
- Provider consent/resource selection may be unavoidable, but normal users must never copy spreadsheet IDs, create hidden resources, edit scopes, open developer consoles, run scripts or use a terminal.
- Provider consent alone is not readiness. Post-consent MIRA schema/resource verification must succeed before the Workspace is bound.

### Current Google capability evidence

Official Google Android/Workspace documentation checked 2026-09-03 established the bounded implementation path:

- Google Identity Services `AuthorizationClient` returns tokens when grants already exist or a `PendingIntent` for unavoidable account/consent UI when they do not.
- Google Drive Picker can be invoked from Android authorization with `AuthorizationRequest.ResourceParameter.PICKER_OAUTH_TRIGGER`.
- The Picker flow uses only `https://www.googleapis.com/auth/drive.file`, with `setOptOutIncludingGrantedScopes(true)`; this scope is the recommended non-sensitive Sheets-capable scope and is sufficient for Sheets values read/append on selected files.
- Picker can be filtered to Google Sheets, limited to one selection, and returns selected IDs through `AuthorizationResult.getTokenResponseParams()` key `picked_file_ids`.
- `play-services-auth` 21.6.0 is the documented current release used by this packet.

### Direction result

**ALIGNED.** Implement a provider-specific Android library below `GoogleWorkspaceTransport` that requests only `drive.file`, uses Google Picker for unavoidable existing-file selection, automatically verifies the selected file as the expected MIRA queued Workspace, and supplies a narrow real Sheets REST gateway. Do not add Drive-wide listing/search scope, persist OAuth access tokens as canonical/offline state, or build broad Connections UI in this packet.

## Active packet

### `M2-M1-007` — Android Google authorization, Workspace binding and Sheets gateway

- **Primary work:** `ANDROID-CLIENT-CORE-001`
- **Primary features:** `CLIENT-ANDROID-001`, `PROVIDER-002`, `API-001`
- **Related invariants/features:** `AUTH-001`, `STORE-001`, `RECOVERY-002`, `DATA-001`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `work/m2-m1-007-google-provider-binding`
- **Base SHA:** `290b78518947f060e06a11d9141faf0c5d64d4e5`
- **Last fully verified implementation head:** `6075c4ddc34f77a609c0f4dece1fd405819c2242`
- **Verified implementation CI:** `33764927985` — success on that exact head
- **Later bounded-response/lifecycle reconciliation commits:** through `efa776fe80538c33dcd7f8bce970fa60278bd5b8` before this evidence commit
- **PR:** #105
- **Status:** implementation/test candidate complete at deterministic evidence ceiling; final evidence head CI and merge closeout remain

## Objective result

**IMPLEMENTED AND TEST-VERIFIED AT THE DETERMINISTIC PROVIDER-ADAPTER EVIDENCE CEILING.**

M2-M1-007 adds the missing real-provider seam beneath the M2-M1-006 Workspace transport without expanding into the full Android app:

1. A separate Android `:google-workspace` library depends on provider-neutral `:core`; `:core` does not depend on Google Play Services or the concrete HTTP implementation.
2. Google Identity Services authorization uses only `drive.file`, opts out of inherited scopes, explicitly requests provider consent, invokes Google-owned Picker, filters to Google spreadsheets, and disallows multiple selection.
3. Successful authorization requires an ephemeral nonblank access token, exact `drive.file` grant, and exactly one valid picked spreadsheet ID. Pending provider resolution remains an explicit user-action outcome rather than fake readiness.
4. Selected files are read-only verified before binding against exact MIRA Metadata plus Commands and Changes protocol headers.
5. Metadata requires `mira-structured-state-v1`, `personal_google_starter`, `STORE-001`, `single_writer`, and `queued_writer`; duplicate/missing/contradictory material fails closed.
6. The bounded Sheets REST gateway can read only Metadata/Commands/Changes and append only to Commands using RAW values + INSERT_ROWS.
7. Ambiguous command append failures are not retried by the gateway; the already-verified `GoogleWorkspaceTransport` owns readback convergence.
8. Provider error bodies are not exposed in gateway errors; network/HTTP/malformed/nested/oversized responses fail explicitly.
9. Access-token and raw selected-provider identifiers are opaque outside the provider package after the privacy-hardening pass. Tokens are never persisted to protected client credentials, offline sync state, canonical MIRROR state, logs or Git.
10. Android production ownership and CI now cover multiple Android modules so provider code cannot sit outside the repository ownership gate.

## Completed evidence

- New provider module: `android-client/google-workspace`.
- `GoogleWorkspaceAuthorization` owns the Google authorization request/result boundary and fail-closed pure grant validation.
- `GoogleSheetsRestGateway` owns bounded HTTPS Sheets values read/Commands append mapping, provider failure handling and response-size bounds.
- `GoogleWorkspaceBinding` owns post-consent zero-write MIRA Metadata/Commands/Changes verification and constructs the already-proven `GoogleWorkspaceTransport` only after exact verification.
- JVM tests cover exact authorization material, missing token/scope/file, inherited extra scope, multiple/malformed selection, provider-resolution evidence, exact REST request/body mapping, Commands-only append, no retry on ambiguous network failure, forbidden arbitrary reads/Changes writes, non-2xx body non-leakage, malformed JSON, nested cells, bounded oversized-response rejection, exact zero-write Workspace bind, wrong/missing/duplicate Metadata, wrong headers, provider read failure and null gateway failure.
- Android ownership governance was generalized from one production root to explicit governed Android production roots and directly tested for multi-module ownership/unowned-source rejection.
- CI now runs both `:core:testDebugUnitTest` and `:google-workspace:testDebugUnitTest`.
- First clean provider-module CI `33763861622` succeeded on `8cdb895e521f9d79b202439bd3efc1d3441d1255`.
- Hardened exact-head CI `33764552075` succeeded on `640e3bf438399f17a6f29d98d2b335cad64b8cb6`.
- Exact head `6075c4ddc34f77a609c0f4dece1fd405819c2242` passed CI `33764927985` after the explicit provider-resolution test seam.
- `ROADMAP.md` now correctly records M2-M1-001 through M2-M1-006 complete and M2-M1-007 active instead of claiming Android client work has not begun.
- `FEATURES.md` now records `CLIENT-ANDROID-001` as test-verified/partially merged with this provider-binding candidate unmerged; the umbrella feature remains incomplete.
- No Work mode, live Google provider mutation, historical disposable proof resource, copied provider ID, account identifier, legacy MIRA production state or secret/provider credential was used.

## Acceptance criteria result

1. Separate Google provider module with core remaining provider-neutral — **satisfied**.
2. Exact least-privilege `drive.file` + Picker single-Sheet request — **satisfied and compiled against Google Play Services 21.6.0**.
3. Exact one-file/token/scope plus verified MIRA contract before binding — **satisfied**.
4. Exact queued-writer Metadata markers and fail-closed contradictions — **satisfied**.
5. Commands/Changes headers verified before transport binding — **satisfied**.
6. Bounded explicit REST reads + RAW Commands append + explicit HTTP/network/malformed/oversized failures — **satisfied**.
7. No provider secrets/private IDs in public Git or canonical/offline state — **satisfied by code scope and privacy-hardening**.
8. Required deterministic authorization/binding/HTTP/error tests — **satisfied**, including explicit provider resolution and oversized response coverage.
9. Android ownership/CI plus existing core suite — **satisfied on multiple exact green heads; final evidence head still requires exact CI**.
10. No Work/live provider mutation before deterministic green — **satisfied; no Work/provider mutation used at all in implementation**.
11. End-of-packet canonical alignment — **recorded below**.
12. Exact-head CI, protected merge, main readback, post-merge CI and final closeout CI — **final evidence CI + merge/closeout pending only**.

## Explicitly deferred

- Broad Android Connections screen/polish and user-facing status presentation beyond provider-layer outcomes.
- Persistent Google account/profile identity and Credential Manager authentication UX not required for the scoped Workspace grant.
- Full `ANDROID-SYNC` canonical entity read/mutation/cross-ChatGPT vertical.
- Conflict-resolution UI.
- Representative physical-device proof and Android release signing/distribution.
- Gmail, Calendar, Contacts, Microsoft, Apple/iCloud, Airtable, finance and other provider adapters.
- Integration recommendation engine under `PROVIDER-004`.

## Session-end alignment verification — 2026-09-03 M2-M1-007

### `FEATURES.md`

`CLIENT-ANDROID-001` remains incomplete but its evidence is reconciled from the old legacy-build-only label to the actual partial merged/test-verified client-core state with this provider-binding candidate still unmerged. `PROVIDER-002` ordinary-user connection semantics remain preserved: unavoidable Google consent/file selection only, then automatic MIRA verification and no copied IDs.

### `BACKLOG.md`

`ANDROID-CLIENT-CORE-001` correctly remains **partial through M2-M1-006** before PR #105 merges. This packet supplies the next provider-binding candidate but does not claim merged evidence early. After protected merge and post-merge verification, the closeout checkpoint must advance the backlog narrative to partial through M2-M1-007. `ANDROID-SYNC` remains the next vertical and is not smuggled into this packet.

### `ROADMAP.md`

M2-M1 status is reconciled to the real progression: command boundary, enrollment/session, protected credentials, encrypted offline state/reconnect and Workspace transport are complete; M2-M1-007 is the active Google authorization/binding/gateway step; canonical Android read, mutation, stock-ChatGPT cross-readback and representative-device proof remain later proof steps.

### `PRODUCT_INVARIANTS.md`

The implementation preserves intent-first connection semantics, least privilege, provider-owned unavoidable UI only, automatic post-consent verification, provider consent not equaling readiness, no copied IDs/developer setup, no silent service activation, no direct canonical mutation from the provider layer, and no second writable master.

### Direction result

**ALIGNED.** M2-M1-007 completes exactly the bounded Google provider-binding prerequisite beneath the existing Workspace transport. The Android umbrella remains partial. No related UI, device proof, integration recommendation, other provider, or full shared-state vertical was added.

## Exact next action / resume point

1. Require CI on the exact final evidence head produced by this checkpoint; repair only packet-required failures.
2. Verify PR #105 remains mergeable and its changed-file scope is exactly the provider module, its tests, Android ownership/CI governance, lifecycle docs and this checkpoint.
3. Merge PR #105 with expected-head protection only after exact green CI.
4. Independently read back remote `main` and verify post-merge CI on the merge SHA.
5. Update `BACKLOG.md` on the closeout checkpoint from partial-through-M2-M1-006 to partial-through-M2-M1-007, while leaving `ANDROID-CLIENT-CORE-001` incomplete and `ANDROID-SYNC` next.
6. Record final M2-M1-007 closure in `CURRENT_WORK.md`, verify final exact-head CI and remote `main`.
7. Do not use Work mode for M2-M1-007 unless deterministic evidence unexpectedly reveals a live-provider-only acceptance blocker. No such blocker is currently known.

## Recovery protocol

Read this file first and verify PR #105 plus the exact branch head. Do not rerun M2-M1-001 through M2-M1-006, do not create another historical proof Sheet/Apps Script project, and do not touch legacy MIRA production data. Resume only the final CI/merge/post-merge/backlog-closeout sequence for M2-M1-007.
