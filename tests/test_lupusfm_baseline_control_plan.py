import pytest

from lupusfm.evaluation.baselines import (
    CELL_TYPE_PROPORTION,
    DONOR_CELL_COUNT,
    LABEL_PERMUTATION_CONTROL,
    METADATA_CONFOUNDER_CONTROL,
    PSEUDOBULK_EXPRESSION,
    REQUIRED_BASELINE_FAMILIES,
    BaselineControlPlan,
    BaselineControlPlanError,
    BaselineSpec,
    baseline_control_plan_from_mapping,
    baseline_control_plan_to_dict,
    validate_baseline_control_plan,
    validate_baseline_spec,
)


def _required_baselines():
    return (
        BaselineSpec("pseudobulk", PSEUDOBULK_EXPRESSION),
        BaselineSpec("composition", CELL_TYPE_PROPORTION, comparison_role="control"),
        BaselineSpec("cell_count", DONOR_CELL_COUNT, comparison_role="control"),
        BaselineSpec(
            "metadata",
            METADATA_CONFOUNDER_CONTROL,
            comparison_role="confounder_control",
        ),
        BaselineSpec(
            "permutation",
            LABEL_PERMUTATION_CONTROL,
            comparison_role="negative_control",
        ),
    )


def _valid_plan(**overrides):
    values = {
        "task": "flare_vs_managed",
        "split_level": "patient",
        "baselines": _required_baselines(),
        "notes": "  baseline plan only  ",
    }
    values.update(overrides)
    return BaselineControlPlan(**values)


def test_baseline_control_plan_accepts_safe_metadata_only_contract():
    plan = _valid_plan()

    validated = validate_baseline_control_plan(plan)

    assert validated.task == "flare_vs_managed"
    assert validated.split_level == "patient"
    assert validated.candidate_representation == "frozen_geneformer_donor_embedding"
    assert {spec.family for spec in validated.baselines} == set(REQUIRED_BASELINE_FAMILIES)
    assert validated.require_pseudobulk_baseline is True
    assert validated.require_cell_type_proportion_baseline is True
    assert validated.require_donor_cell_count_control is True
    assert validated.require_metadata_confounder_control is True
    assert validated.require_label_permutation_control is True
    assert validated.require_same_splits_as_candidate is True
    assert validated.require_fold_internal_preprocessing is True
    assert validated.allow_feature_extraction is False
    assert validated.allow_model_fitting is False
    assert validated.allow_metric_computation is False
    assert validated.allow_modeling is False
    assert validated.performance_claims_added is False
    assert validated.notes == "baseline plan only"


@pytest.mark.parametrize(
    "task",
    ["flare_vs_managed", "flare_vs_healthy", "flare_vs_nonflare"],
)
def test_baseline_control_plan_accepts_allowed_tasks(task):
    validated = validate_baseline_control_plan(_valid_plan(task=task))

    assert validated.task == task


def test_baseline_spec_normalizes_mapping():
    spec = validate_baseline_spec(
        {
            "name": " pseudobulk ",
            "family": "pseudobulk_expression",
            "feature_level": " donor ",
            "comparison_role": " baseline ",
            "required": "true",
            "requires_same_splits_as_candidate": "yes",
            "requires_fold_internal_preprocessing": "1",
            "notes": "  planned only  ",
        }
    )

    assert spec == BaselineSpec(
        name="pseudobulk",
        family=PSEUDOBULK_EXPRESSION,
        feature_level="donor",
        comparison_role="baseline",
        required=True,
        requires_same_splits_as_candidate=True,
        requires_fold_internal_preprocessing=True,
        notes="planned only",
    )


def test_baseline_spec_rejects_cell_level_feature_level():
    with pytest.raises(BaselineControlPlanError, match="feature_level must be one of"):
        validate_baseline_spec(
            BaselineSpec(
                name="bad_cell_level",
                family=PSEUDOBULK_EXPRESSION,
                feature_level="cell",
            )
        )


def test_baseline_spec_requires_same_splits_as_candidate():
    with pytest.raises(BaselineControlPlanError, match="same splits"):
        validate_baseline_spec(
            BaselineSpec(
                name="bad_split_policy",
                family=PSEUDOBULK_EXPRESSION,
                requires_same_splits_as_candidate=False,
            )
        )


def test_baseline_spec_requires_fold_internal_preprocessing():
    with pytest.raises(BaselineControlPlanError, match="fold-internal"):
        validate_baseline_spec(
            BaselineSpec(
                name="bad_preprocessing",
                family=PSEUDOBULK_EXPRESSION,
                requires_fold_internal_preprocessing=False,
            )
        )


def test_baseline_control_plan_requires_all_required_families():
    plan = _valid_plan(
        baselines=(
            BaselineSpec("pseudobulk", PSEUDOBULK_EXPRESSION),
            BaselineSpec("composition", CELL_TYPE_PROPORTION),
            BaselineSpec("cell_count", DONOR_CELL_COUNT),
            BaselineSpec("metadata", METADATA_CONFOUNDER_CONTROL),
        )
    )

    with pytest.raises(BaselineControlPlanError, match="required families"):
        validate_baseline_control_plan(plan)


def test_baseline_control_plan_rejects_duplicate_names():
    plan = _valid_plan(
        baselines=(
            BaselineSpec("duplicate", PSEUDOBULK_EXPRESSION),
            BaselineSpec("duplicate", CELL_TYPE_PROPORTION),
            BaselineSpec("cell_count", DONOR_CELL_COUNT),
            BaselineSpec("metadata", METADATA_CONFOUNDER_CONTROL),
            BaselineSpec("permutation", LABEL_PERMUTATION_CONTROL),
        )
    )

    with pytest.raises(BaselineControlPlanError, match="names must be unique"):
        validate_baseline_control_plan(plan)


def test_baseline_control_plan_rejects_cell_level_split():
    with pytest.raises(BaselineControlPlanError, match="split_level must be one of"):
        validate_baseline_control_plan(_valid_plan(split_level="cell"))


@pytest.mark.parametrize(
    "flag_name",
    [
        "allow_cell_level_features",
        "allow_real_artifact_loading",
        "allow_anndata_loading",
        "allow_feature_extraction",
        "allow_global_preprocessing",
        "allow_scaler_outside_fold",
        "allow_model_fitting",
        "allow_metric_computation",
        "allow_modeling",
        "allow_training",
        "allow_external_validation",
        "performance_claims_added",
    ],
)
def test_baseline_control_plan_keeps_forbidden_flags_disabled(flag_name):
    with pytest.raises(BaselineControlPlanError):
        validate_baseline_control_plan(_valid_plan(**{flag_name: True}))


@pytest.mark.parametrize(
    "requirement_name",
    [
        "require_pseudobulk_baseline",
        "require_cell_type_proportion_baseline",
        "require_donor_cell_count_control",
        "require_metadata_confounder_control",
        "require_label_permutation_control",
        "require_same_splits_as_candidate",
        "require_fold_internal_preprocessing",
    ],
)
def test_baseline_control_plan_keeps_required_controls_enabled(requirement_name):
    with pytest.raises(BaselineControlPlanError):
        validate_baseline_control_plan(_valid_plan(**{requirement_name: False}))


def test_baseline_control_plan_from_mapping_uses_safe_defaults():
    plan = baseline_control_plan_from_mapping(
        {
            "task": "flare_vs_healthy",
            "split_level": "donor",
            "notes": "  normalized  ",
        }
    )

    assert plan.task == "flare_vs_healthy"
    assert plan.split_level == "donor"
    assert {spec.family for spec in plan.baselines} == set(REQUIRED_BASELINE_FAMILIES)
    assert plan.allow_feature_extraction is False
    assert plan.allow_training is False
    assert plan.notes == "normalized"


def test_baseline_control_plan_from_mapping_rejects_non_sequence_baselines():
    with pytest.raises(BaselineControlPlanError, match="baselines must be a sequence"):
        baseline_control_plan_from_mapping(
            {
                "task": "flare_vs_managed",
                "baselines": "pseudobulk",
            }
        )


def test_baseline_control_plan_to_dict_validates_before_serializing():
    serialized = baseline_control_plan_to_dict(_valid_plan())

    assert serialized["task"] == "flare_vs_managed"
    assert serialized["baselines"][0]["family"] == PSEUDOBULK_EXPRESSION
    assert serialized["allow_modeling"] is False
    assert serialized["performance_claims_added"] is False


def test_baseline_control_plan_module_has_no_execution_imports():
    import lupusfm.evaluation.baselines as baselines_module

    source = baselines_module.__loader__.get_source(
        baselines_module.__name__,
    ).lower()
    forbidden_fragments = [
        "import sklearn",
        "from sklearn",
        "import pandas",
        "import numpy",
        "import scanpy",
        "import anndata",
        "import torch",
        "import tensorflow",
        ".fit(",
        ".predict(",
        "roc_auc_score",
        "average_precision_score",
    ]

    for fragment in forbidden_fragments:
        assert fragment not in source
