# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and exact recovery state.

## Product direction

Default Personal MIRA remains stock ChatGPT + Google Workspace with no external infrastructure prerequisite. Android extends the same canonical MIRA semantics and must never become a second provider/database/source authority or bypass the verified serialized shared command boundary.

For the default Personal Android lane, M2-M1-001 selected Google Workspace as the command transport: Android eventually uses the user's provider authorization to append the existing `API-001` command envelope to the durable Workspace `Commands` inbox, while one Apps Script worker owns canonical mutation sequencing. The preserved synchronous WSGI/Cloud Run transport is an advanced profile and must not silently become the Personal default.

Ordinary users must not be exposed to developer/provider mechanics. Google OAuth/connection UI, actual Sheets API calls, provider resource discovery/binding, and representative-device proof remain later packets. This packet is provider-neutral Android reconnect orchestration only.

`M2-M1-001` queued-writer boundary, `M2-M1-002` enrollment/session trust, `M2-M1-003` OS-protected MIRA client credential storage, and `M2-M1-004` encrypted replay/cache/cursor local state are complete and must not be rerun.

## Prior-packet recovery verification — 2026-09-02

- Authoritative remote `main` was read back at `9b7dc8dc681b8af0cd74bbd4c739817f3df030e1`.
- Final M2-M1-004 closeout CI `33699114156` completed successfully on that exact main head.
- M2-M1-004 is therefore durably closed at its declared source/build/test/repository-integration evidence ceiling.

## Session-start alignment verification — 2026-09-02 M2-M1-005

### `FEATURES.md`

- `CLIENT-ANDROID-001` requires the Android native client to use the shared `API-001`, protected credentials, offline replay-safe synchronization, and evidence-based device capabilities without becoming canonical authority.
- `API-001` owns authenticated bounded commands, queries, synchronization and verified mutation readback. Android reconnect orchestration may stage and reconcile transport results but cannot redefine canonical truth.
- `RECOVERY-002` requires transport interruption, stale cursor state, malformed remote results, and local persistence failures to fail closed without silently dropping pending work or advancing synchronization state.

### `BACKLOG.md`

- `ANDROID-CLIENT-CORE-001` remains the unfinished prerequisite before `ANDROID-SYNC`.
- Remaining umbrella scope includes bounded reads, canonical commands, reconnect/cursor sync, and server conflict/readback handling.
- M2-M1-004 completed only the durable local queue/cache/cursor primitive. The next dependency-correct slice is reconnect orchestration over a provider-neutral transport contract.

### `ROADMAP.md`

- M2-M1 step 2 is complete at its declared source/test evidence ceiling through M2-M1-002/003.
- M2-M1 step 3 is replay-safe offline queue plus reconnect/cursor synchronization.
- M2-M1-004 implemented the local durable half of step 3. M2-M1-005 adds the client orchestration contract that safely replays/polls/reconciles remote transport state, but does not implement the real Google provider adapter or claim live synchronization.

### `PRODUCT_INVARIANTS.md`

- Android must reuse MIRA's provider-neutral connection/service semantics and cannot invent technical setup for ordinary users.
- Provider authorization remains a transport-adapter concern. OAuth/provider credentials must not enter `OfflineSyncStateStore` or become canonical identity.
- Future Android Connections UI still needs obvious Connect/Connected/Reconnect/Needs attention/Disconnect semantics and automated post-consent verification.

### M2-M1 command-boundary architecture check

`docs/M1_CONCURRENT_COMMAND_BOUNDARY.md` was re-read before activation. It explicitly selects Google Workspace `Commands` inbox + serialized Apps Script worker for the default Personal Android mutation path. Android eventually uses the user's Google authorization to append the same `API-001` command envelope. The existing `mira/http_transport.py` synchronous `/v1/commands` route executes `ApiService.execute_command` directly and belongs to the preserved advanced managed profile; wiring Personal Android to that route would bypass the queued-writer decision and is rejected.

### Direction result

**ALIGNED.** The smallest safe continuation is a provider-neutral Android reconnect coordinator and transport contract that proves replay/poll/readback/cursor ordering against deterministic fake transport behavior before any Google OAuth/Sheets implementation is attempted.

## Active packet

### `M2-M1-005` — Android client core, reconnect coordinator and transport contract

- **Primary work:** `ANDROID-CLIENT-CORE-001`
- **Primary features:** `CLIENT-ANDROID-001`, `API-001`
- **Related invariants/features:** `RECOVERY-002`, `AUTH-001`, `STORE-001`, `PROVIDER-002`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `work/m2-m1-005-android-reconnect-contract`
- **Base/main SHA:** `9b7dc8dc681b8af0cd74bbd4c739817f3df030e1`
- **Verified base CI:** `33699114156` — success
- **Status:** active; no implementation code committed yet

## Objective

Implement only the Android client-core orchestration seam between `OfflineSyncStateStore` and a future provider/managed transport adapter. The coordinator must preserve exact queued command identity, acknowledge local commands only after verified terminal remote success, apply verified canonical snapshots before advancing the opaque local cursor, and remain replay-safe across interrupted reconnect attempts.

The transport interface is intentionally provider-neutral. A future Personal Google adapter may implement it with the user's Google authorization plus Workspace `Commands`/canonical read surfaces; an advanced managed adapter may use the existing authenticated API profile. Neither provider implementation belongs in this packet.

## Feature alignment

### User-visible behavior this packet must enable later

After a device reconnects, MIRA can safely resume pending Android work without duplicating commands, falsely claiming success, losing unsynced intent, or skipping canonical changes. A later UI can truthfully distinguish pending, synchronized, conflict, authentication/transport failure, and needs-attention states from this orchestration result rather than guessing from connectivity alone.

### Preserved invariants

- Android never mutates canonical provider state directly.
- Workspace Personal commands remain serialized through the M2-M1-001 command boundary.
- Local acknowledgement is not equivalent to submission; only verified terminal remote success permits local acknowledgement.
- Local cached state is nonauthoritative and only receives remote material explicitly marked as verified canonical readback.
- Cursor values remain opaque and advance only after all corresponding verified snapshots are persisted successfully.
- Transport/auth failures do not silently discard pending work, local cache, or cursor state.
- No OAuth/provider secret is persisted in `OfflineSyncStateStore`.

### Explicitly deferred

- Google Sign-In/OAuth UI or token handling;
- actual Google Sheets/Drive API requests;
- discovery/binding of the `Commands`, Resource, Idempotency or provider resources;
- actual managed/Cloud Run HTTP transport use by Android;
- server/provider change-feed implementation if a concrete adapter needs one;
- Android canonical read UI and conflict presentation;
- provider Connections UI;
- notifications/TTS, capture, release signing and representative-device proof.

## Acceptance criteria

1. Add a provider-neutral Android reconnect transport contract with no provider SDK, URL, sheet ID, OAuth token, or canonical mutation implementation.
2. Transport command submission preserves the exact `OfflineSyncStateStore.CommandIntent`; same command retries remain the same logical remote command.
3. Coordinator processes pending commands in stable local FIFO order and never locally acknowledges a command merely because transport accepted/submitted it.
4. Local acknowledgement requires an exact terminal remote success for the same `command_id` and `idempotency_key` with `readback_verified=true`; mismatched/malformed success fails closed.
5. Terminal remote validation/authorization/revision/conflict failure is returned as a deterministic reconnect outcome and leaves the local command unacknowledged for later explicit conflict handling; it is not silently retried as success or discarded.
6. Transport/auth/unavailable failures preserve pending queue, acknowledgement state, snapshots and cursor and stop the bounded reconnect pass without inventing remote truth.
7. Remote change pages carry only verified canonical snapshots plus an opaque current/next cursor contract. The coordinator persists every verified snapshot first and advances the local cursor only after the page is fully stored.
8. Snapshot regression/fork/local-persistence failure prevents cursor advancement and fails closed.
9. Repeating a reconnect after interruption between remote success and local acknowledgement safely resubmits/polls the same command identity and converges without a second local logical command.
10. Repeating a reconnect after snapshots were stored but before cursor advancement is idempotent and may safely store unchanged snapshots before advancing the cursor.
11. Deterministic JVM tests cover FIFO replay, accepted-but-not-terminal state, verified success acknowledgement, conflict retention, malformed/mismatched result rejection, transport failure, cursor ordering, snapshot-before-cursor ordering, interrupted retry, and empty/no-op reconnect.
12. New Android production source is covered by `project/android_code_ownership.json` with direct Java test evidence; no gate is weakened.
13. Existing Android/Python/Apps Script/governance CI remains green.
14. No Google provider resource, Apps Script project, network endpoint or legacy MIRA production state is accessed or modified.
15. Branch/PR scope remains bounded, exact-head CI succeeds, merge/main is read back, and post-merge CI succeeds before packet closeout.

## Completed evidence

- Session-start Git authorities read and reconciled.
- Remote base `main` and exact green CI verified.
- Existing M2-M1 concurrent command-boundary decision re-read.
- Existing synchronous HTTP transport inspected and explicitly rejected as the default Personal Android mutation path because it bypasses the Workspace queued-writer boundary.
- Branch created from exact green base.

## Exact next action / resume point

1. Commit this activation checkpoint before implementation.
2. Inspect the public `OfflineSyncStateStore` API needed by the coordinator and add only the smallest safe accessors if required.
3. Implement the provider-neutral reconnect transport contract and coordinator plus deterministic JVM tests.
4. Extend Android DEV-006 ownership without weakening existing validators.
5. Run exact-head CI, record evidence, open/verify bounded PR, merge only from a verified exact head, require post-merge CI, then write and verify final closeout checkpoint.

## Recovery protocol

Read this file first. Verify remote base/main and packet branch head before continuing. Do not rerun M2-M1-001 through M2-M1-004. Do not touch the historical Google proof resource, create provider resources, invoke provider authorization, or substitute the advanced synchronous HTTP profile for the default Personal queued-writer path merely to make reconnect look implemented.
