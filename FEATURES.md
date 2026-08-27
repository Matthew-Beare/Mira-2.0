# MIRA 2.0 FEATURES

This file is the human-readable canonical feature registry. It is populated and normalized through bounded forensic audit packets. Machine-readable dependency metadata may be added after stable IDs are assigned.

## Feature identity rule

Every durable feature receives a stable semantic ID. IDs do not change merely because roadmap priority or table position changes.

ID families include:

- `CORE-*` — MIRA control plane, canonical state, identity, reconciliation, provenance;
- `MIRROR-*` — companion reality database/state/evidence contracts;
- `OPS-*` — briefs, operational state, trips, routes, tasks, run logs;
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

Each audited feature contains:

- stable feature ID;
- name;
- full user-facing description;
- why it exists / user outcome;
- current requirement status;
- delivery/evidence level and boundary;
- hard dependencies;
- downstream capabilities enabled;
- milestone association;
- known implementation/evidence paths;
- acceptance criteria / verification boundary;
- migration/compatibility notes when relevant;
- superseded/rejected relationship if applicable.

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

**Why it exists / user outcome:** The user needs predictable briefs tied to the operating schedule rather than whatever timezone a device, truck, cloud worker, or model happens to think is fashionable that day.

**Requirement status:** `required`.

**Delivery/evidence:** `test_verified` for repository policy/runtime slot semantics; **live scheduler configuration and actual 02:45/14:45 firing are not yet MIRA 2.0 live-verified**.

**Hard dependencies:** a scheduler/provider capable of named-timezone recurrence and readback; `OPS-003` canonical clock gate for runtime integrity; `OPS-004` for fresh identifiable run delivery.

**Enables:** appointment-slot semantics, scheduled Ops Brief delivery, scheduled run-log proof, recurring operational reconciliation phases.

**Milestone:** foundation for the future Ops Brief vertical slice.

**Legacy evidence:**
- `skill/ops-brief-policy/scripts/ops_policy.py` defines `TZ_NAME = "America/New_York"` and canonical brief slots `((2,45),(14,45))`;
- `skill/ops-brief-policy/references/brief-run.md` defines scheduled New York clock semantics;
- `skill/ops-brief-policy/SKILL.md` requires one standalone control cycle at 2:45 AM/PM Eastern;
- legacy `docs/feature-ledger-2026-08-24.md`, category A row 1;
- PR #31 `project/FEATURES.yaml` candidate `MIRA-F009` independently restates `02:45`, `14:45`, `America/New_York`, exact count two.

**Acceptance / verification boundary:** MIRA 2.0 may call the schedule behavior complete only after scheduler readback proves the intended recurrence/TZID and at least one observed AM and PM firing produce canonical run evidence in the correct slot. Unit tests alone do not prove scheduler firing.

**Compatibility notes:** For a future general-user product, cadence/timezone may become user-configurable through audited profile settings. This record preserves the current user's required deployment behavior and the rule that named-timezone semantics, not fixed UTC math, are authoritative.

---

### `OPS-002` — Single canonical dispatcher and prohibited duplicate schedules

**Description:** Scheduled Ops work must use one canonical dispatcher/control-cycle definition rather than parallel legacy, retry, child, diagnostic, UTC-shifted, 3:00, noon/midnight, or device-local duplicate schedules. Scheduled diagnostic or cleanup work should be consolidated into an existing compatible MIRA cycle when safe instead of consuming independent task slots merely because a feature exists.

**Why it exists / user outcome:** Duplicate automations create duplicate briefs, stale output, contradictory mutations, wasted task slots, and debugging sessions where everyone insists the clock is correct while three different clocks are firing.

**Requirement status:** `required`; supersedes historical duplicate/shifted schedule states.

**Delivery/evidence:** `specified`. Repository policy strongly specifies uniqueness/prohibited variants, and historical evidence says old paused jobs existed, but **current provider-wide duplicate enumeration is not verified in MIRA 2.0**.

**Hard dependencies:** `OPS-001`; provider capability to enumerate/read back scheduled tasks; stable dispatcher identity.

**Enables:** deduplicated scheduled behavior, reliable incident diagnosis, future cleanup/reconciliation consolidation.

**Milestone:** scheduler/control-plane foundation.

**Legacy evidence:**
- legacy feature ledger category A row 2;
- `skill/ops-brief-policy/SKILL.md` prohibits separate active Ops/lifecycle/job-watch, retry, child, 3:00, UTC, Pacific and duplicate jobs;
- PR #31 `project/FEATURES.yaml` `MIRA-F009` repeats forbidden schedule variants;
- PR #31 `starter/scheduler-planner-contract.json` prohibits feature-specific scheduled tasks by default and prefers attaching compatible cleanup work to existing MIRA cycles.

**Acceptance / verification boundary:** Enumerate the provider scheduler, prove exactly one canonical enabled Ops dispatcher for the configured cycle, prove prohibited variants are absent/disabled, and read back the canonical task definition. This remains unverified until provider state is inspected.

**Compatibility notes:** This does **not** prohibit every future MIRA scheduled task. It prohibits unnecessary duplicate schedules for compatible work. A separate schedule may exist only when a bounded feature proves consolidation would be unsafe or impossible.

---

### `OPS-003` — Canonical runtime clock gate with DST-safe slot matching

**Description:** Scheduled MIRA entry uses the executable runtime's own offset-aware system clock, converts that instant through the IANA timezone `America/New_York`, and decides whether execution belongs to the intended 02:45/14:45 logical slot. It handles daylight-saving transitions using timezone rules, records dispatch delay, allows only bounded lateness, and may wait once for an execution handed off no more than 60 seconds early. A model-supplied, prompt-supplied, device, travel, session, or naive local timestamp is not production clock authority.

**Why it exists / user outcome:** A scheduled system should know what time it actually is. This requirement exists because prior failures demonstrated that merely printing an Eastern-looking timestamp is not evidence that execution occurred in the correct slot.

**Requirement status:** `required by failure evidence`.

**Delivery/evidence:** `test_verified` in the legacy executable and regression suite. **Actual MIRA 2.0 scheduler entry remains integration/live-unverified.**

**Hard dependencies:** trustworthy runtime system clock; IANA timezone database; `OPS-001` canonical slot definition.

**Enables:** scheduler-integrity circuit breaking, correct AM/PM derivation, trustworthy Run Log timestamps, travel-safe brief scheduling.

**Milestone:** scheduler/control-plane foundation.

**Legacy evidence:**
- `skill/ops-brief-policy/scripts/ops_policy.py`: `canonical_slot_evidence`, DST gap/repeat handling, grace bounds and runtime-owned live slot evidence;
- `skill/ops-brief-policy/scripts/test_ops_policy_entry.py`: tests equivalent summer/winter instants across Eastern/Central/Mountain/Pacific/UTC, bounded early dispatch, bounded delay, naive-time rejection and canonical-slot contradiction;
- `skill/ops-brief-policy/references/brief-run.md`: scheduled slot-check must run without model-supplied `--now`;
- legacy feature ledger category A row 3.

**Acceptance / verification boundary:** Repository tests must pass for DST/offset/grace behavior; then an actual scheduler integration must demonstrate that scheduled entry invokes the live runtime clock path and records matching canonical evidence. Only the latter can raise this feature beyond `test_verified`.

**Compatibility notes:** Future user-configurable timezones must still use the same IANA/runtime-clock model. No deployment may replace this with fixed UTC offsets.

---

### `OPS-004` — Fresh standalone run delivery with deterministic Run ID

**Description:** Every scheduled brief execution starts as a fresh run from the saved dispatcher rather than reusing an old chat response. A scheduled run receives the deterministic identity `OPS-YYYY-MM-DD-AM` or `OPS-YYYY-MM-DD-PM`; the delivered brief begins with that identity and is generated only from current-run state/evidence. The same identity is used for idempotent Run Log updates so retries or completion updates do not create a second logical run.

**Why it exists / user outcome:** The user must be able to distinguish today's actual brief from stale conversational output and determine whether the scheduler entered at all versus failing later in the workflow.

**Requirement status:** `required by stale-response incident`.

**Delivery/evidence:** `test_verified` for deterministic Run ID generation and policy contract; **fresh provider-created standalone scheduled delivery and live Run Log evidence remain unverified in MIRA 2.0**.

**Hard dependencies:** `OPS-003` canonical scheduled timestamp/slot; canonical Run Log/state feature to be audited later in category A; scheduler/provider capable of fresh-run invocation.

**Enables:** idempotent run logging, scheduler incident diagnosis, notification self-identification, stale-response prevention.

**Milestone:** scheduler and Ops Brief delivery foundation.

**Legacy evidence:**
- `skill/ops-brief-policy/scripts/ops_policy.py` deterministically creates `OPS-{date}-{slot}` Run IDs;
- `skill/ops-brief-policy/scripts/test_ops_policy.py` verifies `OPS-2026-08-15-AM` Run Log identity;
- `skill/ops-brief-policy/references/brief-run.md` requires current-run output and Run ID as the first line;
- `skill/ops-brief-policy/SKILL.md` requires fresh saved-prompt standalone execution;
- legacy feature ledger category A row 4.

**Acceptance / verification boundary:** Tests must verify deterministic identity and idempotent same-row logging semantics. Integration verification requires a scheduled provider run to start fresh, create/update the matching Run Log record, and deliver output beginning with the expected Run ID without reusing prior chat content.

**Compatibility notes:** Manual smoke runs use a separate `OPS-MANUAL-*` namespace and never count as proof of scheduled firing.

---

### `OPS-005` — Deterministic HOME/ROAD context with explicit overrides

**Description:** MIRA resolves the user's operational context deterministically from canonical settings rather than chat inference. The base recurring HOME/ROAD state is defined by configured weekly transitions. An active explicit mode override can temporarily supersede the recurring default, with inclusive start, exclusive expiry, stable override identity, conflict detection, and deterministic precedence. Other later context mechanisms, including active-trip forcing and generic context pairs, are separate audited features and must not silently redefine this record.

**Why it exists / user outcome:** Briefs and actionable tasks must reflect whether the user is operationally HOME or ROAD without guessing from conversation tone, location fragments, or yesterday's state.

**Requirement status:** `required`.

**Delivery/evidence:** `test_verified` for legacy deterministic policy logic. Historical private-deployment claims are not treated as current MIRA 2.0 live evidence.

**Hard dependencies:** canonical settings/state storage; explicit override records; timezone-aware deterministic time parsing. Interaction with active-trip precedence is a separate later category-A feature.

**Enables:** mode-specific task visibility, HOME-only weather, ROAD route/weather behavior, appointment/brief presentation rules, home-early handling.

**Milestone:** operational context foundation.

**Legacy evidence:**
- `skill/ops-brief-policy/scripts/ops_policy.py`: configured `normal_mode`, override preparation and `resolve_mode_at`;
- `skill/ops-brief-policy/scripts/test_ops_policy.py`: weekly-boundary/DST tests plus override start/expiry, latest-start precedence, conflict rejection, uniqueness and Home-early behavior;
- `skill/ops-brief-policy/scripts/test_ops_policy_entry.py`: explicit HOME override beats active trip and active trip interaction is separately exercised;
- `skill/ops-brief-policy/SKILL.md`: mode precedence/invariant;
- legacy feature ledger category A row 5.

**Acceptance / verification boundary:** Deterministic policy tests must pass for weekly boundaries, DST and override conflicts. Integration/live verification later requires canonical MIRA 2.0 state readback showing the configured transitions and an explicit override round trip without reliance on legacy production sheets.

**Compatibility notes:** This record intentionally does not absorb category-A behavior 6 (generic context pairs) or behavior 8 (active trip tracking/ROAD forcing). Those remain separate features so future generalization cannot erase the current HOME/ROAD semantics or pretend downstream dependencies are already complete.

## Audit status

- `M2-G0-002A` audited legacy category-A behaviors 1-5 and assigned `OPS-001` through `OPS-005`.
- The complete historical feature inventory is **not yet imported**. Do not infer absence from this file.
- The next bounded audit begins with legacy category-A behavior 6: generic context pairs (`HOME/ROAD`, `HOME/TRUCK`, `HOME/FIELD`, `HOME/CAMPUS`, `HOME/OFFICE`, `HOME/AWAY`, custom).
