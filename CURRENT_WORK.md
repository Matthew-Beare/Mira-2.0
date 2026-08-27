# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and its exact resume point.

## Completed packet

### `M2-G0-002A` — Feature Audit Slice A1 — scheduler/context foundations

- **Merged PR:** #1
- **Merged audit state SHA:** `c33e89c52dc15d991348cefd2b3e0c51be15fd8e`
- **Audited features:** `OPS-001` through `OPS-005`
- **Changed files:** `FEATURES.md`, `BACKLOG.md`, `CURRENT_WORK.md`
- **Result:** canonical schedule, duplicate-schedule prohibition, runtime clock gate, deterministic Run ID/fresh delivery, and deterministic HOME/ROAD override foundations are durably recorded with requirement/evidence separation.
- **Live Google production touched:** no.
- **Executable product behavior changed:** no.

## Active packet

- **Packet ID:** `M2-G0-002B`
- **Name:** Feature Audit Slice A2 — generalized context/travel foundations
- **Class:** forensic audit / prerequisite
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `audit/g0-002b-context-travel`
- **Base audit-state SHA:** `c33e89c52dc15d991348cefd2b3e0c51be15fd8e`
- **Objective:** Reconstruct the next bounded set of historical MIRA context/travel/weather capabilities, assign stable semantic feature IDs, and document descriptions, dependencies, evidence levels, and compatibility notes without implementing product behavior.

## Audit rows in this packet

Audit exactly legacy category-A behaviors 6-10:

1. Generic context pairs: HOME/ROAD, HOME/TRUCK, HOME/FIELD, HOME/CAMPUS, HOME/OFFICE, HOME/AWAY, custom.
2. Job title/duties inform context recommendation but never silently enable it.
3. Active trip tracking separate from context and paid-work tracking.
4. Multi-leg routes, learned runtime, current location, ETA, ahead/behind inference.
5. ROAD severe-weather/route-condition watch; HOME local weather only.

Do not expand this packet to mileage, tasks, Run Log/recovery, or later category-A behaviors merely because related evidence is nearby.

## Acceptance criteria

1. Each of the five scoped behaviors receives a stable MIRA 2.0 semantic feature ID.
2. Each feature receives a complete user-facing description and rationale.
3. Requirement status is separated from implementation/test/integration/live evidence.
4. Known hard dependencies and downstream enables are recorded.
5. Relevant legacy source/test/evidence paths are recorded without copying private production data.
6. Materially relevant PR #31/branch evidence is reconciled as candidate evidence rather than blindly promoted.
7. Context recommendation, active-trip state, route/runtime inference, and weather gating remain separate capabilities where their dependencies differ.
8. `FEATURES.md` and `BACKLOG.md` are updated and committed on the packet branch.
9. A small PR is opened, scope-verified, merged, and remotely read back before the packet is called complete.
10. `CURRENT_WORK.md` advances to the next exact unaudited behavior before ending the packet.
11. No live Google production state and no executable product behavior is changed.

## Exact next action

Create/confirm branch `audit/g0-002b-context-travel` from the current MIRA 2.0 main checkpoint. Read legacy category-A evidence for behavior 6: **Generic context pairs: HOME/ROAD, HOME/TRUCK, HOME/FIELD, HOME/CAMPUS, HOME/OFFICE, HOME/AWAY, custom**. Inspect its candidate onboarding/context-router implementation and tests, assign its stable MIRA 2.0 feature ID, and draft the audited record before moving to behavior 7.

## Next packet boundary

If `M2-G0-002B` completes, `M2-G0-002C` begins with category-A behavior 11: **Company-paid mileage and estimated gross pay; both Thursday briefs**.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head when tools permit;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture new customer ideas in BACKLOG unless required for acceptance or explicitly reprioritized;
6. every assistant reply ends with the current packet recovery tag.
