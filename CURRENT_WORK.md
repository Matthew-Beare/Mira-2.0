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
- **Pull request:** `#144`.
- **Owned implementation surfaces:** `mira/compute_lifecycle.py`, `tests/test_compute_lifecycle.py`, `project/code_ownership.json`, packet doc, branch-local `CURRENT_WORK.md`.
- **Shared/high-contention surfaces:** `project/code_ownership.json` contains exactly one new `compute-power-lifecycle` entry. Existing worker registry/control-plane/safety modules remain dependency authorities and were not duplicated or mutated.
- **Current status:** lifecycle planner, adversarial tests and exact production ownership are complete; CI #548 passed end-to-end on implementation head `6fb9b1827f4879024dbe618191f917d45dd385b1`; this closeout requires one final exact-head CI before merge.

## Objective

Implement the provider-neutral deterministic lifecycle decision seam that later private power adapters can execute. The planner composes existing durable worker state, durable active compute-job state, optional deterministic safety decisions and explicit user/operator locks into bounded lifecycle actions without directly waking, shutting down, draining or mutating a real machine.

This packet is planner/evidence only. It does not send Wake-on-LAN, call IPMI/Redfish/SSH/OS shutdown, change worker registry state, mutate compute jobs, kill processes, bind a private host, or claim live power-control evidence.

## Required lifecycle semantics

- `do_not_wake` blocks wake requests regardless of worker presence.
- `do_not_shutdown` blocks safe-shutdown execution requests, including safety-driven shutdown requirements; the blocked safety requirement remains visible and requires human/operator resolution rather than being silently discarded.
- `interactive_lock` prevents new MIRA work and causes ordinary work to drain/checkpoint when possible; deterministic safety stop/fault requirements still take precedence over interactive convenience.
- `maintenance_lock` prevents new work/wake and requests drain.
- ordinary graceful drain/shutdown prefers finish/checkpoint semantics over destructive stop.
- critical/sensor-fault safety requirements may require immediate workload stop and worker fault state.
- wake/shutdown results are requests/eligibility only; provider-specific execution and exact hardware readback remain deferred.

## Acceptance state

- M2-M1-028 hardware safety: **merged as PR #143 at `29bf58210d715a5f54e6dff8b8272b496e27fc52`; post-merge CI #547 PASS**.
- M2-M1-029 ID/branch collision check: **complete; no prior packet doc or branch existed**.
- Dependency review: **complete; worker availability/health/interactive lock remain in `WorkerRegistryView`; active lease/job transitions remain in `ComputeJobControlPlane`; deterministic hardware response requirements remain in `ComputeSafetyDecision`**.
- Duplicate-boundary review: **complete; no prior production `compute_lifecycle`/power-control component existed on packet base**.
- Deterministic lifecycle planner: **implemented in `mira/compute_lifecycle.py`**.
- Effective durable+explicit interactive lock semantics: **implemented and synthetically tested**.
- Do-not-wake/maintenance/interactive wake blocking: **implemented and synthetically tested**.
- Graceful drain/interactive/maintenance `finish_or_checkpoint` behavior: **implemented and synthetically tested**.
- Critical/sensor-fault `stop_required` + fault precedence: **implemented and synthetically tested**.
- Do-not-shutdown preservation of blocked safety requirement: **implemented and synthetically tested**.
- Graceful and safety-driven shutdown eligibility after assigned active jobs clear: **implemented and synthetically tested**.
- Other-worker/terminal-job non-authority and deterministic input ordering: **synthetically tested**.
- Secret-free planner result/no provider side-effect surface: **synthetically tested**.
- Exact production ownership: **registered as one `compute-power-lifecycle` component; code-ownership gate PASS in CI #548**.
- Base→implementation diff: **exactly five intended files; ownership manifest changed by nine added lines only**.
- CI #548 on implementation head `6fb9b1827f4879024dbe618191f917d45dd385b1`: **PASS end-to-end including compile, feature registry, product lifecycle, starter distribution, work-session alignment, code ownership, Android proof/provenance/retention, Python unit tests and Workspace Apps Script tests**.
- Final documentation-closeout exact-head CI: **pending**.
- Merge/post-merge verification: **pending**.
- Live WOL/shutdown/private deployment evidence: **not claimed and out of scope**.

## Session-start alignment verification — 2026-09-09

### `FEATURES.md`

`LOCAL-001` requires a scoped local-service bridge with verified capability/readback and no blanket LAN trust. Power/lifecycle planning is a safety/integrity dependency of that bridge, not a new user-facing feature family.

### `BACKLOG.md`

`LOCAL-INTEGRATIONS` remains the accepted compute-fabric work anchor explicitly reprioritized by the product owner.

### `ROADMAP.md`

Advanced/self-hosted infrastructure remains optional. This planner does not create a Standard-path infrastructure prerequisite.

### Reuse and boundary review

- `mira.service_state.WorkerRegistryView` remains worker-state authority.
- `mira.command_sequencer.ComputeJobView` remains durable compute-job authority.
- `mira.compute_safety.ComputeSafetyDecision` remains hardware-safety decision authority.
- `mira.compute_lifecycle` only reconciles those views plus explicit lifecycle locks/intents into action requirements.
- Private WOL/shutdown/sensor/network adapters remain outside public planner code.

### Direction result

ALIGNED

## Exact next action / resume point

1. Run final exact-head CI on the documentation-closeout head.
2. Re-read remote `main`, PR #144 exact head/mergeability and changed-file overlap.
3. Mark PR #144 ready and merge only if final exact-head CI is green, using expected-head protection.
4. Read back merged remote `main` and verify post-merge CI before claiming integration verification.
5. Preserve the evidence ceiling: planner/test/integration verification only; no live WOL/shutdown/private deployment claim.
6. Select the next dependency-ranked compute-fabric child packet from current Git state rather than chat history.

## Recovery protocol

Resume from remote `main`, branch `work/m2-m1-029-power-lifecycle`, this `CURRENT_WORK.md`, `docs/work-packets/M2-M1-029.md`, PR #144, and the latest branch head. Do not reopen M2-M1-021 through M2-M1-028 unless regression evidence requires it.
