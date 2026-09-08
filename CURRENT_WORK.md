# MIRA 2.0 CURRENT WORK

Git is authoritative. This branch records exactly one active packet. Multiple other packet branches may be active repository-wide under `docs/CONCURRENT_WORK_POLICY.md`.

## Active packet

### `M2-M1-027` — Compute observability foundation

- **Primary work:** `LOCAL-INTEGRATIONS`.
- **Primary features:** `OBS-001`, `LOCAL-001`.
- **Related invariants/features:** `RECOVERY-002`, `PROVIDER-001`, `STORE-001`.
- **Repository:** `Matthew-Beare/Mira-2.0`.
- **Branch:** `work/m2-m1-027-compute-observability`.
- **Base SHA:** `d17dbed73d6fc55a7bd77dbd5bc2fa1e166b9499`.
- **Packet:** `docs/work-packets/M2-M1-027.md`.
- **Owned implementation surfaces:** planned `mira/compute_observability.py`, `tests/test_compute_observability.py`, `project/code_ownership.json`, packet doc, branch-local `CURRENT_WORK.md`.
- **Shared/high-contention surfaces:** `project/code_ownership.json` requires one explicit new component entry because production-code ownership is exact-path enforced. Old draft PR #134 also changes that manifest and must reconcile later; M2-M1-027 does not consume any of #134's unfinished feature work.
- **Current status:** packet started from live-workflow-verified M2-M1-026 main; worker/job telemetry contract implementation pending.

## Objective

Add a provider-neutral, read-only observability projection over the existing durable worker registry and compute-job control-plane views. The first slice must produce deterministic Prometheus-compatible metrics for worker health/availability/freshness, job lifecycle state/age/duration/failure, and local-versus-hosted terminal execution use without exposing worker IDs, job IDs, principal IDs, runtime IDs, hostnames, addresses, credentials, model paths or raw task content.

The packet also defines a deterministic Grafana-compatible PromQL panel plan over those metrics. It does not deploy Prometheus, Grafana, a scrape server, collectors on private machines, hardware sensor readers, private dashboards, alert delivery or safety thresholds.

## Acceptance state

- M2-M1-026 trusted self-hosted CI boundary: **merged as PR #141 at `d17dbed73d6fc55a7bd77dbd5bc2fa1e166b9499`; post-merge CI #538 PASS**.
- M2-M1-026 live gate evidence: **Trusted Runner Gate run #1 PASS; retained receipt for upstream CI #538 reports `trusted_canonical_main`, `requires_isolation=true`, `self_hosted_execution_authorized=false`, reason `runner_isolation_missing`, source/policy SHA both `d17dbed73d6fc55a7bd77dbd5bc2fa1e166b9499`**.
- M2-M1-027 ID/branch collision check: **complete; no prior M2-M1-027 branch or PR existed**.
- Existing observability implementation search: **complete; no compute Prometheus/telemetry component found**.
- Existing ownership review: **complete; no OBS-001 component exists, and exact production-path ownership requires a new manifest component for a proper standalone module**.
- Existing state reuse review: **complete; `WorkerRegistryView` and `ComputeJobView` are the source contracts; no second worker/job authority will be created**.
- Compute telemetry implementation/tests: **pending**.
- Exact-head CI/merge/post-merge verification: **pending**.
- Live Prometheus/Grafana/private sensor evidence: **not claimed and out of scope**.

## Session-start alignment verification — 2026-09-08

### `FEATURES.md`

`OBS-001` defines provider-neutral operational observability and read-only dashboard projection that never becomes mutable-state authority. `LOCAL-001` remains the optional local-compute integration anchor. This packet is a read-only projection over existing canonical worker/job state.

### `BACKLOG.md`

`LOCAL-INTEGRATIONS` remains the accepted compute-fabric work anchor explicitly reprioritized by the product owner. The packet adds observability required by the compute-fabric initiative without creating a second work authority.

### `ROADMAP.md`

Advanced/self-hosted infrastructure remains optional. Metrics contracts and dashboard query plans are reusable with hosted or local lanes and do not make Prometheus/Grafana/private infrastructure a Standard-path prerequisite.

### Reuse review

- `mira/service_state.py` already owns the validated secret-free `WorkerRegistryView`.
- `mira/command_sequencer.py` already owns `ComputeJobView` and durable lifecycle truth.
- Observability therefore consumes those views read-only; it does not persist new worker/job state or mutate either source.
- A separate observability module is warranted rather than adding telemetry responsibilities to routing, service-state or job-control modules.

### Privacy/cardinality result

Public metric labels are restricted to bounded state dimensions such as runtime kind, availability, health, identity state, compute mode, lock state, job state and aggregate statistic. Stable worker/job/principal/runtime identifiers and private host/network/material values are never metric labels or dashboard variables in this packet.

### Direction result

ALIGNED

## Exact next action / resume point

1. Implement `mira/compute_observability.py` over `WorkerRegistryView` and `ComputeJobView` with deterministic Prometheus exposition and a read-only Grafana panel query plan.
2. Add adversarial synthetic tests for deterministic ordering, heartbeat freshness/future rejection, job lifecycle aggregation, local-versus-hosted terminal mapping, queue age, terminal duration and identifier/privacy exclusion.
3. Add one explicit `compute-observability` ownership component referencing `OBS-001`, `LOCAL-001` and direct test verification.
4. Open a draft PR and run exact-head CI; fix only packet-scoped failures.
5. Merge only after current-main reconciliation and exact-head green CI, then verify post-merge CI before claiming integration verification.

## Recovery protocol

Resume from current remote `main`, branch `work/m2-m1-027-compute-observability`, this `CURRENT_WORK.md`, `docs/work-packets/M2-M1-027.md`, and the latest branch head. Do not reopen M2-M1-021 through M2-M1-026 unless regression evidence requires it.
