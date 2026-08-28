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
- **Deployment-readiness merged PR:** #48
- **Deployment-readiness merge SHA:** `acb37af4aa378e8128d8591406859fe954af3474`
- **Final deployment-readiness GitHub Actions run:** `33217543700`
- **Post-merge provider-boundary checkpoint:** `829bdbad75e18536fe96d3b262ec3ac11034528c`
- **Backlog reconciliation commit:** `c683aceaf519636983e1304bc02c07594dc2191f`
- **Latest main checkpoint before operator branch:** `8cfcb2101a07d1058a6248e0bd5b00f6d3c4908b`
- **Active operator branch:** `integration/m0-005-cloud-shell-operator`
- **Operator branch start SHA:** `8cfcb2101a07d1058a6248e0bd5b00f6d3c4908b`
- **Status:** runtime/deployment code is merged; authenticated Google Cloud control-plane tooling is still unavailable to ChatGPT; a deterministic two-phase Cloud Shell operator is now implemented on the active branch and awaiting CI/merge before human execution.

## Objective

Deploy the verified runtime to a one-instance Cloud Run service with restart-stable injected same-user bearer authentication and short-lived Google service-identity access tokens, then prove live HTTPS startup and Google-backed canonical entity mutation/readback without committing provider IDs, tokens, credentials, or private data.

## Deployment invariants

1. Cloud Run service-wide manual scaling is fixed at exactly one instance for the M2-M0 Google Sheets writer proof.
2. Request concurrency is fixed at exactly one.
3. No traffic-tag side revision is permitted for live write testing.
4. TLS terminates at Cloud Run; the container receives clear HTTP. The Cloud Run-only adapter may promote `X-Forwarded-Proto: https` to the WSGI scheme; without that explicit proxy signal protected routes retain the API core's HTTPS rejection.
5. Google Sheets access uses short-lived Cloud Run service-identity OAuth tokens from the metadata/runtime identity path. Downloaded service-account JSON keys are prohibited.
6. The bearer client token is injected from Secret Manager/runtime secret configuration and is hashed immediately; raw bearer material is not retained by the authenticator or emitted to logs/repository state.
7. The live Google resource is the isolated synthetic MIRA 2.0 namespace only. Legacy production artifacts remain protected.
8. Gunicorn is one worker / one thread; this complements rather than replaces Cloud Run manual instance count = 1 and request concurrency = 1.
9. Source deployment uses a separate dedicated build service account with the documented Cloud Run Builder role rather than relying on an ambient/default build identity.

## Acceptance criteria

1. Restart-stable injected bearer authenticator with digest-only retention and constant-time comparison. **Implemented/test-verified/merged.**
2. Testable Cloud Run Google service-identity access-token provider with short-lived token cache and no long-lived Google credential material. **Implemented/test-verified/merged.**
3. Environment/secret-driven deployment composition through the existing Google adapter and `assemble_managed_runtime`. **Implemented/test-verified/merged.**
4. Cloud Run HTTPS proxy adaptation preserving protected-route HTTPS rejection without proxy HTTPS assertion. **Implemented/test-verified/merged.**
5. Managed WSGI packaging/entrypoint listening on `$PORT`; no development server. **Implemented/merged.**
6. Manual service scaling = 1, request concurrency = 1, no traffic-tag write path, isolated synthetic namespace. **Recorded in code/operator; live control-plane readback pending.**
7. Direct tests for restart authentication, metadata token cache/refresh, config rejection, proxy handling, rate limit, audit output and authenticated canonical roundtrip with fake provider state. **Implemented; final deployment-readiness CI green.**
8. Direct code ownership and no committed provider IDs/private data/secrets. **Implemented; final deployment-readiness CI green.**
9. Live Cloud Run service returns healthy HTTPS readback before protected API testing. **Pending provider control plane.**
10. Live service identity reads persisted Google Authority state and completes one canonical synthetic entity mutation/exact provider readback through the shared API. **Pending provider control plane.**
11. Live restart proves the same injected bearer remains valid and persisted Authority/entity state remains unchanged/readable. **Synthetic reconstruction verified; live restart pending.**
12. `API-DEPLOYMENT-001` may be marked complete only after 9-11 pass; only then may `CHATGPT-API-CLIENT-001` activate. **Not yet satisfied.**

## Completed deployment-readiness evidence

- `mira/managed_auth.py`: restart-stable `StaticSecretAuthenticator`; SHA-256 digest only; constant-time comparison; validated copied principal/grants.
- `mira/google_runtime_auth.py`: Cloud Run metadata service-identity access-token provider with bounded refresh skew/cache/expiry validation and sanitized transport failures.
- `mira/cloud_run.py`: runtime-only provider configuration, existing Google adapter/runtime assembly reuse, structured JSON audit sink, fixed-window protected-route rate limit and Cloud Run HTTPS proxy adaptation.
- `mira/cloud_run_entrypoint.py`: Gunicorn import target.
- `.python-version`: Python 3.12 major/minor buildpack target.
- `requirements.txt`: pinned `gunicorn==26.2.0`.
- `Procfile`: `$PORT`, one worker, one thread, 90-second worker timeout and stdout/stderr logs.
- `tests/test_managed_auth.py`, `tests/test_google_runtime_auth.py`, `tests/test_cloud_run.py`: direct deployment-boundary evidence including authenticated canonical command/query roundtrip over injected synthetic state.
- `project/code_ownership.json`: direct ownership/evidence coverage for every deployment production module.
- PR #48 final CI run `33217543700`: compile, feature registry, code ownership and full unit/integration suite succeeded.
- PR #48 merge/main readback: `acb37af4aa378e8128d8591406859fe954af3474`.
- `BACKLOG.md` critical-path status reconciliation: `c683aceaf519636983e1304bc02c07594dc2191f`; completed prerequisites are no longer shown as queued and `API-DEPLOYMENT-001` is explicitly active/partial.

## Active control-plane operator sub-slice

Because no supported Google Cloud / Cloud Run connector is available, the live provider boundary is being reduced to the smallest deterministic human action instead of switching hosts or weakening the single-writer invariants.

Implemented on `integration/m0-005-cloud-shell-operator`:

- `ops/cloud_run_live_proof.sh` with two explicit phases:
  - `prepare`: verifies project/authentication, enables only required APIs, creates dedicated runtime and build identities, assigns documented source-deploy roles, creates/reuses the Secret Manager bearer without printing it, grants runtime secret access, and prints the runtime service-account email;
  - `deploy`: after the Sheet is shared, deploys from source using the dedicated build/runtime identities, sets `--scaling=1` and `--concurrency=1`, independently reads the Cloud Run v2 service resource, verifies no traffic tag, checks HTTPS health, executes a canonical entity write/read, redeploys with the same secret, proves bearer/state continuity, performs a post-restart mutation, and emits non-secret evidence for independent Google provider readback.
- `docs/CLOUD_RUN_LIVE_PROOF.md` records the exact operator boundary and failure rules.
- `tests/test_cloud_run_operator.py` checks Bash syntax, required single-writer flags/readback assertions, bounded IAM roles, secret handling, absence of the live spreadsheet ID, restart proof, and independent provider-readback requirement.
- Current Google documentation was rechecked on 2026-08-28 before authoring the operator: manual scaling uses `--scaling=INSTANCE_COUNT`, concurrency uses `--concurrency`, source deployment supports a dedicated `--build-service-account`, and Google documents `roles/run.sourceDeveloper`, `roles/serviceusage.serviceUsageConsumer`, `roles/iam.serviceAccountUser`, and `roles/run.builder` for the bounded source-deploy path.

The operator script itself is **not** live provider evidence. Acceptance criteria 9-11 remain pending until its phases actually execute against Google Cloud and the final Google row is independently read back.

## External account boundary

Google Cloud / Cloud Run control-plane capability is not connected in the current ChatGPT tool set. Plugin discovery was repeated after the readiness merge and again before the operator sub-slice; no installable Google Cloud or Cloud Run connector exists.

The connected Google Drive tool *can* grant writer access to the isolated synthetic Sheet after phase `prepare` returns the exact runtime service-account email. That single-file share should be performed by MIRA rather than broad folder sharing.

The following live writes/readbacks still have **not** occurred and must not be claimed:

- Google Cloud project/API setup or selection;
- Cloud Run service creation/deployment;
- dedicated runtime/build service account creation/assignment;
- Secret Manager bearer secret creation/injection;
- sharing the isolated synthetic Google Sheet with the deployed service identity;
- service-wide manual scaling = 1 readback;
- request concurrency = 1 readback;
- live Cloud Run HTTPS/provider/restart proof;
- independent post-restart Google row readback.

## Exact next action

1. Open a bounded PR for the Cloud Shell operator sub-slice and run the full repository CI.
2. Fix any CI/operator defect without changing the live deployment invariants.
3. Merge/read back the operator only after CI is green.
4. In an authenticated Google Cloud Shell, run `PROJECT_ID=<project> bash ops/cloud_run_live_proof.sh prepare` from the merged repository checkout.
5. Capture only the printed `MIRA_SERVICE_ACCOUNT_EMAIL` and return it to MIRA; do not return the bearer secret.
6. MIRA shares writer access on only `MIRROR Structured State - Synthetic` to that exact service-account email and verifies the Drive permission change.
7. Run `PROJECT_ID=<project> bash ops/cloud_run_live_proof.sh deploy`; the operator prompts for the synthetic Sheet ID locally and performs the live Cloud Run/API/restart proof.
8. Return the non-secret final evidence values (`MIRA_SERVICE_URL`, proof resource ID/revision/phase) to MIRA.
9. MIRA independently reads the Google Sheet row and reconciles the live proof.
10. Only then mark `API-DEPLOYMENT-001` complete and activate `CHATGPT-API-CLIENT-001`.

## Recovery protocol

Read this file first. Verify `main` contains deployment-readiness merge SHA `acb37af4aa378e8128d8591406859fe954af3474`, backlog reconciliation `c683aceaf519636983e1304bc02c07594dc2191f`, and provider-boundary checkpoint `8cfcb2101a07d1058a6248e0bd5b00f6d3c4908b` or descendants. If the operator PR is still open, continue `integration/m0-005-cloud-shell-operator`; if merged, execute the exact provider handoff above. Keep all provider identifiers/private data/secrets out of Git and continue only `M2-M0-005` unless a hard blocker forces scope change.
