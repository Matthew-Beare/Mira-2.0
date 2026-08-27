# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and its exact resume point.

## Completed packet

### `M2-G0-005B` — Feature Audit Slice D2 — knowledge/spec/shopping/location foundations

- **Merged PR:** #11
- **Merge SHA:** `302023ffc2ed97bd543c7dd8202c87e1aeed8be0`
- **Audited features:** `KNOW-001`, `SPEC-001`, `SHOP-001`, `INV-001`, `LOC-001`
- **Result:** manuals/Knowledge, technical specifications, shopping intent, inventory identity and location semantics are normalized at their actual evidence levels.
- **Live Google production touched:** no.
- **Executable product behavior changed:** no.

## Active packet

- **Packet ID:** `M2-G0-005C`
- **Name:** Feature Audit Slice D3 — inventory movement, query, par and grocery foundations
- **Class:** forensic audit / prerequisite
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Objective:** Audit QR/barcode movement, household/shop inventory query behavior, par-level tracking, optional scale sensing and grocery/pantry/freezer flows without entering recipes/meal planning or implementation work.

## Audit rows in this packet

1. QR/barcode scan-in and scan-out.
2. Queryable household/loft/shop inventory.
3. Consumable/grocery par levels and under-level notification.
4. Optional scale-based par sensing.
5. Grocery list/pantry/freezer flows.

Do not expand this packet to recipes/meal planning/category-D row 16, profiles/onboarding, Android implementation, RFID hardware, Home Assistant implementation or product coding.

## Acceptance criteria

1. Each scoped behavior receives a stable semantic feature ID and evidence boundary.
2. QR/barcode movement depends on `INV-001` canonical Entity UUIDs and `LOC-001` location/event semantics; scanning cannot create a shadow identity or silently redefine intended placement.
3. Queryable household/shop inventory is a projection/query capability over canonical entities/locations, not another editable inventory database.
4. Par-level behavior distinguishes observed quantity, target/par quantity and notification state; under-level alerts are opt-in and replay-safe.
5. Scale sensing remains optional hardware/input evidence and cannot become a universal requirement or sole quantity authority.
6. Grocery/pantry/freezer flows remain separate from durable receipt history and from generic asset inventory where their lifecycle/count semantics differ.
7. Relevant legacy policy/code/tests and materially relevant PR #31 evidence are inspected without committing private household inventory data.
8. Only `FEATURES.md`, `BACKLOG.md`, and `CURRENT_WORK.md` are intended changes.
9. A small PR is scope-verified, merged and remotely read back.
10. `CURRENT_WORK.md` advances to `M2-G0-005D` with exact row-16 recipe/meal-planning resume point.
11. No live Google production state and no executable product behavior is changed.

## Exact next action

Create branch `audit/g0-005c-inventory-movement-par-grocery` from current `main`. Inspect category-D row 11: **QR/barcode scan-in and scan-out**, including identity resolution, location/movement event semantics, idempotency, ambiguity, readback and its dependency on `INV-001`/`LOC-001`.

## Next packet boundary

If D3 completes, `M2-G0-005D` audits category-D row 16 only: recipes, meal planning and shopping linkage, then performs category-D consistency closure. Do not begin category E in D3.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head when tools permit;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture new customer ideas in BACKLOG unless required for acceptance or explicitly reprioritized;
6. before the final packet line, state any customer action needed; if none is needed, use `Just tell me to continue.`;
7. the final visible line remains the packet recovery tag.
