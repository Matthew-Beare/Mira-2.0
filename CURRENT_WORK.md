# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and exact recovery state.

## Product direction

Default Personal MIRA is stock ChatGPT + Google Workspace with no external infrastructure prerequisite. Completed work remains durable with evidence and is filtered from future selection rather than deleted. Current priority is repeated useful no-app verticals before Android resumes.

Every work session begins and ends by checking `CURRENT_WORK.md`, `FEATURES.md`, `BACKLOG.md`, and `ROADMAP.md`.

## Completed predecessor

### `M2-M0-015` — Canonical inventory participation + intended/observed location

PR #67 merged to `main` at `7c2675836d2958d23ac37ad471cae8e14017b894` after exact-head CI `33329282677` passed and isolated Google proof verified same-UUID asset/inventory participation plus independent intended-home and observed-location revisions. Two later accidental placeholder add/delete commits left zero file differences from that verified merge tree; current branch base `2da3128cdecad86b45c776f31ccb63e5be5aadc0` is therefore content-identical to the verified PR #67 merge plus no-op history. `LOCATION-STATE-001` must be reconciled completed in `BACKLOG.md` in this packet.

## Active packet

### `M2-M0-016` — Replay-safe inventory movement / observation history

- **Primary work:** `MOVEMENT-CORE-001`
- **Primary features:** `MOVE-001`, movement slice of `LOC-001`
- **Related invariants/features:** `INV-001`, `IDENT-001`, `ASSET-001`, `ASSET-003`, `INV-002`, `LOCATION-STATE-001`, `STORE-001`, `RECOVERY-002`, `CLIENT-ANDROID-001`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `integration/m0-016-inventory-movement`
- **Base SHA:** `2da3128cdecad86b45c776f31ccb63e5be5aadc0`
- **Objective:** record immutable replay-safe movement/observation history for already-tracked canonical assets, resolve assets exactly by Entity UUID or an unambiguous canonical identifier, and reconcile latest observed location without ever rewriting intended-home placement. This packet does not implement camera/barcode/QR capture UI, Android, broad inventory search, par/grocery, fitment, OCR, or legacy migration.

## Session-start alignment verification — 2026-08-30

### `FEATURES.md`

Verified from current `main` before implementation:

- `MOVE-001` requires QR/barcode-driven inventory movement with explicit event/readback semantics and depends on canonical `INV-001`, `IDENT-001`, and `LOC-001` state;
- scanning is an input path over canonical identity/location/movement authorities, not a second identity system;
- `LOC-001` requires intended placement to remain independent from observed/current/last-moved state;
- `INV-001` requires the physical Entity UUID to survive inventory/location/movement changes;
- `IDENT-001` product identifiers may resolve multiple assets, so movement may not guess when identifier lookup is ambiguous.

The historical D3 audit was re-read. It explicitly rejects the old single-field relocation model and requires replay-safe movement/observation events with exact identifier/location resolution, scan-in/out semantics, target readback, and no silent intended-placement rewrite.

### `BACKLOG.md`

Verified from current `main`:

- `LOCATION-STATE-001` is merged by PR #67 and must be reconciled completed;
- `MOVEMENT-CORE-001` is a PREREQUISITE whose `LOCATION-STATE-001` dependency is now satisfied;
- `INVENTORY-QUERY-001` is HARDENING and remains downstream;
- scanner/Android capture remains separate under Android/client work rather than being required for the no-app movement core.

### `ROADMAP.md`

Verified from current `main`:

- M2-M0.5 continues useful assets/inventory/location capability in stock ChatGPT before Android resumes;
- bounded no-app packets must continue adding real capability without importing the entire scanner/client stack;
- Android remains paused at its stronger shared-writer checkpoint.

### Direction result

**ALIGNED.** `MOVEMENT-CORE-001` is the highest-leverage newly unblocked prerequisite. It creates durable history and safe current-observation reconciliation now, while future barcode/QR/Android capture can feed the same canonical movement contract later.

## Required user-visible/canonical behavior

1. A user can record that a tracked asset was observed at or moved to one exact canonical location.
2. The asset may be selected by exact Entity UUID or by an identifier that resolves to exactly one canonical asset; zero or multiple identifier matches fail closed.
3. Every accepted movement/observation becomes immutable ordered history on the asset's inventory stream.
4. A movement/observation updates latest observed location/time but never changes intended-home placement.
5. Replaying the same logical movement performs no duplicate event and converges the latest-observed projection to the event if a prior crash occurred between history append and projection update.
6. `scan_in` can record arrival at an exact destination using the same movement core; actual barcode/QR camera capture is outside this packet.
7. `scan_out` can record departure from the current/exact source and make current observed location unknown without erasing the immutable history or intended home.
8. Explicit source/from-location claims must match canonical current state when the action requires them; MIRA never invents a source location.
9. Event occurrence time is offset-aware and distinct from provider persistence time.
10. Movement history preserves asset UUID, acquisition provenance, identifiers, quantity/tracking mode and intended placement.

## Acceptance criteria

1. Provider-neutral movement service over existing `STORE-001` event streams plus `InventoryLocationService` projection state.
2. Canonical stream is `inventory_state/<Entity UUID>`; event history does not create another asset/inventory identity.
3. Movement event type is explicitly allowed by the Personal starter event schema and is immutable/ordered by stream revision.
4. Deterministic event identity derives from canonical Entity UUID plus stable logical movement idempotency material; exact replay is zero-event-write.
5. Exact Entity UUID resolution and unambiguous canonical identifier resolution are supported; missing/ambiguous identifiers fail closed.
6. Actions support bounded `observed`, `moved`, `scan_in`, and `scan_out` semantics without implementing capture hardware/UI.
7. `observed`, `moved`, and `scan_in` require an exact destination location and update latest observed state/time only.
8. `scan_out` requires/validates an exact current source and clears current observed state while retaining the event history and intended placement.
9. Offset-aware occurrence timestamps are required; future/provider write time is not substituted for event time.
10. Crash/replay recovery: if the immutable event exists but observed-state projection was not completed, replay repairs projection from canonical event history rather than appending a duplicate event.
11. Direct tests cover success, replay, crash-repair, stream ordering, stale/ambiguous resolution, source mismatch, scan-out, intended-home preservation and asset/identifier side-effect isolation.
12. Personal starter/no-app contract adds the movement event type and movement semantics without adding a scanner/Android prerequisite.
13. Distribution/Workspace validation and code ownership cover the movement contract.
14. Exact PR-head CI green.
15. Fresh isolated Google proof persists at least two ordered movement events and exact resulting inventory-state readback while intended placement remains unchanged; replay/readback is verified.
16. End-of-session FEATURES/BACKLOG/ROADMAP reconciliation preserves broad inventory query, par/grocery, fitment, OCR, scanner UI and Android work as unfinished.

## Exact next action

1. Reconcile `LOCATION-STATE-001` completed and mark `MOVEMENT-CORE-001` active in `BACKLOG.md`.
2. Implement the provider-neutral movement event/reconciliation service and direct tests using the existing STORE event stream rather than a parallel movement database.
3. Extend Personal starter/no-app contract/release validation/ownership for the movement event type.
4. Open a bounded PR, run CI, fix evidence-backed failures, then perform a fresh isolated Google movement/provider readback proof only after CI is green.
5. Freeze closeout, run exact-head CI, merge only when green, remotely verify `main`, then select exactly one next bounded packet.

## Recovery protocol

Read this file first. Continue only on `integration/m0-016-inventory-movement` from base `2da3128cdecad86b45c776f31ccb63e5be5aadc0`. Do not broaden into camera/barcode/QR capture UI, Android, broad inventory query/projection, par/grocery, fitment, OCR/photo evidence or legacy migration while this packet is unfinished.