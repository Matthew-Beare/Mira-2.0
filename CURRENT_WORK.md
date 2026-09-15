# MIRA 2.0 CURRENT WORK

Git is authoritative for recovery, but mutable finance truth must be re-read from the connected provider and canonical FinOps sheet before work selection.

## Current objective

Continue `FIN-CANON-AUDIT-001`: prove and close the remaining historical provider-to-canonical finance identity gap without artificial start dates, lost evidence, duplicate economic effects, or fabricated classifications.

## Reconciled state — 2026-09-15

- Live Finances reports transaction coverage `full_history`; freshness remains `unknown`.
- Prior checkpoint recorded complete bounded source counts of Prime Visa = 675 and Joint Checking = 669 transactions.
- Prior canonical readback recorded 1,835 ledger Event IDs and synchronized Spending Review Event IDs with zero duplicate ledger Event IDs, zero duplicate provider Transaction IDs, zero duplicate Spending Review Event IDs, and exact ledger/review Event-ID set equality.
- Joint Checking was previously proven complete at 669/669 provider identities.
- The prior claim that Prime Visa has exactly 256 missing canonical provider identities is **not currently safe to use as a projection queue without recomputing the exact set difference**. Fresh provider-to-canonical spot checks found canonical rows for Prime Visa identities at both 2024-08-09 and 2025-01-01, including their provider Transaction IDs and Event IDs. This does not prove the card is complete; it proves that age/date alone cannot identify the missing set and prevents a duplicate historical replay.
- Historical source data remains authoritative evidence. No existing production data is to be deleted or overwritten merely to simplify reconciliation.

## Customer priority / sequencing

1. Recompute the exact Prime Visa provider-ID set against canonical `FinOps Ledger.Transaction ID` from complete bounded provider reads and current canonical readback. Do not infer missing rows from dates or counts alone.
2. Project only identities proven absent from canonical state, preserving provider evidence and idempotent Event IDs.
3. Correlate ambiguous marketplace/card merchants against available order, receipt, and mail evidence before asking the user; never infer item identity from merchant name alone.
4. Preserve transfer/payment/refund semantics and signed economic-spend rules. Keep unresolved purpose/necessity/funding context reviewable rather than guessed.
5. After identity closure, synchronize Spending Review and run full graph-integrity/readback gates.
6. After historical finance coverage is closed or durably bounded by actual source unavailability, move to the Android inventory/scanning vertical using the existing INV-001, INV-002, MOVE-001, IDENT-001, ASSET-001/002/003 and Android architecture.

## Acceptance gates

1. Actual connected historical range inventoried per relevant source.
2. Provider stable transaction identities compared against canonical MIRROR finance identities using only complete bounded provider reads.
3. Every supported missing provider event projected exactly once; no already-canonical provider identity is replayed.
4. Ambiguous semantic classification remains reviewable rather than fabricated.
5. Exact readback proves duplicate Event IDs, Evidence IDs, Entity IDs, Relation IDs and broken relation endpoints are all zero.
6. Provider identity set is fully represented or explicitly accounted for by documented source unavailability/exclusion.
7. Historical date storage/presentation remains deterministic.
8. Public Git contains only sanitized coverage/proof, never private balances, account/provider IDs, transaction IDs, receipt contents, addresses, or secrets.
9. Repository CI passes at the exact completion head and again after merge before the objective is called complete.

## Resume point

Do **not** blindly append the previously recorded 256 Prime Visa rows. First obtain the current canonical Transaction-ID column and complete bounded Prime Visa provider IDs, compute an exact set difference, and use only that set as the replay queue. Two live spot checks from the historical card range are already canonical, so a date-based replay would risk duplicates. After each bounded append, synchronize Spending Review and require duplicate/set-equality readback.

## Canonical six-line status

Objective: Reconcile every accessible historical provider transaction into canonical MIRROR exactly once.
Progress: Revalidated the historical card path against live provider and canonical evidence; stopped an unsafe count/date-based replay because sampled 2024 and 2025 provider identities are already canonical.
Last 24h: Joint Checking provider identity coverage was completed at 669/669 with synchronized ledger/review surfaces and zero recorded provider-identity duplicates.
Deliverable: Exact Prime Visa provider-to-MIRROR set-difference proof followed by projection of only genuinely missing identities.
Expected delivery: UNKNOWN.
Blocker: none; exact Prime Visa set difference must be recomputed before any further historical card append.