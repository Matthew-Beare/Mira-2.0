# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and its exact resume point.

## Completed packet

### `M2-G0-005D` — Feature Audit Slice D4 — recipes, meal planning and category-D closure

- **Merged PR:** #13
- **Merge SHA:** `998e5fac8a8547c5c11893b4b3a111424b3cd82e`
- **Audited features:** `RECIPE-001`, `MEAL-001`
- **Result:** Category D is complete through all 16 historical rows with recipe knowledge, meal-plan state, grocery stock, shopping intent and purchase truth explicitly separated.
- **Live Google production touched:** no.
- **Executable product behavior changed:** no.

## Active packet

- **Packet ID:** `M2-G0-006A`
- **Name:** Feature Audit Slice E1 — safe starter and onboarding foundations
- **Class:** forensic audit / prerequisite
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Objective:** Audit the first five category-E onboarding/safe-initialization behaviors without entering role/profile variants or implementation work.

## Audit rows in this packet

1. Generic quarantined starter with no inherited personal data.
2. Adaptive first boot: four kickoff questions, then bounded follow-ups.
3. Ask AI use, pain points, job/duties, desired automation, apps/services and constraints.
4. Ask preferred brief cadence/timezone for new users.
5. Explicit service activation states: unresolved/enabled/disabled/not-applicable/deferred.

Do not expand this packet to working/retired/nonworking/parent/dependent roles, family behavior, accessibility, provider portability, distribution, enterprise or product coding.

## Acceptance criteria

1. Each scoped behavior receives stable semantic feature identity and an evidence boundary.
2. Starter/bootstrap state is generic and synthetic by default; it cannot inherit personal production data, identifiers, schedules, private third-party facts or legacy authority IDs.
3. First boot keeps the initial interaction to four or fewer high-value questions before bounded follow-ups and supports Minimum Useful Setup rather than interrogating the user indefinitely.
4. Discovery captures intended AI use, pain points, job/duties, desired automations, apps/services and constraints only to the extent needed for configuration/recommendations; duties may inform recommendations but cannot silently activate services.
5. New-user brief cadence and timezone are explicit configuration, use named IANA timezone semantics, and do not overwrite the personal deployment’s already-audited schedule.
6. Service activation uses finite explicit states including unresolved, enabled, disabled, not-applicable and deferred; recommendations do not equal activation.
7. Rejected/superseded universal-onboarding behavior is preserved as rejected evidence so it cannot resurrect through legacy code.
8. Only `FEATURES.md`, `BACKLOG.md`, and `CURRENT_WORK.md` are intended changes.
9. A small PR is scope-verified, merged and remotely read back.
10. `CURRENT_WORK.md` advances to the next bounded category-E slice without beginning role/profile implementation.
11. No live Google production state and no executable product behavior is changed.

## Exact next action

Create branch `audit/g0-006a-onboarding-foundations` from current `main`. Inspect category-E row 1: **Generic quarantined starter with no inherited personal data**, including clean lineage, synthetic examples, legacy-data exclusion and how rejected onboarding experiments are prevented from becoming defaults.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head when tools permit;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture new customer ideas in BACKLOG unless required for acceptance or explicitly reprioritized;
6. before the final packet line, state any customer action needed; if none is needed, use `Just tell me to continue.`;
7. the final visible line remains the packet recovery tag.
