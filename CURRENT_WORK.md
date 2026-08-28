# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and its exact resume point.

## Completed packet before this activation

### `M2-G0-007H` — Feature Audit Slice F8 — assets/maintenance/warranties/manuals service composition

- **Merged PR:** #27
- **Merge SHA:** `442c68b777444678957f241c3219eedd588afe35`
- **Result:** F18 service key `assets`; no new asset-service domain authority; legacy all-D1-through-D7 readiness normalized to selected paths over existing `ASSET-*`/`FITMENT-001`/`IDENT-001`/`EVID-001`/`KNOW-001`/`SPEC-001` authorities.
- **Backlog:** added `AUDIT-F8` and `SERVICE-DEPS-008`; historical explanatory prose compacted while every pre-F8 ranked work row was preserved unchanged.
- **Remote readback:** F18 `FEATURES.md` mapping and F8 backlog rows verified on `main` after merge.
- **Live Google production touched:** no.
- **Executable MIRA 2.0 product behavior changed:** no.

## Active packet

- **Packet ID:** `M2-G0-008A`
- **Name:** Backup and disaster recovery foundation audit — legacy G16 + F20
- **Class:** forensic audit / data-integrity prerequisite
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `audit/g0-008a-backup-disaster-recovery`
- **Activation base SHA:** `442c68b777444678957f241c3219eedd588afe35`
- **Status:** activated; branch creation and forensic evidence pass next.

## Exact scope

Audit exactly these two historically linked behaviors:

1. **G16 — Twice-daily incremental, daily cloud, weekly full, rotation, encryption, restore tests** — REQUIRED backlog; specification-level.
2. **F20 — Backup/disaster recovery** — REQUIRED backlog; specification-level; legacy service key `recovery`; requires G16.

Do not expand this packet into G17/G18 knowledge ingestion/Drive organization, F19 knowledge service, F21 custom builder, F22 wearables, F23 weather onboarding, other category-G infrastructure, migration execution, or live backup operations.

## Packet-boundary rationale

- G16 is a required data-integrity prerequisite and directly blocks F20.
- G16 and F20 share one backup/restore authority and verification boundary, so auditing them together is a bounded vertical dependency slice rather than unrelated scope growth.
- F19 remains blocked on G17/G18 and is not next merely because it has the lower row number.
- F21 is proposed/accepted and already has category-E source-builder foundations; F22 is proposed; F23 is current-required but does not outrank a required data-integrity prerequisite.
- Existing `RECOVERY-001`/`RECOVERY-002` cover runtime Run Log/checkpoint/circuit-breaker and module failure isolation. Data backup/restore must remain semantically separate unless the evidence proves otherwise.

## Acceptance criteria

1. Assign stable semantic MIRA 2.0 feature ID(s) for durable data backup/restore behavior only if a distinct lifecycle/authority is justified; prefer a `BACKUP-*` family rather than overloading runtime `RECOVERY-*` semantics.
2. Record exact user-facing F20 service key `recovery` and map it through `SERVICE-001`/`SERVICE-002` to the canonical backup behavior without creating a duplicate service database.
3. Define backup/recovery copies as nonauthoritative recovery artifacts, never a second writable master or silent failover authority.
4. Separate backup creation evidence from restore verification. A completed/uploaded snapshot alone must never prove recoverability.
5. Preserve explicit scope for what is protected: portable source/configuration, mutable structured state, retained evidence/files, and any separately selected authorities. Git must not become a dump target for private mutable state or secrets.
6. Preserve provider-neutral adapter semantics: provider version history/snapshots, database-native backup/WAL, object-storage versioning and export archives are implementations beneath one canonical backup/restore contract rather than architecture-specific truth.
7. Define or recover policy semantics for retention/rotation, encryption, backup cadence, recovery-point objective (RPO), recovery-time objective (RTO), last successful backup evidence and restore-test evidence without inventing unsupported numeric defaults.
8. Backup/restore identity and status must be replay/audit safe, with exact source authority/scope, target/provider reference, timestamps, integrity evidence and restore-test result where applicable.
9. Restore testing must use synthetic/sandbox state during MIRA 2.0 development and must not overwrite or repurpose protected legacy production data.
10. Provider/target success requires exact write/readback or equivalent backup-target evidence; restore success requires separate restored-state verification/reconciliation.
11. Failure isolation must preserve canonical live state when backup target/restore testing is unavailable; the recovery service reports blocked/degraded honestly rather than claiming protection.
12. Record requirement status separately from implementation/test/integration/live evidence; legacy contracts/spec prose do not become implementation credit.
13. Reconcile PR #31 and any other legacy backup candidates as evidence only; do not promote unmerged/reference code to MIRA 2.0 integration/live status.
14. Update only `FEATURES.md`, `BACKLOG.md`, and `CURRENT_WORK.md` in this forensic packet.
15. Open a bounded PR, verify server-side scope/mergeability, merge using exact head SHA and remotely read back the resulting backup/recovery registry state.
16. Touch no legacy Google production state and change no executable MIRA 2.0 product behavior.

## Authoritative evidence already identified

- Legacy feature catalog: G16 is REQUIRED backlog, `specification`/`documented`; F20 Backup/disaster recovery is REQUIRED backlog, `specification`/`documented`.
- Legacy dependency graph: `f-20` requires `g-16`; G16 uses dependency profile `backup`.
- Backup dependency profile requires canonical `backup-catalog` authority plus `backup_target` and `restore_test` capabilities.
- Legacy stock-service router exposes exact service key `recovery` and recommends it as a baseline service without auto-enabling it.
- `STATE_AUTHORITY_MODEL.md` says a recovery copy is never a second writable master; provider/native version history/export/snapshot mechanisms are adapter-specific; PostgreSQL uses native backup/WAL plus restore testing; object storage may use versioning/backup; migration snapshots remain nonauthoritative until verified cutover.

## Exact next action

1. Create branch `audit/g0-008a-backup-disaster-recovery` from this activation commit.
2. Inspect legacy G16/F20 evidence across feature catalog/ledger, `behavior-dependencies.json`, `BEHAVIOR_DEPENDENCIES.md`, `STATE_AUTHORITY_MODEL.md`, backup/recovery references, tests, schemas and PR #31 candidates.
3. Determine the minimum canonical backup/restore lifecycle and stable semantic ID, explicitly separating it from `RECOVERY-001`/`RECOVERY-002`.
4. Checkpoint the forensic finding in this file before changing `FEATURES.md` or `BACKLOG.md`.

## Next packet after `M2-G0-008A`

Not preassigned. After G16/F20 closes, rerank remaining unaudited F19/F21/F22/F23 and their category-G prerequisites. Dependency and integrity order, not row order, decides the next packet.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head when tools permit;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture new customer ideas in BACKLOG unless required for acceptance or explicitly reprioritized;
6. finish each MIRA-development response with the configured continuation fallback and packet recovery tag.
