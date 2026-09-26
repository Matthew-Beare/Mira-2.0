from __future__ import annotations

import unittest

from mira.google_bootstrap import (
    GoogleBootstrapError,
    plan_personal_google_bootstrap,
    verify_personal_google_bootstrap,
)
from mira.service_state import (
    AuthorizationState,
    CapabilityEvidenceState,
    CapabilityGate,
    ConnectionState,
    GateObservation,
    ProviderCapabilitySnapshot,
)


NOW = "2026-09-26T07:15:00+00:00"


def snapshot(
    service_id: str,
    gates: tuple[CapabilityGate, ...],
    *,
    provider_id: str = "google",
    state: CapabilityEvidenceState = CapabilityEvidenceState.VERIFIED,
    authorization: AuthorizationState = AuthorizationState.AUTHORIZED,
    observed_at: str = NOW,
    resource_ref: str | None = None,
) -> ProviderCapabilitySnapshot:
    return ProviderCapabilitySnapshot(
        provider_id=provider_id,
        service_id=service_id,
        authorization_state=authorization,
        authorization_observed_at=observed_at,
        gates=tuple(
            GateObservation(
                gate=gate,
                state=state,
                observed_at=observed_at,
            )
            for gate in gates
        ),
        resource_ref=resource_ref,
    )


class PersonalGoogleBootstrapTests(unittest.TestCase):
    def test_plan_is_deterministic_and_deduplicated(self) -> None:
        plan = plan_personal_google_bootstrap(("sheets", "calendar", "sheets"))
        self.assertEqual(plan.provider_id, "google")
        self.assertEqual(
            tuple(service.service_id for service in plan.services),
            ("calendar", "sheets"),
        )

    def test_plan_rejects_unselected_or_unknown_services(self) -> None:
        with self.assertRaises(GoogleBootstrapError):
            plan_personal_google_bootstrap(())
        with self.assertRaises(GoogleBootstrapError):
            plan_personal_google_bootstrap(("drive",))

    def test_all_selected_services_require_fresh_verified_capability(self) -> None:
        plan = plan_personal_google_bootstrap(("gmail", "calendar"))
        evidence = {
            "gmail": snapshot("gmail", (CapabilityGate.READ,)),
            "calendar": snapshot(
                "calendar",
                (
                    CapabilityGate.READ,
                    CapabilityGate.WRITE,
                    CapabilityGate.REMOTE_READBACK,
                ),
                resource_ref="calendar:primary",
            ),
        }
        result = verify_personal_google_bootstrap(
            plan,
            evidence,
            now=NOW,
            max_age_seconds=300,
        )
        self.assertTrue(result.ready)
        self.assertTrue(all(service.ready for service in result.services))
        self.assertEqual(
            result.services[0].connection_state,
            ConnectionState.CONNECTED,
        )
        self.assertEqual(result.services[0].resource_ref, "calendar:primary")

    def test_missing_selected_service_evidence_fails_closed(self) -> None:
        plan = plan_personal_google_bootstrap(("calendar", "gmail"))
        result = verify_personal_google_bootstrap(
            plan,
            {"gmail": snapshot("gmail", (CapabilityGate.READ,))},
            now=NOW,
            max_age_seconds=300,
        )
        calendar = next(
            service for service in result.services if service.service_id == "calendar"
        )
        self.assertFalse(result.ready)
        self.assertFalse(calendar.ready)
        self.assertEqual(calendar.connection_state, ConnectionState.NEEDS_ATTENTION)
        self.assertEqual(calendar.blockers, ("provider:evidence:missing",))

    def test_declared_gate_is_not_verified_capability(self) -> None:
        plan = plan_personal_google_bootstrap(("gmail",))
        result = verify_personal_google_bootstrap(
            plan,
            {
                "gmail": snapshot(
                    "gmail",
                    (CapabilityGate.READ,),
                    state=CapabilityEvidenceState.DECLARED,
                )
            },
            now=NOW,
            max_age_seconds=300,
        )
        self.assertFalse(result.ready)
        self.assertIn(
            "provider:read:not_verified",
            result.services[0].blockers,
        )

    def test_snapshot_identity_mismatch_is_rejected(self) -> None:
        plan = plan_personal_google_bootstrap(("gmail",))
        with self.assertRaises(GoogleBootstrapError):
            verify_personal_google_bootstrap(
                plan,
                {
                    "gmail": snapshot(
                        "gmail",
                        (CapabilityGate.READ,),
                        provider_id="microsoft",
                    )
                },
                now=NOW,
                max_age_seconds=300,
            )


if __name__ == "__main__":
    unittest.main()
