# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and its exact resume point.

## Completed packet

### `M2-G0-005A` — Feature Audit Slice D1 — asset identity and evidence foundations

- **Merged PR:** #10
- **Merge SHA:** `59cb132a351e97173c8a5ef4df1651f0a22c18d8`
- **Audited features:** `ASSET-001`, `FITMENT-001`, `ASSET-002`, `ASSET-003`, `IDENT-001`, `EVID-001`
- **Result:** immutable asset identity, relationship semantics, graph queries, identifiers and evidence enrichment are normalized at their actual evidence levels.
- **Live Google production touched:** no.
- **Executable product behavior changed:** no.

## Active packet

- **Packet ID:** `M2-G0-005B`
- **Name:** Feature Audit Slice D2 — knowledge/spec/shopping/location foundations
- **Class:** forensic audit / prerequisite
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Objective:** Audit manual/knowledge retention, exact technical-spec provenance, shopping-intent separation, inventory identity and location semantics without entering movement/scanning/par/grocery scope.

## Audit rows in this packet

1. Manual discovery, canonical Drive retention and asset linkage.
2. Vehicle/equipment technical specifications with exact applicability and provenance.
3. Shopping intent separate from purchase history.
4. Immutable inventory/item IDs.
5. Hierarchical locations and intended-location versus last-moved-location.

Do not expand this packet to QR/barcode movement, queryable household inventory UX, par sensing, grocery flows, recipes or category-D rows 11-16.

## Acceptance criteria

1. Each scoped behavior receives a stable semantic feature ID and evidence boundary.
2. Manual/reference discovery and retained knowledge identity are separated from asset identity and from provider download success.
3. Safety-critical technical specifications require authoritative provenance, exact subject/applicability and source locator; owner memory/OCR alone cannot become verified.
4. Shopping intent remains separate mutable state from purchase/receipt history and cannot duplicate spend or purchased assets.
5. Inventory/item identity preserves immutable Entity UUID semantics rather than inventing a second inventory identity authority.
6. Location hierarchy distinguishes intended/canonical placement from observed/last-moved location and does not silently rewrite one from the other.
7. Relevant legacy code/tests/policy and materially relevant PR #31 evidence are inspected without private inventory data.
8. Only `FEATURES.md`, `BACKLOG.md`, and `CURRENT_WORK.md` are intended changes.
9. A small PR is scope-verified, merged and remotely read back.
10. `CURRENT_WORK.md` advances to `M2-G0-005C` with exact D3 resume point.
11. No live Google production state and no executable product behavior is changed.

## Exact next action

Create branch `audit/g0-005b-knowledge-spec-location` from current `main`. Inspect category-D row 6: **Manual discovery, canonical Drive retention, and asset linkage**, including authoritative-source preference, retained Knowledge identity, blocked/no-match states, Drive evidence and explicit asset relationships.

## Next packet boundary

If D2 completes, `M2-G0-005C` audits category-D rows 11-15: QR/barcode movement, queryable household/shop inventory, consumable par levels, optional scale sensing, and grocery/pantry/freezer flows.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head when tools permit;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture new customer ideas in BACKLOG unless required for acceptance or explicitly reprioritized;
6. before the final packet line, state any customer action needed; if none is needed, use `Just tell me to continue.`;
7. the final visible line remains the packet recovery tag.
