from __future__ import annotations

from dataclasses import replace
import hashlib
import unittest

from mira.feature_registry import FeatureRecord, FeatureRegistry
from mira.studio_competition import StudioChangeKind
from mira.studio_intake import (
    ConstraintPolarity,
    StudioConstraint,
    StudioIntakeError,
    StudioIntakeInterpretation,
    StudioIntakeNextAction,
    draft_studio_intake,
    interpretation_from_mapping,
)


REGISTRY_SHA = hashlib.sha256(b"canonical-features").hexdigest()


def registry() -> FeatureRegistry:
    return FeatureRegistry(
        source_path="FEATURES.md",
        source_sha256=REGISTRY_SHA,
        features=(
            FeatureRecord(
                feature_id="DEV-001",
                title="Git discipline",
                requirement="Use reviewed Git-backed changes.",
                evidence="specified",
                dependencies=(),
            ),
            FeatureRecord(
                feature_id="DEV-004",
                title="Bounded custom features",
                requirement="Create bounded private features.",
                evidence="specified",
                dependencies=("DEV-001",),
            ),
            FeatureRecord(
                feature_id="DIST-001",
                title="Feature distribution",
                requirement="Share sanitized improvements safely.",
                evidence="specified",
                dependencies=(),
            ),
            FeatureRecord(
                feature_id="STUDIO-001",
                title="MIRA Studio",
                requirement="Guide continuous MIRA improvement.",
                evidence="specified",
                dependencies=("DEV-004", "DIST-001"),
            ),
            FeatureRecord(
                feature_id="TASK-001",
                title="Canonical tasks",
                requirement="Track durable tasks.",
                evidence="specified",
                dependencies=(),
            ),
        ),
    )


def interpretation(
    *,
    kind: StudioChangeKind = StudioChangeKind.FEATURE,
    outcome: str = "Let MIRA turn ordinary language into a bounded Studio draft.",
    features: tuple[str, ...] = ("STUDIO-001",),
    assumptions: tuple[str, ...] = (),
    questions: tuple[str, ...] = (),
) -> StudioIntakeInterpretation:
    return StudioIntakeInterpretation(
        kind=kind,
        desired_outcome=outcome,
        feature_ids=features,
        assumptions=assumptions,
        material_questions=questions,
    )


def draft(**overrides):
    args = {
        "user_request": "Make Studio understand what I want without making me know Git.",
        "explicit_constraints": (),
        "interpretation": interpretation(),
        "registry": registry(),
    }
    args.update(overrides)
    return draft_studio_intake(**args)


class StudioIntakeTests(unittest.TestCase):
    def test_feature_intake_ready_for_review(self):
        result = draft()
        self.assertEqual(result.kind, StudioChangeKind.FEATURE)
        self.assertTrue(result.review_ready)
        self.assertEqual(result.next_action, StudioIntakeNextAction.REVIEW_DRAFT)
        self.assertEqual(result.feature_ids, ("STUDIO-001",))
        self.assertEqual(
            result.dependency_ids, ("DEV-001", "DEV-004", "DIST-001")
        )

    def test_preference_intake_ready_for_review(self):
        result = draft(
            user_request="I want MIRA to keep replies shorter by default.",
            interpretation=interpretation(
                kind=StudioChangeKind.PREFERENCE,
                outcome="Prefer concise replies unless detail is requested.",
            ),
        )
        self.assertEqual(result.kind, StudioChangeKind.PREFERENCE)
        self.assertTrue(result.review_ready)

    def test_workflow_intake_ready_for_review(self):
        result = draft(
            user_request="When I finish a trip, reconcile the mileage before the brief.",
            interpretation=interpretation(
                kind=StudioChangeKind.WORKFLOW,
                outcome="Reconcile completed-trip mileage before rendering a brief.",
                features=("TASK-001",),
            ),
        )
        self.assertEqual(result.kind, StudioChangeKind.WORKFLOW)
        self.assertEqual(result.dependency_ids, ())
        self.assertTrue(result.review_ready)

    def test_dependency_closure_is_transitive_and_excludes_selected_features(self):
        result = draft(
            interpretation=interpretation(features=("DEV-004", "STUDIO-001"))
        )
        self.assertEqual(result.feature_ids, ("DEV-004", "STUDIO-001"))
        self.assertEqual(result.dependency_ids, ("DEV-001", "DIST-001"))

    def test_empty_feature_scope_blocks_and_adds_plain_language_question(self):
        result = draft(interpretation=interpretation(features=()))
        self.assertFalse(result.review_ready)
        self.assertEqual(result.next_action, StudioIntakeNextAction.CLARIFY_INTENT)
        self.assertEqual(
            result.blockers,
            ("feature_scope_unresolved", "material_clarification_required"),
        )
        self.assertIn("What part of MIRA should this change affect?", result.material_questions)

    def test_material_question_blocks_review(self):
        result = draft(
            interpretation=interpretation(
                questions=("Should this happen automatically or only when asked?",)
            )
        )
        self.assertFalse(result.review_ready)
        self.assertEqual(result.blockers, ("material_clarification_required",))

    def test_assumptions_do_not_silently_become_constraints_or_block(self):
        result = draft(
            interpretation=interpretation(
                assumptions=("Assume the existing Studio review flow remains canonical.",)
            )
        )
        self.assertTrue(result.review_ready)
        self.assertEqual(result.explicit_constraints, ())
        self.assertEqual(
            result.assumptions,
            ("Assume the existing Studio review flow remains canonical.",),
        )

    def test_explicit_customer_constraints_are_preserved_separately(self):
        constraints = (
            StudioConstraint("Do not send messages automatically", ConstraintPolarity.FORBID),
            StudioConstraint("Keep the no-app path usable", ConstraintPolarity.REQUIRE),
        )
        result = draft(explicit_constraints=constraints)
        self.assertEqual(result.explicit_constraints, constraints)
        self.assertEqual(result.assumptions, ())

    def test_constraints_must_be_canonically_sorted(self):
        constraints = (
            StudioConstraint("Keep the no-app path usable", ConstraintPolarity.REQUIRE),
            StudioConstraint("Do not send messages automatically", ConstraintPolarity.FORBID),
        )
        with self.assertRaisesRegex(StudioIntakeError, "canonically sorted"):
            draft(explicit_constraints=constraints)

    def test_duplicate_constraints_fail_closed(self):
        value = StudioConstraint("Keep the no-app path usable")
        with self.assertRaisesRegex(StudioIntakeError, "duplicates"):
            draft(explicit_constraints=(value, value))

    def test_opposing_constraints_fail_closed(self):
        constraints = (
            StudioConstraint("Automatically send mail", ConstraintPolarity.FORBID),
            StudioConstraint("Automatically send mail", ConstraintPolarity.REQUIRE),
        )
        with self.assertRaisesRegex(StudioIntakeError, "contradictory"):
            draft(explicit_constraints=constraints)

    def test_unknown_feature_id_fails_closed(self):
        with self.assertRaisesRegex(StudioIntakeError, "unknown feature IDs"):
            draft(interpretation=interpretation(features=("BOGUS-001",)))

    def test_unsorted_interpreted_feature_ids_fail_closed(self):
        with self.assertRaisesRegex(StudioIntakeError, "feature_ids must be sorted"):
            interpretation(features=("STUDIO-001", "DEV-004"))

    def test_duplicate_interpreted_feature_ids_fail_closed(self):
        with self.assertRaisesRegex(StudioIntakeError, "feature_ids contains duplicates"):
            interpretation(features=("STUDIO-001", "STUDIO-001"))

    def test_unsorted_assumptions_fail_closed(self):
        with self.assertRaisesRegex(StudioIntakeError, "assumptions must be sorted"):
            interpretation(assumptions=("z assumption", "a assumption"))

    def test_blank_request_fails_closed(self):
        with self.assertRaisesRegex(StudioIntakeError, "user_request must not be blank"):
            draft(user_request="   ")

    def test_oversized_request_fails_closed(self):
        with self.assertRaisesRegex(StudioIntakeError, "user_request is too long"):
            draft(user_request="x" * 4001)

    def test_control_character_request_fails_closed(self):
        with self.assertRaisesRegex(StudioIntakeError, "control characters"):
            draft(user_request="normal\x00evil")

    def test_identical_evidence_yields_identical_draft_identity(self):
        first = draft()
        second = draft()
        self.assertEqual(first.draft_id, second.draft_id)
        self.assertEqual(first.canonical_bytes(), second.canonical_bytes())

    def test_changed_user_request_changes_draft_identity(self):
        first = draft()
        second = draft(user_request="Make Studio easier for a normal person to use.")
        self.assertNotEqual(first.draft_id, second.draft_id)

    def test_changed_interpretation_changes_draft_identity(self):
        first = draft()
        second = draft(
            interpretation=interpretation(
                outcome="Make Studio intake concise and deterministic."
            )
        )
        self.assertNotEqual(first.draft_id, second.draft_id)

    def test_mapping_parser_accepts_exact_untrusted_schema(self):
        parsed = interpretation_from_mapping(
            {
                "kind": "workflow",
                "desired_outcome": "Create one bounded workflow draft.",
                "feature_ids": ["STUDIO-001"],
                "assumptions": [],
                "material_questions": [],
            }
        )
        self.assertEqual(parsed.kind, StudioChangeKind.WORKFLOW)

    def test_mapping_parser_rejects_execution_authority_smuggling(self):
        material = {
            "kind": "feature",
            "desired_outcome": "Create one bounded feature draft.",
            "feature_ids": ["STUDIO-001"],
            "assumptions": [],
            "material_questions": [],
            "activation_authorized": True,
        }
        with self.assertRaisesRegex(StudioIntakeError, "authority fields"):
            interpretation_from_mapping(material)

    def test_mapping_parser_rejects_internal_packet_identity_smuggling(self):
        material = {
            "kind": "feature",
            "desired_outcome": "Create one bounded feature draft.",
            "feature_ids": ["STUDIO-001"],
            "assumptions": [],
            "material_questions": [],
            "packet_id": "M2-EVIL-999",
        }
        with self.assertRaisesRegex(StudioIntakeError, "authority fields"):
            interpretation_from_mapping(material)

    def test_mapping_parser_rejects_invalid_kind(self):
        with self.assertRaisesRegex(StudioIntakeError, "kind is invalid"):
            interpretation_from_mapping(
                {
                    "kind": "magic",
                    "desired_outcome": "Do magic.",
                    "feature_ids": ["STUDIO-001"],
                    "assumptions": [],
                    "material_questions": [],
                }
            )

    def test_mapping_parser_requires_json_lists(self):
        with self.assertRaisesRegex(StudioIntakeError, "feature_ids must be a JSON list"):
            interpretation_from_mapping(
                {
                    "kind": "feature",
                    "desired_outcome": "Create one bounded feature draft.",
                    "feature_ids": ("STUDIO-001",),
                    "assumptions": [],
                    "material_questions": [],
                }
            )

    def test_intake_never_grants_execution_authority(self):
        result = draft()
        self.assertFalse(result.implementation_authorized)
        self.assertFalse(result.source_mutation_authorized)
        self.assertFalse(result.activation_authorized)
        self.assertFalse(result.share_publication_authorized)
        self.assertFalse(result.install_authorized)

    def test_draft_rejects_authority_flip_even_after_construction(self):
        result = draft()
        with self.assertRaisesRegex(StudioIntakeError, "cannot grant activation_authorized"):
            replace(result, activation_authorized=True)

    def test_registry_unknown_dependency_fails_closed(self):
        broken = registry()
        broken = replace(
            broken,
            features=broken.features
            + (
                FeatureRecord(
                    feature_id="TASK-002",
                    title="Broken",
                    requirement="Broken dependency for test.",
                    evidence="specified",
                    dependencies=("UNKNOWN-001",),
                ),
            ),
        )
        with self.assertRaisesRegex(StudioIntakeError, "unknown feature ID UNKNOWN-001"):
            draft(
                interpretation=interpretation(features=("TASK-002",)),
                registry=broken,
            )

    def test_registry_bad_digest_fails_closed(self):
        broken = replace(registry(), source_sha256="not-a-digest")
        with self.assertRaisesRegex(StudioIntakeError, "registry source_sha256"):
            draft(registry=broken)


if __name__ == "__main__":
    unittest.main()
