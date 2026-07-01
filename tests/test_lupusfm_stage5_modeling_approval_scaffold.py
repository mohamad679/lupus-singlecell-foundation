import pytest

from lupusfm.evaluation.stage5_modeling_approval_scaffold import (
    REQUIRED_COMPLETED_STAGE4_FEATURES,
    SEPARATE_MODELING_STAGE_REQUIRED,
    STAGE5_CURRENT_FEATURE,
    Stage5ModelingApprovalScaffold,
    Stage5ModelingApprovalScaffoldError,
    stage5_modeling_approval_scaffold_from_mapping,
    stage5_modeling_approval_scaffold_to_dict,
    stage5_modeling_approval_summary,
    validate_stage5_modeling_approval_scaffold,
)


def _scaffold(**overrides):
    values = {
        "current_stage": "Stage 5",
        "current_feature": STAGE5_CURRENT_FEATURE,
        "stage5_status": "in_progress",
        "approval_status": "pending",
        "modeling_authorization_status": "not_granted",
        "upstream_stage4_status": "completed",
        "upstream_handoff_decision": SEPARATE_MODELING_STAGE_REQUIRED,
        "completed_stage4_features": REQUIRED_COMPLETED_STAGE4_FEATURES,
        "notes": "  Stage 5 scaffold only  ",
    }
    values.update(overrides)
    return Stage5ModelingApprovalScaffold(**values)


def test_stage5_scaffold_accepts_planning_without_modeling_permission():
    validated = validate_stage5_modeling_approval_scaffold(_scaffold())

    assert validated.current_stage == "Stage 5"
    assert validated.current_feature == "STAGE5-F001"
    assert validated.stage5_status == "in_progress"
    assert validated.approval_status == "pending"
    assert validated.modeling_authorization_status == "not_granted"
    assert validated.upstream_stage4_status == "completed"
    assert validated.upstream_handoff_decision == "separate_modeling_stage_required"
    assert validated.completed_stage4_features == (
        "STAGE4-F001",
        "STAGE4-F002",
        "STAGE4-F003",
        "STAGE4-F004",
        "STAGE4-F005",
        "STAGE4-F006",
    )
    assert validated.requires_explicit_modeling_approval is True
    assert validated.requires_protocol_before_execution is True
    assert validated.requires_donor_level_only is True
    assert validated.forbids_cell_level_split is True
    assert validated.allow_npy_payload_loading is False
    assert validated.allow_input_materialization is False
    assert validated.allow_model_fitting is False
    assert validated.allow_prediction_generation is False
    assert validated.allow_metric_computation is False
    assert validated.modeling_authorization_granted is False
    assert validated.modeling_allowed is False
    assert validated.training_allowed is False
    assert validated.performance_claims_added is False
    assert validated.notes == "Stage 5 scaffold only"


def test_stage5_scaffold_from_mapping_normalizes_values():
    scaffold = stage5_modeling_approval_scaffold_from_mapping(
        {
            "modeling_authorization_status": "blocked_pending_human_review",
            "notes": "  normalized  ",
        }
    )

    assert scaffold.current_feature == "STAGE5-F001"
    assert scaffold.modeling_authorization_status == "blocked_pending_human_review"
    assert scaffold.completed_stage4_features == REQUIRED_COMPLETED_STAGE4_FEATURES
    assert scaffold.notes == "normalized"


def test_stage5_scaffold_rejects_wrong_current_stage():
    with pytest.raises(Stage5ModelingApprovalScaffoldError, match="current_stage"):
        validate_stage5_modeling_approval_scaffold(_scaffold(current_stage="Stage 4"))


def test_stage5_scaffold_rejects_wrong_current_feature():
    with pytest.raises(Stage5ModelingApprovalScaffoldError, match="current_feature"):
        validate_stage5_modeling_approval_scaffold(
            _scaffold(current_feature="STAGE4-F006")
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "upstream_stage4_status",
        "upstream_handoff_decision",
    ],
)
def test_stage5_scaffold_requires_completed_stage4_handoff(field_name):
    invalid = {
        "upstream_stage4_status": "pending",
        "upstream_handoff_decision": "blocked",
    }

    with pytest.raises(Stage5ModelingApprovalScaffoldError, match=field_name):
        validate_stage5_modeling_approval_scaffold(
            _scaffold(**{field_name: invalid[field_name]})
        )


def test_stage5_scaffold_requires_all_completed_stage4_features():
    with pytest.raises(
        Stage5ModelingApprovalScaffoldError,
        match="completed_stage4_features",
    ):
        validate_stage5_modeling_approval_scaffold(
            _scaffold(completed_stage4_features=("STAGE4-F001", "STAGE4-F002"))
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
        "requires_protocol_before_execution",
        "requires_donor_level_only",
        "forbids_cell_level_split",
        "requires_no_large_artifact_commit",
    ],
)
def test_stage5_scaffold_requires_approval_and_leakage_gates(required_gate):
    with pytest.raises(Stage5ModelingApprovalScaffoldError, match="required"):
        validate_stage5_modeling_approval_scaffold(
            _scaffold(**{required_gate: False})
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
def test_stage5_scaffold_keeps_runtime_and_modeling_flags_disabled(flag_name):
    with pytest.raises(Stage5ModelingApprovalScaffoldError):
        validate_stage5_modeling_approval_scaffold(_scaffold(**{flag_name: True}))


def test_stage5_scaffold_to_dict_serializes_stage4_features_as_list():
    serialized = stage5_modeling_approval_scaffold_to_dict(_scaffold())

    assert serialized["current_feature"] == "STAGE5-F001"
    assert serialized["completed_stage4_features"] == [
        "STAGE4-F001",
        "STAGE4-F002",
        "STAGE4-F003",
        "STAGE4-F004",
        "STAGE4-F005",
        "STAGE4-F006",
    ]
    assert serialized["modeling_authorization_granted"] is False
    assert serialized["modeling_allowed"] is False
    assert serialized["allow_metric_computation"] is False
    assert serialized["performance_claims_allowed"] is False


def test_stage5_scaffold_summary_does_not_authorize_modeling():
    summary = stage5_modeling_approval_summary(_scaffold())

    assert summary == {
        "current_stage": "Stage 5",
        "current_feature": "STAGE5-F001",
        "stage5_status": "in_progress",
        "approval_status": "pending",
        "modeling_authorization_status": "not_granted",
        "upstream_handoff_decision": "separate_modeling_stage_required",
        "requires_explicit_modeling_approval": True,
        "requires_protocol_before_execution": True,
        "requires_donor_level_only": True,
        "forbids_cell_level_split": True,
        "modeling_authorization_granted": False,
        "modeling_allowed": False,
        "training_allowed": False,
        "performance_claims_allowed": False,
        "performance_claims_added": False,
    }


def test_stage5_scaffold_module_has_no_runtime_or_modeling_imports():
    import lupusfm.evaluation.stage5_modeling_approval_scaffold as scaffold_module

    source = scaffold_module.__loader__.get_source(scaffold_module.__name__).lower()
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
