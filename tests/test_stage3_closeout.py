from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = REPO_ROOT / "state" / "project_state.yaml"


def _block_between(text, start_marker, end_marker=None):
    start = text.index(start_marker)
    end = text.index(end_marker, start) if end_marker else len(text)
    return text[start:end]


def test_stage3_closeout_historical_record_marks_stage3_complete():
    state = STATE_PATH.read_text()
    block = _block_between(state, "stage3_closeout:", "stage4_planning:")

    assert "status: completed" in block
    assert "current_feature: STAGE3-CLOSEOUT" in block
    assert "stage3_complete: true" in block
    assert "next_phase: Stage 4" in block
    assert "next_feature: STAGE4-F001" in block


def test_stage3_closeout_completes_all_stage3_feature_blocks():
    state = STATE_PATH.read_text()

    expected_blocks = [
        "stage3_embedding_artifact_schema:",
        "stage3_patient_aggregation_design:",
        "stage3_leakage_safe_splits:",
        "stage3_evaluation_protocol_scaffold:",
        "stage3_baseline_control_plan:",
        "stage3_modeling_readiness_gate:",
    ]

    for block in expected_blocks:
        block_start = state.index(block)
        block_text = state[block_start : block_start + 220]
        assert "status: completed" in block_text


def test_stage3_closeout_historical_record_preserves_safety_locks():
    state = STATE_PATH.read_text()
    block = _block_between(state, "stage3_closeout:", "stage4_planning:")

    assert "modeling_allowed: false" in block
    assert "training_allowed: false" in block
    assert "external_validation_allowed: false" in block
    assert "performance_claims_allowed: false" in block
    assert "downloads_allowed: false" in block
    assert "anndata_loading_allowed: false" in block
    assert "geneformer_execution_allowed: false" in block
    assert "tokenizer_execution_allowed: false" in block
    assert "metric_computation_allowed: false" in block
    assert "model_fitting_allowed: false" in block
