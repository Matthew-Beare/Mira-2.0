# MIRA 2.0 CURRENT WORK

Git is authoritative. This branch records exactly one active packet. Multiple other packet branches may be active repository-wide under `docs/CONCURRENT_WORK_POLICY.md`.

## Active packet

### `M2-M1-029` — Deterministic compute power/lifecycle control

- **Primary work:** `LOCAL-INTEGRATIONS`.
- **Primary features:** `LOCAL-001`.
- **Related invariants/features:** `RECOVERY-002`, `OBS-001`, `PROVIDER-001`, `STORE-001`, `API-001`.
- **Repository:** `Matthew-Beare/Mira-2.0`.
- **Branch:** `work/m2-m1-029-power-lifecycle`.
- **Base SHA:** `29bf58210d715a5f54e6dff8b8272b496e27fc52`.
- **Packet:** `docs/work-packets/M2-M1-029.md`.
- **Owned implementation surfaces:** planned `mira/compute_lifecycle.py`, `tests/test_compute_lifecycle.py`, `project/code_ownership.json`, packet doc, branch-local `CURRENT_WORK.md`.
- **Shared/high-contention surfaces:** `project/code_ownership.json` requires exactly one new lifecycle component. Existing worker registry/control-plane/safety modules are dependencies and are not to be duplicated or mutated unless a defect is proven.
- **Current status:** packet started from integration-verified M2-M1-028 main; lifecycle planner implementation pending.

## Objective

Implement the provider-neutral deterministic lifecycle decision seam that later private power adapters can execute. The planner must compose existing durable worker state, durable active compute-job state, optional deterministic safety decisions and explicit user/operator locks into bounded lifecycle actions without directly waking, shutting down, draining or mutating a real machine.

This packet is planner/evidence only. It does not send Wake-on-LAN, call IPMI/Redfish/SSH/OS shutdown, change worker registry state, mutate compute jobs, kill processes, bind a private host, or claim live power-control evidence.

## Required lifecycle semantics

- `do_not_wake` blocks wake requests regardless of worker presence.
- `do_not_shutdown` blocks safe-shutdown execution requests, including safety-driven shutdown requirements; the blocked safety requirement must remain visible and require human/operator resolution rather than being silently discarded.
- `interactive_lock` prevents new MIRA work and causes ordinary work to drain/checkpoint when possible; deterministic safety stop/fault requirements still take precedence over interactive convenience.
- `maintenance_lock` prevents new work/wake and requests drain.
- ordinary graceful drain/shutdown must prefer finish/checkpoint semantics over destructive stop.
- critical/sensor-fault safety requirements may require immediate workload stop and worker fault state.
- wake/shutdown results are requests/eligibility only; provider-specific execution and exact hardware readback remain deferred.

## Acceptance state

- M2-M1-028 hardware safety: **merged as PR #143 at `29bf58210d715a5f54e6dff8b8272b496e27fc52`; post-merge CI #547 PASS**.
- M2-M1-029 ID/branch collision check: **complete; no prior packet doc or branch existed**.
- Dependency review: **complete; worker availability/health/interactive lock already exist in `WorkerRegistryView`; active lease/job transitions already exist in `ComputeJobControlPlane`; deterministic hardware response requirements already exist in `ComputeSafetyDecision`**.
- Duplicate-boundary review: **complete; no existing production `compute_lifecycle`/power-control component exists on current main**.
- Deterministic lifecycle implementation/tests: **pending**.
- Exact production ownership: **pending**.
- Exact-head CI/merge/post-merge verification: **pending**.
- Live WOL/shutdown/private deployment evidence: **not claimed and out of scope**.

## Session-start alignment verification — 2026-09-09

### `FEATURES.md`

`LOCAL-001` requires a scoped local-service bridge with verified capability/readback and no blanket LAN trust. Power/lifecycle planning is a safety/integrity dependency of that bridge, not a new user-facing feature family.

### `BACKLOG.md`

`LOCAL-INTEGRATIONS` remains the accepted compute-fabric work anchor explicitly reprioritized by the product owner.

### `ROADMAP.md`

Advanced/self-hosted infrastructure remains optional. This planner must not create any Standard-path infrastructure prerequisite.

### Reuse and boundary review

- `mira.service_state.WorkerRegistryView` remains worker-state authority.
- `mira.command_sequencer.ComputeJobView` remains durable compute-job authority.
- `mira.compute_safety.ComputeSafetyDecision` remains hardware-safety decision authority.
- `mira.compute_lifecycle` will only reconcile those views plus explicit lifecycle locks/intents into action requirements.
- Private WOL/shutdown/sensor/network adapters remain outside public planner code.

### Direction result

ALIGNED

## Exact next action / resume point

1. Implement immutable lifecycle intent/lock/power/action contracts in `mira/compute_lifecycle.py`.
2. Compose worker state, assigned active jobs and optional safety decision into deterministic actions with explicit blocked-action provenance.
3. Add adversarial tests for do-not-wake/do-not-shutdown, interactive/maintenance drain behavior, safety precedence, graceful shutdown, wake eligibility, deterministic ordering and privacy.
4. Add exactly one production ownership component with direct test verification.
5. Open a draft PR and run full CI; fix only packet-scoped failures.
6. Merge only after exact-head green CI and current-main reconciliation; verify post-merge main CI before integration verification.

## Recovery protocol

Resume from remote `main`, branch `work/m2-m1-029-power-lifecycle`, this `CURRENT_WORK.md`, `docs/work-packets/M2-M1-029.md`, and the latest branch head. Do not reopen M2-M1-021 through M2-M1-028 unless regression evidence requires it.
