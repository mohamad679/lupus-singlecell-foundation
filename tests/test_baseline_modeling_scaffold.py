import importlib.util
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "10_baseline_modeling_scaffold.py"


def load_module():
    spec = importlib.util.spec_from_file_location(
        "baseline_modeling_scaffold_validation", SCRIPT_PATH
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_scaffold_validation_summary_disables_execution():
    module = load_module()

    assert module.run_validation() == {
        "phase": 3,
        "approved_task": "SLE diagnosis / case-control prediction",
        "allow_training": False,
        "allow_deep_learning": False,
        "allow_foundation_models": False,
        "allow_uncertainty_methods": False,
        "split_policy": "patient_or_cohort_only",
        "forbid_cell_level_split": True,
        "design_family_count": 5,
        "training_family_count": 0,
    }


def test_scaffold_rejects_training_or_deep_learning_enablement():
    module = load_module()
    config = module.load_baseline_config()

    for field in [
        "allow_training",
        "allow_deep_learning",
        "allow_foundation_models",
        "allow_uncertainty_methods",
    ]:
        invalid = dict(config)
        invalid[field] = True
        with pytest.raises(module.BaselineScaffoldError, match=field):
            module.validate_baseline_config(invalid)


def test_scaffold_rejects_cell_level_split_policy():
    module = load_module()
    config = module.load_baseline_config()
    config["split_policy"] = "cell_level"

    with pytest.raises(module.BaselineScaffoldError, match="split_policy"):
        module.validate_baseline_config(config)


def test_scaffold_script_contains_no_training_or_data_clients():
    source = SCRIPT_PATH.read_text().lower()
    forbidden_fragments = [
        "import scanpy",
        "import anndata",
        "import sklearn",
        "from sklearn",
        "import torch",
        "from torch",
        "import tensorflow",
        "from tensorflow",
        "import xgboost",
        "from xgboost",
        "import lightgbm",
        "from lightgbm",
        "import joblib",
        "import pickle",
        "import requests",
        "import urllib",
        "import subprocess",
        ".fit(",
        "fit_predict",
        "train_test_split",
    ]

    for fragment in forbidden_fragments:
        assert fragment not in source


def test_no_serialized_model_artifacts_exist():
    forbidden_suffixes = {".pkl", ".pt", ".pth", ".onnx", ".joblib", ".ckpt"}
    artifacts = [
        path
        for path in REPO_ROOT.rglob("*")
        if path.is_file()
        and ".git" not in path.parts
        and path.suffix.lower() in forbidden_suffixes
    ]

    assert artifacts == []
