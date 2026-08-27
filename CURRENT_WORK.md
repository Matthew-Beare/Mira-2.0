# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and its exact resume point.

## Completed packet

### `M2-G0-003B` — Feature Audit Slice B2 — appointment/mail communication safety

- **Merged PR:** #6
- **Merge SHA:** `c557ffdec72114c34e4159fed6ffb81a1731a5ec`
- **Audited features:** `CAL-004`, `MAIL-001`, `MAIL-002`, `MAIL-003`, `CAREER-001`
- **Result:** category B is complete and internally normalized.
- **Live Google production touched:** no.
- **Executable product behavior changed:** no.

## Active packet

- **Packet ID:** `M2-G0-004A`
- **Name:** Feature Audit Slice C1 — fulfillment lifecycle foundations
- **Class:** forensic audit / prerequisite
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `audit/g0-004a-fulfillment-lifecycle`
- **Base audit-state SHA:** `c557ffdec72114c34e4159fed6ffb81a1731a5ec`
- **Objective:** Audit the first bounded commerce/fulfillment lifecycle behaviors as stable feature records while preserving evidence precedence, canonical-state/projection boundaries, and no-duplicate-spend semantics.

## Audit rows in this packet

Audit exactly category-C rows 1-5:

1. Gmail/mail evidence ingestion and carrier/vendor correlation.
2. Ordered → shipped → delivered lifecycle with dedupe.
3. Cancelled, replaced, returned, refunded and no-settlement states.
4. Replacement updates superseded purchase state without duplicate spend.
5. Active-undelivered-only brief output plus five-business-day no-progress action.

Do not expand this packet to receipt/photo intake, spending summaries, financial connectors or category-C rows 6-12.

## Acceptance criteria

1. Each scoped behavior receives a stable semantic feature ID and complete feature record.
2. Evidence ingestion/correlation remains separate from canonical commerce state and active shipment projections.
3. Ordered/shipped/delivered lifecycle, cancellation/replacement/return/refund settlement state, and duplicate-spend prevention remain distinct where their authority/verification boundaries differ.
4. Evidence precedence and ambiguous-match behavior are preserved; MIRA must not invent delivery, correlation, refund, or replacement relationships.
5. Replacement/revision semantics preserve canonical transaction identity and do not double-count spend.
6. Active brief output excludes delivered fulfillment after durable event recording and preserves the five-business-day no-progress action rule at its actual evidence level.
7. Relevant legacy deterministic reconciliation code/tests and materially relevant PR #31 evidence are inspected without importing private transaction data.
8. `FEATURES.md`, `BACKLOG.md`, and `CURRENT_WORK.md` are the only intended changed files.
9. A small PR is scope-verified, merged, and remotely read back.
10. `CURRENT_WORK.md` advances to `M2-G0-004B` with the exact next unaudited category-C behavior.
11. No live Google production state and no executable product behavior is changed.

## Exact next action

Create/confirm branch `audit/g0-004a-fulfillment-lifecycle`. Inspect legacy category-C row 1: **Gmail/mail evidence ingestion and carrier/vendor correlation**, including evidence precedence, matching order, ambiguity handling, and canonical-source-versus-projection boundaries. Assign its stable feature ID before moving to row 2.

## Next packet boundary

If `M2-G0-004A` completes, `M2-G0-004B` begins with category-C row 6: **Receipt intake from email, files, photos/screenshots, and manual entry**.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head when tools permit;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture new customer ideas in BACKLOG unless required for acceptance or explicitly reprioritized;
6. before the final packet line, state any customer action needed; if none is needed, use `Just tell me to continue.`;
7. the final visible line remains the packet recovery tag.
