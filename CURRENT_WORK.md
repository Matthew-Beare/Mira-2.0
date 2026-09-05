# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active/recovery packet and exact recovery state.

## Prior-packet durable closure — 2026-09-05

`M2-G0-012` is durably closed and must not be rerun.

- Governance repair head `e5ddd961dcdb64374e4c6a15a75caee287ea0cec` passed exact-head CI `33951335264`.
- PR #116 merged with expected-head protection as `6e907c900f8d0496fa74296dc5213169d445a683`.
- Remote `main` readback confirmed exactly `6e907c900f8d0496fa74296dc5213169d445a683`.
- Post-merge CI `33951430022` succeeded on that exact main SHA.
- Therefore `M2-M1-011` is durably closed at repository/build evidence and the fresh ranking result selecting representative-device execution is authoritative.

## Active packet

### `M2-M1-012` — Android representative-device execution proof

- **Primary work:** `ANDROID-CLIENT-CORE-001`.
- **Primary features:** `CLIENT-ANDROID-001`, `API-001`.
- **Related invariants/features:** `AUTH-001`, `STORE-001`, `RECOVERY-002`, `PROVIDER-002`, `DATA-001`, `DEV-007`.
- **Repository:** `Matthew-Beare/Mira-2.0`.
- **Branch:** `work/m2-m1-012-android-device-proof`.
- **Base SHA:** `6e907c900f8d0496fa74296dc5213169d445a683`.
- **Last recorded pre-merge checkpoint:** `16895f4b466622db1c4c37bb3b5b66d802b88c8b`, exact-head CI `33984090401`, retained artifact `9974629890`.
- **Merge rule:** the actual PR head is verified externally from GitHub immediately before merge and must pass its own exact-head CI; CURRENT_WORK does not attempt self-referential recording of the commit SHA that contains CURRENT_WORK itself.
- **Dependencies:** M2-M1-001 through M2-M1-011 and M2-G0-012 are durably closed at their recorded evidence ceilings; the existing `device-proof-app`, `core`, and `google-workspace` modules remain the proof surface.
- **Current blocker:** repository/build/signing prerequisites are satisfied. The remaining unearned evidence begins at live provider registration/authorization and physical representative-device execution.
- **Status:** active; stable development signing, exact APK provenance, independent binary verification, exact-head CI and provider-target read-only preflight are complete. Protected merge/main readback and post-merge artifact verification are next; no live Google authorization or physical-device success is claimed yet.

## Objective

Prove the already-implemented Android client path on one representative Android device against isolated synthetic MIRA 2.0 Google state, while preserving the same canonical Authority and honest evidence boundaries used by stock ChatGPT. The packet must not expand into general Android product development.

The representative-device binary must be traceable to exact Git/CI source, use one stable development-only signing identity for the fixed `com.mira.deviceproof` OAuth package/certificate pair, and report success only after provider/canonical readback. Production/release signing remains outside this packet.

## Session-start alignment verification — 2026-09-05 M2-M1-012

### `FEATURES.md`

- `CLIENT-ANDROID-001` remains `specified+implemented+test_verified+partial`; live Android Google authorization/provider-device behavior and representative-device evidence remain unfinished.
- `API-001`, `AUTH-001`, `STORE-001`, and `RECOVERY-002` require the Android client to read and mutate through the shared canonical boundary with exact readback rather than becoming a second authority.
- `PROVIDER-002` requires provider-native ordinary-user connection semantics and forbids avoidable provider IDs, OAuth scopes, developer-console work, pasted code, or terminal setup from becoming future ordinary-user UX.
- `DATA-001` forbids legacy production state from being used as a development fixture.
- `DEV-007` requires this packet to re-check product direction and evidence status before merge/closeout.

### `BACKLOG.md`

- `ANDROID-CLIENT-CORE-001` remains the unfinished prerequisite carrying the live Google authorization/provider-device, conflict-UI, and representative-device evidence gaps.
- `ANDROID-SYNC` is already complete at deterministic integration evidence and must not be reopened simply to acquire physical-device evidence.
- `ANDROID-RELEASE-001` remains later hardening. M2-M1-012 has pulled in only the minimum development-proof signing dependency demonstrated necessary for live OAuth; it does not claim production signing, store distribution, update continuity, or release readiness.
- `ANDROID-NATIVE-DELIVERY-001` and `ANDROID-CAPTURE-001` remain outside this packet unless a direct representative-device acceptance blocker proves otherwise.
- No higher-priority integrity/security blocker or hard prerequisite outranks this bounded representative-device proof.

### `ROADMAP.md`

- Default Personal MIRA remains stock ChatGPT + Google Workspace first; Android is a companion over the same canonical reality.
- The required useful no-app Personal vertical already exists in completed backlog evidence, so representative-device proof is not blocked by the historical no-app-first sequencing rule.
- M2-M1 step 8 is representative-device proof. M2-M1-011 supplied the installable proof shell but did not itself earn physical-device/live-provider evidence.

### Direction result

**ALIGNED.** M2-M1-012 remains the smallest remaining vertical proof for the Android client core. Stable development signing is verified infrastructure evidence, not a production-release claim. The packet now proceeds only into bounded live provider/device proof.

## Stable development proof signing — verified

A dedicated development-only signing identity exists outside Git for package `com.mira.deviceproof`:

- alias: `mira-device-proof`;
- certificate SHA-1: `AF:E0:18:6B:7C:21:EA:74:D3:4C:4A:33:04:FF:B1:15:EF:DB:A5:6D`;
- certificate SHA-256: `B5:6A:2B:03:12:B2:AF:85:58:69:A7:19:66:3E:44:10:11:53:59:19:03:E7:94:8F:2E:0F:FC:F5:08:48:51:7B`;
- private key/keystore: deliberately outside Git;
- purpose: development representative-device OAuth proof only;
- forbidden use: production/release signing or any future claim completing `ANDROID-RELEASE-001`.

The repository workflow consumes optional secret `MIRA_DEVICE_PROOF_KEYSTORE_B64`, validates the stable public certificate fingerprint when present, fails honestly to `ephemeral_ci` when absent, validates the built APK signer, emits SHA-256/provenance, and marks only `stable_secret` artifacts `live_proof_eligible=true`.

After repository secret provisioning, workflow `33952071965` was rerun on unchanged implementation head `423ecc650689f64656115715fed85552d758bafb`; latest job `101353054082` passed with `Secret source: Actions`, `signing_mode=stable_secret`, the exact expected signing certificate, and `live_proof_eligible=true`. Artifact `9974483194` was independently downloaded and its APK SHA-256, sidecar, provenance and embedded signer certificate all matched exactly.

## Pre-merge proof-chain evidence

Successive Git-backed evidence-only CURRENT_WORK checkpoints were intentionally rebuilt and tested through CI. The last recorded checkpoint `16895f4b466622db1c4c37bb3b5b66d802b88c8b` passed CI `33984090401` and retained artifact `9974629890`, stable-secret and live-proof eligible.

The final merge candidate is not encoded into its own CURRENT_WORK text because that would create an impossible self-reference: changing the file to name the commit creates a new commit. Instead, GitHub PR metadata plus exact-head CI are the authoritative external proof for the final merge head immediately before merge. The merge must use `expected_head_sha` on that externally verified SHA.

## Provider target preflight — read only

The existing isolated provider fixture remains available in connected Google Drive under its original disposable M2-M1-001 proof title. Read-only metadata verified the expected `Metadata`, `Commands`, `Resources`, `Events`, and `Idempotency` tabs. Read-only `Resources` inspection verified the synthetic `entity` target remains at revision 1. No Google resource was created, modified, renamed, or republished by this preflight.

This fixture remains the only permitted provider target for the next proof step unless later readback proves it unsuitable. Legacy production state remains forbidden.

## Acceptance criteria

1. Prior packet closure exact-readback verified — **satisfied** by PR #116 merge `6e907c900f8d0496fa74296dc5213169d445a683` and post-merge CI `33951430022`.
2. Exact CI-produced proof APK retention with head/source/checksum provenance — **satisfied**.
3. Default CI debug signing instability proven and excluded from OAuth proof — **satisfied**.
4. Stable development-only proof signing identity exists outside Git with fixed public fingerprint — **satisfied**.
5. Repository secret `MIRA_DEVICE_PROOF_KEYSTORE_B64` provisioned without committing private key material — **satisfied by successful redacted Actions-secret consumption**.
6. Secret-backed CI reports `stable_secret`, expected certificate SHA-1, and `live_proof_eligible=true` — **satisfied**.
7. Stable artifact independently downloaded and APK/checksum/provenance/signer certificate verified — **satisfied**.
8. Final merge candidate exact-head CI — **must be verified externally from GitHub immediately before merge**.
9. Protected PR merge/readback and post-merge `main` CI stable artifact tied to exact merge SHA — **pending**.
10. One representative Android device installs and launches that exact post-merge stable retained debug APK — **pending**.
11. Provider-native Google authorization executes without exposing tokens or turning developer-only setup into future ordinary-user UX — **pending**.
12. Binding is restricted to isolated/synthetic MIRA 2.0 Google proof state; legacy production is untouched — **pending live verification**.
13. Device truthfully demonstrates disconnected/authorizing/verifying/verified-ready states and fails closed when readiness is absent — **pending live verification**.
14. One bounded canonical read reports exact revision and payload SHA-256 without rendering raw canonical payload, OAuth tokens, or private provider IDs — **pending live verification**.
15. One queued canonical mutation reports success only after acknowledged canonical readback through the existing shared writer — **pending live verification**.
16. When the existing stock-ChatGPT/native Workspace read path is available, independently verify the resulting canonical mutation from the same Authority — **pending live verification**.
17. Any device/provider failure is recorded as evidence and repaired only if it directly blocks these criteria; conflict UX, production release signing/distribution, notifications/TTS, capture hardware, and broad product UI remain deferred — **active constraint**.

## Protected constraints

- Never touch legacy MIRA production Sheets, Drive artifacts, Apps Script projects, briefs, schedules, automations, or other live state as development fixtures.
- Do not repeat M2-M1-001 Google provider proof, Google authorization repair, or fresh Apps Script publication.
- Do not create a new Google Sheet or Apps Script project merely for APK installation/proof if the existing isolated synthetic namespace remains suitable.
- Never commit the development proof private key, keystore Base64, tokens, credentials, private provider IDs, live spreadsheet contents, or personal operational state to the public repository.
- CI/build/signing evidence is not physical-device or provider evidence.
- The development proof signing identity must never be promoted into the production release signing identity.

## Exact next action / resume point

1. Freeze the branch. Read PR #117 head from GitHub and require exact-head CI success for that SHA. Do not edit CURRENT_WORK merely to copy that SHA into this file.
2. Merge PR #117 only with `expected_head_sha` equal to that externally verified final head.
3. Independently read back remote `main` at the merge SHA and require post-merge CI on that exact SHA.
4. Require the post-merge main run to retain a stable-secret artifact whose provenance binds both head/source to the merged main SHA; independently verify its APK SHA-256 and embedded signing certificate before installation.
5. Before live authorization, verify the fixed `com.mira.deviceproof` + stable certificate SHA-1 Android OAuth/provider registration path. No suitable Google Cloud/OAuth administration connector is currently available in the connected tool set, so any required provider-console action must be narrowly scoped and evidence-driven rather than guessed.
6. Install only the independently verified post-merge APK on one representative device, then execute provider-native authorization against the already-verified isolated disposable Workspace target.
7. Use the synthetic existing entity at revision 1 for bounded read and revision-checked queued mutation/readback; never substitute a production resource.
8. Independently verify the resulting canonical mutation through the stock-ChatGPT/native Workspace read path.
9. Before packet closeout, re-read FEATURES/BACKLOG/ROADMAP and preserve every unearned evidence gap.

## Recovery protocol

Read this file first, then verify branch/head and PR #117. M2-M1-001 through M2-M1-011 and M2-G0-012 are closed and must not be repeated. The stable development signing secret is provisioned and verified without exposing or committing private key material. The branch is to remain frozen after this self-reference repair; the actual final head and its exact-head CI are read from GitHub externally and merged only with expected-head protection. The isolated disposable Workspace fixture is read-only verified intact and remains the sole permitted provider target. After merge, require exact main/post-merge stable artifact verification, then bounded provider/device execution. Do not claim live-provider/device success until those provider and device readbacks actually occur.
