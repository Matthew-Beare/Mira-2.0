# No-app Personal asset provider proof

Packet: `M2-M0-013` / `ASSET-ACQUISITION-001`

This document records the non-sensitive evidence from a fresh isolated Google Sheets proof for the bounded Personal receipt-linked asset-acquisition vertical. The provider file ID, authenticated account details, and any private provider identifiers are intentionally excluded from public Git.

## Isolation boundary

A brand-new native Google spreadsheet was created for this proof. It was not copied from or written into legacy MIRA receipt, asset, inventory, Drive, brief, automation, or other production state. After verification the file was renamed to include `NOT A STARTER` so it cannot be mistaken for an installable Personal starter.

## Clean starter substrate

Before any mutable proof state was inserted, provider readback confirmed:

- spreadsheet timezone `Etc/UTC`;
- tabs exactly `Metadata`, `Resources`, `Events`, `Idempotency`;
- Metadata schema `mira-structured-state-v1`;
- adapter contract `STORE-001`;
- writer model `single_writer`;
- resource types exactly `authority`, `authority_binding`, `asset`, `entity`, `onboarding_ledger`, `ops_brief_run`, `receipt`, `service_state`, `task`;
- exact STORE-001 headers;
- zero Resource, Event, and Idempotency data rows.

## Authority and receipt prerequisite

Synthetic state was then inserted and read back exactly:

- one enabled/verified `authority/google-sheets-personal` using a synthetic owner token;
- `authority_binding/binding-receipt` routing `receipt` to that authority;
- `authority_binding/binding-asset` routing `asset` to that same authority;
- one captured synthetic receipt at revision 1;
- one receipt line with quantity `2`, leaving capacity for separately tracked physical units;
- matching request hashes, idempotency results, and resource references.

The receipt is synthetic. No real merchant, order, account, purchase, or private user fact appears in this proof.

## Asset revision 1

One explicitly requested receipt-linked acquisition was persisted using the production M2-M0-013 payload shape.

Provider readback confirmed:

- resource type `asset`;
- one RFC 4122 Entity UUID used as both Resource ID and payload `entity_uuid`;
- revision exactly 1;
- `tracking_mode=individual` and `quantity=1`;
- acquisition `source_type=receipt`;
- one stable acquisition key;
- exact canonical receipt ID and receipt-line ID provenance;
- receipt revision 1 provenance;
- one deterministic `receipt-acquisition:<sha256>` source identity;
- no fitment, identifier, location, movement, warranty, maintenance, technical-specification, inventory-placement, or Drive-filing fields;
- exact request hash and matching idempotency result.

## Same-source replay boundary

The implemented `AssetService` resolves an acquisition replay from persisted `source_identity` before creating a second asset. When display name/note are also unchanged, replay is read-only and performs zero store writes.

The provider state contained exactly one asset Resource and one acquisition-create Idempotency row for that source. No second provider mutation was issued merely to manufacture evidence of a zero-write replay. Direct unit tests independently exercise the same-source replay path and prove the same UUID is returned without a new revision.

## Nonidentity enrichment / revision 2

A permitted enrichment then changed only the synthetic display name and note. The asset row was revision-checked from revision 1 to revision 2 and a matching enrichment Idempotency row was appended.

Exact provider readback confirmed:

- the Entity UUID remained identical;
- Resource ID remained identical;
- acquisition source identity remained identical;
- receipt ID, receipt-line ID, receipt revision, acquisition key, source type, tracking mode, and quantity remained identical;
- revision became exactly 2;
- only the allowed display-name/note attributes changed;
- both create and enrichment idempotency records remained present with exact request hashes/result JSON/resource references;
- there was still exactly one asset Resource for the acquisition source.

## Evidence boundary

This proves the Google structured-state substrate can persist and exactly read back the bounded M2-M0-013 receipt-to-asset identity contract, including immutable UUID across enrichment. Together with direct `AssetService` tests, it supplies the provider-persistence evidence required for this packet.

It does **not** claim that fitment inference, serial/UPC/model identifiers, warranty/maintenance, technical specifications, inventory locations, movement/scanning, Drive asset folders, Gmail/OCR acquisition, or Android capture are implemented or live. Those remain separate accepted work.