# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and its exact resume point.

## Completed packet

### `M2-G0-006B` — Feature Audit Slice E2 — role/profile foundations

- **Merged PR:** #15
- **Merge SHA:** `0e7bdd0a5f9c8ee907332bb8b802317df0cab7d9`
- **Audited features:** `PROFILE-001`, `PROFILE-002`, `PROFILE-003`, `PROFILE-004`, `PROFILE-005`
- **Result:** working/self-employed, retired, nonworking, parent/guardian and dependent-minor roles are normalized as routing/profile state with permissions and activation kept separate.
- **Live Google production touched:** no.
- **Executable product behavior changed:** no.

## Active packet

- **Packet ID:** `M2-G0-006C`
- **Name:** Feature Audit Slice E3 — extended roles and usability boundaries
- **Class:** forensic audit / prerequisite
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Objective:** Audit category-E rows 11-15 covering caregiver/household-manager, student, mixed/custom roles, older-adult usability and the rejected public “Boomer mode” boundary without entering later identity/sharing, distribution or implementation work.

## Audit rows in this packet

1. Caregiver and household-manager profiles.
2. Student profile and HOME/CAMPUS option.
3. Mixed/custom roles and preservation of underlying roles.
4. Older-adult usability/profile recommendations without age/ability inference.
5. “Boomer mode” as a private nickname/exclusion boundary rather than a public insulting mode.

Do not expand this packet to per-person identity/relationship permission schemas, personal-fork/upstream feature sharing, clean starter release mechanics, skill builder, automatic instruction updates, browser/provider installation, category F portability/distribution or product coding.

## Acceptance criteria

1. Each scoped behavior receives a stable semantic feature ID and explicit evidence boundary.
2. Caregiver and household-manager are explicit composable roles; their labels may recommend appropriate workflows but never infer ownership, health authority, family access or service activation.
3. Student is an explicit role and HOME/CAMPUS is a context recommendation/configuration under `CTX-*`, not a consequence automatically activated by the student label.
4. Mixed-role state preserves underlying roles and an explicit primary role; `mixed` is a summary, not a replacement identity. Custom roles cannot silently erase or impersonate established role semantics.
5. Older-adult usability is preference/capability configuration, not demographic inference. MIRA must not infer disability, medication, finances, competence or assistance needs from age/retirement labels.
6. “Boomer mode” remains prohibited as a public product/profile label. A user-selected private nickname/alias may exist only as private mutable state and cannot change capabilities, permissions or safety policy.
7. Existing deterministic router/tests and relevant onboarding/accessibility evidence are inspected; code existence is not promoted beyond its actual verification level.
8. Only `FEATURES.md`, `BACKLOG.md`, and `CURRENT_WORK.md` are intended packet changes.
9. A small PR is scope-verified, merged and remotely read back.
10. `CURRENT_WORK.md` advances to the next bounded category-E slice with an exact resume point.
11. No live Google production state and no executable MIRA 2.0 product behavior is changed.

## Exact next action

Create branch `audit/g0-006c-role-customization-foundations` from this current `main` checkpoint. Inspect category-E row 11: **Caregiver and household-manager profile behavior**, including role composition, recommendation versus activation, household-routine ownership boundaries and any direct deterministic tests.

## Next packet boundary

If E3 completes, `M2-G0-006D` audits the next five category-E rows: per-person identity/household-beneficiary relationships/permission scopes; personal fork and reviewed upstream feature sharing; standalone clean starter repository; self-improving/custom skill builder; automatic instruction-update behavior. Do not begin browser/provider installation or category F in E3.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head when tools permit;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture new customer ideas in BACKLOG unless required for acceptance or explicitly reprioritized;
6. before the final packet line, state any customer action needed; if none is needed, use `Just tell me to continue.`;
7. the final visible line remains the packet recovery tag.
