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

`SHOP-001` / `SHOP-CORE-001` are reconciled to merged/completed evidence in `FEATURES.md` and `BACKLOG.md`.

## Active packet

### `M2-M0-019` — Grocery list vs known-stock reconciliation

- **Primary work:** `GROCERY-CORE-001`
- **Primary features:** `GROCERY-001`
- **Related invariants/features:** `SHOP-001`, `INV-001`, `LOC-001`, `RECEIPT-001`, `PAR-001`, `RECIPE-001`, `MEAL-001`, `STORE-001`, `RECOVERY-002`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `integration/m0-019-grocery-core`
- **Base SHA:** `b02e723396c4deb16394c59c63ed37071cdf59c7`
- **PR:** `#73` (open, non-draft, mergeable at latest readback)
- **Merge candidate:** current branch head after the lifecycle/evidence checkpoint; verify it directly from PR #73 immediately before the exact-head CI/merge gate rather than embedding a self-referential SHA here.
- **Last release-wired green head before lifecycle evidence:** `ad32344c97013f2cc370cd887b1e59934b7f8452`
- **Objective:** add the smallest provider-neutral no-app grocery reconciliation slice that distinguishes active grocery procurement intent from known pantry/freezer/household stock using canonical shopping, asset/inventory and location truth, without pretending that acquisition quantity equals current consumable quantity or silently inventing par, recipe, meal-plan, spending, scanner or automatic purchase behavior.

## Session-start alignment verification — 2026-08-30

### `FEATURES.md`

- `GROCERY-001` is accepted and depends on `SHOP-001`, `INV-001`, `LOC-001`, and `RECEIPT-001`.
- Those hard semantic prerequisites are implemented/test/provider verified through merged shopping, receipt, asset/inventory/location packets.
- `PAR-001` is accepted but intentionally **not** a universal dependency of grocery. Quantity-aware target/threshold behavior remains optional rather than being smuggled into this packet.
- `RECIPE-001` and `MEAL-001` remain downstream/adjacent features; grocery core must not become recipe or meal planning.

### `BACKLOG.md`

- `GROCERY-CORE-001` is the one active work packet.
- `PAR-CORE-001` remains a narrower optional quantity/threshold enhancement.
- scanner/capture remains Android/client work and does not outrank a stock-ChatGPT Personal vertical.

### `ROADMAP.md`

- M2-M0.5 still prioritizes repeated useful stock-ChatGPT + Google Workspace verticals before Android.
- meals/groceries are an accepted Personal family.
- this packet remains bounded and does not expand into recipes, meal planning, par automation, finance, ordering, scanning or Android.

### Direction result

**ALIGNED.** Grocery reconciliation is dependency-ready and directly useful in stock ChatGPT. The implementation preserves the audited rule that par/current-quantity tracking is optional, not a hidden prerequisite.

## Acceptance criteria

1. Reconcile `SHOP-001` / `SHOP-CORE-001` to merged/completed evidence before grocery implementation grows, and make `GROCERY-CORE-001` the sole active work row.
2. Define one provider-neutral grocery reconciliation contract over canonical shopping intent plus canonical inventory/location truth; do not create a second shopping-list or purchase-history authority.
3. Grocery intent selection must be explicit/deterministic. Arbitrary shopping text, receipt existence, model memory or fuzzy similarity alone must not silently classify an intent as grocery.
4. Known stock must come only from canonical tracked inventory/asset/location state. Chat memory, a receipt, an order, or a prior purchase does not prove an item is currently in stock.
5. Preserve `intended_location_id` versus `observed_location_id` semantics. Pantry/freezer/household location filtering must use explicit canonical location identity and deterministic descendant behavior where supported.
6. Do not treat immutable acquisition quantity as current consumable quantity. If exact current quantity is unavailable, the result must say presence/known-stock only rather than manufacture a count.
7. `PAR-001` target/threshold/observed-quantity behavior remains optional and outside this first slice unless a hard acceptance dependency is discovered and documented before implementation.
8. The first slice supports bounded deterministic reconciliation of grocery intents into needs-to-buy, known-in-stock, and unresolved/ambiguous, with evidence/rule behind each classification available for readback.
9. No fuzzy or ambiguous automatic matching between grocery intent and inventory. Deterministic explicit identity/mapping or another exact auditable match is required; otherwise remain unresolved.
10. Reconciliation is read-only with respect to shopping intent, receipt, asset, inventory/location and purchase history unless an explicit separately authorized mutation is part of an existing canonical service contract. Merely querying groceries performs zero canonical writes.
11. Grocery reconciliation never creates/fulfills/cancels shopping intent, creates assets, moves inventory, changes fitment, records spending/payment, creates orders/shipments, changes par levels, or alters recipe/meal plans.
12. Receipt evidence may support provenance/identity only where already canonical; a receipt or historical purchase never proves present pantry/freezer stock.
13. Bounded deterministic query supports explicit grocery intent selection, canonical location scope and result limits/order sufficient for a no-app list view.
14. Clean Personal Workspace/no-app release artifacts expose any new canonical resource/binding only if implementation genuinely requires one; this pure projection adds neither.
15. Complete no-app operating instructions define grocery-vs-stock truth, optional quantity honesty, exact-match requirements and forbidden side effects; release guards protect those clauses.
16. Direct tests cover explicit grocery selection, known-stock presence, missing/untracked stock, pantry/freezer location scope, ambiguity, no-fuzzy-match behavior, quantity honesty, deterministic ordering/limits and zero-write reconciliation.
17. Fresh isolated synthetic Google provider proof verifies the selected no-app reconciliation path and zero-write readback without touching protected legacy production state.
18. Exact-head CI and post-merge `main` CI are required before completion.
19. Whole-product reconciliation leaves par automation, recipe library, meal planning, automatic purchasing/orders, spending/finance, scanner/client behavior and Android unfinished.

## Completed evidence in this packet

### Lifecycle and architecture

- `SHOP-001` is merged/provider-readback verified from PR #72 and `SHOP-CORE-001` is completed.
- `GROCERY-CORE-001` is the sole active work row for this packet.
- `GROCERY-001` is now `test_verified+provider_verified+candidate_unmerged`; it is not marked merged early.
- `GROCERY-CORE-001` has candidate PR/CI/provider evidence in `BACKLOG.md` and remains active pending merge/readback.
- No new mutable `grocery` Resource or Authority binding was introduced. Grocery is a read-only projection over already-canonical shopping and inventory/location truth.
- `project/code_ownership.json` registers `grocery-reconciliation`, owning `mira/grocery.py` and directly verified by `tests/test_grocery.py`.

### Provider-neutral grocery implementation

Added `mira/grocery.py` with `GroceryReconciliationService` and explicit outcomes `known_in_stock`, `needs_to_buy`, and `unresolved`.

The bounded contract is:

- callers explicitly select active canonical shopping-intent IDs;
- callers explicitly select one canonical stock-location root;
- stock eligibility uses **observed** location at that root or a canonical descendant, never intended placement alone;
- an explicitly supplied canonical Entity UUID is authoritative for matching;
- otherwise matching is exact equality between shopping `search_text` and asset display name after identical collapsed-whitespace/case-fold normalization;
- fuzzy, substring, semantic and LLM-selected matches are not accepted;
- one exact in-scope match is `known_in_stock`;
- multiple exact matches are `unresolved` until exact Entity UUID identity is supplied;
- no exact in-scope match leaves the active procurement intent as `needs_to_buy`;
- explicit untracked entity or tracked entity with no supported observation is `unresolved`;
- explicit entity observed outside scope is `needs_to_buy` for that scoped procurement query;
- every result retains reason/match basis and exact stock identity/location evidence when available;
- immutable acquisition quantity is never surfaced as remaining consumable quantity: `stock_quantity=null`, `stock_quantity_known=false` in this first slice;
- the service performs no canonical mutation.

### Direct and release evidence

`tests/test_grocery.py` covers:

- one exact observed name becoming known stock;
- acquisition lot quantity 12 remaining explicitly **unknown** as current stock quantity;
- missing exact observed match remaining needs-to-buy;
- multiple exact names remaining unresolved until Entity UUID is supplied;
- explicit entity outside stock scope;
- tracked entity without observation;
- explicit untracked entity;
- observed descendant location scope;
- fuzzy/substring mismatch refusal;
- purchase/asset history without tracked observation not proving stock;
- malformed selection/mapping/scope/terminal-intent validation;
- deterministic ordering and limit;
- exact zero Resource/Event/Idempotency mutation during reconciliation.

Core/release evidence:

- core CI `33348876359` passed on `faea8049d120cd5dae5340cf23b60e9d19b21657`;
- release-wired CI `33349090500` passed on `ad32344c97013f2cc370cd887b1e59934b7f8452`;
- complete no-app protocol now contains a dedicated grocery-vs-known-stock section;
- release markers guard explicit grocery intent selection, observed-location truth, exact-only matching, quantity honesty, zero-write behavior and optional-par separation;
- no clean starter schema change was required because this is a pure projection.

### Fresh isolated Google provider proof

A brand-new native Google Sheet clearly marked `NOT A STARTER` was created solely for M2-M0-019. Its provider identifier/URL is intentionally excluded from public Git. Protected legacy MIRA production state was not opened, copied as state, modified or used as a fixture.

The synthetic sheet contains `Metadata`, `Resources`, `Events`, and `Idempotency` tabs with STORE-001-shaped headers. Metadata declares synthetic-only proof state, the STORE-001 contract, single-writer model, supported source resource types, and `proof_mode=read_only_grocery_projection`.

Seeded canonical synthetic state contains:

- one captured receipt for a synthetic Whole Milk purchase;
- one receipt-linked canonical physical asset named `Whole Milk`, deliberately represented as a `lot` with immutable acquisition quantity **12**;
- hierarchical `Synthetic Home -> Kitchen -> Pantry` locations;
- one tracked `inventory_state` for that asset with intended and observed location both Pantry and an explicit offset-aware observation time;
- two active canonical shopping intents: `Whole Milk` requesting one gallon and `Bananas` requesting six each;
- eight Resource rows total and eight matching seed Idempotency rows;
- no domain Events beyond the header row.

The read-only grocery proof selected both shopping intents and stock scope `Kitchen` and used only bounded provider reads. The resulting deterministic classification was:

1. `Whole Milk` -> `known_in_stock`: exactly one canonical tracked asset has exact normalized name `whole milk`, and its supported observed location is Pantry, a canonical descendant of Kitchen.
2. `Bananas` -> `needs_to_buy`: no exact observed in-scope inventory match exists.
3. The milk asset's acquisition quantity **12** was explicitly ignored as current consumable stock; remaining stock quantity stays unknown.

A complete canonical before snapshot and complete after snapshot of `Metadata`, `Resources`, `Events`, and `Idempotency` were read around the grocery reconciliation. The after readback is unchanged: same eight Resource rows, same revisions/payloads/request hashes, same eight Idempotency rows, and Events remain header-only. Therefore the grocery reconciliation path itself performed **zero Google writes**.

After functional zero-write verification, only noncanonical presentation cleanup widened columns/froze headers for readability; it did not alter canonical Resource/Event/Idempotency values.

This provider proof exercises the stock-ChatGPT/native Google no-app reconciliation protocol directly. It does **not** falsely claim the Python `GroceryReconciliationService` executed inside the Google connector runtime.

## Session-end whole-product reconciliation — 2026-08-30

### `FEATURES.md`

- `SHOP-001`, inventory query, location and movement prerequisites remain merged/test/provider verified.
- `GROCERY-001` has direct implementation, direct tests, release-wired CI and fresh provider-readback evidence and is explicitly `test_verified+provider_verified+candidate_unmerged` until PR #73 lands.
- `PAR-001`, `RECIPE-001`, `MEAL-001`, automatic purchasing/orders, spending/finance, scanner/client behavior and Android remain unfinished.

### `BACKLOG.md`

- `SHOP-CORE-001` is complete.
- `GROCERY-CORE-001` remains the one active work row with PR #73 / CI / provider candidate evidence until merge/readback.
- `PAR-CORE-001` remains optional narrower quantity/threshold work and is not a hidden dependency of this packet.

### `ROADMAP.md`

No roadmap semantic change is required. This remains one bounded M2-M0.5 no-app vertical on the Google-first Personal path. Android remains paused and no advanced runtime dependency was introduced.

### Direction result

**ALIGNED FOR MERGE CANDIDATE.** Implementation, direct tests, no-app/release guards, lifecycle candidate evidence and fresh isolated Google zero-write provider proof are complete. Remaining work is exact-head CI, protected merge and remote `main` verification.

## Exact next action

1. Read PR #73 to resolve the exact current branch head.
2. Run CI on that exact final candidate head.
3. Merge PR #73 only with expected-head protection after exact-head CI succeeds.
4. Remotely verify `main` points to the merge commit and post-merge `main` CI is green.
5. Create the next durable post-merge lifecycle checkpoint that marks `GROCERY-001` / `GROCERY-CORE-001` merged/completed and dynamically ranks the next bounded accepted packet.

## Recovery protocol

Read this file first. Confirm branch `integration/m0-019-grocery-core` descends from verified green base `b02e723396c4deb16394c59c63ed37071cdf59c7`, PR #73 still targets `main`, and latest branch head has not changed unexpectedly. Candidate lifecycle state is reconciled, but a new exact-head CI run is required after this checkpoint. Do not touch protected legacy MIRA production data. Do not expand this packet into par automation, recipes, meal plans, automatic orders/purchasing, finance/spending, scanner/capture or Android.