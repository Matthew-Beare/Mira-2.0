from __future__ import annotations

from dataclasses import replace
import unittest

from mira.calendar_projection import (
    CALENDAR_PROJECTION_RESOURCE_TYPE,
    CalendarEventMaterial,
    CalendarProjectionConflictError,
    CalendarProjectionReadbackError,
    CalendarProjectionRequest,
    CalendarProjectionService,
    CalendarProviderConflictError,
)
from mira.google_calendar_native import (
    GOOGLE_NATIVE_PROTECTION_MODE,
    GoogleCalendarNativeSingleWriterAdapter,
    NativeGoogleCalendarEvent,
    NativeGoogleCalendarWrite,
)
from mira.structured_state import InMemoryStructuredStateAdapter


class _FakeNativeGoogleConnector:
    def __init__(self) -> None:
        self.events: dict[tuple[str, str], NativeGoogleCalendarEvent] = {}
        self.create_count = 0
        self.update_count = 0
        self.read_count = 0
        self.search_count = 0
        self.fail_after_create_once = False
        self._next_id = 1
        self.last_create_write: NativeGoogleCalendarWrite | None = None
        self.last_update_write: NativeGoogleCalendarWrite | None = None
        self.last_update_event_id: str | None = None

    def search_events(
        self,
        calendar_ref: str,
        *,
        query: str,
        time_min: str,
        time_max: str,
    ) -> tuple[NativeGoogleCalendarEvent, ...]:
        self.search_count += 1
        return tuple(
            event
            for (calendar, _), event in self.events.items()
            if calendar == calendar_ref
            and query in (event.description or "")
        )

    def create_event(
        self,
        calendar_ref: str,
        write: NativeGoogleCalendarWrite,
    ) -> NativeGoogleCalendarEvent:
        self.create_count += 1
        self.last_create_write = write
        event_id = f"google-event-{self._next_id}"
        self._next_id += 1
        event = NativeGoogleCalendarEvent(
            event_id=event_id,
            title=write.title,
            start_at=write.start_at,
            end_at=write.end_at,
            timezone=write.timezone,
            location=write.location,
            description=write.description,
        )
        self.events[(calendar_ref, event_id)] = event
        if self.fail_after_create_once:
            self.fail_after_create_once = False
            raise RuntimeError("simulated lost create acknowledgement")
        return event

    def update_event(
        self,
        calendar_ref: str,
        event_id: str,
        write: NativeGoogleCalendarWrite,
    ) -> NativeGoogleCalendarEvent:
        if (calendar_ref, event_id) not in self.events:
            raise KeyError(event_id)
        self.update_count += 1
        self.last_update_event_id = event_id
        self.last_update_write = write
        event = NativeGoogleCalendarEvent(
            event_id=event_id,
            title=write.title,
            start_at=write.start_at,
            end_at=write.end_at,
            timezone=write.timezone,
            location=write.location,
            description=write.description,
        )
        self.events[(calendar_ref, event_id)] = event
        return event

    def read_event(
        self,
        calendar_ref: str,
        event_id: str,
    ) -> NativeGoogleCalendarEvent:
        self.read_count += 1
        return self.events[(calendar_ref, event_id)]

    def replace_for_test(
        self,
        calendar_ref: str,
        event_id: str,
        **changes: object,
    ) -> None:
        current = self.events[(calendar_ref, event_id)]
        self.events[(calendar_ref, event_id)] = replace(current, **changes)


class GoogleCalendarNativeSingleWriterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.state = InMemoryStructuredStateAdapter(
            schema_version="mira-structured-state-v1",
            resource_types=[CALENDAR_PROJECTION_RESOURCE_TYPE],
            event_types=["created", "updated"],
        )
        self.connector = _FakeNativeGoogleConnector()
        self.adapter = GoogleCalendarNativeSingleWriterAdapter(
            self.connector,
            self.state,
        )
        self.service = CalendarProjectionService(self.state, self.adapter)

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
    ) -> CalendarProjectionRequest:
        return CalendarProjectionRequest(
            source_resource_type="appointment",
            source_resource_id="appt-001",
            source_revision=source_revision,
            provider_lane="google",
            calendar_ref="primary",
            event=self.event() if event is None else event,
        )

    def test_capability_evidence_is_plain_intent_single_writer_and_non_atomic(self) -> None:
        evidence = self.adapter.capability_evidence()
        self.assertEqual(evidence["update_protection"], GOOGLE_NATIVE_PROTECTION_MODE)
        self.assertEqual(evidence["supported_writer_model"], "single_writer")
        self.assertFalse(evidence["atomic_provider_version_precondition"])
        self.assertEqual(
            evidence["ordinary_user_activation"],
            "plain_language_intent_plus_provider_consent",
        )

    def test_create_uses_safe_native_write_and_exact_readback(self) -> None:
        result = self.service.project(self.request(), idempotency_key="native-create")

        self.assertEqual(result.status, "created")
        self.assertEqual(self.connector.create_count, 1)
        self.assertGreaterEqual(self.connector.read_count, 1)
        write = self.connector.last_create_write
        assert write is not None
        self.assertEqual(write.attendees, ())
        self.assertFalse(write.add_google_meet)
        self.assertEqual(write.self_attendance, "omit")
        self.assertIn("MIRA-PROJECTION-ID:", write.description)
        self.assertEqual(result.projection.event.description, "Bring insurance card")
        self.assertTrue(result.projection.provider_version.startswith("native:"))

    def test_identical_replay_does_not_create_a_second_event(self) -> None:
        first = self.service.project(self.request(), idempotency_key="native-replay")
        second = self.service.project(self.request(), idempotency_key="native-replay")

        self.assertEqual(second.status, "unchanged")
        self.assertEqual(second.projection.provider_event_id, first.projection.provider_event_id)
        self.assertEqual(self.connector.create_count, 1)
        self.assertEqual(len(self.connector.events), 1)

    def test_lost_create_ack_is_recovered_by_projection_marker_without_duplicate(self) -> None:
        self.connector.fail_after_create_once = True

        result = self.service.project(
            self.request(),
            idempotency_key="native-lost-ack",
        )

        self.assertEqual(result.status, "created")
        self.assertTrue(result.provider_idempotent_replay)
        self.assertEqual(self.connector.create_count, 1)
        self.assertEqual(len(self.connector.events), 1)
        self.assertGreaterEqual(self.connector.search_count, 2)

    def test_newer_source_updates_exact_persisted_event_id(self) -> None:
        first = self.service.project(self.request(), idempotency_key="native-update-a")
        changed = self.event(
            title="Cardiology follow-up",
            start_at="2026-09-10T10:00:00-04:00",
            end_at="2026-09-10T11:00:00-04:00",
            location="Clinic B",
        )
        second = self.service.project(
            self.request(source_revision=2, event=changed),
            idempotency_key="native-update-b",
        )

        self.assertEqual(second.status, "updated")
        self.assertEqual(self.connector.update_count, 1)
        self.assertEqual(
            self.connector.last_update_event_id,
            first.projection.provider_event_id,
        )
        self.assertEqual(second.projection.provider_event_id, first.projection.provider_event_id)
        self.assertEqual(second.projection.event, changed)

    def test_manual_provider_drift_blocks_update_before_write(self) -> None:
        first = self.service.project(self.request(), idempotency_key="native-drift-a")
        self.connector.replace_for_test(
            "primary",
            first.projection.provider_event_id,
            title="Human edited title",
        )

        with self.assertRaises(CalendarProjectionConflictError):
            self.service.project(
                self.request(
                    source_revision=2,
                    event=self.event(title="Legitimate canonical update"),
                ),
                idempotency_key="native-drift-b",
            )
        self.assertEqual(self.connector.update_count, 0)

    def test_removed_projection_marker_fails_closed(self) -> None:
        first = self.service.project(self.request(), idempotency_key="native-marker-a")
        raw = self.connector.events[("primary", first.projection.provider_event_id)]
        self.connector.replace_for_test(
            "primary",
            first.projection.provider_event_id,
            description="Bring insurance card",
        )

        with self.assertRaises(CalendarProjectionReadbackError):
            self.service.project(self.request(), idempotency_key="native-marker-a")
        self.assertEqual(self.connector.update_count, 0)
        self.assertNotEqual(raw.description, "Bring insurance card")

    def test_duplicate_projection_marker_candidates_fail_closed(self) -> None:
        projection = "calproj-duplicate-test"
        event = self.event()
        write = NativeGoogleCalendarWrite(
            title=event.title,
            start_at=event.start_at,
            end_at=event.end_at,
            timezone=event.timezone,
            location=event.location,
            description=f"{event.description}\n\nMIRA-PROJECTION-ID:{projection}",
        )
        self.connector.create_event("primary", write)
        self.connector.create_event("primary", write)

        with self.assertRaises(CalendarProviderConflictError):
            self.adapter.upsert_event(
                "primary",
                projection,
                event,
                idempotency_key="duplicate-marker",
                expected_provider_version=None,
            )


if __name__ == "__main__":
    unittest.main()
