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
- **Research checkpoint commit:** `9e0172ccd34e19c0b63a8e45b9e662d9a8b5f4a7`
- **Feature registry commit:** `953cfe0b2f98a9f4b919998d5def81662c773587`
- **Backlog checkpoint commit:** `6d197a4d6d898f5d7d2a4234455cc8ab19c6ba5a`
- **Status:** acceptance complete; bounded PR/merge/readback pending.

## Audited F3 rows

9. **Shopping/procurement**.
10. **Recipes/meals/groceries**.

## Completed acceptance evidence

1. F9 `shopping` is normalized as a service composition over canonical `SHOP-001`; no duplicate shopping domain feature was created.
2. The narrow legacy `f-09` → D8 mapping is structurally sound. Receipt/order/fitment/provider dependencies remain owned by `SHOP-001` rather than being duplicated into the service wrapper.
3. Shopping remains active procurement intent only and cannot become purchase history, shipment state, spending authority, inventory ownership or automatic purchasing authority.
4. F10 `recipes_meals` is normalized as a selected-submodule umbrella under `SERVICE-001`/`SERVICE-002`, not one all-or-nothing food switch.
5. Recipe-library-only readiness requires `RECIPE-001` and is not blocked by absent meal/grocery capabilities.
6. Pantry-aware meal-planning readiness requires `MEAL-001` + `RECIPE-001` + `GROCERY-001`; shopping reconciliation is inherited through canonical child behavior rather than duplicated as a second purchase authority.
7. Historical D16 remains split into `RECIPE-001` and `MEAL-001`; reusable recipe knowledge and dated meal-plan state are not re-collapsed at the service layer.
8. Planning remains unable to fabricate stock consumption, purchase evidence or shopping fulfillment. Missing-ingredient shopping intent continues through canonical `SHOP-001` rules.
9. Legacy `recipe_library_enabled` is compatibility evidence for recipe-library intent only. It cannot silently authorize meal planning, pantry/grocery tracking, shopping linkage or stock/purchase mutation; broader historical intent remains unresolved until explicitly selected.
10. No new shopping/grocery/recipe/meal implementation tasks were created. Existing `SHOP-CORE-001`, `GROCERY-CORE-001`, `RECIPE-CORE-001`, and `MEAL-CORE-001` remain authoritative domain gaps.
11. Added `AUDIT-F3` and `SERVICE-DEPS-003`; refined `SERVICE-MIGRATION-001` to include recipe-library compatibility semantics.
12. `FEATURES.md` replacement was verified against the research checkpoint: one file only, 32 additions and one stale audit-status deletion; no earlier registry content changed.
13. `BACKLOG.md` replacement was verified against the feature commit: one file only, 14 additions and two intended replacement lines; no unrelated backlog content changed.
14. Service wrappers remain bounded by their weakest selected required child. Catalog/router exposure and compatibility booleans do not create implementation, integration or live evidence.
15. No live Google production state was touched and no executable MIRA 2.0 product behavior changed.

## Exact next action

Compare `audit/g0-007c-shopping-food-services` against `main` and verify the final packet is limited to `FEATURES.md`, `BACKLOG.md`, and `CURRENT_WORK.md` with the branch zero commits behind. Open a pull request to `main`, verify the server-side changed-file list and mergeability, merge using the exact PR head SHA, remotely read back the F3 feature/backlog state from `main`, then inspect authoritative category-F evidence beginning with F11 **Household/errands/admin/maintenance** and activate `M2-G0-007D` from the resulting main handoff commit.

## Next packet after F3

### `M2-G0-007D` — Feature Audit Slice F4

Begin with category-F row 11 **Household/errands/admin/maintenance**. Determine the remainder of the bounded F4 slice from authoritative ledger/dependency evidence only after F3 is merged/read back. Do not pre-expand from conversational memory.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head when tools permit;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture new customer ideas in BACKLOG unless required for acceptance or explicitly reprioritized;
6. before the final packet line, state any customer action needed; if none is needed, use `Just tell me to continue.`;
7. the final visible line remains the packet recovery tag.
