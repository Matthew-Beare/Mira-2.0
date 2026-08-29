# M2-M1 Concurrent Canonical Command Boundary

**Packet:** `M2-M1-001`  
**Status:** selected architecture for deterministic implementation proof; live provider activation not yet claimed.

## Decision

When Android/shared mutation is enabled, MIRA must stop allowing independent clients to perform canonical read-then-write Google Sheets mutations. Clients submit the existing `API-001` `CommandEnvelope` to one durable command stream. Exactly one command worker owns canonical mutation sequencing.

For the ordinary Personal Google Workspace lane, the selected first implementation is a **Google Workspace durable command inbox + serialized Apps Script worker**:

1. stock ChatGPT uses its official authenticated Google Drive/Sheets connection to append a command envelope to a dedicated command inbox;
2. Android uses the user's Google OAuth connection to append the same command envelope shape;
3. Apps Script polls the inbox using an installable time-driven trigger;
4. every worker execution obtains `LockService.getScriptLock()` before it evaluates idempotency/revision state or mutates canonical state;
5. the worker executes the existing `API-001` semantics against the persisted Authority and `STORE-001` state;
6. canonical resource/idempotency mutation and exact readback remain authoritative;
7. the command row receives a terminal result only after canonical execution/readback succeeds;
8. if execution dies after a provider mutation but before queue acknowledgement, retry uses the same idempotency key and must converge to the original result rather than duplicate the mutation.

The existing managed/Cloud Run runtime remains the **synchronous advanced profile**. It is not the default Personal Android requirement unless the asynchronous Workspace worker proves insufficient for accepted user-visible behavior.

## Why the naive event-trigger design is rejected

Google's current Apps Script installable-trigger documentation explicitly states that **script executions and API requests do not cause installable triggers to run**. Therefore a command row appended by stock ChatGPT's Google Sheets action or Android's Sheets API call cannot rely on `onEdit`/installable edit triggers to start processing.

A Google-native command inbox must instead use a time-driven trigger. Google documents time-driven triggers as recurring as frequently as once per minute. The Workspace profile is therefore an asynchronous command boundary with minute-scale scheduling granularity, not a fake synchronous endpoint.

Official references:
- https://developers.google.com/apps-script/guides/triggers/installable

## Why Apps Script can serialize the worker

Google documents `LockService` as mutual exclusion for script code. `getScriptLock()` prevents simultaneous execution of a guarded section regardless of user identity, and `tryLock`/`waitLock` acquire the lock with bounded waiting. This is the correct Google-side primitive for ensuring only one worker execution evaluates revisions/idempotency and mutates shared state at a time.

Official references:
- https://developers.google.com/apps-script/reference/lock/lock-service
- https://developers.google.com/apps-script/reference/lock/lock

## Why an Apps Script web app is not the default stock-ChatGPT command transport

Apps Script web apps accept `doGet(e)`/`doPost(e)` request parameters and bodies, but the documented event object does not expose arbitrary incoming HTTP headers. The earlier M2-M0 analysis therefore rejected smuggling a bearer secret through query/body data.

Apps Script web apps can execute as the owner or as the accessing user, but that browser authorization model does not make stock ChatGPT's existing Google Drive app automatically authenticate to a custom web-app endpoint.

Official reference:
- https://developers.google.com/apps-script/guides/web

## Why Cloud Run remains advanced rather than default

The existing MIRA managed runtime is already compatible with a strict single-sequencer deployment: Cloud Run supports manual service scaling to exactly one instance and per-instance concurrency can be set to `1`. MIRA's preserved Cloud Run operator already encodes those invariants.

However, stock ChatGPT's Personal Google app is not itself a general custom-API client. Current GPT Actions can authenticate custom APIs using API keys or OAuth, but actions are a separately configured GPT surface, and current OpenAI documentation says a GPT can use apps or actions, not both. That would replace rather than transparently extend the ordinary Personal Google-app path proven in M2-M0.

Official references:
- https://docs.cloud.google.com/run/docs/configuring/services/manual-scaling
- https://docs.cloud.google.com/run/docs/about-concurrency
- https://help.openai.com/en/articles/9442513-configuring-actions-in-gpts

## Integrity model

The command inbox is **not** canonical state. It is a durable request transport.

Canonical state remains:

`client command → single sequencer → API-001 → Authority Registry → STORE-001 authority → exact provider readback`

Rules:

- A command ID is stable and cannot be queued twice as two logical commands.
- Idempotency is enforced by canonical `STORE-001`, not by queue row position.
- Same command/material retried after a crash returns the original mutation result without a second provider mutation.
- Same idempotency key with different material fails closed.
- Two commands with the same stale expected revision are serialized; after the first succeeds, the second conflicts rather than overwriting it.
- Queue success is recorded only after canonical exact readback succeeds.
- Provider/readback failures remain retryable; deterministic validation/authorization/conflict failures may become terminal command results.
- Client surfaces must not perform direct canonical mutation while queued-writer mode is active.
- Queue row numbers, sheet IDs and Google-specific transport details never become Android/domain identity.

## Authentication boundary

This packet remains same-user only.

- Stock ChatGPT: official Google Drive/Sheets OAuth connection to the user's Workspace account.
- Android: Google OAuth for the same user's command-inbox access; Android credentials stay in OS-protected storage when that client is implemented.
- Worker: bound Apps Script executes under the user's authorized script context.
- Cross-person/family access remains blocked until `PERMISSION-SCOPE-001`.

The queue transport proves same-user command submission, not cryptographically distinct client identity. `client_id` may be retained for provenance but is not treated as an authorization grant in the Personal same-user worker.

## Operational tradeoff

The zero-infrastructure Workspace worker deliberately trades synchronous mutation latency for ordinary-user deployability. A command can remain pending until the next trigger run. The Android UI must represent `pending` honestly and use its replay-safe offline/reconnect queue rather than pretending a mutation committed immediately.

If later acceptance criteria require consistently synchronous sub-minute canonical writes, the already-built managed API/Cloud Run profile is the upgrade candidate. That is an Authority/execution migration, not a new MIRA data model.

## Deterministic proof before live Google changes

`mira/command_sequencer.py` and `tests/test_command_sequencer.py` prove the provider-neutral critical behavior before a live Workspace worker is enabled:

- duplicate command identity rejected;
- concurrent worker calls serialize;
- two stale-revision commands cannot both commit;
- crash after canonical mutation but before queue acknowledgement retries through idempotency without duplicate mutation;
- sequential expected revisions progress correctly;
- same-user authorization failure is terminal and provider state remains unchanged.

## Next implementation slice

Implement the Google Workspace transport that maps this contract onto a `Commands` inbox and `LockService.getScriptLock()` worker. The first Apps Script slice must:

1. add/validate a dedicated command inbox schema without weakening canonical state tabs;
2. add queued-writer activation state so native ChatGPT direct mutation fails closed once Android/shared mode is enabled;
3. install or validate a one-minute time-driven worker trigger without depending on API-written edit triggers;
4. process a bounded number of commands under one script lock;
5. preserve API-001 compatibility, expected revision and idempotency behavior;
6. persist terminal command results only after exact canonical readback;
7. prove crash/retry recovery in executable fake-Apps-Script tests;
8. stay synthetic until all tests are green.
