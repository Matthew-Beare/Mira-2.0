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

### Preserved onboarding contract

`ONBOARD-003`/`ONBOARD-004` remain preserved in Git and audited legacy source: four-question kickoff, resumable Interview Ledger, current AI-use/friction discovery, and evidence-first reuse of accessible conversation/files/connected sources. Full MIRA 2.0 interview runtime remains queued under `FIRSTBOOT-CORE-001` / `DISCOVERY-CORE-001`; this packet does not absorb it.

## Active packet

### `M2-M1-001` — Concurrent canonical command boundary

- **Primary work:** first bounded slices of `ANDROID-CLIENT-CORE-001`
- **Related features:** `CLIENT-ANDROID-001`, `API-001`, `AUTH-001`, `STORE-001`, `RECOVERY-002`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Provider-neutral sequencer PR #54:** merged `d21869d091cbcfce609d47665ef8872123f2be43`; CI `33274374052` green.
- **Current child branch:** `integration/m1-001-workspace-worker`
- **Child base SHA:** `d21869d091cbcfce609d47665ef8872123f2be43`
- **Architecture:** `docs/M1_CONCURRENT_COMMAND_BOUNDARY.md`
- **Status:** provider-neutral sequencer merged/test-verified; synthetic Workspace Commands inbox + locked worker implemented and awaiting PR/CI. No live Google worker activation yet.

## Selected architecture

For the ordinary Personal Android lane, use a **durable Google Workspace command inbox plus one serialized Apps Script worker** rather than allowing ChatGPT and Android to mutate canonical Sheets independently.

Command flow:

`ChatGPT/Android command → Commands inbox → one ScriptLock worker → API-001 semantics → Authority → STORE-001 → exact readback → durable command result`

The worker is asynchronous. Google documents that API writes do not fire installable edit triggers, so the inbox is polled by a time-driven trigger. Google supports a one-minute trigger cadence. Cloud Run remains the synchronous advanced profile if later accepted behavior requires consistently lower latency.

## Merged provider-neutral proof

`mira/command_sequencer.py` + `tests/test_command_sequencer.py` prove:

- duplicate command identity rejected;
- concurrent stale revision-0 commands serialize so only one can commit;
- crash after canonical mutation but before queue acknowledgement retries through canonical idempotency without a second revision;
- expected revisions progress 0 → 1 → 2 under serialized execution;
- same-user authorization failure is terminal with no provider mutation.

PR #54 passed full CI and merged at `d21869d091cbcfce609d47665ef8872123f2be43`.

## Current synthetic Workspace worker slice

### `workspace/apps_script/CommandWorker.gs`

Implemented:

- dedicated 16-column `Commands` inbox carrying API-001 upsert material and durable result/error fields;
- explicit `mutation_mode=queued_writer` activation in Metadata;
- activation creates/validates exactly one one-minute Apps Script time-driven worker trigger;
- trigger validation occurs **before** queued mode becomes authoritative, so activation failure leaves direct mode intact;
- worker obtains `LockService.getScriptLock()` with bounded wait and flushes before release;
- bounded processing of at most 20 pending commands per run;
- first slice supports canonical `upsert` only;
- API/schema compatibility validation;
- persisted Authority/binding resolution and same-user subject == Authority owner check;
- STORE-001-compatible canonical request fingerprint;
- idempotency replay and same-key/different-material failure;
- stale-revision conflict handling;
- canonical Resource write + Idempotency append + exact readback;
- command success persisted only after exact readback;
- retryable authority/readback/internal failures remain pending;
- deterministic crash recovery when Resource write landed but Idempotency acknowledgement did not: Resource `last_idempotency_key` + `request_hash` + revision/payload prove the exact mutation, then the missing idempotency row is reconstructed without incrementing revision again.

This recovery protocol is intentional because SpreadsheetApp does not provide a documented cross-tab transaction for this path.

### Direct mutation side-door closed

`mira/workspace_native.py` now accepts explicit mutation mode. `direct_single_writer` remains the default M2-M0 behavior. `queued_writer` raises `WorkspaceQueuedWriterRequiredError` and instructs orchestration to submit the API-001 command to the canonical inbox. Unknown modes fail validation.

This is a MIRA software safety boundary, not a claim that a human file owner loses manual edit capability.

### Manifest / bundle

- Apps Script manifest remains current-Sheet scoped and adds only the project trigger-management scope required for the worker.
- `mira/workspace_bundle.py` now requires/validates `CommandWorker.gs`, ScriptLock, one-minute trigger construction and bounded scopes.
- `workspace/apps_script/README.md` documents direct vs queued modes, asynchronous pending semantics, API-trigger limitations, crash recovery and the evidence boundary.

### Executable tests added

`tests/apps_script/workspace_worker.test.js` provides a fake Workspace runtime with mutable Sheets, trigger management, ScriptLock and real SHA-256. It tests:

1. queued-writer activation creates Commands + exactly one one-minute trigger and is idempotent;
2. duplicate triggers fail before queued mode activation;
3. worker locks, creates revision 1, writes one idempotency record, exact-readbacks and acknowledges success;
4. two stale revision-0 commands produce one success + one terminal conflict;
5. synthetic crash after Resource write but before Idempotency append leaves command pending; retry reconstructs acknowledgement and keeps revision 1;
6. worker fails closed without queued mode and still releases ScriptLock;
7. subject/Authority-owner mismatch is terminal authorization failure with no entity mutation.

`tests/test_workspace_mutation_mode.py` verifies direct mode stays compatible, queued mode blocks native direct mutation, and unknown modes fail validation.

## Acceptance status

1. No direct multi-writer Sheets mutation — implemented/test pending CI.
2. One canonical mutation sequencer — provider-neutral proof merged; Workspace worker implemented/test pending CI.
3. Existing API/Authority/STORE semantics — preserved by sequencer/worker design.
4. Same-user authentication boundary — explicit; queued worker checks persisted Authority owner, no prompt/Sheet/URL/Git bearer secrets.
5. Replay safety — merged sequencer proof + Workspace recovery tests pending CI.
6. Stale conflict safety — merged sequencer proof + Workspace tests pending CI.
7. Restart/retry safety — merged sequencer proof + Workspace partial-write recovery tests pending CI.
8. No dual writable masters — direct native planner now fails in `queued_writer` mode; test pending CI.
9. Provider portability — Android/domain command envelope does not depend on Sheet IDs/row coordinates.
10. Synthetic first — satisfied so far; no live worker activation.
11. Legacy preservation — no legacy production touched.
12. Bounded scope — no Android UI, Gmail/Calendar fan-out, onboarding port or live Cloud Run work.

## Exact next action

1. Open PR for `integration/m1-001-workspace-worker` and run full CI.
2. Fix only worker/direct-mode/bundle defects discovered by CI.
3. Merge/read back when green.
4. Only after merge, perform a live proof against an isolated synthetic/copied MIRA 2.0 workbook: add/verify Commands inbox, enable queued mode/trigger, submit a synthetic command through Google Sheets, verify worker result and canonical provider readback, then exercise one retry/conflict path without touching legacy production.
5. Do not begin Android UI/client implementation until live queued-writer provider behavior is proven or the packet records a blocking provider defect.

## Recovery protocol

Read this file first. Verify main contains PR #54 merge `d21869d091cbcfce609d47665ef8872123f2be43` or a descendant. Continue only `M2-M1-001` on `integration/m1-001-workspace-worker` while this worker slice is unmerged. Preserve M2-M0 native Google as single-writer evidence; do not reinterpret it as safe Android concurrency. Preserve Cloud Run checkpoint without claiming live proof. Keep provider IDs, secrets, personal data and live row contents out of public Git.
