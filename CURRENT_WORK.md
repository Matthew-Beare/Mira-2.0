# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active implementation packet and its resume point.

## Completed packet before this branch

### `M2-G1-004` — Synthetic HTTP roundtrip integration proof

- **Merged PR:** #41
- **Merge SHA / main readback:** `3f6a616f3b71f9724d2d51b0e03d3a85d14cef94`
- **Post-merge completion checkpoint / this branch start SHA:** `4fd0de9441ed549200eb7039d18ab25145309a1c`
- **Remote CI:** GitHub Actions run `33210781237`; compile + full unit/integration suite passed.
- **Result:** `CORE-SYNTHETIC-ROUNDTRIP` is integration-verified.

## Active packet

### `M2-G1-005` — Machine-readable feature registry gate

- **Work ID:** `FEATURE-REGISTRY-001`
- **Class:** implementation / repository-growth prerequisite
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `impl/g1-005-feature-registry`
- **Branch start SHA:** `4fd0de9441ed549200eb7039d18ab25145309a1c`
- **Parser/validator/generator:** `0a81110536ed3d4906796d606d9026c944d5697c`
- **Deterministic tests:** `55e918c4b0ec67f3f5599b34235250e063d1b2e8`
- **CI registry gate:** `1017671b14d8f2a9b8d49159c19c287089be464c`
- **Canonical dependency repair:** `e15d3ec6f029967cb59849b54467ca42e2bf1cd9`
- **PR:** #42
- **Status:** implementation/test/CI content committed; first CI failure correctly exposed invalid work-ID dependencies in canonical `FEATURES.md`; source repaired; second CI run pending.

## Engineering decision

`FEATURES.md` remains the only editable feature authority. Machine-readable JSON is generated on demand from those exact source bytes and is never checked in as a second editable registry. CI validates the source graph and deterministic generation on every change.

## Implemented component

Component: **feature-registry**

Owned production surface:
- `mira/feature_registry.py` — canonical feature-index parser, graph validator, deterministic JSON projection and CLI.

Direct verification:
- `tests/test_feature_registry.py` — malformed row, duplicate/invalid ID, unknown/self/duplicate dependency, deterministic cycle path, deterministic projection/source hash, mapping-section isolation and real-repository validation.
- `.github/workflows/ci.yml` — runs `python -m mira.feature_registry check FEATURES.md` before the full unit suite.

## First CI evidence and canonical repair

GitHub Actions run `33211154761` failed specifically at the new **Feature registry** step after compile succeeded:

`feature INV-002 depends on unknown feature ID LOCATION-STATE-001`

Inspection showed both `INV-002` and `MOVE-001` incorrectly included implementation work ID `LOCATION-STATE-001` in the semantic feature dependency column. Both already depended on canonical feature `LOC-001`. The repair removes `LOCATION-STATE-001` from those feature rows; no replacement feature, alias, or validator exception was added.

This preserves the rule that `FEATURES.md` contains feature-to-feature semantic dependencies only; implementation work dependencies remain in `BACKLOG.md`.

## Acceptance criteria status

1. Parse only canonical `## Feature index` records. **Implemented/test-covered.**
2. Preserve authored stable semantic IDs exactly. **Implemented/test-covered.**
3. Parse title/requirement/evidence/dependencies distinctly. **Implemented/test-covered.**
4. Reject malformed rows, duplicate/invalid IDs, self/unknown dependencies. **Implemented/test-covered.**
5. Detect dependency cycles deterministically. **Implemented/test-covered.**
6. Deterministic JSON includes schema version and exact source path/SHA-256. **Implemented/test-covered.**
7. Identical source bytes generate byte-for-byte identical JSON. **Implemented/test-covered.**
8. CLI supports `check` and `json` without source mutation/second registry. **Implemented.**
9. CI validates actual `FEATURES.md` on every PR/push. **Implemented; first failure proved gate is active.**
10. Tests cover bad fixtures and actual repository registry. **Implemented; full run pending after source repair.**
11. Repair canonical dependency errors rather than weakening validation. **Satisfied for discovered `LOCATION-STATE-001` defect.**
12. No product runtime/provider/Android/legacy-state changes. **Satisfied.**

## Exact next action

1. Verify the PR-triggered CI run for repaired head succeeds through registry validation and full suite.
2. If another canonical graph defect appears, repair `FEATURES.md` rather than weakening validation and rerun.
3. Verify PR #42 changed-file scope and mergeability at exact green head.
4. Merge/read back `main` and checkpoint `FEATURE-REGISTRY-001` as test-verified.
5. Activate `M2-G1-006` / `CODE-OWNERSHIP-001` before provider/client fan-out.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head;
3. continue from exact next action;
4. do not broaden scope from chat history;
5. capture unrelated ideas in BACKLOG unless required for acceptance or explicitly reprioritized.
