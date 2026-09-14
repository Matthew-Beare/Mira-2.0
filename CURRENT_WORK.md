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
- **Remote main verified this run:** `83e8bc1141683292da98dfda3351cf9f8ac0c67c`.

## Recovery contract

- Read `PROJECT_INSTRUCTIONS.md`, then this file.
- Verify remote `main`, this branch/head, PR #165, relevant CI, connected finance coverage, and live canonical workbook before every mutation.
- If Git or live canonical state contradicts this checkpoint, reconcile this file first. Never replay already-merged or concurrently completed work.
- Prior packet `M2-M1-046` is merged. PR #165 is the sole active historical-finance PR; duplicate draft PR #164 was closed unmerged.

## Objective

Close the historical finance coverage gap by reconciling every trustworthy provider-visible transaction into canonical MIRROR with stable provider identity, preserved evidence/provenance, idempotent writes, and exact readback. September 1, 2026 is not a history exclusion boundary.

## Verified state

- Connected transactions report `full_history`, available, complete for the bounded queries performed; freshness remains unknown.
- Provider-visible posted history before canonical ledger start (`2026-01-02`) is **1,194 rows across six accounts**, oldest verified row **2024-08-09**.
- Fully reconciled historical accounts: Joint Savings **19**, Home Savings **40**, Matthew's Primary Savings **70**, Rewards Signature **128**.
- **200 historical CREDIT CARD rows** are canonical. Existing production rows were not overwritten.
- Joint Checking was freshly re-bounded from provider data: **436 unique posted rows for 2024–2025** with complete bounded coverage (**127 in 2024 + 309 in 2025**).
- Fresh canonical export plus exact stable-ID subtraction previously exposed a checkpoint counting defect: only **100** Joint Checking provider identities were live at that check, not the previously claimed 120. The stale **577/1,194** checkpoint was rejected before further mutation.
- A prior bounded pass appended **10 identities proven absent** to `FinOps Ledger` rows **1501–1510** and synchronized the same deterministic Event IDs to `Spending Review` rows **1503–1512**. Exact readback verified all 10 ledger rows and all 10 review IDs.
- Concurrent canonical work then advanced Joint Checking further. A second fresh canonical export and provider-ID subtraction proved **151 of 436 Joint Checking identities** represented, leaving **285 Joint Checking identities**. All 2024 Joint Checking identities are represented; the remaining Joint Checking gap begins in 2025.
- A transient ledger/review synchronization gap at the prior newest canonical event was repaired by writing only the missing review Event ID; exact readback verified the repair.
- This run exported the current canonical workbook and re-queried the full **309-row 2025 Joint Checking provider set**. Stable-ID subtraction independently reproduced the checkpoint exactly: **24 already canonical + 285 absent** before mutation.
- This run then appended the first **5 proven-absent 2025 Joint Checking identities** to `FinOps Ledger` rows **1552–1556** and synchronized their deterministic Event IDs to `Spending Review` rows **1554–1558**. Exact readback verified every A:U ledger value and every review Event ID.
- The five newly reconciled rows preserve two Old Dominion payroll deposits as zero-economic-spend income evidence, one unresolved transfer-like deposit as `REVIEW`, one Mountain Electric household utility expense, and one user-corrected HELOC household debt payment.
- Current duplicate checks from the pre-write fresh export were zero for ledger Event IDs, ledger transaction IDs, and review Event IDs; the five-row batch was identity-subtracted immediately before write and exact-read after write.
- The replay preserves payroll/dividend rows as zero-economic-spend income evidence, internal transfers/card repayments as zero-economic-spend transfers, signed credits, necessary household utilities/insurance/HELOC/trash semantics where supported, raw provider categories, and unresolved ambiguity rather than guessing.
- Persisted corrections remain preserved, including Old Dominion payroll normalization, HELOC normalization away from mortgage, Google Store debt-service treatment, and user-confirmed household trash semantics.
- Provider transaction ID remains the canonical identity key and Event ID remains deterministic as `EVT-<provider transaction id>`.
- Successful writes use bounded `updateCells`; formula scaffolding is not targeted: `FinOps Ledger` writes touch A:U only and `Spending Review` writes touch J only.
- Historical reconciliation is now **613 of 1,194 provider rows**. Remaining exact gap is **581 = 280 Joint Checking + 301 CREDIT CARD**.
- Current verified append boundaries are **FinOps Ledger row 1556** and **Spending Review row 1558**, but these are not reservations; fresh identity subtraction and blank-destination readback are mandatory before every batch because concurrent canonical work can move them.
- PR #165 remains open/non-draft and is stale/conflicted against newer `main`. Its prior exact head had no workflow runs; no exact-head CI success claim is made. Reconcile with current `main` only after the live historical objective is complete or at the required pre-merge gate, preserving all newer compatible work.

## Acceptance criteria

1. Enumerate provider-visible posted history before the current canonical start until source exhaustion for every relevant linked account/window.
2. Import only absent rows using stable provider transaction identity and deterministic Event ID; preserve source account/date/signed amount/vendor/category/provenance and never overwrite existing production rows.
3. Preserve transfers and zero-economic-spend rows as evidence while keeping economic treatment explicit; never infer income from retrieval inclusion.
4. Subtract canonical transaction IDs before every write batch and re-read the destination immediately before mutation.
5. Exact readback proves IDs, dates, economic amounts/treatment, classifications, provenance and row counts; unavailable gaps are explicit, never fabricated.
6. Apply user corrections only where identity/evidence supports them; ambiguous transactions remain reviewable rather than guessed.
7. Once historical finance is fully reconciled or bounded by actual source unavailability, move next to Android inventory/scanning using existing `INV-001`, `INV-002`, `MOVE-001`, `IDENT-001`, `ASSET-001`, `ASSET-002`, `ASSET-003` and existing Android architecture.
8. Before merge, semantically reconcile this branch with current main, preserve newer compatible work, require exact-head CI, merge through PR, read back main, and require post-merge CI.

## Alignment

`FEATURES.md`: ALIGNED. Existing finance/recovery/evidence/asset semantics only; no parallel ledger or inventory model.

`BACKLOG.md`: ALIGNED. `FIN-CANON-AUDIT-001` remains the highest-priority blocker; Android inventory/scanning is next after finance closure/bounding.

`ROADMAP.md`: ALIGNED. Provider truth, provenance, canonical state, exact readback, failure isolation and ordinary-user behavior remain the direction.

### Idea/backlog capture audit

CAPTURE AUDIT COMPLETE. No new product feature was introduced; historical reconciliation and inventory/scanning remain represented by existing work IDs.

## Exact resume point

1. Verify fresh remote main, branch/PR head, exact-head CI, connected transaction coverage, and live canonical state.
2. Re-query Joint Checking 2025 and subtract live canonical transaction IDs. At the latest verified boundary **280 Joint Checking identities remain**. Treat this as a checkpoint, not a reservation, because concurrent canonical work may be active.
3. Re-export/re-read canonical state before writing. Verify ledger/review Event-ID set equality and blank destinations; repair only proven synchronization gaps before adding new provider identities.
4. Continue absent identities in bounded A:U slices and matching review Event IDs. Exact-read each slice before advancing. Preserve provider evidence, persisted corrections, zero-spend transfers/payroll, user-confirmed HELOC semantics, signed credits, and unresolved ambiguity.
5. After Joint Checking reaches complete identity coverage, re-bound and finish the **301 currently remaining CREDIT CARD** identities without replaying any concurrent work.
6. When all 1,194 historical rows are reconciled or an actual source-unavailability boundary is proved, perform full duplicate/entity/relation/broken-endpoint integrity proof, semantically reconcile PR #165 with current main, require exact-head CI, merge, and require post-merge CI before switching to Android inventory/scanning.

## Canonical six-line status

Objective: Reconcile every accessible historical provider transaction into canonical MIRROR exactly once before starting inventory scanning.
Progress: Fresh 2025 provider-to-ledger subtraction reproduced the prior 285-row Joint Checking gap exactly; five more proven-absent rows were written and exact-read, bringing verified coverage to 613 of 1,194 with 581 remaining.
Last 24h: Historical projection is live and idempotent; all 2024 Joint Checking history is represented, and stale counting plus ledger/review synchronization defects were caught by exact identity checks instead of being propagated.
Deliverable: Complete provider-to-MIRROR historical finance coverage with exact transaction-ID/readback proof and explicit source gaps.
Expected delivery: UNKNOWN
Blocker: none
