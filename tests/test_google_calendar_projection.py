from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
import re
import unittest

from mira.calendar_projection import (
    CALENDAR_PROJECTION_RESOURCE_TYPE,
    CalendarEventMaterial,
    CalendarProjectionConflictError,
    CalendarProjectionRequest,
    CalendarProjectionService,
    CalendarProviderConflictError,
    CalendarProviderError,
    CalendarProviderIdempotencyConflictError,
    CalendarProviderValidationError,
)
from mira.google_calendar_projection import (
    GoogleCalendarProjectionAdapter,
    GoogleCalendarTransportConflictError,
    GoogleCalendarTransportNotFoundError,
    InMemoryCalendarProviderIdempotencyStore,
    google_event_id,
)
from mira.structured_state import InMemoryStructuredStateAdapter


class _FakeGoogleCalendarTransport:
    def __init__(self) -> None:
        self.roles = {"sandbox": "owner", "reader": "reader"}
        self.events: dict[tuple[str, str], dict] = {}
        self.insert_count = 0
        self.patch_count = 0
        self.get_count = 0
        self.last_if_match: str | None = None
        self.raise_conflict_after_patch_once = False
        self._version = 0

    def calendar_access_role(self, calendar_ref: str) -> str:
        try:
            return self.roles[calendar_ref]
        except KeyError as exc:
            raise GoogleCalendarTransportNotFoundError(calendar_ref) from exc

    def get_event(self, calendar_ref: str, event_id: str) -> dict:
        self.get_count += 1
        try:
            return deepcopy(self.events[(calendar_ref, event_id)])
        except KeyError as exc:
            raise GoogleCalendarTransportNotFoundError(event_id) from exc

    def insert_event(self, calendar_ref: str, event_id: str, body: dict) -> dict:
        if (calendar_ref, event_id) in self.events:
            raise GoogleCalendarTransportConflictError("duplicate event ID")
        raw = deepcopy(body)
        raw["id"] = event_id
        raw["etag"] = self._next_etag()
        self.events[(calendar_ref, event_id)] = raw
        self.insert_count += 1
        return deepcopy(raw)

    def patch_event(
        self,
        calendar_ref: str,
        event_id: str,
        body: dict,
        *,
        if_match_etag: str,
    ) -> dict:
        try:
            current = self.events[(calendar_ref, event_id)]
        except KeyError as exc:
            raise GoogleCalendarTransportNotFoundError(event_id) from exc
        self.last_if_match = if_match_etag
        if current["etag"] != if_match_etag:
            raise GoogleCalendarTransportConflictError("stale etag")
        patched = deepcopy(current)
        for key, value in body.items():
            if key == "extendedProperties":
                patched[key] = deepcopy(value)
            elif value is None:
                patched.pop(key, None)
            else:
                patched[key] = deepcopy(value)
        patched["etag"] = self._next_etag()
        self.events[(calendar_ref, event_id)] = patched
        self.patch_count += 1
        if self.raise_conflict_after_patch_once:
            self.raise_conflict_after_patch_once = False
            raise GoogleCalendarTransportConflictError("response lost after commit")
        return deepcopy(patched)

    def external_change(self, calendar_ref: str, event_id: str, **changes: object) -> None:
        current = deepcopy(self.events[(calendar_ref, event_id)])
        current.update(changes)
        current["etag"] = self._next_etag()
        self.events[(calendar_ref, event_id)] = current

    def _next_etag(self) -> str:
        self._version += 1
        return f'"etag-{self._version}"'


class _FailOnceLedger(InMemoryCalendarProviderIdempotencyStore):
    def __init__(self) -> None:
        super().__init__()
        self.fail_once = True

    def put(self, record):  # type: ignore[no-untyped-def]
        if self.fail_once:
            self.fail_once = False
            raise RuntimeError("simulated ledger outage")
        return super().put(record)


class GoogleCalendarProjectionAdapterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.transport = _FakeGoogleCalendarTransport()
        self.ledger = InMemoryCalendarProviderIdempotencyStore()
        self.adapter = GoogleCalendarProjectionAdapter(self.transport, self.ledger)

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

    def test_google_event_id_is_stable_and_base32hex_compatible(self) -> None:
        first = google_event_id("calproj-123")
        second = google_event_id("calproj-123")
        self.assertEqual(first, second)
        self.assertRegex(first, re.compile(r"^[0-9a-v]{5,1024}$"))
        self.assertNotEqual(first, google_event_id("calproj-456"))

    def test_create_uses_deterministic_id_private_metadata_and_exact_etag(self) -> None:
        result = self.adapter.upsert_event(
            "sandbox",
            "calproj-create",
            self.event(),
            idempotency_key="idem-create",
            expected_provider_version=None,
        )

        self.assertFalse(result.idempotent_replay)
        self.assertEqual(result.event.provider_lane, "google")
        self.assertEqual(result.event.provider_version, '"etag-1"')
        self.assertEqual(result.event.event_id, google_event_id("calproj-create"))
        self.assertEqual(self.transport.insert_count, 1)
        raw = self.transport.events[("sandbox", result.event.event_id)]
        private = raw["extendedProperties"]["private"]
        self.assertEqual(private["miraProjectionKey"], "calproj-create")
        self.assertEqual(private["miraIdempotencyKey"], "idem-create")
        self.assertRegex(private["miraRequestHash"], re.compile(r"^[0-9a-f]{64}$"))
        self.assertEqual(raw["start"]["timeZone"], "America/New_York")
        self.assertEqual(raw["end"]["timeZone"], "America/New_York")

    def test_exact_idempotency_replay_is_zero_write(self) -> None:
        first = self.adapter.upsert_event(
            "sandbox",
            "calproj-replay",
            self.event(),
            idempotency_key="idem-replay",
            expected_provider_version=None,
        )
        second = self.adapter.upsert_event(
            "sandbox",
            "calproj-replay",
            self.event(),
            idempotency_key="idem-replay",
            expected_provider_version=None,
        )
        self.assertTrue(second.idempotent_replay)
        self.assertEqual(second.event, first.event)
        self.assertEqual(self.transport.insert_count, 1)
        self.assertEqual(self.transport.patch_count, 0)

    def test_insert_crash_before_ledger_persistence_recovers_from_provider_metadata(self) -> None:
        ledger = _FailOnceLedger()
        adapter = GoogleCalendarProjectionAdapter(self.transport, ledger)
        with self.assertRaises(CalendarProviderError):
            adapter.upsert_event(
                "sandbox",
                "calproj-insert-crash",
                self.event(),
                idempotency_key="idem-insert-crash",
                expected_provider_version=None,
            )
        self.assertEqual(self.transport.insert_count, 1)

        replay = adapter.upsert_event(
            "sandbox",
            "calproj-insert-crash",
            self.event(),
            idempotency_key="idem-insert-crash",
            expected_provider_version=None,
        )
        self.assertTrue(replay.idempotent_replay)
        self.assertEqual(self.transport.insert_count, 1)

    def test_update_uses_exact_previous_etag_as_if_match(self) -> None:
        first = self.adapter.upsert_event(
            "sandbox",
            "calproj-update",
            self.event(),
            idempotency_key="idem-update-1",
            expected_provider_version=None,
        )
        changed = self.event(title="Cardiology follow-up")
        second = self.adapter.upsert_event(
            "sandbox",
            "calproj-update",
            changed,
            idempotency_key="idem-update-2",
            expected_provider_version=first.event.provider_version,
        )
        self.assertFalse(second.idempotent_replay)
        self.assertEqual(self.transport.last_if_match, '"etag-1"')
        self.assertEqual(second.event.provider_version, '"etag-2"')
        self.assertEqual(second.event.event.title, "Cardiology follow-up")
        self.assertEqual(self.transport.patch_count, 1)

    def test_external_etag_change_blocks_stale_update_before_patch(self) -> None:
        first = self.adapter.upsert_event(
            "sandbox",
            "calproj-stale",
            self.event(),
            idempotency_key="idem-stale-1",
            expected_provider_version=None,
        )
        self.transport.external_change(
            "sandbox", first.event.event_id, summary="External edit"
        )
        with self.assertRaises(CalendarProviderConflictError):
            self.adapter.upsert_event(
                "sandbox",
                "calproj-stale",
                self.event(title="Source update"),
                idempotency_key="idem-stale-2",
                expected_provider_version=first.event.provider_version,
            )
        self.assertEqual(self.transport.patch_count, 0)

    def test_update_response_loss_recovers_using_private_retry_metadata(self) -> None:
        first = self.adapter.upsert_event(
            "sandbox",
            "calproj-patch-crash",
            self.event(),
            idempotency_key="idem-patch-1",
            expected_provider_version=None,
        )
        self.transport.raise_conflict_after_patch_once = True
        changed = self.event(location="Clinic B")
        result = self.adapter.upsert_event(
            "sandbox",
            "calproj-patch-crash",
            changed,
            idempotency_key="idem-patch-2",
            expected_provider_version=first.event.provider_version,
        )
        self.assertTrue(result.idempotent_replay)
        self.assertEqual(result.event.event.location, "Clinic B")
        self.assertEqual(result.event.provider_version, '"etag-2"')
        self.assertEqual(self.transport.patch_count, 1)

    def test_durable_ledger_rejects_old_key_reuse_for_different_material(self) -> None:
        self.adapter.upsert_event(
            "sandbox",
            "calproj-old-key",
            self.event(),
            idempotency_key="idem-old",
            expected_provider_version=None,
        )
        with self.assertRaises(CalendarProviderIdempotencyConflictError):
            self.adapter.upsert_event(
                "sandbox",
                "calproj-old-key",
                self.event(title="Different request"),
                idempotency_key="idem-old",
                expected_provider_version='"etag-1"',
            )
        self.assertEqual(self.transport.patch_count, 0)

    def test_reader_calendar_fails_before_any_provider_write(self) -> None:
        with self.assertRaises(CalendarProviderValidationError):
            self.adapter.upsert_event(
                "reader",
                "calproj-reader",
                self.event(),
                idempotency_key="idem-reader",
                expected_provider_version=None,
            )
        self.assertEqual(self.transport.insert_count, 0)
        self.assertEqual(self.transport.patch_count, 0)

    def test_deterministic_event_collision_with_other_projection_fails_closed(self) -> None:
        event_id = google_event_id("calproj-collision")
        raw = {
            "id": event_id,
            "etag": '"etag-existing"',
            "summary": self.event().title,
            "start": {
                "dateTime": self.event().start_at,
                "timeZone": self.event().timezone,
            },
            "end": {
                "dateTime": self.event().end_at,
                "timeZone": self.event().timezone,
            },
            "location": self.event().location,
            "description": self.event().description,
            "extendedProperties": {
                "private": {"miraProjectionKey": "calproj-other"}
            },
        }
        self.transport.events[("sandbox", event_id)] = raw
        with self.assertRaises(CalendarProviderConflictError):
            self.adapter.upsert_event(
                "sandbox",
                "calproj-collision",
                self.event(),
                idempotency_key="idem-collision",
                expected_provider_version=None,
            )
        self.assertEqual(self.transport.insert_count, 0)
        self.assertEqual(self.transport.patch_count, 0)

    def test_projection_service_integrates_google_adapter_with_opaque_etags(self) -> None:
        state = InMemoryStructuredStateAdapter(
            schema_version="mira-structured-state-v1",
            resource_types=[CALENDAR_PROJECTION_RESOURCE_TYPE],
            event_types=["created", "updated"],
        )
        service = CalendarProjectionService(state, self.adapter)
        first = service.project(
            CalendarProjectionRequest(
                source_resource_type="appointment",
                source_resource_id="appt-google-001",
                source_revision=1,
                provider_lane="google",
                calendar_ref="sandbox",
                event=self.event(),
            ),
            idempotency_key="project-google-1",
        )
        self.assertEqual(first.status, "created")
        self.assertEqual(first.projection.provider_version, '"etag-1"')

        changed = replace(self.event(), title="Updated appointment")
        second = service.project(
            CalendarProjectionRequest(
                source_resource_type="appointment",
                source_resource_id="appt-google-001",
                source_revision=2,
                provider_lane="google",
                calendar_ref="sandbox",
                event=changed,
            ),
            idempotency_key="project-google-2",
        )
        self.assertEqual(second.status, "updated")
        self.assertEqual(second.projection.provider_version, '"etag-2"')
        self.assertEqual(second.projection.provider_event_id, first.projection.provider_event_id)
        self.assertEqual(second.projection.event.title, "Updated appointment")


if __name__ == "__main__":
    unittest.main()
