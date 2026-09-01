# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and exact recovery state.

## Product direction

Default Personal MIRA is stock ChatGPT + Google Workspace with no external infrastructure prerequisite. Repeated useful no-app verticals and integrity/recovery hardening remain ahead of Android. Normal user-facing branding is **MIRA**. `MIRROR` remains an internal database/reality-layer term only when a technical database-specific context requires it.

Ordinary-user setup follows `PRODUCT_INVARIANTS.md`: users state intent in ordinary language, provider-native authorization is the only unavoidable provider ceremony, and MIRA performs technical setup when software can safely do it. Provider capability/readback evidence, service activation, source evidence, and canonical state remain separate truths.

Every work session begins and ends by checking `CURRENT_WORK.md`, `FEATURES.md`, `BACKLOG.md`, `ROADMAP.md`, and applicable cross-feature product invariants.

## Session-start alignment verification — 2026-08-31

### `FEATURES.md`

- `CAL-005` appointment/provider identity reconciliation is merged/test-verified and remains the canonical identity authority.
- `CAL-008` requires multi-source appointment evidence intake from email, image/photo, or text with provenance, confidence/ambiguity handling, dedupe, and canonical reconciliation.
- `CAL-006`/`CAL-007` provide projection semantics, but real Google Calendar event write/readback remains a separate live-evidence boundary.
- `MAIL-002` continues to prohibit outbound provider contact without explicit per-message approval.

### `BACKLOG.md`

- `APPOINTMENT-INTAKE-001` is active in this packet and its provider-neutral implementation is now test-verified.
- `CALENDAR-PROJECTION-GOOGLE-001` is merged/test-verified at the native implementation layer but remains partial at live provider-write evidence.
- Gmail fetching, image/model extraction infrastructure, reminders, Microsoft/Apple Calendar, outbound contact, and Android remain separate work.

### `ROADMAP.md`

- M2-M0.5 prioritizes useful ordinary-user Personal MIRA verticals before Android.
- Appointment intake composes existing identity and projection foundations without making source extraction or provider state into new authorities.
- CI/synthetic proof must not be presented as real provider/source integration proof.

### Direction result

**ALIGNED.** Complete the provider-neutral appointment evidence intake/reconciliation core at its actual evidence level, then merge only after final exact-head CI. Do not expand into provider-specific source ingestion or live Calendar mutation during this packet.

## Completed predecessor

### `M2-M0-023` — Google Calendar Personal projection lane

- **Work:** `CALENDAR-PROJECTION-GOOGLE-001`
- **Features:** `CAL-006`, `CAL-007`
- **PR:** #78
- **Final PR head:** `9f553fe9dee62a1692b703739b0679bae05cc689`
- **Final exact-head CI:** `33438175307` green
- **Merge/main SHA:** `b1d7a4f20ebad3503a3c518ec568c47498e85d42`
- **Post-merge main CI:** `33438237335` green
- **Evidence ceiling:** native Personal Calendar implementation/release contract test-verified; live event write/readback not verified because no isolated writable Calendar was available and protected Primary/Family state was not used as a fixture.

## Active packet

### `M2-M0-024` — Appointment evidence intake/reconciliation core

- **Primary work:** `APPOINTMENT-INTAKE-001`
- **Primary features:** `CAL-008`
- **Related invariants/features:** `CAL-005`, `RECOVERY-002`, `CAL-006`, `CAL-007`, `SERVICE-001`, `MAIL-002`, `PROFILE-013`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `integration/m0-024-appointment-intake`
- **Base SHA:** `b1d7a4f20ebad3503a3c518ec568c47498e85d42`
- **PR:** #79 open
- **Exact green implementation head:** `5992a57db91697decc5e95d20ecd76df3adc3eec`
- **CI on that head:** `33457016348` green
- **Verification count:** 366 Python tests + 30 Workspace Apps Script tests passed; compile, feature registry, product lifecycle ledger, Personal distribution, work-session alignment, and code ownership all green.
- **Current head rule:** lifecycle/documentation commits after `5992a57d...` require one final exact-head CI before merge. Merge must use expected-head protection.

### Objective

Implement the bounded provider-neutral intake core that turns authorized appointment evidence into deterministic canonical provider/appointment reconciliation without making source ingestion, model extraction, or Calendar projection into new authorities.

The packet accepts evidence observations from the three `CAL-008` source classes (`email`, `image`, `text`) plus a structured extraction result. It validates provenance, immutable material fingerprint, offset-aware observation time, normalized facts and field confidence; refuses low-confidence or materially incomplete occurrence identity; reconciles through `AppointmentIdentityService`; surfaces explicit Needs Review reasons; and optionally hands an already-canonical appointment to Calendar projection only when explicit service/capability state permits it.

### Implemented and test-verified evidence

- `mira/appointment_intake.py` implements provider-neutral email/image/text evidence intake over structured extracted facts.
- Accepted source classes are explicit; source reference, SHA-256 material fingerprint, observation timestamp, authority, and per-field confidence are validated.
- Deterministic confidence thresholds are 0.90 for identity/timing and 0.80 for optional descriptive metadata; explicit user-confirmed evidence remains highest authority through `CAL-005`.
- Provider exact identity is preflighted before mutation; provider ambiguity blocks appointment mutation.
- Appointment occurrence identity is preflighted before mutation; ambiguity becomes Needs Review rather than guessed state.
- Exact replay does not grow canonical revisions; same source identity with different material fails closed.
- Canonical appointments now optionally preserve exact `end_at` and IANA `timezone`, because Calendar projection requires a bounded interval. Existing legacy appointment payloads without those fields remain readable.
- Timing validation rejects end-before-start and timezone/offset mismatch.
- Calendar projection is downstream only when appointment service state is effectively active and a verified projection dependency is supplied. Missing/inactive/failed projection never discards reconciled canonical appointment truth.
- Synthetic projection tests prove exact canonical timing handoff without claiming live Calendar provider verification.
- No attendees, Meet creation, reminders, medication/medical inference, or outbound contact is introduced.

### Integrity defect discovered and fixed

The packet exposed an existing `CAL-005` self-collision defect in appointment identity matching. `_matching_views` previously preferred `provider_id` when an `AppointmentView` contains both `provider_id` and `appointment_id`; user-confirmed correction of an existing appointment at the same start time therefore failed to exclude the appointment itself and falsely returned Needs Review.

The matcher now uses `appointment_id` for appointment rows and falls back to `provider_id` only for provider rows. Direct regression test `test_user_confirmed_same_start_correction_does_not_collide_with_itself` passed in CI `33457016348` together with the intake correction test that originally exposed the bug.

### Acceptance criteria status

1. Email/image/text source classes + provenance fingerprint/time without copying raw source bodies: **met/test-verified**.
2. Structured extraction contract for provider/appointment fields + confidence/authority: **met/test-verified**.
3. Deterministic essential identity before mutation; missing/low-confidence essentials -> Needs Review: **met/test-verified**.
4. Explicit confidence thresholds; low-confidence optional fields omitted: **met/test-verified**.
5. Provider-first reconciliation and ambiguity stop: **met/test-verified**.
6. Appointment reconciliation only after provider success; ambiguity fail-closed: **met/test-verified**.
7. Exact replay zero revision growth; conflicting source material fail-closed: **met/test-verified**.
8. User-confirmed correction precedence: **met/test-verified**, including self-collision regression repair.
9. Intake result separates canonical/Needs Review/projection state: **met/test-verified**.
10. Calendar projection only for effectively active service + verified dependency: **met/test-verified with synthetic adapter**.
11. Projection absence/failure preserves canonical appointment: **met/test-verified**.
12. No attendee/Meet/reminder/medical/outbound-contact expansion: **met**.
13. Direct source/replay/confidence/ambiguity/conflict/correction/service/projection tests: **met**.
14. Production ownership and repository alignment gates: **met on implementation head**.
15. Final exact-head CI, expected-head merge, remote-main readback, post-merge CI: **pending lifecycle-doc final head**.

### Evidence state

- **Desired:** yes
- **Specified:** yes
- **Implemented:** yes
- **Test-verified:** yes, PR #79 implementation head `5992a57db91697decc5e95d20ecd76df3adc3eec`, CI `33457016348`
- **Integration-verified:** limited to provider-neutral canonical identity + service-state + synthetic Calendar projection composition in the repository test harness; no Gmail/image-model/live provider integration is claimed
- **Live-verified:** no

### Explicit evidence ceiling / deferred related work

- No Gmail search/fetch or mailbox-to-extraction provider integration was implemented or verified.
- No OCR/image-understanding/model extraction runtime was implemented or verified.
- No real Google/Microsoft/Apple Calendar event mutation was performed in this packet.
- No reminder delivery, outbound provider contact, medical interpretation, migration, or Android behavior is included.
- Protected Primary/Family/legacy Calendar state remains unavailable as development fixtures.

## Exact next action / resume point

1. Update PR #79 description with the green implementation evidence, `CAL-005` self-collision repair, and explicit provider/source evidence ceiling.
2. Re-read the exact PR head after this lifecycle checkpoint and require one final exact-head CI.
3. Fix only packet-local failures if any final gate regresses.
4. Merge PR #79 with `expected_head_sha` only when final exact-head CI is green.
5. Verify remote `main` contains the merged source and verify post-merge `main` CI.
6. After merge evidence exists, create a bounded Git-backed packet-closure checkpoint so `CURRENT_WORK` records the actual merge SHA/post-merge CI before selecting new implementation scope.
7. Do not expand into Gmail fetching, image/model infrastructure, Microsoft/Apple Calendar, reminders, outbound contact, medical meaning, migration, or Android during this packet.

## Recovery protocol

Read this file first, then `FEATURES.md`, `BACKLOG.md`, `ROADMAP.md`, and `PRODUCT_INVARIANTS.md`. Confirm PR #79 and branch `integration/m0-024-appointment-intake`. Treat `CAL-005` as canonical appointment/provider identity authority. The provider-neutral intake implementation is test-verified; source-provider ingestion and real Calendar provider mutation remain unverified external integration layers. Continue only from the exact next action above.
