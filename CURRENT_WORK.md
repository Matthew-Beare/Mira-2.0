# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and its exact resume point.

## Completed packet before this branch

### `M2-G0-008C` — Canonical mutable authority boundary audit — legacy G1

- **Merged PR:** #30
- **Merge SHA / main readback:** `cbb64ab0939b1b10d62d40c8bd52f778cdf30d8f`
- **Main activation sequence:** `b457c531164510fe1e294dc93965521d42f688f5` then branch-start correction `fc95d1c89f4592ebc92cd649349c4f7f5d2fcce6`
- **Result:** added `AUTH-001` Canonical Authority Registry and `STORE-001` provider-neutral structured/evidence-store adapter contracts; Google remains the accepted/default ordinary-user adapter direction rather than MIRROR semantic identity; routine state mutation does not require source-code mutation; provider/backend cutover is staged and never creates dual writable masters.

## Active packet

- **Packet ID:** `M2-G0-008D`
- **Name:** Policy/data API foundation audit — legacy G7, Android prerequisite
- **Class:** forensic audit / foundational prerequisite
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `audit/g0-008d-api-service-foundation`
- **Branch start SHA:** `fc95d1c89f4592ebc92cd649349c4f7f5d2fcce6`
- **Status:** audit normalized and packet-close checkpoint written; PR/server-side verification and merge remain.

## Exact audited scope

1. **G7 — Policy/data API** from the forensic ledger.
2. Determine the provider-neutral API/service boundary required for remote/companion clients to read and mutate canonical MIRROR state without becoming a second authority.
3. Reconcile G7 with existing `AUTH-001`, `STORE-001`, `PROFILE-013`, `RECOVERY-002`, `PROVIDER-001`, and source/runtime contracts only where evidence requires it.
4. Audit authentication, authorization/scope, stable identity, bounded commands/queries, idempotency, readback, error/failure isolation, auditability, version/schema compatibility, and client trust boundaries at specification/evidence level.
5. Inspect legacy runtime/platform contracts, tests, and PR #31 candidate API/service code conservatively.

Do **not** expand this packet into G10 Android/mobile-client behavior, G2/G3 provider portability, live provider provisioning, public-network deployment, executable MIRA 2.0 API coding, or Android application coding.

## Canonical G7 result

1. G7 warrants stable semantic feature **`API-001` — Versioned authenticated MIRROR client service boundary with bounded commands, queries, synchronization and verified mutation readback**.
2. `API-001` is a boundary in front of `AUTH-001`/`STORE-001`; it is not a new canonical data store and no client becomes an authority merely by using the API.
3. All approved clients and AI runtimes converge on the same bounded service semantics. No client receives direct database credentials and no UI owns reconciliation/business policy.
4. Required API classes include authenticated identity/session; bounded query/read models; bounded command/mutation with stable canonical IDs and idempotency; evidence ingress/metadata; integration/capability health; synchronization cursor/event feed; dependency health; and release/update/rollback status where supported.
5. Mutation requires server-side authentication, authorization, dependency/capability preflight, schema/version validation, stable identity/idempotency, canonical-authority write, exact readback and audit event.
6. Remote API transport requires TLS. Public exposure requires strong identity auth, short-lived/scoped credentials, server authorization, rate limiting/audit logging and least privilege; private overlay remains preferred for personal homelab use.
7. `PROFILE-013` remains person/resource/action authorization truth where shared/cross-person access applies. Relationship labels or merely possessing a provider connection cannot grant API resource access.
8. Source mutation (`SOURCE-*`) remains separate from runtime state mutation. Ordinary entity/task/inventory/etc API commands cannot require or imply source-code write authority.
9. API-version compatibility is explicit. Incompatible clients may read compatibility information but must not mutate. Breaking changes require a new API major; unknown/unsupported mutations fail closed.
10. The API/server is conflict authority. Canonical implementation must define stale-version/conflict behavior instead of allowing silent last-writer-wins mutation where state races matter.
11. G10 Companion/mobile app explicitly depends on G7; therefore G7 is a direct Android prerequisite.

## Legacy / PR #31 evidence ceiling

- `docs/runtime-platform-architecture.md` strongly specifies one provider-neutral service/API boundary for web/Android/desktop/CLI/AI clients.
- `starter/runtime-interface-contract.json` machine-defines `client_api` operations: authenticate, query read model, submit idempotent command, upload evidence, register capabilities, sync events, dependency health and update/rollback status.
- `starter/client-api-contract.json` specifies API contract 1.1, command envelope (`command_id`, `command_type`, `actor_id`, `submitted_at`, `idempotency_key`, `payload`), server auth/authz/preflight/schema/idempotency/write/readback/audit responsibilities, cursor sync and client security rules.
- `starter/network-security-contract.json` specifies TLS, scoped short-lived tokens, server-side authorization, rate limiting/audit logging, private-overlay preference and prohibition on direct public database/client DB credentials.
- Legacy tests prove client surfaces use provider-neutral HTTP API contracts, prohibit direct DB credentials, enforce shared release/API-version declarations, and build Android/desktop artifacts from the shared API contract.
- PR #31 `starter/service/app.py` is real unmerged candidate code with `/v1/health`, compatibility, query/read models, `/v1/commands`, evidence ingress, canonical UUIDs, audit events and several direct post-write readbacks.
- PR #31 `starter/service/run.py` installs outer API auth, CORS, device auth, idempotency, compatibility/release and modular service extensions.
- PR #31 `starter/service/device_auth.py` provides expiring single-use enrollment codes, hashed device tokens, revoke/rotate and credential readback; this is useful candidate evidence, not completed scoped authorization.
- PR #31 `starter/service/idempotency.py` provides replay storage and duplicate-processing protection for `/v1/commands` when `Idempotency-Key` is supplied.
- Candidate gaps prevent promotion to implementation/live proof: device tokens are broadly valid rather than resource/action-scoped; bootstrap token is broad; command idempotency header is optional; missing API-version header can still mutate; core command handler does not enforce the full contract envelope/actor scope; no generic per-resource/action authorization layer was found; asset update path has no audited optimistic version/conflict token; candidate service writes directly to SQLite rather than the newly canonical `AUTH-001`/`STORE-001` adapter boundary.
- PR #31 remains salvage/reference only. No MIRA 2.0 runtime/API integration or live network/provider proof is claimed.

## Normalized Git evidence

- Research checkpoint commit: `3c8054c0c034f21489d90499986ef06a28a512d5` — `Checkpoint G7 API forensic findings`.
- Feature normalization commit: `06c2fcc4a7059dc40a43df802786dc7712a2b4a0` — `Normalize G7 API feature boundary`.
- Backlog/dependency normalization commit: `40ac6241b5c8a50978a907f4ea40d621e35995c5` — `Normalize G7 API backlog dependencies`.
- `FEATURES.md` now contains `API-001` and the G7 foundation mapping.
- `BACKLOG.md` now contains completed `AUDIT-G7`, security/data-integrity blocker `API-CORE-001`, G7/API dependency findings, and `CORE-ROUNDTRIP` explicitly depends on `API-CORE-001`.
- No executable MIRA 2.0 code, provider state, protected legacy data, or files outside `FEATURES.md`, `BACKLOG.md`, and `CURRENT_WORK.md` are intended to change in this packet.

## Acceptance criteria

1. Stable semantic API feature. **Satisfied: `API-001`.**
2. Preserve `AUTH-001`/`STORE-001` authority boundaries. **Satisfied.**
3. Authenticated actor/client identity and least-privilege scope. **Specified; candidate is incomplete and gap is explicit.**
4. Bounded query/command, stable IDs, idempotency, conflict/readback. **Specified; candidate partial, canonical gap explicit.**
5. Module/action-scoped failure and auditable downstream outcome. **Satisfied at contract boundary.**
6. API/schema version compatibility and fail-closed mutation. **Specified/test-supported; candidate has missing-header gap.**
7. Source write separate from runtime state API. **Satisfied.**
8. Conservative legacy/PR31 evidence. **Satisfied.**
9. Only `FEATURES.md`, `BACKLOG.md`, `CURRENT_WORK.md`. **Satisfied by intended branch scope; final server-side file-list verification pending.**
10. Bounded PR/merge/readback. **Pending.**
11. No protected legacy production or executable MIRA 2.0 changes. **Satisfied by packet scope; final diff verification pending.**

## Exact next action

1. Compare `audit/g0-008d-api-service-foundation` against `main`; require exactly `FEATURES.md`, `BACKLOG.md`, `CURRENT_WORK.md` changed.
2. Open bounded PR for `M2-G0-008D`.
3. Verify server-side changed-file scope, PR mergeability and exact current head SHA.
4. Merge using the exact verified head SHA.
5. Remotely read back `main` and record the merge SHA/packet completion before activating the next packet.
6. After merge, audit G10 Android/mobile client boundary next unless a higher integrity prerequisite emerges from Git.

## Android milestone relation

Current dependency path is intentionally explicit:

`API-001/G7 audit` → remaining audit/dependency closeout → `AUTHORITY-REGISTRY-001` + `STORE-ADAPTER-001` + `API-CORE-001` + Google/bootstrap prerequisites → `DATA-SANDBOX` → `CORE-ROUNDTRIP` through the shared API → `ANDROID-SYNC` / M2-M1.

G10 Android/mobile behavior remains a separate audit packet, but it no longer needs an undefined backend boundary: it will consume `API-001`.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head when tools permit;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture new customer ideas in BACKLOG unless required for acceptance or explicitly reprioritized;
6. finish each MIRA-development response with the configured continuation fallback and packet recovery tag.
