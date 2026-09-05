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
- **Pre-checkpoint implementation head:** `423ecc650689f64656115715fed85552d758bafb`.
- **Stable-secret verification run:** workflow `33952071965`, rerun/latest job `101353054082` — success on the unchanged authoritative head.
- **Verified stable artifact:** ID `9974483194`, name `mira-device-proof-423ecc650689f64656115715fed85552d758bafb`.
- **Dependencies:** M2-M1-001 through M2-M1-011 and M2-G0-012 are durably closed at their recorded evidence ceilings; the existing `device-proof-app`, `core`, and `google-workspace` modules remain the proof surface.
- **Current blocker:** repository/build/signing prerequisites are now satisfied. The remaining unearned evidence begins at live provider registration/authorization and physical representative-device execution.
- **Status:** active; stable development signing, exact APK provenance, and independent binary verification are complete. No live Google authorization or physical-device success is claimed yet.

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

**ALIGNED.** M2-M1-012 remains the smallest remaining vertical proof for the Android client core. Stable development signing is now verified infrastructure evidence, not a production-release claim. The packet now proceeds only into bounded live provider/device proof.

## Verified APK retention and provenance evidence

The branch first proved deterministic artifact retention and dual-SHA provenance at head `522f249e35e1deb9f8fa8df35e6261922cd69f3d`, CI `33951751487`, artifact `9965052790`. Two separate CI artifacts also proved that default ephemeral Android debug signing produces different certificates across hosted runners and therefore cannot be the fixed Android OAuth identity.

A dedicated development-only signing identity was generated outside Git for package `com.mira.deviceproof`:

- alias: `mira-device-proof`;
- certificate SHA-1: `AF:E0:18:6B:7C:21:EA:74:D3:4C:4A:33:04:FF:B1:15:EF:DB:A5:6D`;
- certificate SHA-256: `B5:6A:2B:03:12:B2:AF:85:58:69:A7:19:66:3E:44:10:11:53:59:19:03:E7:94:8F:2E:0F:FC:F5:08:48:51:7B`;
- private key/keystore: deliberately outside Git;
- purpose: development representative-device OAuth proof only;
- forbidden use: production/release signing or any future claim completing `ANDROID-RELEASE-001`.

The repository workflow now consumes optional secret `MIRA_DEVICE_PROOF_KEYSTORE_B64`, validates the stable public certificate fingerprint when present, fails honestly to `ephemeral_ci` when absent, validates the built APK signer, emits SHA-256/provenance, and marks only `stable_secret` artifacts `live_proof_eligible=true`.

## Stable-secret provider-independent verification — complete

After repository secret provisioning, CI was rerun on the **unchanged** authoritative implementation head `423ecc650689f64656115715fed85552d758bafb`.

Verified remote evidence:

1. workflow run `33952071965`, rerun/latest job `101353054082` completed successfully;
2. GitHub reported `Secret source: Actions`; the secret value remained redacted;
3. signing preparation reported `signing_mode=stable_secret`;
4. prepared certificate SHA-1 exactly matched `AF:E0:18:6B:7C:21:EA:74:D3:4C:4A:33:04:FF:B1:15:EF:DB:A5:6D`;
5. Android core, Google Workspace module, proof-app unit tests and `assembleDebug` all passed;
6. work-session alignment and code-ownership gates passed;
7. 461 Python tests passed;
8. 38 Apps Script tests passed;
9. retained artifact ID `9974483194` was created for exact branch head `423ecc650689f64656115715fed85552d758bafb`;
10. artifact archive digest is `sha256:b2e01ca1664d19778d2d40edd3accf97ff96f2edc418c8b2ac29c91ffa4c70cd`;
11. PR-CI checked-out/tested merge source SHA was `2cf9a3d5749560fb951b60d6251aca519d9b2503`;
12. APK SHA-256 is `9ecb56f8dca3ea51fd1736fea62417f2b0066274ef08977511c15a7ae3d325c6`;
13. provenance records `signing_mode=stable_secret`, the exact expected certificate SHA-1, and `live_proof_eligible=true`.

Independent artifact verification also completed outside the CI assertion path:

- downloaded artifact `9974483194` contained exactly APK, SHA-256 sidecar, and provenance file;
- recomputed APK SHA-256 exactly matched sidecar and provenance;
- the APK embedded signer certificate was independently extracted/read with `keytool` and exactly matched the stable SHA-1/SHA-256 above;
- signed APK entries verify against that certificate;
- no production signing or provider/device success is inferred from this repository/binary evidence.

The older same-head artifact `9965159204` came from the pre-secret run and is explicitly **not** the accepted live-proof binary.

## Acceptance criteria

1. Prior packet closure exact-readback verified — **satisfied** by PR #116 merge `6e907c900f8d0496fa74296dc5213169d445a683` and post-merge CI `33951430022`.
2. Exact CI-produced proof APK retention with head/source/checksum provenance — **satisfied**.
3. Default CI debug signing instability proven and excluded from OAuth proof — **satisfied**.
4. Stable development-only proof signing identity exists outside Git with fixed public fingerprint — **satisfied**.
5. Repository secret `MIRA_DEVICE_PROOF_KEYSTORE_B64` provisioned without committing private key material — **satisfied by successful redacted Actions-secret consumption**.
6. Secret-backed CI reports `stable_secret`, expected certificate SHA-1, and `live_proof_eligible=true` — **satisfied** by workflow `33952071965`, latest job `101353054082`.
7. Stable artifact independently downloaded and APK/checksum/provenance/signer certificate verified — **satisfied** for artifact `9974483194`.
8. Fresh exact-head CI after this durable evidence checkpoint and protected PR merge/readback — **pending**.
9. Post-merge `main` CI produces a stable-secret live-proof-eligible artifact tied to the exact merged main SHA — **pending**.
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

1. Require fresh exact-head CI after this CURRENT_WORK evidence checkpoint. It must still consume the Actions secret and produce a `stable_secret`, expected-fingerprint, `live_proof_eligible=true` artifact.
2. Update PR #117 evidence to the resulting exact checkpoint head and CI/artifact.
3. Merge PR #117 only with exact expected-head protection after all gates are green.
4. Independently read back remote `main` at the merge SHA and require post-merge CI on that exact SHA.
5. Require the post-merge main run to retain a stable-secret artifact whose provenance binds both head/source to the merged main SHA; independently verify its APK SHA-256 and embedded signing certificate before installation.
6. Before live authorization, verify the fixed `com.mira.deviceproof` + stable certificate SHA-1 Android OAuth/provider registration path and recover the existing isolated MIRA 2.0 synthetic Workspace target without creating or touching legacy resources.
7. Install only the independently verified post-merge APK on one representative device, then execute provider-native authorization, canonical read, queued mutation/readback, and stock-ChatGPT cross-readback as bounded evidence.
8. Before packet closeout, re-read FEATURES/BACKLOG/ROADMAP and preserve every unearned evidence gap.

## Recovery protocol

Read this file first, then verify branch/head and PR #117. M2-M1-001 through M2-M1-011 and M2-G0-012 are closed and must not be repeated. The stable development signing secret is provisioned and verified without exposing or committing private key material. Workflow `33952071965` latest job `101353054082` proved the stable signer on implementation head `423ecc650689f64656115715fed85552d758bafb`; artifact `9974483194` is the accepted pre-merge binary evidence, while older artifact `9965159204` is not. The next step is fresh CI on this durable checkpoint, protected merge, exact main/post-merge artifact verification, then bounded provider/device execution. Do not claim live-provider/device success until those provider and device readbacks actually occur.
