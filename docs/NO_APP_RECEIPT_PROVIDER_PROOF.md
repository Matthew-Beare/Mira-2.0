# M2-M0-012 isolated Google receipt provider proof

Date: 2026-08-29/30

This document records bounded provider evidence for the Personal no-app receipt vertical. It contains only synthetic state. The Google provider file identifier and authenticated account details are intentionally not committed to public Git.

## Isolation and preflight

A brand-new native Google Sheet was created specifically for this proof. It was not copied from, linked to, or populated from any legacy MIRA production receipt/order/inventory artifact.

The Sheet was constructed from the Git-backed `distribution/personal_google_starter.json` contract and read back before mutable state was inserted.

Verified pre-mutation state:

- spreadsheet timezone: `Etc/UTC`;
- tabs exactly: `Metadata`, `Resources`, `Events`, `Idempotency`;
- Metadata schema: `mira-structured-state-v1`;
- adapter contract: `STORE-001`;
- writer model: `single_writer`;
- resource types include `authority`, `authority_binding`, `entity`, `onboarding_ledger`, `ops_brief_run`, `receipt`, `service_state`, `task`;
- exact STORE-001 headers were present;
- `Resources`, `Events`, and `Idempotency` contained headers only before proof state was written.

## Synthetic authority and binding

The proof created one synthetic Personal Google authority:

- `authority/google-sheets-personal`, revision 1;
- adapter `google-sheets`;
- schema `mira-structured-state-v1`;
- enabled and verified;
- synthetic owner identity only.

It also created exactly one receipt routing binding:

- `authority_binding/binding-receipt`, revision 1;
- `data_class=receipt`;
- `authority_id=google-sheets-personal`.

Both Resources and their matching Idempotency rows were read back with the planned revisions, request hashes, payloads, results, and resource references.

## Synthetic receipt capture

A fully synthetic purchase was persisted as one canonical `receipt` Resource. The source material represented a made-up tool-store purchase and does not correspond to a real user transaction.

Revision 1 proved:

- stable canonical receipt identity;
- merchant and normalized merchant key;
- synthetic order number;
- purchase date and `USD` currency;
- exact integer-minor-unit total/subtotal/tax values;
- one deterministic line ID with quantity stored as a decimal string;
- state `captured`;
- one synthetic `email` evidence observation identified by a SHA-256 fingerprint;
- matching `proof-receipt-email` idempotency evidence;
- exact request hash and result readback.

## Multi-source merge proof

The same canonical receipt was then updated to revision 2 with a second synthetic `image` evidence observation.

Readback verified:

- the receipt Resource ID did not change;
- revision advanced exactly from 1 to 2;
- the original email evidence remained present;
- the new image evidence was added rather than producing a second purchase Resource;
- both evidence observations retained distinct SHA-256 fingerprints and source references;
- purchase facts and deterministic line identity remained unchanged;
- the Resource row contains the revision-2 request hash and `proof-receipt-image` idempotency key;
- Idempotency retains both the revision-1 email result and revision-2 image result with their exact request hashes and resource references.

The proof spreadsheet was renamed to include `NOT A STARTER` after verification so it is not confused with a distributable clean Personal starter.

## Evidence boundary

This provider proof establishes that the M2-M0-012 receipt/Authority material can persist and read back exactly in an isolated Google Sheets STORE-001 substrate.

It does **not** claim any of the following are live or verified by this proof:

- Gmail receipt discovery or extraction;
- OCR or photo/PDF extraction quality;
- automatic Drive receipt archival;
- order/shipment lifecycle reconciliation;
- asset creation or fitment;
- inventory/location mutation;
- spending, payment, reimbursement, or grocery reconciliation;
- scheduled background receipt processing.

Those remain separate feature/work boundaries and may only claim completion after their own implementation and provider/readback evidence.
