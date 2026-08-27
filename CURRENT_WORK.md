# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and its exact resume point.

## Completed packet before this branch

### `M2-G0-007G` — Feature Audit Slice F7 — travel planning and work-trip/pay composition

- **Merged PR:** #26
- **Merge SHA:** `ad9a97a74ac0cec164a6b0f424dd47407bbebeaa`
- **Rows audited:** F16 Travel/vacation/outdoor planning; F17 Work-trip/route/paid-work tracking.
- **Result:** no `TRAVEL-*` authority. F16 composes `TRIP-001` + `ROUTE-001`; F17 adds independent `MILE-001` + `MILE-002` when paid-work tracking is selected. Ordered multi-leg grouping/revision remains explicit implementation gap `TRIP-ROUTE-CORE-001`.
- **Registry maintenance:** `FEATURES.md` was compacted into the canonical index while verbose forensic detail remains durable in Git history/checkpoints; all stable IDs and audited service mappings were preserved.
- **Remote readback:** F16/F17 registry mappings and F7 backlog findings verified on `main` after merge.
- **Live Google production touched:** no.
- **Executable product behavior changed:** no.

## Active packet

- **Packet ID:** `M2-G0-007H`
- **Name:** Feature Audit Slice F8 — assets/maintenance/warranties/manuals service composition
- **Class:** forensic audit / prerequisite
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `audit/g0-007h-asset-service`
- **Branch start SHA:** this `main` handoff commit; create branch immediately after this write and record exact SHA on branch checkpoint.
- **Status:** activated; F18 forensic audit next.

## Exact category-F scope

18. **Assets/maintenance/warranties/manuals**.

Do not expand this packet into F19 personal knowledge/reference library. Legacy dependency evidence shows F19 requires G17/G18, which are still unaudited category-G behaviors; F19 therefore belongs after those dependencies are normalized. Do not expand into F20+, category G, or executable MIRA 2.0 coding.

## Packet-boundary evidence

- Legacy `starter/behavior-dependencies.json` maps `f-18` to D1-D7 only.
- Category D has already normalized D1-D7 into asset identity/relationships/evidence/query/identifier/manual/specification authorities.
- Legacy `f-19` depends on G17/G18, so F19 is dependency-distinct and cannot be audited honestly before those category-G authorities are normalized.

## Acceptance criteria

1. Determine the exact F18 service key and whether it is pure `SERVICE-002` composition over already-canonical category-D features or requires any distinct lifecycle/authority.
2. Map historical D1-D7 dependencies to current stable IDs without duplicating asset, evidence, knowledge or specification authorities.
3. Keep physical asset identity, fitment/assignment, lifecycle/evidence, graph queries, identifiers, retained manuals and technical specifications separate where their authority/evidence boundaries differ.
4. Maintenance/warranty service readiness must not imply a dedicated lifecycle engine unless implementation/test evidence actually supports one; preserve existing `ASSET-SERVICE-001` gap if applicable.
5. Manual/reference availability must depend on `KNOW-001` retained-document truth rather than filenames/URLs alone; safety-critical technical values remain `SPEC-001` with exact provenance.
6. Service activation/recommendation cannot infer asset ownership, installation, warranty coverage, maintenance completion or specification correctness.
7. Preserve requirement/evidence separation; legacy deterministic category-D cores do not prove MIRA 2.0 service integration/live behavior.
8. Reconcile PR #31 as candidate/reference evidence only.
9. Update only `FEATURES.md`, `BACKLOG.md`, `CURRENT_WORK.md`.
10. Open bounded PR, verify exact changed-file scope/mergeability, merge using exact head SHA and remotely read back before advancing.
11. Touch no legacy Google production state and change no executable MIRA 2.0 behavior.

## Exact next action

1. Create branch `audit/g0-007h-asset-service` from this exact handoff commit.
2. Update branch checkpoint with the exact branch-start SHA.
3. Inspect legacy F18 ledger wording, service/router/catalog key and D1-D7 dependency/evidence paths.
4. Determine whether F18 introduces any new canonical feature ID or only an audited service composition over existing category-D features.
5. Check PR #31 only for evidence ceiling, never implementation credit.

## Next packet after F8

Determine from authoritative dependency evidence after F18 closes. F19 is explicitly blocked on unaudited G17/G18 and must not be pulled into this packet merely by adjacency.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head when tools permit;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture new customer ideas in BACKLOG unless required for acceptance or explicitly reprioritized;
6. finish each MIRA-development response with the current packet tag followed by either a concise customer action needed or exact fallback `Just tell me to continue.`
