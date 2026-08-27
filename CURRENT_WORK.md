# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and its exact resume point.

## Completed packet before this branch

### `M2-G0-007E` — Feature Audit Slice F5 — routines/accountability and education/study services

- **Merged PR:** #24
- **Merge SHA:** `6eac4c03a91532bd9c95169284776bc7b4479e84`
- **Main handoff commit activating F6:** `f86456423e7bf3964965006cd690df10b1430b81`
- **Audited rows:** F13-F14 — Routines/fitness/accountability; Education/study/deadlines/offline preparation.
- **Result:** F13 reuses `ROUTINE-001` + `TASK-001` + `TASK-002` with optional `REMIND-003` and no `FITNESS-*` authority; F14 adds `EDU-001`; generic source-linked Calendar projection is `CAL-007`, with appointment-specific `CAL-006` remaining a specialization.
- **Backlog:** added `AUDIT-F5`, `SERVICE-DEPS-005`, `EDUCATION-CORE-001`; refined existing routine and Calendar projection work instead of duplicating engines.
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
- **Status:** forensic evidence pass complete; registry/backlog normalization next.

## Exact category-F scope in this packet

Audit exactly legacy category-F row 15:

15. **Parent/child school coordination** — CURRENT REQUIRED direction; parent/dependent role routing exists; dedicated family-school service remains specification/skill-level; legacy dependency map references parent/guardian, dependent-minor and Person identity behavior plus optional Calendar projection.

Do not expand this packet into F16 travel/vacation/outdoor planning, F17 work-trip/route/paid-work tracking, F18 assets, F19 knowledge, F20 recovery, F21 skill builder, F22 wearable/activity ingestion, F23 weather onboarding, category G, or executable MIRA 2.0 coding.

## Packet-boundary rationale

- F15 is privacy/authorization-sensitive because coordination may cross Person identities and expose education/calendar/school state.
- F16 immediately returns to ordinary Trip/Route travel planning and has no parent/minor permission dependency. Combining them would mix unrelated authority, privacy and verification boundaries.
- Therefore F6 is deliberately one historical row only.

## Forensic findings

1. The feature ledger marks **Parent/child school coordination** as `CURRENT REQUIRED direction`; parent/dependent role routing is implemented, while the dedicated service remains specification/skill-level.
2. Legacy `f-15` declares `identity-state`, optional Calendar projection and policy-source, and hard-requires historical E9 parent/guardian, E10 dependent-minor and E16 Person identity behavior.
3. That dependency shape is semantically over-bundled. `PROFILE-004` parent/guardian and `PROFILE-005` dependent-minor are routing/profile facts; roles may recommend `family_school` but cannot be runtime capability prerequisites or permission grants.
4. `PROFILE-012` already owns canonical Person UUIDs and explicit relationship truth. Parent, guardian, dependent, caregiver, household-member and other relationship labels describe reality but do not authorize access.
5. `PROFILE-013` already owns explicit actor/resource/action permission and sharing scopes, including personal, whole-authority and scoped-shared authority. Provider/API sharing changes count only after exact identity/scope readback.
6. `STATE_AUTHORITY_MODEL.md` explicitly permits school/shared state to live in a scoped authority when privacy/sharing/failure isolation justifies it and explicitly says never infer that a family member should receive access.
7. `EDU-001` already owns program/course/certification, academic-work/deadline/prerequisite and source-provenance truth. F15 therefore must reference a subject Person's `EDU-001` state rather than creating a second family-school education database.
8. `TASK-*`, `ROUTINE-*` and `REMIND-*` continue to own action/routine/reminder semantics. F15 cannot infer submission, attendance, grades, completion, custody, responsibility or school authority from those records.
9. `CAL-007` is an independently optional Calendar projection. Family-school activation cannot silently enable Calendar projection, create attendees/invitations or grant access to another person's calendar.
10. The onboarding router catalogues `family_school`, recommends it for parent/guardian and dependent-minor roles, and keeps activation unresolved unless explicitly selected. Existing tests prove recommendation/activation separation and dependent-minor routing, not family-school permission enforcement.
11. `questions.profile-and-stock-services.json` asks parents which family/school workflows would help and explicitly states preference/activation questions require user answers; recommendation evidence is not consent.
12. No dedicated family-school engine, family-school-specific state identity or deterministic permission/provider test suite was located in the audited legacy source or PR #31. Code search returned no qualifying `family_school` implementation beyond routing/catalog references.
13. A new `FAMILY-*` domain authority is therefore **not justified**. F15 is a service composition over existing Person/relationship, permission, education, task/routine/reminder and optional Calendar authorities.
14. Canonical F15 readiness should be actor/subject/scope based, not role-token based: exact actor/subject identities and required access scope must be resolved; role labels influence recommendation only.
15. For same-person/private education support, no cross-person sharing grant is needed merely because `family_school` exists. For cross-person access, `PROFILE-013` permission scope is mandatory and must be verified against the exact provider/API/resource where applicable.
16. Minimum-necessary private data applies to dependent/minor state. Synthetic fixtures only may appear in public MIRA 2.0 source/tests.
17. Complete F15 readiness cannot exceed `PROFILE-012`/`PROFILE-013`/`EDU-001` implementation evidence. Existing role/router tests do not promote permission enforcement, shared-state provider integration or live verification.

## Proposed normalization

- F15 service key `family_school` → core subject `EDU-001` plus exact `PROFILE-012` Person/relationship identity; add `PROFILE-013` whenever actor and subject differ or shared/cross-person state is requested.
- `TASK-001`/`TASK-002`, `ROUTINE-001` and `REMIND-003` remain selected workflow dependencies only when the enabled family-school path uses them.
- `CAL-007` remains independently optional and permission-scoped to the exact calendar/resource; invitations/attendees remain separate consequential actions.
- Remove legacy parent/dependent role behaviors from readiness prerequisites. `PROFILE-004`/`PROFILE-005` remain recommendation/routing inputs, not authorization or capability gates.
- Add no `FAMILY-*` feature ID and no duplicate family-school database.
- Add backlog work only for the F6 dependency-map repair; existing `PERSON-GRAPH-001`, `PERMISSION-SCOPE-001`, `EDUCATION-CORE-001` and `CALENDAR-PROJECTION-001` already represent the missing implementation work.

## Acceptance criteria

1. F15 is accounted for without inventing a duplicate family-school authority unless evidence proves a distinct lifecycle.
2. `PROFILE-012` Person/relationship identity remains separate from `PROFILE-013` permission/sharing grants; relationship labels authorize nothing.
3. Parent/guardian role, dependent-minor role, household membership, co-residence, school enrollment or observed calendar traffic cannot silently grant school/calendar/education access.
4. Any cross-person read/write/share path identifies exact actor/subject/resource/action scope and requires explicit authority plus provider/API readback where provider sharing/mutation occurs.
5. Minimum-necessary private data applies to dependent/minor state and public/source fixtures remain synthetic.
6. `EDU-001` remains canonical school/education truth; F15 creates no second education database.
7. Existing task/routine/reminder semantics remain separate and cannot infer completion, attendance, grades, custody or responsibility.
8. Calendar remains independently optional under `CAL-007`; family-school activation cannot silently enable projection, invitations or attendee updates.
9. Service recommendation remains separate from activation under `SERVICE-001`; profile roles do not become readiness or permission gates.
10. Requirement status remains separate from implementation/test/integration/live evidence.
11. Update only `FEATURES.md`, `BACKLOG.md`, and `CURRENT_WORK.md`.
12. Open a bounded PR, verify scope, merge and remotely read back before advancing to F7.
13. Touch no legacy Google production state and change no executable MIRA 2.0 product behavior.

## Exact next action

Normalize F15 in `FEATURES.md` with **no new family domain ID**: record `family_school` as actor/subject/scope-aware service composition over `EDU-001` + `PROFILE-012`, require `PROFILE-013` only for cross-person/shared access, keep `PROFILE-004`/`PROFILE-005` as recommendation inputs rather than readiness gates, and keep `CAL-007`/task/routine/reminder paths optional. Then update `BACKLOG.md` with `AUDIT-F6` and one dependency-repair work item only, close acceptance here, and run the three-file PR/merge/readback gate.

## Next packet after F6

### `M2-G0-007G` — Feature Audit Slice F7

Begin with category-F row 16 **Travel/vacation/outdoor planning** and determine the remainder of the bounded F7 slice from authoritative dependency evidence after F6 closes.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head when tools permit;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture new customer ideas in BACKLOG unless required for acceptance or explicitly reprioritized;
6. before the final packet line, state any customer action needed; if none is needed, use `juset tell me to continue`;
7. the packet recovery tag remains visible in every MIRA-development reply.
