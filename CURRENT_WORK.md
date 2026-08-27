# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and its exact resume point.

## Completed packet before this branch

### `M2-G0-007C` — Feature Audit Slice F3 — shopping and food-service composition

- **Merged PR:** #22
- **Merge SHA:** `f1c1345cdf0e60872df7433771926a26611d3bb1`
- **Audited rows:** F9-F10 — Shopping/procurement; Recipes/meals/groceries.
- **Result:** `shopping` maps to `SHOP-001`; `recipes_meals` uses selected recipe-library versus pantry-aware meal-planning submodules over `RECIPE-001`, `MEAL-001`, and `GROCERY-001`; legacy `recipe_library_enabled` cannot silently enable the whole food stack.
- **Remote readback:** F3 `FEATURES.md` and `BACKLOG.md` were verified on `main` after merge.
- **Live Google production touched:** no.
- **Executable product behavior changed:** no.

## Active packet

- **Packet ID:** `M2-G0-007D`
- **Name:** Feature Audit Slice F4 — household administration and laundry routines
- **Class:** forensic audit / prerequisite
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Planned branch:** `audit/g0-007d-household-laundry-services`
- **Base merge SHA:** `f1c1345cdf0e60872df7433771926a26611d3bb1`
- **Status:** packet activated; branch creation and forensic evidence pass next.

## Exact category-F scope in this packet

Audit exactly legacy category-F rows 11-12:

11. **Household/errands/admin/maintenance** — CURRENT REQUIRED direction; generic task system plus machine-readable household-routine service/onboarding contract; live reminder projection capability-gated.
12. **Laundry stages and drop-off/pickup reminders** — CURRENT REQUIRED; machine-readable router/reminder contract with tests; live brief/Calendar/notification delivery requires provider capability and readback.

Do not expand this packet into F13 Routines/fitness/accountability, F14 Education/study/deadlines/offline road preparation, family-school, travel, later category-F rows, category G, or executable MIRA 2.0 coding.

## Handoff evidence used to bound F4

1. The authoritative forensic ledger places F11 Household/errands/admin/maintenance and F12 Laundry stages/drop-off/pickup reminders together before F13 Routines/fitness/accountability.
2. Legacy dependency map establishes a direct chain:
   - `f-11` uses task-state and requires A13/A14, now `TASK-001` + `TASK-002`;
   - `f-12` requires `f-11` and adds scheduler-delivery, notification-delivery and optional Calendar projection capabilities.
3. The deterministic onboarding router exposes separate `household_admin` and `household_routines` service activation keys. Household-manager role may recommend them, but recommendation never enables either service.
4. The router's household-routine reminder contract explicitly includes laundry-stage and drop-off/pickup examples, requires explicit user confirmation, uses canonical routine/task state, consolidates delivery through brief or Calendar projection rather than one automation per chore, and prohibits ownership inference.
5. Dedicated router tests prove household-routine activation is explicit, include `washer_to_dryer` and `dry_cleaning_or_repair_pickup`, require consolidated delivery, and prohibit ownership inference.
6. F13 changes dependency shape to generic routines/fitness with optional wearable input and no F11/F12 dependency; F14 changes again to education plus task/evidence/optional Calendar concerns. They therefore start later audit slices rather than expanding F4.

## Acceptance criteria

1. Account for F11-F12 with stable semantic mappings and create new feature IDs only where staged routine/delivery behavior is genuinely distinct from `TASK-001`/`TASK-002` and existing scheduler/Calendar features.
2. Reuse `SERVICE-001`/`SERVICE-002` for activation/readiness; household-manager role recommendations remain separate from activation and permissions.
3. Preserve `household_admin` and `household_routines` as separate service choices unless evidence proves one must subsume the other.
4. Determine whether generic household admin is fully represented by `TASK-001` + `TASK-002` or needs an additional canonical household-domain feature.
5. Determine whether staged/repeating household routines and laundry transitions require a distinct canonical routine feature beyond generic tasks.
6. Preserve no-per-chore scheduler fan-out: delivery should consolidate through the control cycle, notification delivery and optional Calendar projection rather than creating one permanent automation per chore/stage.
7. Preserve explicit responsibility/ownership boundaries; household-manager or household-routine activation cannot infer that one person owns every chore/item.
8. Record provider/readback boundaries separately from deterministic routing/reminder-contract evidence.
9. Reconcile relevant PR #31 evidence only as unmerged/reference evidence unless deterministic merged legacy evidence independently supports a higher level.
10. Update only `FEATURES.md`, `BACKLOG.md`, and `CURRENT_WORK.md`.
11. Open a bounded PR, verify scope, merge and remotely read back before advancing to the next category-F slice.
12. Touch no legacy Google production state and change no executable MIRA 2.0 product behavior.

## Exact next action

Create branch `audit/g0-007d-household-laundry-services` from this handoff commit. Audit F11 against `TASK-001`, `TASK-002`, `PROFILE-007`, the legacy `f-11` dependency map, service router/catalog and any household-admin/routine evidence. Then audit F12 staged laundry/drop-off/pickup semantics and delivery/readback boundaries before deciding whether a new canonical routine feature is warranted.

## Next packet after F4

### `M2-G0-007E` — Feature Audit Slice F5

Begin with category-F row 13 **Routines/fitness/accountability** and determine the rest of the bounded F5 slice from authoritative ledger/dependency evidence after F4 closes.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head when tools permit;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture new customer ideas in BACKLOG unless required for acceptance or explicitly reprioritized;
6. before the final packet line, state any customer action needed; if none is needed, use `Just tell me to continue.`;
7. the final visible line remains the packet recovery tag.
