# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and exact recovery state.

## Product direction

Default Personal MIRA remains stock ChatGPT + Google Workspace with no external infrastructure prerequisite. Android extends the same canonical MIRA semantics and must never become a second provider/database/source authority or bypass the verified serialized shared command boundary.

Ordinary users must not be exposed to developer/provider mechanics merely because Android owns more UI. Provider Connections UI, provider consent, network transport, actual canonical read/write and device proof remain later packets. This packet is local client-core state only.

`M2-M1-001` / `ANDROID-COMMAND-BOUNDARY-001`, `M2-M1-002` enrollment/session trust, and `M2-M1-003` OS-protected Android credential storage are complete and must not be rerun.

## Prior-packet recovery verification — 2026-09-02

- Authoritative remote `main` was read back at `8cdd8abc5a5db3d022a9bfd9081d8c93830f99b2`.
- Final M2-M1-003 closeout CI `33685113659` completed successfully on that exact main head.
- M2-M1-003 is therefore durably closed at its declared source/build/test/repository-integration evidence ceiling.

## Session-start alignment verification — 2026-09-02 M2-M1-004

### `FEATURES.md`

- `CLIENT-ANDROID-001` requires the Android native client to use `API-001`, keep protected client credentials, remain replay-safe offline, and never become canonical/provider authority.
- `API-001` owns bounded commands, queries, synchronization and verified mutation readback. Local Android state may stage or cache API material but cannot reinterpret server/provider truth.
- `RECOVERY-002` requires failure isolation. Local corruption/key loss must fail closed and must not silently discard unsynced commands or mutate canonical state.

### `BACKLOG.md`

- `ANDROID-CLIENT-CORE-001` remains the unfinished prerequisite before `ANDROID-SYNC`.
- Its remaining scope includes bounded reads, canonical commands, replay-safe offline queue, reconnect/cursor sync and server conflict/readback handling.
- The smallest next prerequisite was local durable queue/cache/cursor state. Network transport, canonical reads/writes and server conflict resolution remain separate.

### `ROADMAP.md`

- M2-M1 step 2, scoped/revocable client identity plus OS-protected credentials, is complete at source/test evidence through M2-M1-002/003.
- M2-M1 step 3 is replay-safe offline queue and reconnect/cursor synchronization.
- This packet implements only the local durable state machine needed by step 3. It does not claim reconnect synchronization because no transport exists yet.

### `PRODUCT_INVARIANTS.md`

- Android must reuse provider-neutral MIRA service/connection semantics and may not invent a second activation or provider-authority model.
- No provider OAuth token, Google resource identifier, developer setup material, or legacy production state belongs in the local offline-state store.

### Existing API contract check

Before implementation, `mira/api_core.py` was re-read. `CommandEnvelope` is already the canonical transport-independent command intent and includes `command_id`, `subject_id`, `data_class`, `action`, `api_major`, `schema_version`, `resource_id`, payload, `idempotency_key`, optional `expected_revision`, and append-event-only `event_id` / `event_type`. The Android offline queue preserves those semantics rather than inventing a lossy local command shape.

### Direction result

**ALIGNED.** The dependency-correct bounded slice is a durable, replay-safe Android client-core local state machine for exact provider-neutral API command intents, acknowledged-command replay suppression, monotonic cached canonical snapshots, and compare-and-set reconnect cursor state. It remains transport-agnostic and provider-neutral.

## Active packet

### `M2-M1-004` — Android client core, replay-safe local offline state

- **Primary work:** `ANDROID-CLIENT-CORE-001`
- **Primary features:** `CLIENT-ANDROID-001`, `API-001`
- **Related invariants/features:** `RECOVERY-002`, `AUTH-001`, `STORE-001`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `work/m2-m1-004-android-offline-state`
- **Base/main SHA:** `8cdd8abc5a5db3d022a9bfd9081d8c93830f99b2`
- **Verified base CI:** `33685113659` — success
- **Activation checkpoint:** `732b8ed0ff95baf4b181cdb9a36aae3c0b74ee5b`
- **API-envelope alignment checkpoint:** `dbc058877d59b900bfd3d152523a23cf17d9208e`
- **Verified implementation head before this evidence commit:** `00192de7ea6730aab88747a1fdcdbe619bb736a3`
- **Verified implementation-head CI:** `33698665125` — success
- **PR:** #99
- **Verified changed-file scope before this evidence commit:** exactly 4 intended files
- **Status:** bounded implementation/build/test slice satisfied; this evidence head, merge/main readback and post-merge verification remain

## Objective result

**IMPLEMENTED AND TEST-VERIFIED FOR THIS BOUNDED SLICE.** `OfflineSyncStateStore` now provides the local durable state primitive required before Android network reconnect work can be implemented safely. It stores no provider authority and performs no network or canonical mutation.

The state contains four things only:

1. exact provider-neutral `API-001` command intents with stable local FIFO sequence;
2. durable acknowledgement tombstones that suppress already-read-back command re-enqueue after restart;
3. nonauthoritative canonical snapshots keyed by the full canonical identity pair `(data_class, resource_id)` with monotonic revision enforcement; and
4. one opaque synchronization cursor updated only through compare-and-set semantics.

The complete local blob is versioned, encrypted and authenticated using a separate Android Keystore AES-256-GCM key bound to the exact `client_id`, and production persistence uses app-private no-backup storage through Android `AtomicFile`. There is no plaintext fallback and missing/corrupt key material does not silently reset unsynced state.

This packet does **not** complete `ANDROID-CLIENT-CORE-001` or M2-M1 step 3. Actual HTTP/API transport, server cursor acquisition, reconnect execution, canonical reads, command submission, verified server acknowledgement, and conflict/readback presentation remain unfinished.

## Completed implementation evidence

### Exact API command staging

- Added `android-client/core/src/main/java/com/mira/client/core/sync/OfflineSyncStateStore.java`.
- `CommandIntent` preserves the current `API-001` command-envelope semantics required for later replay: command ID, subject ID, data class, action, API major, schema version, resource ID, opaque serialized payload bytes, idempotency key, optional expected revision and append-event-only event ID/type.
- Only current API command actions `upsert` and `append_event` are accepted. Append-event fields are required only for `append_event` and rejected for `upsert`.
- This layer preserves payload bytes exactly; it does not duplicate or reinterpret the API JSON/wire schema.
- Each newly queued command receives a monotonically increasing positive local sequence.
- Exact re-enqueue of an already-pending command is idempotent.
- Reuse of the same `command_id` with different complete command material fails closed.

### Durable acknowledgement replay suppression

- `acknowledge(command_id, idempotency_key)` requires an exact pending identity.
- Successful acknowledgement moves the command from pending state to a durable tombstone containing sequence, command ID, idempotency key and SHA-256 fingerprint of the complete command intent.
- Exact repeated acknowledgement is idempotent.
- Unknown command acknowledgement or mismatched idempotency identity fails closed.
- A command matching an acknowledgement tombstone returns `ALREADY_ACKNOWLEDGED` on later enqueue, including after store re-instantiation.
- Tombstones are bounded and are not silently pruned because safe pruning depends on later verified server/cursor semantics.

### Canonical cache and cursor foundations

- Cached `ResourceSnapshot` identity is `(data_class, resource_id)`, not resource ID alone. This was corrected before CI after reviewing canonical identity semantics so different data classes may safely reuse the same resource ID.
- Snapshot revision must be positive.
- Higher revision replaces lower revision.
- Exact same revision + exact same payload is idempotent.
- Revision regression and same-revision/different-payload fork both fail closed.
- Snapshots are sorted deterministically by data class then resource ID.
- Synchronization cursor material is deliberately opaque.
- `compareAndSetCursor(expected, next)` does not invent lexical/numeric/provider ordering. A stale expected cursor is rejected. An already-applied exact next cursor is idempotent.

### Protected local persistence

- Production state uses a distinct Android Keystore key namespace from client credential storage.
- AES-256-GCM key is generated/loaded via `AndroidKeyStore`, randomized encryption required, no plaintext fallback.
- AES-GCM associated data binds the sealed state to exact `client_id`.
- Versioned encrypted state is stored under `Context.getNoBackupFilesDir()` in `mira-client-offline-state` through `AtomicFile`.
- Client ID is hashed for the local file/key identifier; raw client ID is not used as a filename.
- Missing blob initializes empty state.
- Existing malformed/truncated/tampered blob or missing/invalid key fails closed and leaves the encrypted blob in place rather than silently discarding unsynced state.
- Decrypted plaintext state bytes are zeroed after decode.
- Explicit `discardLocalState()` removes only local encrypted state and its matching key. It is intentionally destructive to unsynced local work and is never a silent recovery path. It does not revoke a session or mutate server/provider/canonical state.

### Bounded state

- Pending command count: 128 maximum.
- Acknowledgement tombstones: 512 maximum.
- Cached snapshots: 128 maximum.
- Command payload: 32 KiB maximum.
- Snapshot payload: 128 KiB maximum.
- Encoded local plaintext state: 8 MiB maximum.
- Capacity exhaustion fails explicitly. No pending command or tombstone is silently dropped or pruned.

### Deterministic JVM tests

Added `android-client/core/src/test/java/com/mira/client/core/sync/OfflineSyncStateStoreTest.java` using an injected JVM AES-GCM cipher and in-memory blob store. This proves portable state/replay semantics without pretending a desktop runner proves Android Keystore runtime behavior.

Tests cover:

- exact command-envelope field and payload preservation across restart;
- stable FIFO sequence across restart;
- plaintext command material absent from persisted encrypted bytes;
- exact duplicate pending suppression;
- durable acknowledgement/re-enqueue suppression across restart;
- conflicting duplicate command rejection;
- wrong/unknown acknowledgement rejection;
- cache identity separation for the same resource ID in different data classes;
- monotonic cache revisions, same-revision idempotency, fork rejection and regression rejection;
- opaque cursor compare-and-set behavior across restart and stale-writer rejection;
- ciphertext tamper failure without silent reset;
- missing-key failure without silent reset;
- copied ciphertext rejection under a different client ID even when the test deliberately copies the same AES key, proving exact-client AAD binding;
- explicit idempotent local discard and clean restart;
- pending capacity exhaustion without command loss; and
- current API action/event-shape validation.

### Repository integrity / DEV-006

- Extended `project/android_code_ownership.json` with component `android-client-offline-sync-state`.
- New production source is owned by `CLIENT-ANDROID-001`, `API-001`, `RECOVERY-002` and work item `ANDROID-CLIENT-CORE-001`.
- Direct verification points at `OfflineSyncStateStoreTest.java`.
- Existing credential-security ownership remains unchanged.
- No validator or gate was weakened.

### CI and scope evidence

- PR #99 opened from `work/m2-m1-004-android-offline-state` against exact base `8cdd8abc5a5db3d022a9bfd9081d8c93830f99b2`.
- Exact implementation head `00192de7ea6730aab88747a1fdcdbe619bb736a3` completed CI run `33698665125` successfully.
- The successful run includes compile, feature registry, lifecycle ledger, Personal starter distribution, work-session alignment, Python + Android ownership, Android client-core unit tests/production compilation, full Python tests, and Workspace Apps Script tests.
- PR #99 settled mergeable at that head.
- Changed-file scope before this evidence commit is exactly:
  - `CURRENT_WORK.md`
  - `android-client/core/src/main/java/com/mira/client/core/sync/OfflineSyncStateStore.java`
  - `android-client/core/src/test/java/com/mira/client/core/sync/OfflineSyncStateStoreTest.java`
  - `project/android_code_ownership.json`
- No Google provider resource, Apps Script project, proof Sheet, provider authorization flow, network endpoint or legacy MIRA production state was accessed or modified.

## Acceptance criteria result

1. Production Android offline-state store with no UI/network/provider/canonical mutation — **satisfied**.
2. AES-256-GCM Android Keystore protection + exact-client AAD + no-backup atomic storage + no plaintext fallback — **satisfied in source/build evidence; device runtime not claimed**.
3. Exact current provider-neutral API command-envelope staging, stable FIFO, duplicate idempotency, conflicting command-ID rejection — **satisfied**.
4. Exact acknowledgement identity, durable tombstone and restart replay suppression — **satisfied**.
5. Pending/tombstone/payload bounds with explicit capacity failure and no silent prune/drop — **satisfied**.
6. Cached canonical snapshot monotonic revision and fork/regression rules using `(data_class, resource_id)` identity — **satisfied**.
7. Opaque cursor compare-and-set with stale-writer rejection — **satisfied**.
8. Versioned bounded local state; missing state empty; malformed/tampered/missing-key state fails closed without silent reset — **satisfied by implementation/JVM tests, with Android Keystore runtime deferred**.
9. Explicit idempotent local discard distinct from server/provider/canonical state — **satisfied**.
10. Deterministic JVM restart/FIFO/replay/cache/cursor/encryption/tamper/wrong-client/discard tests — **satisfied**.
11. Android source compiles against existing pinned toolchain; representative-device evidence not claimed — **satisfied at this evidence ceiling**.
12. Android DEV-006 ownership extended and all existing gates green — **satisfied at exact implementation head**.
13. No provider/network/legacy production resource touched — **satisfied**.
14. Exact PR head/scope CI, merge, main readback and post-merge CI — **partially satisfied**: PR #99 exists, scope is bounded and implementation-head CI is green; this evidence-head CI, merge/main readback and post-merge CI remain.

## Evidence ceiling

- **Implemented:** encrypted Android local queue/tombstone/cache/cursor state and ownership metadata.
- **Test verified:** deterministic JVM AES-GCM/restart/replay/cache/cursor semantics plus Android production compilation.
- **Integration verified:** repository CI integrates the new source/tests into the existing Android/Python/Apps Script and governance suite at exact implementation head.
- **Not network/live/device verified:** Android Keystore execution on a physical device, hardware-backed key availability, process/reboot behavior on device, actual API authentication, HTTP transport, reconnect, server cursor acquisition, command submission, canonical readback, conflict handling, provider consent, or Android mutation of MIRROR.

## Session-end alignment verification — 2026-09-02 M2-M1-004

### `FEATURES.md`

`CLIENT-ANDROID-001` remains partially implemented. M2-M1-004 satisfies the local replay-safe persistence prerequisite only. `API-001` remains the service/canonical boundary; this local store does not execute or authorize API operations. No feature status should be promoted to complete.

### `BACKLOG.md`

`ANDROID-CLIENT-CORE-001` remains unfinished and must not be marked complete. After this packet closes, the next dependency-correct bounded slice is the transport/reconnect adapter that can authenticate with the protected credential, replay pending commands through the shared API/command boundary, acquire/advance server cursor state, and persist only verified readback through the local store. That future packet must itself remain bounded rather than absorbing canonical read UI/conflict presentation/the full Android vertical.

### `ROADMAP.md`

M2-M1 ordering remains correct. M2-M1-004 advances step 3 by implementing its durable local prerequisite but does not satisfy reconnect synchronization without actual transport/server evidence. Steps 4 through 7 remain untouched.

### `PRODUCT_INVARIANTS.md`

The implementation is provider-neutral, stores no provider credentials/resource IDs, exports no setup ceremony to ordinary users, and does not create a second provider activation or authority model. The future Android Connections surface remains a later user-facing requirement.

### Direction result

**ALIGNED.** The packet adds only the durable replay/cache/cursor primitive required before safe Android reconnect work, preserves API/Authority ownership of truth, protects local user state, and keeps transport/provider/device evidence structurally separate.

## Exact next action / resume point

1. Require CI on this evidence commit and fix only M2-M1-004 defects if any gate fails.
2. Re-read PR #99 head, mergeability and changed-file scope; require exact green evidence head and the same four-file bounded scope.
3. Merge PR #99 using the exact verified head.
4. Read back remote `main` and require post-merge CI on the exact merge head.
5. Persist final merge/main/post-merge evidence in `CURRENT_WORK.md` on main, retain the active-packet recovery heading, and require CI on that final closeout head before calling M2-M1-004 durably closed.
6. Do not begin Android transport/reconnect/canonical read-write work until M2-M1-004 is closed.

## Recovery protocol

Read this file first, verify PR #99 branch/head and remote `main`, then continue from the first incomplete acceptance criterion. Treat M2-M1-001 through M2-M1-003 as closed. Never touch the historical Google proof resource or legacy MIRA production state for this packet, and never claim synchronization merely because the local queue/cache/cursor primitive exists.
