# MIRA 2.0 CURRENT WORK

Git is authoritative. This branch records exactly one active packet. Multiple other packet branches may be active repository-wide under `docs/CONCURRENT_WORK_POLICY.md`.

## Active packet

### `M2-M1-026` — Trusted self-hosted CI boundary

- **Primary work:** `LOCAL-INTEGRATIONS`.
- **Primary features:** `LOCAL-001`, `DEV-004`.
- **Related invariants/features:** `DEV-001`, `RECOVERY-002`, `DIST-001`, `API-001`.
- **Repository:** `Matthew-Beare/Mira-2.0`.
- **Branch:** `work/m2-m1-026-trusted-self-hosted-ci`.
- **Base SHA:** `c6692b014cc17508e8334e2b524b64b428857b21`.
- **Packet:** `docs/work-packets/M2-M1-026.md`.
- **Owned implementation surfaces:** `project/ci_trust.py`, `tests/test_ci_trust.py`, `.github/workflows/trusted-runner-gate.yml`, packet doc, branch-local `CURRENT_WORK.md`.
- **Shared/high-contention surfaces:** no `mira/` production module, `project/code_ownership.json`, `FEATURES.md`, `BACKLOG.md`, `ROADMAP.md`, or existing `CI` workflow modification.
- **Current status:** deterministic trust policy, GitHub-hosted preflight workflow and adversarial tests implemented on branch; draft PR and full repository CI pending.

## Objective

Implement a deterministic trust boundary that prevents arbitrary public fork/PR code from being treated as eligible for private self-hosted execution. Source/origin trust and runner isolation remain independent evidence. A trusted canonical-main source may advance only to `requires_isolation` until a restricted/isolated runner is separately proven; PR/fork code remains hosted-only even if an isolation claim is present.

This packet adds a GitHub-hosted preflight evidence workflow only. It does not target, install, register, configure, wake, or execute code on any private/self-hosted runner. It does not commit private runner labels, hostnames, addresses, credentials, LAN topology, or hardware identities.

## Acceptance state

- M2-M1-025 worker authentication/security boundary: **merged as PR #140 at `c6692b014cc17508e8334e2b524b64b428857b21`; post-merge CI #533 PASS**.
- M2-M1-026 ID/branch collision check: **complete; no prior M2-M1-026 branch or PR existed**.
- Existing CI inspection: **complete; current CI is GitHub-hosted only, `contents: read`, with no self-hosted job**.
- Existing self-hosted trust implementation search: **complete; no existing source/origin/runner trust gate found**.
- Compute-fabric child ordering: **confirmed from `M2-M1-021`; Trusted self-hosted CI is child #4 after worker security**.
- Deterministic source-trust and runner-isolation policy: **implemented on branch**.
- GitHub-hosted preflight receipt workflow: **implemented on branch; never targets `self-hosted` and never executes triggering candidate source to determine trust**.
- Adversarial local policy checks: **PASS before commit for trusted-main, missing/safe/unsafe isolation, same-repo PR, fork PR, non-main push, failed CI, wrong workflow and malformed provenance cases**.
- Repository exact-head CI/merge/post-merge verification: **pending**.
- Live private runner evidence: **not claimed and out of scope**.

## Session-start alignment verification — 2026-09-08

### `FEATURES.md`

`LOCAL-001` remains the accepted optional local/private integration bridge; `DEV-004` and `DEV-001` support bounded Git-backed development and repository authority. The packet strengthens the development trust boundary without making local infrastructure a Standard-path dependency.

### `BACKLOG.md`

`LOCAL-INTEGRATIONS` remains the existing accepted anchor explicitly reprioritized by the product owner for the compute-fabric initiative. No new backlog identity is required for this bounded child packet.

### `ROADMAP.md`

Advanced/self-hosted infrastructure remains optional and downstream of the ordinary Personal baseline. This packet adds only reusable trust evidence and does not deploy private infrastructure.

### Reuse review

`.github/workflows/ci.yml` already provides GitHub-hosted exact-head CI and is intentionally left unchanged. `M2-M1-026` layers a separate GitHub-hosted `workflow_run` preflight over completed CI evidence rather than replacing CI or allowing untrusted code to schedule itself directly onto a private runner.

### Security result

- Source trust and runner isolation are separate facts.
- Pull-request/fork source is never private-runner eligible.
- A successful canonical `push` to `main` may become source-trusted but still requires independent runner isolation evidence.
- The preflight workflow itself executes only on GitHub-hosted infrastructure with read-only repository permission and no repository secrets.
- The preflight workflow does not execute the triggering candidate source to decide whether that source is trusted; policy code is checked out from the repository default branch and its policy SHA is recorded.
- The emitted receipt is evidence only and is never itself a scheduling credential.

### Direction result

ALIGNED

## Exact next action / resume point

1. Open a draft PR from exact branch head after final branch diff/readback.
2. Run full exact-head repository CI and inspect any packet-scoped failure.
3. Verify workflow-shape tests and trust-policy adversarial tests pass in repository CI.
4. Reconcile current `main` and concurrent PR overlap before merge.
5. Merge only after exact-head green CI, then verify post-merge `main` CI before claiming integration verification.

## Recovery protocol

Resume from current remote `main`, branch `work/m2-m1-026-trusted-self-hosted-ci`, this `CURRENT_WORK.md`, `docs/work-packets/M2-M1-026.md`, and the latest branch head. Do not reopen M2-M1-021 through M2-M1-025 unless regression evidence requires it.
