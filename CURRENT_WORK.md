# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active/recovery packet and the exact safe resume point. Public Git contains no private household financial values, provider identifiers, email contents, or live spreadsheet IDs.

## Active packet

### `M2-M1-014` — Financial Escape rolling-baseline + dynamic-pace refinement

- **Primary features:** `FIN-HISTORY-001`, `FIN-TRAJECTORY-001`, `FIN-DASH-001`, `FIN-SCENARIO-001`, `FIN-PRIVATE-REF-001`.
- **Repository:** `Matthew-Beare/Mira-2.0`.
- **Branch:** `work/m2-m1-014-financial-escape-refinement`.
- **Base SHA:** `f05d59d5e3204717d319059df1a4f764332b96d5`.
- **Objective:** refine the already-live private Financial Escape projection so the primary ordinary-spend baseline uses a rolling evidence-backed year rather than a short three-month window; make remaining paid-mile requirements for March/April/May/June respond to current debt/date/reserve/APR state; keep 14%/9%/6% retirement paths visually distinct; and use forwarded household-shopping mail only as classification evidence, never as a second financial transaction.

## Explicit customer reprioritization / displaced work

The customer explicitly continued Financial Escape refinement before returning to Android. `M2-M1-012` is therefore displaced, not abandoned.

### Preserved Android resume point

`M2-M1-012 — Android representative-device execution proof` remains blocked at the provider-configuration inspection gate. Do not patch OAuth/result handling or run another phone authorization attempt until a credible authenticated Google Cloud/provider inspection capability can read the existing Android OAuth client and Picker API state. When that signal exists, perform exactly one bounded provider inspection, compare registered package/signing SHA-1 with the already-earned proof artifact, read Picker API enabled state, make only the one already-authorized Picker enablement if inspection proves it disabled, read back provider state, then run one phone retest. Recovery branch remains `work/m2-m1-012-provider-tooling-hold-2`.

## Acceptance criteria

1. Rolling ordinary-spend calibration spans the latest 12 completed calendar months when provider coverage supports it.
2. Normalization excludes confirmed internal transfers, card repayments, education, evidenced repair/tire/tool projects, and extra debt prepayments; ambiguous mixed-retailer purchases remain ordinary until receipt/order/user evidence resolves them.
3. Required HELOC and Honda payments are carried once in all-in spending and separately treated as debt reduction; no double counting.
4. The rolling-year primary is robust against one extreme month and remains auditable with arithmetic-mean and median references.
5. March/April/May/June remaining paid-mile requirements use latest posted debt, current snapshot date, reserve/commitment gap, APR assumptions, normalized spending, and remaining time, not baseline debt.
6. Strong workweeks are visible immediately as a mileage leading signal; authoritative remaining-mile requirements fall when payroll/debt reduction posts and rise when reduction lags or time passes.
7. Dashboard stays phone-first with executive information above analyst detail.
8. Relevant charts use a consistent scenario convention: actual/provider path visually distinct; 14% current path black, 9% scenario yellow, 6% match-floor red. No scenario line is added where the rate has no causal meaning.
9. Connected forwarded shopping email may improve purchase classification across retailers; email evidence must correlate to the underlying financial transaction and never create duplicate spend.
10. AM/PM brief behavior preserves the rolling-year model and dynamic target-mile semantics without overwriting user controls.
11. Private provider data remains outside public Git.
12. Packet closeout must record exact live readback evidence and the exact Android resume point.

## Completed evidence so far

- Private Financial Escape Sheet remains live and provider-readable.
- Connected financial transaction coverage reports full history for the requested rolling-year analysis; freshness remains unknown and is treated honestly.
- A rolling 12-completed-month normalization table was added privately with a robust 10% winsorized primary plus arithmetic-mean and median references.
- Historical bank-labeled MTG movement was reconciled as HELOC behavior rather than a second mortgage before the primary baseline was accepted; current HELOC/Honda obligations are carried forward once.
- Dashboard/readback now uses the rolling-year primary forecast.
- Dashboard and Trends scenario charts were updated to the consistent actual/14%/9%/6% visual convention.
- A rolling-year spend-vs-baseline Trends chart exists.
- Dashboard has explicit remaining paid miles/week rows for March 1, April 1, May 1, and June 1, including 14%/9%/6% variants, and readback confirms formulas resolve from latest snapshot state.
- Previous temporary Pig-Phet anecdotal cash-position reconciliation was removed from the live model; only provider-backed/user-confirmed commitments remain planning inputs.
- AM and PM brief definitions were updated to preserve the rolling-year normalization and forwarded-shopping-evidence rules.

## Dependencies / blockers

- HELOC and Honda APRs remain user estimates until lender/provider evidence verifies them, so interest-sensitive output must retain estimated/provisional labeling.
- Forwarded shared-shopping mail has not yet been observed in the connected inbox; classification enrichment begins only after real forwarded evidence arrives.
- First post-change scheduled AM run still must earn live scheduler/readback verification; configuration readback is not equivalent to scheduler execution.

## Exact next action / resume point

1. Verify the latest Dashboard target-mile rows and rolling-year primary after the next provider-backed debt/payment refresh.
2. When forwarded shared-shopping mail first arrives, correlate a bounded sample against existing bank/card transactions and verify that classification changes do not duplicate spend.
3. Verify the next actual 2:45 AM run creates/updates the correct daily snapshot and preserves rolling-year/dynamic-mile semantics.
4. Close `M2-M1-014` only after those live readbacks or explicitly checkpoint any remaining future-evidence gap.
5. Return active work to `M2-M1-012` at the preserved provider-inspection gate.
