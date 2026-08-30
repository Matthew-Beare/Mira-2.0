# No-app task Ops Brief provider proof

Date: 2026-08-29

Packet: `M2-M0-011`

This evidence uses a newly created isolated synthetic Google spreadsheet. It does not copy, mutate, rename, repurpose, or migrate any legacy MIRA production artifact. No provider resource identifier is committed here.

## Scope

The proof verifies the first task-centered no-app Ops Brief state against Google Workspace:

- expanded Personal starter schema includes `task` and `ops_brief_run`;
- one verified synthetic Google Sheets authority is referenced by explicit bindings for both data classes;
- one canonical open task persists with stable ID/revision, exact payload and exact idempotency request hash;
- one canonical AM Ops Brief run persists with deterministic run ID, exact task revision input, exact rendered text, deterministic source fingerprint and `delivered=false`;
- matching Idempotency records persist for authority, bindings, task and brief run;
- exact Google readback confirms all material state.

This proof does **not** claim that a scheduler or platform notification fired. It proves canonical state plus brief composition/checkpoint persistence only.

## Synthetic task

The proof task used:

- stable task ID `task-provider-proof`;
- title `Synthetic provider proof task`;
- next action `Install the synthetic replacement filter.`;
- priority `high`;
- state `open`;
- context `home`;
- due date `2026-08-30`;
- revision `1`.

The canonical create request hash was independently calculated from the compact sorted-key STORE-001 upsert material and persisted in both Resources and Idempotency. Google readback matched the exact hash and payload.

## Synthetic Ops Brief run

The proof run used:

- run ID `ops-brief:2026-08-30:am`;
- slot `am`;
- authoritative timezone `America/Chicago`;
- scheduled local time `2026-08-30T02:45:00-05:00`;
- scheduled UTC time `2026-08-30T07:45:00+00:00`;
- context `home`;
- input task ID `task-provider-proof` at revision `1`;
- status `composed`;
- delivered `false`.

Rendered text read back from Google:

```text
MIRA Ops Brief — 2026-08-30 AM
Context: HOME

Tasks
- [HIGH] [DUE TODAY] Synthetic provider proof task: Install the synthetic replacement filter.
```

The run source fingerprint and STORE-001 request hash were persisted and read back exactly. The corresponding Idempotency result points to the same canonical `ops_brief_run` resource at revision 1.

## Authority/readback result

Google readback confirmed:

- clean Metadata uses the expanded resource set `authority`, `authority_binding`, `entity`, `onboarding_ledger`, `ops_brief_run`, `service_state`, `task`;
- `authority_binding/binding-task` routes `task` to the synthetic Personal Google authority;
- `authority_binding/binding-ops-brief-run` routes `ops_brief_run` to the same authority;
- task and brief resource rows match their expected stable IDs, revisions, payloads and request hashes;
- Idempotency rows match the expected operation, request hash, result JSON and resource reference;
- brief state explicitly remains `delivered=false`.

Result: **Google-backed canonical task state and composed Ops Brief run are provider-readback verified for the bounded first no-app vertical.**

## Safety / production boundary

The provider proof contains synthetic data only. After verification the spreadsheet was renamed so it cannot be mistaken for an installable clean starter. The proof does not use or expose legacy production data, personal user state, credentials, email/calendar contents, account identifiers, or private third-party information.
