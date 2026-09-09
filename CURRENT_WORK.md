# MIRA 2.0 CURRENT WORK

Git is authoritative. This branch records exactly one active packet. Multiple other packet branches may be active repository-wide under `docs/CONCURRENT_WORK_POLICY.md`.

## Active packet

### `M2-M1-030` — Capability-based local model profiles and benchmark evidence

- **Primary work:** `LOCAL-INTEGRATIONS`.
- **Primary features:** `LOCAL-001`.
- **Related invariants/features:** `PROVIDER-001`, `SOURCE-001`, `RECOVERY-002`, `OBS-001`, `API-001`.
- **Repository:** `Matthew-Beare/Mira-2.0`.
- **Branch:** `work/m2-m1-030-model-profiles`.
- **Base SHA:** `c87fe4bd8a2e9925ea31c6af888213dab36827ff`.
- **Packet:** `docs/work-packets/M2-M1-030.md`.
- **Pull request:** `#145`.
- **Owned implementation surfaces:** `mira/model_profiles.py`, `tests/test_model_profiles.py`, `project/code_ownership.json`, packet doc, branch-local `CURRENT_WORK.md`.
- **Shared/high-contention surfaces:** `project/code_ownership.json` contains exactly one new `compute-model-profiles` entry. Existing runtime routing, worker registry and lifecycle boundaries were not duplicated or mutated.
- **Current status:** implementation, adversarial tests and exact production ownership complete; CI #552 passed end-to-end on exact implementation head `583fdaef8bb110001d7deab5f5b67b0c9e58b19e`; final documentation-closeout exact-head CI pending before merge.

## Objective

Implement a provider-neutral, secret-free model-profile and benchmark-evidence boundary for optional compute runtimes. Explicit profile facts plus explicit benchmark requirements produce deterministic eligibility and selection evidence without hard-coding model families, hardware, private paths, benchmark thresholds, quality claims or deployment topology.

This packet does not install/load a model, execute inference, benchmark real hardware, choose private hosts, alter worker routing, expose raw inference/Python/shell endpoints, or claim live model quality/performance.

## Acceptance state

- M2-M1-029 power/lifecycle planner: **merged as PR #144 at `c87fe4bd8a2e9925ea31c6af888213dab36827ff`; post-merge CI #551 PASS**.
- M2-M1-030 ID/branch collision check: **complete; no prior packet doc or branch existed**.
- Existing model-profile/benchmark implementation search: **complete; no prior current-main authority found**.
- Hard-coded Qwen/gpt-oss/local-inference implementation search: **complete; none found on packet base**.
- Capability/profile/benchmark evaluator: **implemented in `mira/model_profiles.py`**.
- Capability/context/output gates: **implemented and synthetically tested**.
- Explicit benchmark comparator/threshold/unit/freshness/evidence-kind gates: **implemented and synthetically tested**.
- Exact `at_least` / `at_most` equality boundaries: **synthetically tested**.
- Missing/stale/future/unit-mismatched/disallowed/duplicate/threshold-failing evidence: **fails closed and synthetically tested**.
- Extra unrequested evidence non-authority: **synthetically tested**.
- Explicit preferred-profile ordering and stable ID-only fallback tie-break: **synthetically tested**.
- Input-order determinism and private-field exclusion: **synthetically tested**.
- Exact production ownership: **registered as one `compute-model-profiles` component; code-ownership gate PASS in CI #552**.
- Base→implementation diff: **exactly five intended files; ownership manifest +9/-0**.
- CI #552 on exact implementation head `583fdaef8bb110001d7deab5f5b67b0c9e58b19e`: **PASS end-to-end including compile, feature registry, lifecycle ledger, starter distribution, work-session alignment, code ownership, Android proof/provenance/retention, Python unit tests and Workspace Apps Script tests**.
- Final documentation-closeout exact-head CI: **pending**.
- Merge/post-merge verification: **pending**.
- Live model/runtime/benchmark/private-deployment evidence: **not claimed and out of scope**.

## Session-start alignment verification — 2026-09-09

### `FEATURES.md`

`LOCAL-001` remains the optional local-service bridge. Model profiles describe generic capabilities available behind that bridge rather than making a named model or accelerator into a feature dependency.

### `BACKLOG.md`

`LOCAL-INTEGRATIONS` remains the accepted compute-fabric work anchor explicitly reprioritized by the product owner.

### `ROADMAP.md`

Advanced/local compute remains optional. Standard users do not need a local model, accelerator or self-hosted runtime.

### Reuse and boundary review

- `mira.runtime_router` remains runtime/provider selection authority.
- `mira.service_state.WorkerRegistryView` remains worker capability/health/availability authority.
- `mira.compute_lifecycle` remains lifecycle lock/power planning authority.
- `mira.model_profiles` evaluates only model-level capability/capacity and explicit benchmark evidence; it does not select workers or execute inference.
- Named model families and private hardware bindings remain configuration/deployment choices outside public feature dependencies.

### Direction result

ALIGNED

## Exact next action / resume point

1. Run final exact-head CI on the documentation-closeout head.
2. Re-read remote `main`, PR #145 exact head/mergeability and changed-file overlap.
3. Mark PR #145 ready and merge only if final exact-head CI is green, using expected-head protection.
4. Read back merged remote `main` and verify post-merge push CI before claiming integration verification.
5. Preserve the evidence ceiling: policy/profile/evidence evaluation only; no live model/runtime/benchmark/private deployment claim.
6. Select the next dependency-ranked compute-fabric child packet from current Git state rather than chat history.

## Recovery protocol

Resume from remote `main`, branch `work/m2-m1-030-model-profiles`, this `CURRENT_WORK.md`, `docs/work-packets/M2-M1-030.md`, PR #145, and the latest branch head. Do not reopen M2-M1-021 through M2-M1-029 unless regression evidence requires it.
