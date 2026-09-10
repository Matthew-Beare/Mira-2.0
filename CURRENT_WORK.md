# MIRA 2.0 CURRENT WORK

Git is authoritative. This branch records exactly one active packet. Multiple other packet branches may be active repository-wide under `docs/CONCURRENT_WORK_POLICY.md`.

## Active packet

### `M2-M1-032` — Studio staged preview, approval and rollback planning

- **Primary work:** `SKILL-BUILDER-001`.
- **Primary features:** `STUDIO-001`, `DEV-004`.
- **Related invariants/features:** `DEV-001`, `DEV-002`, `DEV-005`, `DEV-006`, `DIST-001`, `SOURCE-001`, `RECOVERY-002`.
- **Repository:** `Matthew-Beare/Mira-2.0`.
- **Branch:** `work/m2-m1-032-studio-staged-lifecycle`.
- **Base SHA:** `be38234a49c60fa28d478dc64132531767cb73c1`.
- **Exact implementation head:** `ebc2bbdddc0b63b54fa51be2803518a2c42276f0`.
- **Packet:** `docs/work-packets/M2-M1-032.md`.
- **Pull request:** `#147` (draft pending final documentation-closeout CI).
- **Owned implementation surfaces:** `mira/studio_competition.py`, `tests/test_studio_staged_lifecycle.py`, packet doc, branch-local `CURRENT_WORK.md`.
- **Shared/high-contention surfaces:** `mira/studio_competition.py` is the existing `studio-competitive-development` component merged by M2-M1-031. No active open PR owns that implementation path. No `FEATURES.md`, `BACKLOG.md`, `ROADMAP.md`, `PROJECT_INSTRUCTIONS.md`, Google Workspace/Sheets, People Discovery, provider, private-runner or local-compute implementation surface is modified by this packet.
- **Current status:** implementation and adversarial tests complete; exact implementation-head CI #566 / run `34417064924` PASS end-to-end; final documentation closeout now requires its own exact-head CI before merge.

## Objective

Extend the provider-neutral Studio development engine with a fail-closed staged-change lifecycle that binds a reviewed proposal to its packet/work identity, reviewed feature scope, exact candidate provenance, declared contracts, preview evidence, exact-proposal test evidence, a deterministic rollback anchor and explicit human approval before producing any activation plan. The packet plans activation/rollback material only. It does not activate a feature, mutate runtime state, execute rollback, call a provider/model, merge Git, publish/import a feature or create final Studio UX.

## Acceptance state

- M2-M1-031 competitive development evidence/planning: **merged at `be38234a49c60fa28d478dc64132531767cb73c1`; exact-merge CI checks PASS**.
- SKILL-BUILDER prerequisites `FEATURE-REGISTRY-001` and `SOURCE-GATES-001`: **complete/CI-enforced**.
- M2-M1-032 branch: **created from exact verified main `be38234a49c60fa28d478dc64132531767cb73c1`**.
- Declared staged-change contract bound to reviewed packet/work identity, reviewed feature scope and exact base/proposed/source provenance: **implemented and adversarially tested**.
- Reviewed competition decision required before staging; absent or candidate-provenance-mismatched integration plans fail closed: **implemented and adversarially tested**.
- Feature-scope relabelling fails closed because the competition decision preserves the originating `feature_ids` and the staged contract must match them exactly: **implemented and adversarially tested**.
- Preview evidence bound to exact change/proposed SHA/source digest with declared-contract coverage: **implemented and adversarially tested**.
- Missing declared preview coverage blocks while extra undeclared preview coverage gains no authority: **implemented and adversarially tested**.
- Required exact-proposal test evidence with missing/failed/stale/duplicate fail-closed behavior: **implemented and adversarially tested**.
- Extra unrequired test evidence excluded from activation authority: **implemented and adversarially tested**.
- Deterministic rollback anchor bound to exact change/base plus prior revision and pre-change state digest: **implemented and adversarially tested**.
- Missing/mismatched rollback material blocks review readiness: **implemented and adversarially tested**.
- Explicit approval required before any activation plan exists: **implemented and adversarially tested**.
- Approval is exact change/head/preview-bound and cannot override failed/missing preview, test or rollback evidence: **implemented and adversarially tested**.
- Approved output preserves upstream competition evidence plus exact source/preview/test/rollback/approval provenance while remaining inert planning material: **implemented and adversarially tested**.
- Deterministic evidence ordering: **implemented and adversarially tested**.
- Public staged-lifecycle contract excludes credentials, provider endpoints, host/network identities, model paths, shell commands, runner labels and execution controls: **implemented and adversarially tested**.
- Targeted `tests/test_studio_staged_lifecycle.py`: **15/15 PASS locally on exact implementation content**.
- Synthetic end-to-end competition → reviewed selection → staging → approval chain: **PASS locally**.
- Exact implementation-head repository CI #566 / run `34417064924` on `ebc2bbdddc0b63b54fa51be2803518a2c42276f0`: **PASS end-to-end**, including compile, feature registry, product lifecycle ledger, Personal starter distribution, work-session alignment, code ownership, Android unit/proof build/provenance/retention, Python unit tests and Workspace Apps Script tests.
- Base→implementation diff: **exactly four declared files; ten commits ahead, zero behind at implementation-head check**.
- Review finding 1: initial staging API accepted only nested `IntegrationPlan`, which left packet/work relabelling insufficiently bound downstream. Fixed before release by requiring the full `StudioCompetitionDecision` and exact selected candidate-evaluation provenance; regression tests added.
- Review finding 2: the reviewed decision initially omitted the originating `feature_ids`, which could have allowed a correct source proposal to be relabelled onto a different feature scope downstream. Fixed before release by carrying exact feature IDs in `StudioCompetitionDecision` and requiring staged-contract equality; regression coverage added.
- Final documentation-closeout exact-head CI: **pending**.
- Merge/post-merge integration verification: **pending**.
- Live feature activation or rollback: **not claimed and out of scope**.

## Session-start alignment verification — 2026-09-09

### `FEATURES.md`

`DEV-004` requires bounded private custom skill/feature creation with declared contracts. `STUDIO-001` requires guided bounded improvement with preview/test/rollback, source provenance and no silent activation. This packet advances those engine semantics without claiming final Studio UX.

### `BACKLOG.md`

`SKILL-BUILDER-001` is queued as the engine beneath MIRA Studio and explicitly requires declared contracts, preview/test evidence and rollback. Its prerequisites `FEATURE-REGISTRY-001` and `SOURCE-GATES-001` are complete. `FEATURE-SHARE-001` and `MIRA-STUDIO-001` remain separate later work.

### `ROADMAP.md`

The packet preserves provider-neutral API/authority semantics, requires no local infrastructure, does not alter the ordinary Personal Google baseline, and remains a bounded development-engine child rather than expanding into the whole product.

### Reuse and boundary review

- M2-M1-031 `mira.studio_competition` remains the exact candidate provenance/evidence and explicit reviewer-selection authority.
- M2-M1-032 extends that same bounded Studio-development component rather than creating duplicate development state.
- Staging consumes the full reviewed competition decision so packet/work identity, originating feature scope and exact candidate evaluation provenance cannot be detached from the selected source.
- Feature registry and source gates remain their existing authorities; this packet consumes logical IDs/digests only.
- Git/provider/model/test execution, runtime activation, rollback execution, publication/import and final Studio UX remain outside this module.
- Open People Discovery PR #134 and Sheets control-surface PR #135 own unrelated surfaces and are not touched.

### Direction result

ALIGNED

## Exact next action / resume point

1. Commit this final packet documentation closeout without changing implementation semantics.
2. Run final CI on the resulting exact documentation-closeout head.
3. Re-read remote `main`, PR #147 exact head/mergeability and changed-file overlap.
4. Mark PR #147 ready and merge only if final exact-head CI is green, using expected-head protection.
5. Read back merged remote `main` and verify post-merge exact-SHA CI before claiming integration verification.
6. Preserve the evidence ceiling: staged evidence/planning only; no live activation/rollback/provider/model/Git-execution claim.
7. After integration verification, select the next dependency-ranked Studio child packet from current Git rather than chat history.

## Recovery protocol

Resume from remote `main`, branch `work/m2-m1-032-studio-staged-lifecycle`, this `CURRENT_WORK.md`, `docs/work-packets/M2-M1-032.md`, PR #147, and the latest branch head. Do not reconstruct implementation state from chat when Git records it.
