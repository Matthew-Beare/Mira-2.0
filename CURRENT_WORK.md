# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and exact recovery state.

## Product direction

Default Personal MIRA is stock ChatGPT + Google Workspace with no external infrastructure prerequisite. Completed work stays in the product corpus with evidence and is filtered from future selection rather than deleted. Android and advanced infrastructure remain preserved later lanes until the no-app Personal product is meaningfully useful.

Every work session begins and ends by checking `CURRENT_WORK.md`, `FEATURES.md`, `BACKLOG.md`, and `ROADMAP.md`.

## Completed predecessor

### `M2-G0-011` — Product corpus reconciliation and progressive onboarding

Merged in PR #61 to `main` at `c776db72d4f3a0e37b0be5004ac1a15141df14e8` after latest-head CI `33281161401` passed. The merged lifecycle ledger tracks 118 canonical features and 143 backlog work items without deleting completed history. Progressive onboarding now offers continue-setup-now versus start-using-MIRA, with a bounded one-topic-per-local-day discovery drip and fitness-goals branch.

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
- **PR:** #62
- **Objective:** replace the hand-maintained clean Google starter as the practical release authority with a deterministic, sanitized Git-backed Personal starter definition that can produce and verify the exact no-app Workspace substrate from one source revision.

## Session-start alignment verification — 2026-08-29

### `FEATURES.md`

Verified before implementation:

- `DIST-002` requires deterministic sanitized starter/distribution from one canonical source revision;
- `ONBOARD-002` requires a generic starter with no inherited personal production state;
- `ONBOARD-006` requires an ordinary-user browser-only path with no terminal fallback;
- `SOURCE-001` must not turn Git knowledge into an ordinary user's installation burden;
- `DATA-001` protects legacy MIRA production artifacts from development/release-fixture use;
- existing Authority, STORE-001, first-boot, progressive-onboarding and no-app protocol semantics must be carried into release artifacts rather than redefined.

### `BACKLOG.md`

Verified before implementation:

- `DIST-STARTER-001` and `STARTER-SANITIZE-001` were the bounded release-integrity gaps;
- `NONTECH-INSTALL-001` remains broader follow-on work and is not pulled into this packet;
- completed first boot/service state/no-app instructions remain completed;
- Android and advanced Cloud Run work remain paused/partial and are not dependencies of this packet.

### `ROADMAP.md`

Verified before implementation:

- deterministic sanitized Workspace starter/distribution is the next listed no-app release concern;
- at least one meaningful user-visible no-app vertical must follow immediately;
- ordinary Personal use remains stock ChatGPT + Google Workspace with no terminal, Linux, SQL, Cloud Run, Android, or separately billed API prerequisite.

### Direction result

**ALIGNED.** The shortest release-integrity gap was making the proven starter reproducible from Git rather than relying on a mutable hand-maintained Google Sheet.

## Implemented evidence

### Git-backed starter blueprint

`distribution/personal_google_starter.json` now defines the clean Personal Google spreadsheet substrate:

- distribution ID `mira-personal-google-workspace-v1`;
- neutral release timezone `Etc/UTC`;
- exactly four tabs: `Metadata`, `Resources`, `Events`, `Idempotency`;
- exact STORE-001 headers;
- exact clean Metadata values;
- zero mutable Resource/Event/Idempotency seed rows;
- explicit privacy invariants;
- exact Workspace artifact set including the current no-app instructions with progressive discovery.

### Deterministic release tooling

`mira/personal_distribution.py` now:

- validates the blueprint and Workspace bundle;
- rejects provider IDs, secret-like material, inherited mutable state and structural drift;
- binds a supplied canonical 40-character source SHA to the blueprint hash and sorted hashes of all Workspace artifacts;
- emits byte-deterministic JSON release manifests;
- verifies manifests against current source;
- verifies independently observed spreadsheet snapshots against exact title/timezone/tab/header/Metadata/clean-state rules.

CI now generates the source-SHA manifest twice, diffs the bytes, and verifies the result.

### Direct tests and ownership

`tests/test_personal_distribution.py` covers:

- valid sanitized blueprint;
- byte-identical manifest generation;
- manifest tamper detection;
- malformed source SHA rejection;
- provider/secret-like material rejection;
- dirty mutable seed rejection;
- exact clean snapshot acceptance;
- header drift/inherited-state rejection;
- Metadata drift rejection.

`project/code_ownership.json` now owns the distribution component under `DIST-002`, `ONBOARD-002`, `ONBOARD-006`, and `DATA-001` with `DIST-STARTER-001` / `STARTER-SANITIZE-001` work evidence.

## Independent Google provider proof — 2026-08-29

A newly created synthetic native Google spreadsheet was built from the Git blueprint rather than by copying the prior clean template or any legacy production artifact.

Provider readback verified:

- timezone `Etc/UTC`;
- exact four-tab set/order;
- exact Metadata seed values;
- exact Resources/Events/Idempotency STORE-001 headers;
- zero non-header mutable-state rows.

The synthetic proof spreadsheet was renamed after verification so it cannot be mistaken for an installable clean starter. The provider resource identifier is intentionally not committed to public Git.

Durable evidence: `docs/PERSONAL_STARTER_DISTRIBUTION_PROOF.md`.

### Bound Apps Script evidence boundary

The connected Google Drive/Sheets capability used here can create a native spreadsheet and issue Sheets batch updates, but it does not expose creation of a bound Apps Script project from source files. Therefore this packet does **not** claim source-to-provider installation of the bound Apps Script bundle.

The Apps Script source remains CI-validated. Browser/provider installation of the bound script belongs to `NONTECH-INSTALL-001` / provider-onboarding capability. This does not invalidate the independently live-verified spreadsheet substrate.

## Lifecycle reconciliation during packet

The generated product ledger remains the selector rather than deleting history. Current backlog semantics before merge:

- `FEATURE-ALIGN-001` — completed by PR #61;
- `DISCOVERY-CORE-001` — partial; progressive slice merged/test-verified, broader evidence-aware discovery remains unfinished;
- `DIST-STARTER-001` — active; implementation/CI/provider proof complete, merge pending;
- `STARTER-SANITIZE-001` — active; implementation/CI/provider proof complete, merge pending;
- Android command boundary remains partial;
- Cloud Run advanced proof remains paused.

Latest lifecycle validation on packet head before this closeout-only commit: 118 features / 143 work items; 50 completed, 74 queued, 2 active, 2 partial, 1 paused, 2 provisional, 10 deferred, 2 split, zero unknown.

## Latest test evidence

PR #62 CI run `33281516248` on head `f568f32b0008c475a9b53041cdb8bd35266c8ed0` passed before this closeout-only CURRENT_WORK commit:

- feature registry — green;
- product lifecycle ledger — green;
- Personal starter distribution validation + deterministic manifest diff + manifest verification — green;
- work-session alignment — green;
- code ownership — green;
- Python unit tests — **176/176 passed**;
- Workspace Apps Script tests — **15/15 passed**.

This closeout changes governance text only and must receive its own latest-head CI before merge.

## End-of-session alignment verification — 2026-08-29

### `FEATURES.md`

Rechecked after implementation:

- all 118 canonical feature IDs remain present;
- receipts/purchases/spending, meals/groceries, assets/fitment/knowledge, inventory/location/movement, routines/fitness, education, travel/mileage, wearables, local integrations, appointments/calendar, Android, Microsoft, Apple/iCloud, backup/recovery, voice, enterprise and MIRA Studio remain preserved;
- distribution code does not redefine canonical state, provider selection, onboarding, service activation, or domain semantics.

### `BACKLOG.md`

Rechecked after implementation:

- all 143 work items remain represented;
- no completed work was deleted;
- current distribution work is explicitly active rather than stale queued text;
- first meaningful no-app vertical `OPS-BRIEF-VSLICE` remains provisional and must be dependency-refined before implementation rather than blindly inheriting generic runtime-router dependencies;
- appointments, receipts/assets/inventory, meals/groceries and other user-visible verticals remain queued behind their actual prerequisites.

### `ROADMAP.md`

Rechecked after implementation:

- deterministic starter/distribution requirement is satisfied at the source + spreadsheet-substrate level pending merge;
- broader one-click/bound-script/provider installation remains correctly deferred;
- the next milestone concern is a meaningful user-visible no-app vertical, not more release/governance architecture;
- Android remains later until no-app MIRA provides real value.

### Direction result

**ALIGNED.** This packet closes the mutable-template release gap without expanding into the entire installer stack, and the next packet must be user-visible product behavior.

## Acceptance result

1. Canonical sanitized Personal Google starter blueprint — PASS.
2. Blueprint privacy/structural validation — PASS.
3. Source-SHA release manifest over exact artifacts — PASS.
4. Byte-for-byte reproducible manifest — PASS.
5. Exact spreadsheet snapshot verifier — PASS.
6. Dirty mutable-state rejection — PASS.
7. Direct distribution tests — PASS.
8. CI distribution integrity gate — PASS.
9. Code ownership/evidence — PASS.
10. Independent Google spreadsheet-substrate live proof — PASS; bound Apps Script source-to-provider installation explicitly NOT CLAIMED.
11. End-of-session whole-life feature preservation / next-vertical check — PASS.

## Exact next action

1. Run CI on this exact closeout head.
2. If green, merge PR #62 and remotely verify `main`.
3. In the next packet, mark `DIST-STARTER-001` and `STARTER-SANITIZE-001` completed with PR #62 evidence.
4. Dependency-audit `OPS-BRIEF-VSLICE` for the narrow stock-ChatGPT Personal lane. Do not require generic runtime/source routing unless it is genuinely needed for the first vertical.
5. Create a bounded no-app Ops Brief/task vertical child if needed, then implement the first real brief from canonical MIRA 2.0 state, including optional progressive-discovery prompt insertion rules.

## Recovery protocol

Read this file first. If PR #62 is still open, verify the exact head and CI before merge. If #62 is merged, verify `main`, then begin the bounded first no-app user-visible vertical from current `main`. Do not resume Android or broaden into the full installer stack by habit.