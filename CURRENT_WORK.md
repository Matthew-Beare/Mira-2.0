# MIRA 2.0 CURRENT WORK

Git is authoritative for recovery, but mutable finance truth must be re-read from the connected provider and canonical FinOps sheet before work selection.

## Status surface
Objective: Close the historical finance identity gap, then deliver Android inventory scanning against the existing canonical inventory graph.
Progress: Re-read live Prime Visa provider history and mechanically verified 675 posted rows = 675 distinct provider transaction IDs, bounded 2024-08-09 through 2026-09-11; no provider-side duplicates exist in that bounded source set.
Last 24h: Reduced the canonical Spending Review queue from 990 to 673 while repairing override formulas and resolving receipt/provider-backed classifications without guessing ambiguous rows.
Deliverable: Exact Prime Visa provider-minus-canonical Transaction ID reconciliation with any proven-missing rows projected idempotently, or the gap durably closed at zero.
Expected delivery: UNKNOWN.
Blocker: none.

## Active packet

`FIN-CANON-AUDIT-001`

## Current objective

Continue canonical transaction reconciliation and high-confidence review-queue reduction. Compare exact provider identities against `FinOps Ledger.Transaction ID` before any projection; never infer identity from date/amount. Classify only where provider semantics, durable user rules, receipts, or resolved precedent are strong. Leave low-confidence purpose/necessity explicitly reviewable.

## User reprioritization

On 2026-09-15 the user explicitly instructed MIRA to work more transactions. This displaces `FIN-MODEL-TARGET-002` until this transaction-audit packet is checkpointed or the user reprioritizes again.

## Canonical source state

- Finances account history coverage remains `full_history`; freshness remains `unknown`.
- Prime Visa source range was re-read on 2026-09-15 and is exactly 675 posted rows / 675 distinct provider transaction IDs, bounded from 2024-08-09 through 2026-09-11. This confirms zero provider-side duplicate transaction IDs in the bounded source set.
- `FinOps Ledger.Transaction ID` remains the stable provider identity key. Joint Checking was previously proven complete at 669/669 provider identities.
- The live Financial Escape Command Center has changed since older finance checkpoints; recompute provider-minus-canonical identity sets mechanically before projecting anything.
- No new provider rows were projected during the current classification pass; work was limited to canonical rule repair, overrides, receipt-backed classification, and readback.

## 2026-09-15 transaction-classification checkpoint

`Spending Review` began these consecutive transaction passes with 990 rows marked `NEEDS REVIEW`. Exact live recount after the latest mutations is **673**, a reduction of **317 rows**. Ambiguous rows remain reviewable.

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
- User rule is durable in `MIRA Durable Operating Addenda`: doctors/medical providers, dentists/dental, and medication/pharmacy are always NECESSARY when evidence establishes that purpose; explicit provider fuel is sufficient Fuel/Gas evidence.

### Structural repairs

- Fixed `FinOps Ledger` review-override lookup formulas that incorrectly began at `Spending Review` row 5 and therefore ignored the first data row 4. V/X/Z/AB/AF now read from row 4 through 3028 by exact Event ID.
- This repair immediately allowed the user-confirmed outdoor-sign transaction to resolve READY.
- Repaired a stale hard-coded `NEEDS REVIEW` status on the receipt-backed Walmart $159.50 row; the normal formula now evaluates it READY.

### Receipt/evidence-backed rows resolved or refined

- Walmart $159.50 (2026-09-11): receipt-backed 33-item delivery/grocery order; Groceries / NECESSARY / NO ALLOWANCE; READY.
- Tacoma Subaru $139.39: backing plate plus intermediate-pipe bolts/springs/nuts; Auto repair / NECESSARY / NO ALLOWANCE; READY.
- SubaruOnlineParts $125.22: remaining OEM repair hardware after backordered hub assemblies were removed; Auto repair / NECESSARY / NO ALLOWANCE; READY.
- September County Clerk $75.67: user-confirmed vehicle registration; Vehicle registration / NECESSARY / NO ALLOWANCE; READY. The separate August same-amount County Clerk row remains unresolved pending stronger evidence.
- Legacy HELOC payment $2,311.24 on 2025-03-15: corrected to NECESSARY / NO ALLOWANCE by exact recurrence against 52 other canonical HELOC-payment rows; READY.
- Mishimoto $148.62: locking lug nuts; Auto repair / UNNECESSARY; allowance owner unresolved.
- System Motorsports $95.25: Project Kics hubrings; Auto repair / UNNECESSARY; allowance owner unresolved.
- Evasive Motorsports $2,415.12: four Enkei wheels plus lug nuts; Auto repair / UNNECESSARY; allowance owner unresolved.
- Eastwood $149.42: fender roller tool; Tools / project / UNNECESSARY; allowance owner unresolved.
- Pro Torque Tools $304.58: two CDI torque wrenches; Tools / project category resolved; necessity/allowance unresolved.
- JEGS $85.38 + $61.30: exact pair equals one $146.68 receipt for ARP Miata wheel studs; Auto repair category resolved; repair-vs-upgrade necessity/allowance remains unresolved.

## Remaining queue character

The 673 remaining rows are now disproportionately evidence-limited: mixed Amazon/Walmart/Target purchases, convenience-store charges without fuel evidence, auto parts/modification purchases where repair-vs-upgrade intent is unclear, Audible/history rows where study-vs-entertainment purpose is unresolved, digital services, beauty/personal-care rows, gifts/clothing, and older generic checks/PayPal purchases. Do not broad-classify these from merchant name alone.

## Required work

1. Re-read live canonical workbook/provider state before each new mutation batch.
2. Continue receipt/order-backed work on recent higher-dollar ambiguous rows first; preserve low-confidence rows for voice review.
3. Prefer exact recurring-pattern and provider-semantic rules over repetitive manual edits, but do not broaden rules past the evidence.
4. Recompute the Prime Visa provider-minus-canonical `Transaction ID` set mechanically before projecting any missing rows.
5. Project only proven-missing provider IDs with provenance, stable identity, correct signed economic treatment, and no duplicate economic effects.
6. After each mutation batch, read back affected rows and exact queue count.
7. Before packet completion, verify duplicate Event IDs = 0, duplicate provider transaction IDs = 0, and review-surface/ledger parity for reviewable Event IDs.

## Displaced packet checkpoint — FIN-MODEL-TARGET-002

Paused, not abandoned. Re-read the live Command Center before resume because Workspace model/dashboard edits continued after the earlier Git checkpoint. Do not reconstruct model state from chat.

## Acceptance gates — FIN-CANON-AUDIT-001

1. Provider and canonical identity sets are compared mechanically using stable transaction IDs.
2. Only proven-missing transactions are projected; replay remains idempotent with zero duplicate economic effects.
3. Source provenance/provider identity are preserved.
4. High-confidence classifications are applied; ambiguous rows remain reviewable.
5. Canonical ledger/review surfaces agree on reviewable Event IDs.
6. Readback confirms no duplicate Event IDs or provider transaction IDs.
7. Remaining provider gap and exact next batch are recorded before switching work.

## Next bounded step

Resume from **673 NEEDS REVIEW**. Mechanically compare the now re-verified 675 Prime Visa provider transaction IDs against live canonical `FinOps Ledger.Transaction ID`; project only exact missing IDs if any. Then continue recent receipt-backed mixed retail/auto/tool classification and exact recurring-pattern anomalies. Historical Amazon remains evidence-limited and should not be guessed.