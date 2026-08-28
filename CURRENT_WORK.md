# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active implementation packet and its resume point.

## Completed packet before this branch

### `M2-G1-001A` — Synthetic structured-state adapter core

- **Merged PR:** #37
- **Merge SHA / main readback:** `a6550d6a44bbe8b02285204e9f475f8caa085d95`
- **Post-merge completion checkpoint / this branch start SHA:** `6b9f9c362da2732f938958810b030d007a543ffe`
- **Remote CI:** GitHub Actions run `33209577735`; compile + 11 unit tests passed.
- **Result:** `STORE-ADAPTER-001A` is implemented/test-verified.

## Active packet

### `M2-G1-002` — Canonical Authority Registry core

- **Work ID:** `AUTHORITY-REGISTRY-001`
- **Class:** implementation / foundational prerequisite
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `impl/g1-002-authority-registry`
- **Branch start SHA:** `6b9f9c362da2732f938958810b030d007a543ffe`
- **Status:** activated; implementation next.

## Objective

Implement a canonical persisted registry that binds each mutable data class to exactly one active authority and resolves that authority through an explicitly registered structured-state adapter.

## Acceptance criteria

1. Define stable Authority records with caller-supplied Authority IDs and bounded adapter/resource/namespace/failure-domain/owner/schema/verification metadata.
2. Persist Authority records and data-class bindings through `StructuredStateAdapter`; registry has no second mutable backing store.
3. Each mutable data class resolves to exactly one active Authority binding; missing binding fails explicitly.
4. Activating/replacing a binding requires optimistic expected revision and is replay-safe/idempotent.
5. Unknown, disabled, unverified or runtime-unregistered authority/adapter cannot resolve as healthy canonical authority.
6. Registering an Authority never silently activates it for a data class.
7. Runtime adapter registration is explicit and separate from persisted Authority metadata; possessing an adapter object grants no data-class authority by itself.
8. Routing returns exact Authority metadata plus the registered adapter without exposing provider/database credentials.
9. Deterministic tests prove registration/readback, activation, one-authority routing, replacement conflict, replay, disabled/unverified/unregistered failure and failure isolation.
10. No HTTP/API, Google/provider-specific adapter, cross-person permission, evidence-store or Android work.

## Scope guard

Allowed:
- Authority metadata/binding types and errors;
- persisted Authority Registry over `StructuredStateAdapter`;
- explicit runtime adapter registration/resolution;
- deterministic unit tests and package exports.

Excluded:
- HTTP/API endpoints/authentication;
- provider-specific adapters;
- credentials/secrets;
- cross-person permission engine;
- evidence store;
- Android/client code;
- legacy production state.

## Exact next action

1. Implement `mira/authority.py` over the merged structured-state contract.
2. Extend package exports and add deterministic registry tests.
3. Run full local suite, then bounded PR/remote CI.
4. Record evidence and merge exact green head.
5. Advance to `API-CORE-001` only after this packet is test-verified.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture unrelated ideas in BACKLOG unless required for acceptance or explicitly reprioritized.
