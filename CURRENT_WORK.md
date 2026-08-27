# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and its exact resume point.

## Completed packet before this branch

### `M2-G0-007C` — Feature Audit Slice F3 — shopping and food-service composition

- **Merged PR:** #22
- **Merge SHA:** `f1c1345cdf0e60872df7433771926a26611d3bb1`
- **Main handoff commit activating F4:** `0b8ec443effb758f4c1944863125b64eda21737d`
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
- **Branch:** `audit/g0-007d-household-laundry-services`
- **Branch start SHA:** `0b8ec443effb758f4c1944863125b64eda21737d`
- **Research checkpoint commit:** `ae33bf7068794d5871d2e8795f5f738860246310`
- **Feature registry commit:** `c54f0da1077c6afbf9a2d5d2c0169dcf4bc3e1bd`
- **Backlog checkpoint commit:** `f16e5d58b4f3fd1cd40caba670b45e44affa9ea3`
- **Status:** acceptance complete; bounded PR/merge/readback pending.

## Audited F4 rows

11. **Household/errands/admin/maintenance**.
12. **Laundry stages and drop-off/pickup reminders**.

## Completed acceptance evidence

1. F11 `household_admin` is normalized as a service composition over `TASK-001` + `TASK-002`; no duplicate household task database or identity authority was created.
2. Asset maintenance evidence/history remains optional under `ASSET-002` and `SPEC-001`; the word “maintenance” in the service label does not make those universal household-admin dependencies.
3. `household_admin` and `household_routines` remain independent activation choices under `SERVICE-001`/`SERVICE-002`.
4. Added `ROUTINE-001` for recurring/staged routine definitions and occurrence lifecycle because generic task records do not prove stable routine/occurrence identity, stages, history, skip/reschedule/miss or responsibility semantics.
5. `ROUTINE-001` keeps reusable routine definition separate from each occurrence, preserves historical occurrences across cadence/responsibility edits, and requires supported evidence or explicit action for completion/stage advancement.
6. Added `REMIND-003` for consolidated routine/stage reminder planning and projection; reminder delivery is a separate failure domain from canonical routine truth.
7. `REMIND-003` prohibits one permanent scheduler/automation per chore, stage or occurrence and uses deterministic/replay-safe reminder identity with consolidated notification/brief/optional Calendar projection.
8. Delivery success/failure cannot mark routine stages complete, erase routine occurrences or create a second routine authority. Provider mutation requires exact target readback.
9. Legacy F12→F11 aggregate dependency is normalized to shared `TASK-001`/`TASK-002` behaviors rather than sibling-service activation. `household_routines` may be enabled while `household_admin` remains disabled or unresolved.
10. Legacy `household_routines_enabled` is semantically narrow enough to map only to `household_routines`; no migration-ambiguity ticket was manufactured. It does not authorize `household_admin`, Calendar projection or person responsibility/ownership.
11. Household-manager role, service activation and observed completion cannot infer future responsibility or ownership for one person.
12. The legacy household-routine router regression proves explicit activation, representative washer-to-dryer/pickup examples, consolidated delivery intent and prohibited ownership inference, but does not promote the missing routine lifecycle or household reminder planner/provider adapters to `test_verified`.
13. Legacy appointment-centric `reminder_delivery.py` is not evidence of household/stage reminder implementation merely because both concepts use reminders.
14. Added only the missing F4 work: `AUDIT-F4`, `SERVICE-DEPS-004`, `ROUTINE-CORE-001`, and `ROUTINE-REMINDER-001`; existing task/profile/asset/provider work remains authoritative rather than duplicated.
15. `FEATURES.md` replacement was verified against the research checkpoint: one file only, 71 additions and two intended replacements; F4 text and the new `ROUTINE-*` identity family were remotely inspected.
16. `BACKLOG.md` replacement was verified against the feature commit: one file only, 18 additions and one intended prior-category closure replacement.
17. No live Google production state was touched and no executable MIRA 2.0 product behavior changed.

## Exact next action

Compare `audit/g0-007d-household-laundry-services` against `main` and verify the final packet is limited to `FEATURES.md`, `BACKLOG.md`, and `CURRENT_WORK.md` with the branch zero commits behind. Open a pull request to `main`, verify the server-side changed-file list and mergeability, merge using the exact PR head SHA, remotely read back the F4 feature/backlog state from `main`, then inspect authoritative category-F evidence beginning with F13 **Routines/fitness/accountability** and activate `M2-G0-007E` from the resulting main handoff commit.

## Next packet after F4

### `M2-G0-007E` — Feature Audit Slice F5

Begin with category-F row 13 **Routines/fitness/accountability**. Determine the remainder of the bounded F5 slice from authoritative ledger/dependency evidence only after F4 is merged/read back. Do not pre-expand from conversational memory.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head when tools permit;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture new customer ideas in BACKLOG unless required for acceptance or explicitly reprioritized;
6. before the final packet line, state any customer action needed; if none is needed, use `Just tell me to continue.`;
7. the final visible line remains the packet recovery tag.
