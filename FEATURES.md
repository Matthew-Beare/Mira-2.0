# MIRA 2.0 FEATURES

This file is the human-readable canonical feature registry. It is populated and normalized through bounded forensic audit packets. Machine-readable dependency metadata may be added after stable IDs are assigned.

## Feature identity rule

Every durable feature receives a stable semantic ID. IDs do not change merely because roadmap priority or table position changes.

ID families include:

- `CORE-*` — MIRA control plane, canonical state, identity, reconciliation, provenance;
- `MIRROR-*` — companion reality database/state/evidence contracts;
- `OPS-*` — briefs, operational state, deployment-specific operations;
- `CTX-*` — user-selected operating-context models and context recommendation;
- `TRIP-*` — trip occurrence state and trip lifecycle;
- `ROUTE-*` — reusable route knowledge, directional routing and runtime/ETA behavior;
- `WEATHER-*` — context-aware weather and route-hazard gating;
- `MILE-*` — paid-mileage occurrences, pay calculations and mileage authority;
- `TASK-*` — task taxonomy, next actions and completion evidence;
- `RECOVERY-*` — run evidence, checkpoints, resumability, circuit breakers and failure isolation;
- `CAL-*` — calendar, appointments and appointment-window semantics;
- `REMIND-*` — reminder planning, medication reminder safety and sharing boundaries;
- `MAIL-*` — email triage, communication safety, evidence ingestion;
- `CAREER-*` — optional career/job monitoring and fit evaluation;
- `ORDER-*` — orders, fulfillment, shipments, replacements, returns, refunds and order-lifecycle evidence;
- `RECEIPT-*` — canonical purchase/receipt identity, evidence intake, history and classification;
- `SPEND-*` — evidence-bounded spending summaries and rollups;
- `PAYMENT-*` — expected merchant charges, settlement matching and financial exceptions;
- `REIMB-*` — beneficiary allocation and non-merchant reimbursement state;
- `SUB-*` — optional subscription/free-trial commitment tracking;
- `FIN-*` — complete connected financial-account ingestion and reconciliation;
- `ASSET-*` — physical asset identity, lifecycle evidence and asset graph behavior;
- `FITMENT-*` — explicit asset/equipment assignment, installation and compatibility relationships;
- `IDENT-*` — namespaced product/device identifiers and validation;
- `EVID-*` — retained multi-source evidence and enrichment behavior;
- `KNOW-*` — retained manuals/reference knowledge, knowledge identity and document relationships;
- `SPEC-*` — technical specifications, applicability and provenance;
- `SHOP-*` — active shopping/procurement intent and fulfillment reconciliation;
- `INV-*` — canonical inventory participation and query/projection behavior;
- `LOC-*` — hierarchical physical location identity and placement/observation semantics;
- `MOVE-*` — inventory movement events and scan-driven relocation workflows;
- `PAR-*` — target stock levels, observed quantity and optional sensing;
- `GROCERY-*` — grocery/pantry/freezer stock and shopping-list reconciliation;
- `RECIPE-*` — durable recipe identity, content and provenance;
- `MEAL-*` — dated meal-plan state and ingredient-gap reconciliation;
- `PROFILE-*` — onboarding, roles, family, customization, accessibility;
- `PROVIDER-*` — Google/Microsoft/Apple/storage/runtime portability;
- `CLIENT-*` — ChatGPT, Android, web, desktop, CLI and device surfaces;
- `DIST-*` — distribution, updates, releases, rollback;
- `ENTERPRISE-*` — locked-down/institutional deployment;
- `DEV-*` — development governance and resumability.

## Evidence levels

Each feature distinguishes requirement status from delivery evidence: `desired`, `specified`, `implemented`, `test_verified`, `integration_verified`, `live_verified`, and `rejected_or_superseded` when applicable. Code existence does not imply completion.

## Seed features established by MIRA 2.0 governance

### `DEV-001` — Git-authoritative development control plane
Git is authoritative for ROADMAP, FEATURES, BACKLOG, CURRENT_WORK, packet policy, and durable engineering decisions. Human dashboards may mirror Git one-way but cannot become independent truth.

**Evidence:** specified/implemented in MIRA 2.0 governance.

### `DEV-002` — Resumable bounded work packets
Development uses bounded packets with explicit acceptance criteria, dependencies, checkpoints and exact resume points. New ideas enter backlog by default; explicit reprioritization checkpoints displaced work first.

**Evidence:** specified/implemented in Project Instructions and project control files.

### `DEV-003` — Dependency-ranked backlog
Priority is recomputed from blockers, prerequisites, leverage, user-visible value and verification needs rather than FIFO arrival order.

**Evidence:** specified/implemented in BACKLOG governance.

### `CORE-001` — MIRA product identity
MIRA is the primary product, assistant and user-facing brand: **Modular Intelligence & Reasoning Assistant**.

**Evidence:** repository README, Project Instructions and branding spec.

### `MIRROR-001` — Companion reality database
MIRROR is MIRA's companion reality database containing durable structured facts, evidence, entities, state, provenance and relationships.

**Evidence:** README, Project Instructions and branding spec.

### `DATA-001` — Legacy production preservation
Legacy MIRA Google spreadsheets, Drive artifacts, briefs, schedules and automations are protected production data. MIRA 2.0 uses separate sandbox state until an explicit migration packet exists.

**Evidence:** Project Instructions and roadmap.

### `ONBOARD-001` — Full-replacement instruction delivery
MIRA supplies whole copy/paste replacement blocks plus nontechnical UI instructions whenever ChatGPT Project/Custom Instructions must change.

**Evidence:** Project Instructions; onboarding implementation pending audit/design.

### `BRAND-001` — Canonical MIRA brand asset system
Canonical vector masters drive symbol, wordmark, lockups, banners, adaptive icon and generated platform derivatives.

**Evidence:** `docs/BRAND_ASSET_SPEC.md`; artwork/integration pending.

## Audited operational features

### `OPS-001` — Canonical twice-daily Ops Brief schedule
**Description:** Exactly two scheduled brief opportunities at 02:45 and 14:45 in named IANA timezone `America/New_York`; device/travel/session timezone and fixed UTC offsets do not reinterpret them. Manual invocation is separate.

**Requirement:** required. **Evidence:** `test_verified` runtime slot semantics; live MIRA 2.0 scheduler/firing unverified. **Dependencies:** named-timezone scheduler/readback, `OPS-003`, `OPS-004`. **Legacy evidence:** runtime/brief policy/tests and PR #31 `MIRA-F009`. **Verification boundary:** provider readback plus observed AM/PM canonical firings.

### `OPS-002` — Single canonical dispatcher and prohibited duplicate schedules
**Description:** One canonical dispatcher rather than parallel legacy/retry/child/diagnostic/shifted duplicates; compatible scheduled work consolidates when safe.

**Requirement:** required. **Evidence:** specified; provider uniqueness unverified. **Dependencies:** `OPS-001`, provider enumeration/readback.

### `OPS-003` — Canonical runtime clock gate with DST-safe slot matching
**Description:** Runtime-owned offset-aware clock converted through IANA timezone rules decides bounded scheduled entry; model/device/travel clocks are not authority.

**Requirement:** required by failure evidence. **Evidence:** `test_verified`; live scheduler path unverified. **Dependencies:** runtime clock/timezone DB, `OPS-001`.

### `OPS-004` — Fresh standalone run delivery with deterministic Run ID
**Description:** Each scheduled brief starts fresh and uses deterministic `OPS-YYYY-MM-DD-AM|PM` identity for output and idempotent Run Log updates.

**Requirement:** required. **Evidence:** `test_verified` ID generation; live standalone delivery unverified. **Dependencies:** `OPS-003`, `RECOVERY-001`, scheduler fresh-run capability.

### `OPS-005` — Deterministic HOME/ROAD context with explicit overrides
**Description:** Base HOME/ROAD state comes from canonical weekly transitions and explicit override records; generalized context and active Trip forcing remain separate capabilities.

**Requirement:** required. **Evidence:** `test_verified`; MIRA 2.0 state integration unverified.

### `CTX-001` — Configurable operating-context pairs
**Description:** MIRA supports two-label operating contexts such as HOME/ROAD, HOME/TRUCK, HOME/FIELD, HOME/CAMPUS, HOME/AWAY and custom labels; HOME/OFFICE is valid through custom configuration.

**Requirement:** accepted direction. **Evidence:** `test_verified` legacy router candidate; MIRA 2.0 integration unverified.

### `CTX-002` — Evidence-gated context recommendation and explicit activation
**Description:** Job/duties may recommend context but never silently enable it; confirmation/user labels control activation and ambiguity remains unresolved.

**Requirement:** required. **Evidence:** `test_verified` legacy router candidate; MIRA 2.0 onboarding/readback unverified.

### `TRIP-001` — Independent trip occurrence lifecycle
**Description:** Trip occurrences are separate from reusable Route knowledge, context and paid mileage, with stable identity and Planned/Active/Arrived/Cancelled lifecycle.

**Requirement:** required. **Evidence:** `test_verified` legacy separation/precedence; MIRA 2.0 persistence unverified.

### `ROUTE-001` — Learned routes, directional runtime, location and ETA inference
**Description:** Reusable Route knowledge is separate from Trip occurrences; supports directional route/runtime, runtime-derived ETA, location evidence and bounded progress primitives.

**Requirement:** required. **Evidence:** `test_verified` for route-average ETA/primitives; human-facing ahead/behind and MIRA 2.0 integration unverified.

### `WEATHER-001` — Context-gated HOME and ROAD weather intelligence
**Description:** HOME permits relevant home weather; ROAD may activate bounded route/corridor weather and official road-condition checks tied to Trip/watch state.

**Requirement:** required. **Evidence:** `test_verified` deterministic gates/expiry; external NWS/DOT/511 unverified in MIRA 2.0.

### `MILE-001` — Company-paid mileage and deterministic gross-pay reporting
**Description:** MIRA reports company-paid miles, not map/odometer distance, and computes gross estimate from verified rate. Both Thursday brief slots report the closed cycle with explicit status/correction/missing-evidence handling.

**Requirement:** required. **Evidence:** `test_verified`; MIRA 2.0 persistence/live Thursday delivery unverified.

### `MILE-002` — Separate authoritative Miles & Pay tracker
**Description:** Mileage/pay state lives in a dedicated logical authority preserving stable occurrences, pay-week history, paid miles, rate, gross, provenance/status and corrections; storage backend is an adapter.

**Requirement:** required. **Evidence:** legacy live authority exists; MIRA 2.0 sandbox authority unverified.

### `TASK-001` — Structured task hierarchy and one-action-per-item rendering
**Description:** Stable Task identity plus priority → classification → optional subsystem → task; each action remains an independent canonical record/bullet with context/window-driven actionability.

**Requirement:** required. **Evidence:** `test_verified`; MIRA 2.0 persistence unverified.

### `TASK-002` — Evidence-grounded next actions and honest completion state
**Description:** Smallest useful next actions derive from canonical open work, deadlines, prerequisites, blocks and context. Partial/completed/missed/removed/blocked state follows evidence; silence never means Done.

**Requirement:** accepted/integrity rule. **Evidence:** specified/skill workflow; generic cross-domain engine not yet test-verified.

### `RECOVERY-001` — Phase-aware Run Log, durable checkpoints and circuit-breaker recovery
**Description:** Durable run/recovery evidence uses stable Run IDs, phase/status/health/mutation evidence, bounded retries and verified-state preservation/readback with a specific recovery action.

**Requirement:** required. **Evidence:** `test_verified` core Run Log/selected degradation paths; broader circuit-breaker strongly specified; MIRA 2.0 live scheduled evidence unverified.

### `RECOVERY-002` — Explicit module dependency boundaries and failure isolation
**Description:** Modules/authorities remain separate failure domains unless an explicit shared dependency exists. Optional failure degrades only the affected module; canonical source state survives downstream projection failure and can re-drive a failed target later.

**Requirement:** required. **Evidence:** `test_verified` representative legacy boundaries; MIRA 2.0 cross-provider isolation unverified.

## Category A consistency result

Category A is complete. Scheduling, context, Trip, Route, mileage, task and recovery authorities are explicitly separated. `TASK-002` remains below test-verified pending dedicated generic tests.

## Audited calendar/reminder and communication features

### `CAL-001` — Saturday AM seven-day appointment lookahead
**Description:** Saturday 02:45 AM includes Saturday-through-Friday appointments, slot-based and mode-independent. **Requirement:** required. **Evidence:** `test_verified`; live Calendar integration unverified.

### `CAL-002` — Day-before and morning-of appointment reminders
**Description:** Deterministic day-before/morning-of coverage with cancelled/disabled suppression, equal-time dedupe and no late reminder. **Requirement:** required. **Evidence:** `test_verified`; projection/delivery unverified.

### `CAL-003` — Configurable relative appointment reminder, default one hour before
**Description:** Configurable pre-event reminder, default 60 minutes, with invalid interval rejection and dedupe. **Requirement:** required. **Evidence:** `test_verified`; delivery unverified.

### `REMIND-001` — Evidence-gated medication reminders
**Description:** Default-off reminders from explicitly confirmed owner/label/pharmacy/clinician schedule only; no dose/timing inference or missed-dose advice. **Requirement:** safety required. **Evidence:** `test_verified`; MIRA 2.0 delivery unverified.

### `REMIND-002` — Explicit opt-in caregiver reminder sharing
**Description:** User-only by default; explicit sharing activation and recipient identity required. **Requirement:** safety required. **Evidence:** gate `test_verified`; recipient/provider delivery unverified.

### `CAL-004` — Context-aware appointment visibility without fabricated confirmation state
**Description:** Deterministic appointment presentation must not invent acknowledgement/confirmation state. **Requirement:** required. **Evidence:** window/isolation logic test-verified, hidden-confirmation rule specified; provider integration unverified.

### `MAIL-001` — Evidence-grounded important-mail triage
**Description:** Bounded material mail triage across work/school/jobs/financial/medical/vendor/security domains, reading relevant threads before conclusions. **Requirement:** required. **Evidence:** specified workflow; general classifier not test-verified.

### `MAIL-002` — Explicit per-message approval for outbound contact
**Description:** MIRA may research/draft but never send/contact without explicit approval for the exact recipient/message/attachments, with no-reply validation and fresh approval after material change. **Requirement:** safety invariant. **Evidence:** specified; provider send-gate tests/integration pending.

### `MAIL-003` — Explicit archive-approval queue with repeat-on-silence
**Description:** Important mail stays pending until explicit approval; silence is never approval. **Requirement:** required. **Evidence:** specified; provider archive readback unverified.

### `CAREER-001` — Optional qualified job watch with realistic fit filtering
**Description:** Optional user-configured job monitoring evaluates mandatory versus preferred qualifications against canonical candidate settings, deduplicates results and never applies/contacts automatically. **Requirement:** legacy personal service, optional general product. **Evidence:** specified; dedicated fit-engine tests/provider integration unverified.

## Category B consistency result

Category B is complete. Appointment visibility, reminder safety, mail triage, archive permission, outbound-contact permission and optional career monitoring remain distinct authority/permission boundaries.

## Audited fulfillment and receipt/financial features

### `ORDER-001` — Evidence-grounded order and carrier correlation
**Description:** Mail/carrier/vendor/owner evidence is normalized and matched by strong identity/precedence; ambiguity causes no mutation. **Requirement:** required. **Evidence:** `test_verified` matching core; provider collection/MIRA 2.0 integration unverified.

### `ORDER-002` — Canonical ordered-to-delivered fulfillment lifecycle with active dedupe
**Description:** Active fulfillment projection tracks nonterminal packages with stable identity; Delivered is durable history and leaves active state. **Requirement:** required. **Evidence:** `test_verified`; provider readback unverified.

### `ORDER-003` — Explicit cancellation, return, refund and no-settlement lifecycle
**Description:** Cancellation/return/settlement/refund are separate facts, including no-settlement and expected correction states. **Requirement:** required. **Evidence:** cancellation and financial-resolution cores `test_verified`; full cross-authority integration unverified.

### `ORDER-004` — Replacement and supersession without duplicate spend
**Description:** Same-order revision preserves one Receipt ID; true replacement gets linked distinct IDs without copying financial totals or double-counting spend. **Requirement:** required. **Evidence:** shipment replacement core test-verified; full purchase graph specified/integration unverified.

### `ORDER-005` — Active-only fulfillment brief and stale-shipment escalation
**Description:** Brief shows only active fulfillment and one-time delivery events; five-business-day no-progress escalation is required. **Requirement:** required. **Evidence:** active/delivery semantics supported; stale-shipment timer lacks dedicated executable/test and is queued as `ORDER-STALE-001`.

### `RECEIPT-001` — Multi-source canonical receipt intake and evidence dedupe
**Description:** Email/file/photo/chat/manual evidence enriches one Receipt ID with provenance rather than creating shadow purchases; OCR is candidate evidence. **Requirement:** required. **Evidence:** normalized evidence core test-supported, provider ingestion specified; MIRA 2.0 integration unverified.

### `RECEIPT-002` — Searchable expandable purchase history and connected receipt graph
**Description:** Receipt-, asset- and identifier-origin queries return the same connected evidence graph; UI is a projection. **Requirement:** required. **Evidence:** graph core `test_verified`; MIRA 2.0 UI/provider readback unverified.

### `SPEND-001` — Evidence-bounded monthly spending rollup
**Description:** Monthly receipt/email-derived totals dedupe one transaction and state coverage limitations; never claim complete finances without complete account coverage. **Requirement:** required. **Evidence:** specified; dedicated rollup tests pending.

### `RECEIPT-003` — Generic configurable receipt taxonomy and line classification
**Description:** Generic/configurable line-item categories support mixed receipts and ambiguity queues without private-user defaults. **Requirement:** accepted/downstream prerequisite. **Evidence:** specification-level; implementation queued.

### `PAYMENT-001` — Expected merchant charge and settlement reconciliation
**Description:** One payment case per Receipt ID/current merchant outcome tracks pending, matched, split, over/undercharge, refund/reversal, no-settlement and ambiguity separately from purchase history. **Requirement:** accepted/financial-integrity. **Evidence:** deterministic core `test_verified`; account-provider integration unverified.

### `REIMB-001` — Beneficiary allocation and household reimbursement reconciliation
**Description:** Gross merchant purchase remains intact while separate beneficiary allocations/reimbursement state determine net household cost; reimbursement is not merchant refund or revenue. **Requirement:** accepted. **Evidence:** strongly specified; deterministic engine/tests queued.

### `SUB-001` — Optional subscription and free-trial tracking
**Description:** Optional/default-off recurring commitment tracking with evidence-backed renewal/trial dates, dedupe, no per-subscription scheduler and no automatic cancel/contact. **Requirement:** proposed/optional. **Evidence:** historical paused concept only; no current implementation.

### `FIN-001` — Complete connected financial-account ingestion and reconciliation
**Description:** Future authorized account ingestion would preserve account/transaction identity, coverage/sync boundaries, pending/posted/debit/credit/transfer semantics and privacy while corroborating rather than replacing receipts/payments. **Requirement:** proposed/infrastructure-deferred. **Evidence:** not present as complete repository capability.

## Category C consistency result

Category C is complete. Fulfillment, purchase identity, bounded spending, merchant settlement, reimbursement, optional subscriptions and future complete finances are separate authorities. Open implementation gaps remain ranked; no MIRA 2.0 integration/live evidence is inherited from legacy providers.

## Audited asset identity and evidence features

### `ASSET-001` — Immutable physical asset identity and idempotent acquisition

**Description:** Every physical asset receives one immutable canonical RFC 4122 Entity UUID. Display names, friendly Asset IDs, owner, category, location, project, backend, receipt enrichment and lifecycle changes are attributes or relationships and never replace the Entity UUID. Asset creation deduplicates by source identity and supported evidence. Replaying the same source preserves the same UUID; enrichment updates attributes without creating a second asset. Set/lot tracking may represent quantity greater than one under one asset UUID when individual serial-level tracking is not useful, while `individual` tracking requires quantity one. Cancelled/removed-before-settlement receipt lines cannot manufacture inventory assets.

**Why it exists / user outcome:** The same physical thing stays the same thing through receipts, moves, repairs, renames and future database migrations instead of collecting new identities every time another subsystem touches it.

**Requirement status:** `required`.

**Delivery/evidence:** `test_verified` in the legacy deterministic inventory reconciler for canonical UUID validation/allocation, source dedupe, idempotent replay, enrichment without UUID replacement, quantity/tracking rules, excluded receipt lines, UUID collision handling and source replay refusing Entity UUID replacement. **MIRA 2.0 canonical asset persistence/provider readback remains unverified.**

**Hard dependencies:** canonical MIRROR entity authority; stable source identity/provenance; `RECEIPT-001` when acquisition originates from purchase evidence; explicit migration/alias semantics for true duplicate consolidation.

**Enables:** fitment relationships, maintenance/warranty history, inventory location/movement, QR/RFID identity, asset search and backend migration.

**Legacy evidence:** category-D row 1; `asset-acquisition.md` immutable identity contract; `inventory_reconciliation.py`; `test_inventory_reconciliation.py` UUID/replay/enrichment/exclusion/collision tests.

**Acceptance / verification boundary:** Preserve deterministic identity tests, then MIRA 2.0 sandbox must create/read back an asset, replay/enrich the same source without replacing UUID, and prove a backend/projection change does not create a second authority.

---

### `FITMENT-001` — Explicit assignment, installation and fitment relationships

**Description:** Vehicle/equipment/tool applicability is represented through explicit relationship records with their own immutable UUIDs, endpoint Entity UUIDs, relationship type/status and source/evidence provenance. `assigned_to` means intended/canonical allocation; it does not imply physical installation. `installed_on` requires supported installation evidence. `used_with`, replacement and other supported relationships remain semantically distinct. Unknown endpoints, self-links, duplicate source identities and identity collisions fail closed. Automotive part fitment may be inferred only when part/application evidence uniquely resolves against known assets/modifications; material ambiguity is queued rather than guessed.

**Why it exists / user outcome:** MIRA can know that a tire set is assigned to a wheel set and that a wheel set belongs with a vehicle without claiming the tires are physically installed today or attaching a part to the wrong car because its dimensions looked plausible.

**Requirement status:** `required`.

**Delivery/evidence:** the explicit relationship core is `test_verified` for creation, replay, endpoint validation, self-link rejection and the `assigned_to` versus `installed_on` distinction. The broader automatic automotive fitment-resolution workflow is strongly `specified` but does not have a dedicated audited deterministic fitment-engine suite sufficient for full-feature `test_verified` status.

**Hard dependencies:** `ASSET-001`; stable relationship identity; evidence/provenance; exact part/identifier information when automatic fitment is attempted; canonical known-asset registry.

**Enables:** item-to-vehicle/tool assignment, installed-part history, fitment-aware shopping/receipts and bidirectional asset queries.

**Legacy evidence:** category-D row 1; `asset-acquisition.md`; `receipt-classification-fitment.md`; `inventory_reconciliation.py`; `test_inventory_reconciliation.py` assignment creation/replay, unknown-target, self-link and “assignment does not claim physical installation” fixtures.

**Acceptance / verification boundary:** Relationship semantics remain test-covered. Before automatic fitment inference is promoted, add deterministic multi-vehicle/ambiguous/exclusion/modification fixtures and prove unsupported fitment remains queued. Integration verification requires sandbox relationship write/readback against stable asset endpoints.

---

### `ASSET-002` — Provenance-linked asset acquisition, reference and lifecycle evidence

**Description:** Asset identity can link to exact purchase/receipt lines, retained manuals/service documents, warranties/support evidence, maintenance/service facts and verified technical specifications without duplicating or replacing the asset itself. Cross-authority links use stable Receipt, Entity, Knowledge, Evidence and Specification IDs plus source identity/readback. A failed receipt/manual/warranty projection does not erase a verified physical asset; similarly, a manual may remain canonical while its asset relationship waits for later reconciliation. Replacement/returned/disposed state is lifecycle history rather than deletion of identity.

**Why it exists / user outcome:** One asset becomes the durable place to reach the evidence needed to own, service, support or sell it instead of scattering the purchase, manual, warranty and specifications across unrelated folders and chats.

**Requirement status:** `accepted / required direction`.

**Delivery/evidence:** normalized purchase/evidence, retained Knowledge relationships and specification records are implemented/test-supported by the legacy evidence core, including exact source identity and knowledge/spec cross-validation. Warranty and maintenance lifecycle depth are primarily `specified` in the audited policy rather than represented by a dedicated deterministic warranty/maintenance engine. Dedicated exact technical-specification provenance rules are audited separately in D2.

**Hard dependencies:** `ASSET-001`; `RECEIPT-001`; retained evidence/Knowledge authorities; stable relationship IDs; future D2 specification provenance feature for safety-critical verified values.

**Enables:** warranty/support retrieval, maintenance history, manuals, asset browser evidence, specifications and lifecycle reporting.

**Legacy evidence:** category-D row 2; `asset-acquisition.md`; `asset_evidence.py` Evidence/Knowledge/Knowledge Relationships/Specifications collections and cross-validation; `test_asset_evidence.py` retained manual, knowledge relationship and specification fixtures.

**Acceptance / verification boundary:** MIRA 2.0 sandbox must link a synthetic asset to a receipt line and retained document/evidence with independent readback. Full warranty/maintenance implementation credit requires deterministic state/event tests rather than inference from generic evidence support.

---

### `ASSET-003` — Bidirectional receipt, asset and identifier graph queries

**Description:** MIRA uses one connected graph to answer from an exact Receipt ID, Entity UUID or namespaced identifier. The resulting query returns the same connected assets, relevant explicit relationships, receipt IDs, evidence, identifiers, Knowledge links and specifications regardless of which supported selector started the query. Relationship traversal excludes general `owned_by` as a graph-expansion edge so asking about one vehicle does not accidentally return every asset owned by the same person. User-facing Receipt Browser and Asset Browser are projections over this graph, not separate mutable databases.

**Why it exists / user outcome:** The user can start from “this receipt,” “this vehicle,” or “this serial/SKU” and reach the same evidence-backed reality.

**Requirement status:** `required`.

**Delivery/evidence:** `test_verified` in the deterministic legacy graph-query core. Tests prove receipt and vehicle selectors return the same connected entity set and identifier queries reach the same receipt/assets while excluding unrelated household-owned assets. **MIRA 2.0 provider/UI projection remains unverified.**

**Hard dependencies:** `ASSET-001`; `FITMENT-001`; `RECEIPT-001`; `IDENT-001`; canonical relationship/evidence graph.

**Enables:** Receipt Browser, Asset Browser, fitment/support lookup, warranty/manual/spec retrieval and future mobile scanning workflows.

**Legacy evidence:** category-D row 3; `asset-acquisition.md` bidirectional query contract; `asset_evidence.py` `query_graph`; `test_asset_evidence.py` receipt/vehicle/identifier query fixtures.

**Acceptance / verification boundary:** Keep deterministic graph equivalence tests, then sandbox integration must persist/read back the graph and prove UI/provider queries do not create a second authority.

---

### `IDENT-001` — Namespaced product and device identifiers with collision safety

**Description:** MIRA preserves exact printed identifier values and deterministic normalized search values for UPC-A, EAN/GTIN variants, merchant/vendor SKU, manufacturer part number, model number, serial number, IMEI and MAC address. UPC/GTIN leading zeroes are retained and check digits validated. IMEI uses Luhn validation; MAC formatting is normalized/validated. Merchant SKU, manufacturer part/model and serial identifiers require an explicit namespace so numeric-looking local IDs are not mislabeled as global barcodes. Verified/observed serial-level identifiers such as serial number, IMEI and MAC cannot belong to two different entities under the same namespace.

**Why it exists / user outcome:** A number means what its source says it means. MIRA should not turn a retailer SKU into a UPC, drop a leading zero, or attach the same serial number to two tools because string matching felt optimistic.

**Requirement status:** `current required`.

**Delivery/evidence:** `test_verified` for GTIN/UPC check digits/leading zeros, IMEI/MAC validation, required namespaces, unique serial-level collision rejection, evidence/entity consistency and immutable identifier/source identity rules.

**Hard dependencies:** `ASSET-001`; `EVID-001`; canonical namespace/source identity rules.

**Enables:** asset dedupe, barcode lookup, exact part/model matching, serial-level warranty/service history, device identity and scan workflows.

**Legacy evidence:** category-D row 4; `asset_evidence.py` identifier types/normalization/validation; `test_asset_evidence.py` UPC, IMEI, MAC, namespace and serial-collision fixtures; `asset-acquisition.md` identity-resolution rules.

**Acceptance / verification boundary:** Preserve deterministic validation/collision tests; MIRA 2.0 integration requires sandbox identifier write/readback and provider/search round-trip without changing source value or namespace.

---

### `EVID-001` — Multi-source asset evidence enrichment without identity replacement

**Description:** Product, barcode, serial-plate, receipt and other photos; Gmail/merchant evidence; manuals/manufacturer pages; and explicit owner confirmation may enrich an existing asset/evidence graph. Each evidence object has stable Evidence UUID, source authority/record identity, retained locator or content hash where applicable, capture/status metadata and exact Entity/Receipt/line linkage. Images are inspected directly before OCR fallback. OCR/barcode decoding is extraction candidate evidence, not truth: it cannot silently replace verified model/serial/identifier facts. Replaying the same source is idempotent, and later stronger evidence updates or supersedes facts on the same canonical Entity UUID rather than creating a duplicate asset.

**Why it exists / user outcome:** Taking a serial-plate photo or receiving a better merchant email should make MIRA know more about the same object, not create a second copy of the object or overwrite a verified serial with an OCR hallucination.

**Requirement status:** `current required`.

**Delivery/evidence:** the provider-neutral evidence normalization/reconciliation core is `test_verified` for source-identity dedupe, idempotent replay, retained-source requirements, unknown/cross-entity evidence rejection and immutable source identity. Gmail/image/OCR/provider acquisition flows are `specified` workflows; actual MIRA 2.0 provider integration/readback is unverified.

**Hard dependencies:** `ASSET-001`; stable Evidence IDs/source identity; retained file/evidence storage where used; `IDENT-001` for identifier enrichment; `RECOVERY-002` for provider failure isolation.

**Enables:** product identification, serial/barcode enrichment, receipt/asset linking, manual/spec lookup and later Android camera/scanner capture.

**Legacy evidence:** category-D row 5; `asset-acquisition.md`; `receipt-photo-intake.md`; `asset_evidence.py`; `test_asset_evidence.py` source/idempotency/evidence-link/cross-entity tests.

**Acceptance / verification boundary:** Keep deterministic evidence replay/cross-link tests; integration verification requires synthetic photo/mail/manual evidence to enrich one sandbox Entity UUID with source readback while OCR ambiguity remains candidate/unresolved rather than verified.

## Category D1 consistency findings

- Asset identity (`ASSET-001`) is not fitment (`FITMENT-001`); fitment is an explicit relationship and cannot replace identity.
- `assigned_to` and `installed_on` remain distinct evidence claims.
- Asset reference/lifecycle evidence (`ASSET-002`) can degrade independently from the verified physical asset; warranty/maintenance depth remains below the stronger evidence-core tests.
- Bidirectional query (`ASSET-003`) has genuine deterministic graph evidence and excludes ownership as a broad join.
- `IDENT-001` is strongly test-verified and preserves namespace/global-identifier semantics.
- `EVID-001` provider-neutral reconciliation is test-verified; actual Gmail/photo/OCR provider ingestion is not MIRA 2.0 integration-verified.
- Dedicated safety-critical technical-spec provenance is intentionally left for D2 rather than being smuggled into D1's broader evidence umbrella.

## Audited knowledge, specification, shopping, inventory-identity and location features

### `KNOW-001` — Canonical manual/reference knowledge identity and retained-document lifecycle

**Description:** Manuals, service manuals, datasheets, bulletins and other durable references are canonical Knowledge objects with immutable RFC 4122 Knowledge UUIDs, source identity, document type, manufacturer/model/part metadata, revision/edition, source URL, retained-file identity and status. A chat upload, email attachment, URL and Drive copy may be evidence paths to the same Knowledge UUID rather than separate documents. Manufacturer/OEM sources are preferred when available. Lookup/download states such as `lookup_queued`, `download_blocked`, `unavailable`, `no_match` or equivalent must remain honest; a failed download cannot be called retained. In the current Google-backed architecture, `retained` requires the canonical Drive file identity/URL plus an explicit version/revision where applicable. Asset/receipt/project links are downstream relationships from the verified Knowledge UUID and may degrade without deleting or duplicating the retained document.

**Why it exists / user outcome:** MIRA should be able to find the actual manual again, know which revision it is, and link it to the correct asset without treating a filename or chat upload as durable knowledge.

**Requirement status:** `current required`.

**Delivery/evidence:** the provider-neutral Knowledge record/status/relationship core is `test_verified` for retained-file/revision requirements, queued-without-retention behavior, immutable source/UUID reconciliation, unknown Knowledge-link rejection and explicit lookup status progression. The Drive download/file/index workflow is strongly `specified`; MIRA 2.0 Drive write/readback is not integration-verified.

**Hard dependencies:** durable knowledge/file authority; `EVID-001`; explicit source identity; `ASSET-001` only when asset linkage is required; `RECOVERY-002` for provider/relationship failure isolation.

**Enables:** manuals on demand, asset support/service references, exact source lookup for `SPEC-001`, migration to later object storage without changing Knowledge identity.

**Legacy evidence:** category-D row 6; `knowledge-manual-ingestion.md`; `asset_evidence.py` Knowledge/Knowledge Relationship/Lookup collections; `test_asset_evidence.py` retained manual, queued manual, unknown Knowledge relationship and lookup-state fixtures.

**Acceptance / verification boundary:** Preserve deterministic record/state tests. MIRA 2.0 integration verification requires synthetic manual discovery, retained Drive file plus Knowledge index readback, idempotent replay preserving Knowledge UUID, and independent handling of a failed asset relationship.

---

### `SPEC-001` — Provenance-locked technical specifications with exact applicability

**Description:** Technical specifications are separate evidence-backed records tied to an exact subject Entity UUID and applicability statement. Safety-critical values such as torque, tire pressure, fluid capacity/specification, alignment and load limits may be `verified` only when supported by OEM/manufacturer/authoritative-regulatory evidence, an exact source URL or retained Knowledge UUID, page/section locator and relevant revision/version. Owner memory, chat recollection, OCR text or a generic web result may remain candidate evidence but cannot silently become verified. Verified value/applicability/source fields are immutable except through an explicit supersession/correction event so a later scrape cannot rewrite a safety-critical fact in place.

**Why it exists / user outcome:** MIRA can answer “what is the torque spec for this exact configuration?” without quietly applying an STI, another model year, another transmission or someone’s forum recollection to the wrong machine.

**Requirement status:** `current required`.

**Delivery/evidence:** `test_verified` for authoritative source-tier enforcement, required source locator, source URL/Knowledge linkage, unknown Knowledge rejection, exact subject binding and refusal to silently mutate a verified specification. MIRA 2.0 provider/document retrieval and live readback remain unverified.

**Hard dependencies:** `ASSET-001` subject identity; `KNOW-001` or another authoritative source locator; `EVID-001`; explicit applicability/version semantics.

**Enables:** safe service answers, maintenance planning, fitment decisions and evidence-grounded technical support.

**Legacy evidence:** category-D row 7; `knowledge-manual-ingestion.md`; `asset_evidence.py` Technical Specifications validator; `test_asset_evidence.py` verified-source/provenance/immutability fixtures.

**Acceptance / verification boundary:** Preserve deterministic provenance tests; sandbox integration must retain/read back an authoritative synthetic/manual-derived specification and reject a candidate owner-memory/OCR value from promotion without the required provenance.

---

### `SHOP-001` — Active shopping intent distinct from durable purchase history

**Description:** `Shopping & Procurement` represents only open procurement intent and is not a purchase ledger, shipment queue, asset registry or spend authority. A shopping intent has its own stable identity, requested item/purpose/target asset or fitment when known, status and provenance. Supported purchase evidence or explicit owner confirmation may fulfill the intent, but the durable purchase remains under `RECEIPT-*`/`ORDER-*`; after verified reconciliation the active shopping row is removed/closed without creating a `Purchased` shadow ledger or duplicate spend. Same-order revisions and true replacement transactions satisfy one underlying intent when appropriate. Cancellation without replacement does not fulfill an still-wanted intent. Partial fulfillment closes only the supported divisible portion. Ambiguous matches remain open/reviewable rather than being closed by category similarity.

**Why it exists / user outcome:** “I need brake pads” and “I bought these brake pads” are related facts, not the same database row pretending to be both a to-do list and accounting system.

**Requirement status:** `accepted`.

**Delivery/evidence:** strongly `specified` in receipt/shopping reconciliation policy, including source-first purchase commit, exact matching, removal/readback and failure isolation. The forensic audit did not locate a dedicated deterministic shopping-intent reconciliation engine/test suite sufficient for `test_verified` status. PR #31 contains broader product/client candidates but does not supersede this evidence ceiling.

**Hard dependencies:** stable shopping-intent identity; `RECEIPT-001`/`ORDER-*` purchase evidence; `FITMENT-001` where target compatibility matters; provider/list readback for mutation.

**Enables:** shopping list, procurement planning, replacement-aware fulfillment, household/grocery linkage without duplicate spend.

**Legacy evidence:** category-D row 8; `receipt-ingestion.md` Shopping & Procurement reconciliation contract.

**Acceptance / verification boundary:** Add deterministic fixtures for exact/ambiguous matching, owner-confirmed fulfillment without receipt identity, cancellation, replacement, partial fulfillment, idempotent replay and target-row deletion/readback. Sandbox integration must prove a fulfilled shopping intent disappears from active state while one canonical purchase remains.

---

### `INV-001` — Inventory participation reuses canonical Entity UUID identity

**Description:** Inventory is a state/projection over canonical physical entities, not a second identity namespace. A physical object or tracked set/lot that enters inventory keeps the immutable Entity UUID from `ASSET-001`; specialized tool/household/inventory views expose that UUID rather than assigning a competing primary identity. Friendly stock IDs, QR labels, shelf labels, serials and vendor codes are aliases/identifiers. Set/lot quantity may remain one Entity UUID when individual tracking is not useful; individually tracked physical units require distinct canonical Entity UUIDs. Location, movement, ownership, category, count and presentation changes never renumber the entity.

**Why it exists / user outcome:** The drill on the receipt, the drill on the shelf, the drill behind a QR code and the drill in a maintenance record remain the same drill.

**Requirement status:** `accepted / foundational prerequisite`.

**Delivery/evidence:** the immutable UUID and inventory-acquisition core is `test_verified` through `ASSET-001`; therefore the no-second-inventory-identity rule is supported by executable identity behavior. Specialized MIRA 2.0 inventory persistence/UI and legacy inventory migration are not integration-verified. This feature does not claim QR movement or location-event behavior, which belongs to later D packets.

**Hard dependencies:** `ASSET-001`; canonical MIRROR entity authority; explicit set/lot versus individual tracking semantics.

**Enables:** `LOC-001`, QR/barcode movement, queryable household/shop inventory, par levels, maintenance and migration without identity duplication.

**Legacy evidence:** category-D row 9; `asset-acquisition.md`; `inventory_reconciliation.py`; `test_inventory_reconciliation.py`; PR #31 inventory code only as unmerged reference for later projections.

**Acceptance / verification boundary:** MIRA 2.0 sandbox must expose the same Entity UUID through asset and inventory views, reject a second primary inventory UUID for the same physical entity, and preserve identity across category/location changes.

---

### `LOC-001` — Hierarchical locations with intended placement separate from observed/last-moved state

**Description:** MIRA models physical locations as stable hierarchical entities such as site/building/room/zone/aisle/shelf/bin/container, with explicit parent relationships and cycle protection. Containers may themselves be movable physical assets while exposing a child location for their contents. Location semantics distinguish at least (a) the intended/canonical home or storage placement for an item and (b) the latest supported observed/moved-to location/evidence. A move/scan observation updates movement/current-observation state but must not silently redefine the intended home location; changing intended placement is an explicit decision. Conversely, an intended shelf does not prove the item is physically there now. The model should support practical household/shop granularity without requiring absurd per-cut/per-piece tracking where it adds no value.

**Why it exists / user outcome:** MIRA can answer both “where does this belong?” and “where was it last put?” without erasing one answer every time the other changes.

**Requirement status:** `required / under active design`.

**Delivery/evidence:** the intended-versus-last-moved semantic remains `specified` and is not yet test-verified. PR #31 contains substantial unmerged `inventory_hierarchy.py` candidate code for nested location paths, container-location linkage, move-following container paths, identifier readback and cycle/self-location protection. Because PR #31 is unmerged/reference-only and the audited code does not prove the required intended-versus-observed separation, `LOC-001` does not receive MIRA 2.0 implementation credit from it.

**Hard dependencies:** `INV-001`; stable Location UUIDs; explicit location relationship/event schema; source/evidence identity; later movement semantics from D3.

**Enables:** QR/barcode scan-in/out, queryable loft/shop inventory, container movement, “where is it?” and “where does it belong?” queries, par/grocery storage organization.

**Legacy evidence:** category-D row 10; feature ledger requirement; PR #31 `starter/service/inventory_hierarchy.py` as unmerged architecture/reference evidence.

**Acceptance / verification boundary:** Implement/test stable hierarchical Location UUIDs, parent/cycle rules, movable-container semantics and separate intended-home versus current/last-observed state. Tests must prove a movement event changes observed/current state without rewriting intended placement and an explicit intended-placement edit does not fabricate a physical move. Integration verification requires sandbox readback from both query paths.

## Category D2 consistency findings

- `KNOW-001` document identity is independent from `ASSET-001`; a manual can remain canonical while an asset link is pending, and a verified asset survives manual-provider failure.
- `SPEC-001` is not free-form knowledge extraction. Verified safety-critical facts require exact subject/applicability and authoritative provenance.
- `SHOP-001` is active intent, not purchase history, shipment state, spend or asset identity.
- `INV-001` deliberately reuses `ASSET-001` Entity UUIDs so MIRA does not create a parallel inventory identity authority.
- `LOC-001` is a location/state model, not merely a text `location` field. Intended placement and observed/last-moved location are distinct facts.
- PR #31 location hierarchy code remains salvage/reference evidence only; it neither changes the MIRA 2.0 evidence level nor proves the intended-versus-observed requirement.
- No category-D2 feature is promoted to MIRA 2.0 integration/live verification from legacy Google state or unmerged PR #31 code.

## Audited inventory movement, query, par and grocery features

### `MOVE-001` — QR/barcode-driven inventory movement with explicit event/readback semantics

**Description:** MIRA may use a QR code, barcode or other exact supported identifier to resolve a canonical Entity UUID and a stable Location UUID, then record a movement/placement observation for that existing entity. A scan never creates a second physical identity merely because a label was new, and ambiguous identifier/location resolution fails closed. Movement is an explicit event or observation with source, time and idempotency identity; successful mutation requires target readback. A scan-driven move updates current/last-observed placement under `LOC-001` but must not silently redefine the item’s intended/canonical home location. Scan-out/removal likewise records state rather than deleting the asset. Manual fallback may resolve the same canonical identifiers when camera scanning is unavailable.

**Why it exists / user outcome:** Scanning a bin and an item should answer “I put this here” reliably, not rename the item, clone it, or permanently change where it is supposed to live.

**Requirement status:** `accepted / required for inventory movement workflow`.

**Delivery/evidence:** the historical ledger recorded this as spec-only. PR #31 raises the evidence ceiling to **unmerged implementation/test candidate**: shared smart-capture code resolves item/location codes, native Android declares camera/ML Kit barcode support, contract tests require smart-capture/barcode functionality, and the service exposes relocation commands with audit/readback. However, PR #31 remains unmerged reference code and its relocation path overwrites one `assets.location_uuid`, collapsing intended and observed placement. Therefore `MOVE-001` is not MIRA 2.0 implemented/test-verified and depends on the `LOCATION-STATE-001` repair before salvage.

**Hard dependencies:** `INV-001`; `IDENT-001`; `LOC-001`; `LOCATION-STATE-001`; stable movement event/idempotency identity; mutation readback.

**Enables:** scan-in/out, shop/loft item movement, container workflows and later Android inventory capture.

**Legacy evidence:** category-D row 11; PR #31 `starter/clients/pwa/smart-capture.js`; `starter/tests/test_smart_capture_contract.py`; Android camera/barcode hooks; service `inventory.location.resolve_code`, `inventory.asset.resolve_code`, `inventory.asset.relocate` commands.

**Acceptance / verification boundary:** Implement deterministic movement events with replay-safe idempotency, exact/ambiguous identifier handling, scan-in/out semantics, missing-location handling and target readback. Tests must prove movement changes observed/current location without changing intended home, repeated scans do not duplicate movement effects, and unresolved scans make no mutation.

---

### `INV-002` — Queryable household, loft and shop inventory projection

**Description:** MIRA exposes searchable/queryable views over canonical entities, identifiers, relationships, quantities and location state so the user can ask what exists, where it belongs, where it was last observed, what is in a container/location, or find an item by exact identifier or supported descriptive criteria. The query surface is a projection over `ASSET-001`/`INV-001`/`LOC-001`, not a second editable inventory database. Queries preserve ambiguity and provenance rather than fabricating certainty from a label match, and broad ownership joins must not turn one item query into the entire household graph.

**Why it exists / user outcome:** Household junk can be organized like a small parts store and found by query without creating a second spreadsheet whose contents drift from the actual asset/location state.

**Requirement status:** `required`.

**Delivery/evidence:** legacy requirement was specification-level. PR #31 contains substantial **unmerged implementation/test candidate** evidence: inventory query commands, identifier/location joins, hierarchy path endpoints and full-inventory UI contract tests covering assets, assigned inventory, identifiers, evidence, media, violations, journal and audit surfaces. Because the branch is unmerged and its location model still collapses intended/observed state, MIRA 2.0 implementation/integration credit remains unearned.

**Hard dependencies:** `INV-001`; `LOC-001`; `IDENT-001`; `ASSET-003` graph/query semantics; `LOCATION-STATE-001` for complete “belongs vs last seen” answers.

**Enables:** garage/loft storage lookup, inventory browser, barcode workflows, par-level views and future family inventory surfaces.

**Legacy evidence:** category-D row 12; PR #31 service inventory query/hierarchy endpoints and `starter/tests/test_full_inventory_ui.py` as unmerged reference evidence.

**Acceptance / verification boundary:** Sandbox queries must return canonical Entity UUIDs and both intended/observed location semantics, support exact identifier and bounded text/location queries, preserve ambiguity, and prove UI/query replay does not create or mutate a second authority.

---

### `PAR-001` — Target/par quantity with opt-in under-level notification

**Description:** Consumable or replenishable stock may define an explicit target/par quantity separately from the latest supported observed quantity. Reorder/under-level state derives deterministically from those facts and configurable threshold semantics. Alerts are opt-in per user/category/item policy, consolidate rather than creating one permanent scheduler/task per item, and are replay-safe so repeated observations below par do not emit duplicate unresolved alerts. Purchases, consumption and manual corrections change observed quantity only from supported evidence; they do not silently rewrite the target par. A target change likewise does not fabricate a stock movement.

**Why it exists / user outcome:** MIRA can tell the user “you are low on this” without confusing how much should be stocked with how much is actually present.

**Requirement status:** `accepted`.

**Delivery/evidence:** `specified` in the historical feature ledger. Repository searches found no dedicated par-level/reorder/threshold implementation or deterministic tests in the audited legacy tree or PR #31. It must not inherit implementation credit from generic inventory UI/movement code.

**Hard dependencies:** canonical quantity/stock observation model; `INV-001`; stable item identity; optional `GROCERY-001` for food-specific use; consolidated notification/control-cycle semantics.

**Enables:** consumable replenishment, low-stock briefs, grocery-list suggestions and optional sensor-driven stock estimation.

**Legacy evidence:** category-D row 13 and associated historical product direction; no executable implementation located during D3 audit.

**Acceptance / verification boundary:** Add deterministic tests for observed quantity versus target par, exact threshold crossing, corrections, target changes, opt-in/out, repeated below-par observations, recovery above threshold and consolidated alert idempotency.

---

### `PAR-002` — Optional scale-based passive stock sensing

**Description:** A scale/load-cell or similar passive sensor may contribute quantity/weight observations for configured consumables when explicitly enabled. Sensor readings are evidence inputs, not canonical identity and not automatically truth: calibration, tare/container weight, unit conversion, noise/outliers, stale data and confidence must be handled before a reading can update an observed-stock estimate. Manual/receipt/scan corrections remain able to supersede or reconcile sensor estimates. Scale hardware is optional and can never become a universal prerequisite for inventory, par levels, groceries or MIRA itself.

**Why it exists / user outcome:** Frequently used consumables can eventually update with less manual scanning, without turning a flaky load cell under a bin into the supreme authority on household reality.

**Requirement status:** `proposed / optional`.

**Delivery/evidence:** `not_present` in the historical ledger and no relevant scale/weight-sensor inventory implementation was found during repository/PR #31 search. This remains future enhancement/research, not current milestone work.

**Hard dependencies:** `PAR-001`; canonical observation/provenance model; optional hardware adapter; calibration/confidence semantics.

**Enables:** passive consumable estimation where worthwhile; does not block any other inventory capability.

**Legacy evidence:** category-D row 14; historical proposal only.

**Acceptance / verification boundary:** If promoted later, synthetic sensor tests must cover calibration/tare, noisy readings, stale samples, unit conversion, confidence, sensor/manual disagreement and failure isolation. Hardware/live verification is separately required before claiming real-world accuracy.

---

### `GROCERY-001` — Grocery list, pantry and freezer stock reconciliation

**Description:** MIRA supports food/household-consumable stock across configured pantry/freezer/fridge/storage locations and a grocery procurement list while keeping durable purchase receipts separate. Grocery stock tracks product/item identity or practical grouped identity, quantity/unit where useful, location, freshness/expiration when supported and evidence/provenance. Grocery-list intent is active procurement state and reconciles with purchases/owner confirmation under `SHOP-001`; a receipt can inform stock without becoming the pantry database. Consumption, spoilage, transfer and manual correction are stock events/observations. Ambiguous package size/product identity remains unresolved rather than corrupting counts. The model permits coarse practical tracking when serial-level asset treatment would be absurd.

**Why it exists / user outcome:** MIRA can know what food is on hand and what needs buying without forcing a box of pasta to behave like a serialized power tool or turning the grocery list into purchase history.

**Requirement status:** `accepted`.

**Delivery/evidence:** `specified` in the historical feature ledger and product discussions. Repository searches found no dedicated grocery/pantry/freezer executable model or deterministic tests in the audited legacy tree or PR #31, so it remains below implementation credit.

**Hard dependencies:** `SHOP-001`; `INV-001`; `LOC-001`; practical quantity/unit observation model; optional `PAR-001`; `RECEIPT-001` only as purchase evidence, not stock authority.

**Enables:** pantry/freezer queries, low-stock grocery suggestions, purchase-to-stock reconciliation and D4 recipe/meal-planning availability checks.

**Legacy evidence:** category-D row 15; historical feature requirement/product direction; no dedicated executable implementation located during D3 audit.

**Acceptance / verification boundary:** Deterministic tests must cover grocery-list intent versus receipt history, purchase-to-stock reconciliation, consumption/spoilage/transfer, package/unit ambiguity, pantry/freezer location changes, manual corrections and replay without duplicate stock increments.

## Category D3 consistency findings

- `MOVE-001` is an event/observation workflow over canonical `INV-001` identity and `LOC-001` state; scanning cannot become identity authority.
- PR #31 smart-capture/relocation code is useful salvage evidence but currently overwrites a single location field and therefore cannot satisfy the intended-versus-observed contract.
- `INV-002` is a read/query projection, not another mutable inventory database.
- `PAR-001` separates target stock from observed stock and has no executable evidence located yet.
- `PAR-002` remains optional/proposed and absent; no other inventory feature depends on owning scale hardware.
- `GROCERY-001` keeps grocery procurement/stock distinct from receipt history and from serial-style durable asset handling where that would be nonsensical.
- No category-D3 feature is promoted to MIRA 2.0 integration/live verification from legacy Google state or unmerged PR #31 code.

## Audited recipe and meal-planning features

### `RECIPE-001` — Durable recipe library with structured ingredients and provenance

**Description:** MIRA may retain user-created, imported or referenced recipes as durable recipe records with stable Recipe identity, title, structured ingredient requirements, instructions or source reference, serving/yield information when supported, tags/aliases and provenance. Source text and extracted ingredient structure are distinguishable so normalization does not silently rewrite the original recipe. A recipe is reusable knowledge, not a dated meal plan, grocery stock record, shopping-list row or purchase. Imported copyrighted source material should retain the canonical source/document rather than duplicating entire protected works into public Git or arbitrary database fields; only the structured/relevant information needed for the user’s authorized knowledge store should be retained according to source policy.

**Why it exists / user outcome:** A recipe should remain one reusable thing that can be planned many times, searched, scaled or compared against available ingredients without being recreated for every week’s menu.

**Requirement status:** `current required`.

**Delivery/evidence:** the historical ledger marks recipes/meal planning/shopping linkage `CURRENT REQUIRED` but `contract-only manifest`. Repository and PR #31 searches during D4 found no dedicated executable recipe-library engine or deterministic recipe tests. Generic `KNOW-001` provenance patterns are reusable architecture, but they do not by themselves implement structured recipes.

**Hard dependencies:** stable Recipe identity; provenance/source handling; optional `KNOW-001` for retained source documents; practical ingredient identity/unit semantics shared with `GROCERY-001`.

**Enables:** `MEAL-001`, recipe search, ingredient-gap analysis and later family/fridge surfaces.

**Legacy evidence:** category-D row 16; project-conversation evidence explicitly records meal planning as a current requirement; no executable recipe core located in D4 audit.

**Acceptance / verification boundary:** Add deterministic tests for recipe identity/dedupe, structured ingredient extraction/manual correction, servings/yield, source provenance, replay, source-text preservation and updates that do not replace Recipe identity.

---

### `MEAL-001` — Dated meal planning with pantry-aware ingredient-gap and shopping reconciliation

**Description:** Meal plans are dated/period-scoped planning state that references recipes or explicit meal entries without mutating recipe identity. Planning may read supported `GROCERY-001` pantry/freezer/fridge availability and quantity evidence to estimate whether ingredients are on hand, but placing a meal on a plan does not consume stock or fabricate a grocery movement. Missing or insufficient ingredients may create/reconcile deduplicated grocery procurement intent through `SHOP-001` under explicit user/configured policy; the meal plan itself is not a shopping list. Purchase evidence later fulfills shopping intent under the existing purchase/shopping rules, while grocery stock changes only through supported stock events/observations. Ambiguous ingredient identity, units, substitutions or quantities remain reviewable rather than silently overbuying or decrementing inventory.

**Why it exists / user outcome:** MIRA can plan meals from what is actually available and turn genuine ingredient gaps into a useful grocery list without claiming food was eaten, bought or stocked merely because an AI generated a weekly menu.

**Requirement status:** `current required`.

**Delivery/evidence:** `contract/specification-level`. The forensic ledger explicitly calls meal planning a current requirement, but no dedicated executable planner, pantry-gap engine or deterministic meal-planning tests were located in the audited repository/PR #31. It therefore receives no implementation credit from generic shopping/inventory code.

**Hard dependencies:** `RECIPE-001`; `GROCERY-001`; `SHOP-001`; practical ingredient/unit matching; optional `PAR-001`; explicit user planning constraints/preferences where configured.

**Enables:** weekly/daily meal plans, pantry-aware recipe selection, deduplicated missing-ingredient grocery intent and later household/fridge presentation.

**Legacy evidence:** category-D row 16 and project-conversation evidence from the failed Foodie onboarding experiment stating meal planning remains a current requirement even though that universal onboarding design was rejected.

**Acceptance / verification boundary:** Deterministic tests must cover dated plan identity/replay, recipe reuse, pantry availability without stock mutation, missing/partial ingredient calculation, unit/identity ambiguity, deduplicated shopping-intent creation, removal/change of planned meals, and proof that planning alone does not alter receipt/purchase or grocery-stock truth.

## Category D consistency result

Category D is complete through all 16 historical rows. The repaired authority/dependency model is:

- Physical asset identity is canonical under `ASSET-001`; inventory participation (`INV-001`) reuses that Entity UUID and never invents a second physical-object identity authority.
- Fitment/assignment/installation (`FITMENT-001`) is relationship state, not identity. `assigned_to` does not imply `installed_on`.
- Purchase/receipt evidence (`RECEIPT-*`/`ORDER-*`) may create or enrich asset/grocery evidence but remains a separate commerce authority.
- Asset evidence (`EVID-001`), durable reference knowledge (`KNOW-001`) and technical specifications (`SPEC-001`) are separate provenance layers with different verification requirements.
- Shopping intent (`SHOP-001`) is active procurement state. It is not purchase history, inventory ownership, grocery stock or a permanent `Purchased` ledger.
- Hierarchical location (`LOC-001`) separates intended home placement from current/last-observed placement. Movement (`MOVE-001`) records observations/events and cannot silently redefine intended placement.
- Inventory query (`INV-002`) is a projection over canonical entities, relationships, identifiers and location state, not another editable database.
- Par targets (`PAR-001`) are separate from observed quantities. Optional scale sensing (`PAR-002`) is merely another evidence source and is not required for ordinary inventory.
- Grocery stock/list state (`GROCERY-001`) uses practical consumable quantity/location semantics and links to shopping/purchase evidence without pretending food is a serialized durable asset.
- Recipe knowledge (`RECIPE-001`) is reusable durable content. Meal-plan state (`MEAL-001`) is date/period-scoped planning that references recipes.
- Meal planning may read grocery availability and create deduplicated missing-ingredient shopping intent, but planning alone cannot consume stock, create a purchase, or claim a shopping item was fulfilled.
- PR #31 contains several useful inventory/scanning/query candidates, but all remain unmerged salvage/reference evidence. The one-field relocation design conflicts with the required intended-versus-observed location model and must be repaired before salvage.
- No category-D feature is promoted to MIRA 2.0 integration/live verification from legacy Google production state, conversation memory, or unmerged PR #31 code.

## Audit status

- Categories A, B, C and D are complete.
- `M2-G0-005A` completed category-D rows 1-5.
- `M2-G0-005B` completed category-D rows 6-10.
- `M2-G0-005C` completed category-D rows 11-15.
- `M2-G0-005D` audited row 16 as `RECIPE-001` and `MEAL-001` and completed the category-D consistency closure.
- The complete historical feature inventory is still in progress. The next bounded audit begins category E with onboarding/safe-initialization foundations; no category-E feature is audited by this packet.
