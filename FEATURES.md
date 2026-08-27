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
- `RECOVERY-*` — run evidence, checkpoints, resumability and circuit breakers;
- `CAL-*` — calendar, appointments, reminders;
- `MAIL-*` — email triage, communication safety, evidence ingestion;
- `ORDER-*` — orders, shipments, replacements, returns, refunds;
- `RECEIPT-*` — receipts, purchases, evidence, payment reconciliation;
- `ASSET-*` — assets, fitment, specifications, manuals, maintenance;
- `INV-*` — inventory, hierarchical locations, movement, scanning, par levels;
- `PROFILE-*` — onboarding, roles, family, customization, accessibility;
- `PROVIDER-*` — Google/Microsoft/Apple/storage/runtime portability;
- `CLIENT-*` — ChatGPT, Android, web, desktop, CLI and device surfaces;
- `DIST-*` — distribution, updates, releases, rollback;
- `ENTERPRISE-*` — locked-down/institutional deployment;
- `DEV-*` — development governance and resumability.

## Evidence levels

Each feature distinguishes requirement status from delivery evidence:

1. `desired`
2. `specified`
3. `implemented`
4. `test_verified`
5. `integration_verified`
6. `live_verified`
7. `rejected_or_superseded` when applicable

Code existence does not imply completion. A feature may have test-verified deterministic logic while its provider integration or live firing remains unverified; that boundary must be stated explicitly.

## Required feature record

Each audited feature contains a stable ID, full user-facing description and outcome, requirement status, evidence level/boundary, dependencies, downstream enables, milestone, evidence paths, acceptance/verification boundary, and compatibility notes where relevant.

## Seed features established by MIRA 2.0 governance

### `DEV-001` — Git-authoritative development control plane
MIRA development uses Git as the authoritative source for ROADMAP, FEATURES, BACKLOG, CURRENT_WORK, packet policy, and durable engineering decisions. Human dashboards may mirror Git one-way but cannot become independent truth.

**Evidence:** specified and implemented in MIRA 2.0 repository governance files.

### `DEV-002` — Resumable bounded work packets
Development work is decomposed into bounded packets with explicit acceptance criteria, dependency/blocker tracking, durable checkpoints, and exact resume points. New customer ideas become backlog by default. Explicit reprioritization checkpoints displaced work before switching.

**Evidence:** specified and implemented in Project Instructions / roadmap / backlog / CURRENT_WORK policy.

### `DEV-003` — Dependency-ranked backlog
Engineering priority is dynamically recomputed from integrity/security blockers, hard prerequisites, architectural leverage, vertical value, and verification requirements rather than FIFO arrival order.

**Evidence:** specified and implemented in BACKLOG governance.

### `CORE-001` — MIRA product identity
**MIRA** is the primary product, assistant, and user-facing brand. MIRA expands to **Modular Intelligence & Reasoning Assistant**.

**Evidence:** specified in repository README, Project Instructions, and branding spec.

### `MIRROR-001` — Companion reality database
MIRROR is MIRA's companion reality database: durable structured facts, evidence, entities, state, provenance, and relationships that MIRA reasons over. MIRROR is a supporting technical component rather than a co-equal primary user-facing brand.

**Evidence:** specified in repository README, Project Instructions, and branding spec.

### `DATA-001` — Legacy production preservation
Existing legacy MIRA Google spreadsheets, Drive artifacts, briefs, schedules, automations, and other live user state are protected production data. MIRA 2.0 development must use separate sandbox state and may not silently overwrite or migrate legacy production artifacts.

**Evidence:** specified in Project Instructions and roadmap.

### `ONBOARD-001` — Full-replacement instruction delivery
Whenever a user must install or change ChatGPT Project Instructions, global Custom Instructions, or another instruction block, MIRA supplies the entire replacement block and simple nontechnical UI steps. Fragment-only instruction patches are prohibited by default.

**Evidence:** specified in Project Instructions; executable onboarding implementation is pending audit/design.

### `BRAND-001` — Canonical MIRA brand asset system
MIRA uses canonical vector source assets for symbol, wordmark, square lockup, wide hero/banner, thin header banner, Android adaptive foreground, and monochrome utility mark. Platform-specific icons are generated deterministically from masters.

**Evidence:** specified in `docs/BRAND_ASSET_SPEC.md`; final artwork and UI integration pending.

## Audited operational features

### `OPS-001` — Canonical twice-daily Ops Brief schedule

**Description:** MIRA's canonical Ops Brief schedule produces exactly two scheduled brief opportunities per calendar day at **02:45** and **14:45** in the named IANA timezone `America/New_York`. Travel location, device timezone, session timezone, and fixed UTC offsets must not reinterpret those wall-clock times. Manual brief invocation is a separate on-demand path and does not count as an extra scheduled brief.

**Why it exists / user outcome:** Predictable briefs tied to the operating schedule rather than whatever timezone a device, cloud worker, or model happens to infer.

**Requirement status:** `required`.

**Delivery/evidence:** `test_verified` for repository policy/runtime slot semantics; **live scheduler configuration and actual 02:45/14:45 firing are not yet MIRA 2.0 live-verified**.

**Hard dependencies:** named-timezone scheduler/provider readback; `OPS-003`; `OPS-004`.

**Enables:** appointment-slot semantics, scheduled brief delivery, Run Log proof, recurring operational reconciliation.

**Legacy evidence:** `skill/ops-brief-policy/scripts/ops_policy.py`; `references/brief-run.md`; `SKILL.md`; legacy feature-ledger category A row 1; PR #31 candidate `MIRA-F009`.

**Acceptance / verification boundary:** Scheduler readback must prove recurrence/TZID and observed AM/PM firings must produce canonical run evidence in the correct slots.

**Compatibility notes:** Future user-configurable timezones still use named-IANA semantics, never fixed UTC math.

---

### `OPS-002` — Single canonical dispatcher and prohibited duplicate schedules

**Description:** Scheduled Ops work uses one canonical dispatcher/control-cycle rather than parallel legacy, retry, child, diagnostic, UTC-shifted, 3:00, noon/midnight, or device-local duplicate schedules. Compatible scheduled work should be consolidated when safe.

**Why it exists / user outcome:** Prevent duplicate briefs, contradictory mutations, stale output and wasted scheduler slots.

**Requirement status:** `required`; supersedes historical duplicate/shifted schedule states.

**Delivery/evidence:** `specified`; **provider-wide duplicate enumeration remains unverified in MIRA 2.0**.

**Hard dependencies:** `OPS-001`; provider task enumeration/readback; stable dispatcher identity.

**Enables:** deduplicated scheduled behavior and reliable scheduler incident diagnosis.

**Legacy evidence:** feature-ledger category A row 2; `SKILL.md`; PR #31 `MIRA-F009`; PR #31 `starter/scheduler-planner-contract.json`.

**Acceptance / verification boundary:** Provider enumeration/readback must prove exactly one canonical enabled dispatcher and absence/disablement of prohibited variants.

---

### `OPS-003` — Canonical runtime clock gate with DST-safe slot matching

**Description:** Scheduled MIRA entry uses the executable runtime's own offset-aware system clock, converts it through the deployment's IANA timezone, handles DST transitions, records dispatch delay, and accepts only the intended logical slot within bounded grace. Model, prompt, device, travel, session, or naive timestamps are not production clock authority.

**Why it exists / user outcome:** Scheduled execution needs evidence of when it actually ran, not an Eastern-looking timestamp produced by wishful thinking.

**Requirement status:** `required by failure evidence`.

**Delivery/evidence:** `test_verified`; MIRA 2.0 live scheduler entry remains integration/live-unverified.

**Hard dependencies:** runtime clock; IANA timezone database; `OPS-001`.

**Enables:** scheduler-integrity circuit breaking, correct slot derivation and trustworthy Run Log timestamps.

**Legacy evidence:** `ops_policy.py` canonical/live slot functions; `test_ops_policy_entry.py`; `brief-run.md`; feature-ledger row 3.

**Acceptance / verification boundary:** Repository DST/offset/grace tests plus an actual scheduler run through the runtime-clock path.

---

### `OPS-004` — Fresh standalone run delivery with deterministic Run ID

**Description:** Every scheduled brief starts as a fresh run from the saved dispatcher. Scheduled identity is `OPS-YYYY-MM-DD-AM|PM`; delivered output begins with that identity and the same ID is used for idempotent Run Log updates.

**Why it exists / user outcome:** Distinguish current output from stale chat output and distinguish “scheduler never entered” from downstream failure.

**Requirement status:** `required by stale-response incident`.

**Delivery/evidence:** `test_verified` for deterministic ID generation; fresh provider standalone delivery and live Run Log evidence are unverified in MIRA 2.0.

**Hard dependencies:** `OPS-003`; `RECOVERY-001`; scheduler/provider fresh-run invocation.

**Enables:** idempotent logging, scheduler diagnosis, self-identifying notifications.

**Legacy evidence:** `ops_policy.py`; `test_ops_policy.py`; `brief-run.md`; `SKILL.md`; feature-ledger row 4.

**Acceptance / verification boundary:** A real scheduled provider run must start fresh, create/update the matching Run Log record and deliver output beginning with the expected Run ID.

---

### `OPS-005` — Deterministic HOME/ROAD context with explicit overrides

**Description:** MIRA resolves base HOME/ROAD state from canonical weekly transitions and explicit override records, with inclusive starts, exclusive expiries, stable identity, conflict detection and deterministic precedence. Generic context labels and active-trip forcing are separate capabilities.

**Why it exists / user outcome:** Mode-sensitive work must use canonical state instead of conversational guesses.

**Requirement status:** `required`.

**Delivery/evidence:** `test_verified` for legacy deterministic policy logic; MIRA 2.0 canonical-state integration is unverified.

**Hard dependencies:** canonical settings/state; override records; timezone-aware parsing.

**Enables:** mode-specific tasks and weather/travel behavior.

**Legacy evidence:** `ops_policy.py`; `test_ops_policy.py`; `test_ops_policy_entry.py`; `SKILL.md`; feature-ledger row 5.

**Acceptance / verification boundary:** Deterministic tests plus MIRA 2.0 sandbox state read/write/readback of transitions and overrides.

---

### `CTX-001` — Configurable operating-context pairs

**Description:** MIRA may use a two-label operating-context model when environment materially changes tasks, equipment, evidence, connectivity, notifications, routes, weather, or routines. Patterns include `HOME / ROAD`, `HOME / TRUCK`, `HOME / FIELD`, `HOME / CAMPUS`, `HOME / AWAY`, and user-defined labels. `HOME / OFFICE` is valid through explicit/custom labels even though the audited legacy heuristic has no dedicated OFFICE recommendation rule. Context is mutable state, not identity or scheduling timezone.

**Why it exists / user outcome:** Different users get useful operating boundaries without inheriting somebody else's hard-coded HOME/ROAD model.

**Requirement status:** `accepted direction`.

**Delivery/evidence:** `test_verified` in the legacy onboarding/context-router candidate; MIRA 2.0 state integration is unverified.

**Hard dependencies:** mutable profile/context authority; explicit selection state; contract-driven downstream consumers.

**Enables:** reusable context-specific behavior across work, family, school and other profiles.

**Legacy evidence:** feature-ledger row 6; `starter/PROFILE_AND_CONTEXT_MODES.md`; `starter/tools/onboarding_profile_router.py`; `starter/tests/test_onboarding_profile_router.py`.

**Acceptance / verification boundary:** Store/read back selected labels in MIRA 2.0 sandbox and prove a downstream module consumes them without changing canonical timezone.

---

### `CTX-002` — Evidence-gated context recommendation and explicit activation

**Description:** Job title/duties may inform context recommendations but never silently enable a context split. Explicit no bypasses it, explicit yes permits a still-confirmable recommendation, unresolved evidence remains unresolved/needs-confirmation, and explicit user labels outrank recommendations.

**Why it exists / user outcome:** Helpful onboarding without MIRA inventing a user's lifestyle from a job title.

**Requirement status:** `required`.

**Delivery/evidence:** `test_verified` in the legacy candidate router; MIRA 2.0 onboarding/readback remain unverified.

**Hard dependencies:** profile/job/duties intake; `CTX-001`; activation/confirmation state.

**Enables:** safe low-friction onboarding.

**Legacy evidence:** feature-ledger row 7; profile/context contract; onboarding router and tests including the Broadway false-match regression.

**Acceptance / verification boundary:** MIRA 2.0 onboarding must prove recommendation cannot become active canonical context without explicit confirmation/readback.

---

### `TRIP-001` — Independent trip occurrence lifecycle

**Description:** MIRA tracks each trip occurrence separately from reusable route knowledge, operating context and paid-mileage accounting. Trips have stable identity and Planned/Active/Arrived/Cancelled lifecycle states. Active trip state may affect context precedence, but context changes and route learning do not manufacture Trip or Mileage occurrences.

**Why it exists / user outcome:** Related travel facts stay linked without collapsing route knowledge, current travel, and payroll into one mutable blob.

**Requirement status:** `required`.

**Delivery/evidence:** `test_verified` for core legacy separation/precedence; MIRA 2.0 persistence/readback unverified.

**Hard dependencies:** canonical trip authority; stable IDs; context precedence contract.

**Enables:** route/weather watches, ETA/location, multi-leg work cycles and mileage linkage.

**Legacy evidence:** feature-ledger row 8; `state-maintenance.md`; `route-weather.md`; `test_ops_policy_entry.py`.

**Acceptance / verification boundary:** MIRA 2.0 sandbox Trip lifecycle must round-trip independently of context and mileage.

---

### `ROUTE-001` — Learned routes, directional runtime, location and ETA inference

**Description:** MIRA keeps reusable route knowledge separate from trip occurrences. Endpoint-pair routes support directional overviews/runtime; stored runtime can derive ETA when no stronger explicit ETA exists; user-reported location/time is preserved; bounded time-progress may support corridor reasoning. Explicit corrections outrank older learned values. Multi-leg work remains separate trip occurrences.

**Why it exists / user outcome:** Recurrent travel can be learned without replacing real operating history with naive map-distance math.

**Requirement status:** `required`.

**Delivery/evidence:** `test_verified` for route-average ETA and related primitives; human-facing ahead/behind interpretation and MIRA 2.0 authority integration are not independently verified.

**Hard dependencies:** `TRIP-001`; stable route IDs/endpoint normalization; supported departure/location evidence.

**Enables:** ETA/status, route-weather scoping, runtime learning and later paid-mile association.

**Legacy evidence:** feature-ledger row 9; `route-weather.md`; `state-maintenance.md`; `ops_policy.py`; `test_ops_policy.py`.

**Acceptance / verification boundary:** Unit coverage for route direction/ETA/location/progress and MIRA 2.0 Route+Trip read/write/readback. Ahead/behind remains labeled inference until supported by observed evidence.

---

### `WEATHER-001` — Context-gated HOME and ROAD weather intelligence

**Description:** HOME context permits home-location weather when useful; ROAD context can activate bounded route/corridor weather and official road-condition checks tied to Trip/watch state. Watches expire deterministically. Forecasts, observed restrictions and estimated corridor position remain distinguishable.

**Why it exists / user outcome:** Relevant weather rather than a generic forecast sprayed into every brief.

**Requirement status:** `required`.

**Delivery/evidence:** `test_verified` for deterministic gates/watch expiry; external NWS/DOT/511 workflow is `specified`, not MIRA 2.0 integration/live verified.

**Hard dependencies:** context; `TRIP-001`; `ROUTE-001`; authoritative external sources for hazard claims.

**Enables:** home-weather decisions and route hazard warnings.

**Legacy evidence:** feature-ledger row 10; `ops_policy.py`; `test_ops_policy.py`; `route-weather.md`; `brief-run.md`.

**Acceptance / verification boundary:** Deterministic gate tests plus MIRA 2.0 sandbox state and source-grounded external evidence. Weather-provider failure must not corrupt unrelated modules.

---

### `MILE-001` — Company-paid mileage and deterministic gross-pay reporting

**Description:** MIRA records and reports **company-paid miles**, not map distance or odometer distance, and computes estimated gross pay from the verified rate attached to or applicable to those mileage records. The canonical reporting behavior produces the closed work-cycle mileage/pay summary on both Thursday Ops Brief slots, validates mileage/rate inputs, distinguishes Final/Estimated/Voided state, preserves corrections, and surfaces missing required paid-mile evidence rather than fabricating a number.

**Why it exists / user outcome:** The user needs a useful weekly pay estimate based on what the employer actually pays, not an attractive but financially meaningless route-distance calculation.

**Requirement status:** `required`.

**Delivery/evidence:** `test_verified` in the legacy deterministic runtime for Thursday totals, gross calculation, pay-week boundaries, status splits, zero/empty weeks, missing-entry actions and section-scoped tracker failure. **MIRA 2.0 canonical mileage persistence and live Thursday delivery remain unverified.**

**Hard dependencies:** `TRIP-001` for occurrence linkage when trip tracking is enabled; `MILE-002` authoritative tracker/settings; verified rate and company-paid-mile evidence; Thursday/brief slot semantics from `OPS-001`.

**Enables:** weekly mileage/pay reporting, work-cycle closeout, later payroll reconciliation and trend history.

**Legacy evidence:**
- feature-ledger category A row 11;
- `policy/ops-brief-policy.yaml` declares verified-live rate source, Thursday summary, confirmed-HOME accrual close and failure isolation;
- `skill/ops-brief-policy/scripts/ops_policy.py` implements mileage parsing/validation, pay-week selection and deterministic summary/gross calculation;
- `skill/ops-brief-policy/scripts/test_ops_policy.py` verifies Thursday paid-mile/gross totals, non-Thursday suppression, status splits, missing-mile actions, explicit zero weeks and degraded tracker behavior;
- `skill/ops-brief-policy/scripts/test_ops_policy_entry.py` verifies Thursday mileage summary remains due even in HOME context.

**Acceptance / verification boundary:** MIRA 2.0 must round-trip synthetic mileage/settings state through its sandbox, reproduce deterministic totals from supported inputs, reject/flag invalid evidence, and demonstrate both Thursday slots consume the same closed work-cycle authority. A live employer/settlement import, if later added, is a separate provider-evidence boundary.

**Compatibility notes:** The historical per-mile rate is mutable deployment data and must never be hard-coded into public source. Each historical mileage record should retain the applicable rate so future rate changes do not rewrite past estimates.

---

### `MILE-002` — Separate authoritative Miles & Pay tracker

**Description:** Mileage/pay state lives in a dedicated canonical tracker/authority rather than being inferred from route geometry, buried in chat history, or duplicated in Git. The tracker preserves stable mileage occurrence identity, work-cycle/pay-week history, paid miles, applicable rate, gross estimate, source/status and corrections. Other MIRA modules read it through an authority contract and treat its failure as a scoped dependency rather than silently creating shadow data.

**Why it exists / user outcome:** Pay history needs to remain queryable and correct over time even when routes, chat sessions, brief rendering or software versions change.

**Requirement status:** `required`.

**Delivery/evidence:** legacy deployment evidence records a **live external authority**, and repository policy/contracts are `specified`/implemented around it. **MIRA 2.0 has not created or read back its own sandbox Miles & Pay authority, so it is not MIRA 2.0 live-verified.**

**Hard dependencies:** MIRROR structured-state/authority contract; stable mileage IDs; provenance; `MILE-001` for deterministic reporting semantics.

**Enables:** historical pay queries, weekly summaries, correction/void preservation and eventual provider migration without rewriting business semantics.

**Legacy evidence:** feature-ledger category A row 12; `state-maintenance.md` mileage rules; `brief-run.md` exact Mileage & Pay Tracker ranges and scoped failure behavior; `policy/ops-brief-policy.yaml` resolves the authority through private deployment state.

**Acceptance / verification boundary:** MIRA 2.0 must provision a separate synthetic tracker through the selected MIRROR adapter, write/read back a mileage occurrence and settings, preserve immutable identity/corrections, and prove reporting consumes that authority. Legacy production rows are migration evidence only and are never copied into Git.

**Compatibility notes:** The logical authority is the feature. Google Sheets may be the initial adapter; a later database adapter must preserve the same IDs, semantics and provenance rather than becoming a second source of truth.

---

### `TASK-001` — Structured task hierarchy and one-action-per-item rendering

**Description:** Canonical tasks carry stable identity and a structured hierarchy of priority tier → classification → optional subsystem → individual task. Normal priority tiers are High, Medium and Low, with Persistent available for explicitly always-visible items. Each task remains an independent canonical record and renders as its own bullet rather than combining unrelated actions into prose. Context/visibility and active/scheduled windows determine whether a task is currently actionable without changing its identity.

**Why it exists / user outcome:** The brief should be scannable and queryable. A task database becomes useless surprisingly quickly when five unrelated chores are stuffed into one cell because a language model felt literary.

**Requirement status:** `required`.

**Delivery/evidence:** `test_verified` for the legacy task schema, validation, context visibility and deterministic tier/classification/subsystem grouping. **MIRA 2.0 task-state persistence/readback remains unverified.**

**Hard dependencies:** canonical task authority; stable Task IDs; context contract when visibility is used.

**Enables:** compact Ops Brief task rendering, filtering/search, next-action selection, project/routine decomposition and later Android task mutation.

**Legacy evidence:** feature-ledger category A row 13; `ops_policy.py` `TASK_KEYS`, task validation, `_group_rows`, `_render_grouped` and `task_output`; `test_ops_policy.py` verifies mode visibility, Persistent behavior and task eligibility; `state-maintenance.md` requires task changes to update canonical state rather than chat memory.

**Acceptance / verification boundary:** MIRA 2.0 must round-trip independent synthetic Task records, preserve IDs and hierarchy, render each actionable task separately, and reject materially malformed records rather than guessing required classification.

**Compatibility notes:** Classification/subsystem vocabulary should remain user/configuration driven. Priority is not permission to infer completion or urgency.

---

### `TASK-002` — Evidence-grounded next actions and honest completion state

**Description:** MIRA can turn goals, projects, routines and task queues into the smallest useful next action by reading canonical open state, deadlines, prerequisites, blocks, context and available time. It must distinguish planned, partial, completed, missed, removed and blocked work from actual evidence. Silence, lack of reminders, or conversational optimism never counts as completion. When evidence is partial, state remains partial rather than being promoted to Done.

**Why it exists / user outcome:** MIRA should help decide what to do next without lying about what has already been done. A planner that quietly completes work because nobody complained is just an extremely confident fiction generator.

**Requirement status:** `accepted` and repeatedly reinforced as an integrity rule.

**Delivery/evidence:** `specified`/skill-workflow behavior. The legacy life-planning contract defines deterministic ranking and completion-evidence rules, but there is not enough audited evidence in this slice to claim a fully test-verified general next-action engine across all domains.

**Hard dependencies:** `TASK-001`; canonical goal/task/routine/project state; verified deadlines/prerequisites where used; context state when actionability depends on environment.

**Enables:** coaching, study planning, routine accountability, project next steps and honest brief status.

**Legacy evidence:** feature-ledger category A row 14; `references/life-planning-accountability.md` defines next-action ordering, partial/miss handling, anti-nag rules and the prohibition on inferred completion; `state-maintenance.md` requires Done/Removed to be explicit canonical state and prohibits inferring completion from silence.

**Acceptance / verification boundary:** Before promotion to `test_verified`, MIRA 2.0 needs deterministic tests showing blocked/context-incompatible/completed items are excluded correctly, smallest supported next actions are selected, partial evidence stays partial, and silence cannot transition state to Done. Integration verification then requires canonical state mutation/readback from explicit completion evidence.

**Compatibility notes:** This is a generic planning capability, not permission for MIRA to invent deadlines, health constraints, academic proof, or hidden priority models.

---

### `RECOVERY-001` — Phase-aware Run Log, durable checkpoints and circuit-breaker recovery

**Description:** MIRA records durable execution/recovery evidence so interrupted or failed work can resume from known-good state instead of from assistant memory. For scheduled control cycles, a deterministic Run ID owns one Run Log record that moves through phase/status evidence such as Running, policy-resolved, Degraded, OK or Error and preserves timestamps, input/module health and stable mutation evidence. Repeated identical failures, no-forward-progress loops, permission/dependency failures, ambiguous partial writes, integrity failures, scheduler misses and unchanged CI loops trip a bounded circuit breaker. The affected module stops writes, verified state is preserved/read back, unrelated healthy work may continue, and recovery gets one specific next action.

**Why it exists / user outcome:** A failed workflow should leave a precise recovery point, not twenty minutes of vanished progress followed by another heroic attempt to remember what happened.

**Requirement status:** `required by repeated stalls and integrity incidents`.

**Delivery/evidence:** `test_verified` for core Run ID/Run Log field generation and selected degraded/error paths; the Module Circuit Breaker transaction and recovery contract are strongly `specified`. Historical claims of installed private-deployment artifacts are **not** treated as MIRA 2.0 live evidence. The next actual scheduled MIRA 2.0 Run Log entry remains unverified.

**Hard dependencies:** stable run/work IDs; canonical mutable Run Log/recovery authority; `OPS-003` clock evidence for scheduled runs; idempotent provider readback for affected modules.

**Enables:** resumable scheduled work, failure diagnosis, safe bounded retries, partial-write reconciliation, scheduler proof, and the same engineering philosophy used by MIRA 2.0 `CURRENT_WORK` packets.

**Legacy evidence:**
- feature-ledger category A row 15;
- `ops_policy.py` emits deterministic `run_log_fields` including Run ID, timestamps, phase/status, canonical clock and module/input health;
- `test_ops_policy.py`/`test_ops_policy_entry.py` verify Run Log identity/status and degraded module outcomes;
- `brief-run.md` requires the same Run ID row to be written `Running` before downstream mutations and finalized rather than duplicated;
- `references/module-circuit-breaker-report.md` defines trip conditions, retry budget, state-preservation transaction, scheduler/CI boundaries and exact recovery behavior;
- `state-maintenance.md` requires canonical-state recovery and prohibits shadow state/chat reconstruction.

**Acceptance / verification boundary:** Repository tests must verify deterministic same-run identity, phase/status transitions and fail/degrade boundaries. Integration verification requires MIRA 2.0 sandbox Run Log write/readback before and after a bounded workflow. Live scheduler verification requires an actual scheduled entry to create the expected Run Log row in the canonical slot. A circuit-breaker incident is cleared only after changed underlying conditions plus verified recovery readback.

**Compatibility notes:** `RECOVERY-001` is user/workflow recovery, while `DEV-002` governs software-development packet recovery. They intentionally use the same principles but are distinct authorities and evidence domains.

## Audit status

- `M2-G0-002A` audited legacy category-A behaviors 1-5: `OPS-001` through `OPS-005`.
- `M2-G0-002B` audited category-A behaviors 6-10: `CTX-001`, `CTX-002`, `TRIP-001`, `ROUTE-001`, `WEATHER-001`.
- `M2-G0-002C` audited category-A behaviors 11-15: `MILE-001`, `MILE-002`, `TASK-001`, `TASK-002`, `RECOVERY-001`.
- The complete historical feature inventory is **not yet imported**. Do not infer absence from this file.
- The next bounded audit begins with category-A behavior 16: optional-module failure isolation, followed by final Slice-A dependency/evidence consistency reconciliation.
