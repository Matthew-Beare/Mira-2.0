import unittest

from mira.feature_registry import parse_registry_bytes
from mira.studio_competition import StudioChangeKind
from mira.studio_intake import (
    StudioIntakeError,
    StudioIntakeNextAction,
    StudioIntakeRequest,
    StudioSemanticInterpretation,
    build_studio_intake,
)


FEATURES = b"""# Test features

## Feature index

- `CORE-001` | Core | required | test | -
- `API-001` | API | required | test | CORE-001
- `APP-001` | App feature | required | test | API-001
- `FLOW-001` | Workflow | required | test | CORE-001
- `PREF-001` | Preference | required | test | CORE-001
"""


def registry():
    return parse_registry_bytes(FEATURES, source_path="FEATURES.md")


def interpretation(
    *,
    kind=StudioChangeKind.FEATURE,
    outcome="Make the capability available from ordinary-language Studio intake.",
    feature_ids=("APP-001",),
    customer_constraints=(),
    assumptions=(),
    unresolved_questions=(),
    constraint_conflicts=(),
    authority_claims=(),
):
    return StudioSemanticInterpretation(
        kind=kind,
        desired_outcome=outcome,
        feature_ids=feature_ids,
        customer_constraints=customer_constraints,
        assumptions=assumptions,
        unresolved_questions=unresolved_questions,
        constraint_conflicts=constraint_conflicts,
        authority_claims=authority_claims,
    )


class StudioIntakeTests(unittest.TestCase):
    def test_feature_intake_is_registry_grounded_and_inert(self):
        request = StudioIntakeRequest(
            "Add a bounded capability I can review before anything changes.",
            ("Do not activate it automatically", "Keep the current data authority"),
        )
        draft = build_studio_intake(
            request,
            interpretation(
                customer_constraints=(
                    "Do not activate it automatically",
                    "Keep the current data authority",
                ),
                assumptions=("A later packet would own implementation",),
            ),
            registry(),
        )

        self.assertEqual(draft.kind, StudioChangeKind.FEATURE)
        self.assertEqual(draft.feature_ids, ("APP-001",))
        self.assertEqual(draft.dependency_ids, ("API-001", "CORE-001"))
        self.assertTrue(draft.review_ready)
        self.assertEqual(draft.next_action, StudioIntakeNextAction.REVIEW_DRAFT)
        self.assertFalse(draft.implementation_authorized)
        self.assertFalse(draft.source_mutation_authorized)
        self.assertFalse(draft.publication_authorized)
        self.assertFalse(draft.install_authorized)
        self.assertFalse(draft.approval_inferred)
        self.assertFalse(draft.activation_authorized)
        self.assertRegex(draft.draft_id, r"^intake-[0-9a-f]{64}$")
        self.assertRegex(draft.projection_sha256, r"^[0-9a-f]{64}$")

    def test_preference_intake_uses_same_boundary(self):
        draft = build_studio_intake(
            StudioIntakeRequest("Prefer concise summaries for this capability."),
            interpretation(
                kind=StudioChangeKind.PREFERENCE,
                outcome="Represent the requested concise-summary preference for review.",
                feature_ids=("PREF-001",),
            ),
            registry(),
        )
        self.assertEqual(draft.kind, StudioChangeKind.PREFERENCE)
        self.assertEqual(draft.dependency_ids, ("CORE-001",))
        self.assertTrue(draft.review_ready)

    def test_workflow_intake_uses_same_boundary(self):
        draft = build_studio_intake(
            StudioIntakeRequest("When evidence arrives, prepare one reviewable workflow draft."),
            interpretation(
                kind=StudioChangeKind.WORKFLOW,
                outcome="Prepare one bounded workflow draft for customer review.",
                feature_ids=("FLOW-001",),
            ),
            registry(),
        )
        self.assertEqual(draft.kind, StudioChangeKind.WORKFLOW)
        self.assertEqual(draft.dependency_ids, ("CORE-001",))

    def test_selected_features_are_not_repeated_as_dependencies(self):
        draft = build_studio_intake(
            StudioIntakeRequest("Draft the feature and its API scope together."),
            interpretation(feature_ids=("API-001", "APP-001")),
            registry(),
        )
        self.assertEqual(draft.feature_ids, ("API-001", "APP-001"))
        self.assertEqual(draft.dependency_ids, ("CORE-001",))

    def test_unresolved_question_blocks_review_with_one_next_action(self):
        draft = build_studio_intake(
            StudioIntakeRequest("Make my brief easier to scan."),
            interpretation(
                feature_ids=("PREF-001",),
                unresolved_questions=("Should the preference apply to every brief?",),
            ),
            registry(),
        )
        self.assertFalse(draft.review_ready)
        self.assertEqual(
            draft.next_action, StudioIntakeNextAction.CLARIFY_WITH_CUSTOMER
        )
        self.assertEqual(
            draft.blockers,
            ("clarification_required:Should the preference apply to every brief?",),
        )

    def test_unknown_feature_scope_fails_closed(self):
        with self.assertRaisesRegex(StudioIntakeError, "unknown feature scope"):
            build_studio_intake(
                StudioIntakeRequest("Add something new."),
                interpretation(feature_ids=("NOPE-001",)),
                registry(),
            )

    def test_customer_constraints_are_normalized_but_not_model_assumptions(self):
        request = StudioIntakeRequest(
            "  Keep   this bounded.  ",
            ("No provider lock-in", "No provider lock-in", "  Preserve state  "),
        )
        draft = build_studio_intake(
            request,
            interpretation(
                feature_ids=("PREF-001",),
                customer_constraints=("No provider lock-in", "Preserve state"),
                assumptions=("Existing feature registry remains authoritative",),
            ),
            registry(),
        )
        self.assertEqual(draft.raw_request, "Keep this bounded.")
        self.assertEqual(
            draft.explicit_constraints, ("No provider lock-in", "Preserve state")
        )
        self.assertEqual(
            draft.assumptions, ("Existing feature registry remains authoritative",)
        )

    def test_interpretation_must_echo_customer_constraints_exactly(self):
        with self.assertRaisesRegex(StudioIntakeError, "preserve explicit customer constraints"):
            build_studio_intake(
                StudioIntakeRequest("Keep it private.", ("No sharing",)),
                interpretation(feature_ids=("PREF-001",), customer_constraints=()),
                registry(),
            )

    def test_assumption_cannot_masquerade_as_customer_constraint(self):
        with self.assertRaisesRegex(StudioIntakeError, "assumptions must remain distinct"):
            build_studio_intake(
                StudioIntakeRequest("Keep it private.", ("No sharing",)),
                interpretation(
                    feature_ids=("PREF-001",),
                    customer_constraints=("No sharing",),
                    assumptions=("No sharing",),
                ),
                registry(),
            )

    def test_reported_constraint_conflict_is_rejected(self):
        with self.assertRaisesRegex(StudioIntakeError, "conflicts with explicit"):
            build_studio_intake(
                StudioIntakeRequest("Do not publish this.", ("No publication",)),
                interpretation(
                    feature_ids=("APP-001",),
                    customer_constraints=("No publication",),
                    constraint_conflicts=("Outcome requires publication",),
                ),
                registry(),
            )

    def test_execution_authority_cannot_be_smuggled_through_intake(self):
        with self.assertRaisesRegex(StudioIntakeError, "cannot accept.*authority"):
            build_studio_intake(
                StudioIntakeRequest("Build this and let me review it."),
                interpretation(
                    authority_claims=("activation approved",),
                ),
                registry(),
            )

    def test_replay_is_deterministic_after_customer_text_normalization(self):
        first = build_studio_intake(
            StudioIntakeRequest(
                "Make this easier to use.",
                ("Keep data local", "No automatic activation"),
            ),
            interpretation(
                kind=StudioChangeKind.PREFERENCE,
                outcome="Represent the usability preference for review.",
                feature_ids=("PREF-001",),
                customer_constraints=("Keep data local", "No automatic activation"),
            ),
            registry(),
        )
        second = build_studio_intake(
            StudioIntakeRequest(
                "  Make   this easier to use.  ",
                ("No automatic activation", "Keep data local", "Keep data local"),
            ),
            interpretation(
                kind=StudioChangeKind.PREFERENCE,
                outcome="Represent the usability preference for review.",
                feature_ids=("PREF-001",),
                customer_constraints=("Keep data local", "No automatic activation"),
            ),
            registry(),
        )
        self.assertEqual(first.draft_id, second.draft_id)
        self.assertEqual(first.projection_sha256, second.projection_sha256)

    def test_material_change_changes_identity(self):
        base = build_studio_intake(
            StudioIntakeRequest("Make this easier to use."),
            interpretation(feature_ids=("PREF-001",)),
            registry(),
        )
        changed = build_studio_intake(
            StudioIntakeRequest("Make this easier to use on mobile."),
            interpretation(feature_ids=("PREF-001",)),
            registry(),
        )
        self.assertNotEqual(base.draft_id, changed.draft_id)

    def test_registry_revision_is_bound_into_identity(self):
        first_registry = registry()
        second_registry = parse_registry_bytes(
            FEATURES + b"\n<!-- evidence-only registry revision -->\n",
            source_path="FEATURES.md",
        )
        request = StudioIntakeRequest("Make this easier to use.")
        semantic = interpretation(feature_ids=("PREF-001",))
        first = build_studio_intake(request, semantic, first_registry)
        second = build_studio_intake(request, semantic, second_registry)
        self.assertNotEqual(first.registry_sha256, second.registry_sha256)
        self.assertNotEqual(first.draft_id, second.draft_id)

    def test_malformed_customer_input_is_rejected(self):
        for raw in ("", "   ", "bad\x00request"):
            with self.subTest(raw=repr(raw)):
                with self.assertRaises(StudioIntakeError):
                    StudioIntakeRequest(raw)
        with self.assertRaisesRegex(StudioIntakeError, "exceeds 8000"):
            StudioIntakeRequest("x" * 8001)

    def test_internal_evidence_must_be_sorted_unique_and_normalized(self):
        bad_feature_sets = (
            ("APP-001", "API-001"),
            ("APP-001", "APP-001"),
            (" APP-001 ",),
        )
        for feature_ids in bad_feature_sets:
            with self.subTest(feature_ids=feature_ids):
                with self.assertRaisesRegex(
                    StudioIntakeError, "normalized, unique, and sorted"
                ):
                    interpretation(feature_ids=feature_ids)

        with self.assertRaisesRegex(
            StudioIntakeError, "normalized, unique, and sorted"
        ):
            interpretation(
                assumptions=("Second assumption", "First assumption"),
            )

    def test_blank_feature_scope_is_rejected(self):
        with self.assertRaisesRegex(StudioIntakeError, "feature_ids must not be empty"):
            interpretation(feature_ids=())


if __name__ == "__main__":
    unittest.main()
