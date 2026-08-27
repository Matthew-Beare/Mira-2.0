# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and its exact resume point.

## Active packet

- **Packet ID:** `M2-G0-006B`
- **Name:** Feature Audit Slice E2 — role/profile foundations
- **Class:** forensic audit / prerequisite
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `audit/g0-006b-role-profile-foundations`
- **Base main SHA:** `8dd07d6e68d26791c82f408b6dbb25881222b2c8`
- **Feature audit commit:** `59abb34c57ebcb472343344f9ca3ac646edade34`
- **Backlog checkpoint commit:** `29e179297e77d2a7737ebf41f6b693b2ee63ae50`
- **Status:** acceptance work complete; PR/merge/readback pending.

## Completed acceptance evidence

1. Assigned five stable semantic features for category-E rows 6-10:
   - `PROFILE-001` composable working/self-employed roles with evidence-gated work-context routing;
   - `PROFILE-002` retired role distinct from nonworking with respectful opt-in support;
   - `PROFILE-003` nonworking/between-jobs role distinct from retirement;
   - `PROFILE-004` parent/guardian as a first-class composable role with permission-scoped recommendations;
   - `PROFILE-005` dependent-minor role with primary routing and explicit privacy/permission gates.
2. Verified the legacy deterministic router keeps working and self-employed as explicit roles, supports role composition, requires an explicit primary role when multiple non-minor roles apply, and never equates recommendation with activation.
3. Recorded `PROFILE-001` as implemented with important working-role context paths test-verified, while keeping the self-employed path below full test verification because no dedicated audited self-employed fixture was located.
4. Verified job-title/context behavior: confirmed recurring away-work may recommend HOME/ROAD, HOME/TRUCK, HOME/FIELD or HOME/AWAY; explicitly-not-away bypasses context; suggestive job titles without recurring-away evidence require confirmation; custom labels require explicit configuration.
5. Verified `PROFILE-002` retired behavior with direct tests for public label `Retired`, `Personal Schedule & Wellbeing` support template, work-context bypass, appointment/medication recommendations remaining unresolved, private alias storage, opt-in reminder semantics and prohibited age/ability inference.
6. Verified retirement and nonworking are distinct deterministic roles. `not working`, `between jobs`, `not employed`, `nonworking` and `unemployed` normalize to nonworking rather than retired.
7. Recorded `PROFILE-003` as test-verified for retired/nonworking classification distinction while keeping the full nonworking transition/recommendation persistence path below integration verification.
8. Verified `PROFILE-004` parent/guardian composition with working, mixed-profile behavior, family/school brief focus, explicit-primary-role enforcement and recommendation/activation separation.
9. Inspected the state-authority sharing contract: family access is never inferred; sharing requires an explicit owner-approved whole-authority or scoped authority grant plus provider/API readback.
10. Preserved the permission boundary that a parent/guardian relationship label grants no custody, calendar, school, health, financial or sharing authority.
11. Verified `PROFILE-005` dependent-minor behavior with direct tests: dependent-minor remains primary when combined with student, default away-context routing is bypassed, and custom HOME/CAMPUS or other recurring away context requires explicit approval/evidence.
12. Preserved minimum-necessary/private-state and no-inferred-family-access requirements for dependent-minor data. Dedicated custody/guardian authorization, family-school execution and provider sharing remain unverified.
13. Added ranked MIRA 2.0 work items `PROFILE-WORK-001`, `PROFILE-RETIRED-001`, `PROFILE-NONWORKING-001`, `PROFILE-PARENT-001`, and `PROFILE-MINOR-001`.
14. Kept privacy-sensitive parent/minor permission work as prerequisites for those features rather than pretending the existing router is an authorization system.
15. Touched no live Google production state and changed no executable MIRA 2.0 product behavior.

## Key audit findings

- A role is descriptive/routing state, not a permission and not service activation.
- Working/self-employed may shape recommendations, but employment does not prove travel and self-employment does not grant business/finance permissions.
- Retirement and nonworking are materially different states and must stay separate.
- Retired does not imply age, disability, illness, medication use or reduced competence.
- Parent/guardian and dependent-minor labels never grant access to another person’s state.
- Dependent-minor routing deliberately fails safer: it stays primary and recurring away context requires explicit approval.
- Family sharing is a separate authority/permission workflow with explicit scope and readback.

## Blockers

None inside this forensic packet. `PROFILE-PARENT-001` and `PROFILE-MINOR-001` are privacy-sensitive prerequisites before those shared/family capabilities can be promoted; the remaining profile ports are separately ranked hardening work.

## Exact next action

Open a pull request from `audit/g0-006b-role-profile-foundations` to `main`, verify changed-file scope is limited to `FEATURES.md`, `BACKLOG.md`, and `CURRENT_WORK.md`, merge it, remotely read back E2, then activate `M2-G0-006C` on current `main` and create branch `audit/g0-006c-role-customization-foundations`.

## Next packet after merge

### `M2-G0-006C` — Feature Audit Slice E3 — extended roles and usability boundaries

Audit exactly category-E rows 11-15:

1. Caregiver and household-manager profiles.
2. Student profile and HOME/CAMPUS option.
3. Mixed/custom roles and preservation of underlying roles.
4. Older-adult usability/profile recommendations without age/ability inference.
5. “Boomer mode” as a private nickname/exclusion boundary rather than a public insulting mode.

Do not expand this packet to per-person identity/relationship permission schemas, personal-fork/upstream feature sharing, clean starter release mechanics, skill builder, automatic instruction updates, browser/provider installation, category F portability/distribution or product coding.

The exact first unaudited behavior is **Caregiver and household-manager profile behavior**.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head when tools permit;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture new customer ideas in BACKLOG unless required for acceptance or explicitly reprioritized;
6. before the final packet line, state any customer action needed; if none is needed, use `Just tell me to continue.`;
7. the final visible line remains the packet recovery tag.
