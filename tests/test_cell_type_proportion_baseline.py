import csv
import importlib.util
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPO_ROOT / "configs" / "cell_type_proportion_baseline.yaml"
MODULE_PATH = REPO_ROOT / "src" / "features" / "cell_type_proportions.py"
FEATURE_PATH = (
    REPO_ROOT / "reports" / "tables" / "cell_type_proportion_features.csv"
)
RESULT_PATH = (
    REPO_ROOT / "reports" / "tables" / "cell_type_proportion_results.csv"
)
STATE_PATH = REPO_ROOT / "state" / "project_state.yaml"

FEATURE_HEADERS = [
    "feature_id",
    "dataset_id",
    "aggregation_unit",
    "aggregation_id",
    "cell_type",
    "cell_count",
    "total_cells",
    "cell_type_fraction",
    "transformation_status",
    "split_group",
    "audit_status",
    "notes",
]
RESULT_HEADERS = [
    "run_id",
    "dataset_id",
    "task",
    "split_policy",
    "model_family",
    "feature_set",
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


def load_module():
    spec = importlib.util.spec_from_file_location(
        "cell_type_proportions", MODULE_PATH
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def valid_mock_row():
    return {
        "feature_id": "mock-composition-001",
        "dataset_id": "MOCK_DATASET",
        "aggregation_unit": "patient_id",
        "aggregation_id": "mock-patient-001",
        "cell_type": "mock-cell-type",
        "cell_count": 25,
        "total_cells": 100,
        "cell_type_fraction": 0.25,
        "transformation_status": "untransformed_mock",
        "split_group": "patient_level_train",
        "audit_status": "mock_only",
        "notes": "mock validation row; no real feature",
    }


def test_config_exists_and_disables_extraction_and_modeling():
    assert CONFIG_PATH.exists()
    module = load_module()
    config = module.load_cell_type_proportion_config()

    assert config["task"] == "SLE diagnosis / case-control prediction"
    assert config["allow_feature_extraction"] is False
    assert config["allow_training"] is False
    assert config["allow_prediction"] is False
    assert config["allow_model_artifacts"] is False
    assert config["input_feature_type"] == "patient_level_cell_type_proportions"
    assert config["forbid_cell_level_features"] is True
    assert config["require_cell_type_labels"] is True


def test_feature_and_result_tables_are_headers_only():
    module = load_module()
    with FEATURE_PATH.open(newline="") as handle:
        feature_rows = list(csv.reader(handle))
    with RESULT_PATH.open(newline="") as handle:
        result_rows = list(csv.reader(handle))

    assert feature_rows == [FEATURE_HEADERS]
    assert result_rows == [RESULT_HEADERS]
    module.validate_cell_type_feature_headers(feature_rows[0])
    module.validate_cell_type_result_headers(result_rows[0])


def test_valid_mock_cell_type_row_passes():
    module = load_module()

    module.validate_mock_cell_type_feature_rows([valid_mock_row()])


@pytest.mark.parametrize("aggregation_unit", ["cell_id", "barcode"])
def test_cell_level_aggregation_fails(aggregation_unit):
    module = load_module()
    row = valid_mock_row()
    row["aggregation_unit"] = aggregation_unit

    with pytest.raises(module.CellTypeProportionScaffoldError, match="cell-level"):
        module.validate_mock_cell_type_feature_rows([row])


def test_missing_audit_status_fails():
    module = load_module()
    row = valid_mock_row()
    row["audit_status"] = ""

    with pytest.raises(
        module.CellTypeProportionScaffoldError,
        match="audit_status",
    ):
        module.validate_mock_cell_type_feature_rows([row])


@pytest.mark.parametrize("fraction", [-0.01, 1.01])
def test_invalid_fraction_fails(fraction):
    module = load_module()
    row = valid_mock_row()
    row["cell_type_fraction"] = fraction

    with pytest.raises(
        module.CellTypeProportionScaffoldError,
        match="between zero and one",
    ):
        module.validate_mock_cell_type_feature_rows([row])


def test_nonpositive_total_cells_fails():
    module = load_module()
    row = valid_mock_row()
    row["total_cells"] = 0

    with pytest.raises(
        module.CellTypeProportionScaffoldError,
        match="greater than zero",
    ):
        module.validate_mock_cell_type_feature_rows([row])


def test_state_preserves_modeling_and_dataset_locks():
    state = STATE_PATH.read_text()

    assert 'current_phase: "Phase 3"' in state
    assert "current_feature: P3-F009" in state
    assert 'primary_task: "SLE diagnosis / case-control prediction"' in state
    assert "allow_modeling: false" in state
    assert "modeling_allowed: false" in state
    assert "selected_datasets: []" in state
    assert "external_validation_cohort: TODO" in state


def test_scaffold_has_no_real_data_or_modeling_imports():
    source = MODULE_PATH.read_text().lower()
    forbidden_fragments = [
        "import scanpy",
        "from scanpy",
        "import anndata",
        "from anndata",
        "import pandas",
        "import numpy",
        "import sklearn",
        "from sklearn",
        "import torch",
        "import tensorflow",
        ".fit(",
        ".predict(",
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
        and path.suffix.lower() in forbidden_suffixes
    ]

    assert artifacts == []
