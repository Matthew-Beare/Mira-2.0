# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and its exact resume point.

## Completed packet before this branch

### `M2-G0-007D` — Feature Audit Slice F4 — household administration and laundry routines

- **Merged PR:** #23
- **Merge SHA:** `c5a57a3c6c2896ad7c0bd47f889fa9832d387877`
- **Audited rows:** F11-F12 — Household/errands/admin/maintenance; Laundry stages and drop-off/pickup reminders.
- **Result:** `household_admin` maps to `TASK-001`/`TASK-002`; `ROUTINE-001` owns recurring/staged routine truth; `REMIND-003` owns consolidated reminder projection; sibling service activation and ownership inference are prohibited.
- **Backlog:** added only `AUDIT-F4`, `SERVICE-DEPS-004`, `ROUTINE-CORE-001`, and `ROUTINE-REMINDER-001`.
- **Remote readback:** F4 `FEATURES.md` and `BACKLOG.md` were verified on `main` after merge.
- **Live Google production touched:** no.
- **Executable product behavior changed:** no.

## Active packet

- **Packet ID:** `M2-G0-007E`
- **Name:** Feature Audit Slice F5 — routines/accountability and education/study services
- **Class:** forensic audit / prerequisite
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `audit/g0-007e-routines-education-services`
- **Base merge SHA:** `c5a57a3c6c2896ad7c0bd47f889fa9832d387877`
- **Status:** activated; forensic evidence pass next.

## Exact category-F scope in this packet

Audit exactly legacy category-F rows 13-14:

13. **Routines/fitness/accountability** — REQUIRED for the reference user; optional stock service; legacy skill workflow plus task-state and optional wearable profile.
14. **Education/study/deadlines/offline road preparation** — REQUIRED for the reference user; optional stock service; legacy skill workflow plus task-state, optional Calendar projection and retained evidence/source-material profile.

Do not expand this packet into F15 Parent/child school coordination, family permissions, travel, work-trip tracking, assets/knowledge, backup/recovery, custom skill building, activity/wearable ingestion itself, weather onboarding, category G, or executable MIRA 2.0 coding.

## Packet-boundary rationale

- F13 and F14 are both user-facing planning/accountability compositions over task/routine state with optional projections/integrations.
- F15 immediately introduces Person/relationship identity plus family/school permission-sensitive behavior (`e-09`, `e-10`, `e-16`), so it begins a different dependency and privacy slice.
- Wearable data ingestion remains F22; F13 may consume an optional verified wearable capability later but cannot claim that integration merely because fitness/accountability exists.

## Acceptance criteria

1. Account for F13-F14 with stable canonical mappings and create new IDs only when generic `TASK-*`/`ROUTINE-*`/evidence/calendar features cannot honestly represent the required lifecycle.
2. Determine whether F13 is fully covered by `ROUTINE-001` + `TASK-001`/`TASK-002` plus optional future wearable capability, without manufacturing a fitness database by label alone.
3. Preserve explicit completion/miss/reschedule evidence and never infer exercise/routine completion from elapsed time, reminder delivery or wearable absence.
4. Keep wearable ingestion optional and outside this packet; F13 cannot depend on F22 being implemented for basic readiness.
5. Determine whether education/study needs a distinct canonical education/course/deadline authority or can safely compose generic tasks/routines/evidence without losing identity/lifecycle semantics.
6. Preserve verified deadlines, prerequisites, source materials, home/away/offline constraints and accountability cadence without fabricating completed work, grades or attendance.
7. Calendar projection for study/deadline state remains optional and provider-readback-gated; Calendar failure cannot erase canonical education/task state.
8. Retained source materials/evidence remain separate from task completion and should reuse canonical evidence/knowledge behavior where possible.
9. Record requirement status separately from implementation/test/integration/live evidence and do not promote skill prose to executable proof.
10. Update only `FEATURES.md`, `BACKLOG.md`, and `CURRENT_WORK.md`.
11. Open a bounded PR, verify scope, merge and remotely read back before advancing to F6.
12. Touch no legacy Google production state and change no executable MIRA 2.0 product behavior.

## Exact next action

Create branch `audit/g0-007e-routines-education-services` from this main handoff commit. Inspect authoritative F13 evidence across the feature ledger, `behavior-dependencies.json`, module catalog, onboarding/profile routing and any dedicated routine/accountability implementation/tests. Decide whether F13 creates any new canonical feature beyond `ROUTINE-001`/`TASK-*`; checkpoint that evidence in this file before auditing F14.

## Next packet after F5

### `M2-G0-007F` — Feature Audit Slice F6

Begin with category-F row 15 **Parent/child school coordination** and determine the remainder of the bounded F6 slice from authoritative dependency evidence after F5 closes.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head when tools permit;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture new customer ideas in BACKLOG unless required for acceptance or explicitly reprioritized;
6. before the final packet line, state any customer action needed; if none is needed, use `Just tell me to continue.`;
7. the final visible line remains the packet recovery tag.
