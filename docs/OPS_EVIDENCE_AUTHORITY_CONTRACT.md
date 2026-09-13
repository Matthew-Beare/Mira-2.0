# MIRA Ops Evidence Authority Contract

## Purpose

Prevent mutable operational facts from being promoted from chat, memory, vendor email, stale projections, or secondary evidence when a fresher canonical authority exists. Also require durable owned purchases to complete the receipt-to-inventory evidence chain before MIRA claims ingestion succeeded.

This contract is provider-neutral and contains no private account, shipment, spreadsheet, or user data.

## Global reconciliation sweep and pre-reply gate

A recurring brief or an explicit request to refresh operational state must not begin with prose composition. It must first execute the applicable deterministic sweep:

`DISCOVER -> RECONCILE -> MUTATE -> REBUILD -> VERIFY -> CHECKPOINT -> REPLY`

For each enabled domain module, the run must:

1. establish deterministic run identity, local timezone/slot/context, canonical authorities, prior durable cursor/checkpoint and required module manifest;
2. discover newly available evidence from the module's authorized sources;
3. reconcile stable source identity, matches, duplicates/replays, transfers/exclusions, unresolved evidence and user corrections;
4. mutate canonical state only when evidence and authority permit it;
5. rebuild dependent projections only after canonical reconciliation;
6. verify module invariants and exact readback for every required canonical mutation;
7. persist a bounded checkpoint containing source coverage/freshness, reconciliation counts, mutations/readback results, next cursors or markers, review items and blockers;
8. pass the pre-reply claim gate before describing the module as current, updated, reconciled, done, complete or equivalent.

Every declared module ends in exactly one state: `complete`, `needs_review`, `blocked`, or `not_applicable`. Silence is not a terminal state. A failed module must not suppress independent healthy modules, but the affected module must fail closed and expose the exact bounded blocker or review state.

A repeated run with the same completed deterministic identity and manifest returns the durable checkpoint instead of rerunning side effects. This contract does not imply that a scheduler or background process exists; live scheduling must be proved separately.

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

### Unresolved shipment evidence diligence

The absence of tracking or ETA is a conclusion, not a first-pass default. Before MIRA may report that tracking could not be found, the applicable AM/PM reconciliation must, when those sources are authorized and reachable:

1. open and read the relevant message or thread rather than relying on subject/snippet text;
2. inspect accessible order/shipment detail links and attachments;
3. correlate split shipments, package indexes/IDs, carrier references and replacement/supersession evidence;
4. search later messages for the same order or shipment identity;
5. recheck every still-active unresolved shipment on each AM/PM run;
6. dereference the live carrier authority when a tracking identifier exists and the carrier is reachable.

If tracking still cannot be established after those checks, the bounded state is `unverified/no tracking found after recheck`, not an absolute claim that no tracking exists. A module must not mark shipment reconciliation complete when a required evidence step was skipped merely because the first message lacked an obvious tracking number.

## User corrections

User corrections are authoritative for facts the user directly controls or observes, such as purpose/category, possession, physical installation, route/mode changes, or explicit household intent.

A user correction does not automatically override an external live authority for facts controlled by a third party, such as a carrier ETA, bank balance, provider account state, employer posting status, or calendar/provider write result. When external live authority is reachable, read it back.

## Mileage reconciliation backstop

During each AM/PM ROAD reconciliation, mileage must be compared across the configured canonical Ops trip state, the authoritative mileage/pay tracker and any explicitly approved shared team-trip evidence source.

When approved shared trip evidence contains a completed paid leg newer than MIRA's own recorded state, MIRA may advance canonical trip/mileage state from that evidence only when the leg identity and paid-mile value are supported. It must not infer company-paid miles from map distance, double-credit a leg already present elsewhere, or multiply team mileage by the number of drivers.

After any catch-up mutation, the affected trip state and aggregate current-cycle paid-mile total must be read back before the brief can call mileage updated or reconciled. Active/in-progress legs remain separate from completed paid mileage.

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

1. require the applicable reconciliation module to reach a terminal disposition;
2. resolve the fact-specific canonical authority;
3. read it when available;
4. distinguish verified, user-reported, stale, unknown and unverified states;
5. never upgrade a secondary source merely because it is convenient or newer than chat history;
6. require exact readback for required mutations before using updated/reconciled/done language;
7. keep independent modules running when another authority is unavailable, but clearly fail closed for the affected fact/module;
8. checkpoint the run before rendering the final reply.

The final response is a projection of the verified checkpoint, not a substitute for executing the reconciliation work.

## Acceptance examples

- Tracking exists; user says ETA is Monday; carrier was not read: output must not say Monday as verified ETA.
- Tracking exists; live carrier says Saturday while vendor/user says Monday: Saturday wins.
- First shipping email has no obvious tracking, but the order detail or later thread does: MIRA must continue the evidence search and correlate the package instead of saying there is no tracking.
- After the full unresolved-shipment recheck still finds no supported tracking: output may say `unverified/no tracking found after recheck`.
- Shared trip evidence contains a newer completed paid leg absent from MIRA: reconcile it once, read back the total, and do not infer mileage from map distance or double-count the team leg.
- A module writes canonical state but cannot read it back: it cannot claim updated/reconciled/done.
- One module is blocked while unrelated modules verify successfully: the reply may include the valid modules plus exact `ACTION REQUIRED` state for the blocked module.
- Receipt email exists but no archived receipt link or canonical inventory readback exists: durable purchase remains incomplete.
- Durable item has archived receipt, category, canonical record, matching receipt link, and successful readback: ingestion may be marked committed.
- Consumable purchase does not create a durable inventory record.
