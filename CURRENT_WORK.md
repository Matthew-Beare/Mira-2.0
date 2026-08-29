# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and exact recovery state.

## Product direction

Default Personal MIRA is stock ChatGPT + Google Workspace with no external infrastructure prerequisite. Completed work stays in the product corpus with evidence and is filtered from future selection rather than deleted. Android and advanced infrastructure remain preserved later lanes until the no-app Personal product is meaningfully usable.

Every work session begins and ends by checking `CURRENT_WORK.md`, `FEATURES.md`, `BACKLOG.md`, and `ROADMAP.md`.

## Completed predecessor

### `M2-G0-011` — Product corpus reconciliation and progressive onboarding

Merged in PR #61 to `main` at `c776db72d4f3a0e37b0be5004ac1a15141df14e8` after latest-head CI `33281161401` passed. The merged product lifecycle ledger tracks 118 canonical features and 143 backlog work items without deleting completed history. Progressive onboarding now offers continue-setup-now versus start-using-MIRA, with a bounded one-topic-per-local-day discovery drip and fitness-goals branch.

`FEATURE-ALIGN-001` is complete by this merge. `DISCOVERY-CORE-001` remains partial because the progressive slice is test-verified but broader evidence-aware history/friction discovery remains unfinished.

## Preserved Android checkpoint

Android / `M2-M1-001` remains paused at the previously recorded live isolated Google queued-writer proof point. Synthetic command-boundary work is preserved and must not be redesigned when resumed.

## Active packet

### `M2-M0-010` — Deterministic Personal Google starter distribution

- **Primary work:** `DIST-STARTER-001`, `STARTER-SANITIZE-001`
- **Primary features:** `DIST-002`, `ONBOARD-002`, `ONBOARD-006`
- **Related invariants/features:** `DATA-001`, `SOURCE-001`, `ONBOARD-007`, `AUTH-001`, `STORE-001`, `RECOVERY-002`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `integration/m0-010-personal-starter-distribution`
- **Base SHA:** `c776db72d4f3a0e37b0be5004ac1a15141df14e8`
- **Objective:** replace the hand-maintained clean Google starter as the practical release authority with a deterministic, sanitized Git-backed Personal starter definition that can produce and verify the exact no-app Workspace substrate from one source revision.

## Session-start alignment verification — 2026-08-29

### `FEATURES.md`

Verified before implementation:

- `DIST-002` requires deterministic sanitized starter/distribution from one canonical source revision;
- `ONBOARD-002` requires a generic starter with no inherited personal production state;
- `ONBOARD-006` requires an ordinary-user browser-only path with no terminal fallback;
- `SOURCE-001` requires source read/write/readback gates but must not make Git knowledge an ordinary user's installation burden;
- `DATA-001` protects legacy MIRA production artifacts from use as release-generation fixtures;
- existing `AUTH-001`, `STORE-001`, first-boot, service-state and no-app protocol semantics must be carried into the generated starter rather than redefined by distribution code.

### `BACKLOG.md`

Verified before implementation:

- `DIST-STARTER-001` is queued specifically because the clean live Workspace template is evidence but not yet a deterministic source-derived release;
- `STARTER-SANITIZE-001` is queued because the existing clean-copy privacy proof still needs a deterministic source/distribution gate;
- `NONTECH-INSTALL-001` remains broader follow-on work and must not expand this packet into every browser/provider onboarding path;
- completed first boot/service-state/no-app instructions remain completed and must not be reimplemented here;
- Android and advanced Cloud Run work remain paused/partial and are not dependencies of this no-app distribution packet.

### `ROADMAP.md`

Verified before implementation:

- deterministic sanitized Workspace starter/distribution is the next listed no-app release concern after first boot/progressive onboarding;
- at least one meaningful user-visible no-app vertical still follows and must not be delayed by turning distribution into a giant installer platform;
- ordinary Personal use must remain stock ChatGPT + Google Workspace with no terminal, Linux, SQL, Cloud Run, Android, or separately billed API prerequisite.

### Direction result

**ALIGNED.** The shortest release-integrity gap is making the already-proven starter reproducible from Git rather than relying on a mutable hand-maintained Google Sheet.

## Required user-visible/release behavior

1. One Git-backed source definition describes the Personal starter tabs, exact headers, required Metadata values and clean-state invariants.
2. A release manifest is deterministically generated for a supplied canonical source SHA and records hashes of every public Workspace artifact plus the starter definition.
3. The starter definition contains no provider IDs, credentials, user identity, personal state, or legacy production references.
4. A verifier can inspect an independently created/copied spreadsheet snapshot and prove that schema/headers/clean-state match the source definition.
5. The generated release definition includes the current no-app instruction artifact, including progressive discovery, and therefore cannot silently ship older onboarding behavior.
6. The clean starter contains zero Resource/Event/Idempotency user data rows before Personal bootstrap.
7. Apps Script remains an embedded Workspace adapter; stock ChatGPT's authenticated Google connection remains the ordinary Personal client boundary.
8. The packet does not require an ordinary user to run Python or use Git. Python tooling is release/build verification only.

## Explicitly deferred

- full one-click browser installer/provider authorization UX (`NONTECH-INSTALL-001`);
- full Google Calendar/Gmail provider bootstrap;
- source-lane/runtime-router implementation;
- Ops Brief/tasks vertical implementation;
- Android/shared-writer live proof;
- Microsoft/Apple distribution adapters;
- legacy production migration.

## Acceptance criteria

1. Git contains a canonical sanitized Personal Google starter blueprint.
2. Blueprint validation rejects secrets/provider IDs/private state and structural drift.
3. Deterministic release manifest binds one source SHA to exact Workspace artifacts and blueprint hashes.
4. Manifest generation is reproducible byte-for-byte for identical inputs.
5. Snapshot verifier checks Metadata, Resources, Events and Idempotency headers plus clean-state invariants.
6. Snapshot verifier rejects inherited Resource/Event/Idempotency data.
7. Direct tests cover valid blueprint/manifest, tamper/hash drift, secret/provider-ID rejection, malformed tabs/headers, and dirty starter rejection.
8. CI validates distribution integrity on every PR.
9. Code ownership/evidence covers new production tooling.
10. Independent Google provider proof creates or copies a fresh starter from the source definition where connector capability permits and reads it back; if provider creation capability cannot reproduce a bound Apps Script project, evidence must state that exact boundary rather than overclaiming.
11. End-of-session FEATURES/BACKLOG/ROADMAP recheck confirms whole-life feature scope remains intact and first meaningful no-app vertical remains next.

## Exact next action

1. Add canonical Personal starter blueprint and deterministic release-manifest/verifier tooling.
2. Add tests, CI gate and ownership evidence.
3. Produce an independent Google spreadsheet from the blueprint where supported and perform exact readback against the verifier contract.
4. Reconcile `FEATURE-ALIGN-001` to completed and `DISCOVERY-CORE-001` to partial/test-verified in backlog status while preserving broader discovery work.
5. Run latest-head CI and end-of-session alignment.
6. Merge if green, then select/implement the first meaningful no-app vertical from unfinished lifecycle state.

## Recovery protocol

Read this file first. Continue on `integration/m0-010-personal-starter-distribution`. Do not resume Android or the broader installer stack while this bounded deterministic-starter packet is unfinished. Use synthetic/new release proof artifacts only; never legacy production Google state.