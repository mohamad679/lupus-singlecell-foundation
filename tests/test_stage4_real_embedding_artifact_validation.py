from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = REPO_ROOT / "state" / "project_state.yaml"
CURRENT_FEATURE_PATH = REPO_ROOT / "state" / "current_feature.md"
GITIGNORE_PATH = REPO_ROOT / ".gitignore"


def _block_between(text, start_marker, end_marker=None):
    start = text.index(start_marker)
    end = text.index(end_marker, start) if end_marker else len(text)
    return text[start:end]


def test_stage4_f001_is_current_project_feature():
    state = STATE_PATH.read_text()

    assert "status: stage4_f001_in_progress" in state
    assert "current_phase: Stage 4" in state
    assert "current_feature: STAGE4-F001" in state
    assert "stage4_real_embedding_artifact_validation:" in state


def test_stage4_f001_validation_block_keeps_runtime_and_modeling_blocked():
    state = STATE_PATH.read_text()
    block = _block_between(state, "stage4_real_embedding_artifact_validation:")

    assert "status: in_progress" in block
    assert "branch: feat/stage4-real-artifact-directory-manifest" in block
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


def test_stage4_f001_current_feature_document_describes_safe_scope():
    current_feature = CURRENT_FEATURE_PATH.read_text()

    assert "STAGE4-F001 - Real embedding artifact validation" in current_feature
    assert "Status: in_progress" in current_feature
    assert "No real embedding artifact is committed" in current_feature
    assert "No AnnData files are loaded" in current_feature
    assert "No Geneformer execution is performed" in current_feature
    assert "No real metrics are computed" in current_feature
    assert "directory of 261 `.npy` files" in current_feature
    assert "absolute local path is not committed" in current_feature


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
