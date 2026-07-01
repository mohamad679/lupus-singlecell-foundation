from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = REPO_ROOT / "state" / "project_state.yaml"
CURRENT_FEATURE_PATH = REPO_ROOT / "state" / "current_feature.md"


def test_stage3_closeout_marks_stage3_complete_and_stage4_pending():
    state = STATE_PATH.read_text()

    assert "current_phase: Stage 3" in state
    assert "current_feature: STAGE3-CLOSEOUT" in state
    assert "status: stage3_complete" in state
    assert "stage3_modeling_readiness_gate:" in state
    assert "stage3_closeout:" in state
    assert "stage4_planning:" in state
    assert "next_phase: Stage 4" in state
    assert "next_feature: STAGE4-F001" in state


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


def test_stage3_closeout_preserves_safety_locks():
    state = STATE_PATH.read_text()

    assert "modeling_allowed: false" in state
    assert "training_allowed: false" in state
    assert "external_validation_allowed: false" in state
    assert "performance_claims_allowed: false" in state
    assert "downloads_allowed: false" in state
    assert "anndata_loading_allowed: false" in state
    assert "geneformer_execution_allowed: false" in state
    assert "tokenizer_execution_allowed: false" in state
    assert "metric_computation_allowed: false" in state
    assert "model_fitting_allowed: false" in state


def test_stage3_closeout_current_feature_document_is_final():
    current_feature = CURRENT_FEATURE_PATH.read_text()

    assert "STAGE3-CLOSEOUT - Stage 3 closeout" in current_feature
    assert "Status: completed" in current_feature
    assert "Stage 3 is complete" in current_feature
    assert "Next phase: Stage 4" in current_feature
    assert "No real embedding artifacts are loaded in this closeout" in current_feature
