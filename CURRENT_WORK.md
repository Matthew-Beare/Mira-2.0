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
- **Status:** activated; code-only deployment readiness implementation in progress.

## Objective

Make the verified runtime deployable to a one-instance Cloud Run service with restart-stable injected same-user bearer authentication and short-lived Google service-identity access tokens, then prove live HTTPS startup and Google-backed canonical entity mutation/readback without committing provider IDs, tokens, credentials, or private data.

## Deployment invariants

1. Cloud Run service-wide manual scaling is fixed at exactly one instance for the M2-M0 Google Sheets writer proof.
2. Request concurrency is fixed at exactly one.
3. No traffic-tag side revision is permitted for live write testing.
4. TLS terminates at Cloud Run; the container receives clear HTTP. The API must trust only the Cloud Run proxy protocol signal for external HTTPS policy rather than pretending the container terminates TLS.
5. Google Sheets access uses short-lived Cloud Run service-identity OAuth tokens from the metadata/runtime identity path. Downloaded service-account JSON keys are prohibited.
6. The bearer client token is injected from Secret Manager/runtime secret configuration and is hashed immediately; raw bearer material is not stored in repository state or logs.
7. The live Google resource is the isolated synthetic MIRA 2.0 namespace only. Legacy production artifacts remain protected.

## Acceptance criteria

1. Add a restart-stable bearer authenticator that accepts its raw high-entropy token only at construction, retains only a cryptographic hash, uses constant-time comparison, and returns one explicitly scoped same-user principal.
2. Add a testable Google runtime access-token provider suitable for Cloud Run service identity; no service-account JSON key, refresh token, or live credential is committed.
3. Add a deployment/application entrypoint that reads all provider identifiers and secrets only from runtime environment/secret injection, builds `GoogleSheetsRestGateway` + `GoogleSheetsStructuredStateAdapter`, and calls the existing `assemble_managed_runtime` path.
4. Preserve the API's external HTTPS-only policy behind Cloud Run TLS termination using a narrowly scoped trusted-proxy adaptation; direct untrusted HTTP semantics remain rejected.
5. Add deterministic packaging/entrypoint files for a managed WSGI server listening on `$PORT`; no development server.
6. Record/enforce Cloud Run deployment invariants: manual service scaling = 1, request concurrency = 1, no traffic-tag write path, synthetic MIRA 2.0 namespace only.
7. Tests prove secret authenticator restart behavior, metadata-token parsing/cache/expiry behavior, environment validation, proxy HTTPS adaptation, and complete application construction with fake Google/runtime dependencies.
8. Update direct ownership and CI; no provider IDs/private data/secrets in Git.
9. Live Cloud Run service must return healthy HTTPS readback before protected API testing.
10. Live service identity must read the isolated synthetic Google state, resolve the persisted `entity` Authority route, create/mutate one canonical synthetic entity through the shared API, and exact-read it back from Google.
11. Repeat/restart proof must show the injected bearer remains valid across a process restart and the persisted Authority/entity route is unchanged/readable.
12. Only after all live evidence passes may `API-DEPLOYMENT-001` be marked complete and `CHATGPT-API-CLIENT-001` become the next packet.

## External account boundary

No Google Cloud deployment connector is available in the current tool set. Complete and merge the code-only deployment-readiness slice first. Then attempt an authenticated Google Cloud control-plane path; if none exists, checkpoint the exact missing provider action and do not claim live deployment.

## Backlog integrity note

Several critical-path status cells in `BACKLOG.md` are stale. Reconcile them without changing dependency order or deleting preserved work before closing this packet.

## Exact next action

1. Implement restart-stable secret bearer authentication and Cloud Run metadata OAuth token provider.
2. Implement environment-driven deployment construction plus trusted proxy HTTPS adaptation.
3. Add `main.py`, pinned Python/buildpack dependency metadata, one-worker/one-thread Gunicorn entrypoint, and synthetic tests.
4. Update code ownership, PR/CI/merge the code-only readiness slice.
5. Attempt live Google Cloud provider setup/deployment; stop only at a real authorization/control-plane boundary.

## Recovery protocol

Read this file first, verify branch/head, enforce the deployment invariants above, keep all provider identifiers/private data/secrets out of Git, and continue only `M2-M0-005` unless a blocker forces scope change.
