# MIRA 2.0 CURRENT WORK

Git is authoritative. This branch records exactly one active packet.

## Active packet

### `M2-M1-045` — Canonical finance live reconciliation continuation

- **Primary work:** `FIN-CANON-AUDIT-001`.
- **Primary features:** `FIN-001`, `OPS-004`.
- **Related invariants/features:** `RECOVERY-001`, `RECOVERY-002`, `MAIL-001`, `ORDER-001`, `ORDER-002`, `ORDER-005`, `MILE-001`, `MILE-002`, `TASK-002`.
- **Follow-on work, only where prerequisite-safe:** `FIN-EVIDENCE-RECONCILE-001`.
- **Bounded presentation dependency:** `OPS-BRIEF-VSLICE`.
- **Repository:** `Matthew-Beare/Mira-2.0`.
- **Branch:** `work/m2-m1-045-finance-live-reconciliation`.
- **Base SHA:** `c77378bc4c6043b5ab351199f141e92250f484ec`.
- **PR:** `#162`.
- **Packet:** `docs/work-packets/M2-M1-045.md`.

## Predecessor closure

`M2-M1-044` / PR #161 is merged at exact `main` SHA `c77378bc4c6043b5ab351199f141e92250f484ec`. Remote `main` points to that SHA and all four visible post-merge checks completed successfully. Its deterministic reconciliation/pre-reply gate is integration-verified at the repository CI ceiling; live provider truth still requires domain evidence.

## Customer outcome

Financial Escape and recurring MIRA briefs must use live provider/Workspace evidence, preserve one canonical finance/evidence/entity model, and stop exposing misleading or noisy operational detail. Current customer rules include:

- elapsed-month spend pacing (~25/50/75/100% by week unless a canonical control explicitly differs), distinguishing ahead-of-pace from over-full-month-budget;
- executive-glance brief formatting with clear breaks/bullets and no routine no-change finance line;
- no tracking/order numbers in ordinary briefs; specific item/part only when known, otherwise generic item + vendor when useful;
- live mutable-state authority for shipment/finance/current-state claims, with verification ceilings stated rather than inferred;
- receipt/order/refund evidence relates to canonical economic events and durable assets without duplicating spend or inventory.

## Collision review

- Draft PR #135 / `M2-M1-020` owns reusable Google Sheets control-surface implementation and older governance-file edits. This packet does not modify its Sheets renderer/control-surface code. Governance overlap must be reconciled before merge.
- Draft PR #160 is Studio/local-worker work and does not displace this finance blocker without explicit reprioritization.
- The bounded `OPS-BRIEF-VSLICE` change touches only generic empty/no-change presentation behavior plus its test/contract; it adds no new provider source or scheduler authority.

## Live evidence earned in this packet

- Financial Escape workbook and relational FinOps tabs were reached directly and read before mutation.
- Connected finance transaction coverage reports full history available, but provider freshness remains **UNKNOWN**. Money-state claims stay at that ceiling.
- Spend Control status formulas now use elapsed-month pacing while preserving the full monthly budget as hard cap; exact readback passed.
- Dashboard spending summaries now show posted MTD / selected budget / percent used / paced status instead of misleading projection/remaining-budget wording; exact readback passed.
- A stale true-free-cash snapshot reference and stale reserve-policy text were repaired against the current canonical policy; exact readback passed.
- The current recent provider slice was reconciled by stable provider transaction identity. Every returned posted transaction resolves to exactly one FinOps Ledger event after an accidental duplicate insertion was detected, rolled back, and re-read.
- Spending Review user inputs remain keyed to stable Event IDs. A projection defect was found where three user review notes were sitting in the vendor-override field, causing the effective vendor to become note text instead of the user-confirmed normalized fuel vendor. Those notes were moved to the dedicated Notes column, vendor overrides cleared, effective vendor re-resolved to `Gas`, headers restored, and canonical Review Notes formulas repaired to bind by stable Event ID. Exact readback passed.
- Current finance invariants read clean: duplicate event/evidence/entity/relation IDs = 0, broken relation endpoints = 0, required SKF net gate = 0, active ChatGPT subscriptions = 2, duplicate allowance debit keys = 0. Vendor overrides = 0 and user review notes = 3 after the projection repair.
- Recent Gmail/order evidence was reconciled against provider activity. One fast-food receipt remains evidence-only because no posted matching transaction is visible; it is not admitted as posted spend.
- Existing Subaru purchase/shipment evidence is linked back to its canonical posted economic event and read back without creating another event.
- One previously identified durable automotive purchase with complete order/shipment evidence was backfilled through the Purchase & Receipt Archive: receipt detail, stable canonical asset identity, explicit `owned_by` relation, and retained evidence rows. Vehicle assignment, installation, and current carrier state remain unverified and were deliberately not inferred.
- Current generic Ops Brief rendering now omits an empty `Tasks / No active tasks` section. `docs/OPS_BRIEF_PRESENTATION_CONTRACT.md` records compact executive-glance, no tracking/order-number, live-authority, spend-pacing, chart-density and module-isolation rules without adding new source integrations.

No private balances, provider identifiers, order/tracking numbers, addresses, receipt contents, or provider secrets are stored in public Git.

## Repository verification

- Draft PR #162 opened from this branch to `main` so repository CI can exercise the bounded code change.
- CI run #653 reached compile, feature registry, product lifecycle ledger and Personal starter distribution successfully, then failed at `Work-session alignment` because this branch's earlier CURRENT_WORK checkpoint omitted the gate-required `Primary features`, `Related invariants/features`, and session-start alignment sections.
- That is a governance/checkpoint defect, not an Ops Brief unit-test result; downstream code ownership/unit tests were skipped by the failed gate.
- This CURRENT_WORK update restores those required authoritative fields/sections. Exact-head CI must be rerun and pass before merge.

## Acceptance state

1. Close predecessor `M2-M1-044` with post-merge exact-SHA checks. **PASS.**
2. Read live Financial Escape authorities and provider coverage/freshness before mutation. **PASS.**
3. Correct/read back spend pacing semantics without changing provider money authority. **PASS.**
4. Enforce compact brief presentation rules in the available operational rendering/control path. **PASS at current surface ceiling — Dashboard + generic Ops Brief renderer + durable presentation contract; unavailable shipment-source code is not fabricated.**
5. Reconcile current financial/order/receipt evidence with stable identity and no duplicate economic effects. **PASS for current slice — all returned recent posted provider transactions resolve once; unmatched receipt remains evidence-only.**
6. Link supported durable acquisitions into canonical receipt/asset state with exact readback; ambiguous items remain reviewable. **PASS for current bounded evidence — one full durable chain committed; generic/ambiguous items were not forced into inventory.**
7. Use `M2-M1-044` reconciliation/pre-reply semantics where integration surfaces permit; unsupported strong claims fail closed. **PASS at current provider ceiling.**
8. Public Git contains sanitized evidence only. **PASS.**
9. Exact-head repository CI and merge/post-merge verification. **PENDING.**

## Session-start alignment verification — 2026-09-13

### `FEATURES.md`

The packet advances existing finance (`FIN-001`), operational brief/run integrity (`OPS-004`, `RECOVERY-001`, `RECOVERY-002`) and existing mail/order/mileage/task semantics. It does not create a second finance model, shipment authority, or provider stack. The bounded Ops Brief presentation change only removes empty/no-change noise and records the approved presentation contract.

### `BACKLOG.md`

`FIN-CANON-AUDIT-001` is the existing canonical-finance blocker and remains the primary work. `FIN-EVIDENCE-RECONCILE-001` is consumed only where its prerequisites are already satisfied. No duplicate finance or receipt/inventory work ID is created.

### `ROADMAP.md`

Direction remains ordinary-language MIRA backed by canonical state, provider-specific authority, exact readback, evidence provenance, failure isolation and no fabricated live claims. Current work improves the recurring user-facing finance/brief path without changing Standard/Advanced provider semantics.

### Idea/backlog capture audit

CAPTURE AUDIT COMPLETE

- Spend pacing and compact-brief presentation requirements are durably represented in the live projection and/or Git contract.
- The discovered review-note/vendor-override corruption was repaired in the existing canonical projection rather than creating another spending database.
- Unmatched receipts, ambiguous durable goods and unverified carrier state remain explicit review/verification states.
- No unrelated feature is admitted.

### Direction result

ALIGNED

## Exact next action / resume point

1. Require PR #162 CI green on the exact head created by this CURRENT_WORK correction.
2. If CI fails, fix only the failing gate/test and rerun; do not expand scope.
3. Re-read PR #162 changed files, mergeability and remote `main`; reconcile any governance overlap from draft PR #135 before merge if Git reports a real conflict.
4. Mark PR #162 ready and merge only with expected-head protection after exact-head CI is green.
5. Read back exact post-merge `main` and require push CI on that exact merge SHA before calling `M2-M1-045` integration verified.
6. After closure, re-read Git authorities and rank the next existing packet rather than inventing parallel work.

## Evidence ceiling

Live Workspace writes above were directly read back. Connected-finance history is available but provider freshness remains UNKNOWN. Carrier state was not live-verified during this packet, so no current shipment ETA/progress claim is accepted from email alone. Repository CI has not yet passed on the current closeout head.
