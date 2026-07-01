from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = REPO_ROOT / "state" / "project_state.yaml"
CURRENT_FEATURE_PATH = REPO_ROOT / "state" / "current_feature.md"
GITIGNORE_PATH = REPO_ROOT / ".gitignore"


def _block_between(text, start_marker, end_marker=None):
    start = text.index(start_marker)
    end = text.index(end_marker, start) if end_marker else len(text)
    return text[start:end]





def test_stage4_f001_validation_block_is_retained_after_f004_start():
    state = STATE_PATH.read_text()
    block = _block_between(
        state,
        "stage4_real_embedding_artifact_validation:",
        "stage4_real_donor_aggregation_run_plan:",
    )

    assert "status: stage4_f004_complete" in state
    assert "current_phase: Stage 4" in state
    assert "current_feature: STAGE4-F004-CLOSEOUT" in state
    assert "status: completed" in block
    assert "current_feature: STAGE4-F001" in block
    assert "closeout_feature: STAGE4-F001-CLOSEOUT" in block
    assert "next_feature: STAGE4-F002" in block

def test_stage4_f001_validation_block_keeps_runtime_and_modeling_blocked():
    state = STATE_PATH.read_text()
    block = _block_between(state, "stage4_real_embedding_artifact_validation:")

    assert "status: completed" in block
    assert "branch: chore/stage4-f001-closeout" in block
    assert "artifact_commit_allowed: false" in block
    assert "large_artifact_commit_allowed: false" in block
    assert "modeling_allowed: false" in block
    assert "training_allowed: false" in block
    assert "external_validation_allowed: false" in block
    assert "performance_claims_allowed: false" in block
    assert "load AnnData files" in block
    assert "execute Geneformer" in block
    assert "parse embedding payload tables" in block
    assert "load .npy embedding payloads" in block
    assert "observed_artifact_format: npy_directory" in block
    assert "observed_file_count: 261" in block
    assert "observed_total_size_bytes: 360839808" in block
    assert "compute metrics" in block





def test_stage4_f001_current_feature_document_has_advanced_to_f004():
    current_feature = CURRENT_FEATURE_PATH.read_text()

    assert "STAGE4-F004-CLOSEOUT - Real evaluation input readiness validation closeout" in current_feature
    assert "Status: completed" in current_feature
    assert "STAGE4-F004 - Real evaluation input readiness validation" in current_feature
    assert "No evaluation array is materialized" in current_feature
    assert "No label array is created from real data" in current_feature
    assert "No predictions are generated" in current_feature
    assert "No real metrics are computed" in current_feature
    assert "STAGE4-F005 - Real pre-modeling audit gate" in current_feature

def test_gitignore_blocks_large_local_embedding_and_model_artifacts():
    gitignore = GITIGNORE_PATH.read_text()

    expected_patterns = [
        "data/",
        "artifacts/",
        "outputs/",
        "local_artifacts/",
        "*.h5ad",
        "*.parquet",
        "*.npz",
        "*.npy",
        "*.pt",
        "*.safetensors",
        "*.joblib",
    ]

    for pattern in expected_patterns:
        assert pattern in gitignore
