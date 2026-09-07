# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active/recovery packet and the exact safe resume point.

## Active packet

### `M2-M1-018` — Finance truth reconciliation and monthly budget control

- **Repository:** `Matthew-Beare/Mira-2.0`.
- **Branch:** `work/m2-m1-018-finance-truth-command-center`.
- **Base / completed predecessor checkpoint:** `244f78c53cb6365dd12050ea9b39e73d47e86af4` (`M2-M1-017`).
- **Packet:** `docs/work-packets/M2-M1-018.md`.
- **Primary work:** full-history household income reconciliation, private finance truth audit, spouse-retirement mirror assumption, final WGU-term funding plan, person-routed allowances, monthly frozen-budget variance/carry semantics and live net-worth/dashboard control state.

## Why work switched

The customer explicitly requested a complete financial-context audit after the protected vehicle migration and wants the command center to stop behaving like a pile of semi-independent spreadsheets. This packet stabilizes the canonical financial state and month-to-month control semantics before a separate presentation packet reduces visible tab clutter.

## Completed predecessor evidence

`M2-M1-017` is complete at bounded private-live migration/readback evidence. Three protected household vehicle ASSET identities preserve legacy UUID continuity in the current MIRROR projection; ownership and one-per-vehicle registration plans resolve cleanly; ambiguous historical renewal-to-vehicle mappings remain unknown; protected source and backup parity were verified; duplicate entity/relation and broken-endpoint diagnostics are zero.

## Current customer corrections to apply

- Use the newer shared Budget and Income source as the active household-budget source. Retire the older household budget from active views/forecasting but do not delete its evidence/history.
- Model exactly one remaining Pig Phet WGU term, with a customer-confirmed six-month horizon from September 1, 2026. Planning due date is March 1, 2027 unless stronger evidence contradicts it.
- The spouse 401(k) cannot currently be linked. For private planning, customer explicitly instructs MIRA to mirror the linked primary-user 401(k) balance exactly until direct spouse-provider evidence becomes available. This is a user-confirmed assumption, never provider-observed truth.
- Allowances are exactly two balances, Matthew and Pig Phet. Only spending assigned to the corresponding person may debit that person's balance; unassigned allowance spend fails closed.
- Main dashboard should expose live net worth and monthly budget surplus/deficit state. Under-budget surplus or over-budget deficit must be carried into the next month through an explicit annotated adjustment, not by rewriting the prior month's frozen budget.
- Full-history household income should use all relevant connected history, with transfers/refunds excluded only after broad inflow retrieval and reconciliation.

## Exact next action / resume point

1. Re-read linked account coverage and retrieve broad full-history posted inflows from every relevant income-receiving/depository account with transfers included in retrieval.
2. Reconcile transfers/refunds/credits/ambiguous inflows and compute explicit full-history household income coverage dates, monthly average and annualized baseline while keeping recent productive-work pace separate.
3. Reconcile current linked cash/liabilities/investments/retirement against private workbook assumptions.
4. Write the spouse-retirement mirror assumption, old-budget retirement/supersession state, final WGU term horizon/funding logic and allowance-person routing into canonical private MIRROR records/views.
5. Implement immutable monthly budget baseline + actual + close variance + annotated next-month carry/trim state.
6. Surface provider-only and assumption-adjusted planning net worth plus current-month budget state on the main Dashboard.
7. Verify formula/readback integrity and exact graph diagnostics.

## Explicitly deferred presentation packet

Once financial truth is stable, open a separate bounded workbook-presentation packet to reduce human-facing tabs, hide/archive redundant projections, convert walls of text to compact tables/headings, and keep canonical raw/evidence tables intact. Do not delete tabs before dependency/reference audit.

## Displaced Android checkpoint

`M2-M1-012` Android representative-device proof remains preserved at `9841928dfce72f516a2bfb243035e7c8f2002692`, with its provider-inspection runbook and hold rules unchanged. No Android provider/app/phone work belongs in `M2-M1-018` unless separately reprioritized.

## Protected constraints

- One logical MIRROR authority; no second finance or budget database.
- Provider observations and user assumptions remain visibly distinct.
- Protected legacy evidence is retired/superseded rather than destructively deleted.
- Existing migrated vehicle UUID continuity and rollback evidence remain untouched.
- Full-history income retrieval must follow broad-inflow-first reconciliation; transfers are retrieval candidates, not income by default.
- Private financial values and identifiers remain out of public Git.
- Unknown evidence stays unknown rather than guessed.
