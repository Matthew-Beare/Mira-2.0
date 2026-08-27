# MIRA 2.0 ROADMAP

Git is authoritative. This roadmap is milestone ordering, not a FIFO task list.

## M2-G0 — Governance and forensic reconstruction

Goal: establish a clean, resumable development operating system and reconstruct the complete MIRA feature/dependency picture before new product implementation.

### G0-001 — Governance/branding baseline
- establish MIRA as the primary product brand;
- define MIRA as Modular Intelligence & Reasoning Assistant;
- define MIRROR as MIRA's companion reality database;
- install full-replacement Project Instructions;
- install packet/recovery rules;
- protect legacy Google production data;
- define brand-asset integration spec.

### G0-002 — Feature Audit Slice A
Governance/core runtime + Brief/Time/Operational State.

### G0-003 — Feature Audit Slice B
Calendar, appointments, reminders, mail, and communication safety.

### G0-004 — Feature Audit Slice C
Orders, shipments, receipts, payments, spending, and reconciliation.

### G0-005 — Feature Audit Slice D
Assets, fitment, inventory, shopping, household storage, identifiers, and evidence.

### G0-006 — Feature Audit Slice E
Profiles, onboarding, family/dependents, customization, accessibility, and user modes.

### G0-007 — Feature Audit Slice F
Providers, Google/Microsoft/Apple portability, distribution, update channels, institutional/locked-down deployment.

### G0-008 — Feature Audit Slice G
ChatGPT, Android, web/PWA, Windows/Linux desktop, CLI, notifications, packaging, scanning, device/hardware surfaces.

### G0-009 — Legacy branch/PR reconciliation
Map PR #31 and other meaningful unmerged/legacy work against stable MIRA 2.0 feature IDs. Salvage bounded components only; never merge the historical mega-PR wholesale.

### G0-010 — Dependency graph and audit closeout
- stable semantic feature IDs;
- full descriptions;
- dependency and enables relationships;
- duplicate/superseded/rejected reconciliation;
- implementation/evidence level;
- acceptance criteria where appropriate;
- final ranked backlog.

## M2-G1 — MIRA 2.0 clean reality sandbox

Goal: create a separate development Google/MIRROR environment without touching legacy production data.

- define canonical entity/state/evidence contracts from audited requirements;
- create separate MIRA 2.0 Google sandbox namespace;
- synthetic test data only unless explicitly approved;
- provider read/write/readback proof;
- verify no legacy artifact overwritten, renamed, repurposed, or migrated.

## M2-M0 — Stock ChatGPT core vertical slice

Goal: MIRA works in stock ChatGPT with Google-backed MIRROR reality state and no required self-hosted server.

Candidate first proof, subject to dependency audit:
- identify canonical MIRA 2.0 reality authority;
- create one canonical entity;
- read it back;
- mutate it;
- deduplicate/reconcile repeat requests;
- prove read-after-write.

## M2-M1 — Android companion vertical slice

Goal: Android reads and mutates the same canonical reality state without becoming a second authority.

## M2-M2 — Ops Brief vertical slice

Goal: generate and deliver a real brief from MIRA 2.0 canonical state with deterministic run identity, correct scheduling semantics, and failure isolation.

## Later milestone families

Exact order is determined after the G0 dependency audit.

- orders/shipments/receipts;
- assets/inventory/location/scanning;
- finance/reconciliation;
- calendar/reminders;
- meal/household workflows;
- web/desktop parity;
- local-service integrations;
- enterprise/locked-down portability;
- migration from legacy MIRA production;
- RFID and specialized hardware.
