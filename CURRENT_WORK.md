# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and its exact resume point.

## Active packet

- **Packet ID:** `M2-G0-006C`
- **Name:** Feature Audit Slice E3 — extended roles and usability boundaries
- **Class:** forensic audit / prerequisite
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `audit/g0-006c-role-customization-foundations`
- **Base main SHA:** `22b8eed925daee868fe34ef494b3a63044f07e50`
- **Feature audit commit:** `b0938a638a48f0e715f98576d39457b9e4823653`
- **Backlog checkpoint commit:** `6db0895530617df0bd0ca832deba6663d2362a12`
- **Status:** acceptance work complete; PR/merge/readback pending.

## Completed acceptance evidence

1. Split category-E row 11 into separate `PROFILE-006` caregiver and `PROFILE-007` household-manager features because their safety and recommendation boundaries differ.
2. Recorded `PROFILE-006` caregiver as an explicit composable role whose health/appointment/household recommendations never grant authority or activation. Legacy router implementation exists, but no dedicated caregiver-only regression fixture was located.
3. Preserved `REMIND-001`, `REMIND-002`, `SERVICE-001` and explicit Person/relationship permission state as independent gates for caregiver-related behavior.
4. Recorded `PROFILE-007` household-manager and verified direct legacy regression coverage for household-routine recommendation/activation, washer-to-dryer and pickup examples, consolidated delivery instead of per-chore automations and prohibited ownership inference.
5. Recorded `PROFILE-008` student as a first-class role with HOME/CAMPUS available only through explicit/recommended context configuration. The audited router does not auto-select HOME/CAMPUS from the student role alone.
6. Preserved dependent-minor precedence when student and dependent-minor roles coexist.
7. Recorded `PROFILE-009` mixed/custom role composition and verified direct tests for underlying-role preservation, explicit primary role, dependent-minor primary precedence, duplicate/contradictory role rejection, unsupported-role failure and custom-plus-known-role rejection.
8. Recorded `PROFILE-010` preference-driven usability/accessibility without demographic inference. Legacy evidence test-supports the non-inference boundary, while a full accessibility/preference engine is not present.
9. Recorded `PROFILE-011` as a durable negative constraint: public “Boomer mode” is rejected/superseded; a private user-selected alias may exist only as private presentation state and cannot change roles, permissions, activation, capabilities or safety policy.
10. Added ranked work items `PROFILE-CARE-001`, `PROFILE-HOUSEHOLD-001`, `PROFILE-STUDENT-001`, `PROFILE-MIXED-001`, `PROFILE-USABILITY-001`, and `PROFILE-LABEL-001`.
11. Kept caregiver/parent/minor shared-state authorization dependent on the later explicit Person/relationship permission authority rather than treating role labels as access control.
12. Touched no live Google production state and changed no executable MIRA 2.0 product behavior.

## Key audit findings

- Caregiver and household-manager are separate roles; neither is an authorization token.
- Household-manager routing has genuine anti-fan-out/no-ownership-inference regression evidence.
- Student role and HOME/CAMPUS context are separate facts; the role alone does not activate the context.
- `mixed` is presentation summary only; canonical roles remain individually preserved.
- Accessibility/usability must follow explicit preferences or device capability, never age/retirement stereotypes.
- Public “Boomer mode” remains rejected. Private aliases are presentation-only mutable state.

## Blockers

None inside this forensic packet. Shared-care/family authorization remains dependent on the explicit Person/relationship permission model to be audited in E4.

## Exact next action

Open a pull request from `audit/g0-006c-role-customization-foundations` to `main`, verify changed-file scope is limited to `FEATURES.md`, `BACKLOG.md`, and `CURRENT_WORK.md`, merge it, remotely read back E3, then activate `M2-G0-006D` on current `main` and create branch `audit/g0-006d-identity-sharing-skill-foundations`.

## Next packet after merge

### `M2-G0-006D` — Feature Audit Slice E4 — identity, sharing and self-extension foundations

Audit exactly category-E rows 16-20:

1. Per-person identity, household/beneficiary relationships and permission scopes.
2. Personal fork plus reviewed upstream feature sharing.
3. Standalone clean starter repository/distribution boundary.
4. Self-improving/custom skill builder.
5. Automatic instruction-update behavior.

Do not expand this packet to browser/provider installation, alternative runtime/provider portability, institutional deployment, category F, category G or product coding.

The exact first unaudited behavior is **Per-person identity, household/beneficiary relationships and permission scopes**.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head when tools permit;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture new customer ideas in BACKLOG unless required for acceptance or explicitly reprioritized;
6. before the final packet line, state any customer action needed; if none is needed, use `Just tell me to continue.`;
7. the final visible line remains the packet recovery tag.
