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
- **Branch:** `audit/g0-006d-identity-sharing-skill-foundations`
- **Base main SHA:** `cb64de3b4d6c10f49881bf74da647f6d72ae3000`
- **Status:** forensic evidence pass complete; `FEATURES.md`/`BACKLOG.md` normalization and final packet release still pending.

## Audit rows in this packet

1. Per-person identity, household/beneficiary relationships and permission scopes.
2. Personal fork plus reviewed upstream feature sharing.
3. Standalone clean starter repository/distribution boundary.
4. Self-improving/custom skill builder.
5. Automatic instruction-update behavior.

Do not expand this packet to browser/provider installation, alternative AI/runtime portability, Microsoft/Apple provider behavior, institutional deployment, category F, category G or product coding.

## Stable mappings chosen from the forensic pass

- `PROFILE-012` — canonical per-person identity and explicit household/beneficiary relationship graph.
- `PROFILE-013` — explicit permission/sharing scopes separate from relationship labels.
- `DIST-001` — private deployment lineage plus explicit sanitized/reviewed upstream feature sharing.
- `DIST-002` — deterministic sanitized starter/distribution generated from one canonical source revision.
- `DEV-004` — bounded custom skill/feature creation with declared dependencies, permissions, state, failure isolation, tests and private-by-default ownership.
- Existing `ONBOARD-001` — full-replacement instruction delivery, now audited as the durable fallback for automatic instruction updates when direct Project/Custom Instructions mutation is unavailable or unverified.

These mappings are durable in this checkpoint but still need their full canonical descriptions/evidence boundaries written into `FEATURES.md` before E4 can close.

## Completed forensic evidence

1. Historical ledger row 16 says per-person identity/household-beneficiary relationships/permission scopes are accepted, with private immutable IDs and an explicit prohibition against relationship labels granting custody, health or finance access.
2. `STATE_AUTHORITY_MODEL.md` defines a logical `People` authority, `Owner person UUID` on Authority Registry rows, stable logical identities surviving backend migration, and explicit personal/whole-authority/scoped-shared authority modes.
3. Sharing state and sharing a feature are explicitly different operations. Family access is never inferred; grants are recorded in the Authority Registry and provider/API access must be read back after the owner changes sharing.
4. Therefore E4 splits historical row 16 into `PROFILE-012` identity/relationship semantics and `PROFILE-013` authorization/sharing semantics. The generic Person/relationship model remains primarily data-model/specification evidence; the permission model is strongly specified but is not yet a complete MIRA 2.0 authorization implementation.
5. Existing `REIMB-001` beneficiary allocation is related evidence but does not replace a general Person/relationship authority. Beneficiary allocation and permission remain separate.
6. `PERSONAL_FORK_LIFECYCLE.md` defines one durable personal/managed source lineage, private mutable state outside Git, feature branches away from known-good state, explicit owner/lineage metadata, deliberate upgrades, rollback checkpoints and remote source readback.
7. That lifecycle contains an explicit portable-feature gate: private by default; ask exactly `Do you want to make this feature available to other people?`; sanitize personal identifiers/state; create synthetic fixtures; declare dependencies/permissions; run privacy/source/tests; show the exact public diff; publish only under explicit publication authority.
8. `SHARED_FEATURE_WORKFLOW.md` reinforces design privately → test → version → optionally sanitize → share; standing permission to commit/push a private deployment is never publication authority.
9. `test_feature_reconciliation.py` provides genuine deterministic evidence for user-owned feature preservation, owner/origin tracking, no silent ownership transfer, dependency-scoped blocking/degradation, proposal-only upgrades, keep-current default and rollback-checkpoint requirements.
10. Therefore `DIST-001` has test-verified ownership/reconciliation sub-behavior plus strongly specified publication/sanitization workflow; actual MIRA 2.0 upstream publication remains integration-unverified.
11. Historical row 18 defines a standalone clean starter release boundary. `distribution/README.md` says generated distributions are deterministic products of one exact canonical source revision and never independent development sources of truth.
12. Legacy `build-distributions.yml` deterministically builds personal/institutional distributions, runs public-source and starter-privacy audits, validates source revision/channel manifests, compiles code, runs dependency/feature reconciliation and starter tests, then re-audits the final generated tree.
13. Therefore `DIST-002` has real CI/test evidence at the legacy distribution boundary, while MIRA 2.0 still lacks its own remotely verified release/promotion proof.
14. Historical row 19 describes self-improving/custom skill creation as proposed/accepted direction. `SHARED_FEATURE_WORKFLOW.md` gives a concrete nontechnical flow: inspect existing behavior, define capability/state/failure contracts, branch, keep personal data out of portable source, record ownership/dependencies, add synthetic tests, verify private behavior, keep private by default and ask before sharing.
15. `test_feature_manifest.py` test-verifies important portable-feature gates including required manifest fields/runtime contracts, no personal data in shared source, safe paths, semantic versions, executable-test requirements for implemented status and closed schema validation.
16. Feature reconciliation tests additionally prove user ownership and dependency behavior. These are strong validator/tooling primitives, but no autonomous end-to-end “skill builder” engine was located. `DEV-004` therefore remains workflow/partial implementation rather than a completed builder.
17. Historical row 20 says automatic instruction updates were requested but technically constrained. `project/INSTRUCTIONS.md.tmpl` already requires a complete `PROJECT INSTRUCTIONS UPDATE` when direct Project write capability is unavailable.
18. Current MIRA project governance strengthens that into the durable full-replacement rule: when Project Instructions, global Custom Instructions or another instruction block must change, provide the complete replacement text plus simple nontechnical UI steps; never assume direct UI mutation capability.
19. E4 therefore maps row 20 to the existing `ONBOARD-001` rather than inventing a duplicate feature. Direct automatic UI mutation remains capability-gated/unverified; source-backed complete replacement delivery is the supported behavior.
20. No live Google production state or executable MIRA 2.0 product behavior was changed during this forensic pass.

## Evidence ceilings to preserve during normalization

- `PROFILE-012`: accepted; data-model/skill-workflow/specification evidence. No generic deterministic Person/relationship engine has been proven yet.
- `PROFILE-013`: privacy-critical and strongly specified; provider/API sharing readback contract exists, but complete generic authorization enforcement is not integration-verified.
- `DIST-001`: ownership/reconciliation core `test_verified`; sanitized public-contribution/publication path specified and CI-supported but not MIRA 2.0 live-verified.
- `DIST-002`: deterministic legacy distribution build/privacy/validation path `test_verified`/CI-enforced; MIRA 2.0 release/promotion/readback unverified.
- `DEV-004`: private feature workflow + manifest/dependency validators strongly implemented/test-supported; autonomous end-to-end builder not proven.
- `ONBOARD-001`: current required governance behavior; full replacement/source-backed fallback specified/implemented as process, direct Project/Custom Instructions write capability unverified.

## Acceptance criteria status

1. Stable semantic mapping/evidence boundary: **forensic mapping complete; canonical FEATURES write pending**.
2. Person identity/relationships separated from permission scopes: **complete in audit; FEATURES write pending**.
3. Private custom behavior/upstream sharing boundary: **complete in audit; FEATURES write pending**.
4. Clean starter/distribution source-of-truth boundary: **complete in audit; FEATURES write pending**.
5. Custom skill/self-extension dependency/privacy/test gates: **complete in audit; FEATURES write pending**.
6. Full-replacement instruction-update behavior: **complete in audit; ONBOARD-001 refinement pending**.
7. Relevant legacy evidence inspected without importing private state: **complete**.
8. Only authority files intended: **still satisfied**.
9. Small PR/merge/readback: **pending**.
10. Advance to next bounded category-E slice: **pending**.
11. No live production/product behavior changed: **satisfied**.

## Exact next action

Normalize the forensic findings into `FEATURES.md` using `PROFILE-012`, `PROFILE-013`, `DIST-001`, `DIST-002`, `DEV-004`, and an expanded/audited `ONBOARD-001`; then update `BACKLOG.md` with the corresponding MIRA 2.0 implementation gaps. After those two commits, checkpoint `CURRENT_WORK.md`, open the three-file E4 PR, verify/merge/read back, and activate E5.

## Planned implementation-gap IDs for BACKLOG normalization

- `PERSON-GRAPH-001` — canonical Person identity and relationship graph.
- `PERMISSION-SCOPE-001` — explicit scoped authorization/grants plus provider/API readback.
- `FEATURE-SHARE-001` — MIRA 2.0 private ownership/reconciliation and sanitized upstream contribution path.
- `DIST-STARTER-001` — MIRA 2.0 deterministic sanitized starter/distribution with source-revision/readback proof.
- `SKILL-BUILDER-001` — bounded private custom feature creation using manifests/dependencies/tests, later optional publication.
- Existing `ONBOARD-INSTRUCTIONS` — expand to cover source-backed complete replacement delivery and capability-gated direct writes under `ONBOARD-001`.

## Next packet boundary after E4 closes

Prefer two remaining onboarding slices rather than cramming six provider/install rows into one packet:

### `M2-G0-006E` — Feature Audit Slice E5 — nontechnical source/runtime onboarding

Audit category-E rows 21-24:
1. Browser-only nontechnical installation with no terminal fallback.
2. Independent ChatGPT GitHub read and Codex GitHub write gates.
3. Provider-neutral AI runtime capability routing.
4. Personal Git, organization Git, managed-central source and explicit no-Git lanes.

### `M2-G0-006F` — Feature Audit Slice E6 — provider onboarding/bootstrap and category-E closure

Audit category-E rows 25-26:
1. Browser-only Google, Microsoft 365/OneDrive, Apple/iCloud and alternative-AI onboarding.
2. Installable provider-neutral MIRA skill and deterministic Personal Google bootstrap.
3. Perform category-E consistency closure.

Do not begin category F inside E4.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head when tools permit;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture new customer ideas in BACKLOG unless required for acceptance or explicitly reprioritized;
6. before the final packet line, state any customer action needed; if none is needed, use `Just tell me to continue.`;
7. the final visible line remains the packet recovery tag.
