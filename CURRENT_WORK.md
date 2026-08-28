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
- **Research checkpoint:** `d0cb02666c918afc24068b4249638aab4d482015`
- **Feature normalization:** `32fad9c2c0b063e09eb5de04e241c034a2aae90c`
- **Status:** forensic research and `FEATURES.md` normalization complete; `BACKLOG.md` normalization is the exact resume point.

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

1. Legacy G19 has real executable/test evidence. `scripts/feature_catalog.py` parses `docs/feature-ledger-2026-08-24.md`, hashes that source, generates JSON/Markdown catalog views, validates evidence paths and fails CI on generated-file drift.
2. Legacy `.github/workflows/ci.yml` explicitly runs `python3 scripts/feature_catalog.py --check` plus tests. Legacy main commit `2c2824c70ddc3268c25333063eb61428817a5bf4` has successful Actions checks, including the CI test job. G19 is therefore implemented + CI/test-verified **in that legacy revision only**.
3. Legacy IDs are not semantically stable: `feature_catalog.py` assigns `<category>-<row_number>` IDs from Markdown order. Inserting/reordering rows renumbers downstream identities and can corrupt durable dependencies.
4. Legacy evidence mapping is title-regex-driven and therefore too brittle to define canonical stable feature/evidence relationships.
5. MIRA 2.0 keeps `FEATURES.md` as the canonical Git-backed feature authority. JSON/dashboard/catalog views are reproducible projections, never independently editable feature truth.
6. Stable semantic IDs are authored identities and never generated from row position, title text or display order.
7. Requirement and evidence states remain separate. Machine-readable projection must preserve stable ID, title, requirement/evidence tier, dependencies and mappings/evidence references without upgrading claims from file existence.
8. Material catalog drift is release-blocking and generated outputs trace to exact source revision/hash.

## Canonical G20 findings

1. Legacy `docs/code-inventory.json` inventories production Python files with path, bounded responsibility, separation rationale and direct test files.
2. `tests/test_code_inventory.py` verifies selected production Python files are listed exactly once, have responsibility/separation metadata and named test evidence; it also applies Python-specific AST/style/security checks. Legacy main CI at `2c2824c...` is green, so this scope is implemented + CI/test-verified in legacy.
3. Durable MIRA semantics are **production artifact/component ownership + evidence coverage**, not “one file equals one feature.”
4. Every production artifact maps to exactly one bounded owning component; one component may cover multiple cohesive files. Unowned or overlapping ownership fails closed.
5. Each component declares why it exists separately, owned path/surface, relevant feature/work IDs and direct verification evidence. A test filename alone does not prove meaningful coverage.
6. Anti-bloat prevents unowned/duplicated responsibilities, accidental debug/test payloads and unjustified parallel implementations. It does not reward arbitrary file fragmentation or minimization.
7. Python-specific docstring/import/exception/dynamic-execution/TODO/shell checks are language/tooling policy, not universal MIRA feature semantics. Android/Kotlin, TypeScript/web, Python services and future runtimes use language-appropriate profiles under the same ownership/evidence rule.

## Authority boundary

- `FEATURES.md` remains canonical for stable feature IDs plus requirement/evidence/dependency state.
- `BACKLOG.md` remains canonical for ranked engineering work.
- `CURRENT_WORK.md` remains canonical for the active packet/resume point.
- `ROADMAP.md` remains canonical for milestones.
- `DEV-005` is a generated machine-readable projection from `FEATURES.md`; there is no dual-edit feature registry.
- `DEV-006` may use a separate Git-backed component ownership manifest because that manifest describes source ownership/verification, not product priority or mutable reality state.

## Normalized feature result

`FEATURES.md` commit `32fad9c2c0b063e09eb5de04e241c034a2aae90c` added:

- **`DEV-005` — Machine-readable projection of canonical feature/dependency/evidence state with reproducible generation and CI drift enforcement**; requirement `required/governance`, evidence `specified+legacy-test-verified`, deps `DEV-001,DEV-003`.
- **`DEV-006` — Production component ownership and direct-verification inventory with anti-bloat/unowned-code release gate**; requirement `required/governance`, evidence `specified+legacy-test-verified`, dep `DEV-001`.
- G19 and G20 foundation mappings.
- Integrity rules rejecting row-position identity, independent generated authority, one-file/one-feature architecture and universal Python-specific policy.
- Category-G audit status now records G1, G7, G10, G16-G20 as audited through this packet, contingent on backlog/packet merge closure.

## Acceptance criteria

1. Stable semantic feature boundary for G19/G20. **Satisfied: `DEV-005`, `DEV-006`.**
2. Git/`FEATURES.md` remains sole feature authority; generated views cannot compete. **Satisfied.**
3. Stable authored IDs; no row-order identity. **Satisfied; legacy defect explicit.**
4. Requirement/evidence/dependency state remains machine-representable without false promotion. **Satisfied.**
5. Material catalog drift is release-blocking and outputs trace exact source revision. **Satisfied as design; legacy implementation/test evidence exists.**
6. Production artifact ownership is bounded and fail-closed for unowned/overlapping code. **Satisfied as design; legacy Python implementation/test evidence exists.**
7. Anti-bloat does not force one-file/one-feature or arbitrary fragmentation. **Satisfied.**
8. Python-specific lint/security rules are not promoted to universal product semantics. **Satisfied.**
9. Legacy evidence classified conservatively. **Satisfied.**
10. No protected legacy production/provider state or executable MIRA 2.0 code touched. **Satisfied so far.**
11. Stable backlog IDs/dependency normalization. **Pending.**
12. Bounded PR/merge/readback. **Pending.**

## Exact next action

1. Normalize `BACKLOG.md` with completed `AUDIT-G19-G20`, `FEATURE-REGISTRY-001`, and `CODE-OWNERSHIP-001`.
2. Make `DEP-GRAPH` depend on `DEV-005`/`FEATURE-REGISTRY-001` so dependency closeout consumes stable machine-readable semantic IDs rather than row-position IDs.
3. Do not make every implementation packet depend on `CODE-OWNERSHIP-001` by prose fan-out; instead record it as a release/growth prerequisite and later enforce it centrally in CI.
4. Update this file with the exact backlog normalization SHA and packet-close state.
5. Compare branch against `main`; require exactly the intended Git authority files.
6. Open bounded PR, verify server-side filenames/head/mergeability, merge exact head and remotely read back `main`.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture unrelated customer ideas in BACKLOG unless required for acceptance or explicitly reprioritized.
