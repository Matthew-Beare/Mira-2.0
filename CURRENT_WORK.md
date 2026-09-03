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
- **Feature-definition commit before this checkpoint:** `9fea012a292a8f50b98c5c973dfd9f7f8ebee931`
- **Status:** active governance normalization only

## Objective

Durably capture the accepted product requirement that MIRA should:

1. ask during optional progressive onboarding how the user currently keeps track of things and what apps/services they already use;
2. dynamically choose examples based on explicit work/lifestyle/goals and integrations that are actually supported/available;
3. later use provenance-bound evidence from already-authorized sources to suggest useful integrations;
4. deduplicate/rate-limit suggestions and preserve Not now / Don't suggest again state;
5. require explicit consent for every connection and heightened explicit intent/disclosure for sensitive domains;
6. keep concrete providers such as Airtable, Plaid-like financial aggregators, Amazon, wearables, work tools and future services behind capability/provider adapters rather than hard-coded product semantics.

## Acceptance criteria

1. `FEATURES.md` contains a stable provider-neutral semantic feature for context-aware integration discovery/recommendation.
2. The feature explicitly covers onboarding existing-tool discovery, dynamic domain-aware examples, later evidence-grounded recommendations, recommendation controls, and sensitive-domain consent boundaries.
3. No provider-specific adapter is made a universal dependency or canonical authority.
4. No product implementation, provider authorization, live external mutation, Work mode, or legacy-data access occurs.
5. Git diff remains bounded to product/governance authority files.
6. Exact-head CI passes before merge.
7. After merge, remote `main` and post-merge CI are verified before the packet is considered closed.

## Completed evidence

- GitHub issue #102 captures `AIRTABLE-ADAPTER-001` as optional later provider-adapter intake without making Airtable a default authority.
- GitHub issue #103 captures the broader context-aware integration discovery/recommendation product intent.
- `FEATURES.md` commit `9fea012a292a8f50b98c5c973dfd9f7f8ebee931` adds canonical semantic feature `PROVIDER-004`.
- Compare against base `50cadf6e18245b4ef0842ad02b143fcb80d92ff0` shows exactly one added FEATURES line and no unrelated file changes before this CURRENT_WORK checkpoint.

## Explicitly deferred

- `INTEGRATION-DISCOVERY-001` implementation/recommendation state machine.
- `AIRTABLE-ADAPTER-001` implementation.
- Financial-account aggregation implementation and provider selection.
- Merchant/site-specific integrations such as a future Amazon connector.
- Wearable/work-tool provider adapters.
- Android Google provider authorization/network binding, which remains the dependency-correct next implementation slice after this governance packet closes.

## Session-end alignment verification — pending

### `FEATURES.md`

Pending final exact diff/readback.

### `BACKLOG.md`

Pending final lifecycle check; this packet does not promote provider-specific adapter intake into active implementation.

### `ROADMAP.md`

Pending final confirmation that M2-M1 remains next after this governance packet.

### `PRODUCT_INVARIANTS.md`

Pending final confirmation that explicit consent, no silent activation and one-authority semantics remain preserved.

### Direction result

**PENDING FINAL CI/DIFF VERIFICATION.**

## Exact next action / resume point

1. Verify the final branch diff contains only the intended `FEATURES.md` semantic addition plus this `CURRENT_WORK.md` packet checkpoint.
2. Run/fetch exact-head CI and repair only governance/integrity failures if any.
3. Record session-end alignment and merge through a bounded PR.
4. Verify remote `main` plus post-merge CI.
5. Close M2-GOV-012, then open exactly one dependency-correct M2-M1 continuation for Android-native Google authorization + automatic Workspace discovery/binding + the concrete narrow Sheets gateway beneath `GoogleWorkspaceTransport`.
6. Do not use Work mode until implementation/source/tests are green and a narrow live provider/browser/device acceptance proof genuinely requires it.

## Recovery protocol

Read this file first. Git remains authoritative. If this packet is interrupted, resume from the exact branch/head and complete only the governance normalization/merge verification before opening Android implementation work.
