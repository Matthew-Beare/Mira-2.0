# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and its exact resume point.

## Active packet

- **Packet ID:** `M2-G0-002A`
- **Name:** Feature Audit Slice A1 — scheduler/context foundations
- **Class:** forensic audit / prerequisite
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `audit/g0-002a-scheduler-context`
- **Base SHA:** `e119bba05be7b074c3de4760fbf5998c3c5be402`
- **Evidence feature commit:** `fdd68b15079797149e70f84588b812089eb30bd6`
- **Backlog checkpoint commit:** `99947a89b5c2eb5a2960e2ecfd044b0628f4e8cc`
- **Status:** acceptance work complete; PR/merge/readback pending.

## Objective

Reconstruct the first bounded set of historical MIRA operational features from legacy evidence, assign stable semantic feature IDs, and document descriptions, dependencies, evidence level, and compatibility notes without implementing product behavior.

## Completed acceptance evidence

1. Assigned stable feature IDs `OPS-001` through `OPS-005` to the five scoped legacy behaviors.
2. Added full user-facing descriptions, rationale, requirement status, evidence boundaries, dependencies, downstream enables, milestone context, evidence paths and compatibility notes to `FEATURES.md`.
3. Separated repository test evidence from provider/live evidence instead of promoting historical implementation claims to MIRA 2.0 completion.
4. Reconciled relevant PR #31 evidence:
   - candidate `MIRA-F009` confirms the two New York brief slots and prohibited schedule variants;
   - `starter/scheduler-planner-contract.json` supports consolidating compatible scheduled work rather than creating feature-specific tasks;
   - neither source is treated as live provider proof.
5. Preserved active-trip forcing and generic context pairs as later separate features instead of silently absorbing them into `OPS-005`.
6. Updated `BACKLOG.md` with `AUDIT-A1` complete, `AUDIT-A2` next, and dependency findings from this slice.
7. Touched no live Google state and implemented no product behavior.

## Key audit findings

- `OPS-001` canonical two-slot semantics are test-supported, but actual MIRA 2.0 scheduler configuration/firing remains unverified.
- `OPS-002` uniqueness/no-duplicate behavior is policy-specified and requires future provider enumeration/readback for verification.
- `OPS-003` canonical runtime clock/DST/grace logic is genuinely test-verified in legacy code.
- `OPS-004` deterministic Run ID generation is test-verified, while fresh standalone provider delivery and Run Log integration remain unverified.
- `OPS-005` HOME/ROAD weekly transitions and explicit override semantics are test-verified in legacy code; live MIRA 2.0 canonical-state integration is not.

## Blockers

None inside the audit packet. Merge/readback is the remaining release step for this bounded documentation packet.

## Exact next action

Open a pull request from `audit/g0-002a-scheduler-context` to `main`, verify the changed-file scope is limited to the audit documentation/control files, merge the packet, remotely read back `FEATURES.md`, `BACKLOG.md`, and `CURRENT_WORK.md`, then update `CURRENT_WORK.md` on `main` to activate `M2-G0-002B`.

## Next packet after merge

### `M2-G0-002B` — Feature Audit Slice A2 — generalized context/travel foundations

Audit exactly legacy category-A behaviors 6-10:

1. Generic context pairs: HOME/ROAD, HOME/TRUCK, HOME/FIELD, HOME/CAMPUS, HOME/OFFICE, HOME/AWAY, custom.
2. Job title/duties inform context recommendation but never silently enable it.
3. Active trip tracking separate from context and paid-work tracking.
4. Multi-leg routes, learned runtime, current location, ETA, ahead/behind inference.
5. ROAD severe-weather/route-condition watch; HOME local weather only.

The first exact unaudited behavior is **Generic context pairs: HOME/ROAD, HOME/TRUCK, HOME/FIELD, HOME/CAMPUS, HOME/OFFICE, HOME/AWAY, custom**.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head when tools permit;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture new customer ideas in BACKLOG unless required for acceptance or explicitly reprioritized;
6. every assistant reply ends with the current packet recovery tag.
