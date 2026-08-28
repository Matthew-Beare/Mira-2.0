# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active implementation packet and its resume point.

## Completed packet before this branch

### `M2-G1-005` — Machine-readable feature registry gate

- **Merged PR:** #42
- **Merge SHA / main readback:** `d635d45cbdfc66dc8f3e8d9eda765340045a9111`
- **Post-merge completion checkpoint / this branch start SHA:** `4bc2790fa304695b96c9edcf06ff3a8c23b3c173`
- **Remote CI:** run `33211317703`; compile + feature registry + full suite succeeded.
- **Result:** `FEATURE-REGISTRY-001` is implemented/test-verified; canonical feature graph is machine-validated.

## Active packet

### `M2-G1-006` — Production component ownership and anti-bloat gate

- **Work ID:** `CODE-OWNERSHIP-001`
- **Class:** implementation / repository-growth prerequisite
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `impl/g1-006-code-ownership`
- **Branch start SHA:** `4bc2790fa304695b96c9edcf06ff3a8c23b3c173`
- **Status:** activated; current production surface inventoried, implementation next.

## Current production inventory

Production root is `mira/`. Current Python artifacts:
- `mira/__init__.py`
- `mira/structured_state.py`
- `mira/authority.py`
- `mira/api_core.py`
- `mira/http_transport.py`
- `mira/feature_registry.py`

This packet will add `mira/code_ownership.py`, which must itself be owned in the manifest. Tests, docs, workflows, `FEATURES.md`, `BACKLOG.md`, and `CURRENT_WORK.md` are verification/governance surfaces, not product-runtime artifacts.

## Objective

Implement a language-neutral component ownership manifest and CI validator so every production artifact has exactly one bounded owner, relevant feature/work linkage and direct verification evidence before provider/client code fan-out.

## Acceptance criteria

1. One canonical ownership manifest with stable component IDs, responsibility, why-separate rationale, owned production paths, feature IDs, work IDs and direct verification paths.
2. Explicit production roots; every production artifact under them is owned exactly once.
3. Reject unowned artifacts, duplicate ownership, missing paths and ownership outside roots.
4. Validate feature IDs against canonical `FEATURES.md` registry.
5. Validate work IDs against canonical `BACKLOG.md` rows.
6. Require direct verification paths and reject missing/non-test evidence.
7. Python verification profile proves verification source materially imports/references the owned module.
8. Multiple cohesive files per component are allowed; no one-file/one-feature rule.
9. CI runs ownership validation before the full suite.
10. Tests cover invalid manifests plus the real repository manifest.
11. Inventory all current `mira/*.py` including the validator itself.
12. No provider/Google/Android/legacy-state changes.

## Exact next action

1. Add `project/code_ownership.json` with current bounded components.
2. Implement `mira/code_ownership.py` validator/CLI over feature/work registries and filesystem inventory.
3. Add deterministic tests and CI gate.
4. Open bounded PR, require remote CI green and exact file scope.
5. Merge/read back main, then begin Wave 2 with the isolated MIRA 2.0 data sandbox.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head;
3. continue from exact next action;
4. do not broaden scope from chat history;
5. capture unrelated ideas in BACKLOG unless required for acceptance or explicitly reprioritized.
