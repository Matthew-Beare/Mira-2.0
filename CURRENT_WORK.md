# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and its exact resume point.

## Completed packet before this branch

### `M2-G0-008C` — Canonical mutable authority boundary audit — legacy G1

- **Merged PR:** #30
- **Merge SHA / main readback:** `cbb64ab0939b1b10d62d40c8bd52f778cdf30d8f`
- **Result:** added `AUTH-001` Canonical Authority Registry and `STORE-001` provider-neutral structured/evidence-store adapter contracts; Google remains the accepted/default ordinary-user adapter direction rather than MIRROR semantic identity; routine state mutation does not require source-code mutation; provider/backend cutover is staged and never creates dual writable masters.

## Active packet

- **Packet ID:** `M2-G0-008D`
- **Name:** Policy/data API foundation audit — legacy G7, Android prerequisite
- **Class:** forensic audit / foundational prerequisite
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `audit/g0-008d-api-service-foundation`
- **Branch start SHA:** `cbb64ab0939b1b10d62d40c8bd52f778cdf30d8f`
- **Status:** activated; research not yet checkpointed.

## Exact audited scope

1. **G7 — Policy/data API** from the forensic ledger.
2. Determine the provider-neutral API/service boundary required for remote/companion clients to read and mutate canonical MIRROR state without becoming a second authority.
3. Reconcile G7 with existing `AUTH-001`, `STORE-001`, `PROFILE-013`, `RECOVERY-002`, `PROVIDER-001`, and source/runtime contracts only where evidence requires it.
4. Audit authentication, authorization/scope, stable identity, bounded commands/queries, idempotency, readback, error/failure isolation, auditability, version/schema compatibility, and client trust boundaries at specification/evidence level.
5. Inspect legacy runtime/platform contracts, tests, and PR #31 candidate API/service code conservatively.

Do **not** expand this packet into G10 Android/mobile-client behavior, G2/G3 provider portability, live provider provisioning, public-network deployment, executable MIRA 2.0 API coding, or Android application coding.

## Why this packet is next

- Legacy G10 Companion/mobile app explicitly requires G7 `api-service`.
- Current roadmap places the Android companion after the stock ChatGPT/core round-trip and requires it to read/mutate the same canonical reality state without becoming a second authority.
- G1 has now established the canonical authority/store boundary that an API must sit in front of.
- Therefore G7 is a direct foundational prerequisite for Android and outranks unrelated remaining category-G enhancements.

## Acceptance criteria

1. Assign/refine stable semantic feature ID(s) for the provider-neutral API boundary only if evidence warrants distinct identity.
2. Preserve `AUTH-001` as canonical authority routing and `STORE-001` as storage-adapter boundary; API clients never become canonical stores by themselves.
3. Define authenticated actor/client identity plus least-privilege resource/action scope; relationship labels or provider connection alone cannot grant access.
4. Define bounded query/command semantics, stable entity IDs, idempotent mutation/replay, optimistic/version conflict behavior where required, and exact read-after-write/readback.
5. Separate API success from downstream provider/store success; partial failures remain module/action scoped and auditable.
6. Define schema/API version compatibility and fail-closed handling for unknown/unsupported mutations.
7. Keep source-code mutation (`SOURCE-*`) separate from ordinary runtime state API mutation.
8. Reconcile legacy/PR #31 evidence conservatively; no implementation/live credit from contracts or unmerged candidate code alone.
9. Update only `FEATURES.md`, `BACKLOG.md`, `CURRENT_WORK.md` in this audit packet.
10. Open bounded PR, verify server-side changed-file scope and mergeability, merge using exact head SHA, and remotely read back `main`.
11. Touch no protected legacy production state and change no executable MIRA 2.0 behavior.

## Exact next action

1. Create branch `audit/g0-008d-api-service-foundation` from `cbb64ab0939b1b10d62d40c8bd52f778cdf30d8f`.
2. Audit legacy G7 ledger/dependency profiles and runtime/platform/API contracts.
3. Search PR #31 only for bounded API/service candidate evidence.
4. Checkpoint research before normalizing `FEATURES.md` or `BACKLOG.md`.

## Android milestone relation

Current dependency path is intentionally explicit:

`G7/API foundation audit` → remaining audit/dependency closeout → `AUTHORITY-REGISTRY-001` + `STORE-ADAPTER-001` + Google/bootstrap prerequisites → `DATA-SANDBOX` → `CORE-ROUNDTRIP` (stock ChatGPT) → `ANDROID-SYNC` / M2-M1.

G10 Android/mobile behavior will be audited after the G7 API boundary is stable; Android implementation still follows the stock-core round-trip so the app consumes one canonical authority rather than creating another.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head when tools permit;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture new customer ideas in BACKLOG unless required for acceptance or explicitly reprioritized;
6. finish each MIRA-development response with the configured continuation fallback and packet recovery tag.
