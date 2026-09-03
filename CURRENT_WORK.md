# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and exact recovery state.

## Product direction

Default Personal MIRA remains stock ChatGPT + Google Workspace with no external infrastructure prerequisite. Android extends the same canonical MIRA semantics and must never become a second provider/database/source authority or bypass the verified serialized shared command boundary.

Ordinary users must not be exposed to developer/provider mechanics merely because Android owns more UI. Provider Connections UI, provider consent, network transport, actual canonical read/write and representative-device proof remain later packets.

`M2-M1-001` queued-writer boundary, `M2-M1-002` enrollment/session trust, and `M2-M1-003` OS-protected Android credential storage are complete and must not be rerun.

## Session-start alignment verification — 2026-09-02 M2-M1-004

### `FEATURES.md`

- `CLIENT-ANDROID-001` requires the native client to use `API-001`, keep credentials protected, remain replay-safe offline and never become canonical/provider authority.
- `API-001` owns commands, queries, synchronization and verified mutation readback. Android local state may stage exact API intent or cache verified readback but cannot reinterpret canonical truth.
- `RECOVERY-002` requires local corruption/key loss to fail closed without silently discarding unsynced work or mutating canonical state.

### `BACKLOG.md`

- `ANDROID-CLIENT-CORE-001` remains the unfinished prerequisite before `ANDROID-SYNC`.
- Its remaining scope includes transport-authenticated bounded reads/commands, reconnect/cursor synchronization and server conflict/readback handling.
- The dependency-correct slice for this packet was local durable replay/cache/cursor state only.

### `ROADMAP.md`

- M2-M1 step 2, scoped/revocable identity plus OS-protected credentials, was completed by M2-M1-002/003 at their stated evidence ceilings.
- M2-M1 step 3 is replay-safe offline queue plus reconnect/cursor synchronization.
- M2-M1-004 implements the durable local prerequisite for step 3 but does not claim reconnect synchronization because no Android transport exists yet.

### `PRODUCT_INVARIANTS.md`

- Android reuses provider-neutral MIRA service/connection semantics and may not invent a second provider activation or authority model.
- Provider OAuth material, Google resource identifiers and developer setup material do not belong in Android offline state.

### Existing API contract check

`mira/api_core.py` was re-read before implementation. Android `CommandIntent` preserves the current transport-independent `CommandEnvelope` semantics required for exact future replay: `command_id`, `subject_id`, `data_class`, `action`, `api_major`, `schema_version`, `resource_id`, opaque serialized payload bytes, `idempotency_key`, optional `expected_revision`, and append-event-only `event_id` / `event_type`.

### Direction result

**ALIGNED.** The bounded slice was a durable encrypted local state machine for exact API command intents, acknowledgement replay suppression, monotonic cached canonical snapshots and opaque cursor compare-and-set state, with no network/provider/canonical authority access.

## Active packet

### `M2-M1-004` — Android client core, replay-safe local offline state

- **Primary work:** `ANDROID-CLIENT-CORE-001`
- **Primary features:** `CLIENT-ANDROID-001`, `API-001`
- **Related invariants/features:** `RECOVERY-002`, `AUTH-001`, `STORE-001`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Implementation branch:** `work/m2-m1-004-android-offline-state`
- **Base/main SHA:** `8cdd8abc5a5db3d022a9bfd9081d8c93830f99b2`
- **Verified base CI:** `33685113659` — success
- **Implementation head:** `00192de7ea6730aab88747a1fdcdbe619bb736a3`
- **Implementation-head CI:** `33698665125` — success
- **Evidence/merge-candidate head:** `090b148f393b281716315f4bd9c300b030e53828`
- **Evidence-head CI:** `33698847886` — success
- **PR:** #99
- **Merge/main SHA:** `5f0de376b001721d79115a42b02b72b8c274fdd4`
- **Post-merge CI:** `33698946968` — success
- **Status:** implementation merged and post-merge verified; this final documentation-only closeout head must pass CI before the packet is called durably closed

## Objective result

**IMPLEMENTED, TEST-VERIFIED, REPOSITORY-INTEGRATED AND MERGED FOR THIS BOUNDED SLICE.** `OfflineSyncStateStore` provides the durable local primitive required before Android reconnect transport can be implemented safely. It stores no provider authority and performs no network or canonical mutation.

The encrypted local state contains only:

1. exact provider-neutral `API-001` command intents with stable local FIFO sequence;
2. durable acknowledgement tombstones that suppress already-read-back command re-enqueue after restart;
3. nonauthoritative canonical snapshots keyed by `(data_class, resource_id)` with monotonic revision enforcement; and
4. one opaque synchronization cursor updated through compare-and-set semantics.

Production persistence uses a separate Android Keystore AES-256-GCM key, exact `client_id` authenticated associated data, Android `AtomicFile`, and `Context.getNoBackupFilesDir()`. There is no plaintext fallback. Missing/corrupt key material or tampered/malformed stored state fails closed rather than silently resetting unsynced state.

This packet does **not** complete `ANDROID-CLIENT-CORE-001` or M2-M1 step 3. HTTP/API transport, server cursor acquisition, reconnect execution, canonical reads, command submission, verified server acknowledgement, and conflict/readback presentation remain unfinished.

## Completed implementation evidence

### Replay-safe command state

- `OfflineSyncStateStore.CommandIntent` preserves the exact current API command-envelope fields needed for later replay.
- Only current command actions `upsert` and `append_event` are accepted with the same event-field shape constraints as `API-001`.
- Payload bytes are preserved exactly; this layer does not become a second JSON/wire-schema implementation.
- New commands receive monotonically increasing local sequence numbers.
- Exact duplicate enqueue is idempotent.
- Same `command_id` with different complete command material fails closed.
- Exact acknowledgement moves a pending command to a durable tombstone containing sequence, command ID, idempotency key and complete-command SHA-256 fingerprint.
- Exact repeated acknowledgement is idempotent; unknown or conflicting acknowledgement fails closed.
- A command matching a durable tombstone returns `ALREADY_ACKNOWLEDGED` after restart rather than being queued again.

### Canonical cache and cursor foundations

- Cached snapshot identity is the full `(data_class, resource_id)` pair, allowing different data classes to reuse the same resource ID without collision.
- Snapshot revisions must be positive and may only advance.
- Exact same revision/payload is idempotent.
- Revision regression and same-revision/different-payload fork fail closed.
- Cursor values are opaque; no lexical, numeric or provider ordering is invented.
- Cursor replacement uses compare-and-set so a stale reconnect flow cannot overwrite a newer local cursor. An already-applied exact next cursor is idempotent.

### Protected bounded persistence

- Offline state uses a distinct Android Keystore key namespace from credential storage.
- Production encryption is AES-256-GCM through `AndroidKeyStore` with randomized encryption required and exact-client AAD binding.
- Versioned encrypted state is stored under no-backup app-private storage using `AtomicFile`.
- Raw client ID is not used as a filename; stable SHA-256-derived local identifiers are used.
- Existing malformed/truncated/tampered state or missing/invalid key fails closed and leaves the blob in place.
- Decrypted plaintext state bytes are zeroed after decode.
- Explicit idempotent `discardLocalState()` removes only the local blob/key and never claims server revocation/provider cleanup/canonical mutation.
- Bounds are explicit: 128 pending commands, 512 acknowledgement tombstones, 128 snapshots, 32 KiB command payload, 128 KiB snapshot payload, and 8 MiB encoded plaintext state. Capacity exhaustion fails explicitly; no pending command or tombstone is silently dropped.

### Deterministic verification

`OfflineSyncStateStoreTest` uses injected JVM AES-GCM and in-memory blob dependencies to prove portable storage/replay semantics without pretending a desktop runner proves Android Keystore execution.

Tests cover restart persistence, exact API field/payload preservation, FIFO sequence, plaintext non-retention in persisted bytes, duplicate pending suppression, durable acknowledged replay suppression, conflicting command/ack rejection, `(data_class, resource_id)` cache identity, cache revision/fork rules, cursor compare-and-set, tamper rejection, missing-key failure, wrong-client AAD rejection even with deliberately copied test AES key, explicit local discard, capacity exhaustion without loss, and current API action/event-shape validation.

### DEV-006 ownership

- `project/android_code_ownership.json` now owns `OfflineSyncStateStore.java` as component `android-client-offline-sync-state`.
- Ownership ties the source to `CLIENT-ANDROID-001`, `API-001`, `RECOVERY-002`, `ANDROID-CLIENT-CORE-001` and direct Java verification in `OfflineSyncStateStoreTest.java`.
- Existing credential-security ownership and validators were not weakened.

## Merge and CI evidence

- PR #99 changed exactly four intended files throughout the verified merge candidate:
  - `CURRENT_WORK.md`
  - `android-client/core/src/main/java/com/mira/client/core/sync/OfflineSyncStateStore.java`
  - `android-client/core/src/test/java/com/mira/client/core/sync/OfflineSyncStateStoreTest.java`
  - `project/android_code_ownership.json`
- Implementation-head CI `33698665125` succeeded on exact head `00192de7ea6730aab88747a1fdcdbe619bb736a3`.
- Evidence-head CI `33698847886` succeeded on exact merge candidate `090b148f393b281716315f4bd9c300b030e53828`.
- PR #99 was re-read as mergeable with the same four-file scope and exact evidence head before merge.
- PR #99 merged successfully using expected head `090b148f393b281716315f4bd9c300b030e53828`.
- Remote `main` independently read back at merge SHA `5f0de376b001721d79115a42b02b72b8c274fdd4`.
- Post-merge CI `33698946968` succeeded on that exact merge SHA. Compile, feature registry, lifecycle ledger, Personal starter distribution, work-session alignment, Python + Android ownership, Android client-core tests/production compilation, Python tests and Workspace Apps Script tests all passed.
- No Google provider resource, Apps Script project, disposable proof Sheet, provider authorization flow, network endpoint or legacy MIRA production state was accessed or modified.

## Acceptance criteria result

1. Production Android offline-state store with no UI/network/provider/canonical mutation — **satisfied**.
2. AES-256-GCM Android Keystore + exact-client AAD + no-backup atomic storage + no plaintext fallback — **satisfied in source/build evidence; device runtime not claimed**.
3. Exact provider-neutral API command staging, stable FIFO, duplicate idempotency and conflicting command-ID rejection — **satisfied**.
4. Exact acknowledgement identity, durable tombstone and restart replay suppression — **satisfied**.
5. Explicit pending/tombstone/payload/state bounds with no silent prune/drop — **satisfied**.
6. `(data_class, resource_id)` cache identity with monotonic revision/fork rules — **satisfied**.
7. Opaque cursor compare-and-set and stale-writer rejection — **satisfied**.
8. Versioned bounded local state; missing state empty; malformed/tampered/missing-key state fails closed without silent reset — **satisfied at deterministic/source evidence ceiling**.
9. Explicit idempotent local discard distinct from server/provider/canonical state — **satisfied**.
10. Deterministic JVM restart/FIFO/replay/cache/cursor/encryption/tamper/wrong-client/discard tests — **satisfied**.
11. Android production source compiles against pinned toolchain; representative-device evidence remains unclaimed — **satisfied at this evidence ceiling**.
12. Android DEV-006 ownership extended and existing gates remain green — **satisfied**.
13. No provider/network/legacy production resource touched — **satisfied**.
14. Branch/PR exact-head scope + CI, merge, remote main readback and post-merge CI — **satisfied**.

## Evidence ceiling

- **Implemented:** encrypted Android local queue/tombstone/cache/cursor state and Android ownership metadata.
- **Test verified:** deterministic JVM AES-GCM/restart/replay/cache/cursor semantics plus Android production-source compilation.
- **Integration verified:** repository CI integrates the new source/tests into the existing Android/Python/Apps Script/governance suite and post-merge main is green.
- **Not network/live/device verified:** physical Android Keystore execution, hardware-backed key availability, app process/reboot behavior, actual API authentication/HTTP transport, reconnect, server cursor acquisition, command submission, canonical readback, conflict handling, provider consent or Android mutation of MIRROR.

## Session-end alignment verification — 2026-09-02 M2-M1-004

### `FEATURES.md`

`CLIENT-ANDROID-001` remains partially implemented. M2-M1-004 satisfies only the protected local replay/cache/cursor prerequisite. `API-001` remains the service/canonical boundary. No feature should be promoted to complete.

### `BACKLOG.md`

`ANDROID-CLIENT-CORE-001` remains unfinished and must not be marked complete. The next dependency-correct bounded slice is Android transport/reconnect plumbing that authenticates with the protected client credential, obtains/advances server synchronization state and replays pending commands only through the shared API/serialized command boundary, persisting only verified readback into this local store. It must not absorb the full Android UI/conflict/canonical-read vertical.

### `ROADMAP.md`

M2-M1 ordering remains correct. M2-M1-004 provides the durable local half of step 3 but does not satisfy reconnect synchronization without transport/server evidence. Steps 4 through 7 remain untouched.

### `PRODUCT_INVARIANTS.md`

The implementation remains provider-neutral, stores no provider credentials/resource identifiers, exports no setup ceremony to ordinary users, and creates no second provider activation/authority model.

### Direction result

**ALIGNED.** M2-M1-004 is bounded, merged and post-merge verified at its stated evidence ceiling. No unrelated feature or provider work entered the packet.

## Exact next action / resume point

1. Require CI on this final documentation-only closeout head. If it succeeds and remote `main` still equals that head, M2-M1-004 is durably closed.
2. On the next explicit `continue`, read this file and remote `main` first, then open a new bounded packet for the next dependency-correct Android transport/reconnect slice under `ANDROID-CLIENT-CORE-001`.
3. Do not reinterpret M2-M1-004 as physical-device or live-network proof and do not rerun provider proof resources.

## Recovery protocol

Read this file first and verify remote `main` plus the final closeout-head CI. Treat M2-M1-001 through M2-M1-003 as closed and M2-M1-004 as closed only after this final closeout head is green. Never touch the historical Google proof resource or legacy MIRA production state merely to resume Android client-core work.
