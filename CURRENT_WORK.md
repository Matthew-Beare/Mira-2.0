# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and its exact resume point.

## Completed packet before this branch

### `M2-G0-007F` — Feature Audit Slice F6 — family-school coordination and permission boundary

- **Merged PR:** #25
- **Merge SHA:** `549690c3a66d295c8effca064c21afb2b5bad0b2`
- **Audited row:** F15 — Parent/child school coordination.
- **Result:** no `FAMILY-*` authority was created; school truth remains `EDU-001`, Person/relationship identity remains `PROFILE-012`, and cross-person permission/sharing remains `PROFILE-013`. Parent/dependent roles are recommendation inputs, never readiness or authorization gates.
- **Backlog:** added `AUDIT-F6` and `SERVICE-DEPS-006`; existing Person, permission, education and Calendar implementation work remains authoritative.
- **Remote readback:** F6 `FEATURES.md` and `BACKLOG.md` verified on `main` after merge.
- **Live Google production touched:** no.
- **Executable product behavior changed:** no.

## Active packet

- **Packet ID:** `M2-G0-007G`
- **Name:** Feature Audit Slice F7 — travel planning and work-trip/pay composition
- **Class:** forensic audit / prerequisite
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `audit/g0-007g-travel-work-trip`
- **Base merge SHA:** `549690c3a66d295c8effca064c21afb2b5bad0b2`
- **Status:** activated; forensic evidence pass next.

## Exact category-F scope in this packet

Audit exactly legacy category-F rows 16-17:

16. **Travel/vacation/outdoor planning** — ACCEPTED direction; legacy dependency map requires A8 active Trip state plus A9 Route/runtime/location/ETA behavior, with Calendar projection optional.
17. **Work-trip/route/paid-work tracking** — REQUIRED; legacy dependency map requires the same A8/A9 Trip/Route foundations plus A11 company-paid mileage/gross and A12 separate Miles & Pay authority.

Do not expand this packet into F18 assets/maintenance/warranties/manuals, F19 personal knowledge/reference library, F20 backup/disaster recovery, F21 custom skill builder, F22 wearable/activity ingestion, F23 weather onboarding, category G, or executable MIRA 2.0 coding.

## Packet-boundary rationale

- F16 and F17 share the same canonical travel foundations: `TRIP-001` and `ROUTE-001`.
- F17 is the paid-work specialization of that travel state and adds the already-separate `MILE-001`/`MILE-002` authority boundary; paid mileage must never become generic Trip distance.
- F16's vacation/outdoor planning prose describes selected planning projections around a Trip: destination/date constraints, reservations, preparation tasks, documents, optional budgets, Calendar and route/weather support. No separate vacation-state engine has yet been evidenced.
- F18 immediately switches to asset/evidence domains, so rows 16-17 form one bounded dependency-coherent slice.

## Acceptance criteria

1. Determine whether F16/F17 are service compositions over existing `TRIP-001`, `ROUTE-001`, `MILE-001`, `MILE-002`, tasks, Calendar/weather/evidence, or whether any distinct canonical travel lifecycle truly requires a new feature ID.
2. Preserve Trip occurrence identity separately from reusable Route knowledge, context state and paid mileage/pay authority.
3. Generic/vacation travel must not imply paid work, company miles, payroll, ROAD context, weather watch, Calendar projection, reservations, documents or budget tracking unless those selected paths are separately configured/evidenced.
4. Work-trip service readiness must require `TRIP-001` + `ROUTE-001` plus `MILE-001`/`MILE-002` only when paid-work tracking is selected; map/odometer/route distance must never substitute for company-paid miles.
5. Trip lifecycle/status must remain evidence-grounded. Route/location/ETA inference cannot fabricate departure, arrival, cancellation, reservation, completion or paid-mile settlement.
6. Multi-leg travel may reuse one Trip occurrence with ordered legs/route references only if the legacy/current evidence supports stable leg identity without collapsing Route identity; otherwise record the implementation gap explicitly rather than inventing completion evidence.
7. Vacation/outdoor preparation should reuse `TASK-*`; retained documents/equipment/weather/Calendar/budget paths stay independent optional integrations with their existing authorities and failure domains.
8. Calendar projection remains independently optional through `CAL-007`; weather/hazard behavior remains independently optional through `WEATHER-001` and cannot become canonical Trip truth.
9. Requirement status remains separate from implementation/test/integration/live evidence; legacy executable A8/A9/A11/A12 evidence does not automatically prove F16/F17 service integration in MIRA 2.0.
10. Reconcile PR #31/legacy branch evidence as candidate evidence only and create no duplicate service/domain engines without a distinct authority/lifecycle justification.
11. Update only `FEATURES.md`, `BACKLOG.md`, and `CURRENT_WORK.md`.
12. Open a bounded PR, verify changed-file scope and mergeability, merge using exact head SHA, and remotely read back before advancing.
13. Touch no legacy Google production state and change no executable MIRA 2.0 product behavior.

## Exact next action

Create branch `audit/g0-007g-travel-work-trip` from this main handoff commit. Inspect authoritative F16/F17 evidence across the feature ledger, `behavior-dependencies.json`, `MODULE_CATALOG.md`, Trip/Route/mileage policy/runtime code and deterministic tests, plus any relevant PR #31 travel candidate. First decide whether F16 or F17 requires any canonical feature beyond existing `TRIP-001`, `ROUTE-001`, `MILE-001`, `MILE-002` and selected task/Calendar/weather/evidence composition; checkpoint that finding before registry normalization.

## Next packet after F7

### `M2-G0-007H` — Feature Audit Slice F8

Begin with category-F row 18 **Assets/maintenance/warranties/manuals** and determine the remainder of the bounded F8 slice from authoritative dependency evidence after F7 closes.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head when tools permit;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture new customer ideas in BACKLOG unless required for acceptance or explicitly reprioritized;
6. before the final packet line, state any customer action needed; if none is needed, use `juset tell me to continue`;
7. the packet recovery tag remains visible in every MIRA-development reply.
