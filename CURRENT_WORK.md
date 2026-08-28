# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and its exact resume point.

## Completed packet before this branch

### `M2-G0-008G` — Remaining feature-ledger closeout

- **Merged PR:** #34
- **Merge SHA / main readback:** `acb7e8c9025b7f6096f9a4fcba0ced8d9d68622c`
- **Post-merge completion checkpoint / this branch start SHA:** `0b734df51c815ec16a05a4b0b5a6446dde5f4e78`
- **Result:** recovered category F is closed through F23 and category G through G20; feature inventory is complete.

## Active packet

- **Packet ID:** `M2-G0-009`
- **Name:** Legacy branch/PR reconciliation
- **Class:** forensic reconciliation / final salvage gate before dependency closeout
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `audit/g0-009-legacy-reconciliation`
- **Branch start SHA:** `0b734df51c815ec16a05a4b0b5a6446dde5f4e78`
- **Status:** activated; legacy repository/PR/branch inventory next.

## Objective

Inventory meaningful unmerged or divergent legacy MIRA work, map every materially useful candidate to existing stable MIRA 2.0 feature/work IDs, and record an explicit **salvage / superseded / rejected / defer** disposition. This packet does not merge historical code wholesale and does not implement MIRA 2.0 features.

## Scope

1. `Matthew-Beare/MIRA-Personal-Production` open/unmerged PRs and materially divergent branches, especially PR #31.
2. Meaningful divergent work in public/institutional experimental legacy repositories only when it is not merely a generated mirror of Personal-Production.
3. Candidate code/contracts/tests/workflows that can accelerate already-defined MIRA 2.0 work.
4. Architectural conflicts that must be explicitly rejected so they cannot be resurrected by later salvage.

Do not inspect every historical commit for sport. Prior audits already reconciled many PR #31 components; reuse those findings and inspect only unresolved material.

## Acceptance criteria

1. Meaningful open/unmerged legacy PRs identified.
2. Material divergent branches identified or shown to be generated/redundant.
3. PR #31 candidate components mapped to stable MIRA 2.0 work IDs with explicit disposition/evidence ceiling.
4. Direct Android-to-provider authority mutation remains rejected.
5. No wholesale PR #31/mega-branch merge is allowed.
6. Generated public/institutional mirrors are not treated as independent feature sources.
7. Useful legacy tests/contracts/workflows are salvage candidates only where they match current semantics.
8. Obsolete/superseded scheduler, authority, distribution or direct-provider designs are explicitly rejected.
9. No protected legacy production/provider state or executable MIRA 2.0 product behavior changes.
10. Bounded Git-authority normalization, PR/merge/readback.

## Android product-state checkpoint

No APK is created in this packet. The value of G0-009 is to determine exactly which legacy Android/API/storage pieces can be reused once implementation starts, reducing rewrite time after G0-010.

## Exact next action

1. List open PRs and non-main branches in `MIRA-Personal-Production`.
2. Identify which branches/PRs contain unique material not already on legacy main.
3. Compare meaningful candidates against current MIRA 2.0 IDs/work rows.
4. Check public/institutional repositories for independent divergence versus generated mirror status.
5. Checkpoint the disposition matrix before modifying `FEATURES.md` or `BACKLOG.md`.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture unrelated ideas in BACKLOG unless required for acceptance or explicitly reprioritized.
