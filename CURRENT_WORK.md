# MIRA 2.0 CURRENT WORK

Git is authoritative. This branch records exactly one active packet. Multiple other packet branches may be active repository-wide under `docs/CONCURRENT_WORK_POLICY.md`.

## Active packet

### `M2-M1-037` — Studio guided intent and clarification planner

- **Primary work:** `MIRA-STUDIO-001`.
- **Primary features:** `STUDIO-001`, `DEV-004`, `DIST-001`.
- **Related invariants/features:** `DEV-002`, `DEV-005`, `DEV-006`, `DEV-007`, `SOURCE-001`, `PROVIDER-001`, `RECOVERY-002`.
- **Repository:** `Matthew-Beare/Mira-2.0`.
- **Branch:** `work/m2-m1-037-studio-intent-planner`.
- **Base SHA:** `d2b89625313b8741ee7d0b5f6d45fe863ba90011`.
- **Packet:** `docs/work-packets/M2-M1-037.md`.
- **Current status:** active implementation packet. M2-M1-036 is merged and exact-merge-SHA CI plus trusted-runner preflight are green; this packet adds the next user-visible Studio seam and reconciles stale Studio backlog lifecycle state.
- **Owned implementation surfaces:** new `mira/studio_intent.py`, new `tests/test_studio_intent.py`, packet doc, branch-local `CURRENT_WORK.md`, one bounded ownership registration, and narrow lifecycle-only edits to the three Studio rows in `BACKLOG.md`.
- **Shared/high-contention surfaces:** no Google Workspace/Sheets, finance, Android, People Discovery, live model/provider/source/share adapter, final graphical UX, or private deployment configuration is owned here.

## Prior packet closeout

`M2-M1-036` / first integrated `MIRA-STUDIO-001` guided lifecycle surface merged through PR #151 at exact merge SHA `d2b89625313b8741ee7d0b5f6d45fe863ba90011`. Post-merge CI #593 / run `34562376624` passed end-to-end and exact merge-SHA `python` plus trusted-runner `preflight` checks passed. It proves deterministic user-visible lifecycle/next-action projection over supplied reviewed change, activation/rollback and inert import evidence. It does not prove model invocation, intent extraction, provider execution or final graphical UX.

`SKILL-BUILDER-001` is now integration-verified at its provider-neutral bounded engine ceiling through M2-M1-031 through M2-M1-033: exact candidate/review evidence, staged preview/test/rollback/approval planning, and explicit approved activation/rollback execution through injected source adapters. Live model/provider/Git execution remains separate evidence.

`FEATURE-SHARE-001` is now integration-verified at its provider-neutral sharing ceiling through M2-M1-034 through M2-M1-035: deterministic sanitized packages, integrity/privacy validation, inert import inspection, explicit publication authorization, exact readback/replay and recovery-required transport semantics. Live public provider publication/import remains separate evidence.

## Objective

Add the deterministic product-side intake contract that turns one bounded, already-normalized user Studio request into either (a) a safe `StudioSession` ready for the existing review lifecycle, or (b) a minimal set of clarification questions only where missing information materially changes user-visible behavior, acceptance criteria, cost, privacy/safety, irreversibility, or sharing intent.

This packet does not use an LLM to interpret prose, invoke a model, generate code, create candidate branches, execute source mutation, publish/import packages, infer approval, or build final graphical/browser UI. An upstream conversational/model surface may propose normalized fields later, but this deterministic planner decides whether enough explicit user authority exists to enter the existing Studio lifecycle.

## Acceptance criteria

1. A bounded `StudioIntentRequest` preserves exact user request text, one proposed change kind, objective, feature/dependency context, acceptance outcomes and explicit constraints without treating model suggestions as user authority.
2. Material decision domains are explicit and finite: user-visible behavior, acceptance criteria, privacy/safety, cost, irreversibility and optional sharing.
3. Missing material decisions produce only the smallest deterministic clarification set needed; non-material technical implementation choices never block intake.
4. Private-by-default behavior is preserved: absence of sharing permission never implies publication/share authority.
5. No source mutation or activation approval can be created by intake; a ready result may create only a `StudioSession` for the existing review lifecycle.
6. Exact explicit user decisions are provenance-bound to the intent and may not be borrowed from another intent/session.
7. Contradictory or malformed decision evidence fails closed rather than silently choosing a side.
8. Deterministic replay of the same normalized request/evidence yields the same plan and digest.
9. Public intent-planning contracts contain no credentials, provider endpoints, shell commands, private host/model paths or runner labels.
10. Direct adversarial tests cover ready intent, each material clarification domain, privacy/share defaults, contradiction/stale evidence, non-material technical choice handling and deterministic replay.
11. `BACKLOG.md` lifecycle text for `SKILL-BUILDER-001`, `FEATURE-SHARE-001` and `MIRA-STUDIO-001` is reconciled to exact earned evidence without pre-crediting live model/provider/final UX behavior.
12. Bounded ownership and repository-wide CI pass at exact head before merge.

## Session-start alignment verification — 2026-09-11

### `FEATURES.md`

`STUDIO-001` requires guided user-facing creation/refinement of bounded preferences/workflows/features with declared contracts, preview/test/rollback, provenance and optional sanitized sharing without silent activation. The lower-level review, activation and sharing boundaries are merged; the next missing product seam is honest intent/clarification planning before those engines are entered.

### `BACKLOG.md`

The three Studio-related rows are stale: `SKILL-BUILDER-001` and `FEATURE-SHARE-001` still say queued despite merged integration evidence, while `MIRA-STUDIO-001` still says queued despite M2-M1-036's merged guided lifecycle surface. This packet owns only the narrow lifecycle reconciliation plus the next bounded Studio child, not unrelated backlog cleanup.

### `ROADMAP.md`

M2-M0.5 prioritizes repeated real user-visible progress without forcing servers, local infrastructure, provider setup or terminal work. A deterministic guided intake/clarification seam advances ordinary-language Studio use while keeping provider/model execution optional and separately evidenced.

### Reuse and boundary review

- `mira.studio` remains authority for Studio lifecycle/next-action projection and `StudioSession`.
- `mira.studio_competition` remains authority for candidate/staged review evidence and approval-bound activation planning.
- `mira.studio_activation` remains authority for approved activation/rollback execution receipts.
- `mira.feature_share` and `mira.feature_share_transport` remain package/transport authorities.
- `mira.studio_intent` will own only deterministic normalized intent authority, clarification planning and safe handoff into `StudioSession`.

### Direction result

ALIGNED

## Exact next action / resume point

1. Reconcile the three stale Studio backlog lifecycle rows against merged packet evidence.
2. Implement deterministic intent/decision provenance plus minimal clarification planning and safe `StudioSession` handoff.
3. Add direct adversarial tests and one bounded ownership registration.
4. Run repository-wide CI at exact branch head, review overlap/diff, close documentation, rerun exact-head CI and merge only with expected-head protection.
5. Verify exact post-merge CI and trusted-runner/preflight before claiming integration verification.
6. Preserve the evidence ceiling: no live model interpretation/invocation, code generation, source mutation, publication/import execution or final graphical UX claim.

## Evidence ceiling

M2-M1-037 begins from integration-verified main `d2b89625313b8741ee7d0b5f6d45fe863ba90011`. No Studio intent-planning implementation evidence is claimed yet.

## Recovery protocol

Resume from branch `work/m2-m1-037-studio-intent-planner`, base `d2b89625313b8741ee7d0b5f6d45fe863ba90011`, this file and `docs/work-packets/M2-M1-037.md`. Git, not chat, is authoritative.
