# MIRA 2.0 CURRENT WORK

Git is authoritative. This branch records exactly one active packet. Multiple other packet branches may be active repository-wide under `docs/CONCURRENT_WORK_POLICY.md`.

## Active packet

### `M2-M1-033` — Studio approved activation and rollback execution boundary

- **Primary work:** `SKILL-BUILDER-001`.
- **Primary features:** `STUDIO-001`, `DEV-004`.
- **Related invariants/features:** `SOURCE-001`, `PROVIDER-001`, `DEV-001`, `DEV-002`, `DEV-005`, `DEV-006`, `DIST-001`, `RECOVERY-002`.
- **Repository:** `Matthew-Beare/Mira-2.0`.
- **Branch:** `work/m2-m1-033-studio-activation-execution`.
- **Base SHA:** `344b58b8332751e42a8d30cd62ffee3539714d6c`.
- **Exact implementation head:** `1723b7d2297a3e39d927cb54e967393be30fa1ac`.
- **Packet:** `docs/work-packets/M2-M1-033.md`.
- **Pull request:** `#148` (draft pending final documentation-closeout CI).
- **Owned implementation surfaces:** new `mira/studio_activation.py`, new `tests/test_studio_activation.py`, packet doc, branch-local `CURRENT_WORK.md`, and the narrow `project/code_ownership.json` registration required for the new production module.
- **Shared/high-contention surfaces:** no Google Workspace/Sheets, People Discovery, finance, Android, private-runner, feature-sharing/import or final Studio UX implementation surface is owned by this packet.
- **Current status:** implementation and direct adversarial tests complete; exact implementation-head CI #570 / run `34518411189` PASS end-to-end; final documentation closeout now requires its own exact-head CI before merge.

## Objective

Close the remaining bounded `SKILL-BUILDER-001` execution seam without inventing provider-specific Git policy. Consume an explicit `StudioActivationPlan` from M2-M1-032, require independently verified source READ, WRITE and REMOTE_READBACK capability, preflight exact current source state, call only an injected source-mutation adapter, require exact post-write remote readback, emit deterministic activation evidence, and support explicit rollback to the recorded prior revision/state with the same stale-state and readback protections.

This packet does not choose a source lane, invoke a model, create candidate code, publish/import a feature, implement final Studio UX, bypass branch protection, execute arbitrary shell, or claim live provider mutation.

## Acceptance state

- M2-M1-032 staged preview/test/rollback plus explicit approval planning: **merged at `344b58b8332751e42a8d30cd62ffee3539714d6c`; post-merge CI #569 PASS**.
- `SOURCE-GATES-001`: **complete/test-verified provider-neutral capability evidence authority; no live mutation implied**.
- Provider-neutral `StudioSourceAdapter` protocol plus explicit source target/state/mutation result contracts: **implemented**.
- Activation requires an existing `StudioActivationPlan`; this boundary creates no approval authority: **implemented and directly tested**.
- Independent READ, WRITE and REMOTE_READBACK gates plus provider/service identity must all pass before preflight: **implemented and directly tested**.
- Missing/denied/ambiguous capability evidence blocks with zero source access or mutation: **implemented and directly tested**.
- Exact preflight revision and recorded rollback-state digest are checked before mutation; stale state blocks with zero write: **implemented and directly tested**.
- Adapter receives exact change ID, expected current revision, reviewed proposal revision and reviewed source digest: **implemented and directly tested**.
- Adapter exceptions after a mutation attempt become `recovery_required` with unknown outcome rather than fabricated clean failure: **implemented and directly tested**.
- Mutation/readback evidence distinguishes `not_attempted`, `performed`, and `unknown`: **implemented and directly tested**.
- Activation succeeds only after exact remote readback matches the adapter-returned applied revision/source/state and the source digest matches the approved source digest: **implemented and directly tested**.
- Applied target revision is intentionally distinct from reviewed proposal revision because merge/cherry-pick adapters may create a new target commit; exact proposal SHA/source digest are still passed to the adapter and the approved source digest remains success authority: **reviewed and preserved intentionally**.
- Verified activation replay is zero-write when current remote state exactly matches the prior successful receipt: **implemented and directly tested**.
- Rollback is explicit only; successful activation does not auto-rollback: **implemented**.
- Explicit rollback requires a successful matching activation receipt, current applied state equality, verified capability and the original plan rollback anchor: **implemented and directly tested**.
- Rollback stale state blocks with zero write; write/readback uncertainty becomes recovery-required rather than success: **implemented and directly tested**.
- Activation/rollback receipts are deterministic and preserve bounded packet/work/change/approver/source-target/revision/digest evidence without credentials or private execution material: **implemented and directly tested**.
- Public execution contracts exclude credentials, tokens, provider endpoints, host/IP/network identities, shell commands, runner labels and model paths: **implemented and directly tested**.
- Direct adversarial suite: **20 test methods in `tests/test_studio_activation.py`; repository Python unit-test gate PASS on exact implementation head**.
- Code ownership: **new `studio-activation-execution` component registered; ownership gate PASS on exact implementation head**.
- Base→implementation diff: **exactly five declared files; five commits ahead and zero behind at implementation-head reconciliation**.
- Exact implementation-head repository CI #570 / run `34518411189` on `1723b7d2297a3e39d927cb54e967393be30fa1ac`: **PASS end-to-end**, including compile, feature registry, product lifecycle ledger, Personal starter distribution, work-session alignment, code ownership, Android unit/proof build/provenance/retention, Python unit tests and Workspace Apps Script tests.
- Final documentation-closeout exact-head CI: **pending**.
- Merge/post-merge integration verification: **pending**.
- Live Git/provider activation or rollback: **not claimed and out of scope**.

## Session-start alignment verification — 2026-09-10

### `FEATURES.md`

`DEV-004` requires bounded custom feature creation; `STUDIO-001` requires preview/test/rollback, source provenance and no silent activation. M2-M1-031 and M2-M1-032 established reviewed candidate selection and explicit approval. M2-M1-033 adds the bounded execution seam beneath Studio without expanding into final UX or sharing.

### `BACKLOG.md`

`SKILL-BUILDER-001` remains queued until this execution seam is merged and post-merge verified. `FEATURE-SHARE-001` and `MIRA-STUDIO-001` remain later dependencies; their work is not pulled into this packet.

### `ROADMAP.md`

The packet preserves provider-neutral source semantics and the default Personal no-server path. It adds no local infrastructure requirement and does not change canonical MIRROR data authorities.

### Reuse and boundary review

- `mira.studio_competition` remains the authority for reviewed candidate provenance, staged preview/test/rollback evidence and explicit approval.
- `mira.service_state` remains the authority for SOURCE-001 capability evidence and independent READ / WRITE / REMOTE_READBACK gates.
- `mira.studio_activation` composes those authorities through an injected adapter rather than duplicating them.
- Source-lane selection remains separate under `SOURCE-LANES-001`; no GitHub/personal/organization/managed/no-Git selection policy is hard-coded here.
- Real Git/provider credentials, branch policies, provider endpoints and private resource bindings remain outside public contracts.
- Open People Discovery PR #134 and Sheets control-surface PR #135 own unrelated surfaces and are untouched.

### Direction result

ALIGNED

## Exact next action / resume point

1. Commit the packet documentation closeout without changing implementation semantics.
2. Run final exact-head CI on the documentation-closeout head.
3. Re-read current remote `main`, PR #148 exact head/mergeability and changed-file overlap.
4. If final exact-head CI is green and no incompatible main movement appeared, mark PR #148 ready and merge using expected-head protection.
5. Read back merged remote `main` and verify post-merge CI on the exact merge SHA before claiming integration verification.
6. Only after integration verification reconcile whether `SKILL-BUILDER-001` is complete enough to unblock `FEATURE-SHARE-001` and final `MIRA-STUDIO-001`.
7. Preserve the evidence ceiling: provider-neutral synthetic/source-adapter execution semantics only; no live Git/provider mutation claim.

## Evidence ceiling

Implemented and exact implementation-head repository-test verified only. The packet provides provider-neutral activation/rollback execution semantics over an injected adapter. No live Git/provider source mutation, feature activation, rollback, model invocation, feature publication/import, final Studio UX or private-runner execution is claimed.

## Recovery protocol

Resume from remote `main`, branch `work/m2-m1-033-studio-activation-execution`, this file, `docs/work-packets/M2-M1-033.md`, PR #148, and the latest remote branch head. Do not reconstruct implementation state from chat when Git records it.
