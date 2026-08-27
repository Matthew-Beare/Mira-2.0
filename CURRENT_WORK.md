# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and its exact resume point.

## Completed packet

### `M2-G0-004A` — Feature Audit Slice C1 — fulfillment lifecycle foundations

- **Merged PR:** #7
- **Merge SHA:** `a453eec8dda237c4ee64a5bfb7b90ff4fb62c7b7`
- **Audited features:** `ORDER-001` through `ORDER-005`
- **Result:** category-C fulfillment lifecycle foundation is normalized; stale-shipment regression gap is explicitly queued as `ORDER-STALE-001`.
- **Live Google production touched:** no.
- **Executable product behavior changed:** no.

## Active packet

- **Packet ID:** `M2-G0-004B`
- **Name:** Feature Audit Slice C2 — receipt and financial evidence foundations
- **Class:** forensic audit / prerequisite
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Objective:** Audit category-C rows 6-10 as stable feature records, preserving canonical receipt identity, evidence provenance, single-count spending semantics, taxonomy boundaries, and payment/refund/reimbursement distinctions.

## Audit rows in this packet

Audit exactly category-C rows 6-10:

1. Receipt intake from email, files, photos/screenshots and manual entry.
2. Searchable expandable receipt/purchase history.
3. Monthly email/receipt-detected spending with dedupe/category totals and explicit evidence-boundary labeling.
4. General receipt taxonomy without private-user hard-coded defaults.
5. Expected charge, refund, reimbursement and household-beneficiary reconciliation.

Do not expand this packet to subscription/free-trial monitoring, complete bank/credit-card ingestion, assets/inventory, or category D.

## Acceptance criteria

1. Each scoped behavior receives a stable semantic feature ID and complete feature record.
2. Receipt evidence sources enrich one canonical Receipt ID and retain provenance; screenshots/OCR/manual evidence never create a shadow purchase ledger.
3. Searchable receipt/purchase history preserves canonical identity, expandable line detail and evidence linkage rather than duplicating transaction totals.
4. Monthly spending remains explicitly evidence-bounded/incomplete unless a complete financial authority is present; duplicate mail/evidence must not double-count spend.
5. Receipt taxonomy remains generic/configurable and does not hard-code this user's private categories/assets as universal defaults.
6. Expected charge, merchant refund, household reimbursement and beneficiary/cost-owner accounting remain distinct financial relationships.
7. Relevant legacy code/tests/policy and materially relevant PR #31 evidence are inspected without importing private transaction data.
8. `FEATURES.md`, `BACKLOG.md`, and `CURRENT_WORK.md` are the only intended changed files.
9. A small PR is scope-verified, merged, and remotely read back.
10. `CURRENT_WORK.md` advances to `M2-G0-004C` with the exact next unaudited category-C behavior.
11. No live Google production state and no executable product behavior is changed.

## Exact next action

Create branch `audit/g0-004b-receipt-financial-evidence` from current `main`. Inspect legacy category-C row 6: **Receipt intake from email, files, photos/screenshots and manual entry**, including canonical Receipt ID dedupe, evidence provenance and failure-domain boundaries. Assign its stable feature ID before moving to row 7.

## Next packet boundary

If `M2-G0-004B` completes, `M2-G0-004C` begins with category-C row 11: **Optional subscription/free-trial tracking**, followed by row 12 and category-C consistency closure.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head when tools permit;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture new customer ideas in BACKLOG unless required for acceptance or explicitly reprioritized;
6. before the final packet line, state any customer action needed; if none is needed, use `Just tell me to continue.`;
7. the final visible line remains the packet recovery tag.
