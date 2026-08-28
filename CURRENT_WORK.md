# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active integrity-bootstrap packet and its resume point.

## Completed packet before this branch

### `M2-M0-002` — Minimal Google structured-state adapter

- **Merged PR:** #45
- **Merge SHA / main readback:** `88d7b4666fbcf4b77ea60baa3c4b3735bfa5aadb`
- **Post-merge completion checkpoint / this branch start SHA:** `7929404403b56286a25399b16797658885cc2d97`
- **Remote CI:** final run `33212658200`; compile + feature registry + code ownership + full suite succeeded.
- **Result:** Google Sheets adapter code is implemented/test-verified; live sandbox schema and equivalent mutation/readback are provider-readback verified; live Python OAuth execution remains pending deployment.

## Active packet

### `M2-M0-003` — Persistent Google Authority Registry bootstrap

- **Related work IDs:** `AUTHORITY-REGISTRY-001`, `GOOGLE-STORE-ADAPTER-001`
- **Class:** hard deployment prerequisite / integrity bootstrap
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `integration/m0-003-google-authority-bootstrap`
- **Branch start SHA:** `7929404403b56286a25399b16797658885cc2d97`
- **Status:** activated; provider metadata/routing bootstrap and runtime helper next.

## Objective

Persist and verify the M2-M0 `entity` Authority route in the isolated Google store, then implement an idempotent runtime bootstrap that creates missing routing state once and fails closed if existing routing differs materially.

## Acceptance criteria

1. Live sandbox `resource_types_json` exactly includes `authority`, `authority_binding`, and `entity`.
2. Persist one verified/enabled synthetic Google Sheets Authority with logical non-secret resource reference.
3. Persist one `authority_binding` for data class `entity`.
4. Provider rows use adapter-compatible fingerprints/idempotency result envelopes and exact readback.
5. Runtime bootstrap registers the adapter and creates missing Authority/binding with deterministic keys.
6. Repeated bootstrap is read-only/idempotent after routing exists.
7. Existing materially different Authority/binding fails closed; no silent overwrite/rebind.
8. Tests prove first boot, restart, mismatch rejection, and `resolve("entity")`.
9. Update code ownership/direct verification.
10. No live provider IDs/credentials/private data in Git.
11. All CI gates green; bounded PR/merge/readback.

## Exact next action

1. Extend provider metadata resource types.
2. Write/read back synthetic Authority and entity binding using adapter-equivalent rows.
3. Implement `mira/runtime_bootstrap.py` and tests.
4. Update ownership manifest, PR/CI/merge.
5. Proceed to provider-neutral managed-runtime/container packet.

## Recovery protocol

Read this file first, verify branch/head, rediscover provider resources when needed, keep live provider identifiers out of Git, and continue only this packet unless blocked.
