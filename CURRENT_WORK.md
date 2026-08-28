# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active managed-runtime assembly packet and its resume point.

## Completed packet before this branch

### `M2-M0-003` — Persistent Google Authority Registry bootstrap

- **Merged PR:** #46
- **Merge SHA / main readback:** `77b2099a9d1efa8306dd160b8d309aa9fb12dbc0`
- **Final GitHub Actions run:** `33216400965`; compile + feature registry + code ownership + full suite succeeded.
- **Result:** provider metadata/routing rows are readback-verified and fail-closed runtime Authority bootstrap is implemented/test-verified.
- **Post-merge close/select checkpoint / this branch start SHA:** `7f0b3fa304825c01b3ea9cf390231140b73200fb`

## Active packet

### `M2-M0-004` — Managed API runtime assembly

- **Related work ID:** `API-DEPLOYMENT-001`
- **Class:** hard deployment prerequisite / bounded runtime assembly
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `integration/m0-004-managed-api-runtime`
- **Branch start SHA:** `7f0b3fa304825c01b3ea9cf390231140b73200fb`
- **Status:** activated; backlog reconciliation and runtime assembly implementation next.

## Objective

Assemble the existing Google structured-state adapter, persistent Authority bootstrap, API service, audit boundary, credential/authenticator boundary, and WSGI transport into one deterministic managed-runtime application factory driven only by explicit injected configuration. Prove startup validation/fail-closed behavior with synthetic/fake provider dependencies. Do not claim live hosting or live Google OAuth in this packet.

## Acceptance criteria

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

## Deployment constraint

`InMemorySessionStore` loses random issued bearer credentials on process restart. This packet exposes authentication as an explicit boundary but does not falsely claim restart-stable credential persistence. The successor live-deployment slice must use an injected/restart-stable scoped credential mechanism and provider readback before `API-DEPLOYMENT-001` is fully complete.

## Exact next action

1. Reconcile stale completed M2-M0 critical-path statuses in `BACKLOG.md` and record this packet as the active bounded child of `API-DEPLOYMENT-001`.
2. Generalize `WsgiApiApp` authentication constructor to an explicit authenticator protocol without changing request behavior.
3. Implement provider-neutral runtime config/application assembly and startup fail-closed checks.
4. Add direct synthetic tests, update ownership, run CI, PR/merge/readback.
5. Activate the live managed deployment/credential/provider-execution slice after this packet closes.

## Recovery protocol

Read this file first, verify branch/head, keep provider IDs/private data/secrets out of Git, and continue only `M2-M0-004` unless a blocker forces scope change.
