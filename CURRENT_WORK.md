# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and its exact resume point.

## Active packet

- **Packet ID:** `M2-G0-003A`
- **Name:** Feature Audit Slice B1 — appointment/reminder safety foundations
- **Class:** forensic audit / prerequisite
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `audit/g0-003a-reminder-safety`
- **Base main SHA:** `3dcf3925b6759c6475b2912a5ad009ca233dee03`
- **Feature audit commit:** `03a59efa4edde4a0d918e32374cae7035b2a1559`
- **Backlog checkpoint commit:** `6a9dcfaf5c8208793448695acd66a8bdc422cf95`
- **Status:** acceptance work complete; PR/merge/readback pending.

## Completed acceptance evidence

1. Assigned stable semantic IDs:
   - `CAL-001` Saturday AM seven-day appointment lookahead;
   - `CAL-002` Day-before and morning-of appointment reminders;
   - `CAL-003` Configurable relative appointment reminder, default one hour before;
   - `REMIND-001` Evidence-gated medication reminders;
   - `REMIND-002` Explicit opt-in caregiver reminder sharing.
2. Added a separate `REMIND-*` family because medication safety and reminder-sharing permissions have different authority/verification boundaries from Calendar appointment state.
3. Reconciled the older ROAD-only Saturday-lookahead wording against repaired policy/tests: the current audited behavior is slot-based and mode-independent, with Saturday AM covering Saturday through Friday.
4. Verified deterministic planner tests for day-before, morning-of, one-hour-before, equal-time dedupe, cancelled/disabled suppression, at/after-start suppression, explicit service activation, named-IANA timezone handling and deterministic replay IDs.
5. Verified medication safety tests for allowed evidence sources, explicit schedule confirmation, nonempty unique schedule times, paused/disabled suppression, DST fail-closed behavior, prohibition on assistant-inferred timing and prohibition on missed-dose advice.
6. Verified caregiver sharing is default-off and recipient-required, while preserving the evidence ceiling that a unit-test recipient string does not prove real recipient identity/authorization/provider delivery.
7. Reconciled PR #31 as broad Android reminder/background candidate evidence only; it does not supersede the dedicated reminder planner or prove Calendar/notification delivery.
8. Updated `FEATURES.md` and `BACKLOG.md`; touched no live Google production state and changed no executable product behavior.

## Key audit findings

- Saturday weekly appointment lookahead is mode-independent in the repaired policy, superseding older ROAD-only wording.
- Appointment visibility/planning semantics are test-verified, but Calendar projection/readback and actual user notification delivery are separate integration/live gates.
- Medication reminders require explicit supported regimen evidence and confirmation; no personal legacy regimen data is imported for development.
- Caregiver-sharing unit tests prove the permission gate, not the human recipient. Exact identity resolution/authorization/revocation require later integration evidence.

## Blockers

None. PR/merge/readback is the remaining packet release step.

## Exact next action

Open a pull request from `audit/g0-003a-reminder-safety` to `main`, verify changed-file scope is limited to `FEATURES.md`, `BACKLOG.md`, and `CURRENT_WORK.md`, merge it, remotely read back the merged state, then update `CURRENT_WORK.md` on `main` to activate `M2-G0-003B`.

## Next packet after merge

### `M2-G0-003B` — Feature Audit Slice B2 — appointment/mail communication safety

Audit exactly category-B rows 6-10:

1. Context-aware appointment windows without exposing misleading confirmation state.
2. Important email triage across school, employer, jobs, financial, medical, vendors, fraud/security.
3. No automatic outbound email or vendor contact.
4. Archive-approval prompt using the exact user-facing question and repeat-on-silence behavior.
5. Career/job watch with realistic qualification filtering.

Do not expand this packet into orders/shipments/receipts or category C.

The exact first unaudited behavior is **Context-aware appointment windows without exposing misleading confirmation state**.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head when tools permit;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture new customer ideas in BACKLOG unless required for acceptance or explicitly reprioritized;
6. before the final packet line, state any customer action needed; if none is needed, use `Just tell me to continue.`;
7. the final visible line remains the packet recovery tag.
