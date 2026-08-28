# MIRA 2.0 CURRENT WORK

Git is authoritative. This file records the completed Authority Registry packet and exact API successor.

## Completed packet

### `M2-G1-002` — Canonical Authority Registry core

- **Work ID:** `AUTHORITY-REGISTRY-001`
- **Merged PR:** #38
- **Merge SHA / main readback:** `a453e54c437a697daa592e51f336a9604dffd8e2`
- **Branch:** `impl/g1-002-authority-registry`
- **Branch start SHA:** `6b9f9c362da2732f938958810b030d007a543ffe`
- **CI-verified PR head:** `f6ac3c983d5cbf625cb6023b578abd66b53e839a`
- **GitHub Actions run:** `33209898891`
- **Remote verification:** compile succeeded; full suite **19 tests, 0 failures/errors**.
- **Result:** persisted Authority metadata, one binding per data class, optimistic/idempotent binding replacement, explicit runtime adapter mounts, fail-closed disabled/unverified/unregistered/unhealthy/schema-mismatched resolution and data-class failure isolation are implemented/test-verified.

## API umbrella split before implementation

`API-CORE-001` is too large for one safe packet. It is split before growth:

1. **`API-CORE-001A` — in-process API service semantics**: authenticated-principal contract, command/query envelopes, same-user resource/action authorization, API/schema compatibility preflight, Authority Registry routing, mandatory idempotency, conflict mapping, exact read-after-write verification and synthetic audit sink. No HTTP/network/session issuance.
2. **`API-CORE-001B` — client authentication + transport boundary**: scoped/revocable client/session identity, HTTP transport, request parsing/error mapping and transport security hooks over 001A. No deployment/provider work.

The umbrella `API-CORE-001` is complete only after both children are verified. This preserves the selected architecture while keeping packets bounded.

## Selected successor

### `M2-G1-003A` — API service semantics core

- **Work ID:** `API-CORE-001A`
- **Class:** implementation / security-data-integrity prerequisite
- **Planned branch:** `impl/g1-003a-api-service-core`
- **Dependencies satisfied:** `STORE-ADAPTER-001A`, `AUTHORITY-REGISTRY-001`.

### Objective

Implement a transport-independent API service core that accepts already-authenticated principal context, authorizes exact same-user actions, rejects incompatible/invalid mutation envelopes before state access, routes only through `AuthorityRegistry`, requires idempotency for commands, maps conflicts explicitly, verifies read-after-write and emits audit events.

### Acceptance criteria

1. Define versioned query/command envelopes with actor subject, data class, action/resource identity and explicit API/schema versions.
2. Define an authenticated-principal contract with stable actor/client IDs and explicit grants; this packet does **not** issue/authenticate tokens.
3. Same-user only: subject must equal authenticated actor; cross-person requests fail closed until permission-scope work exists.
4. Exact resource/action authorization is checked before authority resolution/mutation; query requires class-level query grant.
5. API-major/schema incompatibility and malformed/unknown action fail before mutation.
6. Commands require non-empty idempotency keys and forward expected revision to the structured adapter.
7. All canonical reads/writes route through `AuthorityRegistry`; no direct provider/store selection in service code.
8. Upsert mutation performs exact read-after-write comparison; mismatch fails explicitly.
9. Structured revision/idempotency/validation conflicts map to stable API error categories without hiding canonical state.
10. Synthetic audit sink records actor/client/action/resource/outcome for allowed, denied and failed requests without becoming business-state authority.
11. Deterministic tests prove compatible read/query/upsert/replay, authz denial, cross-person denial, compatibility failure, conflict mapping, readback verification and audit behavior.
12. No HTTP server, token/session issuance, provider-specific adapter, Google, Android, evidence store or legacy production state.

## Exact next action

1. Create `impl/g1-003a-api-service-core` from this exact main checkpoint.
2. Activate `M2-G1-003A` on the branch.
3. Implement transport-independent service core and tests only.
4. Require full local + GitHub CI green before merge.
5. Then activate `M2-G1-003B` for authentication/HTTP transport.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture unrelated ideas in BACKLOG unless required for acceptance or explicitly reprioritized.
