# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and its exact resume point.

## Completed packet

### `M2-G0-002B` — Feature Audit Slice A2 — generalized context/travel foundations

- **Merged PR:** #2
- **Merge SHA:** `4fb45c2cd9e77476294e89eae7857e7dad07b49a`
- **Audited features:** `CTX-001`, `CTX-002`, `TRIP-001`, `ROUTE-001`, `WEATHER-001`
- **Changed files:** `FEATURES.md`, `BACKLOG.md`, `CURRENT_WORK.md`
- **Result:** generalized context selection/recommendation, independent trip lifecycle, learned route/ETA state, and context-gated weather foundations are durably recorded with requirement/evidence separation.
- **Live Google production touched:** no.
- **Executable product behavior changed:** no.

## Active packet

- **Packet ID:** `M2-G0-002C`
- **Name:** Feature Audit Slice A3 — mileage/tasks/recovery foundations
- **Class:** forensic audit / prerequisite
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `audit/g0-002c-mileage-tasks-recovery`
- **Base audit-state SHA:** `4fb45c2cd9e77476294e89eae7857e7dad07b49a`
- **Objective:** Reconstruct the next bounded set of historical MIRA mileage/pay, task structure, completion-evidence, and recovery/run-log capabilities as stable semantic feature records without implementing product behavior.

## Audit rows in this packet

Audit exactly legacy category-A behaviors 11-15:

1. Company-paid mileage and estimated gross pay; both Thursday briefs.
2. Separate accessible Miles & Pay tracker.
3. Task hierarchy High/Medium/Low → classification → subsystem → one task per bullet.
4. Next-action coaching and honest completion evidence.
5. Phase-aware Run Log, last-good checkpoint, resumable recovery, circuit breaker.

Do not expand this packet to optional-module failure isolation, calendar/mail, or later audit categories merely because evidence is nearby.

## Acceptance criteria

1. Each of the five scoped behaviors receives a stable MIRA 2.0 semantic feature ID.
2. Each feature receives a complete user-facing description and rationale.
3. Requirement status is separated from implementation/test/integration/live evidence.
4. Known hard dependencies and downstream enables are recorded.
5. Relevant legacy source/test/evidence paths are recorded without copying private production data.
6. Materially relevant PR #31/branch evidence is reconciled as candidate evidence rather than blindly promoted.
7. Mileage occurrence state, tracker authority, task taxonomy, completion evidence, and run/recovery state remain separate where their authorities or verification boundaries differ.
8. `FEATURES.md` and `BACKLOG.md` are updated and committed on the packet branch.
9. A small PR is opened, scope-verified, merged, and remotely read back before the packet is called complete.
10. `CURRENT_WORK.md` advances to the next exact unaudited behavior before ending the packet.
11. No live Google production state and no executable product behavior is changed.

## Exact next action

Create/confirm branch `audit/g0-002c-mileage-tasks-recovery` from the current MIRA 2.0 main checkpoint. Read legacy category-A evidence for behavior 11: **Company-paid mileage and estimated gross pay; both Thursday briefs**. Inspect deterministic mileage/pay policy and tests, assign its stable MIRA 2.0 feature ID, and draft the audited record before moving to behavior 12.

## Next packet boundary

If `M2-G0-002C` completes, `M2-G0-002D` begins with category-A behavior 16: **Optional module failure isolation** and final Slice-A consistency/dependency reconciliation.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head when tools permit;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture new customer ideas in BACKLOG unless required for acceptance or explicitly reprioritized;
6. before the final packet line, state any customer action needed; if none is needed, use `Just tell me to continue.`;
7. the final visible line remains the packet recovery tag.
