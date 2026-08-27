# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and its exact resume point.

## Completed packet

### `M2-G0-006C` — Feature Audit Slice E3 — extended roles and usability boundaries

- **Merged PR:** #16
- **Merge SHA:** `0c2b698efa5959fba8691dfc351d485fab7de5fb`
- **Audited features:** `PROFILE-006`, `PROFILE-007`, `PROFILE-008`, `PROFILE-009`, `PROFILE-010`, `PROFILE-011`
- **Result:** caregiver, household-manager, student, mixed/custom, preference-driven usability and the rejected public “Boomer mode” boundary are normalized at their actual evidence levels.
- **Live Google production touched:** no.
- **Executable product behavior changed:** no.

## Active packet

- **Packet ID:** `M2-G0-006D`
- **Name:** Feature Audit Slice E4 — identity, sharing and self-extension foundations
- **Class:** forensic audit / prerequisite
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Objective:** Audit category-E rows 16-20 covering per-person/relationship identity and permissions, personal-fork/upstream sharing, clean starter boundaries, custom skill creation and automatic instruction updates without entering provider installation, portability or product coding.

## Audit rows in this packet

1. Per-person identity, household/beneficiary relationships and permission scopes.
2. Personal fork plus reviewed upstream feature sharing.
3. Standalone clean starter repository/distribution boundary.
4. Self-improving/custom skill builder.
5. Automatic instruction-update behavior.

Do not expand this packet to browser/provider installation, alternative AI/runtime portability, Microsoft/Apple provider behavior, institutional deployment, category F, category G or product coding.

## Acceptance criteria

1. Each scoped behavior receives a stable semantic feature ID and explicit evidence boundary.
2. Person identity, household/beneficiary relationships and permission scopes are distinct. Relationship labels never grant access; shared state requires explicit scoped authorization and provider/API readback.
3. Personal forks/deployments may preserve private custom behavior while reusable upstream contributions require explicit user publication approval, sanitization, tests and reviewed source changes; private mutable state never rides upstream.
4. A clean starter/distribution is generated from canonical portable source and remains separate from protected legacy production state; it is not an independent development source of truth.
5. Custom skill/self-extension behavior is bounded by explicit capability, dependency, privacy and test gates; generated features do not silently become enabled or publish themselves.
6. Automatic instruction updates follow the project full-replacement rule: produce the complete replacement block, preserve durable source/version evidence, and never rely on fragmentary patch instructions unless explicitly requested.
7. Relevant legacy source/workflow/tests are inspected without importing private operational data or unmerged tainted history.
8. Only `FEATURES.md`, `BACKLOG.md`, and `CURRENT_WORK.md` are intended packet changes.
9. A small PR is scope-verified, merged and remotely read back.
10. `CURRENT_WORK.md` advances to the next bounded category-E slice with an exact resume point.
11. No live Google production state and no executable MIRA 2.0 product behavior is changed.

## Exact next action

Create branch `audit/g0-006d-identity-sharing-skill-foundations` from this current `main` checkpoint. Inspect category-E row 16: **Per-person identity, household/beneficiary relationships and permission scopes**, including immutable Person identity, relationship identity versus authorization, beneficiary allocation semantics, explicit sharing grants and readback.

## Next packet boundary

If E4 completes, `M2-G0-006E` audits the remaining category-E rows covering browser-only/nontechnical installation, provider/capability onboarding boundaries and related onboarding closure, then closes category E. Do not begin category F inside E4.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head when tools permit;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture new customer ideas in BACKLOG unless required for acceptance or explicitly reprioritized;
6. before the final packet line, state any customer action needed; if none is needed, use `Just tell me to continue.`;
7. the final visible line remains the packet recovery tag.
