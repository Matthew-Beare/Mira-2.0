# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and its exact resume point.

## Active packet

- **Packet ID:** `M2-G0-005C`
- **Name:** Feature Audit Slice D3 — inventory movement, query, par and grocery foundations
- **Class:** forensic audit / prerequisite
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `audit/g0-005c-inventory-movement-par-grocery`
- **Base main SHA:** `d90cc482f12573e9d4eb0b9c9bc5a59336843119`
- **Feature audit commit:** `45f0208a34acf8a9bb56777b21b55f27ee30750d`
- **Backlog checkpoint commit:** `b3c4aa85fd836c403a685617b87ed3120f5503ce`
- **Status:** acceptance work complete; PR/merge/readback pending.

## Completed acceptance evidence

1. Assigned five stable semantic features for category-D rows 11-15:
   - `MOVE-001` QR/barcode-driven inventory movement with explicit event/readback semantics;
   - `INV-002` Queryable household, loft and shop inventory projection;
   - `PAR-001` Target/par quantity with opt-in under-level notification;
   - `PAR-002` Optional scale-based passive stock sensing;
   - `GROCERY-001` Grocery list, pantry and freezer stock reconciliation.
2. Added dedicated `MOVE-*`, `PAR-*` and `GROCERY-*` feature families rather than overloading generic inventory identity.
3. Preserved `MOVE-001` as dependent on `INV-001`, `IDENT-001`, `LOC-001` and the queued `LOCATION-STATE-001` repair. Scanning resolves existing canonical identities and cannot become a second identity authority.
4. Inspected PR #31 smart-capture/Android/service evidence: barcode/location code resolution, Android camera/ML Kit hooks, relocation command, audit/readback and smart-capture contract tests are real unmerged implementation/test candidates.
5. Identified the PR #31 relocation defect explicitly: it overwrites one `assets.location_uuid`, collapsing intended home and observed/moved-to location. The candidate therefore cannot satisfy MIRA 2.0 `MOVE-001` as-is.
6. Added `MOVEMENT-CORE-001` to salvage/redesign movement as replay-safe events/observations with exact resolution, scan-in/out semantics and target readback after `LOCATION-STATE-001`.
7. Recorded `INV-002` as a read/query projection over canonical Entity UUIDs, identifiers, relationships and location state, never a second editable inventory database.
8. Inspected PR #31 inventory query/hierarchy endpoints and `test_full_inventory_ui.py` as unmerged candidate evidence only; added `INVENTORY-QUERY-001` for MIRA 2.0 canonical query proof.
9. Recorded `PAR-001` observed stock quantity separately from target/par quantity, with opt-in replay-safe consolidated under-level state. No dedicated implementation/tests were located; added `PAR-CORE-001`.
10. Preserved `PAR-002` as optional/proposed. Repository/PR #31 search found no scale/load-cell inventory implementation; added deferred `PAR-SCALE-001` rather than making hardware a requirement.
11. Recorded `GROCERY-001` as practical consumable stock and grocery-procurement reconciliation distinct from receipt history and serialized durable-asset treatment. No dedicated executable grocery/pantry/freezer core was located; added `GROCERY-CORE-001`.
12. Searched the legacy repository/PR #31 for par, reorder threshold, pantry, freezer, grocery, scale and weight-sensor implementation evidence and found none sufficient to raise those evidence ceilings.
13. Touched no live Google production state and changed no executable product behavior.

## Key audit findings

- QR/barcode scanning is an input workflow over identity/location/movement authorities, not an identity system.
- PR #31 contains useful scanner/query code worth salvaging later, but its one-field relocation model is incompatible with the required intended-versus-observed location semantics.
- Inventory query is a projection; mutation authority remains canonical MIRROR entity/location/event state.
- Target stock, observed stock and alert state are separate facts.
- Scale sensing remains optional evidence and cannot become a dependency for ordinary MIRA inventory.
- Grocery stock/list behavior has distinct quantity/lifecycle semantics while still linking to `SHOP-001`, `RECEIPT-001`, `LOC-001` and optional `PAR-001`.

## Blockers

None inside this forensic packet. `MOVEMENT-CORE-001`, `INVENTORY-QUERY-001`, `PAR-CORE-001`, `PAR-SCALE-001` and `GROCERY-CORE-001` are separately ranked implementation work.

## Exact next action

Open a pull request from `audit/g0-005c-inventory-movement-par-grocery` to `main`, verify changed-file scope is limited to `FEATURES.md`, `BACKLOG.md`, and `CURRENT_WORK.md`, merge it, remotely read back the merged D3 state, then activate `M2-G0-005D` on current `main` and create its audit branch.

## Next packet after merge

### `M2-G0-005D` — Feature Audit Slice D4 — recipes, meal planning and category-D closure

Audit category-D row 16 only:

1. Recipe knowledge/library behavior.
2. Meal planning using available pantry/freezer/grocery state.
3. Missing-ingredient linkage to grocery/shopping intent.
4. Category-D consistency pass and closure.

Do not begin category E, profile/onboarding work, Android implementation, grocery implementation, recipe UI implementation or Home Assistant/fridge work in this packet.

The exact first unaudited behavior is **Recipes and meal planning linked to grocery/pantry/shopping state**.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head when tools permit;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture new customer ideas in BACKLOG unless required for acceptance or explicitly reprioritized;
6. before the final packet line, state any customer action needed; if none is needed, use `Just tell me to continue.`;
7. the final visible line remains the packet recovery tag.
