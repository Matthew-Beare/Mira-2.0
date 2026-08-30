# M2-M0-015 Personal no-app inventory/location provider proof

Date: 2026-08-30

This document records non-sensitive live-provider evidence for `M2-M0-015` / `LOCATION-STATE-001`. The provider file identifier and authenticated-account details are deliberately excluded from public Git.

## Safety boundary

- A brand-new native Google Sheet was created solely for this synthetic proof.
- No legacy MIRA/MIRROR production spreadsheet, Drive artifact, brief, schedule, inventory, receipt, asset, or other user state was copied, renamed, repurposed, or mutated.
- After verification, the synthetic Sheet was renamed to include `NOT A STARTER` so it cannot be mistaken for an installable Personal starter.
- All proof entities, locations, timestamps, labels, and identifiers are synthetic.

## Clean starter-substrate readback

Before mutable proof state was written, exact Google readback confirmed:

- spreadsheet timezone `Etc/UTC`;
- tabs exactly `Metadata`, `Resources`, `Events`, `Idempotency`;
- `schema_version=mira-structured-state-v1`;
- `adapter_contract=STORE-001`;
- `writer_model=single_writer`;
- resource types include the existing Personal classes plus `inventory_state` and `location`;
- exact STORE-001 table headers;
- zero inherited mutable Resource rows.

## Canonical authority and identity prerequisite

The synthetic proof then persisted/read back:

- one enabled/verified synthetic `authority/google-sheets-personal`;
- `binding-asset` -> `asset`;
- `binding-location` -> `location`;
- `binding-inventory-state` -> `inventory_state`;
- one immutable synthetic physical asset Resource using canonical Entity UUID `55555555-5555-4555-8555-555555555555`;
- the asset remained revision 1 throughout all inventory/location mutations.

The `inventory_state` Resource ID is exactly the same canonical asset Entity UUID. No second physical/inventory UUID was created.

## Location hierarchy proof

Four stable canonical location Resources were persisted at revision 1:

- `location-synthetic-shop` — kind `room`, root;
- `location-synthetic-shelf-a` — kind `shelf`, parent `location-synthetic-shop`;
- `location-synthetic-shelf-b` — kind `shelf`, parent `location-synthetic-shop`;
- `location-synthetic-bench` — kind `zone`, parent `location-synthetic-shop`.

Direct unit tests separately cover parent existence, self-parent rejection, ancestor-cycle rejection, stable identity under update/reparent, malformed persisted hierarchy, and safe traversal bounds. The live provider proof verifies persistence/readback of the valid hierarchy; it does not claim provider execution of every negative fixture.

## Intended-versus-observed revision chain

### Revision 1 — inventory participation / intended home

The synthetic asset was added to inventory state using Resource ID equal to its Entity UUID.

Exact readback showed:

- `participation_state=tracked`;
- `intended_location_id=location-synthetic-shelf-a`;
- `observed_location_id=null`;
- `observed_at=null`.

No asset identity, quantity, tracking mode, or acquisition provenance changed.

### Revision 2 — observation changes only observed state

A canonical revision-checked mutation recorded:

- `observed_location_id=location-synthetic-bench`;
- `observed_at=2026-08-30T12:45:00-06:00`.

Exact Google readback showed revision `2` while preserving:

- the same Entity UUID / Resource ID;
- `intended_location_id=location-synthetic-shelf-a`;
- the same note and participation state.

This proves recording where the item was observed does not silently redefine where it belongs.

### Revision 3 — intended-home change preserves observation

A second canonical revision-checked mutation changed only intended placement to:

- `intended_location_id=location-synthetic-shelf-b`.

Exact Google readback showed revision `3` while preserving:

- `observed_location_id=location-synthetic-bench`;
- `observed_at=2026-08-30T12:45:00-06:00`;
- the same Entity UUID / Resource ID.

This proves changing where the item belongs does not fabricate or overwrite a physical observation.

## Idempotency/readback evidence

Provider readback retained separate idempotency records for:

1. initial inventory participation at revision 1;
2. observed-location mutation at revision 2;
3. intended-home mutation at revision 3.

Each record retained its request hash, canonical upsert result, timestamp, and `inventory_state/<Entity UUID>` resource reference.

A bounded provider search for the synthetic Entity UUID returned exactly:

- the canonical `asset` Resource at revision 1; and
- the canonical `inventory_state` Resource at revision 3.

Both use the same Entity UUID as Resource identity. This verifies inventory participation is a projection over the existing physical asset identity rather than a parallel physical-item database.

## Evidence ceiling

This proof establishes live Google persistence/readback for the bounded `LOCATION-STATE-001` base slice: inventory identity reuse, valid location hierarchy persistence, and independent intended/observed state revisions.

It does **not** prove or activate:

- movement-event history;
- QR/barcode scan-in/out;
- movable-container-following movement semantics;
- broad inventory search/projection;
- par/low-stock or grocery flows;
- fitment inference;
- OCR/photo acquisition;
- Android capture or multi-writer mutation.

Those remain separate work/features and must earn their own implementation and verification evidence.