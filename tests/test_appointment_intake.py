from __future__ import annotations

import hashlib
import unittest

from mira.appointment_intake import (
    AppointmentExtraction,
    AppointmentIntakeService,
    AppointmentIntakeValidationError,
    CalendarProjectionTarget,
)
from mira.appointments import (
    APPOINTMENT_RESOURCE_TYPE,
    PROVIDER_RESOURCE_TYPE,
    AppointmentCandidate,
    AppointmentIdentityService,
    EvidenceRef,
    ProviderCandidate,
)
from mira.calendar_projection import (
    CALENDAR_PROJECTION_RESOURCE_TYPE,
    CalendarProjectionService,
    InMemoryCalendarProjectionAdapter,
)
from mira.service_state import RESOURCE_TYPE as SERVICE_RESOURCE_TYPE, ServiceStateService
from mira.structured_state import InMemoryStructuredStateAdapter


def digest(label: str) -> str:
    return hashlib.sha256(label.encode("utf-8")).hexdigest()


def evidence(
    label: str,
    *,
    source_type: str = "email",
    source_id: str | None = None,
    authority: str = "source",
    observed_at: str = "2026-08-31T12:00:00-04:00",
) -> EvidenceRef:
    return EvidenceRef(
        source_type=source_type,
        source_id=source_id or label,
        material_sha256=digest(label),
        observed_at=observed_at,
        authority=authority,
    )


def extraction(**overrides) -> AppointmentExtraction:
    values = {
        "provider_display_name": "Dr Ada Lovelace",
        "provider_organization": "Synthetic Heart Center",
        "provider_email": "ada@example.test",
        "provider_specialty_type": "Cardiology",
        "appointment_start_at": "2026-09-04T10:00:00-04:00",
        "appointment_end_at": "2026-09-04T11:00:00-04:00",
        "appointment_timezone": "America/New_York",
        "appointment_title": "Cardiology follow-up",
        "appointment_location": "100 Synthetic Way",
        "appointment_type": "Cardiology appointment",
    }
    values.update(overrides)
    if "confidence" not in values:
        values["confidence"] = {
            field: 0.99
            for field, value in values.items()
            if field != "confidence" and value is not None
        }
    return AppointmentExtraction(**values)


class AppointmentIntakeTests(unittest.TestCase):
    def setUp(self) -> None:
        self._reset()

    def _reset(self, *, writable_calendar: bool = True) -> None:
        self.state = InMemoryStructuredStateAdapter(
            schema_version="mira-test-v1",
            resource_types=[
                PROVIDER_RESOURCE_TYPE,
                APPOINTMENT_RESOURCE_TYPE,
                CALENDAR_PROJECTION_RESOURCE_TYPE,
                SERVICE_RESOURCE_TYPE,
            ],
            event_types=["created", "updated"],
        )
        self.identity = AppointmentIdentityService(self.state)
        self.calendar_adapter = InMemoryCalendarProjectionAdapter(
            "google", writable=writable_calendar
        )
        self.calendar = CalendarProjectionService(self.state, self.calendar_adapter)
        self.intake = AppointmentIntakeService(
            self.identity, calendar_projection=self.calendar
        )
        self.services = ServiceStateService(self.state)

    def activate_appointment_service(self):
        self.services.ensure("appointments_calendar")
        self.services.request_enable(
            "appointments_calendar", idempotency_key="request-calendar"
        )
        self.services.set_readiness(
            "appointments_calendar",
            capability_state="available",
            dependency_blockers=(),
            idempotency_key="ready-calendar",
        )
        return self.services.activate(
            "appointments_calendar", idempotency_key="activate-calendar"
        )

    def target(self) -> CalendarProjectionTarget:
        return CalendarProjectionTarget(
            provider_lane="google", calendar_ref="synthetic-calendar"
        )

    def test_email_image_and_text_sources_are_first_class(self) -> None:
        for source_type in ("email", "image", "text"):
            with self.subTest(source_type=source_type):
                self._reset()
                result = self.intake.intake(
                    evidence(f"source-{source_type}", source_type=source_type),
                    extraction(),
                    idempotency_key=f"intake-{source_type}",
                )
                self.assertEqual(result.status, "reconciled")
                self.assertEqual(result.provider_result.status, "created")
                self.assertEqual(result.appointment_result.status, "created")
                self.assertEqual(result.projection_status, "not_requested")
                self.assertEqual(result.appointment.timezone, "America/New_York")
                self.assertEqual(result.appointment.end_at, "2026-09-04T11:00:00-04:00")

    def test_unsupported_source_type_fails_before_any_write(self) -> None:
        with self.assertRaisesRegex(AppointmentIntakeValidationError, "email, image, or text"):
            self.intake.intake(
                evidence("bad", source_type="synthetic"),
                extraction(),
                idempotency_key="bad-source",
            )
        self.assertEqual(self.state.query(PROVIDER_RESOURCE_TYPE), ())
        self.assertEqual(self.state.query(APPOINTMENT_RESOURCE_TYPE), ())

    def test_successful_create_and_exact_replay_do_not_grow_revisions(self) -> None:
        source = evidence("message-1", source_id="gmail-message-1")
        facts = extraction()
        first = self.intake.intake(source, facts, idempotency_key="logical-intake-1")
        second = self.intake.intake(source, facts, idempotency_key="logical-intake-1")

        self.assertEqual(first.status, "reconciled")
        self.assertEqual(second.status, "reconciled")
        self.assertEqual(second.provider_result.status, "replay")
        self.assertEqual(second.appointment_result.status, "replay")
        self.assertEqual(first.provider.provider_id, second.provider.provider_id)
        self.assertEqual(first.appointment.appointment_id, second.appointment.appointment_id)
        self.assertEqual(second.provider.revision, 1)
        self.assertEqual(second.appointment.revision, 1)
        appointment_payload = self.state.get(
            APPOINTMENT_RESOURCE_TYPE, first.appointment.appointment_id
        ).payload
        self.assertNotIn("raw_body", appointment_payload)
        self.assertNotIn("raw_image", appointment_payload)

    def test_low_confidence_occurrence_identity_returns_review_before_mutation(self) -> None:
        facts = extraction()
        confidence = dict(facts.confidence)
        confidence["appointment_start_at"] = 0.50
        result = self.intake.intake(
            evidence("low-start"),
            extraction(confidence=confidence),
            idempotency_key="low-start",
        )

        self.assertEqual(result.status, "needs_review")
        self.assertIn("appointment_start_at", result.omitted_low_confidence_fields)
        self.assertTrue(any("exact start time" in reason for reason in result.review_reasons))
        self.assertEqual(self.state.query(PROVIDER_RESOURCE_TYPE), ())
        self.assertEqual(self.state.query(APPOINTMENT_RESOURCE_TYPE), ())

    def test_low_confidence_optional_field_is_omitted_not_promoted(self) -> None:
        facts = extraction()
        confidence = dict(facts.confidence)
        confidence["appointment_location"] = 0.40
        result = self.intake.intake(
            evidence("low-location"),
            extraction(confidence=confidence),
            idempotency_key="low-location",
        )

        self.assertEqual(result.status, "reconciled")
        self.assertIn("appointment_location", result.omitted_low_confidence_fields)
        self.assertIsNone(result.appointment.location)

    def test_provider_ambiguity_stops_before_appointment_mutation(self) -> None:
        first = self.identity.reconcile_provider(
            ProviderCandidate(
                evidence=evidence("seed-provider-1", source_type="text"),
                display_name="Provider One",
                organization="Clinic One",
                email="one@example.test",
                phone="423-555-0101",
            ),
            idempotency_key="seed-provider-1",
        ).provider
        second = self.identity.reconcile_provider(
            ProviderCandidate(
                evidence=evidence("seed-provider-2", source_type="text"),
                display_name="Provider Two",
                organization="Clinic Two",
                email="two@example.test",
                phone="423-555-0102",
            ),
            idempotency_key="seed-provider-2",
        ).provider

        facts = extraction(
            provider_display_name=None,
            provider_organization=None,
            provider_email="one@example.test",
            provider_phone="423-555-0102",
        )
        result = self.intake.intake(
            evidence("ambiguous-provider"),
            facts,
            idempotency_key="ambiguous-provider",
        )

        self.assertEqual(result.status, "needs_review")
        self.assertEqual(
            set(result.provider_result.candidate_provider_ids),
            {first.provider_id, second.provider_id},
        )
        self.assertEqual(self.state.query(APPOINTMENT_RESOURCE_TYPE), ())

    def test_appointment_ambiguity_surfaces_candidate_occurrences(self) -> None:
        provider = self.identity.reconcile_provider(
            ProviderCandidate(
                evidence=evidence("seed-provider", source_type="text"),
                email="seed@example.test",
            ),
            idempotency_key="seed-provider",
        ).provider
        first = self.identity.reconcile_appointment(
            AppointmentCandidate(
                evidence=evidence("seed-a", source_type="text"),
                provider_id=provider.provider_id,
                start_at="2026-09-04T10:00:00-04:00",
                identity_namespace="ehr",
                identity_value="visit-a",
            ),
            idempotency_key="seed-a",
        ).appointment
        second = self.identity.reconcile_appointment(
            AppointmentCandidate(
                evidence=evidence("seed-b", source_type="text"),
                provider_id=provider.provider_id,
                start_at="2026-09-04T11:00:00-04:00",
                identity_namespace="ehr",
                identity_value="visit-b",
            ),
            idempotency_key="seed-b",
        ).appointment

        result = self.intake.intake(
            evidence("owner-ambiguous", source_type="text", authority="user_confirmed"),
            AppointmentExtraction(
                canonical_provider_id=provider.provider_id,
                appointment_start_at="2026-09-04T11:00:00-04:00",
                appointment_identity_namespace="ehr",
                appointment_identity_value="visit-a",
            ),
            idempotency_key="owner-ambiguous",
        )
        self.assertEqual(result.status, "needs_review")
        self.assertEqual(
            set(result.appointment_result.candidate_appointment_ids),
            {first.appointment_id, second.appointment_id},
        )

    def test_same_source_identity_with_different_material_needs_review(self) -> None:
        first = self.intake.intake(
            evidence("message-original", source_id="gmail-message-1"),
            extraction(),
            idempotency_key="message-original",
        )
        second = self.intake.intake(
            evidence("message-mutated", source_id="gmail-message-1"),
            extraction(),
            idempotency_key="message-mutated",
        )
        self.assertEqual(first.status, "reconciled")
        self.assertEqual(second.status, "needs_review")
        self.assertIn("immutable evidence source", second.review_reasons[0])
        self.assertEqual(second.provider.revision, 1)
        self.assertEqual(
            self.identity.get_appointment(first.appointment.appointment_id).revision,
            1,
        )

    def test_user_confirmed_correction_outranks_later_source_extraction(self) -> None:
        original = self.intake.intake(
            evidence("source-original"),
            extraction(),
            idempotency_key="source-original",
        )
        corrected = self.intake.intake(
            evidence(
                "owner-correction",
                source_type="text",
                authority="user_confirmed",
                observed_at="2026-08-31T13:00:00-04:00",
            ),
            AppointmentExtraction(
                canonical_provider_id=original.provider.provider_id,
                provider_specialty_type="Cardiologist",
                canonical_appointment_id=original.appointment.appointment_id,
                appointment_start_at=original.appointment.start_at,
                appointment_end_at=original.appointment.end_at,
                appointment_timezone=original.appointment.timezone,
                appointment_title="Owner confirmed follow-up",
            ),
            idempotency_key="owner-correction",
        )
        self.assertEqual(corrected.status, "reconciled")
        self.assertEqual(corrected.provider.specialty_type, "Cardiologist")
        self.assertEqual(corrected.appointment.title, "Owner confirmed follow-up")

        later = self.intake.intake(
            evidence("later-source", observed_at="2026-08-31T14:00:00-04:00"),
            extraction(
                provider_specialty_type="Cardiology",
                appointment_title="Cardiology follow-up",
            ),
            idempotency_key="later-source",
        )
        self.assertEqual(later.status, "reconciled")
        self.assertEqual(later.provider.specialty_type, "Cardiologist")
        self.assertEqual(later.appointment.title, "Owner confirmed follow-up")

    def test_requested_but_inactive_service_never_writes_calendar(self) -> None:
        self.services.ensure("appointments_calendar")
        requested = self.services.request_enable(
            "appointments_calendar", idempotency_key="request-only"
        )
        result = self.intake.intake(
            evidence("inactive-calendar"),
            extraction(),
            idempotency_key="inactive-calendar",
            service_state=requested,
            projection_target=self.target(),
        )
        self.assertEqual(result.status, "reconciled")
        self.assertEqual(result.projection_status, "service_inactive")
        self.assertEqual(self.calendar_adapter.write_count, 0)
        self.assertEqual(self.state.query(CALENDAR_PROJECTION_RESOURCE_TYPE), ())

    def test_active_service_projects_exact_canonical_timing(self) -> None:
        active = self.activate_appointment_service()
        result = self.intake.intake(
            evidence("active-calendar"),
            extraction(),
            idempotency_key="active-calendar",
            service_state=active,
            projection_target=self.target(),
        )
        self.assertEqual(result.status, "reconciled")
        self.assertEqual(result.projection_status, "projected")
        self.assertIsNotNone(result.projection_result)
        self.assertEqual(self.calendar_adapter.write_count, 1)
        projected = result.projection_result.projection
        self.assertEqual(projected.source_resource_id, result.appointment.appointment_id)
        self.assertEqual(projected.source_revision, result.appointment.revision)
        self.assertEqual(projected.event.start_at, result.appointment.start_at)
        self.assertEqual(projected.event.end_at, result.appointment.end_at)
        self.assertEqual(projected.event.timezone, result.appointment.timezone)

    def test_projection_failure_does_not_discard_reconciled_appointment(self) -> None:
        self._reset(writable_calendar=False)
        active = self.activate_appointment_service()
        result = self.intake.intake(
            evidence("projection-failure"),
            extraction(),
            idempotency_key="projection-failure",
            service_state=active,
            projection_target=self.target(),
        )
        self.assertEqual(result.status, "reconciled")
        self.assertEqual(result.projection_status, "projection_failed")
        self.assertIsNotNone(result.projection_error)
        self.assertEqual(self.calendar_adapter.write_count, 0)
        stored = self.identity.get_appointment(result.appointment.appointment_id)
        self.assertEqual(stored.revision, result.appointment.revision)


if __name__ == "__main__":
    unittest.main()
