"""Validate the restricted Phase 3 baseline modeling scaffold.

This module reads local configuration only. It does not load data, generate
features, fit models, compute metrics, or create model artifacts.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Mapping


REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPO_ROOT / "configs" / "baseline_modeling.yaml"
APPROVED_TASK = "SLE diagnosis / case-control prediction"
EXPECTED_BASELINE_FAMILIES = {
    "pseudobulk_logistic_regression",
    "pseudobulk_random_forest",
    "pseudobulk_xgboost",
    "hvg_linear_classifier",
    "cell_type_proportion_baseline",
    "deepsets",
}
EXPECTED_BLOCKED_TASKS = {
    "disease_activity_prediction",
    "flare_prediction",
    "lupus_nephritis_prediction",
}


class BaselineScaffoldError(ValueError):
    """Raised when the baseline scaffold violates restricted Phase 3 scope."""


def load_baseline_config(path: Path | str = CONFIG_PATH) -> Dict[str, Any]:
    config_path = Path(path)
    try:
        config = json.loads(config_path.read_text())
    except json.JSONDecodeError as exc:
        raise BaselineScaffoldError(
            f"{config_path} must use JSON-compatible YAML syntax"
        ) from exc
    if not isinstance(config, dict):
        raise BaselineScaffoldError("baseline config must be a mapping")
    return config


def validate_baseline_config(config: Mapping[str, Any]) -> Dict[str, Any]:
    if config.get("phase") != 3:
        raise BaselineScaffoldError("phase must be 3")
    if config.get("approved_task") != APPROVED_TASK:
        raise BaselineScaffoldError("approved_task is outside Human Gate 2 scope")

    required_false = [
        "allow_training",
        "allow_deep_learning",
        "allow_foundation_models",
        "allow_uncertainty_methods",
    ]
    for field in required_false:
        if config.get(field) is not False:
            raise BaselineScaffoldError(f"{field} must be false")

    if config.get("split_policy") != "patient_or_cohort_only":
        raise BaselineScaffoldError("split_policy must be patient_or_cohort_only")
    if config.get("forbid_cell_level_split") is not True:
        raise BaselineScaffoldError("forbid_cell_level_split must be true")

    families = config.get("baseline_families")
    if not isinstance(families, Mapping):
        raise BaselineScaffoldError("baseline_families must be a mapping")
    if set(families) != EXPECTED_BASELINE_FAMILIES:
        raise BaselineScaffoldError("baseline_families do not match scaffold scope")

    for family_name, family in families.items():
        if not isinstance(family, Mapping):
            raise BaselineScaffoldError(f"{family_name} must be a mapping")
        if family.get("enabled_for_training") is not False:
            raise BaselineScaffoldError(
                f"{family_name} enabled_for_training must be false"
            )

    deepsets = families["deepsets"]
    if deepsets.get("enabled_for_design") is not False:
        raise BaselineScaffoldError("deepsets design must remain disabled")

    blocked_tasks = config.get("blocked_tasks")
    if not isinstance(blocked_tasks, list):
        raise BaselineScaffoldError("blocked_tasks must be a list")
    if set(blocked_tasks) != EXPECTED_BLOCKED_TASKS:
        raise BaselineScaffoldError("blocked_tasks do not match Human Gate 2")

    return {
        "phase": 3,
        "approved_task": APPROVED_TASK,
        "allow_training": False,
        "allow_deep_learning": False,
        "allow_foundation_models": False,
        "allow_uncertainty_methods": False,
        "split_policy": "patient_or_cohort_only",
        "forbid_cell_level_split": True,
        "design_family_count": sum(
            family.get("enabled_for_design") is True for family in families.values()
        ),
        "training_family_count": 0,
    }


def run_validation(config_path: Path | str = CONFIG_PATH) -> Dict[str, Any]:
    return validate_baseline_config(load_baseline_config(config_path))


def main() -> int:
    summary = run_validation()
    print("Baseline modeling scaffold validation passed")
    for key, value in summary.items():
        print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
