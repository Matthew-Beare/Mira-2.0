# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and its exact resume point.

## Completed packet before this branch

### `M2-G0-008B` — Personal knowledge/reference foundation audit — legacy G17 + G18 + F19

- **Merged PR:** #29
- **Merge SHA:** `156bbd3f7c654b2e3bef08a9b37dbe4d93726da1`
- **Result:** refined `KNOW-001`, added `KNOW-002`, normalized F19 exact service key `knowledge`, and separated provider filing/search projection from canonical Knowledge identity.

## Active packet

- **Packet ID:** `M2-G0-008C`
- **Name:** Canonical mutable authority boundary audit — legacy G1
- **Class:** forensic audit / foundational prerequisite
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `audit/g0-008c-canonical-authority`
- **Base main SHA:** `156bbd3f7c654b2e3bef08a9b37dbe4d93726da1`
- **Status:** activated; branch creation and bounded forensic audit next.

## Exact scope

1. **G1 — Sheets/Drive as current mutable authority with Git for policy/schema/tests.**
2. Normalize the historical Google-first implementation statement into the provider-neutral MIRA 2.0 canonical-authority contract without changing the accepted stock Google-first product direction.
3. Identify stable semantic feature IDs and implementation gaps for Authority Registry, structured-state/evidence adapters, bounded mutation/readback, and authority migration/cutover boundaries only as required by G1.

No G2/G3 portability audit, no remaining G rows, no F21-F23, no live provider provisioning, no migration execution, and no executable MIRA 2.0 product changes enter this packet.

## Preliminary boundary evidence

1. Legacy `STATE_AUTHORITY_MODEL.md` states storage providers are adapters and canonical identities, schemas, events, provenance and business rules belong to MIRROR rather than Sheets/Drive/SQL/client layout.
2. Every mutable data class has exactly one canonical authority recorded in an Authority Registry; one canonical authority does not require one giant physical workbook/database.
3. Git owns durable source/policy/schema/tests/migrations/non-secret config and lineage, but is explicitly not the mutable database for ordinary life state.
4. Structured state and retained evidence are separate adapter roles. Google Sheets/Drive are current candidates, not architectural requirements.
5. Normal state mutation crosses a bounded service/API contract with authorization, dependency preflight, schema validation, stable identity/idempotency, write, readback and audit. Clients and AI runtimes do not write canonical storage directly.
6. The runtime-interface contract requires provider-neutral structured-state operations including health/schema/get/bounded-query/idempotent-upsert/append-event/atomic-or-compensated mutation/readback/export-for-migration and corresponding evidence-store hash/readback/retention/export operations.
7. Backend migration preserves canonical UUIDs and changes Authority Registry references only after parity/readback/restore evidence; a migration copy is nonauthoritative until verified cutover.
8. Therefore the historical phrase “Sheets/Drive as current mutable authority” is deployment evidence for the Google-first adapter, not the MIRA 2.0 semantic feature name.

## Acceptance criteria

1. Assign stable semantic feature ID(s) for canonical authority registry/data-class routing and provider-neutral mutable-state/evidence adapter contract without making Google the domain identity.
2. Preserve the stock product direction that Google Workspace may be the default ordinary-user adapter while keeping provider choice replaceable.
3. State exactly what Git is authoritative for and explicitly what it is not authoritative for.
4. Preserve one canonical authority per mutable data class, with physical resource isolation/failure domains treated separately.
5. Preserve bounded service/API mutation, idempotency, authorization and exact readback before success claims.
6. Preserve structured-state versus evidence-store separation and stable identity across provider relocation.
7. Preserve Authority Registry minimum semantics: authority UUID/data class/adapter/resource/failure domain/scope/capability/schema/sharing/verification/recovery metadata.
8. Preserve failure isolation: unavailable authority blocks only affected state-changing paths unless a shared invariant requires wider stop.
9. Preserve staged reversible backend migration and explicit cutover/readback; no dual writable masters.
10. Reconcile legacy tests/contracts and PR #31 candidate evidence conservatively; requirement and evidence levels remain separate.
11. Update only `FEATURES.md`, `BACKLOG.md`, `CURRENT_WORK.md` on the packet branch.
12. Open bounded PR, verify exact changed files/mergeability, merge exact head and remotely read back normalized state.
13. No live legacy production state and no executable MIRA 2.0 behavior changes.

## Exact next action

1. Create branch `audit/g0-008c-canonical-authority` from the activation commit containing this file.
2. Audit `STATE_AUTHORITY_MODEL.md`, `runtime-interface-contract.json`, runtime/platform portability tests and relevant dependency assignments for actual implementation/test evidence.
3. Inspect PR #31 only for materially relevant Authority Registry/storage-portability/service-boundary candidate evidence.
4. Decide stable MIRA 2.0 semantic IDs and exact evidence ceiling.
5. Checkpoint findings in `CURRENT_WORK.md` before modifying `FEATURES.md` or `BACKLOG.md`.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head when tools permit;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture new customer ideas in BACKLOG unless required for acceptance or explicitly reprioritized;
6. finish each MIRA-development response with the configured continuation fallback and packet recovery tag.
