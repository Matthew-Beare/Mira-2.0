# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and its exact recovery point.

## Product deployment invariant

Default Personal MIRA is **Google Workspace first, zero infrastructure**. An ordinary user starts with Google Drive/Docs/Sheets and browser-managed Google authorization. Linux, SQL, Cloud Run, containers, tunnels and local services are advanced upgrade paths.

Canonical ladder:
1. Personal Google Workspace: Sheets as first structured MIRROR authority; stock ChatGPT uses its authenticated Google Drive/Sheets connection; bound Apps Script handles embedded Google-side initialization/automation where useful.
2. Advanced profiles: Cloud Run, Linux VM, containers, SQL/local services.
3. Migration preserves `API-001`, `AUTH-001`, `STORE-001`; backend changes are explicit Authority/adapter cutovers, never dual writable masters.

## Preserved displaced packet

### `M2-M0-005` — Cloud Run credential + live Google deployment proof
- Related work: `API-DEPLOYMENT-001B`.
- Paused/deprioritized; not failed/deleted.
- PR #48 merged `acb37af4aa378e8128d8591406859fe954af3474`; CI `33217543700` green.
- PR #49 merged `3332081054d691eca646c1d7bb274d22096f1c62`; CI `33218561781` green.
- Pre-pivot checkpoint: `c392b9b829fab989be8856c9272294c9907e409e`.
- No live Cloud Run evidence claimed.

## Active packet

### `M2-M0-006` — Google Workspace zero-infrastructure first run

- Primary work: `API-DEPLOYMENT-001A`
- Adjacent client work: `CHATGPT-API-CLIENT-001`
- Repository: `Matthew-Beare/Mira-2.0`
- Read-only Workspace PR #50 merged at `e412405a475d1423edaac821d7a99481e4a6eb4b`; CI `33243206658` green.
- Main native-client checkpoint: `682b519483578cca2dc7343e96c0892c0ec666fd`.
- Active protocol branch: `integration/m0-006-native-google-protocol`
- Branch start: `682b519483578cca2dc7343e96c0892c0ec666fd`
- Current implementation head before this checkpoint: `213f179ec243d4bda6d1768e7c65d79c81610964`
- Status: native stock-ChatGPT Google Sheets live roundtrip is provider-verified for the single-writer Personal lane; deterministic protocol code/tests are implemented on the active branch and awaiting PR/CI.

## Objective

Prove the ordinary-user Personal MIRA path without infrastructure administration. Stock ChatGPT uses the user's authenticated Google Drive/Sheets connection to access canonical MIRROR state. Google-specific behavior must preserve the same Authority, revision, idempotency and exact-readback semantics already defined by MIRA.

Target first use: **copy starter → connect/authorize Google → initialize MIRA → use MIRA in ChatGPT**.

## Acceptance criteria

1. No server, Cloud Run, Linux/SQL, tunnel, terminal or paid OpenAI API required for Personal baseline.
2. Copyable Workspace starter contains no live personal IDs/secrets in public source.
3. Google path preserves `API-001`/`AUTH-001`/`STORE-001`; no second Google-only product model.
4. Persisted Authority remains canonical; model/client does not become a second authority.
5. Authentication uses official same-user Google connection; no bearer hidden in Sheet cells/query/body/Git.
6. Synthetic Google roundtrip: create, exact readback, replay preflight, revision-checked mutation, exact readback.
7. Baseline setup remains browser-only.
8. Legacy production Google artifacts remain untouched.
9. Later Linux/SQL/Cloud Run cutover remains portable through `AUTHORITY-MIGRATION-001`.
10. Cloud Run remains nonblocking advanced hardening.

## Completed evidence

### Embedded Workspace slice
PR #50 merged/test-verified:
- copy-bound `MIRA → Initialize this copy` Apps Script flow;
- runtime-only Sheet identity in Script Properties;
- health/schema/read-only query and persisted Authority resolution;
- commands fail closed;
- executable Node Apps Script tests + Python bundle/privacy tests;
- CI `33243206658` green.

### Native stock-ChatGPT client/auth decision
Current stock ChatGPT Google Drive/Sheets actions provide the authenticated same-user client boundary. Personal MIRA therefore does **not** need an Apps Script public API endpoint for stock ChatGPT. This avoids Apps Script's lack of arbitrary incoming request-header access and avoids insecure URL/body secrets.

### Live native Google provider proof — passed
Against only the isolated synthetic MIRROR workbook:
- exact workbook grounded by search + metadata;
- `Metadata`, `Resources`, `Idempotency` read before mutation;
- `STORE-001`, `single_writer`, schema, verified/enabled Google Authority and the `entity` Authority binding read back correctly;
- a fresh synthetic entity identity and idempotency key were proven absent before create;
- create wrote the resource row and idempotency row in one Sheets `batchUpdate`;
- exact provider readback returned revision 1 and exactly one matching idempotency record;
- replay preflight found the same key + same request hash, so the correct replay result is **zero additional writes**;
- revision 1 was re-read immediately before update;
- update replaced the resource with revision 2 and appended its idempotency record in one `batchUpdate`;
- exact provider readback returned revision 2 and the two expected unique idempotency records;
- no legacy production artifact was touched.

No spreadsheet ID or private live row content is committed to Git.

Google documents `spreadsheets.batchUpdate` as atomic: dependent subrequests succeed together or the batch fails without applying them. This protects the resource+idempotency pair within each mutation. It does **not** make a separate read-then-write sequence a distributed compare-and-swap.

### Concurrency boundary
The native connector proof is intentionally **single writer**. Preflight revision/idempotency checks plus atomic mutation are sufficient for the Personal M2-M0 path while one MIRA writer owns mutation. They do not prove safe concurrent Android/multi-client writers. A stronger execution boundary is required before enabling multi-writer clients.

## Protocol implementation on active branch

`mira/workspace_native.py` now provides a deterministic connector-side contract:
- exact STORE-001-compatible upsert request fingerprint;
- duplicate resource/idempotency detection;
- same-key/same-material replay returns a read-only plan with zero batch requests;
- same key/different material fails with idempotency conflict;
- stale expected revision fails closed;
- create/update plans preserve revision semantics;
- runtime-grounded Sheets IDs are converted into one atomic resource+idempotency `batchUpdate` request list;
- exact post-write resource/idempotency readback verification.

`tests/test_workspace_native.py` verifies:
- fingerprint parity with the live proof and existing Google adapter;
- create row/idempotency material parity with `GoogleSheetsStructuredStateAdapter`;
- correct update row targeting and revision increment;
- replay produces zero writes;
- idempotency/revision/duplicate-identity conflicts fail closed;
- exact readback mismatch fails closed.

`project/code_ownership.json` assigns the protocol to `workspace-native-client` under `CHATGPT-API-CLIENT-001`.

## Scope control

Do not fan out into Gmail, Calendar, scheduler, Ops Briefs, family sharing, Android, enterprise, Linux/SQL implementation or Cloud Run. Do not touch legacy production artifacts.

## Exact next action

1. Open PR for `integration/m0-006-native-google-protocol` and run full CI.
2. Fix protocol defects only; do not broaden scope.
3. Merge/read back when green.
4. Update `BACKLOG.md` so `CHATGPT-API-CLIENT-001` records native Google Workspace as the M2-M0 stock-ChatGPT client path and `API-DEPLOYMENT-001A` records the live single-writer provider proof.
5. Then implement only the remaining copyable starter/bootstrap mechanics required for a new ordinary user to obtain the same canonical Sheet state without terminal work.

## Recovery protocol

Read this file first. Verify `main` contains PR #50 merge `e412405a475d1423edaac821d7a99481e4a6eb4b` and native-client checkpoint `682b519483578cca2dc7343e96c0892c0ec666fd` or descendants. If the native protocol PR is open, continue `integration/m0-006-native-google-protocol`; if merged, reconcile backlog and start only the remaining first-run packaging slice. Preserve Cloud Run checkpoint `c392b9b829fab989be8856c9272294c9907e409e`. Keep provider IDs, secrets, personal data and live row contents out of public Git.
