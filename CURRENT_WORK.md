# MIRA 2.0 CURRENT WORK

Git is authoritative. This branch records exactly one active packet. Multiple other packet branches may be active repository-wide under `docs/CONCURRENT_WORK_POLICY.md`.

## Active packet

### `M2-M1-031` — Studio competitive development evidence and integration planning

- **Primary work:** `SKILL-BUILDER-001`.
- **Primary features:** `STUDIO-001`, `DEV-004`.
- **Related invariants/features:** `DEV-001`, `DEV-002`, `DEV-005`, `DEV-006`, `DIST-001`, `LOCAL-001`, `PROVIDER-001`, `RECOVERY-002`.
- **Repository:** `Matthew-Beare/Mira-2.0`.
- **Branch:** `work/m2-m1-031-studio-competitive-dev`.
- **Base SHA:** `e0359ec6a65773c8d01b7a5208f8eb255b093c30`.
- **Packet:** `docs/work-packets/M2-M1-031.md`.
- **Pull request:** `#146`.
- **Owned implementation surfaces:** `mira/studio_competition.py`, `tests/test_studio_competition.py`, `project/code_ownership.json`, packet doc, branch-local `CURRENT_WORK.md`.
- **Shared/high-contention surfaces:** `project/code_ownership.json` contains exactly one new `studio-competitive-development` component. Existing CI trust, runtime routing, source gates, feature registry and Git governance remain separate authorities.
- **Current status:** implementation, adversarial tests and exact production ownership complete; CI #556 passed end-to-end on exact implementation head `831bda18ecfa2c040636838b2ede0b9aaac2a4d7`; final documentation-closeout exact-head CI pending before merge.

## Objective

Implement the provider-neutral evidence contract MIRA Studio can use when multiple independent implementers produce candidate solutions for the same bounded work packet. The contract preserves branch/base/head provenance, deterministic acceptance/verification evidence, independent critique and explicit reviewer selection without executing code, calling a model/provider, mutating Git, or auto-integrating a subjective winner.

## Acceptance state

- M2-M1-030 model profiles/benchmark evidence: **merged as PR #145 at `e0359ec6a65773c8d01b7a5208f8eb255b093c30`; post-merge CI #555 PASS**.
- M2-M1-031 ID/branch collision check: **complete; no prior packet doc or branch existed**.
- Canonical Studio direction: **confirmed; STUDIO-001 requires bounded preview/test/rollback/provenance and no silent imported activation**.
- Backlog anchor: **SKILL-BUILDER-001; full MIRA Studio UX and FEATURE-SHARE-001 remain separate later work**.
- Exact packet/base/branch/head candidate provenance: **implemented and synthetically tested**.
- Acceptance-criterion coverage gates: **implemented and synthetically tested**.
- Exact-head required verification evidence with missing/failed/stale/duplicate fail-closed behavior: **implemented and synthetically tested**.
- Independent critique policy and self-critique rejection: **implemented and synthetically tested**.
- Open blocking versus resolved/accepted-risk critique behavior: **implemented and synthetically tested**.
- Deterministic candidate/evidence ordering: **implemented and synthetically tested**.
- No automatic subjective winner selection: **implemented and synthetically tested**.
- Explicit reviewer selection bound to integration-ready exact head: **implemented and synthetically tested**.
- No Git/provider/model/private-runner execution fields or side effects: **implemented and synthetically tested**.
- Exact production ownership: **registered as one `studio-competitive-development` component; code-ownership gate PASS in CI #556**.
- Base→implementation diff: **exactly five intended files; ownership manifest +9/-0**.
- CI #556 on exact implementation head `831bda18ecfa2c040636838b2ede0b9aaac2a4d7`: **PASS end-to-end including compile, feature registry, product lifecycle ledger, starter distribution, work-session alignment, code ownership, Android proof/provenance/retention, Python unit tests and Workspace Apps Script tests**.
- Final documentation-closeout exact-head CI: **pending**.
- Merge/post-merge verification: **pending**.
- Live competitive model execution, private runner, Git candidate orchestration or merge execution: **not claimed and out of scope**.

## Session-start alignment verification — 2026-09-09

### `FEATURES.md`

`STUDIO-001` is the integrated user-facing continuous-improvement layer over bounded custom feature creation and controlled sharing. Preview/test/rollback, source provenance and no silent activation are required semantics.

### `BACKLOG.md`

`SKILL-BUILDER-001` is the bounded engine beneath Studio. `MIRA-STUDIO-001` remains a later user-facing vertical and `FEATURE-SHARE-001` remains separate sharing/import hardening. This packet advances the engine only.

### `ROADMAP.md`

Competitive development may use local or hosted implementers, but local compute remains optional. No Standard-path local infrastructure dependency is introduced.

### Reuse and boundary review

- Git/packet policy remains branch/work authority.
- `project/ci_trust.py` remains private-runner source-trust/isolation authority.
- Feature registry/alignment gates remain canonical feature/work validation authority.
- `mira.studio_competition` validates candidate provenance/evidence and produces explicit integration-readiness/planning output only.
- GitHub/provider/model invocation, branch creation, test execution, merge execution and private-runner scheduling remain outside this module.

### Direction result

ALIGNED

## Exact next action / resume point

1. Run final exact-head CI on the documentation-closeout head.
2. Re-read remote `main`, PR #146 exact head/mergeability and changed-file overlap.
3. Mark PR #146 ready and merge only if final exact-head CI is green, using expected-head protection.
4. Read back merged remote `main` and verify post-merge push CI before claiming integration verification.
5. Preserve the evidence ceiling: evidence/planning only; no live competitive model/Git/private-runner execution claim.
6. Select the next dependency-ranked compute/Studio child packet from current Git state rather than chat history.

## Recovery protocol

Resume from remote `main`, branch `work/m2-m1-031-studio-competitive-dev`, this `CURRENT_WORK.md`, `docs/work-packets/M2-M1-031.md`, PR #146, and the latest branch head. Do not reopen completed compute packets unless regression evidence requires it.
