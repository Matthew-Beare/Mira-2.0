# M2-M0-014 Personal Google identifier provider proof

Date: 2026-08-30

This document records the non-sensitive evidence for the isolated Google provider proof of `ASSET-IDENTIFIER-001` / `IDENT-001` on the Personal no-app lane.

The proof used a brand-new native Google Sheet created only for this packet. It did not copy, read from, overwrite, rename, repurpose, migrate, or otherwise use any protected legacy MIRA production spreadsheet, receipt, asset, inventory, Drive artifact, automation, or schedule. The provider file ID and authenticated-account details are intentionally excluded from public Git. After proof, the Sheet was renamed to include `NOT A STARTER`.

## Clean starter substrate

Before mutable proof state was written, exact Google readback confirmed:

- spreadsheet timezone `Etc/UTC`;
- tabs exactly `Metadata`, `Resources`, `Events`, and `Idempotency`;
- `schema_version=mira-structured-state-v1`;
- `adapter_contract=STORE-001`;
- `writer_model=single_writer`;
- `resource_types_json` included `identifier` alongside the existing Personal data classes;
- exact canonical Resources / Events / Idempotency headers;
- no inherited mutable rows.

## Authority and bindings

Synthetic canonical state then established and read back:

- one enabled/verified `authority/google-sheets-personal` using a synthetic owner identity;
- `authority_binding/binding-asset` -> `asset`;
- `authority_binding/binding-identifier` -> `identifier`;
- exact request hashes, revisions, idempotency results, and resource references for those records.

No second asset authority or identifier authority was created.

## Canonical asset prerequisite

One synthetic canonical `asset` Resource was persisted and read back at revision 1 using RFC 4122 Entity UUID:

`44444444-4444-4444-8444-444444444444`

The asset remained `tracking_mode=individual`, quantity `1`, and retained synthetic receipt-acquisition provenance. Identifier mutations did not change the asset Resource, UUID, quantity, acquisition source identity, or receipt provenance.

## Product identifier proof

A representative UPC-A identifier was persisted and read back:

- identifier type: `upc_a`;
- exact source value: `012345678905`;
- normalized value: `012345678905`;
- the leading zero remained intact;
- verification state: `verified`;
- deterministic identifier Resource ID: `identifier-4a3fea47273b551395b9d7d69cd96069`;
- linked Entity UUID: the same canonical asset UUID above;
- exact request hash and idempotency result retained.

A bounded provider row search for `012345678905` returned exactly this identifier row. Following its stored `entity_uuid` resolved the canonical `asset` Resource rather than a shadow asset record.

## Serial-level identifier revision proof

A representative namespaced serial identifier was first persisted as revision 1:

- identifier type: `serial_number`;
- namespace: `Synthetic Maker`;
- namespace key: `synthetic maker`;
- exact source value: `SN-0001`;
- normalized value: `sn-0001`;
- verification state: `observed`;
- deterministic Resource ID: `identifier-6572064aab78f06be89e1801827fca6a`;
- linked Entity UUID: the same canonical asset UUID.

A second canonical mutation upgraded only `verification_state` from `observed` to `verified`.

Exact Google readback after revision 2 confirmed all identity-bearing material remained unchanged:

- same identifier Resource ID;
- same Entity UUID;
- same identifier type;
- same namespace and namespace key;
- same exact source value;
- same normalized value;
- same note;
- revision exactly `2`;
- both create and verification-upgrade Idempotency records retained with distinct exact request hashes.

## Identifier-to-asset lookup proof

Provider-origin lookup was exercised without a second asset database:

1. bounded search by UPC normalized value returned the canonical UPC identifier;
2. that identifier payload returned the immutable Entity UUID;
3. bounded search by that UUID returned the canonical `asset` Resource plus the two identifier Resources linked to it.

This proves the Google structured-state substrate can persist the identifier relationship needed by `IdentifierService.lookup_assets`; direct Python tests separately prove deterministic service-level lookup, validation, replay, multi-asset product-identifier reuse, and serial-level collision rejection.

## Scope boundary

This proof does **not** claim implementation or provider verification of:

- OCR/photo/barcode capture;
- automatic fitment or installation inference;
- inventory placement or location;
- movement events;
- warranty/maintenance or technical-specification enrichment;
- Android scanning/camera/NFC/BLE capture;
- concurrent multi-writer mutation.

Those remain separate accepted work. The proof establishes only validated canonical identifier persistence and identifier-origin canonical asset lookup on the isolated Personal Google single-writer substrate.
