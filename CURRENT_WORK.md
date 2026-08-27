# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and its exact resume point.

## Completed packet

### `M2-G0-006F` — Feature Audit Slice E6 — provider onboarding/bootstrap and category-E closure

- **Merged PR:** #19
- **Merge SHA:** `2adf361c86731d76819acc7b24b025c47bb3a730`
- **Main handoff commit activating F1:** `ac44f475b25d3245fceeaade198f3cc2a45d567d`
- **Audited features:** `PROVIDER-002`, `ONBOARD-007`, `PROVIDER-003`.
- **Result:** all 26 historical category-E rows are accounted for and remotely read back on `main`.
- **Live Google production touched:** no.
- **Executable product behavior changed:** no.

## Active packet

- **Packet ID:** `M2-G0-007A`
- **Name:** Feature Audit Slice F1 — core life-service module boundaries
- **Class:** forensic audit / prerequisite
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `audit/g0-007a-core-life-services`
- **Branch start SHA:** `ac44f475b25d3245fceeaade198f3cc2a45d567d`
- **Status:** forensic evidence pass complete; feature/backlog normalization next.

## Exact category-F scope in this packet

Audit exactly the first five rows of legacy category F, **Life-service modules discussed or catalogued**:

1. Briefs/action digest — REQUIRED; executable + skill workflow.
2. Next-action planner — REQUIRED/ACCEPTED; skill workflow.
3. Email triage — REQUIRED; skill workflow.
4. Orders/shipments — REQUIRED; executable + skill workflow.
5. Receipt archive — REQUIRED; skill workflow + partial executables.

Do not expand this packet into personal finance, calendar/reminders, health organization, shopping, meals, household routines or later category-F rows.

## Research findings

1. Category F is a service-catalog/composition layer over behavior already audited in categories A-E. F1 must not manufacture duplicate Brief, Task, Mail, Order or Receipt feature IDs.
2. `starter/MODULE_CATALOG.md` presents Briefs/action digest, Next-action planner, Important-mail triage, Orders/shipment lifecycle and Receipt database as user-discoverable modules/services and explicitly says optional modules are not silently enabled.
3. `starter/tools/onboarding_profile_router.py` has stable service keys `briefs`, `next_actions`, `email_triage`, `orders_shipments`, and `receipt_archive` inside a finite service catalog. All default to `unresolved`; explicit activation is separate from catalog presence and implementation capability.
4. `starter/tests/test_onboarding_profile_router.py` directly verifies the service catalog never claims unverified implementation, never silently activates services, accepts explicit activation/disablement, rejects unknown services and rejects conflicting legacy/current activation state.
5. `starter/behavior-dependencies.json` represents F services as aggregate behaviors with required child behaviors rather than copied implementation:
   - `f-01` requires `a-01`, `a-03`, `a-04`, `a-15`, `a-16`;
   - `f-02` requires `a-13`, `a-14`;
   - `f-03` requires `b-07`, `b-08`, `b-09`;
   - `f-04` requires `c-01`, `c-02`, `c-03`, `c-05`;
   - `f-05` requires `c-06`, `c-07`, `c-09`.
6. `behavior_dependency_check.py` validates dependency references/cycles, evaluates transitive required/optional behavior readiness, blocks only affected behavior, degrades only affected optional paths, and has hard policy gates forbidding automatic dependency installation and automatic behavior enablement.
7. `test_behavior_dependency_check.py` proves every forensic catalog row has one dependency assignment and directly proves an aggregate service (`f-05`) blocks if a required child behavior is unavailable while unrelated workflows remain unchanged.
8. `integration_dependency_router.py`/tests build readiness only from verified capabilities/authorities and preserve explicit-user-goal/no-auto-enable remediation behavior.
9. The distinct missing canonical concept is therefore a generic service-composition contract, provisionally `SERVICE-002`: an activated/catalogued service is a dependency bundle over canonical behaviors, with derived readiness/degradation and failure isolation. The F1 rows are instances/mappings of that contract, not five new behavior implementations.
10. F1 underlying canonical mappings are:
   - Briefs/action digest → `OPS-001`, `OPS-003`, `OPS-004`, `RECOVERY-001`, `RECOVERY-002` plus service activation/composition;
   - Next-action planner → `TASK-001`, `TASK-002` plus service activation/composition;
   - Email triage → `MAIL-001`, `MAIL-002`, `MAIL-003` plus service activation/composition;
   - Orders/shipments → `ORDER-001`, `ORDER-002`, `ORDER-003`, `ORDER-005` plus service activation/composition;
   - Receipt archive → `RECEIPT-001`, `RECEIPT-002`, `RECEIPT-003` plus service activation/composition.
11. Two semantic dependency defects were found in the legacy bundle map:
   - `f-01` omits `a-02` / `OPS-002`, so aggregate Brief readiness does not explicitly require single-dispatcher/no-duplicate-schedule safety;
   - `f-04` omits `c-04` / `ORDER-004`, so aggregate Orders/shipments readiness does not explicitly require replacement/supersession correctness.
12. A compatibility/UI coupling defect also exists: legacy `order_lifecycle_enabled` maps only to `orders_shipments` although the question text says “receipt and order lifecycle.” The canonical service model already contains separate `orders_shipments` and `receipt_archive`; MIRA 2.0 should not let that legacy convenience field silently couple or misstate the two services.
13. The generic service activation/dependency/failure-isolation machinery has real deterministic legacy test evidence. Individual F1 bundle mappings are machine-readable and catalog/CI-validated, but the two omissions above prevent treating every mapping as semantically complete.
14. No MIRA 2.0 service-catalog persistence/readback or end-to-end service activation → dependency-readiness integration is yet verified.
15. No live Google production state was touched and no executable MIRA 2.0 product behavior was changed.

## Acceptance criteria

1. Account for all five F1 ledger rows with stable semantic mapping.
2. Reuse existing canonical feature IDs where the F row is only a service projection/composition of already-audited behavior; create a new stable feature only if the service layer has distinct behavior/authority not represented elsewhere.
3. Keep service activation (`SERVICE-001`) separate from behavior implementation, provider capability and recommendation.
4. Record each service’s required/optional behavior dependencies and failure-domain boundary.
5. Preserve optional/module failure isolation under `RECOVERY-002`; one unavailable service/provider path must not falsify or disable unrelated service state.
6. Preserve communication safety: email triage cannot imply outbound-send authority.
7. Preserve canonical commerce boundaries: orders/shipments and receipt archive are related services but must not merge fulfillment state, receipt/purchase identity or financial settlement authorities.
8. Record actual legacy implementation/test/workflow evidence and MIRA 2.0 verification gaps without promoting contract/skill prose to executable evidence.
9. Reconcile relevant PR #31 candidates only as evidence/salvage reference; never merge wholesale or inherit integration/live status.
10. Update only `FEATURES.md`, `BACKLOG.md`, and `CURRENT_WORK.md` unless a hard audit dependency requires another authority-file change.
11. Open a bounded PR, verify changed-file scope, merge and remotely read back before advancing to F2.
12. Touch no live Google production state and change no executable MIRA 2.0 product behavior.

## Exact next action

Normalize `SERVICE-002` and the five F1 service-to-feature mappings in `FEATURES.md` without duplicating existing OPS/TASK/MAIL/ORDER/RECEIPT features. Add ranked service-dependency hardening for the missing `OPS-002` and `ORDER-004` edges plus legacy order/receipt activation coupling, then update `BACKLOG.md` and close F1 acceptance state.

## Next packet after F1

### `M2-G0-007B` — Feature Audit Slice F2

Begin with category-F row 6 **Personal finance organization** and continue only through the next bounded coherent service slice determined during F1 closure. Do not pre-expand F2 from memory.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head when tools permit;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture new customer ideas in BACKLOG unless required for acceptance or explicitly reprioritized;
6. before the final packet line, state any customer action needed; if none is needed, use `Just tell me to continue.`;
7. the final visible line remains the packet recovery tag.
