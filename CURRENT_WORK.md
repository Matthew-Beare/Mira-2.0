# MIRA 2.0 CURRENT WORK

Git is authoritative. This branch records exactly one active packet. Multiple other packet branches may be active repository-wide under `docs/CONCURRENT_WORK_POLICY.md`.

## Active packet

### `M2-M1-036` — Studio guided user-facing orchestration surface

- **Primary work:** `MIRA-STUDIO-001`.
- **Primary features:** `STUDIO-001`, `DEV-004`, `DIST-001`.
- **Related invariants/features:** `DEV-002`, `DEV-005`, `DEV-006`, `DEV-007`, `SOURCE-001`, `PROVIDER-001`, `RECOVERY-002`.
- **Repository:** `Matthew-Beare/Mira-2.0`.
- **Branch:** `work/m2-m1-036-studio-guided-surface`.
- **Base SHA:** `16c5646e05edb62b3878ade602a3287d12c064f4`.
- **Exact implementation/ownership head:** `811c66302c1ad37af6e6ab187c2d8a77b4bf1f0c`.
- **Packet:** `docs/work-packets/M2-M1-036.md`.
- **Pull request:** `#151` (draft pending final documentation-closeout CI).
- **Current status:** implementation, 21 direct adversarial tests, bounded ownership and repository-wide exact-head CI are green. Documentation closeout has been recorded and therefore requires one final exact-head CI before merge.
- **Owned implementation surfaces:** `mira/studio.py`, `tests/test_studio.py`, packet doc, branch-local `CURRENT_WORK.md`, and bounded `studio-guided-surface` registration in `project/code_ownership.json`.
- **Shared/high-contention surfaces:** no Google Workspace/Sheets, finance, Android, People Discovery, provider credentials/endpoints, live source adapter, live share registry or `BACKLOG.md` row is mutated by this packet.

## Prior packet closeout

`M2-M1-035` / `FEATURE-SHARE-001` merged through PR #150 at exact merge SHA `16c5646e05edb62b3878ade602a3287d12c064f4`. Post-merge CI #588 / run `34561318036` passed end-to-end, and exact merge-SHA `python` plus trusted-runner `preflight` checks passed. M2-M1-034 + M2-M1-035 therefore integration-verify the provider-neutral sanitized package and optional publication/import transport seams. No live provider publication/import or imported activation is claimed.

`M2-M1-031` through `M2-M1-033` provide the bounded Studio skill-builder engine: competitive candidate evidence/review planning, staged preview/test/rollback/approval planning, and explicit approved activation/rollback execution through injected source adapters. Exact live model invocation and provider-specific source mutation remain separate evidence.

## Objective

Create the first integrated user-facing MIRA Studio orchestration surface over the already-merged skill-builder, activation and sharing boundaries. The surface makes one bounded change's current state and next permissible user action explicit while preserving hard separation among preview/review, explicit activation approval, execution/rollback evidence and optional inert sharing/import review.

This packet does not invoke a model, create Git branches, choose a provider, call a live source/share store, install imported behavior, silently activate anything, infer approval, or implement final graphical/browser UX.

## Acceptance state

- Exact bounded Studio session identity and change kind/objective/feature/dependency context: **implemented**.
- Deterministic lifecycle phase, blockers, readiness and one next action: **implemented**.
- Existing `studio_competition.evaluate_staged_change()` remains readiness/approval authority: **implemented/reused**.
- Review-ready but unapproved changes remain approval-gated: **implemented**.
- Activation/rollback receipts bind back to exact approved plan and project APPLIED/BLOCKED/RECOVERY truthfully: **implemented**.
- Sharing remains optional and separate from activation: **implemented**.
- Imported material remains inert review-only material with install/source-mutation/activation authority false: **implemented**.
- Provider/runtime-sensitive execution fields are absent from the public product surface: **implemented/tested**.
- Deterministic replay of identical evidence: **implemented/tested**.
- Direct adversarial Studio surface suite: **21 tests committed**.
- Code ownership: **one bounded `studio-guided-surface` component registered and ownership gate verified**.
- CI #590 / run `34562064822` on exact implementation/ownership head `811c66302c1ad37af6e6ab187c2d8a77b4bf1f0c`: **PASS end-to-end**, including repository Python tests, work-session alignment and code-ownership gates.
- PR #151 at initial implementation review changed exactly five declared files: `CURRENT_WORK.md`, packet doc, `mira/studio.py`, `project/code_ownership.json`, and `tests/test_studio.py`.
- `BACKLOG.md` lifecycle rows for `SKILL-BUILDER-001`, `FEATURE-SHARE-001`, and `MIRA-STUDIO-001` remain stale and intentionally unmodified until M2-M1-036 has exact merged evidence; the next governance/Studio-selection packet owns that reconciliation rather than pre-crediting integration.
- Final documentation-closeout exact-head CI: **pending after this checkpoint commit**.
- Live model/provider/source/share execution and final graphical UX: **not claimed**.

## Session-start alignment verification — 2026-09-11

### `FEATURES.md`

`STUDIO-001` requires an integrated guided user-facing surface over bounded custom features/workflows/preferences with preview/test/rollback, source provenance and optional sanitized sharing without silent imported activation. `DEV-004` and `DIST-001` provide the bounded creation and controlled-sharing foundations.

### `BACKLOG.md`

`MIRA-STUDIO-001` is the user-visible vertical depending on `SKILL-BUILDER-001` and `FEATURE-SHARE-001`. Their implementation evidence is merged/test-verified but lifecycle text is stale. M2-M1-036 earns only the first integrated guided-surface slice; it does not pre-credit complete Studio UX.

### `ROADMAP.md`

The roadmap requires repeated bounded user-visible progress rather than another infrastructure mega-packet. This packet composes already-proven provider-neutral seams into a truthful Studio product surface without introducing local/server/provider prerequisites.

### Reuse and boundary review

- `mira.studio_competition` remains authority for candidate/staged-change evidence evaluation and approval-bound activation planning.
- `mira.studio_activation` remains authority for approved activation/rollback execution receipts through injected source adapters.
- `mira.feature_share` remains authority for sanitized package validation and inert import inspection.
- `mira.feature_share_transport` remains authority for optional publication/import transport with exact readback.
- `mira.studio` owns only deterministic product-level lifecycle projection/orchestration over those existing contracts.

### Direction result

ALIGNED

## Exact next action / resume point

1. Run final exact-head repository CI on the documentation-closeout head created by this checkpoint.
2. Re-read current remote `main`, PR #151 exact head/mergeability and changed-file overlap.
3. If final exact-head CI is green and no incompatible main movement appeared, mark PR #151 ready and merge using expected-head protection.
4. Read back merged remote `main` and verify exact post-merge CI plus trusted-runner/preflight on the merge SHA before claiming integration verification.
5. Start the next bounded Studio/governance packet from that exact merge SHA to reconcile backlog lifecycle state and select the next user-visible Studio child.
6. Preserve the evidence ceiling: no live model invocation, provider/source/share execution, import install/activation or final graphical UX claim.

## Evidence ceiling

Implemented and repository-test verified at exact implementation/ownership head `811c66302c1ad37af6e6ab187c2d8a77b4bf1f0c`. Documentation-closeout exact-head CI and exact post-merge verification remain pending. No live model/provider/source/share execution, imported installation/activation or final graphical/browser UX is claimed.

## Recovery protocol

Resume from remote `main` `16c5646e05edb62b3878ade602a3287d12c064f4`, branch `work/m2-m1-036-studio-guided-surface`, PR #151, this file and `docs/work-packets/M2-M1-036.md`. Git, not chat, is authoritative.
