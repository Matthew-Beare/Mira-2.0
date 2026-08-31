# MIRA Google Workspace first-run bundle

This directory is the copyable Google Workspace execution artifact for the default Personal MIRA path.

## Complete stock-ChatGPT operating instructions

`MIRA_NO_APP_INSTRUCTIONS.md` is the complete source-backed Personal no-app operating-instruction block. It is part of the validated release bundle, not an optional example or a fragment to splice into older instructions.

For a stock-ChatGPT Personal deployment, the entire current Personal MIRA operating-instruction block is replaced with that file's complete contents. The protocol defines canonical Workspace preflight/readback, safe direct-single-writer mutation, the four-question resumable Interview Ledger, intent-first optional-provider activation, and fail-closed behavior when a provider capability or shared-writer path has not actually been verified.

Bundle validation fails if safety-critical protocol clauses disappear, so the copyable Workspace artifact and the instructions that operate it cannot silently drift apart.

## Default Personal mode

A normal stock-ChatGPT Personal setup remains **zero infrastructure**:

1. copy the official MIRA Workspace starter;
2. authorize/connect the Google services the user actually chooses to use;
3. choose **MIRA → Initialize this copy** once for the MIRA Sheet;
4. replace the Personal MIRA operating-instruction block with the complete `MIRA_NO_APP_INSTRUCTIONS.md` contents;
5. use stock ChatGPT's official connected Google capabilities against that user's canonical MIRA state.

Copying the official Google Sheet also copies its default container-bound Apps Script. Ordinary users are not expected to copy script files, deploy Apps Script manually, use `clasp`, configure a Google Cloud project, or paste provider IDs.

In this baseline, MIRA is intentionally `direct_single_writer`: stock ChatGPT is the only software writer. The native Google protocol preserves Authority, revision, idempotency and exact provider-readback semantics without requiring Cloud Run, Linux, SQL, a terminal, or paid OpenAI API usage.

## Intent-first provider activation

Optional features are activated from ordinary-language user intent, not from developer setup screens.

For Calendar the intended interaction is conceptually:

- user: **“Yes, use my calendar.”**
- MIRA: surface the provider's own authorization/connection UI only if Google still requires it;
- after authorization: MIRA discovers the usable Calendar capability, binds the safe selected/default lane according to policy, and performs its own verification.

Calendar is not authorized during unrelated MIRA Sheet setup. A normal user is never asked to create a secondary Calendar, copy Calendar IDs, edit OAuth scopes, open Apps Script, paste code, or use a terminal merely to activate Calendar.

The default Personal Google Calendar lane uses stock ChatGPT's native Google Calendar connector and is explicitly single-writer. MIRA-created events carry a stable trailing `MIRA-PROJECTION-ID:` marker for lost-create-acknowledgement recovery while canonical MIRA state retains the exact provider event ID. Identical replay resolves the exact tracked provider event instead of creating a duplicate.

Before changing a tracked event, MIRA reads the exact persisted provider event ID and compares the provider material with its last verified canonical state. Manual/provider drift fails closed rather than being overwritten. After mutation, MIRA performs exact independent provider readback before canonical success.

The native update surface currently does not expose an atomic ETag/`If-Match` argument. Its protection mode is therefore explicitly `single_writer_preflight_non_atomic`. It is suitable for the default stock-ChatGPT Personal single-writer lane, not concurrent Android/shared-writer Calendar mutation.

The stronger Apps Script Calendar adapter is not part of the default Personal starter. Its MIRA-owned secondary-Calendar bootstrap, private extended properties and atomic ETag `If-Match` path remain source-controlled optional hardening for a later shared-writer/provider profile. It must not make ordinary Personal users perform extra setup or grant Calendar permissions before they ask to use Calendar.

This intent-first rule applies across optional providers and features: ordinary-language yes/no first, provider-native consent when unavoidable, then MIRA performs the technical setup it can safely automate.

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

- **MIRA → Initialize this copy** browser action for the copied structured-state Sheet;
- copied Sheet identity stored at runtime in Apps Script `ScriptProperties`, never hard-coded in public source;
- `/v1/health` web-app readback;
- `/v1/schema` readback against the starter `Metadata` tab;
- `/v1/query` with `action=read` only;
- persisted `authority_binding` → `authority` resolution before canonical resource reads;
- schema/version/header/identity validation and stable MIRA error codes;
- `/v1/commands` fails closed.

Optional providers such as Calendar are deliberately absent from this menu. Their activation begins from MIRA conversation and provider-native consent, not by teaching the user where implementation controls live.

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

The default public Apps Script manifest is intentionally bounded to:

- `spreadsheets.currentonly` for the copied MIRA Sheet;
- `script.scriptapp` for bounded trigger management used by queued-writer mode.

It does **not** pre-request Calendar or external-request scopes. Optional provider permission belongs to the moment the user actually chooses that provider. Calendar authorization is handled through the native connected Calendar capability for the default Personal lane.

No account/provider identifier or long-lived credential is stored in source.

## Template publication boundary

The source-controlled bundle is the release authority for the default Apps Script code and manifest. A public/official starter template must be refreshed from a verified release before it is presented to ordinary users. Copying a spreadsheet preserves its attached bound scripts, so once the official template contains the verified release, user installation is a normal Sheet copy rather than a script-deployment procedure.

Maintainer/template publication evidence is separate from ordinary-user installation evidence. MIRA must not claim a Drive template contains a particular Git release merely because its sheet cells look correct; the bound-script release must be verified before that template becomes the canonical public starter.

## Evidence boundary

The native Calendar adapter, stronger optional Calendar adapter, and queued-writer implementation are tested synthetically before their respective live-provider claims. Code existence or fake-provider tests do **not** count as live provider proof. Legacy MIRA production Sheets and Calendars remain protected and are never development fixtures.

Likewise, validating `MIRA_NO_APP_INSTRUCTIONS.md` proves the stock-ChatGPT operating contract is source-controlled and internally consistent; it does not by itself prove every current connector surface can execute every mutation. Provider behavior is upgraded to live evidence only after the exact provider operations actually required by that lane are verified.

## Portability rule

Apps Script and native Google connections are Personal execution adapters, not MIRA's product model. Canonical `API-001`, `AUTH-001`, and `STORE-001` semantics remain the migration boundary so a later Cloud Run/Linux/SQL profile can take execution/authority through an explicit cutover rather than rewriting user data or creating dual writable masters.
