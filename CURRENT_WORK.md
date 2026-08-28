# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active implementation packet and its resume point.

## Completed packet before this branch

### `M2-G1-003A` — API service semantics core

- **Merged PR:** #39
- **Merge SHA / main readback:** `01c98c4ae404fc8a90cc1cdaba0065aca4c50a37`
- **Post-merge completion checkpoint / this branch start SHA:** `bcae2707444a57420b93c99c808adbdce64d9a5f`
- **Remote CI:** GitHub Actions run `33210306251`; compile + 30 unit tests passed.
- **Result:** `API-CORE-001A` is implemented/test-verified.

## Active packet

### `M2-G1-003B` — Scoped client authentication and HTTP transport

- **Work ID:** `API-CORE-001B`
- **Class:** implementation / security-data-integrity prerequisite
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `impl/g1-003b-http-auth-boundary`
- **Branch start SHA:** `bcae2707444a57420b93c99c808adbdce64d9a5f`
- **Status:** activated; implementation next.

## Objective

Implement a stdlib-only HTTP transport/authentication boundary over `ApiService`: opaque scoped client sessions with hashed bearer-token storage, expiry/revocation, HTTPS enforcement hook, bounded JSON request parsing, stable HTTP error mapping and WSGI-compatible request handling without provider/deployment coupling.

## Acceptance criteria

1. Issue opaque bearer credentials only from explicit actor/client/grant input; raw token returned once and only cryptographic hash retained.
2. Stable session IDs, issue/expiry timestamps and explicit revocation; expired/revoked/unknown tokens fail authentication.
3. Authentication reconstructs exact `AuthenticatedPrincipal` grants; no implicit relationship/provider/device grants.
4. WSGI boundary exposes POST `/v1/query`, POST `/v1/commands`, GET `/v1/health` only.
5. Protected routes require Bearer auth; malformed/missing credentials return 401 without service-state calls.
6. Optional `require_https` rejects protected cleartext before authentication/service execution.
7. JSON body must be object and bounded by content length; malformed/oversized/unknown route/method fail explicitly.
8. Transport converts JSON to existing 001A envelopes only; canonical policy remains in `ApiService`.
9. API errors map deterministically to HTTP status + stable JSON error shape; unexpected errors hide internals.
10. Success responses serialize exact service result/readback information without secrets.
11. Deterministic tests cover issuance/hash/expiry/revoke, HTTPS/401, status mapping, query/command success and no-service-call auth failures.
12. No deployment/TLS certificate/provider/Google/Android/evidence/legacy-production work.

## Scope guard

Allowed:
- in-memory session credential store/authenticator;
- WSGI-compatible transport adapter;
- request/response serialization and error mapping;
- deterministic tests and package exports.

Excluded:
- Internet/cloud deployment;
- certificate/proxy configuration;
- provider adapters;
- Google state;
- Android/client implementation;
- evidence store;
- cross-person permission engine;
- legacy production state.

## Exact next action

1. Implement `mira/http_transport.py` and tests.
2. Update package exports.
3. Run full suite, bounded PR, remote CI.
4. Merge exact green head.
5. Mark `API-CORE-001` umbrella complete/test-verified and activate `CORE-SYNTHETIC-ROUNDTRIP`.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture unrelated ideas in BACKLOG unless required for acceptance or explicitly reprioritized.
