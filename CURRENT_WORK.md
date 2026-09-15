# MIRA 2.0 — Current Work

## Customer status
Objective: Close historical finance reconciliation before moving to the Android inventory/scanning vertical.
Progress: Provider earliest-date/count proof is now complete for every currently connected transaction account; canonical exact-ID proof is confirmed for the three pre-2026 savings lanes, and the remaining work is exact-ID reconciliation for the 2026 lanes plus the documented no-row account.
Last 24h: Historical provider rows were reconciled into the canonical ledger with provenance preserved, including pre-2026 savings history and deterministic non-spend handling for transfers/income.
Deliverable: Durable finance-coverage proof with exact provider/canonical identity coverage per connected transaction account, followed by Android camera/QR/barcode inventory capture using the existing asset/location graph.
Expected delivery: UNKNOWN.
Blocker: none.

## Recovery authority
This file is the authoritative execution checkpoint. Chat context is disposable. Re-read repository instructions, remote `main`, open PRs and CI before selecting work.

## Current objective
`FIN-CANON-AUDIT-001` historical coverage closure. Do not use 2026-09-01 as a historical exclusion boundary. Preserve provider evidence and provenance; represent actual unavailable gaps explicitly.

### Verified live state — 2026-09-15
- Remote `main` independently verified before this checkpoint; one unrelated open PR (#166) remains open and must not be merged or duplicated as part of finance-history closure.
- Finances reports transaction dataset `full_history`, `ready`, and complete for the bounded queries used here; freshness remains unknown.
- Stable connected transaction-account identities were enumerated before querying history.
- Provider aggregate readback from 2024-08-09 forward now covers every currently connected transaction account:
  - Prime Visa / CREDIT CARD: earliest 2026-01-02, 179 rows.
  - Joint Checking: earliest 2026-01-02, 209 rows.
  - Quicksilver: earliest 2026-05-12, 244 rows.
  - Rewards Signature 9854: earliest 2026-01-05, 69 rows.
  - Rewards Signature 5868: no posted rows in the bounded query.
  - Savor: earliest 2026-05-15, 63 rows.
  - Home Savings: earliest 2024-08-17, 61 rows.
  - Joint Savings: earliest 2024-08-30, 24 rows.
  - Matthew's Primary Savings: earliest 2024-08-09, 60 rows.
- Exact canonical FinOps Ledger readback shows the same stable transaction IDs for the historical savings lanes, including the provider-earliest rows for Matthew's Primary Savings (2024-08-09), Home Savings (2024-08-17), and Joint Savings (2024-08-30).
- Canonical FinOps Ledger currently contains 3,000 data rows. Do not infer complete identity coverage for the 2026 lanes from row count or merchant/date/amount; finish stable-ID equality reconciliation.
- Existing `docs/FINANCE_EVIDENCE_COVERAGE_PROOF.md` is stale where it says older provider history remains wholly outside the canonical projection. Do not update it to a closure claim until stable-ID reconciliation is complete.

## Exact resume point
1. Reconcile provider stable transaction IDs against canonical `FinOps Ledger` IDs for Prime Visa, Joint Checking, Quicksilver, Rewards Signature 9854, Savor, and the explicit no-row Rewards Signature 5868 state. Savings lanes are already exact-ID proven at their historical boundary and must not be re-imported.
2. Prefer batched/export-capable provider/canonical reads if available; if connector response-size limits prevent whole-account set comparison, chunk deterministically by date while preserving stable-ID equality.
3. Any provider ID absent from canonical must be imported with original evidence/provenance, then read back exactly. Never delete or overwrite older production rows.
4. After equality reconciliation, verify canonical duplicate count for provider transaction IDs is zero.
5. Update `docs/FINANCE_EVIDENCE_COVERAGE_PROOF.md` with the exact durable coverage boundary and explicit unavailable/no-row states.
6. Mark `FIN-CANON-AUDIT-001` closed only after exact readback supports it.
7. Next priority: Android inventory/scanning vertical using the existing Android client plus `INV-001`, `INV-002`, `MOVE-001`, `IDENT-001`, `ASSET-001/002/003`; implement camera/QR/barcode capture into canonical asset identity and location/movement with exact readback. Do not create a parallel inventory model.

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
