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
- **Verified head/artifact checkpoint:** `522f249e35e1deb9f8fa8df35e6261922cd69f3d`, CI `33951751487`, artifact ID `9965052790`.
- **Stable proof-signing support SHA:** `bd93c73e33b4585c959bd26b5b71dd001cc50328`.
- **Signing-mode gate SHA:** `3eadaea8a530076f5020b1873cc4790f390faab9`.
- **Dependencies:** M2-M1-001 through M2-M1-011 and M2-G0-012 are durably closed at their recorded evidence ceilings; the existing `device-proof-app`, `core`, and `google-workspace` modules remain the proof surface.
- **Current direct blocker:** the representative-device APK must be signed by one stable development identity that can be registered as the Android OAuth package/certificate pair. The private development proof key exists outside Git but its GitHub Actions secret has not yet been provisioned.
- **Status:** active; APK retention/provenance verified; unstable default debug signing proved unsuitable for live Google authorization; stable external proof-signing path implemented; exact-head CI and one repository-secret provisioning action remain before live device proof.

## Objective

Prove the already-implemented Android client path on one representative Android device against isolated synthetic MIRA 2.0 Google state, while preserving the same canonical Authority and honest evidence boundaries used by stock ChatGPT. The packet must not expand into general Android product development.

The representative-device binary must be traceable to an exact branch head and tested source SHA, and it must use one stable development-only signing identity so Google can bind the Android OAuth client to the fixed `com.mira.deviceproof` package/certificate pair. Production/release signing remains outside this packet.

## Session-start alignment verification — 2026-09-05 M2-M1-012

### `FEATURES.md`

- `CLIENT-ANDROID-001` remains `specified+implemented+test_verified+partial`; live Android Google authorization/provider-device behavior and representative-device evidence remain unfinished.
- `API-001`, `AUTH-001`, `STORE-001`, and `RECOVERY-002` require the Android client to read and mutate through the shared canonical boundary with exact readback rather than becoming a second authority.
- `PROVIDER-002` requires provider-native ordinary-user connection semantics and forbids avoidable provider IDs, OAuth scopes, developer-console work, pasted code, or terminal setup from becoming future ordinary-user UX.
- `DATA-001` forbids legacy production state from being used as a development fixture.
- `DEV-007` requires this packet to re-check product direction and evidence status before merge/closeout.

### `BACKLOG.md`

- `ANDROID-CLIENT-CORE-001` is the unfinished prerequisite carrying the live Google authorization/provider-device, conflict-UI, and representative-device evidence gaps.
- `ANDROID-SYNC` is already complete at deterministic integration evidence and must not be reopened simply to acquire physical-device evidence.
- `ANDROID-RELEASE-001` remains later hardening and already specifies a permanent signing identity outside Git. M2-M1-012 pulls in only the minimum development-proof signing dependency now shown to be necessary for live OAuth; it does not claim production signing, store distribution, update continuity, or release readiness.
- `ANDROID-NATIVE-DELIVERY-001` and `ANDROID-CAPTURE-001` remain outside this packet unless a direct representative-device acceptance blocker proves otherwise.
- No higher-priority integrity/security blocker or hard prerequisite outranks this bounded representative-device proof.

### `ROADMAP.md`

- Default Personal MIRA remains stock ChatGPT + Google Workspace first; Android is a companion over the same canonical reality.
- The required useful no-app Personal vertical already exists in completed backlog evidence, so representative-device proof is not blocked by the historical no-app-first sequencing rule.
- M2-M1 step 8 is representative-device proof. M2-M1-011 supplied the installable proof shell but did not itself earn physical-device/live-provider evidence.

### Direction result

**ALIGNED.** M2-M1-012 remains the smallest remaining vertical proof for the Android client core. Stable development signing is now a demonstrated hard dependency of Android OAuth, not speculative release work. No production signing or live-provider/device success is claimed.

## Verified APK retention/provenance evidence

Exact-head CI `33951751487` succeeded on branch head `522f249e35e1deb9f8fa8df35e6261922cd69f3d` and retained artifact:

- artifact name: `mira-device-proof-522f249e35e1deb9f8fa8df35e6261922cd69f3d`;
- artifact ID: `9965052790`;
- artifact archive digest: `sha256:fa83754dfdcbaf37a0564f256848f581f235febeeb41778d09729ffd5e22964d`;
- provenance `head_sha`: `522f249e35e1deb9f8fa8df35e6261922cd69f3d`;
- provenance exact checked-out/tested `source_sha`: `9bccf8aa28ba3e458ad3315bd8040dfd968e9a02`;
- APK SHA-256: `73136ea3566e999718191843825f6f825af3b018893c6b1ff10782891f757a2a`.

Independent archive readback confirmed exactly three expected files: APK, SHA-256 sidecar and provenance file. Recomputed APK SHA-256 exactly matched the sidecar and provenance value.

## Discovered live-auth blocker — unstable default debug signing

The retained CI artifacts proved that the Android Gradle default debug signing key is generated independently on these ephemeral CI runners:

- CI `33951598625` APK signing SHA-1: `13:F5:4D:EB:50:5A:E2:53:59:90:D4:58:04:4C:4F:F1:47:A5:C1:2B`;
- CI `33951751487` APK signing SHA-1: `E8:CB:31:FE:53:DE:AC:64:E0:49:0A:5C:6F:06:77:49:80:D8:E4:68`.

Those certificates differ. Android Google OAuth credentials bind to the application package plus signing-certificate SHA-1, so a per-run signing identity cannot be the representative-device/live-provider proof identity.

This is a direct M2-M1-012 acceptance blocker and justifies the minimum stable-signing dependency from `ANDROID-RELEASE-001` without expanding into production release work.

## Stable development proof identity

A dedicated development-only PKCS#12 signing identity was generated outside Git for `com.mira.deviceproof`.

- alias: `mira-device-proof`;
- certificate SHA-1: `AF:E0:18:6B:7C:21:EA:74:D3:4C:4A:33:04:FF:B1:15:EF:DB:A5:6D`;
- certificate SHA-256: `B5:6A:2B:03:12:B2:AF:85:58:69:A7:19:66:3E:44:10:11:53:59:19:03:E7:94:8F:2E:0F:FC:F5:08:48:51:7B`;
- private key/keystore: deliberately **not committed** and must remain outside the public repository;
- purpose: development representative-device OAuth proof only;
- forbidden use: production/release signing, public distribution identity, or any future claim satisfying `ANDROID-RELEASE-001`.

The workflow/Gradle integration now behaves as follows:

1. `device-proof-app` accepts an external proof keystore only through environment variables; no key material is stored in source.
2. CI consumes optional repository secret `MIRA_DEVICE_PROOF_KEYSTORE_B64`.
3. When that secret is present, CI decodes the fixed external PKCS#12 key, verifies its public SHA-1 equals `AF:E0:18:6B:7C:21:EA:74:D3:4C:4A:33:04:FF:B1:15:EF:DB:A5:6D`, and marks signing mode `stable_secret`.
4. Until the secret is provisioned, CI generates an explicit ephemeral proof key and marks signing mode `ephemeral_ci`.
5. The built APK signing SHA-1 must exactly match the prepared keystore SHA-1 or CI fails.
6. Artifact provenance records `signing_mode`, `signing_cert_sha1`, and `live_proof_eligible`.
7. Only `stable_secret` artifacts are marked `live_proof_eligible=true`; ephemeral artifacts may test the build plumbing but must not be installed as the accepted live-provider proof binary.

## Acceptance criteria

1. Prior packet closure is exact-readback verified — **satisfied** by PR #116 merge `6e907c900f8d0496fa74296dc5213169d445a683` and post-merge CI `33951430022`.
2. Exact CI-produced proof APK retention with head/source/checksum provenance — **satisfied** at head `522f249e35e1deb9f8fa8df35e6261922cd69f3d`, CI `33951751487`, artifact `9965052790`.
3. Default CI debug signing instability is proven and not silently used for OAuth proof — **satisfied** by two distinct signing SHA-1 readbacks above.
4. Stable development-only proof signing identity exists outside Git with fixed public fingerprint — **satisfied locally; GitHub secret provisioning pending**.
5. CI explicitly distinguishes stable vs ephemeral proof signing and marks only stable artifacts live-proof eligible — **implemented; fresh exact-head CI pending**.
6. Repository secret `MIRA_DEVICE_PROOF_KEYSTORE_B64` is provisioned with the private development keystore without committing it — **user/provider action pending**.
7. A fresh exact-head CI run using that secret reports `signing_mode=stable_secret`, exact certificate SHA-1 `AF:E0:18:6B:7C:21:EA:74:D3:4C:4A:33:04:FF:B1:15:EF:DB:A5:6D`, and `live_proof_eligible=true` — **pending**.
8. The accepted stable artifact is independently downloaded/read back and its APK/checksum/provenance/signing certificate are internally consistent — **pending**.
9. One representative Android device installs and launches that exact stable retained debug APK — **pending**.
10. Provider-native Google authorization executes without exposing tokens or turning developer-only setup into future ordinary-user UX — **pending**.
11. Binding is restricted to the existing isolated/synthetic MIRA 2.0 Google proof namespace; legacy production is untouched — **pending live verification**.
12. The device truthfully demonstrates disconnected/authorizing/verifying/verified-ready states and fails closed when readiness is absent — **pending live verification**.
13. One bounded canonical read reports exact revision and payload SHA-256 without rendering raw canonical payload, OAuth tokens, or private provider IDs — **pending live verification**.
14. One queued canonical mutation reports success only after acknowledged canonical readback through the existing shared writer — **pending live verification**.
15. When the existing stock-ChatGPT/native Workspace read path is available, independently verify the resulting canonical mutation from the same Authority — **pending live verification**.
16. Any device/provider failure is recorded as evidence and repaired only if it directly blocks these criteria; conflict UX, production release signing/distribution, notifications/TTS, capture hardware, and broad product UI remain deferred — **active constraint**.

## Protected constraints

- Never touch legacy MIRA production Sheets, Drive artifacts, Apps Script projects, briefs, schedules, automations, or other live state as development fixtures.
- Do not repeat M2-M1-001 Google provider proof, Google authorization repair, or fresh Apps Script publication.
- Do not create a new Google Sheet or Apps Script project merely for APK installation/proof if the existing isolated synthetic namespace remains suitable.
- Never commit the development proof private key, keystore Base64, tokens, credentials, private provider IDs, live spreadsheet contents, or personal operational state to the public repository.
- CI/build evidence is not physical-device or provider evidence.
- The development proof signing identity must never be promoted into the production release signing identity.

## Exact next action / resume point

1. Require fresh exact-head CI after this checkpoint. With the repository secret still absent, the expected result is green CI plus artifact provenance `signing_mode=ephemeral_ci` and `live_proof_eligible=false`; this proves fail-honest behavior but is not the accepted device binary.
2. Provision exactly one GitHub Actions repository secret named `MIRA_DEVICE_PROOF_KEYSTORE_B64` from the private development keystore material held outside Git. This is development infrastructure only, not ordinary-user onboarding.
3. Re-run CI on the unchanged authoritative branch head after secret provisioning.
4. Require `signing_mode=stable_secret`, certificate SHA-1 `AF:E0:18:6B:7C:21:EA:74:D3:4C:4A:33:04:FF:B1:15:EF:DB:A5:6D`, and `live_proof_eligible=true` in artifact provenance.
5. Independently download/read back that stable artifact and verify its APK/checksum/provenance/signature before installation.
6. Register/use the fixed `com.mira.deviceproof` + stable certificate SHA-1 Android OAuth client only in the isolated MIRA 2.0 development authorization project/namespace; never legacy production.
7. Only then proceed to representative-device install, provider-native authorization, canonical read/mutation/readback and stock-ChatGPT cross-readback.
8. Before merge/closeout, re-read FEATURES/BACKLOG/ROADMAP, preserve unearned evidence gaps, merge only with expected-head protection, then require exact remote-main readback and post-merge CI.

## Recovery protocol

Read this file first, then verify branch/head and PR #117. M2-M1-001 through M2-M1-011 and M2-G0-012 are closed and must not be repeated. APK retention and dual-SHA provenance are verified. The active blocker is stable development proof signing for Android OAuth. Private key material must remain outside Git. The current code supports an optional `MIRA_DEVICE_PROOF_KEYSTORE_B64` Actions secret and truthfully marks fallback CI artifacts non-live-proof-eligible. Do not install an `ephemeral_ci` artifact as the accepted provider proof binary and do not claim live-provider/device success until the stable artifact and provider readbacks actually occur.
