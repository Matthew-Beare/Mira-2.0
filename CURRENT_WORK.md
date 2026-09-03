# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active/recovery packet and exact recovery state.

## Prior packet recovery verification — 2026-09-02

- Repository: `Matthew-Beare/Mira-2.0`.
- Authoritative `main`: `7562c247a471c6ebb27f77d8494054e7a54d52b1`.
- M2-M1-005 final closeout CI: `33701057632` — success on that exact head.
- `M2-M1-001` through `M2-M1-005` are durably closed and must not be rerun.
- No Google provider resource or legacy MIRA production state was accessed while recovering this packet.

## Session-start alignment verification — 2026-09-02 M2-M1-006

### `FEATURES.md`

- `CLIENT-ANDROID-001` requires the native Android client to reuse shared `API-001`, protected credentials, replay-safe synchronization and evidence-based provider capabilities without becoming canonical authority.
- `API-001` owns bounded commands, synchronization and verified canonical readback. The Android transport may move exact command/read evidence but may not redefine canonical truth.
- `PROVIDER-002` requires ordinary-user provider onboarding to remain an obvious native Connect/Connected/Reconnect/Needs attention/Disconnect flow with automated post-consent verification. Provider IDs, OAuth scopes, developer consoles and Apps Script mechanics must not become user-facing setup.
- `RECOVERY-002` requires ambiguous network outcomes, duplicate transport delivery, malformed provider rows and partial sync projection failures to fail closed or converge without dropping pending work.

### `BACKLOG.md`

- `ANDROID-CLIENT-CORE-001` remains the active unfinished prerequisite before `ANDROID-SYNC`.
- M2-M1-002 through M2-M1-005 already implemented client trust, protected credentials, encrypted offline state and provider-neutral reconnect orchestration. The backlog row saying there is no Android client implementation is stale and will be corrected in this packet without marking the umbrella complete.
- The next dependency-correct slice is the default-Personal Google Workspace transport needed by `ReconnectCoordinator`; broad UI/device proof remains later.

### `ROADMAP.md`

- M2-M1 step 2 is complete at source/test/repository-integration evidence level.
- M2-M1 step 3 has durable local queue/cursor state plus provider-neutral orchestration but still lacks a concrete Personal Workspace transport.
- Steps 4 through 7 remain incomplete: actual Android canonical read, mutation, stock-ChatGPT cross-readback and representative-device proof are not claimed.

### `PRODUCT_INVARIANTS.md`

- The default Personal lane remains Google Workspace first and must not require servers, copied IDs, developer consoles or terminal work from ordinary users.
- Android must eventually use Google’s native authorization surface. Current Google documentation deprecates legacy `GoogleApiClient`/old Auth entry points in favor of Google Identity Services authorization. This packet does not build the end-user consent UI; it preserves that future seam rather than hard-wiring deprecated auth.
- OAuth/provider access material must remain transport-local and must not be stored in `OfflineSyncStateStore` or confused with the MIRA client credential.

### Workspace command-boundary architecture check

`docs/M1_CONCURRENT_COMMAND_BOUNDARY.md` remains authoritative: default Personal Android submits the existing API command envelope to the Google Workspace `Commands` inbox and one Apps Script worker owns canonical mutation sequencing. The advanced synchronous WSGI/Cloud Run route is not the Personal default.

Google Sheets `values.append` is an append transport, so an ambiguous client network failure can make physical delivery at-least-once. MIRA must therefore treat exact duplicate physical rows with one `command_id` as one logical command when material matches, while failing closed on mismatched duplicates. Canonical idempotency remains in `STORE-001`.

### Direction result

**ALIGNED.** Open one bounded packet for the Workspace row protocol, replay-safe duplicate physical delivery, verified append-only canonical change projection, and Android transport mapping. Do not absorb OAuth/Connections UI or live-provider proof.

## Active packet

### `M2-M1-006` — Android client core, default-Personal Google Workspace transport protocol

- **Primary work:** `ANDROID-CLIENT-CORE-001`
- **Primary features:** `CLIENT-ANDROID-001`, `API-001`
- **Related invariants/features:** `PROVIDER-002`, `RECOVERY-002`, `STORE-001`, `AUTH-001`, `DATA-001`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `work/m2-m1-006-google-workspace-transport`
- **Base SHA:** `7562c247a471c6ebb27f77d8494054e7a54d52b1`
- **Current head:** `2fb79cc466de099a0dc96cb6df5e8b2a4cbeeb56` before this governance correction
- **Status:** active

## Objective

Implement the transport-level default-Personal Google Workspace seam between `ReconnectCoordinator` and the already-proven queued-writer Sheet without accessing a live provider.

The bounded slice will:

1. extend the Workspace worker with an append-only, nonauthoritative verified change projection suitable for opaque cursor synchronization;
2. ensure current canonical resources can be seeded/reconciled into that projection under the serialized worker lock so Android can perform an initial read of pre-Android state;
3. make duplicate physical `Commands` rows for the same exact logical command converge safely, while mismatched duplicate material fails closed;
4. add a provider-specific Android `ReconnectCoordinator.Transport` implementation that maps exact `CommandIntent` values to the Workspace `Commands`/change schemas through a narrow injected Sheets gateway;
5. require exact row/header/material/status/result validation before the Android transport reports pending, success, failure or verified changes;
6. keep spreadsheet discovery, Google Identity Services authorization UI, OAuth token acquisition, real Sheets HTTP/SDK calls and live-provider/device proof outside this packet.

## User-visible behavior enabled

This packet is infrastructure for a later simple Android **Connect Google** experience. It must make reconnect safe enough that the user can lose connectivity after a command append, regain it, and converge without duplicate logical mutations or silently skipped canonical changes. No user-facing UI is shipped in this packet.

## Preserved invariants

- Canonical state remains `single sequencer → API-001 → Authority Registry → STORE-001 → exact readback`.
- `Commands` and the new change projection are transport/read evidence, never canonical authority.
- Same-user Personal semantics remain; cross-person/family scope is still blocked.
- Android stores no provider identifier in source and no OAuth/provider secret in the offline state store.
- Historical M2-M1-001 disposable provider resources and all legacy MIRA production data remain untouched.
- Advanced Cloud Run transport remains available but is not substituted for the default Personal lane.

## Explicitly deferred

- Google Identity Services consent/authorization implementation and account-picker UI.
- Drive/Sheets discovery and automatic provider resource binding.
- Real Sheets REST/SDK network implementation and access-token lifecycle.
- Android Connections UI and disconnect/reconnect presentation.
- Broad canonical read UI or domain rendering.
- Conflict-resolution UI.
- Physical Android device/provider proof.
- Stock ChatGPT cross-readback vertical proof (`ANDROID-SYNC`).
- Notifications/TTS, capture, release signing and broader UI polish.
- Any legacy-production migration.

## Acceptance criteria

1. No live provider/resource/legacy-state access is required for this packet.
2. Workspace change projection is append-only, nonauthoritative, versioned by a strictly increasing opaque sequence and validated with exact headers/material.
3. Every projected change is produced only from canonical `Resources` material that the worker has exact-readback verified; missing projection rows can be reconciled from current canonical state under the worker lock.
4. Projection append/retry is idempotent for the same canonical `(data_class, resource_id, revision, payload)` and fails closed on contradictory same-version material.
5. Android cursor tokens remain opaque outside the Google transport; null initial cursor and empty/no-op pages are deterministic.
6. Android transport validates strict change sequence progression and does not report `readback_verified=true` for malformed/unverified projection rows.
7. Android exact command intent maps losslessly to the Workspace command row schema.
8. A command row is acknowledged locally only through existing `ReconnectCoordinator` semantics after exact logical identity, terminal `succeeded`, valid result JSON and `readback_verified=true`.
9. Exact duplicate physical command rows with identical material converge as one logical remote command; different material under one command ID fails closed.
10. Pending and terminal-failed command states map deterministically without local acknowledgement.
11. Ambiguous append/retry behavior is deterministic in tests: re-reading an already-delivered exact command must not create a second logical mutation.
12. Deterministic Apps Script tests cover change seeding/reconcile, update append, crash/retry projection recovery, exact duplicate physical command delivery and mismatched duplicate rejection.
13. Deterministic Android JVM tests cover exact row mapping, duplicate remote row handling, pending/success/failure parsing, verified change paging, cursor validation, malformed provider data and transport failure preservation.
14. Android production ownership metadata covers the new transport class without weakening existing DEV-006 gates.
15. Existing Android, Python, Apps Script, lifecycle, distribution, alignment and ownership CI remains green.
16. End-of-packet FEATURES/BACKLOG/ROADMAP alignment is recorded before merge; the umbrella `ANDROID-CLIENT-CORE-001` remains incomplete.
17. Exact PR head/scope, merge/main readback and post-merge CI are verified before durable closure.

## Completed evidence

- Session-start Git/main/CI recovery verification complete.
- FEATURES/BACKLOG/ROADMAP/PRODUCT_INVARIANTS direction review complete.
- Current official Google documentation checked for Sheets append semantics and modern Android authorization direction; no legacy Google Auth API is being introduced here.
- PR #101 initial head `2fb79cc466de099a0dc96cb6df5e8b2a4cbeeb56` reached CI `33703372121`; compile, feature registry, lifecycle and Personal distribution were green, then the work-session alignment gate correctly stopped the run because this packet used the noncanonical field label `Related features/invariants`. No product-code gate was weakened; this correction changes the field to the required `Related invariants/features` label.

## Exact next action / resume point

1. Finish the small governance/API-compatibility/test-signature correction set.
2. Run replacement CI through Android ownership/unit tests and Apps Script tests.
3. Correct the stale `ANDROID-CLIENT-CORE-001` backlog status without marking it complete once code behavior is green.
4. Record end-of-packet alignment and exact evidence before merge.

## Recovery protocol

Read this file first. Verify branch/head and `main` before continuing. Do not rerun M2-M1-001 through M2-M1-005. Do not access Google provider state or Work mode merely to test deterministic transport code.
