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
- `INV-*` — inventory, hierarchical locations, movement, scanning, par levels;
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

## Audit status

- Categories A, B and C are complete.
- `M2-G0-005A` audited category-D rows 1-5 as `ASSET-001`, `FITMENT-001`, `ASSET-002`, `ASSET-003`, `IDENT-001`, `EVID-001`.
- The complete historical feature inventory is still in progress.
- The next bounded audit begins with category-D row 6: manual discovery and canonical Drive retention.
