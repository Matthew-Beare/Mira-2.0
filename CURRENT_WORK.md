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
- **Status:** row-by-row forensic reconciliation complete and checkpointed by this commit; feature/backlog normalization next.

## Recovered evidence boundary

The authoritative legacy ledger is `MIRA-Personal-Production/docs/feature-ledger-2026-08-24.md`. Supporting evidence inspected in this packet includes `starter/platform-capabilities.json`, `starter/PROVIDER_ONBOARDING.md`, `starter/ENTERPRISE_PILOT.md`, `distribution/channels.json`, `starter/questions.json`, `docs/architecture.md` and `docs/data-platform-grafana.md`.

Legacy evidence is retained only at its proven level. A contract, architecture document or old CI pass does not create MIRA 2.0 implementation/integration/live credit.

## Category-F reconciliation

### F21 — Custom skill/automation builder

- Already owned by **`DEV-004`** and implementation work **`SKILL-BUILDER-001`**.
- No new semantic feature ID.
- Existing boundary remains: bounded private feature creation, declared contracts/capabilities/dependencies/tests, rollback/checkpoint, source readback; publication is a separate approval path.

### F22 — Activity trackers/wearable data

- Genuine distinct optional capability not currently represented by a stable semantic ID.
- Normalize to **`WEARABLE-001` — Optional activity/wearable data ingestion with explicit authorization, provenance/capability evidence and no dependency from core routine/fitness truth.**
- Requirement: proposed/optional; evidence: not present in MIRA 2.0 and no executable legacy adapter located.
- Wearable absence must never block `ROUTINE-001`, fitness/accountability or basic health-administration behavior.

### F23 — Explicit weather-in-briefs onboarding

- Distinct preference/configuration behavior over existing `WEATHER-001`; the legacy starter has explicit slot, location-policy, detail, units and severe-alert questions with tested onboarding-contract evidence.
- Normalize to **`WEATHER-002` — Explicit weather delivery preferences/onboarding for selected brief slots, location policy, units, detail and severe-alert behavior.**
- Dependencies: `WEATHER-001`, `ONBOARD-004`, `ONBOARD-005`, `SERVICE-001`, context/location capability as selected.
- Weather provider failure remains failure-isolated and cannot corrupt brief/core state.

## Category-G reconciliation

### G2 — Google Workspace + Microsoft 365 state/evidence portability

- Already owned by `STORE-001`, `PROVIDER-001`, `PROVIDER-002`, `SOURCE-002` and provider projection features such as `CAL-007` where selected.
- Google Sheets/Drive and Microsoft Lists/Excel/OneDrive/SharePoint are adapters/resources, not semantic authorities.
- No new feature ID.

### G3 — Apple/iCloud + portable-file manual bridge

- Already owned by `PROVIDER-002`, `SOURCE-002`, `STORE-001` and selected projection/import-export semantics.
- Apple/iCloud remains an honest user-mediated/manual lane unless a future exact adapter proves more. No arbitrary unattended iCloud Drive claim.
- No new feature ID.

### G4 — Locked-down/regulated enterprise and VA deployment lane

- Genuine distinct deployment capability because it adds organization approval/data-classification/managed-source/synthetic-first/fail-closed behavior beyond ordinary personal onboarding.
- Normalize to **`ENTERPRISE-001` — Policy-compliant managed/regulated deployment lane with synthetic-first evaluation, exact organization approval/data-classification gates, managed source/provider resources and no personal-account workarounds.**
- Existing legacy contracts are strong/test-supported boundary evidence only; live organization approval is always deployment-specific and mutable.

### G5 — Personal/Public/Institutional deterministic release channels

- Already owned by `DIST-001` + `DIST-002` and implementation work `DIST-STARTER-001`/`FEATURE-SHARE-001`.
- Channel names/topology are distribution configuration; one source revision and sanitized projection semantics are the feature.
- No new ID.

### G6 — Eventual PostgreSQL/private SQL canonical service

- **Not a semantic product feature.** It is a `STORE-001` structured-state adapter/topology choice behind `API-001`/`AUTH-001`.
- Any cutover is owned by `AUTHORITY-MIGRATION-001`; PostgreSQL never becomes a client-facing authority by brand name.
- No new ID; not a blocker for stock Google-backed M2-M0/M2-M1.

### G8 — Grafana/observability dashboards

- Genuine distinct optional operational capability.
- Normalize to **`OBS-001` — Provider-neutral operational observability/telemetry and read-only dashboard projection that never becomes mutable-state authority.**
- Grafana is one adapter/view choice, not the semantic feature.
- Alerts may report conditions but do not create competing task/reminder/scheduler truth.

### G9 — Object storage/NAS evidence and attachments

- **Not a semantic product feature.** It is an evidence-store adapter/topology under `STORE-001` with hash/provenance/readback/retention boundaries.
- No new ID; not a core blocker.

### G11/G12/G14 — Home Assistant, Plex, NAS/LAN/private-service bridge + VPN access

- These share one generic local-service/network trust boundary rather than each creating an authority model.
- Normalize foundation to **`LOCAL-001` — Explicit local-service integration bridge with scoped network/service permissions, verified capability/readback and no assumption of cloud reachability or blanket LAN trust.**
- Home Assistant, Plex, Paperless, Node-RED, MQTT, NAS/filesystem and similar integrations are later adapters/modules under this boundary and can receive dedicated IDs only when promoted to actual product work.

### G13 — Voice queries/commands

- Genuine optional client/input surface.
- Normalize to **`VOICE-001` — Optional voice query/command client surface using the shared API/authorization path with explicit confirmation for consequential actions.**
- Voice input does not bypass `API-001`, permissions, approval gates or canonical readback.

### G15 — Family site-to-site VPN/redundancy/failover

- External deployment/network infrastructure, not required MIRA product behavior.
- May support `LOCAL-001`/private deployment when explicitly selected, but no semantic MIRA feature ID now.
- Remains deferred and cannot block M2-M0/M2-M1.

## Stable feature additions to normalize

- `WEARABLE-001` — optional activity/wearable ingestion.
- `WEATHER-002` — explicit weather delivery preferences/onboarding.
- `ENTERPRISE-001` — managed/regulated deployment lane.
- `OBS-001` — operational observability/read-only dashboard projection.
- `LOCAL-001` — local-service/network bridge boundary.
- `VOICE-001` — voice query/command client surface.

No new IDs for F21, G2, G3, G5, G6, G9 or G15.

## Backlog normalization direction

Reuse existing rows where possible:
- F21 -> `SKILL-BUILDER-001`.
- G2/G3 -> `PROVIDER-ONBOARD-001`, `SOURCE-LANES-001`, `STORE-ADAPTER-001` and selected provider projections.
- G5 -> `DIST-STARTER-001`, `FEATURE-SHARE-001`.
- G6/G9 -> `STORE-ADAPTER-001`, `AUTHORITY-MIGRATION-001` when selected.
- G11/G12/G14 -> existing `LOCAL-INTEGRATIONS`, refined to depend on `LOCAL-001`.

Add bounded rows only for genuinely distinct gaps:
- `WEARABLE-ADAPTER-001` — LATER/optional.
- `WEATHER-ONBOARD-001` — HARDENING/required for fully generic brief onboarding, not Android core.
- `ENTERPRISE-LANE-001` — LATER until stock core/provider abstraction is proven.
- `OBSERVABILITY-001` — HARDENING/LATER after core runtime exists.
- `LOCAL-BRIDGE-001` — LATER foundation for local adapters.
- `VOICE-CLIENT-001` — LATER client surface after API/client authorization core.

## Acceptance criteria

1. Every remaining F/G ledger row mapped or explicitly classified. **Satisfied conceptually; registry normalization pending.**
2. Category F closes through F23. **Pending feature/backlog write.**
3. Category G ledger coverage closes through G20. **Pending feature/backlog write.**
4. Existing authority/provider/distribution/storage semantics reused. **Satisfied.**
5. Genuine distinct capabilities limited to six new semantic IDs. **Satisfied conceptually.**
6. Backend/topology choices do not become false M2-M0/M2-M1 blockers. **Satisfied.**
7. No false MIRA 2.0 implementation/live evidence. **Satisfied.**
8. No protected provider/legacy production state or executable MIRA 2.0 product code touched. **Satisfied so far.**
9. Bounded normalization/PR/merge/readback. **Pending.**

## Exact next action

1. Add the six stable feature IDs and F21-F23/G2-G15 mappings/closure notes to `FEATURES.md`.
2. Normalize `BACKLOG.md` with completed `AUDIT-F21-F23-G2-G15` plus only the bounded new work rows listed above; refine existing `LOCAL-INTEGRATIONS` rather than duplicate it.
3. Update this file with exact normalization SHAs.
4. Diff gate exactly the intended authority files, then PR/merge/readback.
5. Activate G0-009 legacy branch/PR reconciliation next.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture unrelated ideas in BACKLOG unless required for acceptance or explicitly reprioritized.
