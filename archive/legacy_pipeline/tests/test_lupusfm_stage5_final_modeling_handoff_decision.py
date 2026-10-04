import pytest

from lupusfm.evaluation.stage5_final_modeling_handoff_decision import (
    CELL_LEVEL_SPLIT_FORBIDDEN,
    DONOR_LEVEL_ONLY,
    FUTURE_ONLY_EXPLICIT_STAGE,
    FUTURE_ONLY_NO_COMPUTATION,
    PROHIBITED_UNTIL_EXPLICIT_GATE,
    SEPARATE_EXECUTION_STAGE_REQUIRED,
    STAGE5_CURRENT_FEATURE,
    STAGE5_PREVIOUS_FEATURES,
    Stage5FinalModelingHandoffDecision,
    Stage5FinalModelingHandoffDecisionError,
    stage5_final_modeling_handoff_decision_from_mapping,
    stage5_final_modeling_handoff_decision_to_dict,
    stage5_final_modeling_handoff_summary,
    validate_stage5_final_modeling_handoff_decision,
)


def _decision(**overrides):
    values = {
        "current_stage": "Stage 5",
        "current_feature": STAGE5_CURRENT_FEATURE,
        "stage5_status": "in_progress",
        "handoff_status": "in_progress",
        "handoff_decision": SEPARATE_EXECUTION_STAGE_REQUIRED,
        "modeling_authorization_status": "stage5_does_not_authorize_modeling",
        "future_modeling_policy": FUTURE_ONLY_EXPLICIT_STAGE,
        "completed_stage5_features": STAGE5_PREVIOUS_FEATURES,
        "previous_audit_feature": "STAGE5-F004",
        "previous_audit_status": "completed",
        "notes": "  final handoff only  ",
    }
    values.update(overrides)
    return Stage5FinalModelingHandoffDecision(**values)


def test_stage5_final_handoff_accepts_safe_separate_execution_stage_decision():
    validated = validate_stage5_final_modeling_handoff_decision(_decision())

    assert validated.current_stage == "Stage 5"
    assert validated.current_feature == "STAGE5-F005"
    assert validated.handoff_status == "in_progress"
    assert validated.handoff_decision == "separate_modeling_execution_stage_required"
    assert validated.modeling_authorization_status == "stage5_does_not_authorize_modeling"
    assert validated.future_modeling_policy == "future_only_explicit_execution_stage"
    assert validated.completed_stage5_features == (
        "STAGE5-F001",
        "STAGE5-F002",
        "STAGE5-F003",
        "STAGE5-F004",
    )
    assert validated.previous_audit_feature == "STAGE5-F004"
    assert validated.previous_audit_status == "completed"
    assert validated.handoff_record_level == "donor"
    assert validated.split_policy == "donor_level_only"
    assert validated.leakage_policy == "cell_level_split_forbidden"
    assert validated.handoff_scope_policy == "handoff_only_no_execution"
    assert validated.artifact_loading_policy == "prohibited_until_explicit_gate"
    assert validated.input_materialization_policy == "prohibited_until_explicit_gate"
    assert validated.label_creation_policy == "prohibited_until_explicit_gate"
    assert validated.split_execution_policy == "prohibited_until_explicit_gate"
    assert validated.modeling_execution_policy == "prohibited_until_explicit_gate"
    assert validated.prediction_generation_policy == "prohibited_until_explicit_gate"
    assert validated.metric_computation_policy == "future_only_no_computation"
    assert validated.requires_separate_execution_stage is True
    assert validated.allow_input_materialization is False
    assert validated.allow_split_execution is False
    assert validated.allow_model_fitting is False
    assert validated.allow_prediction_generation is False
    assert validated.allow_metric_computation is False
    assert validated.modeling_authorization_granted is False
    assert validated.modeling_allowed is False
    assert validated.performance_claims_added is False
    assert validated.notes == "final handoff only"


def test_stage5_final_handoff_from_mapping_normalizes_values():
    decision = stage5_final_modeling_handoff_decision_from_mapping(
        {
            "modeling_authorization_status": "not_granted",
            "notes": "  normalized  ",
        }
    )

    assert decision.current_feature == "STAGE5-F005"
    assert decision.handoff_decision == "separate_modeling_execution_stage_required"
    assert decision.future_modeling_policy == "future_only_explicit_execution_stage"
    assert decision.modeling_authorization_status == "not_granted"
    assert decision.completed_stage5_features == STAGE5_PREVIOUS_FEATURES
    assert decision.notes == "normalized"


def test_stage5_final_handoff_rejects_wrong_current_feature():
    with pytest.raises(Stage5FinalModelingHandoffDecisionError, match="current_feature"):
        validate_stage5_final_modeling_handoff_decision(
            _decision(current_feature="STAGE5-F004")
        )


@pytest.mark.parametrize(
    ("field_name", "invalid_value"),
    [
        ("handoff_decision", "modeling_authorized_in_stage5"),
        ("future_modeling_policy", "execute_in_current_stage"),
        ("previous_audit_feature", "STAGE5-F003"),
        ("previous_audit_status", "pending"),
        ("handoff_record_level", "cell"),
    ],
)
def test_stage5_final_handoff_requires_safe_chain_and_decision(
    field_name,
    invalid_value,
):
    with pytest.raises(Stage5FinalModelingHandoffDecisionError, match=field_name):
        validate_stage5_final_modeling_handoff_decision(
            _decision(**{field_name: invalid_value})
        )


def test_stage5_final_handoff_requires_completed_f001_through_f004():
    with pytest.raises(
        Stage5FinalModelingHandoffDecisionError,
        match="completed_stage5_features",
    ):
        validate_stage5_final_modeling_handoff_decision(
            _decision(
                completed_stage5_features=(
                    "STAGE5-F001",
                    "STAGE5-F002",
                    "STAGE5-F003",
                )
            )
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
def test_stage5_final_handoff_rejects_unsafe_policy_changes(field_name, invalid_value):
    with pytest.raises(Stage5FinalModelingHandoffDecisionError):
        validate_stage5_final_modeling_handoff_decision(
            _decision(**{field_name: invalid_value})
        )


@pytest.mark.parametrize(
    "required_gate",
    [
        "requires_explicit_modeling_approval",
        "requires_separate_execution_stage",
        "requires_human_review_before_modeling",
        "requires_reproducibility_review",
        "requires_leakage_review",
        "requires_artifact_integrity_review",
        "requires_scope_review",
        "requires_donor_level_only",
        "forbids_cell_level_split",
        "requires_no_large_artifact_commit",
        "requires_protocol_before_execution",
    ],
)
def test_stage5_final_handoff_requires_all_review_and_execution_stage_gates(
    required_gate,
):
    with pytest.raises(Stage5FinalModelingHandoffDecisionError, match="required"):
        validate_stage5_final_modeling_handoff_decision(
            _decision(**{required_gate: False})
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
def test_stage5_final_handoff_keeps_runtime_and_modeling_flags_disabled(flag_name):
    with pytest.raises(Stage5FinalModelingHandoffDecisionError):
        validate_stage5_final_modeling_handoff_decision(
            _decision(**{flag_name: True})
        )


def test_stage5_final_handoff_to_dict_serializes_completed_features_as_list():
    serialized = stage5_final_modeling_handoff_decision_to_dict(_decision())

    assert serialized["current_feature"] == "STAGE5-F005"
    assert serialized["handoff_decision"] == "separate_modeling_execution_stage_required"
    assert serialized["future_modeling_policy"] == "future_only_explicit_execution_stage"
    assert serialized["completed_stage5_features"] == [
        "STAGE5-F001",
        "STAGE5-F002",
        "STAGE5-F003",
        "STAGE5-F004",
    ]
    assert serialized["handoff_record_level"] == "donor"
    assert serialized["modeling_authorization_granted"] is False
    assert serialized["modeling_allowed"] is False
    assert serialized["allow_metric_computation"] is False
    assert serialized["performance_claims_allowed"] is False


def test_stage5_final_handoff_summary_does_not_authorize_execution():
    summary = stage5_final_modeling_handoff_summary(_decision())

    assert summary == {
        "current_stage": "Stage 5",
        "current_feature": "STAGE5-F005",
        "handoff_status": "in_progress",
        "handoff_decision": "separate_modeling_execution_stage_required",
        "modeling_authorization_status": "stage5_does_not_authorize_modeling",
        "future_modeling_policy": "future_only_explicit_execution_stage",
        "previous_audit_feature": "STAGE5-F004",
        "handoff_record_level": "donor",
        "split_policy": "donor_level_only",
        "leakage_policy": "cell_level_split_forbidden",
        "requires_separate_execution_stage": True,
        "modeling_authorization_granted": False,
        "modeling_allowed": False,
        "training_allowed": False,
        "performance_claims_allowed": False,
        "performance_claims_added": False,
    }


def test_stage5_final_handoff_module_has_no_runtime_or_modeling_imports():
    import lupusfm.evaluation.stage5_final_modeling_handoff_decision as handoff_module

    source = handoff_module.__loader__.get_source(handoff_module.__name__).lower()
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
