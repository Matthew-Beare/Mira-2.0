# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and exact recovery state.

## Product direction

Default Personal MIRA is stock ChatGPT + Google Workspace with no external infrastructure prerequisite. Repeated useful no-app verticals and integrity/recovery hardening remain ahead of Android. Completed work stays durable in Git.

Every work session begins and ends by checking `CURRENT_WORK.md`, `FEATURES.md`, `BACKLOG.md`, and `ROADMAP.md`.

## Completed predecessor

### `M2-M0-019` — Grocery list vs known-stock reconciliation

PR #73 merged to `main` as `a906fdd0e64dc661774fc7530007030dd1249522` from exact verified head `83914c9d5d2074c611547dcdedd786300f8463f2`.

Evidence:
- exact-head CI `33355952138` green;
- post-merge `main` CI `33355975328` green;
- fresh isolated synthetic Google proof verified exact active-grocery selection, observed-descendant stock truth, honest unknown remaining quantity despite acquisition quantity 12, and zero canonical writes;
- protected legacy production state was not used or modified.

`GROCERY-001` / `GROCERY-CORE-001` are reconciled to merged/completed evidence in `FEATURES.md` and `BACKLOG.md`.

## Active packet

### `M2-M0-020` — Provider-neutral backup / restore core

- **Primary work:** `BACKUP-CORE-001`
- **Primary feature:** `BACKUP-001`
- **Related invariants/features:** `RECOVERY-002`, `STORE-001`, `AUTH-001`, `DATA-001`
- **Downstream work unlocked by verified backup:** `AUTHORITY-MIGRATION-001`, `SERVICE-DEPS-009`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `integration/m0-020-backup-core`
- **Base SHA:** `a906fdd0e64dc661774fc7530007030dd1249522`
- **PR:** #74
- **Last green implementation/release head before provider-evidence checkpoint:** `141a66e9372ab2d5bd3daf1e78d3026682b7b2f3`
- **CI:** `33367710706` green on `141a66e9372ab2d5bd3daf1e78d3026682b7b2f3`
- **Objective:** implement the smallest provider-neutral backup/restore integrity slice that deterministically exports canonical current structured Resource state, hashes and verifies the artifact, restores into a fresh isolated compatible authority, and proves material parity without claiming provider archive durability, Event-history recovery, original idempotency-history recovery, encryption, incrementality, scheduling, migration cutover, or disaster-recovery guarantees that are not actually verified.

## Alignment result

**ALIGNED.** `BACKUP-001` is required data-integrity work, depends semantically on test-verified `RECOVERY-002`, and unlocks future protected authority migration. It outranks optional par/recipe/meal enhancements. This packet remains bounded to current-Resource snapshot and isolated restore parity rather than expanding into provider archive infrastructure or migration.

## Implemented contract

`mira/backup.py` implements backup artifact v1 and `BackupService` with these invariants:

1. Backup artifacts are nonauthoritative snapshots, never writable masters.
2. Artifact v1 captures exact schema identity plus complete current Resource state under the public STORE query bound.
3. Resource material is sorted deterministically by `(resource_type, resource_id)` and canonical JSON is SHA-256 digested.
4. Coverage is explicit:
   - Resources: `complete_current_resources_under_query_bound`;
   - Events: `not_exported_interface_not_enumerable`;
   - original persisted idempotency history: `not_exported_interface_not_enumerable`.
5. The public `StructuredStateAdapter` cannot globally enumerate all Event streams or persisted idempotency rows, so v1 does not fabricate completeness for either.
6. If a Resource query returns exactly the 1,000-row public bound, export fails closed because completeness cannot be proven without pagination.
7. Backup creation is read-only and performs no source Resource/Event/idempotency mutation.
8. Restore requires an exact schema match, caller/provider-proven fresh isolated authority, and programmatic Resource emptiness.
9. Current Resource IDs, payloads and revision numbers are reproduced using deterministic restore-only idempotency keys and repeated final-payload upserts.
10. A restore-key replay on the supposedly fresh target is evidence that the target is not fresh and fails closed.
11. Independent target re-export must reproduce the exact unsigned material and SHA-256 digest before restore is marked verified.
12. No Event history is synthesized; original source idempotency history is not copied.
13. Provider-generated timestamps, request hashes and restore-only idempotency records are target execution evidence, not backup material.
14. No claim is made for provider archive durability, offsite redundancy, encryption, incremental backup, retention/rotation, scheduler firing, RPO/RTO, automatic disaster recovery, authority cutover, or legacy migration.

## Direct and release evidence

- `tests/test_backup.py` covers deterministic export/digest, explicit coverage, source zero-write, fresh-target restore, multi-revision parity, malformed/tampered artifact rejection, duplicate/sort validation, incompatible and non-empty target rejection, independent readback drift failure, hidden restore-key replay failure, 1,000-row completeness failure, and canonical parser roundtrip.
- `project/code_ownership.json` registers `backup-restore-core`, owning `mira/backup.py` and directly verified by `tests/test_backup.py`.
- `workspace/apps_script/MIRA_NO_APP_INSTRUCTIONS.md` contains the complete no-app backup/restore integrity contract.
- `mira/workspace_bundle.py` plus `tests/test_backup_release_protocol.py` guard nonauthoritative snapshot semantics, source read-only behavior, fresh-target requirement, explicit Event/idempotency coverage limits, restore replay failure, exact restore verification, and separation from authority migration.
- CI `33367710706` is green on implementation/release head `141a66e9372ab2d5bd3daf1e78d3026682b7b2f3`.

## Fresh isolated Google provider proof

Two brand-new native Google Sheets authorities, both clearly marked `NOT A STARTER`, were created solely for this synthetic proof. Their provider identifiers/URLs are intentionally excluded from public Git. Protected legacy MIRA production state was not opened, copied as state, modified, or used as a fixture.

Both authorities used STORE-001-shaped `Metadata`, `Resources`, `Events`, and `Idempotency` tabs with schema version `1`, resource types `entity`/`task`, event types `created`/`updated`, `writer_model=single_writer`, and synthetic-only proof metadata.

### Source authority

The source contained:
- one canonical Entity at revision 2 with final payload `Synthetic Alpha / verified`;
- one canonical Task at revision 1 with final payload `Synthetic restore proof task / open`;
- one deliberate canonical `created` Event for the Entity;
- four original source idempotency rows covering Entity revision 1, Entity revision 2, Task revision 1, and the Event append.

A complete canonical source snapshot was read before backup/restore work. The exact same canonical source cells were read again afterward and were unchanged: same two Resources, same revisions/payloads/request hashes, same Event, and same four original idempotency rows. Provider backup/export therefore performed zero canonical source writes.

### Backup material

The v1 snapshot contained only the two current Resources, exact schema and explicit coverage declarations. Canonical material SHA-256 was:

`7d99f927d3d5cec73a0c06abd13db06fc707b8f517090f2c6cd195db5ebd4c45`

The deliberate source Event and four original idempotency-history rows were not part of artifact material, exactly as v1 declares.

### Fresh target and restore

Before restore, the independent target had metadata/headers only and zero Resources, zero Events and zero idempotency rows.

Restore replayed exactly the v1 service semantics:
1. final Entity payload -> revision 1;
2. same final Entity payload -> revision 2;
3. final Task payload -> revision 1.

Each revision used a deterministic restore-only idempotency key and an atomic Google batch containing the Resource mutation plus its restore Idempotency record. Exact readback after Entity revisions confirmed the expected state.

Final target state:
- Entity: exact source identity/payload at revision 2;
- Task: exact source identity/payload at revision 1;
- Events: header-only, proving the source Event was **not** silently restored;
- Idempotency: exactly three restore-generated upsert records, not the four original source-history records.

Independent target re-export reproduced the same backup unsigned material and exact SHA-256:

`7d99f927d3d5cec73a0c06abd13db06fc707b8f517090f2c6cd195db5ebd4c45`

This proves the stock-ChatGPT/native Google current-Resource export/fresh-target restore/readback protocol faithfully. It does **not** claim that the Python `BackupService` executed inside Google connector runtime, and it does not upgrade v1 into Event-history, archive, encryption, scheduler, RPO/RTO, or disaster-recovery proof.

Presentation-only header freezing/column sizing occurred only after functional proof and did not alter canonical Resource/Event/Idempotency material.

## Candidate lifecycle state

- `BACKUP-001`: implementation, direct tests, release guards and fresh provider restore/readback evidence complete; must remain **candidate-unmerged** until PR #74 merges and post-merge `main` verification passes.
- `BACKUP-CORE-001`: sole active work row; not complete until exact-head CI, protected merge and post-merge `main` CI are green.
- `AUTHORITY-MIGRATION-001`, provider archive adapters, encryption/retention policy, automatic scheduling, service activation, legacy migration, Android, par, recipes and meals remain unfinished.

## Exact next action

1. Reconcile candidate evidence in `FEATURES.md` and `BACKLOG.md` without marking the packet merged early.
2. Update PR #74 body with implementation, CI and provider evidence.
3. Read the live PR #74 exact head and mergeability.
4. Require CI success on that exact final head.
5. Merge PR #74 only with expected-head protection.
6. Verify remote `main` points to the merge SHA and require post-merge `main` CI success.
7. Create a fresh post-merge lifecycle checkpoint marking `BACKUP-001` / `BACKUP-CORE-001` merged/completed and dynamically rank the next bounded packet.

## Recovery protocol

Read this file first. Confirm branch `integration/m0-020-backup-core` still targets PR #74 against `main`, and verify the live branch head before any merge. Provider proof is complete; do not repeat it against protected state. Do not expose proof spreadsheet identifiers/URLs publicly. Do not expand this packet into provider archive infrastructure, Event-history backup, encryption policy, scheduler automation, authority migration, legacy migration, Android, par, recipes or meal planning.