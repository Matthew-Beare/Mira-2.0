# M2-M0-005 Cloud Run live proof

This runbook exists only to cross the external Google Cloud control-plane boundary for the active `M2-M0-005` packet. Git remains authoritative for packet state in `CURRENT_WORK.md`.

## Safety boundary

The public repository must never contain the Google Cloud project ID, spreadsheet ID, service-account email, bearer token, access token, private Google data, or other account-specific identifiers.

The live proof is constrained to:

- the isolated synthetic MIRA 2.0 Google Sheet;
- one dedicated Cloud Run runtime service account;
- one separate dedicated Cloud Build service account;
- one Secret Manager bearer secret;
- Cloud Run service-wide **manual scaling = 1**;
- Cloud Run request **concurrency = 1**;
- one Gunicorn worker and one thread;
- no traffic-tag side revision for writes;
- public Cloud Run ingress with MIRA bearer authentication protecting `/v1/query` and `/v1/commands`;
- short-lived Google service-identity OAuth tokens from the Cloud Run metadata path;
- no downloaded service-account JSON key.

Google documents `gcloud run deploy SERVICE --scaling=1` as service-wide manual scaling and concurrency `1` as the maximum simultaneous requests per instance. Google also documents a dedicated build service account as the preferred source-deploy path. The operator script sets these explicitly and independently reads the Cloud Run v2 service resource back before any canonical write.

## Phase 1: prepare Cloud resources

Use Google Cloud Shell or another shell with an authenticated `gcloud` CLI. Clone the public repository and run the checked-in operator from the repository root:

```bash
git clone https://github.com/Matthew-Beare/Mira-2.0.git
cd Mira-2.0
PROJECT_ID='<your Google Cloud project ID>' bash ops/cloud_run_live_proof.sh prepare
```

The prepare phase:

1. verifies the active Google Cloud project and authenticated deployer;
2. enables Cloud Run, Cloud Build, Artifact Registry, Secret Manager, and IAM APIs;
3. creates or reuses the dedicated `mira-m0-runtime` Cloud Run service identity;
4. creates or reuses the separate `mira-m0-builder` source-build identity;
5. grants the active deployer only the documented source-deploy roles `roles/run.sourceDeveloper` and `roles/serviceusage.serviceUsageConsumer` on the project;
6. grants the deployer `roles/iam.serviceAccountUser` on only the two bounded service accounts;
7. grants the build identity only `roles/run.builder` on the project;
8. creates the `mira-m0-bearer` secret if missing and generates the bearer without printing it;
9. grants only the runtime service account Secret Manager accessor permission;
10. prints `MIRA_SERVICE_ACCOUNT_EMAIL=...` and stops.

Do not paste the bearer secret into chat or Git. The raw bearer stays in Secret Manager.

## Drive handoff

After phase 1, grant **writer** access on only the isolated synthetic MIRA Sheet to the exact runtime service-account email printed by the script. Do not share legacy production artifacts or the entire Drive folder.

When this workflow is being driven through ChatGPT with connected Google Drive access, MIRA can perform this single-file share after the runtime service-account email is supplied.

## Phase 2: deploy and prove live behavior

After the Sheet share is confirmed, run:

```bash
PROJECT_ID='<your Google Cloud project ID>' bash ops/cloud_run_live_proof.sh deploy
```

The script prompts for the isolated synthetic spreadsheet ID unless `MIRA_GOOGLE_SPREADSHEET_ID` is already set in the shell. The spreadsheet ID is passed only as a runtime environment value and is never written to Git.

The deploy phase:

1. deploys the repository source to Cloud Run using the dedicated build identity and dedicated runtime identity;
2. injects the bearer from Secret Manager;
3. sets `MIRA_GOOGLE_SPREADSHEET_ID` and the bounded rate limit as runtime environment values;
4. sets manual service scaling to exactly one instance and request concurrency to exactly one;
5. reads the Cloud Run v2 service resource and fails if scaling mode, instance count, concurrency, runtime identity, traffic distribution, or traffic tags violate the packet invariants;
6. verifies `/v1/health` over the returned HTTPS service URL;
7. retrieves the bearer from Secret Manager only into the local shell process and uses it for protected API requests;
8. creates or updates the fixed synthetic `cloudrun-live-proof` entity through the deployed shared API and verifies exact API readback;
9. redeploys the same source with the same Secret Manager secret to force a new live revision without a traffic tag;
10. proves the same bearer still authenticates and the same persisted entity remains readable after redeployment;
11. performs a post-restart mutation and exact API readback;
12. prints only non-secret evidence values needed for independent provider readback.

The final successful output includes:

- `MIRA_DEPLOY_STATUS=LIVE_API_AND_RESTART_VERIFIED`
- the HTTPS service URL;
- the runtime service-account email;
- `MIRA_PROOF_RESOURCE_ID=cloudrun-live-proof`;
- the final canonical revision;
- `MIRA_PROOF_PHASE=post-restart`.

## Independent provider readback

API success is not the final evidence. After the deploy phase succeeds, independently read the isolated Google Sheet and verify the `entity/cloudrun-live-proof` row has:

- the final revision printed by the operator;
- payload `{"proof":"cloud-run-live","phase":"post-restart"}`;
- no duplicate canonical identity.

Only after that independent Google readback may acceptance criteria 9-11 be marked live-verified and `API-DEPLOYMENT-001` be completed.

## Failure behavior

The operator intentionally stops on the first failed command or invariant. Do not work around a failure by enabling autoscaling, adding traffic tags, using a second writable service, downloading a service-account key, changing the canonical Sheet, or switching to legacy production data. Record the exact failure in `CURRENT_WORK.md` and repair the bounded cause.
