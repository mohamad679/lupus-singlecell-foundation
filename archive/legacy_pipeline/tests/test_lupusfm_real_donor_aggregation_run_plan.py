import pytest

from lupusfm.embeddings.real_aggregation_plan import (
    IDENTITY_DONOR_EMBEDDING_DIRECTORY,
    STAGE4_CURRENT_FEATURE,
    RealDonorAggregationRunPlan,
    RealDonorAggregationRunPlanError,
    real_donor_aggregation_run_plan_from_mapping,
    real_donor_aggregation_run_plan_to_dict,
    validate_real_donor_aggregation_run_plan,
)


def _valid_plan(**overrides):
    values = {
        "current_feature": STAGE4_CURRENT_FEATURE,
        "plan_status": "pending",
        "aggregation_strategy": IDENTITY_DONOR_EMBEDDING_DIRECTORY,
        "artifact_format": "npy_directory",
        "artifact_layout": "directory",
        "directory_file_suffix": ".npy",
        "input_record_level": "donor",
        "output_record_level": "donor",
        "split_level": "donor",
        "expected_donor_file_count": 261,
        "observed_donor_file_count": 261,
        "observed_total_size_bytes": 360839808,
        "observed_all_files_same_size": True,
        "observed_flare_like_count": 14,
        "observed_healthy_hc_like_count": 48,
        "observed_healthy_igtb_like_count": 50,
        "observed_managed_sle_numeric_like_count": 148,
        "observed_control_like_count": 1,
        "notes": "  donor-level plan only  ",
    }
    values.update(overrides)
    return RealDonorAggregationRunPlan(**values)


def test_real_donor_aggregation_run_plan_accepts_observed_donor_directory_contract():
    validated = validate_real_donor_aggregation_run_plan(_valid_plan())

    assert validated.current_feature == "STAGE4-F002"
    assert validated.plan_status == "pending"
    assert validated.aggregation_strategy == "identity_donor_embedding_directory"
    assert validated.artifact_format == "npy_directory"
    assert validated.artifact_layout == "directory"
    assert validated.directory_file_suffix == ".npy"
    assert validated.input_record_level == "donor"
    assert validated.output_record_level == "donor"
    assert validated.split_level == "donor"
    assert validated.expected_donor_file_count == 261
    assert validated.observed_donor_file_count == 261
    assert validated.observed_total_size_bytes == 360839808
    assert validated.observed_all_files_same_size is True
    assert validated.observed_flare_like_count == 14
    assert validated.observed_healthy_hc_like_count == 48
    assert validated.observed_healthy_igtb_like_count == 50
    assert validated.observed_managed_sle_numeric_like_count == 148
    assert validated.observed_control_like_count == 1
    assert validated.requires_cell_to_donor_pooling is False
    assert validated.requires_payload_loading is False
    assert validated.requires_npy_payload_loading is False
    assert validated.requires_real_aggregation_execution is False
    assert validated.allow_real_artifact_loading is False
    assert validated.allow_npy_payload_loading is False
    assert validated.allow_embedding_vector_parsing is False
    assert validated.allow_real_aggregation_execution is False
    assert validated.allow_model_fitting is False
    assert validated.allow_metric_computation is False
    assert validated.allow_modeling is False
    assert validated.performance_claims_added is False
    assert validated.notes == "donor-level plan only"


def test_real_donor_aggregation_run_plan_from_mapping_normalizes_safe_defaults():
    plan = real_donor_aggregation_run_plan_from_mapping(
        {
            "plan_status": "validated",
            "expected_donor_file_count": "261",
            "observed_donor_file_count": "261",
            "observed_all_files_same_size": "true",
            "notes": "  normalized  ",
        }
    )

    assert plan.current_feature == "STAGE4-F002"
    assert plan.plan_status == "validated"
    assert plan.expected_donor_file_count == 261
    assert plan.observed_donor_file_count == 261
    assert plan.observed_all_files_same_size is True
    assert plan.notes == "normalized"


def test_real_donor_aggregation_run_plan_rejects_wrong_current_feature():
    with pytest.raises(RealDonorAggregationRunPlanError, match="current_feature"):
        validate_real_donor_aggregation_run_plan(
            _valid_plan(current_feature="STAGE4-F001")
        )


def test_real_donor_aggregation_run_plan_rejects_cell_record_level():
    with pytest.raises(RealDonorAggregationRunPlanError, match="input_record_level"):
        validate_real_donor_aggregation_run_plan(_valid_plan(input_record_level="cell"))


def test_real_donor_aggregation_run_plan_rejects_mismatched_file_counts():
    with pytest.raises(
        RealDonorAggregationRunPlanError,
        match="expected and observed donor file counts",
    ):
        validate_real_donor_aggregation_run_plan(
            _valid_plan(expected_donor_file_count=261, observed_donor_file_count=260)
        )


def test_real_donor_aggregation_run_plan_rejects_category_count_mismatch():
    with pytest.raises(
        RealDonorAggregationRunPlanError,
        match="filename category counts",
    ):
        validate_real_donor_aggregation_run_plan(
            _valid_plan(observed_control_like_count=2)
        )


def test_real_donor_aggregation_run_plan_rejects_inconsistent_file_sizes():
    with pytest.raises(
        RealDonorAggregationRunPlanError,
        match="consistent size",
    ):
        validate_real_donor_aggregation_run_plan(
            _valid_plan(observed_all_files_same_size=False)
        )


@pytest.mark.parametrize(
    "flag_name",
    [
        "requires_cell_to_donor_pooling",
        "requires_payload_loading",
        "requires_npy_payload_loading",
        "requires_real_aggregation_execution",
        "requires_anndata_loading",
        "requires_geneformer_execution",
        "requires_tokenizer_execution",
        "requires_embedding_extraction",
        "allow_real_artifact_loading",
        "allow_npy_payload_loading",
        "allow_embedding_vector_parsing",
        "allow_real_aggregation_execution",
        "allow_anndata_loading",
        "allow_geneformer_execution",
        "allow_tokenizer_execution",
        "allow_embedding_extraction",
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
def test_real_donor_aggregation_run_plan_keeps_forbidden_flags_disabled(flag_name):
    with pytest.raises(RealDonorAggregationRunPlanError):
        validate_real_donor_aggregation_run_plan(_valid_plan(**{flag_name: True}))


def test_real_donor_aggregation_run_plan_to_dict_validates_before_serializing():
    serialized = real_donor_aggregation_run_plan_to_dict(_valid_plan())

    assert serialized["current_feature"] == "STAGE4-F002"
    assert serialized["aggregation_strategy"] == "identity_donor_embedding_directory"
    assert serialized["observed_donor_file_count"] == 261
    assert serialized["allow_real_aggregation_execution"] is False
    assert serialized["allow_modeling"] is False
    assert serialized["performance_claims_added"] is False


def test_real_donor_aggregation_plan_module_has_no_runtime_or_modeling_imports():
    import lupusfm.embeddings.real_aggregation_plan as plan_module

    source = plan_module.__loader__.get_source(plan_module.__name__).lower()
    forbidden_fragments = [
        "import sklearn",
        "from sklearn",
        "import pandas",
        "import numpy",
        "import scanpy",
        "import anndata",
        "import torch",
        "import tensorflow",
        "import geneformer",
        "from geneformer",
        "read_h5ad",
        "read_parquet",
        "np.load",
        ".fit(",
        ".predict(",
    ]

    assert not any(fragment in source for fragment in forbidden_fragments)
