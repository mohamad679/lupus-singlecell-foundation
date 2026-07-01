import pytest

from lupusfm.evaluation.readiness import (
    APPROVED_FOR_REAL_DATA_VALIDATION,
    BASELINE_CONTROL_PLAN,
    EMBEDDING_ARTIFACT_SCHEMA,
    EVALUATION_PROTOCOL_SCAFFOLD,
    LEAKAGE_SAFE_SPLITS,
    PATIENT_AGGREGATION_DESIGN,
    REQUIRED_STAGE3_COMPONENTS,
    STAGE3_CURRENT_FEATURE,
    ModelingReadinessGate,
    ModelingReadinessGateError,
    ReadinessComponentStatus,
    modeling_readiness_gate_from_mapping,
    modeling_readiness_gate_to_dict,
    validate_modeling_readiness_gate,
    validate_readiness_component_status,
    validate_readiness_components,
)


def _components():
    return (
        ReadinessComponentStatus(EMBEDDING_ARTIFACT_SCHEMA),
        ReadinessComponentStatus(PATIENT_AGGREGATION_DESIGN),
        ReadinessComponentStatus(LEAKAGE_SAFE_SPLITS),
        ReadinessComponentStatus(EVALUATION_PROTOCOL_SCAFFOLD),
        ReadinessComponentStatus(BASELINE_CONTROL_PLAN),
    )


def _valid_gate(**overrides):
    values = {
        "current_feature": STAGE3_CURRENT_FEATURE,
        "split_level": "patient",
        "components": _components(),
        "notes": "  readiness only  ",
    }
    values.update(overrides)
    return ModelingReadinessGate(**values)


def test_modeling_readiness_gate_accepts_completed_stage3_contract():
    gate = _valid_gate()

    validated = validate_modeling_readiness_gate(gate)

    assert validated.current_feature == "STAGE3-F006"
    assert validated.split_level == "patient"
    assert validated.readiness_decision == APPROVED_FOR_REAL_DATA_VALIDATION
    assert validated.next_step == "real_embedding_artifact_validation"
    assert {component.name for component in validated.components} == set(
        REQUIRED_STAGE3_COMPONENTS
    )
    assert all(component.status == "completed" for component in validated.components)
    assert validated.require_embedding_artifact_schema is True
    assert validated.require_patient_aggregation_design is True
    assert validated.require_leakage_safe_splits is True
    assert validated.require_evaluation_protocol_scaffold is True
    assert validated.require_baseline_control_plan is True
    assert validated.require_patient_level_unit is True
    assert validated.require_same_splits_for_candidate_and_baselines is True
    assert validated.require_fold_internal_preprocessing is True
    assert validated.require_uncertainty_plan is True
    assert validated.require_permutation_plan is True
    assert validated.allow_real_data_validation_next_stage is True
    assert validated.allow_real_artifact_loading is False
    assert validated.allow_anndata_loading is False
    assert validated.allow_embedding_extraction is False
    assert validated.allow_model_fitting is False
    assert validated.allow_metric_computation is False
    assert validated.allow_modeling is False
    assert validated.allow_training is False
    assert validated.performance_claims_added is False
    assert validated.notes == "readiness only"


@pytest.mark.parametrize("split_level", ["patient", "donor"])
def test_modeling_readiness_gate_accepts_patient_or_donor_level(split_level):
    validated = validate_modeling_readiness_gate(_valid_gate(split_level=split_level))

    assert validated.split_level == split_level


def test_readiness_component_status_normalizes_mapping():
    component = validate_readiness_component_status(
        {
            "name": " embedding_artifact_schema ",
            "status": " completed ",
            "evidence": " full suite passed ",
            "required": "true",
            "notes": "  ok  ",
        }
    )

    assert component == ReadinessComponentStatus(
        name=EMBEDDING_ARTIFACT_SCHEMA,
        status="completed",
        evidence="full suite passed",
        required=True,
        notes="ok",
    )


def test_readiness_components_require_all_stage3_components():
    with pytest.raises(ModelingReadinessGateError, match="all required Stage 3"):
        validate_readiness_components(
            [
                ReadinessComponentStatus(EMBEDDING_ARTIFACT_SCHEMA),
                ReadinessComponentStatus(PATIENT_AGGREGATION_DESIGN),
            ]
        )


def test_readiness_components_reject_incomplete_required_component():
    components = list(_components())
    components[0] = ReadinessComponentStatus(
        EMBEDDING_ARTIFACT_SCHEMA,
        status="in_progress",
    )

    with pytest.raises(ModelingReadinessGateError, match="must be completed"):
        validate_readiness_components(components)


def test_readiness_components_reject_duplicate_component_names():
    with pytest.raises(ModelingReadinessGateError, match="names must be unique"):
        validate_readiness_components(
            [
                ReadinessComponentStatus(EMBEDDING_ARTIFACT_SCHEMA),
                ReadinessComponentStatus(EMBEDDING_ARTIFACT_SCHEMA),
                ReadinessComponentStatus(PATIENT_AGGREGATION_DESIGN),
                ReadinessComponentStatus(LEAKAGE_SAFE_SPLITS),
                ReadinessComponentStatus(EVALUATION_PROTOCOL_SCAFFOLD),
                ReadinessComponentStatus(BASELINE_CONTROL_PLAN),
            ]
        )


def test_readiness_gate_rejects_wrong_current_feature():
    with pytest.raises(ModelingReadinessGateError, match="current_feature"):
        validate_modeling_readiness_gate(_valid_gate(current_feature="STAGE3-F005"))


def test_readiness_gate_rejects_cell_level_split():
    with pytest.raises(ModelingReadinessGateError, match="split_level must be one of"):
        validate_modeling_readiness_gate(_valid_gate(split_level="cell"))


def test_readiness_gate_rejects_blocked_decision():
    with pytest.raises(ModelingReadinessGateError, match="must approve"):
        validate_modeling_readiness_gate(
            _valid_gate(readiness_decision="blocked_pending_stage3_components")
        )


@pytest.mark.parametrize(
    "requirement_name",
    [
        "require_embedding_artifact_schema",
        "require_patient_aggregation_design",
        "require_leakage_safe_splits",
        "require_evaluation_protocol_scaffold",
        "require_baseline_control_plan",
        "require_patient_level_unit",
        "require_same_splits_for_candidate_and_baselines",
        "require_fold_internal_preprocessing",
        "require_uncertainty_plan",
        "require_permutation_plan",
        "allow_real_data_validation_next_stage",
    ],
)
def test_readiness_gate_keeps_required_conditions_enabled(requirement_name):
    with pytest.raises(ModelingReadinessGateError):
        validate_modeling_readiness_gate(_valid_gate(**{requirement_name: False}))


@pytest.mark.parametrize(
    "flag_name",
    [
        "allow_cell_level_split",
        "allow_cell_level_features",
        "allow_real_artifact_loading",
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
def test_readiness_gate_keeps_forbidden_runtime_flags_disabled(flag_name):
    with pytest.raises(ModelingReadinessGateError):
        validate_modeling_readiness_gate(_valid_gate(**{flag_name: True}))


def test_modeling_readiness_gate_from_mapping_uses_safe_defaults():
    gate = modeling_readiness_gate_from_mapping(
        {
            "split_level": "donor",
            "next_step": "controlled_embedding_extraction",
            "notes": "  normalized  ",
        }
    )

    assert gate.current_feature == "STAGE3-F006"
    assert gate.split_level == "donor"
    assert gate.next_step == "controlled_embedding_extraction"
    assert gate.readiness_decision == APPROVED_FOR_REAL_DATA_VALIDATION
    assert {component.name for component in gate.components} == set(
        REQUIRED_STAGE3_COMPONENTS
    )
    assert gate.allow_modeling is False
    assert gate.allow_training is False
    assert gate.notes == "normalized"


def test_modeling_readiness_gate_from_mapping_rejects_non_sequence_components():
    with pytest.raises(ModelingReadinessGateError, match="components must be a sequence"):
        modeling_readiness_gate_from_mapping(
            {
                "components": "embedding_artifact_schema",
            }
        )


def test_modeling_readiness_gate_to_dict_validates_before_serializing():
    serialized = modeling_readiness_gate_to_dict(_valid_gate())

    assert serialized["current_feature"] == "STAGE3-F006"
    assert serialized["readiness_decision"] == APPROVED_FOR_REAL_DATA_VALIDATION
    assert serialized["components"][0]["status"] == "completed"
    assert serialized["allow_modeling"] is False
    assert serialized["performance_claims_added"] is False


def test_modeling_readiness_gate_module_has_no_execution_imports():
    import lupusfm.evaluation.readiness as readiness_module

    source = readiness_module.__loader__.get_source(
        readiness_module.__name__,
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
