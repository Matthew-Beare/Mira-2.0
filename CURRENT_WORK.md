# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and its exact resume point.

## Completed packet before this branch

### `M2-G0-008F` — Machine-readable feature catalog and code-ownership integrity audit — legacy G19 + G20

- **Merged PR:** #33
- **Merge SHA / main readback:** `4e332385c6394f58bfce88a03256ebaeec59ef99`
- **Post-merge completion checkpoint / this branch start SHA:** `f7f0608849e96da19cc871c119e11afd0052f319`
- **Result:** `DEV-005`/`DEV-006` are canonical; stable generated feature projection and component-ownership gates are normalized.

## Active packet

- **Packet ID:** `M2-G0-008G`
- **Name:** Remaining feature-ledger closeout — F21-F23 + G2-G6/G8-G9/G11-G15
- **Class:** forensic audit / G0 closeout
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `audit/g0-008g-remaining-ledger-closeout`
- **Branch start SHA:** `f7f0608849e96da19cc871c119e11afd0052f319`
- **Status:** activated; row-by-row reconciliation next.

## Objective

Close every remaining unaudited row from the recovered legacy feature ledger without drifting into implementation. Reuse existing semantic IDs wherever the row is already covered by provider/source/distribution/storage/onboarding architecture; create a new stable feature ID only for a genuinely distinct user-facing or platform capability. Explicitly classify backend/vendor choices and optional infrastructure so they do not become false blockers for M2-M0/M2-M1.

## Exact scope

### Category F
- **F21** Custom skill/automation builder.
- **F22** Activity trackers/wearable data.
- **F23** Explicit weather-in-briefs onboarding with slot, location, units, detail and severe-alert choices.

### Category G
- **G2** Google Workspace and Microsoft 365 state/evidence portability.
- **G3** Apple/iCloud and portable-file manual bridge.
- **G4** Locked-down and regulated enterprise/VA pilot lane.
- **G5** Personal-Production/Public-Experimental/Institutional-Experimental release channels.
- **G6** Eventual PostgreSQL/private SQL canonical service.
- **G8** Grafana/observability dashboards.
- **G9** Object storage/NAS evidence and attachments.
- **G11** Home Assistant bridge.
- **G12** Plex bridge.
- **G13** Voice queries/commands.
- **G14** NAS/LAN/private-service bridge and VPN access.
- **G15** Family site-to-site VPN/redundancy/failover.

Do not implement these capabilities, touch provider state, migrate data, build Android/API code, or expand into G0-009/G0-010 in this packet.

## Reconciliation rules

1. Provider/backend names do not automatically create semantic features when `STORE-001`, `PROVIDER-*`, `SOURCE-*`, `DIST-*` or existing service features already own the behavior.
2. PostgreSQL, object storage, NAS and similar implementation choices remain adapters/topology choices unless they introduce a distinct product behavior.
3. Enterprise/regulated deployment is a product capability only to the extent it changes user-visible policy/compliance/deployment behavior; it does not grant organizational authorization or regulated-data approval by declaration.
4. Home Assistant/Plex/NAS bridges should share a generic local-service/network trust boundary where practical rather than each inventing a second authority model.
5. Wearable/activity ingestion remains optional and cannot block routines/fitness core.
6. Voice is a client/input surface; consequential actions retain normal approval/authorization semantics.
7. Family VPN/redundancy is infrastructure, not a required MIRA core behavior unless a later deployment explicitly selects it.

## Preliminary acceptance criteria

1. Every remaining F/G ledger row is mapped to stable semantic IDs or explicitly classified as backend/topology/external-infrastructure rather than left unaudited.
2. Category F closes through F23.
3. Category G ledger coverage closes through G20.
4. Existing provider/source/distribution/storage IDs are reused instead of duplicating authority concepts.
5. Genuine distinct capabilities receive stable IDs only where necessary.
6. Optional/later infrastructure does not block M2-M0/M2-M1.
7. No provider/live/implementation evidence is fabricated from legacy contracts or documentation.
8. No protected legacy state or executable MIRA 2.0 product code changes.
9. `FEATURES.md`, `BACKLOG.md`, `CURRENT_WORK.md` normalization only unless a governance artifact is demonstrably required.
10. Bounded PR/merge/readback before G0-009 activation.

## Exact next action

1. Re-read the legacy ledger rows and relevant current `FEATURES.md` mappings.
2. Reconcile F21-F23 first, then G2-G6, then G8-G9/G11-G15.
3. Check PR #31/legacy implementation only where needed to classify evidence, not to broaden scope.
4. Checkpoint the complete mapping before modifying `FEATURES.md` or `BACKLOG.md`.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture unrelated ideas in BACKLOG unless required for acceptance or explicitly reprioritized.
