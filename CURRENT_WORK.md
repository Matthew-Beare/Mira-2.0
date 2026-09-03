# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active/recovery packet and exact recovery state.

## Product direction

Default Personal MIRA remains stock ChatGPT + Google Workspace first, with provider-neutral expansion through explicit ordinary-user connections. MIRA should progressively learn what tools and services a user already relies on and recommend useful supported integrations without silently installing, authorizing, activating, migrating, or changing canonical authority.

`M2-M1-006` is durably closed. This is a short governance normalization packet requested by the product owner before the next Android implementation slice. It does not implement integrations or expand into provider adapters.

## Prior-packet recovery verification — 2026-09-03

- Repository: `Matthew-Beare/Mira-2.0`.
- Final M2-M1-006 authoritative `main`: `50cadf6e18245b4ef0842ad02b143fcb80d92ff0`.
- Final M2-M1-006 closeout CI: `33705224181` — success on that exact head.
- M2-M1-001 through M2-M1-006 are durably closed and must not be rerun.
- No Work mode, live provider mutation, historical proof resource, or legacy production fixture is required for this governance packet.

## Session-start alignment verification — 2026-09-03 M2-GOV-012

### `FEATURES.md`

- `ONBOARD-004` already owns progressive post-Minimum-Useful-Setup discovery without silent activation.
- `PROVIDER-002` already owns ordinary-user provider connection semantics and automated post-consent verification.
- The accepted product gap is a stable semantic requirement for learning what tools/services the user already uses and making context-aware, capability-honest integration recommendations over time.

### `BACKLOG.md`

- `DISCOVERY-CORE-001` remains partial and is the existing implementation family for broader evidence-aware progressive discovery.
- `PROVIDER-ONBOARD-001` and `HOST-CONNECT-EXEC-001` already prove provider-neutral connection planning/native host discovery at their bounded evidence ceilings.
- Provider-specific adapters remain separate work and must not become semantic product authority.

### `ROADMAP.md`

- M2-M0.5 explicitly keeps progressive connected-integration discovery in the useful no-app Personal product direction.
- M2-M1 remains the active implementation milestone after this bounded governance normalization.

### `PRODUCT_INVARIANTS.md`

- Optional provider activation must remain intent-first, ordinary-user friendly, least-privilege and explicitly consented.
- Recommendations may suggest connections but must never silently connect, activate, migrate, or create dual writable masters.
- Sensitive finance, health, identity and similar connections require explicit scoped user intent and honest disclosure of added data access/benefit before authorization.

### Direction result

**ALIGNED.** Add one provider-neutral semantic feature for context-aware integration discovery/recommendation. Preserve `ONBOARD-004`, `PROVIDER-002`, `SERVICE-001`, Authority Registry semantics, and provider-specific adapter separation. Do not implement the recommendation engine, Airtable adapter, finance connector, or Android provider binding in this packet.

## Active packet

### `M2-GOV-012` — Context-aware integration discovery product normalization

- **Primary work:** `DISCOVERY-CORE-001`
- **Primary features:** `ONBOARD-004`, `PROVIDER-004`, `PROVIDER-002`
- **Related invariants/features:** `SERVICE-001`, `PROVIDER-001`, `AUTH-001`, `STORE-001`, `RECOVERY-002`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `work/m2-gov-012-integration-discovery`
- **Base SHA:** `50cadf6e18245b4ef0842ad02b143fcb80d92ff0`
- **Canonical normalization head before this evidence commit:** `2c58b0341ef0dd1c9addf6a7dc8254059318327d`
- **Verified exact-head CI:** `33731295422` — success
- **PR:** #104 — open against `main`
- **Status:** merge candidate after this final evidence head passes exact-head CI

## Objective result

**COMPLETE AT THE PRODUCT/GOVERNANCE SPECIFICATION EVIDENCE CEILING.**

M2-GOV-012 durably captures the accepted direction that MIRA should:

1. ask during optional progressive onboarding how the user currently keeps track of things and what apps/services they already use;
2. dynamically choose examples based on explicit work/lifestyle/goals and integrations that are actually supported/available;
3. later use provenance-bound evidence from already-authorized sources to suggest useful integrations;
4. deduplicate/rate-limit suggestions and preserve Not now / Don't suggest again state;
5. require explicit consent for every connection and heightened explicit intent/disclosure for sensitive domains;
6. keep concrete providers such as Airtable, Plaid-like financial aggregators, Amazon, wearables, work tools and future services behind capability/provider adapters rather than hard-coded product semantics.

## Completed evidence

- GitHub issue #102 captured optional Airtable-provider intake.
- GitHub issue #103 captured the broader context-aware integration discovery/recommendation product intent.
- `FEATURES.md` adds stable semantic feature `PROVIDER-004` without making any specific provider a universal dependency.
- `BACKLOG.md` adds `INTEGRATION-DISCOVERY-001` as an enhancement and `AIRTABLE-ADAPTER-001` as optional later work.
- `BACKLOG.md` also reconciles stale Android lifecycle prose: M2-M1-006 is complete, while provider authorization/network binding, automatic Workspace discovery/binding, bounded shared-state vertical, conflict UI and device proof remain unfinished.
- Compare from base `50cadf6e18245b4ef0842ad02b143fcb80d92ff0` to normalization head `2c58b0341ef0dd1c9addf6a7dc8254059318327d` shows only `FEATURES.md`, `BACKLOG.md`, and `CURRENT_WORK.md` changed.
- Exact-head CI `33731295422` succeeded on `2c58b0341ef0dd1c9addf6a7dc8254059318327d`, including compile, feature registry, product lifecycle ledger, Personal starter distribution, work-session alignment, code ownership, Android client core tests, Python tests, and Workspace Apps Script tests.
- No product implementation, Work mode, provider authorization, live external mutation, historical proof resource, or legacy production fixture was used.

## Acceptance criteria result

1. Stable provider-neutral semantic feature — **satisfied by `PROVIDER-004`**.
2. Existing-tool onboarding discovery, dynamic examples, evidence-grounded recommendations, controls and sensitive-domain boundaries — **specified**.
3. Provider-specific adapters remain optional/separate and never implicit canonical authority — **satisfied**.
4. Zero implementation/provider/live/Work/legacy-state scope — **satisfied**.
5. Bounded Git scope — **satisfied: three governance authority files**.
6. Exact-head CI before merge — **satisfied on normalization head `2c58b0341ef0dd1c9addf6a7dc8254059318327d`; this evidence commit requires its own final exact-head CI**.
7. Merge/main readback and post-merge CI — **pending closeout only**.

## Explicitly deferred

- `INTEGRATION-DISCOVERY-001` implementation/recommendation state machine.
- `AIRTABLE-ADAPTER-001` implementation.
- Financial-account aggregation implementation and provider selection.
- Merchant/site-specific integrations such as a future Amazon connector.
- Wearable/work-tool provider adapters.
- Android Google provider authorization/network binding, which remains the dependency-correct next implementation slice after this governance packet closes.

## Session-end alignment verification — 2026-09-03 M2-GOV-012

### `FEATURES.md`

`PROVIDER-004` now explicitly owns context-aware integration discovery/recommendation. `ONBOARD-004` remains the progressive discovery surface and `PROVIDER-002` remains the connection/consent surface. No concrete provider is promoted into semantic authority.

### `BACKLOG.md`

`INTEGRATION-DISCOVERY-001` is queued as an enhancement and `AIRTABLE-ADAPTER-001` is deferred optional provider work. Neither displaces the active M2-M1 critical path. The stale Android row/finding now correctly records M2-M1-006 complete and leaves provider authorization/network binding as the next unfinished client-core dependency.

### `ROADMAP.md`

No roadmap ordering change is required. M2-M0.5 already includes optional connected-integration discovery, and after this governance normalization M2-M1 remains the dependency-correct implementation milestone.

### `PRODUCT_INVARIANTS.md`

Intent-first consent, capability-honest provider connection, no silent activation, least privilege, automatic post-consent verification, and one-authority/no-dual-writable-master semantics remain preserved. `PROVIDER-004` narrows recommendations within those rules rather than weakening them.

### Direction result

**ALIGNED.** The new feature/backlog entries capture the accepted product direction without expanding this packet into implementation. Android Google provider binding remains next after durable governance closeout.

## Exact next action / resume point

1. Require exact-head CI on this final evidence commit.
2. Verify PR #104 remains exactly the intended three governance files and mergeable.
3. Merge PR #104 with expected-head protection only after green CI.
4. Independently read back remote `main` and verify post-merge CI.
5. Record durable M2-GOV-012 closure in `CURRENT_WORK.md` using the established closeout convention and verify its exact-head CI.
6. Then open exactly one dependency-correct M2-M1 continuation for Android-native Google authorization + automatic Workspace discovery/binding + the concrete narrow Sheets gateway beneath `GoogleWorkspaceTransport`.
7. Do not use Work mode until implementation/source/tests are green and a narrow live provider/browser/device acceptance proof genuinely requires it.

## Recovery protocol

Read this file first. Git remains authoritative. If interrupted, resume from PR #104 and the exact branch head, complete only its CI/merge/closeout verification, then open the next Android packet. Do not rerun M2-M1-001 through M2-M1-006.
