import pytest

from lupusfm.evaluation.stage6_donor_level_input_materialization_gate import (
    DEFERRED_MATERIALIZATION_ACTIONS,
    REQUIRED_MATERIALIZATION_CONTRACTS,
    REQUIRED_UPSTREAM_GATES,
    STAGE6_CURRENT_FEATURE,
    Stage6DonorLevelInputMaterializationGate,
    Stage6DonorLevelInputMaterializationGateError,
    stage6_donor_level_input_materialization_gate_from_mapping,
    stage6_donor_level_input_materialization_gate_summary,
    stage6_donor_level_input_materialization_gate_to_dict,
    validate_stage6_donor_level_input_materialization_gate,
)


def _gate(**overrides):
    values = {
        "current_stage": "Stage 6",
        "current_feature": STAGE6_CURRENT_FEATURE,
        "stage6_status": "in_progress",
        "gate_status": "in_progress",
        "gate_decision": "materialization_contract_gate_opened",
        "previous_feature": "STAGE6-F002",
        "previous_feature_status": "completed",
        "completed_stage6_features": ("STAGE6-F001", "STAGE6-F002"),
        "required_upstream_gates": ("STAGE6-F001", "STAGE6-F002"),
        "upstream_authorization_decision": (
            "stage6_controlled_execution_path_authorized"
        ),
        "upstream_artifact_gate_status": (
            "stage6_f002_real_artifact_access_integrity_gate_completed"
        ),
        "notes": "  F003 metadata materialization gate only  ",
    }
    values.update(overrides)
    return Stage6DonorLevelInputMaterializationGate(**values)


def test_stage6_f003_accepts_metadata_only_materialization_gate():
    validated = validate_stage6_donor_level_input_materialization_gate(_gate())

    assert validated.current_stage == "Stage 6"
    assert validated.current_feature == "STAGE6-F003"
    assert validated.gate_status == "in_progress"
    assert validated.gate_decision == "materialization_contract_gate_opened"
    assert validated.previous_feature == "STAGE6-F002"
    assert validated.previous_feature_status == "completed"
    assert validated.completed_stage6_features == ("STAGE6-F001", "STAGE6-F002")
    assert validated.required_upstream_gates == REQUIRED_UPSTREAM_GATES
    assert (
        validated.upstream_authorization_decision
        == "stage6_controlled_execution_path_authorized"
    )
    assert (
        validated.upstream_artifact_gate_status
        == "stage6_f002_real_artifact_access_integrity_gate_completed"
    )
    assert validated.scope == "donor_level_materialization_contract_only_no_arrays"
    assert validated.expected_artifact_format == "npy_directory"
    assert validated.expected_artifact_layout == "one_file_per_donor_embedding"
    assert validated.expected_record_level == "donor"
    assert validated.expected_split_level == "donor"
    assert validated.materialization_target == "future_fold_scoped_donor_level_X_y_arrays"
    assert validated.preprocessing_scope == "fold_local_only"
    assert (
        validated.required_materialization_contracts
        == REQUIRED_MATERIALIZATION_CONTRACTS
    )
    assert validated.deferred_materialization_actions == DEFERRED_MATERIALIZATION_ACTIONS
    assert validated.next_feature == "STAGE6-F004"
    assert validated.first_runtime_execution_feature == "STAGE6-F005"
    assert validated.requires_donor_level_only is True
    assert validated.forbids_cell_level_split is True
    assert validated.allow_materialization_contract_recording is True
    assert validated.allow_label_mapping_contract_recording is True
    assert validated.allow_feature_matrix_contract_recording is True
    assert validated.allow_fold_scope_contract_recording is True
    assert validated.allow_npy_payload_loading is False
    assert validated.allow_embedding_vector_parsing is False
    assert validated.allow_input_materialization is False
    assert validated.allow_label_array_creation is False
    assert validated.allow_feature_matrix_construction is False
    assert validated.allow_preprocessing_fit is False
    assert validated.allow_model_fitting is False
    assert validated.allow_prediction_generation is False
    assert validated.allow_metric_computation is False
    assert validated.performance_claims_added is False
    assert validated.notes == "F003 metadata materialization gate only"


def test_stage6_f003_from_mapping_normalizes_sequences_and_notes():
    gate = stage6_donor_level_input_materialization_gate_from_mapping(
        {
            "completed_stage6_features": ["STAGE6-F001", "STAGE6-F002"],
            "required_upstream_gates": list(REQUIRED_UPSTREAM_GATES),
            "required_materialization_contracts": list(
                REQUIRED_MATERIALIZATION_CONTRACTS
            ),
            "deferred_materialization_actions": list(
                DEFERRED_MATERIALIZATION_ACTIONS
            ),
            "notes": "  normalized  ",
        }
    )

    assert gate.current_feature == "STAGE6-F003"
    assert gate.completed_stage6_features == ("STAGE6-F001", "STAGE6-F002")
    assert gate.required_upstream_gates == REQUIRED_UPSTREAM_GATES
    assert gate.required_materialization_contracts == REQUIRED_MATERIALIZATION_CONTRACTS
    assert gate.deferred_materialization_actions == DEFERRED_MATERIALIZATION_ACTIONS
    assert gate.notes == "normalized"


def test_stage6_f003_rejects_wrong_stage_or_feature():
    with pytest.raises(
        Stage6DonorLevelInputMaterializationGateError,
        match="current_stage",
    ):
        validate_stage6_donor_level_input_materialization_gate(
            _gate(current_stage="Stage 5")
        )

    with pytest.raises(
        Stage6DonorLevelInputMaterializationGateError,
        match="current_feature",
    ):
        validate_stage6_donor_level_input_materialization_gate(
            _gate(current_feature="STAGE6-F002")
        )


def test_stage6_f003_requires_completed_f002_and_artifact_gate():
    with pytest.raises(
        Stage6DonorLevelInputMaterializationGateError,
        match="previous_feature_status",
    ):
        validate_stage6_donor_level_input_materialization_gate(
            _gate(previous_feature_status="in_progress")
        )

    with pytest.raises(
        Stage6DonorLevelInputMaterializationGateError,
        match="upstream_artifact_gate_status",
    ):
        validate_stage6_donor_level_input_materialization_gate(
            _gate(upstream_artifact_gate_status="in_progress")
        )


def test_stage6_f003_requires_exact_upstream_and_materialization_contracts():
    with pytest.raises(
        Stage6DonorLevelInputMaterializationGateError,
        match="required_upstream_gates",
    ):
        validate_stage6_donor_level_input_materialization_gate(
            _gate(required_upstream_gates=("STAGE6-F002",))
        )

    with pytest.raises(
        Stage6DonorLevelInputMaterializationGateError,
        match="required_materialization_contracts",
    ):
        validate_stage6_donor_level_input_materialization_gate(
            _gate(required_materialization_contracts=("donor_index_contract",))
        )

    with pytest.raises(
        Stage6DonorLevelInputMaterializationGateError,
        match="deferred_materialization_actions",
    ):
        validate_stage6_donor_level_input_materialization_gate(
            _gate(deferred_materialization_actions=("construct_feature_matrix",))
        )


@pytest.mark.parametrize(
    "required_gate",
    [
        "requires_completed_stage6_f001",
        "requires_completed_stage6_f002",
        "requires_donor_index_contract",
        "requires_artifact_to_donor_alignment_contract",
        "requires_label_mapping_contract",
        "requires_split_alignment_contract",
        "requires_fold_local_preprocessing_contract",
        "requires_leakage_control_contract",
        "requires_donor_level_only",
        "forbids_cell_level_split",
        "requires_no_payload_materialization",
        "requires_no_runtime_execution",
        "allow_materialization_contract_recording",
        "allow_label_mapping_contract_recording",
        "allow_feature_matrix_contract_recording",
        "allow_fold_scope_contract_recording",
    ],
)
def test_stage6_f003_requires_metadata_contract_flags(required_gate):
    with pytest.raises(
        Stage6DonorLevelInputMaterializationGateError,
        match="required",
    ):
        validate_stage6_donor_level_input_materialization_gate(
            _gate(**{required_gate: False})
        )


@pytest.mark.parametrize(
    "flag_name",
    [
        "allow_filesystem_artifact_access",
        "allow_real_artifact_loading",
        "allow_npy_payload_loading",
        "allow_embedding_vector_parsing",
        "allow_input_materialization",
        "allow_label_array_creation",
        "allow_feature_matrix_construction",
        "allow_label_vector_construction",
        "allow_materialized_array_persistence",
        "allow_split_execution",
        "allow_real_aggregation_execution",
        "allow_anndata_loading",
        "allow_geneformer_execution",
        "allow_tokenizer_execution",
        "allow_embedding_extraction",
        "allow_feature_extraction",
        "allow_global_preprocessing",
        "allow_scaler_outside_fold",
        "allow_preprocessing_fit",
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
def test_stage6_f003_keeps_runtime_array_modeling_metric_and_claims_disabled(
    flag_name,
):
    with pytest.raises(Stage6DonorLevelInputMaterializationGateError):
        validate_stage6_donor_level_input_materialization_gate(
            _gate(**{flag_name: True})
        )


def test_stage6_f003_to_dict_serializes_tuples_as_lists():
    serialized = stage6_donor_level_input_materialization_gate_to_dict(_gate())

    assert serialized["current_feature"] == "STAGE6-F003"
    assert serialized["completed_stage6_features"] == [
        "STAGE6-F001",
        "STAGE6-F002",
    ]
    assert serialized["required_upstream_gates"] == list(REQUIRED_UPSTREAM_GATES)
    assert serialized["required_materialization_contracts"] == list(
        REQUIRED_MATERIALIZATION_CONTRACTS
    )
    assert serialized["deferred_materialization_actions"] == list(
        DEFERRED_MATERIALIZATION_ACTIONS
    )
    assert serialized["allow_input_materialization"] is False
    assert serialized["allow_label_array_creation"] is False
    assert serialized["allow_metric_computation"] is False


def test_stage6_f003_summary_is_donor_level_and_array_free():
    summary = stage6_donor_level_input_materialization_gate_summary(_gate())

    assert summary == {
        "current_stage": "Stage 6",
        "current_feature": "STAGE6-F003",
        "gate_status": "in_progress",
        "gate_decision": "materialization_contract_gate_opened",
        "scope": "donor_level_materialization_contract_only_no_arrays",
        "expected_record_level": "donor",
        "expected_split_level": "donor",
        "materialization_target": "future_fold_scoped_donor_level_X_y_arrays",
        "preprocessing_scope": "fold_local_only",
        "next_feature": "STAGE6-F004",
        "first_runtime_execution_feature": "STAGE6-F005",
        "requires_donor_level_only": True,
        "forbids_cell_level_split": True,
        "allow_materialization_contract_recording": True,
        "allow_npy_payload_loading": False,
        "allow_embedding_vector_parsing": False,
        "allow_input_materialization": False,
        "allow_label_array_creation": False,
        "allow_feature_matrix_construction": False,
        "allow_preprocessing_fit": False,
        "allow_model_fitting": False,
        "allow_prediction_generation": False,
        "allow_metric_computation": False,
        "performance_claims_allowed": False,
        "performance_claims_added": False,
    }


def test_stage6_f003_module_has_no_runtime_or_modeling_imports():
    import lupusfm.evaluation.stage6_donor_level_input_materialization_gate as gate_module

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
