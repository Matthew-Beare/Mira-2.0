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
- **Initial artifact-retention SHA:** `a07696a366c29d8caa15f9190deb068778b49430`.
- **Current provenance-repair implementation SHA:** `13b0ae27d7b923289a643cfc7d59b689cb3e4c52`.
- **Dependencies:** M2-M1-001 through M2-M1-011 and M2-G0-012 are durably closed at their recorded evidence ceilings; the existing `device-proof-app`, `core`, and `google-workspace` modules remain the proof surface.
- **Current direct blocker:** require fresh exact-head CI and artifact readback after the provenance repair, then install the exact retained APK on a representative Android device.
- **Status:** active; exact APK retention/provenance implementation repaired, final exact-head CI/artifact verification and representative-device execution pending.

## Objective

Prove the already-implemented Android client path on one representative Android device against isolated synthetic MIRA 2.0 Google state, while preserving the same canonical Authority and honest evidence boundaries used by stock ChatGPT. The packet must not expand into general Android product development.

The immediate prerequisite is a retained CI-built debug APK whose provenance distinguishes the authoritative branch head from the exact source commit actually checked out and tested by GitHub Actions. No new Google resource or Apps Script publication is required merely to obtain the APK.

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
- `ANDROID-RELEASE-001` remains later hardening. This packet may retain a development debug APK for proof without claiming production signing, store distribution, update continuity, or release readiness.
- `ANDROID-NATIVE-DELIVERY-001` and `ANDROID-CAPTURE-001` remain outside this packet unless a direct representative-device acceptance blocker proves otherwise.
- No higher-priority integrity/security blocker or hard prerequisite outranks the bounded representative-device proof.

### `ROADMAP.md`

- Default Personal MIRA remains stock ChatGPT + Google Workspace first; Android is a companion over the same canonical reality.
- The required useful no-app Personal vertical already exists in completed backlog evidence, so representative-device proof is not blocked by the historical no-app-first sequencing rule.
- M2-M1 step 8 is representative-device proof. M2-M1-011 supplied the installable proof shell but did not itself earn physical-device/live-provider evidence.

### Direction result

**ALIGNED.** M2-M1-012 is the smallest remaining vertical proof for the Android client core. APK retention is a direct prerequisite for exact-binary representative-device evidence, not release engineering scope creep. No live-provider/device success is claimed until provider and device readback actually occur.

## APK provenance findings and repair

### First retained artifact — useful but insufficient provenance

Exact-head CI `33951598625` on branch head `ced0b5cfa52d4e3dca7fbdfc260eec7e5056569d` passed every repository gate, including APK build, SHA-256 generation and upload. It produced artifact ID `9965011238`, digest `sha256:721d5fe73c983593a814bd15740eca011227c7b48572f8e9b5f1debe1ea7c511`.

However, the artifact was named `mira-device-proof-32bc81b787fae530f1f257f35387ca3e86c3dbf9`, not with the authoritative PR head. This exposed an important GitHub Actions semantic: for `pull_request` runs, `github.sha` is the synthetic merge-test commit, while `github.event.pull_request.head.sha` is the actual PR head. The first artifact is therefore retained evidence that the upload mechanism works, but it is **not accepted as the final representative-device binary provenance record**.

### Provenance repair — `13b0ae27d7b923289a643cfc7d59b689cb3e4c52`

The workflow now preserves both truths instead of conflating them:

1. artifact name uses `${{ github.event.pull_request.head.sha || github.sha }}` so PR artifacts are bound visibly to the authoritative head and push artifacts fall back to the pushed SHA;
2. a provenance file records repository, event name, run ID, authoritative `head_sha`, exact checked-out/tested `source_sha`, and APK SHA-256;
3. CI verifies `git rev-parse HEAD` exactly equals the workflow `source_sha` before emitting provenance;
4. the APK SHA-256 sidecar remains required;
5. upload fails closed if expected files are missing;
6. `actions/upload-artifact` is pinned to verified upstream commit `043fb46d1a93c77aae656e7c1c64a875d1fc6a0a` corresponding to v7.0.1.

This keeps normal PR merge-result testing intact while making the representative-device binary traceable to both the branch head under review and the exact source commit that produced the APK.

## Acceptance criteria

1. Prior packet closure is exact-readback verified — **satisfied** by PR #116 merge `6e907c900f8d0496fa74296dc5213169d445a683` and post-merge CI `33951430022`.
2. Exact CI-produced proof APK is retained with head-bound artifact identity, checked-out source SHA, APK SHA-256 sidecar and provenance manifest — **implemented at `13b0ae27d7b923289a643cfc7d59b689cb3e4c52`; final CI/artifact readback pending**.
3. Fresh exact-head CI passes all existing repository gates plus repaired APK provenance/retention — **pending**.
4. The retained artifact is independently listed/read back from the exact successful workflow run and its name matches the authoritative branch head — **pending**.
5. Download/readback confirms the artifact contains the APK, SHA-256 sidecar and provenance file and that the checksum is internally consistent — **pending**.
6. One representative Android device installs and launches the exact retained debug APK — **pending**.
7. Provider-native Google authorization executes without exposing tokens or turning developer-only setup into future ordinary-user UX — **pending**.
8. Binding is restricted to the existing isolated/synthetic MIRA 2.0 Google proof namespace; legacy production is untouched — **pending live verification**.
9. The device truthfully demonstrates disconnected/authorizing/verifying/verified-ready states and fails closed when readiness is absent — **pending live verification**.
10. One bounded canonical read reports exact revision and payload SHA-256 without rendering raw canonical payload, OAuth tokens, or private provider IDs — **pending live verification**.
11. One queued canonical mutation reports success only after acknowledged canonical readback through the existing shared writer — **pending live verification**.
12. When the existing stock-ChatGPT/native Workspace read path is available, independently verify the resulting canonical mutation from the same Authority — **pending live verification**.
13. Any device/provider failure is recorded as evidence and repaired only if it directly blocks these criteria; conflict UX, release signing/distribution, notifications/TTS, capture hardware, and broad product UI remain deferred — **active constraint**.

## Protected constraints

- Never touch legacy MIRA production Sheets, Drive artifacts, Apps Script projects, briefs, schedules, automations, or other live state as development fixtures.
- Do not repeat M2-M1-001 Google provider proof, Google authorization repair, or fresh Apps Script publication.
- Do not create a new Google Sheet or Apps Script project merely for APK installation/proof if the existing isolated synthetic namespace remains suitable.
- Do not commit tokens, credentials, private provider IDs, live spreadsheet contents, or personal operational state to the public repository.
- CI/build evidence is not physical-device or provider evidence.
- A debug artifact retained for development proof does not satisfy `ANDROID-RELEASE-001`.

## Exact next action / resume point

1. Require fresh exact-head CI after this CURRENT_WORK checkpoint; repair only failures directly caused by M2-M1-012.
2. On green CI, list the exact run artifacts and verify one artifact named `mira-device-proof-<authoritative-head-sha>` exists.
3. Download/read back that exact artifact and verify the APK, SHA-256 sidecar and provenance file are present; require checksum consistency and matching head/source fields before installation.
4. Only then proceed to representative-device installation and live provider/canonical proof. The unavoidable physical-device/provider consent actions may require the user, but no provider-resource recreation or broad technical setup should be exported to them.
5. Before merge/closeout, re-read FEATURES/BACKLOG/ROADMAP, preserve unearned evidence gaps, merge only with expected-head protection, then require exact remote-main readback and post-merge CI.

## Recovery protocol

Read this file first, then verify branch/head and PR #117. M2-M1-001 through M2-M1-011 and M2-G0-012 are closed and must not be repeated. The first retained artifact from CI `33951598625` proved upload viability but exposed the PR merge-SHA naming bug and is not the accepted final proof binary. The provenance repair is `13b0ae27d7b923289a643cfc7d59b689cb3e4c52`; this CURRENT_WORK checkpoint follows it and therefore requires a fresh exact-head CI run. Do not claim physical-device/live-provider success until the representative-device actions and canonical readbacks actually occur.
