"""Cell-type proportion baseline design and mock-row validation.

These utilities validate local configuration, table headers, and caller-
provided mock rows. They do not load cells, compute proportions, fit models,
generate predictions, or create artifacts.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Mapping, Sequence


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = (
    REPO_ROOT / "configs" / "cell_type_proportion_baseline.yaml"
)

APPROVED_TASK = "SLE diagnosis / case-control prediction"
INPUT_FEATURE_TYPE = "patient_level_cell_type_proportions"
SPLIT_POLICY = "patient_or_cohort_only"
ALLOWED_AGGREGATION_UNITS = {"patient_id", "donor_id", "sample_id"}
FORBIDDEN_AGGREGATION_UNITS = {"cell_id", "barcode"}
PLANNED_FEATURES = {
    "cell_type_fraction",
    "cell_type_count",
    "logit_transformed_fraction_later",
    "centered_log_ratio_later",
}
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


class CellTypeProportionScaffoldError(ValueError):
    """Raised when composition scaffold validation fails."""


def load_cell_type_proportion_config(
    path: Path | str = DEFAULT_CONFIG_PATH,
) -> Dict[str, Any]:
    """Load and validate JSON-compatible YAML without data dependencies."""
    config_path = Path(path)
    try:
        config = json.loads(config_path.read_text())
    except json.JSONDecodeError as exc:
        raise CellTypeProportionScaffoldError(
            f"{config_path} must use JSON-compatible YAML syntax"
        ) from exc
    if not isinstance(config, dict):
        raise CellTypeProportionScaffoldError("config must be a mapping")
    validate_cell_type_proportion_config(config)
    return config


def validate_cell_type_proportion_config(config: Mapping[str, Any]) -> None:
    """Validate that feature extraction and modeling remain disabled."""
    expected_scalars = {
        "task": APPROVED_TASK,
        "input_feature_type": INPUT_FEATURE_TYPE,
        "split_policy": SPLIT_POLICY,
    }
    for field, expected in expected_scalars.items():
        if config.get(field) != expected:
            raise CellTypeProportionScaffoldError(f"{field} must be {expected}")

    required_false = [
        "allow_feature_extraction",
        "allow_training",
        "allow_prediction",
        "allow_model_artifacts",
    ]
    for field in required_false:
        if config.get(field) is not False:
            raise CellTypeProportionScaffoldError(f"{field} must be false")

    required_true = [
        "forbid_cell_level_features",
        "require_cell_type_labels",
        "require_patient_or_donor_id",
        "require_feature_manifest",
    ]
    for field in required_true:
        if config.get(field) is not True:
            raise CellTypeProportionScaffoldError(f"{field} must be true")

    aggregation_units = config.get("aggregation_units")
    if not isinstance(aggregation_units, list) or set(
        aggregation_units
    ) != ALLOWED_AGGREGATION_UNITS:
        raise CellTypeProportionScaffoldError(
            "aggregation_units must be patient_id, donor_id, and sample_id"
        )

    forbidden_units = config.get("forbidden_aggregation_units")
    if not isinstance(forbidden_units, list) or set(
        forbidden_units
    ) != FORBIDDEN_AGGREGATION_UNITS:
        raise CellTypeProportionScaffoldError(
            "forbidden_aggregation_units must be cell_id and barcode"
        )

    features = config.get("planned_features")
    if not isinstance(features, list) or set(features) != PLANNED_FEATURES:
        raise CellTypeProportionScaffoldError("planned_features are invalid")

    outputs = config.get("required_outputs_later")
    if not isinstance(outputs, list) or set(outputs) != {
        "reports/tables/cell_type_proportion_features.csv",
        "reports/tables/cell_type_proportion_results.csv",
    }:
        raise CellTypeProportionScaffoldError(
            "required_outputs_later are invalid"
        )


def validate_cell_type_feature_headers(columns: Sequence[str]) -> None:
    """Require the exact header-only cell-type feature contract."""
    if list(columns) != FEATURE_HEADERS:
        raise CellTypeProportionScaffoldError(
            "cell-type proportion feature headers are invalid"
        )


def validate_cell_type_result_headers(columns: Sequence[str]) -> None:
    """Require the exact header-only cell-type result contract."""
    if list(columns) != RESULT_HEADERS:
        raise CellTypeProportionScaffoldError(
            "cell-type proportion result headers are invalid"
        )


def reject_cell_level_aggregation(aggregation_unit: Any) -> None:
    """Reject cell/barcode and unsupported biological aggregation units."""
    normalized = str(aggregation_unit).strip()
    if normalized in FORBIDDEN_AGGREGATION_UNITS:
        raise CellTypeProportionScaffoldError(
            f"cell-level aggregation unit is forbidden: {normalized}"
        )
    if normalized not in ALLOWED_AGGREGATION_UNITS:
        raise CellTypeProportionScaffoldError(
            "aggregation_unit must be patient_id, donor_id, or sample_id"
        )


def _missing(value: Any) -> bool:
    return value is None or str(value).strip() == ""


def _as_number(value: Any, field: str, row_index: int) -> float:
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise CellTypeProportionScaffoldError(
            f"row {row_index} {field} must be numeric"
        ) from exc


def validate_mock_cell_type_feature_rows(
    rows: Sequence[Mapping[str, Any]],
) -> None:
    """Validate mock feature rows without computing any composition values."""
    required_values = [
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
    ]

    for index, row in enumerate(rows, start=1):
        if not isinstance(row, Mapping):
            raise CellTypeProportionScaffoldError(f"row {index} must be a mapping")

        missing_fields = [field for field in FEATURE_HEADERS if field not in row]
        if missing_fields:
            raise CellTypeProportionScaffoldError(
                f"row {index} missing fields: " + ", ".join(missing_fields)
            )
        missing_values = [field for field in required_values if _missing(row.get(field))]
        if missing_values:
            raise CellTypeProportionScaffoldError(
                f"row {index} missing required values: "
                + ", ".join(missing_values)
            )

        reject_cell_level_aggregation(row.get("aggregation_unit"))

        cell_count = _as_number(row.get("cell_count"), "cell_count", index)
        total_cells = _as_number(row.get("total_cells"), "total_cells", index)
        fraction = _as_number(
            row.get("cell_type_fraction"), "cell_type_fraction", index
        )

        if total_cells <= 0:
            raise CellTypeProportionScaffoldError(
                f"row {index} total_cells must be greater than zero"
            )
        if cell_count < 0 or cell_count > total_cells:
            raise CellTypeProportionScaffoldError(
                f"row {index} cell_count must be between zero and total_cells"
            )
        if fraction < 0 or fraction > 1:
            raise CellTypeProportionScaffoldError(
                f"row {index} cell_type_fraction must be between zero and one"
            )

        if str(row.get("split_group")).strip().lower() in {
            "cell",
            "cell_id",
            "cell_level",
            "barcode",
        }:
            raise CellTypeProportionScaffoldError(
                f"row {index} uses a cell-level split_group"
            )
