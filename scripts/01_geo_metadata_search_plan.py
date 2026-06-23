"""Safe GEO / NCBI metadata audit scaffold.

This script validates local planning files and creates a header-only GEO
candidate table when needed. It does not query NCBI, download data, or invent
candidate datasets.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, List, Sequence


REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPO_ROOT / "configs" / "data_audit.yaml"
SCHEMA_PATH = REPO_ROOT / "metadata" / "geo_candidate_schema.yaml"
CANDIDATE_TABLE_PATH = REPO_ROOT / "reports" / "tables" / "geo_candidate_datasets.csv"

GEO_SECTION = "geo_ncbi"
REQUIRED_GEO_CONFIG_KEYS = [
    "search_terms",
    "metadata_only",
    "allow_full_download",
    "required_manual_verification",
]
REQUIRED_MANUAL_VERIFICATION = [
    "organism",
    "assay_type",
    "tissue",
    "disease_label",
    "patient_id_availability",
    "activity_label_availability",
    "treatment_metadata",
    "batch_or_cohort",
    "raw_data_availability",
    "processed_object_availability",
]
REQUIRED_SCHEMA_FIELDS = [
    "accession",
    "title",
    "source",
    "publication",
    "organism",
    "tissue",
    "assay_type",
    "disease_context",
    "lupus_subtype",
    "n_patients",
    "n_samples",
    "n_cells",
    "patient_id_available",
    "disease_label_available",
    "activity_label_available",
    "treatment_info_available",
    "batch_info_available",
    "raw_data_available",
    "processed_object_available",
    "notes",
    "audit_status",
]
ALLOWED_AUDIT_STATUSES = [
    "candidate_pending_audit",
    "manual_metadata_verified",
    "rejected_metadata_only",
]


class GeoPlanError(ValueError):
    """Raised when local GEO metadata audit planning files are invalid."""


def _clean_scalar(value: str) -> str | bool:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    if value == "true":
        return True
    if value == "false":
        return False
    return value


def load_simple_yaml(path: Path) -> Dict[str, object]:
    """Load the limited YAML shape used by this repository's config files."""
    root: Dict[str, object] = {}
    current_top: str | None = None
    current_nested: str | None = None

    for line_number, raw_line in enumerate(path.read_text().splitlines(), start=1):
        line = raw_line.split("#", 1)[0].rstrip()
        if not line.strip():
            continue

        if not raw_line.startswith(" ") and line.endswith(":"):
            current_top = line[:-1].strip()
            current_nested = None
            root[current_top] = []
            continue

        if current_top is None:
            raise GeoPlanError(f"Value without section at line {line_number}")

        if line.startswith("  - "):
            section = root.setdefault(current_top, [])
            if not isinstance(section, list):
                raise GeoPlanError(f"Mixed list and mapping at line {line_number}")
            section.append(_clean_scalar(line[4:]))
            continue

        if line.startswith("  ") and not line.startswith("    "):
            section = root.setdefault(current_top, {})
            if not isinstance(section, dict):
                section = {}
                root[current_top] = section
            nested_line = line[2:]
            if nested_line.endswith(":"):
                current_nested = nested_line[:-1].strip()
                section[current_nested] = []
                continue
            if ":" in nested_line:
                key, value = nested_line.split(":", 1)
                current_nested = None
                section[key.strip()] = _clean_scalar(value)
                continue

        if line.startswith("    - "):
            section = root.get(current_top)
            if not isinstance(section, dict) or current_nested is None:
                raise GeoPlanError(f"Nested list item without section at line {line_number}")
            nested_values = section.setdefault(current_nested, [])
            if not isinstance(nested_values, list):
                raise GeoPlanError(f"Mixed nested values at line {line_number}")
            nested_values.append(_clean_scalar(line[6:]))
            continue

        raise GeoPlanError(f"Unsupported YAML shape at line {line_number}: {raw_line}")

    return root


def load_geo_config(config_path: Path = CONFIG_PATH) -> Dict[str, object]:
    config = load_simple_yaml(config_path)
    section = config.get(GEO_SECTION)
    if not isinstance(section, dict):
        raise GeoPlanError("Missing geo_ncbi config section")

    missing_keys = [key for key in REQUIRED_GEO_CONFIG_KEYS if key not in section]
    if missing_keys:
        raise GeoPlanError(f"Missing GEO config keys: {', '.join(missing_keys)}")

    if section["metadata_only"] is not True:
        raise GeoPlanError("geo_ncbi.metadata_only must be true")
    if section["allow_full_download"] is not False:
        raise GeoPlanError("geo_ncbi.allow_full_download must be false")

    search_terms = section["search_terms"]
    if not isinstance(search_terms, list) or not search_terms:
        raise GeoPlanError("geo_ncbi.search_terms must be a non-empty list")

    required_manual = section["required_manual_verification"]
    if not isinstance(required_manual, list):
        raise GeoPlanError("geo_ncbi.required_manual_verification must be a list")
    missing_manual = [
        field for field in REQUIRED_MANUAL_VERIFICATION if field not in required_manual
    ]
    if missing_manual:
        raise GeoPlanError(
            f"Missing manual verification fields: {', '.join(missing_manual)}"
        )

    return section


def load_candidate_schema(schema_path: Path = SCHEMA_PATH) -> Dict[str, List[str]]:
    schema = load_simple_yaml(schema_path)
    required_fields = schema.get("required_fields")
    allowed_statuses = schema.get("allowed_audit_statuses")
    if not isinstance(required_fields, list):
        raise GeoPlanError("geo_candidate_schema.yaml missing required_fields list")
    if not isinstance(allowed_statuses, list):
        raise GeoPlanError("geo_candidate_schema.yaml missing allowed_audit_statuses list")

    missing_fields = [field for field in REQUIRED_SCHEMA_FIELDS if field not in required_fields]
    if missing_fields:
        raise GeoPlanError(f"Missing candidate schema fields: {', '.join(missing_fields)}")

    missing_statuses = [
        status for status in ALLOWED_AUDIT_STATUSES if status not in allowed_statuses
    ]
    if missing_statuses:
        raise GeoPlanError(f"Missing audit statuses: {', '.join(missing_statuses)}")

    return {
        "required_fields": [str(field) for field in required_fields],
        "allowed_audit_statuses": [str(status) for status in allowed_statuses],
    }


def ensure_candidate_table(
    table_path: Path = CANDIDATE_TABLE_PATH,
    required_fields: Sequence[str] = REQUIRED_SCHEMA_FIELDS,
) -> Path:
    table_path.parent.mkdir(parents=True, exist_ok=True)
    if not table_path.exists():
        with table_path.open("w", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(required_fields)
    return table_path


def read_candidate_table(table_path: Path) -> tuple[List[str], List[Dict[str, str]]]:
    with table_path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise GeoPlanError("GEO candidate table is missing a header")
        return list(reader.fieldnames), list(reader)


def validate_candidate_rows(
    rows: Sequence[Dict[str, str]], allowed_statuses: Sequence[str]
) -> None:
    for index, row in enumerate(rows, start=2):
        accession = row.get("accession", "").strip()
        audit_status = row.get("audit_status", "").strip()
        if not accession:
            raise GeoPlanError(f"Candidate row {index} missing explicit accession")
        if not audit_status:
            raise GeoPlanError(f"Candidate row {index} missing audit_status")
        if audit_status not in allowed_statuses:
            raise GeoPlanError(f"Candidate row {index} has invalid audit_status")


def validate_candidate_table(
    table_path: Path,
    required_fields: Sequence[str],
    allowed_statuses: Sequence[str],
) -> None:
    header, rows = read_candidate_table(table_path)
    if header != list(required_fields):
        raise GeoPlanError("GEO candidate table header does not match schema")
    validate_candidate_rows(rows, allowed_statuses)


def run_plan(
    config_path: Path = CONFIG_PATH,
    schema_path: Path = SCHEMA_PATH,
    table_path: Path = CANDIDATE_TABLE_PATH,
) -> Path:
    load_geo_config(config_path)
    schema = load_candidate_schema(schema_path)
    ensure_candidate_table(table_path, schema["required_fields"])
    validate_candidate_table(
        table_path,
        schema["required_fields"],
        schema["allowed_audit_statuses"],
    )
    return table_path


def main() -> int:
    output_path = run_plan()
    print(f"Validated {output_path.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
