# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active/recovery packet and exact recovery state.

## Product direction

Default Personal MIRA remains stock ChatGPT + Google Workspace first. Android is a companion over the same canonical reality and must never become a second authority. M2-M1-001 through M2-M1-010 are durably closed at their recorded evidence ceilings. M2-M1-011 has removed the direct prerequisite that previously blocked honest representative-device proof: the repository now contains a minimal installable Android proof shell that composes the already-tested Android client modules. The implementation is merged and post-merge green. This packet still does not claim live Google authorization or physical-device success.

## Prior-packet recovery verification — 2026-09-04

- Repository: `Matthew-Beare/Mira-2.0`.
- Authoritative base before M2-M1-011: `0a52771046e9009ef0e65401cde3a755a1ee2ea2`.
- M2-M1-010 final closeout PR #113 exact head `ca1cb5d41ff315faf6cc891c77c7e0e3eb1397d0` passed CI `33903867343`, merged at `0a52771046e9009ef0e65401cde3a755a1ee2ea2`, and post-merge CI `33904029036` succeeded on that exact main SHA.
- Therefore M2-M1-010 is durably closed and must not be rerun.

## Session-start alignment verification — 2026-09-04 M2-M1-011

### `FEATURES.md`

- `CLIENT-ANDROID-001` remains `specified+implemented+test_verified+partial` and explicitly requires evidence-based device capabilities.
- `API-001`, `AUTH-001`, `STORE-001`, and `RECOVERY-002` preserve the shared canonical boundary and exact readback semantics already proven through M2-M1-010.
- `PROVIDER-002` requires ordinary-user connection semantics and forbids exporting avoidable technical setup to the user.

### `BACKLOG.md`

- `ANDROID-CLIENT-CORE-001` remains partial because live Android Google authorization/provider-device evidence, conflict UI and representative-device proof remain unfinished.
- `ANDROID-SYNC` is complete at deterministic integration evidence and must not be reopened merely to obtain device evidence.
- `ANDROID-RELEASE-001` remains later hardening; release signing/distribution is not required for the smallest installable proof shell.
- No higher-ranked unfinished BLOCKER on the active M2-M1 critical path was found. The direct prerequisite for representative-device proof was the absence of an installable application surface.

### `ROADMAP.md`

- M2-M1 steps 1 through 7 are complete at their bounded evidence ceilings.
- Step 8 is representative-device proof unless fresh ranking exposes a higher-priority blocker.
- Fresh ranking exposed one direct blocker to step 8: before this packet the repository had `android-client/core` and `android-client/google-workspace` Android library modules, but no installable app module/activity to execute them on a representative device.
- The default Personal no-app invariant remains preserved; this packet does not make Android mandatory for ordinary Personal use.

### `PRODUCT_INVARIANTS.md`

- Android must use the same connection/activation model as the rest of MIRA.
- Ordinary-user Android setup must not require copied provider IDs, edited OAuth scopes, developer-console work, pasted code or terminal commands when the app can automate those steps.
- Provider authorization/readiness and canonical readback must remain truthful and separately evidenced.
- The temporary proof shell is a developer verification surface, so bounded technical proof fields may exist there without becoming the future ordinary-user product UX.
- Legacy MIRA production data remains protected and may not be used as a device-proof fixture.

### Direction result

**ALIGNED.** The smallest direct prerequisite was an installable Android proof shell, not broad app development. The implementation remains bounded to composing the existing tested `core` and `google-workspace` modules into a minimal application surface for later representative-device authorization/binding/read/mutation evidence. It does not add unrelated product UI, notifications/TTS, capture hardware, release signing/distribution, legacy migration or new canonical state semantics.

## Active packet

### `M2-M1-011` — Minimal installable Android representative-device proof shell

- **Primary work:** `ANDROID-CLIENT-CORE-001`
- **Primary features:** `CLIENT-ANDROID-001`, `API-001`
- **Related invariants/features:** `AUTH-001`, `STORE-001`, `RECOVERY-002`, `PROVIDER-002`, `DATA-001`
- **Related work:** `ANDROID-SYNC`, `ANDROID-RELEASE-001`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Implementation branch:** `work/m2-m1-011-android-device-shell`
- **Packet base SHA:** `0a52771046e9009ef0e65401cde3a755a1ee2ea2`
- **Activation SHA:** `875a40008dbcc0739dd3ac11205bcf10492121a6`
- **First implementation candidate head:** `9d4c4564b86cec43986cb24ffa4abeaf05ead638`
- **First CI:** `33905104736` — failed only at the new Android app compile because the app directly consumed Google `AuthorizationResult`/`Task` types while Play Services Auth was hidden behind the provider module's `implementation` dependency; pre-Android governance gates were green.
- **Compile-classpath repair SHA:** `cea4fdd946cefc5c55b13db93d0a493a040cc256`
- **Repaired implementation CI:** `33905422565` — success, including proof-app unit tests and `:device-proof-app:assembleDebug`.
- **Final implementation/evidence head:** `dd6c6cafb4034d5beb242b1d7833ab9616ca2e78`
- **Final implementation exact-head CI:** `33905670967` — success across all repository gates, Android tests and proof APK build.
- **Implementation PR:** #114 — merged with exact expected-head protection.
- **Implementation merge SHA:** `e66d5374dc0076bfa3d8ea87fa5c73437e210b0c`.
- **Implementation remote-main readback:** exact `e66d5374dc0076bfa3d8ea87fa5c73437e210b0c` verified.
- **Implementation post-merge CI:** `33905883963` — success on exact merge SHA, including proof APK build.
- **Lifecycle closeout branch:** `work/m2-m1-011-lifecycle-closeout`.
- **Lifecycle ROADMAP checkpoint:** `1a78f4e3a231beabc149093be263537950cb5b01`.
- **Dependencies:** M2-M1-001 through M2-M1-010 complete at recorded evidence ceilings; M2-M1-011 implementation merge and post-merge verification green.
- **Blocker removed at build/test evidence:** an installable Android application module/activity now exists for later representative-device execution.
- **Remaining evidence gaps:** live Android Google authorization/provider-device execution, representative-device canonical read/mutation proof, and user-facing conflict resolution.
- **Status:** implementation complete and merge/post-merge verified; lifecycle-only self-closing checkpoint active.

## Objective result

**IMPLEMENTED, MERGED, AND TEST-VERIFIED AT REPOSITORY/BUILD EVIDENCE.**

The repository now contains one bounded Android application module, `device-proof-app`, whose sole job is to make the existing MIRA Android client executable on a representative device later.

1. Root Android Gradle configuration exposes the Android application plugin and registers exactly one new `:device-proof-app` module.
2. The app has one exported launcher activity and the required Internet permission; no broad navigation architecture or product redesign was added.
3. `DeviceProofActivity` composes existing `GooglePlayWorkspaceAuthorization`, `GoogleWorkspaceRestApi`, `GoogleWorkspaceConnection`, `GoogleWorkspaceTransport`, `OfflineSyncStateStore`, `ReconnectCoordinator`, `CanonicalResourceReader`, and `CanonicalResourceMutator` rather than copying their logic.
4. Google consent/resource selection remains provider-native and least-authority through the existing `drive.file` authorization facade.
5. Proof actions remain disabled until Workspace binding reports shared-writer readiness; consent alone is never displayed as verified success.
6. The proof surface distinguishes disconnected, authorization, verification, verified-ready, needs-attention and failure states.
7. Canonical read and queued mutation proof actions display resource identity, revision and payload SHA-256 while withholding raw payload from result presentation and never rendering/logging OAuth tokens or Workspace file IDs.
8. Mutation success is rendered only from the existing mutator's `APPLIED` result, which already requires acknowledged verified canonical readback; queued/pending/conflict/transport/protocol/local failures remain explicit non-success states.
9. The proof shell uses encrypted/Keystore-backed existing offline state and does not create a second state authority.
10. `DeviceProofPresentationTest` covers safe readiness/result mapping and verifies failed states cannot masquerade as success.
11. Android code-ownership metadata explicitly owns both proof-shell production classes and points them at direct verification.
12. CI runs existing Android tests, proof-app tests and assembles a debug APK on the same Java 17 / Android 36 toolchain.
13. The first app build correctly exposed a dependency-visibility error. The fix was intentionally narrow: add Play Services Auth directly at the app edge because the Activity directly consumes SDK public types; the provider module's implementation boundary was not widened.
14. Final implementation head `dd6c6cafb4034d5beb242b1d7833ab9616ca2e78` passed exact-head CI `33905670967`.
15. PR #114 merged only from that exact head at `e66d5374dc0076bfa3d8ea87fa5c73437e210b0c`; remote `main` independently read back that SHA.
16. Post-merge CI `33905883963` completed successfully on exact `main` SHA `e66d5374dc0076bfa3d8ea87fa5c73437e210b0c`.

## Acceptance criteria result

1. Exactly one installable Android application module registered — **satisfied**.
2. Application builds in CI on repository toolchain — **satisfied**.
3. One launcher activity/surface; no broad UI architecture — **satisfied**.
4. Existing `core` and `google-workspace` modules are composed, not copied — **satisfied**.
5. Honest connection/readiness state mapping — **satisfied at implementation/test evidence**.
6. Bounded canonical read and queued-mutation proof actions with exact revision/result evidence — **satisfied at implementation/test evidence**.
7. Secrets/tokens/private provider IDs not rendered, logged or committed — **satisfied by implementation boundary and tests; no live-secret claim**.
8. Missing authorization/readiness fails closed — **satisfied at implementation/test evidence**.
9. App wiring/state tests require no live Google credentials — **satisfied**.
10. Existing repository gates remain green — **satisfied through exact implementation post-merge CI `33905883963`**.
11. Ownership metadata expanded only for the proof shell — **satisfied**.
12. No Work mode/live provider mutation/legacy production/physical-device success claim — **satisfied**.
13. Pre-merge FEATURES/BACKLOG/ROADMAP/invariant re-read — **satisfied; no feature completion promotion earned by an APK build alone**.
14. Exact implementation-head CI, expected-head merge, remote-main readback and implementation post-merge CI — **satisfied**.
15. Lifecycle reconciliation preserves `CLIENT-ANDROID-001` / `ANDROID-CLIENT-CORE-001` as partial and records the proof-shell prerequisite without claiming device evidence — **satisfied in ROADMAP + this recovery checkpoint; BACKLOG lifecycle state remains partial and therefore requires no state transition**.
16. Durable packet closure — **pending this lifecycle branch's own exact-head CI, expected-head merge, remote-main readback and post-merge CI**.

## Session-end alignment verification — 2026-09-04 M2-M1-011 lifecycle closeout

### `FEATURES.md`

`CLIENT-ANDROID-001` remains partial. The installable proof shell adds implementation/build evidence but does not prove live Google authorization, provider/device execution, conflict UI or representative-device behavior. No FEATURES lifecycle promotion is warranted.

### `BACKLOG.md`

`ANDROID-CLIENT-CORE-001` remains partial, which is still the correct lifecycle state. M2-M1-011 removes the installable-shell prerequisite but does not close the remaining live authorization/provider-device, conflict-UI or representative-device gaps. Because the lifecycle state itself does not transition, the large canonical backlog is not rewritten solely to refresh evidence prose. `ANDROID-SYNC` remains complete at deterministic integration evidence and is not reopened. `ANDROID-RELEASE-001` remains later hardening.

### `ROADMAP.md`

M2-M1 now records M2-M1-001 through M2-M1-011 complete at their bounded evidence ceilings. Step 8 explicitly records the installable proof-shell prerequisite complete in M2-M1-011 while actual representative-device Google authorization/read/mutation evidence remains unfinished.

### `PRODUCT_INVARIANTS.md`

One-authority semantics, default no-app Personal priority, provider-native consent, ordinary-user connection simplicity, evidence honesty and legacy-data protection remain preserved. The developer proof shell's bounded technical inputs are not future ordinary-user UX and must not leak into the eventual native Connections surface.

### Direction result

**ALIGNED.** M2-M1-011 may close only as an installable, merged, test-verified proof harness. It does not establish physical-device, live-provider or ordinary-user Android readiness.

## Explicitly deferred

- Actual representative-device installation/execution evidence.
- Live Android Google authorization, Workspace verification and canonical read/mutation evidence.
- Ordinary-user native Connections UX and removal/automation of developer-only proof inputs.
- User-facing conflict-resolution workflow beyond truthful proof-state/error rendering.
- Notifications/TTS under `ANDROID-NATIVE-DELIVERY-001`.
- Camera/barcode/QR/NFC/BLE under `ANDROID-CAPTURE-001`.
- Release signing/store distribution/update continuity under `ANDROID-RELEASE-001`.
- Legacy production data and migration.

## Exact next action / resume point

1. Read back `work/m2-m1-011-lifecycle-closeout` exact head and verify it differs from implementation merge `e66d5374dc0076bfa3d8ea87fa5c73437e210b0c` only in lifecycle/recovery documentation.
2. Open one lifecycle-only PR and require exact-head CI.
3. Merge only with exact expected-head protection if green.
4. Independently read back remote `main` at the lifecycle merge SHA and require post-merge CI on that exact SHA.
5. **Once those conditions succeed, M2-M1-011 is durably closed. Do not create another M2-M1-011 closeout commit.**
6. After durable closure, re-read `CURRENT_WORK.md`, `FEATURES.md`, `BACKLOG.md`, `ROADMAP.md`, and `PRODUCT_INVARIANTS.md` from exact remote `main` and select exactly one next bounded packet by current dependency/risk/value ranking. Actual representative-device execution is the expected candidate, not an automatic selection.

## Recovery protocol

Read this file first and inspect its Git context. If this lifecycle checkpoint is on remote `main` and the commit containing it has successful post-merge CI, treat M2-M1-011 as **durably closed** and do not rerun its implementation or lifecycle work. If it remains on `work/m2-m1-011-lifecycle-closeout`, resume only the exact-head CI/expected-head merge/remote-main readback/post-merge CI sequence above. Do not use Work mode for this lifecycle closeout. Any later live representative-device/provider packet must be separately bounded and must not use legacy production state as a fixture.
