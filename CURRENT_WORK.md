# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and its exact resume point.

## Completed packet before this branch

### `M2-G0-008A` — Backup and disaster recovery foundation audit — legacy G16 + F20

- **Merged PR:** #28
- **Merge SHA:** `3abcb58d920ee552fe344527c21669c0b5aa0844`
- **Main activation commit for this packet:** `c21f82fdfe54964c8d864618bc4912cf72f04232`
- **Result:** added `BACKUP-001`; normalized F20 exact service key `recovery`; preserved backup creation/readback separately from restore verification; PR #31 remains partial candidate only.

## Active packet

- **Packet ID:** `M2-G0-008B`
- **Name:** Personal knowledge/reference foundation audit — legacy G17 + G18 + F19
- **Class:** forensic audit / prerequisite
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `audit/g0-008b-knowledge-reference`
- **Branch start SHA:** `c21f82fdfe54964c8d864618bc4912cf72f04232`
- **Status:** forensic evidence complete; registry normalization next.

## Exact scope

1. **G17 — Knowledge ingestion with relevant excerpts, timestamps, URL/title/metadata, provenance, relationships, optional full pin.**
2. **G18 — Drive organization by domain and searchable metadata.**
3. **F19 — Personal knowledge/reference library**, exact legacy service key `knowledge`, requiring G17 and G18.

No F21-F23, other category-G rows, implementation porting, live Drive mutation, migration, or executable MIRA 2.0 product changes enter this packet.

## Forensic findings

1. **`KNOW-001` remains the canonical durable Knowledge source/object identity.** The legacy `asset_evidence.py` core already implements immutable `knowledge_uuid`, generic `reference` knowledge type, source authority/record ID, URL, content hash, tags, summary, retained/queued/unavailable lifecycle and idempotent replay.
2. Legacy tests directly prove retained knowledge requires canonical Drive file ID/URL where retained; manual/service-manual/datasheet/bulletin retention requires revision/edition; queued lookup may exist without falsely claiming retention; unknown knowledge relationships/spec links fail closed; idempotent replay preserves IDs/state.
3. The tested legacy relationship model is too asset-centric for F19/G17. `Knowledge Relationships` currently assume a linked `entity_uuid` and relationship types such as `manual_for`, `datasheet_for`, `bulletin_for`, `reference_for`. General personal knowledge must later support explicit typed links to canonical people/projects/education/tasks/assets/other entities without duplicating the Knowledge source.
4. **G17's excerpt/provenance promise is not implemented as a first-class tested collection.** No dedicated excerpt/chunk entity, stable excerpt ID, source-range timestamp/page/section locator lifecycle or pinning state exists in the audited executable core.
5. Existing verified technical-specification code does prove the narrower principle that a derived fact can reference a Knowledge UUID plus exact `source_locator`, revision and source tier. This supports, but does not implement, the general excerpt model.
6. Therefore add stable semantic feature **`KNOW-002` — Provenance-bound knowledge excerpts and derived facts**. It owns reusable excerpts/derived facts grounded to one exact Knowledge source with stable identity, source locator/range, capture/effective timestamp where applicable, revision/version, provenance and explicit retention/pinning semantics. It never replaces `KNOW-001`.
7. Refine **`KNOW-001` title/description** from manual/reference-only wording to generic durable Knowledge source identity and retained-source lifecycle while preserving all existing tested manual/reference behavior.
8. **G18 is a provider projection, not canonical authority.** `docs/drive-layout.md` explicitly says exact folder names are deployment state resolved through a private Authority Registry; public source must not contain personal folder names/state.
9. Legacy Drive layout provides domain examples and human navigation rules, but moving/renaming folders must never change Knowledge UUID, provenance or relationships.
10. The Personal Google blueprint exposes the historical over-coupling: `Knowledge Index` and `Knowledge Relationships` are nested under the `assets` module. That is valid for asset manuals but insufficient for general personal knowledge. MIRA 2.0 must make knowledge state/provider projection independent from asset-service activation.
11. Searchable metadata belongs to canonical Knowledge state/index semantics; Drive folders/shortcuts/native views are user-facing projections. A folder name/path is not identity and cannot be the only search key.
12. G17 and G18 share the legacy `knowledge-state` + evidence-store boundary. G17 additionally has optional web research. `f-19` requires both G17 and G18.
13. Exact legacy F19 service key is **`knowledge`**. It is present in the deterministic `SERVICE_CATALOG` and recommended for some profiles, but activation/recommendation is separate from implementation/readiness.
14. F19 must compose `KNOW-001` + `KNOW-002` plus provider/search projection readiness through `SERVICE-001`/`SERVICE-002`; it must not create a second personal-knowledge database.
15. Raw/research source may remain temporary when only an excerpt/provenance record is needed. Full source retention/pinning is explicit. If source retention is selected, provider write/readback must succeed before claiming `retained`/`pinned`.
16. Later answers must be re-groundable from exact provenance. Chat memory, generated summaries or copied snippets without source identity/locator are not sufficient canonical evidence.
17. PR #31 contains no dedicated generic knowledge-ingestion/excerpt implementation that raises the evidence level for G17/G18/F19. Its AI processor contract only reinforces that MIRROR owns canonical state/provenance and AI processors are interchangeable workers.
18. Evidence ceiling: `KNOW-001` remains `test_verified` for its current durable-source/manual/reference core, with scope refinement specified; `KNOW-002` is `specified/not_present`; G18 provider projection is `specified/workflow`; F19 service composition is `specified` until normalized/ported.
19. No live Google production state was touched and no executable MIRA 2.0 behavior changed.

## Evidence paths

- `docs/feature-ledger-2026-08-24.md` — G17 requirement and explicit temporary-source/optional-pin wording.
- `docs/feature-catalog.md` — F19/G17/G18 decisions and delivery states.
- `starter/behavior-dependencies.json` — `f-19` requires `g-17` + `g-18`; both share `knowledge-state`/evidence-store profiles.
- `skill/ops-brief-policy/references/knowledge-manual-ingestion.md` — current durable Knowledge identity, dedupe, Drive/index readback, search/answer behavior and source-first reconciliation.
- `skill/ops-brief-policy/scripts/asset_evidence.py` — tested knowledge/source/relationship/specification core.
- `skill/ops-brief-policy/scripts/test_asset_evidence.py` — immutable IDs, replay, retained/queued state, fail-closed knowledge links and source-locator specification tests.
- `docs/drive-layout.md` — private/configurable Drive organization and non-identity folder semantics.
- `docs/lyfeos-data-model.md` — Knowledge Index/relationships and provider migration identity rule.
- `starter/life-planner/assets/personal-google-blueprint.json` — historical asset-coupled Knowledge Index/Relationship projection requiring normalization.
- `starter/tools/onboarding_profile_router.py` — exact service key `knowledge` in the finite service catalog.
- PR #31 `starter/ai-processor-contract.json` — candidate/reference only; processors nonauthoritative.

## Acceptance criteria

1. Stable/refined IDs. **Satisfied by design: `KNOW-001` refined; new `KNOW-002`.**
2. User-facing descriptions/rationale and evidence separation. **Satisfied in checkpoint; registry update pending.**
3. F19 exact service key `knowledge` through `SERVICE-001`/`SERVICE-002`. **Specified; registry update pending.**
4. Temporary raw source vs explicit pin/retention. **Specified.**
5. Immutable Knowledge identity across provider/folder changes. **Satisfied at contract boundary.**
6. Excerpt/source locator/timestamp/revision provenance. **Specified under `KNOW-002`; implementation absent.**
7. Drive layout configurable/private/non-authoritative. **Satisfied at contract boundary.**
8. General typed relationships not asset-only. **Gap identified; implementation work to backlog.**
9. Conservative legacy/PR31 evidence reconciliation. **Satisfied.**
10. Only `FEATURES.md`, `BACKLOG.md`, `CURRENT_WORK.md` on branch. **So far satisfied.**
11. Bounded PR/merge/readback. **Pending.**
12. No legacy production/executable changes. **Satisfied.**

## Exact next action

1. Update `FEATURES.md`: refine `KNOW-001`, add `KNOW-002`, add F19 service mapping/integrity notes and category-G partial audit status.
2. Diff-gate that commit against this checkpoint; only `FEATURES.md` may change.
3. Update `BACKLOG.md` with bounded audit work plus implementation tickets for generic knowledge core/provenance and F19 service dependencies without rewriting existing work rows.
4. Diff-gate `BACKLOG.md` alone.
5. Close this `CURRENT_WORK.md` with exact commits/evidence.
6. Compare branch to `main`; require exactly `FEATURES.md`, `BACKLOG.md`, `CURRENT_WORK.md`, zero behind.
7. Open bounded PR, verify server-side changed filenames/mergeability, merge exact head, read back main and rerank next packet.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head when tools permit;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture new customer ideas in BACKLOG unless required for acceptance or explicitly reprioritized;
6. finish each MIRA-development response with the configured continuation fallback and packet recovery tag.
