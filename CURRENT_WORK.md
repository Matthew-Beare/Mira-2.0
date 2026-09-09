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
- **Pull request:** `#142`.
- **Owned implementation surfaces:** `mira/compute_observability.py`, `tests/test_compute_observability.py`, `project/code_ownership.json`, packet doc, branch-local `CURRENT_WORK.md`.
- **Shared/high-contention surfaces:** `project/code_ownership.json` contains one explicit new `compute-observability` component entry. Old draft PR #134 also changes that manifest and must reconcile later; M2-M1-027 does not consume any of #134's unfinished feature work.
- **Current status:** implementation, adversarial synthetic tests and exact production ownership are complete; CI #539 passed end-to-end on implementation head `cd22c1e1b715575fbd9df28b8e9dc52c5ba5e31e`; this documentation closeout requires one final exact-head CI before merge.

## Objective

Add a provider-neutral, read-only observability projection over the existing durable worker registry and compute-job control-plane views. The bounded slice produces deterministic Prometheus-compatible metrics for worker health/availability/freshness, job lifecycle state/age/duration/failure, and local-versus-hosted terminal execution use without exposing worker IDs, job IDs, principal IDs, runtime IDs, hostnames, addresses, credentials, model paths or raw task content.

It also defines a deterministic Grafana-compatible PromQL panel plan over those metrics. It does not deploy Prometheus, Grafana, a scrape server, collectors on private machines, hardware sensor readers, private dashboards, alert delivery or safety thresholds.

## Acceptance state

- M2-M1-026 trusted self-hosted CI boundary: **merged as PR #141 at `d17dbed73d6fc55a7bd77dbd5bc2fa1e166b9499`; post-merge CI #538 PASS**.
- M2-M1-026 live gate evidence: **Trusted Runner Gate run #1 PASS; retained receipt for upstream CI #538 reports `trusted_canonical_main`, `requires_isolation=true`, `self_hosted_execution_authorized=false`, reason `runner_isolation_missing`, source/policy SHA both `d17dbed73d6fc55a7bd77dbd5bc2fa1e166b9499`**.
- M2-M1-027 ID/branch collision check: **complete; no prior M2-M1-027 branch or PR existed**.
- Existing observability implementation search: **complete; no compute Prometheus/telemetry component found**.
- Existing state reuse review: **complete; `WorkerRegistryView` and `ComputeJobView` remain source contracts; no second worker/job authority exists**.
- Compute telemetry projection: **implemented in `mira/compute_observability.py`**.
- Prometheus deterministic renderer: **implemented and synthetically tested**.
- Grafana-compatible read-only panel query plan: **implemented and synthetically tested**.
- Worker freshness/future timestamp validation: **implemented and synthetically tested**.
- Job lifecycle/queue-age/attempt/duration aggregation: **implemented and synthetically tested**.
- Local/hosted/unknown terminal result reconciliation: **implemented and synthetically tested**.
- Stable/private identifier exclusion: **synthetically tested in Prometheus and Grafana material**.
- Duplicate worker/job ID fail-closed behavior: **synthetically tested**.
- Exact production ownership: **registered as one `compute-observability` component; code-ownership gate passed in CI #539**.
- CI #539 on implementation head `cd22c1e1b715575fbd9df28b8e9dc52c5ba5e31e`: **PASS end-to-end**.
- Final documentation-closeout exact-head CI: **pending**.
- Merge/post-merge verification: **pending**.
- Live Prometheus/Grafana/private sensor evidence: **not claimed and out of scope**.

## Session-start alignment verification — 2026-09-09

### `FEATURES.md`

`OBS-001` defines provider-neutral operational observability and read-only dashboard projection that never becomes mutable-state authority. `LOCAL-001` remains the optional local-compute integration anchor. This packet is a read-only projection over existing canonical worker/job state.

### `BACKLOG.md`

`LOCAL-INTEGRATIONS` remains the accepted compute-fabric work anchor explicitly reprioritized by the product owner. The packet adds observability required by the compute-fabric initiative without creating a second work authority.

### `ROADMAP.md`

Advanced/self-hosted infrastructure remains optional. Metrics contracts and dashboard query plans are reusable with hosted or local lanes and do not make Prometheus/Grafana/private infrastructure a Standard-path prerequisite.

### Reuse review

- `mira/service_state.py` owns the validated secret-free `WorkerRegistryView`.
- `mira.command_sequencer.py` owns `ComputeJobView` and durable lifecycle truth.
- `mira.compute_observability.py` consumes those views read-only and does not persist replacement worker/job state.
- A separate observability component keeps telemetry out of routing, service-state and job-control responsibilities.

### Privacy/cardinality result

Public metric labels are restricted to bounded state dimensions such as runtime kind, availability, health, identity state, compute mode, lock state, job state and aggregate statistic. Stable worker/job/principal/runtime identifiers and private host/network/material values are never metric labels or dashboard variables in this packet.

### Direction result

ALIGNED

## Exact next action / resume point

1. Run final exact-head CI on the latest documentation-closeout head.
2. Re-read remote `main`, PR #142 head/mergeability and changed-file overlap.
3. Mark PR #142 ready and merge only if final exact-head CI is green, using expected-head protection.
4. Read back merged remote `main` and verify post-merge CI before claiming integration verification.
5. After M2-M1-027 closes, select the next dependency-ranked compute-fabric child packet from current Git state rather than chat history.

## Recovery protocol

Resume from current remote `main`, branch `work/m2-m1-027-compute-observability`, this `CURRENT_WORK.md`, `docs/work-packets/M2-M1-027.md`, PR #142, and the latest branch head. Do not reopen M2-M1-021 through M2-M1-026 unless regression evidence requires it.
