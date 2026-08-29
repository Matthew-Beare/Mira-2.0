# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and the exact recovery point for displaced work.

## Product-owner correction captured 2026-08-29

The default Personal MIRA path is **Google Workspace first, zero infrastructure**. An ordinary user should be able to start with Google Drive/Docs/Sheets and a browser-only setup. Linux, SQL, Cloud Run, containers, tunnels, and other infrastructure are advanced upgrade paths, not prerequisites for first use.

Canonical deployment ladder:

1. Personal Google Workspace baseline: Sheets as the first structured MIRROR authority; copied/bound Apps Script as the lightweight HTTPS execution boundary; no terminal or server required.
2. Advanced managed/self-hosted profiles: Cloud Run, Linux VM, containers, SQL, local services, or other supported backends when the user needs them.
3. Migration preserves MIRA semantics: `API-001`, `AUTH-001`, and `STORE-001` remain provider-neutral so backend changes are Authority/adapter cutovers, not product rewrites.

Google documentation was rechecked before this correction: copying a spreadsheet copies attached bound Apps Script, and a bound script can be deployed as a web app. This makes a copy/authorize/deploy style Personal starter technically viable.

## Displaced packet checkpoint

### `M2-M0-005` — Cloud Run credential + live Google deployment proof

- **Related work:** `API-DEPLOYMENT-001B` (formerly the only `API-DEPLOYMENT-001` implementation target)
- **Disposition:** paused/deprioritized, not failed and not deleted.
- **Reason:** Cloud Run is valid advanced infrastructure but violates the intended ordering if required before ordinary Personal Google first use.
- **Deployment-readiness PR:** #48, merged at `acb37af4aa378e8128d8591406859fe954af3474`; CI `33217543700` green.
- **Cloud Shell operator PR:** #49, merged at `3332081054d691eca646c1d7bb274d22096f1c62`; CI `33218561781` green.
- **Exact pre-pivot main checkpoint:** `c392b9b829fab989be8856c9272294c9907e409e`.
- **Exact resume point if/when advanced Cloud Run proof is selected again:** run the merged `ops/cloud_run_live_proof.sh prepare` phase in an authenticated Google Cloud project, return only the runtime service-account email, share only the synthetic MIRROR Sheet, then run `deploy` and perform independent provider readback. No live Cloud Run/provider/restart evidence has been claimed.

All Cloud Run code, tests, IAM/scaling invariants, and operator work remain useful for an advanced deployment profile.

## Active packet

### `M2-M0-006` — Google Workspace zero-infrastructure first run

- **Related work ID:** `API-DEPLOYMENT-001A`
- **Class:** hard M2-M0 prerequisite / ordinary-user vertical deployment slice
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `integration/m0-006-google-workspace-first-run`
- **Branch start SHA:** `fa0ff6741cc0294dd82d128428ea9a03c2a86a2e`
- **Current branch head SHA:** `fa0ff6741cc0294dd82d128428ea9a03c2a86a2e` (no implementation commit yet)
- **Roadmap correction commit:** `c317f59b3c6546bdd92c23a9eaed32474e82574b`
- **Backlog re-rank commit:** `313fdb3c14ef6dfd714e2587130b94838581e41d`
- **Packet activation commit:** `fa0ff6741cc0294dd82d128428ea9a03c2a86a2e`
- **Status:** active; branch created from the remotely verified corrected checkpoint; implementation has not started yet.

## Objective

Prove the default Personal MIRA deployment without requiring the user to provision or understand infrastructure: a copyable Google Workspace starter uses Sheets as the first structured MIRROR authority and bound Apps Script as the lightweight HTTPS endpoint while preserving the already-built provider-neutral MIRA API, Authority, idempotency, conflict, and readback semantics.

The first-run experience should trend toward **copy starter → authorize MIRA → enable/deploy → connect ChatGPT**, not Cloud Console, SSH, Docker, Linux, SQL, or terminal commands.

## Acceptance criteria

1. **No infrastructure prerequisite.** Baseline setup requires no self-hosted server, Cloud Run project, Linux/SQL administration, Cloudflare/WireGuard tunnel, terminal, or paid OpenAI API usage.
2. **Copyable Workspace packaging.** The starter is designed around a Google Sheet whose attached bound Apps Script travels with a user-created copy; no live personal IDs or secrets are committed to the public repository.
3. **Same MIRA API semantics.** Apps Script exposes the minimal health/query/command behavior needed for `API-001`; it must not create a second Google-specific canonical API model.
4. **Same canonical authority semantics.** Structured state remains behind `AUTH-001`/`STORE-001` contracts with exact readback, revisions, idempotency and conflict behavior consistent with the implemented core.
5. **Scoped authentication.** The external ChatGPT-facing endpoint has an explicit same-user authentication boundary; no secret is stored in ordinary visible Sheet cells or committed to Git.
6. **Google-backed roundtrip.** A synthetic entity can be created, exactly read back, mutated, replay-checked and provider-readback verified through the Workspace endpoint.
7. **Browser-first setup proof.** The bounded M2-M0 setup path itself is browser-only; full broader onboarding polish can follow, but terminal fallback is not allowed for the baseline.
8. **Legacy preservation.** Only the isolated MIRA 2.0 synthetic namespace/starter is used. Legacy production Google artifacts remain untouched.
9. **Portability preserved.** Google-specific execution/storage details stay behind adapter/runtime boundaries. The resulting canonical data and API model must remain migratable later through `AUTHORITY-MIGRATION-001` to Linux/SQL/Cloud Run without dual writable masters.
10. **Cloud Run does not block M2-M0.** `API-DEPLOYMENT-001B` remains advanced hardening and may resume later without blocking this packet or `CHATGPT-API-CLIENT-001`.

## Existing evidence available to reuse

- Provider-neutral structured-state, Authority Registry, API core, idempotency/conflict/readback behavior are already implemented and test-verified.
- The isolated synthetic Google Sheet namespace and Google structured-state adapter already have provider readback evidence.
- `ONBOARD-006` already defines browser-only nontechnical installation with no terminal fallback.
- `ONBOARD-002` already requires a sanitized generic starter with no inherited personal production state.
- Google documents that a copied spreadsheet copies attached scripts and that bound scripts can become web apps.
- Cloud Run deployment code remains preserved as an advanced profile and should not be deleted or contorted into the Workspace baseline.

## Scope control

This packet is **not** full Personal Google service onboarding. Do not fan out into Gmail, Calendar, scheduler, Ops Briefs, family sharing, enterprise distribution, Android, Linux/SQL migration implementation, or general UI polish unless required to prove the baseline Workspace endpoint acceptance criteria.

Do not make the customer design Apps Script internals, auth format, schema mapping, or deployment mechanics unless a choice materially changes user-visible behavior, privacy, cost, or irreversibility.

## Exact next action

1. On `integration/m0-006-google-workspace-first-run`, inspect the current `API-001` transport/core and Google structured-state adapter contracts and define the smallest Apps Script surface that preserves those semantics.
2. Implement the first bounded slice: copyable bound-script package structure plus health/schema/read path against synthetic Workspace state, with direct tests and no provider/private IDs.
3. Add write/idempotency/conflict/auth behavior only in subsequent bounded slices if the first slice is green.
4. Keep `CURRENT_WORK.md` updated with exact branch/head/resume evidence after each slice.

## Recovery protocol

Read this file first. Confirm `main` records branch `integration/m0-006-google-workspace-first-run` starting at `fa0ff6741cc0294dd82d128428ea9a03c2a86a2e`, and that `M2-M0-005` remains preserved at checkpoint `c392b9b829fab989be8856c9272294c9907e409e`. Continue only `M2-M0-006` unless the customer explicitly reprioritizes or a hard integrity/security dependency blocks it. Do not resume Cloud Run merely because its code already exists.
