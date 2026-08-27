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
- **Status:** forensic evidence pass complete; feature/backlog normalization next.

## Exact category-F scope in this packet

Audit exactly legacy category-F rows 11-12:

11. **Household/errands/admin/maintenance** — CURRENT REQUIRED direction; generic task system plus machine-readable household-routine service/onboarding contract; live reminder projection capability-gated.
12. **Laundry stages and drop-off/pickup reminders** — CURRENT REQUIRED; machine-readable router/reminder contract with tests; live brief/Calendar/notification delivery requires provider capability and readback.

Do not expand this packet into F13 Routines/fitness/accountability, F14 Education/study/deadlines/offline road preparation, family-school, travel, later category-F rows, category G, or executable MIRA 2.0 coding.

## Forensic findings

### F11 — Household/errands/admin/maintenance

1. Legacy `f-11` uses task-state and requires A13/A14, already normalized as `TASK-001` structured task hierarchy and `TASK-002` evidence-grounded next actions/completion state.
2. The canonical service router exposes `household_admin` independently from `household_routines`; household-manager, retired, nonworking, parent/guardian and caregiver profiles may recommend household/admin work, but recommendation never activates the service.
3. No distinct household-admin database or identity authority is justified by the audited evidence. General errands, paperwork, household administration and maintenance *actions* can remain task records under `TASK-001`/`TASK-002`.
4. Actual asset maintenance evidence/history remains a separate optional concern under `ASSET-002` (and `SPEC-001` where verified technical specifications matter). Basic `household_admin` readiness must not require asset-maintenance history merely because the service label contains “maintenance.”
5. `PROFILE-007` household-manager is a routing/profile fact, not household task ownership. It cannot assign every chore, purchase or asset to the selected household manager.
6. F11 therefore needs no new domain feature: `household_admin` maps to `TASK-001` + `TASK-002` under `SERVICE-001`/`SERVICE-002`, with optional domain integrations selected separately.

### F12 — Laundry stages and drop-off/pickup reminders

7. Legacy `f-12` requires aggregate `f-11` and adds task-state, scheduler-delivery, notification-delivery and optional Calendar projection profiles. This proves a direct historical dependency chain but must not become a sibling-service activation dependency in MIRA 2.0.
8. The canonical router exposes `household_routines` as a separate activation key. Legacy `household_routines_enabled` maps specifically to that service; it does not map to `household_admin`.
9. The router's household-routine contract requires explicit activation, canonical routine/task state, consolidated brief-or-Calendar delivery rather than one scheduled automation per chore, and prohibits ownership inference. Examples include `laundry_start`, `washer_to_dryer`, `fold_and_put_away`, and `dry_cleaning_or_repair_pickup`.
10. `test_onboarding_profile_router.py::test_household_routines_are_explicit_and_do_not_fan_out_schedulers` directly verifies explicit activation, `washer_to_dryer`, pickup/drop-off example coverage, consolidated delivery and `ownership_inference = prohibited`.
11. That test proves a routing/safety contract only. No durable executable routine lifecycle engine was located that models recurring definitions, occurrences, stages, stage transitions, completion, skip/reschedule or replay/idempotency. Generic `TASK-001`/`TASK-002` do not by themselves prove those semantics.
12. A distinct canonical routine-state feature is therefore required: proposed `ROUTINE-001` — recurring/staged routine definitions and occurrence lifecycle with explicit responsibility, stage/completion evidence, miss/reschedule semantics and replay-safe identity. It should be domain-neutral enough for F13 to reuse later, but F13 is not audited in this packet.
13. Reminder/delivery is a separate failure domain from routine truth. The legacy `reminder_delivery.py` implementation/test suite is appointment-centric; it produces appointment visual/spoken intents and does not implement staged household/laundry reminder planning or provider readback.
14. A second distinct canonical feature is therefore required: proposed `REMIND-003` — consolidated routine/stage reminder planning and projection from canonical routine state, with deterministic reminder identity, dedupe, no per-chore scheduler fan-out, approved notification/brief/optional Calendar projection and provider readback where mutation occurs.
15. `REMIND-003` has a directly test-supported anti-fan-out/explicit-activation routing boundary but no dedicated reminder planner/provider integration, so the complete feature remains specification-level rather than `test_verified`.
16. Legacy `f-12` → `f-11` must be normalized to shared underlying canonical behaviors, not service activation. `household_routines` may require `TASK-001`/`TASK-002`, `ROUTINE-001` and selected `REMIND-003` delivery capabilities without requiring `household_admin` itself to be enabled.
17. Optional Calendar projection remains optional. A user may track/advance routine state without Calendar, and a Calendar/notification failure cannot erase or falsify routine completion state.
18. Responsibility/ownership remains explicit. Household-manager role, routine activation or observed completion cannot silently assign future responsibility to one person.
19. No PR #31 evidence located during this bounded pass materially raises the F11/F12 evidence ceiling; existing deterministic router/test evidence is sufficient to establish the contract boundaries but not the missing engines/provider integration.

## Proposed normalization

- F11 `household_admin` → `TASK-001` + `TASK-002` under `SERVICE-001` + `SERVICE-002`; no new household-admin authority.
- Add `ROUTINE-001` — recurring/staged routine definition and occurrence lifecycle with stable identity, explicit responsibility, stage/completion evidence and miss/reschedule semantics.
- Add `REMIND-003` — consolidated routine/stage reminder planning and provider projection, preserving routine truth independently from delivery and prohibiting one scheduler/automation per chore.
- F12 `household_routines` → required `TASK-001`, `TASK-002`, `ROUTINE-001`; reminder-enabled path additionally requires `REMIND-003` and verified delivery capability; Calendar projection is optional.
- Normalize legacy `f-12` dependence on `f-11` into shared canonical task behaviors rather than sibling service activation.
- Keep `household_routines_enabled` as compatibility evidence for the `household_routines` service only; it must not silently enable `household_admin`, Calendar projection or any person ownership/responsibility.

## Acceptance criteria

1. Account for F11-F12 with stable mappings and create only genuinely missing routine/reminder feature IDs.
2. Reuse `TASK-001`/`TASK-002` for household admin rather than creating a household task database.
3. Keep actual asset-maintenance evidence/history separate under `ASSET-002`/`SPEC-001`; it is optional to household-admin tasking.
4. Preserve `household_admin` and `household_routines` as separate activation choices.
5. Add a domain-neutral recurring/staged routine lifecycle only if it remains distinct from generic tasks; current evidence supports `ROUTINE-001`.
6. Keep routine reminder/delivery separate from routine truth; current evidence supports `REMIND-003` with a lower evidence ceiling than the tested router contract.
7. No per-chore scheduler/automation fan-out. Use consolidated control-cycle/notification/optional Calendar projection with deterministic identities/readback.
8. Never infer household ownership/responsibility from profile role, service activation or observed completion.
9. Normalize the legacy F12→F11 aggregate dependency into shared underlying behaviors, not sibling-service activation.
10. Record actual implementation/test/provider evidence without promoting routing-contract tests to a staged routine engine or live delivery proof.
11. Update only `FEATURES.md`, `BACKLOG.md`, and `CURRENT_WORK.md`.
12. Open a bounded PR, verify scope, merge and remotely read back before advancing to F5.
13. Touch no legacy Google production state and change no executable MIRA 2.0 product behavior.

## Exact next action

Normalize F11-F12 in `FEATURES.md`: add the `ROUTINE-*` identity family, record F11 `household_admin` over `TASK-001`/`TASK-002`, add `ROUTINE-001` and `REMIND-003`, and map F12 `household_routines` without sibling-service activation coupling. Then rank only the missing routine/service dependency/provider work in `BACKLOG.md`, close acceptance state here, and run the three-file PR/merge/readback gate.

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
