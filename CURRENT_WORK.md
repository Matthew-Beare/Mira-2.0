# MIRA 2.0 CURRENT WORK

Git is authoritative. This file records the completed feature-registry gate and exact successor.

## Completed packet

### `M2-G1-005` — Machine-readable feature registry gate

- **Work ID:** `FEATURE-REGISTRY-001`
- **Merged PR:** #42
- **Merge SHA / main readback:** `d635d45cbdfc66dc8f3e8d9eda765340045a9111`
- **Branch:** `impl/g1-005-feature-registry`
- **Branch start SHA:** `4fd0de9441ed549200eb7039d18ab25145309a1c`
- **CI-verified PR head:** `3d4e89cb744675b6e7f595589719a1fede1c2938`
- **GitHub Actions run:** `33211317703`
- **Remote verification:** compile succeeded; canonical feature-registry validation succeeded; full unit/integration suite succeeded.
- **Failure-driven repair evidence:** initial run `33211154761` correctly rejected `LOCATION-STATE-001` as an unknown feature dependency. `MOVE-001` and `INV-002` were repaired to retain `LOC-001` as the semantic feature dependency without weakening the validator.
- **Result:** `FEATURES.md` is the only editable feature authority; authored IDs, malformed/duplicate/unknown/self/cyclic dependencies and deterministic source-bound JSON projection are CI-enforced.

## Product-state checkpoint

MIRA 2.0 currently has:
- structured canonical state: implemented/test-verified;
- Authority Registry: implemented/test-verified;
- API service semantics: implemented/test-verified;
- scoped bearer auth + HTTP transport: implemented/test-verified;
- synthetic HTTP canonical roundtrip: integration-verified;
- machine-readable feature/dependency registry gate: implemented/test-verified.

Google/provider deployment and Android shared-state proof are still pending.

## Selected successor

### `M2-G1-006` — Production component ownership and anti-bloat gate

- **Work ID:** `CODE-OWNERSHIP-001`
- **Class:** implementation / repository-growth prerequisite
- **Planned branch:** `impl/g1-006-code-ownership`
- **Dependencies satisfied:** `DEV-006`, `DEV-001`, and `FEATURE-REGISTRY-001` are specified/available; current production surface is small enough to inventory exactly.

### Objective

Implement a language-neutral production-component ownership manifest and CI validator so every production artifact has exactly one bounded owner, relevant feature/work linkage and direct verification evidence before provider/client code fan-out.

### Acceptance criteria

1. Check in one canonical ownership manifest containing stable component IDs, responsibilities, why-separate rationale, owned production paths, relevant feature IDs, work IDs and direct verification paths.
2. Define production roots explicitly; all production artifacts under those roots must be owned exactly once.
3. Reject unowned production artifacts, duplicate/overlapping ownership, nonexistent owned paths and ownership outside declared production roots.
4. Validate referenced feature IDs against the machine-readable `FEATURES.md` registry.
5. Validate referenced work IDs against canonical `BACKLOG.md` work rows.
6. Require at least one direct verification path per component and reject missing/non-test verification paths.
7. Python verification profile proves referenced test files materially reference/import the owned Python module rather than merely existing.
8. Component can own multiple cohesive files; validator does not impose one-file/one-feature or arbitrary file-count minimization.
9. CI runs the ownership gate before the full unit suite.
10. Deterministic tests cover unowned/overlap/missing path/unknown feature/work/missing verification and the real repository manifest.
11. Inventory all current `mira/*.py` production files without reclassifying tests/docs/workflows as product code.
12. No provider/Google/Android/legacy production state changes.

## Exact next action

1. Create `impl/g1-006-code-ownership` from this exact main checkpoint.
2. Activate `M2-G1-006` on that branch.
3. Inventory current production files and map them into bounded components.
4. Implement manifest validator/tests and CI gate.
5. Require exact PR scope and remote CI green, merge/read back main.
6. Then proceed to Wave 2 provider/deployment work, beginning with the isolated MIRA 2.0 data sandbox.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture unrelated ideas in BACKLOG unless required for acceptance or explicitly reprioritized.
