# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and its exact resume point.

## Completed packet before this branch

### `M2-G0-007A` — Feature Audit Slice F1 — core life-service module boundaries

- **Merged PR:** #20
- **Merge SHA:** `9925b1b097342626bb7f2c16d94e2327b144de5c`
- **Audited rows:** F1-F5 — Briefs/action digest; Next-action planner; Email triage; Orders/shipments; Receipt archive.
- **Audited feature:** `SERVICE-002` plus canonical service-to-domain mappings.
- **Result:** service activation, dependency readiness, recommendation, implementation evidence and provider capability are explicitly separated; semantic dependency/migration defects are ranked for repair.
- **Live Google production touched:** no.
- **Executable product behavior changed:** no.

## Active packet

- **Packet ID:** `M2-G0-007B`
- **Name:** Feature Audit Slice F2 — finance, appointment/calendar, and administrative-health services
- **Class:** forensic audit / prerequisite
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `audit/g0-007b-finance-calendar-health-services`
- **Branch start SHA:** `204665fb84cfb7588c64074e5e6c2282c4074453`
- **Status:** forensic evidence pass complete; feature/backlog normalization next.

## Exact category-F scope in this packet

Audit exactly legacy category-F rows 6-8:

6. **Personal finance organization** — ACCEPTED direction; partial reconciliation executables, broader service specification-only.
7. **Appointments/calendar/reminders** — REQUIRED; executable reminder planner + calendar/skill workflow; provider projection requires readback.
8. **Administrative health organization** — PROPOSED/ACCEPTED direction; medication-reminder safety core executable; broader service specification-only and must exclude diagnosis/dosing.

Do not expand this packet into F9 Shopping/procurement, F10 Recipes/meals/groceries, household/laundry/routines, later category-F rows, category G, or executable MIRA 2.0 coding.

## Forensic findings

### F6 — Personal finance organization

1. Legacy `f-06` requires only `c-10` and treats `c-12` as optional. Historical `c-10` combined expected-charge/refund/reimbursement/household-beneficiary reconciliation and was intentionally split during category C into `PAYMENT-001` and `REIMB-001`; `c-12` maps to future complete-account capability `FIN-001`.
2. The onboarding prompt is much broader than that dependency map: spending visibility, budgeting, saving, debt reduction, recurring bills, purchase planning and cash-flow monitoring are presented as possible finance goals.
3. Canonical category-C capabilities are already separated:
   - `SPEND-001` — evidence-bounded spending rollup;
   - `PAYMENT-001` — merchant charge/settlement reconciliation (`test_verified` core);
   - `REIMB-001` — beneficiary/reimbursement reconciliation (specified, deterministic engine absent);
   - `SUB-001` — optional subscription/free-trial tracking (historical concept only);
   - `FIN-001` — complete connected financial-account ingestion/reconciliation (future/infrastructure-deferred).
4. The executable inventory confirms only bounded payment reconciliation/refund-deadline cores in this service area; there is no generic budgeting, savings, debt, cash-flow, subscription, complete-account, or generic reimbursement engine sufficient to make the broad finance service “implemented.”
5. Therefore `finance` is a **goal-scoped service composition**, not one monolithic required dependency set. Only user-selected finance goals should activate their child behavior/capability requirements; unavailable/unselected finance subdomains must remain degraded/unavailable rather than blocking unrelated finance help or being advertised as ready.
6. The legacy F6 map is semantically incomplete because it omits `SPEND-001` for spending visibility and does not represent `SUB-001`/broader future `FIN-001` goals honestly. It also cannot use historical `c-10` as a single child now that payment and reimbursement are separate verification boundaries.

### F7 — Appointments/calendar/reminders

7. The canonical service router already separates `appointments_calendar` from `appointment_reminders`. Historical F7 combines them and therefore must not become one activation bit in MIRA 2.0.
8. Existing category-B features cover special lookahead (`CAL-001`), reminder timing (`CAL-002`/`CAL-003`), context-aware visibility (`CAL-004`), medication reminders (`REMIND-001`) and caregiver sharing (`REMIND-002`), but do not fully capture the broader verified appointment reconciliation + linked Calendar projection contract in the module catalog.
9. `appointment_identity.py` is a genuine deterministic legacy core for appointment provider/service identity: durable alias/source binding, bounded public-research enrichment, owner correction, ambiguity failure and specialty/category labels without unsupported promotion. `test_appointment_identity.py` directly verifies cached resolution, supported research, low-confidence refusal, owner correction and ambiguity failure.
10. `reminder_policy.py` separately validates appointment event/source identity and deterministic reminder planning, but it does not create/read back Calendar events.
11. The module catalog specifies a distinct provider-mutation boundary: one canonical appointment, one linked Calendar event, target calendar, reminder profile, source linkage, revision/cancellation update instead of duplication, and provider readback before calling projection reconciled.
12. PR #31 adds generic Google Calendar capability/readback language in its Google-native skill but no dedicated appointment/calendar implementation that earns MIRA 2.0 integration/live credit.
13. F7 therefore exposes two distinct missing canonical concepts with different evidence ceilings:
   - appointment/provider identity reconciliation and evidence-safe classification, with deterministic legacy tests;
   - idempotent linked Calendar projection/update/readback, strongly specified but not integration-verified.
14. Legacy `f-07` also has a dependency defect: it hard-requires `b-01` / the personal Saturday 02:45 AM seven-day lookahead. That deployment-specific brief projection is not a universal prerequisite for an appointments/calendar service.
15. `CAL-004` context-aware appointment visibility is also not universally required for every deployment and should be conditional/optional when context-aware presentation is selected.
16. Appointment reminders remain a separately activatable service path requiring `CAL-002`/`CAL-003` plus canonical appointment state; enabling appointments/calendar alone does not authorize reminder delivery.

### F8 — Administrative health organization

17. The canonical service router already separates `health_organization` from `medication_reminders`. Historical `f-08` requires medication reminders and treats caregiver sharing as optional, which incorrectly makes the reminder implementation define the broader health service.
18. The ledger explicitly says the broader administrative-health service remains specification-only and must exclude diagnosis/dosing. Existing `REMIND-001` and `REMIND-002` are narrower safety features and cannot be used to claim a broad health-organization implementation.
19. A distinct canonical specification-level feature is warranted for **non-clinical administrative health organization**: organizing user-authorized administrative health state/evidence/tasks without diagnosis, treatment, dose/timing inference or medical advice. Medication reminders and caregiver sharing remain separate opt-in child services/permissions.
20. No dedicated broader health-organization executable/test core or PR #31 implementation was located. Any new health feature therefore remains `specified`/desired, not implemented.

## Proposed normalization

- Refine `SERVICE-002` so an umbrella service may have goal/module-selected child behaviors; readiness is computed only for selected submodules and cannot advertise unsupported adjacent goals.
- F6 service key `finance` maps by selected goal to existing `SPEND-001`, `PAYMENT-001`, `REIMB-001`, optional `SUB-001`, and future/optional `FIN-001`; there is no new monolithic finance implementation feature.
- Add `CAL-005` — evidence-safe appointment/provider identity reconciliation.
- Add `CAL-006` — idempotent linked Calendar projection/update with exact provider readback.
- F7 maps `appointments_calendar` to `CAL-005` + `CAL-006` with conditional `CAL-004`; `appointment_reminders` remains separate and maps to `CAL-002`/`CAL-003` plus canonical appointment state. `CAL-001` stays a Brief/personal-policy projection, not a universal appointment-service dependency.
- Add `HEALTH-001` — non-clinical administrative health organization boundary, specification-level only.
- F8 maps `health_organization` to `HEALTH-001`; `medication_reminders` separately maps to `REMIND-001`; caregiver sharing remains optional `REMIND-002` and requires explicit recipient/permission.

## Acceptance criteria

1. Account for F6-F8 with stable semantic mappings and create new feature IDs only where distinct behavior/authority is genuinely missing.
2. Reuse and, where needed, refine `SERVICE-001`/`SERVICE-002` for activation/readiness rather than duplicating service machinery.
3. Keep finance capability goal-scoped; no umbrella “finance ready” claim may imply budgeting/debt/cash-flow/accounts/subscriptions/reimbursement unless the selected sub-capability and evidence exist.
4. Normalize appointment/provider identity separately from Calendar provider mutation/readback because their evidence and failure domains differ.
5. Keep `appointments_calendar` and `appointment_reminders` separately activatable; remove the personal Saturday lookahead from universal appointment-service readiness.
6. Preserve administrative-health safety: no diagnosis, treatment, dosing, missed-dose advice, or caregiver sharing by implication.
7. Keep `health_organization`, `medication_reminders`, and caregiver sharing as separate activation/permission surfaces.
8. Record actual legacy implementation/test/workflow evidence and MIRA 2.0 verification gaps without promoting contract/skill prose to executable evidence.
9. Reconcile relevant PR #31 evidence only as unmerged/reference evidence.
10. Update only `FEATURES.md`, `BACKLOG.md`, and `CURRENT_WORK.md`.
11. Open a bounded PR, verify scope, merge and remotely read back before advancing to F3.
12. Touch no legacy Google production state and change no executable MIRA 2.0 product behavior.

## Exact next action

Normalize the F2 findings in `FEATURES.md`: refine `SERVICE-002` for selected goal/module dependencies, add `CAL-005`, `CAL-006`, and `HEALTH-001`, and record F6-F8 service mappings/evidence ceilings/dependency defects. Then rank implementation/hardening work in `BACKLOG.md`, close acceptance state in this file, and run the three-file PR/merge/readback gate.

## Next packet after F2

### `M2-G0-007C` — Feature Audit Slice F3

Begin with category-F row 9 **Shopping/procurement** and determine the rest of the bounded F3 slice only after F2 closes. Do not pre-expand from conversational memory.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head when tools permit;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture new customer ideas in BACKLOG unless required for acceptance or explicitly reprioritized;
6. before the final packet line, state any customer action needed; if none is needed, use `Just tell me to continue.`;
7. the final visible line remains the packet recovery tag.
