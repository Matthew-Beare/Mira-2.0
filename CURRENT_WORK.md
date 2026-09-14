# MIRA 2.0 CURRENT WORK

Git is authoritative. This branch records exactly one active packet.

## Active packet

### `M2-M1-047` — Historical finance backfill

- **Primary work:** `FIN-CANON-AUDIT-001`.
- **Primary features:** `FIN-001`, `RECEIPT-001`.
- **Related invariants/features:** `RECOVERY-001`, `RECOVERY-002`, `ORDER-001`, `ORDER-002`, `ASSET-001`, `ASSET-002`, `ASSET-003`.
- **Repository:** `Matthew-Beare/Mira-2.0`.
- **Branch:** `work/m2-m1-047-finance-historical-backfill`.
- **Original base SHA:** `8ed16f9e2b3e2672ff7149488ba0a7d28a4a0222`.
- **Remote main verified this run:** `166ec68dec558e812c463c41a4df1382ab29b24c`.
- **Remote branch head before this checkpoint:** `e4e08151c2ee181c21cc80d9e1559131fc6d3d20`.

## Recovery contract

- Read `PROJECT_INSTRUCTIONS.md`, then this file.
- Verify remote `main`, this packet branch/head, PR state, relevant CI, connected finance coverage, and canonical workbook target before writes.
- If Git contradicts this checkpoint, reconcile this file first. Never repeat merged work.
- Prior packet `M2-M1-046` is merged. PR #165 is the sole active `M2-M1-047` historical-finance PR.
- Duplicate draft PR #164 was closed unmerged on 2026-09-14 to remove conflicting packet ownership.

## Objective

Close the historical finance coverage gap by reconciling all trustworthy provider-visible history into canonical MIRROR finance state with stable provider transaction identity, preserved provenance, idempotent writes, and exact readback. Do not use 2026-09-01 as a history exclusion boundary.

## Verified evidence

- Connected finance transaction coverage reports `full_history`, available, and complete for bounded queries; freshness remains unknown.
- Exact provider aggregation for posted rows before canonical ledger start (`2026-01-02`) yielded **1,194 rows across six accounts**.
- The oldest verified provider-visible row in that bounded historical set is dated **2024-08-09**.
- Canonical `FinOps Ledger` began at `2026-01-02` before this packet's backfill writes.
- **Joint Savings reconciled:** 19 historical provider rows appended and exactly read back.
- **Home Savings reconciled:** 40 historical provider rows appended and exactly read back.
- **Matthew's Primary Savings reconciled:** 70 historical provider identities appended; exact comparison confirmed all 70 present with no duplicate canonical transaction IDs.
- One explicitly named merchant refund in Primary Savings was retained as a negative economic-spend credit rather than excluded merely because the provider categorized it as income.
- **Rewards Signature reconciled:** all 128 provider-visible rows before `2026-01-02` were appended and exactly read back. Exported-workbook verification proved 128 source IDs = 128 canonical IDs, zero missing IDs, zero extras, zero duplicate transaction IDs, zero Event-ID mismatches, zero date mismatches, and zero amount/treatment semantic mismatches.
- Rewards Signature treatment preserved source semantics: 15 credit-card payments are zero-economic-spend `EXCLUDED_TRANSFER`; three cash-back rewards are zero-economic-spend `EXCLUDED_INCOME`; 101 verified fuel rows use the existing user corrections, while convenience-store, grocery, fast-food, beauty and refund rows remain distinct rather than being blanket-rewritten to fuel.
- The existing V:AK formula scaffolding was preserved across the 128 appended rows; representative boundary rows from each write chunk were exported and inspected with formulas intact.
- **Joint Checking source was freshly re-read this run:** 127 posted rows in 2024 and 309 in 2025, 436 unique provider transaction IDs total, both bounded queries complete. The set includes payroll, card payments, savings/account transfers, HELOC payments, dividends/interest, user-named family-loan events and ordinary expenses; it therefore requires semantic treatment rather than a category-blind append.
- Existing user semantics were re-observed in source for the next pass: `Scarlett loan` plus three `Scarlett loan reimbursement` rows, and 34 `HELOC Payment` rows. These remain identity-specific corrections, not broad merchant inference rules.
- Remaining source after Rewards closure is **937 rows:** Joint Checking 436 and CREDIT CARD 501.
- **257 of 1,194 pre-canonical provider rows are reconciled.**
- PR #165 is open and non-draft at exact head `e4e08151c2ee181c21cc80d9e1559131fc6d3d20` before this checkpoint. It is currently reported non-mergeable against newer `main`, which is expected to be resolved only after historical reconciliation is complete and branch/main are semantically reconciled. No workflow run is attached to that exact head, so earlier green CI is not treated as proof.

## Acceptance criteria

1. Enumerate provider-visible posted transaction history before the current canonical ledger start until source exhaustion for every relevant linked account/history window.
2. Import missing historical rows into the existing `FinOps Ledger` using stable provider transaction identity and deterministic Event ID; preserve source account/date/signed amount/vendor/category/provenance and do not overwrite existing production rows.
3. Preserve transfers and zero-economic-spend rows as evidence while keeping their economic-spend treatment explicit; never infer income merely from retrieval inclusion.
4. Reconcile duplicates against existing canonical transaction IDs before each write batch.
5. Exact readback proves imported transaction IDs, dates, signed amounts/provenance, classifications and row counts; unavailable source gaps are recorded explicitly rather than filled by assumption.
6. Historical user corrections are applied only where identity and semantics are sufficiently supported; ambiguous transactions remain reviewable rather than guessed.
7. When finance history is fully reconciled or durably bounded by actual source unavailability, move next to Android inventory/scanning using existing `INV-001`, `INV-002`, `MOVE-001`, `IDENT-001`, `ASSET-001`, `ASSET-002`, `ASSET-003` and existing Android architecture.
8. Before merge, semantically reconcile this branch with current main, preserve newer compatible work, require exact-head CI, merge through PR, read back main, and require post-merge CI.

## Session alignment

### `FEATURES.md`
ALIGNED. Existing finance/recovery/evidence/asset semantics are being advanced; no parallel ledger or inventory model is created.

### `BACKLOG.md`
ALIGNED. `FIN-CANON-AUDIT-001` remains the highest-priority blocker. Android inventory/scanning remains next after historical finance closure or actual source-unavailability bounding.

### `ROADMAP.md`
ALIGNED. Provider truth, explicit provenance, canonical state, exact readback, and ordinary-user behavior remain the direction.

### Idea/backlog capture audit
CAPTURE AUDIT COMPLETE

- Historical reconciliation remains existing `FIN-CANON-AUDIT-001` work.
- Inventory/scanning remains represented by existing `INV-001`, `INV-002`, `MOVE-001`, `IDENT-001`, `ASSET-001`, `ASSET-002`, `ASSET-003`.
- No new material product feature was introduced this run.

### Direction result
ALIGNED

## Exact resume point

1. Re-read live destination rows after 1145 before the next write.
2. Re-query Joint Checking 2024/2025 partitions or reuse only if provider coverage/readback is still the same; compare all 436 provider transaction IDs against canonical state before mutation.
3. Apply existing persisted user corrections only to identities they actually support, including payroll, HELOC and family-loan semantics. Preserve ordinary transfers as zero-economic-spend evidence and keep ambiguous deposits/withdrawals reviewable rather than guessing.
4. Write only absent Joint Checking identities into the existing A:U schema in bounded batches, with exact post-write transaction-ID/date/amount/treatment comparisons and rollback only for an unverified batch.
5. Then reconcile CREDIT CARD in 2024/2025 partitions with the same identity/readback discipline.
6. Before PR merge, reconcile with current main and require exact-head CI. Do not begin Android inventory implementation until all 1,194 historical provider rows are reconciled or an actual source-unavailability boundary is proved.

## Canonical six-line status

Objective: Reconcile the complete provider-visible historical finance record into MIRROR before starting inventory scanning.
Progress: Four complete account histories totaling 257 rows are exactly reconciled; Joint Checking's remaining 436-row source is now freshly bounded and classified for the next write pass.
Last 24h: Rewards Signature's 128-row pre-canonical history was reconciled with exact identity checks while preserving payments, cash-back, refunds and non-fuel purchases as distinct semantics.
Deliverable: Canonical FinOps history backfilled to the provider's actual oldest available boundary with exact transaction-ID readback and explicit unavailable gaps.
Expected delivery: UNKNOWN
Blocker: none
