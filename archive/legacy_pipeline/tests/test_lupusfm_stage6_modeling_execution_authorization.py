import pytest

from lupusfm.evaluation.stage6_modeling_execution_authorization import (
    CONTROLLED_DONOR_LEVEL_EXECUTION_IN_STAGE6,
    NO_ADDITIONAL_EXECUTION_STAGE_REQUIRED,
    SEPARATE_EXECUTION_STAGE_REQUIRED,
    STAGE5_COMPLETED_FEATURES,
    STAGE6_CURRENT_FEATURE,
    STAGE6_REMAINING_FEATURES,
    Stage6ModelingExecutionAuthorization,
    Stage6ModelingExecutionAuthorizationError,
    stage6_modeling_execution_authorization_from_mapping,
    stage6_modeling_execution_authorization_summary,
    stage6_modeling_execution_authorization_to_dict,
    validate_stage6_modeling_execution_authorization,
)


def _authorization(**overrides):
    values = {
        "current_stage": "Stage 6",
        "current_feature": STAGE6_CURRENT_FEATURE,
        "stage6_status": "in_progress",
        "authorization_status": "in_progress",
        "authorization_decision": "stage6_controlled_execution_path_authorized",
        "modeling_authorization_status": "stage6_opened_no_runtime_execution",
        "upstream_stage5_status": "completed",
        "upstream_handoff_decision": SEPARATE_EXECUTION_STAGE_REQUIRED,
        "completed_stage5_features": STAGE5_COMPLETED_FEATURES,
        "stage6_execution_policy": CONTROLLED_DONOR_LEVEL_EXECUTION_IN_STAGE6,
        "additional_execution_stage_policy": NO_ADDITIONAL_EXECUTION_STAGE_REQUIRED,
        "remaining_stage6_features": STAGE6_REMAINING_FEATURES,
        "notes": "  Stage 6 path opened  ",
    }
    values.update(overrides)
    return Stage6ModelingExecutionAuthorization(**values)


def test_stage6_authorization_opens_single_execution_stage_without_runtime_execution():
    validated = validate_stage6_modeling_execution_authorization(_authorization())

    assert validated.current_stage == "Stage 6"
    assert validated.current_feature == "STAGE6-F001"
    assert validated.stage6_status == "in_progress"
    assert validated.authorization_status == "in_progress"
    assert (
        validated.authorization_decision
        == "stage6_controlled_execution_path_authorized"
    )
    assert validated.upstream_stage5_status == "completed"
    assert (
        validated.upstream_handoff_decision
        == "separate_modeling_execution_stage_required"
    )
    assert validated.completed_stage5_features == (
        "STAGE5-F001",
        "STAGE5-F002",
        "STAGE5-F003",
        "STAGE5-F004",
        "STAGE5-F005",
    )
    assert validated.stage6_execution_policy == (
        "controlled_donor_level_execution_in_stage6"
    )
    assert (
        validated.additional_execution_stage_policy
        == "no_additional_execution_stage_required"
    )
    assert validated.first_runtime_execution_feature == "STAGE6-F005"
    assert validated.next_feature == "STAGE6-F002"
    assert validated.requires_donor_level_only is True
    assert validated.forbids_cell_level_split is True
    assert validated.requires_no_additional_execution_stage is True
    assert validated.permits_stage6_controlled_execution_path is True
    assert validated.stage7_required is False
    assert validated.separate_stage7_required is False
    assert validated.allow_real_artifact_loading is False
    assert validated.allow_input_materialization is False
    assert validated.allow_split_execution is False
    assert validated.allow_model_fitting is False
    assert validated.allow_prediction_generation is False
    assert validated.allow_metric_computation is False
    assert validated.modeling_authorization_granted is False
    assert validated.modeling_allowed is False
    assert validated.performance_claims_added is False
    assert validated.notes == "Stage 6 path opened"


def test_stage6_authorization_from_mapping_normalizes_sequences_and_notes():
    authorization = stage6_modeling_execution_authorization_from_mapping(
        {
            "completed_stage5_features": list(STAGE5_COMPLETED_FEATURES),
            "remaining_stage6_features": list(STAGE6_REMAINING_FEATURES),
            "notes": "  normalized  ",
        }
    )

    assert authorization.current_feature == "STAGE6-F001"
    assert authorization.completed_stage5_features == STAGE5_COMPLETED_FEATURES
    assert authorization.remaining_stage6_features == STAGE6_REMAINING_FEATURES
    assert authorization.notes == "normalized"


def test_stage6_authorization_rejects_wrong_stage_or_feature():
    with pytest.raises(Stage6ModelingExecutionAuthorizationError, match="current_stage"):
        validate_stage6_modeling_execution_authorization(
            _authorization(current_stage="Stage 5")
        )

    with pytest.raises(
        Stage6ModelingExecutionAuthorizationError,
        match="current_feature",
    ):
        validate_stage6_modeling_execution_authorization(
            _authorization(current_feature="STAGE6-F002")
        )


def test_stage6_authorization_requires_completed_stage5_handoff():
    with pytest.raises(
        Stage6ModelingExecutionAuthorizationError,
        match="upstream_stage5_status",
    ):
        validate_stage6_modeling_execution_authorization(
            _authorization(upstream_stage5_status="in_progress")
        )

    with pytest.raises(
        Stage6ModelingExecutionAuthorizationError,
        match="upstream_handoff_decision",
    ):
        validate_stage6_modeling_execution_authorization(
            _authorization(upstream_handoff_decision="modeling_authorized")
        )


def test_stage6_authorization_requires_exact_completed_stage5_features():
    with pytest.raises(
        Stage6ModelingExecutionAuthorizationError,
        match="completed_stage5_features",
    ):
        validate_stage6_modeling_execution_authorization(
            _authorization(completed_stage5_features=("STAGE5-F001",))
        )


def test_stage6_authorization_requires_exact_remaining_stage6_features():
    with pytest.raises(
        Stage6ModelingExecutionAuthorizationError,
        match="remaining_stage6_features",
    ):
        validate_stage6_modeling_execution_authorization(
            _authorization(remaining_stage6_features=("STAGE6-F002",))
        )


@pytest.mark.parametrize(
    "required_gate",
    [
        "requires_explicit_modeling_approval",
        "requires_human_review_before_modeling",
        "requires_reproducibility_review",
        "requires_leakage_review",
        "requires_artifact_integrity_review",
        "requires_scope_review",
        "requires_donor_level_only",
        "forbids_cell_level_split",
        "requires_no_large_artifact_commit",
        "requires_protocol_before_execution",
        "requires_no_additional_execution_stage",
        "permits_stage6_controlled_execution_path",
    ],
)
def test_stage6_authorization_requires_gates(required_gate):
    with pytest.raises(Stage6ModelingExecutionAuthorizationError, match="required"):
        validate_stage6_modeling_execution_authorization(
            _authorization(**{required_gate: False})
        )


@pytest.mark.parametrize("stage7_flag", ["stage7_required", "separate_stage7_required"])
def test_stage6_authorization_rejects_deferring_execution_to_stage7(stage7_flag):
    with pytest.raises(Stage6ModelingExecutionAuthorizationError, match="Stage 7"):
        validate_stage6_modeling_execution_authorization(
            _authorization(**{stage7_flag: True})
        )


@pytest.mark.parametrize(
    "flag_name",
    [
        "allow_real_artifact_loading",
        "allow_npy_payload_loading",
        "allow_embedding_vector_parsing",
        "allow_input_materialization",
        "allow_label_array_creation",
        "allow_split_execution",
        "allow_real_aggregation_execution",
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
        "modeling_authorization_granted",
        "modeling_allowed",
        "training_allowed",
        "external_validation_allowed",
        "performance_claims_allowed",
        "performance_claims_added",
    ],
)
def test_stage6_authorization_keeps_runtime_modeling_and_claim_flags_disabled(flag_name):
    with pytest.raises(Stage6ModelingExecutionAuthorizationError):
        validate_stage6_modeling_execution_authorization(
            _authorization(**{flag_name: True})
        )


def test_stage6_authorization_to_dict_serializes_tuples_as_lists():
    serialized = stage6_modeling_execution_authorization_to_dict(_authorization())

    assert serialized["current_feature"] == "STAGE6-F001"
    assert serialized["completed_stage5_features"] == list(STAGE5_COMPLETED_FEATURES)
    assert serialized["remaining_stage6_features"] == list(STAGE6_REMAINING_FEATURES)
    assert serialized["stage7_required"] is False
    assert serialized["allow_model_fitting"] is False
    assert serialized["allow_metric_computation"] is False
    assert serialized["performance_claims_allowed"] is False


def test_stage6_authorization_summary_records_no_stage7_deferral():
    summary = stage6_modeling_execution_authorization_summary(_authorization())

    assert summary == {
        "current_stage": "Stage 6",
        "current_feature": "STAGE6-F001",
        "stage6_status": "in_progress",
        "authorization_status": "in_progress",
        "authorization_decision": "stage6_controlled_execution_path_authorized",
        "stage6_execution_policy": "controlled_donor_level_execution_in_stage6",
        "additional_execution_stage_policy": "no_additional_execution_stage_required",
        "first_runtime_execution_feature": "STAGE6-F005",
        "next_feature": "STAGE6-F002",
        "requires_donor_level_only": True,
        "forbids_cell_level_split": True,
        "requires_no_additional_execution_stage": True,
        "permits_stage6_controlled_execution_path": True,
        "stage7_required": False,
        "modeling_authorization_granted": False,
        "modeling_allowed": False,
        "allow_model_fitting": False,
        "allow_prediction_generation": False,
        "allow_metric_computation": False,
        "performance_claims_allowed": False,
        "performance_claims_added": False,
    }


def test_stage6_authorization_module_has_no_runtime_or_modeling_imports():
    import lupusfm.evaluation.stage6_modeling_execution_authorization as authorization_module

    source = authorization_module.__loader__.get_source(
        authorization_module.__name__
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
        "import geneformer",
        "from geneformer",
        "read_h5ad",
        "read_parquet",
        "np.load",
        ".fit(",
        ".predict(",
        "roc_auc",
        "accuracy_score",
        "classification_report",
    ]

    assert not any(fragment in source for fragment in forbidden_fragments)
