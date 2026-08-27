# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and its exact resume point.

## Completed packet before this branch

### `M2-G0-007D` — Feature Audit Slice F4 — household administration and laundry routines

- **Merged PR:** #23
- **Merge SHA:** `c5a57a3c6c2896ad7c0bd47f889fa9832d387877`
- **Main handoff commit activating F5:** `80d6e5c42d1d6a746d1ab8fbcf595bd82fb4aaf1`
- **Audited rows:** F11-F12 — Household/errands/admin/maintenance; Laundry stages and drop-off/pickup reminders.
- **Result:** `household_admin` maps to `TASK-001`/`TASK-002`; `ROUTINE-001` owns recurring/staged routine truth; `REMIND-003` owns consolidated reminder projection; sibling service activation and ownership inference are prohibited.
- **Remote readback:** F4 `FEATURES.md` and `BACKLOG.md` were verified on `main` after merge.
- **Live Google production touched:** no.
- **Executable product behavior changed:** no.

## Active packet

- **Packet ID:** `M2-G0-007E`
- **Name:** Feature Audit Slice F5 — routines/accountability and education/study services
- **Class:** forensic audit / prerequisite
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `audit/g0-007e-routines-education-services`
- **Branch start SHA:** `80d6e5c42d1d6a746d1ab8fbcf595bd82fb4aaf1`
- **Status:** forensic evidence pass complete; feature/backlog normalization next.

## Exact category-F scope in this packet

Audit exactly legacy category-F rows 13-14:

13. **Routines/fitness/accountability** — REQUIRED for the reference user; optional stock service; legacy skill workflow plus task-state and optional wearable profile.
14. **Education/study/deadlines/offline road preparation** — REQUIRED for the reference user; optional stock service; legacy skill workflow plus task-state, optional Calendar projection and retained evidence/source-material profile.

Do not expand this packet into F15 Parent/child school coordination, family permissions, travel, work-trip tracking, assets/knowledge, backup/recovery, custom skill building, activity/wearable ingestion itself, weather onboarding, category G, or executable MIRA 2.0 coding.

## Forensic findings

### F13 — Routines/fitness/accountability

1. Legacy `f-13` declares `task-state`, optional wearable capability and policy-source but no explicit required child behavior. The service exists in the deterministic service catalog as `routines_fitness` and is recommended for a dependent-minor profile, while catalog presence/recommendation never activates it or proves implementation.
2. The canonical `life-planning-accountability.md` authority explicitly says to reuse the existing canonical task/control/state system when it can represent the workflow cleanly and provision additional routine/plan/study state only when the selected module genuinely needs fields the existing schema cannot safely hold.
3. F13's general lifecycle requirements line up with the already-audited `ROUTINE-001`: purpose/outcome, frequency/window, context variants, resources, minimum viable version, completion definition, partial/missed/rescheduled state and durable history.
4. F13 adds useful optional routine metadata rather than a separate fitness authority: session component blocks, optional duration/sets/reps/load/variation, progression/review rule and evidence-supported progression review. These can refine `ROUTINE-001` occurrence/result semantics without manufacturing `FITNESS-*` identity.
5. Accountability prompting also reuses the F4 split: canonical truth remains `ROUTINE-001`/`TASK-*`; check-ins/reminders are optional `REMIND-003` projections with acknowledgement/anti-nag and selected review cadence. Reminder delivery cannot prove completion.
6. Wearable ingestion is explicitly optional in legacy F13 and is separately catalogued as F22. Basic `routines_fitness` readiness must not require a wearable. Later verified wearable observations may contribute evidence only under F22's future authority/integration rules.
7. No dedicated fitness/accountability engine or deterministic performance/progression suite was found in the audited legacy source or PR #31. The strongest evidence is skill/workflow specification plus the generic task/routine/router safety cores.
8. F13 therefore creates no new domain ID. Canonical mapping should be `routines_fitness` → `ROUTINE-001` + `TASK-001` + `TASK-002`; an accountability/reminder path may additionally use `REMIND-003`; wearable remains optional and outside F5.

### F14 — Education/study/deadlines/offline road preparation

9. Legacy `f-14` declares `task-state`, optional Calendar projection, `evidence-store-rw` and policy-source but no explicit required behavior. The deterministic router exposes `education` independently and recommends it for student/dependent-minor roles without silently enabling it.
10. The life-planning authority requires stable program/course/certification identity plus verified assignments/exams/projects/deadlines, status/prerequisites, weekly target/session sizing, HOME/away applicability, offline/download requirements, source links and accountability cadence.
11. Those semantics do not safely collapse into generic task/routine records: a course/certification track is a durable education entity/lifecycle that many tasks, deadlines, study routines and evidence items may reference. A distinct canonical education feature is justified: proposed `EDU-001` — education track/course/certification identity and verified academic-work/deadline state.
12. `EDU-001` should own track/work identity, status and prerequisites, source/provenance links and offline-readiness facts; `TASK-001`/`TASK-002` continue to own actionable work and evidence-grounded next actions. Recurring study sessions/accountability remain optional `ROUTINE-001`/`REMIND-003` composition rather than a second study scheduler.
13. The same authority forbids fabrication of submissions, attendance, grades, citations or proof of work and forbids academic dishonesty. Deadline/status changes require supported source evidence or explicit user correction; silence does not mean submitted/passed/completed.
14. Retained syllabi/materials remain separate document/evidence state linked from education records. F5 should not preempt F19's broader personal knowledge/reference-library audit by inventing a new generic knowledge authority here. Core education readiness can preserve exact source links/provenance; retained/offline-material handling is a selected provider/evidence capability path.
15. F14's Calendar projection cannot honestly reuse appointment-specific `CAL-006`. The audited generic `calendar-projection.md` contract applies stable Projection ID = source type + source ID + event class, exact target calendar/provider event ID, update/cancel/dedupe/recreate rules and provider readback across school/work deadlines, tasks, trips, deliveries, maintenance and other user-selected classes.
16. That distinct lifecycle justifies proposed `CAL-007` — generic source-linked Calendar projection with stable Projection identity, in-place revision/cancellation and exact provider readback. `CAL-006` remains the appointment-specific specialization and may later reuse the generic core rather than being semantically stretched across unrelated domains.
17. No dedicated education core or generic Calendar projection executable/test suite was found in the audited legacy source or PR #31. Both `EDU-001` and `CAL-007` therefore remain specification/workflow-level until deterministic engines and provider integration are proven.
18. F14 should use selected-submodule semantics: core education/deadline path requires `EDU-001` + `TASK-001` + `TASK-002`; recurring study/accountability may add `ROUTINE-001` and `REMIND-003`; retained/offline-material handling adds the selected evidence/file capability; Calendar projection is optional through `CAL-007`.
19. A failed Calendar/evidence provider path cannot erase or falsify canonical education/task/routine state. Offline readiness must be based on actual retained/downloaded evidence rather than assuming a link remains reachable on the road.
20. PR #31 contains no dedicated education/study implementation files or qualifying generic Calendar engine that raises these evidence ceilings; its broad platform/client work remains reference-only.

## Proposed normalization

- F13 `routines_fitness` → `ROUTINE-001` + `TASK-001` + `TASK-002`; optional accountability/reminder path adds `REMIND-003`; wearable remains optional F22 capability. No `FITNESS-*` feature.
- Refine `ROUTINE-001` with optional session component/result/progression/review metadata and context-valid minimum-viable variants; preserve one routine identity and evidence-grounded occurrence history.
- Refine `REMIND-003` with acknowledged-check-in anti-nag behavior and selected progression/review cadence for routine accountability.
- Add `EDU-001` — durable education program/course/certification plus academic-work/deadline/prerequisite identity and provenance.
- Add `CAL-007` — generic source-linked Calendar projection core across canonical event classes; keep `CAL-006` as appointment-specific specialization.
- F14 `education` uses selected paths: core `EDU-001` + `TASK-001` + `TASK-002`; study/accountability adds `ROUTINE-001`/`REMIND-003`; retained/offline materials and Calendar are optional verified capabilities, with Calendar using `CAL-007`.
- Do not create a new generic knowledge/document authority in F5; defer that broader normalization to F19 while preserving source/evidence links now.

## Acceptance criteria

1. Account for F13-F14 with stable canonical mappings and create new IDs only where distinct lifecycle/authority boundaries require them.
2. F13 creates no fitness database: reuse/refine `ROUTINE-001`, `TASK-001`, `TASK-002` and optional `REMIND-003`.
3. Preserve explicit completion/partial/miss/reschedule evidence and never infer exercise/routine completion from elapsed time, reminder delivery or wearable absence.
4. Keep wearable ingestion optional and outside this packet; F13 basic readiness cannot depend on F22.
5. Add `EDU-001` only for the distinct program/course/certification and academic-work/deadline/prerequisite lifecycle.
6. Preserve verified deadlines, prerequisites, source provenance, home/away/offline constraints and accountability cadence without fabricating submissions, grades or attendance.
7. Add generic `CAL-007` only because non-appointment source-linked Calendar projection has a distinct reusable identity/update/readback contract; do not misuse appointment-specific `CAL-006`.
8. Calendar/evidence provider failure cannot erase canonical education/task/routine state; offline readiness requires actual evidence of retained/downloaded materials.
9. Retained source materials remain separate from education/task completion and broader generic knowledge normalization remains outside F5.
10. Record requirement status separately from implementation/test/integration/live evidence and do not promote skill prose or router catalog presence to executable proof.
11. Update only `FEATURES.md`, `BACKLOG.md`, and `CURRENT_WORK.md`.
12. Open a bounded PR, verify scope, merge and remotely read back before advancing to F6.
13. Touch no legacy Google production state and change no executable MIRA 2.0 product behavior.

## Exact next action

Normalize F13-F14 in `FEATURES.md`: add the `EDU-*` identity family, refine `ROUTINE-001` and `REMIND-003` for F13 without adding a fitness authority, add `EDU-001` and generic `CAL-007`, and record selected-path service mappings. Then update `BACKLOG.md` with only the missing F5 service/dependency/education work and the generic Calendar-core reconciliation, close acceptance here, and run the three-file PR/merge/readback gate.

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
