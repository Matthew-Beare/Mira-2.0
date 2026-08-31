from __future__ import annotations

from dataclasses import replace
import unittest

from mira.calendar_projection import (
    CALENDAR_PROJECTION_RESOURCE_TYPE,
    CalendarEventMaterial,
    CalendarProjectionCapabilityError,
    CalendarProjectionConflictError,
    CalendarProjectionReadbackError,
    CalendarProjectionRequest,
    CalendarProjectionService,
    CalendarProjectionValidationError,
    CalendarProviderIdempotencyConflictError,
    InMemoryCalendarProjectionAdapter,
    ProviderCalendarEvent,
)
from mira.structured_state import InMemoryStructuredStateAdapter, NotFoundError


class _MismatchingReadbackAdapter(InMemoryCalendarProjectionAdapter):
    def read_event(self, calendar_ref: str, event_id: str) -> ProviderCalendarEvent:
        current = super().read_event(calendar_ref, event_id)
        return replace(
            current,
            event=replace(current.event, location="Wrong room"),
        )


class CalendarProjectionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.state = InMemoryStructuredStateAdapter(
            schema_version="mira-structured-state-v1",
            resource_types=[CALENDAR_PROJECTION_RESOURCE_TYPE],
            event_types=["created", "updated"],
        )
        self.provider = InMemoryCalendarProjectionAdapter("google")
        self.service = CalendarProjectionService(self.state, self.provider)

    def event(
        self,
        *,
        title: str = "Cardiologist appointment",
        start_at: str = "2026-09-10T09:00:00-04:00",
        end_at: str = "2026-09-10T10:00:00-04:00",
        location: str | None = "Clinic A",
        description: str | None = "Bring insurance card",
    ) -> CalendarEventMaterial:
        return CalendarEventMaterial(
            title=title,
            start_at=start_at,
            end_at=end_at,
            timezone="America/New_York",
            location=location,
            description=description,
        )

    def request(
        self,
        *,
        source_revision: int = 1,
        event: CalendarEventMaterial | None = None,
        calendar_ref: str = "primary",
        provider_lane: str = "google",
    ) -> CalendarProjectionRequest:
        return CalendarProjectionRequest(
            source_resource_type="appointment",
            source_resource_id="appt-001",
            source_revision=source_revision,
            provider_lane=provider_lane,
            calendar_ref=calendar_ref,
            event=self.event() if event is None else event,
        )

    def test_create_writes_provider_then_verified_canonical_projection(self) -> None:
        result = self.service.project(self.request(), idempotency_key="project-001")

        self.assertEqual(result.status, "created")
        self.assertFalse(result.provider_idempotent_replay)
        self.assertEqual(result.projection.revision, 1)
        self.assertEqual(result.projection.source_resource_type, "appointment")
        self.assertEqual(result.projection.source_resource_id, "appt-001")
        self.assertEqual(result.projection.source_revision, 1)
        self.assertEqual(result.projection.provider_lane, "google")
        self.assertEqual(result.projection.calendar_ref, "primary")
        self.assertEqual(result.projection.provider_version, "memory:1")
        self.assertEqual(result.projection.status, "verified")
        self.assertEqual(
            result.projection.desired_sha256,
            result.projection.readback_sha256,
        )
        self.assertEqual(self.provider.write_count, 1)

        provider_event = self.provider.read_event(
            "primary", result.projection.provider_event_id
        )
        self.assertEqual(provider_event.event, result.projection.event)
        stored = self.state.get(
            CALENDAR_PROJECTION_RESOURCE_TYPE, result.projection.projection_id
        )
        self.assertEqual(stored.revision, 1)
        self.assertEqual(stored.payload["provider_event_id"], provider_event.event_id)

    def test_identical_replay_is_zero_write_and_zero_revision_growth(self) -> None:
        first = self.service.project(self.request(), idempotency_key="project-002")
        second = self.service.project(self.request(), idempotency_key="project-002")

        self.assertEqual(second.status, "unchanged")
        self.assertTrue(second.provider_idempotent_replay)
        self.assertEqual(second.projection.projection_id, first.projection.projection_id)
        self.assertEqual(second.projection.provider_event_id, first.projection.provider_event_id)
        self.assertEqual(second.projection.revision, 1)
        self.assertEqual(second.projection.provider_version, "memory:1")
        self.assertEqual(self.provider.write_count, 1)
        self.assertEqual(
            self.state.get(
                CALENDAR_PROJECTION_RESOURCE_TYPE, first.projection.projection_id
            ).revision,
            1,
        )

    def test_newer_source_revision_updates_same_provider_event(self) -> None:
        first = self.service.project(self.request(), idempotency_key="project-003a")
        changed = self.event(
            title="Cardiology follow-up",
            start_at="2026-09-10T10:00:00-04:00",
            end_at="2026-09-10T11:00:00-04:00",
            location="Clinic B",
        )
        second = self.service.project(
            self.request(source_revision=2, event=changed),
            idempotency_key="project-003b",
        )

        self.assertEqual(second.status, "updated")
        self.assertEqual(second.projection.revision, 2)
        self.assertEqual(second.projection.source_revision, 2)
        self.assertEqual(second.projection.provider_event_id, first.projection.provider_event_id)
        self.assertEqual(second.projection.provider_version, "memory:2")
        self.assertEqual(second.projection.event.title, "Cardiology follow-up")
        self.assertEqual(self.provider.write_count, 2)

    def test_stale_source_revision_fails_without_provider_write(self) -> None:
        self.service.project(self.request(), idempotency_key="project-004a")
        updated = self.event(title="Updated title")
        self.service.project(
            self.request(source_revision=2, event=updated),
            idempotency_key="project-004b",
        )
        writes_before = self.provider.write_count

        with self.assertRaises(CalendarProjectionConflictError):
            self.service.project(
                self.request(source_revision=1),
                idempotency_key="project-004c",
            )
        self.assertEqual(self.provider.write_count, writes_before)

    def test_same_source_revision_cannot_change_desired_material(self) -> None:
        first = self.service.project(self.request(), idempotency_key="project-005a")
        writes_before = self.provider.write_count

        with self.assertRaises(CalendarProjectionConflictError):
            self.service.project(
                self.request(event=self.event(title="Different title")),
                idempotency_key="project-005b",
            )
        self.assertEqual(self.provider.write_count, writes_before)
        self.assertEqual(
            self.state.get(
                CALENDAR_PROJECTION_RESOURCE_TYPE, first.projection.projection_id
            ).revision,
            1,
        )

    def test_provider_adapter_rejects_idempotency_key_reuse_for_other_material(self) -> None:
        first = self.provider.upsert_event(
            "primary",
            "projection-one",
            self.event(),
            idempotency_key="provider-key-001",
            expected_provider_version=None,
        )
        self.assertEqual(first.event.provider_version, "memory:1")

        with self.assertRaises(CalendarProviderIdempotencyConflictError):
            self.provider.upsert_event(
                "primary",
                "projection-one",
                self.event(title="Different"),
                idempotency_key="provider-key-001",
                expected_provider_version="memory:1",
            )

    def test_unsupported_provider_capability_fails_before_mutation(self) -> None:
        cases = (
            {"writable": False},
            {"exact_readback": False},
            {"stable_projection_key": False},
        )
        for index, kwargs in enumerate(cases):
            with self.subTest(kwargs=kwargs):
                state = InMemoryStructuredStateAdapter(
                    schema_version="mira-structured-state-v1",
                    resource_types=[CALENDAR_PROJECTION_RESOURCE_TYPE],
                    event_types=["created", "updated"],
                )
                provider = InMemoryCalendarProjectionAdapter("google", **kwargs)
                service = CalendarProjectionService(state, provider)
                with self.assertRaises(CalendarProjectionCapabilityError):
                    service.project(
                        self.request(), idempotency_key=f"capability-{index}"
                    )
                self.assertEqual(provider.write_count, 0)
                self.assertEqual(
                    state.query(CALENDAR_PROJECTION_RESOURCE_TYPE, limit=10), ()
                )

    def test_provider_lane_mismatch_fails_before_mutation(self) -> None:
        with self.assertRaises(CalendarProjectionCapabilityError):
            self.service.project(
                self.request(provider_lane="microsoft"),
                idempotency_key="lane-mismatch",
            )
        self.assertEqual(self.provider.write_count, 0)

    def test_independent_provider_readback_drift_fails_closed(self) -> None:
        first = self.service.project(self.request(), idempotency_key="project-006")
        self.provider.replace_event_for_test(
            "primary",
            first.projection.provider_event_id,
            self.event(title="Externally changed"),
        )

        with self.assertRaises(CalendarProjectionReadbackError):
            self.service.project(self.request(), idempotency_key="project-006")
        self.assertEqual(
            self.state.get(
                CALENDAR_PROJECTION_RESOURCE_TYPE, first.projection.projection_id
            ).revision,
            1,
        )

    def test_missing_provider_event_fails_closed(self) -> None:
        first = self.service.project(self.request(), idempotency_key="project-007")
        self.provider.delete_event_for_test(
            "primary", first.projection.provider_event_id
        )

        with self.assertRaises(CalendarProjectionReadbackError):
            self.service.project(self.request(), idempotency_key="project-007")
        self.assertEqual(
            self.state.get(
                CALENDAR_PROJECTION_RESOURCE_TYPE, first.projection.projection_id
            ).revision,
            1,
        )

    def test_provider_version_conflict_blocks_newer_source_update(self) -> None:
        first = self.service.project(self.request(), idempotency_key="project-008a")
        self.provider.replace_event_for_test(
            "primary",
            first.projection.provider_event_id,
            self.event(),
            bump_version=True,
        )
        writes_before = self.provider.write_count

        with self.assertRaises(CalendarProjectionConflictError):
            self.service.project(
                self.request(
                    source_revision=2,
                    event=self.event(title="Legitimate source update"),
                ),
                idempotency_key="project-008b",
            )
        self.assertEqual(self.provider.write_count, writes_before)
        self.assertEqual(
            self.state.get(
                CALENDAR_PROJECTION_RESOURCE_TYPE, first.projection.projection_id
            ).revision,
            1,
        )

    def test_immediate_provider_readback_mismatch_never_commits_canonical_state(self) -> None:
        state = InMemoryStructuredStateAdapter(
            schema_version="mira-structured-state-v1",
            resource_types=[CALENDAR_PROJECTION_RESOURCE_TYPE],
            event_types=["created", "updated"],
        )
        provider = _MismatchingReadbackAdapter("google")
        service = CalendarProjectionService(state, provider)

        with self.assertRaises(CalendarProjectionReadbackError):
            service.project(self.request(), idempotency_key="project-009")
        self.assertEqual(provider.write_count, 1)
        self.assertEqual(state.query(CALENDAR_PROJECTION_RESOURCE_TYPE, limit=10), ())

    def test_same_source_can_project_to_two_calendars_without_identity_collision(self) -> None:
        first = self.service.project(
            self.request(calendar_ref="primary"), idempotency_key="project-010a"
        )
        second = self.service.project(
            self.request(calendar_ref="work"), idempotency_key="project-010b"
        )

        self.assertNotEqual(first.projection.projection_id, second.projection.projection_id)
        self.assertNotEqual(
            first.projection.provider_event_id, second.projection.provider_event_id
        )
        rows = self.service.projections_for_source("appointment", "appt-001")
        self.assertEqual(
            {row.calendar_ref for row in rows},
            {"primary", "work"},
        )

    def test_timing_validation_is_strict_and_timezone_aware(self) -> None:
        cases = (
            self.event(start_at="2026-09-10T09:00:00", end_at="2026-09-10T10:00:00"),
            replace(self.event(), timezone="Not/AZone"),
            self.event(
                start_at="2026-09-10T10:00:00-04:00",
                end_at="2026-09-10T09:00:00-04:00",
            ),
            self.event(
                start_at="2026-09-10T09:00:00-05:00",
                end_at="2026-09-10T10:00:00-05:00",
            ),
        )
        for index, event in enumerate(cases):
            with self.subTest(index=index):
                with self.assertRaises(CalendarProjectionValidationError):
                    self.service.project(
                        self.request(event=event),
                        idempotency_key=f"invalid-time-{index}",
                    )
        self.assertEqual(self.provider.write_count, 0)

    def test_projection_core_appends_no_structured_state_events(self) -> None:
        result = self.service.project(self.request(), idempotency_key="project-011")
        self.assertEqual(
            self.state.events_for(
                CALENDAR_PROJECTION_RESOURCE_TYPE,
                result.projection.projection_id,
                limit=100,
            ),
            (),
        )

    def test_unknown_projection_is_an_explicit_not_found_boundary(self) -> None:
        with self.assertRaises(CalendarProjectionValidationError):
            self.service.get_projection("calproj-not-found")
        with self.assertRaises(NotFoundError):
            self.state.get(CALENDAR_PROJECTION_RESOURCE_TYPE, "calproj-not-found")


if __name__ == "__main__":
    unittest.main()
