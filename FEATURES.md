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
- `ASSET-*` — assets, fitment, specifications, manuals, maintenance;
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

**Requirement:** required. **Evidence:** specified; provider uniqueness unverified. **Dependencies:** `OPS-001`, provider enumeration/readback. **Verification:** enumerate provider tasks and prove intended job uniqueness.

### `OPS-003` — Canonical runtime clock gate with DST-safe slot matching
**Description:** Runtime-owned offset-aware clock converted through IANA timezone rules decides bounded scheduled entry; model/device/travel clocks are not authority.

**Requirement:** required by failure evidence. **Evidence:** `test_verified`; live scheduler path unverified. **Dependencies:** runtime clock/timezone DB, `OPS-001`. **Verification:** DST/offset/grace tests plus actual scheduled invocation.

### `OPS-004` — Fresh standalone run delivery with deterministic Run ID
**Description:** Each scheduled brief starts fresh and uses deterministic `OPS-YYYY-MM-DD-AM|PM` identity for output and idempotent Run Log updates.

**Requirement:** required. **Evidence:** `test_verified` ID generation; live standalone delivery unverified. **Dependencies:** `OPS-003`, `RECOVERY-001`, scheduler fresh-run capability.

### `OPS-005` — Deterministic HOME/ROAD context with explicit overrides
**Description:** Base HOME/ROAD state comes from canonical weekly transitions and explicit override records; generalized context and active Trip forcing remain separate capabilities.

**Requirement:** required. **Evidence:** `test_verified`; MIRA 2.0 state integration unverified. **Dependencies:** canonical state and timezone-aware override semantics.

### `CTX-001` — Configurable operating-context pairs
**Description:** MIRA supports two-label operating contexts such as HOME/ROAD, HOME/TRUCK, HOME/FIELD, HOME/CAMPUS, HOME/AWAY and custom labels; HOME/OFFICE is valid through custom configuration.

**Requirement:** accepted direction. **Evidence:** `test_verified` legacy router candidate; MIRA 2.0 integration unverified. **Dependencies:** profile/context authority and explicit selection.

### `CTX-002` — Evidence-gated context recommendation and explicit activation
**Description:** Job/duties may recommend context but never silently enable it; confirmation/user labels control activation and ambiguity remains unresolved.

**Requirement:** required. **Evidence:** `test_verified` legacy router candidate; MIRA 2.0 onboarding/readback unverified. **Dependencies:** profile intake, `CTX-001`, confirmation state.

### `TRIP-001` — Independent trip occurrence lifecycle
**Description:** Trip occurrences are separate from reusable Route knowledge, context and paid mileage, with stable identity and Planned/Active/Arrived/Cancelled lifecycle.

**Requirement:** required. **Evidence:** `test_verified` legacy separation/precedence; MIRA 2.0 persistence unverified. **Dependencies:** Trip authority/stable IDs/context precedence.

### `ROUTE-001` — Learned routes, directional runtime, location and ETA inference
**Description:** Reusable Route knowledge is separate from Trip occurrences; supports directional route/runtime, runtime-derived ETA, location evidence and bounded progress primitives.

**Requirement:** required. **Evidence:** `test_verified` for route-average ETA/primitives; human-facing ahead/behind and MIRA 2.0 integration unverified. **Dependencies:** `TRIP-001` and stable route identity/evidence.

### `WEATHER-001` — Context-gated HOME and ROAD weather intelligence
**Description:** HOME permits relevant home weather; ROAD may activate bounded route/corridor weather and official road-condition checks tied to Trip/watch state.

**Requirement:** required. **Evidence:** `test_verified` deterministic gates/expiry; external NWS/DOT/511 unverified in MIRA 2.0. **Dependencies:** context, `TRIP-001`, `ROUTE-001`, `RECOVERY-002`.

### `MILE-001` — Company-paid mileage and deterministic gross-pay reporting
**Description:** MIRA reports company-paid miles, not map/odometer distance, and computes gross estimate from verified rate. Both Thursday brief slots report the closed cycle with explicit status/correction/missing-evidence handling.

**Requirement:** required. **Evidence:** `test_verified`; MIRA 2.0 persistence/live Thursday delivery unverified. **Dependencies:** `MILE-002`, paid-mile/rate evidence, `OPS-001`, `RECOVERY-002`, optional `TRIP-001` linkage.

### `MILE-002` — Separate authoritative Miles & Pay tracker
**Description:** Mileage/pay state lives in a dedicated logical authority preserving stable occurrences, pay-week history, paid miles, rate, gross, provenance/status and corrections; storage backend is an adapter.

**Requirement:** required. **Evidence:** legacy live authority exists; MIRA 2.0 sandbox authority unverified. **Dependencies:** MIRROR state contract, stable IDs, `MILE-001`.

### `TASK-001` — Structured task hierarchy and one-action-per-item rendering
**Description:** Stable Task identity plus priority → classification → optional subsystem → task; each action remains an independent canonical record/bullet with context/window-driven actionability.

**Requirement:** required. **Evidence:** `test_verified`; MIRA 2.0 persistence unverified. **Dependencies:** task authority/stable IDs/context where applicable.

### `TASK-002` — Evidence-grounded next actions and honest completion state
**Description:** Smallest useful next actions derive from canonical open work, deadlines, prerequisites, blocks and context. Partial/completed/missed/removed/blocked state follows evidence; silence never means Done.

**Requirement:** accepted/integrity rule. **Evidence:** specified/skill workflow; generic cross-domain engine not yet test-verified. **Dependencies:** `TASK-001` plus applicable planning evidence.

### `RECOVERY-001` — Phase-aware Run Log, durable checkpoints and circuit-breaker recovery
**Description:** Durable run/recovery evidence uses stable Run IDs, phase/status/health/mutation evidence, bounded retries and verified-state preservation/readback with a specific recovery action.

**Requirement:** required. **Evidence:** `test_verified` core Run Log/selected degradation paths; broader circuit-breaker strongly specified; MIRA 2.0 live scheduled evidence unverified. **Dependencies:** stable run IDs, recovery authority, `OPS-003`, provider readback.

### `RECOVERY-002` — Explicit module dependency boundaries and failure isolation
**Description:** Modules/authorities remain separate failure domains unless an explicit shared dependency exists. Optional failure degrades only the affected module; canonical source state survives downstream projection failure and can re-drive a failed target later.

**Requirement:** required. **Evidence:** `test_verified` across representative legacy mileage/appointment/travel optional-input boundaries; MIRA 2.0 cross-provider isolation unverified. **Dependencies:** explicit dependency declarations, `RECOVERY-001`, idempotent source/readback semantics.

## Category A consistency result

Category A is complete. Scheduling, context, Trip, Route, mileage, task and recovery authorities are explicitly separated. `TASK-002` remains below test-verified pending dedicated generic tests; no category-A feature is promoted to MIRA 2.0 integration/live status from legacy provider claims.

## Audited calendar/reminder features

### `CAL-001` — Saturday AM seven-day appointment lookahead

**Description:** The Saturday 02:45 canonical AM Ops Brief includes appointments from Saturday through Friday using a half-open seven-calendar-day window. Appointment visibility is slot-based and independent of HOME/ROAD mode. This mode-independent rule supersedes older ledger wording that described the weekly lookahead only as a ROAD behavior.

**Why it exists / user outcome:** Once a week the user gets enough appointment horizon to plan the coming week without turning every daily brief into a calendar dump.

**Requirement status:** `required`; later repaired policy generalizes the historical ROAD-only wording to mode-independent Saturday-AM behavior.

**Delivery/evidence:** `test_verified` for deterministic window calculation in legacy policy. **Live Calendar query coverage and MIRA 2.0 brief integration remain unverified.**

**Hard dependencies:** `OPS-001`; canonical/user timezone; Calendar/evidence adapter; `RECOVERY-002`.

**Legacy evidence:** feature-ledger category B row 1; appointment-window runtime/tests; `brief-run.md`.

**Acceptance / verification boundary:** Deterministic window tests plus MIRA 2.0 sandbox Calendar/evidence read showing exact Saturday-through-Friday inclusion/exclusion.

### `CAL-002` — Day-before and morning-of appointment reminders

**Description:** MIRA provides day-before and morning-of appointment coverage through deterministic reminder candidates and Ops Brief visibility. Cancelled/disabled appointments do not remind, overlapping triggers deduplicate, and late reminders are suppressed.

**Requirement:** required. **Evidence:** `test_verified`; Calendar projection/readback and user delivery unverified. **Dependencies:** appointment identity/evidence, timezone, activation, delivery adapter, `RECOVERY-002`.

### `CAL-003` — Configurable relative appointment reminder, default one hour before

**Description:** Appointment policy includes a configurable relative interval, default 60 minutes, with invalid-interval rejection, at/after-start suppression and trigger dedupe.

**Requirement:** required. **Evidence:** `test_verified`; provider projection/delivery unverified. **Dependencies:** appointment identity/start, `CAL-002`, timezone.

### `REMIND-001` — Evidence-gated medication reminders

**Description:** Medication reminders are default-off and may activate only from explicitly confirmed schedules supported by owner confirmation, prescription label, pharmacy, or clinician evidence. No inferred dose/timing, missed-dose advice, silent activation or assistant-inferred timing source is permitted.

**Requirement:** required safety boundary. **Evidence:** `test_verified` deterministic safety planner; MIRA 2.0 regimen authority/projection/delivery unverified. **Dependencies:** regimen authority/provenance, stable ID, timezone, activation, delivery adapter.

### `REMIND-002` — Explicit opt-in caregiver reminder sharing

**Description:** Reminder audience defaults to the user. Caregiver sharing is default-off and requires explicit activation plus a specific recipient identity; service activation alone never implies sharing permission.

**Requirement:** required safety boundary. **Evidence:** `test_verified` permission/recipient-required gate; real recipient resolution/authorization/provider delivery unverified. **Dependencies:** explicit consent, recipient identity resolution, source reminder, privacy-scoped delivery adapter.

## Audited appointment/mail communication-safety features

### `CAL-004` — Context-aware appointment visibility without fabricated confirmation state

**Description:** MIRA selects appointment visibility from deterministic brief-slot/calendar windows and current configured context rules without inventing or exposing a hidden “confirmed with user” state. Appointment presentation may include supported title, time and preparation evidence, but the system must not imply that the user has acknowledged, confirmed, accepted, or dismissed an appointment unless an authoritative source explicitly records that fact. Malformed/duplicate/unavailable appointment evidence is isolated rather than guessed into a valid event.

**Why it exists / user outcome:** The brief should show the right appointments without quietly manufacturing social state such as “confirmed” merely because the event exists or appeared in a prior brief.

**Requirement status:** `required`.

**Delivery/evidence:** deterministic appointment windows, filtering, duplicate/range isolation and mode-independent rendering are `test_verified`; the specific no-misleading-confirmation rule is `specified` in legacy policy rather than independently proven by a dedicated confirmation-state test. **MIRA 2.0 Calendar integration remains unverified.**

**Hard dependencies:** `CAL-001`/`CAL-002` appointment-window semantics; canonical appointment evidence; `RECOVERY-002` for malformed/unavailable Calendar isolation.

**Enables:** trustworthy appointment sections and future Calendar/reminder projections without hidden anti-nag state leaking into user-facing claims.

**Legacy evidence:** feature-ledger category B row 6; `brief-run.md` appointment rendering contract; `ops_policy.py` appointment filtering; `test_ops_policy.py` window and malformed/duplicate-event isolation.

**Acceptance / verification boundary:** Add/retain tests proving hidden acknowledgement/confirmation metadata cannot change the user-visible appointment claim unless that state is an explicit authoritative field; then verify a MIRA 2.0 sandbox Calendar read with malformed/unavailable evidence degrading only the appointment module.

---

### `MAIL-001` — Evidence-grounded important-mail triage

**Description:** MIRA performs a bounded important-mail pass for materially relevant school/education, employer/work, job/career, financial, medical, vendor/service, fraud and security messages. It reads materially relevant threads completely before conclusions, surfaces concise actionable changes, and avoids treating Promotions/sales noise as important by default. Email remains evidence, not the sole canonical record of downstream business facts.

**Why it exists / user outcome:** The user gets the few messages that actually matter without receiving an “AI summary” of the entire inbox or losing important context from half-read threads.

**Requirement status:** `required`.

**Delivery/evidence:** `specified`/skill-workflow. The legacy policy defines bounded searches, complete-thread reading and material categories, but this audit found no dedicated deterministic classifier test suite sufficient to promote general mail triage to `test_verified`. **MIRA 2.0 Gmail integration is unverified.**

**Hard dependencies:** connected mail/evidence adapter; bounded query policy; `RECOVERY-002` for mail-adapter failure isolation; canonical downstream authorities when a message changes orders, appointments, finance, etc.

**Enables:** Important Email brief section, archive-review queue, job-watch inputs and evidence-driven downstream reconciliation.

**Legacy evidence:** feature-ledger category B row 7; `brief-run.md` Gmail bounded-evidence pass; `email-reconciliation.md` complete-message/evidence rules and `Ops/Archive Approval` behavior; `SKILL.md` important-mail categories.

**Acceptance / verification boundary:** Before `test_verified`, add deterministic fixtures covering material/nonmaterial classification, thread completeness, duplicate/repeated evidence and unsupported ambiguity. Integration verification requires bounded reads against a synthetic/test mailbox or approved non-production fixture with no private mail committed to Git.

---

### `MAIL-002` — Explicit per-message approval for outbound contact

**Description:** MIRA may investigate an external-contact need, validate the recipient/channel, and draft the complete proposed message, but it must never send email or contact a vendor/employer/service automatically. Every send requires explicit approval for the exact current recipient/message/attachments. Before proposing contact, MIRA checks From/Reply-To/body/footer for unmonitored/no-reply instructions and uses an authoritative alternate support channel when needed. Any material change after approval requires fresh approval. The user-facing confirmation request is `Do you want me to send this email?`.

**Why it exists / user outcome:** MIRA can do the tedious research and drafting without becoming the sort of autonomous assistant that emails a vendor at 3 AM because it felt “confident.”

**Requirement status:** `required safety invariant`.

**Delivery/evidence:** `specified`/skill contract. The safety rule is explicit and repeated across legacy policy; this audit does not claim a complete test-verified send gate or MIRA 2.0 provider integration.

**Hard dependencies:** explicit user approval; validated recipient/channel; current issue evidence; outbound provider capability only after approval; audit/event recording after send.

**Enables:** safe vendor/employer/service contact proposals and later bounded outbound integrations.

**Legacy evidence:** feature-ledger category B row 8; `vendor-contact.md`; `email-reconciliation.md` contact-safety section; `SKILL.md` no-auto-email invariant.

**Acceptance / verification boundary:** Dedicated tests must prove no-send without approval, stale approval cannot authorize changed recipient/body/attachments, no-reply/unmonitored routes are rejected, and a permitted send uses exactly the approved payload. Integration verification requires provider readback after an explicitly approved synthetic/test send; no production send is part of this audit.

---

### `MAIL-003` — Explicit archive-approval queue with repeat-on-silence

**Description:** Important or decision-bearing mail remains in the inbox under the archive-review queue until the user explicitly approves archival. The brief groups the pending decisions compactly and ends the section with the exact prompt `Is it OK to archive these emails?`. Silence, failure to answer, or appearance in a previous brief is never approval; the unresolved queue repeats unchanged on later runs. Narrow separately-authorized retention/deletion policies do not override messages currently held for archive approval.

**Why it exists / user outcome:** MIRA can keep the inbox clean without silently hiding messages the user still needs to decide about.

**Requirement status:** `required`.

**Delivery/evidence:** `specified`/skill-workflow. The exact prompt and silence behavior are explicit in legacy run policy, but MIRA 2.0 Gmail label/archive mutation and readback are unverified.

**Hard dependencies:** `MAIL-001`; mail adapter with label/archive readback; explicit user approval identity/scope; `RECOVERY-002` for filing failure isolation.

**Enables:** safe inbox cleanup and durable archive decisions without auto-archiving important mail.

**Legacy evidence:** feature-ledger category B row 9; `brief-run.md` Important Email output contract; `email-reconciliation.md` important/unknown-mail section and Gmail filing order.

**Acceptance / verification boundary:** Tests must prove silence/repeated runs do not change archive state, approval is bounded to the displayed queue, and filing failure leaves messages pending. Integration verification requires synthetic/test-mail label/archive mutation plus provider readback.

---

### `CAREER-001` — Optional qualified job watch with realistic fit filtering

**Description:** MIRA can run an optional career/job-monitoring service that searches configured opportunity sources and evaluates candidate fit only against owner-approved canonical qualifications/settings. Mandatory requirements can reject a role; preferred qualifications alone cannot. Ambiguous postings become `Needs Review` rather than guessed. The service deduplicates by source/application/employer-title-location identity, reports only new realistic fits or specific review blockers, never applies/contacts anyone automatically, and normally runs as a phase of an existing MIRA control cycle rather than as a duplicate scheduler.

**Why it exists / user outcome:** The user sees realistic opportunities instead of a firehose of jobs whose title merely contains “IT,” while MIRA does not quietly rewrite the user's qualifications to make a posting look attractive.

**Requirement status:** `required personal service` for the legacy deployment; **optional per-user capability** in the general MIRA product.

**Delivery/evidence:** `specified`/skill workflow with explicit state/dedupe/fit rules. The audit found no dedicated executable fit-engine test suite sufficient to mark the general capability `test_verified`. **MIRA 2.0 mail/search/provider integration is unverified.**

**Hard dependencies:** explicit service activation; canonical candidate configuration/qualification authority; mail/search evidence adapter; stable Job Watch identity/state; `MAIL-002` for any later external contact; `RECOVERY-002` for module failure isolation.

**Enables:** compact PM career opportunities and review decisions without separate task/scheduler proliferation.

**Legacy evidence:** feature-ledger category B row 10; `qualified-job-watch.md`; `SKILL.md` consolidated-control-cycle routing.

**Acceptance / verification boundary:** Before `test_verified`, add deterministic fixtures for mandatory-vs-preferred requirements, seniority/role exclusions, experience ceilings, ambiguity, dedupe and no-contact behavior. Integration verification requires a synthetic/approved opportunity source plus canonical settings readback. The feature must remain disabled/unconfigured for users who do not opt in.

## Category B consistency result

Category B is fully audited through row 10.

- Appointment visibility (`CAL-*`) is distinct from reminder delivery/safety (`REMIND-*`).
- Mail triage (`MAIL-001`) does not itself authorize filing or contact.
- Outbound-contact permission (`MAIL-002`) is provider-independent and remains an explicit per-action gate even if Gmail is later replaced or supplemented.
- Archive approval (`MAIL-003`) treats silence as no permission and remains separate from narrow retention/deletion exceptions.
- Job watch (`CAREER-001`) is an optional personal service and cannot become a universal default merely because it existed in the legacy deployment.
- No category-B feature is promoted to MIRA 2.0 integration/live verification from legacy provider state.

## Audited fulfillment-lifecycle features

### `ORDER-001` — Evidence-grounded order and carrier correlation

**Description:** MIRA ingests order/fulfillment evidence from supported mail, carrier/vendor/account sources, retained evidence, and explicit owner correction/confirmation, normalizes the facts, and correlates them to existing purchase/fulfillment identity before changing state. Gmail is an evidence adapter, not an exclusive purchase-ingestion gate. Matching prefers exact tracking, then strong vendor/order identity, then order/item/package evidence, and only then a unique combination of weaker facts. More than one plausible match stays unresolved and causes no mutation. Evidence precedence is explicit owner correction first, carrier delivery next, carrier exception/progress next, then vendor fulfillment/status evidence; newer text does not automatically outrank stronger evidence.

**Why it exists / user outcome:** Shipment status should reflect what actually happened instead of whichever email arrived last, while missing or ambiguous email evidence must not make a known purchase disappear or cause MIRA to attach a tracking event to the wrong order.

**Requirement status:** `required`.

**Delivery/evidence:** normalized shipment matching, exact-tracking correlation, user/carrier/vendor precedence, split-package expansion and ambiguity-no-mutation behavior are `test_verified` in the legacy deterministic reconciler. External Gmail/provider collection and MIRA 2.0 canonical-state integration remain `specified`/unverified.

**Hard dependencies:** stable Receipt/Order/Shipment identity; bounded evidence adapters such as `MAIL-001`; canonical commerce history; active shipment projection; `RECOVERY-002` for provider/projection failure isolation.

**Enables:** trustworthy lifecycle transitions, deduplicated active fulfillment, delivery detection, cancellation/replacement correlation and downstream Gmail filing.

**Legacy evidence:** category-C row 1 in `docs/feature-ledger-2026-08-24.md`; `references/email-reconciliation.md`; `references/receipt-ingestion.md`; `scripts/reconcile_shipments.py`; `scripts/test_reconcile_shipments.py` exact tracking, precedence, split tracking and ambiguous-match fixtures; `SKILL.md` owner-evidence fallback and evidence-adapter boundary.

**Acceptance / verification boundary:** Deterministic fixtures must preserve matching order/precedence and refuse ambiguous mutation. MIRA 2.0 integration verification requires synthetic/test evidence to resolve one canonical order/fulfillment identity, provider/source readback where applicable, and proof that unavailable Gmail does not prevent owner-supported canonical purchase state.

**Compatibility notes:** A source message/thread ID is provenance, not the purchase identity itself. Later evidence enriches the same canonical transaction/fulfillment rather than creating chat-local duplicates.

---

### `ORDER-002` — Canonical ordered-to-delivered fulfillment lifecycle with active dedupe

**Description:** MIRA represents active fulfillment separately from durable purchase history. `Awaiting Shipment`, `Shipped`, and material `Exception` states may remain in the active shipment projection; `Delivered` is a terminal lifecycle event recorded durably in canonical commerce history and must leave the active projection after that event is verified. One active shipment identity exists per supported fulfillment/package/tracking identity; split packages can legitimately create multiple active rows for one merchant order. Duplicate Shipment IDs, duplicate active tracking numbers, malformed active schemas, and terminal `Delivered` rows in the active queue fail closed rather than becoming silently inconsistent state.

**Why it exists / user outcome:** The user sees only what is still in flight, can track split shipments correctly, and does not get a permanent cemetery of delivered packages masquerading as current work.

**Requirement status:** `required`.

**Delivery/evidence:** `test_verified` for ordered/shipped/progress/delivered active-state transitions, exact-tracking updates, split-package row creation, duplicate/schema validation, delivered-row removal and rejection of Delivered as an active status. Durable commerce-event/provider readback is not MIRA 2.0 integration-verified.

**Hard dependencies:** `ORDER-001`; canonical purchase/lifecycle event authority; active `Shipments` projection; stable Shipment IDs; source-first projection semantics from `RECOVERY-002`.

**Enables:** active shipment queries, compact Ops Brief fulfillment, delivery-once reporting and later return/replacement state.

**Legacy evidence:** category-C row 2; `reconcile_shipments.py` active status/identity/schema rules; `test_reconcile_shipments.py` delivery removal, split packages, progress updates and active-status validation; `email-reconciliation.md`; `brief-run.md` requires post-reconciliation Shipments readback and active-only rendering.

**Acceptance / verification boundary:** MIRA 2.0 must write/read back a synthetic canonical Ordered event, project Awaiting Shipment/Shipped state without duplicate identity, durably record Delivered, remove the active projection, and verify the target after each mutation. A projection failure after the canonical event must not roll back purchase history.

---

### `ORDER-003` — Explicit cancellation, return, refund and no-settlement lifecycle

**Description:** Cancellation, fulfillment and money movement are separate facts. A cancellation request remains nonterminal until supported confirmation. Confirmed full or partial cancellation updates fulfillment only from supported surviving-item/revised-total evidence; missing surviving detail remains actionable instead of guessed. A physical return does not erase spend. A refund becomes a separately evidenced financial correction/net effect. Cases such as `No Refund Required`, `Revised Before Settlement`, or cancellation before settlement resolve without fabricating a refund. Pending expected refund/reversal remains open until verified and may later become overdue under the financial-resolution policy.

**Why it exists / user outcome:** MIRA must distinguish “I asked them to cancel it,” “they cancelled it before charging me,” “I returned it,” and “the money actually came back.” Human commerce somehow requires all four states because apparently one word would have been too convenient.

**Requirement status:** `required`.

**Delivery/evidence:** full/partial cancellation projection behavior and cancellation-request exception state are `test_verified`; financial resolution states, resolved/no-settlement cases and five-business-day refund/reversal escalation are also `test_verified` in the dedicated financial-resolution engine. Return/net-spend accounting and full cross-authority lifecycle remain strongly `specified` but not end-to-end MIRA 2.0 verified.

**Hard dependencies:** `ORDER-001`/`ORDER-002`; canonical Receipt/Order Event identity; payment/financial evidence; source-first purchase authority; `RECOVERY-002` for independent shipment/financial projection failure.

**Enables:** accurate cancellation status, refund follow-up, return history, financial correction and later payment reconciliation.

**Legacy evidence:** category-C row 3; cancellation/refund sections of `receipt-ingestion.md`; `email-reconciliation.md`; `reconcile_shipments.py` cancellation states; `test_reconcile_shipments.py` cancellation fixtures; `financial_resolution.py`; `test_financial_resolution.py` revised-before-settlement, refunded, pending/overdue and business-day fixtures; `SKILL.md` invariant `Cancellation != refund`.

**Acceptance / verification boundary:** Deterministic tests must cover request-vs-confirmed cancellation, partial-survivor requirements, no-settlement, return-without-refund, refund evidence and overdue expected correction. Integration verification requires synthetic canonical event/readback across commerce history and any active shipment/payment projection without inventing financial state from fulfillment alone.

**Compatibility notes:** The five-business-day financial-correction timer here is not the separate stale-shipment/no-progress rule in `ORDER-005`.

---

### `ORDER-004` — Replacement and supersession without duplicate spend

**Description:** MIRA first distinguishes a revision of the same merchant transaction from a true replacement transaction. The same vendor/order number remains one Receipt ID and is revised in place through append-only lifecycle evidence. A true replacement with a distinct merchant order/transaction receives a distinct Receipt ID; original and replacement are linked reciprocally through `Replaced By` / `Replacement For` plus one shared Replacement Group ID. Original cancellation/refund state is reconciled independently and supported financial totals are never copied or transferred between orders merely to make the numbers balance. One underlying transaction total is counted once per Receipt ID, and the replacement does not create duplicate spend through shadow purchase rows, duplicate shopping history, or mutation of the old Receipt ID into the new one.

**Why it exists / user outcome:** When an order is cancelled and replaced, MIRA should preserve what actually happened without telling the user they bought the same thing twice, while still retaining both real merchant transactions when both truly existed.

**Requirement status:** `required`.

**Delivery/evidence:** shipment-level replacement linking, confirmed-vs-pending original cancellation, required replacement identity and same-order-revision routing are `test_verified` in the legacy reconciler. Reciprocal Receipt ID/group semantics and single-count financial allocation are strongly `specified` in purchase policy, but the complete replacement-plus-spend graph is not yet independently end-to-end test-verified in MIRA 2.0.

**Hard dependencies:** stable Receipt IDs and Order Events; `ORDER-003` original financial resolution; one-transaction/one-total receipt accounting; canonical shopping/asset projection rules when applicable; `RECOVERY-002`.

**Enables:** replacement order tracking, accurate spend, one fulfilled shopping intent, provenance-preserving order history and later asset/fitment linkage to the surviving purchase.

**Legacy evidence:** category-C row 4; `receipt-ingestion.md` replacement/supersession and one-transaction accounting rules; `reconcile_shipments.py`; `test_reconcile_shipments.py` confirmed replacement, pending original cancellation, required replacement fields and same-order revision fixtures; `SKILL.md` same-order vs true-replacement invariants.

**Acceptance / verification boundary:** Before the whole feature can be called `test_verified`, deterministic purchase-domain fixtures must prove same-order revision preserves one Receipt ID, true replacement produces two reciprocal linked IDs with one group ID, original/refund accounting stays independent, balanced allocations count each supported transaction once, and replay does not duplicate either transaction or shopping intent. Integration verification requires MIRA 2.0 sandbox readback of the complete graph.

---

### `ORDER-005` — Active-only fulfillment brief and stale-shipment escalation

**Description:** The Ops Brief renders only current active fulfillment after reconciliation and provider readback, normally as `Item — ETA <date>` or `Item — No ETA`, with status text only for a material exception. Durable delivery events observed since the previous successful run are reported once as `Delivered — <item>` and then disappear from later active output/history presentation. The required policy also calls for an `Action Required` escalation when an undelivered shipment has made no supported progress for five business days without a meaningful ETA/progress resolution.

**Why it exists / user outcome:** The brief stays short and current while still surfacing a shipment that has genuinely gone stale instead of making the user manually remember how many business days a motionless tracking number has been sitting there.

**Requirement status:** `required`.

**Delivery/evidence:** active-only shipment semantics, terminal Delivered exclusion and delivery-once output contract are `test_verified`/strongly specified through the reconciler and brief policy. **The dedicated five-business-day stale-shipment/no-progress escalation is currently only requirement/policy-level evidence in the audited tree: no dedicated executable rule/regression test was located in C1.** It must not be confused with the separately test-verified five-business-day financial-refund timer in `ORDER-003`.

**Hard dependencies:** `ORDER-002`; authoritative last-progress/ETA evidence; business-day calendar semantics; prior successful-run cutoff for delivery-once output; `RECOVERY-002`.

**Enables:** compact shipment brief output and actionable detection of genuinely stalled fulfillment.

**Legacy evidence:** category-C row 5 in `feature-ledger-2026-08-24.md`; `brief-run.md` active-only post-reconciliation rendering and delivery-once contract; shipment reconciler/tests proving Delivered cannot remain active. No separate stale-shipment five-business-day algorithm/test was found in the audited C1 sources.

**Acceptance / verification boundary:** Add deterministic fixtures for Monday-Friday business-day counting, exact stale threshold, ETA/progress reset behavior, weekends, resolved exceptions, and nonduplication of repeated alerts. MIRA 2.0 integration verification then requires synthetic active shipment readback where the same fulfillment crosses the threshold and produces one correct actionable state without becoming falsely Delivered or duplicated.

## Category C1 consistency findings

- `ORDER-001` evidence correlation is not canonical commerce storage; mail/provider evidence can fail while owner-supported purchase state remains valid.
- `ORDER-002` active Shipments is a projection, not purchase history; source-first canonical events survive projection failure.
- `ORDER-003` keeps fulfillment cancellation separate from financial settlement/refund state.
- `ORDER-004` keeps same-order revision separate from true replacement and preserves one-count financial truth.
- `ORDER-005` exposes a concrete verification gap: active-only rendering is supported, but stale-shipment five-business-day escalation needs its own executable/test work before implementation credit.
- PR #31 contains broad reconciliation/receipt-queue/control-cycle candidates but no narrower verified fulfillment behavior that supersedes these audited records.
- No category-C1 feature is promoted to MIRA 2.0 integration/live verification from legacy connected Google state.

## Audited receipt and financial-evidence features

### `RECEIPT-001` — Multi-source canonical receipt intake and evidence dedupe

**Description:** MIRA accepts purchase evidence from supported merchant email/forwarded mail, retained files, receipt photos/screenshots, authoritative account/vendor evidence when permitted, and explicit owner confirmation. The conversation or image is only an intake surface. Before creating a transaction, MIRA reconciles vendor/order/invoice/date/amount/item/payment-hint/message/attachment/image-hash/source identity against existing records so multiple evidence copies enrich one canonical Receipt ID instead of becoming duplicate purchases. Missing Gmail does not block a supported owner-confirmed purchase; unavailable fields remain blank and later evidence enriches the same Receipt ID. OCR/extraction is candidate evidence and cannot silently overwrite a verified identifier or transaction fact.

**Why it exists / user outcome:** A purchase should remain one purchase whether MIRA first learns about it from an email, a phone photo, a screenshot or the user saying what they bought. Humans already have enough duplicate receipts without the assistant manufacturing more.

**Requirement status:** `required`.

**Delivery/evidence:** normalized evidence/source-identity validation and idempotent evidence primitives are implemented/test-supported in the legacy evidence core; photo/manual/email ingestion and canonical dedupe rules are strongly `specified` in receipt policy. PR #31 contains an unmerged durable receipt-processing queue candidate keyed by one receipt/evidence identity, but it is reference evidence only and not MIRA 2.0 implementation. **MIRA 2.0 stock ChatGPT+Google receipt intake/provider readback remains unverified.**

**Hard dependencies:** stable Receipt ID; canonical purchase/evidence authority; provenance/source identity; file/Drive retention when an original is retained; `ORDER-001` when fulfillment evidence is involved; `RECOVERY-002` for downstream projection isolation.

**Enables:** searchable purchase history, order lifecycle, spending rollups, payment reconciliation, asset acquisition and later receipt capture on Android.

**Legacy evidence:** category-C row 6; `receipt-ingestion.md`; `receipt-photo-intake.md`; `receipt-classification-fitment.md`; evidence/source-identity validation in `asset_evidence.py` and its tests; PR #31 candidate `starter/service/receipt_processing.py` demonstrates same-receipt durable processing/readback but is unmerged and architecture-specific.

**Acceptance / verification boundary:** Deterministic fixtures must prove email/photo/manual variants of one transaction converge on one Receipt ID, source provenance survives enrichment, ambiguous identity queues instead of guessing, and OCR cannot overwrite verified facts. MIRA 2.0 integration verification requires synthetic multi-source intake into the sandbox authority plus provider readback, with no legacy production data used as fixtures.

---

### `RECEIPT-002` — Searchable expandable purchase history and connected receipt graph

**Description:** MIRA exposes durable purchase history by canonical Receipt ID with searchable line-item detail and links to connected evidence, assets, identifiers, manuals/specifications and explicit relationships where applicable. Querying the same underlying purchase from a receipt, connected asset or stable identifier should return the same connected graph rather than separate contradictory databases. Household ownership edges that would drag unrelated assets into a purchase query are excluded. User-facing expandable history is a projection over canonical state, not another ledger.

**Why it exists / user outcome:** The user can ask either “what did I buy?” or “what receipt/manual/part evidence belongs to this thing?” and reach the same reality instead of depending on which spreadsheet tab they remembered to search.

**Requirement status:** `required`.

**Delivery/evidence:** `test_verified` for the deterministic connected receipt/asset/identifier graph core. Legacy Google views existed, but **MIRA 2.0 user-facing Receipt Browser/Google readback is not integration/live verified.**

**Hard dependencies:** `RECEIPT-001`; stable Receipt/line/evidence/entity identities; canonical relationship graph; provider/UI projection for user-facing expandable views.

**Enables:** purchase lookup, asset provenance, warranty/manual navigation, support/refund evidence and future Android/web receipt browsing.

**Legacy evidence:** category-C row 7; `receipt-ingestion.md` canonical Receipt Browser/detail model; `asset_evidence.py` `query_graph`; `test_asset_evidence.py` proves receipt and vehicle queries return the same connected graph and identifier queries reach the same receipt/assets.

**Acceptance / verification boundary:** Keep deterministic graph tests, then MIRA 2.0 sandbox integration must write/read back a synthetic receipt with line/evidence/relationship data and prove receipt-, asset- and identifier-origin queries resolve the same canonical records. UI expansion/search is verified separately from the graph core.

---

### `SPEND-001` — Evidence-bounded monthly spending rollup

**Description:** MIRA can summarize a selected month from canonical receipt/email-detected purchase evidence with transaction dedupe, category totals, a monthly total and unresolved/ambiguous items. The output must explicitly state its evidence boundary and must not present itself as complete household/card/bank spending unless a separately verified complete financial authority exists. Confirmation, shipment, delivery, photo and later-enrichment copies of one purchase count once by Receipt ID. Ambiguous ownership/classification stays visible or queued rather than being silently included or excluded.

**Why it exists / user outcome:** The user gets a useful purchase-spending picture without a cheerful lie that an email-derived number equals every dollar that left every account.

**Requirement status:** `required`.

**Delivery/evidence:** `specified`/skill workflow in the audited legacy tree. The audit did not locate a dedicated deterministic monthly rollup test suite sufficient for `test_verified` status. Legacy live summary state does not become MIRA 2.0 verification.

**Hard dependencies:** `RECEIPT-001`; canonical one-count transaction totals/allocations; `RECEIPT-003` classification where category rollups are requested; explicit evidence-coverage metadata.

**Enables:** monthly category summaries and later comparison against complete connected financial data without conflating the two.

**Legacy evidence:** category-C row 8; monthly-rollup section of `receipt-ingestion.md`; line/allocation single-count rules in `receipt-classification-fitment.md`.

**Acceptance / verification boundary:** Add deterministic fixtures for duplicate evidence variants, mixed receipts, excluded/unresolved classifications, refunds/revisions and evidence-boundary labeling. MIRA 2.0 integration verification requires a synthetic month in the sandbox and a reproducible rollup whose total equals included canonical Receipt IDs exactly once.

---

### `RECEIPT-003` — Generic configurable receipt taxonomy and line classification

**Description:** Receipt classification is line-item based and supports generic categories/subcategories, search tags, cost owners, assets/projects and mixed/multi-category receipts without forcing an entire transaction into one label. The portable product may provide a sensible generic baseline such as Automotive, Bills & Utilities, Education, Electronics & Computer, Food & Dining, Health, House, Subscriptions & Services, Tools, Travel and General, but categories must remain configurable and must not hard-code this user's private assets, merchants or household as universal defaults. Ambiguous classification is queued after reasonable evidence work rather than guessed.

**Why it exists / user outcome:** One hardware-store receipt can contain house parts, tools and something for a vehicle without MIRA declaring the whole transaction “Automotive” because one bolt looked enthusiastic.

**Requirement status:** `accepted` / required by downstream spending and asset workflows.

**Delivery/evidence:** classification semantics are strongly `specified`; the old ledger classified the general taxonomy itself as `spec-only`. Existing evidence cores validate identities/relationships, but this audit found no generic configurable taxonomy/classifier implementation sufficient to promote the feature beyond specification.

**Hard dependencies:** `RECEIPT-001`; stable line identities; classification queue; balanced `Expense Ledger` allocation semantics.

**Enables:** `SPEND-001`, asset/fitment assignment, project/cost-owner reporting and user-defined organization.

**Legacy evidence:** category-C row 9; `receipt-ingestion.md` generic category baseline and ambiguity rules; `receipt-classification-fitment.md` independent line classification, Mixed/Multi-category summary and balanced allocations.

**Acceptance / verification boundary:** Implement a configuration-backed taxonomy plus deterministic tests for mixed receipts, unknown categories, user-added categories, correction without Receipt-ID mutation and queue-after-investigation behavior. Integration verification requires sandbox persistence/readback without any private deployment categories encoded in public source.

---

### `PAYMENT-001` — Expected merchant charge and settlement reconciliation

**Description:** MIRA tracks one canonical payment case per Receipt ID/current merchant financial outcome, separate from the purchase ledger itself. The latest supported same-order revision establishes expected settlement; account observations can remain Awaiting Settlement, Pending Match, Matched, Split Settlement, Overcharged, Undercharged, Pending Release, Settlement Contradiction, Refund/Reversal Expected, Resolved No Settlement or Ambiguous. Pending transactions are not final. Debit and credit direction are preserved. A no-settlement claim cannot hide a nonzero posted merchant net, and unmatched merchant charges are investigated rather than fabricated into receipts.

**Why it exists / user outcome:** The user can tell whether the merchant charged what the order actually says, whether a refund/reversal is really resolved, and whether a pending authorization is merely still doing whatever mysterious ritual payment networks perform for several days.

**Requirement status:** `accepted` and required for financially trustworthy receipt lifecycle.

**Delivery/evidence:** deterministic merchant-payment reconciliation is `test_verified` in the legacy executable for missing/pending/exact/split settlement, overcharge, no-settlement contradiction, debit-credit zero-net resolution, pending credits and fail-closed money/state/identity validation. **Connected bank/card provider matching and MIRA 2.0 payment authority readback remain unverified.**

**Hard dependencies:** `RECEIPT-001`; latest supported merchant expected amount; stable Payment Case/Receipt identity; financial-account adapter only when authorized/available; `ORDER-003` for cancellation/refund expectations; `RECOVERY-002`.

**Enables:** expected-charge validation, over/undercharge action, refund/reversal resolution and later complete finance comparison without duplicating purchase history.

**Legacy evidence:** category-C row 10 financial portion; `payment-reconciliation.md`; `payment_reconciliation.py`; `test_payment_reconciliation.py`; `financial_resolution.py`/tests for timed expected corrections; cancellation/financial rules in `receipt-classification-fitment.md`.

**Acceptance / verification boundary:** Preserve deterministic payment tests. MIRA 2.0 integration verification requires synthetic/approved account observations to bind to one sandbox payment case with provider readback and no duplicated financial transaction record. Full-bank coverage is a separate category-C3/provider capability and must not be inferred here.

---

### `REIMB-001` — Beneficiary allocation and household reimbursement reconciliation

**Description:** A merchant purchase remains one canonical Receipt ID and gross merchant total even when part or all of it benefits another person, another person's asset, a shared project, employer/client or other cost owner. Expense allocations identify the economic beneficiary/asset. A separate stable Reimbursement ID records money expected back and actually received with states such as Expected, Partially Received, Received, Waived or Disputed. Reimbursement is not a merchant refund, does not rewrite merchant lifecycle or gross spend, and is not wages/business revenue merely because money came in. Net household cost subtracts verified reimbursement exactly once from the supported beneficiary allocation.

**Why it exists / user outcome:** Buying a $600 mixed receipt with $400 for somebody else should remain a $600 merchant purchase with a $400 reimbursement, not mutate into a fictional $200 receipt or a vendor refund that never happened.

**Requirement status:** `accepted`.

**Delivery/evidence:** strongly `specified` in the legacy reimbursement/receipt contracts. The audit found no dedicated deterministic reimbursement engine/test suite sufficient for `implemented` or `test_verified` status. Provider/identity integration is also unverified in MIRA 2.0.

**Hard dependencies:** `RECEIPT-001`; stable beneficiary/asset identity; balanced expense allocations; explicit expected-reimbursement evidence; incoming-payment evidence when used; separation from `PAYMENT-001` merchant settlement/refund state.

**Enables:** gross-vs-net household cost, purchases for family/other people, reimbursement follow-up and accurate beneficiary reporting.

**Legacy evidence:** category-C row 10 reimbursement/beneficiary portion; `household-reimbursement.md`; receipt/allocation invariants in `receipt-ingestion.md` and `receipt-classification-fitment.md`.

**Acceptance / verification boundary:** Implement deterministic reimbursement state/allocation logic and tests for mixed receipts, partial receipt, waiver/dispute, merchant refund coexistence, duplicate inflow prevention and exact net-household-cost math. Integration verification requires synthetic beneficiary/reimbursement state plus approved incoming-payment evidence/readback.

## Category C2 consistency findings

- `RECEIPT-001` makes Receipt ID the transaction identity and lets multiple evidence forms enrich it; mail/photo/chat/file surfaces are not separate ledgers.
- `RECEIPT-002` has genuine deterministic graph-query evidence, but live user-facing Receipt Browser/provider readback remains a separate gate.
- `SPEND-001` is deliberately evidence-bounded and cannot masquerade as complete account spending.
- `RECEIPT-003` remains specification-level and needs a generic configurable implementation/test layer.
- `PAYMENT-001` merchant settlement is distinct from `REIMB-001` reimbursement. A merchant refund changes merchant financial outcome; a reimbursement changes household net cost while preserving gross purchase history.
- PR #31's receipt-processing queue is an unmerged architecture candidate and does not override the stock ChatGPT+Google MIRA 2.0 direction or provide implementation credit.
- No C2 feature is promoted to MIRA 2.0 integration/live verification from legacy Google/account state.

## Audit status

- Category A is complete through `M2-G0-002D`.
- Category B is complete through `M2-G0-003B`.
- `M2-G0-004A` audited category-C rows 1-5: `ORDER-001` through `ORDER-005`.
- `M2-G0-004B` audited category-C rows 6-10: `RECEIPT-001`, `RECEIPT-002`, `SPEND-001`, `RECEIPT-003`, `PAYMENT-001`, `REIMB-001`.
- The complete historical feature inventory is still in progress.
- The next bounded audit begins with category-C row 11: optional subscription/free-trial tracking, followed by complete financial-ingestion direction and category-C closure.
