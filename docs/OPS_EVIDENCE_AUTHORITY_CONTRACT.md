# MIRA Ops Evidence Authority Contract

## Purpose

Prevent mutable operational facts from being promoted from chat, memory, vendor email, stale projections, or secondary evidence when a fresher canonical authority exists. Also require durable owned purchases to complete the receipt-to-inventory evidence chain before MIRA claims ingestion succeeded.

This contract is provider-neutral and contains no private account, shipment, spreadsheet, or user data.

## Mutable fact rule

For every mutable operational fact, resolve the authority for that fact class before rendering or persisting a current-state claim.

Examples include shipment ETA/status, account balances, route/mode, current mileage, calendar state, order lifecycle, appointment state, and provider sync status.

Secondary evidence may identify an entity or suggest a value, but it must not silently impersonate the canonical authority.

### Shipment authority

When a carrier tracking number exists:

1. The live carrier tracking record is canonical for ETA, progress, exceptions, out-for-delivery state, and delivery state.
2. Vendor shipment email, stale tracking cache, chat history, model memory, and user-provided guesses are secondary evidence only.
3. A user correction can identify the correct shipment/tracking number or report what they observed, but MIRA must still dereference the live carrier authority when the runtime can do so.
4. If carrier readback cannot be completed, do not repeat a secondary ETA as fact. Report the shipment state as unverified and preserve the tracking identifier/link when available.
5. Never claim a live ETA merely because a tracking URL or tracking number was found. Success requires the carrier value itself to be read back.

When no tracking number exists, vendor/user evidence may be reported only with its provenance and verification ceiling.

## User corrections

User corrections are authoritative for facts the user directly controls or observes, such as purpose/category, possession, physical installation, route/mode changes, or explicit household intent.

A user correction does not automatically override an external live authority for facts controlled by a third party, such as a carrier ETA, bank balance, provider account state, employer posting status, or calendar/provider write result. When external live authority is reachable, read it back.

## Durable purchase commit rule

Email receipts and order confirmations are evidence. They do not, by themselves, prove that a durable purchase was fully ingested.

For a newly acquired non-consumable item owned by the household, MIRA must complete the full chain before claiming success:

1. positively identify the purchase/receipt evidence;
2. classify the item without guessing;
3. save or link one durable readable receipt/evidence artifact when the connected provider supports it;
4. write or enrich the existing canonical physical-asset/inventory record rather than creating a duplicate;
5. attach the archived receipt link to the canonical record;
6. create required ownership/assignment/installation relationships without conflating those states;
7. preserve stable IDs and deduplicate by order/item/asset identity;
8. read back the canonical record and receipt link;
9. report success only after the readback agrees.

If any required step is unavailable or ambiguous, fail closed for that item and surface `ACTION REQUIRED` or `Needs Review` rather than silently half-processing it.

## Routing

- Tools/shop equipment use the existing canonical tool inventory surface and physical-asset identity graph.
- Other durable physical goods use the existing canonical physical-asset/inventory authority.
- Installed components attach to the parent asset through an explicit installed-on relationship when evidence supports installation; ownership or assignment alone must not imply installation.
- Consumables remain purchase/receipt/spend evidence and are not forced into durable inventory.
- Returns, cancellations, refunds, replacements, and disposals update lifecycle/provenance rather than creating duplicate assets.

## Brief behavior

Before an Ops Brief reports a mutable current-state value:

1. resolve the fact-specific canonical authority;
2. read it when available;
3. distinguish verified, user-reported, stale, and unverified states;
4. never upgrade a secondary source merely because it is convenient or newer than chat history;
5. keep independent modules running when another authority is unavailable, but clearly fail closed for the affected fact/module.

## Acceptance examples

- Tracking exists; user says ETA is Monday; carrier was not read: output must not say Monday as verified ETA.
- Tracking exists; live carrier says Saturday while vendor/user says Monday: Saturday wins.
- Receipt email exists but no archived receipt link or canonical inventory readback exists: durable purchase remains incomplete.
- Durable item has archived receipt, category, canonical record, matching receipt link, and successful readback: ingestion may be marked committed.
- Consumable purchase does not create a durable inventory record.
