# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and exact recovery state.

## Product direction

Default Personal MIRA is stock ChatGPT + Google Workspace with no external infrastructure prerequisite. Current priority is repeated useful no-app verticals before Android resumes. Completed work remains durable with evidence and is filtered from future selection rather than deleted.

Every work session begins and ends by checking `CURRENT_WORK.md`, `FEATURES.md`, `BACKLOG.md`, and `ROADMAP.md`.

## Completed predecessor

### `M2-M0-017` — Replay-safe inventory movement / observation history

PR #71 merged to `main` as `86778802e0f32cf7d4e83c78063231a6e6e68a31` from exact verified head `e6caf2689421b36de8b8f31ed9e6ce5f615ffcb7`.

Evidence:

- core PR CI `33341918685` green;
- release-wired PR CI `33342170586` green;
- final exact-head CI `33342460536` green after the governance field-label correction;
- post-merge `main` CI `33342490468` green on the merge commit;
- fresh isolated Google proof verified one atomic Event+Idempotency append followed by one atomic Resource+Idempotency observed-state projection, intended-location preservation, exact observed time, and read-only zero-write replay with one Event / revision-2 inventory state / two stable idempotency records;
- `mira/movement.py`, direct recovery tests, complete no-app append/movement protocol, release guards, and code ownership are merged.

`MOVE-001` and `MOVEMENT-CORE-001` must be reconciled to merged/completed evidence in `FEATURES.md` / `BACKLOG.md` in this packet before implementation grows.

## Active packet

### `M2-M0-018` — Canonical shopping intent + receipt reconciliation

- **Primary work:** `SHOP-CORE-001`
- **Primary features:** `SHOP-001`
- **Related invariants/features:** `RECEIPT-001`, `RECEIPT-002`, `FITMENT-001`, `STORE-001`, `RECOVERY-002`, `GROCERY-001`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `integration/m0-018-shopping-intent`
- **Base SHA:** `86778802e0f32cf7d4e83c78063231a6e6e68a31`
- **PR:** not yet opened
- **Objective:** add a provider-neutral no-app shopping-intent authority that records what the user still intends to obtain, keeps that intent separate from durable receipt/purchase history, and allows explicit conservative reconciliation to canonical receipt evidence without silently creating assets, inventory, fitment, spending, grocery stock, or order state.

## Session-start alignment verification — 2026-08-30

### `FEATURES.md`

Verified before implementation:

- `SHOP-001` explicitly requires active shopping intent to remain distinct from durable purchase history;
- `RECEIPT-001`/`RECEIPT-002` already provide canonical purchase evidence and queryable history;
- `FITMENT-001` remains a semantic dependency for fitment-sensitive procurement, but this packet will not invent automatic fitment resolution or silently attach purchased parts to assets;
- `GROCERY-001` depends on shopping intent plus inventory/location truth, so a clean shopping-intent core unlocks later grocery reconciliation without forcing grocery semantics into this packet.

### `BACKLOG.md`

Verified before implementation:

- `SHOP-CORE-001` is queued and depends on the already-merged receipt core;
- `GROCERY-CORE-001` is a higher-level prerequisite that depends on shopping intent and inventory/location truth, so it remains downstream;
- `PAR-CORE-001` is useful but narrower and does not unlock as many accepted no-app behaviors;
- scanner/capture remains Android/client work and therefore does not outrank a stock-ChatGPT Personal vertical.

### `ROADMAP.md`

Verified before implementation:

- M2-M0.5 still prioritizes repeated useful stock-ChatGPT + Google Workspace verticals before Android;
- meals/groceries and shopping/procurement remain accepted later Personal families;
- one bounded packet must not turn shopping intent into the whole grocery, finance, fulfillment, fitment, or recommendation system.

### Direction result

**ALIGNED.** `SHOP-CORE-001` is the best next prerequisite/value slice because it is directly usable in stock ChatGPT and unlocks later grocery/pantry reconciliation, while scanner capture is client-specific and par levels are narrower.

## Acceptance criteria

1. Add one canonical `shopping_intent` mutable data class/resource; it is not a task, receipt, asset, inventory row, order, or spending record.
2. Each intent has one stable opaque intent ID/Resource ID, exact user-facing description, deterministic normalized search text, explicit positive quantity, optional unit/note, state, and timestamps needed for honest lifecycle readback.
3. Supported lifecycle is explicit and finite: `active`, `fulfilled`, or `cancelled`. Cancellation is not fulfillment. Silence, elapsed time, a receipt merely existing, or an item disappearing from chat never fulfills an intent.
4. Create/replay/update behavior is revision-checked and idempotent through STORE-001; same logical replay is zero-write and conflicting identity/material fails closed.
5. Bounded deterministic query supports exact intent ID, state, and case-insensitive description search; active-shopping queries never infer purchase history from chat memory.
6. Fulfillment is an explicit reconciliation operation against one existing canonical captured receipt and, when supplied, one exact receipt line. Missing/review-only receipt evidence fails closed.
7. A fulfillment link stores canonical receipt ID, optional exact receipt-line ID, observed receipt revision and reconciliation timestamp without copying raw evidence or replacing receipt identity.
8. This first slice does not silently auto-match an ambiguous receipt to an intent. If deterministic exact material is not supplied/verified, the intent remains active.
9. Fulfilling or cancelling an intent never mutates the canonical receipt, creates an asset, changes inventory/location, assigns fitment, changes par/grocery stock, creates an order/shipment record, or records spending/payment settlement.
10. Receipt history remains durable even after an intent is fulfilled/cancelled; shopping intent is current procurement intent, not purchase-history authority.
11. Reopening a fulfilled/cancelled intent, if supported, must be explicit on the same stable intent identity and must not delete prior reconciliation facts; otherwise the first slice must reject reopen rather than silently rewriting history.
12. Clean Personal Workspace schema/Authority bootstrap includes `shopping_intent` without changing provider-neutral product semantics or requiring external infrastructure.
13. Complete no-app operating instructions define shopping-intent truth, lifecycle, explicit receipt reconciliation, and forbidden side effects; release validation directly guards those clauses.
14. Direct tests cover create/read/query/replay/conflict, lifecycle transitions, explicit receipt/line fulfillment, missing/review-only evidence, cancellation-vs-fulfillment, deterministic ordering/limits, and forbidden side effects.
15. Provider proof uses a fresh isolated synthetic Google Sheet only and verifies create/replay/fulfillment/provider readback without touching protected legacy production state.
16. `FEATURES.md`, `BACKLOG.md`, `CURRENT_WORK.md` and code ownership are reconciled before merge; `SHOP-001` remains unmerged evidence until the packet actually lands.
17. Required CI is green on the exact merge candidate head and post-merge `main` is remotely verified.
18. Whole-product reconciliation leaves grocery/par, product recommendations, automatic fitment, orders/shipments, spending/finance, asset creation, scanner/client behavior and Android unfinished.

## Exact next action

1. Reconcile `MOVE-001` / `MOVEMENT-CORE-001` to completed merge evidence and mark only `SHOP-CORE-001` active in canonical lifecycle state.
2. Inspect any selectively salvageable legacy shopping semantics; do not import old architecture wholesale.
3. Implement the smallest provider-neutral `shopping_intent` service and direct tests.
4. Add clean Workspace resource/binding support plus complete no-app/release guards.
5. Run CI before provider writes.
6. Perform fresh isolated Google provider proof only after direct/CI evidence is green.
7. Recheck all authority files, run exact-head CI, merge with expected-head protection, and remotely verify `main`.

## Recovery protocol

Read this file first. Confirm branch `integration/m0-018-shopping-intent` descends from verified green base `86778802e0f32cf7d4e83c78063231a6e6e68a31`. Do not touch protected legacy MIRA production data. Do not expand this packet into grocery/par, automatic product recommendation or fitment, orders/shipments, finance/spending, asset/inventory mutation, scanner/capture, or Android.