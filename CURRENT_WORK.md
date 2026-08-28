# MIRA 2.0 CURRENT WORK

Git is authoritative. This file records the completed synthetic integration proof and exact repository-growth successor.

## Completed packet

### `M2-G1-004` — Synthetic HTTP roundtrip integration proof

- **Work ID:** `CORE-SYNTHETIC-ROUNDTRIP`
- **Merged PR:** #41
- **Merge SHA / main readback:** `3f6a616f3b71f9724d2d51b0e03d3a85d14cef94`
- **Branch:** `verify/g1-004-synthetic-roundtrip`
- **Branch start SHA:** `e32d7ee0093aedf70dcec7ca87746a6c726c35e0`
- **CI-verified PR head:** `ccc00dab59f08874914796760190da5ff526330d`
- **GitHub Actions run:** `33210781237`
- **Remote verification:** compile + full repository unit/integration suite succeeded.
- **Result:** create/read/update/replay/conflict/auth isolation/audit/direct-readback all pass through the real WSGI -> session auth -> API service -> Authority Registry -> canonical structured-state stack. `CORE-SYNTHETIC-ROUNDTRIP` is integration-verified.

## Product-state checkpoint

MIRA 2.0 now has a working synthetic same-user service stack:
- canonical mutable structured-state adapter: implemented/test-verified;
- one-authority-per-data-class routing: implemented/test-verified;
- shared API service semantics: implemented/test-verified;
- scoped/revocable client sessions + HTTP transport: implemented/test-verified;
- complete synthetic HTTP roundtrip: integration-verified.

No Google-backed/live deployment or Android client proof is claimed yet.

## Selected successor

### `M2-G1-005` — Machine-readable feature registry gate

- **Work ID:** `FEATURE-REGISTRY-001`
- **Class:** implementation / repository-growth prerequisite
- **Planned branch:** `impl/g1-005-feature-registry`
- **Dependency satisfied:** G0 feature audit is complete and canonical `FEATURES.md` exists.

### Engineering decision

The machine-readable registry will be **generated on demand directly from canonical `FEATURES.md`**, not checked in as an independently editable JSON mirror. This removes an unnecessary second file that can drift while still providing deterministic JSON output, exact source hashing, graph validation and CI enforcement. Git `FEATURES.md` remains the only editable feature authority.

### Acceptance criteria

1. Parse only the canonical `## Feature index` records from `FEATURES.md`; mapping/summary prose cannot silently create features.
2. Preserve authored stable semantic IDs exactly; no row-position/title-derived IDs.
3. Parse title, requirement, evidence and dependency fields distinctly.
4. Reject malformed rows, duplicate IDs, invalid ID shape, self-dependencies and dependencies on unknown feature IDs.
5. Detect dependency cycles and report a deterministic cycle path.
6. Produce deterministic JSON projection containing schema version, source path/hash and sorted feature records/dependencies.
7. Repeated generation from identical bytes is byte-for-byte identical.
8. CLI supports validation/check and JSON emission without modifying `FEATURES.md` or keeping a second editable registry.
9. Repository CI validates the actual checked-in `FEATURES.md` on every PR/push.
10. Tests include malformed/duplicate/unknown/self/cycle fixtures and the real repository registry.
11. If canonical `FEATURES.md` currently contains invalid feature-to-work dependencies, normalize them in this packet rather than weakening validation.
12. No product runtime/provider/Android/legacy production state changes.

## Exact next action

1. Create `impl/g1-005-feature-registry` from this exact main checkpoint.
2. Activate `M2-G1-005`.
3. Implement parser/validator/deterministic generator/CLI plus tests.
4. Run CI against real `FEATURES.md`; repair any invalid canonical dependency entries discovered.
5. Merge exact green head, then activate `CODE-OWNERSHIP-001`.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture unrelated ideas in BACKLOG unless required for acceptance or explicitly reprioritized.
