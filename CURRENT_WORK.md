# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and its exact resume point.

## Completed packet

### `M2-G0-006D` — Feature Audit Slice E4 — identity, sharing and self-extension foundations

- **Merged PR:** #17
- **Merge SHA:** `5027bb4882e3455b47b8c0a0957f972296bb51fe`
- **Audited features:** `PROFILE-012`, `PROFILE-013`, `DIST-001`, `DIST-002`, `DEV-004`, plus E4 refinement of `ONBOARD-001`.
- **Result:** Person/relationship identity is separate from permission scopes; private feature ownership/sharing, deterministic distribution, bounded custom feature creation and full-replacement instruction delivery are normalized at their actual evidence levels.
- **Live Google production touched:** no.
- **Executable product behavior changed:** no.

## Active packet

- **Packet ID:** `M2-G0-006E`
- **Name:** Feature Audit Slice E5 — nontechnical source/runtime onboarding
- **Class:** forensic audit / prerequisite
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `audit/g0-006e-nontechnical-source-runtime-onboarding`
- **Base main SHA:** `5027bb4882e3455b47b8c0a0957f972296bb51fe`
- **Status:** active; forensic evidence pass not yet complete.

## Audit rows in this packet

Audit exactly category-E rows 21-24:

1. Browser-only nontechnical installation with no terminal fallback.
2. Independent ChatGPT GitHub read and Codex GitHub write gates.
3. Provider-neutral AI runtime capability routing.
4. Personal Git, organization Git, managed-central source and explicit no-Git lanes.

Do not expand this packet to Google/Microsoft/Apple state-provider onboarding, Personal Google bootstrap, category F, category G or product coding.

## Acceptance criteria

1. Assign stable semantic feature IDs for all four rows without duplicating existing features.
2. Separate nontechnical installation UX from underlying source-control/runtime capabilities.
3. Preserve the no-terminal default and fail closed when the required browser/runtime capability is unavailable.
4. Separate GitHub read capability from source-write capability and require exact repository/readback verification.
5. Model AI runtime support from observed capabilities/actions/readback rather than provider/brand name.
6. Distinguish personal Git, approved organization Git, managed central source and explicit no-Git/manual lanes without forcing a personal Git account on institutional users.
7. Preserve privacy/security/public-source boundaries from E1-E4.
8. Record actual evidence ceilings; do not promote Markdown contracts or provider names to integration/live evidence.
9. Add only required implementation gaps to `BACKLOG.md` and rank by dependency/security/value.
10. Touch only `FEATURES.md`, `BACKLOG.md`, and `CURRENT_WORK.md` unless a hard audit dependency requires another authority-file change.
11. Open a small PR, verify changed-file scope, merge, and remotely read back before activating E6.
12. Touch no live Google production state and change no executable MIRA 2.0 product behavior.

## Exact next action

Inspect the legacy evidence for **Browser-only nontechnical installation with no terminal fallback**, especially `INSTALL.md`, onboarding capability/readback contracts and their tests. Then inspect the independent ChatGPT-read/Codex-write gates, provider-neutral runtime router and source-mode contracts. Normalize only after the evidence ceilings are established.

## Next packet after merge

### `M2-G0-006F` — Feature Audit Slice E6 — provider onboarding/bootstrap and category-E closure

Audit category-E rows 25-26:
1. Browser-only Google, Microsoft 365/OneDrive, Apple/iCloud and alternative-AI onboarding.
2. Installable provider-neutral MIRA skill and deterministic Personal Google bootstrap.
3. Perform category-E consistency closure.

Do not begin category F inside E5.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head when tools permit;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture new customer ideas in BACKLOG unless required for acceptance or explicitly reprioritized;
6. before the final packet line, state any customer action needed; if none is needed, use `Just tell me to continue.`;
7. the final visible line remains the packet recovery tag.
