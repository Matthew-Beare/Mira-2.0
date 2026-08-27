# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and its exact resume point.

## Active packet

- **Packet ID:** `M2-G0-002C`
- **Name:** Feature Audit Slice A3 — mileage/tasks/recovery foundations
- **Class:** forensic audit / prerequisite
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `audit/g0-002c-mileage-tasks-recovery`
- **Base main SHA:** `d43dbbb44c5ee6e324e89e98fd51f752de44e272`
- **Feature audit commit:** `2f2885508f13b64aa3b96ebd6a7b3ffa77894097`
- **Backlog checkpoint commit:** `324556dd45a4a2cd97544896edb8c6a1c139b943`
- **Status:** acceptance work complete; PR/merge/readback pending.

## Objective

Reconstruct legacy category-A behaviors 11-15 as bounded MIRA 2.0 feature records without changing executable behavior or live Google production state.

## Completed acceptance evidence

1. Assigned stable semantic IDs:
   - `MILE-001` Company-paid mileage and deterministic gross-pay reporting;
   - `MILE-002` Separate authoritative Miles & Pay tracker;
   - `TASK-001` Structured task hierarchy and one-action-per-item rendering;
   - `TASK-002` Evidence-grounded next actions and honest completion state;
   - `RECOVERY-001` Phase-aware Run Log, durable checkpoints and circuit-breaker recovery.
2. Added `MILE-*`, `TASK-*`, and `RECOVERY-*` feature families because the audit showed distinct authorities and verification boundaries.
3. Recorded complete descriptions, outcomes, requirement status, evidence ceilings, dependencies, downstream enables, evidence paths and compatibility boundaries.
4. Verified legacy deterministic mileage behavior for Thursday totals/gross, pay-week boundaries, status splits, explicit zero weeks, missing-mile actions and scoped tracker failure.
5. Kept the historical live Miles & Pay Google tracker as evidence of a prior deployment authority, not MIRA 2.0 live verification.
6. Verified deterministic task schema/grouping/visibility behavior while preserving task identity as one canonical record per action.
7. Kept generic next-action coaching below `test_verified` because policy semantics are strong but dedicated cross-domain tests are not yet audited/proven.
8. Recorded Run Log field/Run ID generation and selected degraded/error behavior as test-supported, while the broader circuit-breaker transaction remains strongly specified and live scheduled Run Log evidence remains unverified.
9. Kept optional-module failure isolation out of this packet for category-A behavior 16 and Slice-A-wide consistency audit in `M2-G0-002D`.
10. Updated `FEATURES.md` and `BACKLOG.md`; touched no live Google production state and changed no executable product behavior.

## Key audit findings

- Company-paid mileage is not route distance; the business rule and authority remain separate from route geometry.
- The logical Miles & Pay authority must survive backend changes; Google Sheets is an adapter, not the definition of the feature.
- Task structure and next-action reasoning are separate capabilities. A valid task registry does not prove good coaching, and a coach cannot invent completion state.
- `RECOVERY-001` is now an explicit dependency of `OPS-004`; a fresh scheduled Run ID is useful only if durable state can prove what happened to it.
- Optional-module failure isolation is system-wide enough to deserve its own final Slice-A audit packet rather than being hidden inside recovery.

## Blockers

None inside this audit packet. PR/merge/readback is the remaining packet release step.

## Exact next action

Open a pull request from `audit/g0-002c-mileage-tasks-recovery` to `main`, verify changed-file scope is limited to `FEATURES.md`, `BACKLOG.md`, and `CURRENT_WORK.md`, merge it, remotely read back the merged state, then update `CURRENT_WORK.md` on `main` to activate `M2-G0-002D`.

## Next packet after merge

### `M2-G0-002D` — Feature Audit Slice A4 — failure isolation and Slice-A closure

Audit exactly category-A behavior 16: **Optional module failure isolation**. Then perform a bounded consistency pass across all Slice-A features (`OPS-*`, `CTX-*`, `TRIP-*`, `ROUTE-*`, `WEATHER-*`, `MILE-*`, `TASK-*`, `RECOVERY-*`) to resolve dependency/evidence contradictions and close category A. Do not begin calendar/mail category B in this packet.

The exact first unaudited behavior is **Optional module failure isolation**.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head when tools permit;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture new customer ideas in BACKLOG unless required for acceptance or explicitly reprioritized;
6. before the final packet line, state any customer action needed; if none is needed, use `Just tell me to continue.`;
7. the final visible line remains the packet recovery tag.
