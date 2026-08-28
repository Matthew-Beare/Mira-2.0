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
- **Backlog normalization:** `cdfb42510941ed6117241dc5964ac0484791f6cc`
- **Status:** acceptance complete; final diff gate, PR, merge and main readback remain.

## Canonical result

1. Added **`DEV-005` — Machine-readable projection of canonical feature/dependency/evidence state with reproducible generation and CI drift enforcement**.
2. Added **`DEV-006` — Production component ownership and direct-verification inventory with anti-bloat/unowned-code release gate**.
3. `FEATURES.md` remains the sole canonical feature authority. JSON/Markdown/dashboard catalogs are generated projections only.
4. Stable semantic IDs are authored identities and never generated from row order, title text or display order. Legacy `<category>-<row_number>` identity is rejected.
5. Requirement state, implementation evidence, test evidence, integration evidence and live evidence remain distinct. File existence or a matching regex cannot upgrade feature evidence.
6. `FEATURE-REGISTRY-001` will implement the MIRA 2.0 stable-ID parser/schema/generator/drift gate and is now a prerequisite for `DEP-GRAPH`.
7. `DEV-006` is component-based, not one-file/one-feature. Every production artifact must map to exactly one bounded component; one component may own several cohesive files.
8. `CODE-OWNERSHIP-001` will implement the language-neutral component ownership/direct-evidence gate. Unowned or overlapping production ownership fails closed.
9. Anti-bloat means no unowned/duplicated responsibilities, accidental debug/test payloads or unjustified parallel implementations; it does not reward arbitrary file fragmentation.
10. Python AST/style/security rules found in the legacy implementation remain language-specific profiles rather than universal MIRA architecture.
11. Legacy G19/G20 implementation and CI at `MIRA-Personal-Production` commit `2c2824c70ddc3268c25333063eb61428817a5bf4` remain valid legacy test evidence only; no MIRA 2.0 executable implementation is claimed.
12. No protected legacy provider/production state or executable MIRA 2.0 product code changed in this packet.

## Android product-state checkpoint

This packet does not change the Android implementation percentage. The current critical Android path remains:

1. `AUTHORITY-REGISTRY-001` + `STORE-ADAPTER-001`;
2. `API-CORE-001` shared service runtime;
3. `CORE-ROUNDTRIP` stock ChatGPT proof;
4. `ANDROID-CLIENT-CORE-001`;
5. `ANDROID-SYNC` proving Android and ChatGPT share one canonical entity;
6. native delivery/capture and signed release hardening.

Legacy Android code has successful CI build evidence, but there is still no MIRA 2.0 APK or shared-API integration proof.

## Acceptance criteria

1. Stable semantic feature boundary for G19/G20. **Satisfied: `DEV-005`, `DEV-006`.**
2. `FEATURES.md` remains sole feature authority. **Satisfied.**
3. Stable authored feature identity and no row-position identity. **Satisfied.**
4. Requirement/evidence/dependency projection without false evidence promotion. **Satisfied.**
5. Reproducible generated projection and material drift gate defined. **Satisfied at specification boundary; legacy test evidence exists.**
6. Component ownership/direct-verification semantics defined. **Satisfied at specification boundary; legacy Python test evidence exists.**
7. Anti-bloat avoids one-file/one-feature fragmentation. **Satisfied.**
8. Language-specific rules remain implementation profiles. **Satisfied.**
9. `AUDIT-G19-G20`, `FEATURE-REGISTRY-001`, `CODE-OWNERSHIP-001` and `DEP-GRAPH` dependencies normalized in `BACKLOG.md`. **Satisfied.**
10. No production/provider state or executable MIRA 2.0 changes. **Satisfied.**
11. Bounded PR/merge/readback. **Pending.**

## Exact next action

1. Compare `audit/g0-008f-catalog-code-integrity` against `main`; require zero commits behind and exactly `FEATURES.md`, `BACKLOG.md`, `CURRENT_WORK.md` changed.
2. Open bounded PR to `main`.
3. Verify GitHub server-side changed filenames, exact head SHA and mergeability.
4. Merge using the exact verified head SHA.
5. Read back `DEV-005`, `DEV-006`, `AUDIT-G19-G20`, `FEATURE-REGISTRY-001`, `CODE-OWNERSHIP-001` and this completion checkpoint from `main`.
6. Dependency-rank and activate one bounded successor packet. Prefer a closeout packet that reconciles the remaining F21-F23/G2-G6/G8-G9/G11-G15 rows without drifting into implementation, so G0 can finish and implementation can begin.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture unrelated customer ideas in BACKLOG unless required for acceptance or explicitly reprioritized.
