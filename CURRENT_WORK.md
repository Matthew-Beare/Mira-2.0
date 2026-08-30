# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and exact recovery state.

## Product direction

Default Personal MIRA is stock ChatGPT + Google Workspace with no external infrastructure prerequisite. Completed work stays durable with evidence and is filtered from future selection rather than deleted. Current priority is repeated useful no-app verticals before Android resumes.

Every work session begins and ends by checking `CURRENT_WORK.md`, `FEATURES.md`, `BACKLOG.md`, and `ROADMAP.md`.

## Completed predecessor

### `M2-M0-013` — Canonical receipt-linked asset acquisition

PR #65 merged to `main` at `36645003e885b6562bb5c7ceeec4430838e148d8` after exact-head CI `33298434246` passed and isolated Google receipt-to-asset revision-1/replay-boundary/revision-2 readback was verified. `ASSET-ACQUISITION-001` is reconciled completed in `BACKLOG.md` on this branch.

After the merge, an accidental one-word temporary placeholder was created and immediately deleted on `main`. Clean-up head `7d4fed8105982f2fe00f9d226da232c321705a7c` compares against the asset merge with zero file differences, so this packet starts from an identical product tree with that later Git history head.

## Active packet

### `M2-M0-014` — Namespaced asset identifiers + lookup

- **Primary work:** `ASSET-IDENTIFIER-001`
- **Primary features:** `IDENT-001`, `ASSET-003`
- **Related invariants/features:** `ASSET-001`, `EVID-001`, `FITMENT-001`, `INV-001`, `MOVE-001`, `INV-002`, `STORE-001`, `RECOVERY-002`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `integration/m0-014-asset-identifiers`
- **Base SHA:** `7d4fed8105982f2fe00f9d226da232c321705a7c`
- **Objective:** attach validated namespaced product/device identifiers to already-existing immutable asset UUIDs and provide deterministic identifier-to-asset lookup without changing asset identity. This packet stops before OCR/photo acquisition, automatic fitment, location/movement, inventory scanning, and Android capture.

## Session-start alignment verification — 2026-08-29/30

### `FEATURES.md`

Rechecked before implementation:

- `IDENT-001` requires exact printed identifier values plus deterministic normalized search values for UPC-A/EAN/GTIN variants, merchant/vendor SKU, manufacturer part number, model number, serial number, IMEI, and MAC;
- UPC/GTIN leading zeroes must be retained and check digits validated;
- IMEI requires Luhn validation; MAC requires deterministic format normalization/validation;
- merchant SKU, manufacturer part/model, and serial identifiers require an explicit namespace so local numeric-looking values are never mislabeled as global barcodes;
- serial-level identifiers such as serial number, IMEI, and MAC cannot resolve to two different Entity UUIDs under the same canonical namespace/value;
- `IDENT-001` depends on already-merged immutable `ASSET-001` identity;
- `ASSET-003` requires identifier-origin queries to reach the same connected assets later, while `FITMENT-001`, `MOVE-001`, and `INV-002` consume identifier truth without redefining it.

Historical PR #10 identifier audit was also re-read. The older deterministic core had evidence for GTIN/UPC check digits/leading zeroes, IMEI/MAC validation, explicit namespace requirements, serial-level collision rejection, and immutable identifier/source identity, but no current executable identifier module survived in the MIRA 2.0 tree. This packet implements those semantics cleanly over the current STORE-001 substrate rather than importing a legacy subsystem wholesale.

### `BACKLOG.md`

Rechecked and reconciled before implementation:

- `ASSET-ACQUISITION-001` is completed by PR #65;
- new stable work item `ASSET-IDENTIFIER-001` is the one active packet;
- `FITMENT-ENGINE-001`, `MOVEMENT-CORE-001`, `INVENTORY-QUERY-001`, `LOCATION-STATE-001`, `ASSET-SERVICE-001`, evidence/OCR work, and Android scanning remain separate unfinished work;
- Android remains partial/paused at the isolated Google queued-writer proof checkpoint.

### `ROADMAP.md`

Rechecked before implementation:

- M2-M0.5 explicitly continues receipts/assets/inventory and other useful no-app feature families before Android;
- repeated bounded verticals are required rather than one giant asset/inventory implementation;
- identifiers have architectural leverage because fitment, scanning/movement, and richer graph lookup depend on them, while still being implementable with stock ChatGPT + Google Workspace.

### Direction result

**ALIGNED.** Stable identifiers are the smallest foundational slice after asset acquisition that unlocks several accepted downstream features without prematurely coupling fitment, movement, OCR, or Android.

## Canonical identifier design decisions

### Separate identifier records, same physical identity

Identifiers are canonical `identifier` resources linked to an existing `asset` Entity UUID. They are not embedded as a new asset identity and cannot replace the RFC 4122 UUID.

One physical asset may have many identifier records. Product-level identifiers such as GTIN, manufacturer part number, model number, or merchant SKU may legitimately attach to multiple physical asset UUIDs. Serial-level identifiers are collision-protected across assets.

### Identifier types

This packet supports:

- `gtin8`
- `upc_a` (12-digit GTIN/UPC-A)
- `ean13`
- `gtin14`
- `merchant_sku`
- `manufacturer_part_number`
- `model_number`
- `serial_number`
- `imei`
- `mac`

Global barcode/device types do not accept an invented local namespace. Local/issuer-scoped types (`merchant_sku`, `manufacturer_part_number`, `model_number`, `serial_number`) require an explicit nonblank namespace describing the merchant/manufacturer/issuer context.

### Exact source value and normalized search value

Each identifier retains the trimmed exact source/printed value supplied to MIRA and a deterministic normalized value used for identity/search.

- GTIN/UPC/EAN normalized form is the exact digits, including leading zeroes.
- IMEI normalized form is the 15 digits.
- MAC normalized form is 12 uppercase hexadecimal digits independent of accepted colon/hyphen/dot presentation.
- namespaced local identifiers normalize Unicode compatibility form, trim/collapse whitespace, and case-fold for deterministic lookup while retaining the exact source value separately.
- namespace identity uses the same conservative compatibility/whitespace/case-fold normalization while retaining the display namespace.

A later observation that normalizes to an existing identifier for the same asset is a replay only when it does not contradict the stored exact/source semantics. This packet does not silently rewrite an established printed value merely because another formatting variant appears.

### Stable identifier resource identity

The identifier Resource ID is deterministic from:

`identifier_type + normalized namespace + normalized identifier value + Entity UUID`

This permits non-unique product identifiers to link to multiple assets while making exact same-asset replay stable. The payload's `identifier_id` must equal the Resource ID.

### Collision policy

`serial_number`, `imei`, and `mac` are serial-level identifiers. Before mutation, MIRA searches canonical identifier state for the same type + normalized namespace + normalized value. If it is already attached to a different Entity UUID, fail closed rather than reassigning or duplicating it.

Product/model identifiers may resolve to multiple assets and therefore are not globally unique asset identities.

### Validation

- GTIN-8, UPC-A/GTIN-12, EAN-13/GTIN-13, and GTIN-14 must contain only the exact required number of digits and pass the standard GTIN modulo-10 check digit.
- IMEI must contain exactly 15 digits and pass Luhn validation.
- MAC accepts ordinary colon, hyphen, compact, or Cisco-dot presentation only when it resolves to exactly 12 hexadecimal digits; normalized search form is uppercase compact hex.
- namespaced local identifiers reject blank value or blank namespace.

### Explicit side-effect boundary

Adding an identifier does not:

- create an asset;
- change the asset UUID, quantity, receipt provenance, or acquisition state;
- infer `assigned_to`, `installed_on`, or fitment;
- move/place inventory;
- create barcode/QR movement events;
- claim OCR/photo extraction quality;
- create warranty/maintenance/specification state;
- activate Android scanning.

## Required user-visible/canonical behavior

1. MIRA can attach a validated identifier to an existing asset UUID.
2. Exact same identifier/asset replay returns the same identifier record without duplicate canonical state.
3. Invalid GTIN/UPC/EAN, IMEI, or MAC values fail closed.
4. Leading zeroes in global trade identifiers are preserved.
5. Namespaced local identifiers cannot be recorded without an explicit namespace.
6. The same product/model identifier may legitimately return multiple assets.
7. The same serial number (within namespace), IMEI, or MAC cannot attach to two different assets.
8. Query by type/value/namespace returns deterministic identifier records and their exact Entity UUIDs.
9. Identifier-origin asset lookup returns canonical asset Resources rather than a shadow asset database.
10. Identifier attachment never silently causes fitment, installation, location, movement, inventory, warranty, or provider-side side effects.

## Acceptance criteria

1. Provider-neutral `IdentifierService` over STORE-001 with attach/read/query/asset-lookup semantics.
2. `identifier` schema version 1 with deterministic stable Resource ID and exact `entity_uuid` linkage.
3. Validation/normalization for GTIN-8, UPC-A, EAN-13, GTIN-14, IMEI, MAC, and namespaced local identifier types.
4. Exact source value retained separately from normalized search value; GTIN leading zeroes preserved.
5. Required namespace enforcement for merchant SKU/manufacturer part/model/serial types.
6. Serial-level collision checks prevent serial/IMEI/MAC reuse across Entity UUIDs.
7. Product-level identifiers may link to multiple assets without false collision.
8. Same-asset replay is zero-write and stable; conflicting replay fails closed.
9. Identifier-origin asset lookup reads canonical `asset` Resources.
10. Direct tests cover valid/invalid check digits, leading zeroes, namespace requirements, replay, product multi-asset reuse, serial collision, MAC/IMEI normalization, missing asset, and side-effect isolation.
11. Personal starter adds `identifier` plus `binding-identifier` without changing the existing asset authority.
12. Complete no-app instructions define identifier validation/collision/lookup and no-side-effect boundaries.
13. Distribution/Workspace validation and code ownership cover the identifier contract.
14. Exact PR-head CI green.
15. Fresh isolated Google proof persists one asset plus representative product and serial-level identifiers and exact identifier-to-asset readback without touching legacy production.
16. End-of-session FEATURES/BACKLOG/ROADMAP reconciliation preserves fitment, inventory, movement, evidence/OCR, Android, and other accepted scope.

## Exact next action

1. Implement `mira/identifiers.py` and direct tests.
2. Expand the Personal starter/no-app authority contract for `identifier` / `binding-identifier`.
3. Add release validation and code ownership.
4. Run CI and fix evidence-backed failures.
5. Perform a fresh isolated Google identifier/provider readback proof.
6. Freeze closeout, run exact-head CI, merge only when green, then select one next bounded packet from verified `main`.

## Recovery protocol

Read this file first. Continue only on `integration/m0-014-asset-identifiers`. Do not broaden into fitment inference, location/movement, QR workflows, OCR/photo evidence acquisition, inventory projection, or Android while this bounded identifier packet is unfinished.
