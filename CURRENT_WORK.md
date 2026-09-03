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
- Existing historical disposable provider proof resources remain protected and are not needed for implementation.

## Session-start alignment verification — 2026-09-03 M2-M1-007

### `FEATURES.md`

- `CLIENT-ANDROID-001` requires an Android client adapter over shared API semantics, protected credentials, offline replay-safe sync and evidence-based capabilities.
- `PROVIDER-002` requires native ordinary-user Connect semantics, automated post-consent discovery/binding/verification, no avoidable technical setup, and exact resource readback.
- `API-001`, `AUTH-001`, `STORE-001` and `RECOVERY-002` preserve one canonical authority, exact command/readback semantics and failure isolation.

### `BACKLOG.md`

- `ANDROID-CLIENT-CORE-001` is partial through M2-M1-006. Enrollment/session trust, protected credentials, encrypted offline state, reconnect orchestration and the default-Personal Workspace row transport are merged/test-verified.
- The next unfinished client-core dependency is real Google provider authorization/network binding plus automatic safe Workspace resource selection/binding.
- `ANDROID-SYNC` remains blocked until the client can reach the verified shared Workspace transport through a real authorized gateway.

### `ROADMAP.md`

- M2-M1 requires Android to read/mutate the same Personal canonical state and later prove stock ChatGPT reads the Android mutation back.
- Broad notification/capture/release polish remains after the shared-state proof unless it becomes a hard dependency.

### `PRODUCT_INVARIANTS.md`

- Android must use the same Connect/Connected/Reconnect/Needs-attention/Disconnect semantics as other MIRA clients.
- Provider consent/resource selection may be unavoidable, but normal users must never copy spreadsheet IDs, create hidden resources, edit scopes, open developer consoles, run scripts or use a terminal.
- Provider consent alone is not readiness. Post-consent MIRA schema/resource verification must succeed before the Workspace is bound.

### Current Google capability evidence

Official Google Android/Workspace documentation checked 2026-09-03 establishes the bounded implementation path:

- Google Identity Services `AuthorizationClient` returns tokens when grants already exist or a `PendingIntent` for unavoidable account/consent UI when they do not.
- Google Drive Picker can be invoked from Android authorization with `AuthorizationRequest.ResourceParameter.PICKER_OAUTH_TRIGGER`.
- The Picker flow uses only `https://www.googleapis.com/auth/drive.file`, with `setOptOutIncludingGrantedScopes(true)`; this scope is the recommended non-sensitive Sheets-capable scope and is sufficient for Sheets values read/append on selected files.
- Picker can be filtered to Google Sheets, limited to one selection, and returns selected IDs through `AuthorizationResult.getTokenResponseParams()` key `picked_file_ids`.
- `play-services-auth` 21.6.0 is the latest documented release as of 2026-05-27.

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
- **Current head before this activation commit:** `290b78518947f060e06a11d9141faf0c5d64d4e5`
- **Status:** active

## Objective

Complete the missing real-provider seam beneath the already-test-verified M2-M1-006 Workspace transport without expanding into the full Android app:

1. Add an Android Google-Workspace provider module separate from provider-neutral core.
2. Build the Google Identity Services authorization request with only `drive.file`, single Google-Sheets Picker selection, explicit provider consent, and no broad Drive/Sheets-all-files scope.
3. Convert successful authorization evidence into an ephemeral access-token + exactly one selected spreadsheet ID; fail closed on missing token/scope/file, multiple files, malformed provider evidence or unresolved consent.
4. Verify the selected spreadsheet is actually a compatible MIRA Personal Workspace before binding: exact Metadata markers, queued-writer mode, and exact Commands/Changes protocol headers.
5. Implement a bounded HTTPS Google Sheets REST gateway for exact table reads and RAW append-row operations required by `GoogleWorkspaceTransport`.
6. Keep access tokens ephemeral/provider-layer only. Never write them to `ProtectedCredentialStore`, `OfflineSyncStateStore`, MIRROR Resources, Git or logs.
7. Preserve ambiguous append semantics already owned by `GoogleWorkspaceTransport`; the gateway reports transport failure and does not invent retries that could duplicate commands.
8. Provide deterministic JVM tests for authorization evidence validation, MIRA Workspace verification, Sheets REST request/response mapping, error handling and no-unverified binding.
9. Update Android component ownership for every new production path.

## Acceptance criteria

1. `:core` remains free of Google Play Services/network implementation dependencies; provider-specific code lives in a separate Android library module depending on `:core`.
2. Authorization request is `drive.file` only, opts out of inherited granted scopes, invokes Picker, filters to Google spreadsheets, and disallows multiple selection.
3. Successful binding requires exactly one selected spreadsheet ID, exact granted `drive.file`, nonblank access token and exact verified MIRA Workspace contract.
4. Metadata verification requires `schema_version=mira-structured-state-v1`, `store_role=personal_google_starter`, `adapter_contract=STORE-001`, `mutation_mode=queued_writer`, and expected writer model; duplicate/missing/contradictory Metadata fails closed.
5. Commands and Changes exact header verification occurs before a transport is considered bound.
6. REST gateway reads only explicit MIRA ranges and appends only through `spreadsheets.values.append` with `valueInputOption=RAW`; non-2xx, malformed JSON, oversized responses and provider/network failures are explicit gateway failures.
7. No access token, spreadsheet ID, account identifier or other private provider state is committed to the public repository or persisted in canonical/offline state.
8. Unit tests cover successful bind, pending/unresolved consent evidence, missing scope/token/file, multiple selected files, wrong Metadata, wrong headers, HTTP/auth failures, malformed provider responses and exact append body/range.
9. Android ownership/CI gates and existing core tests remain green.
10. No Work mode or live provider mutation is used before implementation and deterministic tests are green. Any later live proof must use isolated disposable/synthetic MIRA state only and must not rerun M2-M1-001 publication/setup.
11. End-of-packet FEATURES/BACKLOG/ROADMAP/PRODUCT_INVARIANTS alignment is recorded before merge.
12. Exact-head CI, expected-head merge, remote-main readback, post-merge CI and final closeout CI are all verified before closure.

## Explicitly deferred

- Broad Android Connections screen/polish and user-facing status presentation beyond provider-layer outcomes.
- Persistent Google account/profile identity and Credential Manager authentication UX not required for the scoped Workspace grant.
- Full `ANDROID-SYNC` canonical entity read/mutation/cross-ChatGPT vertical.
- Conflict-resolution UI.
- Representative physical-device proof and Android release signing/distribution.
- Gmail, Calendar, Contacts, Microsoft, Apple/iCloud, Airtable, finance and other provider adapters.
- Integration recommendation engine under `PROVIDER-004`.

## Completed evidence

- M2-M1-006 already supplies `GoogleWorkspaceTransport` with an injected narrow `SheetsGateway`, exact Commands/Changes parsing, ambiguous append readback convergence, verified change cursors and deterministic tests.
- Current Google docs verify `drive.file` is sufficient for Sheets read/append and is the recommended least-privilege scope for selected files.
- Current Google docs verify Android Picker authorization returns `picked_file_ids`, removing any need for normal users to copy a spreadsheet ID.
- Branch is based exactly on verified main `290b78518947f060e06a11d9141faf0c5d64d4e5`.

## Session-end alignment verification — pending

### `FEATURES.md`
Pending implementation/test evidence.

### `BACKLOG.md`
Pending lifecycle reconciliation; `ANDROID-CLIENT-CORE-001` must remain partial unless the entire umbrella is truly complete.

### `ROADMAP.md`
Pending confirmation that `ANDROID-SYNC` remains next after this provider seam.

### `PRODUCT_INVARIANTS.md`
Pending confirmation of least privilege, unavoidable-provider-UI only, automatic verification, no copied IDs and no second authority.

### Direction result

**PENDING IMPLEMENTATION/CI.**

## Exact next action / resume point

1. Add `:google-workspace` Android library module depending on `:core` and `com.google.android.gms:play-services-auth:21.6.0`.
2. Add pure/testable authorization evidence validation and the thin Google Identity Services request/result adapter.
3. Add MIRA Workspace verifier and bounded Sheets REST gateway.
4. Add an explicit non-mutating protocol-verification entry point to `GoogleWorkspaceTransport` if required to avoid duplicated Commands/Changes header definitions.
5. Add deterministic tests and ownership entries.
6. Run exact branch CI and repair only failures required by this packet.
7. Do not enter Work mode unless all deterministic implementation gates are green and a narrowly scoped live provider proof is still required.

## Recovery protocol

Read this file first, verify branch/head against remote Git, and resume from the exact next action. Do not reconstruct M2-M1-001 through M2-M1-006, do not create another historical proof Sheet/Apps Script project, and do not touch legacy MIRA production data.
