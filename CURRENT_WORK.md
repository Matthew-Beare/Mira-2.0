# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and exact recovery state.

## Product direction

Default Personal MIRA is stock ChatGPT + Google Workspace with no external infrastructure prerequisite. Repeated useful no-app verticals and integrity/recovery hardening remain ahead of Android. Normal user-facing branding is **MIRA**. `MIRROR` remains an internal database/reality-layer term only when a technical database-specific context requires it.

Ordinary-user setup follows `PRODUCT_INVARIANTS.md`: the MIRA-side choice is plain-language intent, normally a simple yes/no such as **“Yes, use my calendar.”** If a provider requires authorization, the provider's unavoidable Allow/Connect consent UI is the only provider-specific ceremony. MIRA performs every setup/discovery/binding/verification step that software can safely perform. Normal users are not expected to create hidden resources, copy provider IDs, edit OAuth scopes, open Apps Script/developer consoles, paste code, run a terminal, or understand implementation mechanics.

Every work session begins and ends by checking `CURRENT_WORK.md`, `FEATURES.md`, `BACKLOG.md`, `ROADMAP.md`, and applicable cross-feature product invariants.

## Session alignment — 2026-08-31

### `FEATURES.md`

- `CAL-005` appointment/provider identity is merged/test-verified through PR #76.
- `CAL-007` provider-neutral Calendar projection is merged/test-verified through PR #77; this packet adds the default native Google implementation but does not turn CI into live-provider proof.
- `CAL-006` still requires real preferred-Calendar provider evidence before MIRA may claim Calendar sync is live for a user.
- `CAL-008` remains a separate downstream appointment-intake vertical.
- `ONBOARD-006` / `PROVIDER-002` and `PRODUCT_INVARIANTS.md` require browser-only, plain-language, no-developer-chores provider activation.

### `BACKLOG.md`

- `CALENDAR-PROJECTION-001A` is complete through PR #77.
- `CALENDAR-PROJECTION-GOOGLE-001` is the active work item for `M2-M0-023` and now has native single-writer implementation/test/release evidence.
- `CALENDAR-PROJECTION-GOOGLE-UPDATE-001` is stronger concurrent/shared-writer hardening, not a blocker for ordinary Personal single-writer use.
- Microsoft/Outlook/M365 and Apple/iCloud provider proofs remain separate downstream work.

### `ROADMAP.md`

- M2-M0.5 prioritizes ordinary-user stock-ChatGPT + Personal Google usefulness before Android.
- The Personal Google baseline explicitly accepts native same-user single-writer behavior without pretending it is distributed compare-and-swap.
- Calendar follows the same rule: native Personal lane first, stronger concurrency mechanisms later.

### Direction result

**ALIGNED.** The rejected design required **MIRA → Enable Calendar** inside the copied Sheet. The corrected default flow is ordinary-language intent → Google's own authorization UI if needed → native connected Calendar behavior. The stronger Apps Script managed-Calendar/ETag adapter remains optional hardening and test evidence, not default setup.

## Completed predecessor

### `M2-M0-022` — Provider-neutral Calendar projection core

- **Work:** `CALENDAR-PROJECTION-001A`
- **Feature:** `CAL-007`
- **PR:** #77
- **Merge/main SHA:** `fcc81f0e9d9510d05406acd9068d9ca4ee016806`
- **Post-merge main CI:** `33427385919` green
- **Evidence ceiling:** provider-neutral/synthetic only; no real Calendar provider write/readback was claimed.

## Active packet

### `M2-M0-023` — Google Calendar Personal projection lane

- **Primary work:** `CALENDAR-PROJECTION-GOOGLE-001`
- **Primary features:** `CAL-006`, `CAL-007`
- **Related invariants/features:** `RECOVERY-002`, `PROFILE-013`, `SERVICE-001`, `PROVIDER-002`, `ONBOARD-006`, `CAL-008`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `integration/m0-023-google-calendar-projection`
- **Base SHA:** `fcc81f0e9d9510d05406acd9068d9ca4ee016806`
- **PR:** #78 open
- **Last exact fully green implementation head:** `d0a3c9a2d2b1ab2de59aa2fd8fe3419907b48903`
- **CI on that head:** `33437591056` green; 351 Python tests + 30 Apps Script tests; compile, feature registry, product ledger, Personal distribution, work-session alignment, and code ownership all green.
- **Current head rule:** documentation/lifecycle corrections after that green head require one final exact-head CI before merge. Do not manufacture content-identical commits merely to record their own SHA.

### Objective

Provide the default Personal Google Calendar lane with the lowest-friction safe behavior supported by stock ChatGPT. The user expresses intent in normal conversation, for example **“Yes, use my calendar.”** If Google authorization is missing, MIRA surfaces Google's normal authorization/connection UI. After authorization, MIRA uses the connected Google Calendar capability directly, binds the selected/default authorized calendar according to policy, creates/updates only canonical MIRA-tracked projections, and performs exact provider readback.

The native connector lane is explicitly **single-writer**. It performs exact provider preflight before update, refuses to overwrite provider drift it did not create/verify, targets the exact persisted provider event ID, and performs exact post-write readback. The generic native update surface has no atomic ETag/If-Match precondition, so this lane is not represented as safe for concurrent Android/multi-client mutation. The stronger Apps Script adapter retains atomic ETag semantics for later shared-writer/hardening use.

### User-facing activation invariant

1. MIRA asks only for the user's actual intent/permission in ordinary language.
2. Provider-native consent UI is allowed when the provider itself requires it.
3. MIRA performs technical setup after consent.
4. A hidden Sheet menu, manually created secondary Calendar, copied provider ID, API console, Apps Script editor, OAuth-scope editing, terminal, or pasted code is **not** acceptable default Personal setup.
5. If a provider/runtime cannot support a safe simple lane, MIRA records the capability limitation instead of exporting engineering work to the user.

### Implemented and test-verified evidence

- `mira/google_calendar_native.py` implements the native same-user/single-writer Google Calendar adapter.
- Capability evidence labels update protection `single_writer_preflight_non_atomic`; it does not fake atomic CAS.
- New event creation writes safe material only, with no attendees, Meet link, or self-attendance side effects.
- A stable `MIRA-PROJECTION-ID:` marker supports recovery when provider creation succeeds but acknowledgement is lost.
- Identical replay reuses/re-reads the exact provider event and creates no duplicate.
- Duplicate projection markers fail closed rather than selecting one arbitrarily.
- Canonical provider event identity is preserved across updates.
- Before update, the exact persisted provider event is re-read and must match MIRA's last verified state; manual/provider drift fails closed before mutation.
- Updates target the exact event ID and require exact independent post-write readback.
- Removing the stable projection marker fails readback verification rather than silently adopting provider drift.
- The complete no-app operating instructions now encode intent-first provider activation and native Calendar semantics.
- The default Personal starter no longer requests Calendar/external-request OAuth scopes during unrelated Sheet setup.
- The default Personal release now contains five Workspace artifacts and intentionally excludes `GoogleCalendarProjection.gs`.
- `Code.gs` no longer exposes `MIRA → Enable Calendar` or `miraEnableGoogleCalendar`.
- Release validation and regression tests fail if hidden-menu Calendar activation or optional Calendar permissions creep back into the default package.
- The stronger `GoogleCalendarProjection.gs` ETag/managed-secondary-Calendar adapter remains source-controlled and its isolated Apps Script tests still pass, but it is not part of the default Personal release package.
- Exact implementation head `d0a3c9a2d2b1ab2de59aa2fd8fe3419907b48903` passed CI `33437591056` with 351 Python and 30 Apps Script tests.

### Live-provider evidence boundary

A fresh read-only Google Calendar inventory on 2026-08-31 found only:

- one read-only US holidays calendar;
- the user's Family calendar, writable but protected production state;
- the user's Primary calendar, writable but protected production state.

No isolated synthetic writable Calendar is currently available through the connected Calendar surface. The connector exposes event create/read/update actions but no secondary-Calendar creation action. Primary/Family calendars are therefore **not** used as development fixtures.

Consequently:

- native Google implementation: **implemented**;
- direct/release/CI verification: **verified**;
- live Calendar provider write/readback: **not verified**;
- reason: no isolated writable Calendar target is available through current authorized tools;
- response: preserve the evidence ceiling and do not degrade ordinary-user setup or write test events into protected calendars merely to manufacture a live checkbox.

### Acceptance criteria status

1. `PRODUCT_INVARIANTS.md` intent-first activation rule preserved: **met**.
2. Default Personal activation requires only plain-language consent + provider UI when needed: **met in product/release contract; live consent ceremony not re-enacted**.
3. No mandatory manual Calendar/developer setup: **met**.
4. Native lane explicitly same-user/single-writer/non-CAS: **met**.
5. Create records exact provider identity and requires exact readback: **implemented/test-verified; live provider proof pending isolated target**.
6. Replay cannot duplicate provider event: **implemented/test-verified**.
7. Update preflight rejects provider/manual drift: **implemented/test-verified**.
8. Update targets exact event and requires exact post-write readback; no atomic ETag claim: **implemented/test-verified**.
9. Strong Apps Script `If-Match` lane preserved as optional hardening: **met**.
10. Primary/Family/legacy Calendars not used as dev fixtures: **met**.
11. Direct tests cover create/replay/drift/update/readback/capability labeling: **met**.
12. No-app/release guards prevent hidden-menu/developer-style regression: **met**.
13. Exact final PR-head CI, expected-head merge, remote-main readback, post-merge CI: **pending final lifecycle-doc commit(s)**.
14. Live-provider completion claimed only at proven level: **met; live write remains unverified**.

### Evidence state

- **Desired:** yes
- **Specified:** yes, corrected by explicit user acceptance feedback on 2026-08-31
- **Default native Personal lane implemented:** yes
- **Default native Personal lane test-verified:** yes
- **Default Personal release contract verified:** yes
- **Strong Apps Script lane implemented/test-verified:** yes, optional hardening only
- **Live-provider write verified:** no; isolated writable Calendar unavailable

## Exact next action / resume point

1. Reconcile `BACKLOG.md` so `CALENDAR-PROJECTION-GOOGLE-001` records native implementation/test/release evidence and `CALENDAR-PROJECTION-GOOGLE-UPDATE-001` is HARDENING rather than a default-Personal blocker.
2. Rewrite PR #78 description/title to the corrected native intent-first architecture and explicit live-evidence ceiling.
3. Re-read PR head and run one exact-final-head CI after lifecycle/documentation commits.
4. Merge PR #78 with `expected_head_sha` protection only if exact-head CI is green.
5. Verify remote `main` contains the merged changes and inspect post-merge CI.
6. Preserve live Google write/readback as pending evidence until an isolated writable Calendar can be provisioned through supported software/provider flow; do not use Primary/Family as test fixtures.
7. Do not expand into Microsoft/Apple Calendar, appointment intake, reminders, outbound contact, medical meaning, migration, or Android during this packet.

## Recovery protocol

Read this file and `PRODUCT_INVARIANTS.md` first. Confirm PR #78 and branch `integration/m0-023-google-calendar-projection`. Treat intent-first ordinary-user activation as highest-authority product acceptance feedback. M2-M0-022 remains complete. The native default Personal Google lane is implemented/test-verified, but real provider Calendar write/readback is not yet live-verified because no isolated writable Calendar is visible. Protected Primary/Family/legacy Calendar state remains unavailable as a development fixture.
