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
- **Pull request:** `#140`.
- **Owned implementation surfaces:** `mira/http_transport.py`, `tests/test_compute_worker_auth.py`, packet doc, branch-local `CURRENT_WORK.md`.
- **Shared/high-contention surfaces:** none modified. `project/code_ownership.json`, `FEATURES.md`, `BACKLOG.md`, and `ROADMAP.md` remain untouched.
- **Current status:** implementation and adversarial synthetic tests complete on branch; CI #530 passed end-to-end on implementation head `879cd19516ffb235355766ca1b895e2cc5dbc49e`; documentation closeout requires one final exact-head CI before merge.

## Objective

Implement the missing provider-neutral worker authentication boundary that converts restricted credential and trusted secure-channel evidence into the existing secret-free `WorkerRegistryIdentityEvidence` contract.

The boundary binds one credential to one worker and principal, stores only credential verifiers, enforces expiry/revocation, rejects unapproved or unauthenticated/unconfidential channel evidence, and fails closed on stale/future channel observations. It remains separate from ordinary API client grants and exposes no execution endpoint.

`WorkerChannelEvidence` is an internal trusted transport observation. A later live listener must derive it from the actual authenticated connection context and must never trust worker-supplied booleans/channel labels as proof.

This packet does not deploy a network listener, configure mTLS/WireGuard, bind private hosts/IPs, expose raw shell/Python/inference, execute jobs, load models, control power, or claim live worker evidence.

## Acceptance state

- M2-M1-024 durable control plane: **merged as PR #139 at `28dd86679cef8f69579134b7541bcc45dad9984e`; post-merge CI #529 PASS**.
- M2-M1-025 ID/branch collision check: **complete; no prior M2-M1-025 code, PR, or branch existed**.
- Existing identity seam inspection: **complete; `runtime_router.py` consumes secret-free external identity proof and `service_state.py` persists secret-free worker registry evidence**.
- Existing transport/auth reuse inspection: **complete; `mira/http_transport.py` is the existing provider-neutral credential/transport boundary and is owned by the API component**.
- Worker credential/verifier boundary: **implemented on branch**.
- Exact worker/principal binding + TTL/revocation: **implemented and synthetically tested**.
- Explicit secure-channel allowlist + peer-authentication/confidentiality/freshness checks: **implemented and synthetically tested**.
- Generic API grant separation: **implemented and synthetically tested**.
- Raw worker execution route absence: **synthetically tested**.
- Private-host/secret-free metadata shape: **synthetically tested**.
- CI #530 on implementation head `879cd19516ffb235355766ca1b895e2cc5dbc49e`: **PASS end-to-end**.
- Final documentation-closeout exact-head CI: **pending**.
- Merge/post-merge verification: **pending**.
- Live worker/network/private deployment evidence: **not claimed and out of scope**.

## Session-start alignment verification — 2026-09-08

### `FEATURES.md`

Reviewed from verified main. `LOCAL-001` requires scoped network/service permissions, verified capability/readback, and no assumed cloud reachability or blanket LAN trust. `API-001` already owns the authenticated provider-neutral client/service boundary. The packet adds the missing restricted worker-auth seam without changing Standard MIRA into a local-infrastructure-dependent product.

### `BACKLOG.md`

Reviewed from verified main. `LOCAL-INTEGRATIONS` is the existing accepted anchor for `LOCAL-001` and was explicitly reprioritized by the product owner through the compute-fabric initiative. M2-M1-025 continues that accepted work rather than inventing a second network/security backlog authority.

### `ROADMAP.md`

Reviewed from verified main. Local/self-hosted infrastructure remains an Advanced optional lane; the ordinary Personal baseline requires no server/network administration. This packet therefore defines reusable authentication semantics only and does not make local compute a Standard-path prerequisite.

### Reuse review

`mira/http_transport.py` already owns bounded transport authentication, hashed bearer verifiers, expiry/revocation and HTTPS enforcement for ordinary clients. `mira/runtime_router.py` and `mira/service_state.py` already define the downstream secret-free worker identity contracts. M2-M1-025 extends the existing transport/auth surface rather than create a parallel authentication service.

### Collision/concurrency review

PR #134 owns People Discovery plus the monolithic ownership manifest. PR #135 owns Sheets plus ownership-fragment machinery. Neither overlaps `mira/http_transport.py` and the dedicated worker-auth test surface. The monolithic ownership manifest is not modified.

### Direction result

ALIGNED

## Exact next action / resume point

1. Run final exact-head CI after this documentation closeout.
2. Re-read remote `main`, PR #140 head/mergeability and changed-file overlap.
3. Mark PR #140 ready and merge only if exact-head CI is green, using expected-head protection.
4. Read back merged `main` and verify post-merge CI before claiming integration verification.
5. After M2-M1-025 closes, select the next dependency-ranked compute-fabric child packet from current Git state rather than chat history.

## Recovery protocol

Resume from current remote `main`, branch `work/m2-m1-025-worker-auth-boundary`, this `CURRENT_WORK.md`, `docs/work-packets/M2-M1-025.md`, PR #140, and the branch head. Do not reopen M2-M1-021 through M2-M1-024 unless regression evidence requires it.
