# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and exact recovery state.

## Product direction

Default Personal MIRA is stock ChatGPT + Google Workspace with no external infrastructure prerequisite. Repeated useful no-app verticals and integrity/recovery hardening remain ahead of Android. Normal user-facing branding is **MIRA**. `MIRROR` remains an internal database/reality-layer term only when a technical database-specific context requires it.

Ordinary-user setup must not expose developer chores when MIRA can perform them safely. Calendar activation therefore defaults to one explicit user action that lets MIRA create/recover its own secondary Google Calendar; users are not expected to create calendars, copy provider IDs, edit OAuth scopes, open Apps Script, or understand Calendar API mechanics.

Every work session begins and ends by checking `CURRENT_WORK.md`, `FEATURES.md`, `BACKLOG.md`, and `ROADMAP.md`.

## Session-start alignment verification — 2026-08-31

### `FEATURES.md`

- `CAL-005` appointment/provider identity is merged/test-verified through PR #76.
- `CAL-007` provider-neutral Calendar projection is merged/test-verified through PR #77 with synthetic provider readback only.
- `CAL-006` still requires one real preferred-Calendar lane before MIRA may claim Calendar sync is live.
- `CAL-008` remains queued behind a live-verified default Personal Calendar lane.

### `BACKLOG.md`

- `CALENDAR-PROJECTION-001A` is complete through PR #77.
- `CALENDAR-PROJECTION-GOOGLE-001` remains the single active provider-lane prerequisite in M2-M0-023.
- User acceptance feedback established manual secondary-calendar creation as unacceptable ordinary-user setup, so automatic MIRA-owned Calendar bootstrap is part of this packet's existing usability/protected-state acceptance boundary.
- Microsoft/Outlook/M365 and Apple/iCloud proofs remain separate downstream work.

### `ROADMAP.md`

- M2-M0.5 prioritizes an ordinary-user stock-ChatGPT + Personal Google product before Android.
- A safe Google Calendar lane remains the shortest hard prerequisite between the merged projection core and appointment intake.
- Browser-first means no terminal, copied Calendar IDs, manual API setup, or protected production fixtures.

### Direction result

**ALIGNED.** Continue M2-M0-023 until the Google Calendar provider lane has honest live evidence or an exact external blocker checkpoint. Do not substitute Primary, Family, or legacy calendars for isolated MIRA-owned provider state.

## Completed predecessor

### `M2-M0-022` — Provider-neutral Calendar projection core

- **Work:** `CALENDAR-PROJECTION-001A`
- **Feature:** `CAL-007`
- **PR:** #77
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
- **PR:** #78 open, non-draft, mergeable
- **Last verified green implementation/governance head:** `94150fe1ae3b604495b86e96ce98051d17195331`
- **Exact-head CI:** `33433809624` green on `94150fe1ae3b604495b86e96ce98051d17195331`
- **Current head rule:** this file is the recovery checkpoint. Resolve the live PR head before merge and require green CI on that exact head; do not create another source-only checkpoint merely to restate its own SHA.

### Objective

Provide a browser-first Google Calendar lane with no server/terminal requirement. After explicit Calendar opt-in, an ordinary user chooses **MIRA → Enable Calendar** once, accepts Google's authorization UI when required, and MIRA creates or safely recovers one dedicated secondary Calendar named `MIRA`. Event projection must preserve stable identity, lost-ack recovery, exact readback and atomic Google ETag update protection without touching Primary/Family/legacy calendars.

### Implemented/test-verified evidence

- Provider versions are opaque tokens, allowing exact Google ETags rather than fake counters.
- `GoogleCalendarProjection.gs` implements Calendar REST through bound Apps Script user OAuth.
- `miraEnsureGoogleCalendar_()` creates/recoveries one dedicated MIRA-owned Calendar after explicit opt-in.
- Calendar bootstrap persists an installation UUID before provider creation and stamps a unique ownership marker into the Calendar description; lost create acknowledgement is recovered through read-only CalendarList lookup rather than duplicate creation.
- Missing/deleted/ambiguous/ownership-drifted managed Calendar state fails closed.
- Manifest uses `calendar.app.created` + `calendar.calendarlist.readonly` + `script.external_request`; release validation rejects broad `calendar`, blanket `calendar.events`, and `calendar.calendars` scopes.
- `Code.gs` exposes **MIRA → Enable Calendar** and MIRA-only user-facing initialization wording.
- Event projection uses private extended properties for stable MIRA projection/idempotency identity, independent exact GET readback, and exact prior ETag through `If-Match` for updates.
- No attendees, attendee notifications, Meet links, reminders, appointment extraction, Microsoft/Apple behavior, medical behavior, or legacy Calendar mutation are introduced.
- The deterministic Personal distribution ships the Calendar adapter as part of the validated Workspace bundle.
- `workspace/apps_script/README.md` documents the ordinary-user copy/initialize/Enable Calendar flow, narrow scopes, and the separate maintainer template-publication evidence boundary.
- `mira/workspace_bundle.py` fails release validation if that one-click install/Calendar guidance or narrow-scope contract disappears.
- Google documentation confirms that making a copy of a spreadsheet copies its attached container-bound scripts; therefore the intended public install path is an ordinary Sheet copy rather than per-user script deployment.
- CI `33433809624` passed all repository gates on `94150fe1ae3b604495b86e96ce98051d17195331`.

### Private isolated provider-proof target

A fresh Drive copy named **`MIRA Calendar Provider Proof - ISOLATED DEV - 2026-08-31`** was created from the existing **`MIRA Personal Starter - Clean Template`**. It is synthetic MIRA 2.0 development state, not a legacy production artifact. Its provider ID is intentionally not recorded in public Git.

Copying the template gives us an isolated install target and preserves whatever bound script is actually published in the template. The current connector cannot inspect or execute that bound script, so the next proof must determine whether the template already contains the current **Enable Calendar** release or whether maintainer template publication is still required.

### Live-provider blocker

The ChatGPT Calendar connector can list calendars and mutate events but cannot create a secondary calendar. Drive can copy the starter but cannot inspect/deploy/execute its bound Apps Script. No installed plugin exposes Apps Script deployment/execution.

This is a live execution/template-publication evidence boundary, not an ordinary-user setup design blocker and not a repository test failure.

## Acceptance criteria

1. Google adapter preserves canonical projection identity semantics.
2. Ordinary-user Calendar setup is one MIRA enable action plus Google's unavoidable consent UI; no manual Calendar/API/script setup.
3. Managed Calendar creation/recovery is replay-safe and isolated from Primary/Family/legacy state.
4. OAuth uses app-created Calendar ownership and read-only CalendarList recovery rather than blanket event access.
5. Create/readback/update/replay preserves exact provider identity/version evidence.
6. Updates use atomic Google ETag `If-Match` protection.
7. Missing/drifted/ambiguous/stale/permission/provider failures fail closed.
8. Deterministic Personal packaging contains the exact tested adapter and install contract.
9. Live proof uses isolated MIRA-owned Calendar/event state only.
10. Exact final PR-head CI, expected-head merge protection, remote-main readback and post-merge CI are required before packet completion.

### Evidence state

- **Desired:** yes
- **Specified:** yes
- **Implemented:** yes
- **Test-verified:** yes
- **Integration/release-verified:** yes for source-controlled deterministic Personal packaging
- **Ordinary-user one-click flow:** implemented/test-verified
- **Live-verified:** no

## Exact next action / resume point

1. Open the private isolated Drive copy **`MIRA Calendar Provider Proof - ISOLATED DEV - 2026-08-31`** and observe the MIRA menu. This is a simple UI observation, not developer configuration.
2. If **Enable Calendar** is already present, run it once, approve Google if prompted, then verify the dedicated MIRA-owned Calendar through connected Calendar readback and execute one bounded synthetic event create → exact readback → guarded update → exact readback → replay proof.
3. If **Enable Calendar** is absent, do not ask an ordinary user to paste scripts. Treat the official template as stale and create a bounded maintainer template-publication prerequisite that refreshes the bound script from the verified source release before live proof continues.
4. Never use Primary, Family, or legacy calendars as test fixtures. Never write live provider IDs/tokens/ETags into public Git.
5. After live proof succeeds, reconcile lifecycle state, require fresh exact-head CI, merge PR #78 with expected-head protection, verify remote `main`, and require post-merge main CI.

## Recovery protocol

Read this file first. Confirm PR #78 and branch `integration/m0-023-google-calendar-projection`, then inspect any commit newer than the recorded green head. The isolated Drive proof target must be rediscovered by its synthetic title rather than by committing its provider ID. M2-M0-022 remains complete. Protected personal/legacy Calendar state remains unavailable as a development fixture.
