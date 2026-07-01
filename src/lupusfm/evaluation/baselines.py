"""Stage 3 baseline/control plan scaffold.

This module defines metadata-only contracts for future baseline and control
comparisons. It does not load real embedding artifacts, load AnnData files,
execute Geneformer, execute tokenizers, extract embeddings, extract baseline
features, fit scalers, train models, compute real metrics, evaluate model
performance, perform external validation, or add performance claims.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from typing import Any

from lupusfm.data.anndata_schema import DEFAULT_FORBIDDEN_SPLIT_VALUES


DEFAULT_TASK = "flare_vs_managed"
ALLOWED_TASKS = (
    "flare_vs_managed",
    "flare_vs_healthy",
    "flare_vs_nonflare",
)

DEFAULT_CANDIDATE_REPRESENTATION = "frozen_geneformer_donor_embedding"
ALLOWED_CANDIDATE_REPRESENTATIONS = (
    DEFAULT_CANDIDATE_REPRESENTATION,
)

DEFAULT_SPLIT_LEVEL = "patient"
ALLOWED_PLAN_LEVELS = ("patient", "donor")

PSEUDOBULK_EXPRESSION = "pseudobulk_expression"
CELL_TYPE_PROPORTION = "cell_type_proportion"
DONOR_CELL_COUNT = "donor_cell_count"
METADATA_CONFOUNDER_CONTROL = "metadata_confounder_control"
LABEL_PERMUTATION_CONTROL = "label_permutation_control"

ALLOWED_BASELINE_FAMILIES = (
    PSEUDOBULK_EXPRESSION,
    CELL_TYPE_PROPORTION,
    DONOR_CELL_COUNT,
    METADATA_CONFOUNDER_CONTROL,
    LABEL_PERMUTATION_CONTROL,
)

REQUIRED_BASELINE_FAMILIES = ALLOWED_BASELINE_FAMILIES

ALLOWED_COMPARISON_ROLES = (
    "baseline",
    "control",
    "negative_control",
    "confounder_control",
)


class BaselineControlPlanError(ValueError):
    """Raised when a Stage 3 baseline/control plan violates the contract."""


@dataclass(frozen=True)
class BaselineSpec:
    """One planned future baseline or control comparison."""

    name: str
    family: str
    feature_level: str = DEFAULT_SPLIT_LEVEL
    comparison_role: str = "baseline"
    required: bool = True
    requires_same_splits_as_candidate: bool = True
    requires_fold_internal_preprocessing: bool = True
    notes: str = ""


@dataclass(frozen=True)
class BaselineControlPlan:
    """Metadata-only future baseline/control plan contract."""

    task: str = DEFAULT_TASK
    candidate_representation: str = DEFAULT_CANDIDATE_REPRESENTATION
    split_level: str = DEFAULT_SPLIT_LEVEL
    baselines: tuple[BaselineSpec, ...] = (
        BaselineSpec(
            name="pseudobulk_expression_baseline",
            family=PSEUDOBULK_EXPRESSION,
        ),
        BaselineSpec(
            name="cell_type_proportion_baseline",
            family=CELL_TYPE_PROPORTION,
            comparison_role="control",
        ),
        BaselineSpec(
            name="donor_cell_count_control",
            family=DONOR_CELL_COUNT,
            comparison_role="control",
        ),
        BaselineSpec(
            name="metadata_confounder_control",
            family=METADATA_CONFOUNDER_CONTROL,
            comparison_role="confounder_control",
        ),
        BaselineSpec(
            name="label_permutation_negative_control",
            family=LABEL_PERMUTATION_CONTROL,
            comparison_role="negative_control",
        ),
    )
    require_pseudobulk_baseline: bool = True
    require_cell_type_proportion_baseline: bool = True
    require_donor_cell_count_control: bool = True
    require_metadata_confounder_control: bool = True
    require_label_permutation_control: bool = True
    require_same_splits_as_candidate: bool = True
    require_fold_internal_preprocessing: bool = True
    allow_cell_level_features: bool = False
    allow_real_artifact_loading: bool = False
    allow_anndata_loading: bool = False
    allow_feature_extraction: bool = False
    allow_global_preprocessing: bool = False
    allow_scaler_outside_fold: bool = False
    allow_model_fitting: bool = False
    allow_metric_computation: bool = False
    allow_modeling: bool = False
    allow_training: bool = False
    allow_external_validation: bool = False
    performance_claims_added: bool = False
    notes: str = ""


def _clean_required_string(value: object, field_name: str) -> str:
    """Return a non-empty normalized string or raise."""

    normalized = str(value).strip()
    if not normalized:
        raise BaselineControlPlanError(f"{field_name} must not be empty.")
    return normalized


def _as_bool(value: object) -> bool:
    """Parse common bool-like values."""

    if isinstance(value, bool):
        return value

    return str(value).strip().lower() in {"1", "true", "yes"}


def _validate_choice(value: object, allowed: tuple[str, ...], field_name: str) -> str:
    """Validate a normalized string against an allowed set."""

    normalized = _clean_required_string(value, field_name)
    if normalized not in allowed:
        allowed_text = ", ".join(allowed)
        raise BaselineControlPlanError(
            f"{field_name} must be one of: {allowed_text}; got {normalized!r}."
        )

    return normalized


def _validate_plan_level(value: object, field_name: str) -> str:
    """Validate patient/donor level and reject cell-level policy."""

    level = _validate_choice(value, ALLOWED_PLAN_LEVELS, field_name)
    forbidden_levels = {str(item) for item in DEFAULT_FORBIDDEN_SPLIT_VALUES}
    if level in forbidden_levels:
        raise BaselineControlPlanError("cell-level features are not allowed.")

    return level


def validate_baseline_spec(spec: BaselineSpec | Mapping[str, Any]) -> BaselineSpec:
    """Validate one planned baseline/control specification."""

    if isinstance(spec, Mapping):
        name = spec.get("name", "")
        family = spec.get("family", "")
        feature_level = spec.get("feature_level", DEFAULT_SPLIT_LEVEL)
        comparison_role = spec.get("comparison_role", "baseline")
        required = spec.get("required", True)
        requires_same_splits_as_candidate = spec.get(
            "requires_same_splits_as_candidate",
            True,
        )
        requires_fold_internal_preprocessing = spec.get(
            "requires_fold_internal_preprocessing",
            True,
        )
        notes = spec.get("notes", "")
    else:
        name = spec.name
        family = spec.family
        feature_level = spec.feature_level
        comparison_role = spec.comparison_role
        required = spec.required
        requires_same_splits_as_candidate = spec.requires_same_splits_as_candidate
        requires_fold_internal_preprocessing = (
            spec.requires_fold_internal_preprocessing
        )
        notes = spec.notes

    validated = BaselineSpec(
        name=_clean_required_string(name, "baseline.name"),
        family=_validate_choice(family, ALLOWED_BASELINE_FAMILIES, "baseline.family"),
        feature_level=_validate_plan_level(feature_level, "baseline.feature_level"),
        comparison_role=_validate_choice(
            comparison_role,
            ALLOWED_COMPARISON_ROLES,
            "baseline.comparison_role",
        ),
        required=_as_bool(required),
        requires_same_splits_as_candidate=_as_bool(
            requires_same_splits_as_candidate
        ),
        requires_fold_internal_preprocessing=_as_bool(
            requires_fold_internal_preprocessing
        ),
        notes=str(notes).strip(),
    )

    if not validated.requires_same_splits_as_candidate:
        raise BaselineControlPlanError(
            "baseline/control comparisons must use the same splits as the candidate."
        )
    if not validated.requires_fold_internal_preprocessing:
        raise BaselineControlPlanError(
            "baseline/control preprocessing must be fold-internal."
        )

    return validated


def validate_baseline_control_plan(
    plan: BaselineControlPlan,
) -> BaselineControlPlan:
    """Validate a metadata-only future baseline/control plan."""

    task = _validate_choice(plan.task, ALLOWED_TASKS, "task")
    candidate_representation = _validate_choice(
        plan.candidate_representation,
        ALLOWED_CANDIDATE_REPRESENTATIONS,
        "candidate_representation",
    )
    split_level = _validate_plan_level(plan.split_level, "split_level")

    baselines = tuple(validate_baseline_spec(spec) for spec in plan.baselines)
    if not baselines:
        raise BaselineControlPlanError("at least one baseline/control is required.")

    names = [spec.name for spec in baselines]
    duplicate_names = sorted(
        name for name, count in Counter(names).items() if count > 1
    )
    if duplicate_names:
        raise BaselineControlPlanError("baseline/control names must be unique.")

    families = {spec.family for spec in baselines if spec.required}
    missing_families = sorted(set(REQUIRED_BASELINE_FAMILIES).difference(families))
    if missing_families:
        raise BaselineControlPlanError(
            "baseline/control plan must include all required families."
        )

    if not _as_bool(plan.require_pseudobulk_baseline):
        raise BaselineControlPlanError("pseudobulk baseline is required.")
    if not _as_bool(plan.require_cell_type_proportion_baseline):
        raise BaselineControlPlanError(
            "cell-type proportion baseline is required."
        )
    if not _as_bool(plan.require_donor_cell_count_control):
        raise BaselineControlPlanError("donor cell-count control is required.")
    if not _as_bool(plan.require_metadata_confounder_control):
        raise BaselineControlPlanError("metadata confounder control is required.")
    if not _as_bool(plan.require_label_permutation_control):
        raise BaselineControlPlanError("label permutation control is required.")
    if not _as_bool(plan.require_same_splits_as_candidate):
        raise BaselineControlPlanError(
            "all comparisons must use the same splits as the candidate."
        )
    if not _as_bool(plan.require_fold_internal_preprocessing):
        raise BaselineControlPlanError(
            "all preprocessing must be fold-internal."
        )

    if _as_bool(plan.allow_cell_level_features):
        raise BaselineControlPlanError("cell-level features are not allowed.")
    if _as_bool(plan.allow_real_artifact_loading):
        raise BaselineControlPlanError(
            "baseline/control plan must not load real artifacts."
        )
    if _as_bool(plan.allow_anndata_loading):
        raise BaselineControlPlanError("baseline/control plan must not load AnnData.")
    if _as_bool(plan.allow_feature_extraction):
        raise BaselineControlPlanError(
            "feature extraction is not allowed in the plan scaffold."
        )
    if _as_bool(plan.allow_global_preprocessing):
        raise BaselineControlPlanError(
            "global preprocessing across folds is not allowed."
        )
    if _as_bool(plan.allow_scaler_outside_fold):
        raise BaselineControlPlanError(
            "scaler fitting outside the training fold is not allowed."
        )
    if _as_bool(plan.allow_model_fitting):
        raise BaselineControlPlanError(
            "model fitting is not allowed in the plan scaffold."
        )
    if _as_bool(plan.allow_metric_computation):
        raise BaselineControlPlanError(
            "metric computation is not allowed in the plan scaffold."
        )
    if _as_bool(plan.allow_modeling):
        raise BaselineControlPlanError("Stage 3 baseline plan keeps modeling disabled.")
    if _as_bool(plan.allow_training):
        raise BaselineControlPlanError("Stage 3 baseline plan keeps training disabled.")
    if _as_bool(plan.allow_external_validation):
        raise BaselineControlPlanError(
            "Stage 3 baseline plan keeps external validation disabled."
        )
    if _as_bool(plan.performance_claims_added):
        raise BaselineControlPlanError(
            "Stage 3 baseline plan must not add performance claims."
        )

    return BaselineControlPlan(
        task=task,
        candidate_representation=candidate_representation,
        split_level=split_level,
        baselines=baselines,
        require_pseudobulk_baseline=True,
        require_cell_type_proportion_baseline=True,
        require_donor_cell_count_control=True,
        require_metadata_confounder_control=True,
        require_label_permutation_control=True,
        require_same_splits_as_candidate=True,
        require_fold_internal_preprocessing=True,
        allow_cell_level_features=False,
        allow_real_artifact_loading=False,
        allow_anndata_loading=False,
        allow_feature_extraction=False,
        allow_global_preprocessing=False,
        allow_scaler_outside_fold=False,
        allow_model_fitting=False,
        allow_metric_computation=False,
        allow_modeling=False,
        allow_training=False,
        allow_external_validation=False,
        performance_claims_added=False,
        notes=str(plan.notes).strip(),
    )


def baseline_control_plan_from_mapping(data: Mapping[str, Any]) -> BaselineControlPlan:
    """Build and validate a baseline/control plan from a mapping."""

    baselines_data = data.get("baselines")
    if baselines_data is None:
        baselines = BaselineControlPlan().baselines
    elif isinstance(baselines_data, (str, bytes)) or not isinstance(
        baselines_data,
        Sequence,
    ):
        raise BaselineControlPlanError("baselines must be a sequence.")
    else:
        baselines = tuple(validate_baseline_spec(spec) for spec in baselines_data)

    return validate_baseline_control_plan(
        BaselineControlPlan(
            task=data.get("task", DEFAULT_TASK),
            candidate_representation=data.get(
                "candidate_representation",
                DEFAULT_CANDIDATE_REPRESENTATION,
            ),
            split_level=data.get("split_level", DEFAULT_SPLIT_LEVEL),
            baselines=baselines,
            require_pseudobulk_baseline=data.get(
                "require_pseudobulk_baseline",
                True,
            ),
            require_cell_type_proportion_baseline=data.get(
                "require_cell_type_proportion_baseline",
                True,
            ),
            require_donor_cell_count_control=data.get(
                "require_donor_cell_count_control",
                True,
            ),
            require_metadata_confounder_control=data.get(
                "require_metadata_confounder_control",
                True,
            ),
            require_label_permutation_control=data.get(
                "require_label_permutation_control",
                True,
            ),
            require_same_splits_as_candidate=data.get(
                "require_same_splits_as_candidate",
                True,
            ),
            require_fold_internal_preprocessing=data.get(
                "require_fold_internal_preprocessing",
                True,
            ),
            allow_cell_level_features=data.get("allow_cell_level_features", False),
            allow_real_artifact_loading=data.get("allow_real_artifact_loading", False),
            allow_anndata_loading=data.get("allow_anndata_loading", False),
            allow_feature_extraction=data.get("allow_feature_extraction", False),
            allow_global_preprocessing=data.get("allow_global_preprocessing", False),
            allow_scaler_outside_fold=data.get("allow_scaler_outside_fold", False),
            allow_model_fitting=data.get("allow_model_fitting", False),
            allow_metric_computation=data.get("allow_metric_computation", False),
            allow_modeling=data.get("allow_modeling", False),
            allow_training=data.get("allow_training", False),
            allow_external_validation=data.get("allow_external_validation", False),
            performance_claims_added=data.get("performance_claims_added", False),
            notes=data.get("notes", ""),
        )
    )


def baseline_control_plan_to_dict(plan: BaselineControlPlan) -> dict[str, Any]:
    """Serialize a validated baseline/control plan to a plain dictionary."""

    return asdict(validate_baseline_control_plan(plan))
