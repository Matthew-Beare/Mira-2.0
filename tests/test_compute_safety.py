import dataclasses
import math
import unittest

from mira.compute_safety import (
    ComputeSafetyDecision,
    ComputeSafetyError,
    ComputeSafetyPolicy,
    SafetySeverity,
    SensorDirection,
    SensorEvidenceState,
    SensorObservation,
    SensorSafetyPolicy,
    evaluate_compute_safety,
)


NOW = "2026-09-09T04:45:00Z"


def high_policy(
    sensor_id: str = "thermal_core",
    *,
    warning: float = 70.0,
    critical: float = 80.0,
    max_age: int = 60,
) -> SensorSafetyPolicy:
    return SensorSafetyPolicy(
        sensor_id=sensor_id,
        unit="degC",
        direction=SensorDirection.HIGH_IS_BAD,
        warning_threshold=warning,
        critical_threshold=critical,
        max_age_seconds=max_age,
    )


def low_policy(
    sensor_id: str = "cooling_flow",
    *,
    warning: float = 2.0,
    critical: float = 1.0,
    max_age: int = 60,
) -> SensorSafetyPolicy:
    return SensorSafetyPolicy(
        sensor_id=sensor_id,
        unit="L/min",
        direction=SensorDirection.LOW_IS_BAD,
        warning_threshold=warning,
        critical_threshold=critical,
        max_age_seconds=max_age,
    )


def policy(
    *sensors: SensorSafetyPolicy,
    shutdown_critical: bool = False,
    shutdown_fault: bool = False,
) -> ComputeSafetyPolicy:
    return ComputeSafetyPolicy(
        policy_id="configured-safety-policy",
        sensors=tuple(sensors or (high_policy(),)),
        safe_shutdown_on_critical=shutdown_critical,
        safe_shutdown_on_sensor_fault=shutdown_fault,
    )


def observation(
    sensor_id: str,
    value: float,
    *,
    unit: str = "degC",
    observed_at: str = "2026-09-09T04:44:30Z",
) -> SensorObservation:
    return SensorObservation(
        sensor_id=sensor_id,
        value=value,
        unit=unit,
        observed_at=observed_at,
    )


class ComputeSafetyTests(unittest.TestCase):
    def test_high_is_bad_exact_threshold_boundaries(self):
        configured = policy(high_policy())
        cases = (
            (69.999, SafetySeverity.NORMAL),
            (70.0, SafetySeverity.WARNING),
            (79.999, SafetySeverity.WARNING),
            (80.0, SafetySeverity.CRITICAL),
            (90.0, SafetySeverity.CRITICAL),
        )
        for value, expected in cases:
            with self.subTest(value=value):
                result = evaluate_compute_safety(
                    configured,
                    (observation("thermal_core", value),),
                    now=NOW,
                )
                self.assertEqual(result.aggregate_severity, expected)
                self.assertEqual(result.sensors[0].severity, expected)

    def test_low_is_bad_exact_threshold_boundaries(self):
        configured = policy(low_policy())
        cases = (
            (2.001, SafetySeverity.NORMAL),
            (2.0, SafetySeverity.WARNING),
            (1.001, SafetySeverity.WARNING),
            (1.0, SafetySeverity.CRITICAL),
            (0.5, SafetySeverity.CRITICAL),
        )
        for value, expected in cases:
            with self.subTest(value=value):
                result = evaluate_compute_safety(
                    configured,
                    (observation("cooling_flow", value, unit="L/min"),),
                    now=NOW,
                )
                self.assertEqual(result.aggregate_severity, expected)

    def test_warning_blocks_admission_and_requests_drain_only(self):
        result = evaluate_compute_safety(
            policy(high_policy()),
            (observation("thermal_core", 75.0),),
            now=NOW,
        )
        self.assertEqual(result.aggregate_severity, SafetySeverity.WARNING)
        self.assertFalse(result.response.admit_new_work)
        self.assertTrue(result.response.request_drain)
        self.assertFalse(result.response.stop_workloads)
        self.assertFalse(result.response.fault_node)
        self.assertFalse(result.response.require_safe_shutdown)

    def test_critical_stop_fault_and_shutdown_are_explicit_policy(self):
        reading = (observation("thermal_core", 80.0),)
        no_shutdown = evaluate_compute_safety(
            policy(high_policy(), shutdown_critical=False),
            reading,
            now=NOW,
        )
        shutdown = evaluate_compute_safety(
            policy(high_policy(), shutdown_critical=True),
            reading,
            now=NOW,
        )
        for result in (no_shutdown, shutdown):
            self.assertEqual(result.aggregate_severity, SafetySeverity.CRITICAL)
            self.assertFalse(result.response.admit_new_work)
            self.assertTrue(result.response.request_drain)
            self.assertTrue(result.response.stop_workloads)
            self.assertTrue(result.response.fault_node)
        self.assertFalse(no_shutdown.response.require_safe_shutdown)
        self.assertTrue(shutdown.response.require_safe_shutdown)

    def test_missing_required_sensor_is_fault_and_shutdown_is_explicit(self):
        no_shutdown = evaluate_compute_safety(
            policy(high_policy(), shutdown_fault=False), (), now=NOW
        )
        shutdown = evaluate_compute_safety(
            policy(high_policy(), shutdown_fault=True), (), now=NOW
        )
        for result in (no_shutdown, shutdown):
            self.assertEqual(result.aggregate_severity, SafetySeverity.SENSOR_FAULT)
            self.assertEqual(result.sensors[0].evidence_state, SensorEvidenceState.MISSING)
            self.assertEqual(result.sensors[0].reason_code, "sensor_missing")
            self.assertTrue(result.response.request_drain)
            self.assertTrue(result.response.stop_workloads)
            self.assertTrue(result.response.fault_node)
        self.assertFalse(no_shutdown.response.require_safe_shutdown)
        self.assertTrue(shutdown.response.require_safe_shutdown)

    def test_staleness_boundary_equal_is_fresh_but_greater_is_fault(self):
        configured = policy(high_policy(max_age=60))
        exact = evaluate_compute_safety(
            configured,
            (
                observation(
                    "thermal_core",
                    50.0,
                    observed_at="2026-09-09T04:44:00Z",
                ),
            ),
            now=NOW,
        )
        stale = evaluate_compute_safety(
            configured,
            (
                observation(
                    "thermal_core",
                    50.0,
                    observed_at="2026-09-09T04:43:59Z",
                ),
            ),
            now=NOW,
        )
        self.assertEqual(exact.sensors[0].evidence_state, SensorEvidenceState.FRESH)
        self.assertEqual(exact.aggregate_severity, SafetySeverity.NORMAL)
        self.assertEqual(exact.sensors[0].age_seconds, 60.0)
        self.assertEqual(stale.sensors[0].evidence_state, SensorEvidenceState.STALE)
        self.assertEqual(stale.aggregate_severity, SafetySeverity.SENSOR_FAULT)
        self.assertEqual(stale.sensors[0].age_seconds, 61.0)

    def test_future_configured_observation_fails_validation(self):
        with self.assertRaisesRegex(ComputeSafetyError, "cannot be from the future"):
            evaluate_compute_safety(
                policy(high_policy()),
                (
                    observation(
                        "thermal_core",
                        50.0,
                        observed_at="2026-09-09T04:45:01Z",
                    ),
                ),
                now=NOW,
            )

    def test_unit_mismatch_is_sensor_fault_without_comparing_value(self):
        result = evaluate_compute_safety(
            policy(high_policy(), shutdown_fault=True),
            (observation("thermal_core", -999999.0, unit="rpm"),),
            now=NOW,
        )
        self.assertEqual(result.aggregate_severity, SafetySeverity.SENSOR_FAULT)
        self.assertEqual(
            result.sensors[0].evidence_state, SensorEvidenceState.UNIT_MISMATCH
        )
        self.assertEqual(result.sensors[0].reason_code, "sensor_unit_mismatch")
        self.assertTrue(result.response.require_safe_shutdown)

    def test_unknown_extra_observation_never_acquires_safety_authority(self):
        configured = policy(high_policy())
        baseline = evaluate_compute_safety(
            configured,
            (observation("thermal_core", 50.0),),
            now=NOW,
        )
        with_extra = evaluate_compute_safety(
            configured,
            (
                observation("thermal_core", 50.0),
                observation("unknown_sensor", 999999.0, unit="mystery"),
            ),
            now=NOW,
        )
        self.assertEqual(baseline, with_extra)
        self.assertEqual(with_extra.aggregate_severity, SafetySeverity.NORMAL)
        self.assertEqual(len(with_extra.sensors), 1)

    def test_duplicate_observation_ids_fail_closed_even_if_unknown(self):
        with self.assertRaisesRegex(ComputeSafetyError, "duplicate sensor observation"):
            evaluate_compute_safety(
                policy(high_policy()),
                (
                    observation("unknown", 1.0, unit="x"),
                    observation("unknown", 2.0, unit="x"),
                    observation("thermal_core", 50.0),
                ),
                now=NOW,
            )

    def test_simultaneous_critical_and_sensor_fault_shutdown_is_or_of_explicit_flags(self):
        sensors = (high_policy("thermal_core"), low_policy("cooling_flow"))
        observations = (observation("thermal_core", 85.0),)
        combinations = (
            (False, False, False),
            (True, False, True),
            (False, True, True),
            (True, True, True),
        )
        for shutdown_critical, shutdown_fault, expected in combinations:
            with self.subTest(
                critical=shutdown_critical,
                fault=shutdown_fault,
            ):
                result = evaluate_compute_safety(
                    policy(
                        *sensors,
                        shutdown_critical=shutdown_critical,
                        shutdown_fault=shutdown_fault,
                    ),
                    observations,
                    now=NOW,
                )
                self.assertEqual(
                    result.aggregate_severity, SafetySeverity.SENSOR_FAULT
                )
                self.assertTrue(
                    any(item.severity == SafetySeverity.CRITICAL for item in result.sensors)
                )
                self.assertTrue(
                    any(item.severity == SafetySeverity.SENSOR_FAULT for item in result.sensors)
                )
                self.assertEqual(result.response.require_safe_shutdown, expected)

    def test_policy_and_observation_input_order_do_not_change_decision(self):
        first_policy = policy(
            high_policy("thermal_core"),
            low_policy("cooling_flow"),
            shutdown_critical=True,
        )
        second_policy = policy(
            low_policy("cooling_flow"),
            high_policy("thermal_core"),
            shutdown_critical=True,
        )
        first_observations = (
            observation("thermal_core", 75.0),
            observation("cooling_flow", 3.0, unit="L/min"),
        )
        second_observations = tuple(reversed(first_observations))
        first = evaluate_compute_safety(first_policy, first_observations, now=NOW)
        second = evaluate_compute_safety(second_policy, second_observations, now=NOW)
        self.assertEqual(first, second)
        self.assertEqual(
            tuple(item.sensor_id for item in first.sensors),
            ("cooling_flow", "thermal_core"),
        )
        self.assertEqual(first.reason_codes, tuple(sorted(first.reason_codes)))

    def test_policy_validation_rejects_invalid_configuration(self):
        bad_factories = (
            lambda: SensorSafetyPolicy(
                "high",
                "degC",
                SensorDirection.HIGH_IS_BAD,
                80.0,
                80.0,
                60,
            ),
            lambda: SensorSafetyPolicy(
                "low",
                "rpm",
                SensorDirection.LOW_IS_BAD,
                1.0,
                2.0,
                60,
            ),
            lambda: SensorSafetyPolicy(
                "nan",
                "degC",
                SensorDirection.HIGH_IS_BAD,
                math.nan,
                80.0,
                60,
            ),
            lambda: SensorSafetyPolicy(
                "age",
                "degC",
                SensorDirection.HIGH_IS_BAD,
                70.0,
                80.0,
                0,
            ),
            lambda: ComputeSafetyPolicy(
                "empty",
                (),
                False,
                False,
            ),
            lambda: ComputeSafetyPolicy(
                "duplicate",
                (high_policy("same"), high_policy("same")),
                False,
                False,
            ),
            lambda: ComputeSafetyPolicy(
                "bad-bool",
                (high_policy(),),
                1,
                False,
            ),
        )
        for factory in bad_factories:
            with self.subTest(factory=factory):
                with self.assertRaises(ComputeSafetyError):
                    factory()

    def test_evidence_shape_is_bounded_and_private_machine_free(self):
        decision = evaluate_compute_safety(
            policy(high_policy(), shutdown_critical=True),
            (observation("thermal_core", 81.0),),
            now=NOW,
        )
        self.assertIsInstance(decision, ComputeSafetyDecision)
        material = repr(dataclasses.asdict(decision)).lower()
        for forbidden in (
            "hostname",
            "ip_address",
            "mac_address",
            "serial_number",
            "credential",
            "token",
            "password",
            "shell_command",
            "model_path",
            "provider_resource_id",
        ):
            self.assertNotIn(forbidden, material)

    def test_normal_response_has_no_operational_action_requirement(self):
        result = evaluate_compute_safety(
            policy(high_policy(), shutdown_critical=True, shutdown_fault=True),
            (observation("thermal_core", 50.0),),
            now=NOW,
        )
        self.assertEqual(result.aggregate_severity, SafetySeverity.NORMAL)
        self.assertTrue(result.response.admit_new_work)
        self.assertFalse(result.response.request_drain)
        self.assertFalse(result.response.stop_workloads)
        self.assertFalse(result.response.fault_node)
        self.assertFalse(result.response.require_safe_shutdown)
        self.assertEqual(result.reason_codes, ())


if __name__ == "__main__":
    unittest.main()
