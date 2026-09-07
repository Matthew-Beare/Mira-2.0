# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active/recovery packet and the exact safe resume point. Detailed prior evidence remains preserved in Git history.

## Active packet

### `M2-M1-013` — Financial Escape live command-center vertical

- **Primary work:** `FIN-DASHBOARD-001`, `FIN-SNAPSHOT-001`, `FIN-TRAJECTORY-ENGINE-001`.
- **Primary features:** `FIN-GOAL-001`, `FIN-HISTORY-001`, `FIN-TRAJECTORY-001`, `FIN-DASH-001`, `FIN-SCENARIO-001`, `FIN-COUNTDOWN-001`, `FIN-PRIVATE-REF-001`.
- **Related existing features/invariants:** `FIN-001`, `SPEND-001`, `PAYMENT-001`, `SUB-001`, `MILE-001`, `MILE-002`, `OPS-001`, `DATA-001`, `DEV-007`.
- **Repository:** `Matthew-Beare/Mira-2.0`.
- **Branch:** `work/m2-m1-013-financial-escape-live`.
- **Branch base before active reconciliation:** `c6633202934386d6d6f84daa6ce510912724ae30`.
- **Priority:** explicit customer override; highest current user-visible vertical.
- **Private-state rule:** public Git contains only sanitized contracts, schemas, tests and synthetic examples. Live balances, transactions, account/provider identifiers, household names and other private financial state remain outside the public repository.

## Objective

Deliver the user's private Financial Escape Command Center as a functioning live MIRA vertical: connected evidence feeds a single primary native Google Sheets projection, the top of the dashboard gives a fast red/yellow/green escape view, daily dated observations preserve history/provenance, and the canonical 2:45 AM America/New_York MIRA brief receives a compact verified Financial Escape summary.

The private reference profile is the acceptance reference. Generic/public abstraction may support other users' configurable goals later, but must not weaken the user's private behavior.

## Explicit reprioritization / displaced packet checkpoint

The customer explicitly interrupted the prior Android packet and directed MIRA to implement Financial Escape now. `M2-M1-012` is therefore displaced, not completed.

### Preserved `M2-M1-012` resume point

- Prior packet: `M2-M1-012 — Android representative-device execution proof`.
- Prior primary work: `ANDROID-CLIENT-CORE-001` / `CLIENT-ANDROID-001` / `API-001`.
- Stable merged hold checkpoint: main commit `6e715159feed0b044e3ef3ef610916903e2deb09` (`Merge M2-M1-012 provider tooling hold checkpoint`).
- Exact blocker: Google provider-configuration inspection is still required, while two bounded Work-browser attempts failed before provider state could be inspected. Those failures are tooling evidence only.
- Earned device evidence remains: stable APK install/launch, native Google account chooser opening, and correct-account selection.
- Unearned evidence remains: successful consent/authorization, existing Android OAuth client exact package/SHA-1 readback, Picker API state, canonical live read/mutation/cross-readback.
- **Exact resume action:** only after a credible provider-access recovery signal, inspect the existing development Android OAuth client package/SHA-1 and Picker API state with exact readback; make no other provider change; only then run one bounded phone test. Do not rerun the phone test or burn speculative Work attempts before that signal.

Detailed M2-M1-012 evidence remains in Git history and its prior CURRENT_WORK checkpoint.

## M2-M1-013 bounded first-slice acceptance

1. Forward trajectory starts at the activation baseline; historical driving/pay/spend calibrates realism but does not retroactively mark the household behind.
2. Executive dashboard is broad-first and at-a-glance: R/Y/G status, weeks remaining, signed whole Days Ahead/Behind, Dollars Ahead/Behind, debt, forecast, cash safety, mileage pace and required correction before granular detail.
3. Cash model separates total cash, protected operating reserve, extreme-emergency reserve, project reserves, committed spending and true free cash. Protected cash is not debt-attack cash by default.
4. Debt APRs are editable assumptions with effective-date/provenance semantics and all APR-sensitive projections update from them; missing APR is visibly provisional rather than silently treated as exact.
5. Historical observations are dated and preserve source/freshness/confidence. Unchanged or stale source data must not be fabricated into daily principal movement.
6. Productive-work mileage uses one paid-truck-mile stream and excludes PTO/nonproductive weeks from productive mileage averages; actual payroll remains actual cash-flow evidence.
7. Scenario layer supports reserve catch-up, spending cuts, career-transition offers and a bounded match-preserving 401(k) lever. A blank match input must never mean "cut the full contribution."
8. Anomaly/intervention logic identifies review candidates without declaring mixed-purpose category spend automatically discretionary, and translates a real gap into a monthly cut and/or paid-mile correction.
9. One primary private native Google Sheet is the human-readable projection; connected private evidence/MIRROR semantics remain authoritative.
10. The existing canonical 2:45 AM brief refreshes the private snapshot, verifies readback, and emits a compact Financial Escape block without dumping forensic detail.
11. Public Git contains no private financial values, live spreadsheet/account/provider identifiers, credentials or personal operational data.
12. `M2-M1-012` remains recoverable at the exact provider-inspection gate above.

## Evidence earned in current packet

- A private native Google Sheets command-center workbook has been created with Dashboard, Daily Snapshots, Trucking & Payroll, Cash & Commitments, Contributions, Scenarios, Assumptions, Provenance, and Anomaly/Cuts surfaces.
- The live workbook has provider-readback-verified formulas for the forward baseline, protected/committed/free cash separation, productive mileage windows, household net-per-paid-mile calibration, target pace, reserve catch-up correction, scenarios and the disabled-until-configured retirement lever.
- User-confirmed current paid-trip evidence has been reconciled into the existing Mileage & Pay authority with readback.
- A persistent manual recurring-education commitment is represented in private financial state so it survives provider gaps.
- The existing enabled 2:45 AM America/New_York MIRA brief has been updated in place, not duplicated, with a Financial Escape refresh/snapshot/readback/output contract.
- No private financial values or provider identifiers have been added to this public source file.

These are implementation/live-integration evidence for the private first slice. They do **not** yet earn full feature completion: the APR inputs remain user-supplied, daily scheduler firing with a newly created historical snapshot has not yet occurred, forecast-movement history needs more than the baseline observation, and canonical FEATURES/BACKLOG reconciliation is still required before packet closeout.

## Current blockers / required user input

- **HELOC APR:** user input still required for interest-accurate forecast.
- **Honda APR:** user input still required for interest-accurate forecast.
- **Match-preserving weekly 401(k) employee contribution:** user input required before the retirement-reduction scenario can activate.

These missing inputs do not block the live command center or daily snapshot. They lower forecast confidence and keep APR/401(k)-dependent outputs explicitly provisional/disabled.

## Exact next action / resume point

1. Reconcile the reserved Financial Escape feature IDs into canonical `FEATURES.md` and work IDs into `BACKLOG.md` under `DEV-007`, with this packet ranked as the active customer-priority vertical.
2. Remove the accidental branch-recovery note-file clutter from the work branch while preserving the actual sanitized `M2-M1-013.md` packet contract.
3. Complete and verify the workbook presentation/readback gate: supporting-tab visual consistency, key number formats/input affordances, chart metadata, and a final formula-error scan.
4. Verify the existing 2:45 AM automation still has the exact America/New_York schedule and the Financial Escape refresh block after update.
5. At the next actual 2:45 AM run, verify a new/current dated snapshot, provider/Sheet readback, and the compact Financial Escape brief output. This is the first scheduler-fire evidence; do not claim it before it happens.
6. When the user supplies APRs and the match-preserving contribution, enter them in the private Assumptions surface and verify downstream recalculation/readback.
7. Before closeout, repeat FEATURES/BACKLOG/CURRENT_WORK reconciliation, distinguish implemented vs scheduler/live-verified evidence, and retain any remaining countdown/history/anomaly hardening as bounded follow-on work.

## Recovery protocol

Resume from `work/m2-m1-013-financial-escape-live`. Verify this CURRENT_WORK file first. Do not reconstruct private financial values from public Git. The private live command center and connected financial providers are operational evidence sources, not public source-tree state. `M2-M1-012` remains deliberately displaced at its provider-inspection gate and must not be resumed unless the customer reprioritizes it or this packet closes and dependency ranking selects it next.