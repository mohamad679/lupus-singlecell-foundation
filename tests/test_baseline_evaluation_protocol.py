import csv
import importlib.util
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPO_ROOT / "configs" / "evaluation.yaml"
MODULE_PATH = REPO_ROOT / "src" / "evaluation" / "evaluation_protocol.py"
RESULT_PATH = REPO_ROOT / "reports" / "tables" / "baseline_evaluation_results.csv"
PREDICTION_PATH = (
    REPO_ROOT / "reports" / "tables" / "baseline_prediction_manifest.csv"
)
STATE_PATH = REPO_ROOT / "state" / "project_state.yaml"

RESULT_HEADERS = [
    "run_id",
    "dataset_id",
    "model_family",
    "task",
    "split_policy",
    "evaluation_unit",
    "n_patients",
    "n_cases",
    "n_controls",
    "auroc",
    "auprc",
    "balanced_accuracy",
    "f1",
    "sensitivity",
    "specificity",
    "brier_score",
    "ece",
    "ci_method",
    "ci_lower",
    "ci_upper",
    "status",
    "audit_status",
    "notes",
]
PREDICTION_HEADERS = [
    "run_id",
    "patient_id",
    "donor_id",
    "sample_id",
    "dataset_id",
    "split",
    "true_label",
    "predicted_score",
    "predicted_label",
    "prediction_unit",
    "label_verified",
    "leakage_checks_passed",
    "audit_status",
    "notes",
]


def load_module():
    spec = importlib.util.spec_from_file_location(
        "evaluation_protocol", MODULE_PATH
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def valid_mock_prediction():
    return {
        "run_id": "mock-run-001",
        "patient_id": "mock-patient-001",
        "donor_id": "TODO",
        "sample_id": "mock-sample-001",
        "dataset_id": "MOCK_DATASET",
        "split": "test",
        "true_label": "SLE",
        "predicted_score": 0.75,
        "predicted_label": "SLE",
        "prediction_unit": "patient",
        "label_verified": True,
        "leakage_checks_passed": True,
        "audit_status": "mock_only",
        "notes": "mock validation row; no performance claim",
    }


def test_config_exists_and_disables_real_evaluation_and_claims():
    assert CONFIG_PATH.exists()
    module = load_module()
    config = module.load_evaluation_config()

    assert config["task"] == "SLE diagnosis / case-control prediction"
    assert config["allow_real_evaluation"] is False
    assert config["allow_performance_claims"] is False
    assert config["require_patient_level_predictions"] is True
    assert config["require_verified_labels"] is True
    assert config["require_split_manifest"] is True
    assert config["require_leakage_checks_passed"] is True


def test_results_and_prediction_tables_are_headers_only():
    module = load_module()
    with RESULT_PATH.open(newline="") as handle:
        result_rows = list(csv.reader(handle))
    with PREDICTION_PATH.open(newline="") as handle:
        prediction_rows = list(csv.reader(handle))

    assert result_rows == [RESULT_HEADERS]
    assert prediction_rows == [PREDICTION_HEADERS]
    module.validate_evaluation_results_headers(result_rows[0])
    module.validate_prediction_manifest_headers(prediction_rows[0])


def test_refuse_evaluation_if_disabled_raises():
    module = load_module()
    config = module.load_evaluation_config()

    with pytest.raises(module.EvaluationProtocolError, match="evaluation"):
        module.refuse_evaluation_if_disabled(config)


def test_cell_level_evaluation_is_rejected():
    module = load_module()

    with pytest.raises(module.EvaluationProtocolError, match="cell-level"):
        module.reject_cell_level_evaluation("cell")


def test_valid_mock_patient_prediction_passes():
    module = load_module()

    module.validate_mock_prediction_rows([valid_mock_prediction()])


def test_unverified_label_fails():
    module = load_module()
    row = valid_mock_prediction()
    row["label_verified"] = False

    with pytest.raises(module.EvaluationProtocolError, match="label_verified"):
        module.validate_mock_prediction_rows([row])


def test_failed_leakage_checks_fail():
    module = load_module()
    row = valid_mock_prediction()
    row["leakage_checks_passed"] = False

    with pytest.raises(
        module.EvaluationProtocolError,
        match="leakage_checks_passed",
    ):
        module.validate_mock_prediction_rows([row])


def test_missing_audit_status_fails():
    module = load_module()
    row = valid_mock_prediction()
    row["audit_status"] = ""

    with pytest.raises(module.EvaluationProtocolError, match="audit_status"):
        module.validate_mock_prediction_rows([row])


def test_state_preserves_modeling_and_dataset_locks():
    state = STATE_PATH.read_text()

    assert 'current_phase: "Phase 3"' in state
    assert "current_feature: P3-F011" in state
    assert 'primary_task: "SLE diagnosis / case-control prediction"' in state
    assert "allow_modeling: false" in state
    assert "modeling_allowed: false" in state
    assert "selected_datasets: []" in state
    assert "external_validation_cohort: TODO" in state


def test_protocol_has_no_metric_or_real_data_imports():
    source = MODULE_PATH.read_text().lower()
    forbidden_fragments = [
        "import sklearn",
        "from sklearn",
        "import pandas",
        "import numpy",
        "import scanpy",
        "import anndata",
        "import scipy",
        ".fit(",
        ".predict(",
        "roc_auc_score",
        "average_precision_score",
        "brier_score_loss",
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
