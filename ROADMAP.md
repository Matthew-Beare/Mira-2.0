# MIRA 2.0 ROADMAP

Git is authoritative. This roadmap defines milestone ordering; `BACKLOG.md` owns ranked work and `CURRENT_WORK.md` owns the one active packet.

## M2-G0 — Governance and forensic reconstruction

Goal: establish a clean, resumable development operating system and reconstruct the complete MIRA feature/dependency picture before new product implementation.

- G0-001 governance/branding baseline — complete.
- G0-002 through G0-008 feature audits — complete.
- G0-009 legacy branch/PR reconciliation — complete; PR #31 selective salvage only, wholesale mega-merge prohibited.
- G0-010 dependency graph and audit closeout — active/final G0 packet.

G0-010 closes only when the feature/work graph is acyclic on the M2-M0/M2-M1 critical path, later/conditional work is no longer over-blocking core, and the first bounded implementation packet is selected.

## M2-G1 — Clean reality foundation and synthetic proof

Goal: implement MIRA's canonical state foundation without touching legacy production or requiring an external provider for basic correctness tests.

Ordered foundation proof:
1. provider-neutral structured-state adapter contract plus deterministic in-memory synthetic adapter;
2. canonical Authority Registry using those adapters;
3. shared `API-001` runtime with same-user scoped authorization, mandatory idempotency/version preflight, conflict handling, audit, and exact readback;
4. synthetic API roundtrip proving create/read/mutate/replay/readback without provider state;
5. provider-neutral evidence-store adapter path and central component/feature integrity gates before broad code growth.

Synthetic fixtures only. No legacy Google artifact may be overwritten, renamed, repurposed, migrated, or used as a development fixture.

## M2-M0 — Stock ChatGPT core vertical slice

Goal: MIRA works in stock ChatGPT with Google-backed MIRROR reality state and **no required self-hosted server**.

Integration proof requires:
1. a secure ordinary-user-compatible managed/shared API deployment path;
2. a minimal Google structured/evidence adapter and a separate MIRA 2.0 synthetic sandbox namespace, independent from full end-user onboarding/bootstrap;
3. one canonical entity created through the shared API;
4. exact readback;
5. mutation through the same API;
6. replay/idempotency and conflict behavior;
7. verified Google-backed read-after-write;
8. stock ChatGPT and the deployed service using the same canonical authority path.

Full nontechnical installation, full Personal Google bootstrap, Calendar/Gmail/scheduler setup, and enterprise distribution are later release/onboarding work and do not block this first core proof.

## M2-M1 — Android companion vertical slice

Goal: Android reads and mutates the same canonical entity as M2-M0 without becoming a second authority.

Ordered proof:
1. Android client core against the shared API, with scoped/revocable client identity and OS-protected durable credentials;
2. replay-safe offline queue and reconnect/cursor synchronization;
3. Android read of the M2-M0 canonical entity;
4. Android mutation of that entity through `API-001`;
5. stock ChatGPT reads the Android mutation back from the same authority;
6. representative-device proof.

Native notifications/TTS, camera/barcode/NFC/BLE capture, release signing, and broader UI polish follow the shared-state proof unless required to demonstrate the client core itself.

## M2-M2 — Ops Brief vertical slice

Goal: generate and deliver one real MIRA Ops Brief from canonical MIRA 2.0 state with deterministic run identity, correct scheduling semantics, dependency-derived service readiness, and failure isolation.

## Release/onboarding hardening after core proofs

- machine-readable feature registry/drift tooling and component-ownership enforcement before broad growth;
- provider/account onboarding and full Personal Google bootstrap;
- browser-only nontechnical installation;
- deterministic starter/distribution promotion;
- service composition/readiness normalization;
- backup/restore and observability hardening;
- signed Android release/update continuity.

## Later milestone families

Exact order remains dependency-ranked after M2-M1/M2-M2 evidence.

- orders/shipments/receipts;
- assets/inventory/location/scanning;
- finance/reconciliation;
- calendar/reminders;
- recipes/meals/household workflows;
- web/desktop parity;
- local-service integrations;
- enterprise/locked-down deployment;
- migration from legacy MIRA production;
- wearables, voice, RFID, and specialized hardware.
