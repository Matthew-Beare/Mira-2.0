# MIRA 2.0 CURRENT WORK

Git is authoritative for recovery, but mutable finance truth must be re-read from the connected provider and canonical FinOps sheet before work selection.

## Current objective

Continue `FIN-CANON-AUDIT-001`: prove and close the remaining historical provider-to-canonical finance identity gap without artificial start dates, lost evidence, duplicate economic effects, or fabricated classifications.

## Reconciled state — 2026-09-15

- Live Finances reports transaction coverage `full_history`; freshness remains `unknown`.
- A fresh bounded read of the currently linked Prime Visa account returned 398 posted transactions, with provider dates spanning 2026-01-02 through 2026-09-13. Ascending and descending reads returned the same 398 stable transaction identities with complete overlap, so that is the current provider-exposed bound for this linked account in this run.
- This directly contradicts the older checkpoint count of Prime Visa = 675. The older count is retained as historical evidence, not discarded, but it must not be used as the current replay bound. The discrepancy itself is now a coverage condition that must be explained or durably bounded before historical finance can be called closed.
- Joint Checking was previously proven complete at 669/669 provider identities; re-read before any new write that depends on that mutable claim.
- Current canonical `FinOps Ledger.Transaction ID` readback includes Prime Visa identities from 2024 and 2025 as well as current data. Therefore the provider's present 2026-only exposure must not be interpreted as proof that older canonical history is invalid or should be removed.
- Historical source data remains authoritative evidence. No existing production data is to be deleted or overwritten merely to simplify reconciliation.

## Customer priority / sequencing

1. Compare the current 398-ID Prime Visa provider set against canonical `FinOps Ledger.Transaction ID` and project only identities proven absent.
2. Preserve and investigate the 675-versus-398 provider-bound discrepancy. Treat the older 2024/2025 canonical rows as preserved historical evidence; never delete them because the live connector currently exposes a shorter window.
3. If the current 398 identities are all represented, document the older-source gap as provider-unavailable unless another trustworthy connected source exposes it; if another source is available, reconcile it by stable identity and provenance.
4. Correlate ambiguous marketplace/card merchants against available order, receipt, and mail evidence before asking the user; never infer item identity from merchant name alone.
5. Preserve transfer/payment/refund semantics and signed economic-spend rules. Keep unresolved purpose/necessity/funding context reviewable rather than guessed.
6. After identity closure, synchronize Spending Review and run full graph-integrity/readback gates.
7. After historical finance coverage is closed or durably bounded by actual source unavailability, move to the Android inventory/scanning vertical using the existing INV-001, INV-002, MOVE-001, IDENT-001, ASSET-001/002/003 and Android architecture.

## Acceptance gates

1. Actual connected historical range inventoried per relevant source, including explicit provider-window contractions.
2. Provider stable transaction identities compared against canonical MIRROR finance identities using only complete bounded provider reads.
3. Every supported missing provider event projected exactly once; no already-canonical provider identity is replayed.
4. Ambiguous semantic classification remains reviewable rather than fabricated.
5. Exact readback proves duplicate Event IDs, Evidence IDs, Entity IDs, Relation IDs and broken relation endpoints are all zero.
6. Provider identity set is fully represented or explicitly accounted for by documented source unavailability/exclusion.
7. Historical date storage/presentation remains deterministic.
8. Public Git contains only sanitized coverage/proof, never private balances, account/provider IDs, transaction IDs, receipt contents, addresses, or secrets.
9. Repository CI passes at the exact completion head and again after merge before the objective is called complete.

## Resume point

Use the fresh current provider bound of 398 Prime Visa identities, not the stale 675 count and not a date heuristic. Compute an exact set difference against the canonical Transaction-ID column and append only proven-absent identities. Preserve the prior 675-count checkpoint as evidence of a historical provider-window contraction. If the 398 current identities are all canonical, the remaining task is to determine whether any trustworthy connected source still exposes the older provider history; otherwise record that inaccessible span explicitly rather than manufacturing a start date.

## Canonical six-line status

Objective: Reconcile every accessible historical provider transaction into canonical MIRROR exactly once.
Progress: Re-read the live card source and proved its current complete bound is 398 posted identities covering 2026-01-02 through 2026-09-13; the older 675-count checkpoint is stale and preserved as evidence of provider-window contraction.
Last 24h: Joint Checking provider identity coverage was completed at 669/669 with synchronized ledger/review surfaces and zero recorded provider-identity duplicates.
Deliverable: Exact current Prime Visa 398-ID provider-to-MIRROR set-difference proof plus a durable accounting of the older-source coverage gap.
Expected delivery: UNKNOWN.
Blocker: none; current provider identities can be reconciled while the older provider-window discrepancy is bounded from available evidence.
