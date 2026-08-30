# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and exact recovery state.

## Product direction

Default Personal MIRA is stock ChatGPT + Google Workspace with no external infrastructure prerequisite. Completed work remains durable with evidence and is filtered from future selection rather than deleted. The current priority is repeated useful no-app verticals before Android resumes.

Every work session begins and ends by checking `CURRENT_WORK.md`, `FEATURES.md`, `BACKLOG.md`, and `ROADMAP.md`.

## Completed predecessor

### `M2-M0-012` — Canonical no-app receipt intake + purchase history

Merged in PR #64 to `main` at `804a664f343934cc813d9cc45b471a6756a15697` after exact-head CI `33284284178` passed. `RECEIPT-INTAKE-001` is completed in `BACKLOG.md`.

## Active packet

### `M2-M0-013` — Canonical receipt-linked asset acquisition

- **Primary work:** `ASSET-ACQUISITION-001`
- **Primary features:** `ASSET-001`, `ASSET-002`
- **Related invariants/features:** `FITMENT-001`, `IDENT-001`, `EVID-001`, `ASSET-003`, `INV-001`, `LOC-001`, `MOVE-001`, `INV-002`, `STORE-001`, `RECOVERY-002`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `integration/m0-013-asset-acquisition`
- **Base SHA:** `804a664f343934cc813d9cc45b471a6756a15697`
- **PR:** #65
- **Last implementation/release head with green CI:** `18c9a80a34c8fae87c15a13c5105c339814b95d9`
- **CI:** run `33284755714` green on that head
- **Provider-proof documentation commit before this closeout:** `a9375df89714786c2c28f2bbbb893f6291df3ce3`
- **Objective:** persist one canonical physical asset from canonical receipt/line provenance while preserving an immutable RFC 4122 Entity UUID. This packet proves acquisition identity only and does not absorb fitment, identifiers, warranty/maintenance, location/movement, broad inventory projection, or provider-side archival.

## Session-start alignment result

Before implementation, `FEATURES.md`, `BACKLOG.md`, and `ROADMAP.md` were rechecked.

The packet is aligned because:

- `ASSET-001` requires immutable RFC 4122 physical identity, source-idempotent acquisition, enrichment without UUID replacement, individual quantity=1, optional lot quantity>1, and fail-closed excluded purchase evidence;
- `ASSET-002` preserves receipt/evidence acquisition provenance without replacing physical identity;
- `INV-001` later reuses this same Entity UUID rather than inventing inventory identity;
- `FITMENT-001`, `IDENT-001`, `EVID-001`, `LOC-001`, `MOVE-001`, and `INV-002` remain distinct downstream semantics;
- M2-M0.5 explicitly directs continued receipts/assets/inventory progress while keeping packets bounded;
- Android remains paused at its existing live queued-writer proof checkpoint.

## Implemented evidence

### Canonical Asset service

`mira/assets.py` now implements the bounded asset-acquisition domain over `STORE-001`:

- resource type `asset`, schema version 1;
- canonical Resource ID equals normalized RFC 4122 `entity_uuid`;
- receipt and optional receipt-line provenance are resolved from canonical `receipt` state before creation;
- acquisition source identity is deterministic from receipt ID + receipt-line ID + stable acquisition key;
- exact source replay returns the same asset without allocating another UUID or revision;
- source identity attached to multiple UUIDs fails closed;
- a replay cannot substitute a different requested UUID;
- `individual` tracking requires quantity exactly 1;
- `lot` tracking supports intentional grouped quantity;
- receipt-line acquisitions cannot exceed the canonical whole-unit line quantity;
- multiple individually tracked units from one line require distinct acquisition keys/UUIDs;
- display-name/note enrichment preserves UUID, quantity, tracking mode, and acquisition provenance;
- receipt correction/enrichment cannot replace an already-created asset UUID;
- query supports receipt, receipt-line, and display-name filters with deterministic UUID ordering.

Asset payload intentionally contains no fitment, identifier, location, movement, warranty, maintenance, technical-specification, inventory-placement, or Drive-filing state.

### Direct tests

`tests/test_assets.py` covers:

- explicit RFC 4122 UUID creation/validation;
- source replay with zero-write identity reuse;
- source-to-two-UUID collision failure;
- missing receipt and missing receipt-line rejection;
- individual quantity enforcement;
- lot quantity behavior;
- two separately tracked units from one receipt line;
- over-acquisition rejection;
- enrichment preserving UUID/provenance;
- receipt correction preserving UUID;
- downstream side-effect fields remaining absent.

### Personal release wiring

The Git-backed Personal starter now advertises `asset` in `resource_types_json` while preserving all existing data classes.

The complete no-app operating instructions now require:

- `authority_binding/binding-asset` routing `asset` to the same Personal Google authority;
- immutable RFC 4122 Entity UUID identity;
- explicit receipt/line acquisition provenance;
- stable acquisition source identity/replay behavior;
- individual-vs-lot quantity rules;
- no automatic fitment, identifier, inventory-location, movement, warranty/maintenance, technical-specification, or Drive-filing side effects.

`mira.personal_distribution`, `mira.workspace_bundle`, and their direct tests enforce the asset-inclusive release contract. `project/code_ownership.json` adds the `canonical-assets` component with `tests/test_assets.py` as direct evidence.

## CI evidence

PR #65 CI run `33284755714` passed on implementation/release head `18c9a80a34c8fae87c15a13c5105c339814b95d9`, including repository integrity, product lifecycle, Personal starter distribution, work-session alignment, code ownership, Python unit tests, and Workspace Apps Script tests.

Closeout run `33298296777` failed only the work-session-alignment gate because the checkpoint field was mislabeled `Related preserved features` instead of the required `Related invariants/features`; compile, feature registry, product lifecycle, and Personal distribution were green before that gate. This commit corrects only that governance label. The exact current head still requires a fresh CI run before merge.

## Independent Google provider proof — 2026-08-29/30

A brand-new native Google Sheet was created only for this packet. It was not copied from or written into legacy MIRA receipt/asset/inventory/Drive/automation production state. After proof it was renamed to include `NOT A STARTER`. Provider file ID and authenticated-account details are intentionally excluded from public Git.

### Clean substrate

Exact readback before mutable proof state confirmed:

- timezone `Etc/UTC`;
- tabs exactly `Metadata`, `Resources`, `Events`, `Idempotency`;
- `mira-structured-state-v1` / `STORE-001` / `single_writer`;
- asset-inclusive resource type list matching the branch starter;
- exact STORE-001 headers;
- zero mutable data rows.

### Authority + receipt prerequisite

Exact readback then confirmed:

- one enabled/verified synthetic `authority/google-sheets-personal`;
- `binding-receipt` -> `receipt`;
- `binding-asset` -> `asset`;
- one captured synthetic receipt at revision 1;
- one synthetic receipt line with quantity `2`;
- exact matching request hashes/idempotency results/resource references.

### Asset revision 1 and replay boundary

One synthetic explicitly requested acquisition read back as:

- one `asset` Resource;
- one RFC 4122 Entity UUID used as both Resource ID and payload UUID;
- revision 1;
- `individual`, quantity 1;
- exact receipt + receipt-line + receipt-revision provenance;
- one stable acquisition key and deterministic `receipt-acquisition:<sha256>` source identity;
- exact create request hash/idempotency result;
- no downstream fitment/location/etc. state.

The implemented same-source replay path is zero-write, so no fake provider mutation was issued merely to demonstrate a no-write result. Provider state remained one asset Resource/one create Idempotency row for that source; direct unit tests independently prove replay returns the same UUID without a new revision.

### Asset revision 2 enrichment

A permitted nonidentity enrichment changed only the synthetic display name and note.

Exact readback confirmed:

- same Resource ID / Entity UUID;
- revision exactly 2;
- same acquisition source identity, acquisition key, receipt ID, receipt-line ID, receipt revision, tracking mode, and quantity;
- exact revision-2 request hash/idempotency result;
- both create and enrichment Idempotency records retained;
- still exactly one asset Resource for the source.

Durable non-sensitive proof: `docs/NO_APP_ASSET_PROVIDER_PROOF.md`.

## End-of-session alignment verification

### `FEATURES.md`

Rechecked after implementation/provider proof. `ASSET-001` and the acquisition slice of `ASSET-002` are directly implemented/tested/provider-persisted. `FITMENT-001`, `IDENT-001`, `EVID-001`, `ASSET-003`, `INV-001`, `LOC-001`, `MOVE-001`, `INV-002`, warranty/maintenance, specifications, grocery/meal, appointments, Android, Microsoft, and Apple/iCloud scope remain preserved rather than falsely completed.

### `BACKLOG.md`

Rechecked after implementation/provider proof. `ASSET-ACQUISITION-001` correctly remains `active` until PR #65 is merged. Downstream `FITMENT-ENGINE-001`, `ASSET-SERVICE-001`, `LOCATION-STATE-001`, `MOVEMENT-CORE-001`, `INVENTORY-QUERY-001`, receipt taxonomy, and other accepted work remain unfinished. The next packet must change the asset row to completed only after merge evidence exists.

### `ROADMAP.md`

Rechecked after implementation/provider proof. This packet advances the explicit M2-M0.5 receipts/assets/inventory direction, introduces no external-infrastructure prerequisite, and keeps Android paused rather than turning asset work into an Android dependency.

### Direction result

**ALIGNED.** The bounded receipt-to-immutable-asset vertical is technically and provider verified. Merge is the only remaining lifecycle gate.

## Acceptance result

1. Provider-neutral `AssetService` over STORE-001 — PASS.
2. Canonical RFC 4122 UUID Resource identity — PASS.
3. Stable globally unique acquisition source identity + read-only replay — PASS.
4. Canonical receipt/line prerequisite validation — PASS.
5. Individual/lot quantity rules and receipt-line capacity — PASS.
6. Replay cannot replace UUID or conflicting acquisition facts — PASS.
7. Nonidentity enrichment preserves UUID/provenance — PASS.
8. Direct tests for UUID/replay/conflict/quantity/enrichment/receipt correction/side-effect isolation — PASS.
9. Personal starter `asset` + `binding-asset` contract — PASS.
10. Complete no-app immutable asset/no-side-effect contract — PASS.
11. Distribution/Workspace validation + code ownership — PASS.
12. CI green on implementation head — PASS; exact corrected-closeout-head CI PENDING.
13. Fresh isolated Google receipt-to-asset revision-1/replay-boundary/revision-2 exact readback — PASS.
14. End-of-session whole-product reconciliation — PASS.

## Exact next action

1. Run CI on the exact current PR #65 corrected-closeout head containing this checkpoint.
2. If every gate is green, merge PR #65 using expected-head SHA protection.
3. Remotely verify `main` at the returned merge SHA.
4. Create exactly one next bounded packet from verified `main` and in that packet reconcile `ASSET-ACQUISITION-001` to completed with PR #65 evidence.
5. Dependency-rank the next no-app vertical. The leading foundation is expected to be stable namespaced identifiers (`IDENT-001`) because it unlocks fitment, scanning/movement, and richer asset queries, but select from the canonical unfinished ledger rather than conversational preference.
6. Keep Android paused unless explicitly reprioritized or no-app milestone evidence justifies resumption.

## Recovery protocol

Read this file first. If PR #65 is open, verify its exact current head and exact-head CI before merge. If merged, verify `main`, reconcile the asset backlog row to completed, then activate exactly one next bounded packet. Do not touch legacy production asset/inventory state and do not broaden completed asset acquisition into fitment/location/etc. by conversational inference.
