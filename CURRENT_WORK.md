# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and exact recovery state.

## Product direction

Default Personal MIRA is stock ChatGPT + Google Workspace with no external infrastructure prerequisite. Current priority is repeated useful no-app verticals before Android resumes. Completed work remains durable with evidence and is filtered from future selection rather than deleted.

Every work session begins and ends by checking `CURRENT_WORK.md`, `FEATURES.md`, `BACKLOG.md`, and `ROADMAP.md`.

## Completed predecessor

### `M2-M0-015` — Canonical inventory participation + intended/observed location

PR #67 merged to `main` as `7c2675836d2958d23ac37ad471cae8e14017b894`. Exact PR-head CI run `33329282677` passed on `1296e6bacdcbeab9a905893dbc49742039782de1`. Fresh isolated Google provider proof verified canonical asset-UUID inventory participation, hierarchical locations, and independent intended-versus-observed location state. Current `main` was subsequently verified at `2da3128cdecad86b45c776f31ccb63e5be5aadc0` with CI run `33329434913` green; the intervening placeholder add/remove changed no product state.

`LOCATION-STATE-001` is now reconciled as completed in `BACKLOG.md`, and `LOC-001` carries direct merged/test evidence independently from still-unfinished movement/scanning behavior.

## Active packet

### `M2-M0-016` — Canonical inventory query projection

- **Primary work:** `INVENTORY-QUERY-001`
- **Primary features:** `INV-002`
- **Related invariants/features:** `INV-001`, `LOC-001`, `ASSET-001`, `ASSET-003`, `IDENT-001`, `STORE-001`, `RECOVERY-002`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `integration/m0-016-inventory-query`
- **Base SHA:** `2da3128cdecad86b45c776f31ccb63e5be5aadc0`
- **PR:** `#70` (non-draft replacement merge PR; #69 closed unmerged after connector ready-for-review failure)
- **Objective:** provide a deterministic read-only no-app projection over canonical tracked inventory so MIRA can answer what is owned, identify an item by canonical asset identity/name/identifier, and report intended versus latest observed location without creating a second inventory authority or fabricating movement evidence.

## Session-start alignment verification — 2026-08-30

### `FEATURES.md`

Verified before implementation:

- `INV-002` is the canonical queryable household/loft/shop inventory projection;
- it depends on canonical inventory participation/location plus identifier/asset graph truth rather than a shadow inventory table;
- `INV-001` requires the existing asset Entity UUID to remain the physical/inventory identity;
- `LOC-001` requires intended placement to remain distinct from observed/last-supported state;
- `IDENT-001`/`ASSET-003` already provide identifier-origin resolution back to canonical assets.

### `BACKLOG.md`

Verified before implementation:

- `LOCATION-STATE-001` was stale-text active even though PR #67 had merged, and required reconciliation to completed;
- `INVENTORY-QUERY-001` was queued and its prerequisites were satisfied by merged receipt/asset/identifier/location work;
- `MOVEMENT-CORE-001` was also unblocked, but inventory query provided the shorter immediate no-app user-visible value because it made existing canonical inventory state answerable before scanner/event history exists;
- par/grocery, fitment, movement events, OCR/evidence enrichment and Android remained separate unfinished work.

### `ROADMAP.md`

Verified before implementation:

- M2-M0.5 explicitly prioritizes repeated useful stock-ChatGPT + Google Workspace verticals before Android;
- receipts/assets/inventory are an accepted no-app feature family;
- packets must remain bounded and must not collapse inventory query, movement/scanning, par/grocery and Android capture into one subsystem.

### Direction result

**ALIGNED.** A read-only canonical inventory query projection is the smallest next vertical that turns the merged receipt → asset → identifier → inventory/location foundation into directly useful answers without requiring movement/scanner infrastructure.

## Acceptance criteria

1. Query only canonical `inventory_state`; untracked assets are not silently presented as inventory.
2. Every result reuses the canonical asset Entity UUID and resolves the canonical asset record; no second physical/inventory identity exists.
3. Result projection includes stable asset identity/name/tracking mode/quantity and acquisition provenance needed to trace back to the canonical receipt relationship.
4. Result projection includes canonical identifiers for the asset without letting identifier strings replace asset identity.
5. Result projection resolves intended and observed locations independently and preserves the exact canonical `observed_at` truth.
6. Location presentation includes a deterministic root-to-leaf path derived from canonical parent relationships and fails closed on missing/cyclic/corrupt hierarchy.
7. Bounded query supports direct Entity UUID, case-insensitive asset-name substring, exact canonical identifier lookup, intended-location filter, observed-location filter, and deterministic limit/order semantics.
8. Location filtering may explicitly include descendants, but must never infer container-following movement or rewrite item state.
9. Unknown asset/location/identifier filter material and persisted orphan/corrupt references fail closed with domain errors instead of being ignored.
10. Query execution is read-only: zero Resource/Event/Idempotency mutations and no asset/inventory/location/identifier revision changes.
11. No movement-event history, scan-in/out, QR/barcode capture, fitment, par/grocery, warranty/maintenance, OCR/evidence acquisition, or Android behavior is implemented or claimed.
12. Direct tests cover identity, name, identifier and location filters; descendant matching; intended/observed distinction; path rendering; deterministic ordering/limits; corruption failure; and zero-write behavior.
13. Complete Personal no-app operating instructions describe canonical inventory query behavior and its honesty boundaries.
14. Workspace/release validation directly guards the new no-app query contract.
15. `FEATURES.md`, `BACKLOG.md`, `CURRENT_WORK.md`, and code-ownership evidence are reconciled before merge.
16. Required CI is green on the exact merge candidate head.
17. A fresh isolated Google provider proof demonstrates read-only queryability over synthetic canonical receipt/asset/identifier/location/inventory rows without touching protected legacy production state.
18. End-of-session whole-product reconciliation confirms unfinished movement/scanning/container-following/par/grocery/fitment/OCR/Android work remains unfinished.

## Completed evidence in this packet

### Implementation

- Added provider-neutral `mira/inventory_query.py` as a read-only projection over the existing canonical asset, identifier, inventory-state and location services.
- Query supports canonical Entity UUID, case-insensitive display-name substring, exact canonical identifier lookup, independent intended/observed location filters, explicit descendant inclusion, deterministic root-to-leaf location paths and deterministic sort/limit behavior.
- Projection begins from tracked canonical `inventory_state` only and never allocates a second physical/inventory identity.
- Corrupt/orphan asset or location references and cyclic/broken location ancestry fail closed.
- Query path contains no mutation operation and never infers movement/scanning/container-following behavior.

### Direct/test evidence

- Added `tests/test_inventory_query.py` with ten direct tests covering joined identity/provenance/identifier/location output, all bounded filters, descendant semantics, untracked exclusion, deterministic order/limit, malformed filters, no-match behavior, cyclic hierarchy, orphan inventory state and exact zero mutation of Resource/Event/Idempotency in-memory state.
- Registered the dedicated `canonical-inventory-query` production component in `project/code_ownership.json` with direct verification ownership.
- Early PR-head CI run `33340369948` passed on `a2ef63109b943464ce82239224253b6955012e4f` after the core implementation/tests/ownership checkpoint.
- CI run `33340451667` passed on `0c180fc49064f93979299c707181eaa64bfeda06` after complete no-app instructions and workspace release guards were added.
- Exact-head CI run `33340849539` passed on `66eb512afd7824d872c48c220c9289aac3132559` after lifecycle reconciliation; this SHA was the final #69 draft head before the connector's ready-for-review operation failed.

### Pull-request control-plane evidence

- PR #69 was intentionally opened as draft during implementation and remained green on exact head `66eb512afd7824d872c48c220c9289aac3132559`.
- The GitHub connector's ready-for-review mutation failed before changing PR state because its GraphQL response requested the nonexistent `Repository.fullDatabaseId` field. A direct merge attempt then correctly returned HTTP 405 because #69 was still draft.
- PR #69 was closed **without merge** and with the failure reason recorded. PR #70 was opened non-draft from the same branch and same verified code history. This is a control-plane workaround only; no product implementation was discarded or silently replaced.

### No-app/release evidence

- `workspace/apps_script/MIRA_NO_APP_INSTRUCTIONS.md` now defines canonical read-only inventory query behavior, supported filters, intended-versus-observed honesty, descendant semantics, deterministic location paths, zero-write rules and explicit limits on what an empty result or inventory query proves.
- `mira/workspace_bundle.py` now directly guards those inventory-query clauses so future starter/release drift fails CI.

### Fresh isolated Google provider proof

A new synthetic Google Sheet was created specifically for `M2-M0-016` and clearly marked `NOT A STARTER`; its provider ID/URL is intentionally excluded from public Git. No protected legacy MIRA production artifact was read as a fixture or modified.

Synthetic provider state contained:

- one synthetic receipt with three receipt-linked canonical assets;
- three canonical asset UUIDs, with only two participating in `inventory_state` so the third acted as an untracked control;
- canonical model identifiers for all three assets;
- hierarchical synthetic `site → shop → shelf/workbench` locations;
- two tracked inventory-state rows, one with intended Shelf A plus an independent observed Workbench timestamp and one with intended Shelf B plus no observation;
- exact STORE-001-shaped `Resources`, `Events` and `Idempotency` tabs for bounded provider readback.

Verified read-only query results:

- bounded `inventory_state` query returned exactly the two tracked UUIDs;
- `WRENCH-42` resolved the canonical identifier linked to the tracked wrench UUID;
- querying that UUID joined its canonical asset, identifier and inventory-state rows;
- the untracked drill UUID returned only asset + identifier rows and no inventory-state row;
- canonical location rows proved both shelves and the workbench descend from the same shop without treating ancestry as movement evidence;
- `loc-bench` matched only the wrench's observed-location state;
- provider pre-query and post-query `Resources`, `Events` and `Idempotency` readbacks were logically identical: all Resource revisions remained `1`, `Events` remained header-only and `Idempotency` remained header-only. Drive `modifiedTime` was not used as evidence because it lagged the earlier seed write asynchronously.

This is provider proof of read-only queryability over synthetic canonical rows, not a claim that the fixture seed itself exercised the runtime mutation/idempotency path.

## Session-end authority reconciliation — 2026-08-30

### `FEATURES.md`

- `LOC-001` requirement/evidence is reconciled to `required | test_verified` from merged PR #67 without implying `MOVE-001` is complete.
- `INV-002` correctly remains `candidate_unmerged` until PR #70 actually merges; tests/provider proof do not substitute for merge evidence.

### `BACKLOG.md`

- `LOCATION-STATE-001` is reconciled to completed with PR #67 merge SHA, exact-head CI and provider evidence.
- `INVENTORY-QUERY-001` is the one active work row and records direct-test, no-app/release and isolated Google provider evidence; PR #70 exact-head CI/merge remains the only completion gate.
- `MOVEMENT-CORE-001`, `PAR-CORE-001`, `GROCERY-CORE-001`, fitment, OCR/evidence and Android remain unfinished and outside this packet.

### `ROADMAP.md`

- Rechecked with no semantic change required: M2-M0.5 still prioritizes useful stock-ChatGPT + Google Workspace verticals before Android and still requires bounded packets rather than subsystem fan-out.

### Direction result

**ALIGNED FOR MERGE CANDIDATE.** No adjacent feature was silently absorbed. The only remaining packet work is exact-head CI on the replacement PR, merge, and remote `main` verification.

## Exact next action

1. Reconcile `BACKLOG.md` references from the closed-unmerged #69 control PR to active non-draft PR #70.
2. Verify CI is green on the exact current PR #70 head after these control-plane checkpoint edits.
3. Re-read PR #70 head/mergeability and merge only with expected-head protection.
4. Remotely verify `main` contains the merge and its CI/readback is green.
5. Create the durable post-merge closeout/next-packet checkpoint; only then may another vertical become active.

## Recovery protocol

Read this file first. Confirm branch `integration/m0-016-inventory-query` still descends from verified base `2da3128cdecad86b45c776f31ccb63e5be5aadc0`. PR #70 is the active non-draft packet PR; PR #69 is closed unmerged as control-plane failure evidence. Do not touch protected legacy MIRA production data. Do not implement movement events, scanning, container-following movement, par/grocery, fitment, OCR/evidence capture or Android as part of this packet.