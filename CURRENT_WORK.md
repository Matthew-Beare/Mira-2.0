# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active/recovery packet and exact recovery state.

## Product direction

Default Personal MIRA remains stock ChatGPT + Google Workspace with no external infrastructure prerequisite. Android extends the same canonical MIRA semantics and must never become a second provider/database/source authority or bypass the verified serialized shared command boundary.

For the default Personal Android lane, M2-M1-001 selected Google Workspace as the command transport: Android eventually uses the user's provider authorization to append the existing `API-001` command envelope to the durable Workspace `Commands` inbox, while one Apps Script worker owns canonical mutation sequencing. The preserved synchronous WSGI/Cloud Run transport remains an advanced profile and must not silently become the Personal default.

Ordinary users must not be exposed to developer/provider mechanics. Google OAuth/connection UI, actual Sheets API calls, provider resource discovery/binding, and representative-device proof remain later packets.

`M2-M1-001` queued-writer boundary, `M2-M1-002` enrollment/session trust, `M2-M1-003` OS-protected MIRA client credential storage, and `M2-M1-004` encrypted replay/cache/cursor local state are complete and must not be rerun.

## Prior-packet recovery verification — 2026-09-02

- M2-M1-004 final authoritative `main`: `9b7dc8dc681b8af0cd74bbd4c739817f3df030e1`.
- M2-M1-004 final closeout CI: `33699114156` — success on that exact head.
- M2-M1-004 is durably closed.

## Session-start alignment verification — 2026-09-02 M2-M1-005

### `FEATURES.md`

- `CLIENT-ANDROID-001` requires the Android native client to use shared `API-001`, protected credentials, offline replay-safe synchronization, and evidence-based device capabilities without becoming canonical authority.
- `API-001` owns authenticated bounded commands, queries, synchronization and verified mutation readback. Android reconnect orchestration may reconcile transport results but cannot redefine canonical truth.
- `RECOVERY-002` requires interruption, stale cursor state, malformed remote results, and local persistence failures to fail closed without silently dropping pending work or advancing synchronization state.

### `BACKLOG.md`

- `ANDROID-CLIENT-CORE-001` remains the unfinished prerequisite before `ANDROID-SYNC`.
- M2-M1-004 completed the durable local queue/cache/cursor primitive. M2-M1-005 selected the next dependency-correct slice: provider-neutral reconnect orchestration over that durable state.
- Actual Personal Google transport, bounded canonical reads, provider binding, conflict presentation and the broader Android vertical remain unfinished.

### `ROADMAP.md`

- M2-M1 step 2 is complete at its declared source/test evidence ceiling through M2-M1-002/003.
- M2-M1 step 3 is replay-safe offline queue plus reconnect/cursor synchronization.
- M2-M1-004 implemented the local durable half. M2-M1-005 implements provider-neutral client orchestration only and does not claim live reconnect without a concrete provider transport.

### `PRODUCT_INVARIANTS.md`

- Android reuses MIRA's provider-neutral connection/service semantics and cannot export technical setup to ordinary users.
- Provider authorization remains a transport-adapter concern. OAuth/provider credentials do not enter `OfflineSyncStateStore` or become canonical identity.
- Future Android Connections UI still requires obvious Connect/Connected/Reconnect/Needs attention/Disconnect semantics and automated post-consent verification.

### M2-M1 command-boundary architecture check

`docs/M1_CONCURRENT_COMMAND_BOUNDARY.md` explicitly selects Google Workspace `Commands` inbox + serialized Apps Script worker for the default Personal Android mutation path. The existing `mira/http_transport.py` synchronous `/v1/commands` route executes `ApiService.execute_command` directly and belongs to the advanced managed profile. Wiring Personal Android to it would bypass the queued-writer decision and was rejected.

### Direction result

**ALIGNED.** The smallest safe continuation was a provider-neutral Android reconnect coordinator/transport contract proving replay/readback/cursor ordering before any Google OAuth/Sheets implementation.

## Active packet

### `M2-M1-005` — Android client core, reconnect coordinator and transport contract

- **Primary work:** `ANDROID-CLIENT-CORE-001`
- **Primary features:** `CLIENT-ANDROID-001`, `API-001`
- **Related invariants/features:** `RECOVERY-002`, `AUTH-001`, `STORE-001`, `PROVIDER-002`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Checkpoint branch:** `main`
- **Packet base/main SHA:** `9b7dc8dc681b8af0cd74bbd4c739817f3df030e1`
- **Activation checkpoint:** `450ea4b615403d3444f4d65a8a7abe3b0e1bf23f`
- **Initial coordinator source:** `043f104314f83cd24ad13561eb9da5598dfd1665`
- **Reconnect tests checkpoint:** `6e7c6a12a7c4d784ee492c43979c634e75ce040e`
- **API-23 compatibility correction:** `fd6abe19cff06a334151d5767847a6c889ed990b`
- **Verified implementation head:** `edf7c6a3f1dbb8e9b77900ed1a200c1221932cd1`
- **Verified implementation-head CI:** `33700649333` — success
- **Verified evidence head:** `5ae44b0fa1c561d206ce82f9030daebe12c2a4b2`
- **Verified evidence-head CI:** `33700791833` — success
- **PR:** #100 — merged
- **Merge/main SHA before this closeout commit:** `fc635045b2cce3960a0e206253ca51101557be86`
- **Verified post-merge CI:** `33700898313` — success
- **Merged changed-file scope:** exactly 4 intended files
- **Status:** complete for this bounded source/build/test/repository-integration slice; this final closeout commit requires exact-head CI before durable closure

## Objective result

**COMPLETE AT THE BOUNDED SOURCE/BUILD/TEST/REPOSITORY-INTEGRATION EVIDENCE CEILING.** `ReconnectCoordinator` now defines the provider-neutral orchestration seam between `OfflineSyncStateStore` and future authenticated transport adapters. It contains no Google SDK, provider URL, resource identifier, OAuth material or canonical mutation implementation.

The coordinator enforces:

1. stable FIFO reconciliation of durable pending commands;
2. no local acknowledgement for transport acceptance or pending state;
3. acknowledgement only for exact `command_id` + `idempotency_key` terminal success with `readback_verified=true`;
4. terminal remote conflict/failure retention for later explicit handling;
5. fail-closed transport/protocol/local-state behavior;
6. verified command-result snapshots before local acknowledgement;
7. verified canonical change snapshots before opaque cursor advancement; and
8. no cursor read/advance while a bounded reconnect pass still leaves local commands pending.

This does **not** complete `ANDROID-CLIENT-CORE-001` or live M2-M1 step 3. A concrete default-Personal Google Android transport is still required to authenticate through the intended provider lane, append/read the Workspace command inbox, and expose bounded verified canonical changes to this coordinator.

## Completed implementation evidence

### Provider-neutral reconnect contract

- Added `android-client/core/src/main/java/com/mira/client/core/sync/ReconnectCoordinator.java`.
- Transport receives the exact immutable `OfflineSyncStateStore.CommandIntent`; no second Android command model was invented.
- `RemoteCommandState` distinguishes pending, succeeded and failed remote command state.
- `ChangePage` carries exact requested/from cursor, next opaque cursor, verified canonical snapshots and explicit readback verification.
- `TransportException` carries stable adapter-owned transport/auth/unavailability categories.
- The coordinator never performs direct canonical mutation.

### Replay/readback/cursor integrity

- Exact command/idempotency identity is verified before local state changes.
- Terminal success without verified readback fails closed.
- Pending state and terminal failure remain durable locally.
- Verified command-result snapshots persist before command acknowledgement.
- Verified change snapshots persist before cursor compare-and-set.
- Snapshot fork/regression/local persistence failures prevent cursor advancement.
- Same-cursor empty change pages are allowed as no-op readback; snapshots without cursor progress are rejected.
- A command-limited pass with more local pending work returns `MORE_PENDING` without advancing synchronization state.

### Crash/retry evidence

- Deterministic fault injection proves interruption after verified remote success but before local acknowledgement. Retry resubmits the same durable command identity and converges without a second local logical command.
- Deterministic fault injection proves interruption after verified snapshots but before cursor advancement. Retry safely stores unchanged snapshots again and then advances the cursor.
- No destructive automatic reset path exists.

### Android compatibility

- Initial source used Java convenience APIs not guaranteed by Android API 23.
- Before CI, `List.of()` and `String.isBlank()` were removed instead of adding desugaring/dependency scope.
- Existing minSdk-23 module constraints remain unchanged.

### Deterministic JVM tests

`ReconnectCoordinatorTest` covers:

- exact command field/payload preservation;
- FIFO verified-success acknowledgement;
- accepted/pending state without acknowledgement;
- terminal conflict retention;
- unverified success and mismatched idempotency rejection;
- transport failure preserving pending/cache/cursor state;
- remote-success-before-ack interruption/retry;
- snapshot-before-cursor ordering and fork/regression rejection;
- snapshots-before-cursor interruption/retry;
- malformed/unverified change-page rejection;
- bounded pass with remaining commands; and
- empty/no-op reconnect behavior.

### Repository integrity / DEV-006

- Added `android-client-reconnect-coordinator` to `project/android_code_ownership.json`.
- Production source is owned by `CLIENT-ANDROID-001`, `API-001`, `RECOVERY-002` and work `ANDROID-CLIENT-CORE-001`.
- Direct Java verification points to `ReconnectCoordinatorTest.java`.
- Existing credential/offline ownership remained intact; no validator or CI gate was weakened.

### CI / PR / merge evidence

- PR #100 changed exactly:
  - `CURRENT_WORK.md`
  - `android-client/core/src/main/java/com/mira/client/core/sync/ReconnectCoordinator.java`
  - `android-client/core/src/test/java/com/mira/client/core/sync/ReconnectCoordinatorTest.java`
  - `project/android_code_ownership.json`
- Implementation head `edf7c6a3f1dbb8e9b77900ed1a200c1221932cd1` → CI `33700649333` success.
- Evidence head `5ae44b0fa1c561d206ce82f9030daebe12c2a4b2` → CI `33700791833` success.
- PR #100 was mergeable and merged using the exact verified evidence head.
- Merge/main `fc635045b2cce3960a0e206253ca51101557be86` independently read back from remote `main`.
- Post-merge CI `33700898313` succeeded on that exact merge head with compile, feature registry, lifecycle ledger, distribution, alignment, ownership, Android tests, Python tests and Workspace Apps Script tests green.
- No Google provider resource, Apps Script project, provider authorization flow, network endpoint or legacy MIRA production state was accessed or modified.

## Acceptance criteria result

1. Provider-neutral reconnect contract with no provider SDK/URL/OAuth/resource ID/canonical mutation — **satisfied**.
2. Exact stored command intent passed to transport — **satisfied**.
3. FIFO processing and no acknowledgement on submission/pending — **satisfied**.
4. Ack requires exact identities + terminal success + verified readback — **satisfied**.
5. Terminal remote failure retained locally and returned deterministically — **satisfied**.
6. Transport/auth/unavailable failure preserves local truth — **satisfied**.
7. Verified snapshots persist before cursor advancement — **satisfied**.
8. Snapshot regression/fork/local persistence failure blocks cursor advance — **satisfied**.
9. Interrupted remote-success-before-ack retry converges safely — **satisfied**.
10. Interrupted snapshots-before-cursor retry is idempotent — **satisfied**.
11. Required deterministic JVM cases — **satisfied**.
12. Android DEV-006 ownership without gate weakening — **satisfied**.
13. Existing Android/Python/Apps Script/governance CI green — **satisfied**.
14. No provider/network/legacy resource touched — **satisfied**.
15. Exact PR head/scope, merge/main readback and post-merge CI — **satisfied through merge head `fc635045b2cce3960a0e206253ca51101557be86`; final closeout-head CI is the only remaining recovery gate**.

## Evidence ceiling

- **Implemented:** provider-neutral Android reconnect coordinator/transport contract and ownership metadata.
- **Test verified:** deterministic JVM replay/failure/cursor/crash semantics plus Android production compilation.
- **Integration verified:** merged repository CI integrates the coordinator/tests with the existing Android/Python/Apps Script/governance suite.
- **Not provider/live/device verified:** Google authorization, provider API calls, Workspace command submission/readback from Android, canonical provider change feed, physical-device execution, actual conflict UI, Android canonical read/write or representative-device proof.

## Session-end alignment verification — 2026-09-02 M2-M1-005

### `FEATURES.md`

`CLIENT-ANDROID-001` remains partially implemented. M2-M1-005 satisfies only provider-neutral reconnect orchestration. `API-001` remains the service/canonical boundary; transport adapters must provide verified evidence rather than granting Android provider authority. No feature status is promoted to complete.

### `BACKLOG.md`

`ANDROID-CLIENT-CORE-001` remains unfinished and must not be marked complete. The next dependency-correct bounded slice is the concrete default-Personal Google Android transport needed to implement this contract safely: provider authorization/capability binding, exact Workspace command-inbox submission/status readback, and a bounded verified canonical change-read mechanism. Keep that future packet separate from Connections UI, broad canonical read UI, conflict presentation and the full Android vertical.

### `ROADMAP.md`

M2-M1 ordering remains correct. M2-M1-005 advances step 3 at the client orchestration/test level but does not satisfy actual reconnect synchronization without a concrete provider transport. Steps 4 through 7 remain untouched.

### `PRODUCT_INVARIANTS.md`

The implementation remains provider-neutral and introduces no technical provider setup, OAuth persistence, copied provider IDs or alternate activation model. The future Android Connections surface and automatic post-consent verification remain required before ordinary-user shared access ships.

### Direction result

**ALIGNED.** The merged packet adds only the reconnect orchestration prerequisite, preserves the Workspace queued-writer decision, keeps canonical authority outside Android, and does not counterfeit provider/live/device evidence.

## Exact next action / resume point

1. Require CI on this final main closeout commit and verify it succeeds on the exact pushed head.
2. Independently read back remote `main` at that exact closeout head.
3. Once both are verified, M2-M1-005 is durably closed. Do not rerun its reconnect-coordinator work.
4. In the next development packet, re-read Git first and select exactly one bounded continuation of `ANDROID-CLIENT-CORE-001` for the concrete default-Personal Google Android transport and verified change-read contract.
5. Do not automatically absorb Connections UI, broad Android canonical-read UI, conflict presentation, notifications/TTS, capture, release signing or representative-device proof into that transport packet.
6. Do not touch historical M2-M1-001 proof resources unless a future explicit live-provider acceptance criterion genuinely requires isolated provider verification and Git authorizes it.

## Recovery protocol

Read this file first and verify remote `main` plus exact CI. If the final closeout-head CI is green, treat M2-M1-005 as complete and start no work from chat reconstruction. Do not rerun M2-M1-001 through M2-M1-005; do not substitute the advanced synchronous HTTP profile for the default Personal queued-writer path.
