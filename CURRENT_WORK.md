# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and exact recovery state.

## Product direction

Default Personal MIRA is stock ChatGPT + Google Workspace with no external infrastructure prerequisite. Ordinary-language connection intent should use the closest supported native ChatGPT app/plugin/provider flow; normal users do not perform copied-ID, scope-editing, Apps Script, developer-console, terminal, Linux, SQL, Cloud Run, or paid OpenAI API setup when software can route around it.

Authorization, plugin/app installation, verified provider capability, runtime routing, connection presentation, and MIRA service activation remain separate truths. Android must consume the same semantics. Apple/iCloud remains required direction and must fit the provider-neutral contracts, but full Apple adapter implementation is not a pre-Android blocker.

Every work session begins and ends by checking `CURRENT_WORK.md`, `FEATURES.md`, `BACKLOG.md`, `ROADMAP.md`, and applicable product invariants.

## Session-start alignment verification — 2026-09-01 closure

### `FEATURES.md`

- `PROVIDER-002` remains the ordinary-user provider onboarding feature and M2-M0-028 has implemented its provider-neutral connection-planning slice.
- `PROVIDER-001` and `SOURCE-001` remain the canonical routing/capability truth consumed by that slice.
- `ONBOARD-006`, `SERVICE-001`, and `RECOVERY-002` remain preserved invariants for browser-only ordinary-user setup, activation separation, and failure isolation.

### `BACKLOG.md`

- `PROVIDER-ONBOARD-001` still requires lifecycle reconciliation from queued to the verified PR #88 implementation evidence; this closure packet performs that governance work and must not overclaim live plugin/provider execution.
- `ANDROID-COMMAND-BOUNDARY-001` remains partial with only its live isolated Google worker proof outstanding.
- `ANDROID-CLIENT-CORE-001` remains queued behind that proof.
- No unrelated queued feature outranks the bounded stock-ChatGPT host-execution proof plus live writer proof before Android.

### `ROADMAP.md`

- M2-M0.5 has already delivered a usable no-app foundation and multiple canonical verticals; provider connection hardening is now at closure.
- M2-M1 remains paused only until the live isolated Google queued-writer proof is complete.
- Apple/iCloud support is required direction but explicitly not a blocker for the current Google-first Personal path.

### Direction result

**ALIGNED.** Close M2-M0-028 at its demonstrated provider-neutral evidence ceiling, then prove the stock-ChatGPT native host connection executor seam, then finish the existing live queued-writer proof and start Android client core. Do not insert unrelated feature growth ahead of Android.

## Active packet

### `M2-M0-028` — Ordinary-user provider connection orchestration — closure checkpoint

- **Primary work:** `PROVIDER-ONBOARD-001`
- **Primary features:** `PROVIDER-002`, `PROVIDER-001`, `SOURCE-001`
- **Related invariants/features:** `ONBOARD-006`, `SERVICE-001`, `RECOVERY-002`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Implementation branch:** `integration/m0-028-provider-onboarding`
- **Closure branch:** `governance/m0-028-closure`
- **Base/main SHA:** `7b406021728d39e202071e14d8fa1a53ba4a6ed1`
- **Final PR head:** `ce58d0591213cca616c55a32b713d402385fe3e1`
- **Implementation PR:** #88 merged
- **Merge/main SHA:** `a45dcea4247ff4df2588601277af6f65adb02be8`
- **Exact-head CI:** `33474543309` green
- **Post-merge main CI:** `33474573636` green
- **Remote main readback:** `mira/provider_onboarding.py` present on `main`
- **Blockers:** none for packet closure; broader live host invocation/provider authorization remains separate work

## Completed objective

M2-M0-028 implemented and test-verified the provider-neutral ordinary-user connection orchestration contract over existing capability and runtime-routing truth.

Durable evidence:

- `mira/provider_onboarding.py` is on remote `main` and remains a pure planning layer with no provider I/O or service activation.
- Product-owned and host-controlled connection surfaces are typed separately.
- Host-controlled connection intent can plan native app/plugin discovery/install/connect flow rather than exporting settings or technical setup to the user.
- Connect, Connected, Reconnect, Needs attention, Unavailable, and Disconnect semantics reuse canonical capability/router truth.
- Connected requires fresh verified gates plus an eligible selected runtime lane; installation or consent alone cannot create readiness.
- Disconnect remains connection-scoped and cannot imply provider-data deletion, unrelated-provider revocation, canonical mutation, or service activation changes.
- Hard provider requirements do not silently substitute another provider.
- Broken unrelated lanes remain isolated.
- Synthetic Apple-shaped Calendar coverage proves the orchestration contract is not Google-specific; lack of a supported host-native Apple connector fails honestly rather than substituting Google or exporting technical setup.
- `PRODUCT_INVARIANTS.md` now requires ordinary-language intent to resolve supported host-native app/plugin flow when available.
- `project/code_ownership.json` registers the new orchestration module separately from capability routing and durable service state.
- PR #88 final exact-head CI `33474543309` passed compile, feature registry, product ledger, Personal distribution, work-session alignment, code ownership, Python tests, and Workspace Apps Script tests.
- Expected-head merge completed at `a45dcea4247ff4df2588601277af6f65adb02be8`.
- Post-merge main CI `33474573636` is green and remote main readback confirms the implementation.
- No live provider account, Calendar, Gmail, Drive resource, or legacy production state was mutated.

## Evidence ceiling

This packet does not claim that repository Python can invoke ChatGPT's host UI, install a plugin, perform OAuth, discover live provider resources, or prove a real provider write. It proves the connection decision/orchestration contract and current host-flow semantics. Live host execution and live provider evidence remain separate.

## Re-ranked next work

Feature growth before Android is now frozen except for hard proof dependencies.

1. **Next bounded packet:** prove the stock-ChatGPT host executor seam for ordinary-language connection intent. Verify that a supported service can be discovered through the current ChatGPT plugin/app mechanism and that the host can surface its native install/connect action without manual settings or technical setup. This proof must not silently install or authorize an account without user consent and must not use protected production provider state as a test fixture.
2. **Then:** complete the already-built `ANDROID-COMMAND-BOUNDARY-001` live isolated Google queued-writer proof. Synthetic sequencing/worker behavior is already complete in PRs #54/#55.
3. **Then:** start `ANDROID-CLIENT-CORE-001`. Do not insert Apple implementation, unrelated provider expansion, finance, inventory enhancements, or cosmetic work ahead of Android unless a hard dependency or integrity blocker is discovered.

## Android preserved resume point

- `ANDROID-COMMAND-BOUNDARY-001`: provider-neutral sequencer + synthetic Google Workspace queued-worker proof complete; live isolated Google worker proof pending.
- `ANDROID-CLIENT-CORE-001`: queued immediately after that live proof; owns scoped/revocable client identity, OS-protected credentials, bounded reads/commands, replay-safe offline queue, reconnect/cursor sync, conflict handling and exact server readback.
- `ANDROID-SYNC`: then proves Android mutation and stock ChatGPT readback from the same canonical authority.
- Android UI implementation has not started yet.

## Exact next action / resume point

1. Reconcile `BACKLOG.md` so `PROVIDER-ONBOARD-001` records PR #88 implementation/test evidence without falsely claiming live host/plugin/provider execution.
2. Run closure CI, merge only from exact-head green, verify remote `main`, and verify post-merge CI.
3. Create the next bounded host-execution packet from clean main. Assign a stable work ID and record the host-native discovery/install/connect acceptance contract before implementation/proof.
4. Use current ChatGPT Plugin Management capability for live non-destructive discovery proof. Do not trigger actual provider authorization unless explicit user action is genuinely required by the native host consent UI.
5. After host execution proof closes, resume `ANDROID-COMMAND-BOUNDARY-001` live isolated Google worker proof, then Android client core.

## Recovery protocol

Read this file first, then `FEATURES.md`, `BACKLOG.md`, `ROADMAP.md`, and `PRODUCT_INVARIANTS.md`. M2-M0-028 implementation is merged at `a45dcea4247ff4df2588601277af6f65adb02be8`; final exact-head CI `33474543309` and post-merge CI `33474573636` are green; remote main contains `mira/provider_onboarding.py`. Active work is lifecycle closure on `governance/m0-028-closure`. Do not expand into unrelated feature work before the host-execution proof and live queued-writer proof are complete.