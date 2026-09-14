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
- **Remote branch head verified this run:** `8edad59bf577d1e83806f04fabf10d402a4465aa`.

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
- A prior Rewards Signature tentative write failed exact identity comparison and was fully rolled back in A:U while preserving V:AK formula scaffolding; none of that rejected batch is credited.
- Rewards Signature history before `2026-01-02` was freshly verified at **128 posted rows**, complete for query. The set contains 96 provider-classified fuel rows plus card payments, cash-back rewards, and a small number of clearly non-fuel merchant rows requiring their own semantics rather than blanket fuel rewriting.
- Live canonical workbook readback confirmed rows beginning at **1018** are blank in A:U and retain the expected V:AK formula scaffolding, providing a safe bounded destination for the next exact write.
- Remaining large-account source partitions stay bounded below provider return limits: Joint Checking = **436** rows (127 in 2024, 309 in 2025); CREDIT CARD = **501** rows (150 in 2024, 351 in 2025).
- **129 of 1,194 pre-canonical provider rows are reconciled. 1,065 remain:** Rewards Signature 128, Joint Checking 436, CREDIT CARD 501.
- PR #165 is open and non-draft at verified head `8edad59bf577d1e83806f04fabf10d402a4465aa` before this checkpoint. No workflow/check run is currently attached to that exact head, so earlier green CI is not treated as proof for the current head.

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

1. Re-read live A:U destination immediately before writing Rewards Signature.
2. Re-query the 128-row Rewards Signature source set fresh and compare transaction IDs against canonical state immediately before mutation.
3. Write only absent identities into the existing A:U schema. Preserve payment/cash-back/non-fuel rows with their own semantics; apply the user-confirmed Ducks fuel normalization only where fuel identity is supported.
4. Exact source-to-canonical transaction-ID set comparison must show all 128 source identities represented once and no unexpected identities in the tentative batch. On any mismatch, roll back only that batch.
5. Then continue Joint Checking in 2024/2025 partitions, followed by CREDIT CARD in 2024/2025 partitions, with pre-write readback and post-write exact identity checks for every batch.
6. Before PR merge, reconcile with current main and require exact-head CI. Do not begin Android inventory implementation until all 1,194 historical provider rows are reconciled or an actual source-unavailability boundary is proved.

## Canonical six-line status

Objective: Reconcile the complete provider-visible historical finance record into MIRROR before starting inventory scanning.
Progress: Repository/PR state was reconciled to the live branch head; three account histories totaling 129 rows remain verified complete and the next Rewards Signature destination is bounded for exact write/readback.
Last 24h: Historical finance coverage was proven back to 2024-08-09 and three complete account histories totaling 129 rows were reconciled with exact identity checks.
Deliverable: Canonical FinOps history backfilled to the provider's actual oldest available boundary with exact transaction-ID readback and explicit unavailable gaps.
Expected delivery: UNKNOWN
Blocker: none
