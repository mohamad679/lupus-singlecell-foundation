from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = REPO_ROOT / "state" / "project_state.yaml"
CURRENT_FEATURE_PATH = REPO_ROOT / "state" / "current_feature.md"


def _block_between(text, start_marker, end_marker=None):
    start = text.index(start_marker)
    end = text.index(end_marker, start) if end_marker else len(text)
    return text[start:end]




def test_stage4_f002_run_plan_block_is_retained_after_f004_start():
    state = STATE_PATH.read_text()
    block = _block_between(
        state,
        "stage4_real_donor_aggregation_run_plan:",
        "stage4_real_leakage_safe_split_manifest_validation:",
    )

    assert "status: stage4_f004_complete" in state
    assert "current_phase: Stage 4" in state
    assert "current_feature: STAGE4-F004-CLOSEOUT" in state
    assert "status: completed" in block
    assert "current_feature: STAGE4-F002" in block
    assert "closeout_feature: STAGE4-F002-CLOSEOUT" in block
    assert "next_feature: STAGE4-F003" in block

def test_stage4_f002_run_plan_records_identity_donor_strategy_after_closeout():
    state = STATE_PATH.read_text()
    block = _block_between(
        state,
        "stage4_real_donor_aggregation_run_plan:",
        "stage4_real_leakage_safe_split_manifest_validation:",
    )

    assert "aggregation_strategy: identity_donor_embedding_directory" in block
    assert "input_artifact_format: npy_directory" in block
    assert "input_record_level: donor" in block
    assert "output_record_level: donor" in block
    assert "split_level: donor" in block
    assert "expected_donor_file_count: 261" in block
    assert "observed_donor_file_count: 261" in block
    assert "observed_total_size_bytes: 360839808" in block
    assert "requires_cell_to_donor_pooling: false" in block
    assert "requires_payload_loading: false" in block
    assert "requires_real_aggregation_execution: false" in block


def test_stage4_f002_run_plan_preserves_safety_locks_after_closeout():
    state = STATE_PATH.read_text()
    block = _block_between(
        state,
        "stage4_real_donor_aggregation_run_plan:",
        "stage4_real_leakage_safe_split_manifest_validation:",
    )

    assert "allow_real_artifact_loading: false" in block
    assert "allow_npy_payload_loading: false" in block
    assert "allow_embedding_vector_parsing: false" in block
    assert "allow_real_aggregation_execution: false" in block
    assert "allow_model_fitting: false" in block
    assert "allow_metric_computation: false" in block
    assert "modeling_allowed: false" in block
    assert "training_allowed: false" in block
    assert "external_validation_allowed: false" in block
    assert "performance_claims_allowed: false" in block




def test_stage4_f002_current_feature_document_has_advanced_to_f004():
    current_feature = CURRENT_FEATURE_PATH.read_text()

    assert "STAGE4-F004-CLOSEOUT - Real evaluation input readiness validation closeout" in current_feature
    assert "Status: completed" in current_feature
    assert "STAGE4-F004 - Real evaluation input readiness validation" in current_feature
    assert "No evaluation array is materialized" in current_feature
    assert "No label array is created from real data" in current_feature
    assert "No predictions are generated" in current_feature
    assert "No real metrics are computed" in current_feature
    assert "STAGE4-F005 - Real pre-modeling audit gate" in current_feature