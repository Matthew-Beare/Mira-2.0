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
- **Packet:** `docs/work-packets/M2-M1-036.md`.
- **Current status:** active implementation packet. M2-M1-035 is integration-verified on exact merge SHA; this packet begins the first bounded user-facing Studio composition seam.
- **Owned implementation surfaces:** new `mira/studio.py`, new `tests/test_studio.py`, packet doc, branch-local `CURRENT_WORK.md`, and one narrow code-ownership registration.
- **Shared/high-contention surfaces:** `BACKLOG.md` lifecycle reconciliation may be updated narrowly; no Google Workspace/Sheets, finance, Android, People Discovery, provider credentials/endpoints, live source adapter, or live share registry is owned here.

## Prior packet closeout

`M2-M1-035` / `FEATURE-SHARE-001` merged through PR #150 at exact merge SHA `16c5646e05edb62b3878ade602a3287d12c064f4`. Post-merge CI #588 / run `34561318036` passed end-to-end, and exact merge-SHA `python` plus trusted-runner `preflight` checks both passed. M2-M1-034 + M2-M1-035 therefore integration-verify the provider-neutral sanitized package and optional publication/import transport seams. No live provider publication/import or imported activation is claimed.

`M2-M1-031` through `M2-M1-033` implemented the bounded Studio skill-builder engine: competitive candidate evidence/review planning, preview/test/rollback/approval planning, and explicit approved activation/rollback execution through injected source adapters. Exact live model invocation and provider-specific source mutation remain separate evidence.

## Objective

Create the first integrated user-facing MIRA Studio orchestration surface over the already-merged skill-builder, activation and sharing boundaries. The surface must make the user's current Studio state and next permissible action explicit for preference/workflow/feature changes while preserving hard separation between preview/review, activation approval, rollback and optional sharing/import review.

This packet must not invoke a model, create Git branches, select a provider, call a live source/share store, install imported behavior, silently activate anything, infer approval, or expand into final graphical/browser UX. It is a provider-neutral product orchestration/state surface that composes existing proven contracts and remains fully deterministic/testable with supplied evidence.

## Acceptance criteria

1. A bounded Studio session identifies one exact packet/work/change and one change kind, with a human-readable objective and declared feature/dependency context.
2. The surface deterministically reports lifecycle phase, blockers, readiness and exactly the next user-visible action from supplied evidence.
3. Preview/test/rollback evidence is evaluated through the existing `studio_competition` staged-change boundary rather than duplicated.
4. Activation is never offered as executable authority without an explicit exact approval-bound `StudioActivationPlan`.
5. Applied/blocked/recovery-required activation and rollback receipts map to truthful user-visible state without manufacturing success.
6. Optional sharing remains separate from activation. Share/import material cannot grant install/source-mutation/activation authority.
7. Imported feature material always enters a review-required state and cannot silently become an activation plan.
8. The surface contains no provider credentials/endpoints, shell commands, model paths, private runner labels or raw private identities.
9. Deterministic replay of the same supplied evidence yields the same surface state and next-action decision.
10. Direct adversarial tests cover phase transitions, missing/failed evidence, stale approval, activation recovery, rollback readiness, sharing separation and inert import review.
11. Code ownership remains bounded and repository CI must pass at exact head before merge.

## Session-start alignment verification — 2026-09-11

### `FEATURES.md`

`STUDIO-001` requires an integrated guided user-facing surface over bounded custom features/workflows/preferences with preview/test/rollback, source provenance and optional sanitized sharing without silent imported activation. `DEV-004` and `DIST-001` provide the bounded creation and controlled-sharing foundations.

### `BACKLOG.md`

`MIRA-STUDIO-001` is the user-visible vertical depending on `SKILL-BUILDER-001` and `FEATURE-SHARE-001`. M2-M1-031 through M2-M1-033 integration-verify the bounded skill-builder seams, while M2-M1-034 through M2-M1-035 integration-verify sanitized share packaging and transport. Their backlog lifecycle text is stale and will be reconciled narrowly in this packet.

### `ROADMAP.md`

The roadmap requires repeated bounded user-visible progress rather than another infrastructure mega-packet. This packet composes already-proven provider-neutral seams into a truthful Studio product surface without introducing local/server/provider prerequisites.

### Reuse and boundary review

- `mira.studio_competition` remains authority for candidate/staged-change evidence evaluation and approval-bound activation planning.
- `mira.studio_activation` remains authority for approved activation/rollback execution receipts through injected source adapters.
- `mira.feature_share` remains authority for sanitized package validation and inert import inspection.
- `mira.feature_share_transport` remains authority for optional publication/import transport with exact readback.
- `mira.studio` will own only the guided product-level lifecycle projection/orchestration over those existing contracts.

### Direction result

ALIGNED

## Exact next action / resume point

1. Add the deterministic Studio session/surface model and adversarial tests.
2. Register one bounded `studio-guided-surface` ownership component.
3. Reconcile `SKILL-BUILDER-001` and `FEATURE-SHARE-001` lifecycle status in `BACKLOG.md`, and mark `MIRA-STUDIO-001` active only within this packet.
4. Run repository CI at exact branch head.
5. Review diff/overlap, close documentation, rerun exact-head CI, then merge only with expected-head protection and verify exact post-merge CI.

## Evidence ceiling

M2-M1-036 begins from integration-verified main `16c5646e05edb62b3878ade602a3287d12c064f4`. No user-facing Studio composition implementation evidence is claimed yet.

## Recovery protocol

Resume from branch `work/m2-m1-036-studio-guided-surface`, base `16c5646e05edb62b3878ade602a3287d12c064f4`, this file and `docs/work-packets/M2-M1-036.md`. Git, not chat, is authoritative.
