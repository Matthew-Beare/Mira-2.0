# MIRA Google Workspace first-run bundle

This directory is the copyable Google Workspace execution artifact for the default Personal MIRA path.

## Current bounded slice

Implemented now:

- bound-Sheet menu entry: **MIRA → Initialize this copy**;
- copied Sheet identity stored at runtime in Apps Script `ScriptProperties`, never hard-coded in public source;
- `/v1/health` web-app readback;
- `/v1/schema` readback against the starter `Metadata` tab;
- `/v1/query` with `action=read` only;
- persisted `authority_binding` → `authority` resolution before canonical resource reads;
- schema/version/header/identity validation and stable MIRA error codes;
- `/v1/commands` fails closed.

Not implemented in this slice:

- public deployment authorization;
- ChatGPT client authentication;
- writes, idempotency mutation, or conflict mutation behavior;
- Google provider live deployment evidence.

Do **not** publish the current read-only development slice as an anonymous production endpoint. The next slice must establish the external same-user authentication boundary before protected read/write use.

## Why initialization is required

Google documents that bound-script active-container methods such as `SpreadsheetApp.getActiveSpreadsheet()` are not available when the same script executes as a web app. The browser-only initializer therefore captures the identity of the copied Sheet while the user has it open and stores that value in `ScriptProperties`. The web runtime subsequently reopens exactly that initialized Sheet with `SpreadsheetApp.openById(...)`.

This keeps the public starter free of user spreadsheet IDs while still letting each copied Sheet bind to itself without a terminal, server, Cloud Run project, or SQL database.

## Starter state contract

The Sheet uses the same persisted MIRA structured-state layout already exercised by the Python Google Sheets adapter:

- `Metadata` — `Key`, `Value`;
- `Resources` — `resource_type`, `resource_id`, `revision`, `payload_json`, `updated_at`, `last_idempotency_key`, `request_hash`;
- later mutation slices continue to use `Events` and `Idempotency` rather than creating a second Workspace-only data model.

The starter metadata must declare `adapter_contract=STORE-001` and `writer_model=single_writer`. Canonical data-class routing is read from persisted `authority_binding` and `authority` resources.

## Portability rule

Apps Script is a Personal deployment adapter, not MIRA's product model. Canonical `API-001`, `AUTH-001`, and `STORE-001` semantics remain the migration boundary so a later Linux/SQL/Cloud Run profile can take authority through an explicit cutover rather than rewriting user data or creating dual writable masters.
