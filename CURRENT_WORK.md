# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and its exact resume point.

## Active packet

- **Packet ID:** `M2-G0-002B`
- **Name:** Feature Audit Slice A2 — generalized context/travel foundations
- **Class:** forensic audit / prerequisite
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `audit/g0-002b-context-travel`
- **Base main SHA:** `bee1d50a15e1d84f2fa3b679fb78ae9fdc3deec4`
- **Feature audit commit:** `bffc1f922b4e00c78db157f070b929ce39438e17`
- **Backlog checkpoint commit:** `5a185c5b84b397e76905a81439ac1a0caeb1ec65`
- **Status:** acceptance work complete; PR/merge/readback pending.

## Objective

Reconstruct legacy category-A behaviors 6-10 as bounded MIRA 2.0 feature records without changing executable behavior or live Google production state.

## Completed acceptance evidence

1. Assigned stable semantic IDs:
   - `CTX-001` Configurable operating-context pairs;
   - `CTX-002` Evidence-gated context recommendation and explicit activation;
   - `TRIP-001` Independent trip occurrence lifecycle;
   - `ROUTE-001` Learned routes, directional runtime, location and ETA inference;
   - `WEATHER-001` Context-gated HOME and ROAD weather intelligence.
2. Added `CTX-*`, `TRIP-*`, `ROUTE-*`, and `WEATHER-*` ID families because the audit showed these have distinct authorities/dependencies and should not remain a single overloaded `OPS-*` bucket.
3. Recorded complete user-facing descriptions, rationale, requirement status, delivery/evidence boundaries, dependencies, downstream enables, evidence paths, acceptance boundaries and compatibility notes.
4. Verified legacy candidate context-router behavior through code/tests for HOME/ROAD, HOME/TRUCK, HOME/FIELD, HOME/CAMPUS, HOME/AWAY, custom labels, explicit bypass, needs-confirmation state and title-keyword false-positive protection.
5. Recorded that HOME/OFFICE is a valid configured pair through custom-label support but is not a dedicated audited legacy recommendation heuristic.
6. Kept trip occurrence state independent from reusable Route knowledge and later Mileage/paid-work accounting.
7. Recorded route-average ETA and time-progress primitives as implemented/test-supported while keeping human-facing ahead/behind interpretation below an unearned verification level.
8. Recorded deterministic HOME/ROAD weather gating and route-watch expiry as test-verified, while actual NWS/DOT/511 evidence retrieval remains an external integration boundary.
9. Reconciled materially relevant PR #31 evidence and found no narrower context/travel implementation that supersedes these records; broad candidate `MIRA-F009` only requires mode-specific filtering to remain contract-driven/tested.
10. Updated `BACKLOG.md`, including a non-blocking queued governance item for the corrected reply footer wording `Just tell me to continue.` without expanding this packet.
11. Touched no live Google production state and changed no executable product behavior.

## Key audit findings

- Context recommendation and context activation are separate features and must remain separate in onboarding.
- Generic context labels generalize `OPS-005`; they do not replace its deterministic transition/override semantics.
- Trip, Route, context, Mileage and weather state are related through explicit references, not one combined mutable state object.
- Route/ETA logic has stronger test evidence than the old ledger's wording suggested, but ahead/behind user-facing inference still needs explicit verification.
- Weather gating is deterministic/tested; hazard conclusions still require source-grounded external evidence.

## Blockers

None inside this audit packet. PR/merge/readback is the remaining packet release step.

## Exact next action

Open a pull request from `audit/g0-002b-context-travel` to `main`, verify the changed-file scope is limited to `FEATURES.md`, `BACKLOG.md`, and `CURRENT_WORK.md`, merge it, remotely read back the merged state, then update `CURRENT_WORK.md` on `main` to activate `M2-G0-002C`.

## Next packet after merge

### `M2-G0-002C` — Feature Audit Slice A3 — mileage/tasks/recovery foundations

Audit exactly legacy category-A behaviors 11-15:

1. Company-paid mileage and estimated gross pay; both Thursday briefs.
2. Separate accessible Miles & Pay tracker.
3. Task hierarchy High/Medium/Low → classification → subsystem → one task per bullet.
4. Next-action coaching and honest completion evidence.
5. Phase-aware Run Log, last-good checkpoint, resumable recovery, circuit breaker.

The exact first unaudited behavior is **Company-paid mileage and estimated gross pay; both Thursday briefs**.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head when tools permit;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture new customer ideas in BACKLOG unless required for acceptance or explicitly reprioritized;
6. before the final packet line, state any customer action needed; if none is needed, use `Just tell me to continue.`;
7. the final visible line remains the packet recovery tag.
