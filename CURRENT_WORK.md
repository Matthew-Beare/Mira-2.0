# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active/recovery packet and exact recovery state.

## Product direction

Default Personal MIRA remains stock ChatGPT + Google Workspace first, with provider-neutral expansion through explicit ordinary-user connections. MIRA should progressively learn what tools and services a user already relies on and recommend useful supported integrations without silently installing, authorizing, activating, migrating, or changing canonical authority.

`M2-M1-001` through `M2-M1-006` remain durably closed. `M2-GOV-012` is complete at its bounded product/governance specification evidence ceiling. It added no implementation or provider-specific runtime behavior.

## Prior-packet recovery verification — 2026-09-03

- Repository: `Matthew-Beare/Mira-2.0`.
- M2-M1-006 final authoritative `main`: `50cadf6e18245b4ef0842ad02b143fcb80d92ff0`.
- M2-M1-006 final closeout CI: `33705224181` — success on that exact head.
- M2-M1-001 through M2-M1-006 are durably closed and must not be rerun.

## Session-start alignment verification — 2026-09-03 M2-GOV-012

### `FEATURES.md`

- `ONBOARD-004` already owned progressive post-Minimum-Useful-Setup discovery without silent activation.
- `PROVIDER-002` already owned ordinary-user provider connection semantics and automated post-consent verification.
- The accepted gap was a stable semantic requirement for learning what tools/services the user already uses and making context-aware, capability-honest integration recommendations over time.

### `BACKLOG.md`

- `DISCOVERY-CORE-001` remained partial and already covered broader evidence-aware progressive discovery.
- Provider-specific adapters remained separate work and could not become semantic product authority.
- Android client-core narrative was stale because M2-M1-006 had already closed.

### `ROADMAP.md`

- M2-M0.5 already included progressive connected-integration discovery in the no-app Personal direction.
- M2-M1 remained the implementation milestone after this bounded governance normalization.

### `PRODUCT_INVARIANTS.md`

- Optional provider activation remained intent-first, ordinary-user friendly, least-privilege and explicitly consented.
- Recommendations could suggest connections but could never silently connect, activate, migrate, or create dual writable masters.
- Sensitive finance, health, identity and similar connections required explicit scoped user intent and honest disclosure of added data access/benefit before authorization.

### Direction result

**ALIGNED.** Add one provider-neutral semantic feature for context-aware integration discovery/recommendation, normalize concrete implementation work into BACKLOG, and preserve provider-specific adapter separation without implementing any integration in this packet.

## Active packet

### `M2-GOV-012` — Context-aware integration discovery product normalization

- **Primary work:** `DISCOVERY-CORE-001`
- **Primary features:** `ONBOARD-004`, `PROVIDER-004`, `PROVIDER-002`
- **Related invariants/features:** `SERVICE-001`, `PROVIDER-001`, `AUTH-001`, `STORE-001`, `RECOVERY-002`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Checkpoint branch:** `main`
- **Packet base SHA:** `50cadf6e18245b4ef0842ad02b143fcb80d92ff0`
- **Final verified PR head:** `454700ab0553044f5f4078c9f6a7a09a819ca71c`
- **Final verified PR-head CI:** `33731531260` — success
- **PR:** #104 — merged with expected-head protection
- **Merge/main SHA before this closeout commit:** `00fa7ccf53e8e4e7e0a0630a2e5a891dbd78eac7`
- **Verified post-merge CI:** `33731666665` — success on that exact merge SHA
- **Merged changed-file scope:** exactly `FEATURES.md`, `BACKLOG.md`, `CURRENT_WORK.md`
- **Status:** complete; this final closeout commit requires exact-head CI before durable closure

## Objective result

**COMPLETE AT THE PRODUCT/GOVERNANCE SPECIFICATION EVIDENCE CEILING.**

M2-GOV-012 now durably records that MIRA should:

1. ask during optional progressive onboarding how the user currently keeps track of things and what apps/services they already use;
2. dynamically choose examples from explicit work/lifestyle/goals and integrations that are actually supported/available;
3. later use provenance-bound evidence from already-authorized sources to suggest useful integrations;
4. deduplicate/rate-limit suggestions and preserve Not now / Don't suggest again state;
5. require explicit consent for every connection and heightened explicit intent/disclosure for sensitive domains;
6. keep Airtable, Plaid-like financial aggregators, merchant integrations, wearables, work tools and future services behind replaceable capability/provider adapters rather than hard-coded product semantics.

## Completed evidence

- `FEATURES.md` now contains stable semantic feature `PROVIDER-004` for context-aware integration discovery/recommendation.
- `BACKLOG.md` now contains `INTEGRATION-DISCOVERY-001` as an enhancement and `AIRTABLE-ADAPTER-001` as optional later work.
- Airtable is explicitly not required for default Personal MIRA and does not become canonical authority merely because a connector exists.
- Financial aggregation is preserved as provider-neutral behavior; a specific vendor such as Plaid is not a permanent semantic dependency.
- `BACKLOG.md` now records Android client core partial through M2-M1-006 rather than incorrectly calling M2-M1-006 active.
- GitHub issues #102 and #103 remain durable intake/history for Airtable and broader integration-discovery rationale.
- Final PR head `454700ab0553044f5f4078c9f6a7a09a819ca71c` passed exact-head CI `33731531260`.
- PR #104 merged with expected-head protection.
- Remote `main` independently read back merge SHA `00fa7ccf53e8e4e7e0a0630a2e5a891dbd78eac7`.
- Post-merge CI `33731666665` succeeded on that exact merge SHA, including compile, feature registry, lifecycle, Personal starter distribution, work-session alignment, code ownership, Android tests, Python tests and Workspace Apps Script tests.
- No Work mode, provider authorization, live external mutation, historical proof resource, implementation code or legacy production fixture was used in M2-GOV-012.

## Acceptance criteria result

1. Stable provider-neutral semantic feature — **satisfied by `PROVIDER-004`**.
2. Existing-tool onboarding discovery, dynamic examples, evidence-grounded recommendations, controls and sensitive-domain boundaries — **specified**.
3. Provider-specific adapters remain optional/separate and never implicit canonical authority — **satisfied**.
4. Zero implementation/provider/live/Work/legacy-state scope — **satisfied**.
5. Bounded Git scope — **satisfied: exactly three governance authority files**.
6. Exact-head CI before merge — **satisfied by `33731531260` on `454700ab0553044f5f4078c9f6a7a09a819ca71c`**.
7. Merge/main readback and post-merge CI — **satisfied by merge `00fa7ccf53e8e4e7e0a0630a2e5a891dbd78eac7` and CI `33731666665`**.

## Explicitly deferred

- `INTEGRATION-DISCOVERY-001` implementation/recommendation state machine.
- `AIRTABLE-ADAPTER-001` implementation.
- Financial-account aggregation implementation and provider selection.
- Merchant/site-specific integrations such as a future Amazon connector.
- Wearable/work-tool provider adapters.
- Android Google provider authorization/network binding, which remains the dependency-correct next implementation slice.

## Session-end alignment verification — 2026-09-03 M2-GOV-012

### `FEATURES.md`

`PROVIDER-004` now owns context-aware integration discovery/recommendation. `ONBOARD-004` remains the progressive discovery surface and `PROVIDER-002` remains the connection/consent surface. No concrete provider is promoted into semantic authority.

### `BACKLOG.md`

`INTEGRATION-DISCOVERY-001` is queued as an enhancement and `AIRTABLE-ADAPTER-001` is deferred optional provider work. Neither displaces the M2-M1 critical path. Android lifecycle prose now correctly records M2-M1-006 complete and leaves provider authorization/network binding as the next unfinished client-core dependency.

### `ROADMAP.md`

No roadmap ordering change was required. M2-M0.5 already includes optional connected-integration discovery, and M2-M1 remains dependency-correct after this governance normalization.

### `PRODUCT_INVARIANTS.md`

Intent-first consent, capability-honest provider connection, no silent activation, least privilege, automatic post-consent verification, and one-authority/no-dual-writable-master semantics remain preserved. `PROVIDER-004` narrows recommendations within those rules rather than weakening them.

### Direction result

**ALIGNED.** The new canonical feature/backlog entries preserve the accepted product direction without making any provider or recommendation engine part of this completed packet. Android Google provider binding remains next.

## Exact next action / resume point

1. Require CI on this final `main` closeout commit and verify it succeeds on the exact pushed head.
2. Independently read back remote `main` at that same closeout head.
3. Once both are verified, treat M2-GOV-012 as durably closed.
4. Re-read `CURRENT_WORK.md`, `FEATURES.md`, `BACKLOG.md`, `ROADMAP.md`, and `PRODUCT_INVARIANTS.md` from that authoritative main state.
5. Open exactly one bounded M2-M1 continuation, expected `M2-M1-007`, for Android-native Google authorization + automatic Workspace discovery/binding + the concrete narrow Sheets gateway beneath `GoogleWorkspaceTransport`.
6. Keep broad Connections UI polish, conflict UI, full `ANDROID-SYNC`, stock-ChatGPT cross-readback and representative-device proof separate unless a hard dependency emerges.
7. Do not use Work mode until implementation/source/tests are green and a narrow live provider/browser/device acceptance proof genuinely requires it.

## Recovery protocol

Read this file first. Verify remote `main` plus this final closeout commit's exact-head CI. If both are green, M2-GOV-012 is durably closed. Then open the next M2-M1 packet from Git, not from chat memory. Do not rerun M2-M1-001 through M2-M1-006.
