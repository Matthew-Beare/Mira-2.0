# MIRA 2.0 CURRENT WORK

Git is authoritative. This branch records exactly one active packet.

## Active packet

### `M2-M1-041` — Studio local execution vertical

- **Primary work:** `MIRA-STUDIO-001`.
- **Primary features:** `STUDIO-001`, `DEV-004`, `SOURCE-001`, `PROVIDER-001`, `RECOVERY-002`.
- **Repository:** `Matthew-Beare/Mira-2.0`.
- **Branch:** `work/m2-m1-041-studio-execution-vertical`.
- **Base SHA:** `9303431bb3e573f2a241f6796a2d3da2918527fc`.
- **Packet:** `docs/work-packets/M2-M1-041.md`.

## Customer outcome

Move MIRA Studio from reviewed data structures toward an executable software-engineering loop. A review-ready Studio request must be able to hand bounded implementation work to a local worker that creates an isolated Git worktree/branch, invokes only an explicitly configured loopback model endpoint, applies only allowed file replacements, runs fixed customer/controller-owned tests, performs bounded repair rounds, and produces durable evidence without merging or activating anything.

The customer remains product owner. MIRA owns implementation choices unless they materially change user-visible behavior, privacy/safety, cost, irreversible state, or acceptance criteria.

## Prior packet closeout

`M2-M1-038` / PR #153 merged to `main` at `9303431bb3e573f2a241f6796a2d3da2918527fc`. Exact post-merge CI #618 completed successfully on that exact SHA. Ordinary-language Studio intake is therefore integration-verified at its stated evidence ceiling. Live model invocation and implementation execution were intentionally outside that packet and are admitted here as the next vertical gap.

## Scope

Implement one real local execution path under `ops/` and deterministic tests. Reuse existing Studio contracts, compute-policy concepts and Git authority. Do not create a competing canonical data model or a second roadmap.

The local worker will:

1. require an explicit repo path, exact base SHA, branch name, bounded editable-path allowlist, fixed test argv, model identifier and loopback OpenAI-compatible endpoint;
2. create an isolated Git worktree and branch from the recorded base SHA;
3. send bounded source/spec/test-failure context to the configured local model;
4. accept only a strict JSON file-replacement response for allowlisted paths, never model-generated commands or paths outside the allowlist;
5. run tests with `shell=False`, bounded timeout and durable per-round evidence;
6. stop on green, regression/stagnation/round/time ceilings, or malformed model output;
7. leave the source repository/main untouched and never merge, push, activate, install, publish, or use hosted fallback;
8. emit a machine-readable result containing branch/worktree, tested commit/tree identity, changed paths, test evidence and stop reason.

A real LM Studio/live local-model run is a separate live-verification gate because this environment cannot truthfully prove the user's private worker runtime.

## Acceptance criteria

1. Worker can execute end to end against a temporary real Git repository and fake loopback OpenAI-compatible model server in automated tests.
2. Base SHA mismatch, dirty/unsafe repository state, non-loopback endpoint, invalid branch/path input and symlink/path escape fail closed.
3. Model cannot choose commands, test argv, repo, branch, endpoint or paths outside the allowlist.
4. Tests execute with `shell=False`, timeout, stdout/stderr capture and exact candidate identity.
5. Bounded repair loop records each tested candidate and stops correctly on pass, stagnation, regression, malformed response, round ceiling or wall-clock ceiling.
6. Successful candidate remains on an isolated branch/worktree for Studio review; no merge/push/activation occurs.
7. Existing full repository CI remains green.
8. Exact-head and post-merge CI/readback gates are satisfied before closure.

## Session-start alignment verification — 2026-09-12

### `FEATURES.md`

This packet advances existing `STUDIO-001` / `DEV-004`; it does not invent a new product vertical. `SOURCE-001` and `PROVIDER-001` already require verified source/runtime capability boundaries. The missing value is executable composition of those accepted requirements.

### `BACKLOG.md`

`MIRA-STUDIO-001` is the existing user-facing Studio vertical. `SKILL-BUILDER-001` is already test-verified through staged/activation machinery but explicitly leaves live model invocation and provider-specific source mutation as separate evidence. `STUDIO-INTAKE-001` has now merged through PR #153. Therefore the highest-leverage next work is the execution gap inside existing `MIRA-STUDIO-001`, not another abstract boundary packet.

### `ROADMAP.md`

Direction is unchanged: finish infrastructure sufficiently to support a usable Studio vertical. This packet prioritizes executable end-to-end leverage over additional architecture-only decomposition.

### Idea/backlog capture audit

CAPTURE AUDIT COMPLETE

- No novel product idea is introduced. The customer reiterated the already-canonical `STUDIO-001` outcome: MIRA should behave as the software team and turn ordinary-language intent into bounded implementation work.
- Existing canonical disposition: `MIRA-STUDIO-001` / `STUDIO-001` / `DEV-004`.
- Implementation gap selected: real bounded local execution between review-ready Studio intent and existing review/activation machinery.
- No unrelated feature is admitted.

### Direction result

ALIGNED

## Exact next action / resume point

1. Add the bounded local Studio worker under `ops/` plus adversarial integration tests.
2. Exercise it against temporary real Git repositories and a fake loopback model server.
3. Run exact-head CI and repair only failures within packet scope.
4. After deterministic proof, decide whether one small glue change is required to emit the worker manifest directly from existing Studio intake/session state; include it only if needed for the vertical acceptance criteria.
5. Open/merge only after exact-head evidence; post-merge readback is mandatory.

## Evidence ceiling

Passing deterministic tests proves the executable worker protocol and real Git/test behavior in CI. It does not prove the user's private LM Studio instance, private hardware, credentials, or a provider-specific production source mutation. Those require later live evidence and must not be inferred from CI.