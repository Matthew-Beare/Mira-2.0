# MIRA 2.0 CURRENT WORK

Git is authoritative. This branch records exactly one active packet. Multiple other packet branches may be active repository-wide under `docs/CONCURRENT_WORK_POLICY.md`.

## Active packet

### `M2-M1-025` — Worker authentication and secure-channel boundary

- **Primary work:** `LOCAL-INTEGRATIONS`.
- **Primary features:** `LOCAL-001`, `API-001`.
- **Related invariants/features:** `RECOVERY-002`, `STORE-001`, `PROVIDER-001`.
- **Repository:** `Matthew-Beare/Mira-2.0`.
- **Branch:** `work/m2-m1-025-worker-auth-boundary`.
- **Base SHA:** `28dd86679cef8f69579134b7541bcc45dad9984e`.
- **Packet:** `docs/work-packets/M2-M1-025.md`.
- **Owned implementation surfaces:** `mira/http_transport.py`, `tests/test_compute_worker_auth.py`, packet doc, branch-local `CURRENT_WORK.md`.
- **Shared/high-contention surfaces:** none planned. `project/code_ownership.json`, `FEATURES.md`, `BACKLOG.md`, and `ROADMAP.md` are not modified.
- **Current status:** packet started from post-merge-CI-verified `main`; implementation pending.

## Objective

Implement the missing provider-neutral worker authentication boundary that converts restricted credential and secure-channel evidence into the existing secret-free `WorkerRegistryIdentityEvidence` contract.

The boundary must bind one credential to one worker and principal, store only credential verifiers, enforce expiry/revocation, reject unapproved or unauthenticated/unconfidential channel evidence, and fail closed on stale/future channel observations. It must remain separate from ordinary API client grants and must not expose an execution endpoint.

This packet does not deploy a network listener, configure mTLS/WireGuard, bind private hosts/IPs, expose raw shell/Python/inference, execute jobs, load models, control power, or claim live worker evidence.

## Acceptance state

- M2-M1-024 durable control plane: **merged as PR #139 at `28dd86679cef8f69579134b7541bcc45dad9984e`; post-merge CI #529 PASS**.
- M2-M1-025 ID/branch collision check: **complete; no prior M2-M1-025 code, PR, or branch existed**.
- Existing identity seam inspection: **complete; `runtime_router.py` consumes secret-free external identity proof and `service_state.py` persists secret-free worker registry evidence**.
- Existing transport/auth reuse inspection: **complete; `mira/http_transport.py` is the existing provider-neutral credential/transport boundary and is owned by the API component**.
- Concurrent PR review: **PR #134 and PR #135 remain drafts and currently non-mergeable against newer main; anticipated M2-M1-025 paths do not overlap them**.
- Worker-auth implementation/tests: **pending**.
- Exact-head CI/merge/post-merge verification: **pending**.
- Live worker/network/private deployment evidence: **not claimed and out of scope**.

## Session-start alignment verification — 2026-09-08

### `FEATURES.md`

Reviewed from verified main. `LOCAL-001` requires scoped network/service permissions, verified capability/readback, and no assumed cloud reachability or blanket LAN trust. `API-001` already owns the authenticated provider-neutral client/service boundary. The packet adds the missing restricted worker-auth seam without changing Standard MIRA into a local-infrastructure-dependent product.

### `BACKLOG.md`

Reviewed from verified main. `LOCAL-INTEGRATIONS` is the existing accepted anchor for `LOCAL-001` and was explicitly reprioritized by the product owner through the compute-fabric initiative. M2-M1-025 continues that accepted work rather than inventing a second network/security backlog authority.

### `ROADMAP.md`

Reviewed from verified main. Local/self-hosted infrastructure remains an Advanced optional lane; the ordinary Personal baseline requires no server/network administration. This packet therefore defines reusable authentication semantics only and does not make local compute a Standard-path prerequisite.

### Reuse review

`mira/http_transport.py` already owns bounded transport authentication, hashed bearer verifiers, expiry/revocation and HTTPS enforcement for ordinary clients. `mira/runtime_router.py` and `mira/service_state.py` already define the downstream secret-free worker identity contracts. The packet will extend the existing transport/auth surface rather than create a parallel authentication service.

### Collision/concurrency review

PR #134 owns People Discovery plus the monolithic ownership manifest. PR #135 owns Sheets plus ownership-fragment machinery. Neither overlaps the planned `mira/http_transport.py` and dedicated worker-auth test surface. The monolithic ownership manifest will not be touched.

### Direction result

ALIGNED

## Exact next action / resume point

1. Implement restricted worker credential/session and secure-channel evidence contracts in `mira/http_transport.py`.
2. Add synthetic adversarial tests in `tests/test_compute_worker_auth.py` for exact identity binding, verifier-only storage, expiry/revocation, secure-channel enforcement, evidence freshness and absence of execution/private-host surfaces.
3. Open a draft PR and run full exact-head CI.
4. Fix only packet-scoped failures, then reconcile current `main` and concurrent PR overlap before merge.
5. Merge with expected-head protection only after exact-head green CI; verify post-merge `main` CI before claiming integration verification.

## Recovery protocol

Resume from current remote `main`, branch `work/m2-m1-025-worker-auth-boundary`, this `CURRENT_WORK.md`, `docs/work-packets/M2-M1-025.md`, and the branch head. Do not reopen M2-M1-021 through M2-M1-024 unless regression evidence requires it.
