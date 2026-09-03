# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and exact recovery state.

## Product direction

Default Personal MIRA remains stock ChatGPT + Google Workspace with no external infrastructure prerequisite. Android extends the same canonical MIRA semantics and must never become a second provider/database/source authority or bypass the verified serialized shared command boundary.

Ordinary users must not be exposed to developer/provider mechanics merely because Android owns more UI. Provider Connections UI, provider consent, transport, and actual canonical read/write remain later packets; this packet is local client-core state only.

`M2-M1-001` / `ANDROID-COMMAND-BOUNDARY-001`, `M2-M1-002` enrollment/session trust, and `M2-M1-003` OS-protected Android credential storage are complete and must not be rerun.

## Prior-packet recovery verification — 2026-09-02

- Authoritative remote `main` read back at `8cdd8abc5a5db3d022a9bfd9081d8c93830f99b2`.
- Final closeout CI `33685113659` is complete/success on that exact main head.
- Therefore `M2-M1-003` is durably closed at its declared source/build/test/repository-integration evidence ceiling.

## Session-start alignment verification — 2026-09-02 M2-M1-004

### `FEATURES.md`

- `CLIENT-ANDROID-001` requires the Android native client to use `API-001`, keep protected client credentials, remain replay-safe offline, and never become canonical/provider authority.
- `API-001` owns bounded commands, queries, synchronization and verified mutation readback. Local Android state may stage or cache API material but cannot reinterpret server/provider truth.
- `RECOVERY-002` requires failure isolation. Local corruption/key loss must fail closed and must not silently discard unsynced commands or mutate canonical state.

### `BACKLOG.md`

- `ANDROID-CLIENT-CORE-001` remains the unfinished prerequisite before `ANDROID-SYNC`.
- Its remaining scope includes bounded reads, canonical commands, replay-safe offline queue, reconnect/cursor sync and server conflict/readback handling.
- The smallest next prerequisite is local durable queue/cache/cursor state. Network transport, canonical reads/writes and server conflict resolution remain separate.

### `ROADMAP.md`

- M2-M1 step 2 (scoped/revocable client identity + OS-protected credentials) is complete at source/test evidence through M2-M1-002/003.
- M2-M1 step 3 is replay-safe offline queue and reconnect/cursor synchronization.
- This packet implements only the local durable state machine needed by step 3; it does not claim reconnect synchronization because no transport exists yet.

### `PRODUCT_INVARIANTS.md`

- Android must reuse provider-neutral MIRA service/connection semantics and may not invent a second activation or provider-authority model.
- No provider OAuth token, Google resource identifier, developer setup material, or legacy production state belongs in the local offline-state store.

### Existing API contract check

Before implementation, `mira/api_core.py` was re-read. `CommandEnvelope` is already the canonical transport-independent command intent and includes `command_id`, `subject_id`, `data_class`, `action`, `api_major`, `schema_version`, `resource_id`, payload, `idempotency_key`, optional `expected_revision`, and append-event-only `event_id` / `event_type`. The Android offline queue must preserve those semantics rather than invent a lossy local command shape.

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
- **Status:** active; API-envelope alignment checked before implementation

## Objective

Implement one Android client-core local state primitive with no UI, network, provider SDK or canonical authority access. The primitive must durably preserve exactly the information a later transport/reconnect engine needs to replay safely without creating a second truth source:

1. pending canonical `API-001` command intents in stable FIFO sequence;
2. bounded acknowledged-command tombstones so an already-read-back command is not re-enqueued after process restart;
3. cached canonical resource snapshots that may advance by revision but never regress or fork silently at the same revision; and
4. an opaque synchronization cursor updated by explicit compare-and-set so stale reconnect flows cannot overwrite newer local cursor state.

Production local state must live in app-private no-backup storage and be authenticated/encrypted with a separate Android Keystore AES-256-GCM key bound to the exact `client_id`. This prevents backup/restore duplication from becoming an accidental cross-device replay path and avoids storing queued/cached user data as plaintext. Key loss, malformed/tampered ciphertext, stale cursor writes, revision regression and conflicting duplicate command IDs must fail closed.

## Intended local contract

### Pending commands

A queued command mirrors the provider-neutral `API-001` command envelope fields needed for exact later replay: immutable `command_id`, `subject_id`, `data_class`, `action`, positive `api_major`, trimmed bounded `schema_version`, canonical `resource_id`, bounded serialized payload bytes, `idempotency_key`, optional non-negative `expected_revision`, and append-event-only `event_id` / `event_type`. The store assigns a monotonically increasing local sequence.

- `upsert` and `append_event` are the only accepted command actions because those are the current `API-001` command actions;
- append-event commands require event ID/type while upserts reject event fields;
- exact re-enqueue of the same complete command fingerprint is idempotent;
- same `command_id` with different command content is a local integrity conflict;
- pending listing is stable FIFO and bounded;
- acknowledgement requires the exact command/idempotency identity and moves the command to a durable tombstone;
- an acknowledged command cannot be silently re-enqueued after restart;
- tombstones are bounded and are not silently pruned in this packet because safe pruning depends on later verified server/cursor semantics.

The payload is stored as opaque serialized bytes by this layer. Parsing/encoding JSON or another wire representation belongs to the later transport/API adapter; the offline state layer must preserve bytes exactly rather than becoming a second schema implementation.

### Cached canonical snapshots

A snapshot carries canonical `resource_id`, server/canonical revision and bounded payload bytes.

- higher revision replaces lower revision;
- exact same revision + exact same bytes is idempotent;
- lower revision is rejected;
- same revision + different bytes is rejected as a fork/conflict;
- cached state is explicitly nonauthoritative and may only be populated later from verified API/server readback.

### Cursor

The synchronization cursor is opaque. This packet therefore does not invent ordering semantics for it. Cursor advancement uses compare-and-set (`expected current` -> `next`) so a stale reconnect path cannot overwrite state created by a newer path. Exact same current/next may be idempotent; mismatched expected state fails closed.

### Local-state discard

An explicit local discard operation may remove the encrypted blob and its Android Keystore key. It is destructive to unsynced local work and therefore must never be invoked silently. It does not mutate or revoke any server/provider/canonical state.

## Acceptance criteria

1. Add a production Android client-core offline-state store with no application UI, network client, provider dependency or direct canonical/provider mutation.
2. Production persistence uses an AES-256-GCM key generated/loaded through `AndroidKeyStore`; the state blob is authenticated/encrypted, bound to exact validated `client_id`, stored atomically under `Context.getNoBackupFilesDir()`, and has no plaintext fallback.
3. Pending commands preserve the exact current provider-neutral `API-001` command-envelope semantics required for later replay, use bounded validated fields and a stable local FIFO sequence. Exact duplicate enqueue is idempotent; same command ID with different fingerprint fails closed.
4. Acknowledging a pending command requires exact command/idempotency identity, persists an acknowledgement tombstone and prevents re-enqueue of that same command after store re-instantiation/restart. Unknown or conflicting acknowledgements fail closed.
5. Pending-command and acknowledgement-tombstone counts/payload sizes are bounded. Reaching a bound fails explicitly; no silent drop/prune of unsynced commands or tombstones occurs.
6. Cached snapshots advance monotonically by canonical revision. Revision regression and same-revision/different-payload forks fail closed; exact same revision/payload is idempotent.
7. Opaque cursor writes use compare-and-set semantics and reject stale expected cursors rather than inventing token ordering.
8. Entire local state is versioned and bounded. Missing state initializes empty; malformed/truncated/tampered ciphertext or missing/invalid Keystore key fails closed without silently resetting unsynced state.
9. Explicit local discard deletes the encrypted state and matching Keystore key idempotently and makes no claim about server revocation, canonical mutation, or provider cleanup.
10. Deterministic JVM tests with injected AES-GCM/blob dependencies prove restart persistence, FIFO ordering, duplicate suppression, conflicting duplicate rejection, durable acknowledgement replay suppression, API-envelope field preservation, cache revision rules, cursor compare-and-set, ciphertext plaintext non-retention, tamper/wrong-client rejection and explicit discard behavior.
11. Android production source compiles against the existing pinned Android toolchain; representative-device Keystore/process/reboot evidence remains explicitly unclaimed.
12. `DEV-006` Android ownership is extended for the new production source with direct Java test evidence; existing ownership, feature/lifecycle/alignment, Python, Android and Apps Script gates remain green.
13. No Google provider resource, Apps Script project, disposable proof Sheet, provider authorization flow, network endpoint or legacy MIRA production state is accessed or modified.
14. Branch is pushed, exact PR head/scope are remotely verified, CI succeeds on the exact head, merge succeeds, remote `main` is read back and post-merge CI succeeds before this packet is called complete.

## Explicitly deferred

- Android HTTP/API transport and authentication over the network.
- JSON/wire encoding decisions beyond preserving queued payload bytes exactly.
- Actual reconnect requests or server cursor acquisition.
- Android canonical reads or command submission.
- Server conflict/readback presentation and resolution policy.
- Provider Connections UI/consent/discovery.
- Native notifications/TTS and capture surfaces.
- Release signing/update continuity.
- Representative-device installation, Keystore, reboot/process-death or hardware-backed-key proof.

## Exact next action / resume point

1. Implement the bounded encrypted local offline-state store and deterministic Java tests using the existing `API-001` command contract as semantic authority.
2. Extend the Android ownership manifest for the new production source; do not weaken the existing validator.
3. Run exact-head CI and fix only defects required by this packet.
4. Record implementation/test evidence plus session-end FEATURES/BACKLOG/ROADMAP/PRODUCT_INVARIANTS alignment.
5. Open/verify one bounded PR, require exact-head CI, merge, read back remote `main`, and require post-merge CI before durable closeout.
6. Do not begin Android transport/canonical read-write work until M2-M1-004 is closed.

## Recovery protocol

Read this file first, verify remote branch/head and `main`, then continue from the first incomplete acceptance criterion. Treat M2-M1-001 through M2-M1-003 as closed. Never touch the historical Google proof resource or legacy MIRA production state for this packet, and never claim synchronization merely because local queue/cursor code exists.
