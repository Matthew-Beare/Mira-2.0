#!/usr/bin/env bash
set -Eeuo pipefail

# MIRA M2-M0-005 Cloud Run live-proof operator.
#
# This script deliberately contains no provider IDs, account IDs, spreadsheet IDs,
# bearer secrets, or private data. It is split into two phases:
#   prepare - create/verify Cloud prerequisites and print the runtime service account.
#   deploy  - after the synthetic Sheet is shared to that account, deploy and prove
#             the one-writer Cloud Run invariants plus API/restart behavior.

readonly DEFAULT_REGION="us-east1"
readonly DEFAULT_SERVICE="mira-m0-proof"
readonly DEFAULT_RUNTIME_SERVICE_ACCOUNT="mira-m0-runtime"
readonly DEFAULT_BUILD_SERVICE_ACCOUNT="mira-m0-builder"
readonly DEFAULT_SECRET="mira-m0-bearer"
readonly DEFAULT_RATE_LIMIT="120"
readonly REQUIRED_REPOSITORY="Matthew-Beare/Mira-2.0"

fail() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 1
}

note() {
  printf '%s\n' "$*" >&2
}

require_command() {
  command -v "$1" >/dev/null 2>&1 || fail "required command is unavailable: $1"
}

active_account() {
  gcloud auth list --filter='status:ACTIVE' --format='value(account)' 2>/dev/null | head -n 1
}

project_id() {
  if [[ -n "${PROJECT_ID:-}" ]]; then
    printf '%s' "$PROJECT_ID"
    return
  fi
  gcloud config get-value project 2>/dev/null || true
}

principal_member() {
  local account="$1"
  if [[ "$account" == *"gserviceaccount.com" ]]; then
    printf 'serviceAccount:%s' "$account"
  else
    printf 'user:%s' "$account"
  fi
}

service_account_email() {
  local name="$1"
  local project="$2"
  printf '%s@%s.iam.gserviceaccount.com' "$name" "$project"
}

secret_exists() {
  local project="$1"
  local secret="$2"
  gcloud secrets describe "$secret" --project "$project" >/dev/null 2>&1
}

service_account_exists() {
  local project="$1"
  local email="$2"
  gcloud iam service-accounts describe "$email" --project "$project" >/dev/null 2>&1
}

ensure_service_account() {
  local project="$1"
  local name="$2"
  local display_name="$3"
  local email
  email="$(service_account_email "$name" "$project")"
  if ! service_account_exists "$project" "$email"; then
    gcloud iam service-accounts create "$name" \
      --project "$project" \
      --display-name="$display_name"
  fi
  printf '%s' "$email"
}

ensure_repository_root() {
  [[ -f "Procfile" && -f "requirements.txt" && -f "mira/cloud_run_entrypoint.py" ]] \
    || fail "run this from the root of the ${REQUIRED_REPOSITORY} repository"
}

prepare() {
  local project region runtime_name build_name runtime_email build_email secret account member
  project="$(project_id)"
  [[ -n "$project" && "$project" != "(unset)" ]] || fail "set PROJECT_ID or select a gcloud project first"
  region="${REGION:-$DEFAULT_REGION}"
  runtime_name="${MIRA_CLOUD_RUN_SERVICE_ACCOUNT:-$DEFAULT_RUNTIME_SERVICE_ACCOUNT}"
  build_name="${MIRA_CLOUD_RUN_BUILD_SERVICE_ACCOUNT:-$DEFAULT_BUILD_SERVICE_ACCOUNT}"
  secret="${MIRA_BEARER_SECRET_NAME:-$DEFAULT_SECRET}"
  account="$(active_account)"
  [[ -n "$account" ]] || fail "gcloud has no active authenticated account"
  member="$(principal_member "$account")"

  note "Using project: $project"
  note "Using region: $region"
  gcloud projects describe "$project" >/dev/null
  gcloud config set project "$project" >/dev/null

  note "Enabling bounded deployment APIs..."
  gcloud services enable \
    run.googleapis.com \
    cloudbuild.googleapis.com \
    artifactregistry.googleapis.com \
    secretmanager.googleapis.com \
    iam.googleapis.com \
    --project "$project"

  note "Creating/reusing dedicated runtime and build identities..."
  runtime_email="$(ensure_service_account "$project" "$runtime_name" "MIRA M0 Cloud Run runtime")"
  build_email="$(ensure_service_account "$project" "$build_name" "MIRA M0 Cloud Run builder")"

  note "Granting only the documented source-deploy roles to the active deployer..."
  gcloud projects add-iam-policy-binding "$project" \
    --member="$member" \
    --role='roles/run.sourceDeveloper' >/dev/null
  gcloud projects add-iam-policy-binding "$project" \
    --member="$member" \
    --role='roles/serviceusage.serviceUsageConsumer' >/dev/null

  note "Granting the deployer permission to attach the bounded runtime/build identities..."
  gcloud iam service-accounts add-iam-policy-binding "$runtime_email" \
    --project "$project" \
    --member="$member" \
    --role='roles/iam.serviceAccountUser' >/dev/null
  gcloud iam service-accounts add-iam-policy-binding "$build_email" \
    --project "$project" \
    --member="$member" \
    --role='roles/iam.serviceAccountUser' >/dev/null

  note "Granting the dedicated build identity Cloud Run Builder only..."
  gcloud projects add-iam-policy-binding "$project" \
    --member="serviceAccount:$build_email" \
    --role='roles/run.builder' >/dev/null

  if ! secret_exists "$project" "$secret"; then
    note "Creating restart-stable bearer secret without printing raw material..."
    gcloud secrets create "$secret" \
      --project "$project" \
      --replication-policy='automatic' >/dev/null
    openssl rand -base64 48 | tr -d '\n' | \
      gcloud secrets versions add "$secret" --project "$project" --data-file=- >/dev/null
  else
    note "Bearer secret already exists; preserving the current secret version."
  fi

  note "Granting only the runtime identity access to the bearer secret..."
  gcloud secrets add-iam-policy-binding "$secret" \
    --project "$project" \
    --member="serviceAccount:$runtime_email" \
    --role='roles/secretmanager.secretAccessor' >/dev/null

  printf 'MIRA_PREPARE_STATUS=READY_FOR_DRIVE_SHARE\n'
  printf 'MIRA_SERVICE_ACCOUNT_EMAIL=%s\n' "$runtime_email"
  printf 'MIRA_BUILD_SERVICE_ACCOUNT_EMAIL=%s\n' "$build_email"
  printf 'MIRA_PROJECT_ID=%s\n' "$project"
  printf 'MIRA_REGION=%s\n' "$region"
  printf 'NEXT=Share writer access on the isolated synthetic MIRA Sheet to MIRA_SERVICE_ACCOUNT_EMAIL, then run this script with deploy.\n'
}

read_spreadsheet_id() {
  if [[ -n "${MIRA_GOOGLE_SPREADSHEET_ID:-}" ]]; then
    printf '%s' "$MIRA_GOOGLE_SPREADSHEET_ID"
    return
  fi
  local value
  read -r -p 'Synthetic MIRA Google Sheet ID: ' value
  [[ -n "$value" ]] || fail "MIRA_GOOGLE_SPREADSHEET_ID is required"
  printf '%s' "$value"
}

deploy_once() {
  local project="$1"
  local region="$2"
  local service="$3"
  local runtime_email="$4"
  local build_email="$5"
  local secret="$6"
  local spreadsheet_id="$7"

  gcloud run deploy "$service" \
    --project "$project" \
    --region "$region" \
    --source=. \
    --build-service-account="projects/${project}/serviceAccounts/${build_email}" \
    --service-account="$runtime_email" \
    --allow-unauthenticated \
    --concurrency=1 \
    --scaling=1 \
    --set-env-vars="MIRA_GOOGLE_SPREADSHEET_ID=${spreadsheet_id},MIRA_RATE_LIMIT_PER_MINUTE=${DEFAULT_RATE_LIMIT}" \
    --update-secrets="MIRA_BEARER_TOKEN=${secret}:latest" \
    --quiet
}

service_json() {
  local project="$1"
  local region="$2"
  local service="$3"
  local access_token
  access_token="$(gcloud auth print-access-token)"
  curl -fsS \
    -H "Authorization: Bearer ${access_token}" \
    "https://run.googleapis.com/v2/projects/${project}/locations/${region}/services/${service}"
}

verify_service_control_plane() {
  local project="$1"
  local region="$2"
  local service="$3"
  local expected_runtime_sa="$4"
  service_json "$project" "$region" "$service" | \
    EXPECTED_RUNTIME_SA="$expected_runtime_sa" python3 -c '
import json, os, sys
service = json.load(sys.stdin)
errors = []
scaling = service.get("scaling") or {}
template = service.get("template") or {}
if scaling.get("scalingMode") != "MANUAL":
    errors.append(f"scalingMode={scaling.get('scalingMode')!r}")
if scaling.get("manualInstanceCount") != 1:
    errors.append(f"manualInstanceCount={scaling.get('manualInstanceCount')!r}")
if template.get("maxInstanceRequestConcurrency") != 1:
    errors.append(f"maxInstanceRequestConcurrency={template.get('maxInstanceRequestConcurrency')!r}")
if template.get("serviceAccount") != os.environ["EXPECTED_RUNTIME_SA"]:
    errors.append("runtime service account mismatch")
traffic = service.get("traffic") or []
if any(item.get("tag") for item in traffic):
    errors.append("traffic tag present")
if traffic and sum(int(item.get("percent", 0)) for item in traffic) != 100:
    errors.append("traffic does not total 100 percent")
if errors:
    raise SystemExit("Cloud Run invariant readback failed: " + "; ".join(errors))
print("MIRA_CONTROL_PLANE_STATUS=VERIFIED")
'
}

service_url() {
  local project="$1"
  local region="$2"
  local service="$3"
  gcloud run services describe "$service" \
    --project "$project" \
    --region "$region" \
    --format='value(status.url)'
}

verify_health() {
  local url="$1"
  curl -fsS "${url}/v1/health" | python3 -c '
import json, sys
payload = json.load(sys.stdin)
expected = {"service": "mira", "status": "ok"}
if payload != expected:
    raise SystemExit(f"unexpected health payload: {payload!r}")
print("MIRA_HTTPS_HEALTH_STATUS=VERIFIED")
'
}

read_entity_revision() {
  local url="$1"
  local bearer="$2"
  local resource_id="$3"
  local response_file status
  response_file="$(mktemp)"
  status="$(curl -sS -o "$response_file" -w '%{http_code}' \
    -H "Authorization: Bearer ${bearer}" \
    -H 'Content-Type: application/json' \
    --data "{\"request_id\":\"cloudrun-proof-read-preflight\",\"subject_id\":\"m0-synthetic-user\",\"data_class\":\"entity\",\"action\":\"read\",\"api_major\":1,\"schema_version\":\"mira-api-1\",\"resource_id\":\"${resource_id}\"}" \
    "${url}/v1/query")"
  if [[ "$status" == "404" ]]; then
    rm -f "$response_file"
    printf '0'
    return
  fi
  [[ "$status" == "200" ]] || {
    cat "$response_file" >&2
    rm -f "$response_file"
    fail "entity preflight returned HTTP $status"
  }
  python3 -c 'import json,sys; print(json.load(sys.stdin)["items"][0]["revision"])' < "$response_file"
  rm -f "$response_file"
}

write_entity() {
  local url="$1"
  local bearer="$2"
  local resource_id="$3"
  local expected_revision="$4"
  local idempotency_key="$5"
  local phase="$6"
  curl -fsS \
    -H "Authorization: Bearer ${bearer}" \
    -H 'Content-Type: application/json' \
    --data "{\"command_id\":\"${idempotency_key}\",\"subject_id\":\"m0-synthetic-user\",\"data_class\":\"entity\",\"action\":\"upsert\",\"api_major\":1,\"schema_version\":\"mira-api-1\",\"resource_id\":\"${resource_id}\",\"payload\":{\"proof\":\"cloud-run-live\",\"phase\":\"${phase}\"},\"idempotency_key\":\"${idempotency_key}\",\"expected_revision\":${expected_revision}}" \
    "${url}/v1/commands"
}

verify_command_response() {
  local expected_phase="$1"
  python3 -c '
import json, sys
expected_phase = sys.argv[1]
payload = json.load(sys.stdin)
record = payload.get("record") or {}
if payload.get("readback_verified") is not True:
    raise SystemExit("API did not report exact readback verification")
if record.get("payload") != {"proof": "cloud-run-live", "phase": expected_phase}:
    raise SystemExit(f"unexpected canonical payload: {record.get('payload')!r}")
print(record["revision"])
' "$expected_phase"
}

verify_entity_read() {
  local url="$1"
  local bearer="$2"
  local resource_id="$3"
  local expected_phase="$4"
  local expected_revision="$5"
  curl -fsS \
    -H "Authorization: Bearer ${bearer}" \
    -H 'Content-Type: application/json' \
    --data "{\"request_id\":\"cloudrun-proof-read-${expected_revision}\",\"subject_id\":\"m0-synthetic-user\",\"data_class\":\"entity\",\"action\":\"read\",\"api_major\":1,\"schema_version\":\"mira-api-1\",\"resource_id\":\"${resource_id}\"}" \
    "${url}/v1/query" | \
    EXPECTED_PHASE="$expected_phase" EXPECTED_REVISION="$expected_revision" python3 -c '
import json, os, sys
payload = json.load(sys.stdin)
items = payload.get("items") or []
if len(items) != 1:
    raise SystemExit("expected exactly one canonical entity")
record = items[0]
if record.get("revision") != int(os.environ["EXPECTED_REVISION"]):
    raise SystemExit("canonical revision mismatch")
if record.get("payload") != {"proof": "cloud-run-live", "phase": os.environ["EXPECTED_PHASE"]}:
    raise SystemExit("canonical payload mismatch")
print("MIRA_API_READBACK_STATUS=VERIFIED")
'
}

deploy() {
  local project region service secret runtime_name build_name runtime_email build_email spreadsheet_id bearer url resource_id pre_revision first_revision second_revision run_id
  ensure_repository_root
  project="$(project_id)"
  [[ -n "$project" && "$project" != "(unset)" ]] || fail "set PROJECT_ID or select a gcloud project first"
  region="${REGION:-$DEFAULT_REGION}"
  service="${MIRA_CLOUD_RUN_SERVICE:-$DEFAULT_SERVICE}"
  secret="${MIRA_BEARER_SECRET_NAME:-$DEFAULT_SECRET}"
  runtime_name="${MIRA_CLOUD_RUN_SERVICE_ACCOUNT:-$DEFAULT_RUNTIME_SERVICE_ACCOUNT}"
  build_name="${MIRA_CLOUD_RUN_BUILD_SERVICE_ACCOUNT:-$DEFAULT_BUILD_SERVICE_ACCOUNT}"
  runtime_email="$(service_account_email "$runtime_name" "$project")"
  build_email="$(service_account_email "$build_name" "$project")"
  spreadsheet_id="$(read_spreadsheet_id)"
  run_id="$(date -u +%Y%m%dT%H%M%SZ)-$$"
  resource_id="cloudrun-live-proof"

  service_account_exists "$project" "$runtime_email" || fail "runtime service account does not exist; run prepare first"
  service_account_exists "$project" "$build_email" || fail "build service account does not exist; run prepare first"
  secret_exists "$project" "$secret" || fail "bearer secret does not exist; run prepare first"

  note "Deploying the bounded MIRA service from source..."
  deploy_once "$project" "$region" "$service" "$runtime_email" "$build_email" "$secret" "$spreadsheet_id"
  verify_service_control_plane "$project" "$region" "$service" "$runtime_email"
  url="$(service_url "$project" "$region" "$service")"
  [[ "$url" == https://* ]] || fail "Cloud Run did not return an HTTPS service URL"
  verify_health "$url"

  bearer="$(gcloud secrets versions access latest --secret "$secret" --project "$project")"
  [[ ${#bearer} -ge 32 ]] || fail "retrieved bearer secret is unexpectedly short"

  pre_revision="$(read_entity_revision "$url" "$bearer" "$resource_id")"
  first_revision="$(write_entity "$url" "$bearer" "$resource_id" "$pre_revision" "cloudrun-${run_id}-initial" "initial" | verify_command_response initial)"
  [[ "$first_revision" =~ ^[0-9]+$ ]] || fail "initial API response did not contain a numeric revision"
  verify_entity_read "$url" "$bearer" "$resource_id" initial "$first_revision"

  note "Redeploying the same source with the same Secret Manager bearer to prove restart continuity..."
  deploy_once "$project" "$region" "$service" "$runtime_email" "$build_email" "$secret" "$spreadsheet_id"
  verify_service_control_plane "$project" "$region" "$service" "$runtime_email"
  url="$(service_url "$project" "$region" "$service")"
  verify_health "$url"
  verify_entity_read "$url" "$bearer" "$resource_id" initial "$first_revision"

  second_revision="$(write_entity "$url" "$bearer" "$resource_id" "$first_revision" "cloudrun-${run_id}-post-restart" "post-restart" | verify_command_response post-restart)"
  [[ "$second_revision" =~ ^[0-9]+$ ]] || fail "post-restart API response did not contain a numeric revision"
  verify_entity_read "$url" "$bearer" "$resource_id" post-restart "$second_revision"

  unset bearer
  printf 'MIRA_DEPLOY_STATUS=LIVE_API_AND_RESTART_VERIFIED\n'
  printf 'MIRA_SERVICE_URL=%s\n' "$url"
  printf 'MIRA_SERVICE_ACCOUNT_EMAIL=%s\n' "$runtime_email"
  printf 'MIRA_BUILD_SERVICE_ACCOUNT_EMAIL=%s\n' "$build_email"
  printf 'MIRA_PROOF_RESOURCE_ID=%s\n' "$resource_id"
  printf 'MIRA_PROOF_REVISION=%s\n' "$second_revision"
  printf 'MIRA_PROOF_PHASE=post-restart\n'
  printf 'NEXT=Use an independent Google Sheets readback to verify the persisted entity row at this revision.\n'
}

main() {
  require_command gcloud
  require_command curl
  require_command openssl
  require_command python3

  case "${1:-}" in
    prepare)
      prepare
      ;;
    deploy)
      deploy
      ;;
    *)
      cat >&2 <<'EOF'
Usage:
  PROJECT_ID=<google-cloud-project> bash ops/cloud_run_live_proof.sh prepare
  PROJECT_ID=<google-cloud-project> [REGION=us-east1] bash ops/cloud_run_live_proof.sh deploy

Phase 1 prints the dedicated runtime service-account email and stops. Share only the
isolated synthetic MIRA Sheet to that email as writer before running phase 2.
EOF
      exit 2
      ;;
  esac
}

main "$@"
