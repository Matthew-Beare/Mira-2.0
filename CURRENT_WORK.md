# MIRA 2.0 CURRENT WORK

Git is authoritative. This branch records exactly one active packet.

## Active packet

### `M2-M1-047` — Historical finance backfill

- **Primary work:** `FIN-CANON-AUDIT-001`.
- **Primary features:** `FIN-001`, `RECEIPT-001`.
- **Related invariants/features:** `RECOVERY-001`, `RECOVERY-002`, `ORDER-001`, `ORDER-002`, `ASSET-001`, `ASSET-002`, `ASSET-003`.
- **Repository:** `Matthew-Beare/Mira-2.0`.
- **Branch:** `work/m2-m1-047-finance-historical-backfill`.
- **Base SHA:** `8ed16f9e2b3e2672ff7149488ba0a7d28a4a0222`.

## Recovery contract

- Read `PROJECT_INSTRUCTIONS.md`, then this file.
- Verify remote `main`, this packet branch/head, PR state, and relevant CI before doing work.
- If Git contradicts this checkpoint, reconcile this file first. Never repeat merged work.
- Prior packet `M2-M1-046` is merged into current `main`; its stale ACTIVE checkpoint is superseded by this packet.

## Objective

Close the historical finance coverage gap by reconciling all trustworthy provider-visible history into canonical MIRROR finance state with stable provider transaction identity, provenance, and exact readback. Do not use 2026-09-01 as a history exclusion boundary.

## Verified evidence this packet

- Connected finance transaction coverage re-read on 2026-09-14 reports `full_history`, available and complete for the bounded queries used here; freshness remains unknown.
- Exact provider aggregation for posted rows before the canonical ledger start (`2026-01-02`) yielded **1,194 rows across six accounts**: Matthew's Primary Savings 70, CREDIT CARD 501, Joint Checking 436, Rewards Signature・9854 128, Home Savings 40, Joint Savings 19.
- The oldest verified provider-visible row in that bounded historical set is dated `2024-08-09`; account-specific oldest dates range from 2024-08-09 through 2024-08-30.
- Canonical `Financial Escape` / `FinOps Ledger` began at `2026-01-02` before this packet; direct sheet readback confirmed no earlier production rows before the backfill writes below.
- Provider rows expose stable `transaction_id`, account identity, posted date, signed amount, merchant/name/category data, and confidence suitable for deterministic source identity. Missing check payee/memo/image data remains unknown unless corroborated by another source.
- The first bounded production import is complete for **Joint Savings**: all 19 provider rows dated 2024-08-30 through 2025-12-31 were absent from canonical transaction IDs, appended with deterministic `EVT-<transaction_id>` identity, and read back exactly at rows 888-906.
- The second bounded production import is complete for **Home Savings**: all 40 provider rows dated 2024-08-17 through 2025-12-31 were appended only after confirming the destination range was empty and preserving a concurrently restored current-ledger row immediately ahead of the batch. Exact readback at rows 908-947 confirms stable transaction/Event identity, dates, values, classifications, formula propagation, month derivation and review state.
- Historical income and transfer rows preserve provider signed amount in provenance while canonical economic-spend fields remain zero, matching existing ledger treatment (`EXCLUDED_INCOME` / `EXCLUDED_TRANSFER`).
- **1,135 pre-canonical provider rows remain** after the two verified account batches. A total of 59 of the original 1,194 rows are now reconciled into canonical FinOps history.
- PR #165 is the active packet PR. Exact-head CI #664 completed successfully on head `13c3072ba22b7d980f196f45f89a6c6d3bf38a87`.
- Hourly recovery preflight independently re-verified remote `main` at `8ed16f9e2b3e2672ff7149488ba0a7d28a4a0222`, open PR #165, green exact-head CI, provider full-history coverage, and the complete **70-row Matthew's Primary Savings** pre-canonical source batch.
- Immediate destination readback confirms rows 948 onward have no canonical event/transaction data before the next append; formula scaffolding is present. The 70-row provider batch remains the next bounded write and must still receive exact post-write readback before its reconciliation count is credited.

## Acceptance criteria

1. Enumerate provider-visible posted transaction history before the current canonical ledger start until source exhaustion for every relevant linked account/history window.
2. Import missing historical rows into the existing `FinOps Ledger` using stable provider `transaction_id` identity and deterministic `Event ID`; preserve source account/date/signed amount/vendor/category/provenance and do not overwrite existing production rows.
3. Preserve transfers and zero-economic-spend rows as evidence while keeping their economic-spend treatment explicit; never infer income merely from retrieval inclusion.
4. Reconcile duplicates against existing canonical transaction IDs before each write batch.
5. Exact readback proves imported transaction IDs, dates, signed amounts/provenance, classifications and row counts; unavailable source gaps are recorded explicitly rather than filled by assumption.
6. Historical user corrections already supplied during reconciliation are applied only when identity is sufficiently supported; ambiguous checks remain unresolved.
7. When finance history is fully reconciled or durably bounded by actual source unavailability, checkpoint completion and move next to the Android inventory/scanning vertical reusing `INV-001`, `INV-002`, `MOVE-001`, `IDENT-001`, `ASSET-001`, `ASSET-002`, `ASSET-003`.

## Session-start alignment verification — 2026-09-14

### `FEATURES.md`
ALIGNED. This packet advances existing finance/recovery/evidence/asset semantics and does not create a parallel ledger or inventory model.

### `BACKLOG.md`
ALIGNED. `FIN-CANON-AUDIT-001` remains the highest-priority blocker. Android inventory/scanning stays next only after historical finance closure or a source-unavailability boundary is actually proved.

### `ROADMAP.md`
ALIGNED. The work preserves provider truth, explicit provenance, canonical state, exact readback, and ordinary-user MIRA behavior rather than defining a convenient artificial history boundary.

### Idea/backlog capture audit
CAPTURE AUDIT COMPLETE

- Historical reconciliation is existing `FIN-CANON-AUDIT-001` work.
- The next inventory/scanning outcome is already represented by `INV-001`, `INV-002`, `MOVE-001`, `IDENT-001`, `ASSET-001`, `ASSET-002`, and `ASSET-003`.
- No new material product feature is introduced by this checkpoint repair or the bounded historical imports.

### Direction result
ALIGNED

## Exact resume point

1. Re-read PR #165 head/CI because this checkpoint changes the branch head; require exact-head CI green before unrelated growth.
2. Re-read `FinOps Ledger` transaction IDs and rows 948 onward, then append only still-missing Matthew's Primary Savings identities from the verified 70-row provider batch. Preserve raw signed amount in provenance and conservative transfer/income/refund semantics.
3. Exact-read back the full appended batch, formulas, date formatting, duplicate transaction/Event IDs, and row count before crediting those rows as reconciled.
4. Continue Rewards Signature・9854 (128), then bounded partitions for Joint Checking (436) and CREDIT CARD (501), always re-reading destination state immediately before writes.
5. Do not begin Android inventory implementation until all 1,194 historical provider rows are reconciled or an actual source-unavailability boundary is durably proven.

## Six-line customer status

Objective: Reconcile the complete provider-visible historical finance record into MIRROR before starting inventory scanning.
Progress: Two full historical accounts are reconciled and exactly read back; the next 70-row account batch is source-verified and destination-preflighted for safe append.
Last 24h: Historical finance coverage was proven back to 2024-08-09 and two complete account histories were added without overwriting concurrent production state or creating duplicate economic effects.
Deliverable: Canonical FinOps history backfilled to the provider's actual oldest available boundary with exact transaction-ID readback and explicit unavailable gaps.
Expected delivery: UNKNOWN
Blocker: none
