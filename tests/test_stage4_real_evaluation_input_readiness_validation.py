from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = REPO_ROOT / "state" / "project_state.yaml"
CURRENT_FEATURE_PATH = REPO_ROOT / "state" / "current_feature.md"


def _block_between(text, start_marker, end_marker=None):
    start = text.index(start_marker)
    end = text.index(end_marker, start) if end_marker else len(text)
    return text[start:end]


def test_stage4_f004_is_current_project_feature():
    state = STATE_PATH.read_text()

    assert "status: stage4_f004_in_progress" in state
    assert "current_phase: Stage 4" in state
    assert "current_feature: STAGE4-F004" in state
    assert "stage4_real_evaluation_input_readiness_validation:" in state
    assert "next_feature: STAGE4-F005" in state
    assert "next_feature_name: Real pre-modeling audit gate" in state


def test_stage4_f004_records_readiness_scope_and_upstream_gates():
    state = STATE_PATH.read_text()
    block = _block_between(state, "stage4_real_evaluation_input_readiness_validation:")

    assert "status: in_progress" in block
    assert "branch: feat/stage4-real-evaluation-input-readiness-validation" in block
    assert "current_feature: STAGE4-F004" in block
    assert "artifact_validation_status: completed" in block
    assert "aggregation_plan_status: completed" in block
    assert "split_manifest_validation_status: completed" in block
    assert "input_artifact_format: npy_directory" in block
    assert "input_record_level: donor" in block
    assert "aggregation_strategy: identity_donor_embedding_directory" in block
    assert "split_level: donor" in block
    assert "expected_real_donor_count: 261" in block
    assert "observed_real_donor_count: 261" in block


def test_stage4_f004_preserves_safety_locks():
    state = STATE_PATH.read_text()
    block = _block_between(state, "stage4_real_evaluation_input_readiness_validation:")

    assert "allow_input_materialization: false" in block
    assert "allow_label_array_creation: false" in block
    assert "allow_npy_payload_loading: false" in block
    assert "allow_embedding_vector_parsing: false" in block
    assert "allow_split_execution: false" in block
    assert "allow_model_fitting: false" in block
    assert "allow_prediction_generation: false" in block
    assert "allow_metric_computation: false" in block
    assert "modeling_allowed: false" in block
    assert "training_allowed: false" in block
    assert "external_validation_allowed: false" in block
    assert "performance_claims_allowed: false" in block
    assert "materialize evaluation arrays" in block
    assert "generate predictions" in block
    assert "compute metrics" in block
    assert "add performance claims" in block


def test_stage4_f004_current_feature_document_describes_safe_scope():
    current_feature = CURRENT_FEATURE_PATH.read_text()

    assert "STAGE4-F004 - Real evaluation input readiness validation" in current_feature
    assert "Status: in_progress" in current_feature
    assert "Validate metadata-only readiness" in current_feature
    assert "No evaluation array is materialized" in current_feature
    assert "No label array is created from real data" in current_feature
    assert "No predictions are generated" in current_feature
    assert "No real metrics are computed" in current_feature
    assert "STAGE4-F005 - Real pre-modeling audit gate" in current_feature
