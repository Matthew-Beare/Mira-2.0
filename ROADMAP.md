# MIRA 2.0 ROADMAP

Git is authoritative. This roadmap defines milestone ordering; `BACKLOG.md` owns ranked work and lifecycle status, `FEATURES.md` owns stable semantic product scope, and `CURRENT_WORK.md` owns the one active packet.

## Product deployment invariant — easy first, advanced later

MIRA's default Personal path must be useful to an ordinary Google user before that user needs to understand servers, Linux, SQL, Cloud Run, networking, containers, Git, paid model APIs, or an Android companion app.

The default deployment ladder is therefore:

1. **Personal Google Workspace baseline** — Google Drive/Docs/Sheets provide the user's ordinary Workspace substrate; Sheets is the first structured MIRROR authority, and stock ChatGPT uses its authenticated same-user Google Drive/Sheets connection as the Personal client authorization boundary. A copied/bound Apps Script may provide embedded Google-side initialization, validation or automation, but it is not required to be a public API gateway for stock ChatGPT. First-run setup must be browser-only and require no self-hosted server or terminal.
2. **Useful no-app Personal product** — before Android becomes the development focus, stock ChatGPT + Google Workspace must have a real user-facing MIRA front door, durable Minimum Useful Setup, service-state foundations, progressive optional discovery, and at least one meaningful end-to-end Personal vertical. Plumbing proof alone is not a shippable product.
3. **Companion/provider expansion** — Android, Microsoft/Outlook/M365, and Apple/iCloud extend the same MIRA semantics. Apple/iCloud support is required direction but is not a blocker for the current Google-first Personal product.
4. **Advanced managed/self-hosted runtime** — users who need higher scale, multi-client concurrency, local integrations, heavier automation, or stronger infrastructure control may move the same MIRA API/Authority semantics to Cloud Run, a Linux VM, containers, SQL, or another supported backend.
5. **Migration, not reinvention** — provider-neutral `API-001`, `AUTH-001`, and `STORE-001` contracts must prevent Google-specific storage/execution details from becoming canonical product semantics. `AUTHORITY-MIGRATION-001` owns staged cutover with parity, readback, rollback, and no dual writable masters.

Cloud Run work already completed remains valid as an advanced deployment path. It is not a prerequisite for the ordinary Personal Google first-run experience.

## Work-session direction and lifecycle rule

Every development session must verify `CURRENT_WORK.md` against `FEATURES.md`, `BACKLOG.md`, and this roadmap before implementation and again before handoff/merge. The mechanical CI gate validates referenced IDs and required review sections; the developer still owns the semantic judgment that the active packet is moving MIRA toward the accepted product rather than merely producing locally green code.

Completed work remains in Git with evidence. It is not deleted to make the backlog look smaller. A deterministic product-lifecycle projection derived from `FEATURES.md` + `BACKLOG.md` must make completed/paused/deferred work easy to exclude from next-work selection while retaining history and preventing accidental reimplementation.

## M2-G0 — Governance and forensic reconstruction

Goal: establish a clean, resumable development operating system and reconstruct the complete MIRA feature/dependency picture before broad product implementation.

- G0-001 governance/branding baseline — complete.
- G0-002 through G0-008 feature audits — complete.
- G0-009 legacy branch/PR reconciliation — complete; PR #31 selective salvage only, wholesale mega-merge prohibited.
- G0-010 dependency graph and audit closeout — complete.
- G0-011 product lifecycle reconciliation + progressive onboarding — active: machine-readable feature/work lifecycle, stale completion reconciliation, post-four continue/use-MIRA choice, and bounded progressive discovery.

## M2-G1 — Clean reality foundation and synthetic proof

Goal: implement MIRA's canonical state foundation without touching legacy production or requiring an external provider for basic correctness tests.

Ordered foundation proof:
1. provider-neutral structured-state adapter contract plus deterministic in-memory synthetic adapter;
2. canonical Authority Registry using those adapters;
3. shared `API-001` runtime with same-user scoped authorization, mandatory idempotency/version preflight, conflict handling, audit, and exact readback;
4. synthetic API roundtrip proving create/read/mutate/replay/readback without provider state;
5. provider-neutral evidence-store adapter path and central component/feature integrity gates before broad code growth.

Synthetic fixtures only. No legacy Google artifact may be overwritten, renamed, repurposed, migrated, or used as a development fixture.

## M2-M0 — Stock ChatGPT + Personal Google Workspace core substrate

Goal: prove MIRA's canonical Google-backed MIRROR state can work in stock ChatGPT through an ordinary-user, browser-only Google Workspace path. No self-hosted server, Cloud Run project, terminal, Linux administration, SQL administration, or OpenAI API billing is required for the baseline proof.

**Core substrate status:** completed through `M2-M0-006` live provider evidence and merged protocol/bootstrap code. This proves the state foundation, not a complete user-facing MIRA.

Completed proof:
1. preserve provider-neutral API, Authority Registry and canonical state semantics in an isolated synthetic Google namespace;
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

## M2-M0.5 — Usable no-app Personal MIRA

Goal: turn the proven Google substrate into a product an ordinary person can actually begin using in stock ChatGPT before Android becomes the active development focus.

Ordered direction:

1. `FIRSTBOOT-CORE-001` — four-question Minimum Useful Setup + durable resumable Interview Ledger: **complete** in PR #58;
2. `SERVICE-STATE-001` — explicit request/readiness/activation truth: **complete** in PR #59;
3. `ONBOARD-INSTRUCTIONS` — source-backed stock-ChatGPT no-app operating protocol and fresh-copy first-boot proof: **complete** in PR #60;
4. `DISCOVERY-CORE-001` / `ONBOARD-004` — after question four offer **continue setup now** or **start using MIRA**; immediate continuation asks one topic at a time, while start-using-MIRA may include at most one unanswered discovery topic per local day in an eligible brief for up to seven topic-days, with no inference from silence and explicit opt-out; progressive slice active in M2-G0-011;
5. deterministic starter/distribution and browser-only ordinary-user recovery so the exact tested Personal product can be installed without terminal/server knowledge;
6. deliver at least one meaningful user-visible vertical in stock ChatGPT from canonical MIRA 2.0 state, with Ops Brief/tasks as the current default candidate unless dependency/value evidence selects a better first slice;
7. continue appointments, receipts/assets/inventory, meals/groceries, routines/fitness, education, optional wearables/local integrations, and other accepted feature families in lifecycle/dependency/value order rather than waiting for Android.

Progressive onboarding must not become an onboarding prison. Minimum Useful Setup remains exactly four questions. Deeper discovery is optional, resumable, records explicit accepted/declined/skipped state, and feeds existing canonical domains/services instead of inventing parallel authorities. The first bounded topic is optional fitness/activity/nutrition/weight-goal help with a goals follow-up when accepted; later topics cover meals/groceries, household/routines, education/study, receipts/assets/inventory, travel/work tracking, and optional connected integrations.

A packet in M2-M0.5 must not expand into the entire product. The objective is repeated real user-visible vertical progress on top of the already-proven Google substrate.

## M2-M1 — Android companion vertical slice

Goal: Android reads and mutates the same canonical reality as the no-app Personal product without becoming a second authority.

**Current status:** the shared command-boundary prerequisite is complete in M2-M1-001 at implemented, test, exact existing-project integration and live isolated Google-provider evidence levels. Android client core is next and unblocked; no Android client/UI/device evidence is claimed yet.

Ordered proof when resumed:
1. ~~complete the live isolated Google queued-writer proof for the already-built stronger shared execution boundary~~ — complete in M2-M1-001 on 2026-09-02;
2. Android client core with scoped/revocable client identity and OS-protected durable credentials — next;
3. replay-safe offline queue and reconnect/cursor synchronization;
4. Android read of canonical Personal state;
5. Android mutation through the shared execution boundary;
6. stock ChatGPT reads the Android mutation back from the same authority;
7. representative-device proof.

Native notifications/TTS, camera/barcode/NFC/BLE capture, release signing, and broader UI polish follow the shared-state proof unless required to demonstrate the client core itself.

## M2-M2 — Ops Brief vertical slice

Goal: generate and deliver one real MIRA Ops Brief from canonical MIRA 2.0 state with deterministic run identity, correct scheduling semantics, dependency-derived service readiness, and failure isolation.

M2-M2 may move into M2-M0.5 as the first no-app user-visible vertical if dependency checks confirm it is the shortest high-value slice. Progressive discovery may use an eligible brief slot, but it is limited to one discovery prompt per local day and must not displace higher-priority operational brief content.

## Release/onboarding hardening

These items are dependency-ranked around the no-app verticals rather than automatically postponed until Android:

- evidence-first prior-history discovery and no-silent-activation onboarding continuation;
- deterministic sanitized Workspace starter/distribution and browser-only upgrade/recovery flow;
- replace the M2-M1-001 maintainer-only updater, Apps Script project recovery and unverified developer-consent ceremony with an obvious product connection action and clearly identified, appropriately verified provider consent before ordinary-user shared access ships;
- Personal Google bootstrap expansion only as selected services require it;
- service composition/readiness normalization;
- backup/restore and observability hardening;
- signed Android release/update continuity after Android resumes;
- advanced managed/self-hosted deployment profiles and verified backend migration.

## Later milestone families

Exact order remains dependency-ranked after each user-visible proof rather than being treated as FIFO. The lifecycle ledger retains these families even when current implementation focus is elsewhere.

- orders/shipments/receipts;
- assets/inventory/location/scanning;
- finance/reconciliation;
- calendar/reminders;
- recipes/meals/household workflows;
- routines/fitness/accountability and optional wearables;
- education/study/offline preparation;
- travel/work-trip/mileage tracking;
- web/desktop parity;
- local-service/smart-home integrations;
- enterprise/locked-down deployment;
- migration from legacy MIRA production;
- voice, RFID, and specialized hardware.
