import pytest

from lupusfm.evaluation.stage6_real_artifact_access_integrity_gate import (
    DEFERRED_REAL_ARTIFACT_CHECKS,
    REQUIRED_INTEGRITY_CONTRACTS,
    STAGE6_CURRENT_FEATURE,
    Stage6RealArtifactAccessIntegrityGate,
    Stage6RealArtifactAccessIntegrityGateError,
    stage6_real_artifact_access_integrity_gate_from_mapping,
    stage6_real_artifact_access_integrity_gate_summary,
    stage6_real_artifact_access_integrity_gate_to_dict,
    validate_stage6_real_artifact_access_integrity_gate,
)


def _gate(**overrides):
    values = {
        "current_stage": "Stage 6",
        "current_feature": STAGE6_CURRENT_FEATURE,
        "stage6_status": "in_progress",
        "gate_status": "in_progress",
        "gate_decision": "metadata_access_integrity_gate_opened",
        "previous_feature": "STAGE6-F001",
        "previous_feature_status": "completed",
        "completed_stage6_features": ("STAGE6-F001",),
        "upstream_authorization_decision": (
            "stage6_controlled_execution_path_authorized"
        ),
        "notes": "  F002 metadata gate only  ",
    }
    values.update(overrides)
    return Stage6RealArtifactAccessIntegrityGate(**values)


def test_stage6_f002_accepts_metadata_only_artifact_access_integrity_gate():
    validated = validate_stage6_real_artifact_access_integrity_gate(_gate())

    assert validated.current_stage == "Stage 6"
    assert validated.current_feature == "STAGE6-F002"
    assert validated.gate_status == "in_progress"
    assert validated.gate_decision == "metadata_access_integrity_gate_opened"
    assert validated.previous_feature == "STAGE6-F001"
    assert validated.previous_feature_status == "completed"
    assert validated.completed_stage6_features == ("STAGE6-F001",)
    assert (
        validated.upstream_authorization_decision
        == "stage6_controlled_execution_path_authorized"
    )
    assert validated.access_scope == "path_schema_permission_contract_only"
    assert validated.integrity_scope == "metadata_integrity_contract_only"
    assert validated.expected_artifact_format == "npy_directory"
    assert validated.expected_artifact_layout == "one_file_per_donor_embedding"
    assert validated.expected_record_level == "donor"
    assert validated.expected_split_level == "donor"
    assert (
        validated.expected_artifact_location_policy
        == "external_local_or_remote_path_not_committed"
    )
    assert validated.required_integrity_contracts == REQUIRED_INTEGRITY_CONTRACTS
    assert validated.deferred_real_artifact_checks == DEFERRED_REAL_ARTIFACT_CHECKS
    assert validated.next_feature == "STAGE6-F003"
    assert validated.first_runtime_execution_feature == "STAGE6-F005"
    assert validated.requires_donor_level_only is True
    assert validated.forbids_cell_level_split is True
    assert validated.allow_artifact_path_contract_recording is True
    assert validated.allow_schema_contract_recording is True
    assert validated.allow_permission_contract_recording is True
    assert validated.allow_filesystem_artifact_access is False
    assert validated.allow_real_artifact_loading is False
    assert validated.allow_file_count_scan is False
    assert validated.allow_checksum_calculation is False
    assert validated.allow_npy_payload_loading is False
    assert validated.allow_embedding_vector_parsing is False
    assert validated.allow_input_materialization is False
    assert validated.allow_model_fitting is False
    assert validated.allow_prediction_generation is False
    assert validated.allow_metric_computation is False
    assert validated.performance_claims_added is False
    assert validated.notes == "F002 metadata gate only"


def test_stage6_f002_from_mapping_normalizes_sequences_and_notes():
    gate = stage6_real_artifact_access_integrity_gate_from_mapping(
        {
            "completed_stage6_features": ["STAGE6-F001"],
            "required_integrity_contracts": list(REQUIRED_INTEGRITY_CONTRACTS),
            "deferred_real_artifact_checks": list(DEFERRED_REAL_ARTIFACT_CHECKS),
            "notes": "  normalized  ",
        }
    )

    assert gate.current_feature == "STAGE6-F002"
    assert gate.completed_stage6_features == ("STAGE6-F001",)
    assert gate.required_integrity_contracts == REQUIRED_INTEGRITY_CONTRACTS
    assert gate.deferred_real_artifact_checks == DEFERRED_REAL_ARTIFACT_CHECKS
    assert gate.notes == "normalized"


def test_stage6_f002_rejects_wrong_stage_or_feature():
    with pytest.raises(
        Stage6RealArtifactAccessIntegrityGateError,
        match="current_stage",
    ):
        validate_stage6_real_artifact_access_integrity_gate(
            _gate(current_stage="Stage 5")
        )

    with pytest.raises(
        Stage6RealArtifactAccessIntegrityGateError,
        match="current_feature",
    ):
        validate_stage6_real_artifact_access_integrity_gate(
            _gate(current_feature="STAGE6-F001")
        )


def test_stage6_f002_requires_completed_f001_and_authorization_decision():
    with pytest.raises(
        Stage6RealArtifactAccessIntegrityGateError,
        match="previous_feature_status",
    ):
        validate_stage6_real_artifact_access_integrity_gate(
            _gate(previous_feature_status="in_progress")
        )

    with pytest.raises(
        Stage6RealArtifactAccessIntegrityGateError,
        match="upstream_authorization_decision",
    ):
        validate_stage6_real_artifact_access_integrity_gate(
            _gate(upstream_authorization_decision="not_granted")
        )


def test_stage6_f002_requires_exact_integrity_contract_sequences():
    with pytest.raises(
        Stage6RealArtifactAccessIntegrityGateError,
        match="required_integrity_contracts",
    ):
        validate_stage6_real_artifact_access_integrity_gate(
            _gate(required_integrity_contracts=("path_schema_contract",))
        )

    with pytest.raises(
        Stage6RealArtifactAccessIntegrityGateError,
        match="deferred_real_artifact_checks",
    ):
        validate_stage6_real_artifact_access_integrity_gate(
            _gate(deferred_real_artifact_checks=("npy_payload_loading",))
        )


@pytest.mark.parametrize(
    "required_gate",
    [
        "requires_completed_stage6_f001",
        "requires_artifact_integrity_review",
        "requires_permission_contract",
        "requires_donor_level_only",
        "forbids_cell_level_split",
        "requires_no_large_artifact_commit",
        "requires_payload_free_integrity_gate",
        "requires_no_runtime_execution",
        "allow_artifact_path_contract_recording",
        "allow_schema_contract_recording",
        "allow_permission_contract_recording",
    ],
)
def test_stage6_f002_requires_metadata_contract_flags(required_gate):
    with pytest.raises(Stage6RealArtifactAccessIntegrityGateError, match="required"):
        validate_stage6_real_artifact_access_integrity_gate(
            _gate(**{required_gate: False})
        )


@pytest.mark.parametrize(
    "flag_name",
    [
        "allow_filesystem_artifact_access",
        "allow_real_artifact_loading",
        "allow_file_count_scan",
        "allow_checksum_calculation",
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
def test_stage6_f002_keeps_runtime_modeling_metric_and_claim_flags_disabled(
    flag_name,
):
    with pytest.raises(Stage6RealArtifactAccessIntegrityGateError):
        validate_stage6_real_artifact_access_integrity_gate(
            _gate(**{flag_name: True})
        )


def test_stage6_f002_to_dict_serializes_tuples_as_lists():
    serialized = stage6_real_artifact_access_integrity_gate_to_dict(_gate())

    assert serialized["current_feature"] == "STAGE6-F002"
    assert serialized["completed_stage6_features"] == ["STAGE6-F001"]
    assert serialized["required_integrity_contracts"] == list(
        REQUIRED_INTEGRITY_CONTRACTS
    )
    assert serialized["deferred_real_artifact_checks"] == list(
        DEFERRED_REAL_ARTIFACT_CHECKS
    )
    assert serialized["allow_filesystem_artifact_access"] is False
    assert serialized["allow_real_artifact_loading"] is False
    assert serialized["allow_metric_computation"] is False


def test_stage6_f002_summary_is_payload_free_and_donor_level():
    summary = stage6_real_artifact_access_integrity_gate_summary(_gate())

    assert summary == {
        "current_stage": "Stage 6",
        "current_feature": "STAGE6-F002",
        "gate_status": "in_progress",
        "gate_decision": "metadata_access_integrity_gate_opened",
        "access_scope": "path_schema_permission_contract_only",
        "integrity_scope": "metadata_integrity_contract_only",
        "expected_artifact_format": "npy_directory",
        "expected_record_level": "donor",
        "expected_artifact_location_policy": (
            "external_local_or_remote_path_not_committed"
        ),
        "next_feature": "STAGE6-F003",
        "requires_donor_level_only": True,
        "forbids_cell_level_split": True,
        "allow_artifact_path_contract_recording": True,
        "allow_filesystem_artifact_access": False,
        "allow_real_artifact_loading": False,
        "allow_npy_payload_loading": False,
        "allow_embedding_vector_parsing": False,
        "allow_input_materialization": False,
        "allow_model_fitting": False,
        "allow_prediction_generation": False,
        "allow_metric_computation": False,
        "performance_claims_allowed": False,
        "performance_claims_added": False,
    }


def test_stage6_f002_module_has_no_runtime_or_modeling_imports():
    import lupusfm.evaluation.stage6_real_artifact_access_integrity_gate as gate_module

    source = gate_module.__loader__.get_source(gate_module.__name__).lower()
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
