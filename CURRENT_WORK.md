# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active/recovery packet and the exact safe resume point. Detailed prior evidence remains preserved in Git history and packet checkpoints.

## Active packet

### `M2-M1-012` — Android representative-device execution proof

- **Primary work:** `ANDROID-CLIENT-CORE-001`.
- **Primary features:** `CLIENT-ANDROID-001`, `API-001`.
- **Related invariants/features:** `AUTH-001`, `STORE-001`, `RECOVERY-002`, `PROVIDER-002`, `DATA-001`, `DEV-007`, `MIRROR-001`.
- **Repository:** `Matthew-Beare/Mira-2.0`.
- **Recovery branch:** `work/m2-m1-012-provider-tooling-hold-2`.
- **Current main before this governance branch:** `2f54c2c93a4d6d435ac89772b1da5c1323f4f759`.
- **Stable pre-Financial-Escape checkpoint:** `6e715159feed0b044e3ef3ef610916903e2deb09`.
- **Current status:** active and blocked only at provider-configuration inspection. Repository/build/signing evidence, physical install/launch, Google native account chooser opening, and correct-account selection are earned. Successful Google authorization, consent, Picker display, provider registration readback, canonical binding/readback, and mutation success are not earned.

The Financial Escape interruption packets `M2-M1-013` and `M2-M1-014` are complete at their bounded private-live evidence boundaries. Their private operational state remains outside public Git. Product-level finance generalization remains separate unfinished work and must reuse canonical MIRROR authority rather than create a second database.

## Objective

Complete the already-bounded representative Android device proof against isolated synthetic MIRA 2.0 Google state without turning Android into a second authority, without touching legacy production state, and without expanding into general Android product development.

## Session-start alignment verification — 2026-09-07 post-Financial-Escape restoration

### `FEATURES.md`

- `CLIENT-ANDROID-001` remains `specified+implemented+test_verified+partial`; live Google authorization/provider behavior and the remaining canonical device proof are unfinished.
- `API-001`, `AUTH-001`, `STORE-001`, and `RECOVERY-002` still require Android to operate through the shared canonical boundary with exact readback.
- `MIRROR-001` remains the companion reality database; product projections and provider adapters must not become a second authority.
- `PROVIDER-002` still requires provider-native ordinary-user connection semantics and exact resource verification.
- `DATA-001` still forbids legacy MIRA production state as a development fixture.
- `DEV-007` requires this feature/backlog/roadmap reconciliation before further implementation or closeout.

### `BACKLOG.md`

- `ANDROID-CLIENT-CORE-001` remains the unfinished prerequisite carrying live Google authorization/provider-device and representative-device proof gaps.
- `ANDROID-SYNC` remains complete at deterministic integration evidence and must not be reopened merely because live provider/device proof is incomplete.
- Financial Escape private-live refinement is complete at its bounded evidence boundary; generalized canonical finance ingestion remains future work and does not displace this held Android packet unless explicitly reprioritized again.
- No newly discovered work outranks the current provider-inspection gate.

### `ROADMAP.md`

- M2-M1 step 8 remains representative-device proof.
- Android remains a companion over the same canonical Personal MIRA reality; it does not become a second authority.
- The completed Financial Escape interruption does not change the Android provider-inspection resume point.

### Direction result

**ALIGNED.** `M2-M1-012` is restored as the sole active packet. The smallest unresolved dependency is still exact provider-state inspection/readback. No app-side diagnosis, phone retest, provider inference, or adjacent implementation work is justified while that dependency remains unknown.

## Stable proof identity and repository evidence already earned

The expected development proof identity is known from the verified build artifact, not from provider readback:

- Android package expected by the proof app: `com.mira.deviceproof`.
- Stable development signing certificate SHA-1 expected by the proof artifact: `AF:E0:18:6B:7C:21:EA:74:D3:4C:4A:33:04:FF:B1:15:EF:DB:A5:6D`.
- Stable development signing certificate SHA-256: `B5:6A:2B:03:12:B2:AF:85:58:69:A7:19:66:3E:44:10:11:53:59:19:03:E7:94:8F:2E:0F:FC:F5:08:48:51:7B`.
- Exact retained proof APK SHA-256: `9ecb56f8dca3ea51fd1736fea62417f2b0066274ef08977511c15a7ae3d325c6`.
- PR #117 and the post-merge stable artifact completed repository/build/signing prerequisites before live device execution.

These values are the **expected app/artifact values only**. The actual package/fingerprint currently registered in the existing Google Android OAuth client remain unknown because provider state has not been successfully inspected.

## Representative-device evidence already earned

On one representative Android device:

1. The exact stable-development-signed proof APK installed and launched.
2. Tapping **Connect Google Workspace** opened Google's native account chooser.
3. The correct connected MIRA account was selected.
4. The app returned immediately as `Connection: failed [authorization_cancelled]`.
5. A deliberate second attempt repeated the same result.
6. The user did not cancel either attempt.
7. No Google consent screen appeared.
8. No Google Drive Picker appeared.

This earns physical install/launch and native account-selection evidence only. It does not prove the Google Android OAuth registration, Picker API configuration, provider binding, canonical readback, or app-side root cause.

## Provider inspection evidence — two tooling failures, zero provider-state evidence

Two bounded Work-mode provider inspections failed before Google provider state could be inspected. Google Cloud was unavailable and the second attempt timed out after one reload. The existing Android OAuth client was not inspected, its actual package/SHA-1 remain unknown, Google Picker API state remains unknown, and no provider mutation was made.

These failures are browser/network tooling evidence only. They are not evidence that any Google Cloud configuration is correct or incorrect.

## Current blocker and hold rule

**Blocker:** the packet needs exact readback of existing Google provider configuration, but the browser-capable provider lane failed twice before inspection.

**User action required now: none.**

Until there is a credible provider-access recovery signal:

- do **not** run another phone test;
- do **not** diagnose or patch app-side OAuth/result handling;
- do **not** infer OAuth-client or Picker configuration;
- do **not** create or alter a Google Cloud project or OAuth client;
- do **not** change Google Picker API state;
- do **not** repeat M2-M1-001 publication/authorization work;
- do **not** spend another Work-mode attempt merely because time has passed.

A credible recovery signal means either the browser-capable Work lane is demonstrably able to reach authenticated Google Cloud/Google Accounts again or a supported authenticated Google Cloud administration tool becomes available that can inspect the existing Android OAuth client and Picker API state.

## Acceptance criteria state

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
- Never commit credentials, OAuth tokens, private provider identifiers, keystore material, live spreadsheet contents, email contents, or personal operational state.
- The development proof signing identity is not production release signing.
- Provider configuration must be inspected before app-side OAuth handling is diagnosed or repaired.

## Exact next action / resume point

1. **Hold `M2-M1-012` at the provider-inspection gate. Nothing is required from the user now.**
2. Wait for a credible provider-access recovery signal; do not burn another Work attempt speculatively.
3. When that signal exists, perform exactly one bounded authenticated provider inspection against the existing development project:
   - read the existing Android OAuth client's actual registered package name;
   - read its actual signing SHA-1;
   - compare those actual values to the expected proof identity above;
   - read whether Google Picker API is enabled;
   - enable **only Google Picker API**, and only if inspection proves it disabled and the packet still authorizes that one mutation;
   - make no other provider change.
4. Read back the final provider state exactly.
5. **Only after successful provider readback**, run one phone test using the already-installed exact proof APK.
6. If that phone test still fails, checkpoint the exact live result and only then evaluate whether app-side result handling has become the next proven dependency.
7. Before packet closeout, repeat FEATURES/BACKLOG/ROADMAP reconciliation and preserve every remaining unearned evidence gap.

## Recovery protocol

Start by reading this file and verifying remote `main` plus `work/m2-m1-012-provider-tooling-hold-2`. Financial Escape packets `M2-M1-013` and `M2-M1-014` are complete at their bounded private-live evidence boundaries; do not reopen them merely to continue Android. `M2-M1-012` is again the sole active work packet and remains on deliberate provider-tooling hold.
