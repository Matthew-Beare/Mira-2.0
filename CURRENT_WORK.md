# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and exact recovery state.

## Product direction

Default Personal MIRA remains stock ChatGPT + Google Workspace with no external infrastructure prerequisite. When Android or another software writer is enabled, direct independent Google Sheets mutation remains disabled; commands use the verified serialized shared command boundary.

Ordinary users must never open Apps Script, paste code, manage triggers, copy provider IDs, run a terminal, or understand queued-writer internals merely to enable Android/shared access. The shipped Android path eventually needs an obvious MIRA Connect/Enable action and a clearly identified, appropriately verified provider consent surface.

`M2-M1-001` / `ANDROID-COMMAND-BOUNDARY-001` is complete and must not be rerun. `M2-M1-002` completed the first bounded enrollment/session trust slice of `ANDROID-CLIENT-CORE-001`. This packet implements only the next OS-protected credential-storage slice.

## Session-start alignment verification — 2026-09-02 M2-M1-003

### `FEATURES.md`

- `CLIENT-ANDROID-001` requires the Android native client to use `API-001`, keep durable client credentials OS-protected, remain replay-safe offline, and never become a canonical/provider authority.
- `API-001` remains the authenticated policy/data boundary. The opaque client credential issued by the `ClientSessionRegistry` is client authentication material, not provider/database/source authority.
- `RECOVERY-002` requires protected-credential failure to fail closed without corrupting canonical state or weakening unrelated modules.

### `BACKLOG.md`

- `ANDROID-CLIENT-CORE-001` remains the uncompleted umbrella prerequisite before `ANDROID-SYNC`.
- Enrollment/session identity and revocation were implemented by `M2-M1-002`; OS-protected Android credential storage was the exact next missing prerequisite before offline queue/reconnect work.
- Offline queue, cursor synchronization, bounded network reads/commands, conflict presentation, provider Connections UI, notifications/TTS, capture, and release packaging remain outside this packet.

### `ROADMAP.md`

- M2-M1 step 2 explicitly requires scoped/revocable client identity plus OS-protected durable credentials before step 3 offline queue/reconnect synchronization.
- This packet therefore advances step 2 only. It does not jump into the Android shared-state vertical or native feature fan-out.

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
- **Verified implementation head before this evidence commit:** `9f506c955c638ab9b26ef6d8a3861e6a24ec2904`
- **Verified implementation-head CI:** `33684341143` — success
- **PR:** #98
- **Status:** bounded implementation/build/test slice satisfied; final evidence-head CI, merge, main readback, and post-merge CI remain

## Objective result

**IMPLEMENTED AND TEST-VERIFIED FOR THIS BOUNDED SLICE.** MIRA now has its first Android-native client-core library. `ProtectedCredentialStore` accepts only the opaque MIRA client credential, encrypts it with AES-256-GCM using a key generated/loaded from the `AndroidKeyStore` provider, binds the ciphertext to the exact `client_id` through authenticated associated data, and stores only a versioned IV/ciphertext envelope in app-private no-backup storage.

The storage API clears the caller-supplied mutable credential byte buffer after every store attempt, fails closed on malformed/tampered/wrong-client/missing-key material, and supports idempotent local removal of both ciphertext and the Keystore entry. Local deletion is explicitly not server revocation; server revocation remains authority in the `ClientSessionRegistry` introduced by M2-M1-002.

This packet does **not** complete the `ANDROID-CLIENT-CORE-001` umbrella. Offline replay queue, reconnect/cursor synchronization, Android network transport, bounded API reads/queued commands, conflict/readback presentation, Connections UI, release hardening, and representative-device evidence remain unfinished.

## Implementation evidence

### Android client security library

- Added a minimal `android-client` Gradle library tree with no application UI and no provider SDK dependency.
- Pinned Android build inputs for this slice: AGP 9.3.0, Gradle 9.5.0, JDK 17, compile SDK 36, minimum SDK 23.
- `ProtectedCredentialStore` uses `AES/GCM/NoPadding`, an AES-256 key created through `AndroidKeyStore`, randomized encryption, a 12-byte IV, and 128-bit GCM authentication tags.
- Keystore aliases and ciphertext filenames use SHA-256-derived client identifiers rather than raw client IDs.
- Persisted material is a bounded versioned binary envelope containing only format version, IV, ciphertext length, and ciphertext.
- Ciphertext is stored under `Context.getNoBackupFilesDir()` through Android `AtomicFile`; no plaintext fallback exists.
- Associated data is bound to the exact validated `client_id`, so copied ciphertext cannot authenticate under a different enrolled client identity.
- The credential byte array supplied to `storeAndClear` is wiped in a `finally` path even when validation/encryption/persistence fails.
- Local `delete` removes ciphertext and the matching Android Keystore entry idempotently while making no claim about server-side session revocation.

### Deterministic tests

`ProtectedCredentialStoreTest` uses an injected JVM AES-GCM cipher and in-memory blob store to verify the portable security/storage semantics without pretending a desktop JVM proves Android Keystore runtime behavior. Tests cover:

- exact store/load roundtrip;
- no plaintext credential subsequence in persisted bytes;
- caller-buffer clearing after success and storage failure;
- ciphertext tamper rejection;
- exact client-ID binding / wrong-client substitution rejection;
- replacement with fresh authenticated ciphertext and latest-secret readback;
- idempotent local deletion of ciphertext/key state;
- malformed envelope rejection; and
- invalid client-ID rejection with credential-buffer clearing.

### Repository integrity / DEV-006

The existing mature Python ownership gate remains intact. Because it governs Python AST/import semantics only, this packet adds a parallel Android production ownership manifest and validator rather than pretending Java is Python or leaving Android code outside governance.

- Android production root: `android-client/core/src/main/java`.
- Current Android production artifact is explicitly owned by `CLIENT-ANDROID-001`, `API-001`, `RECOVERY-002`, and `ANDROID-CLIENT-CORE-001`.
- The Android ownership gate rejects unowned Java production source, overlapping ownership, unknown feature/work IDs, missing test evidence, and missing direct Java verification references.
- CI's single Code ownership stage now requires both the existing Python ownership gate and the Android ownership gate.

### CI integration

CI now sets up JDK 17, Gradle 9.5.0, Android SDK platform 36/build-tools 36.0.0, validates both ownership inventories, and runs `:core:testDebugUnitTest` before the existing Python and Workspace Apps Script regression suites.

The first Android-enabled CI run `33684167115` failed only in the new governance script invocation because `python project/android_code_ownership.py check` put `project/` rather than repository root on Python's import path. Existing compile/feature/lifecycle/distribution/alignment/Python ownership gates were already green; Android build/tests were not reached. The gate was fixed by invoking the validator as the repository module `python -m project.android_code_ownership check`; the newly introduced deprecated `actions/setup-java@v4` reference was also corrected to v5. No product/security gate was weakened.

Exact replacement run `33684341143` succeeded on head `9f506c955c638ab9b26ef6d8a3861e6a24ec2904`. All of the following passed:

- Python/Node/JDK/Gradle/Android SDK setup;
- compile;
- feature registry;
- product lifecycle ledger;
- Personal starter distribution;
- work-session alignment;
- Python code ownership;
- Android code ownership;
- Android client-core unit tests / production Android compilation;
- full Python unit tests; and
- Workspace Apps Script tests.

## Acceptance criteria result

1. Minimal Android client-core library builds in repository CI with no application UI/provider dependency — **satisfied**.
2. AES-256-GCM key generated/loaded through `AndroidKeyStore`; no deprecated `EncryptedSharedPreferences`/`MasterKey` dependency — **satisfied in source/build evidence; device runtime not claimed**.
3. Credential encrypted before persistence; versioned IV/ciphertext envelope stored under no-backup app-private storage — **satisfied**.
4. Exact `client_id` AAD binding; wrong-client/tamper behavior fails closed — **satisfied by deterministic tests**.
5. Mutable enrollment credential input cleared after every store attempt — **satisfied by implementation/tests**.
6. Exact credential load only for valid material; malformed/missing/authentication failures explicit and fail closed — **satisfied by implementation/tests, with actual Android Keystore runtime deferred**.
7. Local ciphertext + Keystore-key deletion idempotent and distinct from server revocation — **satisfied by contract/tests**.
8. JVM crypto/storage tests + Android SDK compilation; representative-device runtime proof explicitly unclaimed — **satisfied at this evidence ceiling**.
9. DEV-006 ownership extended to Android rather than bypassed — **satisfied**.
10. Existing repository gates remain green and Android build/test gate added — **satisfied at exact implementation head**.
11. No Google provider proof/resource/authorization or legacy production state touched — **satisfied**.
12. Branch/PR exact-head CI, bounded scope, merge/main/post-merge verification — **partially satisfied**: PR #98 exists, changed-file scope is exactly the intended 13 files, and implementation-head CI is green; final evidence-head CI, merge/main readback, and post-merge CI remain.

## Evidence ceiling

- **Implemented:** Android credential-store source, Android library build surface, Java ownership governance, CI Android build/test integration.
- **Test verified:** deterministic JVM AES-GCM/storage behavior plus Android production-source compilation at exact PR head.
- **Integration verified:** repository CI integrates Android build/test and both ownership gates alongside the existing suite.
- **Not live/device verified:** physical Android Keystore execution, hardware-backed key availability, app installation, process/reboot behavior, biometric/user-auth policy, actual network enrollment, actual client authentication over transport, provider consent, or canonical Android read/write.

## Session-end alignment verification — 2026-09-02 M2-M1-003

### `FEATURES.md`

`CLIENT-ANDROID-001` remains partially implemented. This packet satisfies only its protected-client-credential prerequisite. `API-001` remains the service boundary and Android remains nonauthoritative. No semantic feature-status edit is warranted yet because offline synchronization, transport, and shared-state client behavior remain missing.

### `BACKLOG.md`

`ANDROID-CLIENT-CORE-001` remains the active umbrella work item; it must not be marked complete. The next dependency-correct bounded slice after this packet closes is replay-safe offline command/cache state plus reconnect cursor foundations, before the full Android/shared-state vertical. No BACKLOG lifecycle edit is warranted by this sub-slice alone.

### `ROADMAP.md`

M2-M1 ordering remains correct. M2-M1-002 and this packet jointly advance step 2 (scoped/revocable identity + OS-protected credentials) without skipping into step 3 or `ANDROID-SYNC`. No ROADMAP wording change is required.

### `PRODUCT_INVARIANTS.md`

The implementation stores only MIRA client authentication material and introduces no Google/provider credentials, IDs, authorization ceremony, or Android-specific activation model. The ordinary-user Connect/Enable and appropriately verified consent requirement remains a later release requirement, not falsely satisfied here.

### Direction result

**ALIGNED.** This packet preserves the verified shared-writer/API boundary, adds only the Android credential primitive required by the roadmap, keeps evidence claims below representative-device level, and leaves offline synchronization/transport structurally separate for the next packet.

## Exact next action / resume point

1. Require exact-head CI on this evidence commit; fix only M2-M1-003 defects if any gate fails.
2. Re-read PR #98 metadata and changed-file scope; require it to remain exactly the intended Android credential/build/governance/CI files plus `CURRENT_WORK.md` and be mergeable at the exact green head.
3. Merge PR #98 using that exact verified head.
4. Read back remote `main` and verify post-merge CI on the exact merge head.
5. Persist the final merge/main/post-merge CI evidence in `CURRENT_WORK.md` on main while retaining the required `## Active packet` heading, then require CI on that final closeout head before calling M2-M1-003 complete.
6. Do not begin the offline queue/reconnect slice until this packet is durably closed.

## Recovery protocol

Read this file first, then verify PR #98 / branch / remote main. Do not rerun M2-M1-001 or M2-M1-002, do not touch Google provider proof resources, and do not infer representative-device evidence from CI. Continue only the bounded M2-M1-003 closeout until its final main/readback/CI checkpoint is green.
