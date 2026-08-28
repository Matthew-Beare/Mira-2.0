# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and its exact resume point.

## Completed packet before this branch

### `M2-G0-008E` — Android/mobile client boundary audit — legacy G10

- **Merged PR:** #32
- **Merge SHA / main readback:** `4403af395c56677d30c9cfcae811057933ad27ce`
- **Post-merge completion checkpoint / this branch start SHA:** `c7b9c1269939a41f12172eedf96010251847b664`
- **Result:** `CLIENT-ANDROID-001` is canonical; Android remains a shared-`API-001` client and direct provider-authority mutation is rejected.

## Active packet

- **Packet ID:** `M2-G0-008F`
- **Name:** Machine-readable feature catalog and code-ownership integrity audit — legacy G19 + G20
- **Class:** forensic audit / governance and release-integrity prerequisite
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `audit/g0-008f-catalog-code-integrity`
- **Branch start SHA:** `c7b9c1269939a41f12172eedf96010251847b664`
- **Status:** activated; forensic evidence collection next.

## Source-ledger mapping and ranking decision

The remaining source rows were recovered from legacy `MIRA-Personal-Production/docs/feature-ledger-2026-08-24.md`.

- **F21:** Custom skill/automation builder — proposed/accepted direction; workflow/spec only.
- **F22:** Activity trackers/wearable data — proposed; not present; connector/infrastructure dependent.
- **F23:** Explicit weather-in-briefs onboarding with slot/location/units/detail/severe-alert choices — current required; machine-readable onboarding/provider contract exists.
- **G2:** Google Workspace and Microsoft 365 state/evidence portability.
- **G3:** Apple/iCloud and portable-file manual bridge.
- **G4:** Locked-down and regulated enterprise/VA pilot lane.
- **G5:** Personal/Public/Institutional deterministic release channels.
- **G6:** Eventual PostgreSQL/private SQL canonical service.
- **G8:** Grafana/observability dashboards.
- **G9:** Object storage/NAS evidence and attachments.
- **G11:** Home Assistant bridge.
- **G12:** Plex bridge.
- **G13:** Voice queries/commands.
- **G14:** NAS/LAN/private-service bridge and VPN access.
- **G15:** Family site-to-site VPN/redundancy/failover.
- **G19:** Hierarchical machine-readable feature catalog with CI drift enforcement.
- **G20:** Machine-enforced production-code inventory and anti-bloat ownership gate.

G19 + G20 outrank the other remaining rows for the current audit sequence because they are repository/governance integrity controls that directly support dependency closeout and safe implementation growth. G2-G5 overlap already-audited provider/source/distribution semantics and will be reconciled later; F22/G8/G11-G15 are optional/later infrastructure; G6/G9 require stable core storage/service decisions; F23 is user-visible but does not outrank the release-integrity foundation before implementation growth.

## Objective

Determine the stable MIRA 2.0 repository semantics for machine-readable feature/dependency cataloging, generated human-readable views, drift enforcement, production-code ownership/responsibility inventory, anti-bloat gates and evidence-backed implementation claims. Preserve Git as authority without creating duplicate independent planning authorities.

## Exact scope

1. Audit legacy G19 machine-readable feature catalog, generated Markdown/catalog views, dependency/release metadata and CI drift enforcement.
2. Audit legacy G20 production-code inventory, bounded responsibility/ownership metadata, direct-test evidence requirements and anti-bloat CI gates.
3. Reconcile these with current MIRA 2.0 `FEATURES.md`, `BACKLOG.md`, `CURRENT_WORK.md`, `DEV-001`/`DEV-002`/`DEV-003`, packet policy and future dependency graph.
4. Decide which representation is canonical and which views are generated/derived so no spreadsheet/JSON/Markdown combination becomes competing truth.
5. Separate legitimate quality gates from legacy implementation-specific rules that would overconstrain future languages/platforms or reward file-count games.
6. Determine required release evidence for claiming feature implementation/test coverage from machine-readable metadata.

Do **not** expand this packet into executable catalog tooling/CI implementation, Android/API/provider work, full dependency-graph closeout, code refactoring, legacy repo cleanup, or production data/provider changes.

## Preliminary acceptance criteria

1. Stable semantic feature(s) for machine-readable repository catalog/integrity are identified only if existing `DEV-*` IDs are insufficient.
2. Git remains the sole development authority; generated JSON/Markdown/dashboard views cannot become competing independent truth.
3. Feature registry captures stable ID, requirement/evidence level, dependencies/enables, ownership/scope and relevant verification evidence without conflating desired/spec/implemented/test/integration/live states.
4. Dependency/catalog drift is machine-detectable and release-blocking where material.
5. Production-code ownership gate requires bounded responsibility and evidence but does not enforce arbitrary one-file/one-feature architecture or language-specific style as product semantics.
6. Unlisted production behavior, debug/test leakage, dangerous execution patterns and missing direct evidence are fail-closed where evidence warrants it.
7. Generated distribution/catalog artifacts trace to an exact source revision and are reproducible/readback-verifiable.
8. Historical legacy catalog/code inventory implementation gets only the evidence level actually proven.
9. No protected legacy production/provider state or executable MIRA 2.0 code changes occur.
10. Packet normalization remains bounded to Git authority files unless evidence proves another governance file must change.
11. Bounded PR/merge/readback required before successor activation.

## Exact next action

1. Inspect legacy `docs/feature-catalog.json`, `docs/feature-catalog.md`, `docs/code-inventory.json`, feature-ledger source, validators/tests and CI workflow references.
2. Trace which artifacts are hand-authored versus generated and which CI jobs actually enforce drift/ownership.
3. Inspect failure rules for unlisted production files, ownership, direct tests, debug execution, bare exceptions, wildcard imports and shell execution; distinguish portable integrity semantics from Python-specific policy.
4. Classify evidence as specification, implementation, test, integration and live/release proof.
5. Checkpoint findings before modifying `FEATURES.md` or `BACKLOG.md`.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture unrelated customer ideas in BACKLOG unless required for acceptance or explicitly reprioritized.
