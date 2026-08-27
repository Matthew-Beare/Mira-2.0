# MIRA 2.0 FEATURES

This file is the human-readable canonical feature registry. It will be populated and normalized through bounded forensic audit packets. Machine-readable dependency metadata may be added after stable IDs are assigned.

## Feature identity rule

Every durable feature receives a stable semantic ID. IDs do not change merely because roadmap priority or table position changes.

Planned ID families include, subject to audit normalization:

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

Each feature must distinguish requirement from delivery evidence:

1. `desired`
2. `specified`
3. `implemented`
4. `test_verified`
5. `integration_verified`
6. `live_verified`
7. `rejected_or_superseded` when applicable

Code existence does not imply completion.

## Required feature record

Each audited feature should eventually contain:

- stable feature ID;
- name;
- full user-facing description;
- why it exists / user outcome;
- current requirement status;
- delivery/evidence level;
- hard dependencies;
- downstream capabilities enabled;
- milestone association;
- known implementation/evidence paths;
- acceptance criteria or verification boundary;
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

## Audit status

The complete historical feature inventory has **not yet been imported** into this registry. Do not infer absence from this seed file. The G0 audit packets intentionally reconstruct the remaining feature set from legacy ledgers, code/tests, open PRs/branches, and product decisions in bounded slices.
