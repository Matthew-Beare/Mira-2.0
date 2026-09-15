# MIRA 2.0 — Current Work

## Customer status
Objective: Close historical finance reconciliation before moving to the Android inventory/scanning vertical.
Progress: Expanded provider verification with exact stable-account exports: six active/legacy card/checking lanes now have deterministic row-count/date-boundary evidence, including legacy FNBO history reaching 2024-08-05; canonical stable-ID equality remains the closure gate.
Last 24h: Historical provider rows were reconciled into the canonical ledger with provenance preserved, including pre-2026 savings history and deterministic non-spend handling for transfers/income.
Deliverable: Durable finance-coverage proof with exact provider/canonical identity coverage per connected transaction account, followed by Android camera/QR/barcode inventory capture using the existing asset/location graph.
Expected delivery: UNKNOWN.
Blocker: none.

## Recovery authority
This file is the authoritative execution checkpoint. Chat context is disposable. Re-read repository instructions, remote `main`, open PRs and CI before selecting work.

## Current objective
`FIN-CANON-AUDIT-001` historical coverage closure. Do not use 2026-09-01 as a historical exclusion boundary. Preserve provider evidence and provenance; represent actual unavailable gaps explicitly.

### Verified live state — 2026-09-15
- Remote `main` independently verified before this checkpoint; existing historical-reconciliation framework is merged. Do not repeat merged framework work.
- Finances reports transaction dataset `full_history`, `ready`, and complete for the bounded queries used here; freshness remains unknown.
- Stable connected transaction-account identities were enumerated before querying history.
- Exact stable-account exports performed this run (posted only, transfers included) produced internally verified unique-ID sets with zero within-export duplicate IDs:
  - Prime Visa: 221 rows for 2026-01-01..2026-09-15; returned boundary 2026-01-01..2026-09-15.
  - Joint Checking: 191 rows; returned boundary 2026-01-05..2026-09-15.
  - Quicksilver: 345 rows; returned boundary 2026-01-01..2026-09-15.
  - Rewards Signature 9854: 85 rows; returned boundary 2026-01-03..2026-09-11.
  - Savor: 231 rows; returned boundary 2026-01-02..2026-09-14.
  - Legacy Rewards Signature 5868: 117 rows for 2024-08-01..2026-09-15; returned boundary 2024-08-05..2025-08-02. This currently-zero account contains historical evidence and must not be dropped.
- Earlier provider aggregate proof also established historical savings boundaries and exact canonical FinOps Ledger readback for the provider-earliest savings rows. Savings lanes must not be re-imported merely because this checkpoint expands the card/checking proof.
- Differences between prior aggregate counts/boundaries and these exact stable-account exports mean prior aggregate evidence is not sufficient for closure. Use the exact stable-account exports as the reconciliation input and stable transaction-ID equality as authority.
- Canonical FinOps Ledger contains at least 3,000 data rows. Do not infer complete identity coverage from row count, merchant/date/amount, or previous aggregate projections.
- Existing `docs/FINANCE_EVIDENCE_COVERAGE_PROOF.md` must not claim closure until stable-ID reconciliation is complete.

## Exact resume point
1. Reconcile the exact provider stable transaction-ID sets above against canonical `FinOps Ledger` IDs for Prime Visa, Joint Checking, Quicksilver, Rewards Signature 9854, Savor, and legacy Rewards Signature 5868.
2. Prefer batched/export-capable canonical reads; if connector response-size limits prevent whole-set comparison, chunk deterministically by date while preserving stable-ID equality.
3. Any provider ID absent from canonical must be imported with original evidence/provenance, then read back exactly. Never delete or overwrite older production rows.
4. Verify canonical duplicate count for provider transaction IDs is zero.
5. Update `docs/FINANCE_EVIDENCE_COVERAGE_PROOF.md` with durable per-account boundaries and explicit unavailable/no-row states only after exact equality proof.
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
