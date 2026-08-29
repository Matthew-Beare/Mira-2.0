# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and the exact recovery point.

## Product deployment invariant

Default Personal MIRA remains **Google Workspace first, zero infrastructure**. Stock ChatGPT may use the official same-user Google Drive/Sheets connection for the single-writer Personal lane. Android/shared mutation must not turn that path into unsafe independent multi-writer read-then-write access.

Provider-neutral `API-001`, `AUTH-001` and `STORE-001` remain canonical. No client becomes an independent authority and no dual writable masters are permitted.

## Completed predecessor

### `M2-M0-006` — Google Workspace zero-infrastructure first run

- Complete and remotely verified.
- PR #50 merge `e412405a475d1423edaac821d7a99481e4a6eb4b`; CI `33243206658` green.
- PR #51 merge `641a7ce412bd0de46500c229910e52cb35a90bcc`; CI `33243533206` green.
- PR #52 merge `07d79c3a72cc906e93316e213e282919a1fcc4ff`; CI `33243840207` green.
- Closeout PR #53 merge `983444bf697a58a42c4482859d4fe7f0c17fb454`; CI `33274016785` green.
- Proven Personal path: clean Workspace copy → Authority/binding bootstrap → stock ChatGPT native Google create/read/replay/mutate/readback with exact provider verification.
- Native read-then-write Sheets mutation is single-writer only; it is not distributed compare-and-swap.

## Active packet

### `M2-M1-001` — Concurrent canonical command boundary

- **Primary work:** `ANDROID-COMMAND-BOUNDARY-001`, first prerequisite slice of `ANDROID-CLIENT-CORE-001`
- **Related features:** `CLIENT-ANDROID-001`, `API-001`, `AUTH-001`, `STORE-001`, `RECOVERY-002`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Main implementation baseline:** PR #55 merge `1908629fc887b025a8acb2d6fd5321ca191ad0e7`
- **Provider-neutral sequencer:** PR #54 merge `d21869d091cbcfce609d47665ef8872123f2be43`; CI `33274374052` green.
- **Workspace queued-writer worker:** PR #55 merge `1908629fc887b025a8acb2d6fd5321ca191ad0e7`; CI `33274804921` green.
- **Current requirement/governance capture branch:** `integration/m1-001-feature-contract-capture`
- **Capture branch base:** `1a36010c2941a66a44c420fab441888cd76ac67c` (same product tree as PR #55 merge; intervening commits only removed accidental placeholder files)
- **Architecture:** `docs/M1_CONCURRENT_COMMAND_BOUNDARY.md`
- **Status:** synthetic concurrency and Workspace worker behavior are implemented/test-verified and merged. Live isolated Google Apps Script worker proof remains pending.

## Feature alignment

### Primary behavior this packet must enable

Android and stock ChatGPT must be able to participate in one canonical MIRROR reality without independent writers racing Google Sheets. The packet must establish one replay-safe mutation sequencer before Android becomes a canonical writer.

### Product invariants this packet must preserve

- `CORE-001`: product/assistant identity remains MIRA.
- `API-001` / `AUTH-001` / `STORE-001`: Android is a client, not a second authority or alternate product model.
- `DATA-001`: no legacy production artifact is a test fixture.
- `ONBOARD-006`: ordinary Personal use remains browser-first/zero-infrastructure; Android must not retroactively force every user into Cloud Run/Linux/SQL.
- `CAL-008` / `CAL-006`: the Android design must leave a clean path for appointment evidence capture from photos and preferred-Calendar projection rather than hard-coding entity-only UI or Google row coordinates.
- `STUDIO-001`: Android/shared architecture must remain compatible with later user-generated bounded features/workflows and their declared dependencies.
- `ONBOARD-003`: Android work must not replace or invalidate the four-question first-boot Interview Ledger contract.
- `DEV-007`: passing concurrency tests does not permit a design that makes accepted downstream features impossible.

### Explicitly deferred related features

This packet does **not** implement Android UI, appointment photo/email parsing, preferred Calendar sync, reminder delivery, onboarding runtime, MIRA Studio, family sharing, Gmail/Calendar service fan-out, or Cloud Run live deployment. Those requirements are preserved in `FEATURES.md`/`BACKLOG.md` and must be re-read by the packet that implements them.

## Selected command architecture

For the ordinary Personal Android lane, use a **durable Google Workspace command inbox plus one serialized Apps Script worker** rather than allowing ChatGPT and Android to mutate canonical Sheets independently.

Command flow:

`ChatGPT/Android command → Commands inbox → one ScriptLock worker → API-001 semantics → Authority → STORE-001 → exact readback → durable command result`

The worker is asynchronous. Google documents that API writes do not fire installable edit triggers, so the inbox is polled by a time-driven trigger. The implementation uses a one-minute trigger cadence. Cloud Run remains the synchronous advanced profile if later accepted behavior requires consistently lower latency.

## Completed M2-M1 synthetic evidence

### Provider-neutral sequencer — merged

`mira/command_sequencer.py` + `tests/test_command_sequencer.py` prove:

- duplicate command identity rejected;
- concurrent stale revision-0 commands serialize so only one can commit;
- crash after canonical mutation but before queue acknowledgement retries through canonical idempotency without a second revision;
- expected revisions progress 0 → 1 → 2 under serialized execution;
- same-user authorization failure is terminal with no provider mutation.

PR #54 passed full CI and merged at `d21869d091cbcfce609d47665ef8872123f2be43`.

### Google Workspace queued-writer worker — merged

`workspace/apps_script/CommandWorker.gs` implements:

- dedicated `Commands` inbox carrying API-001 upsert material and durable result/error fields;
- explicit `mutation_mode=queued_writer` activation;
- exactly one one-minute Apps Script time-driven worker trigger;
- activation validates/creates the trigger before queued mode becomes authoritative;
- `LockService.getScriptLock()` critical section with bounded wait;
- bounded command processing;
- API/schema compatibility validation;
- persisted Authority/binding resolution and same-user subject == Authority owner check;
- STORE-001-compatible request fingerprint;
- idempotency replay and same-key/different-material failure;
- stale-revision conflict handling;
- canonical Resource write + Idempotency append + exact readback;
- success acknowledgement only after exact readback;
- retryable authority/readback/internal failures remain pending;
- recovery when Resource write landed but Idempotency acknowledgement did not, reconstructing the missing acknowledgement without incrementing revision again.

`mira/workspace_native.py` fails closed on direct native mutation when `mutation_mode=queued_writer`, closing the second-writer side door.

Executable fake-Apps-Script tests cover trigger activation, ScriptLock behavior, canonical create/readback, stale command conflict, crash/retry recovery, mode failure, and Authority-owner enforcement. PR #55 CI `33274804921` passed and merged at `1908629fc887b025a8acb2d6fd5321ca191ad0e7`.

## Live proof blocker

The connected Google Drive/Sheets tooling available in this development environment can manipulate spreadsheet content but cannot create/update a bound Google Apps Script project. No installable Apps Script plugin/action is currently available.

Google's documented distribution behavior still supports the intended product: a whole spreadsheet copy carries its bound script, while installable triggers are per-user and can be created by `miraEnableQueuedWriter()` on that user's copy. Therefore the remaining provider step is to **seed one isolated MIRA 2.0 release/synthetic workbook with the Git-backed bound Apps Script**, then execute the live queued-writer proof on that isolated copy.

Do not claim live worker evidence until that script is actually installed and provider behavior is read back.

## Newly refined product requirements captured during this packet

These are durable requirements but **do not expand M2-M1-001 implementation scope**:

### Onboarding

`ONBOARD-003` is now explicitly:

1. authoritative IANA timezone;
2. broad life/work/study/caregiving pattern;
3. biggest remembering/organizing/deciding/planning/follow-through goals;
4. whether appointment/reminder help is wanted and, if so, preferred Calendar auto-sync lane.

MIRA's name is fixed and must not be asked. After the four kickoff questions, onboarding tells the user they can ask MIRA at any time to continue the interview with additional questions that improve MIRA's function for them and introduces integrated MIRA Studio plus optional sharing.

### Appointments

`CAL-008` / `APPOINTMENT-INTAKE-001` explicitly require appointment evidence intake from inbound email, user-supplied image/photo, or user text. MIRA detects appointment intent, extracts date/time/timezone/location/provider/contact and provider specialty/type such as cardiologist, reconciles durable provider/appointment identity, preserves provenance/confidence, and only asks when material ambiguity remains.

`CAL-006` / `CALENDAR-PROJECTION-001` require preferred-Calendar projection/sync with exact provider readback for the selected Google, Microsoft/Outlook/M365, or Apple/iCloud lane. Intake and Calendar-write success remain separate truths.

Existing `MAIL-002` still means this requirement does **not** silently authorize MIRA to send outbound emails negotiating appointments with providers. The current interpretation is automatic appointment **capture/scheduling into the user's Calendar from received evidence**. Outbound provider contact remains a separate explicitly approved capability.

### MIRA Studio

`STUDIO-001` / `MIRA-STUDIO-001` define an integrated user-facing Studio for continuously improving MIRA through guided bounded features/workflows/preferences, preview/test/rollback, dependency/provenance awareness, and optional sanitized sharing. Shared/imported behavior never silently activates.

### Development alignment

`DEV-007` and the updated `project/WORK_PACKET_POLICY.md` require every implementation packet to read and record its alignment with the canonical feature set before implementation and before merge.

## Android distance to first functional app

The project is **past the architecture-foundation stage but not yet at an Android APK/UI stage**.

Completed prerequisites:

1. provider-neutral structured state;
2. persistent Authority routing;
3. shared API command/query semantics;
4. stock ChatGPT Google-backed canonical roundtrip;
5. provider-neutral concurrent command sequencer;
6. synthetic Google Workspace queued-writer worker with conflict/replay/crash tests.

Remaining critical slices before the first genuinely functional Android shared-state proof:

1. live isolated Google queued-writer/trigger proof;
2. Android project/client skeleton + same-user enrollment/authentication and OS-protected credentials;
3. Android command submission/read path against the shared boundary;
4. replay-safe offline queue + reconnect/cursor/conflict handling;
5. Android mutates the exact canonical M2-M0 entity and stock ChatGPT reads it back;
6. representative-device proof.

So Android is no longer “we need to invent the backend.” It is roughly **one live provider gate plus four to five bounded client/integration slices away from the first ugly but real shared-state Android app**. Notifications/TTS, camera appointment capture, polished UI, signing/release, and broader services come after that first shared-state proof unless dependency evidence changes the order.

## Acceptance status

1. No direct multi-writer Sheets mutation — test-verified/merged; live pending.
2. One canonical mutation sequencer — test-verified/merged; live pending.
3. Existing API/Authority/STORE semantics — preserved/test-verified.
4. Same-user authentication boundary — specified/synthetic checked; live Android path pending.
5. Replay safety — test-verified/merged.
6. Stale conflict safety — test-verified/merged.
7. Restart/retry safety — test-verified/merged.
8. No dual writable masters — direct native planner guard test-verified/merged.
9. Provider portability — preserved in command/API model.
10. Synthetic first — passed.
11. Legacy preservation — passed so far.
12. Bounded scope — maintained.
13. **Live isolated Google worker/trigger evidence — pending.**

## Exact next action

1. Finish and merge the requirement/governance capture PR from `integration/m1-001-feature-contract-capture`; this PR changes authoritative feature/backlog/policy/checkpoint state only and does not implement appointment/Studio/onboarding features.
2. Resume `M2-M1-001` live proof from the merged head.
3. Seed one isolated synthetic/release MIRA 2.0 workbook with the Git-backed bound Apps Script through an approved provider/operator path; never use a legacy production workbook.
4. Enable queued-writer mode and independently verify the Commands tab, exactly one worker trigger, mutation mode, synthetic command result, canonical Resource/Idempotency readback, and at least one stale/retry behavior.
5. If live proof passes, close `ANDROID-COMMAND-BOUNDARY-001` and create the next bounded `ANDROID-CLIENT-CORE-001` implementation packet.

## Recovery protocol

Read this file first. Verify main contains PR #55 merge `1908629fc887b025a8acb2d6fd5321ca191ad0e7` or a descendant. If `integration/m1-001-feature-contract-capture` is still open, merge only the feature/governance capture after CI. Then continue live provider proof under `M2-M1-001`; do not jump to Android UI until the queued-writer boundary is live-verified or explicitly rejected. Preserve appointment intake, Calendar preference onboarding, MIRA Studio, and feature-alignment requirements in Git without pulling their implementation into this packet. Keep provider IDs, secrets, personal data and live row contents out of public Git.
