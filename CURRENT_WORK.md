# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active/recovery packet and exact recovery state.

## Product direction

Default Personal MIRA remains stock ChatGPT + Google Workspace first, with provider-neutral expansion through explicit ordinary-user connections. MIRA should progressively learn what tools and services a user already relies on and recommend useful supported integrations without silently installing, authorizing, activating, migrating, or changing canonical authority.

`M2-M1-001` through `M2-M1-007` are durably closed at their recorded evidence ceilings. `M2-GOV-012` is also durably closed.

## M2-M1-007 durable closeout — 2026-09-03

- Repository: `Matthew-Beare/Mira-2.0`.
- PR: `#106` — merged.
- Exact merged `main` SHA: `f6d38ee9398bc473425f33b6fe97fb5fb0ae4b35`.
- Exact post-merge CI: `33826483012` / run `374` — **success** on that exact SHA.
- M2-M1-007 reached implemented, deterministic-test and repository-integration evidence for Android Google authorization, provider-native Picker selection, verified Workspace binding and bounded Drive/Sheets transport.
- M2-M1-007 did **not** claim live Google authorization on a physical device, production signing, queued-writer activation, or Android↔stock-ChatGPT shared-state proof.
- M2-M1-001 through M2-M1-007 must not be rerun.

## Session-start alignment verification — 2026-09-03 M2-M1-008

### `FEATURES.md`

- `CLIENT-ANDROID-001` remains the required Android companion feature and is still partial. The next missing user-visible proof is an Android read path from the same canonical Personal reality.
- `API-001`, `AUTH-001`, `STORE-001`, and `RECOVERY-002` continue to require one canonical authority, provider-neutral command/query/sync semantics, exact readback, and failure isolation.
- `PROVIDER-002` / `PROVIDER-003` now have a merged Android Google binding adapter, but live provider/device evidence remains separate from source/test evidence.

### `BACKLOG.md`

- `ANDROID-CLIENT-CORE-001` has merged foundations through M2-M1-007: protected credential storage, encrypted offline queue/cache/cursor state, reconnect orchestration, Google Workspace transport, Google Picker authorization/binding, and bounded provider REST access.
- The next dependency-correct slice is not another provider setup packet. It is the read-only canonical-state vertical that composes those pieces without submitting mutations.
- Full Android mutation, stock-ChatGPT cross-readback, notifications/TTS, capture surfaces, release signing and device proof remain later work.

### `ROADMAP.md`

- M2-M1 ordered proof requires Android canonical read before Android mutation, stock-ChatGPT cross-readback and representative-device proof.
- The roadmap's old sentence saying Android client core is “next” is stale after M2-M1-007 and should be corrected in this packet without inflating completion evidence.

### `PRODUCT_INVARIANTS.md`

- Android remains a client/cache, never a second authority.
- Read-only synchronization must persist only verified canonical snapshots and must never advance a cursor before snapshot durability.
- A read action must not opportunistically submit queued mutations.
- Legacy production state remains protected and cannot be used as a development fixture.

### Direction result

**ALIGNED.** Open one bounded read-only Android vertical. Reuse the merged binding, transport, reconnect and encrypted local-state primitives. Do not add mutation/UI/device scope merely because adjacent code exists.

## Active packet

### `M2-M1-008` — Android canonical Personal read vertical

- **Primary work:** `ANDROID-CLIENT-CORE-001`
- **Primary feature:** `CLIENT-ANDROID-001`
- **Related features/invariants:** `API-001`, `AUTH-001`, `STORE-001`, `RECOVERY-002`, `PROVIDER-002`, `PROVIDER-003`, `SOURCE-001`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `work/m2-m1-008-android-canonical-read`
- **Packet base SHA:** `f6d38ee9398bc473425f33b6fe97fb5fb0ae4b35`
- **Current head SHA:** pending this packet-open checkpoint readback
- **Status:** active

## Objective

Implement the narrow Android read-only vertical that turns the already-merged Google Workspace binding + verified Changes protocol + encrypted offline snapshot store into an application-facing canonical Personal read path. A read refresh must revalidate provider readiness, fetch bounded verified canonical change evidence from the current cursor, durably persist snapshots before cursor movement, and expose immutable cached snapshots to later UI code without submitting queued commands or becoming canonical authority.

This packet does **not** implement Android mutation, conflict resolution UI, stock-ChatGPT cross-readback, physical-device/provider acceptance, notification/TTS delivery, camera/barcode/NFC/BLE capture, release signing, or general app UI.

## Reversible engineering decision — explicit pull-only read path

`ReconnectCoordinator.reconnect()` intentionally reconciles pending local commands before reading changes. Reusing that method for a user-initiated read refresh would allow a read gesture to submit mutations, which violates separation of concerns and makes later UI safety harder to reason about.

M2-M1-008 therefore adds an explicit bounded **pull-only** synchronization operation that uses the same transport/page validation and snapshot-before-cursor ordering while never touching pending commands or acknowledgements. The normal reconnect path retains its existing semantics. This is a reversible orchestration split, not a new authority or protocol.

## Dependencies and blockers

- M2-M1-007 exact post-merge CI `33826483012` — success.
- `OfflineSyncStateStore`, `ReconnectCoordinator`, `GoogleWorkspaceTransport`, `GoogleWorkspaceConnection`, and `GoogleWorkspaceRestApi` — merged and deterministic-test verified.
- Changes projection seeding/repair remains owned by the serialized Google Apps Script worker. The Android client consumes verified projection evidence; it does not manufacture canonical state.
- No live provider/device action is required for this source/test packet.

## Acceptance criteria

1. **Read-only pull primitive** — `ReconnectCoordinator` exposes a bounded pull operation that reads verified changes from the current cursor, persists snapshots, and advances the cursor only after snapshot durability; it must not inspect, submit, acknowledge, reorder, or otherwise mutate pending command state.
2. **Exact failure isolation** — transport/protocol/local failures from a pull preserve pending commands and the prior cursor; already-durable snapshots remain safe for exact retry.
3. **Application-facing read session** — a small Android core adapter composes a previously verified Google binding, a fresh authorization token, bounded Google REST gateway, `GoogleWorkspaceTransport`, `ReconnectCoordinator`, and the encrypted local state store into a read refresh result suitable for later UI mapping.
4. **Fresh binding verification** — each connected read session revalidates the stored non-secret Workspace binding with fresh authorization before constructing the transport. Expired/denied authorization, binding drift, direct-writer-only state, or schema/readiness mismatch fail closed and do not touch local cursor/commands.
5. **Immutable cached reads** — Android core exposes bounded immutable cached snapshot lookup/listing from `OfflineSyncStateStore` after verified pull. The cache remains explicitly nonauthoritative and monotonic by canonical revision.
6. **No hidden mutation** — deterministic tests prove a read refresh performs zero `reconcileCommand` / Commands append calls even when pending local commands exist.
7. **Initial and incremental read behavior** — tests cover null initial cursor, subsequent cursor progression, no-change refresh, snapshot update by higher revision, retry after crash between snapshot persistence and cursor update, and bounded page behavior.
8. **No provider/user secrets or legacy fixtures** — tests use synthetic bindings, fake provider responses and fake local state only. No live spreadsheet IDs, tokens, personal data, or legacy production artifacts are committed.
9. **Regression gates** — all prior Android core tests, Python tests, Apps Script tests, feature/alignment/code-ownership gates, and full repository CI pass on the exact packet head.
10. **Evidence ceiling** — this packet may claim implemented/test/repository-integration evidence for the Android canonical read vertical. It may not claim physical-device, live provider, production signing, Android mutation, or Android↔stock-ChatGPT shared-state acceptance without later exact evidence.

## Completed evidence

- Verified M2-M1-007 merged `main` at `f6d38ee9398bc473425f33b6fe97fb5fb0ae4b35`.
- Verified post-merge exact-head CI run `33826483012` completed **success**.
- Re-read current `ReconnectCoordinator`: normal reconnect intentionally handles queued commands before a verified change page and already enforces snapshot-before-cursor ordering.
- Re-read current `GoogleWorkspaceTransport`: null cursor maps to change sequence zero; Changes rows require contiguous sequence, canonical JSON, deterministic change identity and `readback_verified=true` before becoming snapshots.
- Re-read Apps Script shared-writer worker: every worker pass reconciles current canonical Resources into missing verified Changes rows before command processing, excluding internal authority rows.
- Active branch created from exact verified main SHA: `work/m2-m1-008-android-canonical-read`.

## Exact next action / resume point

1. Add a pull-only method to `ReconnectCoordinator` by extracting/reusing the existing change-page persistence path without changing normal reconnect behavior.
2. Add bounded immutable snapshot-list/read support to `OfflineSyncStateStore` if required by the application-facing read seam.
3. Add `GoogleWorkspaceReadSession` (or equivalently narrow adapter) that revalidates binding, constructs the bounded provider transport, executes pull-only sync, and returns explicit readiness/sync state without storing access tokens.
4. Add deterministic JVM tests proving pending commands are untouched by reads, initial/incremental cursor behavior, exact retry/failure isolation, fresh binding validation and immutable cache reads.
5. Update Android production code-ownership manifest for any new production class.
6. Run exact branch CI, reconcile canonical product files, open/merge PR only after green exact-head evidence, then require post-merge main CI.

## Recovery protocol

Read this file first. Verify branch `work/m2-m1-008-android-canonical-read` is based on `f6d38ee9398bc473425f33b6fe97fb5fb0ae4b35`. Do not rerun M2-M1-001 through M2-M1-007. Continue at the exact next action above.
