# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and exact recovery state.

## Product direction

Default Personal MIRA is stock ChatGPT + Google Workspace with no external infrastructure prerequisite. Completed work remains durable with evidence and is filtered from future selection rather than deleted. Current priority is repeated useful no-app verticals before Android resumes.

Every work session begins and ends by checking `CURRENT_WORK.md`, `FEATURES.md`, `BACKLOG.md`, and `ROADMAP.md`.

## Completed predecessor

### `M2-M0-014` — Namespaced asset identifiers + lookup

PR #66 merged to `main` at `6833d27e20d746d37e389b1756a6f6147225d043` after exact-head CI `33300160170` passed and isolated Google identifier persistence, observed-to-verified revision, leading-zero UPC and identifier-to-canonical-asset readback were verified. `ASSET-IDENTIFIER-001` must be reconciled completed in `BACKLOG.md` in this packet.

## Active packet

### `M2-M0-015` — Canonical inventory participation + intended/observed location

- **Primary work:** `LOCATION-STATE-001`
- **Primary features:** `INV-001`, `LOC-001`
- **Related invariants/features:** `ASSET-001`, `IDENT-001`, `ASSET-003`, `MOVE-001`, `INV-002`, `PAR-001`, `GROCERY-001`, `STORE-001`, `RECOVERY-002`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `integration/m0-015-inventory-location`
- **Base SHA:** `6833d27e20d746d37e389b1756a6f6147225d043`
- **Objective:** expose an existing immutable asset Entity UUID as tracked inventory, model stable hierarchical physical locations, and persist intended-home placement separately from latest supported observed location. This packet does not implement movement-event history, QR/barcode scan-in/out, broad inventory search/projection, par levels, groceries, fitment, OCR or Android capture.

## Session-start alignment verification — 2026-08-30

### `FEATURES.md`

Rechecked from verified `main` before implementation:

- `INV-001` says inventory is a state/projection over canonical physical entities; the asset Entity UUID remains the primary physical identity and category/location/presentation changes may never renumber it;
- friendly inventory IDs, QR/shelf labels, serials and vendor codes are identifiers/aliases rather than a second physical-item identity;
- `LOC-001` requires stable hierarchical physical locations with explicit parent relationships and cycle protection;
- intended/canonical home placement and latest supported observed/current location are distinct facts;
- changing observed location must not silently rewrite intended placement, and changing intended placement must not fabricate a physical observation/move;
- containers may later expose child locations and movement-following semantics, but movement-event behavior belongs to `MOVE-001` and is not required to establish the base intended/observed state model.

Historical audit PR #11 was re-read. It explicitly rejects the old one-field location design, requires the same Entity UUID through asset and inventory views, and records hierarchy/cycle/container mechanics only as salvage/reference evidence rather than MIRA 2.0 implementation proof.

### `BACKLOG.md`

Rechecked from verified `main`:

- `ASSET-IDENTIFIER-001` is merged and must be reconciled completed with PR #66 evidence;
- `LOCATION-STATE-001` is the existing prerequisite work item for intended-versus-observed hierarchical location state;
- `MOVEMENT-CORE-001` depends on `LOCATION-STATE-001` and remains queued;
- `INVENTORY-QUERY-001` also depends on `LOCATION-STATE-001` and remains queued;
- there is no separate implementation work item for `INV-001`; its minimal no-second-identity participation rule is therefore a hard prerequisite inside this bounded location packet rather than a new parallel subsystem.

### `ROADMAP.md`

Rechecked from verified `main`:

- M2-M0.5 explicitly continues receipts/assets/inventory and other useful no-app families before Android;
- packets must remain bounded and should repeatedly add real user-visible capability;
- Android remains paused at its stronger shared-writer checkpoint;
- location state is a prerequisite for later movement/scanning and queryable inventory, so implementing it now unlocks those downstream slices without requiring external infrastructure.

### Direction result

**ALIGNED.** A combined minimal inventory-participation + intended/observed location slice is the smallest useful implementation of the existing `LOCATION-STATE-001` prerequisite. A location-only graph would not answer where an actual asset belongs, while a participation-only projection would be invisible plumbing. Movement events and broad inventory queries remain separate packets.

## Required user-visible/canonical behavior

1. An inventory-participating item reuses an existing canonical asset Entity UUID exactly; no second physical/inventory UUID is allocated.
2. Stable `location` resources can represent site/building/room/zone/aisle/shelf/bin/container-like places with optional parent location.
3. A location cannot parent itself or create an ancestor cycle.
4. Renaming/reparenting a location preserves its stable location ID.
5. Each tracked asset may independently store an intended-home location and a latest observed location.
6. Setting/changing intended placement does not change observed location or fabricate `observed_at` evidence.
7. Setting/changing observed location requires an offset-aware observation timestamp and does not alter intended placement.
8. Clearing observed state does not clear intended placement; clearing intended placement does not erase observation history/current observation.
9. Both intended and observed location references must resolve to canonical location resources.
10. Asset UUID, acquisition provenance, identifiers, tracking mode and quantity remain untouched by inventory/location mutations.
11. No movement event, QR/barcode scan, fitment, par, grocery, warranty or Android action is implied by location state.

## Acceptance criteria

1. Provider-neutral inventory/location service over `STORE-001` with create/read/update location plus track/read/set-intended/set-observed semantics.
2. `inventory_state` Resource ID equals the canonical asset Entity UUID and payload `entity_uuid` exactly.
3. Tracking an unknown asset fails closed; tracking an existing asset never allocates a second physical identity.
4. Stable location Resource IDs with nonblank display name, optional parent, bounded kind and optional note.
5. Parent existence plus self/cycle prevention on create and reparent.
6. Intended and observed state are separate fields/revisions; mutation of one preserves the other.
7. Observed location requires an offset-aware ISO-8601 timestamp; intended location has no fabricated observation timestamp.
8. Referenced locations must exist; stale/missing/corrupt references fail closed.
9. Direct tests prove identity reuse, hierarchy/cycle rules, independent intended/observed mutations, clearing behavior and no downstream side effects.
10. Personal starter adds `location` and `inventory_state` plus bindings without replacing the existing asset/identifier authorities.
11. Complete no-app instructions define inventory identity reuse and intended-versus-observed location truth, while keeping movement/scanning separate.
12. Distribution/Workspace validation and code ownership cover the new contract.
13. Exact PR-head CI green.
14. Fresh isolated Google proof persists one canonical asset, one hierarchy, one inventory-state resource, intended placement and a different observed location with exact readback showing neither overwrites the other.
15. End-of-session FEATURES/BACKLOG/ROADMAP reconciliation preserves movement/scanning, broad inventory query, par/grocery, fitment, OCR and Android work.

## Exact next action

1. Reconcile `ASSET-IDENTIFIER-001` completed in `BACKLOG.md` and mark `LOCATION-STATE-001` active for this packet.
2. Implement provider-neutral inventory/location state and direct tests.
3. Extend Personal starter/no-app contract/release validation/ownership for `location` and `inventory_state`.
4. Run CI and fix evidence-backed failures.
5. Perform a fresh isolated Google intended-versus-observed provider readback proof.
6. Freeze closeout, run exact-head CI, merge only when green, remotely verify `main`, then select exactly one next bounded packet.

## Recovery protocol

Read this file first. Continue only on `integration/m0-015-inventory-location` from base `6833d27e20d746d37e389b1756a6f6147225d043`. Do not broaden into movement-event history, QR/barcode scanning, broad inventory query/projection, par/grocery, fitment, OCR/photo evidence or Android while this packet is unfinished.
