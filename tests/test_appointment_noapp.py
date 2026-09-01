from __future__ import annotations

import hashlib
import json
import unittest

from mira.appointment_intake import AppointmentExtraction, CalendarProjectionTarget
from mira.appointment_noapp import (
    AppointmentNoAppIntegrityError,
    DirectAppointmentEvidence,
    FINGERPRINT_DERIVED_EXTRACTION,
    FINGERPRINT_EXACT_TEXT,
    FINGERPRINT_RAW_IMAGE,
    build_direct_evidence,
    plan_appointment_workspace_bindings,
    plan_direct_appointment_intake,
    verify_appointment_workspace_bindings,
    verify_direct_appointment_readback,
)
from mira.calendar_projection import (
    CALENDAR_PROJECTION_RESOURCE_TYPE,
    CalendarProjectionService,
    InMemoryCalendarProjectionAdapter,
)
from mira.service_state import ServiceStateView
from mira.structured_state import InMemoryStructuredStateAdapter, ResourceRecord
from mira.workspace_native import WorkspaceIdempotencyRecord


OBSERVED_AT = "2026-09-01T09:00:00-04:00"


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
            key: 0.99
            for key, value in values.items()
            if key != "confidence" and value is not None
        }
    return AppointmentExtraction(**values)


def text_source(
    material: str = "Cardiology appointment September 4 at 10 AM",
    *,
    source_ref: str = "chat:conversation-1:turn-1",
    authority: str = "source",
) -> DirectAppointmentEvidence:
    return DirectAppointmentEvidence(
        source_type="text",
        source_ref=source_ref,
        observed_at=OBSERVED_AT,
        authority=authority,
        text_material=material,
    )


def image_source(
    *,
    source_ref: str = "attachment:synthetic-1",
    raw_file_sha256: str | None = None,
    authority: str = "source",
) -> DirectAppointmentEvidence:
    return DirectAppointmentEvidence(
        source_type="image",
        source_ref=source_ref,
        observed_at=OBSERVED_AT,
        authority=authority,
        raw_file_sha256=raw_file_sha256,
    )


def personal_authority() -> ResourceRecord:
    return ResourceRecord(
        "authority",
        "google-sheets-personal",
        {
            "adapter_key": "google-sheets",
            "authority_id": "google-sheets-personal",
            "enabled": True,
            "failure_domain": "google-sheets-personal",
            "namespace": "mira-personal",
            "owner_id": "synthetic-owner",
            "resource_ref": "runtime:google-structured-state",
            "schema_version": "mira-structured-state-v1",
            "verified": True,
        },
        1,
    )


def resource_rows_from_plans(plans, *, start_row: int = 2):
    return [
        (row, plan.record)
        for row, plan in enumerate(plans, start=start_row)
    ]


def idempotency_rows_from_plans(plans, *, start_row: int = 2):
    return [
        WorkspaceIdempotencyRecord(
            row_number=row,
            idempotency_key=plan.idempotency_key,
            operation="upsert",
            request_hash=plan.request_hash,
            result=plan.result,
            resource_ref=f"{plan.record.resource_type}/{plan.record.resource_id}",
        )
        for row, plan in enumerate(plans, start=start_row)
    ]


class AppointmentNoAppTests(unittest.TestCase):
    def test_direct_text_hashes_exact_user_material_without_storing_it(self) -> None:
        raw = "  Dr Ada appointment\nSeptember 4 at 10 AM  "
        facts = extraction()
        observation = build_direct_evidence(text_source(raw), facts)
        self.assertEqual(observation.fingerprint_basis, FINGERPRINT_EXACT_TEXT)
        self.assertEqual(
            observation.evidence.material_sha256,
            hashlib.sha256(raw.encode("utf-8")).hexdigest(),
        )
        self.assertIn("fingerprint_basis=exact_text_sha256", observation.evidence.source_id)

        plan = plan_direct_appointment_intake(
            text_source(raw),
            facts,
            logical_key="direct-text-1",
            resource_rows=[],
            idempotency_rows=[],
        )
        self.assertEqual(plan.intake_result.status, "reconciled")
        self.assertEqual(len(plan.workspace_plans), 2)
        payload_text = json.dumps(
            [native.record.payload for native in plan.workspace_plans],
            sort_keys=True,
        )
        self.assertNotIn(raw, payload_text)
        self.assertNotIn("Dr Ada appointment\\nSeptember 4", payload_text)

    def test_image_uses_verified_raw_hash_when_runtime_exposes_it(self) -> None:
        raw_hash = hashlib.sha256(b"synthetic-image-bytes").hexdigest()
        observation = build_direct_evidence(
            image_source(raw_file_sha256=raw_hash), extraction()
        )
        self.assertEqual(observation.fingerprint_basis, FINGERPRINT_RAW_IMAGE)
        self.assertEqual(observation.evidence.material_sha256, raw_hash)
        self.assertIn("fingerprint_basis=raw_file_sha256", observation.evidence.source_id)

    def test_image_without_raw_hash_labels_normalized_extraction_fallback(self) -> None:
        first = build_direct_evidence(image_source(), extraction())
        second = build_direct_evidence(image_source(), extraction())
        changed = build_direct_evidence(
            image_source(), extraction(appointment_location="200 Different Way")
        )
        self.assertEqual(first.fingerprint_basis, FINGERPRINT_DERIVED_EXTRACTION)
        self.assertEqual(first.evidence.material_sha256, second.evidence.material_sha256)
        self.assertNotEqual(first.evidence.material_sha256, changed.evidence.material_sha256)
        self.assertIn(
            "fingerprint_basis=normalized_extraction_sha256_v1",
            first.evidence.source_id,
        )

    def test_changed_extraction_for_same_derived_image_source_fails_closed(self) -> None:
        first = plan_direct_appointment_intake(
            image_source(),
            extraction(),
            logical_key="image-first",
            resource_rows=[],
            idempotency_rows=[],
        )
        persisted = resource_rows_from_plans(first.workspace_plans)
        second = plan_direct_appointment_intake(
            image_source(),
            extraction(appointment_location="200 Different Way"),
            logical_key="image-second",
            resource_rows=persisted,
            idempotency_rows=idempotency_rows_from_plans(first.workspace_plans),
        )
        self.assertTrue(second.needs_review)
        self.assertIn("already recorded", second.review_question)
        self.assertEqual(second.workspace_plans, ())

    def test_low_confidence_start_returns_only_material_clarification(self) -> None:
        facts = extraction()
        confidence = dict(facts.confidence)
        confidence["appointment_start_at"] = 0.4
        plan = plan_direct_appointment_intake(
            text_source(),
            extraction(confidence=confidence),
            logical_key="low-start",
            resource_rows=[],
            idempotency_rows=[],
        )
        self.assertTrue(plan.needs_review)
        self.assertEqual(
            plan.review_question,
            "What is the exact appointment date and time, including timezone?",
        )
        self.assertEqual(plan.workspace_plans, ())

    def test_create_replay_and_user_confirmed_correction_use_native_plans(self) -> None:
        first = plan_direct_appointment_intake(
            text_source(),
            extraction(),
            logical_key="direct-create",
            resource_rows=[],
            idempotency_rows=[],
        )
        self.assertEqual(len(first.workspace_plans), 2)
        self.assertEqual(
            len(
                first.batch_update_requests(
                    resources_sheet_id=101,
                    idempotency_sheet_id=202,
                    timestamp="2026-09-01T13:05:00Z",
                )
            ),
            4,
        )
        persisted = resource_rows_from_plans(first.workspace_plans)
        idem = idempotency_rows_from_plans(first.workspace_plans)
        verify_direct_appointment_readback(
            first, resource_rows=persisted, idempotency_rows=idem
        )

        replay = plan_direct_appointment_intake(
            text_source(),
            extraction(),
            logical_key="direct-create",
            resource_rows=persisted,
            idempotency_rows=idem,
        )
        self.assertTrue(replay.idempotent_replay)
        self.assertEqual(replay.workspace_plans, ())
        self.assertEqual(replay.intake_result.provider_result.status, "replay")
        self.assertEqual(replay.intake_result.appointment_result.status, "replay")

        provider_id = first.intake_result.provider.provider_id
        appointment_id = first.intake_result.appointment.appointment_id
        corrected = extraction(
            canonical_provider_id=provider_id,
            canonical_appointment_id=appointment_id,
            appointment_location="300 Confirmed Avenue",
            confidence={},
        )
        correction = plan_direct_appointment_intake(
            text_source(
                "User confirms the appointment is at 300 Confirmed Avenue",
                source_ref="chat:conversation-1:turn-2",
                authority="user_confirmed",
            ),
            corrected,
            logical_key="direct-correction",
            resource_rows=persisted,
            idempotency_rows=idem,
        )
        self.assertEqual(correction.intake_result.status, "reconciled")
        self.assertEqual(
            correction.intake_result.appointment.location,
            "300 Confirmed Avenue",
        )
        self.assertEqual(correction.intake_result.appointment.revision, 2)
        self.assertGreaterEqual(len(correction.workspace_plans), 1)

    def test_personal_appointment_bindings_are_added_without_rewriting_entity_bootstrap(self) -> None:
        rows = [(2, personal_authority())]
        plan = plan_appointment_workspace_bindings(
            resource_rows=rows, idempotency_rows=[]
        )
        self.assertEqual(len(plan.plans), 3)
        self.assertEqual(
            {native.record.payload["data_class"] for native in plan.plans},
            {"appointment_provider", "appointment", "calendar_projection"},
        )
        self.assertEqual(
            len(
                plan.batch_update_requests(
                    resources_sheet_id=101,
                    idempotency_sheet_id=202,
                    timestamp="2026-09-01T13:10:00Z",
                )
            ),
            6,
        )
        persisted = rows + resource_rows_from_plans(plan.plans, start_row=3)
        verify_appointment_workspace_bindings(resource_rows=persisted)
        replay = plan_appointment_workspace_bindings(
            resource_rows=persisted,
            idempotency_rows=idempotency_rows_from_plans(plan.plans),
        )
        self.assertTrue(replay.idempotent_replay)

    def test_conflicting_appointment_binding_fails_closed(self) -> None:
        conflict = ResourceRecord(
            "authority_binding",
            "other-binding",
            {"authority_id": "other-authority", "data_class": "appointment"},
            1,
        )
        with self.assertRaisesRegex(
            AppointmentNoAppIntegrityError, "conflicting canonical authority"
        ):
            plan_appointment_workspace_bindings(
                resource_rows=[(2, personal_authority()), (3, conflict)],
                idempotency_rows=[],
            )

    def test_calendar_target_is_suppressed_when_service_is_not_active(self) -> None:
        plan = plan_direct_appointment_intake(
            text_source(),
            extraction(),
            logical_key="calendar-inactive",
            resource_rows=[],
            idempotency_rows=[],
            projection_target=CalendarProjectionTarget(
                provider_lane="google", calendar_ref="synthetic-calendar"
            ),
        )
        self.assertEqual(plan.intake_result.status, "reconciled")
        self.assertEqual(plan.intake_result.projection_status, "service_inactive")
        self.assertEqual(len(plan.workspace_plans), 2)

    def test_active_service_can_handoff_to_synthetic_projection_without_claiming_live_google(self) -> None:
        projection_state = InMemoryStructuredStateAdapter(
            schema_version="synthetic-projection-v1",
            resource_types=[CALENDAR_PROJECTION_RESOURCE_TYPE],
            event_types=["created", "updated"],
        )
        projection = CalendarProjectionService(
            projection_state,
            InMemoryCalendarProjectionAdapter("google", writable=True),
        )
        active = ServiceStateView(
            service_id="appointments_calendar",
            revision=3,
            activation_state="active",
            capability_state="available",
            recommendation_state="none",
            dependency_blockers=(),
            suspension_reason=None,
        )
        plan = plan_direct_appointment_intake(
            text_source(source_ref="chat:projection:turn-1"),
            extraction(),
            logical_key="calendar-active",
            resource_rows=[],
            idempotency_rows=[],
            service_state=active,
            projection_target=CalendarProjectionTarget(
                provider_lane="google", calendar_ref="synthetic-calendar"
            ),
            calendar_projection=projection,
        )
        self.assertEqual(plan.intake_result.status, "reconciled")
        self.assertEqual(plan.intake_result.projection_status, "projected")
        self.assertIsNotNone(plan.intake_result.projection_result)
        self.assertEqual(
            len(projection_state.query(CALENDAR_PROJECTION_RESOURCE_TYPE)), 1
        )


if __name__ == "__main__":
    unittest.main()
