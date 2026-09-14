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
- Remote `main` and the live workbook had advanced beyond the earlier branch checkpoint: **200 historical CREDIT CARD rows** are canonical. Existing production rows were not overwritten.
- Joint Checking was freshly re-bounded from provider data this run: **436 unique posted rows for 2024–2025** with complete bounded coverage (**127 in 2024 + 309 in 2025**).
- Fresh canonical export plus exact stable-ID subtraction exposed a checkpoint counting defect: only **100** Joint Checking provider identities were live before this run, not the previously claimed 120. The stale **577/1,194** checkpoint was therefore rejected and corrected to **557/1,194** before further mutation.
- This run then appended **10 identities proven absent** from Joint Checking to `FinOps Ledger` rows **1501–1510** and synchronized the same deterministic Event IDs to `Spending Review` rows **1503–1512**.
- Exact post-write readback verified all **10 new ledger rows** across A:U and all **10 corresponding review Event IDs**. The slice preserves payroll as zero-economic-spend income evidence, credit-card repayments and an insurance-designated deposit as zero-economic-spend transfers, and Mountain Electric as necessary household utility spend. Raw provider category provenance and provider transaction identity are preserved.
- Persisted corrections remain preserved, including Old Dominion payroll normalization, HELOC normalization away from mortgage, Google Store debt-service treatment, and user-confirmed household trash semantics.
- Provider transaction ID remains the canonical identity key and Event ID remains deterministic as `EVT-<provider transaction id>`.
- Successful writes use bounded `updateCells`; formula scaffolding is not targeted: `FinOps Ledger` writes touch A:U only and `Spending Review` writes touch J only.
- Historical reconciliation is now **567 of 1,194 provider rows**. Remaining exact gap is **627 = 326 Joint Checking + 301 CREDIT CARD**.
- Current verified append boundaries are **FinOps Ledger row 1510** and **Spending Review row 1512**, but these are not reservations; fresh identity subtraction and blank-destination readback are mandatory before every batch because concurrent canonical work can move them.
- PR #165 remains open/non-draft and is currently stale/conflicted against newer `main`. Its prior exact head had no workflow runs; no exact-head CI success claim is made. Reconcile with current `main` only after the live historical objective is complete or at the required pre-merge gate, preserving all newer compatible work.

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
2. Re-query Joint Checking 2024/2025 and subtract live canonical transaction IDs. At this checkpoint **326 Joint Checking identities remain**; do not trust arithmetic from older checkpoints over fresh stable-ID subtraction.
3. Fresh-read the next destinations; only if blank, continue absent identities in bounded A:U slices and write matching Event IDs into the review queue. Current last verified rows are ledger **1510** and review **1512**.
4. Exact-read each slice before advancing. Preserve provider evidence, persisted corrections, zero-spend transfers/payroll, user-confirmed HELOC semantics, signed credits, and unresolved ambiguity.
5. After Joint Checking reaches complete identity coverage, re-bound and finish the **301 currently remaining CREDIT CARD** identities without replaying any concurrent work.
6. When all 1,194 historical rows are reconciled or an actual source-unavailability boundary is proved, perform full duplicate/entity/relation/broken-endpoint integrity proof, semantically reconcile PR #165 with current main, require exact-head CI, merge, and require post-merge CI before switching to Android inventory/scanning.

## Canonical six-line status

Objective: Reconcile every accessible historical provider transaction into canonical MIRROR exactly once before starting inventory scanning.
Progress: Fresh stable-ID subtraction corrected a 20-row checkpoint overcount; 10 proven-absent Joint Checking identities were then added and exactly read back, bringing verified coverage to 567 of 1,194 with 627 remaining.
Last 24h: Historical projection is live and idempotent, and this run caught and corrected stale reconciliation arithmetic before it could cause duplicate or skipped history.
Deliverable: Complete provider-to-MIRROR historical finance coverage with exact transaction-ID/readback proof and explicit source gaps.
Expected delivery: UNKNOWN
Blocker: none
