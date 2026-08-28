# MIRA 2.0 CURRENT WORK

Git is authoritative. This file records the completed persistent Authority bootstrap packet and the exact bounded deployment successor.

## Completed packet

### `M2-M0-003` — Persistent Google Authority Registry bootstrap

- **Related work IDs:** `AUTHORITY-REGISTRY-001`, `GOOGLE-STORE-ADAPTER-001`
- **Merged PR:** #46
- **Merge SHA / main readback:** `77b2099a9d1efa8306dd160b8d309aa9fb12dbc0`
- **Branch:** `integration/m0-003-google-authority-bootstrap`
- **Branch start SHA:** `7929404403b56286a25399b16797658885cc2d97`
- **Implementation commit:** `97d959ddf79158205b80cb4d761ce4c79d5c2af9`
- **CI-verified PR head:** `0ecdce9b4e53d9f7b3b301518e5dba64a5bc51d6`
- **Final GitHub Actions run:** `33216400965`
- **Remote verification:** compile + feature registry + code ownership + full unit/integration suite succeeded.
- **Provider readback:** isolated synthetic Google store exactly exposes `authority`, `authority_binding`, and `entity`; verified/enabled `google-sheets-m0` Authority plus `binding-entity` are persisted with matching idempotency records and logical non-secret resource references.
- **Result:** restart-safe canonical routing metadata is persisted; runtime bootstrap creates only missing routing state, rejects materially different persisted metadata, mounts the adapter, and resolves `entity` before service use.
- **Boundary:** live Python Google OAuth execution and live hosted runtime execution are still not claimed.

## Product-state checkpoint

MIRA 2.0 now has a tested shared API core, deterministic synthetic proof, Google Sheets persistence adapter, isolated synthetic Google provider state, persisted canonical Authority routing, and fail-closed runtime Authority bootstrap. The remaining M2-M0 gap is deployment/runtime assembly, live managed execution, then the stock-ChatGPT client proof.

## Deployment constraint discovered

`WsgiApiApp` is deployable as a WSGI boundary, but its current bearer credential implementation is `InMemorySessionStore`. Randomly issued sessions disappear on process restart. That is acceptable for synthetic tests but is not sufficient evidence for restart-stable managed service credentials.

Do not paper over this by calling a container deployment complete. The deployment work is split into bounded slices:
1. assemble a provider-neutral managed runtime/application factory with explicit injected configuration and a credential/authentication boundary;
2. prove restart-stable injected/scoped credentials plus live managed Google authentication/provider execution and HTTPS deployment;
3. only then prove the stock ChatGPT client path.

## Selected successor

### `M2-M0-004` — Managed API runtime assembly

- **Related work ID:** `API-DEPLOYMENT-001`
- **Class:** hard deployment prerequisite / bounded runtime assembly
- **Planned branch:** `integration/m0-004-managed-api-runtime`

### Objective

Assemble the existing Google structured-state adapter, persistent Authority bootstrap, API service, audit boundary, credential/authenticator boundary, and WSGI transport into one deterministic managed-runtime application factory driven only by explicit injected configuration. Prove startup validation/fail-closed behavior with synthetic/fake provider dependencies. Do not claim live hosting or live Google OAuth in this packet.

### Acceptance criteria

1. Add one provider-neutral runtime configuration model with strict validation; no provider IDs, bearer credentials, tokens, account identifiers, or private data are committed.
2. Add one application/runtime assembly boundary that wires structured-state adapter -> `AuthorityRegistry` -> `bootstrap_runtime_authority` -> `ApiService` -> authenticated `WsgiApiApp` without duplicating authority or API semantics.
3. Runtime construction accepts provider gateway/token and credential/authenticator dependencies by injection so tests require no external network or real secrets.
4. Startup performs provider schema/health and canonical `resolve("entity")` verification before the application is considered ready.
5. Missing/malformed configuration, unhealthy provider, schema mismatch, or persisted Authority/binding mismatch fails closed before serving protected API operations.
6. Make the HTTP authentication dependency an explicit protocol/boundary rather than hard-coding runtime assembly to process-local random session issuance.
7. Preserve current `InMemorySessionStore` behavior for synthetic tests while enabling a later restart-stable managed credential implementation without changing `WsgiApiApp` request semantics.
8. Tests prove successful assembly, config rejection, provider/authority startup failure, and authenticated query/command routing through the assembled WSGI app using synthetic dependencies.
9. Update package exports only where they improve stable composition; do not expose secrets or provider resource identifiers.
10. Update code ownership/direct verification for every new production module.
11. All CI gates green; bounded PR/merge/readback.
12. Live managed hosting, TLS-provider verification, restart-stable injected secret implementation, live Google OAuth/provider execution, and stock ChatGPT connection remain explicit successor evidence, not claims of this packet.

## Exact next action

1. Create `integration/m0-004-managed-api-runtime` from this exact main checkpoint.
2. Activate `M2-M0-004` and reconcile stale completed critical-path statuses in `BACKLOG.md` while preserving the ranked dependency graph.
3. Generalize the WSGI authentication constructor to an explicit authenticator protocol without changing request behavior.
4. Implement/test the runtime configuration/application factory and startup fail-closed checks.
5. Update ownership, PR/CI/merge, then activate the live managed deployment/credential/provider-execution slice of `API-DEPLOYMENT-001`.

## Recovery protocol

On any new conversation/session:
1. read this file first and verify repository/branch/head;
2. never commit live provider IDs/private data/secrets;
3. do not claim live Python Google OAuth or managed hosting until provider/runtime readback proves it;
4. continue only the active packet unless a blocker forces scope change.
