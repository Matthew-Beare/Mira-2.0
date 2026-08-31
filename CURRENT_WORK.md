# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and exact recovery state.

## Product direction

Default Personal MIRA is stock ChatGPT + Google Workspace with no external infrastructure prerequisite. Repeated useful no-app verticals and integrity/recovery hardening remain ahead of Android. Normal user-facing branding is **MIRA**. `MIRROR` remains an internal database/reality-layer term only when a technical database-specific context requires it; normal product UI, brief titles, automation titles, and ordinary conversation say MIRA.

Every work session begins and ends by checking `CURRENT_WORK.md`, `FEATURES.md`, `BACKLOG.md`, and `ROADMAP.md`.

## Session-start alignment verification — 2026-08-31

### `FEATURES.md`

Reviewed the canonical feature index. `CAL-005` is the required provider/appointment identity reconciliation feature; downstream intake, Calendar projection, reminders, outbound contact, and administrative-health composition remain separate feature boundaries.

### `BACKLOG.md`

Reviewed the dynamically ranked backlog. `APPOINTMENT-IDENTITY-001` is the single active work item in `M2-M0-021`; the completed backup predecessor remains closed and no higher-priority integrity blocker is recorded.

### `ROADMAP.md`

Reviewed the active milestone direction. The packet remains aligned with the stock-ChatGPT + Personal Google no-app path and stays ahead of Android/mobile expansion.

### Direction result

**ALIGNED.** Continue the bounded provider-neutral appointment identity core. Do not expand into extraction, Calendar writes, reminders, outbound email, medical interpretation, legacy migration, or Android.

## Completed predecessor

### `M2-M0-020` — Provider-neutral backup / restore core

- **Work:** `BACKUP-CORE-001`
- **Feature:** `BACKUP-001`
- **PR:** #74
- **Final PR head:** `7bc9052090d53790c6d79f658108f94e76efc088`
- **Merge SHA / current verified main checkpoint:** `10a8c43084ae75703a197ce7ea2f0cda734fca04`
- **Exact-head CI:** `33369577945` green
- **Post-merge main CI:** `33369639977` green
- **Provider evidence:** fresh isolated Google source/target proof verified zero source mutation, deterministic current-Resource export, exact revision restore into a fresh target, matching SHA-256 material parity, and explicit noncoverage of Event history/original idempotency history.
- **Evidence ceiling:** no claim of provider archive durability, encryption, retention/rotation, incremental backup, scheduler firing, RPO/RTO, automatic disaster recovery, authority cutover, or legacy migration.

`BACKUP-001` is reconciled to merged/provider-readback evidence in `FEATURES.md`; `BACKUP-CORE-001` is reconciled complete in `BACKLOG.md`.

## Active packet

### `M2-M0-021` — Appointment identity reconciliation core

- **Primary work:** `APPOINTMENT-IDENTITY-001`
- **Primary features:** `CAL-005`
- **Related invariants/features:** `RECOVERY-002`, `STORE-001`, `PROFILE-012`, `PROFILE-013`, `CAL-008`, `CAL-006`, `CAL-007`, `MAIL-002`, `HEALTH-001`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `integration/m0-021-appointment-identity`
- **Base SHA:** `10a8c43084ae75703a197ce7ea2f0cda734fca04`
- **Lifecycle checkpoint commits:** `83faeed82c43eb970926290abd8b30f4d67d3156`, `70c36b758895d32bbf662d365da999b028653f4c`
- **Implementation/ownership head before this checkpoint:** `9702da81571275b2b9ba18ccb35cfa820384b6eb`
- **PR:** #75 draft
- **Blockers:** first PR CI run `33372617001` failed only at the work-session-alignment gate because this file used noncanonical field labels and omitted the required session-start authority review; compile, feature registry, product ledger, and Personal starter distribution passed before that gate stopped the job.

### Objective

Implement the smallest provider-neutral canonical appointment/provider identity slice that can create or reconcile durable provider and appointment identities from already-normalized evidence, preserve provenance/confidence and ambiguity truth, deduplicate deterministic repeats, and return human-usable provider specialty/type semantics without conflating provider identity, appointment occurrence identity, Calendar projection, reminder delivery, or medical meaning.

### Explicitly out of scope

- inbound email/photo/OCR/text extraction (`CAL-008` / `APPOINTMENT-INTAKE-001`);
- Google/Microsoft/Apple Calendar writes or provider readback (`CAL-006` / `CAL-007`);
- reminder scheduling/delivery (`CAL-001` through `CAL-003`);
- outbound email, appointment negotiation, or contact (`MAIL-002` remains intact);
- diagnosis, treatment, medication, clinical inference, or interpreting specialty as medical meaning;
- legacy production migration or use of protected production appointment data as a test fixture;
- Android/mobile work.

## Acceptance criteria

1. Stable canonical provider identity is distinct from appointment occurrence identity.
2. Provider reconciliation supports normalized organization/name plus available contact and specialty/type attributes without requiring every field to exist.
3. Exact durable identifiers or deterministic normalized identity keys reconcile repeats idempotently; fuzzy/semantic guesses do not silently merge distinct providers or appointments.
4. Appointment occurrence identity preserves source/provenance references and supports repeated appointments with the same provider without collapsing them into one record.
5. Conflicting or insufficient identity evidence remains explicitly ambiguous/Needs Review rather than inventing a provider, specialty, time, or relationship.
6. User-confirmed identity corrections outrank lower-authority derived suggestions while original evidence remains immutable/auditable.
7. The core performs no Calendar write, reminder creation, outbound email, medical inference, or legacy production mutation.
8. Direct tests cover provider create/replay/update, same-provider multiple appointments, duplicate appointment reconciliation, conflicting provider candidates, missing optional metadata, user-confirmed correction precedence, and zero out-of-scope side effects.
9. Component ownership/direct-verification mapping and release/no-app contract are updated if new production code is added.
10. Required CI is green on the exact final PR head before merge; merge uses expected-head protection; post-merge main CI must pass before completion is claimed.

## Completed evidence for this packet

- `FEATURES.md` defines `CAL-005` as required appointment/provider identity reconciliation with normalized organization/contact and specialty/type attributes.
- `BACKLOG.md` ranks `APPOINTMENT-IDENTITY-001` active in `M2-M0-021` and records the explicit provider-neutral identity-only scope.
- `mira/appointments.py` now implements separate provider and appointment resources, exact identity-key reconciliation, immutable source fingerprints, field-authority precedence, explicit Needs Review outcomes, and no downstream Calendar/reminder/contact behavior.
- `tests/test_appointments.py` provides 12 direct synthetic tests covering the acceptance boundary; the same matrix passed against a local contract-compatible in-memory adapter before push.
- `project/code_ownership.json` registers `mira/appointments.py` under `APPOINTMENT-IDENTITY-001` / `CAL-005` with direct verification at `tests/test_appointments.py`.
- Draft PR #75 exists solely to run the required PR CI gates before release wiring or merge consideration.
- Protected legacy production state has not been used or modified for this packet.

## Exact next action / resume point

1. Verify the new PR CI run after this alignment repair.
2. If any gate fails, repair only the reported packet/baseline blocker before adding further feature work.
3. Once direct core and repository gates are green, inspect the no-app/release contract and add only the minimum provider-neutral wiring/evidence required by acceptance criterion 9.
4. Re-run exact-head CI, update `CURRENT_WORK`, `FEATURES`, `BACKLOG`, and `ROADMAP` with evidence, then remove draft status only when the packet is actually merge-ready.
5. Do not expand into `CAL-008`, Calendar projection, reminders, outbound email, health interpretation, migration, or Android.

## Recovery protocol

Read this file first. Confirm branch `integration/m0-021-appointment-identity` and its remote head before any implementation. If the branch head differs from the recorded checkpoint, inspect the intervening commits instead of reconstructing from chat. `M2-M0-020` is complete and must not be reopened absent new integrity evidence. Protected legacy MIRA production state remains read-only and unavailable as a development fixture.
