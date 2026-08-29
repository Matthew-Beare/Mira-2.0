# Personal Google starter distribution proof

Date: 2026-08-29

Packet: `M2-M0-010`

This evidence uses a newly created synthetic Google spreadsheet. It does not use, copy, mutate, rename, or migrate any legacy MIRA production artifact. No Google resource identifier is committed here.

## Source contract under test

The spreadsheet substrate was created from `distribution/personal_google_starter.json` on the packet branch, rather than by copying the prior hand-maintained clean template.

The source definition requires:

- spreadsheet title `MIRA Personal Starter` during verification;
- neutral spreadsheet timezone `Etc/UTC`;
- exactly four tabs: `Metadata`, `Resources`, `Events`, `Idempotency`;
- exact STORE-001 headers for each tab;
- exact clean Metadata seed values;
- zero mutable data rows in `Resources`, `Events`, and `Idempotency` before Personal bootstrap.

## Provider actions

1. Created a new blank native Google spreadsheet.
2. In one Sheets batch, set the release-verification title/timezone, renamed the default tab to `Metadata`, created `Resources`, `Events`, and `Idempotency`, and wrote only the Git-defined Metadata/header material.
3. Read all four bounded ranges back from Google.
4. After successful verification, renamed the synthetic proof file so it cannot be mistaken for an installable clean starter.

## Exact provider readback

Google readback confirmed:

- spreadsheet timezone: `Etc/UTC`;
- tab order: `Metadata`, `Resources`, `Events`, `Idempotency`;
- Metadata headers: `Key`, `Value`;
- Metadata values:
  - `schema_version=mira-structured-state-v1`
  - `store_role=personal_google_starter`
  - `environment=mira_2_personal_clean`
  - `data_policy=clean_starter_only`
  - `adapter_contract=STORE-001`
  - `resource_types_json=["authority","authority_binding","entity","onboarding_ledger","service_state"]`
  - `event_types_json=["created","updated"]`
  - `writer_model=single_writer`
- Resources headers: `resource_type`, `resource_id`, `revision`, `payload_json`, `updated_at`, `last_idempotency_key`, `request_hash`;
- Events headers: `event_type`, `event_id`, `stream_type`, `stream_id`, `stream_revision`, `payload_json`, `occurred_at`, `idempotency_key`;
- Idempotency headers: `idempotency_key`, `operation`, `request_hash`, `result_json`, `created_at`, `resource_ref`;
- no non-header rows in `Resources`, `Events`, or `Idempotency`.

Result: **spreadsheet substrate live-verified against the source blueprint.**

## Bound Apps Script evidence boundary

The connected Google Drive/Sheets capability used for this proof can create a native spreadsheet and issue Sheets `batchUpdate` requests, but it does not expose creation of a bound Apps Script project from source files. Therefore this proof does **not** claim source-to-provider installation of the bound Apps Script bundle.

The Apps Script files remain source-controlled and CI-validated through `mira.workspace_bundle`. Browser/provider installation of that bound project belongs to the broader ordinary-user installer/provider-onboarding work (`NONTECH-INSTALL-001` and related provider capability work). This boundary does not block proving the canonical spreadsheet starter itself is reproducible from Git.

## Legacy-data safety

The proof contains synthetic schema material only. It contains no user identity, personal state, provider credentials, legacy spreadsheet contents, email, calendar data, account identifiers, or other production data.
