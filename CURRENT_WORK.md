# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and exact recovery state.

## Product direction

Default Personal MIRA remains stock ChatGPT + Google Workspace with no external infrastructure prerequisite. When Android or another software writer is enabled, direct independent Google Sheets mutation remains disabled; commands use the verified serialized shared command boundary.

Ordinary users must never open Apps Script, paste code, manage triggers, copy provider IDs, run a terminal, or understand queued-writer internals merely to enable Android/shared access. The shipped Android path eventually needs an obvious MIRA Connect/Enable action and a clearly identified, appropriately verified provider consent surface.

`M2-M1-001` / `ANDROID-COMMAND-BOUNDARY-001` is complete and must not be rerun. `M2-M1-002` completed the first bounded enrollment/session trust slice of `ANDROID-CLIENT-CORE-001`. This packet continues only the next dependency-correct slice.

## Session-start alignment verification — 2026-09-02 M2-M1-003

### `FEATURES.md`

- `CLIENT-ANDROID-001` requires the Android native client to use `API-001`, keep durable client credentials OS-protected, remain replay-safe offline, and never become a canonical/provider authority.
- `API-001` remains the authenticated policy/data boundary. The opaque client credential issued by the `ClientSessionRegistry` is client authentication material, not provider/database/source authority.
- `RECOVERY-002` requires protected-credential failure to fail closed without corrupting canonical state or weakening unrelated modules.

### `BACKLOG.md`

- `ANDROID-CLIENT-CORE-001` remains the uncompleted umbrella prerequisite before `ANDROID-SYNC`.
- Enrollment/session identity and revocation are implemented by `M2-M1-002`; OS-protected Android credential storage is the exact next missing prerequisite before offline queue/reconnect work.
- Offline queue, cursor synchronization, bounded network reads/commands, conflict presentation, provider Connections UI, notifications/TTS, capture, and release packaging remain outside this packet.

### `ROADMAP.md`

- M2-M1 step 2 explicitly requires scoped/revocable client identity plus OS-protected durable credentials before step 3 offline queue/reconnect synchronization.
- The packet therefore advances step 2 only. It must not jump into the Android shared-state vertical or native feature fan-out.

### `PRODUCT_INVARIANTS.md`

- Android must reuse provider-neutral MIRA connection/service semantics and must not export developer/provider setup ceremony to ordinary users.
- Provider credentials and Google resource identifiers do not belong in Android protected-client storage. This packet stores only the opaque MIRA client credential needed to authenticate the enrolled same-user client.

### Direction result

**ALIGNED.** The smallest dependency-correct slice is a buildable Android client-core security module that accepts the opaque enrollment credential, protects its encryption key with Android Keystore, stores only authenticated ciphertext in app-private no-backup storage, fails closed on corruption/key loss, and supports local deletion. Offline sync and network transport remain later packets.

## Active packet

### `M2-M1-003` — Android client core, OS-protected credential storage

- **Primary work:** `ANDROID-CLIENT-CORE-001`
- **Primary features:** `CLIENT-ANDROID-001`, `API-001`
- **Related invariants/features:** `RECOVERY-002`, `AUTH-001`, `STORE-001`, `PROVIDER-002`, `ONBOARD-006`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `work/m2-m1-003-android-protected-credentials`
- **Base/main SHA:** `f32b099edf18af52d4eaf80b8de964ec5d359554`
- **Verified base CI:** `33682818812` — success
- **Status:** active; implementation not yet claimed

## Objective

Implement the first real Android-native client-core artifact as a bounded security library with no UI and no provider access. It must accept the opaque MIRA enrollment credential produced by the already-implemented client-session trust seam, encrypt it with an AES-GCM key held by Android Keystore, bind ciphertext to the exact `client_id`, persist only versioned ciphertext in app-private no-backup storage, and support exact local load/delete behavior.

AndroidX `EncryptedSharedPreferences` / `MasterKey` are intentionally not used because current Android API documentation deprecates that crypto layer and directs applications to Android Keystore primitives instead. Device/hardware-backed execution is not claimed merely because the source compiles.

Adding the first non-Python production source also exposes a required repository-integrity dependency: `DEV-006` code ownership currently verifies only Python production artifacts. This packet may extend that existing gate only as far as necessary to own and directly verify the Android Java source; weakening or bypassing the gate is prohibited.

## Feature alignment

### User-visible behavior enabled downstream

- An enrolled Android client can eventually persist its MIRA client credential without storing it in plaintext or embedding provider/database credentials.
- Removing local enrollment material can wipe the client credential without mutating canonical user data or provider resources.
- Android transport can later load the exact enrolled credential from this vault and authenticate through the same shared API/session boundary.

### Must preserve

- Android remains a client adapter over `API-001`, never a provider/database/source authority.
- Only the MIRA opaque client credential is stored; no Google OAuth token, Sheet/project ID, database credential, source credential, or private provider metadata is introduced.
- Protected storage uses Android Keystore directly and app-private no-backup storage; the implementation must not silently fall back to plaintext.
- Ciphertext is authenticated and bound to `client_id`; corruption, wrong-client material, missing key, or malformed format fails closed.
- Revocation remains server truth from `ClientSessionRegistry`; local deletion does not claim server revocation.
- The verified queued-writer boundary remains unchanged.
- No Google provider proof resource or legacy MIRA production data is accessed.

### Explicitly deferred

- Server/network enrollment transport and MIRA Connections UI.
- Android offline command queue and durable replay state.
- Reconnect/cursor synchronization.
- Bounded Android reads and queued command submission.
- Conflict/readback presentation.
- Native notifications/TTS, camera/barcode/QR/NFC/BLE capture.
- Release signing, Gradle-wrapper/release reproducibility hardening, and representative-device Android Keystore evidence.

## Acceptance criteria

1. A minimal Android client-core library builds in repository CI without introducing an application UI or provider dependency.
2. Production storage uses an AES-256 GCM key generated/loaded through the `AndroidKeyStore` provider; no deprecated `EncryptedSharedPreferences`/`MasterKey` dependency is used.
3. The opaque enrollment credential is encrypted before persistence; persisted material contains a versioned IV/ciphertext envelope only and is stored under `Context.getNoBackupFilesDir()`.
4. AES-GCM associated data binds protected material to the exact validated `client_id`; wrong-client substitution or ciphertext tampering fails closed.
5. The credential-store API accepts mutable enrollment credential bytes and clears that caller-provided buffer after the store attempt so this layer does not unnecessarily retain a second plaintext copy.
6. Local load returns the exact credential bytes only when ciphertext and Keystore key are valid. Missing material, malformed envelope, missing/invalid key, or authentication failure maps to an explicit fail-closed credential error.
7. Local delete removes both ciphertext and the Android Keystore entry idempotently. It does not claim or perform server-side revocation.
8. JVM tests with an injected AES-GCM test cipher/blob store prove roundtrip, plaintext non-retention in persisted bytes, tamper rejection, client binding, replacement, input-buffer clearing, and deletion behavior. Android production classes compile against the Android SDK; representative-device runtime proof remains explicitly unclaimed.
9. `DEV-006` code ownership is extended rather than bypassed so the Android production source is owned by `CLIENT-ANDROID-001` / `ANDROID-CLIENT-CORE-001` and directly tied to its Java test source.
10. Existing Python, Apps Script, feature/lifecycle/alignment, distribution, and code-ownership gates remain green. Android unit/build verification is added to CI.
11. No Google provider resource, Apps Script project, disposable proof Sheet, provider authorization flow, or legacy MIRA production state is touched.
12. Branch is pushed, exact PR head is remotely verified, CI succeeds on that exact head, bounded changed-file scope is verified, merge succeeds, remote `main` is read back, and post-merge CI succeeds before this packet is called complete.

## Completed evidence

- Remote `main` read back at `f32b099edf18af52d4eaf80b8de964ec5d359554`.
- Exact base CI run `33682818812` is complete/success with every existing repository gate green.
- Canonical FEATURES/BACKLOG/ROADMAP/PRODUCT_INVARIANTS review is complete and direction is `ALIGNED`.
- Current Android documentation was checked before implementation: deprecated AndroidX security-crypto wrappers are not selected for this new code; direct Android Keystore primitives are the intended storage-key boundary.
- No provider/browser action is required for this packet.

## Exact next action / resume point

1. Add the minimal Android library/security source and JVM tests.
2. Extend the existing code-ownership validator only enough to cover Java production roots with direct Java test evidence, and add regression tests for that gate.
3. Add deterministic Android compile/unit-test execution to CI using a pinned compatible JDK/Gradle/AGP toolchain.
4. Run/inspect exact-head CI and fix only defects required by this packet.
5. Record session-end alignment/evidence, open/verify/merge one bounded PR, then verify remote `main` and post-merge CI.
6. Do not begin offline queue/reconnect work until this packet is durably closed.

## Recovery protocol

Read this file first, verify remote branch/head and `main`, then continue from the first incomplete acceptance criterion. Do not rerun `M2-M1-001` or `M2-M1-002`, do not touch Google proof resources, and do not infer completion from code existence without exact CI/readback evidence.
