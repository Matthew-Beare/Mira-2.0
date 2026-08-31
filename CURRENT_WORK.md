# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and exact recovery state.

## Product direction

Default Personal MIRA is stock ChatGPT + Google Workspace with no external infrastructure prerequisite. Repeated useful no-app verticals and integrity/recovery hardening remain ahead of Android. Normal user-facing branding is **MIRA**. `MIRROR` remains an internal database/reality-layer term only when a technical database-specific context requires it.

Ordinary-user setup must not expose developer chores when MIRA can perform them safely. Calendar activation therefore defaults to one explicit user action that lets MIRA create/recover its own secondary Google Calendar; users are not expected to create test calendars, copy provider IDs, edit OAuth scopes, or understand Calendar API mechanics.

Every work session begins and ends by checking `CURRENT_WORK.md`, `FEATURES.md`, `BACKLOG.md`, and `ROADMAP.md`.

## Session-start alignment verification — 2026-08-31

### `FEATURES.md`

- `CAL-005` appointment/provider identity is merged/test-verified through PR #76.
- `CAL-007` provider-neutral Calendar projection is merged/test-verified through PR #77 with synthetic provider readback only.
- `CAL-006` still requires one real preferred-Calendar lane before MIRA may claim Calendar sync is live.
- `CAL-008` remains the intended user-visible appointment-intake vertical after one default Personal Calendar lane is live-verified.

### `BACKLOG.md`

- `CALENDAR-PROJECTION-001A` is complete through PR #77.
- `CALENDAR-PROJECTION-GOOGLE-001` remains the single active provider-lane prerequisite in M2-M0-023.
- User acceptance feedback exposed manual secondary-calendar creation as unacceptable ordinary-user setup. The active packet now includes automatic MIRA-owned Calendar bootstrap because it is required to satisfy the existing no-app usability and protected-production-data acceptance boundary.
- Microsoft/Outlook/M365 and Apple/iCloud provider proofs remain separate downstream work and are not implied by this packet.
- `APPOINTMENT-INTAKE-001` remains queued behind a live-verified preferred Calendar lane.

### `ROADMAP.md`

- M2-M0.5 continues to prioritize stock-ChatGPT + Personal Google usefulness before Android.
- A safe, ordinary-user Google Calendar lane remains the shortest hard prerequisite between the merged projection core and the appointment-intake vertical.
- Protected personal/legacy provider state is not an acceptable substitute for isolated development evidence.
- Browser-first means Calendar setup must not require terminal commands, manual API setup, copied Calendar IDs, or hidden developer fixtures.

### Direction result

**ALIGNED.** Continue the bounded Google Calendar adapter/readback packet with one-click MIRA-owned Calendar bootstrap. Preserve the evidence ceiling: implemented/test-verified does not equal live-verified, and Primary/Family Calendars remain unavailable as development fixtures.

## Completed predecessor

### `M2-M0-022` — Provider-neutral Calendar projection core

- **Work:** `CALENDAR-PROJECTION-001A`
- **Feature:** `CAL-007`
- **PR:** #77
- **Final PR head:** `ec6fe091bfa68cabce5450e9974ff5337ae55800`
- **Exact-head CI:** `33427269214` green
- **Merge/main SHA:** `fcc81f0e9d9510d05406acd9068d9ca4ee016806`
- **Post-merge main CI:** `33427385919` green
- **Evidence ceiling:** provider-neutral/synthetic only; no real Calendar provider write/readback was claimed.

## Active packet

### `M2-M0-023` — Google Calendar projection adapter/readback

- **Primary work:** `CALENDAR-PROJECTION-GOOGLE-001`
- **Primary features:** `CAL-006`, `CAL-007`
- **Related invariants/features:** `RECOVERY-002`, `PROFILE-013`, `SERVICE-001`, `PROVIDER-002`, `CAL-008`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `integration/m0-023-google-calendar-projection`
- **Base SHA:** `fcc81f0e9d9510d05406acd9068d9ca4ee016806`
- **PR:** #78 open, non-draft
- **Last fully verified implementation/release head before this governance checkpoint:** `3691c357e71cba325e6203edca189da52f7daeb2`
- **Exact-head CI:** `33432595617` green on `3691c357e71cba325e6203edca189da52f7daeb2`
- **Current head rule:** this file is a governance checkpoint. Re-read PR #78 after this commit and require green CI on the new exact live head before any merge decision.

### Objective

Provide a browser-first Google Calendar provider lane that satisfies the merged provider-neutral projection contract without Cloud Run/Linux/SQL/terminal infrastructure. After explicit Calendar opt-in, ordinary users choose **MIRA → Enable Calendar** once; MIRA creates or safely recovers its own dedicated secondary Google Calendar, then uses stable projection identity, replay recovery, guarded ETag updates and exact provider readback. Live verification must use MIRA-owned isolated provider state, never Primary/Family/legacy Calendar data as a development fixture.

### Implemented/test-verified evidence

- `mira/calendar_projection.py` treats provider version material as opaque tokens, preserving exact equality/precondition semantics for real Google ETags. Calendar projection schema is v2 and direct synthetic tests use opaque `memory:N` tokens.
- `workspace/apps_script/GoogleCalendarProjection.gs` implements the Google Calendar REST adapter through bound Apps Script user OAuth, with no external server prerequisite.
- `miraEnsureGoogleCalendar_()` creates a dedicated secondary Calendar named `MIRA` after explicit opt-in instead of requiring manual Calendar creation.
- Calendar bootstrap stores a local installation UUID **before** provider creation and stamps it into the MIRA Calendar description. If the create acknowledgement is lost before its Calendar ID is persisted, read-only CalendarList recovery finds the unique matching installation marker rather than creating a duplicate.
- If a previously persisted MIRA Calendar ID is later missing or its ownership marker/name changed, the adapter fails closed rather than silently replacing user-visible state.
- The manifest uses `calendar.app.created` plus `calendar.calendarlist.readonly`, allowing MIRA to create/manage events on calendars it created while avoiding blanket event access across all user calendars. Broad `calendar`, `calendar.events`, and `calendar.calendars` scopes are rejected by the release validator.
- `Code.gs` exposes `MIRA → Enable Calendar` and uses MIRA-only user-facing branding in initialization messaging.
- Google events carry private extended properties for MIRA projection identity/idempotency material so lost event-create acknowledgements can be recovered without duplicate logical projection creation.
- Existing projected-event updates use the exact previously read Google ETag through `If-Match`; stale provider state fails closed rather than being silently overwritten.
- Create/update acknowledgement is followed by independent exact event GET/readback before success is returned.
- Provider errors distinguish validation, authorization/capability, conflict, not-found and readback failures.
- The adapter creates no attendees, sends no attendee updates, creates no Meet links, and does not implement reminders, appointment extraction, Microsoft/Apple support, or medical behavior.
- `mira/workspace_bundle.py` validates the one-click menu, managed-calendar bootstrap/recovery markers, guarded ETag behavior, exact-readback markers and narrow OAuth scopes.
- `tests/apps_script/google_calendar_projection.test.js` covers managed-calendar create, repeat setup, lost-create-ack recovery, ambiguous ownership markers, user-deleted/missing managed Calendar behavior, event create/replay, guarded update, stale ETag, authorization failure, duplicate projection identity and readback mismatch.
- `tests/apps_script/workspace_read.test.js` locks the `Enable Calendar` menu entry and MIRA-only initialization wording into the browser-first contract.
- `distribution/personal_google_starter.json`, `mira/personal_distribution.py` and `tests/test_personal_distribution.py` ship/hash/verify `GoogleCalendarProjection.gs` as the sixth deterministic Workspace artifact.
- CI `33432595617` passed compile, feature registry, product lifecycle ledger, Personal starter distribution, work-session alignment, code ownership, 343 Python tests and all Workspace Apps Script tests on head `3691c357e71cba325e6203edca189da52f7daeb2`.
- No real Calendar provider mutation has been performed by this packet.

### Live-provider blocker

The currently connected ChatGPT Calendar integration exposes event operations and calendar listing but no secondary-calendar creation action. The connected Drive surface exposes no action to deploy or execute the branch's bound Apps Script code. Therefore this chat runtime cannot execute the newly implemented `MIRA → Enable Calendar` bootstrap against a fresh provider target by itself.

This is now a **live deployment/execution evidence blocker**, not an ordinary-user product-flow blocker and not a code/test failure. The shipped Personal flow no longer asks users to create a Calendar, copy IDs, or configure provider internals. Primary and Family remain protected and must not be used as development fixtures merely to manufacture live evidence.

## Acceptance criteria

1. Google adapter preserves existing canonical projection identity semantics.
2. After explicit Calendar opt-in, ordinary-user setup requires at most one MIRA Calendar enable action plus Google's required authorization UI; no manual Calendar creation/provider-ID/API configuration is required.
3. MIRA-owned Calendar bootstrap is recovery-safe against lost create acknowledgement and fails closed on ambiguous ownership or explicit later deletion/drift.
4. Default OAuth permissions use app-created Calendar ownership plus read-only CalendarList recovery rather than blanket access to every Calendar event.
5. Create writes exact normalized timed-event material and retains exact provider event identity/version evidence.
6. Update targets the exact projected event and uses atomic provider-version/ETag precondition evidence.
7. Identical logical replay cannot create a second managed Calendar or logical projection/event.
8. One idempotency key cannot silently represent different event material.
9. Independent exact Google readback is required before canonical success.
10. Missing/drifted/wrong-target/stale/permission/provider failures are explicit and fail closed.
11. Direct tests cover bootstrap and adapter boundaries with synthetic/fake HTTP provider behavior.
12. Live proof must use MIRA-owned isolated Calendar/event state and preserve public-repo privacy.
13. Existing personal/legacy Calendar state is neither modified nor used as a development fixture.
14. Release/no-app packaging must ship the adapter without claiming Microsoft/Apple support or broad Calendar permission.
15. Exact final PR-head CI, expected-head merge protection, remote-main readback and post-merge main CI are required before packet completion.

### Evidence state

- **Desired:** yes
- **Specified:** yes
- **Implemented:** yes
- **Test-verified:** yes through CI `33432595617` on `3691c357e71cba325e6203edca189da52f7daeb2`
- **Integration/release-verified:** yes for deterministic Personal Workspace packaging on that head
- **Live-verified:** **no; blocked by absence of a branch Apps Script deployment/execution surface in the current connected runtime**

## Exact next action / resume point

1. Re-read PR #78 live head after this governance commit and require CI green on that exact head.
2. Synchronize PR #78 and the no-app installation guidance with the one-click `MIRA → Enable Calendar` design and narrow OAuth scope evidence.
3. Do **not** merge or claim `CAL-006` live/completed merely from synthetic CI.
4. Obtain an authorized execution path for the branch's bound Apps Script artifact or an equivalent isolated installed starter copy; run `MIRA → Enable Calendar` once and verify a dedicated MIRA-owned Calendar is created/recovered without touching Primary/Family.
5. On that MIRA-owned Calendar, run one bounded synthetic event create → exact readback → guarded update → exact readback → replay proof. Keep provider IDs only in private/live evidence, never public Git.
6. After live proof succeeds, reconcile `BACKLOG.md`/`FEATURES.md`, require fresh exact-head CI, merge PR #78 with expected-head protection, verify remote main and post-merge main CI.
7. Do not expand into Microsoft/Apple Calendar, appointment intake, reminders, outbound contact, medical meaning, migration, or Android.

## Recovery protocol

Read this file first. Confirm branch `integration/m0-023-google-calendar-projection`, PR #78 and the remote head. Inspect any commits newer than the recorded last-green implementation head rather than reconstructing from chat. M2-M0-022 remains complete. Protected personal/legacy Calendar state remains unavailable as a development fixture.
