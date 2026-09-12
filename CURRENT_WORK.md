# MIRA 2.0 CURRENT WORK

Git is authoritative. This branch records exactly one active packet.

## Active packet

### `M2-M1-041` — Studio local execution vertical

- **Primary work:** `MIRA-STUDIO-001`.
- **Primary features:** `STUDIO-001`, `DEV-004`, `SOURCE-001`, `PROVIDER-001`, `RECOVERY-002`.
- **Related invariants/features:** `DEV-005`, `DEV-008`, `AUTH-001`.
- **Repository:** `Matthew-Beare/Mira-2.0`.
- **Branch:** `work/m2-m1-041-studio-execution-vertical`.
- **Base SHA:** `9303431bb3e573f2a241f6796a2d3da2918527fc`.
- **Packet:** `docs/work-packets/M2-M1-041.md`.

## Customer outcome

Move MIRA Studio from reviewed data structures to an executable software-engineering loop. Ordinary-language customer intent can now cross a trusted bridge into controller-owned execution policy and drive an isolated local implementation worker without requiring the customer to supply Git SHAs, paths, test commands, model endpoints, or worker budgets.

The customer remains product owner. MIRA owns implementation choices unless they materially change user-visible behavior, privacy/safety, cost, irreversible state, or acceptance criteria.

## Prior packet closeout

`M2-M1-038` / PR #153 merged to `main` at `9303431bb3e573f2a241f6796a2d3da2918527fc`. Exact post-merge CI #618 completed successfully on that exact SHA. Ordinary-language Studio intake is therefore integration-verified at its stated evidence ceiling.

## Implemented vertical

- `ops/studio_execution_bridge.py` binds only review-ready `StudioIntakeDraft` evidence to trusted controller-owned execution policy. Customer request, desired outcome, explicit constraints, assumptions, feature/dependency scope and intake projection identity are preserved; technical policy cannot rewrite them.
- `ops/studio_local_worker.py` validates an exact clean Git root/base SHA, creates an isolated worktree/branch, calls only an explicit loopback OpenAI-compatible model endpoint, accepts only strict JSON complete-file replacements for a canonical allowlist, and runs only fixed controller-owned test argv with `shell=False` and timeouts.
- Candidate changes are committed only on the isolated branch. The source checkout/main remain untouched. The worker has no merge, push, publish, install or activation authority and no hosted fallback.
- Repair is bounded by round and wall-clock ceilings and records baseline/per-round test evidence, model-response digest, changed paths, candidate SHA and stop reason.
- Adversarial handling covers non-loopback endpoints, dirty repositories, path traversal/noncanonical allowlists, model-selected outside paths, markdown/non-JSON output, stagnation, baseline regressions, round ceilings, direct symlinks and symlinked parent directories.
- Pre-merge review found and repaired a real path-safety flaw: recursive parent creation could follow a repository directory symlink and mutate its external target before validation rejected the escape. Parent components are now checked one at a time before creation, containment is reverified after each component, and replacement uses the same gate. The regression test requires the external symlink target to remain unmodified.

## CI / integration evidence

- CI #620 passed on exact head `7982c7c45cf792fd402a19acd5c7d70af8ff9315` after work-session metadata repair.
- CI #622 passed on exact head `a8a65af6792308c740b3d50a8bc41468c3fc30bb` after adding the review-ready-intake execution bridge.
- CI #624 passed on exact head `1a64e984734ec4c46a39de636c9f660aa741f81f` after symlink-parent hardening and its adversarial regression test. Compile, feature registry, lifecycle ledger, Personal starter distribution, work-session alignment, code ownership, Android proof, Python unit tests and Workspace tests all passed.
- This checkpoint itself changes the branch head, so one final exact-head CI run is mandatory before merge. Prior green runs are evidence, not permission to skip the final-head gate.

## Acceptance criteria

1. Worker executes end to end against a temporary real Git repository and fake loopback OpenAI-compatible model server. **PASS — CI #620/#622/#624.**
2. Base/clean-repo, non-loopback, invalid branch/path, direct symlink and symlink-parent escape gates fail closed. **PASS — adversarial tests; symlink-parent external target remains unmodified in CI #624.**
3. Model cannot choose commands, tests, repo, branch, endpoint or paths outside the allowlist. **PASS — worker schema/policy separation plus tests.**
4. Tests execute with `shell=False`, timeout, captured stdout/stderr and candidate identity. **PASS.**
5. Repair records each tested candidate and stops on pass, stagnation, regression, malformed output, round ceiling or wall-clock ceiling. **PASS for deterministic testable paths; wall-clock guard implemented and bounded.**
6. Successful candidate remains isolated for Studio review with no merge/push/activation. **PASS in real-Git integration test.**
7. Review-ready ordinary-language intake binds to execution without asking the customer for engineering plumbing. **PASS — execution bridge and tests in CI #622/#624.**
8. Existing full repository CI remains green. **PASS through CI #624; final checkpoint head pending.**
9. Exact-head and post-merge CI/readback gates are satisfied before closure. **PENDING final checkpoint CI + post-merge readback.**

## Session-start alignment verification — 2026-09-12

### `FEATURES.md`

This packet advances existing `STUDIO-001` / `DEV-004`; it does not invent a new product vertical. `SOURCE-001` and `PROVIDER-001` already require verified source/runtime capability boundaries. The missing value was executable composition of those accepted requirements.

### `BACKLOG.md`

`MIRA-STUDIO-001` is the existing user-facing Studio vertical. `SKILL-BUILDER-001` already supplied staged preview/test/rollback/approval machinery and `STUDIO-INTAKE-001` supplied the ordinary-language front door. This packet fills the next vertical gap by making review-ready intent executable on an isolated local branch rather than adding another review-only abstraction.

### `ROADMAP.md`

Direction is unchanged: finish infrastructure sufficiently to support a usable Studio vertical. This packet prioritizes executable end-to-end leverage over architecture-only decomposition.

### Idea/backlog capture audit

CAPTURE AUDIT COMPLETE

- No novel product vertical was introduced. The customer reiterated the already-canonical `STUDIO-001` outcome: MIRA acts as the software team and turns ordinary-language intent into bounded implementation work.
- Existing canonical disposition remains `MIRA-STUDIO-001` / `STUDIO-001` / `DEV-004`.
- Implementation-discovered requirement: generated code/tests must not be treated as safe to run with ambient host privileges. This is not silently admitted into this packet. Restricted worker identity/runtime isolation remains a hard infrastructure gate before production autonomous local execution can be live-verified.
- The current packet remains bounded to the execution protocol, real Git isolation, controller/model authority split and deterministic evidence.

### Direction result

ALIGNED

## Pre-merge checkpoint — 2026-09-12

### Idea/backlog capture audit

CAPTURE AUDIT COMPLETE

- Studio intake-to-execution glue was required to satisfy the packet's customer-facing vertical outcome and remains inside existing `MIRA-STUDIO-001` scope.
- The symlink-parent flaw was a safety defect inside this packet and was repaired rather than deferred.
- Host-level restricted worker isolation is deliberately not claimed or implemented here; it is the next infrastructure dependency before private live-model execution is considered production-safe.
- No unrelated feature work was admitted.

## Exact next action / resume point

1. Require final exact-head CI green on this checkpoint commit.
2. Re-read remote `main` and PR #157 head/mergeability immediately before merge.
3. Mark PR #157 ready and merge only with expected-head protection if the exact head is green and `main` remains compatible.
4. Read back exact post-merge `main` and require post-merge CI success before closing M2-M1-041.
5. Then rank the next Studio/infrastructure packet around restricted local worker identity/runtime isolation and existing compute-control-plane integration before any claim of production-safe autonomous LM Studio execution.

## Evidence ceiling

Passing CI proves the executable worker protocol, ordinary-language-intake bridge, real Git/worktree behavior, strict loopback/model-output boundary and deterministic test/evidence behavior in CI. It does not prove the user's private LM Studio instance, private hardware, credentials, provider-specific production mutation, or host-level containment of arbitrary generated code. Those require later restricted-runtime implementation and live verification and must not be inferred from this packet.