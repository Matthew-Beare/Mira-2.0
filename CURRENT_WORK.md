# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and its exact resume point.

## Completed packet

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
- **Status:** forensic evidence pass complete; feature/backlog normalization pending.

## Stable feature mapping from forensic pass

1. `ONBOARD-006` — browser-only nontechnical installation with no terminal fallback.
2. `SOURCE-001` — independent source read, source write and remote readback capability gates, including ChatGPT GitHub read versus Codex GitHub write.
3. `PROVIDER-001` — provider-neutral AI runtime capability routing from observed actions/readback, never brand inference.
4. `SOURCE-002` — explicit personal Git, organization Git, managed-central and no-Git/manual source lanes.

`SOURCE-*` is a separate semantic family because durable source lineage/capability is neither a storage provider nor a generic development-internal concern.

## Forensic findings already established

1. `INSTALL.md` explicitly defines the default onboarding path as browser-only: no Command Prompt, PowerShell, Terminal, Git Bash, code editor, Git, GitHub CLI, copied commands, tokens or SSH keys.
2. Browser template creation is fail-closed: if the GitHub template action is unavailable, onboarding stops rather than substituting a fork, Codespace, download, local copy or command-line clone.
3. The personal lane explicitly separates three jobs: GitHub creates the private personal repository, the ChatGPT GitHub app provides read access, and Codex provides lasting source write capability.
4. The read-only ChatGPT GitHub app is explicitly not proof of Codex write capability. Missing write produces a blocked source-setup state; onboarding may continue conversationally but lasting source mutation remains blocked and no CLI fallback is offered.
5. `install-flow.json` is a machine-readable onboarding contract with separate `chatgpt-github-read` and `codex-github-write` gates, exact readback fields, explicit blocked states and a forbidden-action list including CLI installation, read-means-write claims, provider-name capability claims, personal-account policy bypass and success-before-readback.
6. `test_nontechnical_installation.py` directly regression-tests the no-terminal entrypoint, private GitHub-template flow, independent read/write gates, mandatory readback fields and capability-gated enterprise/alternative-runtime lanes.
7. `PLATFORM_PORTABILITY.md` explicitly states that ChatGPT, Claude, Microsoft/organization AI, Gemini and other runtimes do not have automatic feature parity. Each runtime may use the portable core only to the extent that observed tools/permissions satisfy the required contracts.
8. `provider_capability_router.py` deterministically evaluates observed capability booleans, source mode, environment/data classification and requested module capabilities. Unknown capabilities/requests fail closed.
9. The provider router treats `user-git`, `organization-git`, `managed-central`, and `none` as separate source modes. User/org Git require source read + write + remote readback for durable source mutation; managed-central requires readable pinned release and degrades personal policy writes into a managed change process; no-Git/manual mode explicitly lacks durable source lineage for personal changes.
10. Regulated-sensitive data is blocked unless the exact runtime/storage/data use has organization approval plus a current approval-evidence reference.
11. `test_platform_portability.py` directly verifies provider-name-is-not-proof, live write/readback requirements, Claude/Microsoft labels not bypassing missing source write, managed-source behavior, regulated-data approval gates, no fake iCloud automation and fail-closed unknown capabilities.
12. `platform-capabilities.json` enumerates runtime, storage, source and deployment lanes and records the same claim policy. Personal GitHub, GitHub Enterprise, GitLab, Azure Repos and managed-central source are distinct source backends; portable-manual explicitly disables unattended automation/write claims.
13. All four E5 rows therefore have genuine legacy `test_verified` sub/core evidence. MIRA 2.0 has not yet integration/live-verified its own browser install, source read/write/readback, alternate runtime or organization/no-Git lane.
14. No live Google production state was touched and no executable MIRA 2.0 product behavior changed.

## Exact next action

Normalize the four E5 features into `FEATURES.md`, add only the required MIRA 2.0 implementation/readback gaps to `BACKLOG.md`, then update this file with final acceptance evidence and the E6 resume point. Release E5 through a three-authority-file PR/merge/readback gate.

## Next packet after merge

### `M2-G0-006F` — Feature Audit Slice E6 — provider onboarding/bootstrap and category-E closure

Audit category-E rows 25-26:
1. Browser-only Google, Microsoft 365/OneDrive, Apple/iCloud and alternative-AI onboarding.
2. Installable provider-neutral MIRA skill and deterministic Personal Google bootstrap.
3. Perform category-E consistency closure.

Do not begin category F inside E5.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head when tools permit;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture new customer ideas in BACKLOG unless required for acceptance or explicitly reprioritized;
6. before the final packet line, state any customer action needed; if none is needed, use `Just tell me to continue.`;
7. the final visible line remains the packet recovery tag.
