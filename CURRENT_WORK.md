# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and its exact resume point.

## Completed packet

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
- **Status:** forensic evidence pass complete; feature/backlog normalization and category-E closure pending.

## Stable feature mapping from forensic pass

1. `PROVIDER-002` — browser-only provider account/resource onboarding with exact identity, capability, bounded write and readback evidence plus explicit manual/degraded lanes.
2. `ONBOARD-007` — installable provider-neutral MIRA orchestration skill package; current internal package ID `life-planner` remains compatibility-only.
3. `PROVIDER-003` — deterministic Personal Google bootstrap adapter with module-scoped blueprint, plan hash and strict provider/source/readback verifier.

Historical category-E row 26 is intentionally split into `ONBOARD-007` and `PROVIDER-003` because portable MIRA onboarding behavior and the Personal Google adapter are different authorities/capabilities. Google is an adapter, not the product architecture.

## Forensic findings already established

1. `PROVIDER_ONBOARDING.md` defines browser-only provider lanes for Google Workspace, Microsoft 365/OneDrive/SharePoint, Apple/iCloud, Claude/other AI runtimes and institutional/VA deployment. Provider names and connection badges are not treated as capability proof.
2. Google onboarding requires exact identity plus bounded native Sheets/Drive read → write → readback; Gmail and Calendar are independently optional and independently verified when selected.
3. Microsoft onboarding requires exact organization identity and tenant, approved source mode and browser provider resources such as Microsoft Lists/Excel plus OneDrive/SharePoint. Local OneDrive sync is not canonical evidence and provider-created resources must be read back.
4. Apple/iCloud is explicitly a manual bridge unless a verified adapter proves otherwise: deliberate browser/mobile/file import/export may be supported, but unattended iCloud Drive, arbitrary mail automation or background sync must not be claimed without exact observed capability.
5. Alternative AI runtimes reuse the provider-neutral source/state contract only after the exact runtime actions are observed and verified; AI brand never proves feature parity.
6. Institutional/regulated provider setup starts with synthetic/public/non-sensitive data and requires current organization approval for the exact runtime, storage, identity, purpose and action set before regulated-sensitive data is admitted.
7. `install-flow.json` points to `PROVIDER_ONBOARDING.md`, requires structured-state/evidence provider gates with observed provider/resource plus bounded read/write/readback, and contains explicit blocked/manual-only states. `test_nontechnical_installation.py` regression-tests the Google/Microsoft/Apple/alternative-AI provider onboarding document and no-terminal/browser-only contract.
8. The actual portable new-user package is `starter/life-planner/`, not the personal `skill/ops-brief-policy` deployment skill. The package includes `SKILL.md`, Personal Google onboarding reference, module-scoped blueprint, deterministic bootstrap verifier and planning/control-cycle references.
9. `install-flow.json` names `life-planner` as the installable compatibility package and has an independent `life-planner-skill` capability gate. `test_nontechnical_installation.py` verifies the package, blueprint and verifier exist and that onboarding must not fall back to the developer/reference deployment skill.
10. `starter/life-planner/SKILL.md` routes provider/runtime behavior through canonical authorities, behavior dependency preflight and observed Integration Registry capability, and explicitly states that provider names or connection badges are not capability proof. Missing dependencies are surfaced in ordinary language and cannot silently install/connect/enable providers.
11. `personal-google-blueprint.json` defines one required `core` module plus optional planning, appointments, meal-planning, commerce, assets, job-watch and work-travel modules. Only selected modules create their declared workbooks/folders/tabs, preserving failure-domain isolation.
12. The core Google blueprint seeds deployment/source metadata, Authority Registry, Interview Ledger, Integration Registry, People, Services and Run Log; optional modules add only their declared logical authorities.
13. `google_bootstrap.py` validates blueprint provider/schema, module IDs, exact headers, IANA timezone, RFC 4122 UUIDs, exact source repository/SHA, boolean capability gates and Google identity before generating a deterministic plan hash.
14. The bootstrap plan records native Google Sheets requirements, spreadsheet timezone, exact module/failure-domain resources, owner-only Authority Registry rows, integration capability rows and optional Gmail/Calendar/scheduler tests.
15. The verifier checks the plan hash before readback, blocks source repository/commit/read/write/readback/CI drift, Google Drive identity mismatch, workbook/title/native-Sheets/timezone/provider-ID/URL/header/seed drift and folder readback gaps.
16. Optional Gmail, Calendar and first scheduled firing failures degrade only their selected paths. Manual use may remain ready while scheduled use remains unproven; full scheduled readiness requires observed firing.
17. `test_personal_google_bootstrap.py` directly regression-tests required/optional module selection, fail-closed unknown module/timezone/nonboolean configuration, exact ready readback, source/header/timezone/seed/identity drift, plan tampering, optional-provider degradation and strict failure behavior.
18. The Personal Google bootstrap is therefore genuinely `test_verified` as a deterministic plan/verifier core, but it does not itself create live Google resources and no MIRA 2.0 provider transaction has been live/integration verified.
19. The installable MIRA package is implemented and its installation/package-presence gate is test-verified, while a complete MIRA 2.0 new-user installed-skill runtime smoke remains unverified.
20. No live Google production state was touched and no executable MIRA 2.0 product behavior changed.

## Exact next action

Normalize `PROVIDER-002`, `ONBOARD-007`, and `PROVIDER-003` into `FEATURES.md`; add only the required MIRA 2.0 provider-onboarding/skill/bootstrap proof gaps to `BACKLOG.md`; perform category-E consistency closure and account for all 26 historical rows. Then update this file with final acceptance evidence and release E6 through the three-authority-file PR/merge/readback gate.

## Next packet after merge

### `M2-G0-007A` — Feature Audit Slice F1

Begin category F only after E6 is merged and category E is remotely read back as complete. Determine the exact first bounded F rows from the forensic ledger during the handoff; do not infer F scope from memory.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head when tools permit;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture new customer ideas in BACKLOG unless required for acceptance or explicitly reprioritized;
6. before the final packet line, state any customer action needed; if none is needed, use `Just tell me to continue.`;
7. the final visible line remains the packet recovery tag.
