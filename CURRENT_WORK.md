# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and its exact resume point.

## Completed packet

### `M2-G0-003A` — Feature Audit Slice B1 — appointment/reminder safety foundations

- **Merged PR:** #5
- **Merge SHA:** `8cad56b311cdbe7c6e6157044afc9f83779f6e97`
- **Audited features:** `CAL-001`, `CAL-002`, `CAL-003`, `REMIND-001`, `REMIND-002`
- **Live Google production touched:** no.
- **Executable product behavior changed:** no.

## Active packet

- **Packet ID:** `M2-G0-003B`
- **Name:** Feature Audit Slice B2 — appointment/mail communication safety
- **Class:** forensic audit / prerequisite
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `audit/g0-003b-appointment-mail-safety`
- **Base audit-state SHA:** `8cad56b311cdbe7c6e6157044afc9f83779f6e97`
- **Objective:** Audit the remaining category-B appointment/mail/communication-safety behaviors as stable feature records without importing private email/calendar data or changing executable behavior.

## Audit rows in this packet

Audit exactly category-B rows 6-10:

1. Context-aware appointment windows without exposing misleading confirmation state.
2. Important email triage across school, employer, jobs, financial, medical, vendors, fraud/security.
3. No automatic outbound email or vendor contact.
4. Archive-approval prompt using the exact user-facing question and repeat-on-silence behavior.
5. Career/job watch with realistic qualification filtering.

Do not expand this packet into orders/shipments/receipts or category C.

## Acceptance criteria

1. Each scoped behavior receives a stable semantic feature ID and complete feature record.
2. Appointment visibility/state semantics remain separate from reminder planning and from hidden confirmation/anti-nag state.
3. Mail triage, outbound-contact authorization, archive approval, and career watch remain distinct where permissions/defaults differ.
4. Requirement status is separated from implementation/test/integration/live evidence.
5. Relevant legacy policy/reference/test evidence is inspected without copying live email/calendar content into the public repo.
6. No automatic outbound email/contact behavior is weakened during normalization.
7. Archive silence never becomes approval; exact user-facing approval wording is preserved when still current.
8. Career/job watch remains optional/personal, uses realistic qualification filtering, and does not become a universal default or separate duplicate scheduler.
9. `FEATURES.md`, `BACKLOG.md`, and `CURRENT_WORK.md` are the only intended changed files.
10. A small PR is scope-verified, merged, and remotely read back.
11. `CURRENT_WORK.md` advances to the first bounded category-C packet before completion.
12. No live Google production state and no executable product behavior is changed.

## Exact next action

Create/confirm branch `audit/g0-003b-appointment-mail-safety`. Inspect the legacy appointment-window/confirmation-state policy for row 6: **Context-aware appointment windows without exposing misleading confirmation state**. Assign its stable feature ID and evidence boundary before moving to mail triage.

## Next packet boundary

After B2 completes, size category C into bounded packets before auditing orders/shipments/receipts/payments/spending. Do not assume category C fits one session merely because humans enjoy repeating mistakes.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head when tools permit;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture new customer ideas in BACKLOG unless required for acceptance or explicitly reprioritized;
6. before the final packet line, state any customer action needed; if none is needed, use `Just tell me to continue.`;
7. the final visible line remains the packet recovery tag.
