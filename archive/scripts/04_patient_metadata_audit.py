"""Safe patient-level metadata audit scaffold.

This script validates the patient metadata schema and audit table. It does not
download datasets, invent rows, infer patient IDs, split cells, or model.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, List, Sequence


REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPO_ROOT / "metadata" / "patient_metadata_schema.yaml"
AUDIT_TABLE_PATH = REPO_ROOT / "metadata" / "table_schemas" / "patient_metadata_audit.csv"

REQUIRED_FIELDS = [
    "patient_id",
    "donor_id",
    "sample_id",
    "sample_timepoint",
    "cohort_id",
    "batch_id",
    "tissue",
    "disease_label",
    "disease_activity_label",
    "treatment_status",
    "age",
    "sex",
    "cell_count",
    "cell_type_annotation_available",
    "raw_counts_available",
    "processed_object_available",
    "longitudinal_sample",
    "notes",
    "audit_status",
]

REQUIRED_FIELD_ATTRIBUTES = [
    "required_for_training",
    "required_for_external_validation",
    "required_for_activity_prediction",
    "description",
]

TODO_VALUES = {"", "TODO", "todo", "UNKNOWN", "unknown"}


class PatientMetadataAuditError(ValueError):
    """Raised when patient metadata audit inputs are invalid."""


def _clean_scalar(value: str) -> str | bool:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        value = value[1:-1]
    if value == "true":
        return True
    if value == "false":
        return False
    return value


def load_patient_schema(schema_path: Path = SCHEMA_PATH) -> Dict[str, Dict[str, object]]:
    fields: Dict[str, Dict[str, object]] = {}
    in_fields = False
    current_field: str | None = None

    for line_number, raw_line in enumerate(schema_path.read_text().splitlines(), start=1):
        line = raw_line.split("#", 1)[0].rstrip()
        if not line.strip():
            continue

        if line == "fields:":
            in_fields = True
            current_field = None
            continue

        if not in_fields:
            raise PatientMetadataAuditError(
                f"Unsupported schema content before fields at line {line_number}"
            )

        if line.startswith("  ") and not line.startswith("    ") and line.endswith(":"):
            current_field = line[2:-1].strip()
            fields[current_field] = {}
            continue

        if line.startswith("    "):
            if current_field is None:
                raise PatientMetadataAuditError(
                    f"Field attribute without field at line {line_number}"
                )
            attr_line = line[4:]
            if ":" not in attr_line:
                raise PatientMetadataAuditError(
                    f"Malformed field attribute at line {line_number}"
                )
            key, value = attr_line.split(":", 1)
            fields[current_field][key.strip()] = _clean_scalar(value)
            continue

        raise PatientMetadataAuditError(
            f"Unsupported schema shape at line {line_number}: {raw_line}"
        )

    missing_fields = [field for field in REQUIRED_FIELDS if field not in fields]
    if missing_fields:
        raise PatientMetadataAuditError(
            f"Missing patient metadata fields: {', '.join(missing_fields)}"
        )

    for field in REQUIRED_FIELDS:
        missing_attrs = [
            attr for attr in REQUIRED_FIELD_ATTRIBUTES if attr not in fields[field]
        ]
        if missing_attrs:
            raise PatientMetadataAuditError(
                f"{field} missing attributes: {', '.join(missing_attrs)}"
            )

    return fields


def ensure_audit_table(
    table_path: Path = AUDIT_TABLE_PATH,
    required_fields: Sequence[str] = REQUIRED_FIELDS,
) -> Path:
    table_path.parent.mkdir(parents=True, exist_ok=True)
    if not table_path.exists():
        with table_path.open("w", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(required_fields)
    return table_path


def read_audit_table(table_path: Path) -> tuple[List[str], List[Dict[str, str]]]:
    with table_path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise PatientMetadataAuditError("Patient metadata audit table is missing header")
        return list(reader.fieldnames), list(reader)


def _is_missing(value: str | None) -> bool:
    return value is None or value.strip() in TODO_VALUES


def validate_and_normalize_rows(rows: Sequence[Dict[str, str]]) -> List[Dict[str, str]]:
    normalized_rows: List[Dict[str, str]] = []

    for index, row in enumerate(rows, start=2):
        if _is_missing(row.get("patient_id")):
            raise PatientMetadataAuditError(f"Row {index} missing patient_id")
        if _is_missing(row.get("audit_status")):
            raise PatientMetadataAuditError(f"Row {index} missing audit_status")

        normalized_rows.append(
            {
                field: row.get(field, "").strip() if not _is_missing(row.get(field)) else "TODO"
                for field in REQUIRED_FIELDS
            }
        )

    return normalized_rows


def write_audit_table(table_path: Path, rows: Sequence[Dict[str, str]]) -> None:
    with table_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=REQUIRED_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def run_audit(
    schema_path: Path = SCHEMA_PATH,
    table_path: Path = AUDIT_TABLE_PATH,
) -> Path:
    load_patient_schema(schema_path)
    ensure_audit_table(table_path)
    header, rows = read_audit_table(table_path)
    if header != REQUIRED_FIELDS:
        raise PatientMetadataAuditError("Patient metadata audit table header mismatch")

    normalized_rows = validate_and_normalize_rows(rows)
    write_audit_table(table_path, normalized_rows)
    return table_path


def main() -> int:
    table_path = run_audit()
    print(f"Validated {table_path.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
