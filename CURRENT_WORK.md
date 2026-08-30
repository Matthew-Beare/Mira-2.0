# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and exact recovery state.

## Product direction

Default Personal MIRA is stock ChatGPT + Google Workspace with no external infrastructure prerequisite. Current priority is repeated useful no-app verticals before Android resumes. Completed work remains durable with evidence and is filtered from future selection rather than deleted.

Every work session begins and ends by checking `CURRENT_WORK.md`, `FEATURES.md`, `BACKLOG.md`, and `ROADMAP.md`.

## Completed predecessor

### `M2-M0-016` — Canonical inventory query projection

PR #70 merged to `main` as `95728763816b2ab26e29973dd2e204d7c4bdbe9c` from exact verified head `793f9f7866f5998509a6a3d3584cee39ed99323e`. Exact-head CI run `33341004699` passed before merge, and `main` push CI run `33341027064` passed on the merge commit. Remote branch readback proved `main` points to that merge.

The packet added the provider-neutral read-only canonical inventory projection, direct zero-write/corruption/filter tests, complete stock-ChatGPT no-app inventory-query instructions and release guards, and fresh isolated Google provider proof using synthetic `NOT A STARTER` state only. The provider proof verified two tracked assets versus one deliberately untracked control, identifier-origin lookup, hierarchical intended-versus-observed location truth and logically identical pre/post query `Resources`, `Events`, and `Idempotency` readback.

PR #69 remains closed unmerged as control-plane evidence only: the connector's ready-for-review GraphQL mutation failed before changing draft state. No implementation was lost; non-draft replacement PR #70 carried the same branch history and merged normally.

`INVENTORY-QUERY-001` must be reconciled to completed in `BACKLOG.md`, and `INV-002` must be reconciled from `candidate_unmerged` to direct merged/test evidence in `FEATURES.md` as part of this packet checkpoint before implementation expands.

## Active packet

### `M2-M0-017` — Replay-safe inventory movement / observation history

- **Primary work:** `MOVEMENT-CORE-001`
- **Primary features:** `MOVE-001`
- **Related invariants/features:** `INV-001`, `LOC-001`, `INV-002`, `IDENT-001`, `ASSET-001`, `STORE-001`, `RECOVERY-002`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `integration/m0-017-movement-core`
- **Base SHA:** `95728763816b2ab26e29973dd2e204d7c4bdbe9c`
- **PR:** not yet opened
- **Objective:** add a provider-neutral replay-safe event history for explicit physical asset observations/movements that deterministically updates canonical observed location while preserving intended placement, stable asset identity, exact observation time, conflict/replay honesty and readback. This packet establishes movement semantics only; barcode/QR capture, Android, passive reads, container-following propagation and stock-count/par/grocery behavior remain separate.

## Session-start alignment verification — 2026-08-30

### `CURRENT_WORK.md`

Verified the merged predecessor before switching scope. M2-M0-016 had no remaining implementation blocker after PR #70 merge, remote `main` readback, exact-head CI and `main` push CI.

### `FEATURES.md`

Verified before implementation:

- `MOVE-001` is accepted required-direction work for explicit inventory movement with event/readback semantics;
- `INV-001` requires physical identity to remain the canonical asset Entity UUID;
- `LOC-001` requires intended placement to stay separate from observed/last-moved state;
- `INV-002` provides the now-merged query projection over canonical inventory truth and must not become a second mutation authority;
- `IDENT-001` supplies identifier resolution for later scan/capture clients, but the movement core itself must not require barcode/QR hardware input.

### `BACKLOG.md`

Verified before implementation:

- `MOVEMENT-CORE-001` is queued as replay-safe movement/observation events and explicitly says never to collapse intended/observed location;
- its listed prerequisites `INV-001`, `IDENT-001`, and `LOCATION-STATE-001` are now satisfied by merged work;
- `INVENTORY-QUERY-001` is stale-text active even though PR #70 has now merged and must be reconciled to completed before this packet grows;
- `ANDROID-CAPTURE-001`, `PAR-CORE-001`, `GROCERY-CORE-001`, fitment and other adjacent work remain separate.

### `ROADMAP.md`

Verified before implementation:

- M2-M0.5 still prioritizes repeated useful stock-ChatGPT + Google Workspace verticals before Android;
- assets/inventory/location/scanning are an accepted family, but the roadmap explicitly requires bounded packets rather than subsystem fan-out;
- Android camera/barcode/QR/NFC/BLE capture follows shared-state foundations and is not required for this provider-neutral movement-event packet.

### Direction result

**ALIGNED.** Event semantics are the next hard prerequisite for trustworthy asset tracking and later scanning. Implementing movement history before scanner/UI adapters prevents a QR read from being mistaken for canonical movement merely because a client observed an identifier.

## Acceptance criteria

1. A movement/observation event references exactly one existing canonical tracked asset by the same immutable Entity UUID; unknown or untracked assets fail closed.
2. The destination/observed location must be an existing canonical location. Event recording never creates a location implicitly.
3. Every event records an explicit offset-aware ISO-8601 `observed_at`; server/model receipt time is not substituted for the physical observation time.
4. Every event has stable event identity and replay material independent from the asset UUID. Exact logical replay produces zero duplicate event and zero extra inventory-state revision.
5. Reusing the same replay/idempotency identity with materially different asset, destination, timestamp, source or note fails closed.
6. Recording a valid event updates only the canonical asset's **observed** location/timestamp state. It must not change `intended_location_id`, asset identity, acquisition provenance, tracking mode, quantity or identifiers.
7. The event captures enough prior-state material to distinguish an observation/move from fabricated history and to support deterministic conflict/readback checks; any claimed prior observed location must match freshly read canonical state.
8. Stale inventory revision or contradictory prior-location expectations fail closed before acknowledging a new movement.
9. A deterministic bounded history query returns canonical movement/observation events for one asset in a defined stable order and never synthesizes missing events from current state.
10. A direct observation to the same location is permitted only as a new explicit observation with a later/distinct supported timestamp and stable new event identity; it is not silently deduped merely because the location is unchanged.
11. Event/history semantics remain provider-neutral and use existing structured-state Resource/Event/Idempotency primitives rather than inventing a second movement database.
12. Partial-write/recovery behavior is explicit: success is not acknowledged unless the persisted movement event and resulting observed inventory state reconcile on exact readback; an interrupted/replayed operation must converge without duplicate movement history.
13. No passive barcode/QR/NFC/BLE read is treated as movement. No scanner, camera, Android UI, label generation or identifier-capture implementation is added in this packet.
14. No container-following movement or descendant propagation is inferred. Moving/observing a container does not silently rewrite contained assets.
15. No intended-location changes, fitment/installation, par/quantity, grocery, warranty/maintenance or OCR/evidence-enrichment behavior is implemented or claimed.
16. Direct tests cover success, exact replay, conflicting replay, stale revision/prior-state conflict, unknown/untracked asset, missing location, same-location re-observation, intended-location preservation, deterministic history order and recovery/zero-duplicate behavior.
17. Complete Personal no-app instructions describe explicit movement/observation semantics and state that identifier recognition alone is not movement; workspace/release validation guards those clauses.
18. `FEATURES.md`, `BACKLOG.md`, `CURRENT_WORK.md`, and code-ownership evidence are reconciled before merge.
19. Required CI is green on the exact merge-candidate head.
20. Fresh isolated Google provider proof uses synthetic state only and demonstrates persisted movement history plus exact observed-state readback/replay behavior without touching protected legacy production artifacts.
21. End-of-session whole-product reconciliation confirms scanning/capture, container propagation, par/grocery, fitment/OCR and Android remain unfinished.

## Exact next action

1. Reconcile `INV-002`/`INVENTORY-QUERY-001` as completed from PR #70 evidence and mark only `MOVEMENT-CORE-001` active in canonical lifecycle state.
2. Inspect existing structured-state event/idempotency primitives and the merged inventory/location service, then choose the smallest recovery-safe movement transaction design compatible with STORE-001.
3. Implement provider-neutral movement/observation event core and direct tests only; do not add scanner/client behavior.
4. Wire the movement honesty contract into complete no-app instructions and release validation.
5. Run CI, then perform fresh isolated Google provider proof only after direct/CI evidence is green.
6. Recheck all four authority files, record exact evidence, open/merge only with exact-head protection, and remotely verify `main`.

## Recovery protocol

Read this file first. Confirm branch `integration/m0-017-movement-core` descends from verified green base `95728763816b2ab26e29973dd2e204d7c4bdbe9c`. Before implementation, finish lifecycle reconciliation for the now-merged M2-M0-016. Do not touch protected legacy MIRA production data. Do not implement barcode/QR/NFC/BLE capture, Android, passive-read movement, container-following propagation, par/grocery, fitment or OCR/evidence enrichment in this packet.