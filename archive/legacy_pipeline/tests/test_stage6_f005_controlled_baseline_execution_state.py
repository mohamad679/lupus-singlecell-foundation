from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = REPO_ROOT / "state" / "project_state.yaml"
CURRENT_FEATURE_PATH = REPO_ROOT / "state" / "current_feature.md"


def _block_between(text, start_marker, end_marker=None):
    start = text.index(start_marker)
    end = text.index(end_marker, start) if end_marker else len(text)
    return text[start:end]


def test_stage6_f005_compacted_pr_advances_active_feature_to_f006():
    state = STATE_PATH.read_text()

    assert "status: stage6_in_progress" in state
    assert "current_phase: Stage 6" in state
    assert "current_feature: STAGE6-F006" in state
    assert (
        "modeling_readiness: "
        "stage6_f005_complete_pending_prediction_metric_computation"
        in state
    )


def test_stage6_f005_controlled_baseline_execution_block_records_fit_only_scope():
    state = STATE_PATH.read_text()
    block = _block_between(state, "stage6_controlled_baseline_execution:")

    assert "status: completed" in block
    assert "branch: feat/stage6-f005-controlled-baseline-execution" in block
    assert "current_feature: STAGE6-F005" in block
    assert "feature_name: Controlled baseline execution" in block
    assert "gate_decision: controlled_baseline_execution_completed" in block
    assert (
        "scope: in_memory_donor_level_baseline_fit_only_no_predictions_metrics"
        in block
    )
    assert "baseline_family: nearest_centroid_baseline" in block
    assert "expected_record_level: donor" in block
    assert "preprocessing_scope: fold_local_only" in block
    assert "next_feature: STAGE6-F006" in block
    assert "next_feature_name: Prediction and metric computation" in block
    assert "closeout_feature: STAGE6-F005-CLOSEOUT" in block
    assert "closeout_status: completed" in block


def test_stage6_f005_records_allowed_fit_and_forbidden_prediction_metric_actions():
    state = STATE_PATH.read_text()
    block = _block_between(state, "stage6_controlled_baseline_execution:")

    assert "allow_in_memory_donor_records: true" in block
    assert "allow_controlled_baseline_fitting: true" in block
    assert "allow_model_fitting: true" in block
    assert "modeling_authorization_granted: true" in block
    assert "modeling_allowed: true" in block
    assert "allow_filesystem_artifact_access: false" in block
    assert "allow_real_artifact_loading: false" in block
    assert "allow_npy_payload_loading: false" in block
    assert "allow_embedding_vector_parsing_from_disk: false" in block
    assert "allow_input_file_materialization: false" in block
    assert "allow_label_file_materialization: false" in block
    assert "allow_split_execution_from_file: false" in block
    assert "allow_global_preprocessing: false" in block
    assert "allow_scaler_outside_fold: false" in block
    assert "allow_model_artifact_persistence: false" in block
    assert "allow_prediction_generation: false" in block
    assert "allow_metric_computation: false" in block
    assert "allow_training_beyond_controlled_baseline_fit: false" in block
    assert "training_allowed: false" in block
    assert "external_validation_allowed: false" in block
    assert "performance_claims_allowed: false" in block
    assert "performance_claims_added: false" in block


def test_stage6_current_feature_records_f006_ready_after_f005():
    current_feature = CURRENT_FEATURE_PATH.read_text()

    assert "## STAGE6-F006 - Prediction and metric computation" in current_feature
    assert "Status: ready" in current_feature
    assert "STAGE6-F005 is complete." in current_feature
    assert "## STAGE6-F005 - Controlled baseline execution" in current_feature
    assert "Status: completed" in current_feature
    assert "Closeout feature: STAGE6-F005-CLOSEOUT" in current_feature
    assert "Controlled baseline fitting is allowed only for in-memory donor-level records." in current_feature
    assert "No filesystem artifact access is performed." in current_feature
    assert "No `.npy` embedding payload is loaded." in current_feature
    assert "No predictions are generated in F005." in current_feature
    assert "No metrics are computed in F005." in current_feature
    assert "No performance claims are added." in current_feature
