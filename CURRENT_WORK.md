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
- **Status:** forensic audit and `FEATURES.md` normalization complete; `BACKLOG.md` normalization pending before PR.

## Exact category-F scope

18. **Assets/maintenance/warranties/manuals**.

F19 is excluded because legacy `f-19` requires still-unaudited G17/G18. Do not expand into F19+, category G, or executable MIRA 2.0 coding.

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
4. Legacy `f-18` hard-requires D1-D7, but MIRA 2.0 must use `SERVICE-002` selected-path readiness:
   - base asset registry/query → `ASSET-001` + `ASSET-003`;
   - fitment/assignment → add `FITMENT-001`;
   - identifiers/evidence enrichment → add `IDENT-001` + `EVID-001` where selected;
   - maintenance/warranty/reference evidence → add `ASSET-002`; full structured maintenance/warranty lifecycle remains `ASSET-SERVICE-001`;
   - retained manuals → add `KNOW-001`;
   - verified technical specifications → add `SPEC-001`.
5. Missing manual/spec/fitment/warranty capability must not block basic asset registry/query. A working base path cannot make an unavailable selected path look ready.
6. `KNOW-001` retained status requires actual retained-document identity/revision evidence; filename/URL presence alone is insufficient.
7. `SPEC-001` remains the sole verified safety-critical specification authority and retains exact applicability/provenance requirements.
8. Service activation/recommendation cannot infer ownership, installation, warranty coverage, maintenance completion, retained-manual state or verified specification correctness.
9. Existing backlog work remains authoritative: `ASSET-SERVICE-001`, `KNOWLEDGE-INTEGRATION-001`, `SPEC-INTEGRATION-001`, `FITMENT-ENGINE-001`, asset/query/evidence integration work. F8 must not duplicate those engines.
10. PR #31 remains category-D-bounded candidate/salvage evidence only and does not raise F18 service integration/live status.
11. F19 remains deferred until G17/G18 are audited.
12. No live Google production state was touched and no executable MIRA 2.0 behavior changed.

## Durable packet commits

- **Exact branch checkpoint:** `2c8d28d888220e25b616780e262e2b643c7d15ed`
- **Research checkpoint:** `7e38df2347bcf3c87cc0fd274245e4ee0f707961`
- **Feature registry normalization:** `a19f04b735a84630d63ce40dfefa0829b802c3fb`
  - diff gate: only `FEATURES.md`, 11 additions / 1 audit-status replacement;
  - added F18 `assets` selected-path mapping and F8 integrity notes;
  - no new stable feature ID.

## Acceptance criteria

1. Exact service key/composition. **Satisfied.**
2. D1-D7 stable-ID mapping without duplication. **Satisfied.**
3. Preserve asset/fitment/evidence/query/identifier/manual/spec boundaries. **Satisfied.**
4. Preserve maintenance/warranty implementation gap rather than invent completion. **Satisfied.**
5. Preserve `KNOW-001`/`SPEC-001` evidence boundaries. **Satisfied.**
6. No inference from activation/recommendation. **Satisfied.**
7. Evidence levels remain separate from MIRA 2.0 integration/live status. **Satisfied.**
8. PR #31 remains reference evidence. **Satisfied.**
9. Update only `FEATURES.md`, `BACKLOG.md`, `CURRENT_WORK.md`. **In progress: `FEATURES.md` and `CURRENT_WORK.md` changed; `BACKLOG.md` still pending.**
10. Bounded PR/merge/readback. **Pending backlog normalization.**
11. No legacy production/executable changes. **Satisfied so far.**

## Exact next action

Safely update `BACKLOG.md` without losing existing ranked work. Add:
- `AUDIT-F8` — F18 asset/maintenance/warranty/manual service audit, complete in `M2-G0-007H` after merge;
- `SERVICE-DEPS-008` — normalize/test `assets` selected-path readiness: base `ASSET-001` + `ASSET-003`; add `FITMENT-001`, `IDENT-001`/`EVID-001`, `ASSET-002`, `KNOW-001`, `SPEC-001` only for selected paths; prove missing optional paths do not block base assets and base readiness cannot mask unavailable selected paths.
Reuse existing `ASSET-SERVICE-001`, `KNOWLEDGE-INTEGRATION-001`, `SPEC-INTEGRATION-001`, `FITMENT-ENGINE-001` and other category-D work; do not create duplicate implementation tickets.

Because `BACKLOG.md` is currently ~53 KB and the available GitHub contents mutation replaces the whole file, reconstruct/verify the current file or compact it only with an explicit preservation check of every existing Work ID/class/dependency/status. Do not risk silent row loss for convenience.

After the backlog diff gate passes: close this file with exact commit SHAs, compare branch vs `main` for exactly three authority files, open bounded PR, verify server-side filenames/mergeability, merge exact head, remotely read back, then determine the next packet from dependency order.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head when tools permit;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture new customer ideas in BACKLOG unless required for acceptance or explicitly reprioritized;
6. finish each MIRA-development response with the current packet tag followed by either a concise customer action needed or exact fallback `Just tell me to continue.`
