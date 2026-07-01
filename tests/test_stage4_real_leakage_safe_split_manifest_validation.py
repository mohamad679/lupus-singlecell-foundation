from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = REPO_ROOT / "state" / "project_state.yaml"
CURRENT_FEATURE_PATH = REPO_ROOT / "state" / "current_feature.md"


def _block_between(text, start_marker, end_marker=None):
    start = text.index(start_marker)
    end = text.index(end_marker, start) if end_marker else len(text)
    return text[start:end]




def test_stage4_f003_split_manifest_block_is_retained_after_f005_start():
    state = STATE_PATH.read_text()
    block = _block_between(
        state,
        "stage4_real_leakage_safe_split_manifest_validation:",
        "stage4_real_evaluation_input_readiness_validation:",
    )

    assert "status: stage4_f005_complete" in state
    assert "current_phase: Stage 4" in state
    assert "current_feature: STAGE4-F005-CLOSEOUT" in state
    assert "status: completed" in block
    assert "current_feature: STAGE4-F003" in block
    assert "closeout_feature: STAGE4-F003-CLOSEOUT" in block
    assert "next_feature: STAGE4-F004" in block

def test_stage4_f003_records_donor_level_split_manifest_scope_after_closeout():
    state = STATE_PATH.read_text()
    block = _block_between(
        state,
        "stage4_real_leakage_safe_split_manifest_validation:",
        "stage4_real_evaluation_input_readiness_validation:",
    )

    assert "input_artifact_format: npy_directory" in block
    assert "input_record_level: donor" in block
    assert "required_split_level: donor" in block
    assert "expected_real_donor_count: 261" in block
    assert "donor_id values must be unique" in block
    assert "donor_id values must not appear in multiple splits" in block
    assert "cell-level split columns are prohibited" in block


def test_stage4_f003_preserves_safety_locks_after_closeout():
    state = STATE_PATH.read_text()
    block = _block_between(
        state,
        "stage4_real_leakage_safe_split_manifest_validation:",
        "stage4_real_evaluation_input_readiness_validation:",
    )

    assert "allow_cell_level_splits: false" in block
    assert "allow_duplicate_donors_across_splits: false" in block
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





def test_stage4_f003_current_feature_document_has_advanced_to_f005_closeout():
    current_feature = CURRENT_FEATURE_PATH.read_text()

    assert "STAGE4-F005-CLOSEOUT - Real pre-modeling audit gate closeout" in current_feature
    assert "Status: completed" in current_feature
    assert "STAGE4-F005 - Real pre-modeling audit gate" in current_feature
    assert "No `.npy` embedding payload is loaded" in current_feature
    assert "No predictions are generated" in current_feature
    assert "No real metrics are computed" in current_feature
    assert "No performance claims are added" in current_feature
    assert "STAGE4-F006 - Stage 4 final closeout and modeling handoff decision" in current_feature