# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active provider-adapter packet and its resume point.

## Completed packet before this branch

### `M2-M0-001` — Isolated Google/MIRROR data sandbox

- **Merged PR:** #44
- **Merge SHA / main readback:** `2796562f5d1d9233141d598c9385851dd4789da9`
- **Post-merge completion checkpoint / this branch start SHA:** `ae30e8b304da097570d3d0061fd9c863b654f3ca`
- **Remote CI:** run `33211875224`; compile + feature registry + code ownership + full suite succeeded.
- **Result:** isolated MIRA 2.0 Google sandbox hierarchy is provider-verified and legacy LyfeOS resources remain untouched.

## Active packet

### `M2-M0-002` — Minimal Google structured-state adapter

- **Work ID:** `GOOGLE-STORE-ADAPTER-001`
- **Class:** provider adapter implementation / M2-M0 prerequisite
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `integration/m0-002-google-store-adapter`
- **Branch start SHA:** `ae30e8b304da097570d3d0061fd9c863b654f3ca`
- **Activation commit:** `482a42ad0c57accbd080e03d5b2c032554e56264`
- **Adapter implementation:** `dfcd41e8821a4eee2c3695fd357f00904b266c02`
- **Adapter/gateway tests:** `e5565704878317f15bdc484997b178d6e518ba9c`
- **Code ownership update:** `97893a6249846f2c319562ed15de8ca5dd1c7f3c`
- **Initial implementation checkpoint:** `e970aa504c7e7414e2580627d1c15c16b3a0c800`
- **PR:** #45
- **GitHub Actions run:** `33212406023`
- **Status:** adapter implementation/test-verified and live sandbox schema/write-readback verified; final evidence commit CI + merge remain.

## Provider resource evidence

- One native Google Sheet named `MIRROR Structured State - Synthetic` exists under the verified `Structured State` sandbox child.
- Provider metadata shows exactly four tabs: `Metadata`, `Resources`, `Events`, `Idempotency`.
- Bounded provider reads verified headers and synthetic rows.
- Imported timestamps were normalized to literal UTC strings.
- Metadata declares schema version, `STORE-001`, `resource_types_json=["entity"]`, `event_types_json=["created","updated"]`, and `writer_model=single_writer`.
- Initial provider inspection caught an event-schema defect: `stream_type` was missing. The live sandbox was repaired before adapter implementation to use `event_type,event_id,stream_type,stream_id,stream_revision,payload_json,occurred_at,idempotency_key`.
- The original seed resource/event fixture was normalized to adapter-compatible request fingerprints and idempotency result envelopes; the seed event now has an explicit idempotency record.
- Visual verification used a native-Sheets export rendered through the spreadsheet verifier. Long JSON/hash fields were initially overflowing; only the affected data-heavy columns were wrapped/widened and re-exported. Final rendered ranges are readable and the workbook has no formula-error matches.
- All provider content is generic/synthetic. Live IDs/URLs remain outside Git.

## Live provider write/readback proof

A fresh synthetic entity was exercised on the live sandbox provider surface using the same row/idempotency contract produced by the adapter:

1. **Create:** one atomic Sheets batch appended the new resource at revision 1 and its `upsert` idempotency record with the adapter-equivalent canonical request fingerprint/result envelope.
2. **Create readback:** bounded provider reads returned the exact synthetic payload, revision 1, idempotency key, request fingerprint, and result envelope.
3. **Update:** after revision-1 readback, one atomic Sheets batch replaced the same resource identity at revision 2 and appended a second `upsert` idempotency record using an expected-revision-1 fingerprint.
4. **Update readback:** bounded provider reads returned the same identity at revision 2 with the exact updated payload and matching idempotency result.
5. No legacy or personal state was involved.

### Evidence ceiling

- `GoogleSheetsStructuredStateAdapter` + `GoogleSheetsRestGateway`: **implemented/test-verified** through deterministic fake-gateway/REST request tests and the full repository CI suite.
- Live Google Sheet schema and equivalent mutation/readback contract: **provider-readback verified**.
- The Python REST gateway has **not yet executed against a live Google OAuth token**. That integration/live tier requires the managed API deployment/runtime authorization path and is not claimed here.

## Engineering boundary

M2-M0 uses a **single-writer** Google Sheets authority model. `GoogleSheetsStructuredStateAdapter` holds an adapter-local mutation lock and submits each resource/event mutation plus idempotency record as one Sheets batch. Optimistic revision/idempotency checks are exact for one writer process. Google Sheets does not provide distributed cell compare-and-swap, so multi-process/multi-writer safety is not claimed. Initial managed deployment must therefore enforce a single writer instance until a later backend/hardening packet supplies distributed concurrency control.

## Implemented component

`mira/google_sheets_store.py` provides:
- provider-neutral `SheetsGateway` and atomic `SheetRowMutation` boundary;
- stdlib `GoogleSheetsRestGateway` with runtime-injected spreadsheet ID/access-token provider and no hard-coded credential/resource identifiers;
- `GoogleSheetsStructuredStateAdapter` implementing health/schema/get/query/upsert/append-event/events-for semantics;
- exact schema/header validation;
- stable caller IDs, monotonic revisions, bounded queries, idempotency replay/material-conflict checks, stale revision checks and exact post-write readback;
- Google-specific range/tab/row behavior isolated below `STORE-001`.

`tests/test_google_sheets_store.py` covers fake-gateway contract behavior and REST request construction/bearer injection. `project/code_ownership.json` owns the module under `google-sheets-state` with direct test evidence.

## Verification evidence

PR #45 exact implementation head `e970aa504c7e7414e2580627d1c15c16b3a0c800` passed GitHub Actions run `33212406023`:
- compile: success;
- feature registry: success;
- code ownership: success;
- full unit/integration suite including new Google Sheets adapter tests: success.

This final evidence commit changes only `CURRENT_WORK.md`; it must receive a fresh exact-head CI run before merge.

## Acceptance criteria

1. One native synthetic Sheet inside verified child. **Satisfied/provider-read-back.**
2. Four tabs/schema synthetic-only. **Satisfied/provider-read-back; schema defect repaired.**
3. Gateway + adapter without committed credentials/IDs. **Implemented/test-verified.**
4. Contract semantics preserved. **Implemented/test-verified.**
5. Provider details isolated below adapter. **Implemented/test-verified.**
6. Deterministic fake-gateway tests. **Test-verified.**
7. Live synthetic create/update/readback cycle. **Satisfied at provider-surface readback tier; live Python OAuth execution explicitly pending deployment.**
8. Production ownership manifest updated. **Satisfied; ownership gate green.**
9. All CI gates green. **Satisfied on implementation head; final evidence head pending.**
10. No personal/legacy/Gmail/Calendar/scheduler/Android/deployment state. **Satisfied.**
11. Live provider IDs/URLs/account identifiers excluded from Git. **Satisfied.**
12. Bounded PR/merge/readback. **Pending final CI/merge.**

## Exact next action

1. Verify PR #45 final changed-file scope remains exactly packet files.
2. Require fresh PR-triggered compile + feature-registry + code-ownership + full-suite green on this evidence head.
3. Merge exact green head/read back `main`.
4. Checkpoint `GOOGLE-STORE-ADAPTER-001` at implemented/test-verified + provider-readback-verified, not live-OAuth-executed.
5. Activate `API-DEPLOYMENT-001` with a mandatory **single writer instance** constraint and runtime Google OAuth/token injection requirement.

## Recovery protocol

On any new conversation/session:
1. read this file first and verify branch/head;
2. rediscover sandbox resources by exact provider search when needed;
3. never commit live provider IDs/private data;
4. do not claim live Python Google execution until the deployed runtime actually performs it;
5. continue only the active packet unless a blocker forces scope change.
