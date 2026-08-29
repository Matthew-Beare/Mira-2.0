# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and exact recovery state.

## Product direction

Default Personal MIRA is stock ChatGPT + Google Workspace, with no external infrastructure prerequisite. Android, Microsoft, Apple/iCloud, Cloud Run, Linux and SQL remain supported later lanes but do not block the first useful Google-only Personal product.

Every work session begins and ends by checking `FEATURES.md`, `BACKLOG.md`, and `ROADMAP.md`. CI runs `python -m mira.work_session_alignment check` so active work and feature references cannot drift silently.

## Completed no-app foundation this session

- `M2-M0-007` / `FIRSTBOOT-CORE-001` merged in PR #58 at `a60e8879e71b8f464eb1de1ea8cc15cbd309eccb`: four-question resumable Interview Ledger + CI work-session direction gate + isolated Google persistence/readback proof.
- `M2-M0-008` / `SERVICE-STATE-001` merged in PR #59 at `2fd34e1bd66bcb3a73c632e60457564f9e4a859c`: explicit intent/recommendation/readiness/activation state + isolated Google persistence/readback proof.

The Android packet remains paused at its exact live Apps Script queued-writer proof checkpoint in Git history.

## Active packet

### `M2-M0-009` — Stock-ChatGPT no-app operating protocol

- **Primary work:** `ONBOARD-INSTRUCTIONS`
- **Primary features:** `ONBOARD-001`, `ONBOARD-003`, `ONBOARD-006`
- **Related invariants/features:** `CORE-001`, `STORE-001`, `API-001`, `AUTH-001`, `SERVICE-001`, `CAL-006`, `RECOVERY-002`, `DATA-001`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `integration/m0-009-no-app-protocol`
- **Base SHA:** `2fd34e1bd66bcb3a73c632e60457564f9e4a859c`
- **Pull request:** #60
- **Head before closeout checkpoint:** `cf14933629e40e2cdf502f110096bf56424d7ad0`
- **Status:** implementation complete; source-bundle tests/CI green at pre-closeout head; updated clean release template and fresh-copy first-boot provider proof passed; latest closeout-head CI still required before merge.
- **Objective:** ship a complete sanitized source-backed operating instruction/protocol with the Google Workspace starter so stock ChatGPT can execute first boot against canonical MIRROR state instead of requiring a Python process or Android app.

## Session-start alignment verification — 2026-08-29

### `FEATURES.md`

Verified before implementation:

- `ONBOARD-001` requires complete replacement instruction delivery rather than fragmentary patches.
- `ONBOARD-003` defines the exact four-question Minimum Useful Setup and completion orientation.
- `ONBOARD-006` requires ordinary browser-only Personal setup with no terminal fallback.
- `CORE-001` fixes the assistant/product name as MIRA.
- `STORE-001`, `AUTH-001`, and `API-001` require canonical identity, revision/idempotency, exact readback, and one-authority semantics.
- `SERVICE-001` requires appointment-help intent to remain separate from actual service activation.
- `CAL-006` prohibits pretending preferred Calendar sync is active before verified provider capability/readback.
- `DATA-001` prohibits using legacy production state as a test fixture.

### `BACKLOG.md`

Verified before implementation:

- `ONBOARD-INSTRUCTIONS` already exists as source-backed full instruction replacement work.
- full `SERVICE-COMPOSE-001` depends on broader runtime/source routing and is not the shortest path to a usable stock-ChatGPT first boot;
- `NONTECH-INSTALL-001` remains later installation/upgrade hardening;
- `OPS-BRIEF-VSLICE`, appointments, receipts/assets/inventory, and Android remain preserved work.

### `ROADMAP.md`

Verified before implementation:

- M2-M0.5 requires a useful no-app Personal product before Android resumes;
- the next work should promote the proven Google substrate into actual stock-ChatGPT behavior rather than adding unnecessary infrastructure;
- provider-specific details must remain adapter/protocol concerns rather than changing canonical product semantics.

### Direction result

**ALIGNED.** A complete stock-ChatGPT Workspace operating protocol is a shorter path to an actually usable no-app MIRA than entering the broader service-composition dependency tree now.

## Implemented behavior

`workspace/apps_script/MIRA_NO_APP_INSTRUCTIONS.md` is now the complete source-backed Personal no-app operating-instruction block and is part of the validated Workspace release bundle.

The protocol defines:

1. fixed MIRA identity and zero-external-infrastructure Personal deployment;
2. chat/model memory as evidence, never canonical mutable-state authority;
3. exact Workspace Metadata/Resources/Idempotency preflight;
4. fail-closed direct-single-writer vs queued-writer behavior;
5. stable Resource identity, expected revision, deterministic SHA-256 request fingerprint, idempotency replay/conflict handling, atomic write intent, and exact provider readback;
6. one verified Personal Google authority plus explicit persisted Authority bindings for `entity`, `onboarding_ledger`, and `service_state`;
7. exact four-question Minimum Useful Setup/resume behavior;
8. Calendar preference separated from provider capability/projection truth;
9. appointment-help intent mapped to `service_state/appointments_calendar=requested`, never silently active;
10. fail-closed normal operation when provider state, routing, schema, or readback cannot be verified;
11. preservation of accepted later feature families without pretending they are already live.

`mira/workspace_bundle.py` now requires `MIRA_NO_APP_INSTRUCTIONS.md` as part of the release bundle and rejects a bundle if critical identity, Authority routing, onboarding, service-intent, idempotency/readback, zero-infrastructure, Microsoft, or Apple/iCloud clauses disappear.

`tests/test_workspace_bundle.py` directly verifies the complete protocol and verifies missing critical clauses fail validation.

`workspace/apps_script/README.md` now identifies the protocol as a complete replacement artifact rather than an example/patch and describes its place in the browser-only Personal path.

## Release-starter correction and provider evidence

During packet verification, the clean MIRA 2.0 release starter was found to advertise only `authority`, `authority_binding`, and `entity`. That would have made a fresh no-app first boot fail its own schema preflight.

The protected legacy-production rule was preserved: the corrected file is the MIRA 2.0 clean synthetic/release template, not legacy MIRA production state.

The clean template was updated and read back so `resource_types_json` is now exactly:

`["authority","authority_binding","entity","onboarding_ledger","service_state"]`

Its Resources table remained empty after the schema promotion.

### Fresh-copy proof

A brand-new copy was then created from the corrected clean template: `MIRA Personal Starter - Fresh No-App Protocol Proof`.

Before mutation, provider readback verified:

- `schema_version=mira-structured-state-v1`;
- `adapter_contract=STORE-001`;
- `writer_model=single_writer`;
- the five required resource types were present;
- Resources and Idempotency contained headers only.

Using only synthetic data, one Google Sheets batch then materialized the protocol's first-boot state:

- `authority/google-sheets-personal`, revision 1, verified/enabled, synthetic owner identity;
- `authority_binding/binding-entity`, revision 1;
- `authority_binding/binding-onboarding-ledger`, revision 1;
- `authority_binding/binding-service-state`, revision 1;
- `onboarding_ledger/minimum-useful-setup`, revision 1.

All five matching Idempotency results were written in the same provider batch using the exact request-fingerprint material defined by the native Workspace contract.

Exact provider readback then verified:

- one Personal authority;
- exactly one binding for each required data class;
- all bindings point to `google-sheets-personal`;
- the Interview Ledger payload is `status=in_progress`, empty answers, and `next_question_id=timezone`;
- every Resource row's revision/payload/idempotency key/request hash matches its Idempotency result;
- written backend cells retain readable wrapped/top-aligned formatting.

This is a **fresh-copy protocol-shaped provider proof** of the first-boot substrate. It proves that the corrected release starter plus the source-backed operating protocol can produce the exact canonical state needed to ask question one. It does not claim the current ChatGPT product automatically installs the instruction file into Project Instructions; browser-only installation UX remains `NONTECH-INSTALL-001`/distribution hardening.

## Acceptance status

1. Complete sanitized no-app protocol ships in Workspace starter source — **passed**.
2. MIRA fixed/no rename — **passed**.
3. Canonical Workspace preflight/readback and no chat-memory authority — **passed**.
4. Exact four-question first-boot/resume contract — **passed**.
5. Calendar preference without fake sync — **passed**.
6. Appointment intent maps to requested service state, not active — **passed**.
7. Stable IDs/revision/fingerprint/idempotency/write/readback contract — **passed**.
8. Direct single-writer vs queued-writer fail-closed rule — **passed**.
9. Public source contains no runtime provider IDs/secrets/personal production data — **passed by bundle validation/current packet review**.
10. Bundle validation/direct protocol tests — **passed at PR head `cf14933629e40e2cdf502f110096bf56424d7ad0`**.
11. Existing Apps Script/runtime tests — **passed in CI run `33279835768` at that head**.
12. Session-end alignment — **passed below**.
13. Latest closeout-head CI — **pending after this checkpoint write**.

## Session-end alignment verification — 2026-08-29

### `FEATURES.md`

Re-read after implementation. `ONBOARD-001`, `ONBOARD-003`, `ONBOARD-006`, `CORE-001`, `AUTH-001`, `STORE-001`, `API-001`, `SERVICE-001`, `CAL-006`, `DATA-001`, and `RECOVERY-002` remain compatible with the shipped protocol. The Authority-binding gap discovered during provider verification was corrected rather than bypassed. No Android, receipt, asset, inventory, appointment-provider, Microsoft, or Apple feature was removed or weakened.

### `BACKLOG.md`

Re-read after implementation. The accepted work remains intact. A bookkeeping defect was also found: `FIRSTBOOT-CORE-001` and `SERVICE-STATE-001` still display `queued` even though PRs #58/#59 are merged, and `ONBOARD-INSTRUCTIONS` will remain `queued` until this PR merges. This is stale work-status metadata, not missing feature scope. It must be corrected immediately after/with closeout rather than treated as actual implementation state. The next product work remains browser-only install/distribution hardening and the shortest real user-visible no-app vertical, not Android.

### `ROADMAP.md`

Re-read after implementation. M2-M0.5 still correctly requires useful stock-ChatGPT + Google Workspace MIRA before Android resumes. This packet advanced the user-facing execution path rather than adding external infrastructure.

### Direction result

**ALIGNED.** The packet converted first-boot/state code into a complete source-backed stock-ChatGPT operating contract, corrected the release starter schema, and proved a fresh-copy canonical first-boot state with Authority routing and exact provider readback.

## Exact next action

1. Verify latest-head CI for PR #60 after this closeout commit; repair if red.
2. Merge PR #60 only after latest-head CI is green and remotely verify `main`.
3. Correct stale `BACKLOG.md` implementation statuses for `FIRSTBOOT-CORE-001`, `SERVICE-STATE-001`, and `ONBOARD-INSTRUCTIONS` against the merged evidence; do not alter feature scope or ordering while doing that bookkeeping.
4. Start the next bounded M2-M0.5 packet from the merged head.
5. Highest-value direction: make installation/application of the complete no-app instructions and clean starter genuinely browser-only for a normal user, then drive directly into the first visible no-app service/vertical. Avoid the larger service/runtime dependency tree unless it becomes a hard blocker.
6. Android remains paused at its exact Git-backed live queued-writer proof checkpoint.

## Recovery protocol

Read this file first. If PR #60 is still open, inspect latest head and CI before merge. If merged, verify main, correct the three stale backlog statuses, then create the next M2-M0.5 packet. Keep legacy production state untouched and keep private/provider data out of public Git.
