# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and its exact resume point.

## Completed packet before this branch

### `M2-G0-007B` — Feature Audit Slice F2 — finance, appointment/calendar, and administrative-health services

- **Merged PR:** #21
- **Merge SHA:** `e6890dea352f40c5205d1e21f94dada5b5752b50`
- **Main handoff commit activating F3:** `8e252c401f110faf0cce3924697745f8e1b29edb`
- **Audited rows:** F6-F8 — Personal finance organization; Appointments/calendar/reminders; Administrative health organization.
- **Result:** finance is goal-scoped; appointment/provider identity (`CAL-005`) and Calendar projection/readback (`CAL-006`) are separate; administrative health (`HEALTH-001`) is non-clinical and separate from medication reminders/caregiver sharing.
- **Remote readback:** F2 `FEATURES.md` and `BACKLOG.md` were verified on `main` before F3 activation.
- **Live Google production touched:** no.
- **Executable product behavior changed:** no.

## Active packet

- **Packet ID:** `M2-G0-007C`
- **Name:** Feature Audit Slice F3 — shopping and food-service composition
- **Class:** forensic audit / prerequisite
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `audit/g0-007c-shopping-food-services`
- **Branch start SHA:** `8e252c401f110faf0cce3924697745f8e1b29edb`
- **Status:** forensic evidence pass complete; feature/backlog normalization next.

## Exact category-F scope in this packet

Audit exactly legacy category-F rows 9-10:

9. **Shopping/procurement** — ACCEPTED direction; service composition over active shopping intent and purchase reconciliation.
10. **Recipes/meals/groceries** — CURRENT REQUIRED; service composition over grocery stock/list state, recipe knowledge and meal-plan state.

Do not expand this packet into F11 Household/errands/admin/maintenance, F12 Laundry stages/drop-off/pickup reminders, routines/fitness, education, family-school, travel, later category-F rows, category G, or executable MIRA 2.0 coding.

## Forensic findings

### F9 — Shopping/procurement

1. Legacy `f-09` requires only D8, which category-D audit normalized as `SHOP-001` active shopping/procurement intent.
2. `SHOP-001` already owns the important commerce boundary: shopping intent is not receipt/purchase history, shipment state, spending authority or asset identity; verified purchase evidence or explicit owner confirmation may fulfill an intent, and ambiguity stays open/reviewable.
3. The module catalog repeats the same semantics: fulfilled shopping rows are removed only after durable purchase/reconciliation evidence is preserved; cancellation without a supported replacement leaves an still-wanted intent open; missing product identity becomes reconciliation work rather than a fake Purchased tombstone.
4. The deterministic service router exposes `shopping` as its own activation state and may recommend it for parent/guardian or household-manager profiles, but recommendation never activates it and implementation remains capability-verification-gated.
5. No new F9 domain feature is warranted. The service wrapper maps to `SHOP-001` under `SERVICE-001`/`SERVICE-002`, and its evidence ceiling remains constrained by `SHOP-001`, whose deterministic reconciliation engine is still queued.
6. No additional semantic defect was found in the narrow legacy `f-09` → D8 mapping itself; downstream purchase/evidence dependencies remain owned by `SHOP-001` rather than duplicated in the service map.

### F10 — Recipes/meals/groceries

7. Legacy `f-10` requires D15 plus historical D16. Category D normalized those into `GROCERY-001`, `RECIPE-001`, and `MEAL-001`, because pantry/grocery stock, reusable recipe knowledge and dated meal-plan state are distinct authorities/lifecycles.
8. The module catalog preserves the same separation: meal planning may reconcile existing recipes/plans, store structured recipe indexes, accepted meal plans and pantry/freezer state, and must keep meal planning, shopping intent and purchase history separate. It also forbids inventing dietary/medical restrictions.
9. `MEAL-001` already carries the critical no-fabrication boundaries: planning may read grocery availability and create deduplicated missing-ingredient shopping intent, but planning alone cannot consume stock, create a purchase or claim shopping fulfillment.
10. The service router exposes one `recipes_meals` activation key and a legacy compatibility field `recipe_library_enabled` mapped directly to that service. Tests prove this compatibility mapping affects activation without claiming implementation.
11. This creates a semantic migration ambiguity: literal historical `recipe_library_enabled` proves only a recipe-library choice, not consent to enable meal planning, grocery/pantry tracking or shopping linkage. Canonical migration must not interpret that old Boolean as authorization for the full food stack.
12. `SERVICE-002` selected-goal/submodule semantics from F2 apply directly here. The `recipes_meals` user-facing umbrella may expose at least recipe-library and meal-planning paths, with readiness/activation intent resolved at the appropriate submodule granularity rather than treating one weak/legacy Boolean as universal consent.
13. Canonical dependency mapping must replace historical D16 with both `RECIPE-001` and `MEAL-001` where the meal-planning path is selected, and include `GROCERY-001` for the current pantry-aware meal-planning contract. A recipe-library-only path requires `RECIPE-001` and must not be blocked by absent `MEAL-001`/`GROCERY-001`.
14. No new F10 domain feature is warranted; implementation gaps already exist as `RECIPE-CORE-001`, `MEAL-CORE-001`, and `GROCERY-CORE-001`.
15. PR #31 did not previously yield a qualifying dedicated recipe/meal/grocery engine during category-D audit; no higher evidence level is inherited here.

## Proposed normalization

- F9 `shopping` → `SHOP-001` under `SERVICE-001` + `SERVICE-002`; no duplicate feature.
- F10 `recipes_meals` remains a user-facing umbrella but uses selected submodule semantics:
  - recipe-library path → `RECIPE-001`;
  - meal-planning path → `MEAL-001` + `RECIPE-001` + `GROCERY-001` under the current pantry-aware contract, with `SHOP-001` dependency inherited through the canonical meal/grocery behavior rather than a duplicate purchase authority.
- Record the historical F10 D16 split explicitly so dependency readiness cannot treat `RECIPE-001` and `MEAL-001` as the same lifecycle.
- Extend `SERVICE-MIGRATION-001` so legacy `recipe_library_enabled` cannot silently enable meal planning/grocery state; unresolved intent requires explicit user choice.
- Add one F3 service-dependency repair work item; reuse existing `SHOP-CORE-001`, `GROCERY-CORE-001`, `RECIPE-CORE-001`, and `MEAL-CORE-001` rather than duplicating implementation tasks.

## Acceptance criteria

1. Account for F9-F10 with stable canonical service mappings and create no duplicate shopping/grocery/recipe/meal features.
2. Reuse `SERVICE-001`/`SERVICE-002` activation/readiness machinery and selected submodule semantics.
3. Preserve `SHOP-001` active procurement intent as separate from receipts/orders/spending/inventory.
4. Preserve `GROCERY-001`, `RECIPE-001`, and `MEAL-001` as separate authorities/lifecycles; planning cannot fabricate purchase, stock consumption or fulfillment.
5. Reconcile historical F10 D16 to `RECIPE-001` + `MEAL-001` and preserve `GROCERY-001` for the current pantry-aware meal-planning path.
6. Treat legacy `recipe_library_enabled` as compatibility evidence for recipe-library intent only; it cannot silently authorize meal/grocery behavior.
7. Record actual evidence ceilings and do not promote service wrappers above their weakest selected required child.
8. Reuse existing category-D implementation gaps; add only service-layer dependency/migration work required by F3.
9. Update only `FEATURES.md`, `BACKLOG.md`, and `CURRENT_WORK.md`.
10. Open a bounded PR, verify scope, merge and remotely read back before advancing to F4.
11. Touch no legacy Google production state and change no executable MIRA 2.0 product behavior.

## Exact next action

Normalize F9-F10 in `FEATURES.md` as service mappings over existing category-D features, including selected recipe-library versus meal-planning submodule semantics and the legacy `recipe_library_enabled` migration ambiguity. Then add the bounded F3 service dependency/migration work to `BACKLOG.md`, close acceptance state here, and run the three-file PR/merge/readback gate.

## Next packet after F3

### `M2-G0-007D` — Feature Audit Slice F4

Begin with category-F row 11 **Household/errands/admin/maintenance** and determine the rest of the bounded F4 slice from authoritative ledger/dependency evidence after F3 closes.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head when tools permit;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture new customer ideas in BACKLOG unless required for acceptance or explicitly reprioritized;
6. before the final packet line, state any customer action needed; if none is needed, use `Just tell me to continue.`;
7. the final visible line remains the packet recovery tag.
