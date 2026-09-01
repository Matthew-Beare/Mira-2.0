# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and exact recovery state.

## Product direction

Default Personal MIRA is stock ChatGPT + Google Workspace with no external infrastructure prerequisite. Connecting apps must be as close to one-click as the host/provider safely permits. If software can create, discover, bind, verify, or route around technical setup, the user does not perform that setup. Provider-native authorization is acceptable unavoidable ceremony; copied IDs, manually created provider resources, OAuth-scope editing, Apps Script/developer-console work, pasted code, terminal setup, Linux, SQL, Cloud Run, or paid OpenAI API usage are not default Personal prerequisites when software can route around them.

Product-owned clients may expose obvious service-level controls such as **Connect Google Calendar**, **Connect Google Drive**, and **Connect Gmail**. Stock ChatGPT is host-controlled: MIRA must use the closest supported native ChatGPT/provider connection flow and must not promise arbitrary custom host UI that the product cannot render. Current OpenAI product capability allows relevant apps/plugins to be suggested in conversation and a first-use/install flow to prompt the user to connect; therefore ordinary-language connection intent should resolve the relevant supported integration and surface that native install/connect flow when the host exposes it rather than sending the user through settings.

Authorization, plugin/app installation, verified provider capability, runtime routing, connection presentation, and MIRA service activation remain separate truths. Android must later consume the same connection semantics rather than inventing another activation model.

Apple/iCloud remains required product direction but is not a pre-Android implementation blocker. Before Android, provider-neutral connection contracts must prove that Apple-shaped lanes fit without Google-specific assumptions; actual Apple/iCloud provider adapters remain separate work unless a hard dependency is discovered.

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
- Apple/iCloud support is required direction but explicitly not a blocker for the current Google-first Personal product.

### Direction result

**ALIGNED.** Implement the smallest provider-neutral connection orchestration/presentation contract that consumes existing capability and router truth. The first slice defines what connection state/action MIRA may honestly present and what next native-host/provider action is required. For host-controlled ChatGPT, that native action may include plugin/app discovery, installation/enabling, account connection, and provider consent when the host supports those steps. This packet does not itself execute OAuth/provider I/O or activate MIRA services.

## Active packet

### `M2-M0-028` — Ordinary-user provider connection orchestration

- **Primary work:** `PROVIDER-ONBOARD-001`
- **Primary features:** `PROVIDER-002`, `PROVIDER-001`, `SOURCE-001`
- **Related invariants/features:** `ONBOARD-006`, `SERVICE-001`, `RECOVERY-002`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `integration/m0-028-provider-onboarding`
- **Base/main SHA:** `7b406021728d39e202071e14d8fa1a53ba4a6ed1`
- **PR:** #88 open
- **Dependencies:** `SOURCE-GATES-001` and `RUNTIME-ROUTER-001` complete
- **Blockers:** no product blocker identified; PR #88 first CI failed only because this checkpoint used singular `Primary feature` instead of required `Primary features`

### Objective

Implement a deterministic provider-neutral connection orchestration contract for ordinary users. Given the selected service/provider intent, client-surface capabilities, current provider capability evidence, and runtime routing result, MIRA must determine the honest visible connection state and the next user/system action without exporting avoidable technical setup.

The contract supports two client classes:

1. **Product-owned UI** such as future Android/web surfaces, where MIRA can expose explicit service-level connection controls and provider-native flows.
2. **Host-controlled UI** such as stock ChatGPT, where MIRA cannot assume arbitrary custom button rendering and instead routes ordinary-language intent into the closest supported native plugin/app discovery/install/connect/authorization flow.

### Acceptance criteria

1. Connection orchestration uses the existing `ConnectionState`, provider capability evaluation, and runtime router; it does not create a second connection/capability/routing truth model.
2. Client-surface capability is explicit and typed: product-owned connection controls versus host-controlled native connection flow.
3. Service/provider connection intent is explicit. A request to connect Google Calendar cannot silently connect or activate Gmail, Drive, another provider, or another MIRA service.
4. Product-owned presentation can deterministically expose **Connect**, **Connected**, **Reconnect**, **Needs attention**, **Unavailable**, and **Disconnect** behavior from existing capability/router truth.
5. Host-controlled connection planning never promises MIRA-owned buttons. When the host supports app/plugin discovery or installation, an ordinary-language request such as “connect my calendar” must plan a native host flow that can resolve the relevant supported integration and surface its install/connect prompt; only unavoidable provider consent or workspace-admin approval remains for the user.
6. Connect/reconnect planning never assumes plugin installation or provider consent succeeded. Post-connection capability discovery/verification is a distinct required step before Connected is possible.
7. **Connected** is only allowed when the operation/service's required capability gates are fresh/verified and routing selects an eligible lane. Authorization alone is insufficient.
8. **Disconnect** is explicit, scoped to the selected provider/service connection, and must not imply deleting provider data, revoking unrelated provider services, changing canonical data, or deactivating unrelated MIRA services. Actual provider revocation remains adapter/host-specific work.
9. Connection planning must never instruct ordinary Personal users to copy provider IDs, manually create Calendars/folders/resources, edit OAuth scopes, open Apps Script/developer consoles, paste code, run terminals, or provision external infrastructure when a supported native route exists.
10. One broken provider/service lane cannot poison an independently usable connection surface for another service/provider.
11. Provider preference and hard-provider requirements respect existing router semantics; the onboarding layer never silently substitutes a different provider.
12. The orchestration result includes bounded machine-readable next-action/reason data suitable for future Android/web rendering and stock-ChatGPT conversational/tool guidance without making display text canonical state.
13. No credentials, tokens, private provider payloads, personal production identifiers, or live production data appear in public code/tests.
14. Synthetic tests cover fresh Connect, authorized-but-unverified, fully Connected, expired/revoked Reconnect, verification failure Needs attention, unsupported Unavailable, policy/router block, host-controlled native discovery/install/connect planning, product-owned flow, explicit Disconnect semantics, provider no-substitution, unrelated-lane isolation, and an Apple-shaped Calendar lane proving the contract is not Google-specific. Host-controlled Apple with no supported native connector must fail honestly without substitution or manual technical setup.
15. Production code ownership/direct-verification evidence is updated for the new module.
16. Exact-head CI must pass before merge; merge uses expected-head protection followed by remote `main` readback and post-merge CI verification.

### Explicitly deferred

- actual plugin installation or plugin-directory invocation by repository code;
- actual OAuth/provider authorization invocation;
- provider-specific live discovery/binding adapters;
- real Google Calendar/Gmail/Drive write/readback in this packet;
- arbitrary custom button rendering inside stock ChatGPT;
- full Google multi-service bootstrap under `GOOGLE-BOOTSTRAP-001`;
- full browser install/upgrade/recovery under `NONTECH-INSTALL-001`;
- MIRA service composition/activation changes;
- Microsoft/Apple live provider adapters;
- Android client/UI implementation;
- legacy production migration.

## Current implementation evidence on PR #88

- `mira/provider_onboarding.py` implements the pure provider-neutral planner over existing capability/router truth.
- Host-native Connect now emits a `START_NATIVE_CONNECTION_FLOW` action with `host_native_discover_install_connect` reason material rather than modeling the host flow as OAuth-only.
- Host-native Reconnect is separately modeled as a native reconnection flow.
- Product-owned flows remain provider-native and use the same connection state/action contract.
- `PRODUCT_INVARIANTS.md` now durably requires conversational plugin/app resolution and native install/connect prompting when the host exposes it.
- `tests/test_provider_onboarding.py` includes synthetic Apple contract coverage and host-no-Apple-connector failure behavior.
- `project/code_ownership.json` registers `provider-onboarding-orchestration` separately from capability routing and durable service state.
- PR #88 first CI `33474477457` reached compile, feature registry, lifecycle ledger, and distribution gates successfully; it failed at work-session alignment solely because this checkpoint used the singular field label. Code ownership and unit tests were skipped after that gate, so no test-verification claim is made yet.

## Previous packet closure evidence

M2-M0-027 / `RUNTIME-ROUTER-001` is fully lifecycle-reconciled. PR #86 merged implementation at `565c37691f81b15d31bb46266da73f868f3dba26`; final PR head `9266d07f482fabc098bdd9da48fa243a6da2deb2` passed CI `33473329690`; post-merge main CI `33473362976` is green; remote `main` readback confirms `mira/runtime_router.py`. Closure PR #87 merged at `7b406021728d39e202071e14d8fa1a53ba4a6ed1`; post-merge CI `33473606399` is green.

## Android preserved resume point

Android remains M2-M1 and is paused, not discarded.

- `ANDROID-COMMAND-BOUNDARY-001`: provider-neutral sequencing plus synthetic Google Workspace queued-writer proof is complete from PRs #54/#55; live isolated Google worker proof remains pending.
- `ANDROID-CLIENT-CORE-001` follows that live proof and owns scoped/revocable identity, OS-protected credentials, bounded reads/commands, replay-safe offline queue, reconnect/cursor sync, conflict handling, and exact server readback.
- `ANDROID-SYNC` then proves Android mutation and stock-ChatGPT readback against the same canonical authority.
- There is still no MIRA 2.0 Android UI implementation.

## Exact next action / resume point

1. Re-run PR #88 CI after this work-session alignment correction.
2. Fix any actual code/ownership/test failures rather than weakening tests or product invariants.
3. Require exact-head green CI, merge with expected-head protection, verify remote `main`, and verify post-merge CI.
4. Reconcile `PROVIDER-ONBOARD-001` evidence honestly. Provider-neutral planning completion must not be mislabeled as actual live plugin installation/provider authorization proof.
5. Select the smallest live stock-ChatGPT native connection-flow proof next if required to prove the host executor seam, then complete the preserved live isolated Google queued-writer proof before Android mutation work resumes.
6. Keep Apple/iCloud as a first-class provider-neutral contract lane without making full Apple adapter implementation a pre-Android blocker.

## Recovery protocol

Read this file first, then `FEATURES.md`, `BACKLOG.md`, `ROADMAP.md`, and `PRODUCT_INVARIANTS.md`. Active work is `M2-M0-028` / `PROVIDER-ONBOARD-001` on `integration/m0-028-provider-onboarding`, based on clean green main SHA `7b406021728d39e202071e14d8fa1a53ba4a6ed1`; PR #88 is open. The first PR CI failed only at the checkpoint field label before ownership/tests ran. Resume by rerunning exact-head CI after this correction, then fix any substantive failures. Do not reconstruct provider or Android behavior from conversation memory.