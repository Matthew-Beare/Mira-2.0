# MIRA 2.0 CURRENT WORK

Git is authoritative. This file records the completed shared API core and exact synthetic integration successor.

## Completed packet

### `M2-G1-003B` — Scoped client authentication and HTTP transport

- **Work ID:** `API-CORE-001B`
- **Merged PR:** #40
- **Merge SHA / main readback:** `247de3c0e30415f93c7bba65d141ca17f706571f`
- **Branch:** `impl/g1-003b-http-auth-boundary`
- **Branch start SHA:** `bcae2707444a57420b93c99c808adbdce64d9a5f`
- **CI-verified PR head:** `da1fa4025f8e3e3fc1f76e4b8b39681d52aadd1d`
- **GitHub Actions run:** `33210581967`
- **Remote verification:** compile + full unit suite succeeded, including 10 new auth/WSGI transport tests.
- **Result:** opaque scoped bearer sessions, hash-only token retention, expiry/revocation, exact principal reconstruction, HTTPS gate, bounded WSGI routes/body parsing, stable HTTP error mapping and exact success serialization are implemented/test-verified.

## `API-CORE-001` umbrella status

- `API-CORE-001A` transport-independent service semantics: **implemented/test-verified**.
- `API-CORE-001B` client/session authentication + HTTP transport: **implemented/test-verified**.
- Therefore `API-CORE-001` is now **implemented/test-verified for the synthetic same-user boundary**.
- This is not yet deployment/live-provider proof. No public hosting, Google adapter, ChatGPT client or Android client is claimed.

## Selected successor

### `M2-G1-004` — Synthetic HTTP roundtrip integration proof

- **Work ID:** `CORE-SYNTHETIC-ROUNDTRIP`
- **Class:** integration verification / prerequisite
- **Planned branch:** `verify/g1-004-synthetic-roundtrip`
- **Dependencies satisfied:** `STORE-ADAPTER-001A`, `AUTHORITY-REGISTRY-001`, `API-CORE-001A`, `API-CORE-001B`.

### Objective

Prove the assembled MIRA 2.0 stack end-to-end without external provider state: synthetic Authority Registry + canonical structured-state adapter + API service + scoped session auth + WSGI HTTP boundary must create, read, update, replay and reject stale/conflicting mutation for one canonical entity with exact readback and audit evidence.

### Acceptance criteria

1. Integration fixture assembles distinct registry and canonical data stores, registers one verified Authority and explicitly binds one data class.
2. A scoped client session performs entity create through HTTPS WSGI POST `/v1/commands`; response revision/readback are exact.
3. HTTPS WSGI POST `/v1/query` reads the same canonical entity from the bound Authority.
4. A second upsert with expected current revision mutates the same entity and increments revision exactly once.
5. Exact replay of that second command returns `idempotent_replay=true` without another revision increment.
6. Reusing the replay key with different material input returns HTTP 409 and leaves canonical state unchanged.
7. A stale expected revision returns HTTP 409 and leaves canonical state unchanged.
8. Missing/invalid bearer request cannot mutate state and is absent from canonical records.
9. Service audit evidence identifies actor/client/action/resource/outcome and the exact Authority for successful and failed authorized requests.
10. Direct canonical-store readback matches the final HTTP/API representation, proving no second HTTP/client-side state authority.
11. Full repository CI passes with the integration proof.
12. No Google/provider/deployment/Android/evidence-store/legacy production state.

## Exact next action

1. Create `verify/g1-004-synthetic-roundtrip` from this exact main checkpoint.
2. Activate `M2-G1-004`.
3. Add one bounded integration test/harness using the real merged layers, not mocks for canonical routing.
4. Require PR-triggered full CI green, merge/readback.
5. Then execute early repository growth gates (`FEATURE-REGISTRY-001` and `CODE-OWNERSHIP-001`) before provider/client fan-out.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture unrelated ideas in BACKLOG unless required for acceptance or explicitly reprioritized.
