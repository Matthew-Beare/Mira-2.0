# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and its exact resume point.

## Completed packet

### `M2-G0-006A` — Feature Audit Slice E1 — safe starter and onboarding foundations

- **Merged PR:** #14
- **Merge SHA:** `4a86cdf79939fcdb183423e8b8ae94463dc0ae43`
- **Audited features:** `ONBOARD-002`, `ONBOARD-003`, `ONBOARD-004`, `ONBOARD-005`, `SERVICE-001`
- **Result:** safe starter, minimum useful first boot, bounded capability/discovery, new-user schedule/timezone configuration and explicit service activation state are normalized at their actual evidence levels.
- **Live Google production touched:** no.
- **Executable product behavior changed:** no.

## Active packet

- **Packet ID:** `M2-G0-006B`
- **Name:** Feature Audit Slice E2 — role/profile foundations
- **Class:** forensic audit / prerequisite
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Objective:** Audit category-E rows 6-10 covering working/self-employed, retired, nonworking, parent/guardian and dependent-minor profile behavior without entering later profile variants, family sharing implementation or product code.

## Audit rows in this packet

1. Working/self-employed profile behavior.
2. Retired profile behavior distinct from nonworking/unemployed state.
3. Nonworking/between-jobs profile behavior distinct from retirement.
4. Parent/guardian profile behavior and family/household recommendations.
5. Dependent child/minor profile behavior with privacy/permission safety boundaries.

Do not expand this packet to caregiver, household-manager, student or custom profiles; accessibility; family sharing implementation; provider portability; distribution; enterprise; or product coding.

## Acceptance criteria

1. Each scoped behavior receives a stable semantic feature ID and explicit evidence boundary.
2. Working and self-employed are supported as composable but semantically distinct roles when behavior differs; job title/duties may recommend workflows but never silently activate services or context modes.
3. Retired is a first-class role distinct from nonworking/between-jobs and does not infer age, disability, health condition or reduced capability.
4. Nonworking/between-jobs remains distinct from retirement and can surface personal priorities/next actions without forcing work-mode machinery.
5. Parent/guardian is a first-class composable role; family/school, appointments, household actions and shopping are recommendations until explicitly activated.
6. Dependent-minor handling preserves privacy/minimum-necessary data, never infers guardian sharing/consent, and requires explicit safety/permission boundaries for recurring away contexts or shared state.
7. Existing deterministic legacy router/tests and relevant policy are inspected; code existence is not promoted beyond its evidence level.
8. Rejected or unsafe role assumptions remain rejected so they cannot re-enter through legacy code.
9. Only `FEATURES.md`, `BACKLOG.md`, and `CURRENT_WORK.md` are intended packet changes.
10. A small PR is scope-verified, merged and remotely read back.
11. `CURRENT_WORK.md` advances to the next bounded category-E slice with an exact resume point.
12. No live Google production state and no executable MIRA 2.0 product behavior is changed.

## Exact next action

Create branch `audit/g0-006b-role-profile-foundations` from the current `main` checkpoint. Inspect category-E row 6: **Working/self-employed profile behavior**, including role composition, work/context recommendation versus activation, exact job/duties handling and any deterministic router/tests.

## Next packet boundary

If E2 completes, the next bounded category-E slice begins with caregiver/household-manager/student/custom role variants and remaining per-user customization/accessibility rows. Do not begin provider/distribution category F inside E2.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head when tools permit;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture new customer ideas in BACKLOG unless required for acceptance or explicitly reprioritized;
6. before the final packet line, state any customer action needed; if none is needed, use `Just tell me to continue.`;
7. the final visible line remains the packet recovery tag.
