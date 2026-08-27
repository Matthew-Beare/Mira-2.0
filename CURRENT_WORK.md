# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and its exact resume point.

## Completed packet

### `M2-G0-005C` — Feature Audit Slice D3 — inventory movement, query, par and grocery foundations

- **Merged PR:** #12
- **Merge SHA:** `1ed28addd1cb997aea2ead50d88e1b6bfe2833db`
- **Audited features:** `MOVE-001`, `INV-002`, `PAR-001`, `PAR-002`, `GROCERY-001`
- **Result:** movement, inventory query, par-level, optional sensing and grocery-state requirements are separated at their actual evidence levels.
- **Live Google production touched:** no.
- **Executable product behavior changed:** no.

## Active packet

- **Packet ID:** `M2-G0-005D`
- **Name:** Feature Audit Slice D4 — recipes, meal planning and category-D closure
- **Class:** forensic audit / prerequisite
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Objective:** Audit category-D row 16 only, normalize recipe/meal-planning/shopping linkage, perform category-D dependency/evidence consistency closure, and stop before category E.

## Audit scope

1. Recipe knowledge/library behavior.
2. Meal planning using available pantry/freezer/grocery state.
3. Missing-ingredient linkage to grocery/shopping intent.
4. Category-D consistency pass and closure.

Do not begin category E, profile/onboarding work, Android implementation, grocery implementation, recipe UI implementation, Home Assistant/fridge work or product coding.

## Acceptance criteria

1. Row 16 receives stable semantic feature identity/identities with explicit evidence ceilings.
2. Recipe knowledge is separated from per-period meal-plan state where their lifecycle/authority differs.
3. Meal planning may consume `GROCERY-001` availability/stock evidence but does not silently mutate stock merely because a recipe was planned.
4. Missing ingredients may create/reconcile `SHOP-001` grocery intent only through explicit policy and dedupe; the recipe library is not itself a shopping list.
5. Receipt/purchase evidence remains separate from recipes, meal plans, grocery stock and shopping intent.
6. Relevant legacy policy/code/tests and materially relevant PR #31 evidence are inspected; unmerged code receives no MIRA 2.0 implementation credit.
7. Category D1-D4 is checked for identity, location, movement, quantity, grocery, shopping, knowledge and dependency contradictions.
8. Only `FEATURES.md`, `BACKLOG.md`, and `CURRENT_WORK.md` are intended changes.
9. A small PR is scope-verified, merged and remotely read back.
10. Category D is marked complete and `CURRENT_WORK.md` advances to a bounded category-E audit packet without beginning category E implementation.
11. No live Google production state and no executable product behavior is changed.

## Exact next action

Create branch `audit/g0-005d-recipes-close-d` from current `main`. Inspect category-D row 16 and repository/PR #31 evidence for **recipes, meal planning and shopping linkage**, keeping grocery-stock authority under `GROCERY-001` and procurement intent under `SHOP-001`.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head when tools permit;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture new customer ideas in BACKLOG unless required for acceptance or explicitly reprioritized;
6. before the final packet line, state any customer action needed; if none is needed, use `Just tell me to continue.`;
7. the final visible line remains the packet recovery tag.
