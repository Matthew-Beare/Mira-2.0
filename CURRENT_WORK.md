# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and its exact resume point.

## Completed packet before this branch

### `M2-G0-007H` — Feature Audit Slice F8 — assets/maintenance/warranties/manuals service composition

- **Merged PR:** #27
- **Merge SHA:** `442c68b777444678957f241c3219eedd588afe35`
- **Main handoff commit activating backup audit:** `ae84799f27c65f126bb6ee222585750b5f4e6d6e`
- **Result:** F18 service key `assets`; no new asset-service domain authority; selected-path readiness over existing category-D features.
- **Remote readback:** F18 `FEATURES.md` and F8 `BACKLOG.md` state verified on `main`.

## Active packet

- **Packet ID:** `M2-G0-008A`
- **Name:** Backup and disaster recovery foundation audit — legacy G16 + F20
- **Class:** forensic audit / data-integrity prerequisite
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `audit/g0-008a-backup-disaster-recovery`
- **Branch start SHA:** `ae84799f27c65f126bb6ee222585750b5f4e6d6e`
- **Status:** forensic evidence pass complete; feature/backlog normalization next.

## Exact scope

1. **G16 — Twice-daily incremental, daily cloud, weekly full, rotation, encryption, restore tests** — REQUIRED backlog.
2. **F20 — Backup/disaster recovery** — REQUIRED backlog; exact legacy service key `recovery`; requires G16.

F19/G17/G18, F21, F22, F23, other category-G infrastructure, migration execution and live backup operations remain outside this packet.

## Forensic findings

1. A distinct data-protection lifecycle is justified and must not be collapsed into `RECOVERY-001`/`RECOVERY-002`, which own runtime Run Log/checkpoint/circuit-breaker and failure-isolation semantics. The new semantic family will be `BACKUP-*`.
2. One canonical feature is sufficient for this historical slice: **`BACKUP-001` — Verified provider-neutral backup and restore lifecycle**. Backup creation, retention, integrity/readback and restore verification are separate states/evidence within one lifecycle rather than separate authorities.
3. F20 exact legacy service key is `recovery`. It is a `SERVICE-001`/`SERVICE-002` wrapper over `BACKUP-001`, not a second backup database.
4. Legacy dependency graph gives `g-16` profile `backup`, requiring canonical `backup-catalog` plus capabilities `backup_target` and `restore_test`; `f-20` requires `g-16`.
5. Legacy feature catalog records both G16 and F20 as REQUIRED backlog, `specification`/`documented`.
6. Legacy state-authority architecture explicitly says a recovery copy is nonauthoritative and never a second writable master. Provider-native version history/export/snapshots, database backup/WAL and object-storage versioning are adapter implementations beneath the contract.
7. No dedicated backup/restore lifecycle test file exists in the audited legacy `starter/tests` suite. Generic behavior-dependency tests prove catalog coverage and block/degrade mechanics, not backup correctness or recoverability.
8. PR #31 contains meaningful unmerged candidate evidence:
   - `starter/backup-policy.json` defines full/incremental requests, destinations, provider readback, full fallback when incremental change-journal coverage is unprovable, last-good preservation intent and source/runtime-backup separation.
   - `starter/service/backup_scheduler.py` creates stable Backup UUID rows, SQLite snapshots, evidence archives, SHA-256 digests, provider replication/readback, history and policy APIs.
   - `docs/integrations-self-hosting-and-backups.md` explicitly separates source rollback from runtime-data backup and requires backup provider/readback verification.
   - `starter/service/run.py` installs the backup scheduler in the broad candidate service.
9. PR #31 does **not** qualify as complete G16/F20 implementation:
   - no restore implementation or restore-test transaction was located;
   - no direct deterministic backup lifecycle/restore test suite was located;
   - archive encryption is not proven; `encrypt_provider_credentials` is not backup-payload encryption;
   - retention/rotation policy is declared but actual rotation enforcement is absent;
   - no RPO/RTO model or evidence exists;
   - requested incremental backups always become `full_fallback`, which is honest but not incremental capability;
   - candidate defaults use daily incremental requests and weekly full, not the historical twice-daily incremental requirement;
   - the candidate creates its own silent hourly scheduler thread and swallows scheduler exceptions, so it does not prove canonical scheduled delivery, observability or failure reporting;
   - source repository backup is explicitly separate and not implemented by the runtime archive path.
10. Therefore `BACKUP-001` evidence ceiling is **specified + unmerged partial implementation candidate**, with no MIRA 2.0 implementation/integration/live credit.
11. A successful backup occurrence must prove at least exact protected scope/authority, stable Backup ID, type/effective type, destination, integrity digest or equivalent, completed timestamp and target/provider readback. It must not claim recoverability merely from archive creation.
12. A restore test is a separate verification event tied to an exact Backup ID and isolated target/sandbox. It must verify restored canonical identities/material state against expected scope and record result without overwriting the live authority.
13. Backup policy must explicitly cover selected protected data classes/authorities, cadence, retention/rotation, encryption-at-rest/in-transit requirements as applicable, RPO/RTO goals and restore-test cadence. No unsupported numeric defaults are promoted from candidate code.
14. Historical requested cadence remains evidence to preserve/reconcile: twice-daily incremental, daily cloud and weekly full. MIRA 2.0 must not promise true incrementals until complete change-journal/delta semantics are proven; honest full fallback remains preferable to a false incremental claim.
15. Git/source/config backup and mutable runtime state/evidence backup are distinct protection paths. Public/source Git must never receive private mutable state, evidence blobs, secrets or provider credentials as a backup shortcut.
16. Backup failure must not mutate/delete canonical live state or the last verified good recovery artifact; missing backup target/restore capability blocks/degrades only recovery protection and exposes Action Required state.
17. Development restore tests use synthetic MIRA 2.0 sandbox data only. Protected legacy production remains untouched.
18. PR #31 remains unmerged reference/salvage evidence only.

## Acceptance criteria status

1. Stable semantic ID justified: `BACKUP-001`. **Satisfied for audit decision.**
2. F20 service key `recovery` mapped without duplicate authority. **Satisfied for audit decision.**
3. Recovery copies nonauthoritative. **Satisfied.**
4. Backup success separate from restore verification. **Satisfied.**
5. Protected-scope/source/runtime/evidence boundaries defined. **Satisfied.**
6. Provider-neutral adapter semantics preserved. **Satisfied.**
7. Cadence/retention/encryption/RPO/RTO policy semantics recovered without invented numeric defaults. **Satisfied at specification boundary.**
8. Backup/restore audit identity/evidence semantics recovered. **Satisfied at specification boundary.**
9. Synthetic-only restore verification during development. **Satisfied.**
10. Provider backup readback + separate restored-state verification required. **Satisfied.**
11. Failure isolation preserved. **Satisfied.**
12. Requirement/evidence separation. **Satisfied.**
13. PR #31 reconciled without promotion. **Satisfied.**
14. Only authority files changed. **In progress; registry/backlog/current-work writes pending.**
15. PR/merge/readback. **Pending.**
16. No production/executable changes. **Satisfied so far.**

## Exact next action

1. Add `BACKUP-001` and G16/F20 canonical mappings/evidence boundaries to `FEATURES.md`.
2. Add the bounded audit/service/core implementation work to `BACKLOG.md` without disturbing existing ranked rows.
3. Diff-gate each authority write.
4. Close `CURRENT_WORK.md`, final-scope gate the branch, open/verify/merge a bounded PR and remotely read back `main`.

## Next packet after `M2-G0-008A`

Not preassigned. After this data-integrity prerequisite closes, rerank F19/F21/F22/F23 and their remaining category-G prerequisites.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head when tools permit;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture new customer ideas in BACKLOG unless required for acceptance or explicitly reprioritized;
6. finish each MIRA-development response with the configured continuation fallback and packet recovery tag.
