import csv
import importlib.util
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPO_ROOT / "configs" / "logistic_regression_baseline.yaml"
MODULE_PATH = REPO_ROOT / "src" / "models" / "logistic_regression_baseline.py"
RESULTS_PATH = REPO_ROOT / "reports" / "tables" / "logistic_regression_results.csv"
COEFFICIENTS_PATH = (
    REPO_ROOT / "reports" / "tables" / "logistic_regression_coefficients.csv"
)
STATE_PATH = REPO_ROOT / "state" / "project_state.yaml"

RESULTS_HEADERS = [
    "run_id",
    "dataset_id",
    "task",
    "split_policy",
    "model_family",
    "regularization",
    "class_weight",
    "auroc",
    "auprc",
    "balanced_accuracy",
    "f1",
    "sensitivity",
    "specificity",
    "brier_score",
    "ece",
    "status",
    "audit_status",
    "notes",
]
COEFFICIENT_HEADERS = [
    "run_id",
    "feature_id",
    "gene_id",
    "gene_symbol",
    "cell_type",
    "coefficient",
    "coefficient_rank",
    "direction",
    "audit_status",
    "notes",
]


def load_module():
    spec = importlib.util.spec_from_file_location(
        "logistic_regression_baseline", MODULE_PATH
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_config_exists_and_disables_execution():
    assert CONFIG_PATH.exists()
    module = load_module()
    config = module.load_logistic_regression_config()

    assert config["task"] == "SLE diagnosis / case-control prediction"
    assert config["allow_training"] is False
    assert config["allow_prediction"] is False
    assert config["allow_model_artifacts"] is False
    assert config["input_feature_type"] == "patient_level_pseudobulk"
    assert config["forbid_cell_level_features"] is True
    assert config["split_policy"] == "patient_or_cohort_only"
    assert config["model_family"] == "logistic_regression"


def test_results_and_coefficients_tables_are_headers_only():
    assert RESULTS_PATH.exists()
    assert COEFFICIENTS_PATH.exists()
    module = load_module()

    with RESULTS_PATH.open(newline="") as handle:
        result_rows = list(csv.reader(handle))
    with COEFFICIENTS_PATH.open(newline="") as handle:
        coefficient_rows = list(csv.reader(handle))

    assert result_rows == [RESULTS_HEADERS]
    assert coefficient_rows == [COEFFICIENT_HEADERS]
    module.validate_results_table_headers(result_rows[0])


def test_refuse_training_if_disabled_raises():
    module = load_module()
    config = module.load_logistic_regression_config()

    with pytest.raises(module.LogisticRegressionScaffoldError, match="training"):
        module.refuse_training_if_disabled(config)


def test_valid_mock_required_inputs_manifest_passes():
    module = load_module()
    manifest = {
        "pseudobulk_feature_matrix": "MOCK_ONLY",
        "patient_level_labels": "MOCK_ONLY",
        "split_manifest": "MOCK_ONLY",
        "feature_manifest": "MOCK_ONLY",
        "input_feature_type": "patient_level_pseudobulk",
        "split_policy": "patient_or_cohort_only",
        "audit_status": "mock_only",
    }

    module.validate_required_inputs_manifest(manifest)


def test_cell_level_feature_manifest_is_rejected():
    module = load_module()
    manifest = {
        "pseudobulk_feature_matrix": "MOCK_ONLY",
        "patient_level_labels": "MOCK_ONLY",
        "split_manifest": "MOCK_ONLY",
        "feature_manifest": "MOCK_ONLY",
        "input_feature_type": "cell_level_expression",
        "split_policy": "patient_or_cohort_only",
        "audit_status": "mock_only",
    }

    with pytest.raises(
        module.LogisticRegressionScaffoldError,
        match="patient_level_pseudobulk",
    ):
        module.validate_required_inputs_manifest(manifest)


def test_state_preserves_modeling_and_dataset_locks():
    state = STATE_PATH.read_text()

    assert "current_phase: Stage 1" in state
    assert "current_feature: STAGE1-F002" in state
    assert "primary_task: Active SLE flare discrimination" in state
    assert "allow_modeling: false" in state
    assert "modeling_allowed: false" in state
    assert "selected_datasets: []" in state
    assert "external_validation_cohort: TODO" in state


def test_scaffold_has_no_estimator_or_real_data_imports():
    source = MODULE_PATH.read_text().lower()
    forbidden_fragments = [
        "import sklearn",
        "from sklearn",
        "import pandas",
        "import numpy",
        "import scanpy",
        "import anndata",
        "import joblib",
        "import pickle",
        ".fit(",
        ".predict(",
        "predict_proba",
    ]

    for fragment in forbidden_fragments:
        assert fragment not in source


def test_no_model_artifact_files_exist():
    forbidden_suffixes = {".pkl", ".pt", ".pth", ".onnx", ".joblib", ".ckpt"}
    artifacts = [
        path
        for path in REPO_ROOT.rglob("*")
        if path.is_file()
        and ".git" not in path.parts
        and ".venv" not in path.parts
        and "__pycache__" not in path.parts
        and "data" not in path.parts
        and not str(path.relative_to(REPO_ROOT)).startswith("results/phase1/")
        and path.suffix.lower() in forbidden_suffixes
    ]

    assert artifacts == []
