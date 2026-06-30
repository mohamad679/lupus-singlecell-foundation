import csv
import importlib.util
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPO_ROOT / "configs" / "calibration.yaml"
MODULE_PATH = REPO_ROOT / "src" / "evaluation" / "calibration_protocol.py"
RESULT_PATH = REPO_ROOT / "reports" / "tables" / "calibration_results.csv"
RELIABILITY_PATH = (
    REPO_ROOT / "reports" / "tables" / "reliability_diagram_manifest.csv"
)
STATE_PATH = REPO_ROOT / "state" / "project_state.yaml"

RESULT_HEADERS = [
    "run_id",
    "dataset_id",
    "model_family",
    "task",
    "prediction_unit",
    "n_patients",
    "brier_score",
    "ece",
    "ece_binning_strategy",
    "n_bins",
    "label_verified",
    "leakage_checks_passed",
    "status",
    "audit_status",
    "notes",
]
RELIABILITY_HEADERS = [
    "figure_id",
    "run_id",
    "dataset_id",
    "model_family",
    "task",
    "prediction_unit",
    "plot_type",
    "source_predictions",
    "label_verified",
    "leakage_checks_passed",
    "status",
    "audit_status",
    "notes",
]


def load_module():
    spec = importlib.util.spec_from_file_location(
        "calibration_protocol", MODULE_PATH
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def valid_mock_row():
    return {
        "run_id": "mock-run-001",
        "dataset_id": "MOCK_DATASET",
        "model_family": "mock_model",
        "task": "SLE diagnosis / case-control prediction",
        "prediction_unit": "patient",
        "n_patients": 20,
        "brier_score": "TODO",
        "ece": "TODO",
        "ece_binning_strategy": "TODO",
        "n_bins": "TODO",
        "label_verified": True,
        "leakage_checks_passed": True,
        "status": "mock_only",
        "audit_status": "mock_only",
        "notes": "mock metadata only; no calibration computed",
    }


def test_config_exists_and_disables_calibration_uncertainty_plots_and_claims():
    assert CONFIG_PATH.exists()
    module = load_module()
    config = module.load_calibration_config()

    assert config["allow_real_calibration"] is False
    assert config["allow_uncertainty_methods"] is False
    assert config["allow_reliability_plots"] is False
    assert config["allow_performance_claims"] is False
    assert config["require_patient_level_predictions"] is True
    assert config["require_verified_labels"] is True
    assert config["require_leakage_checks_passed"] is True


def test_calibration_and_reliability_tables_are_headers_only():
    module = load_module()
    with RESULT_PATH.open(newline="") as handle:
        result_rows = list(csv.reader(handle))
    with RELIABILITY_PATH.open(newline="") as handle:
        reliability_rows = list(csv.reader(handle))

    assert result_rows == [RESULT_HEADERS]
    assert reliability_rows == [RELIABILITY_HEADERS]
    module.validate_calibration_results_headers(result_rows[0])
    module.validate_reliability_manifest_headers(reliability_rows[0])


def test_refuse_calibration_if_disabled_raises():
    module = load_module()
    config = module.load_calibration_config()

    with pytest.raises(module.CalibrationProtocolError, match="calibration"):
        module.refuse_calibration_if_disabled(config)


def test_cell_level_calibration_is_rejected():
    module = load_module()

    with pytest.raises(module.CalibrationProtocolError, match="cell-level"):
        module.reject_cell_level_calibration("cell")


def test_valid_mock_patient_level_calibration_row_passes():
    module = load_module()

    module.validate_mock_calibration_rows([valid_mock_row()])


def test_unverified_label_fails():
    module = load_module()
    row = valid_mock_row()
    row["label_verified"] = False

    with pytest.raises(module.CalibrationProtocolError, match="label_verified"):
        module.validate_mock_calibration_rows([row])


def test_failed_leakage_checks_fail():
    module = load_module()
    row = valid_mock_row()
    row["leakage_checks_passed"] = False

    with pytest.raises(
        module.CalibrationProtocolError,
        match="leakage_checks_passed",
    ):
        module.validate_mock_calibration_rows([row])


def test_missing_audit_status_fails():
    module = load_module()
    row = valid_mock_row()
    row["audit_status"] = ""

    with pytest.raises(module.CalibrationProtocolError, match="audit_status"):
        module.validate_mock_calibration_rows([row])


def test_state_preserves_modeling_and_dataset_locks():
    state = STATE_PATH.read_text()

    assert "current_phase: Stage 2" in state
    assert "current_feature: STAGE2-CLOSEOUT" in state
    assert "primary_task: Active SLE flare discrimination" in state
    assert "allow_modeling: false" in state
    assert "modeling_allowed: false" in state
    assert "selected_datasets: []" in state
    assert "external_validation_cohort: TODO" in state


def test_protocol_has_no_metric_plot_uncertainty_or_data_imports():
    source = MODULE_PATH.read_text().lower()
    forbidden_fragments = [
        "import sklearn",
        "from sklearn",
        "import pandas",
        "import numpy",
        "import scanpy",
        "import anndata",
        "import scipy",
        "import matplotlib",
        "import seaborn",
        "brier_score_loss",
        "from sklearn.calibration",
        "sklearn.calibration.calibration_curve(",
        ".fit(",
        ".predict(",
        ".savefig(",
    ]

    for fragment in forbidden_fragments:
        assert fragment not in source


def test_no_model_or_plot_artifacts_exist():
    forbidden_suffixes = {
        ".pkl",
        ".pt",
        ".pth",
        ".onnx",
        ".joblib",
        ".ckpt",
        ".png",
        ".jpg",
        ".jpeg",
        ".svg",
        ".pdf",
    }
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
