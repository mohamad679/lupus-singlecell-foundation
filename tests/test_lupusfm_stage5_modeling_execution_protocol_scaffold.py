import pytest

from lupusfm.evaluation.stage5_modeling_execution_protocol_scaffold import (
    CELL_LEVEL_SPLIT_FORBIDDEN,
    DONOR_LEVEL_ONLY,
    FUTURE_ONLY_NO_COMPUTATION,
    PROHIBITED_UNTIL_EXPLICIT_GATE,
    REQUIRED_COMPLETED_STAGE5_FEATURES,
    STAGE5_CURRENT_FEATURE,
    STAGE5_NEXT_FEATURE,
    STAGE5_PREVIOUS_FEATURE,
    Stage5ModelingExecutionProtocolScaffold,
    Stage5ModelingExecutionProtocolScaffoldError,
    stage5_modeling_execution_protocol_scaffold_from_mapping,
    stage5_modeling_execution_protocol_scaffold_to_dict,
    stage5_modeling_execution_protocol_summary,
    validate_stage5_modeling_execution_protocol_scaffold,
)


def _protocol(**overrides):
    values = {
        "current_stage": "Stage 5",
        "current_feature": STAGE5_CURRENT_FEATURE,
        "stage5_status": "in_progress",
        "protocol_status": "in_progress",
        "approval_status": "pending",
        "modeling_authorization_status": "not_granted",
        "previous_feature": STAGE5_PREVIOUS_FEATURE,
        "previous_feature_status": "completed",
        "completed_stage5_features": REQUIRED_COMPLETED_STAGE5_FEATURES,
        "next_feature": STAGE5_NEXT_FEATURE,
        "notes": "  protocol scaffold only  ",
    }
    values.update(overrides)
    return Stage5ModelingExecutionProtocolScaffold(**values)


def test_stage5_protocol_accepts_metadata_only_execution_protocol():
    validated = validate_stage5_modeling_execution_protocol_scaffold(_protocol())

    assert validated.current_stage == "Stage 5"
    assert validated.current_feature == "STAGE5-F002"
    assert validated.protocol_status == "in_progress"
    assert validated.approval_status == "pending"
    assert validated.modeling_authorization_status == "not_granted"
    assert validated.previous_feature == "STAGE5-F001"
    assert validated.previous_feature_status == "completed"
    assert validated.completed_stage5_features == ("STAGE5-F001",)
    assert validated.next_feature == "STAGE5-F003"
    assert validated.protocol_record_level == "donor"
    assert validated.split_policy == "donor_level_only"
    assert validated.leakage_policy == "cell_level_split_forbidden"
    assert validated.artifact_loading_policy == "prohibited_until_explicit_gate"
    assert validated.input_materialization_policy == "prohibited_until_explicit_gate"
    assert validated.label_creation_policy == "prohibited_until_explicit_gate"
    assert validated.aggregation_execution_policy == "prohibited_until_explicit_gate"
    assert validated.modeling_execution_policy == "prohibited_until_explicit_gate"
    assert validated.prediction_generation_policy == "prohibited_until_explicit_gate"
    assert validated.metric_computation_policy == "future_only_no_computation"
    assert validated.external_validation_policy == "prohibited_until_explicit_gate"
    assert validated.performance_claim_policy == "prohibited_until_explicit_gate"
    assert validated.requires_explicit_modeling_approval is True
    assert validated.requires_separate_execution_gate is True
    assert validated.requires_donor_level_only is True
    assert validated.forbids_cell_level_split is True
    assert validated.allow_npy_payload_loading is False
    assert validated.allow_input_materialization is False
    assert validated.allow_model_fitting is False
    assert validated.allow_prediction_generation is False
    assert validated.allow_metric_computation is False
    assert validated.modeling_authorization_granted is False
    assert validated.modeling_allowed is False
    assert validated.performance_claims_added is False
    assert validated.notes == "protocol scaffold only"


def test_stage5_protocol_from_mapping_normalizes_values():
    protocol = stage5_modeling_execution_protocol_scaffold_from_mapping(
        {
            "modeling_authorization_status": "blocked_pending_human_review",
            "notes": "  normalized  ",
        }
    )

    assert protocol.current_feature == "STAGE5-F002"
    assert protocol.modeling_authorization_status == "blocked_pending_human_review"
    assert protocol.completed_stage5_features == REQUIRED_COMPLETED_STAGE5_FEATURES
    assert protocol.notes == "normalized"


def test_stage5_protocol_rejects_wrong_current_feature():
    with pytest.raises(
        Stage5ModelingExecutionProtocolScaffoldError,
        match="current_feature",
    ):
        validate_stage5_modeling_execution_protocol_scaffold(
            _protocol(current_feature="STAGE5-F001")
        )


@pytest.mark.parametrize(
    ("field_name", "invalid_value"),
    [
        ("previous_feature", "STAGE4-F006"),
        ("previous_feature_status", "pending"),
        ("next_feature", "STAGE5-F004"),
        ("protocol_record_level", "cell"),
    ],
)
def test_stage5_protocol_requires_expected_feature_chain_and_record_level(
    field_name,
    invalid_value,
):
    with pytest.raises(Stage5ModelingExecutionProtocolScaffoldError, match=field_name):
        validate_stage5_modeling_execution_protocol_scaffold(
            _protocol(**{field_name: invalid_value})
        )


def test_stage5_protocol_requires_completed_stage5_f001():
    with pytest.raises(
        Stage5ModelingExecutionProtocolScaffoldError,
        match="completed_stage5_features",
    ):
        validate_stage5_modeling_execution_protocol_scaffold(
            _protocol(completed_stage5_features=())
        )


@pytest.mark.parametrize(
    ("field_name", "invalid_value"),
    [
        ("split_policy", CELL_LEVEL_SPLIT_FORBIDDEN),
        ("leakage_policy", DONOR_LEVEL_ONLY),
        ("artifact_loading_policy", FUTURE_ONLY_NO_COMPUTATION),
        ("input_materialization_policy", FUTURE_ONLY_NO_COMPUTATION),
        ("label_creation_policy", FUTURE_ONLY_NO_COMPUTATION),
        ("aggregation_execution_policy", FUTURE_ONLY_NO_COMPUTATION),
        ("modeling_execution_policy", FUTURE_ONLY_NO_COMPUTATION),
        ("prediction_generation_policy", FUTURE_ONLY_NO_COMPUTATION),
        ("metric_computation_policy", PROHIBITED_UNTIL_EXPLICIT_GATE),
        ("external_validation_policy", FUTURE_ONLY_NO_COMPUTATION),
        ("performance_claim_policy", FUTURE_ONLY_NO_COMPUTATION),
    ],
)
def test_stage5_protocol_rejects_unsafe_policy_changes(field_name, invalid_value):
    with pytest.raises(Stage5ModelingExecutionProtocolScaffoldError):
        validate_stage5_modeling_execution_protocol_scaffold(
            _protocol(**{field_name: invalid_value})
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
        "requires_separate_execution_gate",
    ],
)
def test_stage5_protocol_requires_approval_and_execution_gates(required_gate):
    with pytest.raises(Stage5ModelingExecutionProtocolScaffoldError, match="required"):
        validate_stage5_modeling_execution_protocol_scaffold(
            _protocol(**{required_gate: False})
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
def test_stage5_protocol_keeps_runtime_and_modeling_flags_disabled(flag_name):
    with pytest.raises(Stage5ModelingExecutionProtocolScaffoldError):
        validate_stage5_modeling_execution_protocol_scaffold(
            _protocol(**{flag_name: True})
        )


def test_stage5_protocol_to_dict_serializes_completed_features_as_list():
    serialized = stage5_modeling_execution_protocol_scaffold_to_dict(_protocol())

    assert serialized["current_feature"] == "STAGE5-F002"
    assert serialized["completed_stage5_features"] == ["STAGE5-F001"]
    assert serialized["protocol_record_level"] == "donor"
    assert serialized["split_policy"] == "donor_level_only"
    assert serialized["modeling_authorization_granted"] is False
    assert serialized["modeling_allowed"] is False
    assert serialized["allow_metric_computation"] is False
    assert serialized["performance_claims_allowed"] is False


def test_stage5_protocol_summary_does_not_authorize_execution():
    summary = stage5_modeling_execution_protocol_summary(_protocol())

    assert summary == {
        "current_stage": "Stage 5",
        "current_feature": "STAGE5-F002",
        "protocol_status": "in_progress",
        "approval_status": "pending",
        "modeling_authorization_status": "not_granted",
        "previous_feature": "STAGE5-F001",
        "next_feature": "STAGE5-F003",
        "protocol_record_level": "donor",
        "split_policy": "donor_level_only",
        "leakage_policy": "cell_level_split_forbidden",
        "metric_computation_policy": "future_only_no_computation",
        "requires_separate_execution_gate": True,
        "modeling_authorization_granted": False,
        "modeling_allowed": False,
        "training_allowed": False,
        "performance_claims_allowed": False,
        "performance_claims_added": False,
    }


def test_stage5_protocol_module_has_no_runtime_or_modeling_imports():
    import lupusfm.evaluation.stage5_modeling_execution_protocol_scaffold as protocol_module

    source = protocol_module.__loader__.get_source(protocol_module.__name__).lower()
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
