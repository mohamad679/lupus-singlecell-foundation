import pytest

from lupusfm.evaluation.stage6_split_leakage_control_gate import (
    DEFERRED_SPLIT_ACTIONS,
    REQUIRED_SPLIT_CONTRACTS,
    REQUIRED_UPSTREAM_GATES,
    STAGE6_CURRENT_FEATURE,
    Stage6SplitLeakageControlGate,
    Stage6SplitLeakageControlGateError,
    stage6_split_leakage_control_gate_from_mapping,
    stage6_split_leakage_control_gate_summary,
    stage6_split_leakage_control_gate_to_dict,
    validate_stage6_split_leakage_control_gate,
)


def _gate(**overrides):
    values = {
        "current_feature": STAGE6_CURRENT_FEATURE,
        "completed_stage6_features": ("STAGE6-F001", "STAGE6-F002", "STAGE6-F003"),
        "required_upstream_gates": ("STAGE6-F001", "STAGE6-F002", "STAGE6-F003"),
        "notes": "  F004 split/leakage gate only  ",
    }
    values.update(overrides)
    return Stage6SplitLeakageControlGate(**values)


def test_stage6_f004_accepts_completed_metadata_only_split_gate():
    validated = validate_stage6_split_leakage_control_gate(_gate())

    assert validated.current_stage == "Stage 6"
    assert validated.current_feature == "STAGE6-F004"
    assert validated.gate_status == "completed"
    assert validated.gate_decision == "split_leakage_control_gate_completed"
    assert validated.previous_feature == "STAGE6-F003"
    assert validated.previous_feature_status == "completed"
    assert validated.completed_stage6_features == (
        "STAGE6-F001",
        "STAGE6-F002",
        "STAGE6-F003",
    )
    assert validated.required_upstream_gates == REQUIRED_UPSTREAM_GATES
    assert validated.scope == "split_leakage_contract_only_no_execution"
    assert validated.split_target == "future_donor_level_split_manifest"
    assert validated.expected_record_level == "donor"
    assert validated.expected_split_level == "donor"
    assert validated.preprocessing_scope == "fold_local_only"
    assert validated.required_split_contracts == REQUIRED_SPLIT_CONTRACTS
    assert validated.deferred_split_actions == DEFERRED_SPLIT_ACTIONS
    assert validated.next_feature == "STAGE6-F005"
    assert validated.closeout_feature == "STAGE6-F004-CLOSEOUT"
    assert validated.closeout_status == "completed"
    assert validated.requires_no_cell_level_split is True
    assert validated.requires_no_global_preprocessing is True
    assert validated.requires_no_prediction_or_metric_columns is True
    assert validated.allow_split_contract_recording is True
    assert validated.allow_leakage_contract_recording is True
    assert validated.allow_fold_scope_contract_recording is True
    assert validated.allow_split_execution is False
    assert validated.allow_train_test_split_execution is False
    assert validated.allow_fold_index_materialization is False
    assert validated.allow_global_preprocessing is False
    assert validated.allow_scaler_outside_fold is False
    assert validated.allow_preprocessing_fit is False
    assert validated.allow_model_fitting is False
    assert validated.allow_prediction_generation is False
    assert validated.allow_metric_computation is False
    assert validated.performance_claims_added is False
    assert validated.notes == "F004 split/leakage gate only"


def test_stage6_f004_from_mapping_normalizes_sequences():
    gate = stage6_split_leakage_control_gate_from_mapping(
        {
            "completed_stage6_features": [
                "STAGE6-F001",
                "STAGE6-F002",
                "STAGE6-F003",
            ],
            "required_upstream_gates": list(REQUIRED_UPSTREAM_GATES),
            "required_split_contracts": list(REQUIRED_SPLIT_CONTRACTS),
            "deferred_split_actions": list(DEFERRED_SPLIT_ACTIONS),
            "notes": "  normalized  ",
        }
    )

    assert gate.current_feature == "STAGE6-F004"
    assert gate.completed_stage6_features == (
        "STAGE6-F001",
        "STAGE6-F002",
        "STAGE6-F003",
    )
    assert gate.required_upstream_gates == REQUIRED_UPSTREAM_GATES
    assert gate.required_split_contracts == REQUIRED_SPLIT_CONTRACTS
    assert gate.deferred_split_actions == DEFERRED_SPLIT_ACTIONS
    assert gate.notes == "normalized"


def test_stage6_f004_rejects_wrong_feature_or_upstream_status():
    with pytest.raises(Stage6SplitLeakageControlGateError, match="current_feature"):
        validate_stage6_split_leakage_control_gate(
            _gate(current_feature="STAGE6-F003")
        )

    with pytest.raises(
        Stage6SplitLeakageControlGateError,
        match="previous_feature_status",
    ):
        validate_stage6_split_leakage_control_gate(
            _gate(previous_feature_status="in_progress")
        )


def test_stage6_f004_requires_exact_upstream_split_and_deferred_sequences():
    with pytest.raises(Stage6SplitLeakageControlGateError, match="required_upstream"):
        validate_stage6_split_leakage_control_gate(
            _gate(required_upstream_gates=("STAGE6-F003",))
        )

    with pytest.raises(
        Stage6SplitLeakageControlGateError,
        match="required_split_contracts",
    ):
        validate_stage6_split_leakage_control_gate(
            _gate(required_split_contracts=("donor_level_split_contract",))
        )

    with pytest.raises(
        Stage6SplitLeakageControlGateError,
        match="deferred_split_actions",
    ):
        validate_stage6_split_leakage_control_gate(
            _gate(deferred_split_actions=("execute_real_split_assignment",))
        )


@pytest.mark.parametrize(
    "required_gate",
    [
        "requires_completed_stage6_f001",
        "requires_completed_stage6_f002",
        "requires_completed_stage6_f003",
        "requires_donor_level_split_contract",
        "requires_unique_donor_assignment",
        "requires_label_stratification_contract",
        "requires_fold_local_preprocessing_contract",
        "requires_no_cell_level_split",
        "requires_no_global_preprocessing",
        "requires_no_prediction_or_metric_columns",
        "requires_leakage_review",
        "requires_no_runtime_execution",
        "allow_split_contract_recording",
        "allow_leakage_contract_recording",
        "allow_fold_scope_contract_recording",
    ],
)
def test_stage6_f004_requires_split_and_leakage_contract_flags(required_gate):
    with pytest.raises(Stage6SplitLeakageControlGateError, match="required"):
        validate_stage6_split_leakage_control_gate(_gate(**{required_gate: False}))


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
        "allow_split_execution",
        "allow_train_test_split_execution",
        "allow_fold_index_materialization",
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
def test_stage6_f004_keeps_runtime_split_modeling_metric_and_claims_disabled(
    flag_name,
):
    with pytest.raises(Stage6SplitLeakageControlGateError):
        validate_stage6_split_leakage_control_gate(_gate(**{flag_name: True}))


def test_stage6_f004_to_dict_serializes_tuples_as_lists():
    serialized = stage6_split_leakage_control_gate_to_dict(_gate())

    assert serialized["current_feature"] == "STAGE6-F004"
    assert serialized["completed_stage6_features"] == [
        "STAGE6-F001",
        "STAGE6-F002",
        "STAGE6-F003",
    ]
    assert serialized["required_upstream_gates"] == list(REQUIRED_UPSTREAM_GATES)
    assert serialized["required_split_contracts"] == list(REQUIRED_SPLIT_CONTRACTS)
    assert serialized["deferred_split_actions"] == list(DEFERRED_SPLIT_ACTIONS)
    assert serialized["allow_split_execution"] is False
    assert serialized["allow_model_fitting"] is False
    assert serialized["allow_metric_computation"] is False


def test_stage6_f004_summary_is_split_execution_free():
    summary = stage6_split_leakage_control_gate_summary(_gate())

    assert summary == {
        "current_stage": "Stage 6",
        "current_feature": "STAGE6-F004",
        "gate_status": "completed",
        "gate_decision": "split_leakage_control_gate_completed",
        "scope": "split_leakage_contract_only_no_execution",
        "split_target": "future_donor_level_split_manifest",
        "expected_record_level": "donor",
        "expected_split_level": "donor",
        "preprocessing_scope": "fold_local_only",
        "next_feature": "STAGE6-F005",
        "closeout_feature": "STAGE6-F004-CLOSEOUT",
        "requires_no_cell_level_split": True,
        "requires_no_global_preprocessing": True,
        "allow_split_contract_recording": True,
        "allow_split_execution": False,
        "allow_fold_index_materialization": False,
        "allow_global_preprocessing": False,
        "allow_preprocessing_fit": False,
        "allow_model_fitting": False,
        "allow_prediction_generation": False,
        "allow_metric_computation": False,
        "performance_claims_allowed": False,
        "performance_claims_added": False,
    }


def test_stage6_f004_module_has_no_runtime_or_modeling_imports():
    import lupusfm.evaluation.stage6_split_leakage_control_gate as gate_module

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
