import pytest

from lupusfm.evaluation.real_pre_modeling_audit import (
    REQUIRED_COMPLETED_FEATURES,
    STAGE4_CURRENT_FEATURE,
    RealPreModelingAuditGate,
    RealPreModelingAuditGateError,
    pre_modeling_audit_summary,
    real_pre_modeling_audit_gate_from_mapping,
    real_pre_modeling_audit_gate_to_dict,
    validate_real_pre_modeling_audit_gate,
)


def _gate(**overrides):
    values = {
        "current_feature": STAGE4_CURRENT_FEATURE,
        "audit_status": "pending",
        "audit_outcome": "review_required",
        "completed_features": REQUIRED_COMPLETED_FEATURES,
        "artifact_validation_status": "completed",
        "aggregation_plan_status": "completed",
        "split_manifest_validation_status": "completed",
        "evaluation_input_readiness_status": "completed",
        "next_feature": "STAGE4-F006",
        "notes": "  pre-modeling audit only  ",
    }
    values.update(overrides)
    return RealPreModelingAuditGate(**values)


def test_real_pre_modeling_audit_accepts_completed_upstream_gates_without_permission():
    validated = validate_real_pre_modeling_audit_gate(_gate())

    assert validated.current_feature == "STAGE4-F005"
    assert validated.audit_status == "pending"
    assert validated.audit_outcome == "review_required"
    assert validated.completed_features == (
        "STAGE4-F001",
        "STAGE4-F002",
        "STAGE4-F003",
        "STAGE4-F004",
    )
    assert validated.artifact_validation_status == "completed"
    assert validated.aggregation_plan_status == "completed"
    assert validated.split_manifest_validation_status == "completed"
    assert validated.evaluation_input_readiness_status == "completed"
    assert validated.next_feature == "STAGE4-F006"
    assert validated.requires_human_review_before_modeling is True
    assert validated.requires_explicit_modeling_permission is True
    assert validated.allow_npy_payload_loading is False
    assert validated.allow_input_materialization is False
    assert validated.allow_model_fitting is False
    assert validated.allow_prediction_generation is False
    assert validated.allow_metric_computation is False
    assert validated.allow_modeling is False
    assert validated.allow_training is False
    assert validated.performance_claims_added is False
    assert validated.notes == "pre-modeling audit only"


def test_real_pre_modeling_audit_from_mapping_normalizes_values():
    gate = real_pre_modeling_audit_gate_from_mapping(
        {
            "audit_status": "validated",
            "audit_outcome": "blocked",
            "notes": "  normalized  ",
        }
    )

    assert gate.current_feature == "STAGE4-F005"
    assert gate.audit_status == "validated"
    assert gate.audit_outcome == "blocked"
    assert gate.completed_features == REQUIRED_COMPLETED_FEATURES
    assert gate.notes == "normalized"


def test_real_pre_modeling_audit_rejects_wrong_current_feature():
    with pytest.raises(RealPreModelingAuditGateError, match="current_feature"):
        validate_real_pre_modeling_audit_gate(_gate(current_feature="STAGE4-F004"))


@pytest.mark.parametrize(
    "status_field",
    [
        "artifact_validation_status",
        "aggregation_plan_status",
        "split_manifest_validation_status",
        "evaluation_input_readiness_status",
    ],
)
def test_real_pre_modeling_audit_requires_completed_upstream_statuses(status_field):
    with pytest.raises(RealPreModelingAuditGateError, match=status_field):
        validate_real_pre_modeling_audit_gate(_gate(**{status_field: "pending"}))


def test_real_pre_modeling_audit_rejects_missing_completed_feature():
    with pytest.raises(RealPreModelingAuditGateError, match="completed_features"):
        validate_real_pre_modeling_audit_gate(
            _gate(completed_features=("STAGE4-F001", "STAGE4-F002"))
        )


@pytest.mark.parametrize(
    "required_gate",
    [
        "requires_human_review_before_modeling",
        "requires_explicit_modeling_permission",
        "requires_reproducibility_review",
        "requires_leakage_review",
        "requires_artifact_integrity_review",
        "requires_scope_review",
    ],
)
def test_real_pre_modeling_audit_requires_review_gates_enabled(required_gate):
    with pytest.raises(RealPreModelingAuditGateError, match="required"):
        validate_real_pre_modeling_audit_gate(_gate(**{required_gate: False}))


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
        "allow_training",
        "allow_external_validation",
        "performance_claims_added",
    ],
)
def test_real_pre_modeling_audit_keeps_forbidden_flags_disabled(flag_name):
    with pytest.raises(RealPreModelingAuditGateError):
        validate_real_pre_modeling_audit_gate(_gate(**{flag_name: True}))


def test_real_pre_modeling_audit_to_dict_validates_before_serializing():
    serialized = real_pre_modeling_audit_gate_to_dict(_gate())

    assert serialized["current_feature"] == "STAGE4-F005"
    assert serialized["completed_features"] == [
        "STAGE4-F001",
        "STAGE4-F002",
        "STAGE4-F003",
        "STAGE4-F004",
    ]
    assert serialized["allow_model_fitting"] is False
    assert serialized["allow_metric_computation"] is False
    assert serialized["allow_modeling"] is False
    assert serialized["performance_claims_added"] is False


def test_pre_modeling_audit_summary_does_not_grant_modeling_permission():
    summary = pre_modeling_audit_summary(_gate())

    assert summary == {
        "current_feature": "STAGE4-F005",
        "audit_status": "pending",
        "audit_outcome": "review_required",
        "completed_features": [
            "STAGE4-F001",
            "STAGE4-F002",
            "STAGE4-F003",
            "STAGE4-F004",
        ],
        "requires_human_review_before_modeling": True,
        "requires_explicit_modeling_permission": True,
        "allow_modeling": False,
        "allow_metric_computation": False,
        "allow_training": False,
        "performance_claims_added": False,
        "next_feature": "STAGE4-F006",
    }


def test_real_pre_modeling_audit_module_has_no_runtime_or_modeling_imports():
    import lupusfm.evaluation.real_pre_modeling_audit as audit_module

    source = audit_module.__loader__.get_source(audit_module.__name__).lower()
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
