"""Calibration protocol and mock result-row validation.

This module validates local calibration metadata and table headers only. It
does not load predictions, compute calibration metrics, generate reliability
plots, implement uncertainty methods, or make performance claims.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Mapping, Sequence


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = REPO_ROOT / "configs" / "calibration.yaml"

APPROVED_TASK = "SLE diagnosis / case-control prediction"
CALIBRATION_METRICS = {"brier_score", "expected_calibration_error"}
PLANNED_PLOTS = {
    "reliability_diagram",
    "calibration_curve",
    "risk_coverage_curve_later",
}
FORBIDDEN_ACTIONS = {
    "compute_calibration_without_verified_labels",
    "compute_calibration_on_cell_level_predictions",
    "claim_uncertainty_without_uncertainty_protocol",
    "generate_reliability_plot_without_predictions",
}
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
ALLOWED_PREDICTION_UNITS = {
    "patient",
    "patient_id",
    "donor",
    "donor_id",
    "sample",
    "sample_id",
}
FORBIDDEN_PREDICTION_UNITS = {"cell", "cell_id", "cell_level", "barcode"}


class CalibrationProtocolError(ValueError):
    """Raised when calibration scaffold validation fails."""


def load_calibration_config(
    path: Path | str = DEFAULT_CONFIG_PATH,
) -> Dict[str, Any]:
    """Load and validate JSON-compatible YAML without metric dependencies."""
    config_path = Path(path)
    try:
        config = json.loads(config_path.read_text())
    except json.JSONDecodeError as exc:
        raise CalibrationProtocolError(
            f"{config_path} must use JSON-compatible YAML syntax"
        ) from exc
    if not isinstance(config, dict):
        raise CalibrationProtocolError("calibration config must be a mapping")
    validate_calibration_config(config)
    return config


def validate_calibration_config(config: Mapping[str, Any]) -> None:
    """Validate all calibration, uncertainty, plotting, and claim gates."""
    if config.get("task") != APPROVED_TASK:
        raise CalibrationProtocolError("task is outside Human Gate 2 scope")

    required_false = [
        "allow_real_calibration",
        "allow_uncertainty_methods",
        "allow_reliability_plots",
        "allow_performance_claims",
    ]
    for field in required_false:
        if config.get(field) is not False:
            raise CalibrationProtocolError(f"{field} must be false")

    required_true = [
        "require_patient_level_predictions",
        "require_verified_labels",
        "require_leakage_checks_passed",
    ]
    for field in required_true:
        if config.get(field) is not True:
            raise CalibrationProtocolError(f"{field} must be true")

    metrics = config.get("metrics")
    if not isinstance(metrics, list) or set(metrics) != CALIBRATION_METRICS:
        raise CalibrationProtocolError("calibration metrics are invalid")

    plots = config.get("planned_plots_later")
    if not isinstance(plots, list) or set(plots) != PLANNED_PLOTS:
        raise CalibrationProtocolError("planned_plots_later are invalid")

    ece_policy = config.get("ece_policy")
    if not isinstance(ece_policy, Mapping):
        raise CalibrationProtocolError("ece_policy must be a mapping")
    if ece_policy.get("binning_strategy") != "TODO":
        raise CalibrationProtocolError("ECE binning_strategy must remain TODO")
    if ece_policy.get("n_bins") != "TODO":
        raise CalibrationProtocolError("ECE n_bins must remain TODO")
    for field in ["adaptive_binning_later", "fixed_binning_later"]:
        if ece_policy.get(field) is not True:
            raise CalibrationProtocolError(f"ece_policy.{field} must be true")

    forbidden = config.get("forbidden")
    if not isinstance(forbidden, list) or set(forbidden) != FORBIDDEN_ACTIONS:
        raise CalibrationProtocolError("forbidden actions are invalid")


def validate_calibration_results_headers(columns: Sequence[str]) -> None:
    """Require the exact header-only calibration results contract."""
    if list(columns) != RESULT_HEADERS:
        raise CalibrationProtocolError("calibration results headers are invalid")


def validate_reliability_manifest_headers(columns: Sequence[str]) -> None:
    """Require the exact header-only reliability figure contract."""
    if list(columns) != RELIABILITY_HEADERS:
        raise CalibrationProtocolError(
            "reliability diagram manifest headers are invalid"
        )


def refuse_calibration_if_disabled(config: Mapping[str, Any]) -> None:
    """Refuse calibration, plots, uncertainty methods, and performance claims."""
    if config.get("allow_real_calibration") is not True:
        raise CalibrationProtocolError("real calibration is disabled")
    if config.get("allow_reliability_plots") is not True:
        raise CalibrationProtocolError("reliability plots are disabled")
    if config.get("allow_uncertainty_methods") is not True:
        raise CalibrationProtocolError("uncertainty methods are disabled")
    if config.get("allow_performance_claims") is not True:
        raise CalibrationProtocolError("performance claims are disabled")


def reject_cell_level_calibration(prediction_unit: Any) -> None:
    """Reject cell-level and unsupported calibration units."""
    unit = str(prediction_unit).strip().lower()
    if unit in FORBIDDEN_PREDICTION_UNITS:
        raise CalibrationProtocolError(
            f"cell-level calibration is forbidden: {unit}"
        )
    if unit not in ALLOWED_PREDICTION_UNITS:
        raise CalibrationProtocolError(
            "prediction_unit must be patient, donor, or linked sample"
        )


def _missing(value: Any) -> bool:
    return value is None or str(value).strip() == ""


def _as_true(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "yes", "1"}


def validate_mock_calibration_rows(
    rows: Sequence[Mapping[str, Any]],
) -> None:
    """Validate mock calibration metadata without computing any metric."""
    required_values = [
        "run_id",
        "dataset_id",
        "model_family",
        "task",
        "prediction_unit",
        "n_patients",
        "status",
        "audit_status",
    ]
    for index, row in enumerate(rows, start=1):
        if not isinstance(row, Mapping):
            raise CalibrationProtocolError(f"row {index} must be a mapping")
        missing_fields = [field for field in RESULT_HEADERS if field not in row]
        if missing_fields:
            raise CalibrationProtocolError(
                f"row {index} missing fields: " + ", ".join(missing_fields)
            )
        missing_values = [field for field in required_values if _missing(row.get(field))]
        if missing_values:
            raise CalibrationProtocolError(
                f"row {index} missing required values: " + ", ".join(missing_values)
            )

        reject_cell_level_calibration(row.get("prediction_unit"))
        if not _as_true(row.get("label_verified")):
            raise CalibrationProtocolError(
                f"row {index} label_verified must be true"
            )
        if not _as_true(row.get("leakage_checks_passed")):
            raise CalibrationProtocolError(
                f"row {index} leakage_checks_passed must be true"
            )

        try:
            n_patients = int(row.get("n_patients"))
        except (TypeError, ValueError) as exc:
            raise CalibrationProtocolError(
                f"row {index} n_patients must be an integer"
            ) from exc
        if n_patients <= 0:
            raise CalibrationProtocolError(
                f"row {index} n_patients must be greater than zero"
            )
