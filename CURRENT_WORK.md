# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and exact recovery state.

## Product direction

Default Personal MIRA is stock ChatGPT + Google Workspace with no external infrastructure prerequisite. Completed work remains durable with evidence and is filtered from future selection rather than deleted. The current priority is repeated no-app verticals that build trustworthy canonical reality before Android resumes.

Every work session begins and ends by checking `CURRENT_WORK.md`, `FEATURES.md`, `BACKLOG.md`, and `ROADMAP.md`.

## Completed predecessor

### `M2-M0-012` — Canonical no-app receipt intake + purchase history

Merged in PR #64 to `main` at `804a664f343934cc813d9cc45b471a6756a15697` after exact-head CI `33284284178` passed. Canonical receipt capture/history, receipt release wiring and isolated Google multi-source revision-1/revision-2 readback are complete. `RECEIPT-INTAKE-001` is reconciled completed in `BACKLOG.md` on this branch.

## Preserved checkpoints

- Android / `M2-M1-001` remains paused at the isolated Google queued-writer live-proof point.
- Existing live MIRA/legacy Google receipt, asset, inventory, Drive and automation state remains protected production and is not a development fixture.
- Fitment, identifiers, evidence enrichment, warranty/maintenance, inventory/location/movement, shopping, grocery/meal and provider-side archival remain separate accepted work.
- `ASSET-SERVICE-001` remains warranty/maintenance hardening and is not misused as the foundational asset-acquisition packet.

## Active packet

### `M2-M0-013` — Canonical receipt-linked asset acquisition

- **Primary work:** `ASSET-ACQUISITION-001`
- **Primary features:** `ASSET-001`, `ASSET-002`
- **Related invariants/features:** `RECEIPT-001`, `RECEIPT-002`, `INV-001`, `FITMENT-001`, `IDENT-001`, `EVID-001`, `STORE-001`, `RECOVERY-002`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `integration/m0-013-asset-acquisition`
- **Base SHA:** `804a664f343934cc813d9cc45b471a6756a15697`
- **Objective:** create/read/replay/enrich one canonical physical asset from verified canonical receipt/line provenance while preserving an immutable RFC 4122 Entity UUID. The packet proves acquisition identity only; it does not implement fitment, identifiers, warranty/maintenance, location/movement or broad inventory projection.

## Session-start alignment verification — 2026-08-29/30

### `FEATURES.md`

Rechecked before implementation:

- `ASSET-001` requires every physical asset to keep one immutable canonical RFC 4122 Entity UUID; labels, owner, category, location, project, backend, receipt enrichment and lifecycle changes cannot replace that UUID;
- acquisition deduplicates by source identity and supported evidence; replay of the same source preserves the same UUID and compatible enrichment updates the same asset;
- `individual` tracking requires quantity exactly one;
- set/lot tracking may represent quantity greater than one under one UUID when individual serial-level identity is not useful;
- excluded/cancelled/removed-before-settlement purchase evidence must not manufacture assets;
- `ASSET-002` requires provenance-linked acquisition/reference evidence while keeping receipt/evidence projection failure independent from verified physical identity;
- `FITMENT-001` is a relationship feature and cannot be encoded by changing asset identity;
- `INV-001` later reuses the canonical Entity UUID rather than inventing inventory identity;
- `IDENT-001`/`EVID-001` enrich the same entity later and may not replace its UUID.

Historical audit evidence in PR #10 was also re-read. It explicitly records deterministic UUID allocation/validation, source dedupe/replay, enrichment without UUID replacement, quantity/tracking rules, excluded receipt lines and UUID-collision handling as prior test-backed semantics, while MIRA 2.0 provider persistence remains the gap this packet addresses.

### `BACKLOG.md`

Rechecked and reconciled before implementation:

- `RECEIPT-INTAKE-001` is completed by PR #64;
- no existing work item correctly represented foundational `ASSET-001` acquisition; `ASSET-SERVICE-001` is explicitly warranty/maintenance hardening;
- new bounded work ID `ASSET-ACQUISITION-001` therefore owns this implementation slice;
- `FITMENT-ENGINE-001`, `ASSET-SERVICE-001`, `LOCATION-STATE-001`, `MOVEMENT-CORE-001`, `INVENTORY-QUERY-001` and receipt taxonomy remain queued rather than being dragged into this packet.

### `ROADMAP.md`

Rechecked before implementation:

- M2-M0.5 explicitly continues receipts/assets/inventory after the first no-app verticals;
- packets remain bounded and must not collapse the entire asset/inventory stack into one implementation;
- Android remains paused while meaningful no-app vertical coverage grows.

### Direction result

**ALIGNED.** Receipt truth is now merged and the smallest high-value downstream slice is immutable physical asset acquisition. This unlocks later identifiers, fitment and inventory without coupling them into the same packet.

## Required user-visible/canonical behavior

1. A new physical asset receives one RFC 4122 UUID that never changes.
2. Receipt-linked acquisition requires an existing canonical receipt and, when specified, an existing canonical receipt line.
3. Acquisition source identity is explicit and stable so exact replay returns the same asset without a second write/UUID.
4. `individual` tracking always has quantity `1`.
5. `lot` tracking may have positive quantity greater than or equal to one and remains one intentionally grouped asset identity.
6. Multiple physical units that need individual identity require separate acquisitions/UUIDs rather than a quantity>1 individual asset.
7. Compatible enrichment such as a better display name or note updates the same UUID through a new revision; it never reallocates identity.
8. Conflicting replay/source identity or source-to-two-assets collision fails closed.
9. Receipt correction never changes an already-created asset UUID.
10. Asset identity remains independent of fitment, serial/UPC/model identifiers, location, project/backend and later inventory projection.
11. Asset acquisition alone does not imply installed-on/assigned-to relationships, inventory location, warranty/maintenance state, or provider-side Drive filing.

## Acceptance criteria

1. Provider-neutral `AssetService` over STORE-001 with create/read/enrich/query semantics.
2. Canonical asset resource ID is a normalized RFC 4122 UUID and equals payload Entity UUID.
3. Source acquisition identity is persisted and globally unique within asset state; exact replay is zero-write.
4. Receipt and optional receipt-line provenance are validated against canonical receipt state before creation.
5. Tracking/quantity rules enforce individual=1 and bounded positive lot quantity.
6. Source replay cannot replace UUID or silently change conflicting acquisition facts.
7. Enrichment changes attributes only and preserves acquisition provenance/UUID.
8. Direct tests cover UUID validation/allocation, replay, source collision, missing receipt/line, quantity modes, enrichment, receipt correction stability and no fitment/location side effects.
9. Personal Google starter adds `asset` data class plus `binding-asset` without replacing the existing receipt authority.
10. Complete no-app instructions define immutable asset identity/acquisition and the downstream no-side-effect boundary.
11. Personal distribution/Workspace validation and code ownership cover the new contract.
12. Exact PR-head CI green.
13. Fresh isolated Google provider proof creates/read-backs receipt + asset authority/bindings + one synthetic acquisition and same-source replay/enrichment while retaining one UUID.
14. End-of-session FEATURES/BACKLOG/ROADMAP reconciliation preserves the larger asset/inventory stack.

## Exact next action

1. Implement `mira/assets.py` and direct tests.
2. Extend the Personal starter/no-app contract/ownership for `asset` and `binding-asset`.
3. Run CI and fix only evidence-backed failures.
4. Perform a fresh synthetic Google provider proof; do not reuse legacy production or the prior receipt-proof artifact.
5. Freeze closeout, run exact-head CI, merge with expected-head protection, verify `main`, then rank the next bounded vertical.

## Recovery protocol

Read this file first. Continue only on `integration/m0-013-asset-acquisition` from the recorded base. Do not broaden into fitment, identifiers, warranty/maintenance, location, movement, inventory query or provider archival unless a concrete acceptance dependency proves unavoidable.
