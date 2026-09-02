# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and exact recovery state.

## Product direction

Default Personal MIRA remains stock ChatGPT + Google Workspace with no external infrastructure prerequisite. When Android or another software writer is enabled, direct independent Google Sheets mutation remains disabled; commands use the verified serialized shared command boundary.

Ordinary users must never open Apps Script, paste code, manage triggers, copy provider IDs, run a terminal, or understand queued-writer internals merely to enable Android/shared access. The shipped Android path eventually needs an obvious MIRA Connect/Enable action and a clearly identified, appropriately verified provider consent surface.

`M2-M1-001` / `ANDROID-COMMAND-BOUNDARY-001` is complete and must not be rerun. `M2-M1-002` completed the enrollment/session trust slice of `ANDROID-CLIENT-CORE-001`. `M2-M1-003` completes only the next OS-protected Android credential-storage slice; the umbrella Android client core remains unfinished.

## Session-start alignment verification — 2026-09-02 M2-M1-003

### `FEATURES.md`

- `CLIENT-ANDROID-001` requires the Android native client to use `API-001`, keep durable client credentials OS-protected, remain replay-safe offline, and never become a canonical/provider authority.
- `API-001` remains the authenticated policy/data boundary. The opaque client credential issued by the `ClientSessionRegistry` is client authentication material, not provider/database/source authority.
- `RECOVERY-002` requires protected-credential failure to fail closed without corrupting canonical state or weakening unrelated modules.

### `BACKLOG.md`

- `ANDROID-CLIENT-CORE-001` remains the uncompleted umbrella prerequisite before `ANDROID-SYNC`.
- Enrollment/session identity and revocation were implemented by `M2-M1-002`; this packet adds OS-protected Android credential storage.
- Offline queue, cursor synchronization, bounded network reads/commands, conflict presentation, provider Connections UI, notifications/TTS, capture, and release packaging remain outside this packet.

### `ROADMAP.md`

- M2-M1 step 2 requires scoped/revocable client identity plus OS-protected durable credentials before step 3 offline queue/reconnect synchronization.
- This packet advances step 2 only and does not jump into the Android shared-state vertical or native feature fan-out.

### `PRODUCT_INVARIANTS.md`

- Android must reuse provider-neutral MIRA connection/service semantics and must not export developer/provider setup ceremony to ordinary users.
- Provider credentials and Google resource identifiers do not belong in Android protected-client storage. This packet stores only the opaque MIRA client credential needed to authenticate the enrolled same-user client.

### Direction result

**ALIGNED.** The smallest dependency-correct slice was a buildable Android client-core security module that accepts the opaque enrollment credential, protects its encryption key with Android Keystore, stores only authenticated ciphertext in app-private no-backup storage, fails closed on corruption/key loss, and supports local deletion. Offline sync and network transport remain later packets.

## Active packet

### `M2-M1-003` — Android client core, OS-protected credential storage

- **Primary work:** `ANDROID-CLIENT-CORE-001`
- **Primary features:** `CLIENT-ANDROID-001`, `API-001`
- **Related invariants/features:** `RECOVERY-002`, `AUTH-001`, `STORE-001`, `PROVIDER-002`, `ONBOARD-006`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Checkpoint branch:** `main`
- **Packet base/main SHA:** `f32b099edf18af52d4eaf80b8de964ec5d359554`
- **Verified implementation head:** `9f506c955c638ab9b26ef6d8a3861e6a24ec2904`
- **Verified evidence head:** `4b4bfc43a2bac307eeb097258b511ed0221ea964`
- **PR:** #98 — merged
- **Merge/main SHA before this closeout commit:** `6c8e859191e9876885ee7152e7d13f47a560218d`
- **Verified post-merge CI:** `33684865556` — success
- **Status:** complete for this bounded source/build/test/integration evidence slice; this closeout commit still requires exact-head CI before the packet is called durably closed

## Objective result

**COMPLETE AT THE BOUNDED SOURCE/BUILD/TEST/REPOSITORY-INTEGRATION EVIDENCE CEILING.** MIRA now has its first Android-native client-core library. `ProtectedCredentialStore` accepts only the opaque MIRA client credential, encrypts it with AES-256-GCM using a key generated/loaded from the `AndroidKeyStore` provider, binds the ciphertext to the exact `client_id` through authenticated associated data, and stores only a versioned IV/ciphertext envelope in app-private no-backup storage.

The storage API clears the caller-supplied mutable credential byte buffer after every store attempt, fails closed on malformed/tampered/wrong-client/missing-key material, and supports idempotent local removal of both ciphertext and the Keystore entry. Local deletion is explicitly not server revocation; server revocation remains authority in the `ClientSessionRegistry` introduced by M2-M1-002.

This does **not** complete `ANDROID-CLIENT-CORE-001`. Offline replay queue, reconnect/cursor synchronization, Android network transport, bounded API reads/queued commands, conflict/readback presentation, Connections UI, release hardening, and representative-device evidence remain unfinished.

## Completed implementation evidence

### Android client security library

- Added a minimal `android-client` Gradle library tree with no application UI and no provider SDK dependency.
- Pinned build inputs for this slice: AGP 9.3.0, Gradle 9.5.0, JDK 17, compile SDK 36, minimum SDK 23.
- `ProtectedCredentialStore` uses `AES/GCM/NoPadding`, an AES-256 key created through `AndroidKeyStore`, randomized encryption, a 12-byte IV, and 128-bit GCM authentication tags.
- Keystore aliases and ciphertext filenames use SHA-256-derived client identifiers rather than raw client IDs.
- Persisted material is a bounded versioned binary envelope containing only format version, IV, ciphertext length, and ciphertext.
- Ciphertext is stored under `Context.getNoBackupFilesDir()` through Android `AtomicFile`; no plaintext fallback exists.
- Associated data binds protected material to the exact validated `client_id`.
- `storeAndClear` wipes the caller-provided credential byte array in a `finally` path even when validation/encryption/persistence fails.
- Local `delete` removes ciphertext and the matching Android Keystore entry idempotently while making no claim about server-side session revocation.

### Deterministic test evidence

`ProtectedCredentialStoreTest` uses an injected JVM AES-GCM cipher and in-memory blob store to test portable security/storage semantics without pretending a desktop JVM proves Android Keystore runtime behavior. Tests cover:

- exact store/load roundtrip;
- absence of plaintext credential bytes in persisted material;
- caller-buffer clearing after success and storage failure;
- ciphertext tamper rejection;
- exact client-ID binding / wrong-client substitution rejection;
- replacement with fresh authenticated ciphertext and latest-secret readback;
- idempotent local deletion of ciphertext/key state;
- malformed envelope rejection; and
- invalid client-ID rejection with credential-buffer clearing.

### Repository integrity / DEV-006

- The mature Python ownership gate remains intact.
- Added a parallel Android production ownership manifest/validator for `android-client/core/src/main/java` instead of pretending Java is Python or leaving Android source unowned.
- The Android ownership gate rejects unowned Java production source, overlapping ownership, unknown feature/work IDs, missing test evidence, and missing direct Java verification references.
- CI's Code ownership stage requires both Python and Android ownership checks.

### CI evidence

- First Android-enabled run `33684167115` failed only because the new Android ownership script was invoked as a path, causing Python import-root resolution to exclude repository `mira`; Android build/tests were not reached.
- The invocation was corrected to `python -m project.android_code_ownership check`. The newly added deprecated `actions/setup-java@v4` reference was also corrected to v5. No product/security gate was weakened.
- Exact implementation-head CI `33684341143` succeeded on `9f506c955c638ab9b26ef6d8a3861e6a24ec2904`.
- Final PR evidence-head CI `33684646826` succeeded on `4b4bfc43a2bac307eeb097258b511ed0221ea964`.
- PR #98 remained mergeable and changed exactly 13 intended files before merge.
- PR #98 merged to main as `6c8e859191e9876885ee7152e7d13f47a560218d`.
- Remote `main` independently read back at that exact merge SHA.
- Post-merge CI `33684865556` succeeded on that exact merge SHA with Android build/unit tests, both ownership gates, full Python tests, and Workspace Apps Script tests green.
- No Google provider resource, Apps Script project, disposable proof Sheet, authorization flow, or legacy MIRA production state was accessed or modified.

## Acceptance criteria result

1. Minimal Android client-core library builds in repository CI with no application UI/provider dependency — **satisfied**.
2. AES-256-GCM key generated/loaded through `AndroidKeyStore`; no deprecated `EncryptedSharedPreferences`/`MasterKey` dependency — **satisfied in source/build evidence; device runtime not claimed**.
3. Credential encrypted before persistence; versioned IV/ciphertext envelope stored under no-backup app-private storage — **satisfied**.
4. Exact `client_id` AAD binding; wrong-client/tamper behavior fails closed — **satisfied by deterministic tests**.
5. Mutable enrollment credential input cleared after every store attempt — **satisfied by implementation/tests**.
6. Exact credential load only for valid material; malformed/missing/authentication failures explicit and fail closed — **satisfied at source/JVM-test evidence; actual Android Keystore runtime remains deferred**.
7. Local ciphertext + Keystore-key deletion idempotent and distinct from server revocation — **satisfied**.
8. JVM crypto/storage tests + Android SDK compilation; representative-device runtime proof explicitly unclaimed — **satisfied at this evidence ceiling**.
9. DEV-006 ownership extended to Android rather than bypassed — **satisfied**.
10. Existing repository gates remain green and Android build/test gate added — **satisfied**.
11. No Google provider proof/resource/authorization or legacy production state touched — **satisfied**.
12. Branch/PR exact-head CI, bounded scope, merge/main readback/post-merge CI — **satisfied through merge head `6c8e859191e9876885ee7152e7d13f47a560218d`; final closeout-head CI remains the only recovery-checkpoint gate**.

## Evidence ceiling

- **Implemented:** Android credential-store source, Android library build surface, Java ownership governance, CI Android build/test integration.
- **Test verified:** deterministic JVM AES-GCM/storage behavior plus Android production-source compilation.
- **Integration verified:** repository CI integrates Android build/test and both ownership gates alongside the existing suite; merge/post-merge exact-head verification succeeded.
- **Not live/device verified:** physical Android Keystore execution, hardware-backed key availability, app installation, process/reboot behavior, biometric/user-auth policy, actual network enrollment, actual client authentication over transport, provider consent, or canonical Android read/write.

## Session-end alignment verification — 2026-09-02 M2-M1-003

### `FEATURES.md`

`CLIENT-ANDROID-001` remains partially implemented. This packet satisfies only its protected-client-credential prerequisite. `API-001` remains the service boundary and Android remains nonauthoritative. No semantic feature-status edit is warranted because offline synchronization, transport, and shared-state client behavior remain missing.

### `BACKLOG.md`

`ANDROID-CLIENT-CORE-001` remains the unfinished umbrella work item and must not be marked complete. The next dependency-correct bounded slice is replay-safe offline command/cache state plus reconnect cursor foundations before the full Android/shared-state vertical. No BACKLOG lifecycle edit is warranted by this sub-slice alone.

### `ROADMAP.md`

M2-M1 ordering remains correct. M2-M1-002 and M2-M1-003 jointly satisfy the source/test prerequisites for step 2 (scoped/revocable identity + OS-protected credentials) without skipping into step 3 or `ANDROID-SYNC`. No ROADMAP wording change is required.

### `PRODUCT_INVARIANTS.md`

The implementation stores only MIRA client authentication material and introduces no Google/provider credentials, IDs, authorization ceremony, or Android-specific activation model. The ordinary-user Connect/Enable and appropriately verified consent requirement remains a later release requirement and is not falsely satisfied here.

### Direction result

**ALIGNED.** The merged implementation preserves the verified shared-writer/API boundary, adds only the Android credential primitive required by the roadmap, keeps evidence claims below representative-device level, and leaves offline synchronization/transport structurally separate for the next packet.

## Exact next action / resume point

1. Require CI on this final main closeout commit and verify it succeeds on the exact pushed head.
2. Read back remote `main` at that exact closeout head.
3. Once both are verified, M2-M1-003 is durably closed. Do not rerun its Android credential-storage work.
4. In the next development packet, re-read Git first and open exactly one bounded continuation of `ANDROID-CLIENT-CORE-001` for replay-safe offline command/cache state and reconnect/cursor foundations. Do not attempt the entire remaining Android client core at once.
5. Provider Connections UI, actual transport, canonical Android read/write, native delivery, capture, release signing, and representative-device proof remain later evidence layers unless a newly discovered hard dependency requires otherwise.

## Recovery protocol

Read this file first and verify remote `main` plus its exact CI. If the final closeout-head CI is green, treat M2-M1-003 as complete and start no work from chat reconstruction. Do not rerun M2-M1-001, M2-M1-002, or M2-M1-003; do not touch the historical Google proof resource; choose the next bounded Android client-core slice from Git.
