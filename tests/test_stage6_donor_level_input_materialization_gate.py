from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = REPO_ROOT / "state" / "project_state.yaml"
CURRENT_FEATURE_PATH = REPO_ROOT / "state" / "current_feature.md"


def _block_between(text, start_marker, end_marker=None):
    start = text.index(start_marker)
    end = text.index(end_marker, start) if end_marker else len(text)
    return text[start:end]


def test_stage6_f003_records_donor_materialization_gate_metadata():
    state = STATE_PATH.read_text()
    block = _block_between(state, "stage6_donor_level_input_materialization_gate:")

    assert "status: stage6_in_progress" in state
    assert "current_phase: Stage 6" in state
    assert "current_feature: STAGE6-F003" in state
    assert (
        "modeling_readiness: "
        "stage6_f003_donor_level_input_materialization_gate_in_progress"
        in state
    )
    assert "status: in_progress" in block
    assert "branch: feat/stage6-donor-level-input-materialization-gate" in block
    assert "current_feature: STAGE6-F003" in block
    assert "feature_name: Donor-level input materialization gate" in block
    assert "previous_feature: STAGE6-F002" in block
    assert "previous_feature_status: completed" in block
    assert "completed_stage6_features:" in block
    assert "STAGE6-F001" in block
    assert "STAGE6-F002" in block
    assert "gate_decision: materialization_contract_gate_opened" in block
    assert "scope: donor_level_materialization_contract_only_no_arrays" in block
    assert "next_feature: STAGE6-F004" in block
    assert "next_feature_name: Split and leakage-control gate" in block


def test_stage6_f003_retains_f002_completed_readiness_snapshot_for_legacy_tests():
    state = STATE_PATH.read_text()
    block = _block_between(
        state,
        "stage6_f002_completed_project_snapshot_for_legacy_tests:",
        "stage6_donor_level_input_materialization_gate:",
    )

    assert "current_feature: STAGE6-F003" in block
    assert (
        "modeling_readiness: "
        "stage6_f002_complete_pending_donor_level_input_materialization_gate"
        in block
    )
    assert "purpose: retained_historical_snapshot_only" in block
    assert (
        "superseded_by: STAGE6-F003 - Donor-level input materialization gate"
        in block
    )


def test_stage6_f003_records_materialization_contract_without_arrays():
    state = STATE_PATH.read_text()
    block = _block_between(state, "stage6_donor_level_input_materialization_gate:")

    assert "expected_artifact_format: npy_directory" in block
    assert "expected_artifact_layout: one_file_per_donor_embedding" in block
    assert "expected_record_level: donor" in block
    assert "expected_split_level: donor" in block
    assert "materialization_target: future_fold_scoped_donor_level_X_y_arrays" in block
    assert "preprocessing_scope: fold_local_only" in block
    assert "required_materialization_contracts:" in block
    assert "donor_index_contract" in block
    assert "artifact_to_donor_alignment_contract" in block
    assert "label_mapping_contract" in block
    assert "split_alignment_contract" in block
    assert "feature_matrix_contract" in block
    assert "fold_local_preprocessing_contract" in block
    assert "leakage_control_contract" in block
    assert "no_payload_materialization_contract" in block
    assert "deferred_materialization_actions:" in block
    assert "load_npy_payloads" in block
    assert "parse_embedding_vectors" in block
    assert "construct_feature_matrix" in block
    assert "construct_label_array" in block
    assert "fit_fold_preprocessors" in block


def test_stage6_f003_preserves_donor_level_and_runtime_locks():
    state = STATE_PATH.read_text()
    block = _block_between(state, "stage6_donor_level_input_materialization_gate:")

    assert "split_policy: donor_level_only" in block
    assert "leakage_policy: cell_level_split_forbidden" in block
    assert "requires_donor_level_only: true" in block
    assert "forbids_cell_level_split: true" in block
    assert "requires_no_payload_materialization: true" in block
    assert "allow_materialization_contract_recording: true" in block
    assert "allow_label_mapping_contract_recording: true" in block
    assert "allow_feature_matrix_contract_recording: true" in block
    assert "allow_fold_scope_contract_recording: true" in block
    assert "allow_real_artifact_loading: false" in block
    assert "allow_npy_payload_loading: false" in block
    assert "allow_embedding_vector_parsing: false" in block
    assert "allow_input_materialization: false" in block
    assert "allow_label_array_creation: false" in block
    assert "allow_feature_matrix_construction: false" in block
    assert "allow_label_vector_construction: false" in block
    assert "allow_materialized_array_persistence: false" in block
    assert "allow_split_execution: false" in block
    assert "allow_real_aggregation_execution: false" in block
    assert "allow_preprocessing_fit: false" in block
    assert "allow_model_fitting: false" in block
    assert "allow_prediction_generation: false" in block
    assert "allow_metric_computation: false" in block
    assert "modeling_authorization_granted: false" in block
    assert "modeling_allowed: false" in block
    assert "training_allowed: false" in block
    assert "external_validation_allowed: false" in block
    assert "performance_claims_allowed: false" in block
    assert "performance_claims_added: false" in block


def test_stage6_f003_current_feature_document_records_contract_scope():
    current_feature = CURRENT_FEATURE_PATH.read_text()

    assert "## STAGE6-F003 - Donor-level input materialization gate" in current_feature
    assert "Status: in_progress" in current_feature
    assert "Branch: `feat/stage6-donor-level-input-materialization-gate`" in current_feature
    assert "donor-level materialization contract only" in current_feature
    assert "STAGE6-F004 - Split and leakage-control gate" in current_feature
    assert "No `.npy` embedding payload is loaded." in current_feature
    assert "No embedding vector is parsed." in current_feature
    assert "No feature matrix is constructed." in current_feature
    assert "No label array is created from real data." in current_feature
    assert "No evaluation array is materialized." in current_feature
    assert "No fold preprocessor is fit." in current_feature
    assert "No models are fit." in current_feature
    assert "No predictions are generated." in current_feature
    assert "No real metrics are computed." in current_feature
    assert "No performance claims are added." in current_feature
