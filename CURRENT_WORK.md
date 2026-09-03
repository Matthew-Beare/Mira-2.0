# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and exact recovery state.

## Product direction

Default Personal MIRA remains stock ChatGPT + Google Workspace with no external infrastructure prerequisite. Android extends the same canonical MIRA semantics and must never become a second provider/database/source authority or bypass the verified serialized shared command boundary.

For the default Personal Android lane, M2-M1-001 selected Google Workspace as the command transport: Android eventually uses the user's provider authorization to append the existing `API-001` command envelope to the durable Workspace `Commands` inbox, while one Apps Script worker owns canonical mutation sequencing. The preserved synchronous WSGI/Cloud Run transport remains an advanced profile and must not silently become the Personal default.

Ordinary users must not be exposed to developer/provider mechanics. Google OAuth/connection UI, actual Sheets API calls, provider resource discovery/binding, and representative-device proof remain later packets. M2-M1-005 is provider-neutral Android reconnect orchestration only.

`M2-M1-001` queued-writer boundary, `M2-M1-002` enrollment/session trust, `M2-M1-003` OS-protected MIRA client credential storage, and `M2-M1-004` encrypted replay/cache/cursor local state are complete and must not be rerun.

## Prior-packet recovery verification — 2026-09-02

- Authoritative remote `main` was read back at `9b7dc8dc681b8af0cd74bbd4c739817f3df030e1`.
- Final M2-M1-004 closeout CI `33699114156` completed successfully on that exact main head.
- M2-M1-004 is durably closed at its declared source/build/test/repository-integration evidence ceiling.

## Session-start alignment verification — 2026-09-02 M2-M1-005

### `FEATURES.md`

- `CLIENT-ANDROID-001` requires the Android native client to use shared `API-001`, protected credentials, offline replay-safe synchronization, and evidence-based device capabilities without becoming canonical authority.
- `API-001` owns authenticated bounded commands, queries, synchronization and verified mutation readback. Android reconnect orchestration may reconcile transport results but cannot redefine canonical truth.
- `RECOVERY-002` requires transport interruption, stale cursor state, malformed remote results, and local persistence failures to fail closed without silently dropping pending work or advancing synchronization state.

### `BACKLOG.md`

- `ANDROID-CLIENT-CORE-001` remains the unfinished prerequisite before `ANDROID-SYNC`.
- M2-M1-004 completed the durable local queue/cache/cursor primitive. The next dependency-correct slice was reconnect orchestration over a provider-neutral transport contract.
- Actual Personal Google transport, bounded canonical reads, provider binding, conflict presentation and the broader Android vertical remain unfinished.

### `ROADMAP.md`

- M2-M1 step 2 is complete at its declared source/test evidence ceiling through M2-M1-002/003.
- M2-M1 step 3 is replay-safe offline queue plus reconnect/cursor synchronization.
- M2-M1-004 implemented the local durable half of step 3. M2-M1-005 adds provider-neutral client orchestration and does not claim live reconnect because no concrete provider transport is implemented here.

### `PRODUCT_INVARIANTS.md`

- Android must reuse MIRA's provider-neutral connection/service semantics and cannot invent technical setup for ordinary users.
- Provider authorization remains a transport-adapter concern. OAuth/provider credentials do not enter `OfflineSyncStateStore` or become canonical identity.
- Future Android Connections UI still needs obvious Connect/Connected/Reconnect/Needs attention/Disconnect semantics and automated post-consent verification.

### M2-M1 command-boundary architecture check

`docs/M1_CONCURRENT_COMMAND_BOUNDARY.md` was re-read before activation. It explicitly selects Google Workspace `Commands` inbox + serialized Apps Script worker for the default Personal Android mutation path. The existing `mira/http_transport.py` synchronous `/v1/commands` route executes `ApiService.execute_command` directly and belongs to the preserved advanced managed profile; wiring Personal Android to that route would bypass the queued-writer decision and was rejected.

### Direction result

**ALIGNED.** The smallest safe continuation was a provider-neutral Android reconnect coordinator and transport contract proving replay/poll/readback/cursor ordering against deterministic fake transport behavior before any Google OAuth/Sheets implementation.

## Active packet

### `M2-M1-005` — Android client core, reconnect coordinator and transport contract

- **Primary work:** `ANDROID-CLIENT-CORE-001`
- **Primary features:** `CLIENT-ANDROID-001`, `API-001`
- **Related invariants/features:** `RECOVERY-002`, `AUTH-001`, `STORE-001`, `PROVIDER-002`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `work/m2-m1-005-android-reconnect-contract`
- **Base/main SHA:** `9b7dc8dc681b8af0cd74bbd4c739817f3df030e1`
- **Verified base CI:** `33699114156` — success
- **Activation checkpoint:** `450ea4b615403d3444f4d65a8a7abe3b0e1bf23f`
- **Initial coordinator source:** `043f104314f83cd24ad13561eb9da5598dfd1665`
- **Reconnect tests checkpoint:** `6e7c6a12a7c4d784ee492c43979c634e75ce040e`
- **API-23 compatibility correction:** `fd6abe19cff06a334151d5767847a6c889ed990b`
- **Verified implementation head before this evidence commit:** `edf7c6a3f1dbb8e9b77900ed1a200c1221932cd1`
- **Verified implementation-head CI:** `33700649333` — success
- **PR:** #100
- **Verified changed-file scope before this evidence commit:** exactly 4 intended files
- **Status:** bounded implementation/build/test slice satisfied; this evidence head, merge/main readback and post-merge verification remain

## Objective result

**IMPLEMENTED AND TEST-VERIFIED FOR THIS BOUNDED SLICE.** `ReconnectCoordinator` now defines the provider-neutral orchestration seam between `OfflineSyncStateStore` and future authenticated transport adapters. It does not contain Google SDK code, provider URLs, resource identifiers, OAuth material or canonical mutation code.

The coordinator enforces these ordering rules:

1. pending commands are reconciled in stable local FIFO order;
2. transport acceptance/pending state never removes local work;
3. local acknowledgement requires exact `command_id`, exact `idempotency_key`, terminal remote success and `readback_verified=true`;
4. terminal remote validation/authorization/conflict failure is returned without local acknowledgement for later explicit handling;
5. transport/protocol/local-state failure stops the bounded pass without inventing remote truth;
6. verified remote snapshots are persisted before local command acknowledgement when supplied with a command result;
7. after all bounded local commands are resolved, verified canonical change snapshots are persisted before the opaque cursor advances;
8. a bounded pass that leaves local commands pending does not read/advance the change cursor.

This packet does **not** complete `ANDROID-CLIENT-CORE-001` or M2-M1 step 3. A concrete Personal Google transport still must authenticate through the intended provider lane, append/read the Workspace command inbox, read verified canonical changes, and map provider evidence into this contract. No live provider synchronization is claimed.

## Completed implementation evidence

### Provider-neutral transport contract

- Added `android-client/core/src/main/java/com/mira/client/core/sync/ReconnectCoordinator.java`.
- `Transport.reconcileCommand(CommandIntent)` accepts the exact immutable local command intent rather than a second Android command model.
- `Transport.readChanges(cursor, limit)` uses an opaque cursor and returns only adapter-asserted verified canonical snapshots plus exact from/next cursor state.
- Transport failures have stable adapter-owned code/message through `TransportException`.
- No provider, HTTP, OAuth, Google, Cloud Run, Sheet or resource-ID dependency exists in the coordinator source.

### Command reconciliation rules

- Exact command and idempotency identities are required on every remote command projection.
- `PENDING` leaves the command queued and stops the pass honestly.
- `FAILED` leaves the command queued and returns deterministic error material for later conflict/error handling.
- `SUCCEEDED` is rejected unless canonical readback is explicitly verified and no terminal error material is present.
- Verified snapshots accompanying terminal success are stored before acknowledgement.
- Local acknowledgement occurs only after all required local persistence succeeds.
- When a command limit leaves additional local pending work, the pass returns `MORE_PENDING` and does not fetch/advance canonical changes.

### Canonical change/cursor rules

- Change page `fromCursor` must exactly equal the requested current cursor.
- Change pages must explicitly claim verified canonical readback.
- Returned snapshot count may not exceed the requested bound.
- A page may reuse the same cursor only when it contains no snapshots; snapshots without cursor progress fail closed.
- Every verified snapshot is persisted through existing monotonic/fork-safe `OfflineSyncStateStore.putSnapshot` before cursor CAS.
- Snapshot regression/fork or local persistence failure prevents cursor advancement.

### Crash/retry behavior

- A package-private deterministic fault seam simulates interruption after verified remote command success but before local acknowledgement. Retry replays the exact same stored command identity and converges through remote idempotency without creating a second local logical command.
- A second fault seam simulates interruption after verified change snapshots are persisted but before cursor advancement. Retry sees the old cursor, safely re-stores unchanged snapshots, then advances the cursor.
- The production coordinator has no automatic destructive reset path.

### Android compatibility

- The initial source pass used Java collection/string convenience methods that are not guaranteed by Android API 23.
- Before CI, `List.of()` and `String.isBlank()` were removed rather than adding core-library desugaring/dependency scope. Production code now stays compatible with the existing minSdk-23 client module surface.

### Deterministic JVM tests

Added `android-client/core/src/test/java/com/mira/client/core/sync/ReconnectCoordinatorTest.java`. Tests cover:

- exact command-envelope field/payload preservation into transport;
- stable FIFO verified-success acknowledgement;
- accepted/pending remote state without local acknowledgement;
- terminal conflict retention;
- unverified success and mismatched idempotency rejection;
- transport failure preserving pending queue, cache and cursor;
- interruption after remote success before local acknowledgement, then safe exact replay/convergence;
- verified snapshots before cursor progression;
- snapshot fork/regression preventing cursor progression;
- interruption after snapshots before cursor, then idempotent retry;
- malformed/unverified change-page rejection;
- bounded pass behavior with additional pending local commands; and
- empty/no-op reconnect cursor behavior.

### Repository integrity / DEV-006

- Extended `project/android_code_ownership.json` with `android-client-reconnect-coordinator`.
- New production source is owned by `CLIENT-ANDROID-001`, `API-001`, `RECOVERY-002` and work `ANDROID-CLIENT-CORE-001`.
- Direct Java verification references `ReconnectCoordinatorTest.java`.
- Existing credential-security and offline-state ownership entries remain intact; no validator/gate was weakened.

### CI and scope evidence

- PR #100 opened against exact base `9b7dc8dc681b8af0cd74bbd4c739817f3df030e1`.
- Exact implementation head `edf7c6a3f1dbb8e9b77900ed1a200c1221932cd1` completed CI `33700649333` successfully.
- Green stages include compile, feature registry, product lifecycle ledger, Personal starter distribution, work-session alignment, code ownership, Android client-core unit tests, Python unit tests and Workspace Apps Script tests.
- Changed-file scope before this evidence commit is exactly:
  - `CURRENT_WORK.md`
  - `android-client/core/src/main/java/com/mira/client/core/sync/ReconnectCoordinator.java`
  - `android-client/core/src/test/java/com/mira/client/core/sync/ReconnectCoordinatorTest.java`
  - `project/android_code_ownership.json`
- No Google provider resource, Apps Script project, provider authorization flow, network endpoint or legacy MIRA production state was accessed or modified.

## Acceptance criteria result

1. Provider-neutral Android reconnect transport contract with no provider SDK/URL/OAuth/resource ID/canonical mutation implementation — **satisfied**.
2. Exact stored `CommandIntent` passed to transport without inventing a second command model — **satisfied**.
3. Stable FIFO processing and no acknowledgement on submission/pending alone — **satisfied**.
4. Ack requires exact identities + terminal success + verified readback — **satisfied**.
5. Terminal remote failure retained locally and returned deterministically — **satisfied**.
6. Transport/auth/unavailable failure preserves local truth and stops pass — **satisfied**.
7. Verified snapshots persist before cursor advancement — **satisfied**.
8. Snapshot regression/fork/local persistence failure prevents cursor advancement — **satisfied**.
9. Interrupted remote-success-before-ack retry converges with same local command identity — **satisfied**.
10. Interrupted snapshots-before-cursor retry is idempotent — **satisfied**.
11. Deterministic JVM coverage for required replay/pending/failure/cursor cases — **satisfied**.
12. Android DEV-006 ownership extended without weakening gates — **satisfied**.
13. Existing Android/Python/Apps Script/governance CI remains green — **satisfied at exact implementation head**.
14. No provider/network/legacy resource touched — **satisfied**.
15. Exact PR head/scope CI, merge/main readback and post-merge CI — **partially satisfied**: bounded PR exists and implementation-head CI is green; evidence-head CI, merge/readback and post-merge verification remain.

## Evidence ceiling

- **Implemented:** provider-neutral Android reconnect coordinator/transport contract and ownership metadata.
- **Test verified:** deterministic JVM replay/failure/cursor/crash semantics plus Android production compilation.
- **Integration verified:** repository CI integrates the coordinator/tests with the existing Android/Python/Apps Script and governance suite at exact implementation head.
- **Not provider/live/device verified:** Google authorization, provider API calls, Workspace command submission/readback from Android, canonical provider change feed, physical-device execution, process/reboot behavior, actual conflict UI, Android canonical read/write, or representative-device proof.

## Session-end alignment verification — 2026-09-02 M2-M1-005

### `FEATURES.md`

`CLIENT-ANDROID-001` remains partially implemented. M2-M1-005 satisfies only the provider-neutral reconnect orchestration prerequisite. `API-001` remains the service/canonical boundary; transport adapters must provide verified evidence rather than granting the coordinator provider authority. No feature evidence/status should be promoted to complete.

### `BACKLOG.md`

`ANDROID-CLIENT-CORE-001` remains unfinished and must not be marked complete. After this packet closes, the next dependency-correct slice is the concrete default-Personal Google Android transport needed to implement this contract safely: provider authorization/capability binding, exact Workspace command-inbox submission/status readback, and a bounded verified canonical change-read mechanism. That future packet must remain separate from Connections UI, broad canonical read UI, conflict presentation and the full Android vertical.

### `ROADMAP.md`

M2-M1 ordering remains correct. M2-M1-005 advances step 3 at the client orchestration/test level but does not satisfy actual reconnect synchronization without a concrete provider transport. Steps 4 through 7 remain untouched.

### `PRODUCT_INVARIANTS.md`

The implementation remains provider-neutral and introduces no technical provider setup, OAuth persistence, copied provider IDs or alternate activation model. The future Android Connections surface and automatic post-consent verification remain required before ordinary-user shared access ships.

### Direction result

**ALIGNED.** The packet adds only the reconnect orchestration primitive required before safe Personal Google transport integration, preserves the M2-M1 queued-writer decision, keeps canonical authority outside Android, and does not counterfeit provider/live/device evidence.

## Exact next action / resume point

1. Require CI on this evidence commit and fix only M2-M1-005 defects if a gate fails.
2. Re-read PR #100 head, mergeability and changed-file scope; require exact green evidence head and the same four-file bounded scope.
3. Merge PR #100 using the exact verified head.
4. Read back remote `main` and require post-merge CI on the exact merge head.
5. Persist final merge/main/post-merge evidence in `CURRENT_WORK.md` on main, require exact closeout-head CI, and independently read back remote main before declaring M2-M1-005 durably closed.
6. Do not begin the concrete Google transport packet inside M2-M1-005.

## Recovery protocol

Read this file first. Verify PR #100 exact head and CI before merge. Do not rerun M2-M1-001 through M2-M1-004. Do not touch the historical Google proof resource, create provider resources, invoke provider authorization, or substitute the advanced synchronous HTTP profile for the default Personal queued-writer path merely to make reconnect look implemented.
