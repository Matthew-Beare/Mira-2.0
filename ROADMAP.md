# MIRA 2.0 ROADMAP

Git is authoritative. This roadmap defines milestone ordering; `BACKLOG.md` owns ranked work and `CURRENT_WORK.md` owns the one active packet.

## Product deployment invariant — easy first, advanced later

MIRA's default Personal path must be useful to an ordinary Google user before that user needs to understand servers, Linux, SQL, Cloud Run, networking, containers, Git, or paid model APIs.

The default deployment ladder is therefore:

1. **Personal Google Workspace baseline** — Google Drive/Docs/Sheets provide the user's ordinary Workspace substrate; Sheets is the first structured MIRROR authority, and a copied/bound Apps Script provides the lightweight HTTPS execution boundary needed by stock ChatGPT. First-run setup must be browser-only and require no self-hosted server or terminal.
2. **Advanced managed/self-hosted runtime** — users who need higher scale, local integrations, heavier automation, or stronger infrastructure control may move the same MIRA API/Authority semantics to Cloud Run, a Linux VM, containers, SQL, or another supported backend.
3. **Migration, not reinvention** — provider-neutral `API-001`, `AUTH-001`, and `STORE-001` contracts must prevent Google-specific storage/execution details from becoming canonical product semantics. `AUTHORITY-MIGRATION-001` owns staged cutover with parity, readback, rollback, and no dual writable masters.

Cloud Run work already completed remains valid as an advanced deployment path. It is not a prerequisite for the ordinary Personal Google first-run experience.

Google documentation confirms the intended low-friction packaging model: copying a spreadsheet copies attached bound Apps Script, and bound scripts can be deployed as web apps. MIRA should exploit that capability rather than make ordinary users provision infrastructure.

## M2-G0 — Governance and forensic reconstruction

Goal: establish a clean, resumable development operating system and reconstruct the complete MIRA feature/dependency picture before new product implementation.

- G0-001 governance/branding baseline — complete.
- G0-002 through G0-008 feature audits — complete.
- G0-009 legacy branch/PR reconciliation — complete; PR #31 selective salvage only, wholesale mega-merge prohibited.
- G0-010 dependency graph and audit closeout — complete.

## M2-G1 — Clean reality foundation and synthetic proof

Goal: implement MIRA's canonical state foundation without touching legacy production or requiring an external provider for basic correctness tests.

Ordered foundation proof:
1. provider-neutral structured-state adapter contract plus deterministic in-memory synthetic adapter;
2. canonical Authority Registry using those adapters;
3. shared `API-001` runtime with same-user scoped authorization, mandatory idempotency/version preflight, conflict handling, audit, and exact readback;
4. synthetic API roundtrip proving create/read/mutate/replay/readback without provider state;
5. provider-neutral evidence-store adapter path and central component/feature integrity gates before broad code growth.

Synthetic fixtures only. No legacy Google artifact may be overwritten, renamed, repurposed, migrated, or used as a development fixture.

## M2-M0 — Stock ChatGPT + Personal Google Workspace core vertical slice

Goal: MIRA works in stock ChatGPT with Google-backed MIRROR reality state through an **ordinary-user, browser-only Google Workspace first-run path**. No self-hosted server, Cloud Run project, terminal, Linux administration, SQL administration, or OpenAI API billing is required for the baseline proof.

Ordered proof:
1. preserve the existing provider-neutral API, Authority Registry, canonical state semantics, and isolated synthetic Google namespace;
2. package the first Personal Google runtime around a copyable Google Workspace starter, with Sheets as the first structured-state authority and bound Apps Script as the lightweight HTTPS execution boundary;
3. prove first-run setup without terminal or cloud-infrastructure provisioning;
4. prove authenticated health/query/command behavior through the same `API-001` semantics rather than creating a Google-specific second API;
5. stock ChatGPT creates one canonical entity through that endpoint;
6. exact Google-backed readback;
7. mutation through the same endpoint;
8. replay/idempotency and conflict behavior;
9. verified provider read-after-write;
10. confirm the deployment remains portable: Google-specific concerns stay behind adapters and later Linux/SQL/managed migration uses `AUTHORITY-MIGRATION-001`, not a new product model.

Broader Personal Google bootstrap for Calendar/Gmail/brief scheduling, full provider discovery, and polished onboarding remain subsequent hardening. The **baseline installation itself**, however, must already satisfy the ordinary-user/no-terminal product invariant.

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
- expand the baseline Personal Google Workspace starter into full deterministic provider/account onboarding;
- deterministic starter/distribution promotion and upgrade flow;
- service composition/readiness normalization;
- backup/restore and observability hardening;
- signed Android release/update continuity;
- advanced managed/self-hosted deployment profiles and verified backend migration.

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
