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
- **Current status:** active live-state repair. The scheduler is firing, but the Financial Escape workbook has stale live-view/snapshot state; user requested repair before Studio work resumes.
- **Owned live surfaces:** Financial Escape dashboard freshness/audit cells, twice-daily Financial Escape refresh verification behavior, and bounded refresh/readback evidence.
- **Out of scope:** changing debt strategy assumptions without evidence, rewriting historical production evidence without an explicit correction record, or expanding unrelated MIRA features.

## Failure evidence captured 2026-09-11

- Enabled AM brief schedule: 02:45 America/New_York daily; last scheduler invocation was 2026-09-11.
- Enabled PM brief schedule: 14:45 America/New_York daily.
- Financial Escape `Today & Accounts` was still as-of 2026-09-07.
- Latest `Daily Snapshots` row was still 2026-09-07.
- Last `FIN-LIVE-VERIFY-001 COMPLETE` provenance evidence was 2026-09-07.
- Therefore scheduler invocation did not prove successful Financial Escape refresh/readback.
- Dashboard now contains a visible fail-closed freshness indicator and an UPDATE AUDIT block; stale live/snapshot dates render red.
- Current linked-account evidence already differs materially from the stale workbook, including HELOC and cash/card balances, so stale finance output cannot be presented as current.

## Objective

Make Financial Escape self-auditing and operationally trustworthy: every twice-daily cycle must either (a) refresh authoritative sources, update the workbook, read back the expected current-date state, and record durable success evidence, or (b) surface an explicit stale/action-required state and avoid presenting stale finance values as current.

## Acceptance criteria

1. Dashboard visibly shows current-vs-stale state without relying on chat claims.
2. Dashboard exposes last live-view date, latest daily snapshot date, last successful verification, expected twice-daily cadence, and a fail-closed status.
3. AM owns insert-or-update of exactly one snapshot row for the America/New_York date; PM may update the same row but never create a duplicate.
4. A scheduler invocation alone is never treated as success; success requires workbook readback for the intended date.
5. Live provider/account evidence is reconciled before debt/cash/net-worth projections are described as current; source freshness=unknown remains explicitly unknown.
6. Historical evidence is not silently rewritten. Corrections use explicit provenance.
7. Linked retirement value is treated consistently with the canonical verified-net-worth formula when that formula says it is included; any methodology correction is recorded rather than hidden.
8. If the current-date refresh cannot be verified, the user-facing brief must say Financial Escape is stale/action-required rather than repeat stale status as if current.
9. Exact live workbook readback demonstrates the repaired current-date state before this packet closes.
10. After closeout, resume `M2-M1-038` at its preserved first implementation step.

## Exact next action / resume point

1. Refresh current Financial Escape source evidence and reconcile current balances/activity into the live workbook.
2. Repair today/snapshot/provenance state without duplicating transactions or snapshots.
3. Add or harden durable per-run success evidence so AM/PM readback is independently auditable.
4. Verify the dashboard turns CURRENT only when both live-view and snapshot dates are current.
5. Record exact readback evidence here and close the packet only after current-date verification.
6. Resume `M2-M1-038` from commit `3f8d52b2904891b5b9677ec26d64978afb4e4afa` and its first implementation step.

## Evidence ceiling

This packet may claim only the live Financial Escape repair actually read back from the workbook and connected sources. It does not claim that every future provider call will succeed, and it does not treat task scheduler execution as financial refresh proof.

## Recovery protocol

Resume from branch `work/m2-m1-039-financial-escape-refresh-repair`, base `57f9cfab2976be1d93ccae41d07b497354511552`, this file and `docs/work-packets/M2-M1-039.md`. `M2-M1-038` is preserved separately and must not be reconstructed from chat.
