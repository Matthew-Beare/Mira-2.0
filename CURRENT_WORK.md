# MIRA 2.0 — Current Work

## Customer status
Objective: Close historical finance reconciliation before moving to the Android inventory/scanning vertical.
Progress: Fresh full-history provider aggregation corrected stale 2026 account counts and proved zero provider-side duplicate transaction IDs in every nonempty unresolved lane; exact canonical ID equality remains the closure gate.
Last 24h: Historical provider rows were reconciled into the canonical ledger with provenance preserved, including pre-2026 savings history and deterministic non-spend handling for transfers/income.
Deliverable: Durable finance-coverage proof with exact provider/canonical identity coverage per connected transaction account, followed by Android camera/QR/barcode inventory capture using the existing asset/location graph.
Expected delivery: UNKNOWN.
Blocker: none.

## Recovery authority
This file is the authoritative execution checkpoint. Chat context is disposable. Re-read repository instructions, remote `main`, open PRs and CI before selecting work.

## Current objective
`FIN-CANON-AUDIT-001` historical coverage closure. Do not use 2026-09-01 as a historical exclusion boundary. Preserve provider evidence and provenance; represent actual unavailable gaps explicitly.

### Verified live state — 2026-09-15
- Remote `main` and open PR state were independently re-read before this checkpoint. PR #166 remains open on a finance-reconciliation branch; do not duplicate or merge it blindly. Reconcile its intent against current main before any integration.
- Finances reports transaction dataset `full_history`, `ready`, and complete for the bounded queries used here; freshness remains unknown.
- Stable connected transaction-account identities were re-enumerated before querying history.
- Fresh provider aggregation for the unresolved 2026 lanes, bounded 2026-01-01 through 2026-09-15, with transfers included and pending excluded:
  - Prime Visa / CREDIT CARD: 174 rows, 174 distinct transaction IDs, earliest 2026-01-02, latest 2026-09-11.
  - Joint Checking: 233 rows, 233 distinct transaction IDs, earliest 2026-01-02, latest 2026-09-09.
  - Quicksilver: 295 rows, 295 distinct transaction IDs, earliest 2026-05-12, latest 2026-09-11.
  - Rewards Signature 9854: 58 rows, 58 distinct transaction IDs, earliest 2026-01-05, latest 2026-09-10.
  - Savor: 67 rows, 67 distinct transaction IDs, earliest 2026-05-15, latest 2026-09-11.
  - Rewards Signature 5868: no posted rows in the bounded query.
- These fresh counts supersede the stale aggregate counts previously recorded here. Provider-side duplicate count is therefore zero for every nonempty unresolved lane in this bound (`row_count == count_distinct(transaction_id)`). This does NOT prove canonical equality.
- Earlier exact canonical FinOps Ledger readback proved stable transaction-ID presence for the historical savings lanes, including provider-earliest rows for Matthew's Primary Savings (2024-08-09), Home Savings (2024-08-17), and Joint Savings (2024-08-30). Do not re-import them.
- Canonical FinOps Ledger previously contained 3,000 data rows. Do not infer complete identity coverage for the 2026 lanes from row count or merchant/date/amount; finish stable-ID equality reconciliation.
- Existing `docs/FINANCE_EVIDENCE_COVERAGE_PROOF.md` remains stale where it says older provider history remains wholly outside the canonical projection. Do not update it to a closure claim until stable-ID reconciliation is complete.

## Exact resume point
1. Read exact provider transaction IDs for Prime Visa, Joint Checking, Quicksilver, Rewards Signature 9854, and Savor using deterministic date chunks if necessary; preserve the explicit no-row Rewards Signature 5868 state.
2. Compare those stable IDs against canonical `FinOps Ledger` IDs. Prefer batched/export-capable canonical reads. If response-size limits prevent whole-account comparison, chunk deterministically by date.
3. Any provider ID absent from canonical must be imported with original evidence/provenance, then read back exactly. Never delete or overwrite older production rows.
4. Verify canonical duplicate count for provider transaction IDs is zero. Provider-side uniqueness is already proven for the unresolved lanes in the current bound.
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
