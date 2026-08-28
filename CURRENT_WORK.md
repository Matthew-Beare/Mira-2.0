# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and its exact resume point.

## Completed packet before this branch

### `M2-G0-008G` — Remaining feature-ledger closeout

- **Merged PR:** #34
- **Merge SHA / main readback:** `acb7e8c9025b7f6096f9a4fcba0ced8d9d68622c`
- **Post-merge completion checkpoint / this branch start SHA:** `0b734df51c815ec16a05a4b0b5a6446dde5f4e78`
- **Result:** feature inventory is complete through F23/G20.

## Active packet

- **Packet ID:** `M2-G0-009`
- **Name:** Legacy branch/PR reconciliation
- **Class:** forensic reconciliation / final salvage gate before dependency closeout
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `audit/g0-009-legacy-reconciliation`
- **Branch start SHA:** `0b734df51c815ec16a05a4b0b5a6446dde5f4e78`
- **Activation commit:** `cebc9515798563b33da462690b06e00785ec1491`
- **Research/disposition checkpoint:** `bbc3d5446b6d50e9e028a0ba5570574769bff478`
- **Backlog normalization:** `cd79f733ab7bff3f4540812d20fe73996c8374d3`
- **Status:** acceptance complete; diff gate, PR, merge and main readback remain.

## Canonical reconciliation result

- Legacy Personal-Production has two open PRs: **#31** and **#34**.
- PR #31 is **selective salvage/reference only; never wholesale merge**.
- PR #34 governance/control-plane work is **superseded by authoritative Mira-2.0; reject merge**.
- Public and Institutional Experimental repositories explicitly identify themselves as generated, non-canonical distributions and create no independent feature authority.
- Representative architecture/dependency/reconciliation/distribution-fix branches are already ancestors of legacy `main`.
- Diverged manual-brief/distribution-build/install-cleanup branches are semantically superseded by newer legacy-main behavior.
- Old `mira-mirror-branding` work is historical evidence only; current `BRAND-001`/approved modern brand assets win.
- `feature/productization-docker-oauth-full-ui` is a genuine 4-commit independent code quarry. Salvage its repository abstraction/revisioned upserts, compatibility, pairing and idempotency patterns into `STORE-ADAPTER-001`/`API-CORE-001`; reject its coarse auth, direct Google wiring, non-registry backend selection, single-location overwrite model and parallel-service-stack architecture.

## PR #31 salvage ceiling

Selective candidates are already mapped to existing work IDs:

- API/auth/idempotency/compatibility/readback -> `API-CORE-001`.
- storage adapters/portability -> `STORE-ADAPTER-001`, `AUTHORITY-MIGRATION-001`.
- Android core/delivery/capture/release -> `ANDROID-CLIENT-CORE-001`, `ANDROID-NATIVE-DELIVERY-001`, `ANDROID-CAPTURE-001`, `ANDROID-RELEASE-001`.
- backup snapshot/digest/provider replication -> `BACKUP-CORE-001`.
- inventory/location/receipt/reconciliation/migration -> existing domain work including `LOCATION-STATE-001`, `MOVEMENT-CORE-001`, `INVENTORY-QUERY-001`, receipt/order/shop/migration work.
- local-service contracts -> `LOCAL-INTEGRATIONS` under `LOCAL-001`.
- distribution/update/client packaging -> `DIST-STARTER-001`, `FEATURE-SHARE-001`, later client-release work.
- desktop/Tauri/PWA -> `DESKTOP-PARITY` after shared core/API.

Explicit rejects remain direct client-to-provider authority mutation, client DB/provider/source credentials, dual writable masters, relationship/device-token implied permissions, permissive mutation compatibility/idempotency, silent scheduler threads, path identity as Knowledge authority, backup-without-restore claims, collapsed intended/observed location, and CI-implied live/signing/device/provider claims.

## Feature impact

No new semantic feature IDs were required by G0-009. Existing `legacy_*` and `candidate_unmerged` evidence labels remain correct.

## Android product-state checkpoint

- MIRA 2.0 APK: **not built yet**.
- Shared MIRA API: **not built yet**.
- Android shared-state proof: **not yet**.
- Reusable legacy Android/service/storage pieces: **identified and fenced to current architecture**.

The rewrite risk is now lower, but implementation percentage has not materially changed.

## Acceptance criteria

1. Meaningful open/unmerged PRs identified. **Satisfied.**
2. Material divergent branches classified. **Satisfied.**
3. PR #31 mapped to stable work IDs with explicit salvage/reject boundary. **Satisfied.**
4. Independent productization branch mapped/rejected as architecture. **Satisfied.**
5. Generated mirrors excluded as independent sources. **Satisfied.**
6. No wholesale mega-merge/direct-provider authority path permitted. **Satisfied.**
7. No new semantic feature IDs required. **Satisfied.**
8. `AUDIT-LEGACY` marked complete in `BACKLOG.md`. **Satisfied.**
9. No protected legacy production/provider state or executable MIRA 2.0 behavior changed. **Satisfied.**
10. Bounded PR/merge/readback. **Pending.**

## Exact next action

1. Compare `audit/g0-009-legacy-reconciliation` against `main`; require only intended Git authority files.
2. Open bounded PR, verify exact filenames/head/mergeability, merge exact head and read back `main`.
3. Create G0-010 dependency-closeout branch from the post-merge checkpoint.
4. G0-010 is the final pre-implementation packet.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture unrelated ideas in BACKLOG unless required for acceptance or explicitly reprioritized.
