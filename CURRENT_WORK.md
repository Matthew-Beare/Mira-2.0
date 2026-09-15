# MIRA 2.0 CURRENT WORK

Git is authoritative for recovery, but mutable finance truth must be re-read from the connected provider and canonical FinOps sheet before work selection.

## Active packet

`FIN-CANON-AUDIT-001`

## Current objective

Continue canonical transaction reconciliation and high-confidence review-queue reduction. Compare exact provider identities against `FinOps Ledger.Transaction ID` before any projection; never infer identity from date/amount. Classify only where provider semantics, durable user rules, receipts, or resolved precedent are strong. Leave low-confidence purpose/necessity explicitly reviewable.

## User reprioritization

On 2026-09-15 the user explicitly instructed MIRA to work more transactions. This displaces `FIN-MODEL-TARGET-002` until the transaction-audit packet is checkpointed or the user reprioritizes again.

## Canonical source state

- Finances account history coverage remains `full_history`; freshness remains `unknown`.
- Prime Visa source range remains bounded from 2024-08-09 through 2026-09-11.
- Prior bounded provider reads returned 150 transactions for 2024, 351 for 2025, and 174 for 2026: 675 total.
- `FinOps Ledger.Transaction ID` remains the stable provider identity key.
- Joint Checking was previously proven complete at 669/669 provider identities.
- The live Financial Escape Command Center has changed since the prior finance checkpoint, including older Prime Visa rows already present in canonical state. Do not assume the old provider-minus-canonical gap; recompute mechanically before projecting anything.

## 2026-09-15 transaction-classification pass

Live `Spending Review` began this pass with 990 rows marked `NEEDS REVIEW` and ended at 837: 153 rows removed from review through canonical rule repair and high-confidence resolution.

Applied/verified durable logic:
- Rewards Signature・9854 rows whose provider category matches `transportation_fuel` resolve as vendor Gas / category Fuel / NECESSARY under the user's Ducks Unlimited fuel rule.
- Effective Allowance now resolves those Ducks fuel rows to `NO ALLOWANCE` instead of leaving them `UNKNOWN`.
- Exact Amazon Pharmacy rows resolve to `NO ALLOWANCE`; prior Health / medication + NECESSARY treatment remains intact.
- New explicit user rule: doctor, dentist, and medication transactions are always `NECESSARY`.
- `Effective Necessity` now automatically marks observed medical provider categories `dental_care`, `pharmacy_supplements`, `other_medical`, `vision_care`, and `primary_care` as `NECESSARY`.
- Hair/beauty provider categories are intentionally excluded from that medical rule so merchants such as Ulta, Great Clips, salons, cosmetics, etc. do not become necessary merely because the provider taxonomy groups them under health/wellness.

Additional high-confidence rows resolved in this pass included truck gas, Skyline Internet recurring utilities by resolved precedent, Dermatology Associates medical care, and prior user-confirmed outdoor-sign classification where only allowance resolution remained safe.

## Required work

1. Re-read live canonical workbook and provider state before each new mutation batch.
2. Recompute Prime Visa provider-minus-canonical identity set mechanically before projecting any missing rows; never use date-based estimates.
3. Project only proven-missing provider IDs with provenance, stable identity, correct signed economic treatment, and no duplicate economic effects.
4. Continue reducing the 837-row review queue using deterministic merchant/category rules, receipts, Gmail/Drive evidence, and prior confirmed user classifications.
5. Prefer family-level canonical logic fixes over hand-editing repeated rows when the evidence supports a durable rule.
6. Keep ambiguous multipurpose merchants and unclear purchase purpose in `NEEDS REVIEW`; do not guess.
7. After each mutation batch, read back affected rows and current queue count.
8. Before packet completion, verify duplicate Event IDs = 0, duplicate provider transaction IDs = 0, and review-surface/ledger parity for reviewable Event IDs.

## Displaced packet checkpoint — FIN-MODEL-TARGET-002

The model-target packet is paused, not abandoned.

- Objective: retire April 1, 2027 as the active Debt Escape target and make March 1, 2027 the governing target throughout the live Financial Escape Command Center; synchronize dependent calculations/presentation surfaces; add six-month weekly spending to Forecast Charts; elevate rolling net worth on Dashboard.
- Acceptance gates were not completed before reprioritization.
- Re-read the live Command Center on resume; Workspace edits may have occurred after the Git checkpoint.
- Exact resume point: audit the live Command Center for remaining April-target dependencies, Forecast Charts weekly-spend support, and Dashboard rolling-net-worth placement; then apply one synchronized target migration and read back dependent outputs.

## Acceptance gates — FIN-CANON-AUDIT-001

1. Provider and canonical identity sets are compared mechanically using stable transaction IDs.
2. Only proven-missing transactions are projected; replay remains idempotent with zero duplicate economic effects.
3. Source provenance and provider identity are preserved for every projected row.
4. High-confidence classifications are applied; ambiguous rows stay explicitly reviewable.
5. Canonical ledger and review surfaces agree on reviewable Event IDs after mutation.
6. Readback confirms no duplicate Event IDs or provider transaction IDs.
7. Remaining provider gap and exact next batch are recorded here before switching work.

## Next bounded step

Continue the next high-confidence review families from the current 837-row queue, prioritizing deterministic medical/dental/pharmacy, recurring utilities, explicit fuel/truck descriptors, and other merchants with resolved precedent. Then recompute the exact Prime Visa provider-minus-canonical Transaction ID set before any new transaction projection.