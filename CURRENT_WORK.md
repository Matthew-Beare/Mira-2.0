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
- **Status:** activated; parser/validator/generator implementation next.

## Engineering decision

`FEATURES.md` remains the only editable feature authority. Machine-readable JSON is generated on demand from those exact source bytes and is never checked in as a second editable registry. CI validates the source graph and deterministic generation on every change.

## Acceptance criteria

1. Parse only canonical `## Feature index` records.
2. Preserve authored stable semantic IDs exactly.
3. Parse title/requirement/evidence/dependencies distinctly.
4. Reject malformed rows, duplicate/invalid IDs, self/unknown dependencies.
5. Detect dependency cycles deterministically.
6. Deterministic JSON includes schema version and exact source path/SHA-256.
7. Identical source bytes generate byte-for-byte identical JSON.
8. CLI supports `check` and `json` without source mutation/second registry.
9. CI validates actual `FEATURES.md` on every PR/push.
10. Tests cover bad fixtures and actual repository registry.
11. Repair canonical dependency errors rather than weakening validation.
12. No product runtime/provider/Android/legacy-state changes.

## Exact next action

1. Implement `mira/feature_registry.py` parser/graph validator/projection/CLI.
2. Add deterministic fixture tests plus actual `FEATURES.md` validation.
3. Add CI registry-check step.
4. Use CI failure evidence to normalize any invalid current feature dependencies.
5. Merge exact green head, then activate `CODE-OWNERSHIP-001`.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head;
3. continue from exact next action;
4. do not broaden scope from chat history;
5. capture unrelated ideas in BACKLOG unless required for acceptance or explicitly reprioritized.
