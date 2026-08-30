# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and exact recovery state.

## Product direction

Default Personal MIRA is stock ChatGPT + Google Workspace with no external infrastructure prerequisite. Current priority is repeated useful no-app verticals before Android resumes. Completed work remains durable with evidence and is filtered from future selection rather than deleted.

Every work session begins and ends by checking `CURRENT_WORK.md`, `FEATURES.md`, `BACKLOG.md`, and `ROADMAP.md`.

## Completed predecessor

### `M2-M0-015` — Canonical inventory participation + intended/observed location

PR #67 merged to `main` as `7c2675836d2958d23ac37ad471cae8e14017b894`. Exact PR-head CI run `33329282677` passed on `1296e6bacdcbeab9a905893dbc49742039782de1`. Fresh isolated Google provider proof verified canonical asset-UUID inventory participation, hierarchical locations, and independent intended-versus-observed location state. Current `main` was subsequently verified at `2da3128cdecad86b45c776f31ccb63e5be5aadc0` with CI run `33329434913` green; the intervening placeholder add/remove changed no product state.

`LOCATION-STATE-001` must be reconciled to completed in `BACKLOG.md` in this packet with PR #67 evidence.

## Active packet

### `M2-M0-016` — Canonical inventory query projection

- **Primary work:** `INVENTORY-QUERY-001`
- **Primary features:** `INV-002`
- **Related invariants/features:** `INV-001`, `LOC-001`, `ASSET-001`, `ASSET-003`, `IDENT-001`, `STORE-001`, `RECOVERY-002`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `integration/m0-016-inventory-query`
- **Base SHA:** `2da3128cdecad86b45c776f31ccb63e5be5aadc0`
- **PR:** not yet opened
- **Objective:** provide a deterministic read-only no-app projection over canonical tracked inventory so MIRA can answer what is owned, identify an item by canonical asset identity/name/identifier, and report intended versus latest observed location without creating a second inventory authority or fabricating movement evidence.

## Session-start alignment verification — 2026-08-30

### `FEATURES.md`

Verified before implementation:

- `INV-002` is the canonical queryable household/loft/shop inventory projection;
- it depends on canonical inventory participation/location plus identifier/asset graph truth rather than a shadow inventory table;
- `INV-001` requires the existing asset Entity UUID to remain the physical/inventory identity;
- `LOC-001` requires intended placement to remain distinct from observed/last-supported state;
- `IDENT-001`/`ASSET-003` already provide identifier-origin resolution back to canonical assets.

### `BACKLOG.md`

Verified before implementation:

- `LOCATION-STATE-001` is still textually marked active but PR #67 is now merged and must be reconciled to completed in this packet;
- `INVENTORY-QUERY-001` is queued and its prerequisites are now satisfied by merged receipt/asset/identifier/location work;
- `MOVEMENT-CORE-001` is also newly unblocked, but inventory query provides the shorter immediate no-app user-visible value because it makes the existing canonical inventory state answerable before scanner/event history exists;
- par/grocery, fitment, movement events, OCR/evidence enrichment and Android remain separate unfinished work.

### `ROADMAP.md`

Verified before implementation:

- M2-M0.5 explicitly prioritizes repeated useful stock-ChatGPT + Google Workspace verticals before Android;
- receipts/assets/inventory are an accepted no-app feature family;
- packets must remain bounded and must not collapse inventory query, movement/scanning, par/grocery and Android capture into one subsystem.

### Direction result

**ALIGNED.** A read-only canonical inventory query projection is the smallest next vertical that turns the merged receipt → asset → identifier → inventory/location foundation into directly useful answers without requiring movement/scanner infrastructure.

## Acceptance criteria

1. Query only canonical `inventory_state`; untracked assets are not silently presented as inventory.
2. Every result reuses the canonical asset Entity UUID and resolves the canonical asset record; no second physical/inventory identity exists.
3. Result projection includes stable asset identity/name/tracking mode/quantity and acquisition provenance needed to trace back to the canonical receipt relationship.
4. Result projection includes canonical identifiers for the asset without letting identifier strings replace asset identity.
5. Result projection resolves intended and observed locations independently and preserves the exact canonical `observed_at` truth.
6. Location presentation includes a deterministic root-to-leaf path derived from canonical parent relationships and fails closed on missing/cyclic/corrupt hierarchy.
7. Bounded query supports direct Entity UUID, case-insensitive asset-name substring, exact canonical identifier lookup, intended-location filter, observed-location filter, and deterministic limit/order semantics.
8. Location filtering may explicitly include descendants, but must never infer container-following movement or rewrite item state.
9. Unknown asset/location/identifier filter material and persisted orphan/corrupt references fail closed with domain errors instead of being ignored.
10. Query execution is read-only: zero Resource/Event/Idempotency mutations and no asset/inventory/location/identifier revision changes.
11. No movement-event history, scan-in/out, QR/barcode capture, fitment, par/grocery, warranty/maintenance, OCR/evidence acquisition, or Android behavior is implemented or claimed.
12. Direct tests cover identity, name, identifier and location filters; descendant matching; intended/observed distinction; path rendering; deterministic ordering/limits; corruption failure; and zero-write behavior.
13. Complete Personal no-app operating instructions describe canonical inventory query behavior and its honesty boundaries.
14. Workspace/release validation directly guards the new no-app query contract.
15. `FEATURES.md`, `BACKLOG.md`, `CURRENT_WORK.md`, and code-ownership evidence are reconciled before merge.
16. Required CI is green on the exact merge candidate head.
17. A fresh isolated Google provider proof demonstrates read-only queryability over synthetic canonical receipt/asset/identifier/location/inventory rows without touching protected legacy production state.
18. End-of-session whole-product reconciliation confirms unfinished movement/scanning/container-following/par/grocery/fitment/OCR/Android work remains unfinished.

## Exact next action

1. Implement the bounded provider-neutral read-only inventory query projection over the existing canonical services.
2. Add direct tests for the acceptance criteria without broadening into movement/scanning.
3. Wire the query contract into the complete no-app Personal instructions and release validation.
4. Reconcile `LOCATION-STATE-001` as completed and mark only `INVENTORY-QUERY-001` active in the canonical backlog; update feature/evidence and ownership metadata as warranted by direct evidence.
5. Run CI, fix only packet-relevant failures, and keep the branch green before any adjacent work.
6. Perform a fresh isolated Google provider proof only after direct/CI evidence is green.
7. Recheck all four authority files, record exact evidence, open/merge only with exact-head protection, and remotely verify `main`.

## Recovery protocol

Read this file first. Confirm branch `integration/m0-016-inventory-query` still descends from verified base `2da3128cdecad86b45c776f31ccb63e5be5aadc0`. Do not touch protected legacy MIRA production data. Do not implement movement events, scanning, container-following movement, par/grocery, fitment, OCR/evidence capture or Android as part of this packet.