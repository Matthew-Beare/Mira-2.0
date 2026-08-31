# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and exact recovery state.

## Product direction

Default Personal MIRA is stock ChatGPT + Google Workspace with no external infrastructure prerequisite. Repeated useful no-app verticals and integrity/recovery hardening remain ahead of Android. Normal user-facing branding is **MIRA**. `MIRROR` remains an internal database/reality-layer term only when a technical database-specific context requires it; normal product UI, brief titles, automation titles, and ordinary conversation say MIRA.

Every work session begins and ends by checking `CURRENT_WORK.md`, `FEATURES.md`, `BACKLOG.md`, and `ROADMAP.md`.

## Session-start alignment verification — 2026-08-31

### `FEATURES.md`

- `CAL-007` provider-neutral Calendar projection is merged/test-verified synthetically through PR #77 but still lacks a real provider adapter proof.
- `CAL-006` requires the selected Google/Microsoft/Apple Calendar lane to have verified capability and exact provider readback rather than silent substitution.
- `CAL-008` appointment evidence intake remains downstream of safe Calendar projection and therefore still depends on provider-specific projection work.

### `BACKLOG.md`

- `CALENDAR-PROJECTION-001A` is complete through PR #77 at main merge `fcc81f0e9d9510d05406acd9068d9ca4ee016806`.
- `CALENDAR-PROJECTION-001B` is the one active work item. This packet is a bounded Google adapter implementation/test slice; the work item remains incomplete until a separate isolated live-provider proof exists.
- `APPOINTMENT-INTAKE-001` remains the next intended user-visible appointment vertical once the selected Calendar path is honestly verified.

### `ROADMAP.md`

M2-M0.5 continues to prioritize useful stock-ChatGPT + Personal Google verticals before Android. Google is the default Personal Workspace path, so implementing its Calendar adapter contract is the highest-leverage bounded prerequisite after the provider-neutral projection core.

### Provider-sandbox finding

A read-only capability check of the connected Google Calendar account exposed only the user's primary Calendar, a Family Calendar, and US Holidays. The connected Calendar tool does not provide a create-calendar action. None of those existing calendars may be repurposed as a development fixture. Live provider proof is therefore explicitly deferred until an isolated MIRA test Calendar can be created/approved through a safe provider path.

### Direction result

**ALIGNED.** Implement and test the Google Calendar adapter semantics without touching protected live Calendar state. Do not claim live provider verification in this packet.

## Completed predecessor

### `M2-M0-022` — Provider-neutral Calendar projection core

- **Work:** `CALENDAR-PROJECTION-001A`
- **Feature:** `CAL-007`
- **PR:** #77
- **Final PR head:** `ec6fe091bfa68cabce5450e9974ff5337ae55800`
- **Exact-head CI:** `33427269214` green
- **Merge SHA / verified main checkpoint:** `fcc81f0e9d9510d05406acd9068d9ca4ee016806`
- **Post-merge main CI:** `33427385919` green
- **Evidence:** stable source/provider/calendar projection identity, deterministic normalized timed-event material, replay/source/provider conflict handling, exact synthetic provider readback, Personal starter `calendar_projection` Resource type, ownership/direct tests.
- **Evidence ceiling:** no Google/Microsoft/Apple Calendar writes/readback, OAuth/provider onboarding, appointment extraction, reminder delivery, contact, medical inference, migration, or Android proof.

## Active packet

### `M2-M0-023` — Google Calendar adapter core

- **Primary work:** `CALENDAR-PROJECTION-001B`
- **Primary features:** `CAL-006`, `CAL-007`
- **Related invariants/features:** `CAL-005`, `RECOVERY-002`, `STORE-001`, `DATA-001`, `PROFILE-013`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `integration/m0-023-google-calendar-adapter-core`
- **Base SHA:** `fcc81f0e9d9510d05406acd9068d9ca4ee016806`
- **Current head:** resolve from remote before further mutation/merge; this checkpoint is not itself completion evidence.
- **PR:** not yet opened at this checkpoint
- **Dependencies:** merged provider-neutral Calendar projection core; Google Calendar API event semantics; durable replay/idempotency dependency for external mutation.
- **Blockers:** live provider proof is blocked by absence of an isolated MIRA test Calendar in the connected account/tool surface. This does not block the bounded adapter implementation/test slice.

### Objective

Implement the smallest Google-specific adapter that satisfies MIRA's provider-neutral Calendar projection contract without performing live provider writes. The adapter must map canonical timed events to Google event resources, use deterministic Google-valid event IDs, store MIRA projection/retry metadata in private extended properties, preserve exact opaque Google ETags for concurrency, require writer/owner access, support crash-safe replay through an injected durable idempotency store, and fail closed on collisions/drift/stale conditional updates.

### Dependency repair discovered during implementation

The merged provider-neutral core represented `provider_version` as a positive integer. Google Calendar uses an opaque event ETag as its concurrency token and supports conditional updates through `If-Match`; manufacturing a local integer would lose restart-safe provider concurrency truth. This packet therefore includes the minimum hard-dependency repair: provider versions become opaque non-empty strings across `CAL-007`, with the in-memory adapter using `v1`, `v2`, etc. Direct existing tests must remain green after this repair.

### Explicitly out of scope

- any write to the user's current primary, Family, Holidays, legacy, or other live Calendar;
- creation of a new Google Calendar through unsupported/manual side channels;
- OAuth/client-secret/provider credential code;
- live Google Calendar provider verification;
- Microsoft/Outlook/M365 or Apple/iCloud adapters;
- appointment email/photo/text extraction (`CAL-008`);
- reminder scheduling/delivery;
- outbound contact;
- medical interpretation;
- Android/mobile work.

## Acceptance criteria

1. Provider-neutral Calendar versions are opaque strings, preserving exact provider concurrency tokens rather than assuming integers; existing synthetic projection behavior remains regression-tested.
2. Google event identity is deterministic from MIRA projection identity and uses a Google-valid caller-supplied event ID alphabet/length so retry does not create duplicate events.
3. Google event writes include exact MIRA private metadata for projection identity, current provider idempotency key, and request fingerprint; readback validates that metadata.
4. Google event mapping preserves title, start/end instants, IANA timezone, optional location and description while keeping unrelated Google-only fields outside canonical authority.
5. Create is replay-safe across response loss: an already-created deterministic event with exact MIRA retry metadata/material is adopted as replay rather than duplicated.
6. Update uses the exact prior Google ETag as the conditional `If-Match` precondition. Stale/external provider changes fail closed rather than being overwritten.
7. An update that commits at Google but loses its response can be recovered by exact provider readback of the new retry metadata/material and backfilled into the durable idempotency store.
8. Durable provider idempotency history is injected behind a protocol, not held only in adapter process memory. Same idempotency key + different request material is a hard conflict even after later provider mutations.
9. Target Calendar access must be `owner` or `writer`; weaker/read-only access fails before mutation because exact private metadata/readback cannot be guaranteed.
10. Deterministic event-ID collision with a nonmatching MIRA projection fails closed; no event is hijacked.
11. Direct tests prove Google mapping, deterministic ID, create/replay, crash recovery, ETag update/conflict, durable idempotency conflict, access failure, projection collision, and integration through `CalendarProjectionService` using only synthetic transport/store fixtures.
12. New production code is registered in `project/code_ownership.json`; all repository CI gates are green on the exact final PR head before merge.
13. Completion of this packet may claim only **Google adapter implemented/test-verified with synthetic transport**. `CALENDAR-PROJECTION-001B` remains partial until isolated live Google provider write/readback evidence exists; no broader Microsoft/Apple claim is allowed.

## Completed evidence so far

- Official Google Calendar API documentation was checked for current semantics: caller-specified event IDs are allowed using base32hex characters and are recommended to reduce duplicate creation risk; event ETags are opaque concurrency/version evidence; conditional updates can use `If-Match`; private extended properties are writable and calendar/event specific.
- `mira/calendar_projection.py` now models provider versions as opaque strings; the synthetic adapter uses `v1`/`v2` versions while preserving the same conflict/readback semantics.
- `tests/test_calendar_projection.py` is updated to regression-test the opaque-version contract.
- `mira/google_calendar_projection.py` implements an injected Google transport boundary, deterministic Google event IDs, private MIRA projection/retry metadata, exact ETag handling, writer/owner access checks, conditional patch semantics, crash/replay recovery, and an injected durable provider-idempotency protocol.
- `tests/test_google_calendar_projection.py` provides direct synthetic transport/ledger coverage for the adapter and an integration path through `CalendarProjectionService`.
- `BACKLOG.md` closes `CALENDAR-PROJECTION-001A` with PR #77 evidence and marks `CALENDAR-PROJECTION-001B` active for this bounded slice while retaining the live-provider evidence blocker.
- No Calendar provider mutation has occurred in this packet.

## Exact next action / resume point

1. Register `mira/google_calendar_projection.py` in `project/code_ownership.json` with direct verification at `tests/test_google_calendar_projection.py`.
2. Reconcile `FEATURES.md` evidence: `CAL-007` is merged synthetic projection core; `CAL-006` may advance only to Google-adapter candidate/test evidence, never live provider proof.
3. Open a non-draft PR from this branch to `main` and run all repository CI gates.
4. Repair only actual packet/baseline blockers until exact-head CI is green.
5. Checkpoint the exact green head, update the PR evidence ceiling, re-run final exact-head CI if source changes, then merge with `expected_head_sha` protection.
6. Verify remote `main` and post-merge `main` CI before claiming this bounded adapter packet complete.
7. After merge, keep `CALENDAR-PROJECTION-001B` partial/blocking live verification and select the next safe dependency packet. Do not use protected personal Calendars as test fixtures.

## Recovery protocol

Read this file first. Confirm branch `integration/m0-023-google-calendar-adapter-core` and its remote head. `M2-M0-022` is complete and must not be reopened absent new integrity evidence. The live Google provider proof blocker is the absence of an isolated MIRA development Calendar, not a reason to weaken provider-readback requirements or mutate existing user Calendar state.
