# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active implementation packet and its resume point.

## Completed packet before this branch

### `M2-G1-002` — Canonical Authority Registry core

- **Merged PR:** #38
- **Merge SHA / main readback:** `a453e54c437a697daa592e51f336a9604dffd8e2`
- **Post-merge completion checkpoint / this branch start SHA:** `1d4d0108408e76a34a1dea4dcef0cb690e5dd96c`
- **Remote CI:** GitHub Actions run `33209898891`; compile + 19 unit tests passed.
- **Result:** `AUTHORITY-REGISTRY-001` is implemented/test-verified.

## Active packet

### `M2-G1-003A` — API service semantics core

- **Work ID:** `API-CORE-001A`
- **Class:** implementation / security-data-integrity prerequisite
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `impl/g1-003a-api-service-core`
- **Branch start SHA:** `1d4d0108408e76a34a1dea4dcef0cb690e5dd96c`
- **Status:** activated; implementation next.

## API umbrella split

`API-CORE-001` remains an umbrella:
1. `API-CORE-001A` — transport-independent service semantics (active).
2. `API-CORE-001B` — scoped client/session authentication + HTTP transport (next after 001A).

The umbrella is complete only when both are verified.

## Objective

Implement a transport-independent API service core that accepts already-authenticated principal context, authorizes exact same-user actions, rejects incompatible/invalid envelopes before state access, routes only through `AuthorityRegistry`, requires idempotency for commands, maps conflicts explicitly, verifies read-after-write and emits audit events.

## Acceptance criteria

1. Versioned query/command envelopes with subject, data class, action/resource identity and explicit API/schema versions.
2. Authenticated-principal contract with stable actor/client IDs and explicit grants; no token/session issuance in this packet.
3. Same-user only: subject must equal actor; cross-person requests fail closed.
4. Exact resource/action authorization before authority resolution/mutation; query requires class-level query grant.
5. API-major/schema incompatibility and unknown/malformed action fail before mutation.
6. Commands require non-empty idempotency keys and forward expected revision.
7. Canonical reads/writes route only through `AuthorityRegistry`.
8. Upsert performs exact read-after-write comparison and fails explicitly on mismatch.
9. Structured revision/idempotency/validation failures map to stable API error categories.
10. Synthetic audit sink records actor/client/action/resource/outcome for allowed, denied and failed requests without becoming business-state authority.
11. Deterministic tests prove read/query/upsert/replay/authz/cross-person/compatibility/conflict/readback/audit behavior.
12. No HTTP server, token/session issuance, provider-specific adapter, Google, Android, evidence store or legacy production state.

## Scope guard

Allowed:
- API envelope/principal/grant/audit/result/error types;
- transport-independent service core;
- deterministic synthetic audit sink;
- tests and package exports.

Excluded:
- HTTP/FastAPI/network listener;
- credential/token/session issuance or persistence;
- provider-specific adapters/deployment;
- cross-person permission engine;
- Android/client code;
- evidence store;
- legacy production state.

## Exact next action

1. Implement `mira/api_core.py` over `AuthorityRegistry` and `StructuredStateAdapter`.
2. Add deterministic tests and exports.
3. Run full local suite and fix only packet-scoped failures.
4. Open bounded PR and require remote CI green.
5. Merge exact verified head, then activate `M2-G1-003B`.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture unrelated ideas in BACKLOG unless required for acceptance or explicitly reprioritized.
