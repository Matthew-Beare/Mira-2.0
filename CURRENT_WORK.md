# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and its exact resume point.

## Completed packet before this branch

### `M2-G0-007A` — Feature Audit Slice F1 — core life-service module boundaries

- **Merged PR:** #20
- **Merge SHA:** `9925b1b097342626bb7f2c16d94e2327b144de5c`
- **Audited rows:** F1-F5 — Briefs/action digest; Next-action planner; Email triage; Orders/shipments; Receipt archive.
- **Audited feature:** `SERVICE-002` plus canonical service-to-domain mappings.
- **Result:** service activation, dependency readiness, recommendation, implementation evidence and provider capability are now explicitly separated; two semantic dependency defects and one legacy activation-migration ambiguity are ranked for repair.
- **Live Google production touched:** no.
- **Executable product behavior changed:** no.

## Active packet

- **Packet ID:** `M2-G0-007B`
- **Name:** Feature Audit Slice F2 — finance, appointment/calendar, and administrative-health services
- **Class:** forensic audit / prerequisite
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `audit/g0-007b-finance-calendar-health-services`
- **Base merge SHA:** `9925b1b097342626bb7f2c16d94e2327b144de5c`
- **Status:** packet activated; branch creation and forensic evidence pass next.

## Exact category-F scope in this packet

Audit exactly legacy category-F rows 6-8:

6. **Personal finance organization** — ACCEPTED direction; partial reconciliation executables, broader service specification-only.
7. **Appointments/calendar/reminders** — REQUIRED; executable reminder planner + calendar/skill workflow; provider projection requires readback.
8. **Administrative health organization** — PROPOSED/ACCEPTED direction; medication-reminder safety core executable; broader service specification-only and must exclude diagnosis/dosing.

Do not expand this packet into F9 Shopping/procurement, F10 Recipes/meals/groceries, household/laundry/routines, later category-F rows, category G, or executable MIRA 2.0 coding.

## Handoff evidence used to bound F2

1. The authoritative forensic ledger places F6-F8 together immediately after the F1 service slice and before shopping/food services.
2. Legacy dependency map:
   - `f-06` requires `c-10` and treats `c-12` as optional;
   - `f-07` requires `b-01`, `b-02`, `b-03`, `b-06`;
   - `f-08` requires `b-04` and treats `b-05` as optional.
3. F6-F8 share privacy/sensitive-state/readback concerns and therefore form a tighter bounded slice than combining them with shopping/food.
4. The legacy Personal finance onboarding prompt is broader than the current dependency map: spending visibility, budgeting, savings, debt, recurring bills, purchase planning and cash-flow monitoring are discussed, while the dependency graph currently points primarily at reconciliation plus optional complete-account ingestion. This must be reconciled rather than silently treated as complete.
5. Legacy appointment service prose includes verified appointment reconciliation, canonical appointment identity, one linked Calendar event, reminder profiles, provider readback, revision/cancellation update, ambiguity handling and independent Calendar Projection. Category-B audit named reminder/visibility behaviors but did not fully normalize this broader appointment-reconciliation/projection surface, so F7 may expose a distinct missing canonical feature rather than being only a wrapper.
6. `appointment_identity.py` and `test_appointment_identity.py` provide deterministic evidence for provider/service identity resolution, source binding, supported research, owner correction, ambiguity failure and canonical appointment title; they do not alone prove Calendar projection or provider write/readback.
7. F8 must keep administrative health organization distinct from diagnosis, treatment, dose inference, missed-dose advice and caregiver-sharing authority. Existing `REMIND-001`/`REMIND-002` cover medication reminder safety/sharing but may not represent the broader administrative-health service boundary.

## Acceptance criteria

1. Account for F6-F8 with stable semantic mappings and create new feature IDs only where distinct behavior/authority is genuinely missing.
2. Reuse `SERVICE-001`/`SERVICE-002` for activation/readiness rather than duplicating service machinery.
3. For F6, separate bounded spending/reconciliation, beneficiary/reimbursement, subscriptions/recurring commitments and complete financial-account ingestion; do not let a broad “finance” service imply capabilities not present or authorized.
4. For F7, determine whether verified appointment reconciliation/calendar projection requires a new canonical `CAL-*` feature distinct from existing reminder/lookahead/visibility features, and record exact evidence/verification boundary.
5. For F8, preserve medical-safety boundaries: administrative organization only, no diagnosis/dosing/treatment inference, no caregiver sharing without explicit permission.
6. Record required versus optional child behaviors and note semantic dependency defects in legacy F6-F8 mappings.
7. Preserve provider readback requirements for Calendar/financial mutations and exact account/resource scope.
8. Keep service activation separate from capability/permission state.
9. Reconcile relevant deterministic legacy tests and PR #31/reference evidence without promoting unmerged/provider/live claims.
10. Update only `FEATURES.md`, `BACKLOG.md`, and `CURRENT_WORK.md` unless a hard audit dependency requires another authority-file change.
11. Open a bounded PR, verify scope, merge and remotely read back before advancing to F3.
12. Touch no legacy Google production state and change no executable MIRA 2.0 product behavior.

## Exact next action

Create branch `audit/g0-007b-finance-calendar-health-services` from this handoff commit. Then audit F6 **Personal finance organization** first: reconcile the legacy `f-06` dependency map against category-C canonical features and onboarding/module-catalog finance intent, determine whether the service needs `SPEND-001`, `PAYMENT-001`, `REIMB-001`, `SUB-001` and/or optional `FIN-001`, and record evidence/permission boundaries before moving to F7.

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
