# MIRA 2.0 CURRENT WORK

Git is authoritative. This branch records exactly one active packet.

## Active packet

### `M2-M1-045` — Canonical finance live reconciliation continuation

- **Primary work:** `FIN-CANON-AUDIT-001`.
- **Follow-on work, only where prerequisite-safe:** `FIN-EVIDENCE-RECONCILE-001`.
- **Repository:** `Matthew-Beare/Mira-2.0`.
- **Branch:** `work/m2-m1-045-finance-live-reconciliation`.
- **Base SHA:** `c77378bc4c6043b5ab351199f141e92250f484ec`.
- **Packet:** `docs/work-packets/M2-M1-045.md`.

## Predecessor closure

`M2-M1-044` / PR #161 is merged at exact `main` SHA `c77378bc4c6043b5ab351199f141e92250f484ec`. Remote `main` points to that SHA and all four visible post-merge checks completed successfully. The deterministic reconciliation/pre-reply gate is integration-verified at the repository CI ceiling; live provider behavior still requires domain evidence.

## Customer outcome

Financial Escape and recurring MIRA briefs must use live provider/Workspace evidence, preserve one canonical finance/evidence/entity model, and stop exposing misleading or noisy operational detail. Current customer rules include:

- elapsed-month spend pacing (~25/50/75/100% by week unless a canonical control explicitly differs), distinguishing ahead-of-pace from over-full-month-budget;
- executive-glance brief formatting with clear breaks/bullets and no routine no-change finance line;
- no tracking/order numbers in ordinary briefs; use specific part/item when known, otherwise generic item + vendor only when useful;
- live mutable-state authority for shipment/finance/current-state claims, with verification ceilings stated rather than inferred;
- receipt/order/refund evidence relates to canonical economic events and durable assets without duplicating spend or inventory.

## Collision review

Open draft PR #135 / `M2-M1-020` owns reusable Google Sheets control-surface implementation and older governance-file edits. This packet does not duplicate or rewrite its renderer/control-surface code. Governance overlap must be reconciled before merge.

Open draft PR #160 is Studio/local-worker work and does not displace this finance blocker without explicit reprioritization.

## Live evidence earned in this packet

- Financial Escape workbook and its relational FinOps tabs were reached directly and read before mutation.
- Connected finance transaction coverage reports full history available, but provider freshness remains **UNKNOWN**. All money-state claims must stay at that verification ceiling.
- Spend Control status formulas were repaired to use elapsed-month pacing while preserving the full monthly budget as the hard cap. Exact readback confirmed the new formulas and effective status values.
- Dashboard spending summaries were repaired to show posted MTD / selected monthly budget / percent used / paced status, eliminating the misleading `projected` wording and remaining-balance-as-spend display. Exact readback passed.
- A stale Schema & Query Guide reference to an old snapshot row was repaired so true free cash resolves from the latest dated Daily Snapshot. The reserve-policy text was corrected to the configured separate septic reserve. Exact readback passed.
- Current finance invariant formulas read back clean for duplicate event IDs, duplicate evidence IDs, duplicate entity IDs, duplicate relation IDs, broken relation endpoints, the SKF net gate, active ChatGPT subscription count, and duplicate allowance debit keys.
- Recent Gmail/order evidence was reconciled against provider activity. One Friday fast-food receipt remains evidence-only because no posted matching transaction is currently visible; it is not admitted as posted spend.
- One previously identified durable automotive purchase with complete order/shipment evidence was backfilled through the Purchase & Receipt Archive: receipt detail, stable canonical asset identity, explicit `owned_by` relation, and two retained Gmail evidence rows. Exact readback passed. Vehicle assignment, installation, and current carrier state remain unverified and were deliberately not inferred.

No private balances, provider identifiers, order/tracking numbers, addresses, or receipt contents are stored in public Git.

## Acceptance state

1. Close predecessor `M2-M1-044` with post-merge exact-SHA checks. **PASS.**
2. Read live Financial Escape authorities and provider coverage/freshness before mutation. **PASS.**
3. Correct/read back spend pacing semantics in the private live projection. **PASS.**
4. Enforce compact brief presentation rules in the available operational rendering/control path. **PARTIAL — Dashboard projection repaired; recurring brief renderer/config still needs durable integration verification.**
5. Reconcile newly available financial/order/receipt evidence with stable identity and no duplicate economic events. **IN PROGRESS — current recent evidence reviewed; one unmatched receipt remains evidence-only.**
6. Link supported durable acquisitions into canonical receipt/asset state with exact readback; ambiguity remains reviewable. **IN PROGRESS — one complete durable chain backfilled and verified; continue bounded backlog.**
7. Use `M2-M1-044` reconciliation/pre-reply gate semantics where integration surfaces permit; unsupported strong claims fail closed. **IN PROGRESS.**
8. Public Git contains sanitized evidence only. **PASS so far.**

## Exact next action / resume point

1. Reconcile the latest provider transaction slice against canonical FinOps Ledger stable Event IDs and prove no duplicate economic effects.
2. Verify Spending Review / override inputs still bind to the same Event IDs after ordering/refresh; do not disturb user-owned inputs.
3. Process only genuinely new or still-incomplete receipt/order/refund evidence. Keep unmatched evidence out of posted spend and continue durable-asset commits only when identity/evidence is sufficient.
4. Locate the recurring AM/PM brief rendering/config path and durably encode the compact presentation rules without colliding with draft PR #135.
5. Re-run live invariant readbacks, then checkpoint and open/refresh the packet PR only after sanitized evidence is complete.

## Evidence ceiling

Repository evidence proves `M2-M1-044` landed cleanly and post-merge CI is green. Live Workspace writes described above were directly read back. Connected-finance history is available but source freshness remains UNKNOWN. Carrier state was not live-verified during this packet, so no current shipment ETA/progress claim is accepted from email alone.
