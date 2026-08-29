# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and the exact recovery point.

## Product deployment invariant

Default Personal MIRA is **Google Workspace first, zero infrastructure**. An ordinary user starts with Google Drive/Docs/Sheets and browser-managed Google authorization. Linux, SQL, Cloud Run, containers, tunnels and local services are advanced upgrade paths.

Canonical ladder:
1. Personal Google Workspace: Sheets as first structured MIRROR authority; stock ChatGPT uses its authenticated same-user Google Drive/Sheets connection as the Personal client authorization boundary. Bound Apps Script may provide embedded Google-side initialization/validation/automation but is not the required public API gateway for stock ChatGPT.
2. Advanced profiles: Cloud Run, Linux VM, containers, SQL/local services or another stronger shared execution boundary when concurrency/infrastructure needs require one.
3. Migration preserves `API-001`, `AUTH-001`, `STORE-001`; backend changes are explicit Authority/adapter cutovers, never dual writable masters.

## Preserved displaced packet

### `M2-M0-005` — Cloud Run credential + live Google deployment proof
- Related work: `API-DEPLOYMENT-001B`.
- Paused/deprioritized; not failed/deleted.
- PR #48 merged `acb37af4aa378e8128d8591406859fe954af3474`; CI `33217543700` green.
- PR #49 merged `3332081054d691eca646c1d7bb274d22096f1c62`; CI `33218561781` green.
- Pre-pivot checkpoint: `c392b9b829fab989be8856c9272294c9907e409e`.
- No live Cloud Run evidence claimed.

## Active packet

### `M2-M0-006` — Google Workspace zero-infrastructure first run

- **Primary work:** `API-DEPLOYMENT-001A`
- **Adjacent client work:** `CHATGPT-API-CLIENT-001`, `CORE-ROUNDTRIP`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Closeout branch:** `integration/m0-006-closeout`
- **Closeout base:** `07d79c3a72cc906e93316e213e282919a1fcc4ff`
- **Status:** implementation/live acceptance is complete. Only Git reconciliation/CI/merge of the closeout checkpoint remains before the next packet is activated.

## Objective

Prove the ordinary-user Personal MIRA path without infrastructure administration. Stock ChatGPT uses the user's authenticated Google Drive/Sheets connection to access canonical MIRROR state while preserving MIRA Authority, revision, idempotency and exact-readback semantics.

Target first use: **copy starter → connect/authorize Google → initialize MIRA → use MIRA in ChatGPT**.

## Acceptance evidence

### 1. No infrastructure prerequisite — PASSED
No server, Cloud Run project, Linux/SQL administration, tunnel, terminal or paid OpenAI API was required for the Personal proof.

### 2. Clean/copyable Workspace starter — PASSED for live proof
A copied synthetic workbook was sanitized to metadata/schema + empty Resources/Events/Idempotency tables. A separate reusable clean template was then created and verified with the same clean structure. No provider IDs, personal data or live row contents are committed to public Git.

Deterministic public distribution promotion remains separate under `DIST-STARTER-001` / `STARTER-SANITIZE-001`; the live Drive template is evidence, not a Git source of truth.

### 3. Same MIRA semantics — PASSED
`mira/workspace_native.py` preserves STORE-001-compatible request fingerprints, revision behavior, idempotency behavior, exact provider readback and failure categories. Google-specific transport does not create a second product model.

### 4. Canonical Authority — PASSED
A clean copied workbook was bootstrapped from empty state to exactly one verified Google Sheets Authority plus one `entity` Authority binding. The Authority/binding + matching idempotency rows were written as one atomic four-request Sheets batch and read back exactly.

### 5. Scoped authentication — PASSED
Stock ChatGPT's official same-user Google Drive/Sheets connection is the Personal client authorization boundary. No bearer credential is hidden in Sheet cells, URL parameters, prompt text or Git.

### 6. Google-backed roundtrip — PASSED
On the clean copied starter:
- a fresh entity and idempotency key were proven absent;
- create + idempotency wrote atomically;
- exact revision-1 provider readback passed;
- replay preflight resolved same key + same material to the stored result and required zero additional write;
- revision 1 was re-read before mutation;
- revision-2 update + idempotency wrote atomically;
- exact resource/idempotency provider readback passed.

### 7. Browser-first — PASSED
All live Personal proof actions used browser/account-connected Google capabilities only.

### 8. Legacy preservation — PASSED
Only isolated MIRA 2.0 synthetic/copied starter state was modified. Legacy production Google artifacts were not used as fixtures or mutated.

### 9. Portability — PASSED as architecture/evidence boundary
Provider-neutral `API-001`, `AUTH-001`, `STORE-001` remain intact. `AUTHORITY-MIGRATION-001` owns later controlled cutover. The native connector path is not promoted to universal multi-client architecture.

### 10. Cloud Run nonblocking — PASSED
Cloud Run remains advanced hardening at the preserved `M2-M0-005` checkpoint.

## Merged implementation evidence

### PR #50 — embedded Workspace read slice
- merge: `e412405a475d1423edaac821d7a99481e4a6eb4b`
- CI: `33243206658` green
- copy-bound Apps Script initialization, health/schema/read-only query, persisted Authority resolution, commands fail closed, executable Apps Script tests.

### PR #51 — native stock-ChatGPT Workspace protocol
- merge: `641a7ce412bd0de46500c229910e52cb35a90bcc`
- CI: `33243533206` green
- deterministic single-writer native Google protocol; STORE-001 fingerprint/material parity; atomic resource+idempotency batches; replay/no-write; revision/idempotency conflicts; exact readback.

### PR #52 — clean-copy Workspace bootstrap
- merge: `07d79c3a72cc906e93316e213e282919a1fcc4ff`
- CI: `33243840207` green
- deterministic all-new/all-replay Personal Authority bootstrap; atomic four-request Authority+binding initialization; partial/conflicting bootstrap fails closed; live clean-copy bootstrap/provider proof recorded without provider IDs/private rows.

## Concurrency boundary

The Personal native Google path is intentionally **single writer**. Google Sheets `batchUpdate` is atomic inside each mutation, but a separate provider read followed by write is not distributed compare-and-swap. Android or another concurrent writer must not mutate Sheets directly through this protocol. M2-M1 must select/use a stronger shared execution boundary before enabling concurrent canonical mutation.

## Onboarding interview preservation

The user's existing new-user interview design is preserved as audited semantic/source evidence, not silently discarded:

- `ONBOARD-003` requires exactly four kickoff questions before deeper discovery: system name, authoritative IANA timezone, broad life/work pattern, and biggest remembering/organizing/deciding/planning/follow-through problems.
- Follow-up is bounded to at most four related questions at a time and persists a resumable Interview Ledger with `Answered`, `Resolved from evidence`, `Not applicable`, `Deferred`, and `Unresolved` behavior.
- `ONBOARD-004` includes current AI-use/friction discovery and requires inspecting accessible current conversation, files/File Library, Drive/Calendar/email and other connected evidence before asking the user to rebuild history. Inaccessible prior chats must be disclosed rather than invented.
- Preferences, permissions, sharing and destructive choices are never inferred from evidence.
- Legacy detailed source remains in `MIRA-Public-Experimental` (`starter/START_HERE.md`, `starter/LIFE_INTERVIEW.md`, question banks).
- **Truth boundary:** the full Interview Ledger/question-bank engine is not yet ported into MIRA 2.0 runtime code. `FIRSTBOOT-CORE-001` / `DISCOVERY-CORE-001` remain queued; the contract is preserved, not falsely claimed live.

This clarification does not expand M2-M0-006 into onboarding implementation.

## Scope control

Do not fan out into Gmail, Calendar, scheduler, Ops Briefs, family sharing, Android implementation, enterprise, Linux/SQL implementation or Cloud Run during this closeout. Do not touch legacy production artifacts.

## Exact next action

1. Open the `integration/m0-006-closeout` PR containing `ROADMAP.md`, `BACKLOG.md`, and this checkpoint.
2. Run full CI and fix only reconciliation/integrity failures.
3. Merge and remotely verify the merge/head.
4. After merge, activate the next dependency-ranked packet. Current roadmap/backlog points to the first bounded M2-M1 prerequisite: select and prove the stronger concurrent execution boundary required before Android can become a canonical writer.

## Recovery protocol

Read this file first. Verify main contains PR #52 merge `07d79c3a72cc906e93316e213e282919a1fcc4ff` or a descendant. If the closeout PR is still open, finish only `M2-M0-006`. If it is merged, treat M2-M0 core proof as complete and create the next packet from the verified merge head. Preserve Cloud Run checkpoint `c392b9b829fab989be8856c9272294c9907e409e`. Keep provider IDs, secrets, personal data and live row contents out of public Git.
