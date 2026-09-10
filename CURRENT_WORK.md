# MIRA 2.0 CURRENT WORK

Git is authoritative. This branch records exactly one active packet. Multiple other packet branches may be active repository-wide under `docs/CONCURRENT_WORK_POLICY.md`.

## Active packet

### `M2-M1-034` — Sanitized feature sharing and import staging foundation

- **Primary work:** `FEATURE-SHARE-001`.
- **Primary features:** `STUDIO-001`, `DIST-001`.
- **Related invariants/features:** `DEV-004`, `DEV-005`, `DEV-006`, `SOURCE-001`, `SOURCE-002`, `ONBOARD-002`, `RECOVERY-002`.
- **Repository:** `Matthew-Beare/Mira-2.0`.
- **Branch:** `work/m2-m1-034-feature-share-manifest`.
- **Base SHA:** `34cb892b6401fc5ef54e9c318b52d5d88527d2e5`.
- **Packet:** `docs/work-packets/M2-M1-034.md`.
- **Owned implementation surfaces:** packet-local `CURRENT_WORK.md`, `docs/work-packets/M2-M1-034.md`, planned provider-neutral feature-sharing module/tests, narrow code-ownership registration, and `BACKLOG.md` only for the earned `SKILL-BUILDER-001` lifecycle reconciliation.
- **Shared/high-contention surfaces:** no People Discovery, Sheets control-surface, finance, Android, provider-specific source adapter, private-runner, Workspace provider state or final Studio UX implementation is owned by this packet.
- **Current status:** packet started from exact integration-verified M2-M1-033 merge; implementation not yet claimed.

## Objective

Implement the provider-neutral integrity core for optional MIRA feature sharing: exact share-package provenance, artifact-digest and sanitization-evidence binding, dependency/contract compatibility evaluation, private/imported/forked ownership reconciliation, deterministic import staging, and strict no-silent-activation behavior.

This packet does not claim that arbitrary content can be automatically sanitized. Publication eligibility requires explicit sanitization evidence bound to each exact artifact digest and one exact sanitization-policy revision. The package contains public metadata/digests only; provider-specific publication transport and actual source payload transfer remain separate source-lane responsibilities.

## Acceptance state

- M2-M1-033 / `SKILL-BUILDER-001`: **merged as PR #148 at `34cb892b6401fc5ef54e9c318b52d5d88527d2e5`; exact post-merge CI #573 / run `34519124053` PASS end-to-end**.
- `SKILL-BUILDER-001` provider-neutral engine completion boundary: **earned; BACKLOG lifecycle reconciliation is part of this packet checkpoint and must not imply live provider/source-lane execution**.
- `FEATURE-SHARE-001`: **queued at packet start**.
- Existing `mira.personal_distribution` remains the Personal starter release authority; its Google-starter-specific private-material checks are not repurposed as a generic arbitrary-content sanitizer.
- Existing `mira.feature_registry` remains canonical feature/dependency projection authority and should be reused for target compatibility snapshots rather than duplicated.
- Share package schema/provenance: **pending implementation**.
- Per-artifact sanitization evidence binding: **pending implementation**.
- Dependency/contract compatibility evaluation: **pending implementation**.
- Ownership/revision reconciliation and import staging: **pending implementation**.
- No-silent-activation contract: **pending implementation**.
- Exact-head CI and integration verification: **pending**.
- Live publication/import/provider mutation: **not claimed and out of scope**.

## Session-start alignment verification — 2026-09-10

### `FEATURES.md`

`DIST-001` requires private deployment lineage and controlled upstream feature sharing. `STUDIO-001` requires optional sanitized sharing without silently activating imported behavior. `DEV-004` supplies bounded custom feature creation, while `SOURCE-001`/`SOURCE-002` keep provider/source-lane mechanics separate from product semantics.

### `BACKLOG.md`

`FEATURE-SHARE-001` is the remaining direct dependency beside the now integration-verified Skill Builder before final `MIRA-STUDIO-001`. Its prerequisites `DIST-001`, `ONBOARD-002`, `SOURCE-GATES-001`, and `DEV-005` already exist at their declared evidence ceilings. `SOURCE-LANES-001` remains separate provider/source transport work and is not silently absorbed here.

### `ROADMAP.md`

This packet preserves Git authority, deterministic distribution lineage, the ordinary Personal no-server path, and provider-neutral semantics. It does not introduce local-compute or provider-specific infrastructure requirements.

### Reuse and boundary review

- Reuse `mira.feature_registry.FeatureRegistry` for canonical target feature compatibility evidence.
- Preserve `mira.personal_distribution` as the Personal Google starter release implementation; do not duplicate or weaken its authority.
- Feature-sharing core will consume explicit sanitization evidence rather than asserting that metadata-only logic has inspected private source it cannot see.
- Imported material can become staged/reviewable only; activation remains behind the Studio preview/test/approval/execution path merged in M2-M1-031 through M2-M1-033.
- Open People Discovery PR #134 and Sheets control-surface PR #135 remain unrelated and untouched.

### Direction result

ALIGNED

## Exact next action / resume point

1. Create `docs/work-packets/M2-M1-034.md` with the bounded share/import contract.
2. Implement a provider-neutral feature-share manifest and import compatibility/reconciliation module plus direct adversarial tests.
3. Register exact production ownership if a new module is added.
4. Reconcile `SKILL-BUILDER-001` in `BACKLOG.md` only with the exact M2-M1-033 merge/post-merge evidence and preserve its provider-neutral evidence ceiling.
5. Run exact-head repository CI, review the full packet diff, and correct semantic findings before merge.
6. Do not add provider-specific publication transport, arbitrary-content sanitization claims, automatic import activation or final Studio UI to this packet.

## Evidence ceiling

M2-M1-033 is integration-verified at provider-neutral engine semantics. M2-M1-034 has only begun; no feature-sharing implementation or publication/import execution is yet claimed.

## Recovery protocol

Resume from remote `main` at the verified M2-M1-033 merge, branch `work/m2-m1-034-feature-share-manifest`, this file, and `docs/work-packets/M2-M1-034.md` once created. Git remains authoritative over conversational reconstruction.
