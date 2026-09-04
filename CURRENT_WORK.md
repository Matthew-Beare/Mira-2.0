# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active/recovery packet and exact recovery state.

## Product direction

Default Personal MIRA remains stock ChatGPT + Google Workspace first. Android is a companion over the same canonical reality and must never become a second authority. M2-M1-001 through M2-M1-010 are durably closed at their recorded evidence ceilings. M2-M1-011 addresses the hard prerequisite exposed by fresh post-closeout ranking: representative-device proof cannot be performed because the repository currently contains Android library modules but no installable application shell/activity.

## Prior-packet recovery verification — 2026-09-04

- Repository: `Matthew-Beare/Mira-2.0`.
- Authoritative base `main`: `0a52771046e9009ef0e65401cde3a755a1ee2ea2`.
- M2-M1-010 implementation PR #110 merged at `9e2314ee1e653291ecb857c6faa126f603fcd33d`; implementation post-merge CI `33902636268` succeeded.
- M2-M1-010 lifecycle PR #112 merged at `c83e418ea29ce151ff373db96dcbe0db875fe423`; lifecycle post-merge CI `33903459412` succeeded.
- M2-M1-010 final closeout PR #113 exact head `ca1cb5d41ff315faf6cc891c77c7e0e3eb1397d0` passed CI `33903867343`, merged at `0a52771046e9009ef0e65401cde3a755a1ee2ea2`, and post-merge CI `33904029036` succeeded on that exact main SHA.
- Therefore M2-M1-010 is durably closed and must not be rerun.

## Session-start alignment verification — 2026-09-04 M2-M1-011

### `FEATURES.md`

- `CLIENT-ANDROID-001` remains `specified+implemented+test_verified+partial` and explicitly requires evidence-based device capabilities.
- `API-001`, `AUTH-001`, `STORE-001`, and `RECOVERY-002` preserve the shared canonical boundary and exact readback semantics already proven through M2-M1-010.
- `PROVIDER-002` requires ordinary-user connection semantics and forbids exporting avoidable technical setup to the user.

### `BACKLOG.md`

- `ANDROID-CLIENT-CORE-001` remains partial through M2-M1-010 because live Android Google authorization/provider-device evidence, conflict UI and representative-device proof remain unfinished.
- `ANDROID-SYNC` is complete at deterministic integration evidence and must not be reopened merely to obtain device evidence.
- `ANDROID-RELEASE-001` remains later hardening; release signing/distribution is not required to create the smallest installable proof shell.
- No higher-ranked unfinished BLOCKER on the active M2-M1 critical path was found. Other no-app service prerequisites remain valid but are explicitly ranked below the active M2-M0/M2-M1 path unless selected as hard dependencies.

### `ROADMAP.md`

- M2-M1 steps 1 through 7 are complete at their bounded evidence ceilings.
- Step 8 is representative-device proof unless fresh ranking exposes a higher-priority blocker.
- Fresh ranking exposed one direct blocker to step 8: the repository has `android-client/core` and `android-client/google-workspace` Android library modules, but no installable app module/activity to execute the already-tested client code on a representative device.
- The default Personal no-app invariant remains preserved; this packet does not make Android mandatory for ordinary Personal use.

### `PRODUCT_INVARIANTS.md`

- Android must use the same connection/activation model as the rest of MIRA.
- Device proof must not require the user to copy provider IDs, edit OAuth scopes, open developer consoles, paste code, or understand internal plumbing when the app can automate those steps.
- Provider authorization/readiness and canonical readback must remain truthful and separately evidenced.
- Legacy MIRA production data remains protected and may not be used as a device-proof fixture.

### Direction result

**ALIGNED.** The smallest next prerequisite is an installable Android proof shell, not broad app development. It must wire the existing tested `core` and `google-workspace` modules into a minimal application surface capable of later representative-device authorization/binding/read/mutation evidence. It must not add unrelated product UI, notifications/TTS, capture hardware, release signing/distribution, legacy migration, or new canonical state semantics.

## Active packet

### `M2-M1-011` — Minimal installable Android representative-device proof shell

- **Primary work:** `ANDROID-CLIENT-CORE-001`
- **Primary features:** `CLIENT-ANDROID-001`, `API-001`
- **Related invariants/features:** `AUTH-001`, `STORE-001`, `RECOVERY-002`, `PROVIDER-002`, `DATA-001`
- **Related work:** `ANDROID-SYNC`, `ANDROID-RELEASE-001`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `work/m2-m1-011-android-device-shell`
- **Base SHA:** `0a52771046e9009ef0e65401cde3a755a1ee2ea2`
- **Current head:** this activation checkpoint; read back the branch after commit before implementation
- **Dependencies:** M2-M1-001 through M2-M1-010 complete at recorded evidence ceilings; existing Android `core` and `google-workspace` library modules green
- **Blocker being removed:** no installable Android application module/activity exists for representative-device execution
- **Status:** active

## Objective

Create the smallest installable Android application shell required to execute the already-built MIRA Android client path on a representative device later. The shell is a proof harness, not the finished Android product.

It must provide a single bounded application flow that can:

1. launch as an actual Android application;
2. instantiate the existing Google Workspace authorization/binding path rather than duplicate it;
3. expose truthful connection/proof state without treating consent as verified readiness;
4. invoke the existing canonical reader and queued mutator seams through the existing modules;
5. display enough exact identity/revision/result information to collect representative-device evidence without exposing secrets;
6. fail closed and visibly on missing authorization, missing binding, stale/conflict results or transport failure;
7. contain no hard-coded private provider IDs, credentials, tokens, user data or legacy production references.

## Acceptance criteria

1. Add exactly one installable Android application module and register it in the existing Gradle build.
2. Application builds in CI with the repository's current Android SDK/Java/Gradle toolchain.
3. One launcher activity/surface exists; no broad navigation architecture or cosmetic product redesign.
4. The app depends on and calls the existing `core` and `google-workspace` modules rather than copying authorization, transport, reader or mutator logic.
5. Connection state distinguishes at minimum disconnected/authorization-required, connected-but-unverified or needs-attention, and verified-ready semantics using existing evidence where available.
6. A bounded proof action can exercise canonical read and queued mutation seams with exact revision/result rendering suitable for later device evidence.
7. Secrets/tokens/private IDs are never rendered, logged, committed, or baked into resources/build config.
8. Missing provider configuration or device authorization fails closed with explicit non-success state; no fake green path.
9. Unit/build tests cover application wiring and state mapping without requiring live Google credentials in CI.
10. Existing Android, Python, Apps Script, feature-registry, lifecycle, alignment and ownership gates remain green.
11. Code ownership/release guard metadata is updated only as required for the new application component; no unrelated ownership expansion.
12. No live provider mutation, Work mode, legacy production state or physical-device claim occurs in this implementation packet unless the completed shell makes a safe same-session representative-device proof possible through an explicitly bounded follow-on step.
13. Before merge, re-read `FEATURES.md`, `BACKLOG.md`, `ROADMAP.md`, and `PRODUCT_INVARIANTS.md`; reconcile only evidence actually earned.
14. Exact-head CI, expected-head merge, remote-main readback and post-merge CI are required before packet closure.

## Explicitly deferred

- Full Android product UI/navigation/design system.
- Representative-device live Google authorization/read/mutation evidence until an installable shell exists.
- User-facing conflict-resolution workflow beyond truthful proof-state/error rendering.
- Notifications/TTS under `ANDROID-NATIVE-DELIVERY-001`.
- Camera/barcode/QR/NFC/BLE under `ANDROID-CAPTURE-001`.
- Release signing/store distribution/update continuity under `ANDROID-RELEASE-001`.
- Legacy production data and migration.

## Exact next action / resume point

1. Read back `work/m2-m1-011-android-device-shell` and verify this activation checkpoint is the branch head.
2. Inspect root Android Gradle settings/build files and current module contracts.
3. Add the minimal installable application module and launcher surface using existing client modules.
4. Add bounded tests and any required code-ownership metadata.
5. Run repository CI through a PR; repair only packet-relevant failures.
6. Re-read canonical product/lifecycle docs before merge and reconcile evidence honestly.
7. Merge only from exact green head, verify remote `main`, require post-merge CI, then decide whether representative-device execution can be the next bounded packet.

## Recovery protocol

Read this file first, then verify repository/branch/head. M2-M1-001 through M2-M1-010 are closed and must not be repeated. Resume M2-M1-011 only from the exact branch head. Do not broaden this packet into the finished Android application or live provider proof. If a separate integrity/security blocker is discovered, checkpoint this packet before switching scope.
