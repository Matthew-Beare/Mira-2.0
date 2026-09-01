# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and exact recovery state.

## Product direction

Default Personal MIRA is stock ChatGPT + Google Workspace with no external infrastructure prerequisite. Ordinary-user provider setup must be intent-first and as close to one-click as the host/provider safely permits. Product-owned clients expose obvious connection controls; stock ChatGPT uses the closest supported native host/provider flow. Manual resource creation, copied IDs, OAuth-scope editing, Apps Script/developer-console work, pasted code, terminal setup, Linux, SQL, Cloud Run, or paid OpenAI API usage are not prerequisites for the default Personal path when software can route around them.

Connecting a provider, proving provider capabilities, routing an operation, and activating a MIRA service remain separate truths. Android remains paused while no-app Personal MIRA becomes genuinely usable.

Every work session begins and ends by checking `CURRENT_WORK.md`, `FEATURES.md`, `BACKLOG.md`, `ROADMAP.md`, and applicable product invariants.

## Session-start alignment verification — 2026-09-01

### `FEATURES.md`

- `SOURCE-001` independent read/write/remote-readback capability truth is implemented and consumed by the router.
- `PROVIDER-001` provider-neutral routing from observed evidence is implemented by M2-M0-027.
- `PROVIDER-002` remains the next user-facing provider-onboarding requirement: native Connect flow, automatic discovery/binding/verification, and no avoidable technical setup.
- `ONBOARD-006` preserves browser-only nontechnical Personal setup.
- `RECOVERY-002` remains enforced through per-lane routing failure isolation.

### `BACKLOG.md`

- `SOURCE-GATES-001` is complete in M2-M0-026.
- `RUNTIME-ROUTER-001` is complete in M2-M0-027 / PR #86; this closure branch reconciles its lifecycle row to the demonstrated merge/readback/CI evidence.
- `PROVIDER-ONBOARD-001` now has all direct prerequisites complete and is the highest-leverage ordinary-user provider hardening item for the seamless connection requirement.
- `SOURCE-LANES-001`, `SERVICE-COMPOSE-001`, `DISCOVERY-CORE-001`, and `MIRA-SKILL-001` also consume router truth later but do not outrank the accepted ordinary-user Connections vertical for M2-M0.5.
- Android remains separately preserved and paused.

### `ROADMAP.md`

- M2-M0.5 continues to prioritize useful ordinary-user no-app Personal MIRA before Android.
- Seamless provider onboarding is now unblocked by capability gates and runtime routing.
- M2-M1 remains paused at the live isolated Google queued-writer proof resume point.

### Direction result

**ALIGNED.** Close M2-M0-027 at verified evidence and select `PROVIDER-ONBOARD-001` as the next bounded packet unless closure CI exposes an integrity failure. Do not silently expand the closure into live provider authorization, provider mutation, Android, Microsoft/Apple adapters, or legacy production writes.

## Active packet

### `M2-M0-027` — Provider-neutral runtime capability router — closure checkpoint

- **Primary work:** `RUNTIME-ROUTER-001`
- **Primary features:** `PROVIDER-001`, `SOURCE-001`
- **Related invariants/features:** `PROVIDER-002`, `ONBOARD-006`, `RECOVERY-002`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Implementation branch:** `integration/m0-027-runtime-router`
- **Closure branch:** `governance/m0-027-closure`
- **Base/main SHA:** `13503070182ce7eddad3ff17892ffb284b968a24`
- **PR:** #86 merged
- **Final PR head:** `9266d07f482fabc098bdd9da48fa243a6da2deb2`
- **Final exact-head CI:** `33473329690` green
- **Merge/main SHA:** `565c37691f81b15d31bb46266da73f868f3dba26`
- **Post-merge main CI:** `33473362976` green
- **Remote main readback:** `mira/runtime_router.py` present on `main`
- **Blockers:** none; only lifecycle/closure reconciliation remains on this branch

### Completed objective

M2-M0-027 implements a pure provider-neutral runtime router over the existing M2-M0-026 capability evidence model. It selects exactly one eligible runtime/provider lane or fails closed with deterministic machine-readable reasons, while keeping routing separate from authorization, provider I/O, canonical mutation, and service activation.

### Durable implementation evidence

- New `mira/runtime_router.py` is independently visible on remote `main`.
- Route request, runtime candidate, policy/approval, candidate decision, and top-level result shapes are typed.
- Every operation carries explicit required SOURCE-001 gates; read, write, and remote readback remain independent.
- Capability evaluation reuses `ProviderCapabilitySnapshot` and `evaluate_provider_capability`; no second authorization/capability state model was created.
- Policy approval and opaque data-classification constraints can block otherwise capable lanes before provider capability inspection.
- Hard provider requirements never silently substitute another provider; soft provider preferences only rank otherwise eligible candidates.
- Selection is deterministic across input order using provider preference, explicit numeric priority, lane ID, and runtime ID.
- Invalid/future capability evidence is isolated to its candidate and does not poison an independently valid lane.
- Malformed router decision timestamps fail as router validation errors rather than being misreported as provider capability failures.
- Candidate decisions retain the policy ID used for routing provenance.
- Router code performs no provider authorization, discovery, I/O, canonical-state mutation, or service activation.
- Direct synthetic tests cover valid selection, read-only/write rejection, failed readback, revoked/stale evidence, policy denial, classification denial, approval-required state, deterministic ordering, preferred-provider ranking, hard-provider no-substitution, hard-provider/soft-preference conflict, broken-lane isolation, service mismatch, empty candidates, malformed timestamps, duplicate lanes/preferences, and secret-free public shapes.
- `runtime-capability-router` code ownership is registered separately from managed runtime assembly and durable service state.
- Final PR-head CI `33473329690` passed all repository gates/tests.
- Expected-head protected PR #86 merge succeeded at `565c37691f81b15d31bb46266da73f868f3dba26`.
- Post-merge `main` CI `33473362976` passed every gate/test.
- No live Personal provider resource was mutated.

### Evidence ceiling

This packet does not claim live provider discovery/authorization, stock-ChatGPT connection invocation, provider-specific runtime discovery, user-facing connection controls, Calendar/Gmail/Drive mutation/readback, service activation, Microsoft/Apple provider proof, or Android behavior.

## Next selected work

`PROVIDER-ONBOARD-001` is the expected next packet after this closure. Its bounded first slice should consume capability + router truth and define the ordinary-user connection orchestration/presentation contract for product-owned clients and stock-ChatGPT host-controlled flows without pretending MIRA can render arbitrary host UI or bypass provider-native authorization.

The required user experience remains:

- obvious service-level Connect actions where MIRA owns the client UI;
- plain-language connection intent when stock ChatGPT owns the host UI;
- direct native host/provider authorization rather than settings treasure hunts;
- automatic post-consent capability discovery, resource/scope binding, and exact verification;
- Connected only after required capability evidence is verified;
- deterministic Reconnect / Needs attention / Unavailable states from the existing capability model;
- explicit Disconnect that does not silently delete provider data or activate/deactivate unrelated services;
- no avoidable copied IDs, manually created Calendars, scope editing, Apps Script, developer-console work, pasted code, or terminal setup.

## Android preserved resume point

Android remains M2-M1 and is paused, not discarded.

- `ANDROID-COMMAND-BOUNDARY-001`: provider-neutral sequencing plus synthetic Google Workspace queued-writer proof is complete from PRs #54/#55; live isolated Google worker proof remains pending.
- `ANDROID-CLIENT-CORE-001` follows that live proof and owns scoped/revocable identity, OS-protected credentials, bounded reads/commands, replay-safe offline queue, reconnect/cursor sync, conflict handling, and exact server readback.
- `ANDROID-SYNC` then proves Android mutation and stock-ChatGPT readback against the same canonical authority.
- There is still no MIRA 2.0 Android UI implementation.

## Exact next action / resume point

1. Run closure CI with `BACKLOG.md` reconciled to PR #86 evidence and this closure checkpoint.
2. Merge the bounded closure PR only with exact-head green CI and expected-head protection; verify remote `main` readback and post-merge CI.
3. Create `M2-M0-028` for `PROVIDER-ONBOARD-001` from that clean main SHA.
4. Inventory existing onboarding, service-state, native-host/Workspace connection assumptions, and current product capabilities before adding new production code.
5. Implement only the smallest provider-neutral connection orchestration/presentation contract required to consume capability/router truth. Provider-specific live authorization adapters remain separate bounded work unless required for the first honest vertical.
6. Do not resume Android merely because its status was discussed.

## Recovery protocol

Read this file first, then `FEATURES.md`, `BACKLOG.md`, `ROADMAP.md`, and `PRODUCT_INVARIANTS.md`. M2-M0-027 implementation is merged at `565c37691f81b15d31bb46266da73f868f3dba26`; final PR-head CI `33473329690` and post-merge main CI `33473362976` are green; `mira/runtime_router.py` is present on remote `main`. Active work is closure/lifecycle reconciliation on `governance/m0-027-closure`. After closure merges, start `M2-M0-028` / `PROVIDER-ONBOARD-001`; do not reconstruct provider or Android state from conversation memory.