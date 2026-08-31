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
- final exact-head CI `33342460536` green;
- post-merge `main` CI `33342490468` green on the merge commit;
- fresh isolated Google proof verified event-first/projection-second movement, intended-location preservation, exact observed time, and zero-write replay;
- `MOVE-001` and `MOVEMENT-CORE-001` are reconciled to merged/completed evidence in canonical lifecycle state.

## Active packet

### `M2-M0-018` — Canonical shopping intent + receipt reconciliation

- **Primary work:** `SHOP-CORE-001`
- **Primary features:** `SHOP-001`
- **Related invariants/features:** `RECEIPT-001`, `RECEIPT-002`, `FITMENT-001`, `STORE-001`, `RECOVERY-002`, `GROCERY-001`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `integration/m0-018-shopping-intent`
- **Base SHA:** `86778802e0f32cf7d4e83c78063231a6e6e68a31`
- **PR:** `#72` (open, non-draft)
- **Last fully green release-wired head before this evidence checkpoint:** `6b1000b9edb25c9cab7aeb703f6d2fe49228a167`
- **Objective:** add a provider-neutral no-app shopping-intent authority that records what the user still intends to obtain, keeps that intent separate from durable receipt/purchase history, and allows explicit conservative reconciliation to canonical captured-receipt evidence without silently creating assets, inventory, fitment, spending, grocery stock, or order state.

## Session-start alignment verification — 2026-08-30

### `FEATURES.md`

Verified before implementation:

- `SHOP-001` requires active shopping intent to remain distinct from durable purchase history;
- `RECEIPT-001` / `RECEIPT-002` already provide canonical purchase evidence and queryable history;
- `FITMENT-001` remains a separate fitment truth and this packet must not invent automatic fitment resolution;
- `GROCERY-001` remains downstream and depends on shopping intent plus inventory/location truth.

### `BACKLOG.md`

Verified and reconciled before implementation:

- `MOVEMENT-CORE-001` is complete from PR #71;
- `SHOP-CORE-001` is the one active work row;
- `GROCERY-CORE-001`, `PAR-CORE-001`, scanner/capture, fitment, orders and finance remain separate unfinished work.

### `ROADMAP.md`

Verified before implementation and again before merge-candidate closeout:

- M2-M0.5 prioritizes repeated useful stock-ChatGPT + Google Workspace verticals before Android;
- shopping/procurement and meals/groceries are accepted Personal families;
- a bounded packet must not fan out into grocery, finance, fulfillment, fitment, recommendation or Android/client systems.

### Direction result

**ALIGNED.** `SHOP-CORE-001` is directly useful in stock ChatGPT and unlocks later grocery/pantry reconciliation while preserving bounded authority boundaries.

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
11. The first slice rejects implicit reopen of fulfilled/cancelled intent rather than rewriting terminal history.
12. Clean Personal Workspace schema/Authority bootstrap includes `shopping_intent` without external infrastructure.
13. Complete no-app operating instructions define shopping-intent truth, lifecycle, explicit receipt reconciliation, historical receipt-revision provenance and forbidden side effects; release validation guards those clauses.
14. Direct tests cover create/read/query/replay/conflict, lifecycle transitions, explicit receipt/line fulfillment, missing/review-only evidence, cancellation-vs-fulfillment, deterministic ordering/limits, later receipt revision, malformed state and forbidden side effects.
15. Provider proof uses a fresh isolated synthetic Google Sheet only and verifies create/replay/fulfillment/provider readback without touching protected legacy production state.
16. `FEATURES.md`, `BACKLOG.md`, `CURRENT_WORK.md` and code ownership are reconciled before merge; `SHOP-001` remains unmerged evidence until PR #72 lands.
17. Required CI is green on the exact merge candidate head and post-merge `main` is remotely verified.
18. Whole-product reconciliation leaves grocery/par, product recommendations, automatic fitment, orders/shipments, spending/finance, asset creation, scanner/client behavior and Android unfinished.

## Completed evidence in this packet

### Lifecycle and component alignment

- `BACKLOG.md` was first reconciled so `MOVEMENT-CORE-001` is complete and `SHOP-CORE-001` is the sole active work row.
- `project/code_ownership.json` registers `canonical-shopping-intent`, owning `mira/shopping.py` and directly verified by `tests/test_shopping.py`.
- No legacy production Google state was used as a fixture.

### Provider-neutral shopping implementation

Added `mira/shopping.py` with canonical resource type `shopping_intent`, schema version 1 and lifecycle states `active|fulfilled|cancelled`.

The service provides:

- stable intent creation/read;
- active-intent update;
- explicit cancellation;
- explicit fulfillment from one canonical captured receipt, optionally one exact receipt line;
- bounded deterministic query by exact intent ID, lifecycle state and case-insensitive description substring;
- positive decimal-string quantity normalization and offset-aware timestamps;
- canonical Resource revision/idempotency conflict handling and exact readback;
- exact semantic zero-write replay for create/update/cancel/fulfill;
- historical reconciliation retaining receipt ID, optional line ID, the receipt revision actually observed, and reconciliation time;
- replay of fulfilled intent against stored historical reconciliation even if the receipt later advances to a newer revision;
- no receipt mutation or downstream asset/inventory/fitment/order/spending/grocery side effects.

Terminal fulfilled/cancelled intent is intentionally not silently reopened in this slice.

### Direct/test evidence

`tests/test_shopping.py` covers:

- create/read and exact create replay;
- conflicting idempotency material;
- revisioned active update and semantic zero-write update replay;
- deterministic query filtering/order/limit;
- receipt existence alone not fulfilling intent;
- explicit receipt-line fulfillment and receipt immutability;
- explicit whole-receipt fulfillment;
- missing receipt, missing line and `needs_review` receipt rejection;
- cancellation distinct from fulfillment and terminal no-reopen behavior;
- fulfilled replay with no extra revision and conflicting reconciliation rejection;
- later receipt correction not rewriting historical shopping reconciliation;
- timestamp, quantity and query validation;
- corrupt persisted identity failing closed.

Core CI run `33343292090` passed on `6e16387d0352137fbf00c5fcc7e3bd735450842c`.

### Clean Personal release wiring

The clean Personal starter now includes `shopping_intent` in exact `resource_types_json`, and `mira/personal_distribution.py` plus direct distribution tests require that schema.

The complete `workspace/apps_script/MIRA_NO_APP_INSTRUCTIONS.md` now includes:

- `shopping_intent` in Workspace preflight and Authority bootstrap;
- `authority_binding/binding-shopping-intent`;
- explicit current-procurement authority separate from purchase history;
- `active|fulfilled|cancelled` lifecycle;
- receipt existence never implying fulfillment;
- fulfillment requiring canonical receipt state `captured`;
- `needs_review` receipt rejection;
- optional exact receipt-line reconciliation;
- historical receipt-revision provenance and later-correction stability;
- exact replay with zero write;
- receipt immutability and forbidden downstream side effects;
- deterministic shopping query semantics.

`mira/workspace_bundle.py` and `tests/test_workspace_bundle.py` directly guard the shopping binding, receipt-does-not-auto-fulfill rule, captured-only rule, review-only rejection, and receipt-immutability boundary.

An intermediate release CI run `33343612807` failed before unit tests only because one exact protocol marker used lowercase `shopping` while the canonical sentence began `Shopping`. The guard was corrected without changing semantics. Release-wired CI run `33343692494` then passed on exact head `6b1000b9edb25c9cab7aeb703f6d2fe49228a167`.

### Fresh isolated Google provider proof

A brand-new native Google Sheet clearly marked `NOT A STARTER` was created solely for M2-M0-018. Its provider identifier/URL is intentionally excluded from public Git. No protected legacy MIRA artifact was opened, altered, copied as state, or used as a fixture.

The synthetic sheet uses native `Metadata`, `Resources`, `Events`, and `Idempotency` tabs with STORE-001-shaped headers and metadata declaring the synthetic environment and `shopping_intent` resource support.

Synthetic canonical source evidence:

- one captured receipt at revision 1;
- one exact receipt line for a synthetic torque wrench;
- receipt Resource + matching seed Idempotency result persisted before shopping operations;
- Events remained header-only throughout the shopping proof.

Shopping proof sequence:

1. Created one `shopping_intent` as revision 1 / `active` using one atomic Resource+Idempotency batch and exact readback.
2. Re-read the exact create idempotency key/hash/result and Resource state. Because replay material matched, the correct replay path invoked **no Google write**; the intent remained revision 1.
3. Explicitly reconciled the active intent to the exact captured receipt line using expected revision 1 and one atomic Resource+Idempotency batch.
4. Exact readback proved shopping intent revision 2 / `fulfilled`, with reconciliation storing the exact receipt ID, exact line ID, receipt revision 1 and exact offset-aware reconciliation time.
5. Exact readback simultaneously proved the canonical receipt remained revision 1 with its original payload, request hash and idempotency key unchanged.
6. Events remained empty: shopping lifecycle in this slice is Resource-state lifecycle, not fabricated event history.
7. The final store contained only the synthetic receipt and shopping-intent Resources. No asset, inventory, location, fitment, order/shipment, spending/payment, par or grocery state appeared.
8. Terminal replay was verified by read-only lookup of the fulfillment idempotency record: the stable fulfillment key resolves to the exact persisted request hash and revision-2 result, so replay correctly requires zero write.

The proof sheet received only minimal presentation cleanup after functional replay verification: native tabs retained their schema, header rows were frozen, and long JSON columns were widened. Final metadata readback confirmed all four native tabs remained intact.

This provider proof exercises the stock-ChatGPT/native Google STORE protocol directly. It does not falsely claim that the Python `ShoppingIntentService` executed inside the Google connector runtime.

## Session-end whole-product reconciliation — 2026-08-30

### `FEATURES.md`

- `MOVE-001` remains correctly merged/test/provider verified from M2-M0-017.
- `SHOP-001` now has direct implementation/test/provider evidence but must remain explicitly **unmerged** until PR #72 lands.
- `GROCERY-001`, `PAR-001`, fitment, orders/shipments, finance and Android/client features remain separate unfinished scope.

### `BACKLOG.md`

- `MOVEMENT-CORE-001` is complete.
- `SHOP-CORE-001` remains the one active work row until PR #72 merge/readback.
- `GROCERY-CORE-001` is now dependency-close except for `SHOP-001` actually merging; it is a likely next no-app candidate, not part of this packet.

### `ROADMAP.md`

No semantic roadmap change is required. This remains one bounded M2-M0.5 no-app vertical/prerequisite on the Google-first Personal path. Android stays paused and no advanced runtime dependency was introduced.

### Direction result

**ALIGNED FOR MERGE CANDIDATE.** Implementation, direct tests, starter/bootstrap changes, complete no-app/release guards and fresh isolated Google provider proof are complete. Remaining work is final lifecycle evidence text, exact-head CI, protected merge and remote `main` verification.

## Exact next action

1. Reconcile `SHOP-001` to explicit candidate-unmerged evidence and enrich the active `SHOP-CORE-001` backlog row with PR/CI/provider evidence without marking it complete early.
2. Re-read PR #72 and record its exact current head/mergeability.
3. Run CI on the exact final documentation/lifecycle head.
4. Update PR #72 merge gate to that exact SHA and merge only with expected-head protection after CI succeeds.
5. Remotely verify `main` points to the merge and post-merge push CI is green.
6. Create a post-merge lifecycle checkpoint that marks `SHOP-001` / `SHOP-CORE-001` merged/completed and reranks unfinished accepted work before activating the next bounded packet.

## Recovery protocol

Read this file first. Confirm branch `integration/m0-018-shopping-intent` descends from verified green base `86778802e0f32cf7d4e83c78063231a6e6e68a31` and PR #72 still targets `main`. The last fully green release-wired pre-evidence head is `6b1000b9edb25c9cab7aeb703f6d2fe49228a167`; a new exact-head run is required after lifecycle/evidence commits. Do not touch protected legacy MIRA production data. Do not expand this packet into grocery/par, automatic product recommendation or fitment, orders/shipments, finance/spending, asset/inventory mutation, scanner/capture, or Android.