# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active live-deployment proof packet and its recovery point.

## Completed packet before this branch

### `M2-M0-004` — Managed API runtime assembly

- **Merged PR:** #47
- **Merge SHA / main readback:** `51f4bd3c6281558ff7312def4491b8d99d35b6ff`
- **Final GitHub Actions run:** `33216893134`; compile + feature registry + code ownership + full suite succeeded.
- **Post-merge close/select checkpoint / this branch start SHA:** `7fc04ce4a9aa3f3487b8dbdcd7eee448aa9217de`
- **Result:** provider-neutral fail-closed managed runtime composition and pluggable bearer authentication are implemented/test-verified.

## Active packet

### `M2-M0-005` — Cloud Run credential + live Google deployment proof

- **Related work ID:** `API-DEPLOYMENT-001`
- **Class:** hard deployment prerequisite / live integration proof
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `integration/m0-005-cloud-run-live-proof`
- **Branch start SHA:** `7fc04ce4a9aa3f3487b8dbdcd7eee448aa9217de`
- **PR:** #48
- **CI-verified code head:** `7f23cd8d375e2cbff4b18fe8fff9849d0e6427cb`
- **GitHub Actions run:** `33217499694`
- **Status:** code-only deployment readiness implemented and CI green; final documentation checkpoint/CI/merge pending; live provider execution still blocked on Google Cloud control-plane access.

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

1. Add a restart-stable bearer authenticator that accepts its raw high-entropy token only at construction, retains only a cryptographic hash, uses constant-time comparison, and returns one explicitly scoped same-user principal. **Implemented/test-verified.**
2. Add a testable Google runtime access-token provider suitable for Cloud Run service identity; no service-account JSON key, refresh token, or live credential is committed. **Implemented/test-verified.**
3. Add a deployment/application entrypoint that reads all provider identifiers and secrets only from runtime environment/secret injection, builds `GoogleSheetsRestGateway` + `GoogleSheetsStructuredStateAdapter`, and calls the existing `assemble_managed_runtime` path. **Implemented/test-verified with injected fake provider state.**
4. Preserve the API's external HTTPS-only policy behind Cloud Run TLS termination using a narrowly scoped trusted-proxy adaptation; direct untrusted HTTP semantics remain rejected. **Implemented/test-verified.**
5. Add deterministic packaging/entrypoint files for a managed WSGI server listening on `$PORT`; no development server. **Implemented: `.python-version`, pinned `requirements.txt`, root `Procfile`, `mira.cloud_run_entrypoint`.**
6. Record/enforce Cloud Run deployment invariants: manual service scaling = 1, request concurrency = 1, no traffic-tag write path, synthetic MIRA 2.0 namespace only. **Recorded; live provider readback pending.**
7. Tests prove secret authenticator restart behavior, metadata-token parsing/cache/expiry behavior, environment validation, proxy HTTPS adaptation, and complete application construction with fake Google/runtime dependencies. **Implemented/test-verified.**
8. Update direct ownership and CI; no provider IDs/private data/secrets in Git. **Implemented; CI run `33217499694` green.**
9. Live Cloud Run service must return healthy HTTPS readback before protected API testing. **Pending live provider control plane.**
10. Live service identity must read the isolated synthetic Google state, resolve the persisted `entity` Authority route, create/mutate one canonical synthetic entity through the shared API, and exact-read it back from Google. **Pending live provider control plane.**
11. Repeat/restart proof must show the injected bearer remains valid across a process restart and the persisted Authority/entity route is unchanged/readable. **Synthetic authenticator reconstruction verified; live restart/readback pending.**
12. Only after all live evidence passes may `API-DEPLOYMENT-001` be marked complete and `CHATGPT-API-CLIENT-001` become the next packet. **Not yet satisfied.**

## Completed code evidence

- `mira/managed_auth.py`: restart-stable `StaticSecretAuthenticator`; SHA-256 digest only; constant-time comparison; validated copied principal/grants.
- `mira/google_runtime_auth.py`: Cloud Run metadata service-identity access-token provider with bounded refresh skew, cache/expiry validation, sanitized transport errors, and no long-lived Google credential material.
- `mira/cloud_run.py`: runtime-only provider configuration, existing Google adapter/runtime assembly reuse, structured JSON audit sink, one-instance fixed-window API rate limit, and Cloud Run HTTPS proxy adaptation.
- `mira/cloud_run_entrypoint.py`: Gunicorn import target.
- `.python-version`: Python 3.12 major/minor buildpack target.
- `requirements.txt`: pinned `gunicorn==26.2.0`.
- `Procfile`: `$PORT`, one worker, one thread, 90-second worker timeout, stdout/stderr logs.
- `tests/test_managed_auth.py`, `tests/test_google_runtime_auth.py`, `tests/test_cloud_run.py`: direct deployment-boundary evidence, including authenticated canonical command/query roundtrip over injected synthetic state.
- `project/code_ownership.json`: direct ownership/evidence coverage for every new production module.
- PR #48 CI run `33217499694`: compile, feature registry, code ownership, and full unit/integration suite succeeded.

## External account boundary

No Google Cloud deployment/control-plane connector is available in the current tool set, and plugin discovery found no installable Google Cloud / Cloud Run connector. Therefore the following writes have **not** occurred and must not be claimed:
- Google Cloud project/API setup or selection;
- Cloud Run service creation/deployment;
- Cloud Run service account creation/assignment;
- Secret Manager secret creation/injection;
- sharing the isolated synthetic Google Sheet with the deployed service identity;
- live Cloud Run HTTPS/provider/restart readback.

The code-only readiness slice can merge independently because it introduces no live provider identifiers or secrets and its behavior is fully synthetic-test verified. The packet remains active after merge until the external live evidence is obtained.

## Backlog integrity note

Several critical-path status cells in `BACKLOG.md` are stale. Reconcile them without changing dependency order or deleting preserved work before closing this packet. `API-DEPLOYMENT-001` must remain active/partial, not complete, until criteria 9-11 pass live.

## Exact next action

1. Let the CURRENT_WORK documentation checkpoint trigger final PR #48 CI; inspect any failure.
2. If green, merge PR #48 with expected head SHA and read back `main`.
3. Reconcile stale completed M2-M0 critical-path statuses in `BACKLOG.md` while leaving `API-DEPLOYMENT-001` active/partial.
4. Re-attempt Google Cloud control-plane discovery. If still unavailable, stop at this exact provider authorization boundary rather than fabricating deployment evidence.
5. When Google Cloud control-plane access exists, create/configure the one-instance/one-concurrency service, dedicated service identity and Secret Manager injection, share only the isolated synthetic Sheet, deploy, then execute criteria 9-11 with provider readback.

## Recovery protocol

Read this file first, verify branch/head, enforce the deployment invariants above, keep all provider identifiers/private data/secrets out of Git, and continue only `M2-M0-005` unless a blocker forces scope change.
