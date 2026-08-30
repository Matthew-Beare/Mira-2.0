# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and exact recovery state.

## Product direction

Default Personal MIRA is stock ChatGPT + Google Workspace with no external infrastructure prerequisite. Completed work remains in the durable product corpus with evidence and is filtered from future selection rather than deleted. The current priority is repeated user-visible no-app verticals that build trustworthy canonical reality before Android resumes.

Every work session begins and ends by checking `CURRENT_WORK.md`, `FEATURES.md`, `BACKLOG.md`, and `ROADMAP.md`.

## Completed predecessor

### `M2-M0-011` — First useful no-app Ops Brief + canonical tasks

Merged in PR #63 to `main` at `f96b227e009eb144235dccfef2ca0b8570e0801b` after exact-head CI `33282946569` passed. `OPS-BRIEF-VSLICE` is reconciled completed in `BACKLOG.md`.

A read-only capability check also confirmed that stock ChatGPT Automations can provide exact recurring timezone-aware scheduling without Cloud Run, Apps Script, Linux, SQL, or another server. Existing live MIRA brief automations remain protected production and were not modified.

## Preserved checkpoints

- Android / `M2-M1-001` remains paused at the live isolated Google queued-writer proof point; synthetic command-boundary work remains intact.
- `DISCOVERY-CORE-001` remains partial; broader evidence-aware history/friction discovery is unfinished.
- `NONTECH-INSTALL-001` remains queued; bound Apps Script/provider setup is not part of this receipt packet.
- Receipt taxonomy, order/shipment lifecycle, spending/payment/reimbursement, assets/fitment, inventory/location/movement, groceries/meals, appointments, Microsoft/Apple lanes and provider-side raw-evidence archival remain separate accepted work. This packet does not silently complete them.

## Active packet

### `M2-M0-012` — Canonical no-app receipt intake + purchase history

- **Primary work:** `RECEIPT-INTAKE-001`
- **Primary features:** `RECEIPT-001`, `RECEIPT-002`
- **Related invariants/features:** `RECEIPT-003`, `ORDER-001`, `ORDER-002`, `ASSET-001`, `ASSET-003`, `SPEND-001`, `SHOP-001`, `STORE-001`, `RECOVERY-002`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `integration/m0-012-receipt-intake`
- **Base SHA:** `f96b227e009eb144235dccfef2ca0b8570e0801b`
- **PR:** #64
- **Last pre-closeout checkpoint SHA:** `cfd7ad2928614af29bdfcfadf3ec6e82d8195117`
- **Objective:** let stock-ChatGPT Personal MIRA persist normalized receipt/purchase evidence from authorized email-derived facts, user-supplied image/photo-derived facts, or user text as one canonical purchase record with exact money, stable identity, provenance fingerprints, conservative dedupe and queryable purchase history. This packet establishes purchase truth only; downstream side effects remain separate.

## Session-start alignment verification — 2026-08-29

### `FEATURES.md`

Verified before implementation:

- `RECEIPT-001` requires multi-source canonical receipt intake and evidence dedupe;
- `RECEIPT-002` requires searchable purchase history and connected receipt semantics;
- `RECEIPT-003` owns later taxonomy/classification rather than basic transaction truth;
- `ASSET-001` explicitly depends on `RECEIPT-001`, so receipt truth is a prerequisite for safe asset acquisition;
- `SPEND-001`, `ASSET-003`, `SHOP-001`, `GROCERY-001` and inventory work consume receipt truth without redefining it;
- `STORE-001` and `RECOVERY-002` remain the persistence/failure-isolation substrate.

### `BACKLOG.md`

Verified before implementation:

- `OPS-BRIEF-VSLICE` was completed by PR #63;
- `RECEIPT-INTAKE-001` was activated as one bounded vertical;
- receipt taxonomy, spending, assets, fitment, inventory/location/movement and provider-side archival remained separate unfinished work;
- Android remained paused.

### `ROADMAP.md`

Verified before implementation:

- M2-M0.5 requires continued no-app vertical progress after tasks/briefs;
- receipts/assets/inventory is explicitly part of that direction;
- packets must stay bounded instead of attempting the whole chain at once.

### Direction result

**ALIGNED.** Canonical receipt truth is a high-leverage no-app slice because assets, inventory and several later reconciliation features depend on trustworthy purchase identity.

## Implemented evidence

### Canonical receipt service

`mira/receipts.py` implements provider-neutral receipt/purchase state over `STORE-001`:

- resource type `receipt`, schema version 1;
- stable receipt ID and revision;
- integer minor-unit money only; floats are rejected;
- uppercase three-letter currency;
- decimal-string quantities with non-finite/negative values rejected;
- deterministic stable line IDs;
- source types `email`, `image`, `text`;
- SHA-256 evidence fingerprints plus optional source reference and offset-aware observation time;
- exact source replay is read-only when facts agree;
- same-source factual conflict fails closed;
- unique merchant/order or merchant/date/currency/total correlation may merge compatible new evidence;
- multiple plausible matches fail as ambiguous rather than choosing a row;
- explicit `distinct_transaction` permits two legitimate otherwise matching purchases while never bypassing exact source identity;
- new compatible evidence fills unknown optional facts without overwriting contradictions;
- explicit correction preserves the stable receipt ID;
- exact repeated correction whose desired state is already canonical is a zero-write semantic replay;
- purchase history filters by receipt ID, merchant, order number and date range and sorts newest-first deterministically;
- raw source content is not stored in structured receipt payloads.

### Side-effect boundary

Receipt capture does **not** automatically mutate:

- assets or fitment;
- inventory/location/movement;
- orders/shipments;
- spending/payment/reimbursement;
- groceries/pantry;
- Gmail labels/archive state;
- Drive receipt archives.

Those remain separate authorities/work packets with their own exact-readback requirements.

### Personal Google/no-app release wiring

The clean Personal starter now advertises:

`["authority","authority_binding","entity","onboarding_ledger","ops_brief_run","receipt","service_state","task"]`

The complete no-app operating instructions now require:

- `authority_binding/binding-receipt` -> `receipt`;
- canonical receipt money/evidence/identity rules;
- ambiguous/conflicting evidence fail-closed behavior;
- purchase-history query semantics;
- explicit correction on stable identity;
- the no-side-effect boundary above.

`mira.personal_distribution` validates the receipt-inclusive starter Metadata, while `mira.workspace_bundle` fails if required receipt safety clauses disappear.

### Direct tests and ownership

`tests/test_receipts.py` covers:

- email capture, exact money and stable line identity;
- exact source replay;
- exact source conflict;
- image evidence merge into the same canonical order;
- conflicting new evidence;
- explicit distinct same-core transactions plus later ambiguity detection;
- explicit correction and repeated correction replay;
- purchase-history filters/order;
- float money and invalid quantities;
- first-class text evidence and absence of raw source payloads.

`tests/test_workspace_bundle.py` and `tests/test_personal_distribution.py` directly verify receipt release clauses/schema.

`project/code_ownership.json` adds `canonical-receipts`, owning `mira/receipts.py` with direct `tests/test_receipts.py` evidence.

## CI evidence

Initial PR #64 CI run `33283965544` passed all repository/release/alignment/ownership gates but found one legitimate receipt-domain failure: repeating an already-successful explicit correction with the same logical idempotency key rebuilt the store fingerprint against the newer current revision and conflicted.

The fix recognizes an already-satisfied desired correction as a read-only semantic replay before asking the store to create another revision, while still validating the idempotency key.

CI run `33284061382` on fix head `eeefc1d5e84a8a3cecb58069e179fb39b8f426d9` passed:

- compile;
- feature registry;
- product lifecycle ledger;
- Personal starter distribution;
- work-session alignment;
- code ownership;
- all Python unit tests;
- all Workspace Apps Script tests.

Later commits add provider-proof documentation/lifecycle text only; the final closeout head still requires its own exact-head CI before merge.

## Independent Google provider proof — 2026-08-29/30

A brand-new native Google Sheet was created only for M2-M0-012 synthetic proof. It was not a copy of or write into legacy MIRA production receipt/order/inventory state.

### Clean substrate proof

Before inserting mutable proof state, exact readback confirmed:

- spreadsheet timezone `Etc/UTC`;
- tabs `Metadata`, `Resources`, `Events`, `Idempotency`;
- schema `mira-structured-state-v1`;
- `STORE-001`;
- `writer_model=single_writer`;
- receipt-inclusive resource type list exactly matching the Git-backed Personal starter;
- exact STORE-001 headers;
- zero mutable Resource/Event/Idempotency data rows.

### Authority/binding proof

Synthetic provider state then read back exactly:

- `authority/google-sheets-personal`, revision 1;
- `authority_binding/binding-receipt`, revision 1;
- binding `data_class=receipt` pointing to `google-sheets-personal`;
- matching idempotency operation, request hashes, result JSON and resource references.

No real account identity was committed; a synthetic owner token was used in proof state.

### Receipt revision 1

One fully synthetic tool-store purchase read back with:

- one stable `receipt` Resource ID;
- revision 1;
- exact integer total/subtotal/tax values;
- deterministic line ID and decimal-string quantity;
- one synthetic `email` evidence fingerprint/source reference;
- exact request hash and matching revision-1 idempotency result.

### Multi-source revision 2

The same Resource row was revision-checked to revision 2 with one additional synthetic `image` evidence observation.

Exact readback confirmed:

- same receipt ID, not a duplicate purchase;
- revision exactly 2;
- both email and image evidence observations retained;
- unchanged transaction facts and line identity;
- revision-2 request hash on the Resource row;
- both revision-1 and revision-2 receipt Idempotency rows retained with exact result JSON/resource references.

After proof, the spreadsheet was renamed to include `NOT A STARTER`. Its provider file ID and authenticated-account details are intentionally excluded from public Git.

Durable non-sensitive evidence: `docs/NO_APP_RECEIPT_PROVIDER_PROOF.md`.

This proof does **not** claim Gmail extraction, OCR/photo extraction quality, Drive archival, order/shipment state, assets, inventory, spending, reimbursement, groceries or background receipt processing are live.

## End-of-session alignment verification — 2026-08-29/30

### `FEATURES.md`

Rechecked after implementation:

- `RECEIPT-001` multi-source evidence/dedupe semantics are directly implemented/tested and provider-persistence proved for the bounded no-app receipt slice;
- `RECEIPT-002` purchase-history query semantics are directly implemented/tested;
- `RECEIPT-003` taxonomy remains unfinished;
- `ASSET-001` still depends on receipt truth and remains separate;
- `ASSET-002`, `ASSET-003`, `FITMENT-001`, `INV-001`, `LOC-001`, `MOVE-001`, `INV-002`, `SPEND-001`, `PAYMENT-001`, `REIMB-001`, `GROCERY-001`, `RECIPE-001`, `MEAL-001`, appointment/calendar, Android, Microsoft and Apple/iCloud scope remain preserved rather than falsely completed;
- no second receipt authority/data model was created.

### `BACKLOG.md`

Rechecked after implementation/provider proof:

- `RECEIPT-INTAKE-001` remains the only active work item until PR #64 merges;
- its code/tests/release wiring/provider proof are recorded complete, with exact-head closeout/merge still pending;
- downstream receipt taxonomy, spending, assets/fitment, inventory/location/movement and provider automation remain queued;
- Android remains partial/paused at its preserved checkpoint;
- the completed Ops Brief vertical remains completed rather than being reopened.

### `ROADMAP.md`

Rechecked after implementation:

- the packet advances M2-M0.5's explicit receipts/assets/inventory direction;
- it does not pull Android forward or make external infrastructure a prerequisite;
- it remains one bounded vertical instead of collapsing receipt, asset and inventory truth into a single untestable packet.

### Direction result

**ALIGNED.** MIRA now has canonical purchase truth ready to become the safe prerequisite for the next asset/inventory vertical, pending #64 exact-head CI and merge.

## Acceptance result

1. Provider-neutral Receipt service over STORE-001 — PASS.
2. Integer minor money / three-letter currency / float rejection — PASS.
3. Normalized decimal quantity validation — PASS.
4. Deterministic line/receipt identity — PASS.
5. Same-source read-only replay — PASS.
6. Same-source conflict fail closed — PASS.
7. Unique correlation merge and ambiguous-match failure — PASS.
8. Stable-ID explicit correction and repeated correction replay — PASS.
9. Deterministic purchase-history query — PASS.
10. Personal starter `receipt` + `binding-receipt` contract — PASS.
11. Complete no-app receipt/no-side-effect operating contract — PASS.
12. Direct receipt/release tests — PASS.
13. Deterministic Personal starter/Workspace validation — PASS.
14. Code ownership — PASS.
15. Exact final PR-head CI — PENDING this closeout commit.
16. Isolated Google receipt/binding/idempotency revision-1/revision-2 exact readback — PASS.
17. End-of-session whole-product preservation/alignment — PASS.

## Exact next action

1. Run CI on the exact PR #64 closeout head containing this checkpoint.
2. If every gate is green, merge PR #64 using exact expected head SHA.
3. Remotely verify `main` at the returned merge SHA.
4. In the next bounded packet, reconcile `RECEIPT-INTAKE-001` from active to completed with PR #64 merge evidence before selecting implementation work.
5. Dependency-rank the next no-app vertical. Default direction is the receipt -> asset -> inventory chain, beginning with the smallest canonical asset/acquisition slice that consumes receipt truth without yet swallowing location/movement/inventory; override only if FEATURES/BACKLOG/ROADMAP show a harder integrity prerequisite or the customer explicitly reprioritizes.
6. Keep Android paused unless explicitly reprioritized or no-app milestone evidence justifies resumption.

## Recovery protocol

Read this file first. If PR #64 is still open, verify its exact current head and exact-head CI before merge. If merged, verify `main`, reconcile the receipt backlog row to completed, then create exactly one next bounded packet from current `main`. Do not broaden from conversational memory and do not touch legacy receipt/order production state.
