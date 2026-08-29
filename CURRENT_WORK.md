# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and the exact recovery point for displaced work.

## Product-owner correction captured 2026-08-29

The default Personal MIRA path is **Google Workspace first, zero infrastructure**. An ordinary user should be able to start with Google Drive/Docs/Sheets and a browser-only setup. Linux, SQL, Cloud Run, containers, tunnels, and other infrastructure are advanced upgrade paths, not prerequisites for first use.

Canonical deployment ladder:

1. Personal Google Workspace baseline: Sheets as the first structured MIRROR authority; copied/bound Apps Script as the lightweight browser-managed execution layer; no terminal or server required.
2. Advanced managed/self-hosted profiles: Cloud Run, Linux VM, containers, SQL, local services, or other supported backends when the user needs them.
3. Migration preserves MIRA semantics: `API-001`, `AUTH-001`, and `STORE-001` remain provider-neutral so backend changes are Authority/adapter cutovers, not product rewrites.

## Displaced packet checkpoint

### `M2-M0-005` — Cloud Run credential + live Google deployment proof

- **Related work:** `API-DEPLOYMENT-001B`.
- **Disposition:** paused/deprioritized, not failed and not deleted.
- **Deployment-readiness PR:** #48, merged at `acb37af4aa378e8128d8591406859fe954af3474`; CI `33217543700` green.
- **Cloud Shell operator PR:** #49, merged at `3332081054d691eca646c1d7bb274d22096f1c62`; CI `33218561781` green.
- **Exact pre-pivot main checkpoint:** `c392b9b829fab989be8856c9272294c9907e409e`.
- **Exact resume point if advanced Cloud Run proof is selected again:** run the merged `ops/cloud_run_live_proof.sh prepare` phase in an authenticated Google Cloud project, return only the runtime service-account email, share only the synthetic MIRROR Sheet, then run `deploy` and perform independent provider readback.

No live Cloud Run/provider/restart evidence has been claimed. All Cloud Run code/tests remain preserved as an advanced deployment profile.

## Active packet

### `M2-M0-006` — Google Workspace zero-infrastructure first run

- **Related work ID:** `API-DEPLOYMENT-001A`
- **Class:** hard M2-M0 prerequisite / ordinary-user vertical deployment slice
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `integration/m0-006-google-workspace-first-run`
- **Branch start SHA:** `fa0ff6741cc0294dd82d128428ea9a03c2a86a2e`
- **Current implementation head before this checkpoint:** `bbf2f8cc8563b66ac84d9696a76e24990e108ebf`
- **Roadmap correction:** `c317f59b3c6546bdd92c23a9eaed32474e82574b`
- **Backlog re-rank:** `313fdb3c14ef6dfd714e2587130b94838581e41d`
- **Main branch-record checkpoint:** `d38dc1d42373582c8737ccb7c71e363e92327aff`
- **Status:** first bounded Workspace read slice implemented; PR/CI pending.

## Objective

Prove the default Personal MIRA deployment without requiring infrastructure administration. A copyable Google Workspace starter uses Sheets as the first structured MIRROR authority and bound Apps Script as the browser-managed execution layer while preserving provider-neutral MIRA API, Authority, idempotency, conflict, and readback semantics.

The intended user experience trends toward **copy starter → authorize MIRA → initialize/enable → connect ChatGPT**, not Cloud Console, SSH, Docker, Linux, SQL, or terminal commands.

## Acceptance criteria

1. **No infrastructure prerequisite.** Baseline setup requires no self-hosted server, Cloud Run project, Linux/SQL administration, Cloudflare/WireGuard tunnel, terminal, or paid OpenAI API usage.
2. **Copyable Workspace packaging.** The starter is designed around a Google Sheet whose attached bound Apps Script travels with a user-created copy; no live personal IDs or secrets are committed to the public repository.
3. **Same MIRA API semantics.** Apps Script exposes the minimal health/query/command behavior needed for `API-001`; it must not create a second Google-specific canonical API model.
4. **Same canonical authority semantics.** Structured state remains behind `AUTH-001`/`STORE-001` contracts with exact readback, revisions, idempotency and conflict behavior consistent with the implemented core.
5. **Scoped authentication.** The external ChatGPT-facing boundary must have explicit same-user authentication; no secret may be stored in ordinary visible Sheet cells or committed to Git.
6. **Google-backed roundtrip.** A synthetic entity can be created, exactly read back, mutated, replay-checked and provider-readback verified through the Workspace path.
7. **Browser-first setup proof.** The bounded M2-M0 setup path itself is browser-only; terminal fallback is not allowed for the baseline.
8. **Legacy preservation.** Only the isolated MIRA 2.0 synthetic namespace/starter is used. Legacy production Google artifacts remain untouched.
9. **Portability preserved.** Google-specific execution/storage details stay behind adapter/runtime boundaries so later `AUTHORITY-MIGRATION-001` cutover to Linux/SQL/Cloud Run does not create dual writable masters.
10. **Cloud Run does not block M2-M0.** `API-DEPLOYMENT-001B` remains advanced hardening.

## First bounded slice implemented

- `workspace/apps_script/Code.gs`
  - bound-Sheet `MIRA → Initialize this copy` menu action;
  - runtime-only spreadsheet identity stored in Script Properties;
  - web runtime reopens only the initialized copy with `SpreadsheetApp.openById` because Google does not expose bound-container active methods to web-app execution;
  - `/v1/health` validates state before returning the existing MIRA health payload;
  - `/v1/schema` reads/validates `STORE-001` Metadata state;
  - `/v1/query` supports `action=read` only;
  - persisted `authority_binding` → `authority` resolution occurs before canonical reads;
  - API/schema/header/resource validation and stable MIRA error categories;
  - `/v1/commands` explicitly fails closed.
- `workspace/apps_script/appsscript.json`: V8/current-Sheet scope manifest for the starter artifact.
- `workspace/apps_script/README.md`: scope, packaging, portability, and no-public-deploy warning.
- `mira/workspace_bundle.py`: public-bundle shape/privacy validator; rejects provider IDs and secret markers and verifies runtime-only copy binding.
- `tests/test_workspace_bundle.py`: direct Python bundle/privacy verification.
- `tests/apps_script/workspace_read.test.js`: executable Node tests with fake Apps Script/Spreadsheet services for initialization, health, schema, canonical authority read, compatibility failure, missing entity, and commands fail-closed.
- CI now pins Node 22 and runs the Apps Script test suite in addition to existing Python gates.
- `project/code_ownership.json`: `workspace-first-run` owns the Python bundle integrity boundary under `API-DEPLOYMENT-001A`.

## Important platform constraints discovered

1. Google documents that bound-container methods such as `SpreadsheetApp.getActiveSpreadsheet()` are unavailable when the bound script runs as a web app. Therefore the browser initializer captures the copied Sheet identity into Script Properties and web execution reopens that exact Sheet by ID.
2. Apps Script `doGet(e)` / `doPost(e)` event data exposes path/query/body fields but does **not** expose arbitrary incoming request headers. OpenAI GPT Actions API-key authentication is delivered as Basic/Bearer/custom headers. Therefore standard GPT Action API-key auth cannot simply be copied onto an Apps Script web app.
3. This first slice is deliberately read-only and must **not** be deployed as an anonymous production endpoint. The next slice must resolve the stock-ChatGPT authentication/client boundary before protected reads or any writes are enabled.

The authentication constraint is a real compatibility gate, not permission to weaken security or hide a bearer token in visible Sheet cells.

## Scope control

This packet is not full Personal Google service onboarding. Do not fan out into Gmail, Calendar, scheduler, Ops Briefs, family sharing, enterprise distribution, Android, Linux/SQL migration implementation, or UI polish unless required to prove the baseline Workspace path.

Do not resume Cloud Run merely because its code exists. Do not enable Workspace writes until the external client/auth path is explicitly safe.

## Exact next action

1. Open a PR for the first read-only Workspace slice and run full CI, including the Node Apps Script tests.
2. Fix any CI defect without broadening scope.
3. Merge/read back the read slice only when green.
4. Then resolve the stock-ChatGPT authentication/client path under the zero-infrastructure constraint. Evaluate supported native Google Workspace/ChatGPT connectivity before inventing a URL/body secret workaround; standard GPT Action API-key headers are not directly visible to Apps Script web apps.
5. Only after the auth/client boundary is safe, implement the next bounded slice for write/idempotency/conflict behavior and live synthetic Google readback.

## Recovery protocol

Read this file first. Continue `M2-M0-006` on `integration/m0-006-google-workspace-first-run` until the first read-only slice is merged. Preserve `M2-M0-005` at checkpoint `c392b9b829fab989be8856c9272294c9907e409e`. Do not claim live Apps Script deployment/auth/write evidence from code-only tests. Keep provider IDs, personal data, and secrets out of Git.
