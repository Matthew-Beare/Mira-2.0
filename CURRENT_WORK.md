# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and its exact resume point.

## Completed packet before this branch

### `M2-G0-008G` — Remaining feature-ledger closeout

- **Merged PR:** #34
- **Merge SHA / main readback:** `acb7e8c9025b7f6096f9a4fcba0ced8d9d68622c`
- **Post-merge completion checkpoint / this branch start SHA:** `0b734df51c815ec16a05a4b0b5a6446dde5f4e78`
- **Result:** recovered category F is closed through F23 and category G through G20; feature inventory is complete.

## Active packet

- **Packet ID:** `M2-G0-009`
- **Name:** Legacy branch/PR reconciliation
- **Class:** forensic reconciliation / final salvage gate before dependency closeout
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `audit/g0-009-legacy-reconciliation`
- **Branch start SHA:** `0b734df51c815ec16a05a4b0b5a6446dde5f4e78`
- **Activation commit:** `cebc9515798563b33da462690b06e00785ec1491`
- **Status:** legacy inventory and disposition analysis complete and checkpointed by this commit; `BACKLOG.md` normalization next.

## Legacy repository inventory result

### Open legacy PRs

Only two open PRs were found in `Matthew-Beare/MIRA-Personal-Production`:

1. **PR #31 — MIRA // MIRROR 1.0 pilot mega-candidate.** Open/unmerged; broad cross-platform/service/inventory/reconciliation/release work. This is **salvage/reference only and must never be wholesale-merged**.
2. **PR #34 — Install resumable MIRROR development control plane.** Its five control-plane files are the predecessor concept of the now-authoritative `Matthew-Beare/Mira-2.0` repository. It is **superseded/rejected for merge**.

### Generated distribution repositories

- `Matthew-Beare/MIRA-Public-Experimental` explicitly states it is a public sanitized distribution, not canonical source, and pins canonical source through `DEPLOYMENT_CHANNEL.json`.
- `Matthew-Beare/MIRA-Institutional-Experimental` explicitly states it is a generated distribution, not an independent source of truth, and pins the canonical source revision.
- Therefore neither repository contributes independent feature authority or separate salvage obligations. Their portable-source evidence is already represented by `DIST-001`/`DIST-002`/`ENTERPRISE-001` and related work.

## Branch reconciliation result

### Already absorbed into legacy `main`

Git compare proves these representative branches are ancestors of legacy `main` and therefore have no unique unmerged work:

- `architecture/server-api-sql-client-ready-v1` — 0 ahead / 18 behind.
- `architecture/future-runtime-hardening-v3` — 0 ahead / 1 behind; earlier v1/v2 are superseded predecessors.
- `feature/full-behavior-dependency-map-v1` — 0 ahead / 30 behind.
- `feature/integration-dependency-guidance-v1` — 0 ahead / 19 behind.
- `feature/owned-feature-reconciliation-v1` — 0 ahead / 51 behind.
- `fix/distribution-current-tree-audit` — 0 ahead / 88 behind.
- `fix/distribution-release-test-parity` — 0 ahead / 81 behind.

Branches pointing at the same historical `8f3fcb...` head are aliases/stale names rather than independent feature sources.

### Diverged but semantically superseded

- `feature/manual-brief-smoke` is 10 commits ahead / 111 behind, but legacy `main` contains a newer `manual_brief_smoke.py` implementation with expanded AUTO-slot behavior. **Disposition: superseded by legacy main; no separate salvage.**
- `feature/distribution-build-artifacts` is 1 ahead / 110 behind, but legacy `main` contains an expanded `build-distributions.yml` workflow. **Disposition: superseded by legacy main.**
- `fix/mira-ci-clean` is 1 ahead / 112 behind and only alters old install documentation/test partitioning. Current legacy main plus audited `ONBOARD-006`/installation tests supersede it. **Disposition: no independent salvage.**
- `mira-mirror-branding` is 3 ahead / 117 behind and changes old naming/onboarding assets. Current MIRA 2.0 `BRAND-001` plus approved modern brand asset work supersede it. **Disposition: historical evidence only; do not import old brand assets/UI.**

### Independent competing productization branch

`feature/productization-docker-oauth-full-ui` is genuinely unique: 4 commits ahead / 0 behind legacy `main`, with a separate `starter/server/mirror_service/` implementation and PWA rewrite.

**Salvage candidates:**
- `starter/server/mirror_service/repository.py` provider/backend repository abstraction and revisioned Memory/Google/Postgres upserts -> `STORE-ADAPTER-001` candidate evidence.
- API version/compatibility checks -> `API-CORE-001` candidate evidence.
- device pairing/token issuance patterns -> `API-CORE-001` + `ANDROID-CLIENT-CORE-001` candidate evidence.
- idempotency key handling and bounded command envelope concepts -> `API-CORE-001` candidate evidence.
- PWA presentation patterns -> later `DESKTOP-PARITY`/web-client work only.

**Reject as current architecture:**
- coarse bearer/session authentication without canonical resource/action scopes;
- direct Google provisioning/provider wiring in the service instead of routing all mutable state through `AUTH-001`/`STORE-001`;
- provider/backend choice selected directly by application configuration without canonical Authority Registry semantics;
- asset move operation overwriting a single `location_uuid`, which violates intended-versus-observed location semantics;
- wholesale branch merge or resurrection as a parallel service stack.

This branch is a useful code quarry, not an architecture source of truth.

## PR #31 disposition matrix

PR #31 remains the largest unmerged candidate. Prior packet audits already established its evidence ceiling and the following durable mapping is now final:

### Salvage selectively

- FastAPI query/command paths, device enrollment/auth, compatibility checks, idempotency, audit/readback concepts -> `API-CORE-001`.
- storage portability/provider adapters and backend migration ideas -> `STORE-ADAPTER-001`, `AUTHORITY-MIGRATION-001`.
- Android build structure, protected-client concepts, WebView shell, reconnect/capture foundations -> `ANDROID-CLIENT-CORE-001`.
- Android visual/TTS scheduling pieces -> `ANDROID-NATIVE-DELIVERY-001`.
- ML Kit barcode, NFC and BLE observation bridges -> `ANDROID-CAPTURE-001`.
- APK/AAB build/signing policy and signature verification -> `ANDROID-RELEASE-001`.
- backup UUID/history/snapshot/digest/provider replication/readback concepts -> `BACKUP-CORE-001`.
- inventory hierarchy/query/identifier/reconciliation pieces -> `LOCATION-STATE-001`, `MOVEMENT-CORE-001`, `INVENTORY-QUERY-001`, existing asset/receipt work.
- receipts/reconciliation/migration candidates -> existing `RECEIPT-*`, `ORDER-*`, `SHOP-CORE-001`, `SERVICE-MIGRATION-001`, `LEGACY-MIGRATION` as applicable.
- local integration catalog/bridge contracts -> `LOCAL-INTEGRATIONS` under `LOCAL-001`.
- release/update/distribution tooling concepts -> `DIST-STARTER-001`, `FEATURE-SHARE-001`, client release work.
- desktop/Tauri/CLI/PWA client work -> later `DESKTOP-PARITY` only after shared API/core semantics exist.

### Explicitly reject

- **wholesale PR #31 merge**;
- direct Android/PWA client OAuth/access-token calls to Google or other canonical provider authorities;
- any client receiving database/provider/source credentials;
- client-specific writable authority or dual-master state;
- broad relationship/device-token implied permissions instead of `PROFILE-013` exact scopes;
- optional idempotency or permissive API/schema fallback for mutations;
- silent scheduler threads that bypass canonical scheduling/run evidence;
- folder/path identity as canonical Knowledge identity;
- backup “success” without restore verification;
- asset/location mutation models that collapse intended and observed location state;
- production signing, physical-device behavior, live provider permissions or integration claims inferred from CI alone;
- old branding/artwork as canonical current MIRA brand assets.

## Governance PR #34 disposition

Legacy PR #34 adds `ROADMAP.md`, `FEATURES.md`, `BACKLOG.md`, `CURRENT_WORK.md` and `project/WORK_PACKET_POLICY.md` to the legacy production repo. Those concepts are now implemented and substantially evolved in the authoritative `Matthew-Beare/Mira-2.0` repository.

**Disposition: superseded/rejected for merge.** It should remain historical evidence only; future governance changes belong in Mira-2.0.

## Feature/evidence impact

No new semantic feature IDs are required by this packet. Existing `candidate_unmerged` and legacy evidence labels already correctly represent the useful unmerged code. G0-009 changes implementation planning/disposition, not product semantics.

## Android product-state impact

This packet does **not** increase the amount of MIRA 2.0 Android code built. It does reduce expected rewrite work:

- we have reusable legacy Android build/release/capture/TTS pieces;
- reusable service patterns exist in both PR #31 and the productization branch;
- the rejected direct-provider/auth/location designs are now explicitly fenced off.

After G0-010, implementation can start without another legacy hunt.

## Acceptance criteria

1. Meaningful open/unmerged legacy PRs identified. **Satisfied: PR #31 and PR #34.**
2. Material divergent branches identified/classified. **Satisfied.**
3. PR #31 mapped to stable MIRA 2.0 work IDs. **Satisfied.**
4. Independent productization branch mapped to `STORE-ADAPTER-001`/`API-CORE-001`/client candidates with conflicts rejected. **Satisfied.**
5. Direct Android-to-provider mutation remains rejected. **Satisfied.**
6. No wholesale mega-branch/PR merge allowed. **Satisfied.**
7. Generated public/institutional mirrors excluded as independent sources. **Satisfied.**
8. Superseded scheduler/distribution/governance/branding branches classified. **Satisfied.**
9. No new semantic feature IDs required. **Satisfied.**
10. No protected legacy production/provider state or executable MIRA 2.0 behavior changed. **Satisfied.**
11. `BACKLOG.md` reconciliation status and durable findings. **Pending.**
12. Bounded PR/merge/readback. **Pending.**

## Exact next action

1. Mark `AUDIT-LEGACY` complete in `BACKLOG.md` and add a concise durable legacy-reconciliation findings section preserving this disposition matrix.
2. Update this file with the backlog normalization SHA and packet-close state.
3. Diff gate intended Git authority files only.
4. Open/verify/merge bounded G0-009 PR and read back `main`.
5. Activate G0-010 `DEP-GRAPH` from the post-merge checkpoint.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture unrelated ideas in BACKLOG unless required for acceptance or explicitly reprioritized.
