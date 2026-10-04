"""Baseline evaluation protocol and mock prediction validation.

This module validates local protocol metadata, table headers, and caller-
provided mock prediction rows. It does not read predictions, compute metrics,
train models, load datasets, or create artifacts.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Mapping, Sequence


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = REPO_ROOT / "configs" / "evaluation.yaml"

APPROVED_TASK = "SLE diagnosis / case-control prediction"
CLASSIFICATION_METRICS = {
    "auroc",
    "auprc",
    "balanced_accuracy",
    "f1",
    "sensitivity",
    "specificity",
}
CALIBRATION_METRICS = {"brier_score", "expected_calibration_error"}
UNCERTAINTY_LATER = {"entropy", "risk_coverage", "selective_prediction"}
FORBIDDEN_ACTIONS = {
    "report_metric_without_verified_labels",
    "evaluate_cell_level_predictions_as_patient_level",
    "use_test_set_for_threshold_selection",
    "claim_clinical_utility",
}
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
ALLOWED_PREDICTION_UNITS = {"patient", "patient_id", "donor", "donor_id", "sample", "sample_id"}
FORBIDDEN_PREDICTION_UNITS = {"cell", "cell_id", "cell_level", "barcode"}


class EvaluationProtocolError(ValueError):
    """Raised when evaluation protocol safety validation fails."""


def load_evaluation_config(
    path: Path | str = DEFAULT_CONFIG_PATH,
) -> Dict[str, Any]:
    """Load and validate JSON-compatible YAML without metric dependencies."""
    config_path = Path(path)
    try:
        config = json.loads(config_path.read_text())
    except json.JSONDecodeError as exc:
        raise EvaluationProtocolError(
            f"{config_path} must use JSON-compatible YAML syntax"
        ) from exc
    if not isinstance(config, dict):
        raise EvaluationProtocolError("evaluation config must be a mapping")
    validate_evaluation_config(config)
    return config


def validate_evaluation_config(config: Mapping[str, Any]) -> None:
    """Validate required protocol gates and metric lists."""
    if config.get("task") != APPROVED_TASK:
        raise EvaluationProtocolError("task is outside Human Gate 2 scope")
    for field in ["allow_real_evaluation", "allow_performance_claims"]:
        if config.get(field) is not False:
            raise EvaluationProtocolError(f"{field} must be false")
    required_true = [
        "require_patient_level_predictions",
        "require_verified_labels",
        "require_split_manifest",
        "require_leakage_checks_passed",
        "external_validation_required_later",
    ]
    for field in required_true:
        if config.get(field) is not True:
            raise EvaluationProtocolError(f"{field} must be true")

    metrics = config.get("metrics")
    if not isinstance(metrics, Mapping):
        raise EvaluationProtocolError("metrics must be a mapping")
    expected_metrics = {
        "classification": CLASSIFICATION_METRICS,
        "calibration": CALIBRATION_METRICS,
        "uncertainty_later": UNCERTAINTY_LATER,
    }
    for section, expected in expected_metrics.items():
        values = metrics.get(section)
        if not isinstance(values, list) or set(values) != expected:
            raise EvaluationProtocolError(f"metrics.{section} is invalid")

    confidence_intervals = config.get("confidence_intervals")
    if not isinstance(confidence_intervals, Mapping):
        raise EvaluationProtocolError("confidence_intervals must be a mapping")
    if confidence_intervals.get("enabled_later") is not True:
        raise EvaluationProtocolError("confidence intervals must be enabled later")
    if confidence_intervals.get("method") != "bootstrap":
        raise EvaluationProtocolError("confidence interval method must be bootstrap")
    if confidence_intervals.get("n_bootstraps") != "TODO":
        raise EvaluationProtocolError("n_bootstraps must remain TODO")

    forbidden = config.get("forbidden")
    if not isinstance(forbidden, list) or set(forbidden) != FORBIDDEN_ACTIONS:
        raise EvaluationProtocolError("forbidden actions are invalid")


def validate_evaluation_results_headers(columns: Sequence[str]) -> None:
    """Require the exact header-only evaluation results contract."""
    if list(columns) != RESULT_HEADERS:
        raise EvaluationProtocolError("evaluation results headers are invalid")


def validate_prediction_manifest_headers(columns: Sequence[str]) -> None:
    """Require the exact header-only prediction manifest contract."""
    if list(columns) != PREDICTION_HEADERS:
        raise EvaluationProtocolError("prediction manifest headers are invalid")


def refuse_evaluation_if_disabled(config: Mapping[str, Any]) -> None:
    """Refuse real evaluation and performance reporting in scaffold mode."""
    if config.get("allow_real_evaluation") is not True:
        raise EvaluationProtocolError("real evaluation is disabled")
    if config.get("allow_performance_claims") is not True:
        raise EvaluationProtocolError("performance claims are disabled")


def reject_cell_level_evaluation(prediction_unit: Any) -> None:
    """Reject cell-level and unsupported evaluation units."""
    unit = str(prediction_unit).strip().lower()
    if unit in FORBIDDEN_PREDICTION_UNITS:
        raise EvaluationProtocolError(
            f"cell-level evaluation is forbidden: {unit}"
        )
    if unit not in ALLOWED_PREDICTION_UNITS:
        raise EvaluationProtocolError(
            "prediction_unit must be patient, donor, or linked sample"
        )


def _missing(value: Any) -> bool:
    return value is None or str(value).strip() == ""


def _as_true(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "yes", "1"}


def validate_mock_prediction_rows(rows: Sequence[Mapping[str, Any]]) -> None:
    """Validate mock rows without computing metrics or reading prediction data."""
    required_values = [
        "run_id",
        "dataset_id",
        "split",
        "true_label",
        "predicted_score",
        "predicted_label",
        "prediction_unit",
        "audit_status",
    ]
    for index, row in enumerate(rows, start=1):
        if not isinstance(row, Mapping):
            raise EvaluationProtocolError(f"row {index} must be a mapping")
        missing_fields = [field for field in PREDICTION_HEADERS if field not in row]
        if missing_fields:
            raise EvaluationProtocolError(
                f"row {index} missing fields: " + ", ".join(missing_fields)
            )
        missing_values = [field for field in required_values if _missing(row.get(field))]
        if missing_values:
            raise EvaluationProtocolError(
                f"row {index} missing required values: " + ", ".join(missing_values)
            )

        reject_cell_level_evaluation(row.get("prediction_unit"))
        if not any(
            not _missing(row.get(field))
            for field in ["patient_id", "donor_id", "sample_id"]
        ):
            raise EvaluationProtocolError(
                f"row {index} requires patient, donor, or sample identifier"
            )
        if not _as_true(row.get("label_verified")):
            raise EvaluationProtocolError(f"row {index} label_verified must be true")
        if not _as_true(row.get("leakage_checks_passed")):
            raise EvaluationProtocolError(
                f"row {index} leakage_checks_passed must be true"
            )
