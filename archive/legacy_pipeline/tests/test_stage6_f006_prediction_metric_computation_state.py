from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = REPO_ROOT / "state" / "project_state.yaml"
CURRENT_FEATURE_PATH = REPO_ROOT / "state" / "current_feature.md"


def _block_between(text, start_marker, end_marker=None):
    start = text.index(start_marker)
    end = text.index(end_marker, start) if end_marker else len(text)
    return text[start:end]


def test_stage6_f006_compacted_pr_advances_active_feature_to_f007():
    state = STATE_PATH.read_text()

    assert "status: stage6_in_progress" in state
    assert "current_phase: Stage 6" in state
    assert "current_feature: STAGE6-F007" in state
    assert (
        "modeling_readiness: "
        "stage6_f006_complete_pending_final_result_report_closeout"
        in state
    )


def test_stage6_f006_prediction_metric_block_records_scope():
    state = STATE_PATH.read_text()
    block = _block_between(state, "stage6_prediction_metric_computation:")

    assert "status: completed" in block
    assert "branch: feat/stage6-f006-prediction-metric-computation" in block
    assert "current_feature: STAGE6-F006" in block
    assert "feature_name: Prediction and metric computation" in block
    assert "gate_decision: prediction_metric_computation_completed" in block
    assert (
        "scope: in_memory_donor_level_prediction_metric_only_no_artifacts_claims"
        in block
    )
    assert "baseline_family: nearest_centroid_baseline" in block
    assert "expected_record_level: donor" in block
    assert "preprocessing_scope: fold_local_only" in block
    assert "next_feature: STAGE6-F007" in block
    assert "next_feature_name: Stage 6 final result report and closeout" in block
    assert "closeout_feature: STAGE6-F006-CLOSEOUT" in block
    assert "closeout_status: completed" in block


def test_stage6_f006_records_allowed_prediction_metric_and_forbidden_outputs():
    state = STATE_PATH.read_text()
    block = _block_between(state, "stage6_prediction_metric_computation:")

    assert "allow_in_memory_prediction_generation: true" in block
    assert "allow_in_memory_metric_computation: true" in block
    assert "allow_prediction_generation: true" in block
    assert "allow_metric_computation: true" in block
    assert "allow_filesystem_artifact_access: false" in block
    assert "allow_real_artifact_loading: false" in block
    assert "allow_npy_payload_loading: false" in block
    assert "allow_embedding_vector_parsing_from_disk: false" in block
    assert "allow_split_execution_from_file: false" in block
    assert "allow_model_refit: false" in block
    assert "allow_training: false" in block
    assert "training_allowed: false" in block
    assert "allow_model_artifact_persistence: false" in block
    assert "allow_prediction_manifest_write: false" in block
    assert "allow_metric_table_write: false" in block
    assert "external_validation_allowed: false" in block
    assert "allow_external_validation: false" in block
    assert "performance_claims_allowed: false" in block
    assert "performance_claims_added: false" in block


def test_stage6_current_feature_records_f007_ready_after_f006():
    current_feature = CURRENT_FEATURE_PATH.read_text()

    assert "## STAGE6-F007 - Stage 6 final result report and closeout" in current_feature
    assert "Status: ready" in current_feature
    assert "STAGE6-F006 is complete." in current_feature
    assert "## STAGE6-F006 - Prediction and metric computation" in current_feature
    assert "Status: completed" in current_feature
    assert "Closeout feature: STAGE6-F006-CLOSEOUT" in current_feature
    assert "Prediction generation is allowed only for in-memory donor-level records." in current_feature
    assert "Metric computation is allowed only for in-memory donor-level predictions." in current_feature
    assert "No prediction manifest is written." in current_feature
    assert "No metric table is written." in current_feature
    assert "No external validation is performed." in current_feature
    assert "No performance claims are added." in current_feature
