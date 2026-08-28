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
- **Status:** provider schema grounded/corrected; adapter/test content committed; remote CI and live mutation proof next.

## Provider resource evidence

- One native Google Sheet named `MIRROR Structured State - Synthetic` was created from a synthetic-only workbook and moved under the verified `Structured State` sandbox child.
- Provider metadata shows exactly four tabs: `Metadata`, `Resources`, `Events`, `Idempotency`.
- Bounded provider reads verified headers and seed synthetic rows.
- Imported ISO timestamp cells were normalized back to literal UTC strings after conversion had treated them as spreadsheet serial dates.
- Metadata was extended with `resource_types_json=["entity"]`, `event_types_json=["created","updated"]`, and `writer_model=single_writer`.
- The first bounded read exposed a schema defect: `Events` had `stream_id` but no `stream_type`. The live sandbox schema was corrected to the eight-column event contract `event_type,event_id,stream_type,stream_id,stream_revision,payload_json,occurred_at,idempotency_key` before adapter implementation.
- All provider content remains generic/synthetic. Live IDs/URLs are intentionally omitted from Git.

## Engineering boundary

M2-M0 uses a **single-writer** Google Sheets authority model. `GoogleSheetsStructuredStateAdapter` holds an adapter-local mutation lock and submits each resource/event mutation plus idempotency record as one Sheets batch. Optimistic revision/idempotency checks are exact for one writer process. Google Sheets does not provide distributed cell compare-and-swap, so multi-process/multi-writer safety is not claimed and must be hardened before any deployment topology that permits concurrent independent writers.

## Implemented component

`mira/google_sheets_store.py` provides:
- provider-neutral `SheetsGateway` and atomic `SheetRowMutation` boundary;
- stdlib `GoogleSheetsRestGateway` with runtime-injected spreadsheet ID/access-token provider and no hard-coded credential/resource identifiers;
- `GoogleSheetsStructuredStateAdapter` implementing health/schema/get/query/upsert/append-event/events-for semantics;
- exact schema/header validation;
- stable caller IDs, monotonic revisions, bounded queries, idempotency replay/material-conflict checks, stale revision checks and exact post-write readback;
- Google-specific range/tab/row behavior isolated below `STORE-001`.

`tests/test_google_sheets_store.py` covers fake-gateway contract behavior and REST request construction/bearer injection. `project/code_ownership.json` owns the new module under component `google-sheets-state` with direct test evidence.

## Acceptance criteria status

1. One native synthetic Sheet inside verified child. **Provider-created/read-back.**
2. Four tabs/schema synthetic-only. **Provider-read-back; Events schema defect corrected.**
3. Gateway + adapter without committed credentials/IDs. **Implemented.**
4. Contract semantics preserved. **Test content committed; remote CI pending.**
5. Provider details isolated below adapter. **Implemented.**
6. Deterministic fake-gateway tests. **Committed; remote CI pending.**
7. Live synthetic create/update/readback cycle. **Pending.**
8. Production ownership manifest updated. **Committed.**
9. All CI gates green. **Pending.**
10. No personal/legacy/Gmail/Calendar/scheduler/Android/deployment state. **Satisfied.**
11. Live provider IDs/URLs/account identifiers excluded from Git. **Satisfied.**
12. Bounded PR/merge/readback. **Pending.**

## Exact next action

1. Open a bounded PR and let compile/feature-registry/code-ownership/full tests validate the implementation.
2. Fix only packet-scoped failures; do not weaken existing contract/gates.
3. After code is green, exercise the equivalent create -> read -> update -> replay/conflict readback sequence against the live sandbox Sheet using bounded provider operations.
4. Record only sanitized live-integration evidence in this file.
5. Re-run exact-head CI if evidence bookkeeping changes, merge/read back main.
6. Activate `API-DEPLOYMENT-001` next.

## Recovery protocol

On any new conversation/session:
1. read this file first and verify branch/head;
2. rediscover the sandbox Sheet by exact provider search when its resource reference is needed;
3. never commit live provider IDs/private data;
4. continue only the active packet unless a blocker forces scope change.
