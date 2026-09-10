import dataclasses
import unittest

from mira.studio_competition import (
    CandidateEvaluation,
    IntegrationPlan,
    StudioActivationApproval,
    StudioActivationPlan,
    StudioChangeContract,
    StudioChangeKind,
    StudioCompetitionDecision,
    StudioCompetitionError,
    StudioPreviewEvidence,
    StudioRollbackAnchor,
    StudioStagedChangeDecision,
    StudioTestEvidence,
    VerificationOutcome,
    evaluate_staged_change,
)

BASE = "1" * 40
HEAD = "2" * 40
OLD_HEAD = "3" * 40
SOURCE = "a" * 64
UPSTREAM_VERIFY = "b" * 64
UPSTREAM_CRITIQUE = "c" * 64
PREVIEW = "d" * 64
TEST_CI = "e" * 64
TEST_UNIT = "f" * 64
ROLLBACK_STATE = "1" * 64
ROLLBACK_EVIDENCE = "2" * 64
APPROVAL = "3" * 64


def integration_plan(**changes):
    values = dict(
        reviewer_id="integrator",
        candidate_id="candidate-a",
        producer_id="producer-a",
        branch="studio/candidate-a",
        base_sha=BASE,
        head_sha=HEAD,
        source_sha256=SOURCE,
        verification_evidence_sha256s=(UPSTREAM_VERIFY,),
        critique_evidence_sha256s=(UPSTREAM_CRITIQUE,),
    )
    values.update(changes)
    return IntegrationPlan(**values)


def competition_decision(**changes):
    values = dict(
        packet_id="M2-M1-032",
        work_id="SKILL-BUILDER-001",
        base_sha=BASE,
        feature_ids=("DEV-004", "STUDIO-001"),
        evaluations=(
            CandidateEvaluation(
                candidate_id="candidate-a",
                producer_id="producer-a",
                branch="studio/candidate-a",
                head_sha=HEAD,
                integration_ready=True,
                blockers=(),
                verified_suite_ids=("ci", "unit"),
                critique_finding_ids=("finding-a",),
            ),
        ),
        eligible_candidate_ids=("candidate-a",),
        integration_plan=integration_plan(),
    )
    values.update(changes)
    return StudioCompetitionDecision(**values)


def contract(**changes):
    values = dict(
        change_id="change-a",
        packet_id="M2-M1-032",
        work_id="SKILL-BUILDER-001",
        kind=StudioChangeKind.FEATURE,
        base_sha=BASE,
        proposed_sha=HEAD,
        source_sha256=SOURCE,
        feature_ids=("DEV-004", "STUDIO-001"),
        declared_contract_ids=("contract-api", "contract-rollback"),
        required_test_suites=("ci", "unit"),
    )
    values.update(changes)
    return StudioChangeContract(**values)


def preview(**changes):
    values = dict(
        change_id="change-a",
        proposed_sha=HEAD,
        source_sha256=SOURCE,
        preview_sha256=PREVIEW,
        covered_contract_ids=("contract-api", "contract-rollback"),
    )
    values.update(changes)
    return StudioPreviewEvidence(**values)


def test_evidence(suite_id, digest, **changes):
    values = dict(
        change_id="change-a",
        proposed_sha=HEAD,
        suite_id=suite_id,
        outcome=VerificationOutcome.PASSED,
        evidence_sha256=digest,
    )
    values.update(changes)
    return StudioTestEvidence(**values)


def tests():
    return (
        test_evidence("ci", TEST_CI),
        test_evidence("unit", TEST_UNIT),
    )


def rollback(**changes):
    values = dict(
        change_id="change-a",
        base_sha=BASE,
        prior_revision_id="revision-41",
        prior_state_sha256=ROLLBACK_STATE,
        evidence_sha256=ROLLBACK_EVIDENCE,
    )
    values.update(changes)
    return StudioRollbackAnchor(**values)


def approval(**changes):
    values = dict(
        approver_id="human-reviewer",
        change_id="change-a",
        proposed_sha=HEAD,
        preview_sha256=PREVIEW,
        evidence_sha256=APPROVAL,
    )
    values.update(changes)
    return StudioActivationApproval(**values)


class StudioStagedLifecycleTests(unittest.TestCase):
    def test_complete_evidence_is_review_ready_but_not_silently_approved(self):
        decision = evaluate_staged_change(
            competition_decision(), contract(), preview(), tests(), rollback()
        )
        self.assertIsInstance(decision, StudioStagedChangeDecision)
        self.assertTrue(decision.preview_ready)
        self.assertTrue(decision.review_ready)
        self.assertEqual(decision.blockers, ())
        self.assertEqual(decision.verified_suite_ids, ("ci", "unit"))
        self.assertIsNone(decision.activation_plan)

    def test_explicit_approval_emits_inert_plan_with_exact_provenance(self):
        decision = evaluate_staged_change(
            competition_decision(),
            contract(),
            preview(),
            tests(),
            rollback(),
            approval=approval(),
        )
        plan = decision.activation_plan
        self.assertIsInstance(plan, StudioActivationPlan)
        self.assertEqual(plan.approver_id, "human-reviewer")
        self.assertEqual(plan.change_id, "change-a")
        self.assertEqual(plan.base_sha, BASE)
        self.assertEqual(plan.proposed_sha, HEAD)
        self.assertEqual(plan.source_sha256, SOURCE)
        self.assertEqual(plan.preview_sha256, PREVIEW)
        self.assertEqual(
            plan.upstream_evidence_sha256s,
            tuple(sorted((UPSTREAM_VERIFY, UPSTREAM_CRITIQUE))),
        )
        self.assertEqual(
            plan.test_evidence_sha256s, tuple(sorted((TEST_CI, TEST_UNIT)))
        )
        self.assertEqual(plan.rollback_revision_id, "revision-41")
        self.assertEqual(plan.rollback_state_sha256, ROLLBACK_STATE)
        self.assertEqual(plan.rollback_evidence_sha256, ROLLBACK_EVIDENCE)
        self.assertEqual(plan.approval_evidence_sha256, APPROVAL)

    def test_contract_must_match_reviewed_competition_decision(self):
        with self.assertRaises(StudioCompetitionError):
            evaluate_staged_change(
                competition_decision(),
                contract(base_sha="4" * 40),
                preview(),
                tests(),
                rollback(),
            )
        with self.assertRaises(StudioCompetitionError):
            evaluate_staged_change(
                competition_decision(),
                contract(proposed_sha=OLD_HEAD),
                preview(),
                tests(),
                rollback(),
            )
        with self.assertRaises(StudioCompetitionError):
            evaluate_staged_change(
                competition_decision(),
                contract(source_sha256="4" * 64),
                preview(),
                tests(),
                rollback(),
            )
        with self.assertRaises(StudioCompetitionError):
            evaluate_staged_change(
                competition_decision(),
                contract(packet_id="M2-M1-999"),
                preview(),
                tests(),
                rollback(),
            )
        with self.assertRaises(StudioCompetitionError):
            evaluate_staged_change(
                competition_decision(),
                contract(work_id="OTHER-WORK-001"),
                preview(),
                tests(),
                rollback(),
            )
        with self.assertRaises(StudioCompetitionError):
            evaluate_staged_change(
                competition_decision(),
                contract(feature_ids=("DEV-004",)),
                preview(),
                tests(),
                rollback(),
            )
        with self.assertRaises(StudioCompetitionError):
            evaluate_staged_change(
                competition_decision(integration_plan=None),
                contract(),
                preview(),
                tests(),
                rollback(),
            )
        with self.assertRaises(StudioCompetitionError):
            evaluate_staged_change(
                competition_decision(
                    integration_plan=integration_plan(producer_id="producer-b")
                ),
                contract(),
                preview(),
                tests(),
                rollback(),
            )

    def test_missing_preview_contract_coverage_blocks_review(self):
        decision = evaluate_staged_change(
            competition_decision(),
            contract(),
            preview(covered_contract_ids=("contract-api",)),
            tests(),
            rollback(),
        )
        self.assertFalse(decision.preview_ready)
        self.assertFalse(decision.review_ready)
        self.assertIn(
            "preview:contract:contract-rollback:missing", decision.blockers
        )

    def test_extra_preview_contract_does_not_gain_authority(self):
        decision = evaluate_staged_change(
            competition_decision(),
            contract(),
            preview(
                covered_contract_ids=(
                    "contract-api",
                    "contract-extra",
                    "contract-rollback",
                )
            ),
            tests(),
            rollback(),
        )
        self.assertTrue(decision.review_ready)

    def test_preview_must_bind_exact_change_head_and_source(self):
        for changed_preview, expected in (
            (preview(change_id="change-b"), "preview:change_mismatch"),
            (preview(proposed_sha=OLD_HEAD), "preview:head_mismatch"),
            (preview(source_sha256="5" * 64), "preview:source_mismatch"),
        ):
            with self.subTest(expected=expected):
                decision = evaluate_staged_change(
                    competition_decision(), contract(), changed_preview, tests(), rollback()
                )
                self.assertIn(expected, decision.blockers)

    def test_required_tests_fail_closed_for_missing_failed_stale_and_duplicate(self):
        cases = (
            (
                (test_evidence("ci", TEST_CI),),
                "test:unit:missing",
            ),
            (
                (
                    test_evidence("ci", TEST_CI, outcome=VerificationOutcome.FAILED),
                    test_evidence("unit", TEST_UNIT),
                ),
                "test:ci:failed",
            ),
            (
                (
                    test_evidence("ci", TEST_CI, proposed_sha=OLD_HEAD),
                    test_evidence("unit", TEST_UNIT),
                ),
                "test:ci:head_mismatch",
            ),
            (
                tests() + (test_evidence("ci", "6" * 64),),
                "test:ci:duplicate",
            ),
        )
        for evidence, expected in cases:
            with self.subTest(expected=expected):
                decision = evaluate_staged_change(
                    competition_decision(), contract(), preview(), evidence, rollback()
                )
                self.assertFalse(decision.review_ready)
                self.assertIn(expected, decision.blockers)

    def test_extra_unrequired_test_is_excluded_from_activation_authority(self):
        extra_digest = "7" * 64
        evidence = tests() + (
            test_evidence("benchmark", extra_digest, proposed_sha=OLD_HEAD),
        )
        decision = evaluate_staged_change(
            competition_decision(),
            contract(),
            preview(),
            evidence,
            rollback(),
            approval=approval(),
        )
        self.assertNotIn(extra_digest, decision.activation_plan.test_evidence_sha256s)

    def test_test_evidence_for_another_change_is_rejected(self):
        with self.assertRaises(StudioCompetitionError):
            evaluate_staged_change(
                competition_decision(),
                contract(),
                preview(),
                tests() + (test_evidence("benchmark", "8" * 64, change_id="change-b"),),
                rollback(),
            )

    def test_rollback_is_mandatory_and_bound_to_change_and_base(self):
        decision = evaluate_staged_change(
            competition_decision(), contract(), preview(), tests(), None
        )
        self.assertIn("rollback:missing", decision.blockers)
        self.assertFalse(decision.review_ready)

        decision = evaluate_staged_change(
            competition_decision(),
            contract(),
            preview(),
            tests(),
            rollback(change_id="change-b", base_sha="4" * 40),
        )
        self.assertIn("rollback:change_mismatch", decision.blockers)
        self.assertIn("rollback:base_mismatch", decision.blockers)

    def test_approval_cannot_override_blockers(self):
        with self.assertRaises(StudioCompetitionError):
            evaluate_staged_change(
                competition_decision(),
                contract(),
                preview(covered_contract_ids=("contract-api",)),
                tests(),
                rollback(),
                approval=approval(),
            )

    def test_approval_must_target_exact_change_head_and_preview(self):
        for changed_approval in (
            approval(change_id="change-b"),
            approval(proposed_sha=OLD_HEAD),
            approval(preview_sha256="9" * 64),
        ):
            with self.subTest(approval=changed_approval):
                with self.assertRaises(StudioCompetitionError):
                    evaluate_staged_change(
                        competition_decision(),
                        contract(),
                        preview(),
                        tests(),
                        rollback(),
                        approval=changed_approval,
                    )

    def test_test_input_order_does_not_change_decision(self):
        first = evaluate_staged_change(
            competition_decision(), contract(), preview(), tests(), rollback()
        )
        second = evaluate_staged_change(
            competition_decision(),
            contract(),
            preview(),
            tuple(reversed(tests())),
            rollback(),
        )
        self.assertEqual(first, second)

    def test_contract_validation_rejects_unsorted_or_malformed_material(self):
        with self.assertRaises(StudioCompetitionError):
            contract(feature_ids=("STUDIO-001", "DEV-004"))
        with self.assertRaises(StudioCompetitionError):
            contract(proposed_sha=BASE)
        with self.assertRaises(StudioCompetitionError):
            contract(kind="feature")
        with self.assertRaises(StudioCompetitionError):
            preview(preview_sha256="not-a-digest")
        with self.assertRaises(StudioCompetitionError):
            rollback(prior_revision_id="bad revision")

    def test_public_contracts_contain_no_execution_or_private_binding_fields(self):
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
            "activate",
            "execute",
        }
        classes = (
            StudioChangeContract,
            StudioPreviewEvidence,
            StudioTestEvidence,
            StudioRollbackAnchor,
            StudioActivationApproval,
            StudioActivationPlan,
            StudioStagedChangeDecision,
        )
        for cls in classes:
            names = {field.name for field in dataclasses.fields(cls)}
            self.assertTrue(forbidden.isdisjoint(names), (cls.__name__, names))


if __name__ == "__main__":
    unittest.main()
