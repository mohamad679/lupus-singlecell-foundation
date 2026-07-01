from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = REPO_ROOT / "state" / "project_state.yaml"
CURRENT_FEATURE_PATH = REPO_ROOT / "state" / "current_feature.md"


def _block_between(text, start_marker, end_marker=None):
    start = text.index(start_marker)
    end = text.index(end_marker, start) if end_marker else len(text)
    return text[start:end]




def test_stage4_f001_closeout_history_marks_feature_complete_and_next_feature_ready():
    state = STATE_PATH.read_text()
    block = _block_between(
        state,
        "stage4_real_embedding_artifact_validation:",
        "stage4_real_donor_aggregation_run_plan:",
    )

    assert "status: stage4_f003_in_progress" in state
    assert "current_phase: Stage 4" in state
    assert "current_feature: STAGE4-F003" in state
    assert "status: completed" in block
    assert "current_feature: STAGE4-F001" in block
    assert "closeout_feature: STAGE4-F001-CLOSEOUT" in block
    assert "next_feature: STAGE4-F002" in block
    assert "next_feature_name: Real donor-level aggregation run plan" in block

def test_stage4_f001_closeout_preserves_observed_npy_directory_metadata():
    state = STATE_PATH.read_text()
    block = _block_between(state, "stage4_real_embedding_artifact_validation:")

    assert "status: completed" in block
    assert "manifest_status: completed_observed_npy_directory_metadata_without_payload_loading" in block
    assert "observed_artifact_format: npy_directory" in block
    assert "observed_record_level: donor" in block
    assert "observed_file_count: 261" in block
    assert "observed_total_size_bytes: 360839808" in block
    assert "observed_total_size_mb: 344.12" in block
    assert "observed_all_files_same_size: true" in block
    assert "observed_min_file_size_bytes: 1382528" in block
    assert "observed_max_file_size_bytes: 1382528" in block
    assert "flare_like: 14" in block
    assert "healthy_hc_like: 48" in block
    assert "healthy_igtb_like: 50" in block
    assert "managed_sle_numeric_like: 148" in block
    assert "control_like: 1" in block


def test_stage4_f001_closeout_preserves_safety_locks():
    state = STATE_PATH.read_text()
    block = _block_between(state, "stage4_real_embedding_artifact_validation:")

    assert "artifact_commit_allowed: false" in block
    assert "large_artifact_commit_allowed: false" in block
    assert "modeling_allowed: false" in block
    assert "training_allowed: false" in block
    assert "external_validation_allowed: false" in block
    assert "performance_claims_allowed: false" in block
    assert "load .npy embedding payloads" in block
    assert "aggregate real embeddings" in block
    assert "fit models" in block
    assert "compute metrics" in block
    assert "add performance claims" in block




def test_stage4_f001_closeout_current_feature_document_has_advanced_to_f003():
    current_feature = CURRENT_FEATURE_PATH.read_text()
    normalized_current_feature = " ".join(current_feature.split())

    assert "STAGE4-F003 - Real leakage-safe split manifest validation" in current_feature
    assert "Status: in_progress" in current_feature
    assert "donor-level split manifest contract" in current_feature
    assert "Donor IDs must not leak across train, validation, and test assignments" in normalized_current_feature
    assert "No `.npy` embedding payload is loaded" in current_feature
    assert "No real donor-level aggregation is executed" in current_feature
    assert "No real metrics are computed" in current_feature
    assert "STAGE4-F004 - Real evaluation input readiness validation" in current_feature