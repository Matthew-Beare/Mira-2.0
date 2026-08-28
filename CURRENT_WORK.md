# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and its exact resume point.

## Completed packet before this branch

### `M2-G0-008A` — Backup and disaster recovery foundation audit — legacy G16 + F20

- **Merged PR:** #28
- **Merge SHA:** `3abcb58d920ee552fe344527c21669c0b5aa0844`
- **Main activation commit for this packet:** `c21f82fdfe54964c8d864618bc4912cf72f04232`

## Active packet

- **Packet ID:** `M2-G0-008B`
- **Name:** Personal knowledge/reference foundation audit — legacy G17 + G18 + F19
- **Class:** forensic audit / prerequisite
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `audit/g0-008b-knowledge-reference`
- **Branch start SHA:** `c21f82fdfe54964c8d864618bc4912cf72f04232`
- **Research checkpoint:** `ba6d5780a02a609b6dabdb1b30aa6c9819283b1d`
- **Feature registry commit:** `7e3808d78a321b7dfc960186155837019900a441`
- **Backlog commit:** `4eb5a4b411d031298ab90c424b3089a27a19fc46`
- **Status:** acceptance complete; bounded PR/merge/readback pending.

## Exact audited scope

1. **G17 — Knowledge ingestion with relevant excerpts, timestamps, URL/title/metadata, provenance, relationships, optional full pin.**
2. **G18 — Drive organization by domain and searchable metadata.**
3. **F19 — Personal knowledge/reference library**, exact legacy service key `knowledge`, requiring G17 and G18.

No F21-F23, other category-G rows, implementation porting, live Drive mutation, migration, or executable MIRA 2.0 product changes entered this packet.

## Canonical result

1. **`KNOW-001` refined** to **Canonical durable Knowledge source identity and retained-source lifecycle**. It remains the one immutable source/object authority and keeps its legacy test-verified manual/reference behavior.
2. `KNOW-001` no longer semantically depends on asset ownership. Manuals/assets are selected relationships, not the definition of Knowledge.
3. Added **`KNOW-002` — Provenance-bound knowledge excerpts and derived facts**.
4. `KNOW-002` owns stable excerpt/fact identity, exact parent Knowledge UUID, source locator/range, applicable timestamp/page/section/revision, provenance/source tier, correction/supersession and explicit temporary-source versus pinned/retained semantics.
5. The audited legacy executable core does **not** implement a dedicated excerpt/chunk collection. `KNOW-002` evidence is therefore `specified/not_present`.
6. Legacy `asset_evidence.py` and tests do prove `KNOW-001` immutable IDs, idempotent replay, retained/queued lifecycle, Drive-file/revision requirements for retained manuals, fail-closed knowledge links and exact source locators for verified technical specifications.
7. General Knowledge relationships must later support explicit typed links to canonical people/projects/education/tasks/assets/other entities without duplicating the Knowledge source. The legacy relationship model is asset-centric.
8. G18 Drive organization is a **provider projection/configuration**, not canonical identity. Folder names/layout stay private deployment state and moving/renaming them cannot change Knowledge UUID/provenance.
9. Searchable metadata belongs to canonical Knowledge/index state; Drive folders/shortcuts/native views are human navigation projections.
10. The legacy Personal Google blueprint places Knowledge Index/Relationships under the `assets` module. That is valid historical evidence for manuals but must not remain the general F19 authority boundary.
11. Raw/research source may remain temporary when provenance is preserved honestly. Full source retention/pinning is explicit; selected provider retention requires exact write/readback before `retained`/`pinned` may be claimed.
12. Later answers must be re-groundable from exact provenance. Chat/model memory or copied snippets without source identity/locator do not become canonical evidence.
13. Exact F19 service key is **`knowledge`**. It composes `KNOW-001` + `KNOW-002` through `SERVICE-001`/`SERVICE-002`; selected provider filing/search projection may degrade independently without erasing Knowledge truth.
14. F19 service activation/recommendation never proves that content is retained, pinned, grounded or provider-synchronized.
15. PR #31 contains no dedicated generic knowledge-ingestion/excerpt implementation. Its AI processor contract only reinforces that MIRROR owns canonical state/provenance and processors are interchangeable workers.
16. No live Google production state was touched and no executable MIRA 2.0 behavior changed.

## Durable normalization evidence

- `FEATURES.md` commit `7e3808d78a321b7dfc960186155837019900a441`:
  - immediate diff gate: only `FEATURES.md` changed;
  - 17 additions / 4 replacements;
  - refines `KNOW-001`, adds `KNOW-002`, adds F19 mapping and knowledge/reference integrity notes.
- `BACKLOG.md` commit `4eb5a4b411d031298ab90c424b3089a27a19fc46`:
  - immediate diff gate: only `BACKLOG.md` changed;
  - 19 additions / 3 replacements;
  - adds exactly `AUDIT-G17-G18-F19`, `SERVICE-DEPS-010`, `KNOWLEDGE-CORE-001`, `KNOWLEDGE-PROVENANCE-001`, and `KNOWLEDGE-PROJECTION-001` plus bounded dependency findings.

## Evidence paths

- `docs/feature-ledger-2026-08-24.md`
- `docs/feature-catalog.md`
- `starter/behavior-dependencies.json`
- `skill/ops-brief-policy/references/knowledge-manual-ingestion.md`
- `skill/ops-brief-policy/scripts/asset_evidence.py`
- `skill/ops-brief-policy/scripts/test_asset_evidence.py`
- `docs/drive-layout.md`
- `docs/lyfeos-data-model.md`
- `starter/life-planner/assets/personal-google-blueprint.json`
- `starter/tools/onboarding_profile_router.py`
- PR #31 `starter/ai-processor-contract.json` as candidate/reference only.

## Acceptance criteria

1. Stable/refined IDs. **Satisfied: `KNOW-001` refined; new `KNOW-002`.**
2. User-facing descriptions/rationale and evidence separation. **Satisfied.**
3. F19 exact service key `knowledge` through `SERVICE-001`/`SERVICE-002`. **Satisfied.**
4. Temporary raw source vs explicit pin/retention. **Satisfied at contract boundary.**
5. Immutable Knowledge identity across provider/folder changes. **Satisfied.**
6. Excerpt/source locator/timestamp/revision provenance. **Specified under `KNOW-002`; implementation absent and honestly recorded.**
7. Drive layout configurable/private/non-authoritative. **Satisfied.**
8. General typed relationships not asset-only. **Gap recorded in `KNOWLEDGE-CORE-001`.**
9. Conservative legacy/PR31 evidence reconciliation. **Satisfied.**
10. Only `FEATURES.md`, `BACKLOG.md`, `CURRENT_WORK.md` on branch. **Satisfied so far; final branch gate pending.**
11. Bounded PR/merge/readback. **Pending.**
12. No legacy production/executable changes. **Satisfied.**

## Exact next action

1. Compare `audit/g0-008b-knowledge-reference` against `main`; require zero commits behind and exactly `FEATURES.md`, `BACKLOG.md`, `CURRENT_WORK.md` changed.
2. Open a bounded PR to `main`.
3. Verify GitHub server-side changed filenames and mergeability.
4. Merge using the exact verified PR head SHA.
5. Remotely read back `KNOW-001`, `KNOW-002`, F19 mapping and new knowledge backlog work from `main`.
6. Rerank remaining unaudited F21-F23 and category-G rows; activate the next bounded packet from actual dependency priority.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head when tools permit;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture new customer ideas in BACKLOG unless required for acceptance or explicitly reprioritized;
6. finish each MIRA-development response with the configured continuation fallback and packet recovery tag.
