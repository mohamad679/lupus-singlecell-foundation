from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = REPO_ROOT / "state" / "project_state.yaml"
CURRENT_FEATURE_PATH = REPO_ROOT / "state" / "current_feature.md"


def _block_between(text, start_marker, end_marker=None):
    start = text.index(start_marker)
    end = text.index(end_marker, start) if end_marker else len(text)
    return text[start:end]


def test_stage6_compacted_pr_advances_active_feature_to_f005():
    state = STATE_PATH.read_text()

    assert "status: stage6_in_progress" in state
    assert "current_phase: Stage 6" in state
    assert (
        "current_phase_name: Stage 6 - Controlled donor-level modeling execution"
        in state
    )
    assert "current_feature: STAGE6-F005" in state
    assert (
        "modeling_readiness: "
        "stage6_f004_complete_pending_controlled_baseline_execution"
        in state
    )


def test_stage6_f003_closeout_is_recorded_without_array_materialization():
    state = STATE_PATH.read_text()
    block = _block_between(
        state,
        "stage6_donor_level_input_materialization_closeout:",
        "stage6_split_leakage_control_gate:",
    )

    assert "status: completed" in block
    assert "closeout_feature: STAGE6-F003-CLOSEOUT" in block
    assert "closeout_branch: feat/stage6-f004-split-leakage-control-gate" in block
    assert "previous_feature: STAGE6-F003" in block
    assert "next_feature: STAGE6-F004" in block
    assert "allow_input_materialization: false" in block
    assert "allow_label_array_creation: false" in block
    assert "allow_feature_matrix_construction: false" in block
    assert "allow_split_execution: false" in block
    assert "allow_model_fitting: false" in block
    assert "allow_prediction_generation: false" in block
    assert "allow_metric_computation: false" in block
    assert "performance_claims_added: false" in block


def test_stage6_f004_split_leakage_gate_is_completed_in_same_pr():
    state = STATE_PATH.read_text()
    block = _block_between(state, "stage6_split_leakage_control_gate:")

    assert "status: completed" in block
    assert "branch: feat/stage6-f004-split-leakage-control-gate" in block
    assert "current_feature: STAGE6-F004" in block
    assert "feature_name: Split and leakage-control gate" in block
    assert "gate_decision: split_leakage_control_gate_completed" in block
    assert "previous_feature: STAGE6-F003" in block
    assert "previous_feature_status: completed" in block
    assert "completed_stage6_features:" in block
    assert "STAGE6-F001" in block
    assert "STAGE6-F002" in block
    assert "STAGE6-F003" in block
    assert "next_feature: STAGE6-F005" in block
    assert "next_feature_name: Controlled baseline execution" in block
    assert "closeout_feature: STAGE6-F004-CLOSEOUT" in block
    assert "closeout_status: completed" in block
    assert (
        "closeout_scope: feature_and_closeout_combined_no_runtime_execution"
        in block
    )


def test_stage6_f004_records_split_contract_without_split_execution():
    state = STATE_PATH.read_text()
    block = _block_between(state, "stage6_split_leakage_control_gate:")

    assert "scope: split_leakage_contract_only_no_execution" in block
    assert "split_target: future_donor_level_split_manifest" in block
    assert "expected_record_level: donor" in block
    assert "expected_split_level: donor" in block
    assert "preprocessing_scope: fold_local_only" in block
    assert "required_split_contracts:" in block
    assert "donor_level_split_contract" in block
    assert "unique_donor_assignment_contract" in block
    assert "label_stratification_contract" in block
    assert "fold_local_preprocessing_contract" in block
    assert "no_cell_level_split_contract" in block
    assert "no_global_preprocessing_contract" in block
    assert "no_prediction_metric_columns_contract" in block
    assert "leakage_review_contract" in block
    assert "deferred_split_actions:" in block
    assert "execute_real_split_assignment" in block
    assert "materialize_fold_indices" in block
    assert "fit_fold_preprocessors" in block
    assert "fit_models" in block
    assert "generate_predictions" in block
    assert "compute_metrics" in block


def test_stage6_f004_preserves_runtime_modeling_metric_and_claim_locks():
    state = STATE_PATH.read_text()
    block = _block_between(state, "stage6_split_leakage_control_gate:")

    assert "split_policy: donor_level_only" in block
    assert "leakage_policy: cell_level_split_forbidden" in block
    assert "requires_no_cell_level_split: true" in block
    assert "requires_no_global_preprocessing: true" in block
    assert "requires_no_prediction_or_metric_columns: true" in block
    assert "allow_split_contract_recording: true" in block
    assert "allow_leakage_contract_recording: true" in block
    assert "allow_fold_scope_contract_recording: true" in block
    assert "allow_npy_payload_loading: false" in block
    assert "allow_embedding_vector_parsing: false" in block
    assert "allow_input_materialization: false" in block
    assert "allow_label_array_creation: false" in block
    assert "allow_feature_matrix_construction: false" in block
    assert "allow_split_execution: false" in block
    assert "allow_train_test_split_execution: false" in block
    assert "allow_fold_index_materialization: false" in block
    assert "allow_global_preprocessing: false" in block
    assert "allow_scaler_outside_fold: false" in block
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


def test_stage6_current_feature_records_f005_ready_after_compacted_f004():
    current_feature = CURRENT_FEATURE_PATH.read_text()

    assert "## STAGE6-F005 - Controlled baseline execution" in current_feature
    assert "Status: ready" in current_feature
    assert "Branch: `feat/stage6-f004-split-leakage-control-gate`" in current_feature
    assert "STAGE6-F003 and STAGE6-F004 are complete." in current_feature
    assert "## STAGE6-F004 - Split and leakage-control gate" in current_feature
    assert "Status: completed" in current_feature
    assert "Closeout feature: STAGE6-F004-CLOSEOUT" in current_feature
    assert "No real split assignment is executed." in current_feature
    assert "No fold index is materialized." in current_feature
    assert "No global preprocessing is performed." in current_feature
    assert "No fold preprocessor is fit." in current_feature
    assert "No models are fit." in current_feature
    assert "No predictions are generated." in current_feature
    assert "No real metrics are computed." in current_feature
    assert "No performance claims are added." in current_feature
