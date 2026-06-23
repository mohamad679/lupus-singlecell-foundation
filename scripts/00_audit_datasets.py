"""Safe Phase 1 scaffold for dataset feasibility reporting.

This script reads local planning inputs and writes a local feasibility table.
It does not search remote sources, acquire data, add candidate rows, or model.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, List, Sequence


REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPO_ROOT / "configs" / "data_audit.yaml"
CATALOG_PATH = REPO_ROOT / "metadata" / "dataset_catalog.csv"
REPORT_PATH = REPO_ROOT / "reports" / "tables" / "dataset_feasibility_table.csv"

REQUIRED_CONFIG_KEYS = [
    "search_terms",
    "sources_to_audit",
    "required_fields",
    "eligibility_scoring_fields",
    "forbidden_actions",
]

REQUIRED_FORBIDDEN_ACTIONS = [
    "invent_accessions",
    "assume_patient_ids",
    "treat_bulk_as_single_cell",
    "download_full_data_before_approval",
    "start_modeling_before_human_gate_1",
]

REPORT_EXTRA_COLUMNS = ["audit_status", "audit_notes"]


class AuditConfigError(ValueError):
    """Raised when the local audit configuration is invalid."""


def _clean_scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def load_simple_yaml(path: Path) -> Dict[str, List[str]]:
    """Load the limited top-level list YAML shape used by data_audit.yaml."""
    data: Dict[str, List[str]] = {}
    current_key: str | None = None

    for line_number, raw_line in enumerate(path.read_text().splitlines(), start=1):
        line = raw_line.split("#", 1)[0].rstrip()
        if not line.strip():
            continue

        if not raw_line.startswith(" ") and line.endswith(":"):
            current_key = line[:-1].strip()
            data[current_key] = []
            continue

        if line.startswith("  - "):
            if current_key is None:
                raise AuditConfigError(f"List item without section at line {line_number}")
            data[current_key].append(_clean_scalar(line[4:]))
            continue

        raise AuditConfigError(f"Unsupported YAML shape at line {line_number}: {raw_line}")

    return data


def load_config(config_path: Path = CONFIG_PATH) -> Dict[str, List[str]]:
    config = load_simple_yaml(config_path)
    missing_keys = [key for key in REQUIRED_CONFIG_KEYS if key not in config]
    if missing_keys:
        raise AuditConfigError(f"Missing config keys: {', '.join(missing_keys)}")

    empty_keys = [key for key in REQUIRED_CONFIG_KEYS if not config[key]]
    if empty_keys:
        raise AuditConfigError(f"Config keys must not be empty: {', '.join(empty_keys)}")

    missing_forbidden = [
        action for action in REQUIRED_FORBIDDEN_ACTIONS if action not in config["forbidden_actions"]
    ]
    if missing_forbidden:
        raise AuditConfigError(
            f"Missing forbidden actions: {', '.join(missing_forbidden)}"
        )

    return config


def read_catalog(catalog_path: Path = CATALOG_PATH) -> tuple[List[str], List[Dict[str, str]]]:
    with catalog_path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError("Dataset catalog is missing a header")
        rows = list(reader)
        return list(reader.fieldnames), rows


def validate_required_columns(header: Sequence[str], required_fields: Sequence[str]) -> None:
    missing = [field for field in required_fields if field not in header]
    if missing:
        raise ValueError(f"Dataset catalog missing required columns: {', '.join(missing)}")


def build_report_rows(
    header: Sequence[str], rows: Sequence[Dict[str, str]]
) -> List[Dict[str, str]]:
    report_rows: List[Dict[str, str]] = []
    for row in rows:
        report_row = {field: row.get(field, "") for field in header}
        report_row["audit_status"] = "pending_manual_source_audit"
        report_row["audit_notes"] = (
            "Existing catalog row copied for audit tracking; no candidate row was invented."
        )
        report_rows.append(report_row)
    return report_rows


def write_report(
    output_path: Path, header: Sequence[str], report_rows: Sequence[Dict[str, str]]
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(header) + REPORT_EXTRA_COLUMNS
    with output_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(report_rows)


def run_audit(
    config_path: Path = CONFIG_PATH,
    catalog_path: Path = CATALOG_PATH,
    output_path: Path = REPORT_PATH,
) -> Path:
    config = load_config(config_path)
    header, rows = read_catalog(catalog_path)
    validate_required_columns(header, config["required_fields"])
    report_rows = build_report_rows(header, rows)
    write_report(output_path, header, report_rows)
    return output_path


def main() -> int:
    output_path = run_audit()
    print(f"Wrote {output_path.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
