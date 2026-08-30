# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and exact recovery state.

## Product direction

Default Personal MIRA is stock ChatGPT + Google Workspace with no external infrastructure prerequisite. Completed work remains durable with evidence and is filtered from future selection rather than deleted. Current priority is repeated useful no-app verticals before Android resumes.

Every work session begins and ends by checking `CURRENT_WORK.md`, `FEATURES.md`, `BACKLOG.md`, and `ROADMAP.md`.

## Completed predecessor

### `M2-M0-013` — Canonical receipt-linked asset acquisition

PR #65 merged to `main` at `36645003e885b6562bb5c7ceeec4430838e148d8` after exact-head CI `33298434246` passed and isolated Google receipt-to-asset readback was verified. The later `main` head `7d4fed8105982f2fe00f9d226da232c321705a7c` contains only an accidental temporary-file add/delete pair and has zero file differences from that verified merge tree.

## Active packet

### `M2-M0-014` — Namespaced asset identifiers + lookup

- **Primary work:** `ASSET-IDENTIFIER-001`
- **Primary features:** `IDENT-001`, `ASSET-003`
- **Related invariants/features:** `ASSET-001`, `EVID-001`, `FITMENT-001`, `INV-001`, `MOVE-001`, `INV-002`, `STORE-001`, `RECOVERY-002`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `integration/m0-014-asset-identifiers`
- **Base SHA:** `7d4fed8105982f2fe00f9d226da232c321705a7c`
- **PR:** #66
- **Implementation/release head with green CI:** `ba05f25a4389a22c0035205a019b5677fd441b2a`
- **CI:** run `33299034811` green on that head
- **Provider-proof documentation commit:** `545bf8bdd7a08b2aded1eef392b98c86e5d49def`
- **Objective:** attach validated namespaced product/device identifiers to already-existing immutable asset UUIDs and provide deterministic identifier-to-asset lookup without changing asset identity. OCR/photo acquisition, fitment inference, location/movement, inventory scanning and Android capture remain outside this packet.

## Session-start alignment verification — 2026-08-29/30

### `FEATURES.md`

Verified before implementation:

- `IDENT-001` requires exact printed identifier values plus deterministic normalized search values for UPC/EAN/GTIN, merchant/vendor SKU, manufacturer part number, model number, serial number, IMEI and MAC;
- UPC/GTIN leading zeroes and check digits are significant;
- IMEI requires Luhn validation and MAC requires deterministic normalization/validation;
- merchant SKU, manufacturer part/model and serial identifiers require an explicit namespace;
- serial-level identifiers may not resolve to two different Entity UUIDs under the same canonical type/namespace/value;
- `IDENT-001` depends on immutable `ASSET-001` identity, while fitment/movement/inventory consume identifiers without redefining asset identity.

### `BACKLOG.md`

Verified before implementation:

- `ASSET-ACQUISITION-001` is completed by PR #65;
- `ASSET-IDENTIFIER-001` is the one bounded active work item;
- `FITMENT-ENGINE-001`, `LOCATION-STATE-001`, `MOVEMENT-CORE-001`, `INVENTORY-QUERY-001`, `ASSET-SERVICE-001`, evidence/OCR work and Android scanning remain separate unfinished work.

### `ROADMAP.md`

Verified before implementation:

- M2-M0.5 explicitly continues useful receipts/assets/inventory and other no-app feature families before Android;
- packets must remain bounded rather than collapsing the asset/inventory stack into one implementation;
- identifiers are a high-leverage dependency for fitment, scanning/movement and richer graph lookup while remaining usable on the stock ChatGPT + Google Workspace substrate.

### Direction result

**ALIGNED.** Stable namespaced identifiers are the smallest foundational slice after immutable asset acquisition that unlocks multiple accepted downstream capabilities without prematurely coupling fitment, movement, OCR or Android.

## Implemented evidence

### Canonical identifier service

`mira/identifiers.py` implements provider-neutral `identifier` schema version 1 over `STORE-001`:

- identifiers attach only to an existing canonical asset Entity UUID;
- supported types: `gtin8`, `upc_a`, `ean13`, `gtin14`, `merchant_sku`, `manufacturer_part_number`, `model_number`, `serial_number`, `imei`, `mac`;
- exact source/printed value is retained separately from deterministic normalized search value;
- GTIN-8 / UPC-A / EAN-13 / GTIN-14 enforce exact digit length and modulo-10 check digit while preserving leading zeroes;
- IMEI requires 15 digits plus Luhn validation;
- MAC accepts compact, colon, hyphen or Cisco-dot forms and normalizes to uppercase 12-hex search form;
- merchant SKU, manufacturer part/model and serial types require explicit namespace with deterministic namespace-key normalization;
- deterministic identifier Resource ID derives from identifier type + normalized namespace + normalized value + immutable Entity UUID;
- product/model identifiers may attach to multiple assets;
- `serial_number`, `imei` and `mac` fail closed when the same canonical identifier is already attached to another Entity UUID;
- same-asset exact replay is zero-write;
- `observed` may upgrade to `verified` on the same identifier identity/revision chain;
- conflicting replay cannot silently replace exact source value, namespace or note;
- `lookup_assets` resolves identifier matches back through canonical `asset` Resources, not a shadow asset database.

Identifier attachment has no fitment, location, movement, inventory, warranty, specification, OCR or Android side effects.

### Direct tests

`tests/test_identifiers.py` covers:

- valid and invalid GTIN/UPC/EAN check digits;
- leading-zero preservation;
- required namespace behavior;
- same-asset replay and verification upgrade;
- product-level identifier reuse across assets;
- serial-level collision rejection;
- IMEI and MAC validation/normalization;
- missing asset rejection;
- deterministic lookup back to canonical assets;
- downstream side-effect isolation.

### Personal release wiring

The Git-backed Personal starter now includes `identifier` in `resource_types_json`.

The complete no-app operating instructions now include:

- `authority_binding/binding-identifier`;
- exact identifier/source-value and normalized-value semantics;
- GTIN/UPC/EAN, IMEI and MAC validation requirements;
- required local identifier namespaces;
- serial-level collision safety;
- identifier-origin canonical asset lookup;
- explicit no-side-effect boundaries for fitment, movement, inventory, OCR and Android.

`mira.personal_distribution`, `mira.workspace_bundle`, direct release tests and `project/code_ownership.json` enforce the identifier-inclusive contract. The `canonical-identifiers` component owns `mira/identifiers.py` with `tests/test_identifiers.py` as direct evidence.

## CI evidence

PR #66 CI run `33299034811` passed on implementation/release head `ba05f25a4389a22c0035205a019b5677fd441b2a`, including compile, feature registry, product lifecycle ledger, Personal starter distribution, work-session alignment, code ownership, Python unit tests and Workspace Apps Script tests.

Provider-proof documentation and this closeout checkpoint are later commits, so exact current-head CI is still required before merge.

## Independent Google provider proof — 2026-08-30

A brand-new native Google Sheet was created only for this packet and placed in the ChatGPT Drive folder. It did not copy or touch protected legacy MIRA production state. Provider file ID and authenticated-account details are intentionally excluded from public Git. After verification the Sheet was renamed to include `NOT A STARTER`.

### Clean substrate

Exact Google readback before mutable proof state confirmed:

- timezone `Etc/UTC`;
- tabs exactly `Metadata`, `Resources`, `Events`, `Idempotency`;
- `mira-structured-state-v1` / `STORE-001` / `single_writer`;
- identifier-inclusive resource-type list matching this branch;
- exact STORE-001 headers;
- zero inherited mutable rows.

### Authority and asset prerequisite

Exact readback then confirmed:

- one enabled/verified synthetic `authority/google-sheets-personal`;
- `binding-asset` -> `asset`;
- `binding-identifier` -> `identifier`;
- one immutable canonical synthetic asset Resource at Entity UUID `44444444-4444-4444-8444-444444444444`;
- exact matching request hashes, revisions, idempotency results and resource references.

Identifier writes did not mutate the asset UUID, quantity or acquisition provenance.

### Product identifier

A representative UPC-A was persisted/read back at revision 1:

- exact source value `012345678905`;
- normalized value `012345678905` with leading zero intact;
- verification `verified`;
- deterministic Resource ID `identifier-4a3fea47273b551395b9d7d69cd96069`;
- linked to the same immutable asset UUID;
- exact request/idempotency evidence retained.

### Serial identifier revision chain

A representative namespaced serial was first persisted/read back at revision 1:

- namespace `Synthetic Maker` / namespace key `synthetic maker`;
- exact value `SN-0001` / normalized value `sn-0001`;
- verification `observed`;
- deterministic Resource ID `identifier-6572064aab78f06be89e1801827fca6a`;
- same immutable asset UUID.

A second canonical mutation changed only verification state to `verified`.

Revision-2 readback confirmed the same Resource ID, Entity UUID, type, namespace, namespace key, exact source value, normalized value and note, with revision exactly `2` and both Idempotency rows retained.

### Identifier-origin asset lookup

A bounded provider search for `012345678905` returned exactly the canonical UPC identifier. Its persisted Entity UUID was then used for a bounded provider search that returned the canonical `asset` Resource and both linked identifier Resources. This demonstrates identifier-origin lookup over one canonical asset authority rather than a second asset database.

Durable non-sensitive proof: `docs/NO_APP_IDENTIFIER_PROVIDER_PROOF.md`.

## End-of-session alignment verification — 2026-08-30

### `FEATURES.md`

Rechecked after implementation/provider proof. `IDENT-001` and the identifier-origin lookup slice of `ASSET-003` are directly implemented/tested/provider-persisted. `FITMENT-001`, `EVID-001`, `INV-001`, `LOC-001`, `MOVE-001`, `INV-002`, OCR/photo capture, warranty/maintenance, specifications and Android capture remain explicitly unfinished/preserved.

### `BACKLOG.md`

Rechecked after implementation/provider proof. `ASSET-IDENTIFIER-001` correctly remains `active` until PR #66 actually merges. `FITMENT-ENGINE-001`, `LOCATION-STATE-001`, `MOVEMENT-CORE-001`, `INVENTORY-QUERY-001`, `ASSET-SERVICE-001`, evidence/OCR work and Android work remain unfinished.

### `ROADMAP.md`

Rechecked after implementation/provider proof. This packet advances the M2-M0.5 receipts/assets/inventory direction without adding external infrastructure and keeps Android paused at its preserved shared-writer checkpoint.

### Direction result

**ALIGNED.** Canonical identifier persistence, validation and identifier-origin asset lookup are technically and provider verified. Merge is the only remaining lifecycle gate.

## Acceptance result

1. Provider-neutral `IdentifierService` over STORE-001 — PASS.
2. Schema-v1 deterministic identifier Resource identity + immutable Entity UUID linkage — PASS.
3. GTIN/UPC/EAN, IMEI, MAC and local identifier validation/normalization — PASS.
4. Exact source value separate from normalized value; leading zeroes preserved — PASS.
5. Explicit namespace requirements — PASS.
6. Serial-level collision safety — PASS.
7. Product-level multi-asset reuse — PASS.
8. Stable zero-write replay + fail-closed conflicting replay — PASS.
9. Identifier-origin lookup returns canonical assets — PASS.
10. Direct validation/replay/collision/lookup/side-effect tests — PASS.
11. Personal starter `identifier` + `binding-identifier` contract — PASS.
12. Complete no-app identifier contract — PASS.
13. Distribution/Workspace validation + code ownership — PASS.
14. CI green on implementation head — PASS; exact closeout-head CI PENDING.
15. Fresh isolated Google asset + product identifier + serial revision/lookup proof — PASS.
16. End-of-session whole-product reconciliation — PASS.

## Exact next action

1. Run CI on the exact current PR #66 closeout head containing this checkpoint.
2. If every gate is green, merge PR #66 using expected-head SHA protection.
3. Remotely verify `main` at the returned merge SHA.
4. Create exactly one next bounded packet from verified `main`; in that packet reconcile `ASSET-IDENTIFIER-001` to completed with PR #66 evidence.
5. Dependency-rank the next no-app vertical from the canonical unfinished ledger. Likely candidates now unlocked include fitment and inventory/location foundations, but select from Git based on leverage and bounded user-visible value rather than conversational momentum.
6. Keep Android paused unless explicitly reprioritized or no-app milestone evidence justifies resumption.

## Recovery protocol

Read this file first. If PR #66 is open, verify its exact current head and exact-head CI before merge. If merged, verify `main`, reconcile `ASSET-IDENTIFIER-001` to completed, then activate exactly one next bounded packet. Never touch protected legacy asset/inventory state and never broaden identifier attachment into fitment/location/movement/OCR/Android by inference.
