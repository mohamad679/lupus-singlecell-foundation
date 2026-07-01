import pytest

from lupusfm.evaluation.stage4_modeling_handoff_decision import (
    REQUIRED_COMPLETED_FEATURES,
    SEPARATE_MODELING_STAGE_REQUIRED,
    STAGE4_FINAL_FEATURE,
    Stage4ModelingHandoffDecision,
    Stage4ModelingHandoffDecisionError,
    stage4_handoff_summary,
    stage4_modeling_handoff_decision_from_mapping,
    stage4_modeling_handoff_decision_to_dict,
    validate_stage4_modeling_handoff_decision,
)


def _decision(**overrides):
    values = {
        "current_feature": STAGE4_FINAL_FEATURE,
        "stage4_status": "completed",
        "decision_status": "completed",
        "handoff_decision": SEPARATE_MODELING_STAGE_REQUIRED,
        "completed_features": REQUIRED_COMPLETED_FEATURES,
        "artifact_validation_status": "completed",
        "aggregation_plan_status": "completed",
        "split_manifest_validation_status": "completed",
        "evaluation_input_readiness_status": "completed",
        "pre_modeling_audit_status": "completed",
        "notes": "  final Stage 4 closeout  ",
    }
    values.update(overrides)
    return Stage4ModelingHandoffDecision(**values)


def test_stage4_handoff_accepts_completed_stage4_without_modeling_permission():
    validated = validate_stage4_modeling_handoff_decision(_decision())

    assert validated.current_feature == "STAGE4-F006"
    assert validated.stage4_status == "completed"
    assert validated.decision_status == "completed"
    assert validated.handoff_decision == "separate_modeling_stage_required"
    assert validated.completed_features == (
        "STAGE4-F001",
        "STAGE4-F002",
        "STAGE4-F003",
        "STAGE4-F004",
        "STAGE4-F005",
    )
    assert validated.artifact_validation_status == "completed"
    assert validated.aggregation_plan_status == "completed"
    assert validated.split_manifest_validation_status == "completed"
    assert validated.evaluation_input_readiness_status == "completed"
    assert validated.pre_modeling_audit_status == "completed"
    assert validated.requires_separate_modeling_stage is True
    assert validated.requires_explicit_modeling_approval is True
    assert validated.allow_npy_payload_loading is False
    assert validated.allow_input_materialization is False
    assert validated.allow_model_fitting is False
    assert validated.allow_prediction_generation is False
    assert validated.allow_metric_computation is False
    assert validated.modeling_authorization_granted is False
    assert validated.modeling_allowed is False
    assert validated.training_allowed is False
    assert validated.performance_claims_added is False
    assert validated.notes == "final Stage 4 closeout"


def test_stage4_handoff_from_mapping_normalizes_decision():
    decision = stage4_modeling_handoff_decision_from_mapping(
        {
            "handoff_decision": "blocked_pending_human_review",
            "notes": "  normalized  ",
        }
    )

    assert decision.current_feature == "STAGE4-F006"
    assert decision.handoff_decision == "blocked_pending_human_review"
    assert decision.completed_features == REQUIRED_COMPLETED_FEATURES
    assert decision.notes == "normalized"


def test_stage4_handoff_rejects_wrong_current_feature():
    with pytest.raises(Stage4ModelingHandoffDecisionError, match="current_feature"):
        validate_stage4_modeling_handoff_decision(
            _decision(current_feature="STAGE4-F005")
        )


@pytest.mark.parametrize(
    "status_field",
    [
        "artifact_validation_status",
        "aggregation_plan_status",
        "split_manifest_validation_status",
        "evaluation_input_readiness_status",
        "pre_modeling_audit_status",
    ],
)
def test_stage4_handoff_requires_completed_upstream_statuses(status_field):
    with pytest.raises(Stage4ModelingHandoffDecisionError, match=status_field):
        validate_stage4_modeling_handoff_decision(
            _decision(**{status_field: "pending"})
        )


def test_stage4_handoff_rejects_missing_completed_feature():
    with pytest.raises(Stage4ModelingHandoffDecisionError, match="completed_features"):
        validate_stage4_modeling_handoff_decision(
            _decision(completed_features=("STAGE4-F001", "STAGE4-F002"))
        )


@pytest.mark.parametrize(
    "required_gate",
    [
        "requires_separate_modeling_stage",
        "requires_new_branch_for_modeling",
        "requires_explicit_modeling_approval",
        "requires_human_review_before_modeling",
        "requires_reproducibility_review",
        "requires_leakage_review",
        "requires_artifact_integrity_review",
        "requires_scope_review",
    ],
)
def test_stage4_handoff_requires_review_and_separate_stage_gates(required_gate):
    with pytest.raises(Stage4ModelingHandoffDecisionError, match="required"):
        validate_stage4_modeling_handoff_decision(
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
        "modeling_authorization_granted",
        "modeling_allowed",
        "training_allowed",
        "external_validation_allowed",
        "performance_claims_allowed",
        "performance_claims_added",
    ],
)
def test_stage4_handoff_keeps_forbidden_flags_disabled(flag_name):
    with pytest.raises(Stage4ModelingHandoffDecisionError):
        validate_stage4_modeling_handoff_decision(_decision(**{flag_name: True}))


def test_stage4_handoff_to_dict_serializes_completed_features_as_list():
    serialized = stage4_modeling_handoff_decision_to_dict(_decision())

    assert serialized["current_feature"] == "STAGE4-F006"
    assert serialized["completed_features"] == [
        "STAGE4-F001",
        "STAGE4-F002",
        "STAGE4-F003",
        "STAGE4-F004",
        "STAGE4-F005",
    ]
    assert serialized["modeling_authorization_granted"] is False
    assert serialized["modeling_allowed"] is False
    assert serialized["allow_metric_computation"] is False
    assert serialized["performance_claims_allowed"] is False


def test_stage4_handoff_summary_does_not_authorize_modeling():
    summary = stage4_handoff_summary(_decision())

    assert summary == {
        "current_feature": "STAGE4-F006",
        "stage4_status": "completed",
        "decision_status": "completed",
        "handoff_decision": "separate_modeling_stage_required",
        "completed_features": [
            "STAGE4-F001",
            "STAGE4-F002",
            "STAGE4-F003",
            "STAGE4-F004",
            "STAGE4-F005",
        ],
        "requires_separate_modeling_stage": True,
        "requires_explicit_modeling_approval": True,
        "modeling_authorization_granted": False,
        "modeling_allowed": False,
        "training_allowed": False,
        "performance_claims_allowed": False,
        "performance_claims_added": False,
        "next_phase": "separate_modeling_stage_requires_explicit_approval",
    }


def test_stage4_handoff_module_has_no_runtime_or_modeling_imports():
    import lupusfm.evaluation.stage4_modeling_handoff_decision as handoff_module

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
    ]

    assert not any(fragment in source for fragment in forbidden_fragments)
