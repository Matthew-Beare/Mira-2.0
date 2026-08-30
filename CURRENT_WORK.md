# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and exact recovery state.

## Product direction

Default Personal MIRA is stock ChatGPT + Google Workspace with no external infrastructure prerequisite. Completed work remains durable with evidence and is filtered from future selection rather than deleted. Current priority is repeated useful no-app verticals before Android resumes.

Every work session begins and ends by checking `CURRENT_WORK.md`, `FEATURES.md`, `BACKLOG.md`, and `ROADMAP.md`.

## Completed predecessor

`M2-M0-012` / `RECEIPT-INTAKE-001` merged in PR #64 to `main` at `804a664f343934cc813d9cc45b471a6756a15697` after exact-head CI `33284284178` passed.

## Active packet

### `M2-M0-013` — Canonical receipt-linked asset acquisition

- **Primary work:** `ASSET-ACQUISITION-001`
- **Primary features:** `ASSET-001`, `ASSET-002`
- **Related invariants/features:** `FITMENT-001`, `IDENT-001`, `EVID-001`, `ASSET-003`, `INV-001`, `LOC-001`, `MOVE-001`, `INV-002`, `STORE-001`, `RECOVERY-002`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `integration/m0-013-asset-acquisition`
- **Base SHA:** `804a664f343934cc813d9cc45b471a6756a15697`
- **PR:** #65
- **Implementation/release head with full green CI:** `18c9a80a34c8fae87c15a13c5105c339814b95d9`, run `33284755714`
- **Provider-proof documentation commit:** `a9375df89714786c2c28f2bbbb893f6291df3ce3`
- **Objective:** create/read/replay/enrich canonical physical assets from canonical receipt/line provenance while preserving one immutable RFC 4122 Entity UUID. Fitment, identifiers, warranty/maintenance, locations/movement, broad inventory projection, and provider-side archival remain outside this packet.

## Session-start alignment verification — 2026-08-29/30

### `FEATURES.md`

Verified before implementation:

- `ASSET-001` requires immutable RFC 4122 physical identity, idempotent source replay, compatible enrichment without UUID replacement, `individual` quantity=1, optional grouped-lot quantity, and fail-closed excluded purchase evidence.
- `ASSET-002` preserves receipt/evidence acquisition provenance without replacing identity.
- `FITMENT-001`, `IDENT-001`, `EVID-001`, `ASSET-003`, `INV-001`, `LOC-001`, `MOVE-001`, and `INV-002` are separate downstream semantics. `INV-001` later reuses the same Entity UUID.
- Historical PR #10 asset audit was re-read and confirms the same identity/replay/quantity boundaries.

### `BACKLOG.md`

Verified before implementation:

- `RECEIPT-INTAKE-001` is completed by PR #64.
- `ASSET-ACQUISITION-001` is the bounded foundational asset-acquisition work item.
- `FITMENT-ENGINE-001`, `ASSET-SERVICE-001`, `LOCATION-STATE-001`, `MOVEMENT-CORE-001`, `INVENTORY-QUERY-001`, receipt taxonomy, and other downstream work remain separate/unfinished.

### `ROADMAP.md`

Verified before implementation:

- M2-M0.5 explicitly continues receipts/assets/inventory after the first no-app verticals.
- Packets must remain bounded and must not collapse the whole asset/inventory stack into one change.
- Android remains paused while useful no-app coverage grows.

### Direction result

**ALIGNED.** Receipt truth is merged, and immutable receipt-linked asset acquisition is the smallest high-leverage downstream slice before identifiers/fitment/inventory.

## Implemented evidence

`mira/assets.py` now provides `asset` schema version 1 over `STORE-001` with:

- Resource ID equal to canonical RFC 4122 `entity_uuid`;
- canonical receipt and optional receipt-line prerequisite validation;
- deterministic source identity from receipt ID + receipt-line ID + stable acquisition key;
- zero-write exact source replay preserving UUID;
- fail-closed source-to-two-UUID and requested-UUID replacement conflicts;
- `individual` quantity exactly 1 and intentional `lot` grouping;
- receipt-line whole-unit capacity enforcement;
- separate acquisition keys/UUIDs for individually tracked units;
- display-name/note enrichment preserving UUID, quantity, tracking mode, and provenance;
- receipt correction unable to replace asset UUID;
- deterministic query by receipt, receipt line, or display name.

The asset payload contains no fitment, identifier, location, movement, warranty, maintenance, technical-specification, inventory-placement, or Drive-filing state.

`tests/test_assets.py` directly covers UUID validation/allocation, replay, source collision, missing receipt/line, quantity modes, multiple units, over-acquisition, enrichment, receipt correction stability, and downstream side-effect isolation.

The Personal starter now advertises `asset`; complete no-app instructions add `binding-asset`, immutable UUID/acquisition rules, and explicit no-side-effect boundaries. Distribution/Workspace validators and tests enforce the contract. `project/code_ownership.json` includes `canonical-assets` with direct asset tests.

## CI evidence

- PR #65 implementation/release head `18c9a80a34c8fae87c15a13c5105c339814b95d9`: CI `33284755714` fully green.
- Closeout run `33298296777` failed only because this checkpoint omitted the parser-required `Related invariants/features` label.
- Corrected run `33298374616` then failed only because the session-start section heading/subheadings were compressed away from the exact alignment-checker contract.
- Both failed closeout runs passed compile, feature registry, product lifecycle, and Personal distribution before the alignment gate. No product/provider defect was reported.
- This commit restores the exact checker-required heading plus `FEATURES.md` / `BACKLOG.md` / `ROADMAP.md` / Direction result structure. A new exact-head CI run is required before merge.

## Independent Google provider proof — 2026-08-29/30

A brand-new native Google Sheet was created only for this packet, never copied from or written into protected legacy production, and renamed after proof to include `NOT A STARTER`. Provider file ID/account details are excluded from public Git.

Clean readback proved `Etc/UTC`, exact four-tab STORE-001 substrate, asset-inclusive resource types, exact headers, and zero mutable rows.

Synthetic proof then read back exactly:

- one enabled/verified synthetic Personal Google authority;
- `binding-receipt` and `binding-asset` to the same authority;
- one captured synthetic receipt revision 1 with a quantity-2 line;
- one `asset` revision 1 with a single RFC 4122 UUID, `individual` quantity 1, exact receipt/line/revision provenance, stable acquisition key/source identity, and matching request/idempotency evidence;
- no fake provider write for zero-write same-source replay; direct tests prove replay returns the same UUID/revision;
- one permitted enrichment to asset revision 2 changing only display name/note while Resource ID/UUID, source identity, acquisition key, receipt/line/revision provenance, tracking mode, and quantity remained identical;
- both create/enrichment idempotency records retained and still exactly one asset Resource.

Durable non-sensitive proof: `docs/NO_APP_ASSET_PROVIDER_PROOF.md`.

## End-of-session alignment verification — 2026-08-29/30

`FEATURES.md`, `BACKLOG.md`, and `ROADMAP.md` were re-read after implementation/provider proof. `ASSET-001` plus the bounded acquisition slice of `ASSET-002` are implemented/tested/provider-persisted. Fitment, identifiers, evidence enrichment, graph queries, inventory/location/movement, warranty/maintenance, specifications, grocery/meal, appointments, Android, Microsoft, and Apple/iCloud scope remain explicitly unfinished/preserved.

`ASSET-ACQUISITION-001` remains `active` until PR #65 actually merges. It must be changed to completed only in the next packet after merge evidence exists.

## Acceptance result

1. Provider-neutral `AssetService` over STORE-001 — PASS.
2. Canonical RFC 4122 UUID Resource identity — PASS.
3. Stable acquisition source identity + read-only replay — PASS.
4. Canonical receipt/line prerequisite validation — PASS.
5. Individual/lot quantity rules + receipt-line capacity — PASS.
6. Replay cannot replace UUID/conflicting acquisition facts — PASS.
7. Nonidentity enrichment preserves UUID/provenance — PASS.
8. Direct tests — PASS.
9. Personal starter `asset` + `binding-asset` — PASS.
10. Complete no-app immutable asset/no-side-effect contract — PASS.
11. Distribution/Workspace validation + code ownership — PASS.
12. Full CI on implementation head — PASS; exact current-head CI PENDING.
13. Fresh isolated Google revision-1/replay-boundary/revision-2 proof — PASS.
14. Whole-product alignment/preservation — PASS.

## Exact next action

1. Run CI on this exact PR #65 head.
2. If every gate is green, merge #65 with expected-head protection and remotely verify `main`.
3. Create exactly one next bounded packet from verified `main`; first reconcile `ASSET-ACQUISITION-001` to completed with PR #65 evidence.
4. Dependency-rank unfinished work. Stable namespaced identifiers (`IDENT-001`) are the leading expected foundation because they unlock fitment, scanning/movement, and richer asset graph behavior, but Git authorities decide selection.
5. Keep Android paused unless explicitly reprioritized or no-app milestone evidence justifies resumption.

## Recovery protocol

Read this file first. If PR #65 is open, verify its exact head and exact-head CI before merge. If merged, verify `main`, reconcile asset acquisition to completed, then activate exactly one next bounded packet. Never touch protected legacy asset/inventory state or silently broaden this asset acquisition slice.
