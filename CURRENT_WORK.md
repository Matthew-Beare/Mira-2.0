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
- **Research checkpoint commit:** `43a9475336d18fc18170049e3afb9d243b16cf20`
- **Feature registry commit:** `ce4de6a1a6b115673e1320524c6671394365ac7c`
- **Backlog checkpoint commit:** `6a912a49631dd843a2012130c4704cdf70fab5d2`
- **Status:** acceptance complete; bounded PR/merge/readback pending.

## Audited F2 rows

6. **Personal finance organization**.
7. **Appointments/calendar/reminders**.
8. **Administrative health organization**.

## Completed acceptance evidence

1. F6 finance is normalized as a goal/submodule-scoped `SERVICE-002` composition rather than a monolithic finance implementation claim.
2. Existing canonical finance authorities remain separate: `SPEND-001`, `PAYMENT-001`, `REIMB-001`, optional `SUB-001`, and future `FIN-001`. Budgeting, debt, savings and broad cash-flow support are not claimed from those children without their own future evidence.
3. Added `CAL-005` — evidence-safe appointment/provider identity reconciliation. Legacy provider-identity resolution/correction/ambiguity handling is directly test-verified; broader canonical appointment lifecycle and MIRA 2.0 persistence remain unverified.
4. Added `CAL-006` — idempotent linked Calendar projection/update with exact provider readback. This is strongly specified but has no dedicated audited Calendar mutation/readback implementation and therefore remains below `test_verified`/integration status.
5. F7 keeps `appointments_calendar` and `appointment_reminders` separately activatable. `appointments_calendar` maps to `CAL-005` + `CAL-006` with conditional `CAL-004`; reminder activation maps separately to `CAL-002` + `CAL-003` plus canonical appointment state.
6. Legacy `f-07` dependency on personal `CAL-001` Saturday lookahead is recorded as a semantic defect; deployment-specific Brief projection is not universal appointment-service readiness.
7. Added `HEALTH-001` — non-clinical administrative health organization. It is specification-level only and explicitly excludes diagnosis, treatment, dose/timing inference, missed-dose advice and relationship-derived caregiver access.
8. F8 keeps `health_organization`, `medication_reminders` (`REMIND-001`) and caregiver sharing (`REMIND-002` plus exact permission/recipient identity) as independent activation/permission surfaces.
9. Legacy `f-08` medication-reminder-as-health-service coupling is recorded as a semantic defect in both directions.
10. `SERVICE-002` is refined so umbrella services derive readiness only for selected goals/submodules; a working child path cannot make unsupported adjacent goals appear ready.
11. Added `AUDIT-F2`, `SERVICE-DEPS-002`, `APPOINTMENT-IDENTITY-001`, `CALENDAR-PROJECTION-001`, and `HEALTH-ADMIN-001`; refined `SERVICE-COMPOSE-001`. Existing underlying finance tasks were reused rather than duplicated.
12. `FEATURES.md` replacement was verified against the research checkpoint: one file only, 97 additions and 2 stale audit-status deletions, with the intended ID-family/refinement/F2 hunks only.
13. `BACKLOG.md` replacement was verified against the feature commit: one file only, 21 additions and 3 updated/stale lines, with only F2 audit/work/dependency findings and the intended `SERVICE-COMPOSE-001` refinement.
14. No F2 feature or service was promoted to MIRA 2.0 integration/live status from legacy deterministic subcores, workflow prose or unmerged PR #31 evidence.
15. No live Google production state was touched and no executable MIRA 2.0 product behavior changed.

## Exact next action

Compare `audit/g0-007b-finance-calendar-health-services` against `main` and verify the final packet is limited to `FEATURES.md`, `BACKLOG.md`, and `CURRENT_WORK.md`. Open a pull request to `main`, verify the server-side changed-file list and mergeability, merge with the exact PR head SHA, remotely read back the F2 feature/backlog state from `main`, then inspect the authoritative category-F ledger/dependency evidence beginning with F9 **Shopping/procurement** and activate `M2-G0-007C` from the resulting main handoff commit.

## Next packet after F2

### `M2-G0-007C` — Feature Audit Slice F3

Begin with category-F row 9 **Shopping/procurement**. Determine the rest of the bounded F3 slice from authoritative ledger/dependency evidence only after F2 is merged/read back. Do not pre-expand from conversational memory.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head when tools permit;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture new customer ideas in BACKLOG unless required for acceptance or explicitly reprioritized;
6. before the final packet line, state any customer action needed; if none is needed, use `Just tell me to continue.`;
7. the final visible line remains the packet recovery tag.
