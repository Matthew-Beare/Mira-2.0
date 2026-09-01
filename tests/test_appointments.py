from __future__ import annotations

import hashlib
import unittest

from mira.appointments import (
    APPOINTMENT_RESOURCE_TYPE,
    PROVIDER_RESOURCE_TYPE,
    AppointmentCandidate,
    AppointmentIdentityConflictError,
    AppointmentIdentityIntegrityError,
    AppointmentIdentityService,
    AppointmentIdentityValidationError,
    EvidenceRef,
    ProviderCandidate,
)
from mira.structured_state import InMemoryStructuredStateAdapter, ResourceRecord


def digest(label: str) -> str:
    return hashlib.sha256(label.encode("utf-8")).hexdigest()


def evidence(
    label: str,
    *,
    source_id: str | None = None,
    authority: str = "source",
    observed_at: str = "2026-08-31T08:00:00-04:00",
) -> EvidenceRef:
    return EvidenceRef(
        source_type="synthetic",
        source_id=source_id or label,
        material_sha256=digest(label),
        observed_at=observed_at,
        authority=authority,
    )


class AppointmentIdentityServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.adapter = InMemoryStructuredStateAdapter(
            schema_version="mira-test-v1",
            resource_types=[PROVIDER_RESOURCE_TYPE, APPOINTMENT_RESOURCE_TYPE],
            event_types=["created", "updated"],
        )
        self.service = AppointmentIdentityService(self.adapter)

    def provider(self, label: str = "p1", **overrides):
        values = {
            "evidence": evidence(label),
            "display_name": "Dr Ada Lovelace",
            "organization": "Synthetic Heart Center",
            "email": "ada@example.test",
            "specialty_type": "Cardiology",
        }
        values.update(overrides)
        return self.service.reconcile_provider(
            ProviderCandidate(**values), idempotency_key=f"provider-{label}"
        )

    def appointment(self, provider_id: str, label: str = "a1", **overrides):
        values = {
            "evidence": evidence(label, observed_at="2026-08-31T08:05:00-04:00"),
            "provider_id": provider_id,
            "start_at": "2026-09-04T10:00:00-04:00",
            "end_at": "2026-09-04T11:00:00-04:00",
            "timezone": "America/New_York",
            "title": "Follow-up appointment",
            "location": "100 Synthetic Way",
            "appointment_type": "Cardiology appointment",
        }
        values.update(overrides)
        return self.service.reconcile_appointment(
            AppointmentCandidate(**values), idempotency_key=f"appointment-{label}"
        )

    def test_provider_create_exact_replay_and_source_enrichment(self) -> None:
        created = self.provider()
        replay = self.provider()
        self.assertEqual(created.status, "created")
        self.assertEqual(created.provider.revision, 1)
        self.assertEqual(replay.status, "replay")
        self.assertEqual(replay.provider.revision, 1)

        enriched = self.provider(
            "p2",
            evidence=evidence("p2", observed_at="2026-08-31T09:00:00-04:00"),
            phone="423-555-0100",
        )
        self.assertEqual(enriched.status, "updated")
        self.assertEqual(enriched.provider.revision, 2)
        self.assertIn("phone:4235550100", enriched.provider.identity_keys)
        self.assertEqual(len(enriched.provider.evidence), 2)

    def test_provider_requires_exact_identity_and_never_fuzzy_merges(self) -> None:
        weak = self.provider(
            "weak",
            display_name="Dr Only Name",
            organization=None,
            email=None,
            phone=None,
        )
        self.assertEqual(weak.status, "needs_review")
        self.assertIsNone(weak.provider)

        one = self.provider(
            "st-mary",
            display_name="Jane Smith",
            organization="St Mary Clinic",
            email=None,
        )
        two = self.provider(
            "saint-mary",
            display_name="Jane Smith",
            organization="Saint Mary Clinic",
            email=None,
        )
        self.assertEqual(one.status, "created")
        self.assertEqual(two.status, "created")
        self.assertNotEqual(one.provider.provider_id, two.provider.provider_id)

    def test_exact_evidence_matching_multiple_providers_needs_review(self) -> None:
        first = self.provider(
            "first",
            email="first@example.test",
            phone="423-555-0101",
            identity_namespace="npi",
            identity_value="111",
        ).provider
        second = self.provider(
            "second",
            display_name="Dr Grace Hopper",
            organization="Synthetic Neuro Center",
            email="second@example.test",
            phone="423-555-0102",
            identity_namespace="npi",
            identity_value="222",
        ).provider
        ambiguous = self.provider(
            "ambiguous",
            display_name=None,
            organization=None,
            email="first@example.test",
            phone="423-555-0102",
        )
        self.assertEqual(ambiguous.status, "needs_review")
        self.assertEqual(
            set(ambiguous.candidate_provider_ids),
            {first.provider_id, second.provider_id},
        )

    def test_user_confirmed_provider_correction_outranks_source_and_preserves_evidence(self) -> None:
        original = self.provider().provider
        corrected = self.service.reconcile_provider(
            ProviderCandidate(
                evidence=evidence(
                    "owner-correction",
                    authority="user_confirmed",
                    observed_at="2026-08-31T10:00:00-04:00",
                ),
                canonical_provider_id=original.provider_id,
                specialty_type="Cardiologist",
            ),
            idempotency_key="provider-owner-correction",
        )
        self.assertEqual(corrected.status, "updated")
        self.assertEqual(corrected.provider.specialty_type, "Cardiologist")
        self.assertEqual(
            corrected.provider.field_authority["specialty_type"], "user_confirmed"
        )
        self.assertEqual(len(corrected.provider.evidence), 2)
        self.assertEqual(corrected.provider.evidence[0].material_sha256, digest("p1"))

        lower = self.service.reconcile_provider(
            ProviderCandidate(
                evidence=evidence(
                    "lower-source",
                    observed_at="2026-08-31T11:00:00-04:00",
                ),
                email="ada@example.test",
                specialty_type="Cardiology",
            ),
            idempotency_key="provider-lower-source",
        )
        self.assertEqual(lower.status, "updated")
        self.assertEqual(lower.provider.specialty_type, "Cardiologist")
        self.assertEqual(len(lower.provider.evidence), 3)

    def test_conflicting_user_confirmed_provider_value_fails_closed(self) -> None:
        original = self.provider().provider
        self.service.reconcile_provider(
            ProviderCandidate(
                evidence=evidence("confirm-one", authority="user_confirmed"),
                canonical_provider_id=original.provider_id,
                specialty_type="Cardiologist",
            ),
            idempotency_key="confirm-one",
        )
        with self.assertRaises(AppointmentIdentityConflictError):
            self.service.reconcile_provider(
                ProviderCandidate(
                    evidence=evidence("confirm-two", authority="user_confirmed"),
                    canonical_provider_id=original.provider_id,
                    specialty_type="Neurologist",
                ),
                idempotency_key="confirm-two",
            )

    def test_one_evidence_source_identity_with_different_material_needs_review(self) -> None:
        created = self.provider().provider
        result = self.service.reconcile_provider(
            ProviderCandidate(
                evidence=evidence(
                    "different-material",
                    source_id="p1",
                    observed_at="2026-08-31T12:00:00-04:00",
                ),
                email="ada@example.test",
            ),
            idempotency_key="provider-source-mutation",
        )
        self.assertEqual(result.status, "needs_review")
        self.assertEqual(result.provider.provider_id, created.provider_id)
        self.assertEqual(result.provider.revision, 1)

    def test_same_provider_can_have_multiple_distinct_appointments(self) -> None:
        provider_id = self.provider().provider.provider_id
        first = self.appointment(provider_id, "a1")
        second = self.appointment(
            provider_id,
            "a2",
            start_at="2026-10-02T10:00:00-04:00",
            end_at="2026-10-02T11:00:00-04:00",
        )
        self.assertEqual(first.status, "created")
        self.assertEqual(second.status, "created")
        self.assertNotEqual(first.appointment.appointment_id, second.appointment.appointment_id)
        self.assertEqual(len(self.service.appointments()), 2)

    def test_duplicate_appointment_reconciles_by_provider_and_exact_start(self) -> None:
        provider_id = self.provider().provider.provider_id
        first = self.appointment(provider_id, "a1")
        replay = self.appointment(provider_id, "a1")
        self.assertEqual(replay.status, "replay")
        self.assertEqual(
            replay.appointment.appointment_id, first.appointment.appointment_id
        )
        enriched = self.appointment(
            provider_id,
            "a2",
            evidence=evidence("a2", observed_at="2026-08-31T09:00:00-04:00"),
            location="200 Verified Avenue",
        )
        self.assertEqual(enriched.status, "needs_review")
        self.assertEqual(enriched.appointment.location, "100 Synthetic Way")

    def test_user_confirmed_appointment_correction_adds_new_identity_alias(self) -> None:
        provider_id = self.provider().provider.provider_id
        original = self.appointment(provider_id).appointment
        corrected = self.service.reconcile_appointment(
            AppointmentCandidate(
                evidence=evidence(
                    "appointment-correction",
                    authority="user_confirmed",
                    observed_at="2026-08-31T10:00:00-04:00",
                ),
                canonical_appointment_id=original.appointment_id,
                provider_id=provider_id,
                start_at="2026-09-04T11:00:00-04:00",
                end_at="2026-09-04T12:00:00-04:00",
                timezone="America/New_York",
                location="200 Verified Avenue",
            ),
            idempotency_key="appointment-owner-correction",
        )
        self.assertEqual(corrected.status, "updated")
        self.assertEqual(corrected.appointment.start_at, "2026-09-04T11:00:00-04:00")
        self.assertEqual(corrected.appointment.end_at, "2026-09-04T12:00:00-04:00")
        self.assertEqual(corrected.appointment.timezone, "America/New_York")
        self.assertEqual(corrected.appointment.location, "200 Verified Avenue")
        self.assertEqual(corrected.appointment.field_authority["start_at"], "user_confirmed")
        self.assertEqual(len(corrected.appointment.identity_keys), 2)
        self.assertEqual(len(corrected.appointment.evidence), 2)

    def test_user_confirmed_same_start_correction_does_not_collide_with_itself(self) -> None:
        provider_id = self.provider().provider.provider_id
        original = self.appointment(provider_id).appointment
        corrected = self.service.reconcile_appointment(
            AppointmentCandidate(
                evidence=evidence(
                    "same-start-correction",
                    authority="user_confirmed",
                    observed_at="2026-08-31T10:30:00-04:00",
                ),
                canonical_appointment_id=original.appointment_id,
                provider_id=provider_id,
                start_at=original.start_at,
                end_at=original.end_at,
                timezone=original.timezone,
                title="Owner confirmed follow-up",
            ),
            idempotency_key="same-start-correction",
        )
        self.assertEqual(corrected.status, "updated")
        self.assertEqual(corrected.appointment.appointment_id, original.appointment_id)
        self.assertEqual(corrected.appointment.start_at, original.start_at)
        self.assertEqual(corrected.appointment.title, "Owner confirmed follow-up")
        self.assertEqual(corrected.appointment.revision, 2)

    def test_appointment_requires_known_provider_and_strong_occurrence_identity(self) -> None:
        with self.assertRaises(AppointmentIdentityValidationError):
            self.appointment("provider-does-not-exist")
        provider_id = self.provider().provider.provider_id
        weak = self.appointment(
            provider_id,
            "weak-a",
            start_at=None,
            end_at=None,
            timezone=None,
        )
        self.assertEqual(weak.status, "needs_review")
        explicit = self.appointment(
            provider_id,
            "external-a",
            start_at=None,
            end_at=None,
            timezone=None,
            identity_namespace="ehr",
            identity_value="visit-123",
        )
        self.assertEqual(explicit.status, "created")

    def test_projection_timing_is_durable_and_validated(self) -> None:
        provider_id = self.provider().provider.provider_id
        created = self.appointment(provider_id).appointment
        self.assertEqual(created.end_at, "2026-09-04T11:00:00-04:00")
        self.assertEqual(created.timezone, "America/New_York")

        with self.assertRaisesRegex(AppointmentIdentityValidationError, "later than"):
            self.appointment(
                provider_id,
                "bad-end",
                end_at="2026-09-04T09:00:00-04:00",
            )
        with self.assertRaisesRegex(AppointmentIdentityValidationError, "offset"):
            self.appointment(
                provider_id,
                "bad-zone",
                timezone="America/Phoenix",
            )

    def test_legacy_appointment_without_extended_timing_remains_readable(self) -> None:
        provider_id = self.provider().provider.provider_id
        created = self.appointment(provider_id).appointment
        key = (APPOINTMENT_RESOURCE_TYPE, created.appointment_id)
        record = self.adapter._records[key]
        payload = dict(record.payload)
        payload.pop("end_at")
        payload.pop("timezone")
        authority = dict(payload["field_authority"])
        authority.pop("end_at")
        authority.pop("timezone")
        payload["field_authority"] = authority
        self.adapter._records[key] = ResourceRecord(
            resource_type=record.resource_type,
            resource_id=record.resource_id,
            payload=payload,
            revision=record.revision,
        )

        legacy = self.service.get_appointment(created.appointment_id)
        self.assertEqual(legacy.start_at, created.start_at)
        self.assertIsNone(legacy.end_at)
        self.assertIsNone(legacy.timezone)

    def test_no_calendar_reminder_or_event_side_effects(self) -> None:
        provider = self.provider().provider
        self.appointment(provider.provider_id)
        self.assertEqual(len(self.adapter.query(PROVIDER_RESOURCE_TYPE)), 1)
        self.assertEqual(len(self.adapter.query(APPOINTMENT_RESOURCE_TYPE)), 1)
        self.assertEqual(
            self.adapter.events_for(PROVIDER_RESOURCE_TYPE, provider.provider_id), ()
        )
        self.assertEqual(
            self.adapter.events_for(
                APPOINTMENT_RESOURCE_TYPE,
                self.service.appointments()[0].appointment_id,
            ),
            (),
        )

    def test_corrupt_persisted_identity_fails_integrity(self) -> None:
        provider = self.provider().provider
        record = self.adapter._records[(PROVIDER_RESOURCE_TYPE, provider.provider_id)]
        self.adapter._records[(PROVIDER_RESOURCE_TYPE, provider.provider_id)] = ResourceRecord(
            resource_type=PROVIDER_RESOURCE_TYPE,
            resource_id=provider.provider_id,
            payload={**record.payload, "provider_id": "provider-other"},
            revision=record.revision,
        )
        with self.assertRaises(AppointmentIdentityIntegrityError):
            self.service.get_provider(provider.provider_id)


if __name__ == "__main__":
    unittest.main()
