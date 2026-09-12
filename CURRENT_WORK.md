# MIRA 2.0 CURRENT WORK

Git is authoritative. This branch records exactly one active packet.

## Active packet

### `M2-M1-040` — Ops mutable-fact authority and receipt-to-inventory reliability

- **Primary work:** `OPS-BRIEF-VSLICE`, `RECEIPT-INTAKE-001`, `ASSET-ACQUISITION-001`.
- **Primary features:** `OPS-004`, `ORDER-001`, `RECEIPT-001`, `ASSET-001`.
- **Related invariants/features:** `AUTH-001`, `RECOVERY-002`, `TASK-002`, `INV-001`, `FITMENT-001`.
- **Repository:** `Matthew-Beare/Mira-2.0`.
- **Branch:** `work/m2-m1-040-ops-evidence-authority`.
- **Base SHA:** `6551691c7836a9c70a8be080cd11bb2ee18536d2`.
- **Latest implementation/evidence checkpoint before this CURRENT_WORK write:** `05d97acefc84d388df86c0a2c7563a8a83098d37`.
- **Packet:** `docs/work-packets/M2-M1-040.md`.
- **Trigger:** a shipment ETA was reported without live carrier readback, then a false user-supplied ETA was accepted despite an existing tracking number; durable receipt-to-inventory processing was also found to be implied rather than enforced end-to-end.
- **Owned surfaces:** `mira/authority.py`, `tests/test_ops_evidence_policy.py`, `docs/OPS_EVIDENCE_AUTHORITY_CONTRACT.md`, this packet document, this branch `CURRENT_WORK.md`, and enabled AM/PM brief prompt policy as live operational deployment state.
- **Shared/high-contention surface:** this branch `CURRENT_WORK.md` only. `project/code_ownership.json` is deliberately untouched because Studio PR #153 has a separate additive change there.
- **Out of scope:** Studio implementation, financial authority changes, wholesale historical receipt migration, or private production data in public Git.

## Implemented and deployed

- Added provider-neutral shipment authority resolution to the existing canonical Authority boundary: when tracking exists, carrier readback is required for verified ETA/status; secondary user/vendor values cannot be promoted to carrier truth.
- Added provider-neutral durable-purchase commit gating: non-consumables require ownership confirmation, receipt evidence identity, archived receipt link, category, canonical record identity, matching receipt link on the canonical record, and successful readback.
- Consumables explicitly do not require durable inventory records.
- Added public provider-neutral policy documentation with no private operational identifiers.
- Added six synthetic regression tests covering the exact false-ETA failure and receipt-to-inventory completion gates; isolated run passed all six.
- Live Workspace inspection confirmed existing authorities already support the intended chain: purchase/receipt archive physical-asset identity/relationship tables plus tool inventory receipt-link fields. No duplicate inventory store is needed.
- Enabled MIRA AM Brief prompt updated and read back with mandatory live-fact authority and receipt-to-inventory contracts.
- Enabled MIRA PM Brief prompt updated and read back with the same contracts.
- Open Studio PR #153 ownership-manifest patch was inspected. It only adds `studio-intake`; this packet avoids touching the manifest and therefore avoids manufacturing a concurrent merge conflict there.

## CI history

- PR #155 CI #605: compile/feature-registry/product-lifecycle/distribution passed; work-session alignment failed because the first checkpoint omitted required alignment metadata. Fixed without bypassing the gate.
- PR #155 CI #606: alignment passed; code ownership failed because the first implementation created a new unregistered `mira/ops_evidence_policy.py`. Fixed without weakening ownership enforcement by moving the policy into already-owned `mira/authority.py`, retargeting tests, and deleting the redundant unowned module.
- Exact-head full CI after the code-ownership-safe placement is **pending**.

## Acceptance criteria

1. Tracking present + no carrier readback + user/vendor ETA => no verified ETA. **PASS in deterministic test.**
2. Tracking present + live carrier readback => carrier state wins. **PASS in deterministic test.**
3. Receipt email alone cannot commit a durable purchase. **PASS in deterministic test.**
4. Receipt-link mismatch fails closed. **PASS in deterministic test.**
5. Full durable evidence/archive/inventory/link/readback chain can commit. **PASS in deterministic test.**
6. Consumables do not create mandatory durable inventory rows. **PASS in deterministic test.**
7. Enabled AM and PM brief prompts explicitly enforce both contracts. **PASS — deployed and read back.**
8. Exact remote branch and integration evidence recorded. **PRE-MERGE PASS; final CI/post-merge verification pending.**

## Session-start alignment verification — 2026-09-12

### `FEATURES.md`

This reliability repair is directly grounded in canonical existing features rather than inventing a new product surface. `OPS-004` requires a fresh standalone run rather than replayed/stale state; `ORDER-001` requires evidence-grounded order/carrier correlation; `RECEIPT-001` requires canonical evidence dedupe; `ASSET-001` requires idempotent acquisition. `AUTH-001`, `RECOVERY-002`, `TASK-002`, `INV-001`, and `FITMENT-001` provide the authority, failure-isolation, honest-state, inventory-participation, and explicit relationship invariants used by the repair.

### `BACKLOG.md`

`OPS-BRIEF-VSLICE`, `RECEIPT-INTAKE-001`, and `ASSET-ACQUISITION-001` are existing canonical work items whose completed boundaries this packet hardens. The packet does not reopen or redefine those implementations; it adds a bounded integrity guard discovered by live failure evidence. No duplicate receipt, asset, inventory, or brief subsystem is introduced.

### `ROADMAP.md`

The repair preserves the Personal Google/no-app direction and restores trustworthy user-visible operation. It is an integrity interruption under the existing roadmap, not a scope expansion. Existing provider/Workspace surfaces remain the runtime path, and the open Studio packet remains isolated for later resumption.

### Direction result

ALIGNED

## Exact next action / resume point

1. Require PR #155 exact-head CI green after the code-ownership-safe placement.
2. Re-read `main` immediately before merge and recheck PR #153 overlap.
3. If CI is green and `main` remains compatible, merge PR #155 with expected-head protection.
4. Read back post-merge `main` and exact post-merge CI/status evidence.
5. Preserve/reconcile Studio PR #153 rather than discarding its concurrent work.

## Evidence ceiling

This packet enforces fail-closed behavior when the live authority cannot be read. It cannot guarantee that every carrier/provider exposes package-specific state to every runtime. Lack of carrier readback therefore results in `UNVERIFIED`, never a fabricated or merely repeated ETA.
