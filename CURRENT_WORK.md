# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and its exact resume point.

## Completed packet before this branch

### `M2-G0-008A` — Backup and disaster recovery foundation audit — legacy G16 + F20

- **Merged PR:** #28
- **Merge SHA:** `3abcb58d920ee552fe344527c21669c0b5aa0844`
- **Result:** added `BACKUP-001`; normalized F20 exact service key `recovery`; preserved backup creation/readback separately from restore verification; PR #31 remains partial candidate only.

## Active packet

- **Packet ID:** `M2-G0-008B`
- **Name:** Personal knowledge/reference foundation audit — legacy G17 + G18 + F19
- **Class:** forensic audit / prerequisite
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `audit/g0-008b-knowledge-reference`
- **Base main SHA:** `3abcb58d920ee552fe344527c21669c0b5aa0844`
- **Status:** activated; branch creation and bounded forensic normalization next.

## Exact scope

1. **G17 — Knowledge ingestion with relevant excerpts, timestamps, URL/title/metadata, provenance, relationships, optional full pin.**
2. **G18 — Drive organization by domain and searchable metadata.**
3. **F19 — Personal knowledge/reference library**, exact legacy service key `knowledge`, requiring G17 and G18.

No F21-F23, other category-G rows, implementation porting, live Drive mutation, migration, or executable MIRA 2.0 product changes enter this packet.

## Boundary decision already established

1. Existing `KNOW-001` is broader than its original manual-focused title: it already supplies immutable Knowledge UUID/source identity, generic `reference` records, retained-file state, URL/hash/metadata/tags/summary, dedupe and provider-neutral reconciliation.
2. G17 requires a distinct excerpt/derived-knowledge lifecycle with exact source locator/timestamp/page/section provenance and optional full-source pinning; raw source may remain temporary unless explicitly retained.
3. Therefore the current design target is to **refine `KNOW-001` as generic durable Knowledge source/object identity** and add a narrower semantic feature for provenance-bound excerpts/derived knowledge if the remaining forensic evidence supports that separation.
4. G18 Drive organization is a provider projection/configuration over canonical Knowledge identity and searchable metadata, not a second canonical knowledge authority. Folder names/layout remain private deployment state.
5. F19 exact service key `knowledge` composes the canonical knowledge behaviors through `SERVICE-001`/`SERVICE-002`; it does not create another personal-knowledge database.
6. Legacy `g-17` and `g-18` share `knowledge-state` and evidence-store dependency boundaries; `f-19` requires both.
7. PR #31 has no dedicated generic knowledge-ingestion implementation that earns MIRA 2.0 implementation/integration/live credit.

## Acceptance criteria

1. Assign/refine stable semantic feature IDs for durable Knowledge source identity and provenance-bound excerpt/derived knowledge without duplicate authority.
2. Record complete user-facing descriptions/rationale and keep requirement state separate from evidence level.
3. Normalize F19 exact service key `knowledge` through `SERVICE-001`/`SERVICE-002`.
4. Preserve raw-source-temporary versus explicitly pinned/retained semantics.
5. Preserve immutable Knowledge identity across provider/folder/layout changes.
6. Define excerpt/source locator/timestamp/page/section/revision provenance sufficient to re-ground later answers.
7. Keep Drive domain/folder organization configurable/private and explicitly nonauthoritative.
8. Keep knowledge relationships separate from asset-only applicability so future people/projects/education/other domains can link by stable IDs without duplicating the source.
9. Reconcile legacy executable/tests and PR #31 candidate evidence conservatively; no blind evidence promotion.
10. Update only `FEATURES.md`, `BACKLOG.md`, `CURRENT_WORK.md` on the packet branch.
11. Open bounded PR, verify changed files/mergeability, merge exact verified head and remotely read back normalized state.
12. No live legacy production state and no executable MIRA 2.0 behavior changes.

## Exact next action

1. Create branch `audit/g0-008b-knowledge-reference` from the activation commit containing this file.
2. Read the legacy G17 executable/provenance tests and knowledge-index implementation deeply enough to determine the final `KNOW-001` refinement and whether the excerpt capability receives stable ID `KNOW-002`.
3. Audit G18 Drive/searchable-metadata workflow and its authority/readback boundary.
4. Reconcile F19 service composition and PR #31 only as candidate/reference evidence.
5. Checkpoint forensic conclusions in `CURRENT_WORK.md` before modifying `FEATURES.md` or `BACKLOG.md`.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head when tools permit;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture new customer ideas in BACKLOG unless required for acceptance or explicitly reprioritized;
6. finish each MIRA-development response with the configured continuation fallback and packet recovery tag.
