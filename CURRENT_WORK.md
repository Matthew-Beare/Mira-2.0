# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and its exact resume point.

## Completed packet before this branch

### `M2-G0-008B` — Personal knowledge/reference foundation audit — legacy G17 + G18 + F19

- **Merged PR:** #29
- **Merge SHA:** `156bbd3f7c654b2e3bef08a9b37dbe4d93726da1`
- **Main activation commit for this packet:** `491acd9573ad70b1d45c8b20f0d1ec687cbd2c24`

## Active packet

- **Packet ID:** `M2-G0-008C`
- **Name:** Canonical mutable authority boundary audit — legacy G1
- **Class:** forensic audit / foundational prerequisite
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `audit/g0-008c-canonical-authority`
- **Branch start SHA:** `491acd9573ad70b1d45c8b20f0d1ec687cbd2c24`
- **Research checkpoint:** `28bc902046bf7f0fc361fcaa4d3dfbcf2994daff`
- **Feature registry commit:** `d53959e43888038e27e469c73f1f0be52c138338`
- **Backlog commit:** `bf8fa0ee5e34b5aaad6dcaf4944cb781b105a58f`
- **Status:** acceptance complete; bounded PR/merge/readback pending.

## Exact audited scope

1. **G1 — Sheets/Drive as current mutable authority with Git for policy/schema/tests.**
2. Normalize the historical Google-first implementation statement into the provider-neutral MIRA 2.0 canonical-authority contract without changing the accepted stock Google-first product direction.
3. Identify stable semantic feature IDs and implementation gaps for Authority Registry, structured-state/evidence adapters, bounded mutation/readback and authority migration/cutover boundaries only as required by G1.

No G2/G3 portability audit, no remaining G rows, no F21-F23, no live provider provisioning, no migration execution, and no executable MIRA 2.0 product changes entered this packet.

## Canonical result

1. Added **`AUTH-001` — Canonical Authority Registry and one-authority-per-data-class routing** with evidence `specified+tested-boundary`.
2. Added **`STORE-001` — Provider-neutral structured-state and evidence-store adapter contracts with verified mutation/readback** with evidence `specified+tested-boundary+candidate_unmerged`.
3. G1 now maps to provider-neutral `AUTH-001` + `STORE-001`, with existing `DEV-001`/`SOURCE-001` retaining Git/source authority. Google Sheets/Drive remain accepted/default adapter choices, not semantic domain IDs.
4. `AUTH-001` owns exact canonical authority routing and metadata: Authority UUID, data class, adapter/provider, exact resource/namespace, failure domain, owner/scope, read/write/readback capability state, schema/migration version, sharing policy, last verification and recovery/backup reference.
5. Exactly one writable canonical authority exists per mutable data class. Physical resources may be split for failure-domain/privacy/volume reasons without creating multiple truths.
6. `STORE-001` keeps structured-state and evidence-store roles distinct. Structured state requires bounded/exact reads, idempotent mutation, append-event where appropriate, atomic-or-compensated semantics, audit, readback and export. Evidence requires hash-preserving put/read/metadata/readback/retention/export semantics.
7. Normal mutation crosses a bounded MIRROR service/adapter boundary with dependency preflight, authorization, schema validation, stable identity/idempotency, smallest required write, audit and exact readback. Clients/AI runtimes are not unrestricted canonical database writers.
8. Git is authoritative for durable code, policy, schemas, migrations, tests, feature manifests, non-secret configuration and source lineage. It is not the ordinary mutable-state database, evidence-body store or provider-secret store.
9. Legacy G1 `source-mutation` is over-bundled as a universal runtime dependency. Source write/readback gates durable behavior/policy/schema changes, not every routine canonical-state transaction.
10. Legacy G1 `integration-registry` is also over-bundled as a universal canonical-state blocker. Integration health/config remains separate and will be audited later; unrelated integration-catalog failure cannot manufacture canonical-state failure.
11. Dependency/capability routing is executable/test-supported for provider-name non-proof, structured/evidence read-write-readback gates, fail-closed unknowns and module-scoped failure/degradation.
12. No audited legacy-main executable provides a generic persistent Authority Registry router or complete provider-neutral storage adapter runtime, so runtime implementation credit is not claimed.
13. PR #31 is mixed unmerged candidate evidence only: Google-default provider configuration, a separate storage-portability experiment, and direct SQLite service commands/readback exist, but no generic Authority Registry/cutover engine or coherent proof of one reconciled canonical topology.
14. Provider/backend migration is staged and reversible. Candidate target is nonauthoritative until UUID/row/hash/relationship parity, bounded mutation/readback and recovery evidence pass; then `AUTH-001` may switch the authority reference. There are never two writable masters.
15. Provider/backend cutover remains an integrity rule plus implementation work `AUTHORITY-MIGRATION-001`; G2/G3 may later promote/refine portability-specific semantic features without changing `AUTH-001` or `STORE-001` identity.
16. `DATA-SANDBOX` dependency is now explicit: `AUTHORITY-REGISTRY-001` + `STORE-ADAPTER-001` + `GOOGLE-BOOTSTRAP-001` replace the previous vague “canonical state contract” wording.
17. Historical legacy G1 `live_external` status is not transferred to MIRA 2.0. No protected legacy provider state was queried or mutated and no MIRA 2.0 live-provider credit is claimed.
18. No live Google production state was touched and no executable MIRA 2.0 behavior changed.

## Durable normalization evidence

- `FEATURES.md` commit `d53959e43888038e27e469c73f1f0be52c138338`:
  - immediate diff gate: only `FEATURES.md` changed;
  - 23 additions / 1 audit-status replacement;
  - adds `AUTH-001`, `STORE-001`, G1 foundation mapping and canonical-authority integrity notes.
- `BACKLOG.md` commit `bf8fa0ee5e34b5aaad6dcaf4944cb781b105a58f`:
  - immediate diff gate: only `BACKLOG.md` changed;
  - 20 additions / 3 replacements;
  - adds `AUDIT-G1`, `AUTHORITY-REGISTRY-001`, `STORE-ADAPTER-001`, `AUTHORITY-MIGRATION-001`, bounded findings, and exact `DATA-SANDBOX` prerequisites.

## Evidence paths

- `starter/STATE_AUTHORITY_MODEL.md`
- `starter/runtime-interface-contract.json`
- `docs/runtime-platform-architecture.md`
- `starter/behavior-dependencies.json`
- `starter/tools/provider_capability_router.py`
- `starter/tests/test_platform_portability.py`
- `starter/tests/test_behavior_dependency_check.py`
- `tests/test_failure_domain_architecture.py`
- PR #31 `starter/provider-defaults.json` — candidate/reference only.
- PR #31 `starter/storage-portability-contract.json` — candidate/reference only.
- PR #31 `starter/service/app.py` — partial SQLite/service candidate only.
- PR #31 `starter/chatgpt-google-native/authority-schema.json` — Google-native schema candidate only.

## Acceptance criteria

1. Stable semantic IDs. **Satisfied: `AUTH-001`, `STORE-001`.**
2. Google-first default remains adapter direction, not domain identity. **Satisfied.**
3. Git authority/non-authority boundary explicit. **Satisfied.**
4. One canonical authority per mutable data class; physical isolation separate. **Satisfied.**
5. Bounded mutation/idempotency/authorization/readback semantics. **Satisfied at contract boundary; MIRA 2.0 runtime unverified.**
6. Structured state versus evidence-store separation. **Satisfied.**
7. Authority Registry minimum semantics. **Satisfied at specification boundary.**
8. Failure isolation/module-scoped blocking. **Test-supported and satisfied.**
9. Staged reversible migration/no dual writable masters. **Satisfied at contract boundary.**
10. Conservative legacy/PR31 evidence reconciliation. **Satisfied.**
11. Only `FEATURES.md`, `BACKLOG.md`, `CURRENT_WORK.md` on branch. **Satisfied so far; final branch gate pending.**
12. Bounded PR/merge/readback. **Pending.**
13. No legacy production/executable changes. **Satisfied.**

## Exact next action

1. Compare `audit/g0-008c-canonical-authority` against `main`; require zero commits behind and exactly `FEATURES.md`, `BACKLOG.md`, `CURRENT_WORK.md` changed.
2. Open a bounded PR to `main`.
3. Verify GitHub server-side changed filenames and mergeability.
4. Merge using the exact verified PR head SHA.
5. Remotely read back `AUTH-001`, `STORE-001`, G1 mapping and new authority/store backlog work from `main`.
6. Rerank G2/G3, remaining category-G rows and F21-F23; activate the next bounded packet from actual dependency priority.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head when tools permit;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture new customer ideas in BACKLOG unless required for acceptance or explicitly reprioritized;
6. finish each MIRA-development response with the configured continuation fallback and packet recovery tag.
