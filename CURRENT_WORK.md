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
- **Status:** forensic evidence complete; registry normalization next.

## Exact scope

1. **G1 — Sheets/Drive as current mutable authority with Git for policy/schema/tests.**
2. Normalize the historical Google-first implementation statement into the provider-neutral MIRA 2.0 canonical-authority contract without changing the accepted stock Google-first product direction.
3. Identify stable semantic feature IDs and implementation gaps for Authority Registry, structured-state/evidence adapters, bounded mutation/readback, and authority migration/cutover boundaries only as required by G1.

No G2/G3 portability audit, no remaining G rows, no F21-F23, no live provider provisioning, no migration execution, and no executable MIRA 2.0 product changes enter this packet.

## Forensic findings

1. **G1 is foundational and required, but the semantic feature is not “Google Sheets/Drive.”** Google Workspace is a supported/default ordinary-user adapter profile; provider identity is not capability proof and does not define MIRROR domain identity.
2. Add stable semantic feature **`AUTH-001` — Canonical Authority Registry and one-authority-per-data-class routing**.
3. `AUTH-001` owns the canonical mapping from mutable data class to one exact authority, including Authority UUID, data class, adapter/provider type, provider resource/namespace, failure domain, owner/scope, read/write/readback capability status, schema/migration version, sharing policy, last verified timestamp, recovery/backup reference and notes.
4. One canonical authority per data class does **not** mean one workbook/database/resource. Physical resource isolation follows failure-domain/privacy/volume needs while canonical identity/routing remains singular.
5. Add stable semantic feature **`STORE-001` — Provider-neutral structured-state and evidence-store adapter contracts with verified mutation/readback**.
6. `STORE-001` keeps structured state and retained evidence as distinct adapter roles. Structured state requires health/schema/exact-key get/bounded query/idempotent create-upsert/append-event/atomic-or-compensated mutation/readback/export-for-migration semantics. Evidence requires health/hash-preserving put/read/metadata/readback/retention/export semantics.
7. Normal mutable-state writes cross a bounded MIRROR service/adapter boundary that performs dependency preflight, authorization, schema validation, stable identity/idempotency, smallest required mutation, exact readback and audit. Clients and AI runtimes never receive unrestricted database authority or become direct canonical writers.
8. Git remains authoritative for durable source, policy, schemas, migrations, tests, feature manifests, non-secret configuration and source lineage under existing `DEV-001`/`SOURCE-001`. Git is **not** the mutable database for ordinary life state, evidence bodies or provider secrets.
9. Legacy `g-01` dependency assignment includes `authority-registry`, `integration-registry`, `evidence-store-rw`, `source-mutation` and `policy-source`. This is structurally useful but semantically over-bundled for runtime readiness.
10. `source-mutation` is required for durable behavior/policy/schema changes, not for every routine mutable-state transaction. Lack of source write/readback must not force otherwise healthy canonical state to pretend it is unavailable; source-editing/deployment changes degrade/block their own path under `SOURCE-001`.
11. The Integration Registry is capability/configuration/health observability, not a second business-state authority. G1 needs verified adapter health, but basic canonical state must not be blocked by unrelated external-integration catalog state. Integration Registry semantics remain separate for later category-G audit rather than being absorbed into `AUTH-001`.
12. Legacy dependency profiles are executable/tested for fail-closed capability resolution and module-scoped failure. `authority-registry` requires its exact Authority Registry authority plus structured-state read/write/readback; `evidence-store-rw` separately requires the selected evidence store plus evidence read/write/readback.
13. `starter/tools/provider_capability_router.py` plus `starter/tests/test_platform_portability.py` are executable/test-verified for provider-name non-proof, observed structured-state/evidence read-write-readback gates, fail-closed unknown capability keys, regulated approval evidence and provider-neutral readiness/degradation semantics.
14. `tests/test_failure_domain_architecture.py` test-verifies important architectural boundaries: canonical identity versus physical resource isolation, required-failure module blocking, unrelated-module continuation, recovery snapshots not becoming second writable masters and source-first cross-authority transaction behavior. Much of this is contract/string validation rather than a generic Authority Registry runtime.
15. No audited legacy-main executable implements a generic persistent Authority Registry router or complete provider-neutral `STORE-001` adapter layer. Therefore `AUTH-001` evidence ceiling is **`specified+tested-boundary`**, not implemented/test-verified as a runtime.
16. `STORE-001` evidence ceiling is **`specified+tested-boundary+candidate_unmerged`**: capability gating is test-verified, while generic adapter execution/readback remains unimplemented in audited main.
17. PR #31 is useful but internally mixed candidate evidence. `provider-defaults.json` makes Google Workspace default while keeping alternate state/evidence candidates; `storage-portability-contract.json` instead treats Google Sheets as migration/projection and declares a local SQLite starter. This confirms provider-neutral direction but not one coherent shipped topology.
18. PR #31 `starter/service/app.py` is a partial unmerged service candidate: it provides bounded HTTP commands, SQLite-backed UUID state, audit rows and post-write readback for a subset of inventory operations plus hashed local evidence ingestion. It directly opens SQLite rather than using a generic structured-state adapter and contains no Authority Registry router/cutover engine.
19. PR #31 `authority-schema.json` provides a broad Google-native table candidate but no generic Authority Registry table and no proof that the Google authority and SQLite service are one reconciled canonical deployment. It earns no MIRA 2.0 integration/live credit.
20. Backend/provider migration remains staged and reversible: candidate target is nonauthoritative until UUID/row/hash/relationship parity, bounded write/readback and recovery evidence pass; only then may `AUTH-001` switch the authority reference. There are never two writable masters.
21. Provider/backend migration is recorded as a G1 integrity rule and implementation gap, not promoted to a third semantic domain feature in this packet. G2/G3 portability audit may later refine/promote portability-specific feature semantics without changing `AUTH-001`/`STORE-001` identity.
22. Legacy catalog `live_external/live_readback_required` is historical deployment evidence only. Protected legacy production was not queried or mutated in this packet, so no MIRA 2.0 live-provider credit is claimed.
23. No live Google production state was touched and no executable MIRA 2.0 behavior changed.

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

1. Stable semantic IDs. **Satisfied by design: `AUTH-001`, `STORE-001`.**
2. Google-first ordinary-user direction remains adapter/default rather than domain identity. **Satisfied.**
3. Git authority/non-authority boundary explicit. **Satisfied.**
4. One canonical authority per mutable data class; physical isolation separate. **Satisfied.**
5. Bounded service mutation/idempotency/authorization/readback semantics. **Satisfied at contract boundary; generic MIRA 2.0 runtime unverified.**
6. Structured state versus evidence-store separation. **Satisfied.**
7. Authority Registry minimum semantics. **Satisfied at specification boundary.**
8. Failure isolation/module-scoped blocking. **Test-supported and satisfied.**
9. Staged reversible migration/no dual writable masters. **Satisfied at contract boundary.**
10. Conservative legacy/PR31 evidence reconciliation. **Satisfied.**
11. Only `FEATURES.md`, `BACKLOG.md`, `CURRENT_WORK.md` on branch. **So far satisfied.**
12. Bounded PR/merge/readback. **Pending.**
13. No legacy production/executable changes. **Satisfied.**

## Exact next action

1. Update `FEATURES.md`: add `AUTH-001` and `STORE-001`, add G1 foundation/integrity mapping and partial category-G audit status.
2. Diff-gate that commit; only `FEATURES.md` may change.
3. Update `BACKLOG.md` with bounded `AUDIT-G1` plus implementation work for Authority Registry core, provider-neutral state/evidence adapters and verified authority cutover/migration; preserve existing work rows except any dependency wording strictly required by this audit.
4. Diff-gate `BACKLOG.md` alone.
5. Close this `CURRENT_WORK.md` with exact commit evidence.
6. Compare branch to `main`; require zero commits behind and exactly `FEATURES.md`, `BACKLOG.md`, `CURRENT_WORK.md` changed.
7. Open bounded PR, verify server-side changed filenames/mergeability, merge exact verified head and remotely read back normalized state.
8. Rerank G2/G3, remaining G rows and F21-F23 from actual dependencies.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head when tools permit;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture new customer ideas in BACKLOG unless required for acceptance or explicitly reprioritized;
6. finish each MIRA-development response with the configured continuation fallback and packet recovery tag.
