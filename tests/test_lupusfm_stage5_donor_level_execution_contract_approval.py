import pytest

from lupusfm.evaluation.stage5_donor_level_execution_contract_approval import (
    CELL_LEVEL_SPLIT_FORBIDDEN,
    DONOR_LEVEL_ONLY,
    FUTURE_ONLY_NO_COMPUTATION,
    PROHIBITED_UNTIL_EXPLICIT_GATE,
    STAGE5_CURRENT_FEATURE,
    STAGE5_NEXT_FEATURE,
    STAGE5_PREVIOUS_FEATURES,
    Stage5DonorLevelExecutionContractApproval,
    Stage5DonorLevelExecutionContractApprovalError,
    stage5_donor_level_execution_contract_approval_from_mapping,
    stage5_donor_level_execution_contract_approval_to_dict,
    stage5_donor_level_execution_contract_summary,
    validate_stage5_donor_level_execution_contract_approval,
)


def _contract(**overrides):
    values = {
        "current_stage": "Stage 5",
        "current_feature": STAGE5_CURRENT_FEATURE,
        "stage5_status": "in_progress",
        "contract_status": "in_progress",
        "contract_approval_decision": "pending_contract_review",
        "completed_stage5_features": STAGE5_PREVIOUS_FEATURES,
        "previous_protocol_feature": "STAGE5-F002",
        "previous_protocol_status": "completed",
        "next_feature": STAGE5_NEXT_FEATURE,
        "notes": "  donor contract only  ",
    }
    values.update(overrides)
    return Stage5DonorLevelExecutionContractApproval(**values)


def test_stage5_contract_accepts_donor_level_contract_without_execution():
    validated = validate_stage5_donor_level_execution_contract_approval(_contract())

    assert validated.current_stage == "Stage 5"
    assert validated.current_feature == "STAGE5-F003"
    assert validated.contract_status == "in_progress"
    assert validated.contract_approval_decision == "pending_contract_review"
    assert validated.completed_stage5_features == ("STAGE5-F001", "STAGE5-F002")
    assert validated.previous_protocol_feature == "STAGE5-F002"
    assert validated.previous_protocol_status == "completed"
    assert validated.next_feature == "STAGE5-F004"
    assert validated.contract_record_level == "donor"
    assert validated.contract_split_level == "donor"
    assert validated.contract_label_level == "donor"
    assert validated.contract_prediction_level == "donor"
    assert validated.split_policy == "donor_level_only"
    assert validated.leakage_policy == "cell_level_split_forbidden"
    assert validated.contract_scope_policy == "contract_review_only_no_execution"
    assert validated.artifact_loading_policy == "prohibited_until_explicit_gate"
    assert validated.input_materialization_policy == "prohibited_until_explicit_gate"
    assert validated.label_creation_policy == "prohibited_until_explicit_gate"
    assert validated.split_execution_policy == "prohibited_until_explicit_gate"
    assert validated.modeling_execution_policy == "prohibited_until_explicit_gate"
    assert validated.prediction_generation_policy == "prohibited_until_explicit_gate"
    assert validated.metric_computation_policy == "future_only_no_computation"
    assert validated.requires_pre_execution_audit is True
    assert validated.allow_input_materialization is False
    assert validated.allow_split_execution is False
    assert validated.allow_model_fitting is False
    assert validated.allow_prediction_generation is False
    assert validated.allow_metric_computation is False
    assert validated.modeling_authorization_granted is False
    assert validated.modeling_allowed is False
    assert validated.performance_claims_added is False
    assert validated.notes == "donor contract only"


def test_stage5_contract_from_mapping_normalizes_values():
    contract = stage5_donor_level_execution_contract_approval_from_mapping(
        {
            "contract_approval_decision": "blocked_pending_review",
            "notes": "  normalized  ",
        }
    )

    assert contract.current_feature == "STAGE5-F003"
    assert contract.contract_approval_decision == "blocked_pending_review"
    assert contract.completed_stage5_features == STAGE5_PREVIOUS_FEATURES
    assert contract.notes == "normalized"


def test_stage5_contract_rejects_wrong_current_feature():
    with pytest.raises(
        Stage5DonorLevelExecutionContractApprovalError,
        match="current_feature",
    ):
        validate_stage5_donor_level_execution_contract_approval(
            _contract(current_feature="STAGE5-F002")
        )


@pytest.mark.parametrize(
    ("field_name", "invalid_value"),
    [
        ("previous_protocol_feature", "STAGE5-F001"),
        ("previous_protocol_status", "pending"),
        ("next_feature", "STAGE5-F005"),
        ("contract_record_level", "cell"),
        ("contract_split_level", "cell"),
        ("contract_label_level", "cell"),
        ("contract_prediction_level", "cell"),
    ],
)
def test_stage5_contract_requires_expected_chain_and_donor_record_levels(
    field_name,
    invalid_value,
):
    with pytest.raises(Stage5DonorLevelExecutionContractApprovalError, match=field_name):
        validate_stage5_donor_level_execution_contract_approval(
            _contract(**{field_name: invalid_value})
        )


def test_stage5_contract_requires_completed_f001_and_f002():
    with pytest.raises(
        Stage5DonorLevelExecutionContractApprovalError,
        match="completed_stage5_features",
    ):
        validate_stage5_donor_level_execution_contract_approval(
            _contract(completed_stage5_features=("STAGE5-F001",))
        )


@pytest.mark.parametrize(
    ("field_name", "invalid_value"),
    [
        ("split_policy", CELL_LEVEL_SPLIT_FORBIDDEN),
        ("leakage_policy", DONOR_LEVEL_ONLY),
        ("artifact_loading_policy", FUTURE_ONLY_NO_COMPUTATION),
        ("input_materialization_policy", FUTURE_ONLY_NO_COMPUTATION),
        ("label_creation_policy", FUTURE_ONLY_NO_COMPUTATION),
        ("split_execution_policy", FUTURE_ONLY_NO_COMPUTATION),
        ("aggregation_execution_policy", FUTURE_ONLY_NO_COMPUTATION),
        ("modeling_execution_policy", FUTURE_ONLY_NO_COMPUTATION),
        ("prediction_generation_policy", FUTURE_ONLY_NO_COMPUTATION),
        ("metric_computation_policy", PROHIBITED_UNTIL_EXPLICIT_GATE),
        ("external_validation_policy", FUTURE_ONLY_NO_COMPUTATION),
        ("performance_claim_policy", FUTURE_ONLY_NO_COMPUTATION),
    ],
)
def test_stage5_contract_rejects_unsafe_policy_changes(field_name, invalid_value):
    with pytest.raises(Stage5DonorLevelExecutionContractApprovalError):
        validate_stage5_donor_level_execution_contract_approval(
            _contract(**{field_name: invalid_value})
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
        "requires_pre_execution_audit",
    ],
)
def test_stage5_contract_requires_review_and_execution_gates(required_gate):
    with pytest.raises(Stage5DonorLevelExecutionContractApprovalError, match="required"):
        validate_stage5_donor_level_execution_contract_approval(
            _contract(**{required_gate: False})
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
def test_stage5_contract_keeps_runtime_and_modeling_flags_disabled(flag_name):
    with pytest.raises(Stage5DonorLevelExecutionContractApprovalError):
        validate_stage5_donor_level_execution_contract_approval(
            _contract(**{flag_name: True})
        )


def test_stage5_contract_to_dict_serializes_completed_features_as_list():
    serialized = stage5_donor_level_execution_contract_approval_to_dict(_contract())

    assert serialized["current_feature"] == "STAGE5-F003"
    assert serialized["completed_stage5_features"] == ["STAGE5-F001", "STAGE5-F002"]
    assert serialized["contract_record_level"] == "donor"
    assert serialized["split_policy"] == "donor_level_only"
    assert serialized["modeling_authorization_granted"] is False
    assert serialized["modeling_allowed"] is False
    assert serialized["allow_metric_computation"] is False
    assert serialized["performance_claims_allowed"] is False


def test_stage5_contract_summary_does_not_authorize_execution():
    summary = stage5_donor_level_execution_contract_summary(_contract())

    assert summary == {
        "current_stage": "Stage 5",
        "current_feature": "STAGE5-F003",
        "contract_status": "in_progress",
        "contract_approval_decision": "pending_contract_review",
        "previous_protocol_feature": "STAGE5-F002",
        "next_feature": "STAGE5-F004",
        "contract_record_level": "donor",
        "contract_split_level": "donor",
        "contract_label_level": "donor",
        "contract_prediction_level": "donor",
        "split_policy": "donor_level_only",
        "leakage_policy": "cell_level_split_forbidden",
        "requires_pre_execution_audit": True,
        "modeling_authorization_granted": False,
        "modeling_allowed": False,
        "training_allowed": False,
        "performance_claims_allowed": False,
        "performance_claims_added": False,
    }


def test_stage5_contract_module_has_no_runtime_or_modeling_imports():
    import lupusfm.evaluation.stage5_donor_level_execution_contract_approval as contract_module

    source = contract_module.__loader__.get_source(contract_module.__name__).lower()
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
