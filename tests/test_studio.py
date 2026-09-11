import dataclasses
import unittest

from mira.feature_share import build_feature_share_package
from mira.studio import (
    StudioImportSurface,
    StudioNextAction,
    StudioSession,
    StudioSurface,
    StudioSurfaceError,
    StudioSurfacePhase,
    inspect_studio_import,
    project_activation_receipt,
    project_rollback_receipt,
    project_studio_draft,
    review_studio_change,
)
from mira.studio_activation import (
    MutationDisposition,
    StudioActivationReceipt,
    StudioExecutionStatus,
    StudioRollbackReceipt,
    StudioSourceTarget,
)
from mira.studio_competition import (
    ReviewerSelection,
    StudioActivationApproval,
    StudioCandidate,
    StudioChangeContract,
    StudioChangeKind,
    StudioCompetitionError,
    StudioPreviewEvidence,
    StudioRollbackAnchor,
    StudioTestEvidence,
    StudioWorkSpec,
    VerificationEvidence,
    VerificationOutcome,
    evaluate_studio_competition,
)

BASE = "1" * 40
PROPOSED = "2" * 40
APPLIED = "3" * 40
ROLLED = "4" * 40
OTHER_SHA = "5" * 40
SOURCE = "a" * 64
PREVIEW = "b" * 64
UPSTREAM_TEST = "c" * 64
STAGED_TEST = "d" * 64
ROLLBACK_STATE = "e" * 64
ROLLBACK_EVIDENCE = "f" * 64
APPROVAL = "1" * 64
APPLIED_STATE = "2" * 64
ADAPTER_EVIDENCE = "3" * 64
ROLLBACK_ADAPTER_EVIDENCE = "4" * 64


def session(**changes):
    values = dict(
        session_id="session-1",
        packet_id="M2-M1-036",
        work_id="MIRA-STUDIO-001",
        change_id="change-1",
        kind=StudioChangeKind.FEATURE,
        objective="Add one bounded Studio feature with explicit review and activation.",
        feature_ids=("STUDIO-001",),
        dependency_ids=("DEV-004",),
    )
    values.update(changes)
    return StudioSession(**values)


def competition_decision(**candidate_changes):
    spec = StudioWorkSpec(
        packet_id="M2-M1-036",
        work_id="MIRA-STUDIO-001",
        base_sha=BASE,
        feature_ids=("STUDIO-001",),
        acceptance_criteria=("criterion-1",),
        required_verification_suites=("upstream-suite",),
        require_independent_critique=False,
    )
    candidate_values = dict(
        candidate_id="candidate-1",
        producer_id="worker-1",
        branch="work/candidate-1",
        base_sha=BASE,
        head_sha=PROPOSED,
        acceptance_criteria=("criterion-1",),
        source_sha256=SOURCE,
    )
    candidate_values.update(candidate_changes)
    candidate = StudioCandidate(**candidate_values)
    verification = VerificationEvidence(
        candidate_id="candidate-1",
        head_sha=candidate.head_sha,
        suite_id="upstream-suite",
        outcome=VerificationOutcome.PASSED,
        evidence_sha256=UPSTREAM_TEST,
    )
    selection = ReviewerSelection(
        reviewer_id="reviewer-1",
        candidate_id="candidate-1",
        head_sha=candidate.head_sha,
    )
    return evaluate_studio_competition(
        spec,
        (candidate,),
        (verification,),
        (),
        reviewer_selection=selection,
    )


def contract(**changes):
    values = dict(
        change_id="change-1",
        packet_id="M2-M1-036",
        work_id="MIRA-STUDIO-001",
        kind=StudioChangeKind.FEATURE,
        base_sha=BASE,
        proposed_sha=PROPOSED,
        source_sha256=SOURCE,
        feature_ids=("STUDIO-001",),
        declared_contract_ids=("contract-1",),
        required_test_suites=("staged-suite",),
    )
    values.update(changes)
    return StudioChangeContract(**values)


def preview(**changes):
    values = dict(
        change_id="change-1",
        proposed_sha=PROPOSED,
        source_sha256=SOURCE,
        preview_sha256=PREVIEW,
        covered_contract_ids=("contract-1",),
    )
    values.update(changes)
    return StudioPreviewEvidence(**values)


def staged_test(outcome=VerificationOutcome.PASSED, **changes):
    values = dict(
        change_id="change-1",
        proposed_sha=PROPOSED,
        suite_id="staged-suite",
        outcome=outcome,
        evidence_sha256=STAGED_TEST,
    )
    values.update(changes)
    return StudioTestEvidence(**values)


def rollback_anchor(**changes):
    values = dict(
        change_id="change-1",
        base_sha=BASE,
        prior_revision_id="prior-revision-1",
        prior_state_sha256=ROLLBACK_STATE,
        evidence_sha256=ROLLBACK_EVIDENCE,
    )
    values.update(changes)
    return StudioRollbackAnchor(**values)


def approval(**changes):
    values = dict(
        approver_id="operator-1",
        change_id="change-1",
        proposed_sha=PROPOSED,
        preview_sha256=PREVIEW,
        evidence_sha256=APPROVAL,
    )
    values.update(changes)
    return StudioActivationApproval(**values)


def reviewed(*, approved=False, tests=None, preview_value=None, rollback=None):
    return review_studio_change(
        session(),
        competition_decision(),
        contract(),
        preview_value or preview(),
        (staged_test(),) if tests is None else tests,
        rollback_anchor() if rollback is None else rollback,
        approval=approval() if approved else None,
    )


def target():
    return StudioSourceTarget(
        provider_id="source-provider",
        service_id="source-service",
        target_ref="refs/heads/main",
    )


def activation_receipt(status=StudioExecutionStatus.APPLIED, **changes):
    if status == StudioExecutionStatus.APPLIED:
        values = dict(
            status=status,
            reason_code="applied_and_verified",
            packet_id="M2-M1-036",
            work_id="MIRA-STUDIO-001",
            change_id="change-1",
            approver_id="operator-1",
            target=target(),
            base_sha=BASE,
            proposed_sha=PROPOSED,
            approved_source_sha256=SOURCE,
            applied_revision_sha=APPLIED,
            applied_state_sha256=APPLIED_STATE,
            adapter_evidence_sha256=ADAPTER_EVIDENCE,
            mutation_disposition=MutationDisposition.PERFORMED,
        )
    elif status == StudioExecutionStatus.BLOCKED:
        values = dict(
            status=status,
            reason_code="write_capability_denied",
            packet_id="M2-M1-036",
            work_id="MIRA-STUDIO-001",
            change_id="change-1",
            approver_id="operator-1",
            target=target(),
            base_sha=BASE,
            proposed_sha=PROPOSED,
            approved_source_sha256=SOURCE,
            applied_revision_sha=None,
            applied_state_sha256=None,
            adapter_evidence_sha256=None,
            mutation_disposition=MutationDisposition.NOT_ATTEMPTED,
        )
    elif status == StudioExecutionStatus.RECOVERY_REQUIRED:
        values = dict(
            status=status,
            reason_code="activation_write_outcome_unknown",
            packet_id="M2-M1-036",
            work_id="MIRA-STUDIO-001",
            change_id="change-1",
            approver_id="operator-1",
            target=target(),
            base_sha=BASE,
            proposed_sha=PROPOSED,
            approved_source_sha256=SOURCE,
            applied_revision_sha=None,
            applied_state_sha256=None,
            adapter_evidence_sha256=None,
            mutation_disposition=MutationDisposition.UNKNOWN,
        )
    else:
        raise AssertionError("unsupported activation receipt fixture")
    values.update(changes)
    return StudioActivationReceipt(**values)


def rollback_receipt(status=StudioExecutionStatus.ROLLED_BACK, **changes):
    if status == StudioExecutionStatus.ROLLED_BACK:
        values = dict(
            status=status,
            reason_code="rolled_back_and_verified",
            packet_id="M2-M1-036",
            work_id="MIRA-STUDIO-001",
            change_id="change-1",
            target=target(),
            from_revision_sha=APPLIED,
            rollback_revision_id="prior-revision-1",
            rollback_state_sha256=ROLLBACK_STATE,
            resulting_revision_sha=ROLLED,
            adapter_evidence_sha256=ROLLBACK_ADAPTER_EVIDENCE,
            mutation_disposition=MutationDisposition.PERFORMED,
        )
    elif status == StudioExecutionStatus.BLOCKED:
        values = dict(
            status=status,
            reason_code="preflight_revision_mismatch",
            packet_id="M2-M1-036",
            work_id="MIRA-STUDIO-001",
            change_id="change-1",
            target=target(),
            from_revision_sha=APPLIED,
            rollback_revision_id="prior-revision-1",
            rollback_state_sha256=ROLLBACK_STATE,
            resulting_revision_sha=None,
            adapter_evidence_sha256=None,
            mutation_disposition=MutationDisposition.NOT_ATTEMPTED,
        )
    elif status == StudioExecutionStatus.RECOVERY_REQUIRED:
        values = dict(
            status=status,
            reason_code="rollback_write_outcome_unknown",
            packet_id="M2-M1-036",
            work_id="MIRA-STUDIO-001",
            change_id="change-1",
            target=target(),
            from_revision_sha=APPLIED,
            rollback_revision_id="prior-revision-1",
            rollback_state_sha256=ROLLBACK_STATE,
            resulting_revision_sha=None,
            adapter_evidence_sha256=None,
            mutation_disposition=MutationDisposition.UNKNOWN,
        )
    else:
        raise AssertionError("unsupported rollback receipt fixture")
    values.update(changes)
    return StudioRollbackReceipt(**values)


def import_package(*, dependencies=(), min_schema=1, max_schema=3):
    return build_feature_share_package(
        private_owner_id="private-owner-1",
        change_id="CHANGE-1",
        source_revision="revision-1",
        reviewed_source_sha256=SOURCE,
        feature_ids=("STUDIO-001",),
        dependency_ids=dependencies,
        min_runtime_schema=min_schema,
        max_runtime_schema=max_schema,
        artifacts={"mira/example.py": "VALUE = 1\n"},
    ).projection()


class StudioSurfaceTests(unittest.TestCase):
    def test_draft_has_one_non_executing_next_action(self):
        surface = project_studio_draft(session())
        self.assertEqual(surface.phase, StudioSurfacePhase.DRAFT)
        self.assertEqual(
            surface.next_action, StudioNextAction.PROVIDE_REVIEW_EVIDENCE
        )
        self.assertFalse(surface.activation_approved)
        self.assertFalse(surface.activation_verified)
        self.assertFalse(surface.rollback_available)

    def test_review_ready_without_approval_waits_for_explicit_approval(self):
        result = reviewed()
        self.assertTrue(result.decision.review_ready)
        self.assertIsNone(result.activation_plan)
        self.assertEqual(result.surface.phase, StudioSurfacePhase.AWAITING_APPROVAL)
        self.assertEqual(
            result.surface.next_action, StudioNextAction.REVIEW_AND_APPROVE
        )
        self.assertFalse(result.surface.activation_approved)

    def test_exact_approval_produces_ready_to_activate_not_active(self):
        result = reviewed(approved=True)
        self.assertIsNotNone(result.activation_plan)
        self.assertEqual(result.surface.phase, StudioSurfacePhase.READY_TO_ACTIVATE)
        self.assertEqual(
            result.surface.next_action, StudioNextAction.ACTIVATE_APPROVED_CHANGE
        )
        self.assertTrue(result.surface.activation_approved)
        self.assertFalse(result.surface.activation_verified)
        self.assertFalse(result.surface.share_review_available)

    def test_missing_preview_contract_coverage_blocks_review(self):
        result = reviewed(
            preview_value=preview(covered_contract_ids=()),
        )
        self.assertEqual(result.surface.phase, StudioSurfacePhase.REVIEW_BLOCKED)
        self.assertIn("preview:contract:contract-1:missing", result.surface.blockers)
        self.assertEqual(
            result.surface.next_action, StudioNextAction.RESOLVE_REVIEW_BLOCKERS
        )

    def test_failed_required_test_blocks_review(self):
        result = reviewed(tests=(staged_test(VerificationOutcome.FAILED),))
        self.assertEqual(result.surface.phase, StudioSurfacePhase.REVIEW_BLOCKED)
        self.assertIn("test:staged-suite:failed", result.surface.blockers)
        self.assertFalse(result.surface.review_ready)

    def test_session_contract_identity_mismatch_fails_closed(self):
        with self.assertRaises(StudioSurfaceError):
            review_studio_change(
                session(change_id="other-change"),
                competition_decision(),
                contract(),
                preview(),
                (staged_test(),),
                rollback_anchor(),
            )

    def test_stale_approval_cannot_override_exact_preview_binding(self):
        with self.assertRaises(StudioCompetitionError):
            review_studio_change(
                session(),
                competition_decision(),
                contract(),
                preview(),
                (staged_test(),),
                rollback_anchor(),
                approval=approval(preview_sha256="9" * 64),
            )

    def test_applied_activation_becomes_active_with_explicit_rollback_and_share_readiness(self):
        surface = project_activation_receipt(
            reviewed(approved=True), activation_receipt()
        )
        self.assertEqual(surface.phase, StudioSurfacePhase.ACTIVE)
        self.assertEqual(surface.next_action, StudioNextAction.NONE_REQUIRED)
        self.assertTrue(surface.activation_verified)
        self.assertTrue(surface.rollback_available)
        self.assertTrue(surface.share_review_available)

    def test_blocked_activation_does_not_manufacture_success(self):
        surface = project_activation_receipt(
            reviewed(approved=True),
            activation_receipt(StudioExecutionStatus.BLOCKED),
        )
        self.assertEqual(surface.phase, StudioSurfacePhase.ACTIVATION_BLOCKED)
        self.assertEqual(
            surface.next_action, StudioNextAction.RESOLVE_ACTIVATION_BLOCKER
        )
        self.assertFalse(surface.activation_verified)
        self.assertFalse(surface.share_review_available)

    def test_uncertain_activation_requires_reconciliation(self):
        surface = project_activation_receipt(
            reviewed(approved=True),
            activation_receipt(StudioExecutionStatus.RECOVERY_REQUIRED),
        )
        self.assertEqual(
            surface.phase, StudioSurfacePhase.ACTIVATION_RECOVERY_REQUIRED
        )
        self.assertEqual(
            surface.next_action, StudioNextAction.RECONCILE_ACTIVATION_STATE
        )
        self.assertFalse(surface.activation_verified)

    def test_activation_receipt_must_match_exact_approved_source(self):
        with self.assertRaises(StudioSurfaceError):
            project_activation_receipt(
                reviewed(approved=True),
                activation_receipt(approved_source_sha256="9" * 64),
            )

    def test_verified_rollback_projects_rolled_back_state(self):
        review = reviewed(approved=True)
        activation = activation_receipt()
        surface = project_rollback_receipt(
            review,
            activation,
            rollback_receipt(),
        )
        self.assertEqual(surface.phase, StudioSurfacePhase.ROLLED_BACK)
        self.assertFalse(surface.activation_verified)
        self.assertFalse(surface.rollback_available)
        self.assertFalse(surface.share_review_available)

    def test_blocked_rollback_preserves_known_active_state_but_not_share_offer(self):
        review = reviewed(approved=True)
        activation = activation_receipt()
        surface = project_rollback_receipt(
            review,
            activation,
            rollback_receipt(StudioExecutionStatus.BLOCKED),
        )
        self.assertEqual(surface.phase, StudioSurfacePhase.ROLLBACK_BLOCKED)
        self.assertTrue(surface.activation_verified)
        self.assertTrue(surface.rollback_available)
        self.assertFalse(surface.share_review_available)

    def test_uncertain_rollback_requires_reconciliation(self):
        review = reviewed(approved=True)
        activation = activation_receipt()
        surface = project_rollback_receipt(
            review,
            activation,
            rollback_receipt(StudioExecutionStatus.RECOVERY_REQUIRED),
        )
        self.assertEqual(
            surface.phase, StudioSurfacePhase.ROLLBACK_RECOVERY_REQUIRED
        )
        self.assertEqual(
            surface.next_action, StudioNextAction.RECONCILE_ROLLBACK_STATE
        )
        self.assertFalse(surface.activation_verified)
        self.assertFalse(surface.rollback_available)

    def test_rollback_receipt_must_match_exact_activation_target_and_anchor(self):
        review = reviewed(approved=True)
        activation = activation_receipt()
        with self.assertRaises(StudioSurfaceError):
            project_rollback_receipt(
                review,
                activation,
                rollback_receipt(rollback_revision_id="wrong-revision"),
            )

    def test_ready_import_is_review_required_and_never_authorized(self):
        surface = inspect_studio_import(
            import_package(), runtime_schema=2, available_feature_ids=()
        )
        self.assertEqual(
            surface.phase, StudioSurfacePhase.IMPORT_REVIEW_REQUIRED
        )
        self.assertEqual(surface.next_action, StudioNextAction.REVIEW_IMPORT)
        self.assertTrue(surface.ready_for_review)
        self.assertFalse(surface.activation_authorized)
        self.assertFalse(surface.source_mutation_authorized)
        self.assertFalse(surface.install_authorized)

    def test_import_with_missing_dependency_is_blocked_not_installed(self):
        surface = inspect_studio_import(
            import_package(dependencies=("DEV-004",)),
            runtime_schema=2,
            available_feature_ids=(),
        )
        self.assertEqual(surface.phase, StudioSurfacePhase.IMPORT_BLOCKED)
        self.assertEqual(
            surface.next_action, StudioNextAction.RESOLVE_IMPORT_BLOCKERS
        )
        self.assertEqual(surface.missing_dependencies, ("DEV-004",))
        self.assertFalse(surface.ready_for_review)
        self.assertFalse(surface.install_authorized)

    def test_incompatible_import_is_blocked(self):
        surface = inspect_studio_import(
            import_package(min_schema=3, max_schema=4),
            runtime_schema=2,
            available_feature_ids=(),
        )
        self.assertEqual(surface.phase, StudioSurfacePhase.IMPORT_BLOCKED)
        self.assertFalse(surface.compatible)
        self.assertFalse(surface.ready_for_review)

    def test_replay_of_same_evidence_is_deterministic(self):
        first = reviewed(approved=True).surface
        second = reviewed(approved=True).surface
        self.assertEqual(first, second)
        self.assertEqual(first.surface_sha256, second.surface_sha256)

        package = import_package()
        import_first = inspect_studio_import(
            package, runtime_schema=2, available_feature_ids=()
        )
        import_second = inspect_studio_import(
            package, runtime_schema=2, available_feature_ids=()
        )
        self.assertEqual(import_first, import_second)
        self.assertEqual(import_first.surface_sha256, import_second.surface_sha256)

    def test_public_surface_contract_has_no_execution_secret_or_runtime_fields(self):
        forbidden = {
            "credential",
            "token",
            "secret",
            "endpoint",
            "hostname",
            "host",
            "ip_address",
            "mac_address",
            "shell",
            "command",
            "runner_label",
            "model_path",
        }
        for cls in (StudioSession, StudioSurface, StudioImportSurface):
            names = {field.name.lower() for field in dataclasses.fields(cls)}
            self.assertFalse(names & forbidden, (cls.__name__, names & forbidden))

    def test_surface_invariants_reject_verified_activation_without_approval(self):
        draft = project_studio_draft(session())
        values = {
            field.name: getattr(draft, field.name)
            for field in dataclasses.fields(StudioSurface)
        }
        values["activation_verified"] = True
        with self.assertRaises(StudioSurfaceError):
            StudioSurface(**values)


if __name__ == "__main__":
    unittest.main()
