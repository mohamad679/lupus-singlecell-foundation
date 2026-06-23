from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "08_phase2_pipeline_scaffold.py"
STATE_PATH = REPO_ROOT / "state" / "project_state.yaml"
SRC_DIR = REPO_ROOT / "src"


def test_phase2_package_markers_exist():
    assert (SRC_DIR / "data" / "__init__.py").exists()
    assert (SRC_DIR / "qc" / "__init__.py").exists()
    assert (SRC_DIR / "utils" / "__init__.py").exists()


def test_scaffold_script_exists_and_has_no_network_or_process_clients():
    assert SCRIPT_PATH.exists()
    source = SCRIPT_PATH.read_text()

    forbidden_fragments = [
        "requests",
        "urllib",
        "http.client",
        "ftplib",
        "socket",
        "subprocess",
        "curl",
        "wget",
    ]

    for fragment in forbidden_fragments:
        assert fragment not in source


def test_scaffold_script_does_not_import_processing_or_modeling_libraries():
    source = SCRIPT_PATH.read_text().lower()

    forbidden_fragments = [
        "import scanpy",
        "import anndata",
        "from scanpy",
        "from anndata",
        "sklearn",
        "torch",
        "tensorflow",
        "xgboost",
        "lightgbm",
    ]

    for fragment in forbidden_fragments:
        assert fragment not in source


def test_selected_datasets_and_external_validation_remain_empty():
    state = STATE_PATH.read_text()

    assert "selected_datasets: []" in state
    assert "external_validation_cohort: TODO" in state


def test_no_model_files_are_created():
    forbidden_paths = []
    for path in REPO_ROOT.rglob("*"):
        if ".git" in path.parts:
            continue
        lower_name = path.name.lower()
        if path.is_file() and lower_name.endswith(
            (".pkl", ".pt", ".pth", ".onnx", ".joblib")
        ):
            forbidden_paths.append(path)

    assert forbidden_paths == []


def test_models_package_contains_safe_scaffold_only():
    models_dir = SRC_DIR / "models"

    assert models_dir.exists()
    assert {path.name for path in models_dir.iterdir()} == {
        "__init__.py",
        "logistic_regression_baseline.py",
    }


def test_no_dataset_files_are_created():
    forbidden_suffixes = {
        ".h5ad",
        ".h5",
        ".loom",
        ".rds",
        ".mtx",
        ".tar",
        ".fastq",
    }
    forbidden_paths = []
    for path in REPO_ROOT.rglob("*"):
        if ".git" in path.parts:
            continue
        name = path.name.lower()
        if path.is_file() and (
            any(name.endswith(suffix) for suffix in forbidden_suffixes)
            or name.endswith(".fastq.gz")
            or name.endswith(".mtx.gz")
        ):
            forbidden_paths.append(path)

    assert forbidden_paths == []
