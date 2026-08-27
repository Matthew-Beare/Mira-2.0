# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and its exact resume point.

## Completed packet before this branch

### `M2-G0-007F` — Feature Audit Slice F6 — family-school coordination and permission boundary

- **Merged PR:** #25
- **Merge SHA:** `549690c3a66d295c8effca064c21afb2b5bad0b2`
- **Main handoff commit activating F7:** `73fb7b59067507a51690cc04dfd509a3783787f9`
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
- **Branch start SHA:** `73fb7b59067507a51690cc04dfd509a3783787f9`
- **Status:** forensic evidence complete; registry normalization next.

## Exact category-F scope in this packet

16. **Travel/vacation/outdoor planning**.
17. **Work-trip/route/paid-work tracking**.

Do not expand this packet into F18 assets/maintenance/warranties/manuals, F19 personal knowledge/reference library, F20 backup/disaster recovery, F21 custom skill builder, F22 wearable/activity ingestion, F23 weather onboarding, category G, or executable MIRA 2.0 coding.

## Research checkpoint findings

1. Legacy `behavior-dependencies.json` maps F16 to A8 + A9 and F17 to A8 + A9 + A11 + A12. The shared canonical foundations are therefore `TRIP-001` + `ROUTE-001`; F17 additionally composes `MILE-001` + `MILE-002`.
2. No distinct `TRAVEL-*` or vacation database/lifecycle is justified. F16 is a selected planning composition around canonical Trip/Route state rather than a new authority.
3. `MODULE_CATALOG.md` describes vacation/trip planning through destination research, date constraints, reservations, Calendar projection, packing/preparation, documents, optional budgets and context-aware tasks. Those are optional adjacent paths and do not replace canonical Trip identity.
4. Outdoor/recreation planning similarly composes preparation tasks, equipment, reservations/permits, weather/routes, maintenance/consumables and trip plans; it does not justify a second trip database.
5. Legacy `ops_policy.py` has separate Route, Trip and Mileage schemas. Trip rows carry stable Trip ID, Route ID, origin/destination, departure, ETA/source, current location/time, weather watch, status and route override. Mileage rows separately carry Entry ID, Trip/Route references, company-paid miles, rate, gross estimate, source and settlement status.
6. Legacy deterministic tests verify bidirectional Route matching, reverse-route fallback, route-average ETA, explicit user ETA precedence, active-trip ROAD forcing, explicit HOME override precedence, route-weather gating/expiry, planned-trip prompt suppression and active-trip location refresh behavior.
7. Mileage tests verify Thursday company-paid-mile/gross summaries and entry tests prove directional paid miles are distinct fields, HOME mode does not suppress Thursday pay reporting, and malformed mileage input degrades the mileage path without aborting Trip/context operation.
8. `TRIP-001`, `ROUTE-001`, `MILE-001` and the legacy policy subcores retain their already-audited evidence levels. F16/F17 service wrappers do not receive MIRA 2.0 integration/live credit merely because child behavior is deterministic.
9. The legacy runtime is endpoint-to-endpoint. No durable ordered Trip-Leg entity or stable leg lifecycle was found; source search of the runtime exposes no dedicated leg model. Historical “multi-leg” support therefore cannot be claimed as a durable implemented itinerary lifecycle.
10. The practical current representation may use multiple Trip occurrences and Route references for successive legs, but grouping/order/revision semantics for one larger itinerary/work assignment remain an implementation gap unless separately specified and tested.
11. Route/location/ETA inference is projection/evidence, not lifecycle authority: it cannot fabricate departure, arrival, cancellation, reservation completion or paid-mile settlement.
12. Generic/vacation travel must not imply paid work, company mileage, payroll, ROAD context, weather watches, Calendar, reservations, retained documents or budget tracking unless those paths are separately selected/evidenced.
13. F17 work-trip readiness must preserve `MILE-001`/`MILE-002` independence. Route/map/odometer distance cannot substitute for company-paid miles; mileage/provider failure cannot erase Trip/Route truth.
14. Calendar projection remains optional through `CAL-007`; weather/hazard behavior remains optional through `WEATHER-001`; preparation uses `TASK-001`/`TASK-002`; evidence/documents and finance/budgeting remain separate domains.
15. PR #31 changed broad platform/runtime/client code but contains no dedicated travel/vacation/work-trip engine or feature entry that raises F16/F17 evidence. It remains candidate/reference evidence only.
16. No live Google production state was touched and no executable MIRA 2.0 behavior changed.

## Acceptance criteria

1. Determine whether F16/F17 are service compositions over existing `TRIP-001`, `ROUTE-001`, `MILE-001`, `MILE-002`, tasks, Calendar/weather/evidence, or whether any distinct canonical travel lifecycle truly requires a new feature ID. **Satisfied: no new travel authority justified.**
2. Preserve Trip occurrence identity separately from reusable Route knowledge, context state and paid mileage/pay authority. **Satisfied.**
3. Generic/vacation travel must not imply paid work, company miles, payroll, ROAD context, weather watch, Calendar projection, reservations, documents or budget tracking unless those selected paths are separately configured/evidenced. **Satisfied.**
4. Work-trip service readiness must require `TRIP-001` + `ROUTE-001` plus `MILE-001`/`MILE-002` only when paid-work tracking is selected; map/odometer/route distance must never substitute for company-paid miles. **Satisfied.**
5. Trip lifecycle/status must remain evidence-grounded. Route/location/ETA inference cannot fabricate departure, arrival, cancellation, reservation, completion or paid-mile settlement. **Satisfied.**
6. Multi-leg travel may reuse one Trip occurrence with ordered legs/route references only if the legacy/current evidence supports stable leg identity without collapsing Route identity; otherwise record the implementation gap explicitly rather than inventing completion evidence. **Satisfied: durable leg model absent and gap recorded.**
7. Vacation/outdoor preparation should reuse `TASK-*`; retained documents/equipment/weather/Calendar/budget paths stay independent optional integrations with their existing authorities and failure domains. **Satisfied.**
8. Calendar projection remains independently optional through `CAL-007`; weather/hazard behavior remains independently optional through `WEATHER-001` and cannot become canonical Trip truth. **Satisfied.**
9. Requirement status remains separate from implementation/test/integration/live evidence; legacy executable A8/A9/A11/A12 evidence does not automatically prove F16/F17 service integration in MIRA 2.0. **Satisfied.**
10. Reconcile PR #31/legacy branch evidence as candidate evidence only and create no duplicate service/domain engines without a distinct authority/lifecycle justification. **Satisfied.**
11. Update only `FEATURES.md`, `BACKLOG.md`, and `CURRENT_WORK.md`. Pending registry/backlog writes.
12. Open a bounded PR, verify changed-file scope and mergeability, merge using exact head SHA, and remotely read back before advancing. Pending.
13. Touch no legacy Google production state and change no executable MIRA 2.0 product behavior. **Satisfied so far.**

## Exact next action

Normalize F16/F17 into `FEATURES.md`: document `travel_planning` as selected composition over `TRIP-001`/`ROUTE-001` plus optional tasks/Calendar/weather/evidence/budget paths; document `work_trip_tracking` as `TRIP-001`/`ROUTE-001` plus `MILE-001`/`MILE-002`; explicitly record the absent durable Trip-Leg model without inventing a new feature unless the required lifecycle justifies it. Then update `BACKLOG.md` with `AUDIT-F7`, `SERVICE-DEPS-007`, and one bounded Trip/Route hardening ticket only if no existing work already covers stable multi-leg grouping/revision semantics.

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
