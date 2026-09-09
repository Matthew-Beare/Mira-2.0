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
- **Owned implementation surfaces:** planned `mira/model_profiles.py`, `tests/test_model_profiles.py`, `project/code_ownership.json`, packet doc, branch-local `CURRENT_WORK.md`.
- **Shared/high-contention surfaces:** `project/code_ownership.json` requires exactly one new model-profile component entry. Existing runtime routing/worker registry/lifecycle boundaries are dependencies and must not be duplicated.
- **Current status:** packet started from integration-verified M2-M1-029 main; capability/profile/benchmark implementation pending.

## Objective

Implement a provider-neutral, secret-free model-profile and benchmark-evidence boundary for optional compute runtimes. Explicit profile facts plus explicit benchmark requirements must produce deterministic eligibility and selection evidence without hard-coding model families, hardware, private paths, benchmark thresholds, quality claims or deployment topology.

This packet does not install/load a model, execute inference, benchmark real hardware, choose private hosts, alter worker routing, expose raw inference/Python/shell endpoints, or claim live model quality/performance.

## Required semantics

- Model profiles declare only logical IDs, runtime IDs, artifact identity/digest, generic capabilities and explicit context/output capacities.
- Benchmark observations are evidence with benchmark/version/capability/metric identity, value/unit, UTC time, sample count, evidence kind and provenance digest.
- Selection requirements explicitly define capability/context/output minima and zero or more benchmark threshold requirements; public code supplies no numeric benchmark defaults.
- Benchmark requirements specify comparator, threshold, unit, freshness and allowed evidence kinds.
- Missing, stale, unit-mismatched, disallowed-kind or threshold-failing benchmark evidence blocks that profile for that requirement.
- Future benchmark evidence fails closed.
- Extra benchmark observations do not acquire selection authority.
- Optional ordered preferred profile IDs are policy input; otherwise eligible profiles use stable logical profile-ID tie-breaking, never an inferred quality ranking.
- Result ordering is deterministic and contains no hostnames, IP/MAC addresses, credentials, model paths, shell commands or private provider resource IDs.

## Acceptance state

- M2-M1-029 power/lifecycle planner: **merged as PR #144 at `c87fe4bd8a2e9925ea31c6af888213dab36827ff`; post-merge CI #551 PASS**.
- M2-M1-030 ID/branch collision check: **complete; no prior packet doc or branch existed**.
- Existing model-profile/benchmark implementation search: **complete; no existing current-main authority found under model-profile/benchmark/local-model terms**.
- Hard-coded model family search: **complete; no Qwen/gpt-oss/local-inference implementation found on current main**.
- Deterministic profile/benchmark implementation/tests: **pending**.
- Exact production ownership: **pending**.
- Exact-head CI/merge/post-merge verification: **pending**.
- Live model/runtime/benchmark evidence: **not claimed and out of scope**.

## Session-start alignment verification — 2026-09-09

### `FEATURES.md`

`LOCAL-001` remains the optional local-service bridge. Model profiles describe generic capabilities available behind that bridge rather than making a named model or accelerator into a feature dependency.

### `BACKLOG.md`

`LOCAL-INTEGRATIONS` remains the accepted compute-fabric work anchor explicitly reprioritized by the product owner.

### `ROADMAP.md`

Advanced/local compute remains optional. Standard users must not need a local model, accelerator or self-hosted runtime.

### Reuse and boundary review

- `mira.runtime_router` remains runtime/provider selection authority.
- `mira.service_state.WorkerRegistryView` remains worker capability/health/availability authority.
- `mira.compute_lifecycle` remains lifecycle lock/power planning authority.
- `mira.model_profiles` will only evaluate model-level capability/capacity and benchmark evidence; it will not select workers or execute inference.
- Named model families and private hardware bindings remain configuration/deployment choices outside public feature dependencies.

### Direction result

ALIGNED

## Exact next action / resume point

1. Implement immutable profile, benchmark observation, benchmark requirement and selection-decision contracts in `mira/model_profiles.py`.
2. Add adversarial synthetic tests for exact thresholds, freshness, units, evidence kinds, duplicates, extra evidence, capability/capacity gates, preference/tie-breaking, determinism and privacy.
3. Add exactly one `compute-model-profiles` production ownership component with direct verification.
4. Diff from exact base and verify only intended files changed.
5. Open a draft PR and run full CI; fix only packet-scoped failures.
6. Merge only after exact-head green CI and current-main reconciliation; verify post-merge main CI before integration verification.

## Recovery protocol

Resume from remote `main`, branch `work/m2-m1-030-model-profiles`, this `CURRENT_WORK.md`, `docs/work-packets/M2-M1-030.md`, and the latest branch head. Do not reopen M2-M1-021 through M2-M1-029 unless regression evidence requires it.
