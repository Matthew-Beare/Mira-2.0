# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and its exact resume point.

## Completed packet before this branch

### `M2-G0-007E` — Feature Audit Slice F5 — routines/accountability and education/study services

- **Merged PR:** #24
- **Merge SHA:** `6eac4c03a91532bd9c95169284776bc7b4479e84`
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
- **Base merge SHA:** `6eac4c03a91532bd9c95169284776bc7b4479e84`
- **Status:** activated; forensic evidence pass next.

## Exact category-F scope in this packet

Audit exactly legacy category-F row 15:

15. **Parent/child school coordination** — CURRENT REQUIRED direction; parent/dependent role routing exists; dedicated family-school service remains specification/skill-level; legacy dependency map references parent/guardian, dependent-minor and Person identity behavior plus optional Calendar projection.

Do not expand this packet into F16 travel/vacation/outdoor planning, F17 work-trip/route/paid-work tracking, F18 assets, F19 knowledge, F20 recovery, F21 skill builder, F22 wearable/activity ingestion, F23 weather onboarding, category G, or executable MIRA 2.0 coding.

## Packet-boundary rationale

- F15 is privacy/authorization-sensitive because coordination may cross Person identities and expose education/calendar/school state.
- Its relevant foundations are `PROFILE-004`, `PROFILE-005`, `PROFILE-012`, `PROFILE-013`, `EDU-001`, `SERVICE-001`/`SERVICE-002` and optional `CAL-007`.
- F16 immediately returns to ordinary Trip/Route travel planning and has no parent/minor permission dependency. Combining them would create one packet with unrelated authority, privacy and verification boundaries.
- Therefore F6 is deliberately one historical row only.

## Acceptance criteria

1. Determine whether F15 is purely a service composition over existing Person/permission/education/task/calendar authorities or whether a distinct canonical family-school coordination lifecycle genuinely requires a new feature ID.
2. Preserve `PROFILE-012` Person/relationship identity separately from `PROFILE-013` permission/sharing grants; relationship labels never authorize access.
3. Parent/guardian role, dependent-minor role, household membership, co-residence, school enrollment or observed calendar traffic must not silently grant school/calendar/education access.
4. Any cross-person read/write/share path must identify exact actor/subject/resource/action scope and require explicit authority plus provider/API readback where provider sharing/mutation occurs.
5. Minimum-necessary private data applies to dependent/minor state. Public source and synthetic fixtures must contain no real family/school/private production data.
6. Reuse `EDU-001` for program/course/academic-work/deadline truth; family-school coordination must not create a second education database.
7. Reuse `TASK-*`/`ROUTINE-*`/`REMIND-*` only for their existing action/routine/reminder semantics; coordination cannot infer completion, attendance, grades, custody or responsibility.
8. Calendar projection remains independently optional through `CAL-007`; enabling family-school coordination cannot silently enable Calendar projection, invitations or attendee updates.
9. Service recommendation remains separate from activation under `SERVICE-001`; parent/dependent profile recommendations cannot enable F15 automatically.
10. Record requirement status separately from implementation/test/integration/live evidence and do not promote router/profile tests to permission-enforcement/provider proof.
11. Update only `FEATURES.md`, `BACKLOG.md`, and `CURRENT_WORK.md`.
12. Open a bounded PR, verify scope, merge and remotely read back before advancing to F7.
13. Touch no legacy Google production state and change no executable MIRA 2.0 product behavior.

## Exact next action

Create branch `audit/g0-007f-family-school-permissions` from this main handoff commit. Inspect authoritative F15 evidence across the feature ledger, `behavior-dependencies.json`, parent/dependent/profile router and tests, `questions.profile-and-stock-services.json`, `STATE_AUTHORITY_MODEL.md`, and any family-school specific skill/code/tests. Decide first whether F15 needs any canonical feature beyond `PROFILE-012`/`PROFILE-013` + `EDU-001` + existing task/routine/calendar composition; checkpoint the finding before registry normalization.

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
