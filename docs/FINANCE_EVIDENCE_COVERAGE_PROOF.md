# Finance evidence coverage proof

Date: 2026-09-13

Packet: `M2-M1-046`

This document records sanitized verification for the bounded evidence-coverage closure of `FIN-CANON-AUDIT-001`. It intentionally excludes private financial values, account/provider identifiers, transaction/order/tracking identifiers, addresses, receipt/email contents and provider secrets.

## Provider ceiling

Connected financial transaction history was read before reconciliation. The provider reports full-history availability and complete coverage for the bounded queries used here, while freshness remains **UNKNOWN**. Provider-observed transactions therefore remain money authority, but this proof does not claim current-to-the-second completeness.

## Evidence lanes reached

The live reconciliation directly reached:

- the historical mailbox evidence archive already indexed into Financial Escape;
- connected current Gmail for post-archive incremental evidence; and
- the current Purchase & Receipt Archive, including its order/detail/audit/classification surfaces.

These sources explain meaning and provenance. None of them independently proves that money posted.

## Canonical evidence coverage

Exact live readback after reconciliation showed:

- 914 indexed evidence rows;
- 914 unique source dedup keys;
- zero duplicate source dedup keys;
- zero rows without a deterministic audit disposition;
- 161 unmatched amount-evidence rows;
- 57 unmatched order-evidence rows;
- 55 explicit non-economic commerce hints;
- 58 shipping/delivery support rows;
- 572 unresolved-review rows; and
- six current evidence rows explicitly retained as supported meaning/evidence state.

These are evidence-state counts. They are not purchase counts or spend totals.

## False-positive cleanup

A bounded review found marketing mail incorrectly promoted to purchase, return or shipping evidence because promotional copy contained commerce keywords or amount-like text. Clearly promotional rows in the reviewed slice were reclassified to non-economic commerce hints while preserving source identity, raw provenance and replay keys.

A zero-cash-credit order was also corrected so it cannot masquerade as unmatched cash spend.

This repair narrows the review queue without deleting evidence or inventing a purchase.

## Current connected-mail reconciliation

Two current receipt cases exercise the intended boundary:

1. One receipt matched an existing posted provider event. It was linked as supporting evidence to that existing canonical event and did not create another economic event.
2. A later receipt had no matching posted provider transaction in the refreshed bounded slice. It remains unmatched evidence only and does not change posted spend.

This proves both the positive-link and fail-closed no-money-authority paths using live provider/mail evidence.

## Graph and replay integrity

After the bounded mutations, exact readback confirmed:

- duplicate canonical economic-event IDs: 0;
- duplicate evidence IDs: 0;
- duplicate entity IDs: 0;
- duplicate relation IDs: 0;
- broken relation endpoints: 0;
- canonical entity count: 3,023; and
- canonical relation count: 3,668.

The canonical ledger remained at 886 economic-event rows. New evidence therefore enriched existing state without silently manufacturing spend.

## Remaining blocker

`FIN-CANON-AUDIT-001` is not yet fully closable. The connected provider exposes history predating the lower bound of the current canonical finance projection, and that older history remains explicitly marked `OPEN HISTORICAL BACKFILL` in the live control surface.

The next bounded packet must either reconcile that older provider history through stable provider identity or establish an explicit durable product boundary that intentionally excludes it. Until then, MIRA must not claim full historical finance projection coverage.

## Result

**PASS for current indexed evidence coverage and deterministic exception disposition. BLOCKED for overall canonical-finance audit closure by the explicit pre-projection historical-coverage gap.**
