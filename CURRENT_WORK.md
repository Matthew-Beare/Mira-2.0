# MIRA 2.0 CURRENT WORK

Git is authoritative. This file records the completed managed-runtime assembly packet and selects the bounded live deployment successor.

## Completed packet

### `M2-M0-004` — Managed API runtime assembly

- **Related work ID:** `API-DEPLOYMENT-001`
- **Merged PR:** #47
- **Merge SHA / main readback:** `51f4bd3c6281558ff7312def4491b8d99d35b6ff`
- **Branch:** `integration/m0-004-managed-api-runtime`
- **Branch start SHA:** `7f0b3fa304825c01b3ea9cf390231140b73200fb`
- **CI-verified final PR head:** `559be964d769cab96647055c99eb1246ebfc8dc0`
- **Final GitHub Actions run:** `33216893134`
- **Remote verification:** compile + feature registry + code ownership + full suite succeeded.
- **Result:** `WsgiApiApp` now consumes an explicit bearer-authenticator boundary; `mira/runtime.py` assembles state -> persistent Authority bootstrap -> API service -> authenticated WSGI app with startup health/schema/route verification and synthetic direct tests.
- **Boundary:** live managed hosting, restart-stable scoped credentials, live Google service identity/provider execution, and stock ChatGPT connection are not yet claimed.

## Deployment architecture decision

For the M2-M0 Google Sheets authority proof, the selected managed host is Google Cloud Run with **service-wide manual scaling fixed at one instance** and **request concurrency fixed at one**. The current Google Sheets adapter intentionally guarantees optimistic revisions only within one writer process, so default Cloud Run autoscaling is prohibited for this proof. No traffic-tag side revision may be used for live write testing.

Cloud Run terminates public TLS before forwarding clear HTTP to the container. The deployment entrypoint must therefore preserve the API's HTTPS-only client policy using trusted proxy scheme information rather than requiring TLS inside the container.

The preferred Google provider identity is the Cloud Run service account obtaining short-lived OAuth access tokens from Google metadata/runtime identity. No downloaded service-account JSON key is required or permitted for this proof. The isolated synthetic Sheet must be explicitly shared only with the deployed service identity before live write/readback testing.

## Selected successor

### `M2-M0-005` — Cloud Run credential + live Google deployment proof

- **Related work ID:** `API-DEPLOYMENT-001`
- **Class:** hard deployment prerequisite / live integration proof
- **Planned branch:** `integration/m0-005-cloud-run-live-proof`

### Objective

Make the verified runtime deployable to a one-instance Cloud Run service with restart-stable injected same-user bearer authentication and short-lived Google service-identity access tokens, then prove live HTTPS startup and Google-backed canonical entity mutation/readback without committing provider IDs, tokens, credentials, or private data.

### Acceptance criteria

1. Add a restart-stable bearer authenticator that accepts its raw high-entropy token only at construction, retains only a cryptographic hash, uses constant-time comparison, and returns one explicitly scoped same-user principal.
2. Add a testable Google runtime access-token provider suitable for Cloud Run service identity; no service-account JSON key, refresh token, or live credential is committed.
3. Add a deployment/application entrypoint that reads all provider identifiers and secrets only from runtime environment/secret injection, builds `GoogleSheetsRestGateway` + `GoogleSheetsStructuredStateAdapter`, and calls the existing `assemble_managed_runtime` path.
4. Preserve the API's external HTTPS-only policy behind Cloud Run TLS termination using a narrowly scoped trusted-proxy adaptation; direct untrusted HTTP semantics remain rejected.
5. Add deterministic packaging/entrypoint files for a managed WSGI server listening on `$PORT`; no development server.
6. Record/enforce Cloud Run deployment invariants: manual service scaling = 1, request concurrency = 1, no traffic-tag write path, synthetic MIRA 2.0 namespace only.
7. Tests prove secret authenticator restart behavior, metadata-token parsing/cache/expiry behavior, environment validation, proxy HTTPS adaptation, and complete application construction with fake Google gateway/runtime dependencies.
8. Update direct ownership and CI; no provider IDs/private data/secrets in Git.
9. Live Cloud Run service must return healthy HTTPS readback before protected API testing.
10. Live service identity must read the isolated synthetic Google state, resolve the persisted `entity` Authority route, create/mutate one canonical synthetic entity through the shared API, and exact-read it back from Google.
11. Repeat/restart proof must show the injected bearer remains valid across a process restart and the persisted Authority/entity route is unchanged/readable.
12. Only after all live evidence passes may `API-DEPLOYMENT-001` be marked complete and `CHATGPT-API-CLIENT-001` become the next packet.

## External account boundary

No Google Cloud deployment connector is currently available in the connected tool set. Code, tests, deployment configuration, and provider-neutral preflight can be completed in Git now. Creating the actual Cloud Run project/service, service identity, Secret Manager secret, and deployed revision requires an authenticated Google Cloud control-plane connection or equivalent user-authorized provider action. Do not claim those external writes until provider readback exists.

## Backlog integrity note

Several M2-M0 critical-path status cells in `BACKLOG.md` still say `queued` even though their implementation/evidence has merged. Reconcile those stale status cells in this packet's first governance commit without changing dependency ordering or deleting preserved later work.

## Exact next action

1. Create `integration/m0-005-cloud-run-live-proof` from this checkpoint.
2. Reconcile stale critical-path `BACKLOG.md` statuses.
3. Implement restart-stable injected bearer authentication, Cloud Run metadata access-token provider, trusted proxy HTTPS adaptation, and deploy entrypoint/package with synthetic tests.
4. PR/CI/merge the code-only deployment readiness slice if green.
5. Attempt/provider-connect the actual Google Cloud control plane; if unavailable, stop with an exact external-action checkpoint rather than inventing live deployment evidence.

## Recovery protocol

Read this file first, verify repository/branch/head, keep all provider identifiers/private data/secrets out of Git, and do not claim live Cloud Run or Google OAuth/provider execution until provider readback proves it.
