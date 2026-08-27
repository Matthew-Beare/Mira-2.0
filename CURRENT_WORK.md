# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and its exact resume point.

## Completed packet before this branch

### `M2-G0-006F` — Feature Audit Slice E6 — provider onboarding/bootstrap and category-E closure

- **Merged PR:** #19
- **Merge SHA:** `2adf361c86731d76819acc7b24b025c47bb3a730`
- **Main handoff commit activating F1:** `ac44f475b25d3245fceeaade198f3cc2a45d567d`
- **Result:** all 26 historical category-E rows are accounted for and remotely read back on `main`.
- **Live Google production touched:** no.
- **Executable product behavior changed:** no.

## Active packet

- **Packet ID:** `M2-G0-007A`
- **Name:** Feature Audit Slice F1 — core life-service module boundaries
- **Class:** forensic audit / prerequisite
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `audit/g0-007a-core-life-services`
- **Branch start SHA:** `ac44f475b25d3245fceeaade198f3cc2a45d567d`
- **Research checkpoint commit:** `c6fd0905ab358229631b85cec919352d28098bc1`
- **Feature registry commit:** `5eee407ee19a129b63e5172f88b1a873e39b77f5`
- **Backlog checkpoint commit:** `b60a2f91f96c95c00c24e76759b0698b2fae6dad`
- **Status:** acceptance work complete; remove one unrelated backlog-diff artifact, then PR/merge/readback.

## Audited F1 rows

1. Briefs/action digest.
2. Next-action planner.
3. Email triage.
4. Orders/shipments.
5. Receipt archive.

## Completed acceptance evidence

1. Accounted for all five F1 ledger rows without duplicating existing `OPS-*`, `TASK-*`, `MAIL-*`, `ORDER-*` or `RECEIPT-*` feature families.
2. Added `SERVICE-002` — activatable service bundles over canonical behaviors with dependency-derived readiness.
3. Preserved `SERVICE-001` as the independent activation-state authority. Recommendation, activation, implementation evidence, dependency readiness and provider capability remain separate facts.
4. Recorded the five service mappings:
   - Briefs → `OPS-001`, `OPS-003`, `OPS-004`, `RECOVERY-001`, `RECOVERY-002` plus service activation/composition;
   - Next actions → `TASK-001`, `TASK-002` plus service activation/composition;
   - Email triage → `MAIL-001`, `MAIL-002`, `MAIL-003` plus service activation/composition;
   - Orders/shipments → `ORDER-001`, `ORDER-002`, `ORDER-003`, `ORDER-005` plus service activation/composition;
   - Receipt archive → `RECEIPT-001`, `RECEIPT-002`, `RECEIPT-003` plus service activation/composition.
5. Verified generic service composition/dependency semantics have deterministic legacy test evidence: unknown refs/cycles fail, required-child failure blocks affected aggregate service, optional-child failure degrades affected path, unrelated workflows remain unchanged, and no dependency install/enable occurs automatically.
6. Preserved communication safety: Email triage includes `MAIL-002`; activation cannot grant outbound-send authority.
7. Preserved commerce separation: Orders/shipments and Receipt archive are distinct service bundles and do not merge fulfillment, purchase identity, receipt archive or settlement authorities.
8. Found and recorded two real dependency defects:
   - legacy `f-01` Briefs omits A2 / `OPS-002`, so MIRA 2.0 must add single-dispatcher/no-duplicate-schedule safety to the canonical service bundle;
   - legacy `f-04` Orders/shipments omits C4 / `ORDER-004`, so MIRA 2.0 must add replacement/supersession correctness to the canonical service bundle.
9. Found and recorded legacy activation-coupling ambiguity: `order_lifecycle_enabled` maps only to `orders_shipments` although its prompt says “receipt and order lifecycle”; canonical MIRA keeps `orders_shipments` and `receipt_archive` separately activatable.
10. Added ranked work `SERVICE-COMPOSE-001`, `SERVICE-DEPS-001`, and `SERVICE-MIGRATION-001`.
11. Re-ranked `MIRA-SKILL-001` to depend on service composition and `OPS-BRIEF-VSLICE` to require service composition/dependency repair.
12. Verified the `FEATURES.md` commit is bounded to one final-section hunk: 69 net added lines, with only stale audit-status lines removed.
13. Verified the `BACKLOG.md` semantic changes are bounded to category-F correction, F1 work, service dependency findings and explicit affected dependencies, except for one accidental unrelated `IDENT-001` addition to `INVENTORY-QUERY-001` that must be removed before PR.
14. No F1 service is promoted to MIRA 2.0 integration/live status from legacy catalog, skill or deterministic test evidence alone.
15. No live Google production state was touched and no executable MIRA 2.0 product behavior changed.

## Exact next action

Remove the accidental unrelated `IDENT-001` dependency addition from the `INVENTORY-QUERY-001` backlog row so the F1 diff is scope-clean. Then compare branch against `main`, open a pull request limited to `FEATURES.md`, `BACKLOG.md`, and `CURRENT_WORK.md`, verify server-side changed-file scope and mergeability, merge with expected head SHA, remotely read back F1, and only then activate `M2-G0-007B`.

## Next packet after merge

### `M2-G0-007B` — Feature Audit Slice F2

Begin with category-F row 6 **Personal finance organization**. Determine the rest of the bounded F2 slice from the authoritative forensic ledger and dependency evidence at handoff; do not pre-expand from conversational memory.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head when tools permit;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture new customer ideas in BACKLOG unless required for acceptance or explicitly reprioritized;
6. before the final packet line, state any customer action needed; if none is needed, use `Just tell me to continue.`;
7. the final visible line remains the packet recovery tag.
