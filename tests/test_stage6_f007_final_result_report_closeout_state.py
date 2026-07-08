from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = REPO_ROOT / "state" / "project_state.yaml"
CURRENT_FEATURE_PATH = REPO_ROOT / "state" / "current_feature.md"


def _block_between(text, start_marker, end_marker=None):
    start = text.index(start_marker)
    end = text.index(end_marker, start) if end_marker else len(text)
    return text[start:end]


def test_stage6_final_closeout_is_retained_after_stage7_completion():
    state = STATE_PATH.read_text()

    project_header = _block_between(
        state,
        "project:",
        "stage7_kaggle_result_reconciliation:",
    )

    assert "status: stage7_complete" in project_header
    assert "current_phase: Stage 7" in project_header
    assert "current_phase_name: Stage 7 Complete - Leakage-safe reconciliation" in project_header
    assert "current_feature: STAGE7-COMPLETE" in project_header
    assert "modeling_readiness: stage7_internal_reconciliation_complete_external_validation_pending" in project_header
    assert "blocked: false" in project_header

    stage6_block = _block_between(state, "stage6_final_result_report_closeout:")

    assert "final_current_feature: STAGE6-COMPLETE" in stage6_block
    assert "final_stage_status: completed" in stage6_block
    assert "stage7_policy: no_stage7_required" in stage6_block


def test_stage6_final_closeout_block_records_all_features_complete():
    state = STATE_PATH.read_text()
    block = _block_between(state, "stage6_final_result_report_closeout:")

    assert "status: completed" in block
    assert "branch: chore/stage6-final-result-report-closeout" in block
    assert "current_feature: STAGE6-F007" in block
    assert "feature_name: Stage 6 final result report and closeout" in block
    assert "closeout_feature: STAGE6-F007-CLOSEOUT" in block
    assert "closeout_status: completed" in block
    assert "closeout_decision: stage6_final_result_report_closeout_completed" in block
    assert "final_current_feature: STAGE6-COMPLETE" in block
    assert "final_stage_status: completed" in block
    assert "stage7_policy: no_stage7_required" in block
    for feature in [
        "STAGE6-F001",
        "STAGE6-F002",
        "STAGE6-F003",
        "STAGE6-F004",
        "STAGE6-F005",
        "STAGE6-F006",
        "STAGE6-F007",
    ]:
        assert feature in block


def test_stage6_final_closeout_documents_limitations_and_no_claims():
    state = STATE_PATH.read_text()
    block = _block_between(state, "stage6_final_result_report_closeout:")

    assert "scope: stage6_final_report_closeout_no_real_performance_claims" in block
    assert "record_level: donor" in block
    assert "execution_scope: in_memory_only" in block
    assert "prediction_metric_scope: in_memory_donor_level_predictions_only" in block
    assert "report_artifact_policy: no_report_artifact_written" in block
    assert "performance_claim_policy: no_real_cohort_performance_claim" in block
    assert "external_validation_policy: not_performed" in block
    assert "no_real_cohort_performance_claim" in block
    assert "no_external_validation_performed" in block
    assert "no_prediction_or_metric_artifact_written" in block
    assert "no_npy_payload_loaded" in block
    assert "in_memory_execution_scope_only" in block


def test_stage6_final_closeout_keeps_all_output_and_claim_locks_disabled():
    state = STATE_PATH.read_text()
    block = _block_between(state, "stage6_final_result_report_closeout:")

    assert "allow_final_report_metadata: true" in block
    assert "allow_stage6_closeout: true" in block
    assert "require_no_stage7: true" in block
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
    assert "allow_report_artifact_write: false" in block
    assert "external_validation_allowed: false" in block
    assert "allow_external_validation: false" in block
    assert "performance_claims_allowed: false" in block
    assert "performance_claims_added: false" in block


def test_current_feature_records_stage6_complete():
    current_feature = CURRENT_FEATURE_PATH.read_text()

    assert "## STAGE6-COMPLETE" in current_feature
    assert "Status: completed" in current_feature
    assert "STAGE6-F007 is complete." in current_feature
    assert "Stage 6 is complete." in current_feature
    assert "No Stage 7 is required." in current_feature
    assert "No real-cohort performance claim is added." in current_feature
    assert "Prediction and metric computation were limited to in-memory donor-level records." in current_feature
    assert "No prediction manifest was written." in current_feature
    assert "No metric table was written." in current_feature
    assert "No external validation was performed." in current_feature
