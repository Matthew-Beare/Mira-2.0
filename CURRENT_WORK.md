# MIRA 2.0 CURRENT WORK

Git is authoritative. This branch records exactly one active packet. Multiple other packet branches may be active repository-wide under `docs/CONCURRENT_WORK_POLICY.md`.

## Active packet

### `M2-M1-039` — Financial Escape twice-daily refresh reliability repair

- **Primary work:** restore trustworthy twice-daily Financial Escape refresh/readback for the 02:45 and 14:45 America/New_York brief cycle.
- **Repository:** `Matthew-Beare/Mira-2.0`.
- **Branch:** `work/m2-m1-039-financial-escape-refresh-repair`.
- **Base SHA:** `57f9cfab2976be1d93ccae41d07b497354511552`.
- **Packet:** `docs/work-packets/M2-M1-039.md`.
- **Displaced work:** `M2-M1-038` / `STUDIO-INTAKE-001`, checkpointed on its branch at commit `3f8d52b2904891b5b9677ec26d64978afb4e4afa`; no implementation had begun. Resume from its existing first implementation step after this packet closes.
- **Current status:** LIVE REPAIR VERIFIED on 2026-09-11. Workbook readback is current and fail-closed audit gates pass. A dedicated pre-brief Financial Escape refresh now runs at 02:35 and 14:35 America/New_York ahead of the existing 02:45/14:45 briefs. Documentation closeout/merge remains.
- **Owned live surfaces:** Financial Escape dashboard freshness/audit cells, twice-daily Financial Escape refresh verification behavior, and bounded refresh/readback evidence.
- **Out of scope:** changing debt strategy assumptions without evidence, rewriting historical production evidence without an explicit correction record, or expanding unrelated MIRA features.

## Failure evidence captured 2026-09-11

- Enabled AM brief schedule: 02:45 America/New_York daily; scheduler invocation alone had occurred without a successful finance refresh.
- Enabled PM brief schedule: 14:45 America/New_York daily.
- Financial Escape `Today & Accounts` was still as-of 2026-09-07.
- Latest `Daily Snapshots` row was still 2026-09-07.
- Last `FIN-LIVE-VERIFY-001 COMPLETE` provenance evidence was 2026-09-07.
- Current linked-account evidence materially differed from the stale workbook.
- Inserting a new snapshot row exposed a structural bug: ordinary row references followed the old current snapshot to row 5, so current-model formulas could silently continue using stale data.

## Repair implemented and read back

- `Today & Accounts` now reads 2026-09-11 and explicitly preserves provider transaction freshness as UNKNOWN.
- `Daily Snapshots` row 4 is the current 2026-09-11 snapshot; there is exactly one 2026-09-11 row. Missing Sep 8–10 daily snapshots were not fabricated.
- Current live readback: HELOC $42,471.61; Honda $43,005.77; total payoff debt $85,477.38; depository cash $25,671.75; positive card balances $455.21.
- Current linked assets used by the declared verified-net-worth formula: retirement $249,903.44; taxable brokerage $16,850.65; crypto $148.13. Verified net worth reads $206,641.38.
- Historical Sep 7 snapshot evidence was restored/frozen rather than silently rewritten when the retirement-methodology inconsistency was discovered. Current verified-net-worth history now starts a clean methodology baseline instead of reporting the resulting accounting discontinuity as investment gain.
- Posted Sep 8–10 provider transactions were upserted into the canonical FinOps Ledger by stable transaction/Event ID, including the user-authoritative correction that bank label `MTG` is HELOC cash movement, not a mortgage. Duplicate Event IDs read back as 0.
- Completed workweek mileage ending 2026-09-10 was reconciled to 5,582 paid miles. Current 8-worked-week pace reads 5,796 mi/week.
- Snapshot-dependent formulas in Dashboard, Assumptions, Forecast Charts, Details, Scenarios and Spend Control were hardened so insertion of a new current row does not silently retarget current-model formulas to the prior snapshot.
- Remaining-time model math was corrected to use the current snapshot date rather than repeatedly granting the original baseline duration. Current model fallback reads escape-ready 2027-03-28, May 1 minimum 5,123 paid mi/week, 8W buffer +674 mi/week, and `AHEAD • -5w`.
- Dashboard now shows a visible `DATA FRESHNESS` gate and `UPDATE AUDIT` block. Readback on 2026-09-11: live view 2026-09-11; latest snapshot 2026-09-11; snapshot age 0 days; last live verification 2026-09-11; duplicate Event IDs 0; today's snapshot rows 1; freshness `CURRENT`.
- `FIN-LIVE-VERIFY-002 COMPLETE`, methodology-correction, reliability-repair and historical-gap provenance rows were written and read back.
- Dedicated pre-brief Financial Escape refresh schedule is enabled for 02:35 and 14:35 America/New_York. It must refresh, upsert, snapshot, read back and append durable verification evidence; silent success is allowed only after all gates pass, while failure must notify `ACTION REQUIRED` with the exact failed gate.

## Acceptance criteria

1. Dashboard visibly shows current-vs-stale state without relying on chat claims. **PASS.**
2. Dashboard exposes last live-view date, latest daily snapshot date, last successful verification, expected twice-daily cadence, and a fail-closed status. **PASS.**
3. Current snapshot contract is exactly one America/New_York row 4 for today; next-day refresh must freeze the outgoing row before inserting the new current row. **PASS for current-date live state; durable pre-brief contract installed.**
4. Scheduler invocation alone is never treated as success; success requires workbook readback. **PASS.**
5. Live provider/account evidence is reconciled before projections are described as current; source freshness=unknown remains explicitly unknown. **PASS.**
6. Historical evidence is not silently rewritten; corrections use explicit provenance. **PASS.**
7. Linked retirement value is treated consistently with the declared verified-net-worth formula; methodology correction is explicit. **PASS.**
8. Failed refresh is required to surface stale/action-required rather than repeat stale finance values as current. **PASS by fail-closed dashboard + refresh contract.**
9. Exact live workbook readback demonstrates repaired current-date state. **PASS.**
10. After closeout, resume `M2-M1-038` at its preserved first implementation step. **PENDING packet merge/closeout only.**

## Exact next action / resume point

1. Commit this exact live evidence closeout documentation.
2. Run normal repository/PR closeout gates for this docs-only packet and merge if green.
3. Verify exact post-merge CI; do not overclaim future provider success beyond the fail-closed contract.
4. Resume `M2-M1-038` from checkpoint commit `3f8d52b2904891b5b9677ec26d64978afb4e4afa` and its first implementation step.

## Evidence ceiling

M2-M1-039 proves the 2026-09-11 live repair, current-date workbook readback, fail-closed freshness/audit gates, insertion-safe current-snapshot references, corrected remaining-time calculations and installation of the dedicated pre-brief refresh contract. It does not prove that every future external provider call will succeed; future success remains gated by live readback rather than scheduler invocation.

## Recovery protocol

Resume from branch `work/m2-m1-039-financial-escape-refresh-repair`, base `57f9cfab2976be1d93ccae41d07b497354511552`, this file and `docs/work-packets/M2-M1-039.md`. `M2-M1-038` is preserved separately and must not be reconstructed from chat.
