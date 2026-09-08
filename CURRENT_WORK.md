# MIRA 2.0 CURRENT WORK

Git is authoritative. This branch records exactly one active packet. Other MIRA packets may progress independently on isolated branches under `docs/CONCURRENT_WORK_POLICY.md`.

## Active packet

### `M2-M1-019` — People Discovery vertical slice

- **Primary work:** `PEOPLE-DISCOVERY-001`.
- **Primary features:** `CAREER-001`.
- **Related invariants/features:** `AUTH-001`, `STORE-001`, `RECOVERY-002`, `MAIL-002`, `DATA-001`.
- **Repository:** `Matthew-Beare/Mira-2.0`.
- **Branch:** `work/m2-m1-019-people-discovery`.
- **Base SHA:** `738ebf082cd3921a0ba807604acabfa756f40c1d`.
- **Packet:** `docs/work-packets/M2-M1-019.md`.
- **Owned implementation surfaces:** People Discovery domain/provider/tracker modules and tests; packet-specific synthetic fixtures/docs.
- **Shared/high-contention surfaces:** `FEATURES.md`, `BACKLOG.md`, `project/code_ownership.json`, branch-local `CURRENT_WORK.md`; reconcile against then-current `main` immediately before merge.
- **Current status:** implementation active. Candidate normalization/identity/scoring/provenance core, canonical relationship interaction/reply tracking, synthetic tests and a bounded search-only People Data Labs adapter are implemented on this branch. Complete Google tracker persistence/readback, provider credential/live proof and final lifecycle reconciliation remain open. No live third-party people data has been written and no outbound-contact action exists.

## Objective

Deploy a first-class MIRA job-seeking feature that repeatedly discovers useful professional contacts at active target employers, with Austin and Research Triangle/Raleigh-Durham as the initial markets and WGU plus networking/cloud/infrastructure relevance strongly prioritized. Normalize, deduplicate, score and retain provenance for candidates; maintain a Google Sheets user-facing tracker; track the user's manual outreach and incoming replies/follow-ups; and never perform automated outreach.

The feature is part of the public MIRA codebase and must remain publishable in sanitized form. Public Git contains implementation, schemas, tests and synthetic fixtures only. Private third-party people data, provider credentials, live spreadsheet identifiers, actual message contents and personal job-search state remain outside the public repository.

Do not name or frame this feature as "2-hour job search", `2HJS`, or similar shorthand. It is MIRA career / People Discovery functionality.

## Relationship and messaging semantics

MIRA must answer ordinary-language questions such as:

- Have I contacted this person?
- Which channel did I use?
- When was the last interaction?
- Did they reply?
- Am I waiting on them or do I owe a follow-up?
- Is there an active conversation or referral?
- Which company/job was the interaction tied to?

Canonical interaction history records channel, direction, kind, timestamp, outcome, optional private summary/source reference, reply linkage and follow-up due date. Relationship state is derived from history rather than maintained as an independent truth column.

Implemented branch module: `mira/people_tracker.py`.

The tracker exposes no `send`, `send_message`, `send_email`, `connect`, `post`, or `comment` operation. Human-performed outreach may be recorded after it happens; incoming replies may be recorded or later observed through an authorized provider path.

## Hard boundaries

- No automated email, LinkedIn connection request/message, comment, post, or other contact action.
- No unauthorized LinkedIn scraping, login automation, or browser scraping.
- LinkedIn URLs may be stored when returned by legitimate providers/public sources.
- One logical MIRROR authority. The Google tracker is a projection/bounded input surface, not a second conflicting truth store.
- Public Git contains synthetic examples only; private people/message/provider/workbook state stays private.
- Uncertain identity matches fail closed rather than silently merging people.
- The feature must be sanitizable and publicly publishable without leaking customer/provider data.

## Provider decision state

Official documentation was inspected for People Data Labs and Apollo during packet setup.

- People Data Labs Person Search remains the leading first adapter because it supports the strongest WGU-first search dimensions: current employer, education/school, title, location, skills, work history and LinkedIn URL.
- A bounded injected-credential PDL search adapter is now implemented with explicit per-run request/record caps, a WGU-first query phase and a broader target-employer fallback phase. It exposes search only.
- Apollo remains a replaceable secondary adapter and is not required before independent implementation can continue.
- The user does **not** need to connect both providers. Independent engineering proceeds first.
- If a provider credential remains the only external boundary after implementation/CI, request the smallest single action required for the first live proof, expected to be one PDL credential/account path unless later evidence changes the adapter choice.

## Acceptance state

- Unique packet/branch isolated from other MIRA work: **satisfied**.
- Existing Sheets/canonical-state architecture inspected: **reusable structured-state and Google Sheets paths confirmed; tracker persistence still open**.
- Provider-neutral candidate model: **implemented**.
- Candidate normalization: **implemented; synthetic tests added; CI pending latest head**.
- Entity resolution/dedupe: **implemented; synthetic tests added; CI pending latest head**.
- Relevance scoring with WGU/network/cloud/infrastructure weighting: **implemented; synthetic tests added; CI pending latest head**.
- Provenance retention: **implemented; synthetic tests added; CI pending latest head**.
- Canonical manual interaction history: **implemented**.
- Derived contacted/replied/awaiting-reply/follow-up state: **implemented and hardened for timezone/reply-cycle/follow-up ordering**.
- No outbound-send API in relationship tracker/provider: **implemented with synthetic tests**.
- Google tracker schema with `COMPANIES` / `PEOPLE` / `INTERACTIONS` / `JOBS`: **implemented as provider-neutral projection schema; complete persistence/readback pending**.
- Bounded People Data Labs provider adapter: **implemented; synthetic tests added; credential/live proof pending**.
- Real provider operational: **pending credential/preflight/live proof**.
- Repeat discovery update proof: **synthetic core coverage added; live proof pending**.
- Exact live tracker readback: **pending**.
- Manual interaction-state live write/readback: **pending**.
- Public sanitization discipline: **implemented structurally; final branch audit pending**.
- Relevant tests/baseline gates: **tests added; prior CI failed at work-session alignment before Python tests; governance repair in progress**.
- Remote Git/CI completion proof: **pending**.

## Exact next action / resume point

1. Register `PEOPLE-DISCOVERY-001` in canonical `BACKLOG.md` and keep this packet aligned to existing `CAREER-001`; refine stable career feature semantics before merge without inventing a parallel feature authority.
2. Re-run exact-head CI and repair any actual Python/code-ownership failures now that the work-session alignment gate can proceed.
3. Complete canonical People Discovery persistence and Google tracker writer/readback using existing MIRA structured-state/Sheets conventions rather than a duplicate store.
4. Reconcile any required `FEATURES.md` refinement and `project/code_ownership.json` change only after then-current-main collision inspection.
5. Keep PR #134 draft until implementation tests, provider boundary and live tracker proof are earned.
6. Perform provider capability/credential preflight only after the independent implementation is green.
7. If the only remaining boundary is a PDL API key/account, request exactly that single user action. Apollo is optional fallback/secondary coverage, not a prerequisite.
8. Execute real discovery, real Sheet write/readback, rerun-update proof and manual interaction/reply proof before claiming deployment.

## Concurrent work / control-room rule

This conversation may coordinate MIRA work generally, but implementation remains packet/branch isolated. Finance/Financial Escape, Android/provider work and other MIRA packets are not abandoned merely because this packet is active. Before switching implementation scope, checkpoint the current packet's exact remote head/resume point, then continue the next prioritized packet on its own branch. Do not mix unrelated source changes into this branch.

## Session-start alignment verification — 2026-09-07

### `FEATURES.md`

Reviewed. Existing `CAREER-001` is the current canonical career feature anchor. `M2-M1-019` extends the user-visible career capability with People Discovery, relationship tracking and a no-automated-outreach boundary while preserving `AUTH-001`, `STORE-001`, `RECOVERY-002`, `MAIL-002` and `DATA-001`. Stable career feature wording may be refined before merge, but this packet does not create a competing feature authority.

### `BACKLOG.md`

Reviewed. Existing backlog did not yet contain a dedicated People Discovery work item. `PEOPLE-DISCOVERY-001` is the bounded work ID for this vertical and is being registered as part of the governance repair before CI is treated as meaningful implementation evidence.

### `ROADMAP.md`

Reviewed. People Discovery is a user-visible Personal MIRA career vertical built on the existing Google/Sheets and canonical-state foundations. It does not change the Personal Google architecture, require Android, authorize automated outreach or weaken public-repository privacy rules.

### Direction result

ALIGNED

## Recovery protocol

Resume by reading current remote `main`, this branch's `CURRENT_WORK.md`, `docs/work-packets/M2-M1-019.md`, and this branch's remote head. Inspect active packet branches/PRs for overlap before shared-file writes. Do not reconstruct private people/provider/message state from public Git or chat memory.
