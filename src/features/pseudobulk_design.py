"""Pseudobulk design validation for local config, schema, and mock rows.

These utilities do not load datasets, create expression matrices, aggregate
cells, fit classifiers, or write model artifacts.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Mapping, Sequence


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = REPO_ROOT / "configs" / "pseudobulk.yaml"

APPROVED_TASK = "SLE diagnosis / case-control prediction"
ALLOWED_AGGREGATION_UNITS = {"patient_id", "donor_id", "sample_id"}
FORBIDDEN_AGGREGATION_UNITS = {"cell_id", "barcode"}
ALLOWED_AGGREGATIONS = {"sum_counts", "mean_expression", "fraction_expressing"}
REQUIRED_SCHEMA_FIELDS = [
    "feature_id",
    "dataset_id",
    "aggregation_unit",
    "aggregation_id",
    "cell_type",
    "gene_id",
    "gene_symbol",
    "aggregation_method",
    "value_type",
    "normalization_status",
    "split_group",
    "audit_status",
]
MANIFEST_HEADERS = REQUIRED_SCHEMA_FIELDS + ["notes"]
REQUIRED_FIELD_SPEC_KEYS = ["description", "required", "allowed_missing", "notes"]


class PseudobulkDesignError(ValueError):
    """Raised when pseudobulk design safety or schema validation fails."""


def _load_json_compatible_yaml(path: Path | str, label: str) -> Dict[str, Any]:
    source_path = Path(path)
    try:
        value = json.loads(source_path.read_text())
    except json.JSONDecodeError as exc:
        raise PseudobulkDesignError(
            f"{source_path} must use JSON-compatible YAML syntax"
        ) from exc
    if not isinstance(value, dict):
        raise PseudobulkDesignError(f"{label} must be a mapping")
    return value


def load_pseudobulk_config(
    path: Path | str = DEFAULT_CONFIG_PATH,
) -> Dict[str, Any]:
    """Load and validate the local pseudobulk design config."""
    config = _load_json_compatible_yaml(path, "pseudobulk config")
    validate_pseudobulk_config(config)
    return config


def validate_pseudobulk_config(config: Mapping[str, Any]) -> None:
    """Validate that pseudobulk execution and training remain disabled."""
    if config.get("task") != APPROVED_TASK:
        raise PseudobulkDesignError("task is outside restricted Human Gate 2 scope")
    if config.get("allow_real_extraction") is not False:
        raise PseudobulkDesignError("allow_real_extraction must be false")
    if config.get("allow_training") is not False:
        raise PseudobulkDesignError("allow_training must be false")

    aggregation_units = config.get("aggregation_units")
    if not isinstance(aggregation_units, list):
        raise PseudobulkDesignError("aggregation_units must be a list")
    if set(aggregation_units) != ALLOWED_AGGREGATION_UNITS:
        raise PseudobulkDesignError(
            "aggregation_units must be patient_id, donor_id, and sample_id"
        )

    forbidden_units = config.get("forbidden_aggregation_units")
    if not isinstance(forbidden_units, list):
        raise PseudobulkDesignError("forbidden_aggregation_units must be a list")
    if set(forbidden_units) != FORBIDDEN_AGGREGATION_UNITS:
        raise PseudobulkDesignError(
            "forbidden_aggregation_units must be cell_id and barcode"
        )

    aggregations = config.get("allowed_aggregations")
    if not isinstance(aggregations, list):
        raise PseudobulkDesignError("allowed_aggregations must be a list")
    if set(aggregations) != ALLOWED_AGGREGATIONS:
        raise PseudobulkDesignError("allowed_aggregations are incomplete")

    required_true = [
        "cell_type_stratified",
        "require_patient_level_split",
        "require_no_cell_level_leakage",
        "require_feature_manifest",
    ]
    for field in required_true:
        if config.get(field) is not True:
            raise PseudobulkDesignError(f"{field} must be true")

    for field in ["normalization_policy", "gene_filtering_policy"]:
        if config.get(field) != "TODO":
            raise PseudobulkDesignError(f"{field} must remain TODO")


def validate_pseudobulk_feature_schema(schema: Mapping[str, Any]) -> None:
    """Validate the static pseudobulk feature schema."""
    if schema.get("required_fields") != REQUIRED_SCHEMA_FIELDS:
        raise PseudobulkDesignError("pseudobulk schema required_fields are invalid")
    fields = schema.get("fields")
    if not isinstance(fields, Mapping):
        raise PseudobulkDesignError("pseudobulk schema fields must be a mapping")

    missing_specs = [field for field in REQUIRED_SCHEMA_FIELDS if field not in fields]
    if missing_specs:
        raise PseudobulkDesignError(
            "pseudobulk schema missing field specs: " + ", ".join(missing_specs)
        )
    for field_name in REQUIRED_SCHEMA_FIELDS:
        field_spec = fields[field_name]
        if not isinstance(field_spec, Mapping):
            raise PseudobulkDesignError(f"{field_name} field spec must be a mapping")
        missing_keys = [
            key for key in REQUIRED_FIELD_SPEC_KEYS if key not in field_spec
        ]
        if missing_keys:
            raise PseudobulkDesignError(
                f"{field_name} missing schema keys: " + ", ".join(missing_keys)
            )


def validate_pseudobulk_manifest_headers(columns: Sequence[str]) -> None:
    """Require the exact header-only pseudobulk feature manifest contract."""
    if list(columns) != MANIFEST_HEADERS:
        raise PseudobulkDesignError("pseudobulk feature manifest headers are invalid")


def reject_cell_level_aggregation(aggregation_unit: Any) -> None:
    """Reject cell/barcode aggregation and unknown biological replicate units."""
    normalized = str(aggregation_unit).strip()
    if normalized in FORBIDDEN_AGGREGATION_UNITS:
        raise PseudobulkDesignError(
            f"cell-level aggregation unit is forbidden: {normalized}"
        )
    if normalized not in ALLOWED_AGGREGATION_UNITS:
        raise PseudobulkDesignError(
            f"aggregation_unit must be patient_id, donor_id, or sample_id: {normalized}"
        )


def _missing(value: Any) -> bool:
    return value is None or str(value).strip() == ""


def validate_mock_pseudobulk_rows(rows: Sequence[Mapping[str, Any]]) -> None:
    """Validate caller-provided mock manifest rows without extracting features."""
    for index, row in enumerate(rows, start=1):
        if not isinstance(row, Mapping):
            raise PseudobulkDesignError(f"row {index} must be a mapping")
        missing_fields = [field for field in REQUIRED_SCHEMA_FIELDS if field not in row]
        if missing_fields:
            raise PseudobulkDesignError(
                f"row {index} missing fields: " + ", ".join(missing_fields)
            )

        reject_cell_level_aggregation(row.get("aggregation_unit"))
        if row.get("aggregation_method") not in ALLOWED_AGGREGATIONS:
            raise PseudobulkDesignError(
                f"row {index} has invalid aggregation_method"
            )

        required_values = [
            "feature_id",
            "dataset_id",
            "aggregation_id",
            "aggregation_method",
            "value_type",
            "normalization_status",
            "split_group",
            "audit_status",
        ]
        missing_values = [field for field in required_values if _missing(row.get(field))]
        if missing_values:
            raise PseudobulkDesignError(
                f"row {index} missing required values: " + ", ".join(missing_values)
            )

        if str(row.get("split_group")).strip().lower() in {
            "cell",
            "cell_id",
            "cell_level",
            "barcode",
        }:
            raise PseudobulkDesignError(f"row {index} uses a cell-level split_group")
