# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and exact recovery state.

## Product direction

Default Personal MIRA is stock ChatGPT + Google Workspace with no external infrastructure prerequisite. Repeated useful no-app verticals and integrity/recovery hardening remain ahead of Android. Completed work stays durable in Git.

Every work session begins and ends by checking `CURRENT_WORK.md`, `FEATURES.md`, `BACKLOG.md`, and `ROADMAP.md`.

## Completed predecessor

### `M2-M0-019` — Grocery list vs known-stock reconciliation

PR #73 merged to `main` as `a906fdd0e64dc661774fc7530007030dd1249522` from exact verified head `83914c9d5d2074c611547dcdedd786300f8463f2`.

Evidence:
- core CI `33348876359` green;
- release-wired CI `33349090500` green;
- final exact-head CI `33355952138` green on `83914c9d5d2074c611547dcdedd786300f8463f2`;
- post-merge `main` CI `33355975328` green on `a906fdd0e64dc661774fc7530007030dd1249522`;
- fresh isolated synthetic Google proof verified exact active-grocery selection, observed-descendant stock truth, honest unknown remaining quantity despite acquisition quantity 12, and zero canonical writes;
- complete no-app/release guards are merged;
- protected legacy production state was not used or modified.

`GROCERY-001` / `GROCERY-CORE-001` must be reconciled from candidate/active to merged/completed evidence before implementation grows.

## Active packet

### `M2-M0-020` — Provider-neutral backup / restore core

- **Primary work:** `BACKUP-CORE-001`
- **Primary features:** `BACKUP-001`
- **Related invariants/features:** `RECOVERY-002`, `STORE-001`, `AUTH-001`, `AUTHORITY-MIGRATION-001`, `SERVICE-DEPS-009`, `DATA-001`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `integration/m0-020-backup-core`
- **Base SHA:** `a906fdd0e64dc661774fc7530007030dd1249522`
- **PR:** not yet opened
- **Objective:** implement the smallest provider-neutral backup/restore integrity slice that deterministically exports canonical structured state, hashes and verifies the artifact, restores into a fresh isolated compatible authority, and proves material parity without claiming provider archive durability, encryption, incrementality, scheduling, migration cutover, or disaster-recovery guarantees that are not actually verified.

## Session-start alignment verification — 2026-08-30

### `FEATURES.md`
- `BACKUP-001` is `required/data-integrity` and depends only on `RECOVERY-002` semantically.
- `RECOVERY-002` is test-verified.
- `AUTHORITY-MIGRATION-001` depends on verified backup/restore, so this unlocks protected future backend cutover.
- `GROCERY-001` is merged in PR #73 and requires lifecycle evidence reconciliation only.

### `BACKLOG.md`
- `BACKUP-CORE-001` is a PREREQUISITE with dependencies `BACKUP-001`, `RECOVERY-002`, and completed `STORE-ADAPTER-001A`.
- `PAR-CORE-001` is an optional ENHANCEMENT; recipe/meal work is LATER.
- data-integrity work outranks convenience enhancements.

### `ROADMAP.md`
- M2-M0.5 explicitly includes backup/restore under release/onboarding hardening around no-app verticals.
- future Linux/SQL/managed migration must preserve the same canonical semantics rather than invent a new product model.
- backup core does not require Android or advanced managed infrastructure.

### Legacy salvage finding
- PR #31 is historical audit/specification evidence, not implementation authority.
- its older backup design bundled provider routing, scheduling, encryption/rotation/RPO/RTO and other concerns into one oversized packet; selective semantic salvage only.

### Direction result

**ALIGNED.** Backup/restore outranks par and other optional enhancements because it is required data-integrity infrastructure, is dependency-ready, and unlocks safe authority migration/recovery while preserving the easy Google-first Personal baseline.

## Acceptance criteria

1. Reconcile `GROCERY-001` / `GROCERY-CORE-001` to merged/completed evidence and make `BACKUP-CORE-001` the sole active work row before implementation grows.
2. Define one provider-neutral backup artifact contract for canonical structured state; a backup is a nonauthoritative snapshot, never a writable master.
3. Capture declared schema identity and every Resource record in the selected full structured-state scope in deterministic order.
4. Preserve Event history only where the public source contract can enumerate it deterministically; otherwise document the exact limitation rather than fabricate completeness.
5. Use deterministic canonical serialization and SHA-256 over the exact artifact material.
6. Backup creation is read-only and performs zero source Resource/Event/idempotency mutation.
7. Restore targets a fresh isolated compatible adapter only; reject non-empty mutable targets in this first slice.
8. Preserve canonical resource type, stable Resource ID, payload, and revision meaning. Invent no new domain identity.
9. Because normal STORE upsert increments revisions, reproduce source revisions deterministically through replay-safe writes or fail closed when exact revision parity cannot be achieved.
10. Independently read back restored state and compare it to backup material before marking restore verified.
11. Digest mismatch, malformed artifact, duplicate identity, unsupported schema/type, partial restore, target drift, or readback mismatch fails closed.
12. Backup creation and restore verification are separate facts; successful serialization alone does not prove restorability.
13. First slice is full snapshot only. Do not claim incremental/delta semantics.
14. Do not claim encryption-at-rest, provider archive durability, retention/rotation, RPO/RTO, scheduler firing, offsite redundancy, or automatic disaster recovery.
15. Never commit real private backup material to the public repo; tests use synthetic fixtures only.
16. Direct tests cover deterministic export/digest, source zero-write, empty-target restore, multi-revision parity, tamper/malformed/incompatible rejection, non-empty target rejection, and independent readback parity.
17. Record component ownership and direct verification for the backup core.
18. No-app instructions state that snapshots are nonauthoritative, require digest/readback verification, and do not equal offsite/disaster-recovery guarantees; release guards protect those boundaries.
19. After CI, perform the strongest faithful fresh isolated synthetic Google proof the native contract supports. If connector limits prevent faithful restore, record the limitation instead of claiming provider restore verification.
20. Exact-head CI and post-merge `main` CI are required.
21. Leave provider archive adapters, encryption/retention policy, automatic scheduling, service activation, authority cutover, legacy migration, Android, par, recipes and meals unfinished.

## Exact next action

1. Reconcile grocery merge evidence and mark only `BACKUP-CORE-001` active.
2. Inspect `StructuredStateAdapter` and provider adapters for deterministic export/restore and Event-enumeration limits.
3. Define minimal versioned artifact/digest/parity semantics.
4. Implement provider-neutral backup/restore core and synthetic tests.
5. Wire ownership and no-app/release guards.
6. Run CI before provider writes.
7. Perform the strongest faithful isolated Google proof, then candidate lifecycle, exact-head CI, protected merge and remote `main` verification.

## Recovery protocol

Read this file first. Confirm branch `integration/m0-020-backup-core` descends exactly from verified-green `main` SHA `a906fdd0e64dc661774fc7530007030dd1249522`. Do not touch protected legacy production state. Do not expand this packet into provider archive infrastructure, encryption policy, scheduler automation, authority migration, legacy migration, Android, par, recipes or meal planning.