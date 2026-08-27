# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and its exact resume point.

## Completed packet before this branch

### `M2-G0-006C` — Feature Audit Slice E3 — extended roles and usability boundaries

- **Merged PR:** #16
- **Merge SHA:** `0c2b698efa5959fba8691dfc351d485fab7de5fb`
- **Live Google production touched:** no.
- **Executable product behavior changed:** no.

## Active packet

- **Packet ID:** `M2-G0-006D`
- **Name:** Feature Audit Slice E4 — identity, sharing and self-extension foundations
- **Class:** forensic audit / prerequisite
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `audit/g0-006d-identity-sharing-skill-foundations`
- **Base main SHA:** `cb64de3b4d6c10f49881bf74da647f6d72ae3000`
- **Research checkpoint commit:** `e05780a2475236f14454b2c29b9bb70cec1d553e`
- **Feature registry commit:** `fe3e0fafbc4293d0e64da57f14a1f65a3f694f39`
- **Backlog checkpoint commit:** `797b76385c1eb4b3d3556fa4efd496bbe9b64113`
- **Status:** acceptance work complete; PR/merge/readback pending.

## Completed acceptance evidence

1. Normalized category-E rows 16-20 into stable semantic features without duplicating existing authority:
   - `PROFILE-012` canonical per-person identity and explicit relationship graph;
   - `PROFILE-013` explicit permission/sharing scopes separate from relationships;
   - `DIST-001` private deployment lineage plus controlled sanitized upstream sharing;
   - `DIST-002` deterministic sanitized distributions from one canonical source revision;
   - `DEV-004` bounded private custom skill/feature creation;
   - historical automatic instruction updates refined existing `ONBOARD-001` rather than creating a duplicate feature.
2. Split Person/relationship truth from authorization. Household, beneficiary, parent, guardian, caregiver, spouse/partner or dependent relationships never grant access.
3. Recorded `PROFILE-012` at specification/data-model evidence because no generic deterministic Person/relationship engine has yet been proven.
4. Recorded `PROFILE-013` as a privacy-critical prerequisite. Sharing requires an explicit actor/resource/action scope plus provider/API readback; generic enforcement remains unverified.
5. Verified legacy feature-reconciliation tests provide genuine deterministic evidence for user-owned feature preservation, owner/origin tracking, no silent ownership transfer, dependency-scoped block/degrade behavior, proposal-only upgrades, keep-current default and rollback checkpoints.
6. Preserved private-by-default upstream sharing semantics: a reusable feature is sanitized with synthetic fixtures and exact-diff review; private source-write authority is never publication authority.
7. Verified the legacy distribution boundary deterministically builds generated channels from one exact source SHA and runs privacy/source/manifest/dependency/feature/test gates. Generated distributions are not independent sources of truth.
8. Recorded `DEV-004` as workflow/partial implementation only. Manifest/reconciliation validators are strong primitives but do not prove an autonomous end-to-end builder.
9. Refined `ONBOARD-001` to require complete replacement text, exact target naming and nontechnical UI steps whenever direct Project/Custom Instructions write/readback capability is unavailable or unverified.
10. Added ranked MIRA 2.0 work items `PERSON-GRAPH-001`, `PERMISSION-SCOPE-001`, `FEATURE-SHARE-001`, `DIST-STARTER-001`, `SKILL-BUILDER-001`, and expanded `ONBOARD-INSTRUCTIONS`.
11. Ranked `PERMISSION-SCOPE-001` as a privacy/integrity blocker for parent/minor/caregiver shared-state promotion.
12. Rewired earlier parent/minor/caregiver dependencies to the now-canonical `PROFILE-012`/`PROFILE-013` authority instead of leaving “E4 pending” placeholders.
13. Touched only `FEATURES.md`, `BACKLOG.md`, and `CURRENT_WORK.md` on this packet branch.
14. Touched no live Google production state and changed no executable MIRA 2.0 product behavior.

## Key audit findings

- Person identity, relationship, beneficiary allocation and authorization are distinct facts.
- Sharing state and sharing source/features are separate operations with separate approval and readback boundaries.
- User-owned private features are preserved by default; upstream changes are proposals, not authority to overwrite local behavior.
- Generated distributions are release products of canonical source, not alternate development branches.
- Custom feature creation can be customer-language driven while still requiring bounded contracts, dependencies, tests and private-by-default ownership.
- Direct instruction-surface mutation is a capability claim, not an assumption; full replacement remains the reliable fallback.

## Blockers

None inside this forensic packet. `PERMISSION-SCOPE-001` is a post-audit privacy blocker before shared family/caregiver/minor capabilities can be promoted.

## Exact next action

Open a pull request from `audit/g0-006d-identity-sharing-skill-foundations` to `main`, verify changed-file scope is limited to `FEATURES.md`, `BACKLOG.md`, and `CURRENT_WORK.md`, merge it, remotely read back E4, then activate `M2-G0-006E` on current `main` and create branch `audit/g0-006e-nontechnical-source-runtime-onboarding`.

## Next packet after merge

### `M2-G0-006E` — Feature Audit Slice E5 — nontechnical source/runtime onboarding

Audit exactly category-E rows 21-24:

1. Browser-only nontechnical installation with no terminal fallback.
2. Independent ChatGPT GitHub read and Codex GitHub write gates.
3. Provider-neutral AI runtime capability routing.
4. Personal Git, organization Git, managed-central source and explicit no-Git lanes.

Do not expand this packet to Google/Microsoft/Apple state-provider onboarding, Personal Google bootstrap, category F, category G or product coding.

The exact first unaudited behavior is **Browser-only nontechnical installation with no terminal fallback**.

## Packet after E5

### `M2-G0-006F` — Feature Audit Slice E6 — provider onboarding/bootstrap and category-E closure

Audit category-E rows 25-26, then close category E.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head when tools permit;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture new customer ideas in BACKLOG unless required for acceptance or explicitly reprioritized;
6. before the final packet line, state any customer action needed; if none is needed, use `Just tell me to continue.`;
7. the final visible line remains the packet recovery tag.
