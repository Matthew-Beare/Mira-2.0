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
- **Artifact-retention implementation SHA:** `a07696a366c29d8caa15f9190deb068778b49430`.
- **Dependencies:** M2-M1-001 through M2-M1-011 and M2-G0-012 are durably closed at their recorded evidence ceilings; the existing `device-proof-app`, `core`, and `google-workspace` modules remain the proof surface.
- **Current direct blocker:** M2-M1-011 CI assembled a debug APK but retained no downloadable Actions artifact, so representative-device installation cannot yet use an exact CI-produced binary with durable provenance.
- **Status:** active; artifact-retention prerequisite implemented, exact-head CI/artifact readback and representative-device execution pending.

## Objective

Prove the already-implemented Android client path on one representative Android device against isolated synthetic MIRA 2.0 Google state, while preserving the same canonical Authority and honest evidence boundaries used by stock ChatGPT. The packet must not expand into general Android product development.

The smallest immediate prerequisite is to retain the exact CI-built debug APK plus SHA-256 provenance so the binary installed on the representative device can be tied to an exact Git revision. No new Google resource or Apps Script publication is required merely to obtain the APK.

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

## Implemented prerequisite — exact proof APK retention

At `a07696a366c29d8caa15f9190deb068778b49430`, CI was extended only after the existing Android test/assemble step to:

1. require the expected debug output at `android-client/device-proof-app/build/outputs/apk/debug/device-proof-app-debug.apk`;
2. generate a SHA-256 sidecar for that exact APK;
3. fail closed if the APK is absent;
4. retain the APK and SHA-256 as a GitHub Actions artifact named `mira-device-proof-${{ github.sha }}`;
5. use the current GitHub `actions/upload-artifact@v7` line.

This change does not alter Android runtime behavior, provider scopes, canonical state semantics, app permissions, signing identity, or any Google resource.

## Acceptance criteria

1. Prior packet closure is exact-readback verified — **satisfied** by PR #116 merge `6e907c900f8d0496fa74296dc5213169d445a683` and post-merge CI `33951430022`.
2. Exact CI-produced proof APK is retained with commit-bound artifact identity and SHA-256 sidecar — **implemented; CI/artifact readback pending**.
3. Fresh exact-head CI passes all existing repository gates plus APK provenance/retention — **pending**.
4. The retained artifact is independently listed/read back from the exact successful workflow run before installation — **pending**.
5. One representative Android device installs and launches the exact retained debug APK — **pending**.
6. Provider-native Google authorization executes without exposing tokens or turning developer-only setup into future ordinary-user UX — **pending**.
7. Binding is restricted to the existing isolated/synthetic MIRA 2.0 Google proof namespace; legacy production is untouched — **pending live verification**.
8. The device truthfully demonstrates disconnected/authorizing/verifying/verified-ready states and fails closed when readiness is absent — **pending live verification**.
9. One bounded canonical read reports exact revision and payload SHA-256 without rendering raw canonical payload, OAuth tokens, or private provider IDs — **pending live verification**.
10. One queued canonical mutation reports success only after acknowledged canonical readback through the existing shared writer — **pending live verification**.
11. When the existing stock-ChatGPT/native Workspace read path is available, independently verify the resulting canonical mutation from the same Authority — **pending live verification**.
12. Any device/provider failure is recorded as evidence and repaired only if it directly blocks these criteria; conflict UX, release signing/distribution, notifications/TTS, capture hardware, and broad product UI remain deferred — **active constraint**.

## Protected constraints

- Never touch legacy MIRA production Sheets, Drive artifacts, Apps Script projects, briefs, schedules, automations, or other live state as development fixtures.
- Do not repeat M2-M1-001 Google provider proof, Google authorization repair, or fresh Apps Script publication.
- Do not create a new Google Sheet or Apps Script project merely for APK installation/proof if the existing isolated synthetic namespace remains suitable.
- Do not commit tokens, credentials, private provider IDs, live spreadsheet contents, or personal operational state to the public repository.
- CI/build evidence is not physical-device or provider evidence.
- A debug artifact retained for development proof does not satisfy `ANDROID-RELEASE-001`.

## Exact next action / resume point

1. Open the bounded M2-M1-012 PR from `work/m2-m1-012-android-device-proof`.
2. Require fresh exact-head CI after this CURRENT_WORK checkpoint; repair only failures directly caused by M2-M1-012.
3. On green CI, list the exact run artifacts and verify one `mira-device-proof-<exact-head-sha>` artifact exists before claiming APK retention succeeded.
4. Download/read back that exact artifact and verify the included APK plus SHA-256 sidecar are present and internally consistent.
5. Only then proceed to representative-device installation and live provider/canonical proof. The unavoidable physical-device/provider consent actions may require the user, but no provider-resource recreation or broad technical setup should be exported to them.
6. Before merge/closeout, re-read FEATURES/BACKLOG/ROADMAP, preserve unearned evidence gaps, merge only with expected-head protection, then require exact remote-main readback and post-merge CI.

## Recovery protocol

Read this file first, then verify branch/head and the active M2-M1-012 PR. M2-M1-001 through M2-M1-011 and M2-G0-012 are closed and must not be repeated. The artifact-retention implementation is `a07696a366c29d8caa15f9190deb068778b49430`; this CURRENT_WORK checkpoint follows it and therefore requires a fresh exact-head CI run. Do not claim physical-device/live-provider success until the representative-device actions and canonical readbacks actually occur.
