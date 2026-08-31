# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and exact recovery state.

## Product direction

Default Personal MIRA is stock ChatGPT + Google Workspace with no external infrastructure prerequisite. Repeated useful no-app verticals and integrity/recovery hardening remain ahead of Android. Normal user-facing branding is **MIRA**. `MIRROR` remains an internal database/reality-layer term only when a technical database-specific context requires it.

Every work session begins and ends by checking `CURRENT_WORK.md`, `FEATURES.md`, `BACKLOG.md`, and `ROADMAP.md`.

## Session-start alignment verification — 2026-08-31

- `CAL-005` appointment/provider identity is merged/test-verified through PR #76.
- `CAL-007` provider-neutral Calendar projection is merged/test-verified through PR #77 with synthetic provider readback only.
- `CAL-006` still requires a real preferred-Calendar lane before MIRA may claim Calendar sync is live.
- `CAL-008` remains the intended user-visible appointment-intake vertical after one default Personal Calendar lane is live-verified.
- M2-M0.5 continues to prioritize stock-ChatGPT + Personal Google usefulness before Android.

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
- **Last fully verified implementation/release head before this governance checkpoint:** `26e85dbc36364db6579f3b1bc3f38df20d98a75b`
- **Exact-head CI:** `33431397360` green on `26e85dbc36364db6579f3b1bc3f38df20d98a75b`
- **Current head rule:** this file is itself a governance checkpoint. Re-read PR #78 after this commit and require green CI on the new exact live head before any merge decision.

### Objective

Provide a browser-first Google Calendar provider lane that satisfies the merged provider-neutral projection contract without requiring Cloud Run/Linux/SQL/terminal infrastructure: stable projection identity, replay recovery, guarded updates using real Google ETags, exact provider readback and fail-closed error handling. Live verification must use isolated synthetic provider state, never Primary/Family/legacy Calendar data as a development fixture.

### Implemented/test-verified evidence

- `mira/calendar_projection.py` now treats provider version material as an opaque token rather than an integer counter, preserving equality/precondition semantics for real provider ETags. Calendar projection schema is v2 and direct synthetic tests use opaque `memory:N` tokens.
- `workspace/apps_script/GoogleCalendarProjection.gs` implements a bound-Apps-Script Google Calendar REST adapter using user OAuth rather than external infrastructure.
- Google events carry private extended properties for MIRA projection identity/idempotency material so lost create acknowledgements can be recovered without duplicate logical projection creation.
- Existing projected event updates use the exact previously read Google ETag through `If-Match`; stale provider state fails closed rather than being silently overwritten.
- Create/update acknowledgement is followed by independent exact event GET/readback before success is returned.
- Provider errors distinguish validation, authorization/capability, conflict, not-found and readback failures.
- The adapter creates no attendees, sends no attendee updates, creates no Meet links, and does not implement reminders, appointment extraction, Microsoft/Apple support, or medical behavior.
- `workspace/apps_script/appsscript.json` requests only event read/write plus Apps Script external-request permission in addition to existing Sheet/trigger scopes; it does not grant Calendar-management scope.
- `mira/workspace_bundle.py` validates the new adapter artifact, required symbols, guarded ETag behavior, exact-readback markers and least-privilege scopes.
- `tests/apps_script/google_calendar_projection.test.js` directly covers create, replay/lost-ack recovery, guarded update, stale ETag conflict, authorization failure, duplicate projection identity and readback mismatch.
- `distribution/personal_google_starter.json`, `mira/personal_distribution.py` and `tests/test_personal_distribution.py` now ship/hash/verify `GoogleCalendarProjection.gs` as the sixth deterministic Workspace artifact.
- CI `33431397360` passed compile, feature registry, product lifecycle ledger, Personal starter distribution, work-session alignment, code ownership, full Python tests and Workspace Apps Script tests on head `26e85dbc36364db6579f3b1bc3f38df20d98a75b`.
- No real Calendar provider mutation has been performed by this packet.

### Live-provider blocker

Connected Google Calendar discovery exposes only the user's Primary Calendar, the Family Calendar and the read-only US Holidays Calendar. The connector can create/update/delete events but exposes no action to create a new secondary Calendar. Plugin discovery found no alternative authorized Calendar integration with calendar-creation capability, and the connected Google Drive surface exposes no Apps Script execution action.

Therefore an isolated synthetic Calendar cannot currently be created from this runtime. Primary and Family are protected user state and must not be used as development fixtures merely to manufacture live evidence. This is an external capability blocker, not a code/test failure.

## Acceptance criteria

1. Google adapter preserves existing canonical projection identity semantics.
2. Capability/authorization failures fail closed before false canonical success.
3. Create writes exact normalized timed-event material and retains exact provider event identity/version evidence.
4. Update targets the exact projected event and uses atomic provider-version/ETag precondition evidence.
5. Identical logical replay cannot create a second logical projection/event.
6. One idempotency key cannot silently represent different material.
7. Independent exact Google readback is required before canonical success.
8. Missing/drifted/wrong-target/stale/permission/provider failures are explicit and fail closed.
9. Direct tests cover the adapter boundary with synthetic/fake HTTP provider behavior.
10. Live proof must use an isolated synthetic Calendar/event namespace and preserve public-repo privacy.
11. Existing personal/legacy Calendar state is neither modified nor used as a development fixture.
12. Release/no-app packaging must ship the adapter without claiming Microsoft/Apple support or broad Calendar-management permission.
13. Exact final PR-head CI, expected-head merge protection, remote-main readback and post-merge main CI are required before packet completion.

### Evidence state

- **Desired:** yes
- **Specified:** yes
- **Implemented:** yes
- **Test-verified:** yes through CI `33431397360` on `26e85dbc36364db6579f3b1bc3f38df20d98a75b`
- **Integration/release-verified:** yes for deterministic Personal Workspace packaging on that head
- **Live-verified:** **no; blocked by absence of an isolated writable synthetic Calendar target**

## Exact next action / resume point

1. Re-read PR #78 live head after this governance commit and require CI green on that exact head.
2. Update PR #78 description with the implemented/test-verified evidence and explicit live-proof blocker/evidence ceiling.
3. Do **not** merge or claim `CAL-006` live/completed merely from synthetic CI.
4. When an isolated writable Google Calendar becomes available through an authorized connector/runtime, run one bounded synthetic create → exact readback → guarded update → exact readback → replay proof. Record provider identifiers only in private/live evidence, never public Git.
5. After live proof succeeds, reconcile `BACKLOG.md`/`FEATURES.md`, require fresh exact-head CI, merge PR #78 with expected-head protection, verify remote main and post-merge main CI.
6. If the isolated-Calendar capability remains unavailable, preserve this exact checkpoint and dynamically select only work that is not falsely presented as satisfying the blocked Calendar live-verification dependency.
7. Do not use Primary or Family as test fixtures; do not expand into Microsoft/Apple Calendar, appointment intake, reminders, outbound contact, medical meaning, migration, or Android.

## Recovery protocol

Read this file first. Confirm branch `integration/m0-023-google-calendar-projection`, PR #78 and the remote head. Inspect any commits newer than the recorded last-green implementation head rather than reconstructing from chat. M2-M0-022 remains complete. Protected personal/legacy Calendar state remains unavailable as a development fixture.
