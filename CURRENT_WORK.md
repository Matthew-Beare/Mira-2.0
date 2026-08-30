# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and exact recovery state.

## Product direction

Default Personal MIRA is stock ChatGPT + Google Workspace with no external infrastructure prerequisite. Completed work remains durable with evidence and is filtered from future selection rather than deleted. Current priority is repeated useful no-app verticals before Android resumes.

Every work session begins and ends by checking `CURRENT_WORK.md`, `FEATURES.md`, `BACKLOG.md`, and `ROADMAP.md`.

## Completed predecessor

### `M2-M0-014` — Namespaced asset identifiers + lookup

PR #66 merged to `main` at `6833d27e20d746d37e389b1756a6f6147225d043` after exact-head CI `33300160170` passed and isolated Google identifier persistence, observed-to-verified revision, leading-zero UPC and identifier-to-canonical-asset readback were verified. `BACKLOG.md` in this packet reconciles `ASSET-IDENTIFIER-001` as completed with that evidence.

## Active packet

### `M2-M0-015` — Canonical inventory participation + intended/observed location

- **Primary work:** `LOCATION-STATE-001`
- **Primary features:** `INV-001`, base slice of `LOC-001`
- **Related preserved features:** `MOVE-001`, `INV-002`, `PAR-001`, `GROCERY-001`, `ASSET-001`, `IDENT-001`, `ASSET-003`, `STORE-001`, `RECOVERY-002`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `integration/m0-015-inventory-location`
- **Base SHA:** `6833d27e20d746d37e389b1756a6f6147225d043`
- **PR:** #67
- **Implementation/release head with green CI:** `b15a7305863c91f8429b0b1bfcca87047be476a5`
- **CI:** run `33300802923` green on that head
- **Provider-proof documentation commit:** `08b6e41e1f5a55920536aa25272d683ea76ec628`
- **Objective:** expose an existing immutable asset Entity UUID as tracked inventory, model stable hierarchical physical locations, and persist intended-home placement separately from latest supported observed location. Movement-event history, QR/barcode scan-in/out, movable-container-following movement, broad inventory search/projection, par/grocery, fitment, OCR and Android capture remain outside this packet.

## Session-start alignment verification — 2026-08-30

### `FEATURES.md`

Verified before implementation:

- `INV-001` requires inventory to reuse canonical physical Entity UUID identity rather than allocate a second physical/inventory identity;
- `LOC-001` requires hierarchical locations, cycle protection and intended placement separate from current/last-observed state;
- changing observed state must not silently rewrite intended placement;
- changing intended placement must not fabricate a physical observation;
- movable-container-following movement belongs to broader location/movement behavior and is not silently claimed by this bounded base-state packet.

### `BACKLOG.md`

Verified before implementation:

- PR #66 was merged and `ASSET-IDENTIFIER-001` required completion reconciliation;
- `LOCATION-STATE-001` was the existing prerequisite for intended-versus-observed hierarchical location state;
- `MOVEMENT-CORE-001` and `INVENTORY-QUERY-001` remain downstream unfinished work;
- `LOCATION-STATE-001` is the sole active work item in this packet.

### `ROADMAP.md`

Verified before implementation:

- M2-M0.5 continues useful receipts/assets/inventory capability in stock ChatGPT before Android resumes;
- packets remain bounded rather than collapsing the inventory stack into one subsystem;
- Android remains paused at its stronger shared-writer checkpoint.

### Direction result

**ALIGNED.** Minimal inventory participation plus independent intended/observed location state is the smallest useful prerequisite for later movement/scanning and queryable inventory.

## Implemented evidence

### Provider-neutral inventory/location core

`mira/inventory_location.py` implements:

- canonical `location` resources, schema version 1;
- canonical `inventory_state` resources, schema version 1;
- inventory Resource ID equal exactly to the existing asset Entity UUID;
- no allocation of a second physical/inventory UUID;
- stable location IDs with display name, bounded kind, optional parent and optional note;
- parent existence checks, self-parent rejection, ancestor-cycle rejection and bounded hierarchy traversal;
- location update/reparent without changing location identity;
- inventory tracking only for an existing canonical asset;
- independent `intended_location_id` and `observed_location_id` fields;
- offset-aware `observed_at` required whenever observed location is set;
- intended-state mutation preserves observation state/time;
- observed-state mutation preserves intended placement;
- clearing one state does not erase the other;
- persisted asset/location reference validation and fail-closed integrity errors;
- no fitment, movement-event, scanner, par/grocery, warranty, OCR or Android side effects.

### Direct tests

`tests/test_inventory_location.py` covers:

- same Entity UUID through asset and inventory state;
- missing asset/location rejection;
- stable hierarchy and nested parents;
- self-parent and ancestor-cycle rejection;
- intended-versus-observed independence;
- offset-aware observation time validation;
- independent clearing behavior;
- persisted missing/corrupt reference failure;
- asset side-effect isolation.

### Personal release wiring

The Personal starter and release verifier now include `inventory_state` and `location`.

The complete no-app instructions now include:

- `binding-location` and `binding-inventory-state`;
- inventory identity reuse over canonical asset Entity UUID;
- hierarchical location state;
- explicit distinction between “where it belongs” and “where it was last observed”;
- observation timestamp truth;
- explicit prohibition on treating a location-state update as movement history or scanner evidence.

`mira.workspace_bundle`, `mira.personal_distribution`, direct release tests and `project/code_ownership.json` enforce the new contract. The `inventory-location` component owns `mira/inventory_location.py` with `tests/test_inventory_location.py` as direct evidence.

## CI evidence

PR #67 CI run `33300802923` passed on implementation/release head `b15a7305863c91f8429b0b1bfcca87047be476a5`, including compile, feature registry, product lifecycle ledger, Personal starter distribution, work-session alignment, code ownership, Python unit tests and Workspace Apps Script tests.

Provider-proof documentation and this closeout checkpoint are later commits, so exact current-head CI remains required before merge.

## Independent Google provider proof — 2026-08-30

A brand-new native Google Sheet was created only for this packet. It did not copy or touch protected legacy MIRA production state. Provider file ID and authenticated-account details are intentionally excluded from public Git. After verification, the Sheet was renamed to include `NOT A STARTER`.

### Clean substrate

Exact provider readback before mutable proof state confirmed:

- timezone `Etc/UTC`;
- tabs exactly `Metadata`, `Resources`, `Events`, `Idempotency`;
- `mira-structured-state-v1` / `STORE-001` / `single_writer`;
- resource types include `inventory_state` and `location`;
- exact STORE-001 headers;
- zero inherited mutable Resources.

### Authority and asset prerequisite

Exact readback confirmed:

- one enabled/verified synthetic `authority/google-sheets-personal`;
- `binding-asset` -> `asset`;
- `binding-location` -> `location`;
- `binding-inventory-state` -> `inventory_state`;
- one immutable synthetic asset Resource at Entity UUID `55555555-5555-4555-8555-555555555555`.

The asset remained revision 1 throughout inventory/location mutations.

### Hierarchy persistence

Four stable locations persisted/read back at revision 1:

- synthetic shop root;
- Shelf A under the shop;
- Shelf B under the shop;
- Workbench under the shop.

Negative hierarchy fixtures remain direct-test evidence rather than being fabricated as live-provider execution.

### Intended/observed revision chain

Inventory revision 1:

- Resource ID = same asset Entity UUID;
- intended home = Shelf A;
- observed location/time = null.

Inventory revision 2 recorded only a supported observation:

- observed location = Workbench;
- observed timestamp = `2026-08-30T12:45:00-06:00`;
- intended home remained Shelf A.

Inventory revision 3 changed only intended placement:

- intended home = Shelf B;
- observed location remained Workbench;
- the exact original observed timestamp remained unchanged.

Provider readback retained all three inventory idempotency records and request hashes. A bounded search by Entity UUID returned exactly the canonical `asset` and `inventory_state` rows, both keyed by the same physical Entity UUID.

Durable non-sensitive proof: `docs/NO_APP_INVENTORY_LOCATION_PROVIDER_PROOF.md`.

## End-of-session alignment verification — 2026-08-30

### `FEATURES.md`

Rechecked after implementation/provider proof. `INV-001` identity reuse is directly implemented/tested/provider-persisted. The bounded base-state portion of `LOC-001` covering hierarchy plus intended/observed separation is directly implemented/tested/provider-persisted. Broader movable-container-following movement semantics are not claimed complete and remain with later movement work.

### `BACKLOG.md`

Rechecked after implementation/provider proof. `LOCATION-STATE-001` correctly remains active until PR #67 actually merges. `MOVEMENT-CORE-001`, `INVENTORY-QUERY-001`, `PAR-CORE-001`, `GROCERY-CORE-001`, fitment, OCR/evidence and Android work remain unfinished.

### `ROADMAP.md`

Rechecked after implementation/provider proof. This packet advances the no-app assets/inventory/location family without requiring external infrastructure and keeps Android paused.

### Direction result

**ALIGNED.** The bounded prerequisite is implemented and provider-verified without overstating movement/scanning/container-following or broad inventory capability.

## Acceptance result

1. Provider-neutral inventory/location service over STORE-001 — PASS.
2. `inventory_state` Resource ID equals canonical asset Entity UUID — PASS.
3. Unknown asset fails closed / no second physical identity — PASS.
4. Stable hierarchical locations — PASS.
5. Parent existence, self/cycle protection — PASS.
6. Intended and observed state mutate independently — PASS.
7. Offset-aware observed timestamp semantics — PASS.
8. Canonical referenced-location validation — PASS.
9. Direct identity/hierarchy/separation/clearing/side-effect tests — PASS.
10. Personal starter `location` + `inventory_state` bindings — PASS.
11. Complete no-app inventory/location base contract — PASS.
12. Distribution/Workspace validation + code ownership — PASS.
13. CI green on implementation/release head — PASS; exact closeout-head CI PENDING.
14. Fresh isolated Google intended-versus-observed provider proof — PASS.
15. End-of-session whole-product reconciliation — PASS.

## Exact next action

1. Run CI on the exact current PR #67 closeout head containing this checkpoint.
2. If every gate is green, merge PR #67 using expected-head SHA protection.
3. Remotely verify `main` at the returned merge SHA.
4. Create exactly one next bounded packet from verified `main`; in that packet reconcile `LOCATION-STATE-001` to completed with PR #67 evidence.
5. Dependency-rank the next no-app vertical from the canonical unfinished ledger. `MOVEMENT-CORE-001` is newly unblocked by this packet, but it must compete on leverage/value with other queued work rather than being selected merely by conversational momentum.
6. Keep broader `LOC-001` movable-container/movement semantics unfinished unless their own work earns direct/provider evidence.
7. Keep Android paused unless explicitly reprioritized or no-app milestone evidence justifies resumption.

## Recovery protocol

Read this file first. If PR #67 is open, verify its exact current head and exact-head CI before merge. If merged, verify `main`, reconcile `LOCATION-STATE-001` to completed, then activate exactly one next bounded packet. Never touch protected legacy inventory/location state and never broaden location state into movement-event history, scanning, par/grocery, fitment, OCR or Android by inference.