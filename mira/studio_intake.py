"""Deterministic ordinary-language intake boundary for MIRA Studio.

A customer supplies ordinary-language intent. A host/model may propose a semantic
interpretation of that intent, but this module is the deterministic authority for
validating that interpretation against the exact feature registry, deriving feature
dependencies, separating explicit customer constraints from assistant assumptions,
generating stable intake identity, and deciding whether the draft is ready for
customer review.

This module does not invoke a model, create implementation packets or Git branches,
mutate source/provider state, publish or install feature shares, approve changes, or
activate behavior.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
import re
from typing import Any, Mapping, Sequence

from .feature_registry import FeatureRecord, FeatureRegistry
from .studio_competition import StudioChangeKind


class StudioIntakeError(ValueError):
    """Raised when Studio intake material is malformed, unsafe, or contradictory."""


class ConstraintPolarity(str, Enum):
    REQUIRE = "require"
    FORBID = "forbid"


class StudioIntakeNextAction(str, Enum):
    CLARIFY_INTENT = "clarify_intent"
    REVIEW_DRAFT = "review_draft"


_TEXT_CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_FEATURE_ID_RE = re.compile(r"^[A-Z][A-Z0-9-]{1,79}$")
_DIGEST_RE = re.compile(r"^[0-9a-f]{64}$")
_MAX_REQUEST = 4000
_MAX_OUTCOME = 1200
_MAX_TEXT_ITEM = 1000
_MAX_ITEMS = 32
_INTERPRETATION_FIELDS = frozenset(
    {"kind", "desired_outcome", "feature_ids", "assumptions", "material_questions"}
)
_FORBIDDEN_AUTHORITY_FIELDS = frozenset(
    {
        "approved",
        "approval",
        "activate",
        "activation",
        "activation_authorized",
        "implementation_authorized",
        "source_mutation_authorized",
        "publication_authorized",
        "share_publication_authorized",
        "install_authorized",
        "provider_capability",
        "remote_readback",
        "packet_id",
        "work_id",
        "change_id",
        "branch",
        "provider",
        "model",
    }
)


@dataclass(frozen=True)
class StudioConstraint:
    """One explicit customer-stated constraint extracted from the conversation."""

    text: str
    polarity: ConstraintPolarity = ConstraintPolarity.REQUIRE

    def __post_init__(self) -> None:
        _bounded_text(self.text, "constraint text", max_length=_MAX_TEXT_ITEM)
        if not isinstance(self.polarity, ConstraintPolarity):
            raise StudioIntakeError("constraint polarity must be a ConstraintPolarity")

    @property
    def canonical_key(self) -> tuple[str, str]:
        return (self.normalized_text, self.polarity.value)

    @property
    def normalized_text(self) -> str:
        return _normalize_space(self.text).casefold()

    def projection(self) -> dict[str, str]:
        return {"text": _normalize_space(self.text), "polarity": self.polarity.value}


@dataclass(frozen=True)
class StudioIntakeInterpretation:
    """Host/model-proposed semantics that deterministic MIRA independently validates."""

    kind: StudioChangeKind
    desired_outcome: str
    feature_ids: tuple[str, ...]
    assumptions: tuple[str, ...] = ()
    material_questions: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.kind, StudioChangeKind):
            raise StudioIntakeError("kind must be a StudioChangeKind")
        _bounded_text(self.desired_outcome, "desired_outcome", max_length=_MAX_OUTCOME)
        _sorted_feature_ids(self.feature_ids, "feature_ids", allow_empty=True)
        _sorted_text_items(self.assumptions, "assumptions")
        _sorted_text_items(self.material_questions, "material_questions")

    def projection(self) -> dict[str, object]:
        return {
            "kind": self.kind.value,
            "desired_outcome": _normalize_space(self.desired_outcome),
            "feature_ids": list(self.feature_ids),
            "assumptions": [_normalize_space(item) for item in self.assumptions],
            "material_questions": [
                _normalize_space(item) for item in self.material_questions
            ],
        }


@dataclass(frozen=True)
class StudioIntakeDraft:
    """Bounded reviewable Studio draft with no implementation/execution authority."""

    draft_id: str
    registry_sha256: str
    kind: StudioChangeKind
    user_request: str
    desired_outcome: str
    explicit_constraints: tuple[StudioConstraint, ...]
    assumptions: tuple[str, ...]
    feature_ids: tuple[str, ...]
    dependency_ids: tuple[str, ...]
    blockers: tuple[str, ...]
    material_questions: tuple[str, ...]
    review_ready: bool
    next_action: StudioIntakeNextAction
    implementation_authorized: bool = False
    source_mutation_authorized: bool = False
    activation_authorized: bool = False
    share_publication_authorized: bool = False
    install_authorized: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.draft_id, str) or not re.fullmatch(
            r"studio-intake-[0-9a-f]{24}", self.draft_id
        ):
            raise StudioIntakeError("draft_id must be a generated Studio intake ID")
        _digest(self.registry_sha256, "registry_sha256")
        if not isinstance(self.kind, StudioChangeKind):
            raise StudioIntakeError("kind must be a StudioChangeKind")
        _bounded_text(self.user_request, "user_request", max_length=_MAX_REQUEST)
        _bounded_text(self.desired_outcome, "desired_outcome", max_length=_MAX_OUTCOME)
        _validated_constraints(self.explicit_constraints)
        _sorted_text_items(self.assumptions, "assumptions")
        _sorted_feature_ids(self.feature_ids, "feature_ids", allow_empty=True)
        _sorted_feature_ids(self.dependency_ids, "dependency_ids", allow_empty=True)
        if set(self.feature_ids) & set(self.dependency_ids):
            raise StudioIntakeError("feature_ids and dependency_ids must be disjoint")
        _sorted_machine_tokens(self.blockers, "blockers")
        _sorted_text_items(self.material_questions, "material_questions")
        if not isinstance(self.review_ready, bool):
            raise StudioIntakeError("review_ready must be boolean")
        if not isinstance(self.next_action, StudioIntakeNextAction):
            raise StudioIntakeError("next_action must be a StudioIntakeNextAction")
        if self.review_ready != (not self.blockers):
            raise StudioIntakeError("review_ready must exactly reflect blocker absence")
        expected_action = (
            StudioIntakeNextAction.REVIEW_DRAFT
            if self.review_ready
            else StudioIntakeNextAction.CLARIFY_INTENT
        )
        if self.next_action is not expected_action:
            raise StudioIntakeError("next_action does not match review readiness")
        for field, value in (
            ("implementation_authorized", self.implementation_authorized),
            ("source_mutation_authorized", self.source_mutation_authorized),
            ("activation_authorized", self.activation_authorized),
            ("share_publication_authorized", self.share_publication_authorized),
            ("install_authorized", self.install_authorized),
        ):
            if value is not False:
                raise StudioIntakeError(f"intake cannot grant {field}")

    def projection(self) -> dict[str, object]:
        return {
            "draft_id": self.draft_id,
            "registry_sha256": self.registry_sha256,
            "kind": self.kind.value,
            "user_request": _normalize_space(self.user_request),
            "desired_outcome": _normalize_space(self.desired_outcome),
            "explicit_constraints": [
                constraint.projection() for constraint in self.explicit_constraints
            ],
            "assumptions": [_normalize_space(item) for item in self.assumptions],
            "feature_ids": list(self.feature_ids),
            "dependency_ids": list(self.dependency_ids),
            "blockers": list(self.blockers),
            "material_questions": [
                _normalize_space(item) for item in self.material_questions
            ],
            "review_ready": self.review_ready,
            "next_action": self.next_action.value,
            "implementation_authorized": False,
            "source_mutation_authorized": False,
            "activation_authorized": False,
            "share_publication_authorized": False,
            "install_authorized": False,
        }

    def canonical_bytes(self) -> bytes:
        return _canonical_json(self.projection()) + b"\n"


def interpretation_from_mapping(material: Mapping[str, Any]) -> StudioIntakeInterpretation:
    """Parse untrusted host/model interpretation without accepting execution authority."""

    if not isinstance(material, Mapping):
        raise StudioIntakeError("interpretation must be an object")
    forbidden = sorted(set(material) & _FORBIDDEN_AUTHORITY_FIELDS)
    if forbidden:
        raise StudioIntakeError(
            "interpretation attempts to supply internal/execution authority fields: "
            + ", ".join(forbidden)
        )
    if set(material) != _INTERPRETATION_FIELDS:
        raise StudioIntakeError("interpretation fields do not match schema")
    try:
        kind = StudioChangeKind(material["kind"])
    except (TypeError, ValueError) as exc:
        raise StudioIntakeError("interpretation kind is invalid") from exc
    feature_ids = _tuple_of_strings(material["feature_ids"], "feature_ids")
    assumptions = _tuple_of_strings(material["assumptions"], "assumptions")
    questions = _tuple_of_strings(
        material["material_questions"], "material_questions"
    )
    return StudioIntakeInterpretation(
        kind=kind,
        desired_outcome=material["desired_outcome"],
        feature_ids=feature_ids,
        assumptions=assumptions,
        material_questions=questions,
    )


def draft_studio_intake(
    *,
    user_request: str,
    explicit_constraints: Sequence[StudioConstraint],
    interpretation: StudioIntakeInterpretation | Mapping[str, Any],
    registry: FeatureRegistry,
) -> StudioIntakeDraft:
    """Build one deterministic registry-grounded draft from customer intent evidence."""

    request = _bounded_text(user_request, "user_request", max_length=_MAX_REQUEST)
    constraints = _validated_constraints(tuple(explicit_constraints))
    semantic = (
        interpretation_from_mapping(interpretation)
        if isinstance(interpretation, Mapping)
        else interpretation
    )
    if not isinstance(semantic, StudioIntakeInterpretation):
        raise StudioIntakeError(
            "interpretation must be StudioIntakeInterpretation or a mapping"
        )
    _validate_registry(registry)
    feature_map = registry.feature_map()
    unknown = tuple(fid for fid in semantic.feature_ids if fid not in feature_map)
    if unknown:
        raise StudioIntakeError(
            "interpretation references unknown feature IDs: " + ", ".join(unknown)
        )

    dependencies = _derive_dependency_closure(
        feature_map=feature_map,
        selected_feature_ids=semantic.feature_ids,
    )

    questions = list(semantic.material_questions)
    blockers: list[str] = []
    if not semantic.feature_ids:
        blockers.append("feature_scope_unresolved")
        default_question = "What part of MIRA should this change affect?"
        if default_question not in questions:
            questions.append(default_question)
    if questions:
        blockers.append("material_clarification_required")
    questions_tuple = tuple(sorted(questions))
    blockers_tuple = tuple(sorted(set(blockers)))

    identity_material = {
        "registry_sha256": registry.source_sha256,
        "kind": semantic.kind.value,
        "user_request": request,
        "desired_outcome": _normalize_space(semantic.desired_outcome),
        "explicit_constraints": [c.projection() for c in constraints],
        "assumptions": [_normalize_space(item) for item in semantic.assumptions],
        "feature_ids": list(semantic.feature_ids),
        "dependency_ids": list(dependencies),
        "blockers": list(blockers_tuple),
        "material_questions": [_normalize_space(item) for item in questions_tuple],
    }
    digest = hashlib.sha256(_canonical_json(identity_material)).hexdigest()
    draft_id = f"studio-intake-{digest[:24]}"
    ready = not blockers_tuple

    return StudioIntakeDraft(
        draft_id=draft_id,
        registry_sha256=registry.source_sha256,
        kind=semantic.kind,
        user_request=request,
        desired_outcome=_normalize_space(semantic.desired_outcome),
        explicit_constraints=constraints,
        assumptions=semantic.assumptions,
        feature_ids=semantic.feature_ids,
        dependency_ids=dependencies,
        blockers=blockers_tuple,
        material_questions=questions_tuple,
        review_ready=ready,
        next_action=(
            StudioIntakeNextAction.REVIEW_DRAFT
            if ready
            else StudioIntakeNextAction.CLARIFY_INTENT
        ),
    )


def _derive_dependency_closure(
    *,
    feature_map: Mapping[str, FeatureRecord],
    selected_feature_ids: Sequence[str],
) -> tuple[str, ...]:
    selected = set(selected_feature_ids)
    discovered: set[str] = set()
    visiting: set[str] = set()

    def visit(feature_id: str) -> None:
        if feature_id in visiting:
            raise StudioIntakeError("feature registry contains a dependency cycle")
        record = feature_map.get(feature_id)
        if record is None:
            raise StudioIntakeError(
                f"feature registry dependency references unknown feature ID {feature_id}"
            )
        visiting.add(feature_id)
        for dependency in record.dependencies:
            if dependency not in feature_map:
                raise StudioIntakeError(
                    "feature registry dependency references unknown feature ID "
                    + dependency
                )
            if dependency not in selected:
                discovered.add(dependency)
            visit(dependency)
        visiting.remove(feature_id)

    for feature_id in selected_feature_ids:
        visit(feature_id)
    return tuple(sorted(discovered - selected))


def _validate_registry(registry: FeatureRegistry) -> None:
    if not isinstance(registry, FeatureRegistry):
        raise StudioIntakeError("registry must be a FeatureRegistry")
    _digest(registry.source_sha256, "registry source_sha256")
    if not registry.features:
        raise StudioIntakeError("registry must contain at least one feature")
    feature_map = registry.feature_map()
    if len(feature_map) != len(registry.features):
        raise StudioIntakeError("registry contains duplicate feature IDs")
    for feature_id, record in feature_map.items():
        if not _FEATURE_ID_RE.fullmatch(feature_id):
            raise StudioIntakeError("registry contains an invalid feature ID")
        if record.feature_id != feature_id:
            raise StudioIntakeError("registry feature map is internally inconsistent")


def _validated_constraints(
    constraints: Sequence[StudioConstraint],
) -> tuple[StudioConstraint, ...]:
    if isinstance(constraints, (str, bytes)) or not isinstance(constraints, Sequence):
        raise StudioIntakeError("explicit_constraints must be a sequence")
    if len(constraints) > _MAX_ITEMS:
        raise StudioIntakeError("explicit_constraints contains too many items")
    for constraint in constraints:
        if not isinstance(constraint, StudioConstraint):
            raise StudioIntakeError(
                "explicit_constraints must contain StudioConstraint values"
            )
    ordered = tuple(sorted(constraints, key=lambda item: item.canonical_key))
    if tuple(constraints) != ordered:
        raise StudioIntakeError("explicit_constraints must be canonically sorted")
    keys = [constraint.canonical_key for constraint in constraints]
    if len(set(keys)) != len(keys):
        raise StudioIntakeError("explicit_constraints contains duplicates")
    by_text: dict[str, set[ConstraintPolarity]] = {}
    for constraint in constraints:
        by_text.setdefault(constraint.normalized_text, set()).add(constraint.polarity)
    contradictory = sorted(
        text for text, polarities in by_text.items() if len(polarities) > 1
    )
    if contradictory:
        raise StudioIntakeError(
            "explicit_constraints contain contradictory require/forbid rules: "
            + ", ".join(contradictory)
        )
    return tuple(constraints)


def _tuple_of_strings(value: Any, field: str) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise StudioIntakeError(f"{field} must be a JSON list")
    if not all(isinstance(item, str) for item in value):
        raise StudioIntakeError(f"{field} must contain only text")
    return tuple(value)


def _sorted_feature_ids(
    values: Sequence[str], field: str, *, allow_empty: bool
) -> None:
    if isinstance(values, (str, bytes)) or not isinstance(values, tuple):
        raise StudioIntakeError(f"{field} must be a tuple")
    if not allow_empty and not values:
        raise StudioIntakeError(f"{field} must not be empty")
    if len(values) > _MAX_ITEMS:
        raise StudioIntakeError(f"{field} contains too many items")
    for value in values:
        if not isinstance(value, str) or not _FEATURE_ID_RE.fullmatch(value):
            raise StudioIntakeError(f"{field} contains an invalid feature ID")
    if len(set(values)) != len(values):
        raise StudioIntakeError(f"{field} contains duplicates")
    if values != tuple(sorted(values)):
        raise StudioIntakeError(f"{field} must be sorted")


def _sorted_text_items(values: Sequence[str], field: str) -> None:
    if isinstance(values, (str, bytes)) or not isinstance(values, tuple):
        raise StudioIntakeError(f"{field} must be a tuple")
    if len(values) > _MAX_ITEMS:
        raise StudioIntakeError(f"{field} contains too many items")
    normalized: list[str] = []
    for item in values:
        normalized.append(
            _bounded_text(item, field, max_length=_MAX_TEXT_ITEM)
        )
    if len(set(normalized)) != len(normalized):
        raise StudioIntakeError(f"{field} contains duplicates")
    if tuple(normalized) != tuple(sorted(normalized)):
        raise StudioIntakeError(f"{field} must be sorted")


def _sorted_machine_tokens(values: Sequence[str], field: str) -> None:
    if not isinstance(values, tuple):
        raise StudioIntakeError(f"{field} must be a tuple")
    if len(set(values)) != len(values):
        raise StudioIntakeError(f"{field} contains duplicates")
    for item in values:
        if not isinstance(item, str) or not re.fullmatch(r"[a-z][a-z0-9_]{1,79}", item):
            raise StudioIntakeError(f"{field} contains an invalid machine token")
    if values != tuple(sorted(values)):
        raise StudioIntakeError(f"{field} must be sorted")


def _bounded_text(value: Any, field: str, *, max_length: int) -> str:
    if not isinstance(value, str):
        raise StudioIntakeError(f"{field} must be text")
    normalized = _normalize_space(value)
    if not normalized:
        raise StudioIntakeError(f"{field} must not be blank")
    if len(normalized) > max_length:
        raise StudioIntakeError(f"{field} is too long")
    if _TEXT_CONTROL_RE.search(value):
        raise StudioIntakeError(f"{field} contains control characters")
    return normalized


def _normalize_space(value: str) -> str:
    return " ".join(value.split())


def _digest(value: Any, field: str) -> str:
    if not isinstance(value, str) or not _DIGEST_RE.fullmatch(value):
        raise StudioIntakeError(f"{field} must be a lowercase SHA-256 digest")
    return value


def _canonical_json(material: Mapping[str, object]) -> bytes:
    return json.dumps(
        material,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
