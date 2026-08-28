# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and its exact resume point.

## Completed packet before this branch

### `M2-G0-007G` — Feature Audit Slice F7 — travel planning and work-trip/pay composition

- **Merged PR:** #26
- **Merge SHA:** `ad9a97a74ac0cec164a6b0f424dd47407bbebeaa`
- **Main handoff commit activating F8:** `3db7203c9f7f1b232c63122e94f478898c1ae975`
- **Result:** no `TRAVEL-*`; F16/F17 reuse canonical Trip/Route and independent paid-mileage state; multi-leg gap remains `TRIP-ROUTE-CORE-001`.

## Active packet

- **Packet ID:** `M2-G0-007H`
- **Name:** Feature Audit Slice F8 — assets/maintenance/warranties/manuals service composition
- **Class:** forensic audit / prerequisite
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `audit/g0-007h-asset-service`
- **Branch start SHA:** `3db7203c9f7f1b232c63122e94f478898c1ae975`
- **Status:** acceptance complete; bounded PR/merge/readback pending.

## Exact category-F scope

18. **Assets/maintenance/warranties/manuals**.

F19 remains excluded because legacy `f-19` requires still-unaudited G17/G18. No F19+, category-G or executable MIRA 2.0 behavior entered this packet.

## Canonical F8 result

1. Exact service key is `assets`.
2. F18 creates no new asset/maintenance/warranty/manual/specification authority.
3. Historical D1-D7 map to existing stable features:
   - D1 → `ASSET-001` plus selected `FITMENT-001`;
   - D2 → `ASSET-002`;
   - D3 → `ASSET-003`;
   - D4 → `IDENT-001`;
   - D5 → `EVID-001`;
   - D6 → `KNOW-001`;
   - D7 → `SPEC-001`.
4. MIRA 2.0 uses selected-path readiness rather than legacy F18's all-D1-through-D7 requirement:
   - base asset registry/query → `ASSET-001` + `ASSET-003`;
   - fitment/assignment → add `FITMENT-001`;
   - identifiers/evidence enrichment → add `IDENT-001` + `EVID-001` where selected;
   - maintenance/warranty/reference evidence → add `ASSET-002`; full structured maintenance/warranty lifecycle remains `ASSET-SERVICE-001`;
   - retained manuals → add `KNOW-001`;
   - verified technical specifications → add `SPEC-001`.
5. Missing manual/spec/fitment/warranty capability cannot block basic asset registry/query. A working base path cannot make an unavailable selected path look ready.
6. `KNOW-001` retained state requires actual retained-document identity/revision evidence; filename/URL presence alone is insufficient.
7. `SPEC-001` remains the only verified safety-critical specification authority and retains exact applicability/provenance requirements.
8. Service activation/recommendation cannot infer ownership, installation, warranty coverage, maintenance completion, retained-manual state or verified specification correctness.
9. Existing work remains authoritative: `ASSET-SERVICE-001`, `KNOWLEDGE-INTEGRATION-001`, `SPEC-INTEGRATION-001`, `FITMENT-ENGINE-001` and other category-D implementation tickets. F8 adds no duplicate engine.
10. PR #31 remains category-D-bounded candidate/salvage evidence only and gives F18 no MIRA 2.0 integration/live credit.
11. F19 remains dependency-blocked on G17/G18.
12. No live Google production state was touched and no executable MIRA 2.0 behavior changed.

## Durable packet commits

- **Exact branch checkpoint:** `2c8d28d888220e25b616780e262e2b643c7d15ed`
- **Research checkpoint:** `7e38df2347bcf3c87cc0fd274245e4ee0f707961`
- **Feature registry normalization:** `a19f04b735a84630d63ce40dfefa0829b802c3fb`
  - only `FEATURES.md` changed for the registry write;
  - 11 additions / 1 audit-status replacement;
  - added F18 `assets` selected-path mapping and F8 integrity notes;
  - no new stable feature ID.
- **Backlog normalization/compaction:** `1607217de641cb95fa3f6371f13f7bde9642a149`
  - added only `AUDIT-F8` and `SERVICE-DEPS-008` to ranked work;
  - GitHub commit diff proves the pre-existing work tables had no row deletion or modification: the only table changes are the two F8 additions;
  - 117 deleted lines are historical explanatory dependency prose intentionally compacted after the ranked tables, with forensic detail retained in `FEATURES.md`, prior packet commits and Git history;
  - preserved every pre-F8 Work ID, Class, Work description, Dependencies and Status.

## Acceptance criteria

1. Exact service key/composition. **Satisfied.**
2. D1-D7 stable-ID mapping without duplication. **Satisfied.**
3. Preserve asset/fitment/evidence/query/identifier/manual/spec boundaries. **Satisfied.**
4. Preserve maintenance/warranty implementation gap rather than invent completion. **Satisfied.**
5. Preserve `KNOW-001`/`SPEC-001` evidence boundaries. **Satisfied.**
6. No inference from activation/recommendation. **Satisfied.**
7. Evidence levels remain separate from MIRA 2.0 integration/live status. **Satisfied.**
8. PR #31 remains reference evidence. **Satisfied.**
9. Update only `FEATURES.md`, `BACKLOG.md`, and `CURRENT_WORK.md`. **Satisfied on branch; final branch scope gate pending.**
10. Bounded PR/merge/readback. **Pending.**
11. No legacy production/executable changes. **Satisfied.**

## Exact next action

1. Compare `audit/g0-007h-asset-service` against `main`; require zero commits behind and exactly `FEATURES.md`, `BACKLOG.md`, `CURRENT_WORK.md` changed.
2. Open a bounded PR to `main`.
3. Verify GitHub server-side changed filenames and mergeability.
4. Merge using the exact verified PR head SHA.
5. Remotely read back F18 `FEATURES.md` and F8 `BACKLOG.md` state from `main`.
6. Inspect authoritative legacy dependency assignments for F19-F23 and their category-G dependencies. Determine the next packet by dependency order rather than row adjacency, checkpoint it on `main`, then create its branch.

## Next packet after F8

Not yet assigned. F19 cannot proceed until G17/G18 are normalized. After merge/readback, inspect F19-F23 dependency assignments plus category-G ordering and activate the highest-priority bounded prerequisite packet.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head when tools permit;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture new customer ideas in BACKLOG unless required for acceptance or explicitly reprioritized;
6. finish each MIRA-development response with the current packet tag and the configured continuation fallback when no customer action is needed.
