# MIRA 2.0 CURRENT WORK

Git is authoritative. This file records the completed Google structured-state adapter packet and exact deployment prerequisite discovered during runtime assembly.

## Completed packet

### `M2-M0-002` — Minimal Google structured-state adapter

- **Work ID:** `GOOGLE-STORE-ADAPTER-001`
- **Merged PR:** #45
- **Merge SHA / main readback:** `88d7b4666fbcf4b77ea60baa3c4b3735bfa5aadb`
- **Branch:** `integration/m0-002-google-store-adapter`
- **Branch start SHA:** `ae30e8b304da097570d3d0061fd9c863b654f3ca`
- **CI-verified PR head:** `3018a23bf45f79066c5e1f1d65bbb0cf9c3b5145`
- **Final GitHub Actions run:** `33212658200`
- **Remote verification:** compile + feature registry + code ownership + full unit/integration suite succeeded.
- **Result:** Google Sheets REST gateway and single-writer `StructuredStateAdapter` are implemented/test-verified. The isolated live Sheet schema and equivalent create/update/idempotency/readback pattern are provider-readback verified. Live Python OAuth execution is not yet claimed.
- **Provider integrity:** synthetic-only Sheet, corrected event schema, replay-compatible seed fixture, readable rendered tables, no committed provider IDs/credentials/private data.

## Product-state checkpoint

MIRA 2.0 has a tested shared API core and a tested Google Sheets persistence adapter, plus a real isolated Google Sheet whose schema/mutation pattern is provider-verified. The service is not yet hosted and the Python gateway has not yet authenticated live to Google.

## Hard dependency discovered before deployment

`AuthorityRegistry` is defined as persistent. A managed service cannot safely bootstrap it into an in-memory store on every process restart. The first deployment therefore needs persisted `authority` and `authority_binding` records before hosting.

For M2-M0, the smallest safe model is to use the same isolated Google Sheets `StructuredStateAdapter` as both:
- registry store for `authority` / `authority_binding`; and
- canonical store for `entity`.

API routing still asks the registry for data class `entity`, and the service only operates on the routed data class, so registry rows do not become client-visible entity rows. A later backend split remains possible through `AUTH-001` migration semantics.

## Selected successor

### `M2-M0-003` — Persistent Google Authority Registry bootstrap

- **Related work IDs:** `AUTHORITY-REGISTRY-001`, `GOOGLE-STORE-ADAPTER-001`
- **Class:** hard deployment prerequisite / integrity bootstrap
- **Planned branch:** `integration/m0-003-google-authority-bootstrap`

### Objective

Persist and verify the canonical M2-M0 `entity` Authority binding in the isolated Google store and implement an idempotent runtime bootstrap that creates missing routing state once but fails closed on unexpected existing metadata.

### Acceptance criteria

1. Extend live sandbox metadata resource types to exactly include `authority`, `authority_binding`, and `entity`.
2. Persist one synthetic verified/enabled Authority record for the Google Sheets adapter using a logical non-secret resource reference, not a live provider ID.
3. Persist one `authority_binding` record binding data class `entity` to that Authority.
4. Authority and binding writes use normal adapter-compatible fingerprints/idempotency result envelopes and provider readback.
5. Implement `runtime_bootstrap` helper over `AuthorityRegistry` that registers the runtime adapter, creates missing Authority/binding with deterministic idempotency keys, and is safe to call repeatedly.
6. If an Authority/binding already exists with materially different metadata, startup fails closed rather than overwriting/rebinding it.
7. Unit tests prove first bootstrap, replay/restart, mismatch rejection, and successful `resolve("entity")` to the mounted adapter.
8. Update code ownership/direct verification for new production code.
9. No live provider IDs/credentials in Git; all live provider rows remain synthetic.
10. All CI gates green; bounded PR/merge/readback.
11. After this packet, managed runtime/container work may proceed without an ephemeral Authority Registry.

## Exact next action

1. Create `integration/m0-003-google-authority-bootstrap` from this exact main checkpoint.
2. Activate `M2-M0-003`.
3. Extend live sandbox metadata and write/read back Authority + entity binding using adapter-equivalent provider rows.
4. Implement/test idempotent runtime bootstrap and update ownership manifest.
5. PR/CI/merge, then activate the provider-neutral managed-runtime deployment packet.

## Recovery protocol

On any new conversation/session:
1. read this file first and verify repository/branch/head;
2. rediscover provider resources by exact search when needed;
3. never commit live provider IDs/private data;
4. do not claim live Python Google OAuth execution until a managed runtime actually performs it;
5. continue only the active packet unless a blocker forces scope change.
