# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and exact recovery state.

## Product direction

Default Personal MIRA is stock ChatGPT + Google Workspace with no external infrastructure prerequisite. Repeated useful no-app verticals and integrity/recovery hardening remain ahead of Android. Normal user-facing branding is **MIRA**. `MIRROR` remains an internal database/reality-layer term only when a technical database-specific context requires it.

Ordinary-user setup follows `PRODUCT_INVARIANTS.md`: users state what they want in ordinary language, provider-native authorization is the only unavoidable provider ceremony, and MIRA performs technical setup when software can do it safely. Provider capability/readback evidence and service activation remain separate truths.

Every work session begins and ends by checking `CURRENT_WORK.md`, `FEATURES.md`, `BACKLOG.md`, `ROADMAP.md`, and applicable cross-feature product invariants.

## Session-start alignment verification — 2026-08-31

### `FEATURES.md`

- `CAL-005` appointment/provider identity reconciliation is merged/test-verified and already accepts normalized provenance-bound evidence.
- `CAL-008` explicitly requires multi-source appointment evidence intake from inbound email, user-supplied image/photo, or user text, with provenance, confidence/ambiguity handling, dedupe, and canonical appointment/provider reconciliation. Its universal dependencies are `CAL-005` and `RECOVERY-002`.
- `CAL-006` remains specified/requirement-refined. The default native Google lane is implemented/test-verified, but real provider event write/readback is not yet live-verified because no isolated writable Calendar target is available.
- `MAIL-002` still requires explicit per-message approval for outbound provider communication. Appointment intake does not imply permission to email or negotiate with a provider.

### `BACKLOG.md`

- `APPOINTMENT-INTAKE-001` is the highest-value queued user-visible appointment vertical now that provider-neutral identity and a default native Google projection implementation exist.
- `CALENDAR-PROJECTION-GOOGLE-001` is partial only at the live-provider evidence layer; its native implementation/test/release contract is merged.
- `CALENDAR-PROJECTION-GOOGLE-UPDATE-001` is HARDENING for concurrent/shared writers, not a blocker for this intake core.
- Microsoft/Outlook/M365, Apple/iCloud, reminders, outbound contact, and Android remain separate work.

### `ROADMAP.md`

- M2-M0.5 prioritizes useful ordinary-user Personal MIRA verticals before Android.
- Appointment intake is a direct user-visible composition over already-built identity/projection foundations.
- Provider-specific extraction/connectors and live Calendar activation evidence must not be faked by unit-test success.

### Direction result

**ALIGNED.** Start the appointment evidence intake/reconciliation core. The packet may define and test a provider-neutral extraction-result contract for email/image/text evidence, but it must not silently claim Gmail parsing, OCR/model extraction, live Calendar mutation, reminder delivery, or outbound provider contact that has not been independently verified.

## Completed predecessor

### `M2-M0-023` — Google Calendar Personal projection lane

- **Work:** `CALENDAR-PROJECTION-GOOGLE-001`
- **Features:** `CAL-006`, `CAL-007`
- **PR:** #78
- **Final PR head:** `9f553fe9dee62a1692b703739b0679bae05cc689`
- **Final exact-head CI:** `33438175307` green
- **Merge/main SHA:** `b1d7a4f20ebad3503a3c518ec568c47498e85d42`
- **Post-merge main CI:** `33438237335` green
- **Evidence:** default native Personal Google Calendar adapter/release contract implemented and test-verified; 351 Python + 30 Apps Script tests green on the implementation branch; intent-first activation invariant merged; atomic ETag path demoted to shared-writer hardening.
- **Live evidence ceiling:** no isolated writable Calendar is visible through the connected provider surface, so no live event write/readback was performed against protected Primary/Family state. `CAL-006` is not represented as live-provider verified.

## Active packet

### `M2-M0-024` — Appointment evidence intake/reconciliation core

- **Primary work:** `APPOINTMENT-INTAKE-001`
- **Primary feature:** `CAL-008`
- **Related features/invariants:** `CAL-005`, `RECOVERY-002`, `CAL-006`, `CAL-007`, `SERVICE-001`, `MAIL-002`, `PROFILE-013`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `integration/m0-024-appointment-intake`
- **Base SHA:** `b1d7a4f20ebad3503a3c518ec568c47498e85d42`
- **Current head before packet checkpoint commit:** `b1d7a4f20ebad3503a3c518ec568c47498e85d42`
- **PR:** not opened yet

### Objective

Implement the bounded provider-neutral intake core that turns authorized appointment evidence into deterministic canonical provider/appointment reconciliation without making source ingestion or Calendar projection into new authorities.

This packet accepts evidence observations from the three `CAL-008` source classes (`email`, `image`, `text`) plus a structured extraction result produced by the connected MIRA runtime or a later provider-specific extractor. The core validates provenance, material fingerprint, timestamps, normalized facts and confidence; refuses low-confidence or materially incomplete occurrence identity; reconciles through the existing `AppointmentIdentityService`; exposes explicit Needs Review reasons; and optionally hands an already-canonical appointment to Calendar projection only when explicit service/capability state permits it.

The packet does **not** implement Gmail search/fetch, OCR/image understanding, a new LLM/API extraction runtime, provider scheduling/negotiation, reminder delivery, or live Calendar-provider proof. Those remain separate integration/evidence layers.

### Acceptance criteria

1. Accept exactly the authorized source classes `email`, `image`, and `text`; retain stable source reference/fingerprint and offset-aware observation time without copying raw source bodies/images into canonical structured state.
2. Define a structured extraction-result contract for provider name/organization/contact/specialty, appointment date-time/timezone/location/type/title, optional explicit provider/appointment identity, and per-field confidence/evidence authority.
3. Essential occurrence identity must be deterministic before mutation: provider evidence must have an exact identity key supported by `CAL-005`, and appointment occurrence must have an exact start time or explicit occurrence identity. Missing/low-confidence essential fields return `needs_review` rather than guessing.
4. Confidence thresholds are explicit and deterministic; low-confidence optional fields may be omitted rather than promoted to canonical truth.
5. Reconcile provider first through `AppointmentIdentityService`; provider ambiguity/conflict stops appointment mutation and surfaces exact candidate IDs/reason.
6. Reconcile appointment only after provider reconciliation succeeds; appointment ambiguity/conflict surfaces Needs Review and never invents one of several plausible occurrences.
7. Exact evidence replay with materially identical extraction performs no additional canonical revision; same source fingerprint/reference with conflicting material must not silently overwrite canonical truth.
8. User-confirmed corrections continue to outrank lower-authority source/derived facts through the existing `CAL-005` authority rules.
9. Intake result clearly separates: captured/reconciled canonical state, Needs Review state, and Calendar projection state.
10. Calendar projection is attempted only when explicit appointment service state is effectively active and a verified projection dependency is supplied. Requested/disabled/unavailable/suspended service state must not become an event write.
11. Failure or absence of Calendar capability never discards successfully reconciled canonical appointment truth; projection is a downstream side effect with its own evidence status.
12. No attendee notifications, Meet creation, reminder scheduling, medication/medical inference, or outbound email/contact is introduced.
13. Direct tests cover each source class, successful create, exact replay, low-confidence/missing essentials, provider ambiguity, appointment ambiguity, conflicting source replay, user-confirmed precedence boundary, inactive service projection suppression, and active-service projection handoff using synthetic provider adapters only.
14. Add production ownership/direct-test evidence and preserve release/work-session alignment gates.
15. Exact final PR-head CI, expected-head merge protection, remote-main readback, and post-merge CI are required before packet completion.

### Evidence state

- **Desired:** yes
- **Specified:** yes in `CAL-008` / `APPOINTMENT-INTAKE-001`
- **Implemented:** no
- **Test-verified:** no
- **Integration-verified:** no
- **Live-verified:** no

## Exact next action / resume point

1. Inspect `mira/appointments.py`, `mira/service_state.py`, `mira/calendar_projection.py`, receipt/evidence patterns, package exports, and code-ownership rules.
2. Implement the smallest `mira/appointment_intake.py` orchestration contract satisfying the acceptance criteria without duplicating `CAL-005` identity logic.
3. Add direct synthetic tests before any provider connector work.
4. Register production ownership/test evidence and run all repository gates.
5. Open a bounded PR only after local/source gates are green.
6. Do not expand into Gmail provider fetching, OCR/model infrastructure, Microsoft/Apple Calendar, reminders, outbound contact, medical meaning, migration, or Android during this packet.

## Recovery protocol

Read this file first, then `FEATURES.md`, `BACKLOG.md`, `ROADMAP.md`, and `PRODUCT_INVARIANTS.md`. Confirm branch `integration/m0-024-appointment-intake` is based on merged `main` SHA `b1d7a4f20ebad3503a3c518ec568c47498e85d42`. Treat `CAL-005` as the canonical identity/reconciliation authority and keep source extraction, service activation, Calendar projection, reminders, and outbound contact as separate capability/evidence boundaries.
