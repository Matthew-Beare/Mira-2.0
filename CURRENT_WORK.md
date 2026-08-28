# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active live-deployment proof packet and its recovery point.

## Completed prerequisite packet

### `M2-M0-004` — Managed API runtime assembly

- **Merged PR:** #47
- **Merge SHA / main readback:** `51f4bd3c6281558ff7312def4491b8d99d35b6ff`
- **Final GitHub Actions run:** `33216893134`; compile + feature registry + code ownership + full suite succeeded.
- **Result:** provider-neutral fail-closed managed runtime composition and pluggable bearer authentication are implemented/test-verified.

## Active packet

### `M2-M0-005` — Cloud Run credential + live Google deployment proof

- **Related work ID:** `API-DEPLOYMENT-001`
- **Class:** hard deployment prerequisite / live integration proof
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Code branch:** `integration/m0-005-cloud-run-live-proof`
- **Branch start SHA:** `7fc04ce4a9aa3f3487b8dbdcd7eee448aa9217de`
- **Merged PR:** #48
- **Final PR head:** `f0b584a7e66b7349d349297150cebdde6915a206`
- **Final GitHub Actions run:** `33217543700`
- **Merge SHA / main readback:** `acb37af4aa378e8128d8591406859fe954af3474`
- **Status:** code-only deployment readiness merged and remotely verified; packet remains active and blocked only on authenticated Google Cloud control-plane access for live deployment/provider/restart evidence.

## Objective

Make the verified runtime deployable to a one-instance Cloud Run service with restart-stable injected same-user bearer authentication and short-lived Google service-identity access tokens, then prove live HTTPS startup and Google-backed canonical entity mutation/readback without committing provider IDs, tokens, credentials, or private data.

## Deployment invariants

1. Cloud Run service-wide manual scaling is fixed at exactly one instance for the M2-M0 Google Sheets writer proof.
2. Request concurrency is fixed at exactly one.
3. No traffic-tag side revision is permitted for live write testing.
4. TLS terminates at Cloud Run; the container receives clear HTTP. The Cloud Run-only adapter may promote `X-Forwarded-Proto: https` to the WSGI scheme; without that explicit proxy signal protected routes retain the API core's HTTPS rejection.
5. Google Sheets access uses short-lived Cloud Run service-identity OAuth tokens from the metadata/runtime identity path. Downloaded service-account JSON keys are prohibited.
6. The bearer client token is injected from Secret Manager/runtime secret configuration and is hashed immediately; raw bearer material is not retained by the authenticator or emitted to logs/repository state.
7. The live Google resource is the isolated synthetic MIRA 2.0 namespace only. Legacy production artifacts remain protected.
8. Gunicorn is one worker / one thread; this complements rather than replaces Cloud Run manual instance count = 1 and request concurrency = 1.

## Acceptance criteria

1. Restart-stable injected bearer authenticator with digest-only retention and constant-time comparison. **Implemented/test-verified/merged.**
2. Testable Cloud Run Google service-identity access-token provider with short-lived token cache and no long-lived Google credential material. **Implemented/test-verified/merged.**
3. Environment/secret-driven deployment composition through the existing Google adapter and `assemble_managed_runtime`. **Implemented/test-verified/merged.**
4. Cloud Run HTTPS proxy adaptation preserving protected-route HTTPS rejection without proxy HTTPS assertion. **Implemented/test-verified/merged.**
5. Managed WSGI packaging/entrypoint listening on `$PORT`; no development server. **Implemented/merged.**
6. Manual service scaling = 1, request concurrency = 1, no traffic-tag write path, isolated synthetic namespace. **Recorded; live control-plane readback pending.**
7. Direct tests for restart authentication, metadata token cache/refresh, config rejection, proxy handling, rate limit, audit output and authenticated canonical roundtrip with fake provider state. **Implemented; final CI green.**
8. Direct code ownership and no committed provider IDs/private data/secrets. **Implemented; final CI green.**
9. Live Cloud Run service returns healthy HTTPS readback before protected API testing. **Pending provider control plane.**
10. Live service identity reads persisted Google Authority state and completes one canonical synthetic entity mutation/exact provider readback through the shared API. **Pending provider control plane.**
11. Live restart proves the same injected bearer remains valid and persisted Authority/entity state remains unchanged/readable. **Synthetic reconstruction verified; live restart pending.**
12. `API-DEPLOYMENT-001` may be marked complete only after 9-11 pass; only then may `CHATGPT-API-CLIENT-001` activate. **Not yet satisfied.**

## Completed code evidence

- `mira/managed_auth.py`: restart-stable `StaticSecretAuthenticator`; SHA-256 digest only; constant-time comparison; validated copied principal/grants.
- `mira/google_runtime_auth.py`: Cloud Run metadata service-identity access-token provider with bounded refresh skew/cache/expiry validation and sanitized transport failures.
- `mira/cloud_run.py`: runtime-only provider configuration, existing Google adapter/runtime assembly reuse, structured JSON audit sink, fixed-window protected-route rate limit and Cloud Run HTTPS proxy adaptation.
- `mira/cloud_run_entrypoint.py`: Gunicorn import target.
- `.python-version`: Python 3.12 major/minor buildpack target.
- `requirements.txt`: pinned `gunicorn==26.2.0`.
- `Procfile`: `$PORT`, one worker, one thread, 90-second worker timeout and stdout/stderr logs.
- `tests/test_managed_auth.py`, `tests/test_google_runtime_auth.py`, `tests/test_cloud_run.py`: direct deployment-boundary evidence including authenticated canonical command/query roundtrip over injected synthetic state.
- `project/code_ownership.json`: direct ownership/evidence coverage for every new production module.
- PR #48 final CI run `33217543700`: compile, feature registry, code ownership and full unit/integration suite succeeded.
- PR #48 merge/main readback: `acb37af4aa378e8128d8591406859fe954af3474`.

## External account boundary

Google Cloud / Cloud Run control-plane capability is not connected in the current tool set, and plugin discovery returned no installable Google Cloud or Cloud Run connector. Therefore these writes/readbacks have **not** occurred and must not be claimed:
- Google Cloud project/API setup or selection;
- Cloud Run service creation/deployment;
- dedicated Cloud Run service account creation/assignment;
- Secret Manager bearer secret creation/injection;
- sharing the isolated synthetic Google Sheet with the deployed service identity;
- service-wide manual scaling = 1 readback;
- request concurrency = 1 readback;
- live Cloud Run HTTPS health/API/provider/restart proof.

This is now the only blocking boundary for this packet. Do not switch to `CHATGPT-API-CLIENT-001` merely because the deployment code exists.

## Backlog integrity note

Several M2-M0 critical-path statuses in `BACKLOG.md` still reflect pre-implementation state. Reconcile completed rows and set `API-DEPLOYMENT-001` to active/partial before closing this packet. Do not mark it complete until live criteria 9-11 pass.

## Exact next action

1. Reconcile stale critical-path statuses in `BACKLOG.md` while preserving dependency order and all later work.
2. Re-attempt Google Cloud control-plane discovery only through authenticated supported tooling; do not substitute a different host that violates the single-writer deployment invariants.
3. When Google Cloud control-plane access exists, configure one Cloud Run service with service-wide manual scaling = 1 and request concurrency = 1, dedicated service identity, Secret Manager bearer injection and no traffic-tag side write revision.
4. Share only the isolated synthetic Google Sheet with that service identity.
5. Deploy and execute live acceptance criteria 9-11 with exact Cloud Run and Google provider readback.

## Recovery protocol

Read this file first, verify `main` contains merge SHA `acb37af4aa378e8128d8591406859fe954af3474` or a descendant carrying this checkpoint, enforce the deployment invariants above, keep provider identifiers/private data/secrets out of Git, and continue only `M2-M0-005` unless a blocker forces scope change.
