"""QC policy scaffold utilities.

These helpers validate local QC policy configuration and mock report rows.
They do not load real datasets, create AnnData outputs, preprocess cells,
remove cells, infer thresholds, download data, or perform modeling.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Sequence


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = REPO_ROOT / "configs" / "qc.yaml"

REQUIRED_QC_POLICY = {
    "allow_real_filtering": False,
    "require_qc_report": True,
    "require_before_after_counts": True,
    "require_sample_level_summary": True,
    "require_patient_level_summary": True,
    "forbid_unlogged_cell_removal": True,
    "forbid_threshold_guessing": True,
}
REQUIRED_CELL_LEVEL_METRICS = [
    "n_genes_by_counts",
    "total_counts",
    "pct_counts_mt",
    "pct_counts_ribo",
    "doublet_score",
    "cell_type",
    "batch_id",
    "sample_id",
    "patient_id",
]
REQUIRED_SAMPLE_LEVEL_METRICS = [
    "n_cells",
    "median_genes_per_cell",
    "median_counts_per_cell",
    "median_pct_mt",
    "doublet_rate",
    "disease_label_distribution",
]
REQUIRED_PATIENT_LEVEL_METRICS = [
    "n_samples",
    "n_cells_total",
    "disease_label",
    "treatment_status",
    "batch_distribution",
]
REQUIRED_OUTPUTS = [
    "metadata/table_schemas/qc_summary.csv",
    "metadata/table_schemas/qc_threshold_decisions.csv",
]
QC_SUMMARY_HEADERS = [
    "dataset_id",
    "sample_id",
    "patient_id",
    "n_cells",
    "median_genes_per_cell",
    "median_counts_per_cell",
    "median_pct_mt",
    "doublet_rate",
    "disease_label",
    "batch_id",
    "qc_status",
    "notes",
    "audit_status",
]
QC_THRESHOLD_HEADERS = [
    "dataset_id",
    "metric",
    "threshold_value",
    "threshold_direction",
    "threshold_source",
    "rationale",
    "applied",
    "approved_by",
    "notes",
    "audit_status",
]


class QCPolicyError(ValueError):
    """Raised when QC scaffold policy validation fails."""


def _parse_scalar(value: str) -> object:
    normalized = value.strip()
    if normalized == "true":
        return True
    if normalized == "false":
        return False
    if normalized.isdigit():
        return int(normalized)
    return normalized


def load_qc_config(path: Path | str = DEFAULT_CONFIG_PATH) -> Dict[str, object]:
    """Parse the small local YAML shape used by configs/qc.yaml."""
    config_path = Path(path)
    data: Dict[str, object] = {}
    current_key: str | None = None

    for line_number, raw_line in enumerate(config_path.read_text().splitlines(), start=1):
        line = raw_line.split("#", 1)[0].rstrip()
        if not line.strip():
            continue

        if not raw_line.startswith(" ") and ":" in line:
            key, value = line.split(":", 1)
            current_key = key.strip()
            value = value.strip()
            data[current_key] = _parse_scalar(value) if value else None
            continue

        if current_key is None:
            raise QCPolicyError(f"Nested value without section at line {line_number}")

        if line.startswith("  - "):
            section = data.get(current_key)
            if section is None:
                section = []
                data[current_key] = section
            if not isinstance(section, list):
                raise QCPolicyError(
                    f"List item under non-list section {current_key} at line {line_number}"
                )
            section.append(_parse_scalar(line[4:]))
            continue

        if raw_line.startswith("  ") and ":" in line:
            section = data.get(current_key)
            if section is None:
                section = {}
                data[current_key] = section
            if not isinstance(section, dict):
                raise QCPolicyError(
                    f"Mapping item under non-mapping section {current_key} at line {line_number}"
                )
            key, value = line.strip().split(":", 1)
            section[key.strip()] = _parse_scalar(value.strip())
            continue

        raise QCPolicyError(f"Unsupported QC config YAML shape at line {line_number}")

    return data


def _require_list_values(
    config: Mapping[str, object],
    key: str,
    expected_values: Iterable[str],
) -> None:
    values = config.get(key)
    if not isinstance(values, list):
        raise QCPolicyError(f"{key} must be a list")
    missing = [value for value in expected_values if value not in values]
    if missing:
        raise QCPolicyError(f"{key} missing required values: " + ", ".join(missing))


def validate_qc_config(config: Mapping[str, object]) -> None:
    """Validate the QC policy config blocks real filtering and guessed thresholds."""
    qc_policy = config.get("qc_policy")
    if not isinstance(qc_policy, Mapping):
        raise QCPolicyError("qc_policy must be a mapping")

    for key, expected_value in REQUIRED_QC_POLICY.items():
        if qc_policy.get(key) is not expected_value:
            raise QCPolicyError(f"qc_policy.{key} must be {str(expected_value).lower()}")

    if qc_policy.get("threshold_source") == "guessed":
        raise QCPolicyError("qc_policy.threshold_source must not be guessed")

    _require_list_values(config, "cell_level_metrics", REQUIRED_CELL_LEVEL_METRICS)
    _require_list_values(config, "sample_level_metrics", REQUIRED_SAMPLE_LEVEL_METRICS)
    _require_list_values(config, "patient_level_metrics", REQUIRED_PATIENT_LEVEL_METRICS)
    _require_list_values(config, "required_outputs", REQUIRED_OUTPUTS)


def validate_qc_summary_headers(columns: Sequence[str]) -> None:
    """Validate QC summary columns for mock/header-only report tables."""
    missing = [header for header in QC_SUMMARY_HEADERS if header not in columns]
    if missing:
        raise QCPolicyError("qc_summary missing required headers: " + ", ".join(missing))


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "yes", "1"}


def validate_threshold_decision_rows(rows: Sequence[Mapping[str, Any]]) -> None:
    """Validate mock threshold-decision rows without applying thresholds."""
    for index, row in enumerate(rows, start=1):
        missing = [header for header in QC_THRESHOLD_HEADERS if header not in row]
        if missing:
            raise QCPolicyError(
                f"threshold decision row {index} missing headers: " + ", ".join(missing)
            )
        if not row.get("audit_status"):
            raise QCPolicyError(f"threshold decision row {index} missing audit_status")
        if str(row.get("threshold_source", "")).strip().lower() == "guessed":
            raise QCPolicyError(f"threshold decision row {index} uses guessed threshold_source")
        if _as_bool(row.get("applied")) and not str(row.get("approved_by", "")).strip():
            raise QCPolicyError(
                f"threshold decision row {index} cannot be applied without approved_by"
            )
