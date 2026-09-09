# MIRA 2.0 CURRENT WORK

Git is authoritative. This branch records exactly one active packet. Multiple other packet branches may be active repository-wide under `docs/CONCURRENT_WORK_POLICY.md`.

## Active packet

### `M2-M1-028` — Deterministic compute hardware-safety policy

- **Primary work:** `LOCAL-INTEGRATIONS`.
- **Primary features:** `LOCAL-001`.
- **Related invariants/features:** `OBS-001`, `RECOVERY-002`, `API-001`.
- **Repository:** `Matthew-Beare/Mira-2.0`.
- **Branch:** `work/m2-m1-028-hardware-safety`.
- **Base SHA:** `20aa43c99e03cef8e9aa80817890d3484ea0f04f`.
- **Packet:** `docs/work-packets/M2-M1-028.md`.
- **Pull request:** `#143`.
- **Owned implementation surfaces:** `mira/compute_safety.py`, `tests/test_compute_safety.py`, `project/code_ownership.json`, packet doc, branch-local `CURRENT_WORK.md`.
- **Shared/high-contention surfaces:** `project/code_ownership.json` contains exactly one new `compute-hardware-safety` component entry. Old draft PR #134 also changes that manifest and must reconcile later; this packet uses current main as authority and does not consume People Discovery work.
- **Current status:** deterministic safety policy, adversarial synthetic tests and exact production ownership are complete; CI #544 passed end-to-end on corrected implementation head `c7d84a8a79a32b9ec2c2619edfb4af377ae4e8a5`; this documentation closeout requires one final exact-head CI before merge.

## Objective

Implement a provider-neutral deterministic safety-decision boundary for optional compute workers. Explicit configured sensor thresholds plus fresh observations produce reproducible normal/warning/critical/sensor-fault decisions and response requirements without an LLM inventing hardware limits or directly operating private machines.

This packet is policy/evidence only. It does not read real sensors, call private hardware APIs, stop workloads, drain a live scheduler, change worker registry state, power off hardware, send Wake-on-LAN, or claim a live safety path.

## Acceptance state

- M2-M1-027 compute observability: **merged as PR #142 at `20aa43c99e03cef8e9aa80817890d3484ea0f04f`; post-merge CI #542 PASS**.
- M2-M1-028 ID/branch collision check: **complete; no prior M2-M1-028 branch or PR existed**.
- Existing hardware-safety/sensor implementation search: **complete; no existing compute safety/thermal/sensor-threshold component found on current main**.
- Feature alignment: **complete; `LOCAL-001` is the scoped local-service integration anchor; `OBS-001` is read-only observability and does not become safety authority**.
- Threshold-source rule: **implemented; public code supplies no hardware threshold values**.
- Deterministic safety policy implementation: **complete in `mira/compute_safety.py`**.
- High-is-bad/low-is-bad exact threshold semantics: **implemented and synthetically tested**.
- Missing/stale/unit-mismatched required evidence fail-closed behavior: **implemented and synthetically tested**.
- Future timestamp and duplicate observation rejection: **implemented and synthetically tested**.
- Unknown extra observation non-authority: **synthetically tested**.
- Warning vs critical/sensor-fault response requirements: **implemented and synthetically tested**.
- Safe-shutdown requirement from explicit critical/fault booleans only: **implemented and synthetically tested**.
- Deterministic input-order behavior and bounded evidence shape: **synthetically tested**.
- Exact production ownership: **registered as one `compute-hardware-safety` component; code-ownership gate PASS in CI #544**.
- CI #543 on initial PR head `379abae1952b4ccc84b9c08d26a0c6095b4064d0`: **FAIL at work-session alignment only because branch metadata used singular `Primary feature`; compile, feature registry, product lifecycle and starter distribution passed; later gates were skipped**.
- Corrective metadata commit `c7d84a8a79a32b9ec2c2619edfb4af377ae4e8a5`: **changed only the machine-parsed field label to `Primary features`**.
- CI #544 on corrected implementation head `c7d84a8a79a32b9ec2c2619edfb4af377ae4e8a5`: **PASS end-to-end including work-session alignment, code ownership, Android proof/provenance/retention, Python unit tests and Workspace Apps Script tests**.
- Final documentation-closeout exact-head CI: **pending**.
- Merge/post-merge verification: **pending**.
- Live sensor/shutdown/private deployment evidence: **not claimed and out of scope**.

## Session-start alignment verification — 2026-09-09

### `FEATURES.md`

`LOCAL-001` requires an explicit local-service bridge with scoped permissions, verified capability/readback and no blanket LAN trust. Hardware safety is a required integrity boundary before private compute lifecycle execution can be trusted. `OBS-001` remains a read-only operational projection and is related only because later telemetry will expose safety state; it is not used as mutable safety authority.

### `BACKLOG.md`

`LOCAL-INTEGRATIONS` remains the accepted compute-fabric work anchor explicitly reprioritized by the product owner. M2-M1-028 continues that bounded initiative rather than inventing a second work authority.

### `ROADMAP.md`

Advanced/self-hosted infrastructure remains optional. A deterministic safety policy is reusable infrastructure and does not make private compute or hardware administration a Standard-path prerequisite.

### Reuse and boundary review

- `mira.service_state.WorkerRegistryView` owns worker operational truth but does not define hardware threshold semantics.
- `mira.compute_observability` is read-only telemetry and must not mutate or decide hardware safety.
- `mira.compute_safety` now owns configured sensor-policy/evidence evaluation only.
- Later private adapters may supply observations; later lifecycle/power control may execute response requirements. M2-M1-028 owns neither provider I/O nor physical action.

### Safety result

Thresholds and shutdown eligibility are explicit configuration. Missing/stale required evidence fails closed. Critical/sensor-fault decisions require workload stop + node fault semantics; safe-shutdown requirement is explicit policy, never model judgment.

### Direction result

ALIGNED

## Exact next action / resume point

1. Run final exact-head CI on the documentation-closeout head.
2. Re-read remote `main`, PR #143 head/mergeability and changed-file overlap.
3. Mark PR #143 ready and merge only if final exact-head CI is green, using expected-head protection.
4. Read back merged remote `main` and verify post-merge CI before claiming integration verification.
5. After M2-M1-028 closes, select the next dependency-ranked compute-fabric child packet from current Git state rather than chat history.

## Recovery protocol

Resume from current remote `main`, branch `work/m2-m1-028-hardware-safety`, this `CURRENT_WORK.md`, `docs/work-packets/M2-M1-028.md`, PR #143, and the latest branch head. Do not reopen M2-M1-021 through M2-M1-027 unless regression evidence requires it.
