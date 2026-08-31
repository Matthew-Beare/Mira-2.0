# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and exact recovery state.

## Product direction

Default Personal MIRA is stock ChatGPT + Google Workspace with no external infrastructure prerequisite. Current priority is repeated useful no-app verticals before Android resumes. Completed work remains durable with evidence and is filtered from future selection rather than deleted.

Every work session begins and ends by checking `CURRENT_WORK.md`, `FEATURES.md`, `BACKLOG.md`, and `ROADMAP.md`.

## Completed predecessor

### `M2-M0-018` — Canonical shopping intent + receipt reconciliation

PR #72 merged to `main` as `b02e723396c4deb16394c59c63ed37071cdf59c7` from exact verified head `c380602b8538186a6b9ecac01376b47cdd209fd2`.

Evidence:

- core CI `33343292090` green;
- release-wired CI `33343692494` green;
- final exact-head CI `33347846273` green on `c380602b8538186a6b9ecac01376b47cdd209fd2`;
- post-merge `main` CI `33347884489` green on `b02e723396c4deb16394c59c63ed37071cdf59c7`;
- fresh isolated synthetic Google proof verified active shopping-intent create, read-only zero-write replay, exact captured-receipt-line fulfillment, unchanged receipt truth, no fabricated Events and no asset/inventory/fitment/order/spending/grocery side effects;
- clean Personal Workspace schema, Authority bootstrap, complete no-app protocol, direct regression guards and component ownership are merged;
- protected legacy MIRA production state was not used as a fixture or modified.

`SHOP-001` / `SHOP-CORE-001` must be reconciled from candidate/active to merged/completed evidence before this packet grows implementation.

## Active packet

### `M2-M0-019` — Grocery list vs known-stock reconciliation

- **Primary work:** `GROCERY-CORE-001`
- **Primary features:** `GROCERY-001`
- **Related invariants/features:** `SHOP-001`, `INV-001`, `LOC-001`, `RECEIPT-001`, `PAR-001`, `RECIPE-001`, `MEAL-001`, `STORE-001`, `RECOVERY-002`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `integration/m0-019-grocery-core`
- **Base SHA:** `b02e723396c4deb16394c59c63ed37071cdf59c7`
- **PR:** not yet opened
- **Objective:** add the smallest provider-neutral no-app grocery reconciliation slice that distinguishes active grocery procurement intent from known pantry/freezer/household stock using canonical shopping, asset/inventory and location truth, without pretending that acquisition quantity equals current consumable quantity or silently inventing par, recipe, meal-plan, spending, scanner or automatic purchase behavior.

## Session-start alignment verification — 2026-08-30

### `FEATURES.md`

- `GROCERY-001` is accepted and depends on `SHOP-001`, `INV-001`, `LOC-001`, and `RECEIPT-001`.
- Those hard semantic prerequisites are now implemented/test/provider verified through the merged shopping, receipt, asset/inventory/location packets.
- `PAR-001` is accepted but intentionally **not** a universal dependency of grocery. Quantity-aware target/threshold behavior must remain optional rather than being smuggled into this packet.
- `RECIPE-001` and `MEAL-001` remain downstream/adjacent features; grocery core must not become recipe or meal planning.

### `BACKLOG.md`

- `GROCERY-CORE-001` is the highest-leverage newly unblocked no-app prerequisite after shopping merge because it composes already-landed shopping and inventory/location truth.
- `PAR-CORE-001` remains a narrower optional quantity/threshold enhancement.
- scanner/capture remains Android/client work and does not outrank a stock-ChatGPT Personal vertical.

### `ROADMAP.md`

- M2-M0.5 still prioritizes repeated useful stock-ChatGPT + Google Workspace verticals before Android.
- meals/groceries are an accepted Personal family.
- this packet must remain bounded and must not expand into recipes, meal planning, par automation, finance, ordering, scanning or Android.

### Direction result

**ALIGNED.** Grocery reconciliation is now dependency-ready and directly useful in stock ChatGPT. The first implementation decision must preserve the audited rule that par/observed-quantity tracking is optional, not a hidden prerequisite.

## Acceptance criteria

1. Reconcile `SHOP-001` / `SHOP-CORE-001` to merged/completed evidence before grocery implementation grows, and make `GROCERY-CORE-001` the sole active work row.
2. Define one provider-neutral grocery reconciliation contract over canonical shopping intent plus canonical inventory/location truth; do not create a second shopping-list or purchase-history authority.
3. Grocery intent selection must be explicit/deterministic. Arbitrary shopping text, receipt existence, model memory or fuzzy similarity alone must not silently classify an intent as grocery.
4. Known stock must come only from canonical tracked inventory/asset/location state. Chat memory, a receipt, an order, or a prior purchase does not prove an item is currently in stock.
5. Preserve `intended_location_id` versus `observed_location_id` semantics. Pantry/freezer/household location filtering must use explicit canonical location identity and deterministic descendant behavior where supported.
6. Do not treat immutable acquisition quantity as current consumable quantity. If exact current quantity is unavailable, the result must say presence/known-stock only rather than manufacture a count.
7. `PAR-001` target/threshold/observed-quantity behavior remains optional and outside this first slice unless a hard acceptance dependency is discovered and documented before implementation.
8. The first slice must support bounded deterministic reconciliation of grocery intents into at least: needs-to-buy, known-in-stock, and unresolved/ambiguous, with the evidence/rule behind each classification available for readback.
9. No fuzzy or ambiguous automatic matching between grocery intent and inventory. Deterministic explicit identity/mapping or another exact auditable match is required; otherwise remain unresolved.
10. Reconciliation is read-only with respect to shopping intent, receipt, asset, inventory/location and purchase history unless an explicit separately authorized mutation is part of an existing canonical service contract. Merely querying groceries performs zero canonical writes.
11. Grocery reconciliation never creates/fulfills/cancels shopping intent, creates assets, moves inventory, changes fitment, records spending/payment, creates orders/shipments, changes par levels, or alters recipe/meal plans.
12. Receipt evidence may support provenance/identity only where already canonical; a receipt or historical purchase never proves present pantry/freezer stock.
13. Bounded deterministic query supports explicit grocery intent selection, canonical location scope and result limits/order sufficient for a no-app list view.
14. Clean Personal Workspace/no-app release artifacts expose any new canonical resource/binding only if the implementation genuinely requires one; avoid schema growth for a pure projection.
15. Complete no-app operating instructions define grocery-vs-stock truth, optional quantity honesty, exact-match requirements and forbidden side effects; release guards protect those clauses.
16. Direct tests cover explicit grocery selection, known-stock presence, missing/untracked stock, pantry/freezer location scope, ambiguity, no-fuzzy-match behavior, quantity honesty, deterministic ordering/limits and zero-write reconciliation.
17. Fresh isolated synthetic Google provider proof verifies the selected no-app reconciliation path and zero-write readback without touching protected legacy production state.
18. Exact-head CI and post-merge `main` CI are required before completion.
19. Whole-product reconciliation leaves par automation, recipe library, meal planning, automatic purchasing/orders, spending/finance, scanner/client behavior and Android unfinished.

## Exact next action

1. Reconcile `SHOP-001` / `SHOP-CORE-001` to merged/completed evidence and mark only `GROCERY-CORE-001` active in canonical lifecycle state.
2. Inspect existing asset/inventory/location/shopping contracts and selectively salvage any legacy grocery semantics; do not import legacy architecture wholesale.
3. Decide the smallest deterministic grocery-selection/matching model that does not make par quantity a hidden dependency.
4. Implement provider-neutral reconciliation and direct tests.
5. Wire complete no-app/release guards and clean starter schema only if required by the chosen model.
6. Run CI before provider writes.
7. Perform fresh isolated Google provider proof, recheck authority files, exact-head merge and remote `main` verification.

## Recovery protocol

Read this file first. Confirm branch `integration/m0-019-grocery-core` descends from verified green base `b02e723396c4deb16394c59c63ed37071cdf59c7`. Do not touch protected legacy MIRA production data. Do not expand this packet into par automation, recipes, meal plans, automatic orders/purchasing, finance/spending, scanner/capture or Android.