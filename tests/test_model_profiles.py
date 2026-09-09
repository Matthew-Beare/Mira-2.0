import dataclasses
import math
import unittest

from mira.model_profiles import (
    BenchmarkComparator,
    BenchmarkEvidenceKind,
    BenchmarkObservation,
    BenchmarkRequirement,
    ModelProfile,
    ModelProfileError,
    ModelSelectionRequest,
    evaluate_model_profiles,
)


NOW = "2026-09-09T05:30:00Z"


def profile(
    profile_id: str,
    *,
    capabilities: tuple[str, ...] = ("code", "reasoning"),
    context: int = 32768,
    output: int = 4096,
) -> ModelProfile:
    return ModelProfile(
        profile_id=profile_id,
        runtime_id=f"runtime-{profile_id}",
        artifact_id=f"artifact-{profile_id}",
        artifact_sha256=("a" if profile_id.endswith("a") else "b") * 64,
        capabilities=capabilities,
        context_window_tokens=context,
        max_output_tokens=output,
    )


def requirement(
    *,
    benchmark_id: str = "quality-suite",
    version: str = "v1",
    capability: str = "reasoning",
    metric: str = "score",
    comparator: BenchmarkComparator = BenchmarkComparator.AT_LEAST,
    threshold: float = 0.8,
    unit: str = "ratio",
    max_age: int = 3600,
    allowed: tuple[BenchmarkEvidenceKind, ...] = (BenchmarkEvidenceKind.MEASURED,),
) -> BenchmarkRequirement:
    return BenchmarkRequirement(
        benchmark_id=benchmark_id,
        benchmark_version=version,
        capability_id=capability,
        metric_id=metric,
        comparator=comparator,
        threshold=threshold,
        unit=unit,
        max_age_seconds=max_age,
        allowed_evidence_kinds=allowed,
    )


def observation(
    profile_id: str,
    *,
    benchmark_id: str = "quality-suite",
    version: str = "v1",
    capability: str = "reasoning",
    metric: str = "score",
    value: float = 0.9,
    unit: str = "ratio",
    observed_at: str = "2026-09-09T05:20:00Z",
    sample_count: int = 5,
    kind: BenchmarkEvidenceKind = BenchmarkEvidenceKind.MEASURED,
    provenance_char: str = "c",
) -> BenchmarkObservation:
    return BenchmarkObservation(
        profile_id=profile_id,
        benchmark_id=benchmark_id,
        benchmark_version=version,
        capability_id=capability,
        metric_id=metric,
        value=value,
        unit=unit,
        observed_at=observed_at,
        sample_count=sample_count,
        evidence_kind=kind,
        provenance_sha256=provenance_char * 64,
    )


def request(
    *,
    capabilities: tuple[str, ...] = ("reasoning",),
    context: int = 8192,
    output: int = 1024,
    requirements: tuple[BenchmarkRequirement, ...] = (),
    preferred: tuple[str, ...] = (),
) -> ModelSelectionRequest:
    return ModelSelectionRequest(
        required_capabilities=capabilities,
        min_context_window_tokens=context,
        min_max_output_tokens=output,
        benchmark_requirements=requirements,
        preferred_profile_ids=preferred,
    )


class ModelProfileTests(unittest.TestCase):
    def test_profile_requires_sorted_unique_capabilities(self) -> None:
        with self.assertRaisesRegex(ModelProfileError, "sorted and unique"):
            profile("profile-a", capabilities=("reasoning", "code"))
        with self.assertRaisesRegex(ModelProfileError, "sorted and unique"):
            profile("profile-a", capabilities=("code", "code"))

    def test_profile_capacity_and_digest_validation(self) -> None:
        with self.assertRaisesRegex(ModelProfileError, "cannot exceed"):
            profile("profile-a", context=1024, output=2048)
        with self.assertRaisesRegex(ModelProfileError, "SHA-256"):
            ModelProfile(
                profile_id="profile-a",
                runtime_id="runtime-a",
                artifact_id="artifact-a",
                artifact_sha256="ABC",
                capabilities=("code",),
                context_window_tokens=1024,
                max_output_tokens=128,
            )

    def test_observation_rejects_nonfinite_value_invalid_kind_and_sample_count(self) -> None:
        with self.assertRaisesRegex(ModelProfileError, "finite"):
            observation("profile-a", value=math.inf)
        with self.assertRaisesRegex(ModelProfileError, "BenchmarkEvidenceKind"):
            BenchmarkObservation(
                profile_id="profile-a",
                benchmark_id="quality-suite",
                benchmark_version="v1",
                capability_id="reasoning",
                metric_id="score",
                value=0.9,
                unit="ratio",
                observed_at="2026-09-09T05:20:00Z",
                sample_count=5,
                evidence_kind="measured",  # type: ignore[arg-type]
                provenance_sha256="c" * 64,
            )
        with self.assertRaisesRegex(ModelProfileError, "positive integer"):
            observation("profile-a", sample_count=0)

    def test_requirement_rejects_invalid_comparator_and_unsorted_evidence_kinds(self) -> None:
        with self.assertRaisesRegex(ModelProfileError, "BenchmarkComparator"):
            BenchmarkRequirement(
                benchmark_id="quality-suite",
                benchmark_version="v1",
                capability_id="reasoning",
                metric_id="score",
                comparator="at_least",  # type: ignore[arg-type]
                threshold=0.8,
                unit="ratio",
                max_age_seconds=60,
                allowed_evidence_kinds=(BenchmarkEvidenceKind.MEASURED,),
            )
        with self.assertRaisesRegex(ModelProfileError, "sorted and unique"):
            requirement(
                allowed=(
                    BenchmarkEvidenceKind.SYNTHETIC,
                    BenchmarkEvidenceKind.MEASURED,
                )
            )

    def test_request_requires_sorted_capabilities_and_benchmark_capability_alignment(self) -> None:
        with self.assertRaisesRegex(ModelProfileError, "sorted and unique"):
            request(capabilities=("reasoning", "code"))
        with self.assertRaisesRegex(ModelProfileError, "must also be required"):
            request(capabilities=("code",), requirements=(requirement(),))

    def test_capability_gate_blocks_missing_capability(self) -> None:
        decision = evaluate_model_profiles(
            (profile("profile-a", capabilities=("code",)),),
            (),
            request(),
            now=NOW,
        )
        evaluation = decision.evaluations[0]
        self.assertFalse(evaluation.eligible)
        self.assertEqual(
            evaluation.blocker_reason_codes,
            ("capability_missing:reasoning",),
        )
        self.assertIsNone(decision.selected_profile_id)
        self.assertEqual(decision.selection_reason_code, "no_eligible_profile")

    def test_context_and_output_capacity_gates(self) -> None:
        context_decision = evaluate_model_profiles(
            (profile("profile-a", context=4096, output=1024),),
            (),
            request(context=8192, output=1024),
            now=NOW,
        )
        self.assertIn(
            "context_window_below_minimum",
            context_decision.evaluations[0].blocker_reason_codes,
        )
        output_decision = evaluate_model_profiles(
            (profile("profile-a", context=8192, output=512),),
            (),
            request(context=8192, output=1024),
            now=NOW,
        )
        self.assertIn(
            "max_output_below_minimum",
            output_decision.evaluations[0].blocker_reason_codes,
        )

    def test_at_least_exact_threshold_is_eligible(self) -> None:
        req = requirement(threshold=0.8)
        decision = evaluate_model_profiles(
            (profile("profile-a"),),
            (observation("profile-a", value=0.8),),
            request(requirements=(req,)),
            now=NOW,
        )
        self.assertTrue(decision.evaluations[0].eligible)
        self.assertEqual(decision.selected_profile_id, "profile-a")

    def test_at_most_exact_threshold_is_eligible(self) -> None:
        req = requirement(
            benchmark_id="latency-suite",
            metric="p50_ms",
            comparator=BenchmarkComparator.AT_MOST,
            threshold=100.0,
            unit="ms",
        )
        obs = observation(
            "profile-a",
            benchmark_id="latency-suite",
            metric="p50_ms",
            value=100.0,
            unit="ms",
        )
        decision = evaluate_model_profiles(
            (profile("profile-a"),),
            (obs,),
            request(requirements=(req,)),
            now=NOW,
        )
        self.assertTrue(decision.evaluations[0].eligible)

    def test_threshold_failures_are_directional(self) -> None:
        quality = evaluate_model_profiles(
            (profile("profile-a"),),
            (observation("profile-a", value=0.79),),
            request(requirements=(requirement(threshold=0.8),)),
            now=NOW,
        )
        self.assertIn(
            "benchmark:quality-suite:score:threshold_not_met",
            quality.evaluations[0].blocker_reason_codes,
        )
        latency_req = requirement(
            benchmark_id="latency-suite",
            metric="p50_ms",
            comparator=BenchmarkComparator.AT_MOST,
            threshold=100.0,
            unit="ms",
        )
        latency = evaluate_model_profiles(
            (profile("profile-a"),),
            (
                observation(
                    "profile-a",
                    benchmark_id="latency-suite",
                    metric="p50_ms",
                    value=100.1,
                    unit="ms",
                ),
            ),
            request(requirements=(latency_req,)),
            now=NOW,
        )
        self.assertIn(
            "benchmark:latency-suite:p50_ms:threshold_not_met",
            latency.evaluations[0].blocker_reason_codes,
        )

    def test_missing_benchmark_evidence_blocks_profile(self) -> None:
        decision = evaluate_model_profiles(
            (profile("profile-a"),),
            (),
            request(requirements=(requirement(),)),
            now=NOW,
        )
        self.assertEqual(
            decision.evaluations[0].blocker_reason_codes,
            ("benchmark:quality-suite:score:evidence_missing",),
        )

    def test_stale_benchmark_evidence_blocks_profile(self) -> None:
        decision = evaluate_model_profiles(
            (profile("profile-a"),),
            (
                observation(
                    "profile-a",
                    observed_at="2026-09-09T04:00:00Z",
                ),
            ),
            request(requirements=(requirement(max_age=3600),)),
            now=NOW,
        )
        self.assertIn(
            "benchmark:quality-suite:score:evidence_stale",
            decision.evaluations[0].blocker_reason_codes,
        )

    def test_unit_mismatch_blocks_profile(self) -> None:
        decision = evaluate_model_profiles(
            (profile("profile-a"),),
            (observation("profile-a", unit="percent"),),
            request(requirements=(requirement(unit="ratio"),)),
            now=NOW,
        )
        self.assertIn(
            "benchmark:quality-suite:score:unit_mismatch",
            decision.evaluations[0].blocker_reason_codes,
        )

    def test_disallowed_evidence_kind_blocks_profile(self) -> None:
        decision = evaluate_model_profiles(
            (profile("profile-a"),),
            (
                observation(
                    "profile-a",
                    kind=BenchmarkEvidenceKind.SYNTHETIC,
                ),
            ),
            request(requirements=(requirement(),)),
            now=NOW,
        )
        self.assertIn(
            "benchmark:quality-suite:score:evidence_kind_disallowed",
            decision.evaluations[0].blocker_reason_codes,
        )

    def test_explicit_policy_can_allow_synthetic_evidence(self) -> None:
        req = requirement(allowed=(BenchmarkEvidenceKind.SYNTHETIC,))
        decision = evaluate_model_profiles(
            (profile("profile-a"),),
            (
                observation(
                    "profile-a",
                    kind=BenchmarkEvidenceKind.SYNTHETIC,
                ),
            ),
            request(requirements=(req,)),
            now=NOW,
        )
        self.assertTrue(decision.evaluations[0].eligible)

    def test_future_matching_evidence_fails_profile_closed(self) -> None:
        decision = evaluate_model_profiles(
            (profile("profile-a"),),
            (
                observation(
                    "profile-a",
                    observed_at="2026-09-09T05:31:00Z",
                ),
            ),
            request(requirements=(requirement(),)),
            now=NOW,
        )
        self.assertIn(
            "benchmark:quality-suite:score:evidence_from_future",
            decision.evaluations[0].blocker_reason_codes,
        )
        self.assertIsNone(decision.selected_profile_id)

    def test_duplicate_observation_key_fails_closed(self) -> None:
        first = observation("profile-a", value=0.8)
        second = observation("profile-a", value=0.9, provenance_char="d")
        with self.assertRaisesRegex(ModelProfileError, "keys must be unique"):
            evaluate_model_profiles(
                (profile("profile-a"),),
                (first, second),
                request(requirements=(requirement(),)),
                now=NOW,
            )

    def test_extra_unrelated_observation_does_not_gain_authority(self) -> None:
        relevant = observation("profile-a", value=0.9)
        unrelated = observation(
            "profile-a",
            benchmark_id="unrequested-suite",
            capability="code",
            metric="throughput",
            value=-9999.0,
            unit="tok/s",
            observed_at="2026-09-09T05:40:00Z",
            kind=BenchmarkEvidenceKind.SYNTHETIC,
            provenance_char="e",
        )
        decision = evaluate_model_profiles(
            (profile("profile-a"),),
            (unrelated, relevant),
            request(requirements=(requirement(),)),
            now=NOW,
        )
        self.assertTrue(decision.evaluations[0].eligible)

    def test_explicit_preference_order_wins_among_eligible_profiles(self) -> None:
        decision = evaluate_model_profiles(
            (profile("profile-a"), profile("profile-b")),
            (),
            request(preferred=("profile-b", "profile-a")),
            now=NOW,
        )
        self.assertEqual(decision.selected_profile_id, "profile-b")
        self.assertEqual(decision.selection_reason_code, "preferred_profile_eligible")

    def test_ineligible_preferred_profile_is_skipped(self) -> None:
        decision = evaluate_model_profiles(
            (
                profile("profile-a"),
                profile("profile-b", capabilities=("code",)),
            ),
            (),
            request(preferred=("profile-b", "profile-a")),
            now=NOW,
        )
        self.assertEqual(decision.selected_profile_id, "profile-a")
        self.assertEqual(decision.selection_reason_code, "preferred_profile_eligible")

    def test_stable_profile_id_tie_break_has_no_inferred_quality_meaning(self) -> None:
        decision = evaluate_model_profiles(
            (profile("profile-b"), profile("profile-a")),
            (),
            request(),
            now=NOW,
        )
        self.assertEqual(decision.selected_profile_id, "profile-a")
        self.assertEqual(decision.selection_reason_code, "stable_profile_id_tiebreak")

    def test_profile_and_observation_input_order_do_not_change_result(self) -> None:
        req = requirement()
        profiles_a = (profile("profile-b"), profile("profile-a"))
        observations_a = (
            observation("profile-b", value=0.85, provenance_char="d"),
            observation("profile-a", value=0.90),
        )
        left = evaluate_model_profiles(
            profiles_a,
            observations_a,
            request(requirements=(req,)),
            now=NOW,
        )
        right = evaluate_model_profiles(
            tuple(reversed(profiles_a)),
            tuple(reversed(observations_a)),
            request(requirements=(req,)),
            now=NOW,
        )
        self.assertEqual(left, right)

    def test_duplicate_profile_ids_fail_closed(self) -> None:
        with self.assertRaisesRegex(ModelProfileError, "profile IDs must be unique"):
            evaluate_model_profiles(
                (profile("profile-a"), profile("profile-a")),
                (),
                request(),
                now=NOW,
            )

    def test_no_eligible_profile_is_explicit(self) -> None:
        decision = evaluate_model_profiles(
            (profile("profile-a", capabilities=("code",)),),
            (),
            request(),
            now=NOW,
        )
        self.assertIsNone(decision.selected_profile_id)
        self.assertEqual(decision.selection_reason_code, "no_eligible_profile")

    def test_public_profile_and_decision_shapes_have_no_private_binding_fields(self) -> None:
        decision = evaluate_model_profiles(
            (profile("profile-a"),),
            (),
            request(),
            now=NOW,
        )
        keys = set(dataclasses.asdict(profile("profile-a")).keys())
        keys.update(dataclasses.asdict(decision).keys())
        serialized_keys = " ".join(sorted(keys)).lower()
        for forbidden in (
            "hostname",
            "ip_address",
            "mac_address",
            "credential",
            "private_key",
            "model_path",
            "shell_command",
            "inference_endpoint",
            "provider_resource",
            "gpu_serial",
        ):
            self.assertNotIn(forbidden, serialized_keys)

    def test_preferred_profile_ids_must_be_unique(self) -> None:
        with self.assertRaisesRegex(ModelProfileError, "must be unique"):
            request(preferred=("profile-a", "profile-a"))


if __name__ == "__main__":
    unittest.main()
