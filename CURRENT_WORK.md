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
- **Packet:** `docs/work-packets/M2-M1-032.md`.
- **Pull request:** pending.
- **Owned implementation surfaces:** `mira/studio_competition.py`, `tests/test_studio_staged_lifecycle.py`, packet doc, branch-local `CURRENT_WORK.md`.
- **Shared/high-contention surfaces:** `mira/studio_competition.py` is the existing `studio-competitive-development` component merged by M2-M1-031. No active open PR owns that implementation path. No `FEATURES.md`, `BACKLOG.md`, `ROADMAP.md`, `PROJECT_INSTRUCTIONS.md`, Google Workspace/Sheets, People Discovery, provider, private-runner or local-compute implementation surface is modified by this packet.
- **Current status:** packet branch created from integration-verified M2-M1-031 merge; session-start alignment complete; implementation pending.

## Objective

Extend the provider-neutral Studio development engine with a fail-closed staged-change lifecycle that binds a selected proposal to declared contracts, preview evidence, exact-proposal test evidence, a deterministic rollback anchor and explicit human approval before producing any activation plan. The packet plans activation/rollback material only. It does not activate a feature, mutate runtime state, execute rollback, call a provider/model, merge Git, publish/import a feature or create final Studio UX.

## Acceptance state

- M2-M1-031 competitive development evidence/planning: **merged at `be38234a49c60fa28d478dc64132531767cb73c1`; exact-merge CI checks PASS**.
- SKILL-BUILDER prerequisites `FEATURE-REGISTRY-001` and `SOURCE-GATES-001`: **complete/CI-enforced**.
- M2-M1-032 branch: **created from exact verified main `be38234a49c60fa28d478dc64132531767cb73c1`**.
- Declared staged-change contract bound to exact base/proposed source provenance: pending.
- Preview evidence bound to exact proposal and declared contract coverage: pending.
- Required exact-proposal test evidence with missing/failed/stale/duplicate fail-closed behavior: pending.
- Deterministic rollback anchor bound to exact pre-change base/revision/state digest: pending.
- Explicit approval required before any activation plan exists: pending.
- Approval cannot override failed/missing preview, test or rollback evidence: pending.
- Deterministic ordering and extra-unrequired-test non-authority: pending.
- Public contract excludes credentials, provider endpoints, private host identity, shell commands and automatic activation execution: pending.
- Targeted tests and repository CI: pending.
- Merge/post-merge integration verification: pending.
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
- Feature registry and source gates remain their existing authorities; this packet consumes logical IDs/digests only.
- Git/provider/model/test execution, runtime activation, rollback execution, publication/import and final Studio UX remain outside this module.
- Open People Discovery PR #134 and Sheets control-surface PR #135 own unrelated surfaces and are not touched.

### Direction result

ALIGNED

## Exact next action / resume point

1. Implement the staged-change contract and deterministic evaluation in `mira/studio_competition.py`.
2. Add adversarial direct tests in `tests/test_studio_staged_lifecycle.py`.
3. Run targeted tests and required repository gates; correct only packet-scoped failures.
4. Record exact branch head/test evidence in this file and `docs/work-packets/M2-M1-032.md`.
5. Open a draft PR, verify exact-head CI and reconcile current `main` before merge.
6. Merge only after green exact-head evidence; read back merge SHA and post-merge CI before claiming integration verification.
7. Preserve the evidence ceiling: staged evidence/planning only, no live activation/rollback/provider/model/Git-execution claim.

## Recovery protocol

Resume from current remote `main`, branch `work/m2-m1-032-studio-staged-lifecycle`, this `CURRENT_WORK.md`, `docs/work-packets/M2-M1-032.md`, and the latest branch head/open PR. Do not reconstruct implementation state from chat when Git records it.
