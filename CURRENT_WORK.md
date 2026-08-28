# MIRA 2.0 CURRENT WORK

Git is authoritative. This file records the completed API service-semantics packet and exact transport/auth successor.

## Completed packet

### `M2-G1-003A` — API service semantics core

- **Work ID:** `API-CORE-001A`
- **Merged PR:** #39
- **Merge SHA / main readback:** `01c98c4ae404fc8a90cc1cdaba0065aca4c50a37`
- **Branch:** `impl/g1-003a-api-service-core`
- **Branch start SHA:** `1d4d0108408e76a34a1dea4dcef0cb690e5dd96c`
- **CI-verified PR head:** `50229390a4831d80c84e5130abd8c1483f3d02b2`
- **GitHub Actions run:** `33210306251`
- **Remote verification:** compile succeeded; full suite **30 tests, 0 failures/errors**.
- **Result:** versioned envelopes, already-authenticated principal/grants, same-user fail-closed authorization, compatibility preflight, Authority Registry-only routing, mandatory idempotency/revision propagation, exact readback, stable API error mapping and nonauthoritative audit recording are implemented/test-verified.

## API umbrella state

`API-CORE-001` has two bounded children:
- `API-CORE-001A` — **complete/test-verified**.
- `API-CORE-001B` — client/session authentication + HTTP transport — **next**.

The umbrella becomes implemented/test-verified after 001B passes.

## Selected successor

### `M2-G1-003B` — Scoped client authentication and HTTP transport

- **Work ID:** `API-CORE-001B`
- **Class:** implementation / security-data-integrity prerequisite
- **Planned branch:** `impl/g1-003b-http-auth-boundary`
- **Dependency satisfied:** `API-CORE-001A` is merged/test-verified.

### Objective

Implement a stdlib-only HTTP transport/authentication boundary over `ApiService`: opaque scoped client sessions with hashed bearer-token storage, expiry/revocation, HTTPS enforcement hook, bounded JSON request parsing, stable HTTP error mapping and WSGI-compatible request handling without provider/deployment coupling.

### Acceptance criteria

1. Issue opaque bearer credentials only from explicit actor/client/grant input; raw token is returned once and only a cryptographic hash is retained.
2. Sessions have stable session IDs, issued/expiry timestamps and explicit revocation; expired/revoked/unknown tokens fail authentication.
3. Authentication reconstructs the exact `AuthenticatedPrincipal` grants; no relationship/provider/device identity can add grants implicitly.
4. WSGI HTTP boundary exposes bounded `/v1/query` and `/v1/commands` POST routes plus a non-secret `/v1/health` GET route.
5. Protected routes require `Authorization: Bearer`; malformed/missing credentials return 401 without calling service state.
6. Optional `require_https` transport hook rejects protected cleartext requests before authentication/service execution.
7. Request bodies are JSON objects with bounded content length; malformed/oversized/unknown routes/methods fail explicitly.
8. JSON requests are converted to existing 001A envelopes only; transport layer does not duplicate canonical policy/authorization/state semantics.
9. API errors map deterministically to HTTP status + `{error:{code,message}}`; unexpected failures do not leak internals.
10. Successful responses serialize exact service result/readback information without secrets.
11. Deterministic tests cover issuance/authentication, token hashing, expiry/revocation, HTTPS gate, 401/403/409/404/400 mapping, query/command success and no-service-call auth failures.
12. No external network deployment, TLS certificate management, provider adapter, Google, Android, evidence store or legacy production state.

## Exact next action

1. Create `impl/g1-003b-http-auth-boundary` from this exact main checkpoint.
2. Activate `M2-G1-003B` on the branch.
3. Implement session auth + WSGI transport and deterministic tests.
4. Require full local + GitHub CI green.
5. Merge exact verified head; then `API-CORE-001` is complete and the next packet is `CORE-SYNTHETIC-ROUNDTRIP`.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture unrelated ideas in BACKLOG unless required for acceptance or explicitly reprioritized.
