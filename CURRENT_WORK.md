# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active/recovery packet and exact recovery state.

## Product direction

Default Personal MIRA remains stock ChatGPT + Google Workspace first. Android extends the same canonical reality without becoming a second authority. M2-M1-001 through M2-M1-007 are durably closed. The dependency-correct next proof is a truthful Android canonical read before any new Android mutation work.

## Prior-packet recovery verification — 2026-09-04

- Repository: `Matthew-Beare/Mira-2.0`.
- Authoritative `main` before this packet: `4e79ea15caabfc753fe422354a986a1bc650797d`.
- M2-M1-007 final closeout CI: `33836075071` — success on that exact head.
- Remote `main` independently read back the same SHA.
- M2-M1-001 through M2-M1-007 and M2-GOV-012 are durably closed and must not be rerun.
- No Work mode, live provider mutation, historical proof resource, or legacy production fixture is required for this deterministic read slice.

## Session-start alignment verification — 2026-09-04 M2-M1-008

### `FEATURES.md`

- `CLIENT-ANDROID-001` is partial with merged implementation/test evidence through M2-M1-007.
- `API-001`, `AUTH-001`, `STORE-001` and `RECOVERY-002` require exact verified canonical readback and forbid Android cache state from becoming authority.
- This packet advances the Android feature only at the canonical-read implementation/test layer; mutation, cross-ChatGPT readback and device proof remain separate evidence.

### `BACKLOG.md`

- `ANDROID-CLIENT-CORE-001` is partial through M2-M1-007.
- `ANDROID-SYNC` is the next vertical and requires Android read/mutation/cross-readback from the same authority.
- The smallest dependency-correct child slice is canonical Android read with freshness truth. Mutation must not be added merely because it is adjacent in the umbrella.

### `ROADMAP.md`

- M2-M1 ordered proof explicitly places Android canonical read before Android mutation, stock-ChatGPT cross-readback and representative-device proof.
- M2-M1-008 therefore implements the read half only unless a hard dependency is discovered.

### `PRODUCT_INVARIANTS.md`

- One canonical authority remains authoritative; Android snapshots are nonauthoritative cache material.
- Provider consent/read success alone cannot be presented as canonical freshness unless the verified change projection has been fully consumed to a known boundary.
- A read operation must not silently flush pending local mutations merely to obtain fresh remote state.
- No legacy MIRA production state may be used as a development fixture.

### Direction result

**ALIGNED.** Implement a bounded read-only Android synchronization surface that can prove when its local snapshot reflects all verified remote Changes currently exposed by the transport. Do not queue/submit commands, add mutation UX, perform stock-ChatGPT cross-readback, or use live provider/device state in this packet.

## Active packet

### `M2-M1-008` — Canonical Android read and freshness boundary

- **Primary work:** `ANDROID-SYNC`
- **Primary features:** `CLIENT-ANDROID-001`, `API-001`
- **Related invariants/features:** `AUTH-001`, `STORE-001`, `RECOVERY-002`, `DATA-001`, `PROVIDER-002`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `work/m2-m1-008-canonical-read`
- **Base SHA:** `4e79ea15caabfc753fe422354a986a1bc650797d`
- **Status:** active

## Integrity finding that bounds this packet

`ReconnectCoordinator` currently performs one bounded remote Changes page per reconnect pass and returns `COMPLETE` after storing that page. `GoogleWorkspaceTransport` can already see the entire verified Changes projection before truncating to the requested page limit, but `ChangePage` does not expose whether additional verified rows remain after the emitted page.

That behavior is safe as a bounded reconnect-pass result, but it is insufficient for a user-facing canonical read: a target resource may have revision 1 in the first page and a newer revision in a later page. Returning the cached revision after page one as “fresh canonical state” would be false.

M2-M1-008 therefore makes remote pagination completeness explicit before adding a canonical read surface.

## Objective

Deliver the smallest trustworthy Android read vertical over the already-merged transport/cache layers:

1. Extend the provider-neutral change-page contract with explicit `moreAvailable` evidence.
2. Make `GoogleWorkspaceTransport` derive that flag from the fully validated Changes projection rather than guessing from page size alone.
3. Add a read-only change-refresh path in `ReconnectCoordinator` that never reconciles or submits pending commands.
4. Preserve snapshot-before-cursor ordering, monotonic/fork protection and crash-safe retry semantics on the read-only path.
5. Add a provider-neutral Android canonical resource reader that returns fresh found/missing only after the current remote projection is fully consumed; if more verified Changes remain, return an explicit more-data state and never label the cached snapshot fresh.
6. Keep pending command state untouched during canonical reads.
7. Provide deterministic tests proving a later-page higher revision cannot be hidden by an earlier cached revision.

## Acceptance criteria

1. `ReconnectCoordinator.ChangePage` carries explicit remote-pagination completeness, and transport/page validation rejects contradictory material.
2. `GoogleWorkspaceTransport.readChanges` sets `moreAvailable=true` exactly when a validated Change exists after the last emitted sequence for the requested page; an exactly-full terminal page is not falsely marked as more data.
3. A new read-only refresh operation never calls `Transport.reconcileCommand`, even when local pending commands exist.
4. Read-only refresh stores all verified snapshots from the page before advancing its opaque cursor and preserves existing revision/fork protections.
5. Read-only refresh exposes `MORE_REMOTE_CHANGES` when more verified Changes remain and `COMPLETE` only when the current verified remote projection is exhausted.
6. A canonical resource read may return `FRESH_FOUND` or `FRESH_MISSING` only after a `COMPLETE` read-only refresh. It must not expose a cached snapshot as fresh while `MORE_REMOTE_CHANGES` remains.
7. Deterministic pagination test: page one contains target revision 1 and reports more; a later page contains target revision 2. The first read must not claim freshness; after exhaustion the reader returns exactly revision 2.
8. Missing-resource truth is equally strict: `FRESH_MISSING` is possible only after full remote exhaustion, not after an intermediate page.
9. Existing command replay/reconnect behavior remains unchanged and all prior tests stay green.
10. New production Android source is added to the ownership manifest with direct JVM verification. No provider-specific SDK dependency is added to `:core`.
11. No Work mode, live provider access, legacy MIRA production state, historical proof resource, personal identifier or secret is used.
12. End-of-packet FEATURES/BACKLOG/ROADMAP/PRODUCT_INVARIANTS alignment is recorded before merge; `ANDROID-SYNC` remains partial because mutation/cross-readback is deferred.
13. Exact-head CI, expected-head merge, remote-main readback, post-merge CI and final closeout CI are verified before durable closure.

## Explicitly deferred

- Android canonical mutation submission and acknowledgement proof.
- Stock ChatGPT reading an Android mutation back from the same authority.
- Live Android Google authorization/provider-device proof.
- Conflict-resolution UI.
- Broad Connections UI/presentation.
- Representative-device proof and release signing/distribution.
- Notifications/TTS, camera/barcode/NFC/BLE capture.
- Other provider adapters and integration recommendations.

## Completed evidence

- M2-M1-007 is durably closed at `main` `4e79ea15caabfc753fe422354a986a1bc650797d`, CI `33836075071` success.
- Canonical FEATURES/BACKLOG/ROADMAP/PRODUCT_INVARIANTS were re-read from that exact main state before packet activation.
- Existing `OfflineSyncStateStore` already stores encrypted nonauthoritative snapshots with monotonic revision/fork rejection and exposes exact class/resource lookup.
- Existing `ReconnectCoordinator` already stores verified snapshots before cursor advancement but currently combines command replay with change refresh.
- Existing `GoogleWorkspaceTransport` validates the complete bounded Changes table and therefore has sufficient evidence to determine whether rows remain after an emitted page.
- Branch `work/m2-m1-008-canonical-read` was created exactly from verified main `4e79ea15caabfc753fe422354a986a1bc650797d`.

## Session-end alignment verification — pending

### `FEATURES.md`
Pending implementation/test evidence.

### `BACKLOG.md`
Pending M2-M1-008 read-slice evidence; `ANDROID-SYNC` must remain partial.

### `ROADMAP.md`
Pending confirmation that canonical read is complete while mutation/cross-readback remain next.

### `PRODUCT_INVARIANTS.md`
Pending confirmation of freshness truth, no hidden write on read, one authority and nonauthoritative local cache.

### Direction result

**PENDING IMPLEMENTATION/CI.**

## Exact next action / resume point

1. Extend `ChangePage` and Google Workspace change pagination with explicit `moreAvailable` evidence and tests.
2. Add `ReconnectCoordinator.refreshChangesOnly(...)` with no command reconciliation and explicit complete/more-remote results.
3. Add the smallest provider-neutral canonical resource reader over verified refresh + `OfflineSyncStateStore.snapshot(...)`.
4. Add direct tests for later-page revision supersession, fresh missing, pending-command non-mutation, failures, cursor ordering and retry.
5. Update Android ownership for new production source.
6. Run exact branch CI and repair only packet-scoped failures.
7. Do not use Work mode; this packet has no live-provider-only acceptance requirement.

## Recovery protocol

Read this file first and verify branch/head against remote Git. M2-M1-001 through M2-M1-007 are durably closed. Resume only this canonical-read/freshness slice; do not expand into Android mutation, cross-ChatGPT proof, device proof or another provider implementation.
