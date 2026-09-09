import dataclasses
import unittest

from mira.studio_competition import (
    CandidateEvaluation,
    CritiqueEvidence,
    CritiqueResolution,
    CritiqueSeverity,
    IntegrationPlan,
    ReviewerSelection,
    StudioCandidate,
    StudioCompetitionDecision,
    StudioCompetitionError,
    StudioWorkSpec,
    VerificationEvidence,
    VerificationOutcome,
    evaluate_studio_competition,
)


BASE = "1" * 40
HEAD_A = "2" * 40
HEAD_B = "3" * 40
OLD_HEAD = "4" * 40
SOURCE_A = "a" * 64
SOURCE_B = "b" * 64
VERIFY_CI_A = "c" * 64
VERIFY_UNIT_A = "d" * 64
VERIFY_CI_B = "e" * 64
VERIFY_UNIT_B = "f" * 64
CRITIQUE_A = "1" * 64
CRITIQUE_B = "2" * 64


def spec(*, independent: bool = True) -> StudioWorkSpec:
    return StudioWorkSpec(
        packet_id="M2-M1-031",
        work_id="SKILL-BUILDER-001",
        base_sha=BASE,
        feature_ids=("DEV-004", "STUDIO-001"),
        acceptance_criteria=("criterion-api", "criterion-tests"),
        required_verification_suites=("ci", "unit"),
        require_independent_critique=independent,
    )


def candidate_a(**changes) -> StudioCandidate:
    values = dict(
        candidate_id="candidate-a",
        producer_id="producer-a",
        branch="studio/candidate-a",
        base_sha=BASE,
        head_sha=HEAD_A,
        acceptance_criteria=("criterion-api", "criterion-tests"),
        source_sha256=SOURCE_A,
    )
    values.update(changes)
    return StudioCandidate(**values)


def candidate_b(**changes) -> StudioCandidate:
    values = dict(
        candidate_id="candidate-b",
        producer_id="producer-b",
        branch="studio/candidate-b",
        base_sha=BASE,
        head_sha=HEAD_B,
        acceptance_criteria=("criterion-api", "criterion-tests"),
        source_sha256=SOURCE_B,
    )
    values.update(changes)
    return StudioCandidate(**values)


def verification(
    candidate_id: str,
    head_sha: str,
    suite_id: str,
    digest: str,
    *,
    outcome: VerificationOutcome = VerificationOutcome.PASSED,
) -> VerificationEvidence:
    return VerificationEvidence(
        candidate_id=candidate_id,
        head_sha=head_sha,
        suite_id=suite_id,
        outcome=outcome,
        evidence_sha256=digest,
    )


def a_verifications():
    return (
        verification("candidate-a", HEAD_A, "ci", VERIFY_CI_A),
        verification("candidate-a", HEAD_A, "unit", VERIFY_UNIT_A),
    )


def b_verifications():
    return (
        verification("candidate-b", HEAD_B, "ci", VERIFY_CI_B),
        verification("candidate-b", HEAD_B, "unit", VERIFY_UNIT_B),
    )


def critique_a(
    *,
    critic_id: str = "reviewer-b",
    head_sha: str = HEAD_A,
    severity: CritiqueSeverity = CritiqueSeverity.NON_BLOCKING,
    resolution: CritiqueResolution = CritiqueResolution.OPEN,
    finding_id: str = "finding-a",
    digest: str = CRITIQUE_A,
) -> CritiqueEvidence:
    return CritiqueEvidence(
        target_candidate_id="candidate-a",
        target_head_sha=head_sha,
        critic_id=critic_id,
        finding_id=finding_id,
        severity=severity,
        resolution=resolution,
        evidence_sha256=digest,
    )


def critique_b() -> CritiqueEvidence:
    return CritiqueEvidence(
        target_candidate_id="candidate-b",
        target_head_sha=HEAD_B,
        critic_id="reviewer-a",
        finding_id="finding-b",
        severity=CritiqueSeverity.BLOCKING,
        resolution=CritiqueResolution.RESOLVED,
        evidence_sha256=CRITIQUE_B,
    )


class StudioCompetitionTests(unittest.TestCase):
    def test_ready_candidate_requires_no_automatic_integration_plan(self):
        decision = evaluate_studio_competition(
            spec(),
            (candidate_a(),),
            a_verifications(),
            (critique_a(),),
        )
        self.assertEqual(decision.eligible_candidate_ids, ("candidate-a",))
        self.assertTrue(decision.evaluations[0].integration_ready)
        self.assertEqual(decision.evaluations[0].blockers, ())
        self.assertIsNone(decision.integration_plan)

    def test_explicit_reviewer_selection_binds_exact_head_and_evidence(self):
        decision = evaluate_studio_competition(
            spec(),
            (candidate_a(),),
            a_verifications(),
            (critique_a(),),
            reviewer_selection=ReviewerSelection(
                reviewer_id="integrator",
                candidate_id="candidate-a",
                head_sha=HEAD_A,
            ),
        )
        self.assertIsInstance(decision.integration_plan, IntegrationPlan)
        plan = decision.integration_plan
        self.assertEqual(plan.candidate_id, "candidate-a")
        self.assertEqual(plan.branch, "studio/candidate-a")
        self.assertEqual(plan.base_sha, BASE)
        self.assertEqual(plan.head_sha, HEAD_A)
        self.assertEqual(plan.source_sha256, SOURCE_A)
        self.assertEqual(
            plan.verification_evidence_sha256s,
            tuple(sorted((VERIFY_CI_A, VERIFY_UNIT_A))),
        )
        self.assertEqual(plan.critique_evidence_sha256s, (CRITIQUE_A,))

    def test_multiple_ready_candidates_are_sorted_and_not_auto_ranked(self):
        decision = evaluate_studio_competition(
            spec(),
            (candidate_b(), candidate_a()),
            tuple(reversed(a_verifications() + b_verifications())),
            (critique_b(), critique_a()),
        )
        self.assertEqual(
            tuple(item.candidate_id for item in decision.evaluations),
            ("candidate-a", "candidate-b"),
        )
        self.assertEqual(
            decision.eligible_candidate_ids,
            ("candidate-a", "candidate-b"),
        )
        self.assertIsNone(decision.integration_plan)

    def test_input_order_does_not_change_decision(self):
        candidates = (candidate_a(), candidate_b())
        verifications = a_verifications() + b_verifications()
        critiques = (critique_a(), critique_b())
        first = evaluate_studio_competition(
            spec(), candidates, verifications, critiques
        )
        second = evaluate_studio_competition(
            spec(),
            tuple(reversed(candidates)),
            tuple(reversed(verifications)),
            tuple(reversed(critiques)),
        )
        self.assertEqual(first, second)

    def test_missing_acceptance_criterion_blocks_candidate(self):
        decision = evaluate_studio_competition(
            spec(),
            (candidate_a(acceptance_criteria=("criterion-api",)),),
            a_verifications(),
            (critique_a(),),
        )
        self.assertEqual(decision.eligible_candidate_ids, ())
        self.assertIn(
            "acceptance:criterion-tests:missing",
            decision.evaluations[0].blockers,
        )

    def test_candidate_base_mismatch_blocks_candidate(self):
        decision = evaluate_studio_competition(
            spec(),
            (candidate_a(base_sha="5" * 40),),
            a_verifications(),
            (critique_a(),),
        )
        self.assertIn("candidate:base_sha_mismatch", decision.evaluations[0].blockers)

    def test_missing_required_verification_blocks(self):
        decision = evaluate_studio_competition(
            spec(),
            (candidate_a(),),
            (verification("candidate-a", HEAD_A, "ci", VERIFY_CI_A),),
            (critique_a(),),
        )
        self.assertIn("verification:unit:missing", decision.evaluations[0].blockers)

    def test_failed_required_verification_blocks(self):
        evidence = (
            verification(
                "candidate-a",
                HEAD_A,
                "ci",
                VERIFY_CI_A,
                outcome=VerificationOutcome.FAILED,
            ),
            verification("candidate-a", HEAD_A, "unit", VERIFY_UNIT_A),
        )
        decision = evaluate_studio_competition(
            spec(), (candidate_a(),), evidence, (critique_a(),)
        )
        self.assertIn("verification:ci:failed", decision.evaluations[0].blockers)

    def test_stale_head_green_verification_has_no_authority(self):
        evidence = (
            verification("candidate-a", OLD_HEAD, "ci", VERIFY_CI_A),
            verification("candidate-a", HEAD_A, "unit", VERIFY_UNIT_A),
        )
        decision = evaluate_studio_competition(
            spec(), (candidate_a(),), evidence, (critique_a(),)
        )
        self.assertIn(
            "verification:ci:head_mismatch", decision.evaluations[0].blockers
        )

    def test_duplicate_required_suite_evidence_fails_closed(self):
        evidence = a_verifications() + (
            verification("candidate-a", OLD_HEAD, "ci", "3" * 64),
        )
        decision = evaluate_studio_competition(
            spec(), (candidate_a(),), evidence, (critique_a(),)
        )
        self.assertIn("verification:ci:duplicate", decision.evaluations[0].blockers)

    def test_extra_unrequired_verification_does_not_gain_authority(self):
        evidence = a_verifications() + (
            verification("candidate-a", OLD_HEAD, "benchmark", "4" * 64),
        )
        decision = evaluate_studio_competition(
            spec(), (candidate_a(),), evidence, (critique_a(),)
        )
        self.assertEqual(decision.eligible_candidate_ids, ("candidate-a",))

    def test_self_critique_does_not_satisfy_independent_policy(self):
        decision = evaluate_studio_competition(
            spec(),
            (candidate_a(),),
            a_verifications(),
            (critique_a(critic_id="producer-a"),),
        )
        self.assertIn(
            "critique:independent_required", decision.evaluations[0].blockers
        )

    def test_open_blocking_critique_blocks_candidate(self):
        decision = evaluate_studio_competition(
            spec(),
            (candidate_a(),),
            a_verifications(),
            (
                critique_a(
                    severity=CritiqueSeverity.BLOCKING,
                    resolution=CritiqueResolution.OPEN,
                ),
            ),
        )
        self.assertIn(
            "critique:finding-a:open_blocking",
            decision.evaluations[0].blockers,
        )

    def test_resolved_and_accepted_risk_blocking_findings_do_not_block(self):
        for resolution in (
            CritiqueResolution.RESOLVED,
            CritiqueResolution.ACCEPTED_RISK,
        ):
            with self.subTest(resolution=resolution):
                decision = evaluate_studio_competition(
                    spec(),
                    (candidate_a(),),
                    a_verifications(),
                    (
                        critique_a(
                            severity=CritiqueSeverity.BLOCKING,
                            resolution=resolution,
                        ),
                    ),
                )
                self.assertEqual(
                    decision.eligible_candidate_ids, ("candidate-a",)
                )

    def test_stale_head_critique_fails_closed(self):
        decision = evaluate_studio_competition(
            spec(),
            (candidate_a(),),
            a_verifications(),
            (critique_a(head_sha=OLD_HEAD),),
        )
        self.assertIn(
            "critique:finding-a:head_mismatch",
            decision.evaluations[0].blockers,
        )
        self.assertIn(
            "critique:independent_required",
            decision.evaluations[0].blockers,
        )

    def test_duplicate_finding_id_fails_closed(self):
        critiques = (
            critique_a(),
            critique_a(critic_id="another-reviewer", digest="5" * 64),
        )
        decision = evaluate_studio_competition(
            spec(), (candidate_a(),), a_verifications(), critiques
        )
        self.assertIn(
            "critique:finding-a:duplicate", decision.evaluations[0].blockers
        )

    def test_unique_candidate_ids_and_branches_are_required(self):
        with self.assertRaises(StudioCompetitionError):
            evaluate_studio_competition(
                spec(),
                (candidate_a(), candidate_a()),
                a_verifications(),
                (critique_a(),),
            )
        with self.assertRaises(StudioCompetitionError):
            evaluate_studio_competition(
                spec(),
                (candidate_a(), candidate_b(branch="studio/candidate-a")),
                a_verifications() + b_verifications(),
                (critique_a(), critique_b()),
            )

    def test_unknown_candidate_evidence_is_rejected(self):
        with self.assertRaises(StudioCompetitionError):
            evaluate_studio_competition(
                spec(),
                (candidate_a(),),
                a_verifications()
                + (verification("candidate-x", HEAD_A, "ci", "6" * 64),),
                (critique_a(),),
            )

    def test_reviewer_selection_must_target_ready_exact_head(self):
        with self.assertRaises(StudioCompetitionError):
            evaluate_studio_competition(
                spec(),
                (candidate_a(),),
                a_verifications(),
                (critique_a(),),
                reviewer_selection=ReviewerSelection(
                    reviewer_id="integrator",
                    candidate_id="candidate-a",
                    head_sha=OLD_HEAD,
                ),
            )
        with self.assertRaises(StudioCompetitionError):
            evaluate_studio_competition(
                spec(),
                (candidate_a(acceptance_criteria=("criterion-api",)),),
                a_verifications(),
                (critique_a(),),
                reviewer_selection=ReviewerSelection(
                    reviewer_id="integrator",
                    candidate_id="candidate-a",
                    head_sha=HEAD_A,
                ),
            )

    def test_independent_critique_can_be_disabled_explicitly(self):
        decision = evaluate_studio_competition(
            spec(independent=False),
            (candidate_a(),),
            a_verifications(),
            (),
        )
        self.assertEqual(decision.eligible_candidate_ids, ("candidate-a",))

    def test_validation_rejects_unsorted_sets_and_malformed_material(self):
        with self.assertRaises(StudioCompetitionError):
            StudioWorkSpec(
                packet_id="M2-M1-031",
                work_id="SKILL-BUILDER-001",
                base_sha=BASE,
                feature_ids=("STUDIO-001", "DEV-004"),
                acceptance_criteria=("criterion-api", "criterion-tests"),
                required_verification_suites=("ci", "unit"),
                require_independent_critique=True,
            )
        with self.assertRaises(StudioCompetitionError):
            candidate_a(head_sha=BASE)
        with self.assertRaises(StudioCompetitionError):
            candidate_a(branch="bad branch")
        with self.assertRaises(StudioCompetitionError):
            verification("candidate-a", HEAD_A, "ci", "not-a-digest")
        with self.assertRaises(StudioCompetitionError):
            VerificationEvidence(
                candidate_id="candidate-a",
                head_sha=HEAD_A,
                suite_id="ci",
                outcome="passed",
                evidence_sha256=VERIFY_CI_A,
            )

    def test_public_contract_has_no_execution_or_private_binding_fields(self):
        forbidden = {
            "hostname",
            "ip",
            "mac",
            "credential",
            "token",
            "model_path",
            "shell",
            "command",
            "runner_label",
            "provider_endpoint",
            "quality_score",
        }
        classes = (
            StudioWorkSpec,
            StudioCandidate,
            VerificationEvidence,
            CritiqueEvidence,
            ReviewerSelection,
            CandidateEvaluation,
            IntegrationPlan,
            StudioCompetitionDecision,
        )
        for cls in classes:
            names = {field.name for field in dataclasses.fields(cls)}
            self.assertTrue(forbidden.isdisjoint(names), (cls.__name__, names))


if __name__ == "__main__":
    unittest.main()
