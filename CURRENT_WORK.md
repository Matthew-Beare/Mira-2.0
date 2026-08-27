# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and its exact resume point.

## Completed packet before this branch

### `M2-G0-007D` — Feature Audit Slice F4 — household administration and laundry routines

- **Merged PR:** #23
- **Merge SHA:** `c5a57a3c6c2896ad7c0bd47f889fa9832d387877`
- **Main handoff commit activating F5:** `80d6e5c42d1d6a746d1ab8fbcf595bd82fb4aaf1`
- **Audited rows:** F11-F12 — Household/errands/admin/maintenance; Laundry stages and drop-off/pickup reminders.
- **Result:** `household_admin` maps to `TASK-001`/`TASK-002`; `ROUTINE-001` owns recurring/staged routine truth; `REMIND-003` owns consolidated reminder projection; sibling service activation and ownership inference are prohibited.
- **Remote readback:** F4 `FEATURES.md` and `BACKLOG.md` verified on `main` after merge.
- **Live Google production touched:** no.
- **Executable product behavior changed:** no.

## Active packet

- **Packet ID:** `M2-G0-007E`
- **Name:** Feature Audit Slice F5 — routines/accountability and education/study services
- **Class:** forensic audit / prerequisite
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `audit/g0-007e-routines-education-services`
- **Branch start SHA:** `80d6e5c42d1d6a746d1ab8fbcf595bd82fb4aaf1`
- **Research checkpoint:** `2ed4d62470632deec063be1bfdd86ebf9a10deec`
- **Feature registry commit:** `8682a5b8dc2974e72a4a3acf32337fce5bf31a59`
- **Backlog checkpoint commit:** `bdc04b262fc74b212027915a4d37a4d4f76fb254`
- **Status:** acceptance complete; bounded PR/merge/readback pending.

## Audited F5 rows

13. **Routines/fitness/accountability**.
14. **Education/study/deadlines/offline road preparation**.

## Completed acceptance evidence

1. F13 `routines_fitness` is service composition rather than a new fitness database. Basic readiness maps to `ROUTINE-001` + `TASK-001` + `TASK-002`.
2. Optional accountability/reminder behavior reuses `REMIND-003`; reminder delivery, elapsed time, silence or missing wearable data never proves routine completion.
3. `ROUTINE-001` was refined to permit optional session-component/result/progression/review metadata and context-valid minimum-viable variants while preserving one routine/occurrence authority and evidence-grounded completion/miss/reschedule history.
4. `REMIND-003` was refined for acknowledgement/anti-nag and selected progression/review cadence without becoming routine truth.
5. Wearable ingestion remains optional F22 work and is outside this packet. Basic F13 readiness cannot depend on a wearable.
6. No `FITNESS-*` identity family or duplicate fitness engine was created because no distinct canonical lifecycle justified one.
7. Added `EDU-001` because durable program/course/certification identity, academic-work/deadline/prerequisite state and source provenance outlive individual tasks and study sessions.
8. `TASK-001`/`TASK-002` remain the action/next-action authority for education work; optional recurring study/accountability uses `ROUTINE-001`/`REMIND-003` instead of a second study scheduler.
9. `EDU-001` preserves HOME/away applicability, verified deadlines/prerequisites and honest offline-readiness facts while prohibiting fabricated submissions, attendance, grades, citations or proof of completion.
10. Retained source materials/evidence remain separate from education/task completion. Broader generic knowledge normalization is intentionally left for the later F19 audit.
11. Added `CAL-007` for generic source-linked Calendar projection because stable Projection identity, exact provider-event linkage, update/cancel/dedupe/recreate semantics and provider readback apply beyond appointments.
12. `CAL-006` remains the appointment-specific specialization and should reuse the generic `CAL-007` core rather than being stretched into unrelated domains or implemented as a competing projection engine.
13. Calendar, retained/offline materials and routine/accountability are independently optional education paths; failure of those providers cannot erase or falsify canonical education/task/routine state.
14. Offline readiness requires actual retained/downloaded evidence; a source link alone is not proof that material will work without connectivity.
15. Legacy onboarding/router evidence proves catalog/recommendation boundaries but does not silently activate F13/F14 or prove domain implementation.
16. Legacy `life-planning-accountability.md` provides strong workflow/specification evidence but no dedicated education, routine-progression or generic Calendar provider engine/test suite was located.
17. PR #31 contains no qualifying F13/F14 implementation that raises MIRA 2.0 evidence to integration/live status.
18. `FEATURES.md` whole-file replacement was diff-gated against the research checkpoint: one file only, 76 additions and four intentional replacements; `EDU-*`, `CAL-*` and F5 tail were spot-read back.
19. `BACKLOG.md` whole-file replacement was diff-gated against the feature commit: one file only, 21 additions and four intentional replacements. It added `AUDIT-F5`, `SERVICE-DEPS-005`, `EDUCATION-CORE-001`, refined existing routine work, and reconciled existing `CALENDAR-PROJECTION-001` to the generic `CAL-007` core rather than minting duplicate work.
20. No live Google production state was touched and no executable MIRA 2.0 product behavior changed.

## Exact next action

Compare `audit/g0-007e-routines-education-services` against `main` and verify the packet is limited to `FEATURES.md`, `BACKLOG.md`, and `CURRENT_WORK.md` with the branch zero commits behind. Open a pull request to `main`, verify GitHub's server-side changed-file list and mergeability, merge using the exact PR head SHA, remotely read back the F5 feature/backlog state from `main`, then inspect authoritative category-F evidence beginning with F15 **Parent/child school coordination** and activate `M2-G0-007F` from the resulting main handoff commit.

## Next packet after F5

### `M2-G0-007F` — Feature Audit Slice F6

Begin with category-F row 15 **Parent/child school coordination**. Determine the remainder of the bounded F6 slice from authoritative ledger/dependency evidence after F5 closes. Do not pre-expand from conversational memory.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head when tools permit;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture new customer ideas in BACKLOG unless required for acceptance or explicitly reprioritized;
6. before the final packet line, state any customer action needed; if none is needed, use `juset tell me to continue`;
7. the packet recovery tag remains visible in every MIRA-development reply.
