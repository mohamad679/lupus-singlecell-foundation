"""Restricted random forest and XGBoost baseline scaffolds.

This module validates local configuration and table headers only. It does not
load features, import estimator libraries, fit models, generate predictions,
compute importance, or create model artifacts.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Mapping, Sequence


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = REPO_ROOT / "configs" / "tree_baseline.yaml"

APPROVED_TASK = "SLE diagnosis / case-control prediction"
INPUT_FEATURE_TYPE = "patient_level_pseudobulk"
SPLIT_POLICY = "patient_or_cohort_only"
MODEL_FAMILIES = {"random_forest", "xgboost"}
PLANNED_METRICS = {
    "auroc",
    "auprc",
    "balanced_accuracy",
    "f1",
    "sensitivity",
    "specificity",
    "brier_score",
    "ece",
}
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


class TreeBaselineScaffoldError(ValueError):
    """Raised when tree-baseline configuration violates restricted scope."""


def load_tree_baseline_config(
    path: Path | str = DEFAULT_CONFIG_PATH,
) -> Dict[str, Any]:
    """Load and validate JSON-compatible YAML without optional dependencies."""
    config_path = Path(path)
    try:
        config = json.loads(config_path.read_text())
    except json.JSONDecodeError as exc:
        raise TreeBaselineScaffoldError(
            f"{config_path} must use JSON-compatible YAML syntax"
        ) from exc
    if not isinstance(config, dict):
        raise TreeBaselineScaffoldError("tree baseline config must be a mapping")
    validate_tree_baseline_config(config)
    return config


def validate_tree_baseline_config(config: Mapping[str, Any]) -> None:
    """Validate design metadata while keeping all execution disabled."""
    expected_scalars = {
        "task": APPROVED_TASK,
        "input_feature_type": INPUT_FEATURE_TYPE,
        "split_policy": SPLIT_POLICY,
    }
    for field, expected in expected_scalars.items():
        if config.get(field) != expected:
            raise TreeBaselineScaffoldError(f"{field} must be {expected}")

    for field in ["allow_training", "allow_prediction", "allow_model_artifacts"]:
        if config.get(field) is not False:
            raise TreeBaselineScaffoldError(f"{field} must be false")
    if config.get("forbid_cell_level_features") is not True:
        raise TreeBaselineScaffoldError(
            "forbid_cell_level_features must be true"
        )

    families = config.get("model_families")
    if not isinstance(families, Mapping) or set(families) != MODEL_FAMILIES:
        raise TreeBaselineScaffoldError(
            "model_families must contain random_forest and xgboost"
        )
    for family_name, family in families.items():
        if not isinstance(family, Mapping):
            raise TreeBaselineScaffoldError(f"{family_name} must be a mapping")
        if family.get("enabled_for_design") is not True:
            raise TreeBaselineScaffoldError(
                f"{family_name} enabled_for_design must be true"
            )
        if family.get("enabled_for_training") is not False:
            raise TreeBaselineScaffoldError(
                f"{family_name} enabled_for_training must be false"
            )

    metrics = config.get("planned_metrics")
    if not isinstance(metrics, list) or set(metrics) != PLANNED_METRICS:
        raise TreeBaselineScaffoldError("planned_metrics are invalid")

    outputs = config.get("required_outputs_later")
    if not isinstance(outputs, list) or set(outputs) != {
        "metadata/table_schemas/tree_baseline_results.csv",
        "metadata/table_schemas/tree_feature_importance.csv",
    }:
        raise TreeBaselineScaffoldError("required_outputs_later are invalid")

    validate_no_required_xgboost_dependency(config)


def refuse_training_if_disabled(config: Mapping[str, Any]) -> None:
    """Refuse training, prediction, and artifact creation in scaffold mode."""
    if config.get("allow_training") is not True:
        raise TreeBaselineScaffoldError(
            "training is disabled for tree baseline scaffolds"
        )
    if config.get("allow_prediction") is not True:
        raise TreeBaselineScaffoldError(
            "prediction is disabled for tree baseline scaffolds"
        )
    if config.get("allow_model_artifacts") is not True:
        raise TreeBaselineScaffoldError(
            "model artifacts are disabled for tree baseline scaffolds"
        )


def validate_tree_results_headers(columns: Sequence[str]) -> None:
    """Require the exact header-only tree results contract."""
    if list(columns) != RESULTS_HEADERS:
        raise TreeBaselineScaffoldError("tree baseline results headers are invalid")


def validate_tree_importance_headers(columns: Sequence[str]) -> None:
    """Require the exact header-only feature-importance contract."""
    if list(columns) != IMPORTANCE_HEADERS:
        raise TreeBaselineScaffoldError("tree feature importance headers are invalid")


def validate_no_required_xgboost_dependency(config: Mapping[str, Any]) -> None:
    """Require XGBoost to remain optional and disabled for training."""
    families = config.get("model_families")
    if not isinstance(families, Mapping):
        raise TreeBaselineScaffoldError("model_families must be a mapping")
    xgb = families.get("xgboost")
    if not isinstance(xgb, Mapping):
        raise TreeBaselineScaffoldError("xgboost design metadata is required")
    if xgb.get("optional_dependency") is not True:
        raise TreeBaselineScaffoldError(
            "xgboost must remain an optional dependency"
        )
    if xgb.get("enabled_for_training") is not False:
        raise TreeBaselineScaffoldError("xgboost training must remain disabled")
