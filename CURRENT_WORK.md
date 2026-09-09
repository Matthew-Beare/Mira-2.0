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
- **Owned implementation surfaces:** planned `mira/studio_competition.py`, `tests/test_studio_competition.py`, `project/code_ownership.json`, packet doc, branch-local `CURRENT_WORK.md`.
- **Shared/high-contention surfaces:** `project/code_ownership.json` requires exactly one new Studio competitive-development component. Existing CI trust, runtime routing, source gates, feature registry and Git governance remain separate authorities.
- **Current status:** packet started from integration-verified M2-M1-030 main; implementation pending.

## Objective

Implement the provider-neutral evidence contract MIRA Studio can use when multiple independent implementers produce candidate solutions for the same bounded work packet. The contract must preserve branch/base/head provenance, deterministic acceptance/verification evidence, independent critique and explicit reviewer selection without executing code, calling a model/provider, mutating Git, or auto-integrating a subjective winner.

## Required semantics

- Every candidate is bound to the same explicit packet/work/base SHA and its own unique branch/head SHA.
- Candidate provenance contains only logical producer/candidate IDs, branch/base/head SHA, declared acceptance-criterion coverage and source/artifact digest.
- Required verification suites are explicit policy input. Evidence must target the exact candidate head SHA and pass; a green check on another SHA has no authority.
- Optional independent-critique policy can require at least one critique whose critic identity differs from the candidate producer.
- Open blocking critique makes a candidate not integration-ready. Resolved or explicitly accepted-risk critique retains provenance but no longer blocks.
- Missing declared acceptance-criterion coverage fails closed.
- Candidate/input order cannot change eligibility or output ordering.
- Multiple eligible candidates do not trigger automatic subjective ranking. Explicit reviewer selection is required before an integration plan exists.
- Reviewer selection must name an integration-ready candidate and is bound to that candidate's exact head SHA.
- The result is a plan/evidence object only. It does not merge branches, execute tests, invoke local/hosted models, or authorize private-runner execution.

## Acceptance state

- M2-M1-030 model profiles/benchmark evidence: **merged as PR #145 at `e0359ec6a65773c8d01b7a5208f8eb255b093c30`; post-merge CI #555 PASS**.
- M2-M1-031 ID/branch collision check: **complete; no prior packet doc or branch existed**.
- Canonical Studio direction: **confirmed; STUDIO-001 requires bounded preview/test/rollback/provenance and no silent imported activation**.
- Backlog anchor: **SKILL-BUILDER-001 queued beneath MIRA Studio; FEATURE-SHARE-001 remains a separate later hardening path**.
- Trusted private CI dependency: **M2-M1-026 remains the source-trust/isolation boundary; this packet will not weaken it or add self-hosted execution**.
- Competitive candidate implementation/tests: **pending**.
- Exact production ownership: **pending**.
- Exact-head CI/merge/post-merge verification: **pending**.
- Live model/Git/private-runner/integration execution evidence: **not claimed and out of scope**.

## Session-start alignment verification — 2026-09-09

### `FEATURES.md`

`STUDIO-001` is the integrated user-facing continuous-improvement layer over bounded custom feature creation and controlled sharing. Preview/test/rollback, source provenance and no silent activation are required semantics.

### `BACKLOG.md`

`SKILL-BUILDER-001` is the bounded engine beneath Studio. `MIRA-STUDIO-001` remains a later user-facing vertical and `FEATURE-SHARE-001` remains separate sharing/import hardening. This packet advances the engine only.

### `ROADMAP.md`

Competitive development may use local or hosted implementers, but local compute remains optional. No Standard-path local infrastructure dependency may be introduced.

### Reuse and boundary review

- Git/packet policy remains branch/work authority.
- `project/ci_trust.py` remains private-runner source-trust/isolation authority.
- Feature registry/alignment gates remain canonical feature/work validation authority.
- `mira.studio_competition` will only validate candidate provenance/evidence and produce explicit integration-readiness/planning output.
- GitHub/provider/model invocation, branch creation, test execution, merge execution and private runner scheduling remain outside this module.

### Direction result

ALIGNED

## Exact next action / resume point

1. Implement immutable work-spec, candidate, verification, critique, reviewer-selection and integration-plan contracts in `mira/studio_competition.py`.
2. Add adversarial tests for cross-branch/base/head binding, exact-SHA verification, criterion coverage, independent critique, blocking finding resolution, deterministic ordering and explicit reviewer selection.
3. Add exactly one `studio-competitive-development` production ownership component with direct tests.
4. Diff from exact base and verify only intended files changed.
5. Open a draft PR and run full CI; fix only packet-scoped failures.
6. Merge only after exact-head green CI and current-main reconciliation; verify post-merge main CI before integration verification.

## Recovery protocol

Resume from remote `main`, branch `work/m2-m1-031-studio-competitive-dev`, this `CURRENT_WORK.md`, `docs/work-packets/M2-M1-031.md`, and the latest branch head. Do not reopen completed compute packets unless regression evidence requires it.
