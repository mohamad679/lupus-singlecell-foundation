"""Restricted logistic regression baseline scaffold.

This module validates local configuration, caller-supplied manifest metadata,
and result-table headers. It does not load feature data, instantiate or fit an
estimator, generate predictions, compute metrics, or write model artifacts.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Mapping, Sequence


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = REPO_ROOT / "configs" / "logistic_regression_baseline.yaml"

APPROVED_TASK = "SLE diagnosis / case-control prediction"
INPUT_FEATURE_TYPE = "patient_level_pseudobulk"
SPLIT_POLICY = "patient_or_cohort_only"
MODEL_FAMILY = "logistic_regression"
REQUIRED_INPUTS = [
    "pseudobulk_feature_matrix",
    "patient_level_labels",
    "split_manifest",
    "feature_manifest",
]
RESULTS_TABLE_HEADERS = [
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


class LogisticRegressionScaffoldError(ValueError):
    """Raised when the logistic baseline violates restricted design scope."""


def load_logistic_regression_config(
    path: Path | str = DEFAULT_CONFIG_PATH,
) -> Dict[str, Any]:
    """Load and validate JSON-compatible YAML without external dependencies."""
    config_path = Path(path)
    try:
        config = json.loads(config_path.read_text())
    except json.JSONDecodeError as exc:
        raise LogisticRegressionScaffoldError(
            f"{config_path} must use JSON-compatible YAML syntax"
        ) from exc
    if not isinstance(config, dict):
        raise LogisticRegressionScaffoldError("logistic config must be a mapping")
    validate_logistic_regression_config(config)
    return config


def validate_logistic_regression_config(config: Mapping[str, Any]) -> None:
    """Validate that the scaffold cannot train, predict, or write artifacts."""
    expected_scalars = {
        "task": APPROVED_TASK,
        "input_feature_type": INPUT_FEATURE_TYPE,
        "split_policy": SPLIT_POLICY,
        "model_family": MODEL_FAMILY,
    }
    for field, expected in expected_scalars.items():
        if config.get(field) != expected:
            raise LogisticRegressionScaffoldError(
                f"{field} must be {expected}"
            )

    for field in ["allow_training", "allow_prediction", "allow_model_artifacts"]:
        if config.get(field) is not False:
            raise LogisticRegressionScaffoldError(f"{field} must be false")
    if config.get("forbid_cell_level_features") is not True:
        raise LogisticRegressionScaffoldError(
            "forbid_cell_level_features must be true"
        )

    expected_lists = {
        "planned_solver_options": {"liblinear", "saga"},
        "planned_regularization": {"l1", "l2", "elasticnet"},
        "planned_class_weight": {"balanced", "none"},
        "required_inputs": set(REQUIRED_INPUTS),
    }
    for field, expected in expected_lists.items():
        value = config.get(field)
        if not isinstance(value, list) or set(value) != expected:
            raise LogisticRegressionScaffoldError(f"{field} is invalid")

    outputs = config.get("required_outputs_later")
    if not isinstance(outputs, list) or len(outputs) != 3:
        raise LogisticRegressionScaffoldError(
            "required_outputs_later must contain three planned outputs"
        )


def _missing(value: Any) -> bool:
    return value is None or str(value).strip() == ""


def validate_required_inputs_manifest(manifest: Mapping[str, Any]) -> None:
    """Validate mock input-manifest metadata without opening any referenced file."""
    if not isinstance(manifest, Mapping):
        raise LogisticRegressionScaffoldError("input manifest must be a mapping")

    missing = [field for field in REQUIRED_INPUTS if _missing(manifest.get(field))]
    if missing:
        raise LogisticRegressionScaffoldError(
            "input manifest missing required inputs: " + ", ".join(missing)
        )

    feature_type = str(manifest.get("input_feature_type", "")).strip()
    if feature_type != INPUT_FEATURE_TYPE:
        raise LogisticRegressionScaffoldError(
            "input_feature_type must be patient_level_pseudobulk"
        )
    if str(manifest.get("split_policy", "")).strip() != SPLIT_POLICY:
        raise LogisticRegressionScaffoldError(
            "split_policy must be patient_or_cohort_only"
        )
    if not str(manifest.get("audit_status", "")).strip():
        raise LogisticRegressionScaffoldError("input manifest requires audit_status")


def refuse_training_if_disabled(config: Mapping[str, Any]) -> None:
    """Refuse both training and prediction under the scaffold safety flags."""
    if config.get("allow_training") is not True:
        raise LogisticRegressionScaffoldError(
            "training is disabled for the logistic regression scaffold"
        )
    if config.get("allow_prediction") is not True:
        raise LogisticRegressionScaffoldError(
            "prediction is disabled for the logistic regression scaffold"
        )
    if config.get("allow_model_artifacts") is not True:
        raise LogisticRegressionScaffoldError(
            "model artifacts are disabled for the logistic regression scaffold"
        )


def validate_results_table_headers(columns: Sequence[str]) -> None:
    """Require the exact header-only results-table contract."""
    if list(columns) != RESULTS_TABLE_HEADERS:
        raise LogisticRegressionScaffoldError(
            "logistic regression results headers are invalid"
        )
