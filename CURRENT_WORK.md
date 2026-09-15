# MIRA 2.0 — Current Work

## Customer status
Objective: Close historical finance reconciliation before moving to the Android inventory/scanning vertical.
Progress: Re-verified connected provider history against the canonical FinOps Ledger; stable transaction IDs and exact readback show the previously identified pre-projection history is already present for the bounded historical savings lanes, so the remaining gap is now narrowed to account-by-account earliest-date proof rather than missing canonical rows.
Last 24h: Historical provider rows were reconciled into the canonical ledger with provenance preserved, including pre-2026 savings history and deterministic non-spend handling for transfers/income.
Deliverable: Durable finance-coverage proof with exact earliest provider/canonical dates per connected transaction account, followed by Android camera/QR/barcode inventory capture using the existing asset/location graph.
Expected delivery: UNKNOWN.
Blocker: none.

## Recovery authority
This file is the authoritative execution checkpoint. Chat context is disposable. Re-read repository instructions, remote `main`, open PRs and CI before selecting work.

## Current objective
`FIN-CANON-AUDIT-001` historical coverage closure. Do not use 2026-09-01 as a historical exclusion boundary. Preserve provider evidence and provenance; represent actual unavailable gaps explicitly.

### Verified live state — 2026-09-15
- Remote `main` independently verified at `d6b7327abed3ca49b47e8cd53bd03b958d257195` before this checkpoint.
- One open PR exists (#166); it is unrelated to finance-history closure and remains open. Do not merge or duplicate it as part of this packet.
- Recent `main` CI was inspected before selecting work.
- Finances reports transaction dataset `full_history`, `ready`, and complete for the bounded queries used here; freshness remains unknown.
- Stable connected transaction-account identities were enumerated before querying history.
- Provider aggregate readback from 2024-08-09 forward produced these earliest dates/counts for the currently relevant transaction accounts:
  - Prime Visa / CREDIT CARD: earliest 2026-01-02, 179 rows.
  - Joint Checking: earliest 2026-01-02, 209 rows.
  - Quicksilver: earliest 2026-05-12, 244 rows.
  - Rewards Signature 9854: earliest 2026-01-05, 69 rows.
  - Rewards Signature 5868: no posted rows in the bounded query.
  - Savor: earliest 2026-05-15, 63 rows.
  - Home Savings: earliest 2024-08-17, 61 rows.
  - Joint Savings: earliest 2024-08-30, 24 rows.
  - Matthew's Primary Savings: earliest 2024-08-09, 60 rows.
- Exact canonical FinOps Ledger readback shows the same stable transaction IDs for the historical savings lanes, including:
  - Matthew's Primary Savings row on 2024-08-09.
  - Home Savings row on 2024-08-17.
  - Joint Savings row on 2024-08-30.
- The canonical ledger therefore demonstrably contains provider-backed pre-2026 history; do not repeat the already-completed historical savings import.
- Existing `docs/FINANCE_EVIDENCE_COVERAGE_PROOF.md` is now stale where it says older provider history remains wholly outside the canonical projection. Update that proof only after finishing the account-by-account earliest-date reconciliation so the closure claim is exact.

## Exact resume point
1. Continue account-by-account provider-vs-canonical earliest-date/count reconciliation. The goal is to prove every currently connected transaction account is either represented from its provider-exposed earliest date or explicitly bounded by no provider rows/source unavailability.
2. Use stable provider transaction IDs for equality. Do not infer equality from merchant/date/amount when a provider ID exists.
3. Read back the canonical ledger after any mutation. Do not delete or overwrite older production rows.
4. When all connected transaction accounts are reconciled, update `docs/FINANCE_EVIDENCE_COVERAGE_PROOF.md` to replace the stale open-gap statement with the exact durable coverage boundary and remaining unavailable gaps, if any.
5. Then mark `FIN-CANON-AUDIT-001` closed in the appropriate control surface only after exact readback supports it.
6. Next priority after finance closure: Android inventory/scanning vertical. Reuse existing Android client plus `INV-001`, `INV-002`, `MOVE-001`, `IDENT-001`, `ASSET-001/002/003`; implement camera/QR/barcode capture into canonical asset identity and location/movement with exact readback. Do not create a parallel inventory model.

## Acceptance gates for finance closure
- Provider coverage status recorded.
- Every connected transaction account has an explicit provider earliest date or explicit no-row/unavailable state.
- Canonical ledger contains every provider transaction in the covered interval exactly once by stable transaction ID, or any exception is durably enumerated.
- Transfers/income/refunds remain economic-state preserving and are not silently converted into spend.
- Historical provenance is preserved.
- Exact post-write/readback shows no duplicate canonical transaction IDs introduced.
- Coverage proof and CURRENT_WORK agree with live state.

## Constraints
- Do not manufacture a historical start date for convenience.
- Do not claim provider freshness beyond what Finances reports.
- Do not expose private account IDs, transaction IDs, amounts, addresses, receipt contents or provider secrets in public proof docs.
- Routine worker runs remain silent to the user; checkpoint progress here.
