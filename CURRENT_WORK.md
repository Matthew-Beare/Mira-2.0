# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and its exact resume point.

## Completed packet

### `M2-G0-002D` — Feature Audit Slice A4 — failure isolation and Slice-A closure

- **Merged PR:** #4
- **Merge SHA:** `0f4f2f9a304df5379bfa477076ed7fb7f61202fd`
- **Audited feature:** `RECOVERY-002`
- **Result:** category A is complete and internally reconciled.
- **Live Google production touched:** no.
- **Executable product behavior changed:** no.

## Active packet

- **Packet ID:** `M2-G0-003A`
- **Name:** Feature Audit Slice B1 — appointment/reminder safety foundations
- **Class:** forensic audit / prerequisite
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `audit/g0-003a-reminder-safety`
- **Base audit-state SHA:** `0f4f2f9a304df5379bfa477076ed7fb7f61202fd`
- **Objective:** Audit the first bounded calendar/reminder safety behaviors as stable feature records, preserving safety/evidence boundaries and separating deterministic planning from live Calendar/provider proof.

## Audit rows in this packet

Audit exactly category-B rows 1-5:

1. Saturday 2:45 AM ROAD appointment lookahead for the next week.
2. Appointment reminder day before and morning of.
3. Appointment reminder one hour before.
4. Medication reminders only from explicit owner, prescription-label, pharmacy, or clinician evidence.
5. Caregiver reminder sharing with explicit opt-in and exact recipient identity.

Do not expand this packet to important-mail triage, auto-email rules, archive approval or job-watch behavior.

## Acceptance criteria

1. Each scoped behavior receives a stable MIRA 2.0 semantic feature ID and complete feature record.
2. Appointment-window behavior, reminder planning, medication evidence rules and caregiver-sharing permission remain separate where their safety/verification boundaries differ.
3. Requirement status is separated from implementation/test/integration/live evidence.
4. Relevant legacy planner/policy/tests are inspected and materially relevant PR #31 evidence reconciled without promotion-by-association.
5. Live Calendar projection/readback is not claimed from deterministic tests.
6. No medication dose/schedule is inferred and no caregiver sharing is treated as enabled from historical data.
7. `FEATURES.md`, `BACKLOG.md`, and `CURRENT_WORK.md` are the only intended changed files.
8. A small PR is scope-verified, merged, and remotely read back.
9. `CURRENT_WORK.md` advances to the next exact category-B audit behavior.
10. No live Google production state and no executable product behavior is changed.

## Exact next action

Create/confirm branch `audit/g0-003a-reminder-safety`. Inspect the legacy appointment-window and reminder-planner policy/tests for category-B row 1: **Saturday 2:45 AM ROAD appointment lookahead for the next week**. Assign the stable feature ID and record its evidence boundary before moving to row 2.

## Next packet boundary

If `M2-G0-003A` completes, `M2-G0-003B` begins with category-B row 6: **Context-aware appointment windows without exposing misleading confirmation state**, followed by the scoped mail/communication-safety rows through row 10.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head when tools permit;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture new customer ideas in BACKLOG unless required for acceptance or explicitly reprioritized;
6. before the final packet line, state any customer action needed; if none is needed, use `Just tell me to continue.`;
7. the final visible line remains the packet recovery tag.
