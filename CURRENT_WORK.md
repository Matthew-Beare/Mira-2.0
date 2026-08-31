# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and exact recovery state.

## Product direction

Default Personal MIRA is stock ChatGPT + Google Workspace with no external infrastructure prerequisite. Repeated useful no-app verticals and integrity/recovery hardening remain ahead of Android. Normal user-facing branding is **MIRA**. `MIRROR` remains an internal database/reality-layer term only when a technical database-specific context requires it; normal product UI, brief titles, automation titles, and ordinary conversation say MIRA.

Every work session begins and ends by checking `CURRENT_WORK.md`, `FEATURES.md`, `BACKLOG.md`, and `ROADMAP.md`.

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
- **Primary feature:** `CAL-005`
- **Related features/invariants:** `RECOVERY-002`, `PROFILE-012`, `PROFILE-013`, `CAL-008`, `CAL-006`, `CAL-007`, `MAIL-002`, `HEALTH-001`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `integration/m0-021-appointment-identity`
- **Base SHA:** `10a8c43084ae75703a197ce7ea2f0cda734fca04`
- **Lifecycle checkpoint commits:** `83faeed82c43eb970926290abd8b30f4d67d3156`, `70c36b758895d32bbf662d365da999b028653f4c`
- **Current head before this checkpoint:** `70c36b758895d32bbf662d365da999b028653f4c`
- **PR:** not opened yet
- **Blockers:** none known; implementation must remain provider-neutral and synthetic-first.

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
- Branch `integration/m0-021-appointment-identity` is based on the verified PR #74 merge checkpoint and contains only lifecycle activation changes so far.
- Protected legacy production state has not been used or modified for this packet.

## Exact next action / resume point

1. Inspect existing canonical identity/resource models and appointment/provider-related tests/contracts before adding code.
2. Draft the minimal data/service contract for provider identity, appointment occurrence identity, reconciliation result, provenance/confidence, and ambiguity handling.
3. Implement the smallest synthetic provider-neutral slice with direct tests.
4. Run baseline repository gates before adding release/no-app wiring.
5. Keep `CURRENT_WORK`, `FEATURES`, `BACKLOG`, and `ROADMAP` aligned at every checkpoint; do not expand into `CAL-008`, Calendar projection, reminders, outbound email, health interpretation, migration, or Android.

## Recovery protocol

Read this file first. Confirm branch `integration/m0-021-appointment-identity` and its remote head before any implementation. If the branch head differs from the recorded checkpoint, inspect the intervening commits instead of reconstructing from chat. `M2-M0-020` is complete and must not be reopened absent new integrity evidence. Protected legacy MIRA production state remains read-only and unavailable as a development fixture.
