# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and its exact resume point.

## Completed packet before this branch

### `M2-G0-007F` — Feature Audit Slice F6 — family-school coordination and permission boundary

- **Merged PR:** #25
- **Merge SHA:** `549690c3a66d295c8effca064c21afb2b5bad0b2`
- **Main handoff commit activating F7:** `73fb7b59067507a51690cc04dfd509a3783787f9`
- **Result:** F15 creates no `FAMILY-*` authority. Education remains `EDU-001`; Person/relationship identity remains `PROFILE-012`; authorization remains `PROFILE-013`; profile roles recommend/route but do not grant access.

## Active packet

- **Packet ID:** `M2-G0-007G`
- **Name:** Feature Audit Slice F7 — travel planning and work-trip/pay composition
- **Class:** forensic audit / prerequisite
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `audit/g0-007g-travel-work-trip`
- **Branch start SHA:** `73fb7b59067507a51690cc04dfd509a3783787f9`
- **Status:** audit and authority-file normalization complete; PR/merge/readback pending.

## Exact category-F scope

16. **Travel/vacation/outdoor planning**.
17. **Work-trip/route/paid-work tracking**.

Do not expand this packet into F18 assets/maintenance/warranties/manuals, later category-F rows, category G, or executable MIRA 2.0 coding.

## F7 canonical result

1. No `TRAVEL-*` domain authority is created.
2. F16 `travel_planning` is selected-path composition over `TRIP-001` + `ROUTE-001`, governed by `SERVICE-001` + `SERVICE-002`.
3. Optional travel paths such as `TASK-*`, `CAL-007`, `WEATHER-001`, retained evidence/documents, equipment/assets, reservations and budgets remain independent authorities/capabilities and failure domains.
4. Generic/vacation/outdoor travel does not imply paid work, company mileage, payroll, ROAD context, weather watch, Calendar projection, reservations, documents, equipment state or budgeting.
5. F17 `work_trip_tracking` reuses `TRIP-001` + `ROUTE-001`; selected paid-work tracking additionally requires independent `MILE-001` + `MILE-002`.
6. Route/map/odometer distance cannot substitute for company-paid miles or pay evidence.
7. Location/ETA/progress evidence cannot fabricate Trip departure, arrival, cancellation, reservation completion or mileage settlement.
8. Legacy deterministic evidence proves endpoint Trip/Route behavior, directional route matching/runtime/ETA, active-Trip precedence, weather gating and mileage/pay summaries, but MIRA 2.0 persistence/integration/live evidence remains unverified.
9. No durable ordered Trip-Leg identity/grouping/revision lifecycle was found. The implementation gap is recorded as `TRIP-ROUTE-CORE-001`; no new semantic feature ID is minted solely to disguise that gap.
10. PR #31 contains no qualifying travel engine that raises F16/F17 evidence.
11. No live Google production state was touched and no executable MIRA 2.0 behavior changed.

## Durable packet commits

- **Research checkpoint:** `2160468d2bdd5d5734a2f9b11627a627ab073864`
- **Backlog normalization:** `accb824836564914eb92da836e05d6aed2169df5`
  - records `AUDIT-F7`, `SERVICE-DEPS-007`, `TRIP-ROUTE-CORE-001` and F7 dependency findings.
- **Feature registry normalization / maintenance:** `31ab984e6dca12c655340a6970a0b065e853247e`
  - original verbose `FEATURES.md`: 201,772 bytes, blob `1660321c0e25a323a8065f868e321229d8dbf9b5`;
  - compact canonical feature index blob: `85de04abddeedbf406de30fa2547e8a13d80fc1c`;
  - all 101 stable feature IDs, requirement/evidence status, canonical dependency IDs and F1-F17 service mappings are retained in the current index;
  - verbose rationale, evidence paths/tests and verification boundaries remain durable in Git history and prior packet checkpoints rather than being discarded.
  - this compaction was a reversible tooling/maintainability decision after the GitHub contents API became unreliable for ~200 KB whole-file replacement; it does not change product semantics or evidence levels.

## Acceptance criteria

1. Determine whether F16/F17 are compositions or require a distinct canonical travel lifecycle. **Satisfied: compositions; no `TRAVEL-*`.**
2. Preserve Trip identity separately from Route, context and mileage/pay. **Satisfied.**
3. Generic travel must not imply paid-work or optional adjacent modules. **Satisfied.**
4. Work-trip paid tracking preserves `MILE-001`/`MILE-002`; map/odometer distance cannot substitute. **Satisfied.**
5. ETA/location inference cannot fabricate lifecycle/payment state. **Satisfied.**
6. Multi-leg support must be evidence-grounded. **Satisfied: durable ordered-leg lifecycle absent; gap recorded as `TRIP-ROUTE-CORE-001`.**
7. Tasks/Calendar/weather/evidence/equipment/budget paths remain optional separate authorities. **Satisfied.**
8. Requirement and evidence levels remain separate. **Satisfied.**
9. PR #31 remains candidate/reference evidence only. **Satisfied.**
10. Update only `FEATURES.md`, `BACKLOG.md`, `CURRENT_WORK.md`. **Satisfied so far; final branch compare confirms only these three files.**
11. Open bounded PR, verify server-side changed-file scope/mergeability, merge using exact head SHA and remotely read back `main`. **Pending.**
12. Touch no legacy Google production and change no executable product behavior. **Satisfied.**

## Exact next action

1. Compare this branch against `main` and confirm zero-behind plus exactly `FEATURES.md`, `BACKLOG.md`, `CURRENT_WORK.md`.
2. Open the bounded F7 PR.
3. Verify GitHub server-side changed filenames and mergeability.
4. Merge using the exact branch head SHA.
5. Remotely read back F16/F17 feature mappings, F7 backlog findings and merge state from `main`.
6. Only after readback, update `CURRENT_WORK.md` on `main` to activate `M2-G0-007H` and create its branch from that exact handoff.

## Next packet after F7

### `M2-G0-007H` — Feature Audit Slice F8

Begin with category-F row 18 **Assets/maintenance/warranties/manuals**. Determine the remainder of the bounded F8 slice from authoritative ledger/dependency evidence after F7 closes; do not infer the boundary from row adjacency.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head when tools permit;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture new customer ideas in BACKLOG unless required for acceptance or explicitly reprioritized;
6. finish each MIRA-development response with the current packet tag followed by either a concise customer action needed or exact fallback `Just tell me to continue.`
