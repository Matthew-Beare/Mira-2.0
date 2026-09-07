# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active/recovery packet and the exact safe resume point. Detailed prior evidence remains preserved in Git history and packet checkpoints.

## Active packet

### `M2-M1-014` — Financial Escape budget intake and earmark reconciliation

- **Primary work:** `FIN-BUDGET-RECON-001`, `FIN-EARMARK-001`.
- **Related packet:** `M2-M1-013` Financial Escape private-live vertical.
- **Repository:** `Matthew-Beare/Mira-2.0`.
- **Base main before interruption:** `266a9da57ebd2136c270061ea23e736d56b3d1e1`.
- **Packet-start checkpoint:** `6faec5e62fed1ebd00b0b6509f96adc55c02fef2`.
- **Current status:** customer-priority interruption is active. Newly shared private household budget/income evidence is being reconciled non-destructively into the existing private Financial Escape projection. Existing forecast/history state must not be overwritten merely because the new source differs.

## Objective

Preserve the newly shared budget/income evidence as a comparison/scenario source, represent current checking earmarks and recurring allowance balances without changing provider-observed balances, update the existing protected project reserve through its established assumption path, and verify that free/discretionary cash excludes earmarked money without double counting.

## Acceptance / hold rules

- The source budget/income document is read-only evidence.
- Materially different source assumptions go into a separate private projection tab rather than overwriting the current budget basis.
- Linked-account balances remain provider observations; earmarks are allocation semantics only.
- Existing transaction history, daily snapshots, normalized-spend history, debt history, mileage history, and forecast history are preserved.
- Protected reserves and checking earmarks remain separate where their funding semantics differ.
- Current allowance balances are forward starting balances; recurring monthly additions begin on the next first-of-month boundary and do not retroactively add the current month.
- No purchase-to-allowance debit automation is activated in this packet.
- No private values, document IDs, spreadsheet IDs, or account identifiers are committed to public Git.

## Displaced packet checkpoint

### `M2-M1-012` — Android representative-device execution proof

`M2-M1-012` is displaced but fully preserved. Its scope, evidence, and exact resume point are unchanged by this Financial Escape interruption.

- **Primary work:** `ANDROID-CLIENT-CORE-001`.
- **Primary features:** `CLIENT-ANDROID-001`, `API-001`.
- **Recovery branch:** `work/m2-m1-012-provider-tooling-hold-2`.
- **Stable pre-Financial-Escape checkpoint:** `6e715159feed0b044e3ef3ef610916903e2deb09`.
- **Status:** blocked at provider-configuration inspection because no authenticated Google Cloud OAuth/API administration capability is currently available in regular Chat and prior browser-capable provider attempts failed before provider state could be read.

### Android evidence already earned

1. The exact stable-development-signed proof APK installed and launched on a representative Android device.
2. Tapping **Connect Google Workspace** opened Google's native account chooser.
3. The correct connected MIRA account was selected.
4. The app returned immediately as `Connection: failed [authorization_cancelled]`.
5. A deliberate second attempt repeated the same result.
6. The user did not cancel either attempt.
7. No Google consent screen appeared.
8. No Google Drive Picker appeared.

This proves physical install/launch and native account selection only. It does not prove Google OAuth registration, Picker API configuration, provider binding, canonical readback, or app-side root cause.

### Android hold rule

Until a credible provider-access recovery signal exists:

- do **not** run another phone authorization test;
- do **not** diagnose or patch app-side OAuth/result handling;
- do **not** infer the registered package/SHA-1 or Picker API state;
- do **not** create or alter a Google Cloud project or OAuth client;
- do **not** change Google Picker API state;
- do **not** spend another browser-capable Work attempt merely because time passed.

### Exact Android resume point

1. Hold at provider inspection until a credible recovery signal exists.
2. When the signal exists, perform exactly one bounded authenticated inspection of the existing development provider configuration: read the actual Android package name, signing SHA-1, and Google Picker API enablement state; compare package/SHA-1 with the already-earned proof identity; enable only Google Picker API if inspection proves it disabled and the packet still authorizes that one change.
3. Read back the final provider state exactly.
4. Only after successful provider readback, run one phone test using the already-installed proof APK.
5. If that test still fails, checkpoint the exact result and only then decide whether app-side handling is the next proven dependency.

## Prior Financial Escape checkpoint

`M2-M1-013 — Financial Escape live command-center vertical` remains the prior private-live slice. It includes the mobile/control refinement and three-axis spending-review/telemetry follow-ups. This new packet extends private operational behavior without rewriting the earlier evidence boundary.

## Exact next action / resume point

1. Read exact current reserve/assumption cells and provider-observed cash balances.
2. Build a separate private source-budget projection for materially different newly shared budget/income evidence.
3. Add a bounded checking-earmark/allowance projection with forward monthly accrual semantics.
4. Change the existing protected project reserve only through its established assumption cell and verify downstream formulas.
5. Wire the minimum free-cash calculation needed to exclude checking earmarks, avoiding any second subtraction of already-protected reserves.
6. Read back all affected formulas and outputs, then checkpoint the packet and restore `M2-M1-012` only after this bounded refinement is complete.

## Recovery protocol

Start by reading this file, then verify remote `main`. For private Financial Escape values, use the live connected financial/provider sources and private spreadsheet rather than public Git. Do not reconstruct private values from repository history.