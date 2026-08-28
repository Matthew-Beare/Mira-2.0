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
- **Activation commit:** `4c1001f1b230328d370ad3789f29ccba422252db`
- **Research checkpoint:** `01845ec769c26de3ffb1cbe03456ec0ae37026c7`
- **Feature normalization:** `6b5c982eafe786918bda12e73d6f021d092f57a3`
- **Backlog normalization:** `1243f1b617a0a33c357368e51efa3930baf5cc75`
- **Status:** acceptance complete; final diff gate, bounded PR, merge and main readback remain.

## Canonical result

All recovered category-F and category-G ledger rows are now mapped.

### New stable features

- `WEARABLE-001` — optional activity/wearable ingestion; never required for core routine/fitness truth.
- `WEATHER-002` — explicit weather delivery/onboarding preferences over `WEATHER-001`.
- `ENTERPRISE-001` — managed/regulated deployment lane with synthetic-first and exact organization approval/data-classification gates.
- `OBS-001` — provider-neutral operational observability/read-only dashboard projection.
- `LOCAL-001` — scoped local-service/network integration bridge boundary.
- `VOICE-001` — optional voice query/command client surface over normal API/authorization rules.

### Rows deliberately not promoted to new product authorities

- F21 reuses `DEV-004` + `SKILL-BUILDER-001`.
- G2/G3 Google/Microsoft/Apple portability reuses `STORE-001`, `PROVIDER-*`, `SOURCE-002` and selected projections.
- G5 release channels reuse `DIST-001`/`DIST-002`.
- G6 PostgreSQL/private SQL and G9 object storage/NAS are backend adapter/topology choices under `STORE-001`, not semantic product authorities.
- G15 family site-to-site VPN/redundancy remains deferred external infrastructure.

### Backlog result

- Added `WEATHER-ONBOARD-001`, `WEARABLE-ADAPTER-001`, `OBSERVABILITY-001`, `VOICE-CLIENT-001`.
- Refined existing `LOCAL-INTEGRATIONS` around `LOCAL-001`; no duplicate local-bridge work ID.
- Refined existing `ENTERPRISE` around `ENTERPRISE-001`; no duplicate enterprise-lane work ID.
- `AUDIT-F` is complete through this packet.
- `AUDIT-G` is complete through recovered G1-G20 coverage.
- Optional/backend/local/voice infrastructure does **not** become a blocker for M2-M0/M2-M1.

## Android product-state checkpoint

This packet materially reduces pre-implementation uncertainty but does not create an APK. Current state:

- Android architecture/boundaries: substantially specified.
- Legacy Android build evidence: real and reusable as salvage evidence.
- MIRA 2.0 APK: **not built yet**.
- Shared MIRA API runtime: **not built yet**.
- Android shared-state integration: **not proven yet**.

Critical implementation chain after G0 closeout:

1. `AUTHORITY-REGISTRY-001` + `STORE-ADAPTER-001`;
2. `API-CORE-001`;
3. `CORE-ROUNDTRIP`;
4. `ANDROID-CLIENT-CORE-001`;
5. `ANDROID-SYNC`;
6. native delivery/capture and `ANDROID-RELEASE-001`.

## Acceptance criteria

1. Every recovered F/G ledger row mapped or explicitly classified. **Satisfied.**
2. Category F closed through F23. **Satisfied.**
3. Category G recovered ledger closed through G20. **Satisfied.**
4. Existing provider/storage/distribution authorities reused rather than duplicated. **Satisfied.**
5. Backend/topology/optional infrastructure kept off the Android/core critical path. **Satisfied.**
6. No false MIRA 2.0 implementation/live evidence. **Satisfied.**
7. No protected legacy production/provider state or executable MIRA 2.0 product code changed. **Satisfied.**
8. Stable feature/backlog normalization complete. **Satisfied.**
9. Bounded PR/merge/readback. **Pending.**

## Exact next action

1. Compare `audit/g0-008g-remaining-ledger-closeout` against `main`; require zero commits behind and exactly `FEATURES.md`, `BACKLOG.md`, `CURRENT_WORK.md` changed.
2. Open bounded PR to `main`.
3. Verify exact server-side filenames, head SHA and mergeability.
4. Merge using the exact verified head SHA.
5. Read back category-F/G closure and the six new feature IDs from `main`.
6. Activate G0-009 legacy branch/PR reconciliation from the post-merge completion checkpoint.

## Remaining before implementation begins

After this packet merges, exactly two G0 closeout stages remain:

1. **G0-009** — reconcile meaningful legacy branches/PRs against stable IDs and salvage only bounded components.
2. **G0-010** — final dependency/enables graph, dedupe/supersession map and ranked implementation backlog.

Then new MIRA 2.0 implementation starts.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture unrelated ideas in BACKLOG unless required for acceptance or explicitly reprioritized.
