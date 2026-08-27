# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and its exact resume point.

## Completed packet before this branch

### `M2-G0-007B` — Feature Audit Slice F2 — finance, appointment/calendar, and administrative-health services

- **Merged PR:** #21
- **Merge SHA:** `e6890dea352f40c5205d1e21f94dada5b5752b50`
- **Audited rows:** F6-F8 — Personal finance organization; Appointments/calendar/reminders; Administrative health organization.
- **Result:** finance is goal-scoped; appointment/provider identity (`CAL-005`) and Calendar projection/readback (`CAL-006`) are separate; administrative health (`HEALTH-001`) is non-clinical and separate from medication reminders/caregiver sharing.
- **Remote readback:** `FEATURES.md` and `BACKLOG.md` on `main` contain the F2 registry and ranked work.
- **Live Google production touched:** no.
- **Executable product behavior changed:** no.

## Active packet

- **Packet ID:** `M2-G0-007C`
- **Name:** Feature Audit Slice F3 — shopping and food-service composition
- **Class:** forensic audit / prerequisite
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Planned branch:** `audit/g0-007c-shopping-food-services`
- **Base merge SHA:** `e6890dea352f40c5205d1e21f94dada5b5752b50`
- **Status:** packet activated; branch creation and forensic evidence pass next.

## Exact category-F scope in this packet

Audit exactly legacy category-F rows 9-10:

9. **Shopping/procurement** — ACCEPTED direction; service composition over active shopping intent and purchase reconciliation.
10. **Recipes/meals/groceries** — CURRENT REQUIRED; service composition over grocery stock/list state, recipe knowledge and meal-plan state.

Do not expand this packet into F11 Household/errands/admin/maintenance, F12 Laundry stages/drop-off/pickup reminders, routines/fitness, education, family-school, travel, later category-F rows, category G, or executable MIRA 2.0 coding.

## Handoff evidence used to bound F3

1. Authoritative forensic ledger places F9 Shopping/procurement and F10 Recipes/meals/groceries immediately after F2 and before household/routine services.
2. Legacy dependency map is narrow and coherent:
   - `f-09` requires `d-08` Shopping/procurement intent;
   - `f-10` requires `d-15` Grocery/pantry/freezer state and `d-16` historical Recipes/meal-planning row.
3. Category D already normalized those behaviors into `SHOP-001`, `GROCERY-001`, `RECIPE-001`, and `MEAL-001`; F3 should therefore audit service composition/readiness without duplicating domain features unless a distinct service-layer behavior is genuinely missing.
4. Historical D16 was split into `RECIPE-001` and `MEAL-001` because reusable recipe knowledge and dated meal-plan state have different lifecycle semantics. The legacy F10 dependency map must be reconciled to both canonical features rather than treating D16 as one undifferentiated child.
5. F11-F12 shift to task/routine/scheduler/notification semantics: `f-11` requires A13/A14 and task state; `f-12` depends on `f-11` plus scheduler/notification and optional Calendar projection. They are therefore a separate packet boundary rather than being dragged into shopping/food.

## Acceptance criteria

1. Account for F9-F10 with stable canonical service mappings and create no duplicate shopping/grocery/recipe/meal features.
2. Reuse `SERVICE-001`/`SERVICE-002` activation/readiness machinery.
3. Preserve `SHOP-001` active procurement intent as separate from receipts/orders/spending/inventory.
4. Preserve `GROCERY-001`, `RECIPE-001`, and `MEAL-001` as separate authorities/lifecycles; planning cannot fabricate purchase, stock consumption or fulfillment.
5. Reconcile the historical F10 single D16 dependency to the canonical `RECIPE-001` + `MEAL-001` split and record any other semantic dependency defects.
6. Record actual evidence ceilings and do not promote service wrappers above their weakest selected required child.
7. Reconcile relevant service catalog/router/test/PR #31 evidence only where it materially changes the evidence boundary.
8. Update only `FEATURES.md`, `BACKLOG.md`, and `CURRENT_WORK.md` unless a hard audit dependency requires another authority-file change.
9. Open a bounded PR, verify scope, merge and remotely read back before advancing to F4.
10. Touch no legacy Google production state and change no executable MIRA 2.0 product behavior.

## Exact next action

Create branch `audit/g0-007c-shopping-food-services` from this handoff commit. Audit F9 **Shopping/procurement** first against `SHOP-001`, the legacy `f-09` dependency map, service catalog/onboarding activation semantics and any deterministic reconciliation evidence. Then audit F10 against `GROCERY-001`, `RECIPE-001`, `MEAL-001` and the legacy `f-10` mapping before normalizing service mappings/evidence gaps.

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
