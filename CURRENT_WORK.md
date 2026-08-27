# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and its exact resume point.

## Completed packet before this branch

### `M2-G0-006D` — Feature Audit Slice E4 — identity, sharing and self-extension foundations

- **Merged PR:** #17
- **Merge SHA:** `5027bb4882e3455b47b8c0a0957f972296bb51fe`
- **Main handoff commit activating E5:** `e4c6be90887d716f99c421b1e1f5ec1c60fcb511`
- **Live Google production touched:** no.
- **Executable product behavior changed:** no.

## Active packet

- **Packet ID:** `M2-G0-006E`
- **Name:** Feature Audit Slice E5 — nontechnical source/runtime onboarding
- **Class:** forensic audit / prerequisite
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `audit/g0-006e-nontechnical-source-runtime-onboarding`
- **Branch start SHA:** `e4c6be90887d716f99c421b1e1f5ec1c60fcb511`
- **Research checkpoint commit:** `1e609fa4babc84c44a618ab97f1683ff7111eda2`
- **Feature registry commit:** `afcf9c8f5670fb7e89aef24a44fa1c62d1607a0a`
- **Backlog checkpoint commit:** `7a08ab8d10278eb51b3c5167e83d28641a9671e1`
- **Status:** acceptance work complete; PR/merge/readback pending.

## Completed acceptance evidence

1. Added the `SOURCE-*` semantic family for durable source modes and source read/write/readback capability, distinct from storage-provider portability and internal dev governance.
2. Assigned four stable semantic features for category-E rows 21-24:
   - `ONBOARD-006` browser-only nontechnical installation with no terminal fallback;
   - `SOURCE-001` independent source read, source write and remote-readback gates;
   - `PROVIDER-001` provider-neutral AI runtime capability routing from observed evidence;
   - `SOURCE-002` explicit personal Git, organization Git, managed-central and no-Git/manual source lanes.
3. Verified `ONBOARD-006` has direct legacy regression coverage for no Command Prompt/PowerShell/Terminal/Git/GitHub CLI fallback, private GitHub-template creation, blocked-template behavior, mandatory readback fields and browser-only enterprise/alternative-runtime lanes.
4. Verified missing browser/template/runtime/source capability stays blocked; the installer does not substitute a fork, Codespace, download, local clone or terminal instructions.
5. Verified `SOURCE-001` through machine-readable gates and tests: ChatGPT GitHub read is independent from Codex/source write, and durable source mutation requires source write plus remote readback against the exact target.
6. Verified `PROVIDER-001` through deterministic router/tests: provider/runtime names are never proof; observed capabilities, data classification, exact organization approval evidence, source mode and requested module capabilities drive ready/degraded/blocked results.
7. Verified Claude/Microsoft runtime labels cannot bypass missing source-write evidence and regulated-sensitive data is blocked without current approval evidence/reference.
8. Verified unknown capability/request keys fail closed rather than being silently ignored.
9. Verified `SOURCE-002` explicitly supports `user-git`, `organization-git`, `managed-central`, and `none` source modes with distinct behavior.
10. Verified managed-central source can serve organization users without a personal Git account while personal source changes remain blocked or enter a managed change process.
11. Verified no-Git/manual portability cannot claim durable personal source mutation, unattended synchronization or automated writes.
12. Added ranked MIRA 2.0 work items `NONTECH-INSTALL-001`, `SOURCE-GATES-001`, `RUNTIME-ROUTER-001`, and `SOURCE-LANES-001`.
13. Rewired feature sharing, skill builder and discovery dependencies to the now-canonical source/runtime gate work where appropriate.
14. Recorded all four E5 features as legacy `test_verified` at the deterministic contract/core level while preserving MIRA 2.0 integration/live status as unverified.
15. Touched only `FEATURES.md`, `BACKLOG.md`, and `CURRENT_WORK.md` on this packet branch.
16. Touched no live Google production state and changed no executable MIRA 2.0 product behavior.

## Key audit findings

- Nontechnical installation UX is separate from the capabilities that make it work.
- Source read, source write and source remote readback are separate facts.
- ChatGPT-read/Codex-write is an adapter arrangement, not a universal architecture baked into MIRA.
- AI runtime/provider labels never imply feature parity, organization approval or write capability.
- Personal Git is one supported source lane, not a universal prerequisite.
- Managed/no-Git lanes must degrade honestly rather than creating personal-account workarounds or pretending to have durable source mutation.
- Browser-only means browser-only. Missing capability is a blocked state, not an excuse to smuggle in a shell tutorial.

## Blockers

None inside this forensic packet. `SOURCE-GATES-001`, `RUNTIME-ROUTER-001`, `SOURCE-LANES-001`, and `NONTECH-INSTALL-001` are ranked post-audit prerequisites for future onboarding/release proof.

## Exact next action

Open a pull request from `audit/g0-006e-nontechnical-source-runtime-onboarding` to `main`, verify changed-file scope is limited to `FEATURES.md`, `BACKLOG.md`, and `CURRENT_WORK.md`, merge it, remotely read back E5, then activate `M2-G0-006F` on current `main` and create branch `audit/g0-006f-provider-bootstrap-category-e-closure`.

## Next packet after merge

### `M2-G0-006F` — Feature Audit Slice E6 — provider onboarding/bootstrap and category-E closure

Audit exactly category-E rows 25-26:

1. Browser-only Google, Microsoft 365/OneDrive, Apple/iCloud and alternative-AI onboarding.
2. Installable provider-neutral MIRA skill and deterministic Personal Google bootstrap.
3. Reconcile category-E consistency/dependencies and close category E.

Do not expand this packet to category F provider/platform architecture, category G client surfaces or executable MIRA 2.0 product coding.

The exact first unaudited behavior is **Browser-only Google, Microsoft 365/OneDrive, Apple/iCloud and alternative-AI onboarding**.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head when tools permit;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture new customer ideas in BACKLOG unless required for acceptance or explicitly reprioritized;
6. before the final packet line, state any customer action needed; if none is needed, use `Just tell me to continue.`;
7. the final visible line remains the packet recovery tag.
