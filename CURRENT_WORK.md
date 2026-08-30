# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and exact recovery state.

## Product direction

Default Personal MIRA is stock ChatGPT + Google Workspace with no external infrastructure prerequisite. Completed work remains in the durable product corpus with evidence and is filtered from future selection rather than deleted. The current priority is repeated user-visible no-app verticals that build trustworthy canonical reality before Android resumes.

Every work session begins and ends by checking `CURRENT_WORK.md`, `FEATURES.md`, `BACKLOG.md`, and `ROADMAP.md`.

## Completed predecessor

### `M2-M0-011` — First useful no-app Ops Brief + canonical tasks

Merged in PR #63 to `main` at `f96b227e009eb144235dccfef2ca0b8570e0801b` after exact-head CI `33282946569` passed. The merged vertical provides durable canonical tasks plus deterministic 02:45/14:45 task-centered Ops Brief composition, immutable composed run checkpoints, bounded progressive-discovery prompting, and isolated Google task/run exact-readback evidence. `OPS-BRIEF-VSLICE` is reconciled completed in `BACKLOG.md`.

A read-only check of stock ChatGPT Automations confirmed that exact recurring timezone-aware scheduling is available without Cloud Run, Apps Script, Linux, SQL, or another server. Existing user MIRA brief automations are protected production state and were not modified. Scheduled-delivery onboarding remains a later bounded adapter packet rather than a blocker for receipt work.

## Preserved checkpoints

- Android / `M2-M1-001` remains paused at the live isolated Google queued-writer proof point; synthetic command-boundary work remains intact.
- `DISCOVERY-CORE-001` remains partial: progressive discovery is test-verified, including repeated unanswered prompt-days and pending fitness-goals follow-up; broader evidence-aware history/friction discovery remains unfinished.
- `NONTECH-INSTALL-001` remains queued; bound Apps Script/provider setup is not pulled into this packet.
- Assets, fitment, inventory, location/movement, spending, orders/shipments, meal/grocery planning and receipt taxonomy remain canonical accepted scope but are explicitly downstream of this bounded receipt-truth slice unless an acceptance dependency is discovered.

## Active packet

### `M2-M0-012` — Canonical no-app receipt intake + purchase history

- **Primary work:** `RECEIPT-INTAKE-001`
- **Primary features:** `RECEIPT-001`, `RECEIPT-002`
- **Related invariants/features:** `RECEIPT-003`, `ORDER-001`, `ORDER-002`, `ASSET-001`, `ASSET-003`, `SPEND-001`, `SHOP-001`, `STORE-001`, `RECOVERY-002`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `integration/m0-012-receipt-intake`
- **Base SHA:** `f96b227e009eb144235dccfef2ca0b8570e0801b`
- **Objective:** let stock-ChatGPT Personal MIRA take normalized receipt/purchase evidence derived from authorized email, user-supplied image/photo, or user text and persist one canonical purchase record with exact money, stable identity, provenance fingerprints, conservative evidence dedupe and queryable purchase history. This packet establishes purchase truth only; it does not silently create assets, inventory, orders, spending allocations or provider-side receipt archives.

## Session-start alignment verification — 2026-08-29

### `FEATURES.md`

Verified before implementation:

- `RECEIPT-001` requires multi-source canonical receipt intake and evidence dedupe;
- `RECEIPT-002` requires searchable purchase history and a connected receipt graph;
- `RECEIPT-003` owns later configurable taxonomy/line classification and must not be conflated with basic receipt truth;
- `SPEND-001` requires evidence-bounded monthly spending rollup but is downstream of canonical receipt capture;
- `ASSET-001` explicitly depends on `RECEIPT-001`, confirming that stable receipt truth is a prerequisite for safe automatic acquisition/asset behavior;
- `ASSET-003`, `SHOP-001`, `GROCERY-001` and later inventory semantics consume or relate to receipt truth rather than redefining it;
- `STORE-001` and `RECOVERY-002` remain the provider-neutral persistence/failure-isolation substrate.

### `BACKLOG.md`

Verified before implementation:

- `OPS-BRIEF-VSLICE` is completed by PR #63 with test/provider evidence;
- new bounded work item `RECEIPT-INTAKE-001` is active and deliberately excludes asset/inventory/order/spend side effects;
- `RECEIPT-TAXONOMY-001`, `SPEND-ROLLUP-001`, `ASSET-SERVICE-001`, `FITMENT-ENGINE-001`, `INVENTORY-QUERY-001`, `LOCATION-STATE-001`, `MOVEMENT-CORE-001`, `GROCERY-CORE-001` and related work remain separate unfinished packets;
- scheduled brief delivery is de-risked through stock Automations capability but is not a hard prerequisite for receipt truth.

### `ROADMAP.md`

Verified before implementation:

- after the first no-app vertical, the roadmap explicitly directs continued appointments, receipts/assets/inventory, meals/groceries and other useful verticals before Android;
- the receipt -> asset -> inventory chain has high architectural leverage because multiple downstream feature families depend on canonical purchase evidence;
- packets must remain bounded and must not expand into the entire product.

### Direction result

**ALIGNED.** Canonical receipt/purchase truth is the highest-leverage next user-visible slice because it directly unlocks the asset/inventory chain the customer explicitly wants while remaining implementable in stock ChatGPT + Google Workspace.

## Canonical receipt design decisions

### Structured truth vs raw evidence

The first slice stores normalized purchase facts plus provenance metadata in canonical structured state. Raw email bodies, uploaded photos/images, PDFs and provider attachments remain in their originating/authorized provider or future evidence-store location. This packet does not require `STORE-ADAPTER-001B` merely to copy raw bytes into MIRROR.

Each evidence observation records:

- `source_type`: `email`, `image`, or `text`;
- lowercase SHA-256 `source_fingerprint` of the normalized source/evidence material supplied to the receipt service;
- optional `source_ref` pointing to the authorized provider/source identity without embedding raw source content;
- offset-aware `observed_at` timestamp.

### Money semantics

- receipt monetary values are integer minor units, never binary floating point;
- currency is uppercase ISO-style three-letter text;
- `total_minor` is required and non-negative;
- optional subtotal/tax/shipping/discount and line-level money use the same currency/minor-unit convention;
- missing components remain unknown rather than being reverse-engineered from the total;
- line totals are not required to sum to the receipt total because tax, discounts, fees and partial extraction may exist. MIRA must never claim an arithmetic reconciliation that the evidence does not support.

### Stable identity and dedupe

On initial capture:

1. exact evidence fingerprint match finds the existing canonical receipt. Materially identical facts are a read-only replay; materially conflicting facts fail closed instead of overwriting history;
2. a normalized merchant + order number match may reconcile additional evidence only when it resolves to exactly one existing receipt;
3. without an order number, normalized merchant + purchase date + currency + total may reconcile only when exactly one existing receipt matches;
4. multiple plausible matches are an ambiguity and require explicit resolution; do not choose one;
5. when no match exists, create a stable receipt ID derived from normalized transaction material plus the first source fingerprint so two legitimate same-store/same-total/same-day transactions do not collide;
6. once created, the receipt ID is immutable even if later explicit correction changes merchant/date/amount facts.

New evidence may be appended only when normalized transaction facts agree. Contradictory evidence becomes an explicit conflict/needs-review path; it never silently replaces user-confirmed or earlier canonical facts.

### Receipt/line state

The first canonical receipt payload includes:

- schema version and stable `receipt_id`;
- merchant display name + normalized merchant key;
- optional normalized order number;
- purchase date;
- currency + total minor units;
- optional subtotal/tax/shipping/discount minor units;
- ordered line items with deterministic stable line IDs, description, decimal-string quantity, optional unit price and line total minor units;
- receipt state `captured` or `needs_review` (no false “verified” claim in this packet);
- ordered evidence observations;
- optional user note.

Line classification/taxonomy remains `RECEIPT-003` work. This packet does not guess category, vehicle, asset, inventory location or beneficiary.

## Required user-visible behavior

1. MIRA can capture a normalized receipt supplied from email-derived evidence, image/photo-derived evidence, or explicit user text.
2. The same source cannot create duplicate canonical purchases.
3. A second matching source can attach provenance to the same receipt without duplicating the transaction.
4. Conflicting source evidence cannot silently rewrite merchant, date, currency, total or line facts.
5. Two legitimate same-merchant/same-date/same-total purchases with different source evidence can remain distinct when no unique correlation evidence exists.
6. Purchase history is queryable by stable receipt ID, merchant, order number and date range and returns deterministic newest-first results.
7. Corrections update the existing stable receipt identity through an explicit correction path; they never create a replacement receipt merely to change facts.
8. Raw email/photo/PDF content is not copied into structured-state payloads merely because it was used as extraction evidence.
9. Capturing a receipt does not automatically create an asset, inventory item, shipment/order state, spending allocation, reimbursement, grocery stock mutation or Drive archive.
10. The Personal Google starter and no-app instruction contract gain `receipt` as a canonical data class without introducing another writable authority.

## Explicitly deferred

- configurable receipt/line taxonomy and classification (`RECEIPT-TAXONOMY-001`);
- spending rollups/allocations (`SPEND-ROLLUP-001`);
- order/shipment lifecycle side effects;
- automatic asset creation/acquisition and fitment;
- inventory/location/movement side effects;
- grocery/pantry stock side effects;
- provider-side Drive receipt archival and raw evidence storage;
- Gmail archival/label mutation;
- payment/account settlement reconciliation;
- reimbursement and finance connectors.

## Acceptance criteria

1. Provider-neutral canonical Receipt service persists `receipt` resources through STORE-001 semantics.
2. Exact money validation uses integer minor units and three-letter currency; floats are rejected.
3. Quantity uses a normalized decimal string and rejects non-finite/negative values.
4. Deterministic line IDs and receipt IDs are stable for identical normalized input.
5. Exact source-fingerprint replay is zero-write/read-only when facts agree.
6. Exact source-fingerprint material conflict fails closed.
7. Unique merchant/order or merchant/date/currency/total correlation merges a new evidence observation into one receipt; ambiguous matches fail closed.
8. Explicit correction updates facts on the same stable receipt ID and records revision history through STORE-001 rather than replacement identity.
9. Purchase-history query supports receipt ID, merchant, order number and bounded date range with deterministic newest-first ordering.
10. Personal starter Metadata adds `receipt`; no-app authority bootstrap adds `binding-receipt`.
11. No-app operating instructions define evidence-first receipt capture and explicit no-side-effect boundaries.
12. Direct tests cover email/image/text evidence, replay, evidence merge, ambiguous duplicate, conflict, exact money/quantity validation, correction, purchase-history filtering/order and retained stable identity.
13. Distribution/Workspace validation remains deterministic after receipt resource expansion.
14. Code ownership maps the receipt component and direct evidence.
15. CI is green on exact PR head.
16. Where connector capability permits, create an isolated synthetic Google starter receipt + binding/idempotency state and read it back exactly without touching legacy production.
17. End-of-session FEATURES/BACKLOG/ROADMAP reconciliation preserves downstream asset, inventory, meal/grocery, appointment and Android scope and marks only genuinely completed receipt work complete.

## Exact next action

1. Implement provider-neutral receipt model/service and deterministic purchase-history query.
2. Add direct tests for money, identity, evidence dedupe/conflict/correction and history search.
3. Expand Personal starter/Authority/no-app instructions for `receipt`.
4. Add code ownership and release validation.
5. Run CI and fix failures.
6. Perform isolated synthetic Google receipt/provider-readback proof.
7. Reconcile packet lifecycle/feature state, run exact-head CI and merge only when green.

## Recovery protocol

Read this file first. Continue on `integration/m0-012-receipt-intake`. Do not resume Android, broaden into assets/inventory, or mutate legacy MIRA receipt/order production state while this bounded canonical receipt packet is unfinished.