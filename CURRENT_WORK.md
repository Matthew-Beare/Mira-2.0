# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and its exact resume point.

## Active packet

- **Packet ID:** `M2-G0-006A`
- **Name:** Feature Audit Slice E1 — safe starter and onboarding foundations
- **Class:** forensic audit / prerequisite
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `audit/g0-006a-onboarding-foundations`
- **Base main SHA:** `a490b2dbf15985e49565c6fb89d65a420ed33f0e`
- **Feature audit commit:** `bbb2db77449c3b3cd70f43420c319bab80996ddf`
- **Backlog checkpoint commit:** `f36b4281d61942706d96d2f75655ff571cd5eafd`
- **Status:** acceptance work complete; PR/merge/readback pending.

## Completed acceptance evidence

1. Assigned five stable semantic features for category-E rows 1-5:
   - `ONBOARD-002` Sanitized generic starter with no inherited personal production state;
   - `ONBOARD-003` Four-question Minimum Useful Setup with resumable bounded interview;
   - `ONBOARD-004` Capability, friction, AI-use and work-context discovery without silent activation;
   - `ONBOARD-005` Explicit new-user brief cadence and canonical IANA timezone configuration;
   - `SERVICE-001` Explicit finite service activation state separate from capability and recommendation.
2. Added `ONBOARD-*` and `SERVICE-*` registry families so onboarding workflow and activation state are not hidden inside generic profile labels.
3. Verified the legacy starter privacy boundary is executable and CI-enforced: `audit_starter_privacy.py` rejects production markers, non-placeholder emails, concrete Google resource URLs, authority IDs and symlinks, while CI also performs full-history public-source audit before validation/tests.
4. Recorded `ONBOARD-002` as test/CI-enforced in legacy portable source while keeping MIRA 2.0 starter/distribution integration unverified; added `STARTER-SANITIZE-001`.
5. Verified `START_HERE.md` explicitly prohibits inheriting another deployment’s timezone, schedules, accounts, assets, routines, goals, IDs, configuration, aliases or state.
6. Recorded the exact four-question kickoff contract and `LIFE_INTERVIEW.md` bounded/resumable Interview Ledger behavior under `ONBOARD-003` without promoting the complete conversational flow to test-verified; added `FIRSTBOOT-CORE-001`.
7. Recorded AI-use/pain-point/job/duty/automation/app/service/constraint discovery under `ONBOARD-004`, with questions limited to decisions that affect workflow, dependency, schema, schedule, permission or recommendation.
8. Verified deterministic sub-boundaries for discovery: work-away/context recommendations require confirmation, catalog presence does not equal implementation, recommendations do not silently activate services, malformed inputs fail closed and context routing cannot change canonical timezone; added `DISCOVERY-CORE-001` for the untested end-to-end discovery flow.
9. Recorded new-user cadence/slot/IANA-timezone configuration under `ONBOARD-005`, explicitly separate from the current personal deployment’s audited schedule; added `ONBOARD-SCHEDULE-001` for persistence/readback and routing tests.
10. Verified `SERVICE-001` finite activation states `unresolved`, `enabled`, `disabled`, `not_applicable`, and `deferred` are deterministic/test-backed, with default unresolved, explicit enable/disable, conflict rejection, unknown-state failure and separate `requires_capability_verification` implementation status.
11. Added `SERVICE-STATE-001` to port/prove those tested semantics in MIRA 2.0 canonical configuration.
12. Preserved the rejected/unsafe universal-onboarding experiment as rejected evidence so it cannot silently become the current default through legacy branch/code resurrection.
13. Touched no live Google production state and changed no executable MIRA 2.0 product behavior.

## Key audit findings

- Starter sanitization is a privacy/source-lineage control, not merely onboarding copy.
- Minimum Useful Setup and the deeper life interview are separate phases; the user does not need to finish an exhaustive questionnaire before MIRA becomes useful.
- Discovery/recommendation is not authorization. Job title, duties or available provider capabilities may suggest services but never activate them.
- New-user cadence/timezone is deployment configuration, not inherited personal policy and not device/travel time.
- Service catalog presence, capability availability, recommendation and activation are four separate states/claims.

## Blockers

None inside this forensic packet. MIRA 2.0 implementation/integration work is separately ranked as `STARTER-SANITIZE-001`, `FIRSTBOOT-CORE-001`, `DISCOVERY-CORE-001`, `ONBOARD-SCHEDULE-001`, and `SERVICE-STATE-001`.

## Exact next action

Open a pull request from `audit/g0-006a-onboarding-foundations` to `main`, verify changed-file scope is limited to `FEATURES.md`, `BACKLOG.md`, and `CURRENT_WORK.md`, merge it, remotely read back E1, then activate `M2-G0-006B` on current `main` and create branch `audit/g0-006b-role-profile-foundations`.

## Next packet after merge

### `M2-G0-006B` — Feature Audit Slice E2 — role/profile foundations

Audit exactly category-E rows 6-10:

1. Working/self-employed profile behavior.
2. Retired profile behavior distinct from nonworking/unemployed state.
3. Nonworking/between-jobs profile behavior distinct from retirement.
4. Parent/guardian profile behavior and family/household recommendations.
5. Dependent child/minor profile behavior with privacy/permission safety boundaries.

Do not expand this packet to caregiver/household-manager/student/custom profiles, accessibility, family sharing implementation, provider portability, distribution or product coding.

The exact first unaudited behavior is **Working/self-employed profile behavior**.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head when tools permit;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture new customer ideas in BACKLOG unless required for acceptance or explicitly reprioritized;
6. before the final packet line, state any customer action needed; if none is needed, use `Just tell me to continue.`;
7. the final visible line remains the packet recovery tag.
