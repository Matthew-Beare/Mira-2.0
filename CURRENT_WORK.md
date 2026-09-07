# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active/recovery packet and the exact safe resume point.

## Active packet

### `M2-M1-015` — Finance unification, registration reconciliation, and allowance debit

- **Repository:** `Matthew-Beare/Mira-2.0`.
- **Branch:** `work/m2-m1-015-finance-unification-allowance-debit`.
- **Base SHA / displaced Android checkpoint:** `9841928dfce72f516a2bfb243035e7c8f2002692`.
- **Primary work IDs:** `FIN-EARMARK-001`, `FIN-SPEND-CLASSIFY-001`, `FIN-ALLOWANCE-DEBIT-001`, `FIN-BUDGET-RECON-001`.
- **Related invariants/features:** `MIRROR-001`, `AUTH-001`, `STORE-001`, `API-001`, `DEV-007`.
- **Packet:** `docs/work-packets/M2-M1-015.md`.

## Why work switched

The customer explicitly reprioritized finance/MIRROR work while Android is held at an external Google provider-inspection gate. The new packet corrects under-modelled vehicle-registration planning, removes a duplicated network reserve, activates allowance debiting as built-in canonical behaviour, audits full evidence/asset integration, and recomputes Financial Escape trajectory.

## Displaced packet checkpoint

`M2-M1-012` Android representative-device proof is preserved exactly at `9841928dfce72f516a2bfb243035e7c8f2002692`. The recovery branch `work/m2-m1-012-provider-tooling-hold-2` was verified at that same SHA before this switch. Its Google provider-inspection runbook and hold rules remain unchanged. No Android provider, app-side OAuth, or phone-test work belongs in `M2-M1-015`.

## Current private-live findings that drive this packet

- The household has three cars and therefore needs three vehicle-registration planning obligations in total. Historical County Clerk economic events are evidence, not duplicate planned spends.
- The prior checking earmark model incorrectly represented both a network reserve and a network-switch reserve. The customer clarified there is only one network-switch reserve; the duplicate must be removed from active earmark calculations.
- Allowance debiting is now explicitly authorized as built-in behaviour. It must be driven by canonical economic-event identity and effective allowance classification, be idempotent, and support reversible refund/reclassification reconciliation.
- Pig Phet/shared-budget evidence is already integrated through canonical entity/relation/subscription/plan records, but source-vs-current comparison should be made easier to read and must never become a second authority.
- Receipt/order/evidence infrastructure exists; this packet must audit whether photo, product, serial-number, warranty, and related asset evidence are fully joinable through MIRROR and capture any missing generalized work.

## Exact next action / resume point

1. Reconcile the private workbook to three total vehicle-registration plan items without inventing vehicle assignments, amounts, or dates that are not evidenced.
2. Remove the duplicate network reserve and verify derived earmark/free-cash calculations.
3. Implement canonical allowance debit/reversal state from FinOps Ledger economic events with deterministic idempotency.
4. Read back touched ranges and scan for spreadsheet errors.
5. Audit receipt/order/photo/product/serial/warranty integration coverage and create stable follow-on IDs only where real gaps exist.
6. Use current connected account/liability/recurring/income evidence plus the corrected private MIRROR planning state to recompute Financial Escape trajectory and report an estimated beginning/middle/end-of-month escape window with assumptions and uncertainty.

## Protected constraints

- One logical MIRROR authority; no separate finance, receipt, asset, or Pig Phet database.
- Provider-observed account balances are never mutated by spreadsheet earmarks or planning controls.
- Legacy MIRA production artifacts remain protected.
- Private financial values, account IDs, transaction IDs, receipts, household operational details, and credentials stay out of public Git.
- Unknown evidence stays unknown rather than being guessed.
