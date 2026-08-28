# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and its exact resume point.

## Completed packet before this branch

### `M2-G0-008E` — Android/mobile client boundary audit — legacy G10

- **Merged PR:** #32
- **Merge SHA / main readback:** `4403af395c56677d30c9cfcae811057933ad27ce`
- **Post-merge completion checkpoint / this branch start SHA:** `c7b9c1269939a41f12172eedf96010251847b664`
- **Result:** `CLIENT-ANDROID-001` is canonical; Android remains a shared-`API-001` client and direct provider-authority mutation is rejected.

## Active packet

- **Packet ID:** `M2-G0-008F`
- **Name:** Machine-readable feature catalog and code-ownership integrity audit — legacy G19 + G20
- **Class:** forensic audit / governance and release-integrity prerequisite
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `audit/g0-008f-catalog-code-integrity`
- **Branch start SHA:** `c7b9c1269939a41f12172eedf96010251847b664`
- **Activation commit:** `d25063b86006ac3d79b8ddb122189fc88f1205d0`
- **Status:** forensic research complete and checkpointed by this commit; feature/backlog normalization next.

## Source-ledger mapping and ranking decision

The remaining source rows were recovered from legacy `MIRA-Personal-Production/docs/feature-ledger-2026-08-24.md`.

- **F21:** Custom skill/automation builder.
- **F22:** Activity trackers/wearable data.
- **F23:** Explicit weather-in-briefs onboarding.
- **G2-G6:** provider portability, regulated lane, release channels and eventual SQL.
- **G8-G9:** observability and object/evidence storage.
- **G11-G15:** Home Assistant, Plex, voice, private-service/VPN and family-site infrastructure.
- **G19:** hierarchical machine-readable feature catalog with CI drift enforcement.
- **G20:** machine-enforced production-code inventory and anti-bloat ownership gate.

G19 + G20 outrank the other remaining rows because they are repository/release-integrity foundations that support dependency closeout and safe implementation growth. Optional/later infrastructure does not outrank them; F23 remains current-required but user-visible rather than foundational.

## Canonical G19 findings

1. Legacy G19 has real executable/test evidence. `scripts/feature_catalog.py` parses `docs/feature-ledger-2026-08-24.md`, computes a SHA-256 of that source, generates `docs/feature-catalog.json` and `docs/feature-catalog.md`, validates evidence paths and fails `--check` on generated-file drift.
2. Legacy `.github/workflows/ci.yml` explicitly runs `python3 scripts/feature_catalog.py --check` plus the full test suites. The legacy main commit `2c2824c70ddc3268c25333063eb61428817a5bf4` has successful GitHub Actions checks including the CI `test` job, so G19's legacy generator/drift gate is **implemented + CI/test-verified at that revision**.
3. `tests/test_feature_catalog.py` verifies catalog completeness/unique IDs, checked-in JSON parity and honest delivery states for selected infrastructure/spec-only features.
4. The legacy catalog correctly warns that repository/CI evidence does not prove live provider permissions, scheduler firing or mutable-state readback.
5. However legacy IDs are **not semantically stable**: `feature_catalog.py` assigns IDs as `<category>-<row_number>` while parsing Markdown. Inserting/reordering ledger rows renumbers downstream IDs and can corrupt durable dependency references.
6. Legacy evidence mapping is title-regex-driven. That is useful as a release check but too brittle to be the canonical relationship between a stable feature and its evidence.
7. For MIRA 2.0, `FEATURES.md` must remain the Git-backed canonical feature authority under current governance. Any JSON/dashboard/catalog view is derived/reproducible from that authority, never an independently editable competing feature registry.
8. Stable semantic IDs already present in `FEATURES.md` must be preserved and machine-parsed as authored IDs; machine-readable projection must never generate feature identity from row position, title text or display order.
9. Requirement state and evidence state remain separate. The machine-readable projection must preserve at minimum stable ID, title, requirement/decision, evidence tier, dependencies and relevant mappings/evidence references without upgrading claims from file existence alone.
10. Catalog drift that changes material feature/dependency/evidence claims without updating the canonical source must fail CI. Generated outputs must trace to an exact source revision/hash.

## Canonical G20 findings

1. Legacy `docs/code-inventory.json` is a real inventory of deployed/release-gate Python files with `path`, bounded `responsibility`, `why_separate` and direct `tests` evidence.
2. `tests/test_code_inventory.py` proves every production Python file matching selected globs is listed exactly once, each entry has responsibility/separation justification and test files exist. It also applies Python-specific AST/style/security checks.
3. Legacy CI's general `python -m unittest discover -s tests` runs `test_code_inventory.py`; the audited legacy main CI `test` check succeeded at commit `2c2824c...`, so the inventory/enforcement is **implemented + CI/test-verified for the audited Python scope**.
4. The durable MIRA semantic is **production artifact/component ownership + evidence coverage**, not “one file equals one feature” and not “split code until every file has one tiny purpose.”
5. Every production artifact should map to exactly one bounded owning component/module responsibility; a component may legitimately cover multiple cohesive files. Unowned production code and overlapping ownership mappings fail closed.
6. Each production component must declare why it exists separately, its owned path(s)/surface, relevant feature/work IDs and direct verification evidence appropriate to that component. Existence of a test path is not by itself proof that the test meaningfully exercises the component; implementation should validate direct coverage/contracts where practical.
7. Anti-bloat means preventing unowned/duplicated responsibilities, accidental debug/test payloads and unjustified parallel implementations. It must not reward arbitrary file-count minimization or fragmentation.
8. Legacy rules such as Python module docstrings, no wildcard imports, bare-except rejection, `eval`/`exec`/`breakpoint` bans, TODO/FIXME/XXX rejection and `shell=True` rejection are **language/tooling policies**, not universal MIRA product semantics. Appropriate static/security rules may remain in per-language profiles, but G20 does not hard-code Python syntax as cross-platform architecture.
9. Dangerous dynamic execution/secrets/privacy/release checks remain important, but should be enforced by security/release tooling matched to the implementation language and threat model rather than smuggled into feature identity.
10. A future Android/Kotlin, TypeScript/web, Python service or other client must pass the same ownership/evidence principle through language-appropriate tooling.

## Authority and migration boundary

- `FEATURES.md` remains canonical for stable feature IDs and feature requirement/evidence/dependency state.
- `BACKLOG.md` remains canonical for ranked implementation work.
- `CURRENT_WORK.md` remains canonical for the one active packet/resume point.
- `ROADMAP.md` remains canonical for milestones.
- A future machine-readable feature catalog is a **generated projection** from canonical `FEATURES.md`, not a second planning database.
- A code/component ownership manifest may be a separate Git-backed engineering metadata authority because it describes source ownership/verification, not feature priority or mutable product state.
- If/when a generated feature registry is introduced, migration must preserve all current semantic IDs and dependencies exactly; there is no row-position renumbering or dual-edit period.

## Preliminary feature/work normalization decision

Existing `DEV-001` (Git-authoritative development control plane), `DEV-002` (resumable packets) and `DEV-003` (dependency-ranked backlog) do not fully encode G19/G20.

Likely stable additions, pending normalization:
- **`DEV-005`** — Machine-readable projection of canonical feature/dependency/evidence state with reproducible generation and CI drift enforcement.
- **`DEV-006`** — Production component ownership and direct-verification inventory with anti-bloat/unowned-code release gate.

Likely implementation work, pending backlog normalization:
- `FEATURE-REGISTRY-001` — implement parser/schema/generator/drift checks from canonical MIRA 2.0 `FEATURES.md`, preserving semantic IDs.
- `CODE-OWNERSHIP-001` — implement provider/language-neutral component ownership/evidence manifest and fail-closed coverage gate, then language-specific static/security profiles as separate tooling.

## Acceptance criteria

1. Stable semantic feature boundary for G19/G20. **Satisfied conceptually; IDs pending registry normalization.**
2. Git/`FEATURES.md` remains sole feature authority; generated views cannot compete. **Satisfied.**
3. Stable authored IDs; no row-order identity. **Satisfied as required design; legacy defect explicit.**
4. Requirement/evidence/dependency state remains machine-representable without false promotion. **Satisfied as required design.**
5. Material catalog drift is release-blocking and outputs trace exact source revision. **Satisfied as required design; legacy implementation/test evidence exists.**
6. Production artifact ownership is bounded and fail-closed for unowned/overlapping code. **Satisfied as required design; legacy Python implementation/test evidence exists.**
7. Anti-bloat does not force one-file/one-feature or arbitrary fragmentation. **Satisfied.**
8. Python-specific lint/security rules are not promoted to universal product semantics. **Satisfied.**
9. Legacy evidence classified conservatively. **Satisfied.**
10. No protected legacy production/provider state or executable MIRA 2.0 code touched. **Satisfied.**
11. Stable IDs/backlog dependency normalization. **Pending.**
12. Bounded PR/merge/readback. **Pending.**

## Exact next action

1. Add `DEV-005` and `DEV-006` to `FEATURES.md` with G19/G20 mappings and integrity notes.
2. Add completed `AUDIT-G19-G20`, `FEATURE-REGISTRY-001` and `CODE-OWNERSHIP-001` to `BACKLOG.md`; link `DEP-GRAPH` and future implementation growth to the machine-readable registry/ownership gates where warranted.
3. Update this file with exact normalization SHAs and close evidence.
4. Compare branch against `main`; require only intended Git authority files.
5. Open bounded PR, verify exact changed files/head/mergeability, merge exact head and remotely read back `main`.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture unrelated customer ideas in BACKLOG unless required for acceptance or explicitly reprioritized.
