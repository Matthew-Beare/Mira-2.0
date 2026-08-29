# MIRA 2.0 ROADMAP

Git is authoritative. This roadmap defines milestone ordering; `BACKLOG.md` owns ranked work and `CURRENT_WORK.md` owns the one active packet.

## Product deployment invariant — easy first, advanced later

MIRA's default Personal path must be useful to an ordinary Google user before that user needs to understand servers, Linux, SQL, Cloud Run, networking, containers, Git, or paid model APIs.

The default deployment ladder is therefore:

1. **Personal Google Workspace baseline** — Google Drive/Docs/Sheets provide the user's ordinary Workspace substrate; Sheets is the first structured MIRROR authority, and stock ChatGPT uses its authenticated same-user Google Drive/Sheets connection as the Personal client authorization boundary. A copied/bound Apps Script may provide embedded Google-side initialization, validation or automation, but it is not required to be a public API gateway for stock ChatGPT. First-run setup must be browser-only and require no self-hosted server or terminal.
2. **Advanced managed/self-hosted runtime** — users who need higher scale, multi-client concurrency, local integrations, heavier automation, or stronger infrastructure control may move the same MIRA API/Authority semantics to Cloud Run, a Linux VM, containers, SQL, or another supported backend.
3. **Migration, not reinvention** — provider-neutral `API-001`, `AUTH-001`, and `STORE-001` contracts must prevent Google-specific storage/execution details from becoming canonical product semantics. `AUTHORITY-MIGRATION-001` owns staged cutover with parity, readback, rollback, and no dual writable masters.

Cloud Run work already completed remains valid as an advanced deployment path. It is not a prerequisite for the ordinary Personal Google first-run experience.

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

**Core proof status:** completed through `M2-M0-006` live provider evidence and merged protocol/bootstrap code. Broader onboarding and distribution hardening remain separate work.

Completed proof:
1. preserve the provider-neutral API, Authority Registry and canonical state semantics in an isolated synthetic Google namespace;
2. establish stock ChatGPT's official same-user Google Drive/Sheets connection as the Personal authenticated client boundary;
3. copy and sanitize a Google Workspace starter to metadata/schema + empty state tables only;
4. bootstrap a verified Google Sheets Authority and `entity` binding into the clean copy with exact idempotency/readback semantics;
5. create one canonical entity through the native Workspace client path;
6. exact Google-backed revision-1 readback;
7. same-request replay resolves to the persisted idempotency result with zero additional write;
8. revision-checked mutation to revision 2;
9. exact provider readback of resource and idempotency state;
10. codify the native connector protocol and clean-copy bootstrap with CI-verified failure behavior;
11. preserve portability: Google-specific concerns remain behind adapter/client protocol boundaries, and later Linux/SQL/managed migration uses `AUTHORITY-MIGRATION-001`, not a new product model.

The native Google connector proof is deliberately **single writer**. Google Sheets batch updates provide atomicity inside each mutation, but native read-then-write preflight is not distributed compare-and-swap. Android or other concurrent writers require a stronger execution boundary before they may mutate canonical state.

The preserved onboarding contract remains important but is not falsely counted as M2-M0 runtime implementation. `ONBOARD-003` still requires the four-question Minimum Useful Setup and resumable Interview Ledger. The full legacy interview/question-bank behavior remains source evidence until ported and test-verified in MIRA 2.0 under `FIRSTBOOT-CORE-001` / related onboarding work.

## M2-M1 — Android companion vertical slice

Goal: Android reads and mutates the same canonical entity as M2-M0 without becoming a second authority.

Ordered proof:
1. select a stronger shared execution boundary appropriate for concurrent Android + ChatGPT writers while preserving `API-001`/`AUTH-001`/`STORE-001`;
2. Android client core with scoped/revocable client identity and OS-protected durable credentials;
3. replay-safe offline queue and reconnect/cursor synchronization;
4. Android read of the M2-M0 canonical entity;
5. Android mutation of that entity through the shared execution boundary;
6. stock ChatGPT reads the Android mutation back from the same authority;
7. representative-device proof.

Native notifications/TTS, camera/barcode/NFC/BLE capture, release signing, and broader UI polish follow the shared-state proof unless required to demonstrate the client core itself.

## M2-M2 — Ops Brief vertical slice

Goal: generate and deliver one real MIRA Ops Brief from canonical MIRA 2.0 state with deterministic run identity, correct scheduling semantics, dependency-derived service readiness, and failure isolation.

## Release/onboarding hardening after core proofs

- port and test the four-question Minimum Useful Setup, durable resumable Interview Ledger, evidence-first prior-history discovery, and no-silent-activation onboarding contract;
- promote deterministic sanitized Workspace starter/distribution and browser-only upgrade/recovery flow;
- expand Personal Google bootstrap into full provider/account onboarding only as selected services require it;
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
