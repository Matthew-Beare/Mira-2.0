# MIRA Google Workspace first-run bundle

This directory is the copyable Google Workspace execution artifact for the default Personal MIRA path.

## Complete stock-ChatGPT operating instructions

`MIRA_NO_APP_INSTRUCTIONS.md` is the complete source-backed Personal no-app operating-instruction block. It is part of the validated release bundle, not an optional example or a fragment to splice into older instructions.

For a stock-ChatGPT Personal deployment, the entire current Personal MIRA operating-instruction block is replaced with that file's complete contents. The protocol defines canonical Workspace preflight/readback, safe direct-single-writer mutation, the four-question resumable Interview Ledger, explicit appointment-service intent, and fail-closed behavior when a provider capability or shared-writer path has not actually been verified.

Bundle validation fails if safety-critical protocol clauses disappear, so the copyable Workspace artifact and the instructions that operate it cannot silently drift apart.

## Default Personal mode

A normal stock-ChatGPT Personal setup remains **zero infrastructure**:

1. copy the official MIRA Workspace starter;
2. authorize/connect Google;
3. choose **MIRA → Initialize this copy** once;
4. replace the Personal MIRA operating-instruction block with the complete `MIRA_NO_APP_INSTRUCTIONS.md` contents;
5. use stock ChatGPT's official Google Drive/Sheets connection against that user's canonical MIRA state.

Copying the official Google Sheet also copies its container-bound Apps Script. Ordinary users are not expected to copy script files, deploy Apps Script manually, use `clasp`, configure a Google Cloud project, or paste provider IDs.

In this baseline, MIRA is intentionally `direct_single_writer`: stock ChatGPT is the only software writer. The existing native Google protocol preserves Authority, revision, idempotency and exact provider-readback semantics without requiring Cloud Run, Linux, SQL, a terminal, or paid OpenAI API usage.

## One-click Calendar activation

Calendar support is opt-in. When the user has requested Google Calendar support, the copied starter exposes **MIRA → Enable Calendar**.

The ordinary-user flow is:

1. choose **MIRA → Enable Calendar**;
2. approve Google's required authorization screen if prompted;
3. MIRA creates or safely recovers one dedicated secondary Calendar named `MIRA`.

The user does **not** manually create a secondary calendar, copy a Calendar ID, edit OAuth scopes, open the Apps Script editor, or configure Calendar API details.

The managed Calendar bootstrap is deliberately isolated from Primary, Family and legacy calendars. Before provider creation MIRA persists a local installation UUID. The created Calendar carries the corresponding ownership marker in its description. If provider creation succeeds but the acknowledgement is lost before the Calendar ID is stored, MIRA uses a read-only CalendarList scan to recover the unique matching managed Calendar instead of creating a duplicate. Ambiguous ownership markers, a missing previously stored managed Calendar, or ownership/name drift fail closed.

Calendar event projection then uses private extended properties for stable MIRA projection/idempotency identity, exact provider GET readback, and Google ETags with `If-Match` for guarded updates. It does not add attendees, send attendee notifications, create Meet links, or infer appointment/medical meaning.

## Shared / Android queued-writer mode

When Android or another software writer is enabled, MIRA must **stop direct native canonical mutation**. Two independent Google Sheets read-then-write clients are not a safe concurrency model, no matter how politely they promise not to collide.

`CommandWorker.gs` adds the first zero-infrastructure shared-writer profile:

- dedicated `Commands` inbox containing API-001 command envelopes and durable results;
- `mutation_mode=queued_writer` persisted in `Metadata` when the user explicitly activates shared-writer mode;
- one Apps Script time-driven worker trigger, scheduled every minute;
- one `LockService.getScriptLock()` critical section around command preflight, canonical mutation and readback;
- bounded processing per run;
- stale revision and idempotency conflicts fail closed;
- same-user subject must match the persisted canonical Authority owner;
- command success is written only after exact canonical resource + idempotency readback;
- retryable provider/readback/internal failures leave the command pending;
- crash recovery uses the canonical Resource row's `last_idempotency_key` + `request_hash` to reconstruct a missing idempotency acknowledgement without incrementing the resource revision again.

The queue is **transport, not canonical state**. Canonical mutation still resolves through the same MIRA Authority / STORE-001 model.

### Why it polls instead of using `onEdit`

Google documents that API requests and script executions do not fire installable edit triggers. Commands written by stock ChatGPT's Google Sheets action or a future Android Google API client therefore cannot depend on `onEdit` waking the worker.

The Personal zero-infrastructure worker uses a time-driven trigger instead. Google permits time-driven triggers as frequently as once per minute, so queued-writer mode is explicitly **asynchronous**. A client must represent `pending` honestly instead of pretending a command committed immediately.

### Why `/v1/commands` still fails closed

The bound Apps Script web app is not the stock-ChatGPT authentication boundary. Its documented request event does not expose arbitrary inbound HTTP headers, and MIRA will not hide bearer secrets in query strings, request bodies, visible Sheet cells, prompt text, or public Git.

Stock ChatGPT submits Personal commands through its official authenticated Google connection. `CommandWorker.gs` processes the durable inbox internally. `/v1/commands` therefore remains closed in this Workspace web-app slice.

## Browser initialization

Implemented in `Code.gs`:

- **MIRA → Initialize this copy** browser action;
- **MIRA → Enable Calendar** opt-in Calendar action;
- copied Sheet identity stored at runtime in Apps Script `ScriptProperties`, never hard-coded in public source;
- `/v1/health` web-app readback;
- `/v1/schema` readback against the starter `Metadata` tab;
- `/v1/query` with `action=read` only;
- persisted `authority_binding` → `authority` resolution before canonical resource reads;
- schema/version/header/identity validation and stable MIRA error codes;
- `/v1/commands` fails closed.

Google documents that bound-script active-container methods such as `SpreadsheetApp.getActiveSpreadsheet()` are not available when the same script executes as a web app. The browser initializer captures the copied Sheet identity while it is open and stores it in `ScriptProperties`. Later executions reopen only that initialized Sheet using `SpreadsheetApp.openById(...)`.

## Starter state contract

The bundle continues the same persisted MIRA structured-state model used by the Python Google Sheets adapter:

- `Metadata` — `Key`, `Value`;
- `Resources` — `resource_type`, `resource_id`, `revision`, `payload_json`, `updated_at`, `last_idempotency_key`, `request_hash`;
- `Events` — append-only event material;
- `Idempotency` — canonical replay results;
- `Commands` — noncanonical queued API-001 request/result transport, created when queued-writer mode is activated.

The starter metadata declares `adapter_contract=STORE-001` and `writer_model=single_writer`. Canonical data-class routing is read from persisted `authority_binding` and `authority` resources.

## Authorization scopes

The public Apps Script manifest is intentionally bounded to:

- `spreadsheets.currentonly` for the copied MIRA Sheet;
- `script.scriptapp` for bounded trigger management used by queued-writer mode;
- `script.external_request` for Google Calendar REST calls from the bound script;
- `calendar.app.created` so MIRA can create/manage the Calendar and events created by MIRA itself;
- `calendar.calendarlist.readonly` only to recover a uniquely marked MIRA-owned Calendar after a lost creation acknowledgement.

The release validator rejects broad `calendar`, blanket `calendar.events`, and `calendar.calendars` scopes. No account/provider identifier or long-lived credential is stored in source.

## Template publication boundary

The source-controlled bundle is the release authority for Apps Script code and its manifest. A public/official starter template must be refreshed from a verified release before it is presented to ordinary users. Copying a spreadsheet preserves its attached bound scripts, so once the official template contains the verified release, user installation is a normal Sheet copy rather than a script-deployment procedure.

Maintainer/template publication evidence is separate from ordinary-user installation evidence. MIRA must not claim a Drive template contains a particular Git release merely because its sheet cells look correct; the bound-script release must be verified before that template becomes the canonical public starter.

## Evidence boundary

The queued-writer implementation and Calendar adapter are tested synthetically before any live Google activation. Code existence or fake-Apps-Script tests do **not** count as live provider proof. Legacy MIRA production Sheets and Calendars remain protected and are never test fixtures.

Likewise, validating `MIRA_NO_APP_INSTRUCTIONS.md` proves the stock-ChatGPT operating contract is source-controlled and internally consistent; it does not by itself prove every current ChatGPT connector surface can execute every mutation. Provider behavior is upgraded to live evidence only after exact read/write/readback proof against isolated MIRA-owned Workspace state.

## Portability rule

Apps Script and the native Google connection are Personal execution adapters, not MIRA's product model. Canonical `API-001`, `AUTH-001`, and `STORE-001` semantics remain the migration boundary so a later Cloud Run/Linux/SQL profile can take execution/authority through an explicit cutover rather than rewriting user data or creating dual writable masters.
