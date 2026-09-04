# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active/recovery packet and exact recovery state.

## Product direction

Default Personal MIRA remains stock ChatGPT + Google Workspace first. Android extends the same canonical reality and must not become a second authority. Provider-specific Android authorization/network code must remain replaceable behind the shared client/core transport semantics so later Microsoft, Apple/iCloud and other provider lanes do not inherit Google as an architectural dependency.

M2-M1-001 through M2-M1-006 and M2-GOV-012 are durably closed. M2-M1-007 remains active because a duplicate concurrent implementation was discovered after PR #106 merged and before durable packet closeout.

## Prior-packet / remote-main verification — 2026-09-04

- Repository: `Matthew-Beare/Mira-2.0`.
- PR #106 merged M2-M1-007 implementation candidate to `main` at `f6d38ee9398bc473425f33b6fe97fb5fb0ae4b35`.
- Post-merge CI `33826483012` succeeded on exact merge SHA `f6d38ee9398bc473425f33b6fe97fb5fb0ae4b35`.
- A second concurrent M2-M1-007 implementation existed in PR #105 / `work/m2-m1-007-google-provider-binding`; PR #105 is now closed unmerged and preserved only as salvage evidence.
- The duplicate implementation is an active architecture/integrity blocker for packet closure, not a new product feature.

## Session-start alignment verification — reconciliation checkpoint

### `FEATURES.md`

- `CLIENT-ANDROID-001` remains partial and requires provider-neutral shared client semantics, protected credentials, replay-safe sync and evidence-based capability truth.
- `PROVIDER-002` requires ordinary-user native connection, unavoidable provider consent only, automatic post-consent verification/binding and no copied provider IDs or technical setup.
- `API-001`, `AUTH-001`, `STORE-001` and `RECOVERY-002` remain provider-neutral integrity boundaries.

### `BACKLOG.md`

- `ANDROID-CLIENT-CORE-001` remains partial; provider binding is only one prerequisite beneath the later `ANDROID-SYNC` vertical.
- `ANDROID-SYNC` remains unstarted and must not be smuggled into this reconciliation.
- The concurrent duplicate does not create a second work item; it must be reconciled inside M2-M1-007 before closure.

### `ROADMAP.md`

- M2-M1 still requires one Android connection/transport path into the same canonical Personal Workspace, followed later by canonical read, mutation, stock-ChatGPT cross-readback and representative-device proof.
- Two parallel Google provider stacks would contradict the single client path and increase migration/provider coupling risk.

### `PRODUCT_INVARIANTS.md`

- Provider consent is not readiness.
- Ordinary users must never copy IDs/scopes/tokens or perform developer setup.
- Google-specific provider details must not become canonical product semantics or a dependency of unrelated provider-neutral core behavior.
- No legacy MIRA production state may be used as a development fixture.

### Direction result

**ALIGNED WITH RECONCILIATION REQUIRED.** Keep the stronger product behavior from merged PR #106, but remove Google SDK/network dependencies from provider-neutral `:core` and salvage the separate provider module, stronger privacy surface, multi-module ownership/CI and stricter HTTP bounds from closed PR #105. Do not retain two implementations.

## Active packet

### `M2-M1-007` — Android Google authorization and Workspace binding reconciliation

- **Primary work:** `ANDROID-CLIENT-CORE-001`
- **Primary features:** `CLIENT-ANDROID-001`, `PROVIDER-002`, `PROVIDER-003`
- **Related invariants/features:** `AUTH-001`, `STORE-001`, `API-001`, `RECOVERY-002`, `DATA-001`, `SOURCE-001`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `work/m2-m1-007-provider-module-reconcile`
- **Base/main SHA:** `f6d38ee9398bc473425f33b6fe97fb5fb0ae4b35`
- **Source implementation:** merged PR #106
- **Salvage reference:** closed unmerged PR #105 / head `51d2203a6f951ae0bd8ef50b4e5ab3e596c2fa16`
- **Status:** active integrity reconciliation before durable M2-M1-007 closure

## Reconciliation decision

Keep from PR #106/main:

1. Google Identity Services Picker flow with exact `drive.file` scope and explicit revoke support.
2. Drive file metadata verification: selected ID, Google-Sheet MIME type, Trash state, edit capability and display name.
3. Clean-starter Metadata verification including environment/data-policy markers.
4. Distinction between `direct_single_writer` binding and verified `queued_writer` shared-write readiness.
5. Fresh-token revalidation of a token-free persisted binding.
6. Bounded Commands/Changes REST gateway and explicit provider failure mapping.

Salvage/strengthen from PR #105:

1. Move Google SDK/network implementation into a dedicated `:google-workspace` Android library depending on `:core`; `:core` must not depend on Google Play Services or INTERNET solely for this provider.
2. Extend Android ownership governance to multiple explicit Android production roots and run direct tests for all provider production files.
3. CI must execute both `:core` and `:google-workspace` unit tests.
4. Make access-token material package-internal/opaque outside the provider module; never expose it through public value-object getters or string representations.
5. Remove provider file IDs from `toString`/accidental log surfaces while retaining the non-secret binding identity internally for future persistence/revalidation.
6. Ensure HTTP connections disconnect in failure paths, bound response size is tested, response cells are primitive-only, and provider error bodies are never leaked.

## Acceptance criteria

1. Exactly one Google Workspace provider implementation remains in production source after reconciliation.
2. `android-client/core` contains only provider-neutral Android/client/transport semantics and has no Google Play Services dependency or provider-specific INTERNET requirement.
3. `android-client/google-workspace` owns Google Identity Services authorization/revocation, Picker grant parsing, Drive/Sheets verification, readiness/revalidation and concrete REST gateway behavior.
4. Merged PR #106 product behavior is preserved: file metadata verification, clean starter markers, direct-vs-queued readiness, queued headers, revalidation and revocation.
5. Provider token material is ephemeral and not publicly exposed by provider value objects; no token/file ID appears in `toString` or logs.
6. REST behavior remains bounded and fail-closed; arbitrary table mutation/read surfaces are rejected, ambiguous command append is not internally retried, response size and primitive-cell validation are directly tested.
7. Multi-module Android ownership and CI gates cover all production Java source with direct JVM test references.
8. No live provider mutation, Work mode, historical proof resource or legacy MIRA production fixture is used.
9. Exact-head CI passes before reconciliation merge.
10. After merge, remote main readback, post-merge CI, canonical lifecycle reconciliation and final closeout CI are verified before M2-M1-007 closes.

## Completed evidence

- PR #106 product implementation and exact post-merge CI are green on current main.
- PR #105 duplicate is closed unmerged; its branch remains available for salvage/readback.
- Comparative review found PR #106 stronger in readiness/file-verification/revalidation/revocation semantics and PR #105 stronger in provider-module separation/privacy/multi-module governance/HTTP hardening.
- Reconciliation branch created exactly from green main `f6d38ee9398bc473425f33b6fe97fb5fb0ae4b35`.

## Explicitly deferred

- Full `ANDROID-SYNC` canonical read/mutation/cross-ChatGPT proof.
- Broad Connections UI polish and conflict UI.
- Persistent account/profile UX beyond the token-free binding contract.
- Representative physical-device proof and release signing/distribution.
- Gmail, Calendar, Contacts, Microsoft, Apple/iCloud, Airtable, finance and other provider adapters.
- Integration recommendation engine under `PROVIDER-004`.

## Session-end alignment verification — pending reconciliation CI

### `FEATURES.md`

Pending final provider-module evidence reconciliation. `CLIENT-ANDROID-001` must remain partial.

### `BACKLOG.md`

Pending final M2-M1-007 closeout status. `ANDROID-CLIENT-CORE-001` remains partial and `ANDROID-SYNC` remains next.

### `ROADMAP.md`

Pending final confirmation that one reconciled provider path fills the M2-M1 provider-binding prerequisite without advancing the shared-state vertical.

### `PRODUCT_INVARIANTS.md`

Pending final confirmation of ordinary-user connection, least privilege, provider-neutral core, no second authority and no legacy-state mutation.

### Direction result

**PENDING RECONCILIATION IMPLEMENTATION/CI.**

## Exact next action / resume point

1. Port the PR #106 Google provider implementation from `:core` into a dedicated `:google-workspace` module while preserving its stronger readiness/revalidation/revocation behavior.
2. Apply the PR #105 privacy/HTTP/multi-module ownership/CI hardening.
3. Delete the duplicate Google provider production/test files and Google SDK/network requirements from `:core`.
4. Run exact-head CI and repair only M2-M1-007 integrity failures.
5. Record final FEATURES/BACKLOG/ROADMAP/PRODUCT_INVARIANTS alignment, merge the reconciliation PR with expected-head protection, verify main/post-merge CI, then perform final lifecycle closeout.
6. Do not enter Work mode; no live-provider-only blocker is currently known.

## Recovery protocol

Read this file first. Authoritative base is green main `f6d38ee9398bc473425f33b6fe97fb5fb0ae4b35`. PR #105 is closed salvage only; PR #106 is merged source behavior. Resume only the reconciliation steps above and do not create a third provider stack.
