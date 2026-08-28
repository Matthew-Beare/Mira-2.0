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
- **Activation commit:** `e9d77b2db5267901089a7c4bed2eedf68277536e`
- **Session/WSGI implementation:** `607b622b064519dc075207894f60bd0c985cf2a6`
- **Transport tests:** `586293ffbc19413efedcababeed785dd6b4edc4d`
- **Package exports:** `b69146d81d238a677c672f17792c2d0eec0a324c`
- **Status:** implementation/test content complete; bounded PR and remote CI are the executable verification gate.

## Implemented component

Component: **http-auth-boundary**

Owned production surface:
- `mira/http_transport.py` — scoped session issuance/authentication/revocation plus bounded WSGI HTTP transport.
- `mira/__init__.py` — package exports.

Direct verification:
- `tests/test_http_transport.py` plus the existing 30-test structured-state/Authority/API suite.
- existing `.github/workflows/ci.yml` compiles all package/tests and runs the full stdlib unit suite.

## Implemented semantics

- opaque bearer sessions issued only from explicit `AuthenticatedPrincipal` input;
- raw bearer token returned only in `IssuedCredential`; store retains SHA-256 token hash, actor/client IDs, exact grants and lifecycle metadata;
- stable session IDs, bounded TTL, expiry and explicit revocation;
- authentication reconstructs exact grants without relationship/provider/device augmentation;
- WSGI routes limited to GET `/v1/health`, POST `/v1/query`, POST `/v1/commands`;
- protected routes require Bearer authentication;
- optional HTTPS scheme gate occurs before authentication/service execution;
- bounded `Content-Length`, object-only UTF-8 JSON parsing and explicit 404/405/411/413 failures;
- transport builds existing 001A envelopes only and delegates canonical policy/state to `ApiService`;
- deterministic API error-to-HTTP status mapping;
- success serialization uses exact service result/readback data and contains no bearer credential.

## Acceptance criteria status before remote CI

1. One-time opaque token + hash-only retained session state. **Implemented/test-covered.**
2. Stable session lifecycle/expiry/revocation. **Implemented/test-covered.**
3. Exact principal/grant reconstruction. **Implemented/test-covered.**
4. Bounded WSGI routes. **Implemented/test-covered.**
5. Bearer 401 before service calls. **Implemented/test-covered.**
6. HTTPS hook before auth/service. **Implemented/test-covered.**
7. Bounded JSON/body/route/method failures. **Implemented/test-covered.**
8. Existing 001A envelopes/policy reused. **Implemented.**
9. Stable HTTP error mapping. **Implemented/test-covered.**
10. Exact success serialization without secrets. **Implemented/test-covered.**
11. Deterministic auth/transport tests. **Content committed; remote CI pending.**
12. No deployment/provider/Google/Android/evidence/legacy state. **Satisfied.**

## Exact next action

1. Compare branch to `main`; expected changed files are `CURRENT_WORK.md`, `mira/__init__.py`, `mira/http_transport.py`, `tests/test_http_transport.py`.
2. Open bounded PR and verify exact file list.
3. Require PR-triggered compile + full unit-suite green; fix packet-scoped failures if any.
4. Merge exact verified head/read back `main`.
5. Mark `API-CORE-001` umbrella complete/test-verified and activate `CORE-SYNTHETIC-ROUNDTRIP`.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture unrelated ideas in BACKLOG unless required for acceptance or explicitly reprioritized.
