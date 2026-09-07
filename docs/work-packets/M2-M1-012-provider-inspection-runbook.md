# M2-M1-012 — bounded Google provider inspection runbook

Status: readiness documentation only. This file does not claim provider access, provider correctness, successful authorization, Picker display, or representative-device completion.

`CURRENT_WORK.md` remains authoritative for the active packet and exact resume point.

## Purpose

Use one recovered authenticated Google Cloud administration session to resolve the smallest remaining unknown in `M2-M1-012`: the actual existing Android OAuth registration and Google Picker API enablement state for the already-established development project.

This runbook is intentionally narrow. It is not permission to redesign OAuth, create replacement credentials, alter the Cloud project, create API keys, change consent configuration, patch the Android app, or retest the phone before provider readback is complete.

## Expected proof identity

These values come from the already-verified retained development proof artifact and are comparison targets only:

- expected package name: `com.mira.deviceproof`
- expected signing SHA-1: `AF:E0:18:6B:7C:21:EA:74:D3:4C:4A:33:04:FF:B1:15:EF:DB:A5:6D`
- retained proof APK SHA-256: `9ecb56f8dca3ea51fd1736fea62417f2b0066274ef08977511c15a7ae3d325c6`

Do not infer that Google currently contains those values. The provider values remain unearned evidence until read directly.

## Preconditions

Proceed only when a supported authenticated administration lane can actually reach the existing Google Cloud project. A browser merely loading a generic Google page is not enough.

Before touching provider state:

1. confirm the selected project is the existing MIRA 2.0 development project;
2. do not create a project, OAuth client, API key, consent-screen configuration, or replacement credential;
3. do not use legacy MIRA production resources as a substitute;
4. keep provider/project/client identifiers and any private execution details out of public Git;
5. if the existing development project cannot be identified with confidence, stop with zero mutations.

## Inspection sequence

### A. Read the existing Android OAuth client

1. Open Google Cloud Console → **APIs & Services** → **Credentials**.
2. Locate the existing OAuth 2.0 client whose application type is **Android**. Do not create one.
3. Open that client and read the registered:
   - package name;
   - signing-certificate fingerprint / SHA-1.
4. Compare them exactly with the expected proof identity above.
5. Record the actual provider values in private execution evidence, not public Git.

Google's Android OAuth documentation treats package name and signing-certificate SHA-1 as the identifying registration fields for an Android client.

### B. Stop on OAuth-registration mismatch

If either registered value does not exactly match the expected proof identity:

- record **provider OAuth registration mismatch** as the newly proven dependency;
- make no provider mutation in this run;
- do not create or repair an OAuth client under this packet;
- do not enable unrelated APIs;
- do not run another phone test;
- checkpoint the mismatch before any follow-on repair packet is considered.

This preserves causal evidence instead of changing multiple variables at once.

### C. Read Google Picker API state

Only if the Android OAuth registration matches exactly:

1. Open **APIs & Services** → **Enabled APIs & services** or the API Library for the same project.
2. Search for **Google Picker API**.
3. Read whether it is enabled.
4. Record the exact enabled/disabled result in private execution evidence.

Google's current Picker documentation explicitly requires enabling the Google Picker API in the Cloud project.

### D. Single permitted provider mutation

If and only if all of the following are true:

- the existing Android OAuth package name matches exactly;
- the existing Android OAuth SHA-1 matches exactly;
- Google Picker API is proven disabled;
- `CURRENT_WORK.md` still authorizes the mutation;

then enable **only Google Picker API**.

After enabling it:

1. re-open/read the API state;
2. confirm it is now enabled;
3. make no other provider change.

Do not create an API key merely because Picker web documentation discusses API keys. This packet authorizes only the already-recorded Picker API enablement mutation, not additional credential creation.

## Required provider evidence record

The private execution checkpoint should capture, at minimum:

- authenticated administration lane used;
- existing development project positively identified: yes/no;
- Android OAuth client found: yes/no;
- registered package compared to expected: match/mismatch;
- registered SHA-1 compared to expected: match/mismatch;
- Google Picker API state before any allowed mutation: enabled/disabled/unknown;
- mutation performed: none / enabled Google Picker API only;
- final Google Picker API state: enabled/disabled/unknown;
- any provider error text encountered;
- explicit statement that no other provider state was changed.

Public Git should contain only sanitized evidence classification and checkpoint status, not private provider identifiers or credentials.

## Phone-test gate

Run exactly one representative-device test only after successful provider readback shows:

- exact Android OAuth package match;
- exact Android OAuth SHA-1 match;
- Google Picker API enabled.

Use the already-installed exact retained proof APK. Do not rebuild merely to retest provider configuration.

For that one phone test, record the observable sequence exactly:

1. app launch;
2. Connect Google Workspace action;
3. native account chooser result;
4. consent screen shown or not shown;
5. Picker shown or not shown;
6. final app connection state / exact error.

If the provider state is verified and the same post-account-selection failure still occurs, only then may app-side result handling become a proven next diagnostic dependency.

## Hard stop conditions

Stop without further mutation if any of these occurs:

- wrong or uncertain Cloud project;
- no existing Android OAuth client can be positively identified;
- package mismatch;
- SHA-1 mismatch;
- provider page/tool cannot read the needed fields;
- requested permission would require broader project/IAM/credential changes;
- any proposed action exceeds enabling Google Picker API after the exact-match preconditions above.

## Official reference basis

- Google Cloud / Google for Developers documentation for Android OAuth client IDs requires the Android package name and signing-certificate SHA-1 when registering an Android client.
- Google Drive Picker documentation requires the Google Picker API to be enabled in the selected Cloud project.
- Google Cloud API documentation describes enabling an API from the API Library after selecting the intended project.

References checked for this runbook on 2026-09-07:

- https://developers.google.com/identity/sign-in/android/legacy-gsi-start
- https://cloud.google.com/endpoints/docs/frameworks/java/creating-client-ids
- https://developers.google.com/workspace/drive/picker/guides/web-picker
- https://cloud.google.com/apis/docs/getting-started

## Resume rule

Until the preconditions are met, `M2-M1-012` remains deliberately held at provider inspection. This runbook improves execution readiness; it does not itself constitute provider evidence or permission to bypass the hold.