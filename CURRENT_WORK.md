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
- **Remote PR head verified at run start:** `c51aab505e82eae23e0d12c97ac360f06bd7a2ce`.

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
- Rewards Signature treatment preserved source semantics: credit-card payments are zero-economic-spend `EXCLUDED_TRANSFER`; cash-back rewards are zero-economic-spend `EXCLUDED_INCOME`; verified fuel uses existing user corrections, while convenience-store, grocery, fast-food, beauty and refund rows remain distinct rather than being blanket-rewritten to fuel.
- **Joint Checking source is freshly bounded:** 127 posted rows in 2024 and 309 in 2025, **436 unique provider transaction IDs**, and both bounded queries report complete full-history coverage.
- Persisted finance corrections were re-read before mutation. They confirm identity-specific Scarlett loan/reimbursement semantics, HELOC normalization away from mortgage, and Old Dominion payroll normalization without touching unrelated utility transactions.
- **Joint Checking historical ingestion now has 50 source identities written and exactly read back** in canonical rows 1146–1195. Exact readback matched transaction identity, date serial, economic-spend treatment, vendor/category semantics, confidence and provenance for both bounded write slices.
- The 50-row canonical slice preserves zero-economic-spend transfers and payroll/income, user-confirmed HELOC debt payments, the user-confirmed Scarlett family-help loan event, ordinary bills/shopping/insurance/gifts, and a merchant credit as negative economic spend. No source row was discarded to simplify the model.
- The existing V:AK formula scaffolding was not targeted by these writes; A:U only was mutated.
- Canonical append boundary is now **row 1196** for the next absent Joint Checking identity.
- Remaining source after this checkpoint is **887 rows:** Joint Checking 386 and CREDIT CARD 501.
- **307 of 1,194 pre-canonical provider rows are reconciled.**
- PR #165 remains open and non-draft. No CI claim is made for the new checkpoint commits until an exact-head run exists. The PR was non-mergeable against newer `main` at run start; resolve that only after historical reconciliation is complete and branch/main are semantically reconciled.

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

1. Verify remote main/PR head and re-read canonical row 1195 plus the next blank destination row before mutation.
2. Continue Joint Checking from source identity 51 of 436; **386 source identities remain**. Re-query the bounded partition if provider coverage or source evidence changed.
3. Apply persisted user corrections only to identities they support. Keep ordinary transfers at zero economic spend, payroll/income excluded from spend, HELOC payments normalized to the user-confirmed HELOC, supported reimbursements as negative economic-spend credits, and ambiguous transactions reviewable rather than guessed.
4. Append only absent identities into A:U in bounded batches beginning at row 1196. Preserve V:AK formula scaffolding and exact-read each written batch before advancing the checkpoint.
5. After all 436 Joint Checking identities are present and exactly reconciled, reconcile CREDIT CARD's remaining 501 historical rows with the same identity/readback discipline.
6. Before PR merge, semantically reconcile with current main and require exact-head CI. Do not begin Android inventory implementation until all 1,194 historical provider rows are reconciled or an actual source-unavailability boundary is proved.

## Canonical six-line status

Objective: Reconcile the complete provider-visible historical finance record into MIRROR before starting inventory scanning.
Progress: 307 of 1,194 historical provider rows are reconciled; Joint Checking now has its first 50 historical identities written and exactly read back, leaving 386 there plus 501 on the final card account.
Last 24h: Rewards Signature was fully reconciled and Joint Checking ingestion advanced through 50 verified rows with persisted payroll, HELOC and family-help semantics applied before mutation.
Deliverable: Canonical FinOps history backfilled to the provider's actual oldest available boundary with exact transaction-ID readback and explicit unavailable gaps.
Expected delivery: UNKNOWN
Blocker: none
