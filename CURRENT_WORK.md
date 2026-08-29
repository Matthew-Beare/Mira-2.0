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
- Truth boundary: native read-then-write Sheets mutation is single-writer only; it is not distributed compare-and-swap.

### Preserved onboarding contract

`ONBOARD-003`/`ONBOARD-004` remain preserved in Git and audited legacy source: four-question kickoff, resumable Interview Ledger, current AI-use/friction discovery, and evidence-first reuse of accessible conversation/files/connected sources. Full MIRA 2.0 interview runtime remains queued under `FIRSTBOOT-CORE-001` / `DISCOVERY-CORE-001`; this packet does not absorb it.

## Preserved advanced deployment work

### `M2-M0-005` — Cloud Run credential + live Google deployment proof

- Related work: `API-DEPLOYMENT-001B`.
- Paused/deprioritized as a Personal-baseline prerequisite; reusable synchronous advanced profile.
- PR #48 merged `acb37af4aa378e8128d8591406859fe954af3474`; CI `33217543700` green.
- PR #49 merged `3332081054d691eca646c1d7bb274d22096f1c62`; CI `33218561781` green.
- Pre-pivot checkpoint: `c392b9b829fab989be8856c9272294c9907e409e`.
- No live Cloud Run evidence is claimed.

## Active packet

### `M2-M1-001` — Concurrent canonical command boundary

- **Primary work:** first bounded slice of `ANDROID-CLIENT-CORE-001`
- **Related features:** `CLIENT-ANDROID-001`, `API-001`, `AUTH-001`, `STORE-001`, `RECOVERY-002`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `integration/m1-001-concurrent-boundary`
- **Base SHA:** `983444bf697a58a42c4482859d4fe7f0c17fb454`
- **Architecture document:** `docs/M1_CONCURRENT_COMMAND_BOUNDARY.md`
- **Current implementation:** `mira/command_sequencer.py` + `tests/test_command_sequencer.py`
- **Status:** Google/native vs managed decision is narrowed and provider-neutral sequencer semantics are implemented; full CI and Apps Script transport remain pending.

## Selected architecture

For the ordinary Personal Android lane, use a **durable Google Workspace command inbox plus one serialized Apps Script worker** rather than allowing ChatGPT and Android to mutate canonical Sheets independently.

Command flow:

`ChatGPT/Android command → durable inbox → one serialized worker → API-001 → Authority Registry → STORE-001 → exact readback → durable command result`

The worker will use `LockService.getScriptLock()` around revision/idempotency evaluation and canonical mutation. A time-driven trigger polls the inbox. This is intentionally asynchronous with minute-scale scheduling granularity.

Cloud Run remains the synchronous advanced profile if later accepted behavior requires consistently lower latency.

## Current provider evidence

### Google event-trigger limitation — decisive

Current Google Apps Script documentation states that script executions and API requests do **not** cause installable triggers to run. Therefore a command appended by stock ChatGPT's Google Sheets action or Android's Sheets API cannot rely on `onEdit` or an installable edit trigger.

Google documents time-driven triggers as recurring as frequently as once per minute. The zero-infrastructure Workspace design must therefore poll a durable inbox rather than pretend API writes create synchronous trigger events.

### Google serialization primitive — supported

Current `LockService` documentation states that `getScriptLock()` prevents simultaneous execution of a guarded code section regardless of user identity. `tryLock`/`waitLock` acquire the lock with bounded waiting. This is the selected Workspace critical-section primitive.

### Apps Script web-app limitation

Apps Script web apps expose query/body request data through `doGet(e)`/`doPost(e)` but do not document arbitrary inbound HTTP headers in the event object. The M2-M0 rejection of bearer secrets in query/body remains valid. Browser execute-as-user authorization also does not make stock ChatGPT's existing Google Drive app automatically authenticate to a custom Apps Script web endpoint.

### Managed runtime remains technically valid but not the Personal default

Cloud Run supports manual scaling to one instance and per-instance concurrency `1`, which is a valid synchronous sequencer. MIRA already has code/operator support for those invariants. Current OpenAI GPT Actions can authenticate custom APIs with API key or OAuth, but they are a separately configured GPT surface and current OpenAI documentation says GPTs use apps or actions, not both. That does not transparently extend the stock Personal Google-app path proven in M2-M0.

## Deterministic sequencer implementation

`mira/command_sequencer.py` now defines the provider-neutral queue/worker contract:

- stable command IDs cannot be queued twice;
- queued commands remain `pending` until canonical execution is acknowledged;
- exactly one worker critical section executes a command at a time;
- the worker calls existing `ApiService.execute_command` rather than duplicating business/Authority semantics;
- deterministic API validation/authorization/revision/idempotency errors can become terminal failed command results;
- authority/readback failures remain pending for retry;
- a fault after canonical mutation but before queue acknowledgement leaves the command pending so the same idempotency key can converge to the original result on retry.

`tests/test_command_sequencer.py` covers:

- duplicate queued command rejection;
- two concurrent worker calls against two stale revision-0 commands, proving only one commits and the second conflicts;
- synthetic crash after canonical success but before queue acknowledgement, then idempotent retry with no second revision;
- revision 0 → 1 → 2 serialized progression;
- same-user authorization failure with no provider mutation.

`project/code_ownership.json` assigns this component to `ANDROID-CLIENT-CORE-001`.

## Acceptance criteria

1. No direct multi-writer Sheets mutation.
2. One canonical mutation sequencer owns conflict decisions.
3. Existing API/Authority/STORE semantics remain canonical.
4. Same-user authentication is explicit; no prompt/Sheet/URL/Git secrets.
5. Replay cannot duplicate canonical mutation.
6. Two stale commands cannot both succeed.
7. Restart/retry cannot silently duplicate a committed command.
8. Native Personal mutation switches to read-only/client-command mode when shared writer mode activates.
9. Android/domain identity never depends on Google row coordinates or Sheet IDs.
10. Deterministic synthetic proof precedes live provider changes.
11. Legacy production is untouched.
12. No Android UI, notifications/TTS, camera/NFC/BLE, Gmail/Calendar fan-out, full onboarding port or live Cloud Run work in this packet.

## Scope control

Do not implement Android UI. Do not touch live provider state until the sequencer and Workspace worker tests are green. Do not resume Cloud Run live deployment. Do not broaden into onboarding, Ops Briefs, Gmail, Calendar, family sharing or enterprise.

## Exact next action

1. Open a PR for the provider-neutral sequencer + architecture decision and run full CI.
2. Fix only sequencer/ownership defects.
3. When green, implement the next bounded slice on the same packet or a child branch: dedicated Workspace `Commands` inbox, queued-writer activation mode, one-minute worker trigger, `ScriptLock`, bounded processing, retry/readback semantics, and executable fake-Apps-Script tests.
4. Do not perform live Google worker activation until that Apps Script slice is green.

## Recovery protocol

Read this file first. Verify main contains M2-M0 closeout merge `983444bf697a58a42c4482859d4fe7f0c17fb454` or a descendant. Continue only `M2-M1-001` on `integration/m1-001-concurrent-boundary` while its PR is open. Preserve M2-M0 native Google as single-writer evidence; do not reinterpret it as safe Android concurrency. Preserve Cloud Run checkpoint without claiming live proof. Keep provider IDs, secrets, personal data and live row contents out of public Git.
