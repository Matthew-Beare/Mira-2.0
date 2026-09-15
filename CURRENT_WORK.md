# MIRA 2.0 CURRENT WORK

Git is authoritative for recovery, but mutable finance truth must be re-read from the connected provider and canonical FinOps sheet before work selection.

## Status surface
Objective: Close the historical finance identity gap, then deliver Android inventory scanning against the existing canonical inventory graph.
Progress: Re-read connected finance history across the historical boundary and verified posted transaction coverage reaches 2024-08-09; an explicit query for dates before 2024-08-09 returned zero rows, durably bounding the accessible provider history instead of imposing an artificial MIRA start date.
Last 24h: Reduced the canonical Spending Review queue from 990 to 673 while repairing override formulas and resolving receipt/provider-backed classifications without guessing ambiguous rows.
Deliverable: Exact provider-minus-canonical Transaction ID reconciliation across all accessible history, followed by Android camera/QR/barcode inventory capture against the existing asset graph.
Expected delivery: UNKNOWN.
Blocker: none.

## Active packet

`FIN-CANON-AUDIT-001`

## Current objective

Close the remaining historical finance coverage gap using stable provider identity and exact canonical readback. Historical evidence is preserved; unavailable history is represented explicitly. Continue high-confidence review-queue reduction only where provider semantics, durable user rules, receipts, or resolved precedent are strong.

## Historical coverage verification — 2026-09-15

- Connected Finances reports transaction coverage `full_history` and query-complete for the requested slices; freshness remains `unknown`.
- Exact posted-history slice `date >= 2026-08-01` returned 237 rows through 2026-09-11.
- Exact posted-history slice `date < 2026-08-01` first returned 1,000 rows with more available, spanning 2025-07-13 through 2026-07-31.
- A second bounded query `date < 2025-07-13` returned 854 rows, spanning 2024-08-09 through 2025-07-11.
- A boundary probe `date < 2024-08-09` returned exactly zero rows with `has_more=false` and query-complete coverage.
- Therefore the currently accessible connected transaction-history boundary is **2024-08-09**. Do not claim earlier history is reconciled or unavailable in reality; claim only that the connected source currently exposes no posted transactions before this boundary.
- This supersedes any implied September 2026 finance start boundary. September may bound recurring processes, never historical truth.

## Canonical source state

- `FinOps Ledger.Transaction ID` is the stable provider identity key. Joint Checking was previously proven complete at 669/669 provider identities.
- Prime Visa source range was previously re-read as exactly 675 posted rows / 675 distinct provider transaction IDs, bounded 2024-08-09 through 2026-09-11, confirming zero provider-side duplicate transaction IDs in that bounded source set.
- The live Financial Escape Command Center changes independently of Git checkpoints; recompute provider-minus-canonical identity sets mechanically before projecting anything.
- Preserve original evidence and provenance. Never delete or overwrite historical production rows to simplify the model.

## 2026-09-15 transaction-classification checkpoint

`Spending Review` began these consecutive transaction passes with 990 rows marked `NEEDS REVIEW`. Latest verified checkpoint is **673**, a reduction of **317 rows**. Ambiguous rows remain reviewable.

### Deterministic canonical rules now active

- Provider `transportation / transportation_fuel` => category Fuel, vendor Gas, NECESSARY, NO ALLOWANCE across cards.
- Ducks/Rewards Signature・9854 rows already normalized to Fuel + Gas + NECESSARY also resolve NO ALLOWANCE even where older provider taxonomy was only generic transportation.
- Exact provider grocery category `groceries / groceries_groceries` => Groceries / NECESSARY / NO ALLOWANCE.
- Provider education category `education / education_tuition_courses` => Education / NECESSARY / NO ALLOWANCE.
- `bills_utilities / bills_utilities_*` => Utilities / NECESSARY / NO ALLOWANCE.
- `financial / financial_insurance` => Insurance / NECESSARY / NO ALLOWANCE.
- `financial / financial_taxes` => Taxes / NECESSARY / NO ALLOWANCE.
- Medical provider categories `dental_care`, `pharmacy_supplements`, `other_medical`, `vision_care`, and `primary_care` => NECESSARY / NO ALLOWANCE. Hair/beauty is deliberately excluded.
- Household-funded rows already proven NECESSARY resolve NO ALLOWANCE.
- Amazon Pharmacy remains Health / medication / NECESSARY / NO ALLOWANCE.

### Structural repairs

- Fixed `FinOps Ledger` review-override lookup formulas that incorrectly began at `Spending Review` row 5 and ignored first data row 4. V/X/Z/AB/AF now read from row 4 through 3028 by exact Event ID.
- Repaired a stale hard-coded `NEEDS REVIEW` status on the receipt-backed Walmart $159.50 row; normal formula now evaluates it READY.

### Evidence-backed examples already resolved/refined

- Walmart $159.50 (2026-09-11): receipt-backed 33-item delivery/grocery order; Groceries / NECESSARY / NO ALLOWANCE; READY.
- Tacoma Subaru $139.39 and SubaruOnlineParts $125.22: OEM repair parts/hardware; Auto repair / NECESSARY / NO ALLOWANCE; READY.
- September County Clerk $75.67: user-confirmed vehicle registration; NECESSARY / NO ALLOWANCE; READY. Separate August same-amount row remains unresolved.
- Legacy HELOC payment $2,311.24 on 2025-03-15: corrected by exact recurrence against 52 other canonical HELOC-payment rows; READY.
- Modification/tool rows retain unresolved necessity/allowance where evidence does not establish repair-vs-upgrade intent.

## Required work

1. Re-read live canonical workbook/provider state before each mutation batch.
2. Mechanically compare provider transaction IDs against canonical `FinOps Ledger.Transaction ID` across the entire accessible boundary, account by account; never infer identity from date/amount.
3. Project only proven-missing provider IDs with provenance, stable identity, correct signed economic treatment, and no duplicate economic effects.
4. Explicitly record source-unavailable historical gaps rather than inventing a start date.
5. Continue receipt/order-backed recent higher-dollar ambiguous rows; preserve low-confidence rows for voice review.
6. After each mutation batch, read back affected rows and exact queue count.
7. Before packet completion, verify duplicate Event IDs = 0, duplicate provider transaction IDs = 0, and review-surface/ledger parity for reviewable Event IDs.
8. Once finance history is closed or durably bounded, switch priority to Android inventory/scanning using existing INV-001, INV-002, MOVE-001, IDENT-001, ASSET-001/002/003 and Android architecture. Do not create a parallel inventory model.

## Acceptance gates — FIN-CANON-AUDIT-001

1. Provider and canonical identity sets are compared mechanically using stable transaction IDs across all accessible history.
2. Only proven-missing transactions are projected; replay remains idempotent with zero duplicate economic effects.
3. Source provenance/provider identity are preserved.
4. Source-unavailable history is explicitly bounded.
5. High-confidence classifications are applied; ambiguous rows remain reviewable.
6. Canonical ledger/review surfaces agree on reviewable Event IDs.
7. Readback confirms no duplicate Event IDs or provider transaction IDs.

## Next bounded step

Use the verified **2024-08-09** connected-history boundary. Re-read live `FinOps Ledger.Transaction ID`, then compare stable provider identities account-by-account across the complete accessible range. Prime Visa and Joint Checking already have strong prior evidence; verify them against current canonical state rather than trusting stale counts. Project only exact missing IDs. After the historical finance identity gap is zero or durably bounded, begin the Android inventory/scanning vertical.