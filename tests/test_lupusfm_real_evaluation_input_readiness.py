import pytest

from lupusfm.evaluation.real_input_readiness import (
    STAGE4_CURRENT_FEATURE,
    RealEvaluationInputReadinessContract,
    RealEvaluationInputReadinessError,
    readiness_gate_summary,
    real_evaluation_input_readiness_from_mapping,
    real_evaluation_input_readiness_to_dict,
    validate_real_evaluation_input_readiness,
)


def _contract(**overrides):
    values = {
        "current_feature": STAGE4_CURRENT_FEATURE,
        "readiness_status": "pending",
        "artifact_validation_status": "completed",
        "aggregation_plan_status": "completed",
        "split_manifest_validation_status": "completed",
        "artifact_format": "npy_directory",
        "artifact_layout": "directory",
        "artifact_record_level": "donor",
        "aggregation_strategy": "identity_donor_embedding_directory",
        "split_level": "donor",
        "expected_donor_count": 261,
        "observed_donor_count": 261,
        "notes": "  readiness metadata only  ",
    }
    values.update(overrides)
    return RealEvaluationInputReadinessContract(**values)


def test_real_evaluation_input_readiness_accepts_completed_upstream_contracts():
    validated = validate_real_evaluation_input_readiness(_contract())

    assert validated.current_feature == "STAGE4-F004"
    assert validated.readiness_status == "pending"
    assert validated.artifact_validation_status == "completed"
    assert validated.aggregation_plan_status == "completed"
    assert validated.split_manifest_validation_status == "completed"
    assert validated.artifact_format == "npy_directory"
    assert validated.artifact_layout == "directory"
    assert validated.artifact_record_level == "donor"
    assert validated.aggregation_strategy == "identity_donor_embedding_directory"
    assert validated.split_level == "donor"
    assert validated.expected_donor_count == 261
    assert validated.observed_donor_count == 261
    assert validated.require_unique_donors_across_splits is True
    assert validated.require_no_cell_level_splits is True
    assert validated.require_no_prediction_or_metric_columns is True
    assert validated.allow_input_materialization is False
    assert validated.allow_label_array_creation is False
    assert validated.allow_npy_payload_loading is False
    assert validated.allow_split_execution is False
    assert validated.allow_model_fitting is False
    assert validated.allow_prediction_generation is False
    assert validated.allow_metric_computation is False
    assert validated.allow_modeling is False
    assert validated.performance_claims_added is False
    assert validated.notes == "readiness metadata only"


def test_real_evaluation_input_readiness_from_mapping_normalizes_values():
    contract = real_evaluation_input_readiness_from_mapping(
        {
            "readiness_status": "validated",
            "expected_donor_count": "261",
            "observed_donor_count": "261",
            "notes": "  normalized  ",
        }
    )

    assert contract.current_feature == "STAGE4-F004"
    assert contract.readiness_status == "validated"
    assert contract.expected_donor_count == 261
    assert contract.observed_donor_count == 261
    assert contract.notes == "normalized"


def test_real_evaluation_input_readiness_rejects_wrong_current_feature():
    with pytest.raises(RealEvaluationInputReadinessError, match="current_feature"):
        validate_real_evaluation_input_readiness(
            _contract(current_feature="STAGE4-F003")
        )


@pytest.mark.parametrize(
    "status_field",
    [
        "artifact_validation_status",
        "aggregation_plan_status",
        "split_manifest_validation_status",
    ],
)
def test_real_evaluation_input_readiness_requires_completed_upstream_statuses(status_field):
    with pytest.raises(RealEvaluationInputReadinessError, match=status_field):
        validate_real_evaluation_input_readiness(_contract(**{status_field: "pending"}))


def test_real_evaluation_input_readiness_rejects_non_donor_record_level():
    with pytest.raises(RealEvaluationInputReadinessError, match="artifact_record_level"):
        validate_real_evaluation_input_readiness(_contract(artifact_record_level="cell"))


def test_real_evaluation_input_readiness_rejects_donor_count_mismatch():
    with pytest.raises(RealEvaluationInputReadinessError, match="expected_donor_count"):
        validate_real_evaluation_input_readiness(
            _contract(expected_donor_count=261, observed_donor_count=260)
        )


@pytest.mark.parametrize(
    "required_gate",
    [
        "require_unique_donors_across_splits",
        "require_no_cell_level_splits",
        "require_no_prediction_or_metric_columns",
    ],
)
def test_real_evaluation_input_readiness_requires_leakage_gates_enabled(required_gate):
    with pytest.raises(RealEvaluationInputReadinessError, match="required"):
        validate_real_evaluation_input_readiness(_contract(**{required_gate: False}))


@pytest.mark.parametrize(
    "flag_name",
    [
        "allow_input_materialization",
        "allow_label_array_creation",
        "allow_real_artifact_loading",
        "allow_npy_payload_loading",
        "allow_embedding_vector_parsing",
        "allow_real_aggregation_execution",
        "allow_split_execution",
        "allow_anndata_loading",
        "allow_geneformer_execution",
        "allow_tokenizer_execution",
        "allow_embedding_extraction",
        "allow_feature_extraction",
        "allow_global_preprocessing",
        "allow_scaler_outside_fold",
        "allow_model_fitting",
        "allow_prediction_generation",
        "allow_metric_computation",
        "allow_modeling",
        "allow_training",
        "allow_external_validation",
        "performance_claims_added",
    ],
)
def test_real_evaluation_input_readiness_keeps_forbidden_flags_disabled(flag_name):
    with pytest.raises(RealEvaluationInputReadinessError):
        validate_real_evaluation_input_readiness(_contract(**{flag_name: True}))


def test_real_evaluation_input_readiness_to_dict_validates_before_serializing():
    serialized = real_evaluation_input_readiness_to_dict(_contract())

    assert serialized["current_feature"] == "STAGE4-F004"
    assert serialized["expected_donor_count"] == 261
    assert serialized["allow_input_materialization"] is False
    assert serialized["allow_modeling"] is False
    assert serialized["allow_metric_computation"] is False
    assert serialized["performance_claims_added"] is False


def test_readiness_gate_summary_has_no_metrics_or_predictions():
    summary = readiness_gate_summary(_contract())

    assert summary == {
        "current_feature": "STAGE4-F004",
        "readiness_status": "pending",
        "artifact_validation_status": "completed",
        "aggregation_plan_status": "completed",
        "split_manifest_validation_status": "completed",
        "expected_donor_count": 261,
        "observed_donor_count": 261,
        "split_level": "donor",
        "allow_input_materialization": False,
        "allow_modeling": False,
        "allow_metric_computation": False,
        "performance_claims_added": False,
    }


def test_real_evaluation_input_readiness_module_has_no_runtime_or_modeling_imports():
    import lupusfm.evaluation.real_input_readiness as readiness_module

    source = readiness_module.__loader__.get_source(readiness_module.__name__).lower()
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
