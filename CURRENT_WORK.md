# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and its exact resume point.

## Completed packet before this branch

### `M2-G0-007G` — Feature Audit Slice F7 — travel planning and work-trip/pay composition

- **Merged PR:** #26
- **Merge SHA:** `ad9a97a74ac0cec164a6b0f424dd47407bbebeaa`
- **Main handoff commit activating F8:** `3db7203c9f7f1b232c63122e94f478898c1ae975`
- **Result:** no `TRAVEL-*` authority; F16 composes `TRIP-001` + `ROUTE-001`; F17 adds independent `MILE-001` + `MILE-002` when paid-work tracking is selected; ordered multi-leg grouping/revision remains `TRIP-ROUTE-CORE-001`.
- **Remote readback:** F7 registry/backlog verified on `main`.

## Active packet

- **Packet ID:** `M2-G0-007H`
- **Name:** Feature Audit Slice F8 — assets/maintenance/warranties/manuals service composition
- **Class:** forensic audit / prerequisite
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `audit/g0-007h-asset-service`
- **Branch start SHA:** `3db7203c9f7f1b232c63122e94f478898c1ae975`
- **Status:** forensic evidence complete; registry/backlog normalization next.

## Exact category-F scope

18. **Assets/maintenance/warranties/manuals**.

F19 is excluded because legacy `f-19` requires still-unaudited G17/G18. Do not expand into F19+, category G, or executable MIRA 2.0 coding.

## Research checkpoint findings

1. Legacy `onboarding_profile_router.py` exposes the exact independent service key `assets`; `knowledge` is a different service key. The generic router test proves every catalogued service defaults to `unresolved` with `requires_capability_verification`, so catalog/recommendation never proves activation or implementation.
2. `household_manager` may recommend `assets`, but role/recommendation does not activate it or infer ownership/responsibility.
3. Legacy F18 decision is **ACCEPTED**, current status **skill workflow/contracts**.
4. Legacy `behavior-dependencies.json` hard-requires D1-D7 for `f-18`.
5. Category-D normalization maps those historical rows as follows:
   - D1 → `ASSET-001` plus `FITMENT-001` where assignment/fitment is selected;
   - D2 → `ASSET-002` acquisition/reference/lifecycle evidence;
   - D3 → `ASSET-003` bidirectional graph queries;
   - D4 → `IDENT-001` namespaced identifiers;
   - D5 → `EVID-001` multi-source enrichment;
   - D6 → `KNOW-001` retained manuals/reference knowledge;
   - D7 → `SPEC-001` verified technical specifications.
6. No new `ASSET-*`, maintenance, warranty or manual authority is justified by F18. The user-facing `assets` service is composition over those already-canonical authorities.
7. Legacy F18's all-D1-D7 readiness is too broad after category-D normalization. `SERVICE-002` selected-path semantics should apply:
   - base asset registry/query path requires `ASSET-001` + `ASSET-003`;
   - fitment/assignment path adds `FITMENT-001`;
   - identifier/evidence enrichment path adds `IDENT-001` + `EVID-001` as applicable;
   - maintenance/warranty/reference-evidence path adds `ASSET-002`; full structured maintenance/warranty lifecycle remains existing backlog gap `ASSET-SERVICE-001`;
   - retained-manual path adds `KNOW-001`;
   - verified-specification path adds `SPEC-001` and its exact provenance requirements.
8. Missing manual/spec/fitment/warranty capability must not block a user who selected only basic asset registry/query. Conversely, a working base path cannot make an unavailable selected maintenance/manual/spec path appear ready.
9. `KNOW-001` retained status requires real retained-document identity/revision evidence; filename/URL presence alone cannot satisfy the manual path.
10. `SPEC-001` remains the only authority for verified safety-critical technical values, including exact applicability and source provenance. Service activation cannot promote candidate/OCR/owner-memory values to verified.
11. `ASSET-002` generic evidence support does not prove a complete maintenance/warranty lifecycle. Existing `ASSET-SERVICE-001` remains the correct implementation gap; F18 creates no duplicate engine.
12. Service activation/recommendation cannot infer physical ownership, `installed_on`, warranty coverage, maintenance completion, manual retention or specification correctness.
13. Category-D deterministic cores retain their existing evidence levels. The F18 service wrapper receives no MIRA 2.0 integration/live credit until selected service state and provider-backed paths are integrated/read back.
14. PR #31 inventory/assets/manual candidates remain reference/salvage evidence already bounded by category D; no F18-specific implementation found that raises the service evidence ceiling.
15. F19 is dependency-distinct: legacy `f-19` requires G17/G18 and is therefore deferred until those category-G behaviors are normalized.
16. No live Google production state was touched and no executable MIRA 2.0 behavior changed.

## Acceptance criteria

1. Determine exact F18 service key and composition. **Satisfied: service key `assets`; no new authority.**
2. Map D1-D7 to stable IDs without duplication. **Satisfied.**
3. Preserve asset/fitment/evidence/query/identifier/manual/spec boundaries. **Satisfied.**
4. Do not imply a complete maintenance/warranty engine. **Satisfied: retain `ASSET-SERVICE-001`.**
5. Manual path uses `KNOW-001`; specs use `SPEC-001`. **Satisfied.**
6. Activation/recommendation cannot infer ownership/install/warranty/maintenance/spec facts. **Satisfied.**
7. Preserve evidence levels and no integration/live inflation. **Satisfied.**
8. PR #31 remains candidate/reference evidence. **Satisfied.**
9. Update only `FEATURES.md`, `BACKLOG.md`, `CURRENT_WORK.md`. Pending normalization writes.
10. Bounded PR/merge/readback. Pending.
11. No legacy production or executable behavior changes. **Satisfied so far.**

## Exact next action

Normalize F18 into compact `FEATURES.md` as selected-path `assets` service composition over the existing category-D IDs. Add `AUDIT-F8` and one bounded `SERVICE-DEPS-008` repair to `BACKLOG.md`, reusing existing `ASSET-SERVICE-001`, `KNOWLEDGE-INTEGRATION-001`, `SPEC-INTEGRATION-001`, and fitment/query/evidence work rather than duplicating them. Then close `CURRENT_WORK.md`, run the three-file PR/merge/readback gate, and determine the next packet from dependency order.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head when tools permit;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture new customer ideas in BACKLOG unless required for acceptance or explicitly reprioritized;
6. finish each MIRA-development response with the current packet tag followed by either a concise customer action needed or exact fallback `Just tell me to continue.`
