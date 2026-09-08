# MIRA 2.0 CURRENT WORK

Git is authoritative. Multiple packets may be active repository-wide at the same time, but each chat/session owns exactly one packet and one branch. `main` is the serialized integration branch.

For exact packet recovery, the packet document plus its remote branch head are authoritative. This file is the repository-wide coordination index.

See `docs/CONCURRENT_WORK_POLICY.md`.

## Active packets

### `M2-GOV-001` — Concurrent work-packet safety

- **Chat role:** current governance packet for the People Discovery execution chat.
- **Branch:** `work/m2-gov-001-concurrent-packets`.
- **Base SHA:** `51649d6e1987d5a0601131715732a2560b26b193`.
- **Packet:** `docs/work-packets/M2-GOV-001.md`.
- **Owned surfaces:** `PROJECT_INSTRUCTIONS.md`, `docs/CONCURRENT_WORK_POLICY.md`, concurrency model in `CURRENT_WORK.md`.
- **Status:** in progress; merge/readback required before starting People Discovery.
- **Exact next action:** open/merge the governance PR, verify remote `main`, then start the People Discovery packet from the new verified `main`.

### `M2-M1-015` — Canonical finance evidence audit and projection repair

- **Primary work:** `FIN-CANON-AUDIT-001`.
- **Branch:** `work/m2-m1-015-financial-canonical-audit`.
- **Base SHA:** `5075a23c0a3513118b0dceaf711cd041b1d3798a`.
- **Verified remote branch head at concurrency handoff:** `04b88d027fdacb14f580fa31674c23fee1aa9d7a`.
- **Packet:** `docs/work-packets/M2-M1-015.md` on that branch.
- **Status:** active and independently resumable; one-authority spending integration plus retirement-lever/confidence repair are implemented/read back; cross-source evidence reconciliation remains open.
- **Exact resume:** read that branch's `CURRENT_WORK.md` and packet document, then continue the recorded cross-source reconciliation cursor. Do not reconstruct it from this summary.
- **Concurrency note:** this packet may continue in another chat. Before its eventual merge, reconcile it with then-current `main` and preserve the concurrent-work governance rules.

## Blocked / held packets

### `M2-M1-012` — Android representative-device execution proof

- **Recovery branch:** `work/m2-m1-012-provider-tooling-hold-2`.
- **Stable pre-finance checkpoint:** `6e715159feed0b044e3ef3ef610916903e2deb09`.
- **Provider-inspection runbook:** `docs/work-packets/M2-M1-012-provider-inspection-runbook.md`.
- **Earned device proof:** exact stable-development-signed APK installed/launched; native Google account chooser opened; correct account selected; app returned `authorization_cancelled`; no consent screen or Drive Picker appeared.
- **Expected proof identity:** package `com.mira.deviceproof`; signing SHA-1 `AF:E0:18:6B:7C:21:EA:74:D3:4C:4A:33:04:FF:B1:15:EF:DB:A5:6D`.
- **Unknown provider state:** actual Android OAuth registered package/SHA-1 and Google Picker API enabled/disabled state.
- **Hold rule:** do not rerun the phone flow or mutate provider configuration until a credible authenticated provider-access recovery signal exists. Resume only through the recorded runbook.

## Requested next packet

### People Discovery

The product owner has explicitly requested a bounded execution packet to deploy People Discovery for the job search, with Austin and Research Triangle/Raleigh-Durham as initial markets and WGU + networking/cloud/infrastructure contacts strongly prioritized.

This is intentionally **not yet marked active** until `M2-GOV-001` is merged/read back. Once governance is integrated, create a new unique packet/branch from verified `main`, inspect existing Google Workspace/Sheets and provider abstractions, then implement the end-to-end discovery vertical slice without automated outreach.

## Repository-wide integration rules

- Parallel implementation is allowed only on isolated packet branches.
- Each chat owns one packet at a time.
- Do not intentionally edit another active packet's owned implementation surface without an explicit dependency/integration plan.
- High-contention governance files must be reconciled against current `main` immediately before merge.
- Integration into `main` is serialized.
- Before merge, detect intervening main changes, reconcile semantically, rerun affected tests, and preserve compatible newer work from all packets.
- Never force-update `main` or another packet branch to avoid a conflict.

## Recovery protocol

Any chat should recover by reading, in order:

1. current remote `main`;
2. this `CURRENT_WORK.md`;
3. the relevant packet document;
4. the relevant remote packet branch head and open PR if any.

Conversation history is secondary evidence only.
