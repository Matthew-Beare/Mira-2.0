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

`M2-M1-044` / PR #161 is merged at exact `main` SHA `c77378bc4c6043b5ab351199f141e92250f484ec`. GitHub reports PR #161 merged, remote `main` points to that SHA, and all four post-merge checks visible on that exact SHA completed successfully (`python` x2 and `preflight` x2). The deterministic reconciliation/pre-reply gate is therefore integration-verified at the repository CI ceiling; live Gmail/bank/card/carrier/shared-trip/scheduler behavior remains domain work, exactly as the packet stated.

## Customer outcome

Financial Escape and recurring MIRA briefs must use live provider/Workspace evidence, preserve one canonical finance/evidence/entity model, and stop exposing misleading or noisy operational detail. Current customer rules to enforce include:

- elapsed-month spend pacing (~25/50/75/100% by week unless a canonical control explicitly differs), distinguishing ahead-of-pace from over-full-month-budget;
- executive-glance brief formatting with clear breaks/bullets and no routine no-change finance line;
- no tracking/order numbers in ordinary briefs; use specific part/item when known, otherwise generic item + vendor only when useful;
- live mutable-state authority for shipment/finance/current-state claims, with verification ceilings stated rather than inferred;
- receipt/order/refund evidence relates to canonical economic events and durable assets without duplicating spend or inventory.

## Collision review

Open draft PR #135 / `M2-M1-020` owns reusable Google Sheets control-surface implementation and older `BACKLOG.md` / `FEATURES.md` / `CURRENT_WORK.md` edits. This packet does not duplicate or modify its Sheets renderer/control-surface code. Governance overlap is handled by rebasing/reconciling before either packet can merge.

Open draft PR #160 is Studio/local-worker work and is not the selected customer-priority path after `M2-M1-044`; it must not displace this finance blocker without explicit reprioritization.

## Acceptance state

1. Close predecessor `M2-M1-044` with post-merge exact-SHA checks. **PASS.**
2. Read live Financial Escape authorities and provider coverage/freshness before mutation. **PENDING.**
3. Correct/read back spend pacing semantics in the private live projection. **PENDING.**
4. Enforce compact brief presentation rules in the available operational rendering/control path. **PENDING.**
5. Reconcile newly available financial/order/receipt evidence with stable identity and no duplicate economic events. **PENDING.**
6. Link supported durable acquisitions into canonical receipt/asset state with exact readback; ambiguity remains reviewable. **PENDING.**
7. Use `M2-M1-044` reconciliation/pre-reply gate semantics where integration surfaces permit; unsupported strong claims fail closed. **PENDING.**
8. Public Git contains sanitized evidence only. **PASS so far.**

## Exact next action / resume point

1. Discover/read the live Financial Escape workbook and related private canonical surfaces.
2. Read current connected-finance account coverage/freshness before drawing money-state conclusions.
3. Inspect and repair spend-control pacing and brief-rendering control semantics, then read them back.
4. Reconcile new order/receipt/refund evidence only through canonical identities and verify mutations exactly.
5. Checkpoint sanitized evidence, unresolved review items, provider ceilings and the next exact resume point here before stopping.

## Evidence ceiling

Repository evidence proves `M2-M1-044` landed cleanly and post-merge CI is green. This packet has not yet claimed any live private finance, Gmail, carrier, mileage-sheet or receipt/archive mutation. Those claims require direct provider/workbook evidence and exact readback during this packet.
