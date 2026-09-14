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
- **Current remote main observed:** `166938afd3f6d7a218f2cbaa0432962359d2101e`.
- **Current branch head observed before this checkpoint:** `d876232fcd13e3ab2ba026cd47b1d8e3986e50c9`.

## Recovery contract

- Read `PROJECT_INSTRUCTIONS.md`, then this file.
- Verify remote `main`, this packet branch/head, PR state, and relevant CI before doing work.
- If Git contradicts this checkpoint, reconcile this file first. Never repeat merged work.
- Prior packet `M2-M1-046` is merged. PR #165 remains the active historical-finance packet and must be semantically reconciled against current `main` before merge.

## Objective

Close the historical finance coverage gap by reconciling all trustworthy provider-visible history into canonical MIRROR finance state with stable provider transaction identity, provenance, and exact readback. Do not use 2026-09-01 as a history exclusion boundary.

## Verified evidence this packet

- Connected finance transaction coverage re-read on 2026-09-14 reports `full_history`, available and complete for bounded queries; freshness remains unknown.
- Exact provider aggregation for posted rows before the canonical ledger start (`2026-01-02`) yielded **1,194 rows across six accounts**.
- The oldest verified provider-visible row in that bounded historical set is dated `2024-08-09`; account-specific oldest dates range from 2024-08-09 through 2024-08-30.
- Canonical `Financial Escape` / `FinOps Ledger` began at `2026-01-02` before this packet; direct sheet readback confirmed no earlier production rows before this packet's backfill writes.
- Provider rows expose stable transaction identity, account identity, posted date, signed amount, merchant/name/category data, and confidence suitable for deterministic source identity. Missing check payee/memo/image data remains unknown unless corroborated by another source.
- **Joint Savings is reconciled:** all 19 historical provider rows were appended and exactly read back.
- **Home Savings is reconciled:** all 40 historical provider rows were appended and exactly read back without overwriting adjacent current production state.
- **Matthew's Primary Savings is now reconciled:** all 70 historical provider transaction identities were appended and exact live-workbook comparison confirms all 70 provider IDs are present canonically with no duplicate canonical transaction IDs.
- One provider misclassification was corrected during Primary Savings readback: an explicitly named merchant refund was retained as a negative economic-spend credit instead of being excluded merely because the provider labeled it as income.
- A Rewards Signature historical write was rejected after exact exported-workbook reconciliation proved that the written identities did not match the current 128-row provider source set. The entire tentative A:U write range was cleared while preserving V:AK formula scaffolding. **No Rewards Signature rows are credited as reconciled by this checkpoint.**
- Exact post-rollback readback confirms the Rewards destination is blank in A:U and formulas remain intact.
- Historical source partition sizes were independently re-proven for the remaining large accounts: Joint Checking = **436** rows (127 in 2024, 309 in 2025); CREDIT CARD = **501** rows (150 in 2024, 351 in 2025). These year partitions keep every next query below the provider row-return ceiling.
- Canonical transaction-ID audit on the exported live workbook found **zero duplicate canonical transaction IDs** at this checkpoint.
- **129 of 1,194 pre-canonical provider rows are reconciled. 1,065 remain:** Rewards Signature 128, Joint Checking 436, CREDIT CARD 501.
- PR #165 is open and draft. Before this checkpoint its exact head was `d876232fcd13e3ab2ba026cd47b1d8e3986e50c9`; exact-head tests and secret-scan were green (runs 672 and 673).
- Remote main independently read back at `166938afd3f6d7a218f2cbaa0432962359d2101e` before this checkpoint.

## Acceptance criteria

1. Enumerate provider-visible posted transaction history before the current canonical ledger start until source exhaustion for every relevant linked account/history window.
2. Import missing historical rows into the existing `FinOps Ledger` using stable provider transaction identity and deterministic Event ID; preserve source account/date/signed amount/vendor/category/provenance and do not overwrite existing production rows.
3. Preserve transfers and zero-economic-spend rows as evidence while keeping their economic-spend treatment explicit; never infer income merely from retrieval inclusion.
4. Reconcile duplicates against existing canonical transaction IDs before each write batch.
5. Exact readback proves imported transaction IDs, dates, signed amounts/provenance, classifications and row counts; unavailable source gaps are recorded explicitly rather than filled by assumption.
6. Historical user corrections already supplied during reconciliation are applied only when identity is sufficiently supported; ambiguous checks remain unresolved.
7. When finance history is fully reconciled or durably bounded by actual source unavailability, checkpoint completion and move next to the Android inventory/scanning vertical reusing `INV-001`, `INV-002`, `MOVE-001`, `IDENT-001`, `ASSET-001`, `ASSET-002`, `ASSET-003`.
8. Before merge, reconcile this branch against current main, preserve the newer main checkpoint semantics, rerun affected CI, and verify post-merge main.

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
- No new material product feature is introduced by this reconciliation checkpoint.

### Direction result
ALIGNED

## Exact resume point

1. Verify the new branch head from this checkpoint and require exact-head CI green before unrelated growth.
2. Re-read the live Rewards Signature destination immediately before writing. Query the 128-row provider set fresh and import only identities absent from canonical state.
3. Use an exact source-to-live-workbook ID-set comparison after every bounded write. If any provider identity is absent or any unexpected identity appears, roll back only the tentative batch and do not credit it.
4. After Rewards Signature is proven, continue Joint Checking in the verified 2024/2025 partitions (127 + 309), then CREDIT CARD in the verified 2024/2025 partitions (150 + 351). Re-read destination state before every write.
5. Extend `FinOps Ledger` row capacity/formula scaffolding before any batch would exceed the current sheet grid; preserve all existing formulas and production rows.
6. Require global provider-precanonical minus canonical transaction-ID set = zero and canonical duplicate transaction/Event IDs = zero before declaring `FIN-CANON-AUDIT-001` historical coverage closed.
7. Before PR merge, semantically reconcile the branch with current main because `CURRENT_WORK.md` is a high-contention checkpoint surface.
8. Do not begin Android inventory implementation until all 1,194 historical provider rows are reconciled or an actual source-unavailability boundary is durably proven.

## Six-line customer status

Objective: Reconcile the complete provider-visible historical finance record into MIRROR before starting inventory scanning.
Progress: A third full historical account is now reconciled, bringing verified coverage to 129 of 1,194 rows; a mismatched tentative batch was detected by exact ID readback and cleanly rolled back before it could contaminate canonical state.
Last 24h: Historical finance coverage was proven back to 2024-08-09, three complete account histories were added, and exact source-to-canonical verification now gates every remaining batch.
Deliverable: Canonical FinOps history backfilled to the provider's actual oldest available boundary with exact transaction-ID readback and explicit unavailable gaps.
Expected delivery: UNKNOWN
Blocker: none
