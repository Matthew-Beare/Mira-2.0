# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and its exact resume point.

## Completed packet before this branch

### `M2-G0-006E` — Feature Audit Slice E5 — nontechnical source/runtime onboarding

- **Merged PR:** #18
- **Merge SHA:** `b8ca9f03634c3ca5764549bc18603b4cab3b04c5`
- **Main handoff commit activating E6:** `499786a9a48667fdbb83333a6a20a9a492c08f40`
- **Live Google production touched:** no.
- **Executable product behavior changed:** no.

## Active packet

- **Packet ID:** `M2-G0-006F`
- **Name:** Feature Audit Slice E6 — provider onboarding/bootstrap and category-E closure
- **Class:** forensic audit / prerequisite
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `audit/g0-006f-provider-bootstrap-category-e-closure`
- **Branch start SHA:** `499786a9a48667fdbb83333a6a20a9a492c08f40`
- **Research checkpoint commit:** `fde54ab0fba1bb90ac65fad210fe08a13905a604`
- **Feature registry commit:** `9fa959c3a8dd9a8046cedab85329c8f6e6e524cf`
- **Backlog checkpoint commit:** `bad393ca23cb91f021f5c3a0d1e763db5f00381b`
- **Status:** acceptance work complete; PR/merge/readback pending.

## Completed acceptance evidence

1. Assigned stable semantic feature IDs for the two remaining historical category-E rows while splitting row 26 only where authority/capability boundaries require it:
   - `PROVIDER-002` — browser-only provider account/resource onboarding with exact identity/resource/action readback;
   - `ONBOARD-007` — installable provider-neutral MIRA orchestration skill package;
   - `PROVIDER-003` — deterministic Personal Google bootstrap adapter with strict drift/readback verification.
2. Preserved provider-account/resource onboarding separately from AI-runtime capability routing (`PROVIDER-001`) and durable source mode/capability (`SOURCE-001`/`SOURCE-002`).
3. Preserved ordinary-user browser/no-terminal behavior. Missing provider/runtime/source capability remains blocked or explicit manual/degraded state rather than triggering a CLI workaround.
4. Recorded Google, Microsoft 365/OneDrive/SharePoint, Apple/iCloud and alternative-AI onboarding differences honestly. Apple/iCloud remains user-mediated/manual unless an exact adapter proves unattended actions.
5. Recorded exact provider onboarding evidence requirements: signed-in identity/tenant where relevant, narrowly scoped resource, provider ID/URL, action scope, bounded read, approved synthetic write when needed and readback of the exact provider record.
6. Preserved regulated-sensitive data gating behind current organization approval for the exact runtime, storage, purpose and action set.
7. Established `ONBOARD-007` as the provider-neutral portable MIRA orchestration package. The historical `life-planner` ID is compatibility-only and must not become product branding or a route to the developer/reference deployment’s personal Ops state.
8. Established `PROVIDER-003` as a provider adapter beneath MIRA rather than product architecture. Google resource shapes are not universal MIRROR schema requirements.
9. Verified the legacy Personal Google deterministic core is genuinely test-verified for selected-module planning, exact source repo/SHA, UUID/IANA-timezone/config validation, plan hashing, provider identity/resource/header/seed/timezone drift, optional Gmail/Calendar/scheduler degradation and strict failure behavior.
10. Preserved module-scoped provisioning: one required core authority plus only explicitly selected optional modules/failure domains.
11. Preserved the bootstrap readiness distinction between manual readiness and scheduled readiness; a selected recurring schedule is not fully proven until an observed firing exists.
12. Added ranked MIRA 2.0 implementation work:
   - `MIRA-SKILL-001`;
   - `PROVIDER-ONBOARD-001`;
   - `GOOGLE-BOOTSTRAP-001`.
13. Updated `NONTECH-INSTALL-001` and `CORE-ROUNDTRIP` dependencies so the future personal Google vertical cannot bypass portable-skill/provider/bootstrap prerequisites.
14. Reconciled all 26 historical category-E rows. Combined historical rows were split only where different identity, authorization, runtime, source, provider or adapter verification boundaries require it.
15. Marked category E complete in `FEATURES.md` and `BACKLOG.md`; categories F and G remain unaudited.
16. Verified the `FEATURES.md` normalization diff is bounded: 80 additions and 8 deletions, with the deletions limited to the stale pre-E6 audit-status block.
17. Touched no live Google production state and changed no executable MIRA 2.0 product behavior.

## Key category-E closure findings

- Profile/relationship identity, authorization, source access, runtime capability, provider-resource access and service activation are distinct facts.
- Browser installation does not prove source write or provider mutation.
- Source read does not prove source write; source write does not prove provider-state mutation.
- AI/provider names and connection badges do not prove capability or organization approval.
- The portable MIRA skill owns orchestration behavior; provider adapters implement exact external-resource transactions beneath it.
- Personal Google is the current first provider vertical, not the universal MIRA/MIRROR architecture.
- Manual portability is allowed to be manual. MIRA must not relabel import/export or ICS handoff as unattended synchronization.
- Legacy deterministic tests can justify `test_verified` core/contract evidence, but MIRA 2.0 integration/live status still requires synthetic new-repo/runtime/provider execution and remote readback.

## Blockers

None inside this forensic packet. The newly ranked provider/skill/bootstrap work remains post-audit prerequisite implementation and does not block closing the historical category-E audit.

## Exact next action

Open a pull request from `audit/g0-006f-provider-bootstrap-category-e-closure` to `main`, verify changed-file scope is limited to `FEATURES.md`, `BACKLOG.md`, and `CURRENT_WORK.md`, merge it, remotely read back category-E closure on `main`, then inspect the authoritative legacy forensic ledger for category F and activate `M2-G0-007A` from current `main` with the exact first bounded F rows recorded in `CURRENT_WORK.md` before creating its audit branch.

## Next packet after merge

### `M2-G0-007A` — Feature Audit Slice F1

Begin category F only after E6 is merged and remotely read back as complete. Determine the exact F1 rows/scope from the authoritative forensic ledger at handoff rather than from conversational memory. Do not expand into category G or executable MIRA 2.0 product coding.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head when tools permit;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture new customer ideas in BACKLOG unless required for acceptance or explicitly reprioritized;
6. before the final packet line, state any customer action needed; if none is needed, use `Just tell me to continue.`;
7. the final visible line remains the packet recovery tag.
