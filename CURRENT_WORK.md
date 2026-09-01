# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and exact recovery state.

## Product direction

Default Personal MIRA is stock ChatGPT + Google Workspace with no external infrastructure prerequisite. Connecting apps must be as close to one-click as the host/provider safely permits. If software can create, discover, bind, verify, or route around technical setup, the user does not perform that setup. Provider-native authorization is acceptable unavoidable ceremony; copied IDs, manually created provider resources, OAuth-scope editing, Apps Script/developer-console work, pasted code, terminal setup, Linux, SQL, Cloud Run, or paid OpenAI API usage are not default Personal prerequisites when software can route around them.

Product-owned clients may expose obvious service-level controls such as **Connect Google Calendar**, **Connect Google Drive**, and **Connect Gmail**. Stock ChatGPT is host-controlled: MIRA must use the closest supported native ChatGPT/provider connection flow and must not promise arbitrary custom host UI that the product cannot render.

Authorization, verified provider capability, runtime routing, connection presentation, and MIRA service activation remain separate truths. Android must later consume the same connection semantics rather than inventing another activation model.

Every work session begins and ends by checking `CURRENT_WORK.md`, `FEATURES.md`, `BACKLOG.md`, `ROADMAP.md`, and applicable product invariants.

## Session-start alignment verification — 2026-09-01

### `FEATURES.md`

- `PROVIDER-002` is the primary feature: ordinary-user provider onboarding through native consent, automatic discovery/binding/verification, and no avoidable technical setup.
- `PROVIDER-001` runtime routing is complete and must be reused rather than duplicated.
- `SOURCE-001` capability evidence is complete and remains canonical for authorization/read/write/remote-readback truth.
- `ONBOARD-006` requires browser-only nontechnical Personal setup with no terminal fallback.
- `SERVICE-001` preserves explicit user intent and activation separately from connection/capability state.
- `RECOVERY-002` requires one broken provider/service connection to fail closed without poisoning unrelated lanes.

### `BACKLOG.md`

- `SOURCE-GATES-001` is complete in M2-M0-026.
- `RUNTIME-ROUTER-001` is complete in M2-M0-027 / PR #86; closure PR #87 merged at `7b406021728d39e202071e14d8fa1a53ba4a6ed1` with post-merge CI `33473606399` green.
- `PROVIDER-ONBOARD-001` is now the highest-leverage ordinary-user M2-M0.5 item and has its direct architectural prerequisites complete.
- `GOOGLE-BOOTSTRAP-001`, `NONTECH-INSTALL-001`, `SOURCE-LANES-001`, `SERVICE-COMPOSE-001`, `DISCOVERY-CORE-001`, and `MIRA-SKILL-001` remain downstream/adjacent and do not expand this packet.
- Android remains separately preserved and paused.

### `ROADMAP.md`

- M2-M0.5 continues to prioritize useful ordinary-user no-app Personal MIRA before Android.
- Seamless provider onboarding is now unblocked by capability gates and runtime routing.
- M2-M1 remains paused at the live isolated Google queued-writer proof resume point.

### Direction result

**ALIGNED.** Implement the smallest provider-neutral connection orchestration/presentation contract that consumes existing capability and router truth. The first slice defines what connection state/action MIRA may honestly present and what next native-host/provider action is required. It does not perform OAuth, provider discovery, provider mutation, or service activation.

## Active packet

### `M2-M0-028` — Ordinary-user provider connection orchestration

- **Primary work:** `PROVIDER-ONBOARD-001`
- **Primary feature:** `PROVIDER-002`
- **Related features/invariants:** `PROVIDER-001`, `SOURCE-001`, `ONBOARD-006`, `SERVICE-001`, `RECOVERY-002`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `integration/m0-028-provider-onboarding`
- **Base/main SHA:** `7b406021728d39e202071e14d8fa1a53ba4a6ed1`
- **Starting branch head:** `7b406021728d39e202071e14d8fa1a53ba4a6ed1`
- **Dependencies:** `SOURCE-GATES-001` and `RUNTIME-ROUTER-001` complete
- **Blockers:** none identified for a provider-neutral synthetic first slice; host-specific behavior must be verified against current supported product capabilities before encoding promises

### Objective

Implement a deterministic provider-neutral connection orchestration contract for ordinary users. Given the selected service/provider intent, client-surface capabilities, current provider capability evidence, and runtime routing result, MIRA must determine the honest visible connection state and the next user/system action without exporting avoidable technical setup.

The contract must support two client classes:

1. **Product-owned UI** such as future Android/web surfaces, where MIRA can expose explicit service-level connection controls.
2. **Host-controlled UI** such as stock ChatGPT, where MIRA cannot assume arbitrary custom button rendering and must route ordinary-language intent to the closest supported native host/provider authorization flow.

### Acceptance criteria

1. Connection orchestration uses the existing `ConnectionState`, provider capability evaluation, and runtime router; it does not create a second connection/capability/routing truth model.
2. Client-surface capability is explicit and typed: product-owned connection controls versus host-controlled native connection flow.
3. Service/provider connection intent is explicit. A request to connect Google Calendar cannot silently connect or activate Gmail, Drive, another provider, or another MIRA service.
4. Product-owned presentation can deterministically expose **Connect**, **Connected**, **Reconnect**, **Needs attention**, **Unavailable**, and **Disconnect** behavior from existing capability/router truth.
5. Host-controlled presentation never promises MIRA-owned buttons. It emits an ordinary-user native-host/provider authorization step only when authorization/reauthorization is actually needed and otherwise proceeds to verification/routing or reports the bounded blocker.
6. Connect/reconnect planning never assumes provider consent succeeded. Post-consent capability discovery/verification is a distinct required step before Connected is possible.
7. **Connected** is only allowed when the operation/service's required capability gates are fresh/verified and routing selects an eligible lane. Authorization alone is insufficient.
8. **Disconnect** is explicit, scoped to the selected provider/service connection, and must not imply deleting provider data, revoking unrelated provider services, changing canonical data, or deactivating unrelated MIRA services. Actual provider revocation remains adapter/host-specific work.
9. Connection planning must never instruct ordinary Personal users to copy provider IDs, manually create Calendars/folders/resources, edit OAuth scopes, open Apps Script/developer consoles, paste code, run terminals, or provision external infrastructure when a supported native route exists.
10. One broken provider/service lane cannot poison an independently usable connection surface for another service/provider.
11. Provider preference and hard-provider requirements respect existing router semantics; the onboarding layer never silently substitutes a different provider.
12. The orchestration result includes bounded machine-readable next-action/reason data suitable for future Android/web rendering and stock-ChatGPT conversational guidance without making display text canonical state.
13. No credentials, tokens, private provider payloads, personal production identifiers, or live production data appear in public code/tests.
14. Synthetic tests cover at minimum: fresh Connect, authorized-but-unverified, fully Connected, expired/revoked Reconnect, verification failure Needs attention, unsupported Unavailable, policy/router block, host-controlled flow, product-owned flow, explicit Disconnect semantics, provider no-substitution, and unrelated-lane isolation.
15. Production code ownership/direct-verification evidence is updated if a new module is added.
16. Exact-head CI must pass before merge; merge uses expected-head protection followed by remote `main` readback and post-merge CI verification.

### Explicitly deferred

- actual OAuth/provider authorization invocation;
- provider-specific live discovery/binding adapters;
- real Google Calendar/Gmail/Drive write/readback;
- arbitrary custom button rendering inside stock ChatGPT;
- full Google multi-service bootstrap under `GOOGLE-BOOTSTRAP-001`;
- full browser install/upgrade/recovery under `NONTECH-INSTALL-001`;
- MIRA service composition/activation changes;
- Microsoft/Apple provider adapters;
- Android client/UI implementation;
- legacy production migration.

## Previous packet closure evidence

M2-M0-027 / `RUNTIME-ROUTER-001` is fully lifecycle-reconciled. PR #86 merged implementation at `565c37691f81b15d31bb46266da73f868f3dba26`; final PR head `9266d07f482fabc098bdd9da48fa243a6da2deb2` passed CI `33473329690`; post-merge main CI `33473362976` is green; remote `main` readback confirms `mira/runtime_router.py`. Closure PR #87 merged at `7b406021728d39e202071e14d8fa1a53ba4a6ed1`; post-merge CI `33473606399` is green.

## Android preserved resume point

Android remains M2-M1 and is paused, not discarded.

- `ANDROID-COMMAND-BOUNDARY-001`: provider-neutral sequencing plus synthetic Google Workspace queued-writer proof is complete from PRs #54/#55; live isolated Google worker proof remains pending.
- `ANDROID-CLIENT-CORE-001` follows that live proof and owns scoped/revocable identity, OS-protected credentials, bounded reads/commands, replay-safe offline queue, reconnect/cursor sync, conflict handling, and exact server readback.
- `ANDROID-SYNC` then proves Android mutation and stock-ChatGPT readback against the same canonical authority.
- There is still no MIRA 2.0 Android UI implementation.

## Exact next action / resume point

1. Inventory existing `onboarding.py`, `service_state.py`, `runtime_router.py`, native Google/Workspace adapters, relevant tests, distribution/instruction assumptions, and code ownership before adding a new module.
2. Verify current stock-ChatGPT provider/app connection capabilities from authoritative OpenAI product documentation before encoding host-controlled behavior.
3. Reuse existing connection/capability/router semantics directly; do not create duplicate truth.
4. Implement the smallest pure orchestration/presentation layer and synthetic tests.
5. Update code ownership only if a new production module is added.
6. Run full repository CI in a bounded PR, require exact-head green, merge with expected-head protection, verify remote `main`, and verify post-merge CI.
7. Reconcile `PROVIDER-ONBOARD-001` evidence honestly. Provider-neutral orchestration completion must not be mislabeled as live provider authorization proof.

## Recovery protocol

Read this file first, then `FEATURES.md`, `BACKLOG.md`, `ROADMAP.md`, and `PRODUCT_INVARIANTS.md`. Active work is `M2-M0-028` / `PROVIDER-ONBOARD-001` on `integration/m0-028-provider-onboarding`, based on clean green `main` SHA `7b406021728d39e202071e14d8fa1a53ba4a6ed1`. Resume by inventorying the existing onboarding/service/capability/router/native-host seams and verifying current stock-ChatGPT connection capabilities. Do not reconstruct provider or Android behavior from conversational memory.