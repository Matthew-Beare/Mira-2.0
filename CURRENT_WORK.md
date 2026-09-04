# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active/recovery packet and exact recovery state.

## Product direction

Default Personal MIRA remains stock ChatGPT + Google Workspace first, with provider-neutral expansion through explicit ordinary-user connections. MIRA should progressively learn what tools and services a user already relies on and recommend useful supported integrations without silently installing, authorizing, activating, migrating, or changing canonical authority.

`M2-M1-001` through `M2-M1-006` are durably closed. `M2-GOV-012` is also durably closed at its bounded product/governance specification evidence ceiling.

## Prior-packet recovery verification — 2026-09-03

- Repository: `Matthew-Beare/Mira-2.0`.
- M2-GOV-012 final closeout/main SHA: `290b78518947f060e06a11d9141faf0c5d64d4e5`.
- Exact-head CI: `33731858470` — success on that exact SHA.
- M2-GOV-012 parent/merge SHA: `00fa7ccf53e8e4e7e0a0630a2e5a891dbd78eac7`.
- M2-M1-001 through M2-M1-006 and M2-GOV-012 must not be rerun.

## Session-start alignment verification — 2026-09-03 M2-M1-007

### `FEATURES.md`

- `CLIENT-ANDROID-001` remains the required Android client feature and is only partially evidenced.
- `PROVIDER-002` requires an ordinary-user Connect flow with provider-native consent/selection, automated post-consent verification/binding, capability verification and exact readback.
- `PROVIDER-003` already defines deterministic Personal Google bootstrap/readback semantics and must remain the Google-specific implementation boundary rather than changing product semantics.
- `AUTH-001`, `STORE-001`, `API-001`, `RECOVERY-002`, and `SERVICE-001` remain integrity boundaries that this packet must preserve.

### `BACKLOG.md`

- `ANDROID-COMMAND-BOUNDARY-001` is complete and must not be revisited.
- `ANDROID-CLIENT-CORE-001` is partial through M2-M1-006. The next unfinished dependency-correct slice is real Google provider authorization/network binding plus ordinary-user Workspace selection/verification beneath the already-tested `GoogleWorkspaceTransport` contract.
- `ANDROID-SYNC` remains a later vertical and is not pulled into this packet except where a narrow test seam is required.

### `ROADMAP.md`

- M2-M1 requires Android to read and mutate the same canonical Personal reality without becoming a second authority.
- The next proof step is Android client core provider binding, before full shared-state mutation/readback or representative-device proof.

### `PRODUCT_INVARIANTS.md`

- Android must use the same simple connection semantics as stock ChatGPT and must not export OAuth scopes, resource IDs, developer-console work, terminal steps, or hidden-resource creation to an ordinary user.
- Provider consent, capability verification, resource binding, service activation and canonical authority remain separate truths.
- Legacy production state remains protected and cannot be used as a development fixture.

### Direction result

**ALIGNED.** Open one bounded Android provider-binding packet. Implement source and deterministic tests first. Do not use Work mode or live provider state until source/CI evidence is green and a narrow live acceptance proof is actually needed.

## Active packet

### `M2-M1-007` — Android Google authorization and Workspace binding

- **Primary work:** `ANDROID-CLIENT-CORE-001`
- **Primary features:** `CLIENT-ANDROID-001`, `PROVIDER-002`, `PROVIDER-003`
- **Related invariants/features:** `AUTH-001`, `STORE-001`, `API-001`, `SERVICE-001`, `RECOVERY-002`, `SOURCE-001`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `work/m2-m1-007-android-google-binding`
- **Packet base SHA:** `290b78518947f060e06a11d9141faf0c5d64d4e5`
- **Current head SHA:** pending source checkpoint readback
- **Status:** active

## Objective

Implement the narrow Android-native Google connection boundary required by the already-tested `GoogleWorkspaceTransport`: obtain revocable same-user Google authorization through a product-owned Android connection flow, use Google's provider-native mobile Picker so the user grants exactly one MIRA spreadsheet without copying any provider ID, verify that selected file against bounded MIRA metadata/protocol state, bind a concrete bounded Sheets gateway, and expose honest connection/readiness state to the existing reconnect layer.

This packet does **not** implement the full Android app, full `ANDROID-SYNC`, conflict UI, notification/TTS delivery, camera/NFC/BLE capture, release signing, representative-device proof, stock-ChatGPT cross-readback, or automatic activation of the queued writer on a direct-only starter.

## Reversible engineering decision — least-authority Google file grant

Current Google provider documentation explicitly supports the mobile Google Picker from Android through Google Identity Services using `AuthorizationRequest.ResourceParameter.PICKER_OAUTH_TRIGGER`. Google requires the mobile/desktop Picker lane to use `drive.file` and does not permit combining it with broader scopes in that flow. MIRA therefore uses the provider-owned Picker plus **only** `https://www.googleapis.com/auth/drive.file` rather than requesting restricted `drive.metadata.readonly`, `drive.readonly`, or full Drive access merely to discover a spreadsheet.

Consequences:

- the ordinary user taps Connect Google and chooses the MIRA spreadsheet in Google's own file UI; they never copy a spreadsheet ID, OAuth scope, token, or developer-console value;
- MIRA verifies the returned opaque file identity against Drive metadata and bounded `Metadata`, `Commands`, and `Changes` cells before shared-write readiness is claimed;
- a valid direct/single-writer MIRA starter may be bound but reports `needs_shared_writer_activation`; the Android transport gateway cannot be constructed until queued-writer readiness is verified;
- access tokens remain ephemeral and are not persisted in the provider binding;
- this avoids a restricted all-Drive metadata permission and its heavier privacy/verification burden while preserving provider-neutral MIRA semantics.

This decision is reversible if Google changes the Picker contract or a later product requirement genuinely needs broader discovery.

## Dependencies and blockers

- `ANDROID-COMMAND-BOUNDARY-001` — complete.
- `GoogleWorkspaceTransport`, `ReconnectCoordinator`, protected credential storage, encrypted offline queue/cache/cursor state — merged/test-verified through M2-M1-006.
- Google OAuth client registration/release signing configuration is deployment/provider configuration, not repository secret material. No client secret or personal provider identifier may be committed.
- Live Google/device proof is intentionally deferred until source/tests/CI are green.

## Acceptance criteria

1. **Android-native authorization boundary** — production code uses Google Identity Services and the provider-native mobile Picker with the non-sensitive `drive.file` scope only, supports provider resolution/revocation semantics, and never requires an ordinary user to copy OAuth scopes, IDs, tokens, or provider resource identifiers.
2. **Provider-native Workspace selection + automatic verification** — after provider consent/selection, code accepts exactly one Picker-returned Google Sheet identity and automatically validates MIRA identity by bounded `Metadata` reads. Zero/multiple selections, MIME/type mismatch, Trash/read-only state, metadata mismatch, legacy-looking state, or unsupported mutation mode fail closed rather than being guessed through broad Drive search.
3. **Exact binding/readiness evidence** — the selected spreadsheet binding stores only non-secret provider identity/configuration, never the access token, distinguishes a valid direct-writer binding from verified queued-writer readiness, and can be revalidated with a fresh token before use.
4. **Concrete narrow Sheets gateway** — a Google-backed implementation of `GoogleWorkspaceTransport.SheetsGateway` can read only bounded `Commands`/`Changes` ranges and append exactly one 16-cell command row, with provider error normalization and no generic arbitrary-sheet mutation surface. Gateway creation is refused unless queued-writer readiness was verified.
5. **Provider-neutral transport preserved** — `GoogleWorkspaceTransport`, canonical command semantics, cursor/replay rules, Authority/store ownership, and readback requirements remain unchanged.
6. **No legacy production mutation** — deterministic tests use fakes/synthetic fixtures only. No personal Sheet ID, token, email, credential, legacy MIRA artifact, or live production content is committed or used as a fixture.
7. **Tests** — unit tests cover successful Picker grant handoff, denied/expired authorization material, exact-scope enforcement, zero/multiple selection rejection, exact metadata validation, direct-vs-queued readiness, schema/header mismatch, gateway bounded reads/appends, arbitrary-range mutation rejection, HTTP/provider failure mapping, reconnect/revalidation, and no-manual-ID behavior.
8. **Build/CI** — required Android unit tests and repository CI pass on the exact packet head before merge.
9. **Evidence ceiling** — this packet may reach implemented/test/integration evidence in Git. It must not claim live provider authorization, physical-device behavior, production signing, queued-writer activation, or shared-state Android↔ChatGPT proof without separate exact provider/device evidence.

## Completed evidence

- Session-start Git recovery verified remote `main` at `290b78518947f060e06a11d9141faf0c5d64d4e5`.
- Exact-head CI `33731858470` succeeded on that closeout SHA.
- Canonical feature/backlog/roadmap/invariant alignment was re-read before implementation.
- Active branch created from the exact verified main SHA: `work/m2-m1-007-android-google-binding`.
- Current official Google Drive/Picker authorization guidance was rechecked before choosing scopes: Android mobile Picker supports Google Identity Services `AuthorizationRequest`, requires `drive.file` for this flow, supports Picker resource parameters, and returns selected file IDs through authorization result parameters.
- Source checkpoint implements token-free Workspace binding/revalidation, Google Identity Services Picker handoff, and a bounded Drive/Sheets REST gateway beneath the existing transport seam.
- Deterministic JVM test sources cover grant parsing, metadata/readiness validation, REST bounds/error mapping, and refusal of arbitrary table mutation. CI evidence is still pending.

## Exact next action / resume point

1. Commit/read back the M2-M1-007 source checkpoint and record its exact remote SHA.
2. Open a PR against `main` to trigger repository CI.
3. Diagnose only actual CI failures; do not expand packet scope.
4. After exact-head CI is green, reconcile `BACKLOG.md`, `FEATURES.md`, `ROADMAP.md`, `PRODUCT_INVARIANTS.md`, and `CURRENT_WORK.md` against the evidence ceiling.
5. Merge only when review/alignment gates are satisfied, then verify remote `main` and exact-head post-merge CI.
6. Only then decide whether a separate provider/device acceptance packet is required. Do not invoke Work mode preemptively.

## Recovery protocol

Read this file first. Verify branch `work/m2-m1-007-android-google-binding` is based on `290b78518947f060e06a11d9141faf0c5d64d4e5`. Do not rerun M2-M1-001 through M2-M1-006 or M2-GOV-012. Continue at the exact next action above.
