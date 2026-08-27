# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and its exact resume point.

## Completed packet before this branch

### `M2-G0-007E` — Feature Audit Slice F5 — routines/accountability and education/study services

- **Merged PR:** #24
- **Merge SHA:** `6eac4c03a91532bd9c95169284776bc7b4479e84`
- **Main handoff commit activating F6:** `f86456423e7bf3964965006cd690df10b1430b81`
- **Audited rows:** F13-F14 — Routines/fitness/accountability; Education/study/deadlines/offline preparation.
- **Result:** F13 reuses `ROUTINE-001` + `TASK-001` + `TASK-002` with optional `REMIND-003` and no `FITNESS-*` authority; F14 adds `EDU-001`; generic source-linked Calendar projection is `CAL-007`.
- **Remote readback:** F5 `FEATURES.md` and `BACKLOG.md` verified on `main` after merge.
- **Live Google production touched:** no.
- **Executable product behavior changed:** no.

## Active packet

- **Packet ID:** `M2-G0-007F`
- **Name:** Feature Audit Slice F6 — family-school coordination and permission boundary
- **Class:** forensic audit / privacy prerequisite
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `audit/g0-007f-family-school-permissions`
- **Branch start SHA:** `f86456423e7bf3964965006cd690df10b1430b81`
- **Research checkpoint:** `2aa2e88765eca4bda68e0f2bd1a6151620610f4c`
- **Feature registry commit:** `1012b20a0a2615dce498fb9b72ff73d32139df38`
- **Backlog checkpoint commit:** `7966c6bd9a7c7beb78b06182b914e6df8a695450`
- **Status:** acceptance complete; bounded PR/merge/readback pending.

## Audited F6 row

15. **Parent/child school coordination**.

## Completed acceptance evidence

1. F15 `family_school` is actor/subject/scope-aware service composition, not a new family-school database or identity authority.
2. School/education truth remains `EDU-001`; exact people and relationships remain `PROFILE-012`; access/sharing grants remain `PROFILE-013`.
3. No `FAMILY-*` feature family or duplicate family-school engine was created because no distinct canonical lifecycle was found.
4. Legacy `f-15` is semantically defective because it hard-requires parent/guardian and dependent-minor role behaviors. `PROFILE-004`/`PROFILE-005` are recommendation/routing inputs, not runtime readiness or authorization gates.
5. Same-person/private education support does not require a cross-person sharing grant merely because `family_school` is enabled.
6. Cross-person/shared read, write or sharing requires exact actor, subject, resource and action scope under `PROFILE-013`; provider/API mutation or sharing counts only after exact readback.
7. Relationship labels, household membership, co-residence, school enrollment, observed Calendar traffic, role labels or prior completion never imply custody or access rights.
8. Minimum-necessary dependent/minor data applies and public/source fixtures must remain synthetic.
9. `TASK-*`, `ROUTINE-001`, `REMIND-003` and `CAL-007` remain optional selected workflow/projection dependencies with separate failure domains.
10. `CAL-007` projection cannot silently enable Calendar, invitations, attendees or access to another person's calendar.
11. Existing `PERSON-GRAPH-001`, `PERMISSION-SCOPE-001`, `EDUCATION-CORE-001` and `CALENDAR-PROJECTION-001` already represent the underlying implementation gaps; F6 added no duplicate implementation core.
12. Added only `AUDIT-F6` and `SERVICE-DEPS-006` to the backlog.
13. Legacy profile-router tests prove recommendation/activation and dependent-minor routing boundaries, not permission enforcement, provider sharing or live family-school behavior.
14. No dedicated family-school engine or qualifying PR #31 implementation was located, so F15 remains specification-level with no integration/live credit.
15. `FEATURES.md` whole-file replacement was diff-gated against the research checkpoint: exactly one file, 29 additions and two intended status replacements.
16. `BACKLOG.md` whole-file replacement was diff-gated against the feature commit: exactly one file, 16 additions and one intended closure-line replacement.
17. No live Google production state was touched and no executable MIRA 2.0 product behavior changed.

## Exact next action

Compare `audit/g0-007f-family-school-permissions` against `main` and verify the packet is limited to `FEATURES.md`, `BACKLOG.md`, and `CURRENT_WORK.md` with the branch zero commits behind. Open a pull request to `main`, verify GitHub's server-side changed-file list and mergeability, merge using the exact PR head SHA, remotely read back the F6 registry/backlog state from `main`, then inspect authoritative category-F evidence beginning with F16 **Travel/vacation/outdoor planning** and activate `M2-G0-007G` from the resulting main handoff commit.

## Next packet after F6

### `M2-G0-007G` — Feature Audit Slice F7

Begin with category-F row 16 **Travel/vacation/outdoor planning**. Determine the remainder of the bounded F7 slice from authoritative dependency evidence after F6 closes. Do not pre-expand from conversational memory.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head when tools permit;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture new customer ideas in BACKLOG unless required for acceptance or explicitly reprioritized;
6. before the final packet line, state any customer action needed; if none is needed, use `juset tell me to continue`;
7. the packet recovery tag remains visible in every MIRA-development reply.
