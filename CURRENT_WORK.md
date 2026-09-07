# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active/recovery packet and the exact safe resume point.

## Active packet

### `M2-M1-012` — Android representative-device execution proof

- **Primary work:** `ANDROID-CLIENT-CORE-001`.
- **Primary features:** `CLIENT-ANDROID-001`, `API-001`.
- **Related invariants/features:** `AUTH-001`, `STORE-001`, `RECOVERY-002`, `PROVIDER-002`, `DATA-001`, `DEV-007`, `MIRROR-001`.
- **Repository:** `Matthew-Beare/Mira-2.0`.
- **Recovery branch:** `work/m2-m1-012-provider-tooling-hold-2`.
- **Stable pre-Financial-Escape checkpoint:** `6e715159feed0b044e3ef3ef610916903e2deb09`.
- **Latest bounded Financial Escape privacy-sanitized checkpoint:** `777728702a69d87cb99c16dfadf6a75c8610bc91` (`docs/work-packets/M2-M1-014.md`).
- **Provider-inspection readiness runbook checkpoint:** `6677397ca16307808bbcd456e0e24fb1b0838008` (`docs/work-packets/M2-M1-012-provider-inspection-runbook.md`).
- **Current status:** active and blocked only at provider-configuration inspection.

The Financial Escape interruption packets `M2-M1-013` and `M2-M1-014` are complete at their bounded private-live evidence boundaries. Current public packet files contain generalized product/engineering semantics only; private operational state remains outside those current files. A privacy audit found that earlier public Financial Escape commit history used some overly specific private-life descriptors even though inspected packet history did not contain the private finance amounts, balances, account IDs, provider IDs, document IDs, or spreadsheet IDs. Those current files have been sanitized. Purging historical Git objects would require an explicit destructive history rewrite and has not been performed implicitly.

The latest private-live correction preserves one logical MIRROR finance model, corrected private allocation/planning cardinality, deferred purchase-to-allocation debits, and a reduced user-facing workbook surface with backend/source sheets hidden rather than deleted. These finance corrections do not displace or expand the active Android packet.

## Objective

Complete the already-bounded representative Android device proof against isolated synthetic MIRA 2.0 Google state without turning Android into a second authority, without touching legacy production state, and without expanding into general Android product development.

## Alignment

- `CLIENT-ANDROID-001` remains implemented/test-verified but only partially live-verified.
- `API-001`, `AUTH-001`, `STORE-001`, and `RECOVERY-002` still require Android to operate through the shared canonical boundary with exact readback.
- `MIRROR-001` remains the companion reality database; projections and provider adapters must not become second authorities.
- `PROVIDER-002` still requires provider-native ordinary-user connection semantics and exact resource verification.
- `DATA-001` still forbids legacy production state as a development fixture.
- M2-M1 roadmap step 8 remains representative-device proof.

**Direction result:** `M2-M1-012` remains the sole active implementation packet. The smallest unresolved dependency is exact provider-state inspection/readback.

## Stable proof identity already earned

The expected development proof identity comes from the verified build artifact, not provider readback:

- Android package: `com.mira.deviceproof`.
- Stable development signing certificate SHA-1: `AF:E0:18:6B:7C:21:EA:74:D3:4C:4A:33:04:FF:B1:15:EF:DB:A5:6D`.
- Stable development signing certificate SHA-256: `B5:6A:2B:03:12:B2:AF:85:58:69:A7:19:66:3E:44:10:11:53:59:19:03:E7:94:8F:2E:0F:FC:F5:08:48:51:7B`.
- Retained proof APK SHA-256: `9ecb56f8dca3ea51fd1736fea62417f2b0066274ef08977511c15a7ae3d325c6`.

The actual package/fingerprint registered in the existing Google Android OAuth client remain unknown because provider state has not been successfully inspected.

## Representative-device evidence already earned

On a representative Android device:

1. The exact stable-development-signed proof APK installed and launched.
2. **Connect Google Workspace** opened Google's native account chooser.
3. The correct connected MIRA account was selected.
4. The app immediately returned `Connection: failed [authorization_cancelled]`.
5. A deliberate second attempt repeated the same result.
6. The user did not cancel either attempt.
7. No Google consent screen appeared.
8. No Google Drive Picker appeared.

This earns install/launch and native account-selection evidence only. It does not prove Google Android OAuth registration, Picker API configuration, provider binding, canonical readback, or app-side root cause.

## Current blocker and hold rule

Two bounded browser-capable provider inspections failed before Google provider state could be read. The existing Android OAuth client's actual package/SHA-1 and Google Picker API state remain unknown; no provider mutation was made.

Until there is a credible provider-access recovery signal:

- do **not** run another phone test;
- do **not** diagnose or patch app-side OAuth/result handling;
- do **not** infer OAuth-client or Picker configuration;
- do **not** create or alter a Google Cloud project or OAuth client;
- do **not** change Google Picker API state;
- do **not** repeat prior publication/authorization work;
- do **not** spend another Work-mode attempt merely because time has passed.

A credible recovery signal means the authenticated browser-capable lane can reach Google Cloud/Google Accounts again, or a supported authenticated Google Cloud administration tool becomes available that can inspect the existing Android OAuth client and Picker API state.

## Acceptance state

- Repository/build/signing provenance: **satisfied**.
- Representative-device install and launch: **satisfied**.
- Native Google account chooser and correct-account selection: **satisfied**.
- Successful provider-native Google authorization/consent: **pending**.
- Existing Android OAuth client exact provider readback: **pending**.
- Google Picker API exact enabled/disabled readback: **pending**.
- Isolated synthetic Workspace binding/readiness: **pending live verification**.
- Bounded canonical read with revision/hash: **pending live verification**.
- Queued canonical mutation with acknowledged readback: **pending live verification**.
- Stock-ChatGPT/native Workspace cross-readback: **pending live verification**.

## Protected constraints

- Legacy MIRA production Sheets, Drive artifacts, Apps Script projects, briefs, schedules, automations, and live state remain protected production data.
- The existing isolated synthetic M2-M1-001 fixture remains the only permitted provider target for this proof unless fresh readback proves it unsuitable.
- Never commit credentials, OAuth tokens, private provider identifiers, keystore material, live spreadsheet contents, email contents, personal financial details, or personal operational state.
- The development proof signing identity is not production release signing.
- Provider configuration must be inspected before app-side OAuth handling is diagnosed or repaired.

## Exact next action / resume point

1. Hold `M2-M1-012` at the provider-inspection gate. Nothing is required from the user now.
2. Wait for a credible provider-access recovery signal; do not burn another Work attempt speculatively.
3. When that signal exists, follow `docs/work-packets/M2-M1-012-provider-inspection-runbook.md` for exactly one bounded authenticated inspection against the existing development project:
   - read the existing Android OAuth client's registered package name;
   - read its signing SHA-1;
   - compare both to the expected proof identity above;
   - if either mismatches, checkpoint and stop with zero provider mutations;
   - if both match, read whether Google Picker API is enabled;
   - enable **only Google Picker API**, and only if inspection proves it disabled and the packet still authorizes that one mutation;
   - make no other provider change.
4. Read back final provider state exactly.
5. Only after successful provider readback, run one phone test with the already-installed exact proof APK.
6. If that test still fails, checkpoint the exact live result before evaluating app-side handling.
7. Reconcile FEATURES/BACKLOG/ROADMAP before packet closeout.

## Recovery protocol

Start by reading this file and verifying remote `main` plus `work/m2-m1-012-provider-tooling-hold-2`. Read the provider-inspection runbook before any recovered provider session. Financial Escape packets remain closed at their bounded private-live evidence boundaries; do not reopen them merely to continue Android.
