from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = REPO_ROOT / "state" / "project_state.yaml"
CURRENT_FEATURE_PATH = REPO_ROOT / "state" / "current_feature.md"


def _block_between(text, start_marker, end_marker=None):
    start = text.index(start_marker)
    end = text.index(end_marker, start) if end_marker else len(text)
    return text[start:end]


def test_stage4_f003_is_current_project_feature():
    state = STATE_PATH.read_text()

    assert "status: stage4_f003_in_progress" in state
    assert "current_phase: Stage 4" in state
    assert "current_feature: STAGE4-F003" in state
    assert "stage4_real_leakage_safe_split_manifest_validation:" in state
    assert "next_feature: STAGE4-F004" in state
    assert "next_feature_name: Real evaluation input readiness validation" in state


def test_stage4_f003_records_donor_level_split_manifest_scope():
    state = STATE_PATH.read_text()
    block = _block_between(state, "stage4_real_leakage_safe_split_manifest_validation:")

    assert "status: in_progress" in block
    assert "branch: feat/stage4-real-leakage-safe-split-manifest-validation" in block
    assert "current_feature: STAGE4-F003" in block
    assert "input_artifact_format: npy_directory" in block
    assert "input_record_level: donor" in block
    assert "required_split_level: donor" in block
    assert "expected_real_donor_count: 261" in block
    assert "donor_id values must be unique" in block
    assert "donor_id values must not appear in multiple splits" in block
    assert "cell-level split columns are prohibited" in block


def test_stage4_f003_preserves_safety_locks():
    state = STATE_PATH.read_text()
    block = _block_between(state, "stage4_real_leakage_safe_split_manifest_validation:")

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
    assert "load .npy embedding payloads" in block
    assert "aggregate real embeddings" in block
    assert "compute metrics" in block
    assert "add performance claims" in block


def test_stage4_f003_current_feature_document_describes_safe_scope():
    current_feature = CURRENT_FEATURE_PATH.read_text()

    assert "STAGE4-F003 - Real leakage-safe split manifest validation" in current_feature
    assert "Status: in_progress" in current_feature
    assert "donor-level split manifest contract" in current_feature
    normalized_current_feature = " ".join(current_feature.split())
    assert "Donor IDs must not leak across train, validation, and test assignments" in normalized_current_feature
    assert "No `.npy` embedding payload is loaded" in current_feature
    assert "No real donor-level aggregation is executed" in current_feature
    assert "No real metrics are computed" in current_feature
    assert "STAGE4-F004 - Real evaluation input readiness validation" in current_feature
