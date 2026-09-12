# MIRA 2.0 CURRENT WORK

Git is authoritative. This branch records exactly one active packet.

## Active packet

### `M2-M1-040` — Ops mutable-fact authority and receipt-to-inventory reliability

- **Repository:** `Matthew-Beare/Mira-2.0`.
- **Branch:** `work/m2-m1-040-ops-evidence-authority`.
- **Base SHA:** `6551691c7836a9c70a8be080cd11bb2ee18536d2`.
- **Packet:** `docs/work-packets/M2-M1-040.md`.
- **Trigger:** a shipment ETA was reported without live carrier readback, then a false user-supplied ETA was accepted despite an existing tracking number; durable receipt-to-inventory processing was also found to be implied rather than enforced end-to-end.
- **Owned surfaces:** `mira/ops_evidence_policy.py`, `tests/test_ops_evidence_policy.py`, `docs/OPS_EVIDENCE_AUTHORITY_CONTRACT.md`, this packet document, this branch `CURRENT_WORK.md`, and enabled AM/PM brief prompt policy as live operational deployment state.
- **Shared/high-contention surface:** this branch `CURRENT_WORK.md` only.
- **Out of scope:** Studio implementation, financial authority changes, wholesale historical receipt migration, or private production data in public Git.

## Implemented

- Added deterministic shipment authority resolution: when tracking exists, carrier readback is required for verified ETA/status; secondary user/vendor values cannot be promoted to carrier truth.
- Added deterministic durable-purchase commit gate: non-consumables require ownership confirmation, receipt evidence identity, archived receipt link, category, canonical record identity, matching receipt link on the canonical record, and successful readback.
- Consumables explicitly do not require durable inventory records.
- Added public provider-neutral policy documentation with no private operational identifiers.
- Added six synthetic unit tests covering the exact false-ETA failure and receipt-to-inventory completion gates.
- Isolated local test execution: **6 passed**.
- Live Workspace inspection confirmed existing authorities already support the intended chain: purchase/receipt archive physical-asset identity/relationship tables plus tool inventory receipt-link fields. No duplicate inventory store is needed.

## Acceptance criteria

1. Tracking present + no carrier readback + user/vendor ETA => no verified ETA. **PASS in deterministic test.**
2. Tracking present + live carrier readback => carrier state wins. **PASS in deterministic test.**
3. Receipt email alone cannot commit a durable purchase. **PASS in deterministic test.**
4. Receipt-link mismatch fails closed. **PASS in deterministic test.**
5. Full durable evidence/archive/inventory/link/readback chain can commit. **PASS in deterministic test.**
6. Consumables do not create mandatory durable inventory rows. **PASS in deterministic test.**
7. Enabled AM and PM brief prompts explicitly enforce both contracts. **PENDING deployment/readback.**
8. Exact remote branch head/readback and integration evidence recorded. **PENDING.**

## Exact next action / resume point

1. Update the enabled MIRA AM Brief and MIRA PM Brief prompts with the fact-specific live-authority and receipt-to-inventory commit rules.
2. Read both automation definitions back and confirm deployment.
3. Re-read this branch head and changed files, then record the exact head here.
4. Check current `main` and open PR overlap before integration.

## Evidence ceiling

This packet can enforce fail-closed behavior when the live authority cannot be read. It cannot guarantee that every carrier/provider exposes package-specific state to every runtime. Lack of carrier readback therefore results in `UNVERIFIED`, never a fabricated or merely repeated ETA.
