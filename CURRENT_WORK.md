# MIRA 2.0 CURRENT WORK

Git is authoritative. This branch records exactly one active packet. Multiple other packet branches may be active repository-wide under `docs/CONCURRENT_WORK_POLICY.md`.

## Active packet

### `M2-M1-038` — Ordinary-language Studio intake

- **Primary work:** `STUDIO-INTAKE-001`.
- **Primary features:** `STUDIO-001`, `DEV-004`.
- **Related invariants/features:** `DEV-005`, `DEV-007`, `DIST-001`, `SOURCE-001`, `RECOVERY-002`.
- **Repository:** `Matthew-Beare/Mira-2.0`.
- **Branch:** `work/m2-m1-038-studio-intake`.
- **Base SHA:** `6551691c7836a9c70a8be080cd11bb2ee18536d2`.
- **Preserved pre-rebase checkpoint:** `3f8d52b2904891b5b9677ec26d64978afb4e4afa`, retained on `checkpoint/m2-m1-038-pre-financial-repair`.
- **Packet:** `docs/work-packets/M2-M1-038.md`.
- **Pull request:** `#153` (draft until implementation and exact-head verification complete).
- **Current status:** ACTIVE. The customer-priority Financial Escape repair `M2-M1-039` is merged and exact post-merge CI is green; this packet has resumed from its preserved first implementation step on the verified current `main` base.
- **Owned implementation surfaces:** new `mira/studio_intake.py`, new `tests/test_studio_intake.py`, packet doc, branch-local `CURRENT_WORK.md`, and one bounded `studio-intake` code-ownership registration.
- **Shared/high-contention surfaces:** no Google Workspace/Sheets, finance, Android, People Discovery, live provider/source/share adapter, final graphical Studio UX, or live user data is owned by this packet.

## Prior packet closeout

`M2-M1-039` merged through PR #154 at exact merge SHA `6551691c7836a9c70a8be080cd11bb2ee18536d2`. Post-merge CI run `34633322661` passed end-to-end, including feature registry, product lifecycle ledger, work-session alignment, code ownership, Android proof build/provenance, Python tests and Workspace Apps Script tests. The Financial Escape repair remains fail-closed and live-provider success is not pre-credited beyond readback evidence.

The earlier `M2-M1-038` displacement checkpoint remains preserved at `3f8d52b2904891b5b9677ec26d64978afb4e4afa`; no intake runtime implementation existed there. The working branch was intentionally realigned onto the verified `M2-M1-039` merge before implementation to avoid carrying a stale concurrent `CURRENT_WORK.md` ancestry into PR #153.

## Objective

Implement the stock-ChatGPT/no-app Studio front door so the customer can describe a desired preference, workflow, or capability in ordinary language without supplying internal engineering identifiers.

The customer-facing input is the raw request plus any explicit constraints they actually stated. A host/model may propose a semantic interpretation of that request. Deterministic MIRA code validates the interpretation against the exact canonical `FeatureRegistry`, derives dependency scope, preserves explicit constraints separately from assistant/model assumptions, generates stable intake identity, surfaces material blockers/questions, and decides whether the result is ready for customer review.

This packet does not invoke a model, create an implementation packet/branch, mutate source/provider state, publish/install/share/activate behavior, infer customer approval, or implement final graphical/browser Studio UX.

## Acceptance state

- M2-M1-039 merge `6551691c7836a9c70a8be080cd11bb2ee18536d2`: **integration-verified by post-merge CI run `34633322661`**.
- Ordinary-language customer request contract: **pending implementation**.
- Host/model semantic interpretation validation: **pending implementation**.
- Exact feature-registry grounding and deterministic dependency derivation: **pending implementation**.
- Explicit customer constraints vs assistant/model assumptions: **pending implementation**.
- Material clarification/blocker state and exactly one next action: **pending implementation**.
- Stable generated intake identity with no customer-supplied packet/work/change/Git/provider identifiers: **pending implementation**.
- Zero implementation/source/share/install/activation authority from intake: **pending implementation**.
- Direct adversarial tests: **pending**.
- Exact-head repository CI: **pending**.
- Live model/provider/source execution: **not claimed and out of scope**.

## Session-start alignment verification — 2026-09-11 resumed after M2-M1-039

### `FEATURES.md`

`STUDIO-001` requires an integrated guided user-facing Studio over bounded preferences/workflows/features with source/dependency awareness and no silent activation. `DEV-004` supplies the bounded private feature-building direction, while `DEV-005` keeps the canonical feature registry authoritative for exact scope/dependency grounding. This packet closes the user-facing gap between ordinary-language intent and the already-merged lower-level Studio lifecycle.

### `BACKLOG.md`

`STUDIO-INTAKE-001` remains the selected next `MIRA-STUDIO-001` child. The Financial Escape reliability interruption is now merged and integration-verified, so the exact displaced Studio resume point is again the highest-priority active implementation work. Skill Builder and Feature Share remain complete at their bounded evidence ceilings and are reused rather than reopened.

### `ROADMAP.md`

The roadmap prioritizes bounded no-app Personal usefulness. Ordinary-language Studio intake advances that direction without requiring Android, a server, terminal work, hard-coded providers, local compute, or paid model APIs as product dependencies.

### Reuse and boundary review

- `mira.feature_registry` remains the authority for exact feature IDs and feature dependencies.
- `mira.studio` remains the downstream deterministic Studio lifecycle projection after a bounded change exists.
- `mira.studio_competition` and `mira.studio_activation` remain review/approval/execution authorities.
- `mira.feature_share` and `mira.feature_share_transport` remain sharing/import authorities.
- `mira.studio_intake` owns only ordinary-language intake validation, registry grounding, deterministic draft identity, constraint/assumption separation, blocker/question state and review readiness.
- Financial Escape surfaces are explicitly out of scope for this resumed packet.

### Direction result

ALIGNED

## Exact next action / resume point

1. Implement `mira/studio_intake.py` with raw request + semantic interpretation contracts, registry grounding, transitive dependency derivation, stable generated draft identity, constraints/assumptions separation, clarification/blocker state and zero execution authority.
2. Add direct adversarial `tests/test_studio_intake.py` for preference/workflow/feature, ambiguity, dependencies, unknown features, replay, malformed input and authority escalation.
3. Register exactly one bounded `studio-intake` ownership component.
4. Run exact-head repository CI and repair only packet-owned failures.
5. Close/merge only from green evidence and verify exact post-merge CI.

## Evidence ceiling

M2-M1-038 may prove deterministic registry-grounded intake/draft behavior only. It does not prove live model interpretation, generated implementation beyond this deterministic intake boundary, Git/source mutation from intake, provider I/O, customer approval, activation, sharing/provider publication, imported installation, or final graphical/browser Studio UX.

## Recovery protocol

Resume from remote `main` merge `6551691c7836a9c70a8be080cd11bb2ee18536d2`, branch `work/m2-m1-038-studio-intake`, this file and `docs/work-packets/M2-M1-038.md`. The preserved pre-rebase checkpoint is `3f8d52b2904891b5b9677ec26d64978afb4e4afa`. Git, not chat, is authoritative.
