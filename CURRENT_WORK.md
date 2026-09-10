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
- **Packet:** `docs/work-packets/M2-M1-033.md`.
- **Pull request:** pending.
- **Owned implementation surfaces:** new `mira/studio_activation.py`, new `tests/test_studio_activation.py`, packet doc, branch-local `CURRENT_WORK.md`, and the narrow `project/code_ownership.json` registration required for the new production module.
- **Shared/high-contention surfaces:** no Google Workspace/Sheets, People Discovery, finance, Android, private-runner, feature-sharing/import or final Studio UX implementation surface is owned by this packet.
- **Current status:** branch created from integration-verified M2-M1-032 merge; implementation pending.

## Objective

Close the remaining bounded `SKILL-BUILDER-001` execution seam without inventing provider-specific Git policy. Consume an explicit `StudioActivationPlan` from M2-M1-032, require independently verified source WRITE and REMOTE_READBACK capability, preflight the exact current source revision, call only an injected source-mutation adapter, require exact remote readback, emit deterministic activation evidence, and support explicit rollback to the recorded prior revision/state with the same stale-state and readback protections.

This packet does not choose a source lane, invoke a model, create candidate code, publish/import a feature, implement final Studio UX, bypass branch protection, execute arbitrary shell, or claim live provider mutation unless separately demonstrated.

## Session-start alignment verification — 2026-09-10

### `FEATURES.md`

`DEV-004` requires bounded custom feature creation; `STUDIO-001` requires preview/test/rollback, source provenance and no silent activation. M2-M1-031 and M2-M1-032 established reviewed candidate selection and explicit approval, but M2-M1-032 intentionally stops at an inert activation plan.

### `BACKLOG.md`

`SKILL-BUILDER-001` remains queued. `SOURCE-GATES-001` is complete at provider-neutral capability-evidence semantics but explicitly does not claim live provider mutation. `FEATURE-SHARE-001` and `MIRA-STUDIO-001` remain later dependencies; sharing should not start while the private Skill Builder cannot yet apply/verify/rollback an approved change.

### `ROADMAP.md`

The packet preserves provider-neutral source semantics and the default Personal no-server path. It adds no local infrastructure requirement and does not change canonical data authorities.

### Reuse and boundary review

- `mira.studio_competition` remains the authority for reviewed candidate provenance, staged preview/test/rollback evidence and explicit approval.
- `mira.service_state` remains the authority for SOURCE-001 capability evidence and independent WRITE / REMOTE_READBACK gates.
- M2-M1-033 composes those authorities. It does not duplicate them.
- Source-lane selection remains separate under `SOURCE-LANES-001`; the adapter is injected by a later routing/deployment layer.
- Real Git/provider credentials, branch policies and resource identifiers remain outside public contracts.

### Direction result

ALIGNED

## Acceptance criteria

1. Activation requires a valid `StudioActivationPlan`; unapproved staged decisions cannot reach this boundary.
2. Activation requires an independently evaluated provider capability decision with both WRITE and REMOTE_READBACK allowed; authorization/read-only evidence is insufficient.
3. Capability provider/service identity is bound to an explicit source-target descriptor without credentials or private provider payloads.
4. Exact preflight read must report the plan base revision before any write; stale current source fails closed with zero mutation.
5. The injected adapter receives the exact approved proposal identity/source digest and expected current revision; the core never constructs provider-specific shell/Git commands.
6. After mutation, exact remote readback is mandatory. Success requires an applied revision plus source/state digest matching the approved proposal material defined by the adapter contract.
7. Write success without matching remote readback is not activation success and produces a deterministic recovery-required result.
8. Activation receipts preserve packet/work/change/approver/proposal/base/applied revision, source digest and source-target provenance without secrets.
9. Replaying an already verified activation is deterministic/idempotent and performs zero additional mutation when exact readback already matches the recorded applied state.
10. Rollback is explicit; activation does not automatically roll itself back without a caller instruction.
11. Rollback requires exact current applied revision, verified WRITE + REMOTE_READBACK gates, and the M2-M1-032 rollback anchor from the activation plan.
12. Rollback writes only toward the recorded prior revision/state identity and requires exact remote readback before reporting success.
13. Stale rollback current state fails closed with zero mutation; rollback readback mismatch is recovery-required, not success.
14. Adapter exceptions are converted to deterministic fail-closed execution results without fabricating remote state.
15. Public contracts expose no credentials, tokens, provider endpoints, host identities, shell commands, runner labels or private network details.
16. Direct adversarial tests cover capability denial, stale preflight, activation success, replay/no-op, readback mismatch, adapter failure, rollback success, rollback stale state and rollback readback mismatch.
17. Existing M2-M1-031/032 Studio tests remain green and full repository CI passes on the exact packet head before merge, followed by exact post-merge CI.

## Exact next action / resume point

1. Implement `mira/studio_activation.py` as a provider-neutral execution boundary over injected source adapter operations.
2. Add direct adversarial tests in `tests/test_studio_activation.py`.
3. Register the new production module in `project/code_ownership.json` with direct verification.
4. Run targeted Studio tests and full repository gates; fix only packet-scoped failures.
5. Record exact implementation evidence, open a bounded draft PR, require exact-head CI, reconcile current `main`, merge with expected-head protection, and require post-merge exact-SHA CI.
6. Only after integration verification decide whether `SKILL-BUILDER-001` is complete enough to unblock `FEATURE-SHARE-001` and final `MIRA-STUDIO-001`.

## Evidence ceiling

Specified and branch-checkpointed only. No source mutation, activation, rollback, provider/model invocation, publication/import or final Studio UX is claimed.

## Recovery protocol

Resume from remote `main`, branch `work/m2-m1-033-studio-activation-execution`, this file, `docs/work-packets/M2-M1-033.md`, and the latest remote branch head. Do not reconstruct implementation state from chat when Git records it.
