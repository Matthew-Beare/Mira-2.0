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
- **Status:** activated after initial successor provider resource creation; metadata/tab/range verification next.

## Provider timing/readback note

After M2-M0-001 merged, before this branch activation commit was written, successor-scope work created a native Google Sheet named `MIRROR Structured State - Synthetic` from a local synthetic-only workbook and moved it into the verified `Structured State` sandbox child. Native conversion and the destination parent were provider-read-back before this activation. No live provider ID is recorded here.

## Objective

Implement and integration-prove a Google Sheets-backed `StructuredStateAdapter` path using only synthetic data inside the isolated MIRA 2.0 sandbox, preserving the existing provider-neutral state semantics.

## Acceptance criteria

1. Exactly one native Google Sheet with the selected synthetic title exists in the verified `Structured State` child.
2. `Metadata`, `Resources`, `Events`, and `Idempotency` tabs/schema are provider-read-back and contain synthetic data only.
3. Implement provider-neutral Sheets gateway boundary plus Google Sheets adapter without credentials or resource IDs in Git.
4. Stable IDs, revisions, bounded query, exact readback, append-only events, idempotency and stale-revision behavior match `StructuredStateAdapter` semantics.
5. Google row/tab persistence remains isolated behind the adapter/gateway; API and Authority Registry remain provider-agnostic.
6. Deterministic fake-gateway tests cover create/read/query/update/replay/conflict/events/readback.
7. Live provider proof performs a synthetic create/update/readback cycle and verifies exact provider rows after mutation.
8. Update production ownership manifest for new code and direct tests.
9. All feature-registry/code-ownership/unit/integration CI gates pass.
10. No personal data, legacy data, Gmail, Calendar, scheduler, Android, or deployment changes.
11. Live provider IDs/URLs/account identifiers remain outside public Git.
12. Bounded PR/merge/readback, then advance to managed API deployment.

## Exact next action

1. Read native spreadsheet metadata and resolve exact tab names/sheet IDs.
2. Read bounded header/seed ranges from each tab.
3. Implement the Sheets gateway/adapter and tests, update ownership manifest.
4. Perform live synthetic mutation/readback through the provider surface and record sanitized evidence.
5. Require all CI gates green, merge/read back main.
6. Activate `API-DEPLOYMENT-001` next.

## Recovery protocol

On any new conversation/session:
1. read this file first and verify branch/head;
2. rediscover the sandbox Sheet by exact title/provider folder if its resource reference is needed;
3. never commit live provider IDs/private data;
4. continue only the active packet unless a blocker forces scope change.
