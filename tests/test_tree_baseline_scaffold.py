import csv
import importlib.util
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPO_ROOT / "configs" / "tree_baseline.yaml"
MODULE_PATH = REPO_ROOT / "src" / "models" / "tree_baselines.py"
RESULTS_PATH = REPO_ROOT / "reports" / "tables" / "tree_baseline_results.csv"
IMPORTANCE_PATH = REPO_ROOT / "reports" / "tables" / "tree_feature_importance.csv"
STATE_PATH = REPO_ROOT / "state" / "project_state.yaml"

RESULTS_HEADERS = [
    "run_id",
    "dataset_id",
    "task",
    "split_policy",
    "model_family",
    "hyperparameter_profile",
    "class_weight_or_scale_pos_weight",
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
IMPORTANCE_HEADERS = [
    "run_id",
    "model_family",
    "feature_id",
    "gene_id",
    "gene_symbol",
    "cell_type",
    "importance_value",
    "importance_rank",
    "importance_method",
    "audit_status",
    "notes",
]


def load_module():
    spec = importlib.util.spec_from_file_location("tree_baselines", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_config_exists_and_disables_tree_execution():
    assert CONFIG_PATH.exists()
    module = load_module()
    config = module.load_tree_baseline_config()

    assert config["task"] == "SLE diagnosis / case-control prediction"
    assert config["allow_training"] is False
    assert config["allow_prediction"] is False
    assert config["allow_model_artifacts"] is False
    assert config["input_feature_type"] == "patient_level_pseudobulk"
    assert config["forbid_cell_level_features"] is True
    assert config["split_policy"] == "patient_or_cohort_only"


def test_random_forest_and_xgboost_training_are_disabled():
    module = load_module()
    config = module.load_tree_baseline_config()
    families = config["model_families"]

    assert families["random_forest"]["enabled_for_training"] is False
    assert families["xgboost"]["enabled_for_training"] is False
    assert families["xgboost"]["optional_dependency"] is True
    module.validate_no_required_xgboost_dependency(config)


def test_results_and_importance_tables_are_headers_only():
    module = load_module()
    with RESULTS_PATH.open(newline="") as handle:
        result_rows = list(csv.reader(handle))
    with IMPORTANCE_PATH.open(newline="") as handle:
        importance_rows = list(csv.reader(handle))

    assert result_rows == [RESULTS_HEADERS]
    assert importance_rows == [IMPORTANCE_HEADERS]
    module.validate_tree_results_headers(result_rows[0])
    module.validate_tree_importance_headers(importance_rows[0])


def test_refuse_training_if_disabled_raises():
    module = load_module()
    config = module.load_tree_baseline_config()

    with pytest.raises(module.TreeBaselineScaffoldError, match="training"):
        module.refuse_training_if_disabled(config)


def test_required_xgboost_dependency_is_rejected():
    module = load_module()
    config = module.load_tree_baseline_config()
    config["model_families"]["xgboost"]["optional_dependency"] = False

    with pytest.raises(module.TreeBaselineScaffoldError, match="optional"):
        module.validate_no_required_xgboost_dependency(config)


def test_state_preserves_modeling_and_dataset_locks():
    state = STATE_PATH.read_text()

    assert "current_phase: Stage 2" in state
    assert "current_feature: STAGE2-F002" in state
    assert "primary_task: Active SLE flare discrimination" in state
    assert "allow_modeling: false" in state
    assert "modeling_allowed: false" in state
    assert "selected_datasets: []" in state
    assert "external_validation_cohort: TODO" in state


def test_scaffold_has_no_estimator_or_real_data_imports():
    source = MODULE_PATH.read_text().lower()
    forbidden_fragments = [
        "import xgboost",
        "from xgboost",
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
