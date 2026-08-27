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
- `ONBOARD-*` — safe starter, first boot, discovery and user configuration intake;
- `SERVICE-*` — explicit service activation and capability-verification state;
- `PROFILE-*` — roles, family, customization and accessibility;
- `SOURCE-*` — durable source modes, source read/write/readback capability and source-lineage behavior;
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
MIRA supplies whole copy/paste replacement blocks plus nontechnical UI instructions whenever ChatGPT Project/Custom Instructions must change. Direct mutation of Project Instructions, global Custom Instructions or an equivalent instruction surface is never assumed from runtime identity or general account access; it must be capability-proven and read back. When direct write is unavailable or unverified, the supported behavior is a complete source-backed replacement block, clearly naming which existing instruction block must be fully replaced and giving simple nontechnical UI steps. Partial “add this line” patches are prohibited unless the user explicitly asks for a patch.

**Evidence:** current MIRA Project Instructions plus legacy `project/INSTRUCTIONS.md.tmpl`; process/specification implemented as governance. Direct Project/Custom Instructions UI mutation remains unverified and capability-gated.

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

## Audited safe-starter and onboarding foundation features

### `ONBOARD-002` — Sanitized generic starter with no inherited personal production state

**Description:** Every new MIRA/MIRROR deployment begins from portable generic source and synthetic/example configuration, never from another user’s mutable life state. Starter/distribution source must not contain production-specific personal data, non-placeholder email addresses, concrete Google resource URLs, deployment authority IDs, credentials, live schedules, private third-party facts, asset IDs, aliases, goals or other inherited operational state. Legacy production data is neither copied into public source nor silently used as a development fixture. Private mutable state is created in the new deployment’s selected authority only after onboarding/configuration. Rejected or contaminated legacy branches remain evidence, not defaults.

**Why it exists / user outcome:** Installing MIRA should create *your* assistant, not a disturbingly intimate clone of whoever happened to develop the template first.

**Requirement status:** `required / privacy boundary`.

**Delivery/evidence:** the legacy portable starter has an executable `audit_starter_privacy.py` scanner that rejects blocklisted production markers, non-placeholder emails, concrete Google Drive/Docs URLs, authority IDs and symlinks. The canonical CI workflow runs both full-history public-source audit and starter-privacy audit before repository validation/tests, making starter sanitization a genuine `test_verified`/CI-enforced legacy-source guardrail. `START_HERE.md` also explicitly prohibits inheriting another deployment’s timezone, schedules, accounts, assets, routines, goals, IDs, configuration, aliases or state. **MIRA 2.0 has not yet integration-verified a generated starter/distribution from its new canonical repo.**

**Hard dependencies:** public-source privacy policy; synthetic fixtures; `DATA-001`; clean source lineage; distribution/build pipeline when one is introduced.

**Enables:** safe public template/onboarding, personal forks/deployments, later institutional distribution and migration without privacy contamination.

**Legacy evidence:** category-E row 1; `scripts/audit_starter_privacy.py`; `.github/workflows/ci.yml`; `START_HERE.md`; historical clean-lineage/sanitization work.

**Acceptance / verification boundary:** Preserve scanner/CI semantics in MIRA 2.0, generate a synthetic starter/distribution, run privacy and history audits against it, and prove no protected legacy identifiers/state appear in source or fixtures. Live personal state must remain outside public Git.

---

### `ONBOARD-003` — Four-question Minimum Useful Setup with resumable bounded interview

**Description:** First boot begins with no more than four high-value kickoff questions before any deeper discovery. The canonical initial set captures system name, authoritative IANA timezone, broad current life/work pattern including job/duties/work-away details when relevant, and the biggest problems the user wants help remembering/organizing/deciding/planning/following through on. Follow-up discovery is bounded to at most four related questions at a time, persists durable Interview Ledger state, does not restart after conversational detours, never treats silence as an answer, and permits `Deferred`, `Unresolved`, `Answered`, `Resolved from evidence` and `Not applicable` progress. MIRA should synthesize a Minimum Useful Setup rather than requiring a human to complete an exhaustive life questionnaire before receiving value.

**Why it exists / user outcome:** A new user gets useful MIRA behavior quickly instead of enduring an onboarding deposition conducted by an assistant with unlimited curiosity and no social instincts.

**Requirement status:** `required`.

**Delivery/evidence:** `START_HERE.md` contains an explicit four-question first-boot contract and `LIFE_INTERVIEW.md` defines bounded/resumable Interview Ledger mechanics. These are implemented workflow/source artifacts. The audit did not locate a dedicated deterministic regression test that proves the complete four-question → resumable-Minimum-Useful-Setup flow, so the full behavior remains below `test_verified` despite strong specification/implementation evidence.

**Hard dependencies:** durable Interview Ledger/state authority; `ONBOARD-002`; explicit user input; capability discovery; no-silent-provisioning boundary.

**Enables:** nontechnical onboarding, progressive personalization, later role/profile discovery and safe incremental configuration.

**Legacy evidence:** category-E row 2; `starter/START_HERE.md`; `starter/LIFE_INTERVIEW.md`; Interview Ledger contract.

**Acceptance / verification boundary:** Add deterministic conversation/state fixtures proving exactly ≤4 kickoff questions, durable resume after detours/restart, silence/defer semantics, evidence-resolved factual items, preference/permission non-inference and Minimum Useful Setup before exhaustive interview completion.

---

### `ONBOARD-004` — Capability, friction, AI-use and work-context discovery without silent activation

**Description:** After kickoff, MIRA discovers how the user currently uses AI, recurring friction/pain points, exact job title/duties/work-away pattern when relevant, desired automations, existing apps/services/data sources and important constraints. It inspects reachable capabilities/evidence before asking the user to recreate information or reconnect tools. Discovery may recommend services, context modes or adjacent workflows, but recommendations never silently enable a service, permission, sharing scope or context. Unknown/inaccessible capabilities remain unresolved and MIRA must not promise feature parity or integrations it cannot verify. Questions are asked only when their answers can materially change workflow, dependency, schema, schedule, permission or recommendation.

**Why it exists / user outcome:** MIRA learns enough about the user’s actual life and tools to suggest useful automation without forcing the user to design the system or enabling things merely because a job title matched a keyword.

**Requirement status:** `required`.

**Delivery/evidence:** `START_HERE.md`, `LIFE_INTERVIEW.md` and `CAPABILITY_DISCOVERY.md` provide strong workflow/specification evidence. Deterministic profile-router tests prove important sub-boundaries: work-away recommendations require confirmation, catalog presence does not equal implementation, recommendations do not silently activate services, malformed/unknown inputs fail closed, and context never changes canonical timezone. The broad end-to-end discovery interview itself is not independently `test_verified`.

**Hard dependencies:** `ONBOARD-003`; capability/provider introspection; `SERVICE-001`; `CTX-002`; explicit consent/permission boundaries.

**Enables:** adaptive configuration, role/profile routing, context recommendations, provider selection and useful automation suggestions without capability hallucination.

**Legacy evidence:** category-E row 3; `START_HERE.md`; `LIFE_INTERVIEW.md`; `CAPABILITY_DISCOVERY.md`; `onboarding_profile_router.py`; `test_onboarding_profile_router.py`.

**Acceptance / verification boundary:** Add structured fixtures for discovery/resume, already-connected capability reuse, unavailable-provider behavior, job/duty recommendation without activation, explicit constraints and no unsupported capability claims. MIRA 2.0 integration must persist only approved configuration/state to the selected sandbox authority.

---

### `ONBOARD-005` — Explicit new-user brief cadence and canonical IANA timezone configuration

**Description:** A new deployment asks the user for its preferred brief/action-digest cadence, local schedule slots and one authoritative named IANA timezone rather than inheriting another deployment’s schedule or a device/travel timezone. Timezone is durable configuration used by scheduler semantics such as `OPS-003`; later travel/context changes do not silently change it. New-user configuration is distinct from the existing personal production deployment’s already-audited fixed schedule. If briefs are disabled/not applicable/deferred, onboarding does not create a dispatcher merely because the feature exists in the catalog.

**Why it exists / user outcome:** A new user’s assistant runs on *their* schedule, while MIRA stops treating whatever timezone a phone happens to display as constitutional law.

**Requirement status:** `required`.

**Delivery/evidence:** `START_HERE.md` explicitly asks authoritative IANA timezone in kickoff and requires cadence/slots/timezone when briefs are enabled; `LIFE_INTERVIEW.md` reinforces canonical-time rules. Core named-timezone scheduler semantics are separately `test_verified` under `OPS-003`, but the complete onboarding capture → persisted configuration → scheduler/readback path is not yet integration/test-verified as one feature.

**Hard dependencies:** `ONBOARD-003`; `SERVICE-001` brief activation; named IANA timezone validation; `OPS-001`/`OPS-003` when briefs are enabled; canonical configuration authority.

**Enables:** portable new-user brief scheduling without copying personal deployment timing.

**Legacy evidence:** category-E row 4; `START_HERE.md`; `LIFE_INTERVIEW.md`; existing `OPS-003` deterministic timezone tests.

**Acceptance / verification boundary:** Add onboarding fixtures for valid/invalid IANA zones, enabled/disabled/deferred briefs, cadence/slot validation and persistence/readback. Sandbox integration must prove the captured timezone/slots drive configuration without changing from device/travel context.

---

### `SERVICE-001` — Explicit finite service activation state separate from capability and recommendation

**Description:** Every catalogued MIRA service has one explicit activation state: `unresolved`, `enabled`, `disabled`, `not_applicable`, or `deferred`. Catalog presence does not prove implementation, capability availability does not imply activation, and a recommendation does not authorize enabling. Disabled/not-applicable services are excluded from normal recommendations; deferred services remain known future choices without pretending to be active. Legacy boolean fields may map to the finite model only when non-conflicting. Unknown services, invalid states and contradictory activation inputs fail closed. Service implementation/capability verification is tracked separately from activation.

**Why it exists / user outcome:** “MIRA knows this feature exists,” “this device/account can support it,” “MIRA recommends it,” and “the user enabled it” stop being four different meanings of the same Boolean-shaped disaster.

**Requirement status:** `required for honest onboarding and runtime configuration`.

**Delivery/evidence:** `test_verified` in the legacy deterministic onboarding router. Tests prove default `unresolved`, explicit enable/disable, finite state validation, no silent activation from recommendations/catalog presence, disabled/not-applicable recommendation suppression, conflicting legacy/current state rejection, unknown-service failure and separate `requires_capability_verification` implementation status.

**Hard dependencies:** canonical service catalog/IDs; configuration authority; explicit user decisions; capability-verification state.

**Enables:** safe onboarding, module routing, deferred services, role-based recommendations and honest capability reporting.

**Legacy evidence:** category-E row 5; `starter/tools/onboarding_profile_router.py`; `starter/tests/test_onboarding_profile_router.py`; `START_HERE.md` stock-service activation contract.

**Acceptance / verification boundary:** Preserve deterministic state-machine tests in MIRA 2.0 and persist/read back service activation separately from capability/implementation state. Prove recommendation changes cannot mutate activation without explicit user/configuration action.

## Category E1 consistency findings

- `ONBOARD-002` is a privacy/source-lineage boundary, not merely a friendly onboarding screen. Starter sanitization is CI-enforced in legacy source but still needs MIRA 2.0 distribution proof.
- `ONBOARD-003` owns interview pacing/resume; it does not itself decide which services are active.
- `ONBOARD-004` discovers facts/preferences/capabilities and may recommend, but activation authority remains `SERVICE-001`.
- `ONBOARD-005` configures a new deployment’s schedule/timezone only when applicable; it cannot overwrite another deployment’s schedule and runtime semantics remain under `OPS-*`.
- `SERVICE-001` separates activation, recommendation, catalog presence and capability verification.
- The rejected/unsafe universal-onboarding experiment remains rejected evidence. Its existence cannot override current bounded, explicit, browser/nontechnical-safe onboarding rules.
- No E1 feature is promoted to MIRA 2.0 integration/live status merely because the legacy starter or tests exist.

## Audited role/profile foundation features

### `PROFILE-001` — Composable working and self-employed roles with evidence-gated work-context routing

**Description:** MIRA represents `working` and `self_employed` as explicit composable profile roles rather than a universal “work mode.” A person may hold either role alongside other roles such as parent/guardian, with an explicit primary role when multiple non-minor roles apply. Working uses a work-and-personal operations presentation; self-employed may surface business/personal operations and finance-oriented focus, but neither role silently enables email, finance, work-trip tracking, briefs or a context split. Exact job title/duties and recurring work-away evidence may recommend HOME/ROAD, HOME/TRUCK, HOME/FIELD, HOME/AWAY or custom labels under `CTX-002`; explicit user configuration controls activation. Being employed does not prove travel, and being self-employed does not grant business-account permissions or make every finance feature applicable.

**Why it exists / user outcome:** MIRA can adapt to ordinary employment or self-employment without assuming that every worker travels, every contractor runs the same business workflow, or a job title is permission to rearrange the user’s life.

**Requirement status:** `accepted`.

**Delivery/evidence:** the legacy deterministic profile router implements both role tokens, distinct public labels/templates, composability, service recommendations and work-context routing. Working-role context behavior has direct regression tests covering confirmed-away, explicitly-not-away, ambiguous field work, custom labels and no silent selection. The self-employed route exists in executable code but the audited suite does not contain a dedicated self-employed fixture proving all of its distinctions, so the combined feature is `implemented` with important working-role subpaths `test_verified`, not fully test-verified end to end.

**Hard dependencies:** `ONBOARD-004`; `SERVICE-001`; `CTX-002`; canonical profile/configuration authority; explicit role/primary-role input when required.

**Enables:** work-aware briefs/next actions, optional work-trip/finance/email recommendations, later work profiles without hard-coded trucking behavior.

**Legacy evidence:** category-E row 6; `starter/tools/onboarding_profile_router.py`; `starter/tests/test_onboarding_profile_router.py`; `questions.profile-and-stock-services.json`.

**Acceptance / verification boundary:** Add dedicated self-employed and mixed-role fixtures, prove recommendations never mutate activation, preserve explicit primary-role handling, and persist/read back role/context configuration in the MIRA 2.0 sandbox without importing deployment-specific job data into public source.

---

### `PROFILE-002` — Retired role distinct from nonworking with respectful, opt-in support

**Description:** `retired` is a first-class composable role with public label `Retired` and support template `Personal Schedule & Wellbeing`. Retirement is not shorthand for unemployment, old age, disability, reduced competence, illness or medication use. Work-away context routing is bypassed by default unless independently justified. The role may recommend appointments, appointment reminders, medication reminders, household/admin, routines, travel and knowledge workflows, but recommendations remain unresolved until explicitly enabled under `SERVICE-001`. Medication schedules remain evidence-gated under `REMIND-001`, caregiver sharing is off until explicit opt-in, and age/ability inference is prohibited.

**Why it exists / user outcome:** A retired user gets useful schedule, household, travel and project support without MIRA deciding that retirement means frailty, medical dependence, or “basically unemployed but older.”

**Requirement status:** `current required`.

**Delivery/evidence:** the legacy router and tests `test_verified` the retired/nonworking distinction, retired public label/template, work-context bypass, appointment/medication recommendations remaining unactivated, private profile alias storage, explicit reminder activation and prohibited age/ability inference. Provider delivery and MIRA 2.0 canonical profile persistence remain unverified.

**Hard dependencies:** `SERVICE-001`; `REMIND-001`/`REMIND-002` when reminder features are selected; canonical profile authority; `CTX-002` for any separately justified context mode.

**Enables:** retiree-friendly onboarding and briefs, hobbies/projects/travel/household focus, opt-in appointment/reminder workflows.

**Legacy evidence:** category-E row 7; `onboarding_profile_router.py`; `test_onboarding_profile_router.py`; `questions.profile-and-stock-services.json` retiree support prompt.

**Acceptance / verification boundary:** Preserve deterministic role/recommendation/non-inference tests. MIRA 2.0 sandbox must persist/read back retired role separately from employment state and prove role changes do not activate health/sharing features or infer age/ability.

---

### `PROFILE-003` — Nonworking/between-jobs role distinct from retirement

**Description:** `nonworking` represents a current not-working, between-jobs, not-employed or equivalent state without collapsing it into retirement. It uses a `Not currently working` presentation and may emphasize next actions, personal priorities, household/admin, routines or skill-building. Work-away machinery is bypassed by default because employment/context state is absent, while future job-search/career features remain separate opt-in services. The role does not imply financial distress, unemployment-benefit status, job-seeking intent, disability, retirement, caregiving or any other unsupported circumstance.

**Why it exists / user outcome:** Someone between jobs should not be treated as retired, and someone retired should not be treated as temporarily unemployed. Apparently nouns still need schemas because software enjoys category mistakes.

**Requirement status:** `accepted`.

**Delivery/evidence:** the legacy router implements aliases for `not working`, `between jobs`, `not employed`, `nonworking` and `unemployed`, a distinct presentation/template, separate recommendations and default context bypass. Regression tests directly prove retired versus nonworking classification, while the full nonworking recommendation/persistence flow is not independently integration-verified.

**Hard dependencies:** `SERVICE-001`; canonical profile authority; `ONBOARD-004` for current-life-pattern discovery.

**Enables:** personal-priority/next-action support without inappropriate work machinery and later explicit career/job-search activation when wanted.

**Legacy evidence:** category-E row 8; `onboarding_profile_router.py`; `test_onboarding_profile_router.py` retired/nonworking distinction.

**Acceptance / verification boundary:** Add dedicated nonworking recommendation and role-transition fixtures, persist/read back the role in MIRA 2.0, and prove transitions among working/nonworking/retired do not silently activate or delete unrelated services/state.

---

### `PROFILE-004` — Parent/guardian as a first-class composable role with permission-scoped recommendations

**Description:** `parent_guardian` is a first-class composable role rather than an inferred household property. It may coexist with working, retired or other roles; when multiple non-minor roles apply the user explicitly selects the primary routing role. Parent/guardian may surface family/school, appointments, household/admin, next actions and shopping recommendations, but recommendation is not activation and the relationship label itself grants no calendar, school, health, financial, custody or sharing authority. Family access uses explicit owner-approved whole-authority or scoped shared-authority grants with provider/API readback. Private friendly aliases stay in mutable private state, not portable public source.

**Why it exists / user outcome:** MIRA can help coordinate family life without interpreting “parent” as a master password to another person’s calendar, school records or health information.

**Requirement status:** `current required`.

**Delivery/evidence:** the legacy router/test suite `test_verified` first-class parent composition with working and mixed-profile behavior, explicit-primary-role enforcement, family/school brief focus, contradiction failure and recommendation/activation separation. The state-authority model strongly specifies explicit sharing grants and never-infer-family-access behavior. Dedicated family-school service execution, custody/permission enforcement and MIRA 2.0 provider readback are not integration-verified.

**Hard dependencies:** `SERVICE-001`; canonical Person/profile identity; explicit relationship records; scoped authority/sharing model; provider/API authorization and readback for shared state.

**Enables:** family/school coordination, household and appointment recommendations, later scoped shared household authorities.

**Legacy evidence:** category-E row 9; `onboarding_profile_router.py`; `test_onboarding_profile_router.py`; `questions.profile-and-stock-services.json`; `STATE_AUTHORITY_MODEL.md` sharing contract.

**Acceptance / verification boundary:** Preserve role-composition tests; add permission fixtures proving relationship labels cannot grant access, explicit shared scopes are required/read back, disabled/not-applicable family services stay inactive, and MIRA 2.0 profile/relationship persistence uses synthetic people only.

---

### `PROFILE-005` — Dependent-minor role with primary routing and explicit privacy/permission gates

**Description:** `dependent_minor` is an explicit profile role and, when present with another role such as student, remains the primary routing role rather than being flattened into a generic mixed profile. By default recurring away-context routing is bypassed; custom HOME/CAMPUS or other away contexts require explicit approval/evidence instead of being inferred from school/student labels. Recommended services are limited to appropriate categories such as education, family/school and routines, while every service still retains independent activation/capability state. The minor/dependent relationship itself grants no guardian, custody, school, calendar, health, financial or sharing permission. Store only minimum necessary private data in the selected authority, and require explicit scoped grants/readback for any shared state.

**Why it exists / user outcome:** MIRA can support a dependent’s school/routine coordination without using “minor” as permission to expose everything to everyone who happens to have a family label.

**Requirement status:** `accepted direction / privacy-sensitive`.

**Delivery/evidence:** the legacy router and tests `test_verified` dependent-minor primary-role precedence, non-mixed routing, default away-context bypass and explicit approval before custom away context. The question bank requires dependent-minor primary routing and explicit answers for preferences/activation; the authority model forbids inferred family access. Dedicated family-school execution, minimum-necessary data schema, custody/guardian authorization and provider sharing readback remain specification/integration gaps.

**Hard dependencies:** `SERVICE-001`; canonical Person/profile identity; explicit relationship/permission scopes; sharing/authorization model; `CTX-002`; privacy/minimum-necessary data policy.

**Enables:** safe dependent/student routing and later family-school coordination without implicit access rights.

**Legacy evidence:** category-E row 10; `onboarding_profile_router.py`; `test_onboarding_profile_router.py` dependent-minor fixtures; `questions.profile-and-stock-services.json`; `STATE_AUTHORITY_MODEL.md` sharing contract.

**Acceptance / verification boundary:** Preserve primary/context tests; implement deterministic permission/minimum-data fixtures, prove no relationship label grants access, require explicit shared-scope readback, and use only synthetic dependent/guardian records until privacy/authorization behavior is integration-verified.

## Category E2 consistency findings

- Roles are descriptive/routing inputs, not permissions and not service activation.
- `PROFILE-001` may recommend work/context behavior, but job title/duties never silently select context or enable a service.
- `PROFILE-002` retirement and `PROFILE-003` nonworking are distinct states; neither implies health, age, disability, financial or competence facts.
- `PROFILE-004` parent/guardian composes with other roles but grants no custody, calendar, school, health, finance or sharing authority by itself.
- `PROFILE-005` dependent-minor remains primary for safety-oriented routing; explicit approval is required before recurring away-context selection.
- Family sharing is an authority/permission operation with explicit scope and readback, never an implication of a profile relationship.
- Legacy router implementation/tests establish useful deterministic evidence, but MIRA 2.0 profile persistence, provider sharing and family-service integration remain unverified.

## Audited extended-role and usability features

### `PROFILE-006` — Caregiver role with explicit health and sharing boundaries

**Description:** `caregiver` is an explicit composable role for a person who coordinates care, rides, appointments, paperwork or responsibilities for another person. It may recommend appointment/calendar, reminder, household/admin, household-routine and health-organization services, but the caregiver label itself grants no authority over another person’s health, calendar, finances, communications or private state. Medication reminders remain governed by `REMIND-001`, caregiver reminder sharing remains governed by `REMIND-002`, and every recommended service stays independently unresolved/disabled/enabled under `SERVICE-001`. Caregiver status must not be inferred from a family relationship, age, co-residence or observed appointment traffic.

**Why it exists / user outcome:** MIRA can help someone coordinate caregiving work without deciding that “caregiver” is a blanket authorization token for another human being’s life.

**Requirement status:** `proposed / accepted direction`.

**Delivery/evidence:** the legacy deterministic router implements a first-class `caregiver` role, public presentation, brief focus and role-specific service recommendations. The broader onboarding/question bank explicitly asks about caregiving duties rather than inferring them. No dedicated caregiver-only regression fixture was located in the audited test suite, and dedicated care/health service execution or permission readback remains unverified. The feature is therefore `implemented` at the router level, not fully `test_verified` end to end.

**Hard dependencies:** `SERVICE-001`; explicit Person/relationship/permission authority; `REMIND-001`/`REMIND-002` for selected reminders; privacy/minimum-necessary policy.

**Enables:** caregiver-focused next actions, appointment/household coordination and later scoped shared-care workflows.

**Legacy evidence:** category-E row 11; `starter/tools/onboarding_profile_router.py`; `questions.json` caregiving discovery; historical ledger caregiver/household-manager row.

**Acceptance / verification boundary:** Add dedicated caregiver fixtures for role composition, service recommendations, no silent activation and no inferred authority. MIRA 2.0 integration must use synthetic people and prove any shared-care scope requires explicit authorization/readback.

---

### `PROFILE-007` — Household-manager role with explicit routine ownership and consolidated delivery

**Description:** `household_manager` is an explicit composable role for household administration/coordination. It may recommend household admin, household routines, shopping, assets and recipes/meals, but it does not imply sole ownership of chores, property, purchases or another person’s data. Household routines remain canonical task/routine state and should consolidate into brief or Calendar projection rather than creating one permanent scheduler/automation per chore. Laundry and pickup/drop-off examples are discoverable options, not universal defaults, and ownership/responsibility is never inferred merely because the role exists.

**Why it exists / user outcome:** MIRA can help run a household without assigning every sock, grocery run and broken appliance to one person because someone selected “household manager.”

**Requirement status:** `proposed / accepted direction`.

**Delivery/evidence:** the legacy router implements the role and dedicated regression coverage verifies household-routine recommendation/activation, washer-to-dryer and pickup examples, consolidated delivery rather than per-chore automations, and `ownership_inference = prohibited`. Broader household service/provider integration remains unverified, but the routing/safety core is `test_verified`.

**Hard dependencies:** `SERVICE-001`; `TASK-001`/routine authority; explicit household relationship/responsibility state where shared; Calendar/brief projection only when enabled.

**Enables:** household routines, errands, shopping/admin coordination and later shared-household surfaces.

**Legacy evidence:** category-E row 11; `onboarding_profile_router.py`; `test_onboarding_profile_router.py::test_household_routines_are_explicit_and_do_not_fan_out_schedulers`.

**Acceptance / verification boundary:** Preserve deterministic anti-fan-out/ownership tests, add mixed-role persistence fixtures and prove MIRA 2.0 household recommendations cannot mutate another person’s responsibility or activate services without explicit state.

---

### `PROFILE-008` — Student role with explicit HOME/CAMPUS context option

**Description:** `student` is a first-class composable role with study/deadline/next-action focus and optional education, skill-building and appointment recommendations. HOME/CAMPUS is an available context pair under `CTX-001`, not something automatically activated merely because a student role exists. Campus/away context requires explicit work-away/context evidence or user-selected labels; student identity, enrollment or school evidence cannot silently create a recurring away mode. When `dependent_minor` is also present, the dependent-minor safety precedence from `PROFILE-005` remains primary.

**Why it exists / user outcome:** A student can get study-oriented planning and a useful campus context when it actually fits, without MIRA assuming every student commutes, lives on campus or wants school to become the organizing principle of the whole system.

**Requirement status:** `accepted`.

**Delivery/evidence:** the legacy router implements the `student` role, public presentation and recommendations. HOME/CAMPUS is supported through the generic custom-context mechanism and is exercised in the dependent-minor/student safety test only after explicit away approval. The audited suite does not contain a standalone student fixture proving a student-derived HOME/CAMPUS recommendation; in fact the router does not auto-select HOME/CAMPUS from the role alone. Therefore the role is `implemented`, while the explicit context option is supported and safety-consistent but not a fully test-verified automatic student workflow.

**Hard dependencies:** `SERVICE-001`; `CTX-001`/`CTX-002`; canonical profile/configuration state; `PROFILE-005` when dependent-minor applies.

**Enables:** study/deadline routing, optional HOME/CAMPUS views and later education integrations.

**Legacy evidence:** category-E row 12; `onboarding_profile_router.py`; dependent-minor/student HOME/CAMPUS test; historical ledger student row.

**Acceptance / verification boundary:** Add dedicated adult-student and dependent-student fixtures, prove HOME/CAMPUS remains explicit/recommended rather than silently activated, and persist/read back student/context state in the MIRA 2.0 sandbox.

---

### `PROFILE-009` — Mixed/custom role composition preserves underlying roles and explicit primary routing

**Description:** MIRA supports multiple simultaneous roles without collapsing the underlying role set into one synthetic identity. `mixed` is only a summary presentation when multiple non-minor roles apply; the canonical roles remain individually preserved and an explicit `primary_role` controls routing precedence. `dependent_minor` remains primary when present for safety. The generic `custom` role is a fallback for a life pattern not represented by current roles and cannot be combined with established roles to erase their semantics. Duplicate, contradictory, unsupported or malformed role inputs fail closed.

**Why it exists / user outcome:** A person can be working, parenting and studying at the same time without the database concluding that their true occupation is “mixed.”

**Requirement status:** `required for generality`.

**Delivery/evidence:** the legacy router/test suite `test_verified` mixed-role preservation, explicit primary-role requirement, retired+parent composition, dependent-minor primary precedence, duplicate-role rejection, custom-plus-known-role rejection, contradictory flags and unsupported-role failure. MIRA 2.0 profile persistence/readback remains unverified.

**Hard dependencies:** canonical profile identity/state; stable role vocabulary; explicit primary-role semantics; `SERVICE-001` for any recommendations.

**Enables:** realistic multi-role profiles and future role additions without destructive remapping.

**Legacy evidence:** category-E row 13; `onboarding_profile_router.py`; `test_onboarding_profile_router.py` mixed/primary/duplicate/custom-role fixtures.

**Acceptance / verification boundary:** Preserve deterministic composition/fail-closed tests and prove MIRA 2.0 role edits preserve unaffected roles/services while changing only explicit routing state.

---

### `PROFILE-010` — Preference-driven usability and accessibility without demographic inference

**Description:** MIRA may adapt wording, interaction density, reminder presentation, input/output modality, text size/readability guidance, spoken delivery and other usability choices from explicit user preference, observed device capability or accessibility configuration. Age, retirement status, family role or another demographic label must never be used as a shortcut to infer disability, competence, medication needs, financial sophistication, hearing/vision status or “simplified mode.” A retired or older user may receive the same full feature set as any other user unless explicit preferences/capabilities say otherwise. Usability configuration is separate from role identity and from service activation.

**Why it exists / user outcome:** MIRA can be easier to use for someone who wants larger text, simpler instructions or spoken reminders without first deciding what kind of human they are based on age stereotypes.

**Requirement status:** `accepted direction`.

**Delivery/evidence:** the historical ledger records older-adult usability as accepted direction and explicitly prohibits age/ability/competence inference. The legacy router returns `age_or_ability_inference = prohibited`, and retired-profile tests verify that boundary. Broader accessibility/preference routing is discovery-driven rather than represented by a dedicated deterministic accessibility engine, so only the non-inference core is test-supported; the full usability feature remains `specified/partially implemented` rather than test-verified.

**Hard dependencies:** explicit preference/configuration authority; device/capability discovery when modality matters; `SERVICE-001`; privacy/non-inference policy.

**Enables:** nontechnical/older-adult usability, accessible reminders and device-appropriate presentation without demographic modes.

**Legacy evidence:** category-E row 14; historical ledger; `onboarding_profile_router.py` non-inference output; retired-profile regression tests.

**Acceptance / verification boundary:** Add explicit usability/accessibility preference schema and deterministic fixtures proving preferences, not age/role, control presentation. Test that identical preferences produce identical behavior across age/role labels and that absent preferences do not trigger demographic defaults.

---

### `PROFILE-011` — Public “Boomer mode” is rejected; private user-chosen alias remains presentation-only

**Description:** MIRA has no public profile, capability set or usability mode named “Boomer mode.” That nickname is rejected as a product-facing demographic mode because it is imprecise, potentially insulting and encourages age-based capability assumptions. If a user deliberately chooses a private friendly alias or joke label for their own profile, it may be stored as private mutable presentation state under the normal profile-alias mechanism. A private alias cannot change roles, permissions, service activation, safety policy, capability availability, accessibility settings or public/shared labels unless separately and explicitly configured.

**Why it exists / user outcome:** The product can be friendly without turning a generation label into an architecture decision. Humanity has already invented enough settings menus that quietly mean “we assume you are bad at computers.”

**Requirement status:** public mode `rejected_or_superseded`; optional private alias `accepted`.

**Delivery/evidence:** the forensic ledger explicitly says the nickname was proposed but is deliberately not a public mode. The legacy router has no `boomer` role, supports only the finite canonical role vocabulary, fails closed on unsupported roles, and stores `profile_alias` in `private-mutable-state`. No dedicated regression test uses the literal nickname, so the public rejection is a durable specification/negative constraint while private-alias storage is implemented/test-supported through existing profile tests.

**Hard dependencies:** `PROFILE-010`; canonical profile alias/private-state semantics; public-source sanitization under `ONBOARD-002`.

**Enables:** respectful public UI while still allowing user-chosen private humor/nicknames.

**Legacy evidence:** category-E row 15; historical ledger “Boomer mode” exclusion; `onboarding_profile_router.py` finite roles/private alias; profile-router tests for private alias and unknown-role failure.

**Acceptance / verification boundary:** Add a MIRA 2.0 regression asserting no public role/mode identifier uses the rejected label and prove private aliases are presentation-only, private, non-authorizing and excluded from portable/public source.

## Category E3 consistency findings

- Caregiver and household-manager are separate composable roles because their safety and recommendation surfaces differ; neither role grants ownership or access authority.
- Caregiver health/reminder recommendations remain behind `SERVICE-001`, `REMIND-001` and `REMIND-002`; the role is not health authorization.
- Household-manager routing has direct anti-fan-out and no-ownership-inference tests; broader shared-household behavior remains separate.
- Student is a role; HOME/CAMPUS is a context option. The role alone does not silently activate that context.
- `mixed` is summary presentation only and never replaces canonical underlying roles. `custom` cannot erase established role semantics.
- Accessibility/usability is preference/capability configuration, not age or retirement inference.
- Public “Boomer mode” remains rejected. A private user-selected alias is harmless presentation state only and cannot change capabilities, permissions or safety policy.
- No E3 feature is promoted to MIRA 2.0 integration/live verification from legacy router code alone.

## Audited identity, sharing and self-extension foundation features

### `PROFILE-012` — Canonical per-person identity and explicit relationship graph

**Description:** Every person represented in MIRROR has one private immutable Person UUID that survives display-name changes, provider changes and backend migration. Household, spouse/partner, parent, guardian, dependent, beneficiary, caregiver, household-member and other configured relationships are explicit relationship records between Person UUIDs with their own type, provenance/status and lifecycle semantics. Relationship labels describe reality; they are not permission grants. Ownership/beneficiary links used by orders, reimbursements, household state or shared services reference canonical Person UUIDs rather than names or chat-local identity. Duplicate people, uncertain matches and relationship changes must be reconciled explicitly rather than silently merged from similar names.

**Why it exists / user outcome:** MIRA can know who a person is and how people are related without using a display name as an identifier or turning “spouse,” “parent,” “guardian,” “caregiver” or “beneficiary” into an accidental access-control system.

**Requirement status:** `accepted / foundational prerequisite`.

**Delivery/evidence:** the legacy state-authority architecture strongly specifies a `People` authority, immutable owner Person UUIDs on authority records, stable identities across backend migration and explicit household/beneficiary relationship semantics. Existing reimbursement/profile workflows depend on these concepts, but the audit did not locate a generic deterministic Person/relationship engine with enough dedicated tests for full `test_verified` status. Therefore this feature remains `specified`/data-model-workflow evidence rather than a proven MIRA 2.0 implementation.

**Hard dependencies:** canonical MIRROR identity authority; provenance/source identity; privacy/minimum-necessary data policy; `PROFILE-013` for any permission-bearing use.

**Enables:** parent/minor/caregiver safety, household sharing, reimbursements/beneficiaries, per-person profiles, family-school workflows and multi-person state without name-based identity drift.

**Legacy evidence:** category-E row 16; `STATE_AUTHORITY_MODEL.md` `People`, owner Person UUID and sharing model; `REIMB-001` beneficiary semantics; prior profile audit boundaries.

**Acceptance / verification boundary:** Implement deterministic Person/relationship identity tests covering immutable UUID allocation/replay, alias/display-name changes, duplicate/ambiguous matching, relationship add/change/remove history and exact endpoint validation. MIRA 2.0 sandbox must persist/read back synthetic people/relationships without exposing personal production data.

---

### `PROFILE-013` — Explicit permission and sharing scopes separate from relationship labels

**Description:** Authorization is represented as explicit owner-approved grants over a named authority/data class/action scope, never inferred from family, caregiver, beneficiary, guardian or household relationships. A grant identifies the exact actor/recipient Person or service identity, authority/resource, scope, permitted actions such as read or read/write, status, provenance and last provider/API verification. Personal, whole-authority shared and scoped-shared authorities are distinct options. No relationship label grants custody, health, finance, school, calendar, email or general private-state access. Provider-side sharing changes count only after remote readback confirms the intended identity and scope; removing or narrowing access follows the same verification rule.

**Why it exists / user outcome:** “This person is my spouse/parent/caregiver” and “this person may read this calendar or edit this household list” remain different facts instead of one privacy incident wearing two database columns.

**Requirement status:** `required / privacy-critical prerequisite`.

**Delivery/evidence:** `STATE_AUTHORITY_MODEL.md` strongly specifies explicit grants, personal/whole/scoped sharing, Authority Registry recording and provider/API readback, and explicitly forbids inferred family access. Parent/minor/caregiver audit features already depend on this boundary. The generic authorization engine and provider adapters are not yet MIRA 2.0 integration-verified, so this feature remains specification/architecture evidence rather than a completed permission system.

**Hard dependencies:** `PROFILE-012`; canonical Authority Registry; provider/API identity and readback capability; privacy/security policy; least-privilege mutation boundary.

**Enables:** safe household/family/caregiver collaboration, shared calendars/state, institutional scopes and downstream permission-sensitive services.

**Legacy evidence:** category-E row 16; `STATE_AUTHORITY_MODEL.md` sharing/collaboration and mutation contracts; prior `PROFILE-004`, `PROFILE-005`, `PROFILE-006`, `REMIND-002` boundaries.

**Acceptance / verification boundary:** Add deterministic authorization fixtures proving relationship labels alone authorize nothing, explicit grants are scope/action-specific, revoked/narrowed grants stop access, cross-authority leakage fails closed and provider/API readback is mandatory. MIRA 2.0 integration must use synthetic identities before any real shared personal data.

---

### `DIST-001` — Private deployment lineage and controlled upstream feature sharing

**Description:** A deployment keeps one durable source lineage for behavior/configuration while mutable personal state remains in canonical runtime authorities. Personal/custom features are private and user-owned by default. Feature ownership/origin, upstream base, local revision, dependencies and rollback policy are recorded. When a private feature becomes reusable, MIRA asks exactly `Do you want to make this feature available to other people?`. A yes authorizes preparation, not publication: personal identifiers/state/provider references are removed, synthetic fixtures and declared permissions/dependencies are added, privacy/source/dependency/tests run, the exact public diff is shown, and publication/opening an upstream PR requires separate explicit publication authority. Upstream updates are deliberate proposal-only reconciliations; local user-owned behavior is preserved by default and cannot be silently deleted, overwritten, re-owned or merged merely because upstream changed.

**Why it exists / user outcome:** MIRA can evolve privately and contribute reusable improvements upstream without turning the user’s life data or working customizations into collateral damage for open-source enthusiasm.

**Requirement status:** `required`.

**Delivery/evidence:** the legacy feature-reconciliation core is `test_verified` for owner/origin tracking, no silent ownership transfer, dependency-scoped blocking/degradation, proposal-only upgrades, keep-current default, local-feature preservation and rollback-checkpoint requirements. `PERSONAL_FORK_LIFECYCLE.md` and `SHARED_FEATURE_WORKFLOW.md` strongly specify sanitization, synthetic fixtures, exact-diff review and separate publication authority. Actual MIRA 2.0 public contribution/publish readback remains integration-unverified.

**Hard dependencies:** Git/managed-source capability with remote readback when source mutation is allowed; `ONBOARD-002`; feature/dependency manifests; public-source privacy audit; explicit publication authority.

**Enables:** private customization, safe upstream contribution, user-owned feature longevity and later update/reconciliation workflows.

**Legacy evidence:** category-E row 17; `PERSONAL_FORK_LIFECYCLE.md`; `SHARED_FEATURE_WORKFLOW.md`; `test_feature_reconciliation.py`; feature lock/dependency map contracts.

**Acceptance / verification boundary:** Preserve deterministic ownership/reconciliation tests; MIRA 2.0 must prove a synthetic user feature remains locally owned across an upstream upgrade proposal, can be sanitized into a public candidate without private state, and cannot be published without explicit publication approval/readback.

---

### `DIST-002` — Deterministic sanitized starter/distribution from one canonical source revision

**Description:** Public/personal/institutional starter distributions are generated products of one exact canonical MIRA source revision, not independent development branches or editable sources of truth. Distribution differences are limited to allowed deployment policy/configuration; portable application behavior comes from the same canonical revision. Each generated tree carries channel/source-revision identity, runs current-tree public-source/privacy audits plus distribution/manifest/dependency/feature/tests, and is remotely verified before release. A generated distribution never inherits mutable production data, secrets or private provider state and cannot silently drift from canonical source. Historical contamination in an old distribution repository is not release payload if the current generated tree is pinned to a clean canonical revision, but canonical reachable history must satisfy the publication boundary before promotion.

**Why it exists / user outcome:** There is one product source instead of three cousins who all claim to be MIRA while quietly accumulating different bugs and somebody’s spreadsheet IDs.

**Requirement status:** `accepted release boundary / required for distribution`.

**Delivery/evidence:** the legacy `Build Distributions` workflow deterministically builds personal/institutional distributions from one exact source SHA, runs source/privacy audits, validates channel/source-revision manifests, compiles code, runs behavior/feature reconciliation and starter tests, then re-audits the generated tree. `distribution/README.md` codifies the same-code/source-of-truth invariant. This gives the legacy distribution boundary genuine `test_verified`/CI-enforced evidence. MIRA 2.0 has not yet produced and remotely verified its own release promotion, so no MIRA 2.0 integration/live credit is inherited.

**Hard dependencies:** canonical clean source lineage; `ONBOARD-002`; deterministic build/promotion pipeline; distribution manifest; CI; remote repository/readback capability.

**Enables:** safe public starter, personal/institutional channels, reproducible releases and later provider/runtime installation.

**Legacy evidence:** category-E row 18; `distribution/README.md`; `.github/workflows/build-distributions.yml`; privacy/source/distribution validators.

**Acceptance / verification boundary:** Port deterministic build/audit/manifest tests to MIRA 2.0, generate synthetic distributions from an exact commit, remotely read back source revision/channel/tree identity and require green CI before declaring release completion.

---

### `DEV-004` — Bounded private custom skill/feature creation with declared contracts

**Description:** MIRA may help a user create a new private reusable behavior from repeated friction or an explicit request without requiring the user to design implementation details. Before building, MIRA inspects existing features/skills/dependencies to avoid duplication; defines the behavior, authority/state boundary, required/optional capabilities, permissions, failure domain and acceptance criteria; works on a feature branch; keeps private data/secrets out of portable source; records ownership/lineage/dependencies; adds executable tests and synthetic fixtures; validates/reconciles/readbacks a coherent private checkpoint; and keeps the result private by default. Packaging as a portable feature/skill and publication are separate later decisions governed by `DIST-001`.

**Why it exists / user outcome:** The user can say what recurring problem should be solved while MIRA handles the tedious software-company bits, which is fortunately the arrangement humans invented computers for before assigning them meeting attendance.

**Requirement status:** `proposed / accepted direction`.

**Delivery/evidence:** `SHARED_FEATURE_WORKFLOW.md` defines the nontechnical creation workflow. Feature-manifest validation/tests genuinely enforce required manifest/runtime contracts, safe paths, no personal data in shared source, semantic-version/config-schema validity and executable-test/script requirements before `implemented` status. Feature-reconciliation tests add ownership/dependency safeguards. These are strong tooling primitives, but the audit did not locate a complete autonomous end-to-end custom-skill builder that executes the whole workflow without developer orchestration, so the feature is `specified/partially implemented`, not fully test-verified as a builder.

**Hard dependencies:** `DEV-001`/`DEV-002`; feature/dependency registry; source-write/readback capability when enabled; privacy/source audits; `DIST-001` for optional sharing.

**Enables:** safe private extensibility, future Feature Studio-style experiences and reusable user-developed modules without uncontrolled source bloat.

**Legacy evidence:** category-E row 19; `SHARED_FEATURE_WORKFLOW.md`; `test_feature_manifest.py`; `test_feature_reconciliation.py`; feature manifest/dependency contracts.

**Acceptance / verification boundary:** Implement a bounded MIRA 2.0 flow that takes a synthetic outcome request through duplicate inspection, contract creation, branch/checkpoint, manifest/dependency registration, tests/privacy validation and remote readback while remaining private. Publication must remain a separate explicit `DIST-001` action.

---

### `ONBOARD-001` E4 audit refinement — instruction updates are capability-gated full replacements

Historical category-E row 20 is normalized into the existing `ONBOARD-001`, not a duplicate feature. Automatic instruction mutation is technically constrained and must never be assumed from runtime identity or unrelated connector access. Durable behavior should live in versioned policy/source where possible. When a Project Instructions, global Custom Instructions or equivalent block must change and no verified direct-write/readback capability exists, MIRA provides the **complete replacement text**, clearly states which existing block to replace, and gives simple nontechnical UI steps. Only a user-requested patch may be partial. A future direct-write path may be used only after exact capability/target verification and readback.

**Requirement status:** `current required governance behavior`.

**Delivery/evidence:** current MIRA Project Instructions implement the complete-replacement rule; legacy `project/INSTRUCTIONS.md.tmpl` already requires a complete `PROJECT INSTRUCTIONS UPDATE` when direct Project write capability is unavailable. No general direct ChatGPT Project/Custom Instructions mutation/readback implementation is proven, so automated UI mutation remains unverified rather than promised.

**Hard dependencies:** exact instruction-surface capability discovery; source/versioned policy where applicable; user-visible full-replacement template; direct-write readback only if capability exists.

**Acceptance / verification boundary:** Test the fallback output contract and target labeling; if a direct-write integration is ever introduced, separately prove exact target, bounded write and readback before suppressing the copy/paste replacement path.

## Category E4 consistency findings

- Person identity (`PROFILE-012`) and authorization (`PROFILE-013`) are separate authorities. A relationship edge never grants access.
- Beneficiary/reimbursement relationships may reference the Person graph but do not imply permission or replace the general identity model.
- Sharing mutable state and sharing reusable source/features are separate operations with separate approval/readback boundaries.
- `DIST-001` preserves user-owned private behavior by default; publication is a separately approved sanitized operation.
- `DIST-002` treats generated starter/distribution repositories as reproducible release products, not alternate sources of truth.
- `DEV-004` gives MIRA a private-by-default extensibility workflow, but current validators/workflows do not justify claiming a completed autonomous builder.
- Historical automatic instruction updates are normalized into `ONBOARD-001`; full replacement is the supported fallback, direct UI mutation remains capability-gated.
- No E4 feature is promoted to MIRA 2.0 integration/live verification from legacy source/tests alone.

## Audited nontechnical source/runtime onboarding features

### `ONBOARD-006` — Browser-only nontechnical installation with no terminal fallback

**Description:** Default MIRA installation for an ordinary personal user is a browser-only flow. The user does not open Command Prompt, PowerShell, Terminal, Git Bash or a code editor; does not install Git or GitHub CLI; and does not paste commands, tokens, SSH keys or passwords. The personal path creates a private repository through the audited GitHub web-template flow, connects the exact repository to the required runtime capabilities and verifies owner, visibility, default branch, source revision and capability status before setup is called successful. If the required template, runtime skill or source-write capability is unavailable, onboarding reports a specific blocked state and stops that path rather than substituting a fork, Codespace, download, local clone or shell instructions. Developer/CLI setup may exist separately only after the user explicitly chooses developer mode.

**Why it exists / user outcome:** A nontechnical user can install MIRA without being ambushed halfway through by `git clone`, a token prompt or the usual industry ritual of pretending a terminal is self-explanatory.

**Requirement status:** `current required`.

**Delivery/evidence:** the legacy browser installer is `test_verified`. `INSTALL.md` explicitly prohibits terminal/CLI fallbacks; `install-flow.json` defines `nontechnical-browser-only`, private GitHub-template creation, blocked states and forbidden actions; `test_nontechnical_installation.py` directly asserts the no-terminal wording, absence of `git clone`/`gh repo create`, private browser template flow, fail-closed template behavior, alternate-runtime/enterprise browser lanes and required verification fields. Live MIRA 2.0 installation has not yet been integration-verified.

**Hard dependencies:** `DIST-002`; `ONBOARD-002`; `SOURCE-001`; current browser/runtime product surfaces; exact repository/capability readback.

**Enables:** genuinely nontechnical personal onboarding, later provider setup and ordinary-user distribution without local development tooling.

**Legacy evidence:** category-E row 21; `starter/INSTALL.md`; `starter/install-flow.json`; `starter/tests/test_nontechnical_installation.py`.

**Acceptance / verification boundary:** Port the machine-readable installer contract/tests to MIRA 2.0 and perform one synthetic browser-only install from the MIRA 2.0 starter. Verify no CLI/local tooling is required, blocked capabilities stay blocked, and the created private source/readback matches the intended deployment.

---

### `SOURCE-001` — Independent source read, source write and remote-readback capability gates

**Description:** Durable source access is not one Boolean. MIRA tracks at least source read, source write and source remote readback independently for the exact repository/source target. In the personal ChatGPT/Codex lane the ChatGPT GitHub app may prove repository read while Codex separately proves bounded write; read access is never evidence of write authority. Lasting source/config changes are called successful only after the intended remote source commit/state is read back. Missing source write may degrade or block durable personal source mutation without preventing unrelated conversational/onboarding work. An authorization button, readable file, local copy or provider brand is not proof of write/readback.

**Why it exists / user outcome:** “I can see your repo” stops being translated into “therefore I can safely commit to it,” a leap that has caused enough software damage without MIRA joining in.

**Requirement status:** `current required / integrity boundary`.

**Delivery/evidence:** the legacy gate is `test_verified`. `install-flow.json` has separate `chatgpt-github-read` and `codex-github-write` gates and requires remote write/readback evidence. `test_nontechnical_installation.py` asserts those gates are independent. `provider_capability_router.py` requires `source_read`, `source_write` and `source_remote_readback` for verified durable source mutation in user/organization Git lanes; `test_platform_portability.py` verifies missing write/readback degrades rather than being falsely claimed.

**Hard dependencies:** exact source target identity; runtime/source connector capability; remote source readback; `DIST-001`/`DEV-004` when source mutation is performed.

**Enables:** honest Git/source onboarding, safe durable configuration changes, private custom features and verified releases.

**Legacy evidence:** category-E row 22; `INSTALL.md`; `install-flow.json`; `provider_capability_router.py`; `test_nontechnical_installation.py`; `test_platform_portability.py`.

**Acceptance / verification boundary:** Port deterministic gate tests to MIRA 2.0 and prove against a synthetic repository that read-only access cannot satisfy write, a bounded source write requires remote commit readback, and a moved/unauthorized target fails closed rather than reporting success.

---

### `PROVIDER-001` — Provider-neutral AI runtime capability routing from observed evidence

**Description:** MIRA supports ChatGPT/Codex, Claude, approved Microsoft/organizational AI, Gemini, local-model and generic MCP-capable runtimes only through observed capability contracts. Runtime/provider name, connection button, readable integration, plan marketing or local client presence never establishes feature parity. The router evaluates the exact runtime/deployment, data classification, organization approval evidence, source mode and observed capabilities such as state/evidence read-write-readback, email read, calendar projection and scheduled delivery. Unknown capability/request keys fail closed. Regulated-sensitive data is blocked unless the exact runtime/storage/use/actions are organization-approved with current approval evidence. Missing optional capabilities degrade only affected paths; missing required capabilities block the affected plan/module rather than being invented.

**Why it exists / user outcome:** MIRA can move between AI products without claiming that every logo has secretly implemented the same connector, scheduler and permission model.

**Requirement status:** `current required`.

**Delivery/evidence:** the legacy provider-neutral router is `test_verified`. `provider_capability_router.py` deterministically evaluates observed capability booleans and never uses provider name as proof. `test_platform_portability.py` verifies a fully observed lane, proves Claude/Microsoft labels cannot bypass missing source-write evidence, blocks regulated data without approval/reference, verifies managed-source degradation, optional adapter degradation and unknown-key failure. `platform-capabilities.json` and `PLATFORM_PORTABILITY.md` define the portable runtime/storage/source contract.

**Hard dependencies:** observed runtime/tool capabilities; data-classification/approval state; `SOURCE-001`; provider/resource identity/readback for any live adapter.

**Enables:** ChatGPT-first product portability, alternate AI runtimes, regulated deployment gating and future provider adapters without false parity claims.

**Legacy evidence:** category-E row 23; `PLATFORM_PORTABILITY.md`; `platform-capabilities.json`; `provider_capability_router.py`; `test_platform_portability.py`.

**Acceptance / verification boundary:** Port the router/manifest/tests to MIRA 2.0, keep capability evaluation deterministic/fail-closed, then integration-verify representative runtime lanes only from their exact observed tools and readback. No runtime receives live feature credit from its brand name.

---

### `SOURCE-002` — Explicit personal Git, organization Git, managed-central and no-Git/manual source lanes

**Description:** MIRA treats durable source mode as deployment configuration rather than forcing every user into a personal GitHub account. Supported modes are personal/user Git, approved organization Git, managed-central source and explicit no-Git/manual portability. Personal Git may use the browser template/private-repository path. Organization Git may use approved GitHub Enterprise, GitLab, Azure Repos or equivalent source with exact read/write/readback. Managed-central source lets administrators maintain a pinned release so end users need no Git account; personal behavior/source changes are blocked or routed through the approved managed change process. No-Git/manual mode may consume pinned releases and deliberate CSV/JSON/ICS/document exchanges but cannot claim durable personal source mutation, unattended synchronization or automated writes. Mutable personal state never moves into Git merely because source mode changes.

**Why it exists / user outcome:** MIRA can work for a personal user, a locked-down employee or someone with no Git account without instructing the last two to create a personal GitHub account behind IT’s back. Revolutionary stuff: respecting the deployment environment.

**Requirement status:** `current required`.

**Delivery/evidence:** the legacy source-mode contract is `test_verified`. `provider_capability_router.py` accepts exactly `user-git`, `organization-git`, `managed-central`, and `none` and assigns distinct required/degraded behavior. `test_platform_portability.py` verifies managed-central operation and remote-readback degradation. `platform-capabilities.json` enumerates personal GitHub, GitHub Enterprise, GitLab, Azure Repos, managed-central and portable-manual deployment lanes. `INSTALL.md` explicitly forbids personal-account workarounds in corporate/government/health-care environments.

**Hard dependencies:** `SOURCE-001`; `PROVIDER-001`; approved source identity/policy for organization/managed lanes; `DIST-002` for pinned releases; privacy/state authority separation.

**Enables:** consumer, enterprise-managed and manual portability without source-control coercion or shadow IT.

**Legacy evidence:** category-E row 24; `INSTALL.md`; `PLATFORM_PORTABILITY.md`; `platform-capabilities.json`; `provider_capability_router.py`; `test_platform_portability.py`.

**Acceptance / verification boundary:** Preserve deterministic source-mode tests in MIRA 2.0 and integration-verify at least one personal Git and one managed/no-user-Git lane with synthetic data. Prove `none` cannot report durable source mutation and organization/managed lanes never require a personal-account bypass.

## Category E5 consistency findings

- `ONBOARD-006` owns ordinary-user installation UX; it does not itself grant source or provider capabilities.
- `SOURCE-001` owns source read/write/readback truth. ChatGPT read and Codex write are one current adapter example, not hard-coded universal architecture.
- `PROVIDER-001` owns runtime capability claims. Runtime/provider names never imply parity, approval or action support.
- `SOURCE-002` owns source-lineage mode. Personal Git is one lane, not a prerequisite for all MIRA users.
- Managed-central and no-Git/manual lanes preserve the distinction between portable source and mutable personal state.
- Nontechnical onboarding never uses a CLI fallback to paper over a missing browser/runtime capability; blocked means blocked until an approved path exists.
- Regulated-sensitive use is separately gated by exact organization approval evidence and does not inherit permission from runtime availability.
- All four E5 features have genuine deterministic legacy tests, but none receives MIRA 2.0 integration/live verification until the new repo/runtime lanes are exercised and read back.

## Audited provider onboarding and bootstrap features

### `PROVIDER-002` — Browser-only provider authority onboarding with exact resource readback

**Description:** MIRA onboards selected structured-state, retained-evidence, mail and calendar providers through browser or organization-approved integration surfaces and treats every provider capability as an independently verified fact. Setup records the exact signed-in identity and tenant/workspace where relevant, the selected narrowly scoped resource, stable provider ID/URL, requested action scope, bounded read, approved harmless synthetic write where mutation is required, and readback of that exact provider record before declaring the capability installed. Google may use native Sheets/Drive plus optional Gmail/Calendar; Microsoft may use Microsoft Lists or an explicit Excel table plus OneDrive/SharePoint and optional Outlook; Apple/iCloud remains an explicit user-mediated import/export/ICS lane unless a specific adapter proves more. Regulated-sensitive use additionally requires current organization approval evidence for the exact runtime, storage, purpose and action set. A connection badge, provider name, tenant login, readable file or broad OAuth scope is never proof of mutation/readback capability.

**Why it exists / user outcome:** Connecting an account should prove what MIRA can actually do with the exact resources the user selected instead of translating a cheerful “Connected” badge into imaginary write access to an entire cloud estate.

**Requirement status:** `current required`.

**Delivery/evidence:** the legacy provider-onboarding contract is `test_verified` at the browser/onboarding-contract level. `PROVIDER_ONBOARDING.md` explicitly defines Google, Microsoft 365/OneDrive/SharePoint, Apple/iCloud, alternative-AI and institutional lanes plus the common bounded read → write → readback transaction. `install-flow.json` wires provider onboarding into structured-state/evidence capability gates and explicit blocked/manual-only states. `test_nontechnical_installation.py` regression-tests the presence of the Google/Microsoft/Apple/alternative-runtime browser lanes, no-terminal behavior and read/write/readback wording. Actual provider mutations for these lanes are not MIRA 2.0 integration-verified.

**Hard dependencies:** `ONBOARD-006`; `PROVIDER-001`; exact provider/account/resource identity; Authority/Integration Registry state; provider read/write/readback capability; current organization approval evidence when regulated-sensitive.

**Enables:** safe provider-specific structured state/evidence/calendar/mail setup, `PROVIDER-003`, later Microsoft/Apple adapters and honest manual/degraded portability.

**Legacy evidence:** category-E row 25; `starter/PROVIDER_ONBOARDING.md`; `starter/install-flow.json`; `starter/tests/test_nontechnical_installation.py`.

**Acceptance / verification boundary:** Port the provider-onboarding contract/tests to MIRA 2.0. Integration verification requires synthetic setup against exact provider resources with identity/resource/action readback; at least one Google lane and one non-Google or explicit manual lane must prove that unsupported automation remains degraded/manual rather than being fabricated.

---

### `ONBOARD-007` — Installable provider-neutral MIRA orchestration skill

**Description:** MIRA has one portable installable orchestration package that supplies the provider-neutral runtime behavior needed for onboarding, dependency preflight, Integration Registry capability checks, control-cycle routing, planning and provider-adapter invocation. The legacy package ID `life-planner` is a compatibility identifier only; it is not the product name or a license to expose legacy branding. The package is installed from the exact deployment source/release and must never substitute the developer/reference deployment’s personal Ops skill or mutable production state. Provider names, personal schedules, private accounts and provider resource IDs are deployment data or adapter configuration, not hard-coded product identity. Missing dependencies are surfaced in ordinary language and do not authorize the package to connect accounts, create resources, change permissions or enable services automatically.

**Why it exists / user outcome:** A new MIRA deployment receives the same portable reasoning/orchestration behavior without inheriting somebody else’s personal brief policy, accounts, schedules or Google layout.

**Requirement status:** `current required / foundational onboarding runtime`.

**Delivery/evidence:** the legacy package is `implemented`, and its installation/package-presence boundary is `test_verified`. `starter/life-planner/SKILL.md` defines provider-neutral routing, dependency preflight, Integration Registry behavior, safe provider remediation and core transaction boundaries. `install-flow.json` names the package independently from provider setup, while `test_nontechnical_installation.py` verifies that `SKILL.md`, the provider adapter blueprint/verifier and the `life-planner-skill` capability gate exist and explicitly forbids falling back to the reference deployment skill. A complete MIRA 2.0 installed-skill runtime smoke is not yet integration-verified.

**Hard dependencies:** `ONBOARD-002`; `ONBOARD-006`; `SOURCE-001`; `PROVIDER-001`; canonical behavior/dependency registry; exact deployment source/release identity.

**Enables:** portable first boot, provider adapters, deterministic bootstrap, dependency-aware operational modules and later runtime portability without duplicating MIRA logic per provider.

**Legacy evidence:** category-E row 26 split; `starter/life-planner/SKILL.md`; `starter/install-flow.json`; `starter/tests/test_nontechnical_installation.py`.

**Acceptance / verification boundary:** Port the package under canonical MIRA branding, preserve its provider-neutral contracts, install it from one synthetic MIRA 2.0 source/release, and prove runtime discovery/preflight plus one provider-adapter handoff without importing reference-deployment private state or requiring a CLI for the ordinary-user path.

---

### `PROVIDER-003` — Deterministic Personal Google bootstrap adapter with strict drift/readback verification

**Description:** The Personal Google adapter deterministically converts approved onboarding configuration into a plan for one required core authority plus only the optional modules the user selected. The plan binds exact deployment/owner UUIDs, canonical IANA timezone, source repository and exact source commit, Google identity, module/failure-domain resources, native Sheets requirements, ordered headers/seed rows, Drive folders, Authority Registry, Interview Ledger, Integration Registry, People, Services and Run Log, then protects the plan with a deterministic hash. Verification rejects plan tampering and blocks core readiness on source repository/commit/read/write/remote-readback/CI drift, Google Drive identity mismatch, missing/wrong workbook/folder identity, non-native Sheets, spreadsheet-timezone drift, header/seed drift or missing provider IDs/URLs. Optional Gmail, Calendar and scheduled-delivery failures degrade only their selected paths; full scheduled readiness requires observed firing while manual use may remain ready. The adapter plans/verifies provider state; its existence does not prove live Google provisioning.

**Why it exists / user outcome:** Personal Google onboarding can create the exact MIRA resources requested and prove they match the intended schema instead of declaring success because several spreadsheets with plausible names appeared in Drive.

**Requirement status:** `current required for Personal Google lane`.

**Delivery/evidence:** the deterministic legacy plan/verifier core is `test_verified`. `personal-google-blueprint.json` defines required core plus module-scoped optional authorities. `google_bootstrap.py` validates provider/schema/module IDs, exact configuration types, UUIDs, IANA timezone, source repo/SHA, Google identity, plan hash and provider readback. `test_personal_google_bootstrap.py` directly covers required/optional module selection, fail-closed unknown modules/timezones/nonboolean gates, exact ready readback, source/header/timezone/seed/identity drift, plan tampering, optional Gmail/Calendar/scheduler degradation and strict failure behavior. No MIRA 2.0 Google sandbox has yet been provisioned/read back through this adapter, so integration/live status remains unverified.

**Hard dependencies:** `ONBOARD-007`; `PROVIDER-002`; `SOURCE-001`; exact Personal Google identity and provider capabilities; canonical MIRA schema/Authority Registry; `ONBOARD-005`/`OPS-003` only when recurring scheduling is selected.

**Enables:** separate MIRA 2.0 Personal Google sandbox, canonical Google-backed MIRROR state, later `CORE-ROUNDTRIP` proof and provider-adapter comparison without making Google the product architecture.

**Legacy evidence:** category-E row 26 split; `starter/life-planner/assets/personal-google-blueprint.json`; `starter/life-planner/scripts/google_bootstrap.py`; `starter/life-planner/references/personal-google-onboarding.md`; `starter/tests/test_personal_google_bootstrap.py`.

**Acceptance / verification boundary:** Port the deterministic core/tests, then use only a separate synthetic MIRA 2.0 Google namespace to plan/provision/read back the exact selected modules. Verify provider IDs, source revision, schema/headers/seeds/timezone, optional degradation and one full ready transaction without touching legacy production.

## Category E consistency result

Category E is complete through all 26 historical rows. The final authority/dependency model is:

- Rows 1-5 map to `ONBOARD-002` through `ONBOARD-005` plus `SERVICE-001`; rows 6-10 map to `PROFILE-001` through `PROFILE-005`; rows 11-15 map to `PROFILE-006` through `PROFILE-011`; rows 16-20 map to `PROFILE-012`, `PROFILE-013`, `DIST-001`, `DIST-002`, `DEV-004` and the `ONBOARD-001` refinement; rows 21-24 map to `ONBOARD-006`, `SOURCE-001`, `PROVIDER-001` and `SOURCE-002`; row 25 maps to `PROVIDER-002`; row 26 intentionally splits into `ONBOARD-007` and `PROVIDER-003`.
- Historical combined rows are split only where different authority, permission or verification boundaries require it. The split does not manufacture extra historical requirements.
- `ONBOARD-006` owns ordinary-user browser installation UX. It does not prove source access, runtime parity or provider mutation.
- `SOURCE-001`/`SOURCE-002` own durable source capability/mode. Source access is not provider-state access and personal Git is not universal.
- `PROVIDER-001` owns runtime capability routing; `PROVIDER-002` owns account/resource onboarding; `ONBOARD-007` owns portable MIRA orchestration; `PROVIDER-003` is one Personal Google adapter beneath those contracts.
- Google is an adapter and current first vertical, not MIRA’s architecture. Microsoft and future providers can implement the same logical authority/readback contracts without inheriting Google resource shapes.
- Apple/iCloud remains explicit manual/user-mediated portability unless an exact adapter proves unattended actions. MIRA does not upgrade manual import/export into imaginary synchronization.
- Provider names, connection badges, readable resources, relationship labels and AI brands are never permissions or capability proof. Exact identity, scope, bounded action and readback remain separate evidence.
- The portable MIRA package may route remediation but cannot silently connect providers, create resources, enable services or grant permissions.
- Legacy deterministic tests establish strong implementation evidence for several E features, but no category-E feature is promoted to MIRA 2.0 integration/live verification until the new source/runtime/provider path is exercised with synthetic state and read back.
- No live Google production state was touched during category-E audit and no executable MIRA 2.0 product behavior was changed.

## Audited core life-service composition features

### `SERVICE-002` — Activatable service bundles over canonical behaviors with dependency-derived readiness

**Description:** A MIRA life service is an activatable, user-facing bundle over already-canonical behaviors, authorities and capabilities rather than a duplicate implementation of those behaviors. `SERVICE-001` owns whether the user has enabled, disabled, deferred or left the service unresolved. `SERVICE-002` owns what an enabled/catalogued service depends on and how readiness is derived. Required child behavior/capability/authority failure blocks only that service and its dependents; optional failure degrades only that service path. Service dependency evaluation never installs a dependency, enables another behavior, mutates provider state or treats a recommendation as activation. The catalog and dependency map must remain complete, cycle-safe and semantically aligned with the canonical feature registry.

**Why it exists / user outcome:** MIRA can expose simple choices such as “Briefs,” “Email triage” or “Orders” while still knowing exactly which underlying behaviors have to work. A friendly service name does not get to hide missing safety, provider or data dependencies behind a green toggle.

**Requirement status:** `required for modular service composition`.

**Delivery/evidence:** the generic legacy service-composition/dependency core is `test_verified`. `behavior-dependencies.json` models category-F services as aggregate behaviors with `requires_behaviors`/`optional_behaviors`; `behavior_dependency_check.py` validates unknown references, required dependency cycles and the fail-isolated block/degrade policy, recursively derives dependency status, and explicitly forbids automatic dependency installation or behavior enablement. `test_behavior_dependency_check.py` proves every forensic catalog row has one dependency assignment and directly proves aggregate service `f-05` blocks when required child `c-06` is unavailable while unrelated workflows remain unchanged. `onboarding_profile_router.py` and its tests separately prove finite service activation and implementation-capability status. MIRA 2.0 has not yet persisted/read back service state or run an end-to-end activation → dependency-readiness transaction.

**Hard dependencies:** `SERVICE-001`; canonical behavior/dependency registry; `RECOVERY-002`; `PROVIDER-001`/Integration Registry for live capability evidence; exact service-to-behavior mappings.

**Enables:** all category-F life-service modules, capability-aware onboarding, role-based recommendations, honest blocked/degraded service status and modular future services without duplicating domain logic.

**Legacy evidence:** category-F aggregate dependency assignments; `starter/MODULE_CATALOG.md`; `starter/behavior-dependencies.json`; `starter/tools/behavior_dependency_check.py`; `starter/tools/integration_dependency_router.py`; `starter/tools/onboarding_profile_router.py`; `starter/tests/test_behavior_dependency_check.py`; `starter/tests/test_integration_dependency_router.py`; `starter/tests/test_onboarding_profile_router.py`.

**Acceptance / verification boundary:** Port the catalog/dependency/activation contracts to MIRA 2.0 and prove with synthetic service state that an enabled service derives readiness only from its declared canonical behaviors and verified authorities/capabilities, a missing required dependency blocks only affected services, optional dependency failure degrades only affected paths, disabled services stay disabled, and no dependency remediation changes state without explicit authorization/readback.

## F1 service mappings

### F row 1 — Briefs/action digest

**Canonical mapping:** service key `briefs` → `OPS-001`, `OPS-003`, `OPS-004`, `RECOVERY-001`, `RECOVERY-002`, governed by `SERVICE-001` + `SERVICE-002`. The legacy `f-01` aggregate maps to A1/A3/A4/A15/A16.

**Evidence ceiling:** aggregate service is catalogued as executable/CI-evidenced and its underlying scheduling/recovery cores carry their already-audited evidence levels. The service wrapper itself inherits only the generic `SERVICE-002` test evidence until MIRA 2.0 service-state/readiness integration is proven.

**Dependency defect:** legacy `f-01` omits A2 / `OPS-002`. MIRA 2.0 Brief-service readiness must require the canonical single-dispatcher/no-duplicate-schedules invariant rather than permitting a service to appear ready while parallel legacy schedules exist.

### F row 2 — Next-action planner

**Canonical mapping:** service key `next_actions` → `TASK-001`, `TASK-002`, governed by `SERVICE-001` + `SERVICE-002`. Legacy `f-02` requires A13/A14.

**Evidence ceiling:** service is workflow/documented at the historical F layer. `TASK-001` is test-verified; `TASK-002` remains specification/skill-level. The aggregate service cannot outrank its weakest required canonical behavior.

### F row 3 — Email triage

**Canonical mapping:** service key `email_triage` → `MAIL-001`, `MAIL-002`, `MAIL-003`, governed by `SERVICE-001` + `SERVICE-002`. Legacy `f-03` requires B7/B8/B9.

**Evidence ceiling:** service is workflow/documented. This mapping correctly includes the no-automatic-outbound-contact safety invariant and explicit archive-approval behavior; enabling triage never grants email-send authority.

### F row 4 — Orders/shipments

**Canonical mapping:** service key `orders_shipments` → `ORDER-001`, `ORDER-002`, `ORDER-003`, `ORDER-005`, governed by `SERVICE-001` + `SERVICE-002`. Legacy `f-04` requires C1/C2/C3/C5.

**Evidence ceiling:** historical aggregate is executable/documented and underlying order cores have mixed test/specification evidence already recorded in category C. Service readiness must reflect those actual child levels rather than the old aggregate label.

**Dependency defect:** legacy `f-04` omits C4 / `ORDER-004`. MIRA 2.0 Orders/shipments readiness must include replacement/supersession correctness so a service cannot be called ready while replacement transactions can duplicate spend or state.

### F row 5 — Receipt archive

**Canonical mapping:** service key `receipt_archive` → `RECEIPT-001`, `RECEIPT-002`, `RECEIPT-003`, governed by `SERVICE-001` + `SERVICE-002`. Legacy `f-05` requires C6/C7/C9.

**Evidence ceiling:** historical aggregate is executable/documented. The generic aggregate-block behavior has direct test coverage using `f-05`, but `RECEIPT-003` remains specification-level, so complete MIRA 2.0 Receipt-archive service readiness remains unproven until that required child behavior exists and service integration is tested.

## Category F1 consistency findings

- The first five category-F rows are service compositions, not new copies of `OPS-*`, `TASK-*`, `MAIL-*`, `ORDER-*` or `RECEIPT-*` behavior.
- `SERVICE-001` answers **whether the user enabled the service**. `SERVICE-002` answers **what that service requires and whether those requirements are currently ready**. Neither concept may substitute for the other.
- Service readiness is derived from canonical child behavior plus verified authority/capability state. A historical aggregate label such as `executable` cannot raise a weak/unimplemented child behavior to a higher evidence level.
- Briefs must add `OPS-002` to its required dependency bundle when MIRA 2.0 ports the legacy map.
- Orders/shipments must add `ORDER-004` to its required dependency bundle when MIRA 2.0 ports the legacy map.
- Legacy `order_lifecycle_enabled` is only a compatibility input mapped to `orders_shipments` even though its onboarding prompt says “receipt and order lifecycle.” Canonical MIRA 2.0 keeps `orders_shipments` and `receipt_archive` separately activatable; compatibility migration must not silently enable/disable or misstate the other service.
- Email triage explicitly includes `MAIL-002`; service activation therefore never implies outbound-send permission.
- Orders/shipments and Receipt archive remain separate service bundles over related but distinct fulfillment, purchase/evidence and classification authorities. Neither bundle absorbs financial settlement by implication.
- `RECOVERY-002` failure isolation applies at service composition boundaries: missing requirements block/degrade only affected services and their explicit dependents.
- No F1 service receives MIRA 2.0 integration/live verification from legacy catalog labels, skill prose or deterministic legacy tests alone.

## Audit status

- Categories A, B, C, D and E are complete.
- Category F is in progress. Rows F1-F5 are audited in `M2-G0-007A`; row F6 **Personal finance organization** is the next unaudited category-F behavior.
- Category G remains unaudited.
- The complete historical feature inventory remains in progress until F and G are closed.
