# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active/recovery packet and exact recovery state.

## Prior-packet durable closure — 2026-09-05

`M2-G0-012` is durably closed and must not be rerun.

- Governance repair head `e5ddd961dcdb64374e4c6a15a75caee287ea0cec` passed exact-head CI `33951335264`.
- PR #116 merged with expected-head protection as `6e907c900f8d0496fa74296dc5213169d445a683`.
- Remote `main` readback confirmed exactly `6e907c900f8d0496fa74296dc5213169d445a683`.
- Post-merge CI `33951430022` succeeded on that exact main SHA.
- `M2-M1-011` is therefore durably closed at repository/build evidence and must not be reopened for device proof.

## Active packet

### `M2-M1-012` — Android representative-device execution proof

- **Primary work:** `ANDROID-CLIENT-CORE-001`.
- **Primary features:** `CLIENT-ANDROID-001`, `API-001`.
- **Related invariants/features:** `AUTH-001`, `STORE-001`, `RECOVERY-002`, `PROVIDER-002`, `DATA-001`, `DEV-007`.
- **Repository:** `Matthew-Beare/Mira-2.0`.
- **Branch:** `work/m2-m1-012-postmerge-live-proof-gate`.
- **Base SHA:** `fa72b8f8b206f4295521f742e5059988d58c5ae0`.
- **Merged implementation/evidence PR:** #117.
- **Merged implementation/evidence SHA:** `fa72b8f8b206f4295521f742e5059988d58c5ae0`.
- **Post-merge exact-head CI:** `33984445584` — success.
- **Post-merge retained artifact:** ID `9974729883`, name `mira-device-proof-fa72b8f8b206f4295521f742e5059988d58c5ae0`.
- **Dependencies:** M2-M1-001 through M2-M1-011 and M2-G0-012 are durably closed at their recorded evidence ceilings. The existing `device-proof-app`, `core`, and `google-workspace` modules remain the bounded proof surface.
- **Current blocker:** repository/build/signing prerequisites are complete. The remaining unearned evidence begins at live Google Android OAuth registration/authorization and physical representative-device execution.
- **Status:** active; protected merge, exact main readback, post-merge CI, retained stable artifact, independent APK checksum/provenance verification and embedded signer verification are complete. No live Google authorization or physical-device success is claimed yet.

## Objective

Prove the already-implemented Android client path on one representative Android device against isolated synthetic MIRA 2.0 Google state while preserving the same canonical Authority and honest evidence boundaries used by stock ChatGPT. This packet must not expand into general Android product development.

The representative-device binary must remain traceable to exact Git/CI source, use the existing stable development-only signing identity for the fixed `com.mira.deviceproof` OAuth package/certificate pair, and report success only after provider/canonical readback. Production/release signing remains outside this packet.

## Session-start alignment verification — 2026-09-05 M2-M1-012 post-merge gate

### `FEATURES.md`

- `CLIENT-ANDROID-001` remains `specified+implemented+test_verified+partial`; live Android Google authorization/provider-device behavior and representative-device evidence remain unfinished.
- `API-001`, `AUTH-001`, `STORE-001`, and `RECOVERY-002` require the Android client to read and mutate through the shared canonical boundary with exact readback rather than becoming a second authority.
- `PROVIDER-002` requires provider-native ordinary-user connection semantics and forbids avoidable provider IDs, OAuth scopes, developer-console work, pasted code, or terminal setup from becoming future ordinary-user UX. Development-only provider registration required to prove the Android client is not ordinary-user onboarding.
- `DATA-001` forbids legacy production state from being used as a development fixture.
- `DEV-007` requires this packet to re-check product direction and evidence status before closeout.

### `BACKLOG.md`

- `ANDROID-CLIENT-CORE-001` remains the unfinished prerequisite carrying the live Google authorization/provider-device, conflict-UI, and representative-device evidence gaps.
- `ANDROID-SYNC` is already complete at deterministic integration evidence and must not be reopened merely to acquire physical-device evidence.
- `ANDROID-RELEASE-001` remains later hardening. M2-M1-012 used only the minimum stable development-proof signing dependency required for Android OAuth and does not claim production signing, store distribution, update continuity, or release readiness.
- `ANDROID-NATIVE-DELIVERY-001` and `ANDROID-CAPTURE-001` remain outside this packet unless a direct representative-device acceptance blocker proves otherwise.
- No higher-priority integrity/security blocker or hard prerequisite outranks this bounded representative-device proof.

### `ROADMAP.md`

- Default Personal MIRA remains stock ChatGPT + Google Workspace first; Android is a companion over the same canonical reality.
- The required useful no-app Personal vertical already exists in completed backlog evidence, so representative-device proof is not blocked by the historical no-app-first sequencing rule.
- M2-M1 step 8 remains representative-device proof. M2-M1-011 supplied the installable proof shell; PR #117 completed the stable-signing and exact-artifact prerequisites but did not earn physical-device/live-provider evidence.

### Direction result

**ALIGNED.** M2-M1-012 remains the smallest remaining vertical proof for the Android client core. Repository/build/signing evidence is complete. The packet now proceeds only into bounded live Google OAuth/provider and physical-device proof.

## Stable development proof signing — verified

A dedicated development-only signing identity exists outside Git for package `com.mira.deviceproof`:

- alias: `mira-device-proof`;
- certificate SHA-1: `AF:E0:18:6B:7C:21:EA:74:D3:4C:4A:33:04:FF:B1:15:EF:DB:A5:6D`;
- certificate SHA-256: `B5:6A:2B:03:12:B2:AF:85:58:69:A7:19:66:3E:44:10:11:53:59:19:03:E7:94:8F:2E:0F:FC:F5:08:48:51:7B`;
- private key/keystore: deliberately outside Git;
- purpose: development representative-device OAuth proof only;
- forbidden use: production/release signing or any future claim completing `ANDROID-RELEASE-001`.

Repository Actions secret `MIRA_DEVICE_PROOF_KEYSTORE_B64` is already provisioned and was successfully consumed by CI without exposing or committing private key material. The workflow validates the fixed public certificate fingerprint, emits APK SHA-256/provenance, and marks only the stable-secret artifact `live_proof_eligible=true`.

## Repository/build/signing evidence — complete through merge

1. PR #117 final head `114730c5ad0cb8caf24baad7d4c20243b7c06644` passed exact-head CI `33984339295`.
2. Exact-head artifact `9974701564`, `mira-device-proof-114730c5ad0cb8caf24baad7d4c20243b7c06644`, was retained before merge.
3. PR #117 merged with expected-head protection as `fa72b8f8b206f4295521f742e5059988d58c5ae0`.
4. Remote `main` readback confirmed exactly `fa72b8f8b206f4295521f742e5059988d58c5ae0`.
5. Post-merge exact-head CI `33984445584` succeeded on that exact main SHA.
6. Post-merge artifact `9974729883`, `mira-device-proof-fa72b8f8b206f4295521f742e5059988d58c5ae0`, was retained from that exact run. Artifact archive digest: `sha256:698e601cf42f76d566e9461fb88bac468e03eac6d2bd2a3997c18e556ee922ae`.
7. Independent archive extraction recomputed APK SHA-256 `9ecb56f8dca3ea51fd1736fea62417f2b0066274ef08977511c15a7ae3d325c6`; it matched the retained SHA-256 sidecar exactly.
8. Retained provenance reports `repository=Matthew-Beare/Mira-2.0`, `run_id=33984445584`, `head_sha=fa72b8f8b206f4295521f742e5059988d58c5ae0`, `source_sha=fa72b8f8b206f4295521f742e5059988d58c5ae0`, `signing_mode=stable_secret`, the expected signing SHA-1, and `live_proof_eligible=true`.
9. Independent APK signer inspection verified subject `CN=MIRA Device Proof Development, O=MIRA Development, C=US`, certificate SHA-1 `AF:E0:18:6B:7C:21:EA:74:D3:4C:4A:33:04:FF:B1:15:EF:DB:A5:6D`, and certificate SHA-256 `B5:6A:2B:03:12:B2:AF:85:58:69:A7:19:66:3E:44:10:11:53:59:19:03:E7:94:8F:2E:0F:FC:F5:08:48:51:7B`.

Repository/build/signing evidence is therefore complete for this packet. It does not prove live Google authorization or physical-device execution.

## Provider target preflight — read only

The existing isolated provider fixture remains available in connected Google Drive under its original disposable M2-M1-001 proof title. Read-only metadata previously verified the expected `Metadata`, `Commands`, `Resources`, `Events`, and `Idempotency` tabs. Read-only `Resources` inspection verified the synthetic `entity` target remains at revision 1. No Google resource was created, modified, renamed, or republished by this preflight.

This fixture remains the only permitted provider target for the next proof step unless fresh readback proves it unsuitable. Legacy production state remains forbidden.

No connected Google Cloud/OAuth administration capability is currently available in the active tool set. Provider-console work must therefore use a browser-capable authenticated Google Cloud Console lane and must inspect existing registration state before creating or changing anything.

## Acceptance criteria

1. Prior packet closure exact-readback verified — **satisfied** by PR #116 merge `6e907c900f8d0496fa74296dc5213169d445a683` and post-merge CI `33951430022`.
2. Exact CI-produced proof APK retention with head/source/checksum provenance — **satisfied**.
3. Default CI debug signing instability proven and excluded from OAuth proof — **satisfied**.
4. Stable development-only proof signing identity exists outside Git with fixed public fingerprint — **satisfied**.
5. Repository secret `MIRA_DEVICE_PROOF_KEYSTORE_B64` provisioned without committing private key material — **satisfied**.
6. Secret-backed CI reports `stable_secret`, expected certificate SHA-1, and `live_proof_eligible=true` — **satisfied**.
7. Stable artifact independently downloaded and APK/checksum/provenance/signer certificate verified — **satisfied**.
8. Final merge-candidate exact-head CI — **satisfied** by head `114730c5ad0cb8caf24baad7d4c20243b7c06644`, CI `33984339295`, artifact `9974701564`.
9. Protected PR merge/readback and post-merge `main` CI stable artifact tied to exact merge SHA — **satisfied** by merge `fa72b8f8b206f4295521f742e5059988d58c5ae0`, CI `33984445584`, artifact `9974729883`, and independent binary verification.
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
- Never commit the development proof private key, keystore Base64, OAuth tokens, credentials, private provider IDs, live spreadsheet contents, email contents, or personal operational state to the public repository.
- CI/build/signing evidence is not physical-device or provider evidence.
- The development proof signing identity must never be promoted into the production release signing identity.
- Inspect existing Google Android OAuth registration before creating or altering credentials; do not create duplicates by assumption.

## Exact next action / resume point

1. In a browser-capable authenticated Google Cloud Console session, inspect the applicable development project OAuth credentials and verify whether an Android OAuth client already exists for package `com.mira.deviceproof` with certificate SHA-1 `AF:E0:18:6B:7C:21:EA:74:D3:4C:4A:33:04:FF:B1:15:EF:DB:A5:6D`. Create or alter exactly one credential only if inspection proves it is missing or incorrect. Do not expose credential secrets in chat or Git.
2. Install only the exact post-merge APK with SHA-256 `9ecb56f8dca3ea51fd1736fea62417f2b0066274ef08977511c15a7ae3d325c6` on one representative Android device and confirm launch.
3. Execute provider-native Google authorization and bind only to the already-approved isolated disposable Workspace target. Never substitute legacy production state.
4. Verify truthful disconnected / authorizing / verifying / verified-ready state transitions and fail-closed behavior when readiness is absent.
5. Read the existing synthetic entity at revision 1 and capture only the exact revision plus payload SHA-256 required by the proof, not raw canonical payload or secrets.
6. Perform one revision-checked queued canonical mutation through the existing shared writer and require acknowledged canonical readback before displaying success.
7. Independently verify the resulting canonical mutation through the stock-ChatGPT/native Workspace read path.
8. Before packet closeout, re-read FEATURES/BACKLOG/ROADMAP, reconcile earned evidence only, and preserve every remaining unearned gap.

## Recovery protocol

Read this file first, then verify remote `main` and this active checkpoint branch. M2-M1-001 through M2-M1-011 and M2-G0-012 are closed and must not be repeated. PR #117 is merged as `fa72b8f8b206f4295521f742e5059988d58c5ae0`; post-merge CI `33984445584` and artifact `9974729883` are independently verified and complete the repository/build/signing prerequisite. The sole next gate is live Google Android OAuth registration/authorization plus representative-device execution against the existing isolated synthetic Workspace fixture. No live-provider/device success has yet been earned.
