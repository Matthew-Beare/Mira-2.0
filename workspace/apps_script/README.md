# MIRA Google Workspace first-run bundle

This directory is the copyable Google Workspace execution artifact for the default Personal MIRA path.

## Default Personal mode

A normal stock-ChatGPT Personal setup remains **zero infrastructure**:

1. copy the MIRA Workspace starter;
2. authorize/connect Google;
3. initialize the copied Sheet;
4. use stock ChatGPT's official Google Drive/Sheets connection against that user's canonical MIRROR state.

In this baseline, MIRA is intentionally `direct_single_writer`: stock ChatGPT is the only software writer. The existing native Google protocol preserves Authority, revision, idempotency and exact provider-readback semantics without requiring Cloud Run, Linux, SQL, a terminal, or paid OpenAI API usage.

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

- the current spreadsheet;
- this Apps Script project's trigger-management scope, required to install/verify the time-driven command worker.

No account/provider identifier or long-lived credential is stored in source.

## Evidence boundary

The queued-writer implementation is tested synthetically before any live Google worker activation. Code existence or fake-Apps-Script tests do **not** count as live provider proof. Legacy MIRA production Sheets remain protected and are never test fixtures.

## Portability rule

Apps Script is a Personal execution adapter, not MIRA's product model. Canonical `API-001`, `AUTH-001`, and `STORE-001` semantics remain the migration boundary so a later Cloud Run/Linux/SQL profile can take execution/authority through an explicit cutover rather than rewriting user data or creating dual writable masters.
