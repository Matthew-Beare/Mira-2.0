# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active/recovery packet and exact recovery state.

## Product direction

Default Personal MIRA remains stock ChatGPT + Google Workspace first, with provider-neutral expansion through explicit ordinary-user connections. MIRA should progressively learn what tools and services a user already relies on and recommend useful supported integrations without silently installing, authorizing, activating, migrating, or changing canonical authority.

`M2-M1-001` through `M2-M1-006` are durably closed. `M2-GOV-012` is also durably closed at its bounded product/governance specification evidence ceiling.

## Prior-packet recovery verification — 2026-09-03

- Repository: `Matthew-Beare/Mira-2.0`.
- M2-GOV-012 final closeout/main SHA: `290b78518947f060e06a11d9141faf0c5d64d4e5`.
- Exact-head CI: `33731858470` — success on that exact SHA.
- M2-GOV-012 parent/merge SHA: `00fa7ccf53e8e4e7e0a0630a2e5a891dbd78eac7`.
- M2-M1-001 through M2-M1-006 and M2-GOV-012 must not be rerun.

## Session-start alignment verification — 2026-09-03 M2-M1-007

### `FEATURES.md`

- `CLIENT-ANDROID-001` remains the required Android client feature and is only partially evidenced.
- `PROVIDER-002` requires an ordinary-user Connect flow with automated post-consent discovery, binding, capability verification and exact readback.
- `PROVIDER-003` already defines deterministic Personal Google bootstrap/readback semantics and must remain the Google-specific implementation boundary rather than changing product semantics.
- `AUTH-001`, `STORE-001`, `API-001`, `RECOVERY-002`, and `SERVICE-001` remain integrity boundaries that this packet must preserve.

### `BACKLOG.md`

- `ANDROID-COMMAND-BOUNDARY-001` is complete and must not be revisited.
- `ANDROID-CLIENT-CORE-001` is partial through M2-M1-006. The next unfinished dependency-correct slice is real Google provider authorization/network binding plus automatic Workspace discovery/binding beneath the already-tested `GoogleWorkspaceTransport` contract.
- `ANDROID-SYNC` remains a later vertical and is not pulled into this packet except where a narrow test seam is required.

### `ROADMAP.md`

- M2-M1 requires Android to read and mutate the same canonical Personal reality without becoming a second authority.
- The next proof step is Android client core provider binding, before full shared-state mutation/readback or representative-device proof.

### `PRODUCT_INVARIANTS.md`

- Android must use the same simple connection semantics as stock ChatGPT and must not export OAuth scopes, resource IDs, developer-console work, terminal steps, or hidden-resource creation to an ordinary user.
- Provider consent, capability verification, resource binding, service activation and canonical authority remain separate truths.
- Legacy production state remains protected and cannot be used as a development fixture.

### Direction result

**ALIGNED.** Open one bounded Android provider-binding packet. Implement source and deterministic tests first. Do not use Work mode or live provider state until local/source/CI evidence is green and a narrow live acceptance proof is actually needed.

## Active packet

### `M2-M1-007` — Android Google authorization and Workspace binding

- **Primary work:** `ANDROID-CLIENT-CORE-001`
- **Primary features:** `CLIENT-ANDROID-001`, `PROVIDER-002`, `PROVIDER-003`
- **Related invariants/features:** `AUTH-001`, `STORE-001`, `API-001`, `SERVICE-001`, `RECOVERY-002`, `SOURCE-001`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `work/m2-m1-007-android-google-binding`
- **Packet base SHA:** `290b78518947f060e06a11d9141faf0c5d64d4e5`
- **Current head SHA:** pending this checkpoint commit
- **Status:** active

## Objective

Implement the narrow Android-native Google connection boundary required by the already-tested `GoogleWorkspaceTransport`: obtain revocable same-user Google authorization through a product-owned Android connection flow, automatically discover and verify the correct MIRA Personal Workspace spreadsheet without asking the user for a spreadsheet ID, bind a concrete bounded Sheets gateway, and expose honest connection/readiness state to the existing reconnect layer.

This packet does **not** implement the full Android app, full `ANDROID-SYNC`, conflict UI, notification/TTS delivery, camera/NFC/BLE capture, release signing, representative-device proof, or stock-ChatGPT cross-readback.

## Dependencies and blockers

- `ANDROID-COMMAND-BOUNDARY-001` — complete.
- `GoogleWorkspaceTransport`, `ReconnectCoordinator`, protected credential storage, encrypted offline queue/cache/cursor state — merged/test-verified through M2-M1-006.
- Google OAuth client registration/release signing configuration is deployment/provider configuration, not repository secret material. No client secret or personal provider identifier may be committed.
- Live Google/device proof is intentionally deferred until source/tests/CI are green.

## Acceptance criteria

1. **Android-native authorization boundary** — production code defines a product-owned Google authorization adapter that requests only the minimum Drive/Sheets access needed for this lane, supports reconnect/revocation semantics, and never requires an ordinary user to copy OAuth scopes, IDs, tokens, or provider resource identifiers.
2. **Automatic Workspace discovery** — after authorization, code discovers candidate Google Sheets files through provider metadata and validates MIRA identity by reading bounded `Metadata` cells. Selection must fail closed on zero matches, ambiguity, schema mismatch, or non-Personal/legacy-looking state rather than guessing.
3. **Exact binding evidence** — the selected spreadsheet binding records only non-secret provider identity/configuration needed by the client, distinguishes authorization from verified readiness, and can be revalidated before use.
4. **Concrete narrow Sheets gateway** — a Google-backed implementation of `GoogleWorkspaceTransport.SheetsGateway` can read the bounded `Commands` and `Changes` tables and append exactly one command row with provider error normalization and no generic arbitrary-sheet mutation surface.
5. **Provider-neutral transport preserved** — `GoogleWorkspaceTransport`, canonical command semantics, cursor/replay rules, Authority/store ownership, and readback requirements remain unchanged except for the concrete adapter seam needed to bind the provider.
6. **No legacy production mutation** — deterministic tests use fakes/synthetic fixtures only. No personal Sheet ID, token, email, credential, legacy MIRA artifact, or live production content is committed or used as a fixture.
7. **Tests** — unit tests cover successful authorization handoff, denied/expired authorization, candidate discovery, exact metadata validation, ambiguous candidates, schema mismatch, gateway bounded reads/appends, HTTP/provider failure mapping, reconnect/revalidation, and no-manual-ID behavior.
8. **Build/CI** — required Android unit tests and repository CI pass on the exact packet head before merge.
9. **Evidence ceiling** — this packet may reach implemented/test/integration evidence in Git. It must not claim live provider authorization, physical-device behavior, production signing, or shared-state Android↔ChatGPT proof without separate exact provider/device evidence.

## Completed evidence

- Session-start Git recovery verified remote `main` at `290b78518947f060e06a11d9141faf0c5d64d4e5`.
- Exact-head CI `33731858470` succeeded on that closeout SHA.
- Canonical feature/backlog/roadmap/invariant alignment was re-read before implementation.
- Active branch created from the exact verified main SHA: `work/m2-m1-007-android-google-binding`.

## Exact next action / resume point

1. Inspect the current `GoogleWorkspaceTransport`, Android core build dependencies and provider bootstrap metadata contract.
2. Add the bounded Google authorization/discovery/binding abstractions and concrete Sheets gateway without provider secrets or user-specific IDs.
3. Add deterministic JVM tests with fake authorization/HTTP/provider responses.
4. Run/verify Android unit tests and full repository CI.
5. Reconcile `BACKLOG.md`, `FEATURES.md`, `ROADMAP.md`, `PRODUCT_INVARIANTS.md`, and `CURRENT_WORK.md` before merge.
6. Only after green source/CI evidence decide whether a separate Work/provider/device acceptance proof is necessary.

## Recovery protocol

Read this file first. Verify branch `work/m2-m1-007-android-google-binding` is based on `290b78518947f060e06a11d9141faf0c5d64d4e5`. Do not rerun M2-M1-001 through M2-M1-006 or M2-GOV-012. Continue at the exact next action above.
