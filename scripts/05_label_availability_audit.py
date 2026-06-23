"""Safe label availability audit scaffold.

This script validates label dictionary/schema files and a local audit table. It
does not invent labels, infer disease activity, download datasets, or model.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, List, Sequence


REPO_ROOT = Path(__file__).resolve().parents[1]
LABEL_DICTIONARY_PATH = REPO_ROOT / "metadata" / "label_dictionary.yaml"
LABEL_SCHEMA_PATH = REPO_ROOT / "metadata" / "label_availability_schema.yaml"
AUDIT_TABLE_PATH = REPO_ROOT / "reports" / "tables" / "label_availability_audit.csv"

ALLOWED_LABEL_TYPES = [
    "diagnosis",
    "disease_activity",
    "lupus_nephritis_status",
    "flare_status",
    "treatment_status",
    "treatment_response",
    "control_type",
    "cohort_label",
    "batch_label",
]

LABEL_TYPE_ATTRIBUTES = [
    "description",
    "required_for_task",
    "allowed_values",
    "provenance_required",
    "can_be_inferred",
    "notes",
]

REQUIRED_FIELDS = [
    "dataset_id",
    "source",
    "accession_or_collection_id",
    "prediction_task",
    "label_type",
    "label_name_in_source",
    "label_values_observed",
    "label_provenance",
    "patient_level_available",
    "sample_level_available",
    "cell_level_only",
    "n_labeled_patients",
    "n_labeled_samples",
    "control_group_available",
    "activity_score_available",
    "activity_score_name",
    "lupus_nephritis_label_available",
    "treatment_label_available",
    "ambiguity_flag",
    "ambiguity_reason",
    "usable_for_training",
    "usable_for_external_validation",
    "notes",
    "audit_status",
]

REQUIRED_SCHEMA_ATTRIBUTES = ["required", "description"]
CRITICAL_ROW_FIELDS = [
    "dataset_id",
    "prediction_task",
    "label_type",
    "label_provenance",
    "audit_status",
]
TODO_VALUES = {"", "TODO", "todo", "UNKNOWN", "unknown"}
TRUE_VALUES = {"true", "yes", "1", "y"}


class LabelAvailabilityAuditError(ValueError):
    """Raised when label audit inputs are invalid."""


def _clean_scalar(value: str) -> str | bool:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        value = value[1:-1]
    if value == "true":
        return True
    if value == "false":
        return False
    return value


def load_label_dictionary(
    dictionary_path: Path = LABEL_DICTIONARY_PATH,
) -> Dict[str, object]:
    allowed_label_types: List[str] = []
    label_types: Dict[str, Dict[str, object]] = {}
    current_section: str | None = None
    current_label_type: str | None = None
    current_attribute: str | None = None

    for line_number, raw_line in enumerate(dictionary_path.read_text().splitlines(), start=1):
        line = raw_line.split("#", 1)[0].rstrip()
        if not line.strip():
            continue

        if not raw_line.startswith(" ") and line.endswith(":"):
            current_section = line[:-1].strip()
            current_label_type = None
            current_attribute = None
            continue

        if current_section == "allowed_label_types" and line.startswith("  - "):
            allowed_label_types.append(str(_clean_scalar(line[4:])))
            continue

        if current_section == "label_types":
            if line.startswith("  ") and not line.startswith("    ") and line.endswith(":"):
                current_label_type = line[2:-1].strip()
                current_attribute = None
                label_types[current_label_type] = {}
                continue

            if line.startswith("    ") and not line.startswith("      "):
                if current_label_type is None:
                    raise LabelAvailabilityAuditError(
                        f"Label attribute without label type at line {line_number}"
                    )
                attr_line = line[4:]
                if ":" not in attr_line:
                    raise LabelAvailabilityAuditError(
                        f"Malformed label attribute at line {line_number}"
                    )
                key, value = attr_line.split(":", 1)
                key = key.strip()
                value = value.strip()
                current_attribute = key
                if value:
                    label_types[current_label_type][key] = _clean_scalar(value)
                else:
                    label_types[current_label_type][key] = []
                continue

            if line.startswith("      - "):
                if current_label_type is None or current_attribute is None:
                    raise LabelAvailabilityAuditError(
                        f"Nested list item without label attribute at line {line_number}"
                    )
                values = label_types[current_label_type].setdefault(current_attribute, [])
                if not isinstance(values, list):
                    raise LabelAvailabilityAuditError(
                        f"Mixed scalar/list label attribute at line {line_number}"
                    )
                values.append(_clean_scalar(line[8:]))
                continue

        raise LabelAvailabilityAuditError(
            f"Unsupported label dictionary shape at line {line_number}: {raw_line}"
        )

    missing_types = [
        label_type for label_type in ALLOWED_LABEL_TYPES if label_type not in allowed_label_types
    ]
    if missing_types:
        raise LabelAvailabilityAuditError(
            f"Missing allowed label types: {', '.join(missing_types)}"
        )

    for label_type in ALLOWED_LABEL_TYPES:
        if label_type not in label_types:
            raise LabelAvailabilityAuditError(f"Missing label type metadata: {label_type}")
        missing_attrs = [
            attr for attr in LABEL_TYPE_ATTRIBUTES if attr not in label_types[label_type]
        ]
        if missing_attrs:
            raise LabelAvailabilityAuditError(
                f"{label_type} missing attributes: {', '.join(missing_attrs)}"
            )
        if label_types[label_type]["can_be_inferred"] is not False:
            raise LabelAvailabilityAuditError(
                f"{label_type}.can_be_inferred must be false"
            )
        if label_types[label_type]["provenance_required"] is not True:
            raise LabelAvailabilityAuditError(
                f"{label_type}.provenance_required must be true"
            )

    return {
        "allowed_label_types": allowed_label_types,
        "label_types": label_types,
    }


def load_label_schema(
    schema_path: Path = LABEL_SCHEMA_PATH,
) -> Dict[str, Dict[str, object]]:
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
            raise LabelAvailabilityAuditError(
                f"Unsupported schema content before fields at line {line_number}"
            )

        if line.startswith("  ") and not line.startswith("    ") and line.endswith(":"):
            current_field = line[2:-1].strip()
            fields[current_field] = {}
            continue

        if line.startswith("    "):
            if current_field is None:
                raise LabelAvailabilityAuditError(
                    f"Field attribute without field at line {line_number}"
                )
            attr_line = line[4:]
            if ":" not in attr_line:
                raise LabelAvailabilityAuditError(
                    f"Malformed field attribute at line {line_number}"
                )
            key, value = attr_line.split(":", 1)
            fields[current_field][key.strip()] = _clean_scalar(value)
            continue

        raise LabelAvailabilityAuditError(
            f"Unsupported schema shape at line {line_number}: {raw_line}"
        )

    missing_fields = [field for field in REQUIRED_FIELDS if field not in fields]
    if missing_fields:
        raise LabelAvailabilityAuditError(
            f"Missing label availability fields: {', '.join(missing_fields)}"
        )

    for field in REQUIRED_FIELDS:
        missing_attrs = [
            attr for attr in REQUIRED_SCHEMA_ATTRIBUTES if attr not in fields[field]
        ]
        if missing_attrs:
            raise LabelAvailabilityAuditError(
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
            raise LabelAvailabilityAuditError("Label availability audit table missing header")
        return list(reader.fieldnames), list(reader)


def _is_missing(value: str | None) -> bool:
    return value is None or value.strip() in TODO_VALUES


def _is_true(value: str | None) -> bool:
    return value is not None and value.strip().lower() in TRUE_VALUES


def validate_and_normalize_rows(
    rows: Sequence[Dict[str, str]],
    allowed_label_types: Sequence[str],
) -> List[Dict[str, str]]:
    normalized_rows: List[Dict[str, str]] = []

    for index, row in enumerate(rows, start=2):
        for field in CRITICAL_ROW_FIELDS:
            if _is_missing(row.get(field)):
                raise LabelAvailabilityAuditError(f"Row {index} missing {field}")

        label_type = row.get("label_type", "").strip()
        if label_type not in allowed_label_types:
            raise LabelAvailabilityAuditError(f"Row {index} has invalid label_type")

        if _is_true(row.get("cell_level_only")):
            raise LabelAvailabilityAuditError(
                f"Row {index} uses cell_level_only labels for patient-level prediction"
            )

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
    dictionary_path: Path = LABEL_DICTIONARY_PATH,
    schema_path: Path = LABEL_SCHEMA_PATH,
    table_path: Path = AUDIT_TABLE_PATH,
) -> Path:
    dictionary = load_label_dictionary(dictionary_path)
    load_label_schema(schema_path)
    ensure_audit_table(table_path)
    header, rows = read_audit_table(table_path)
    if header != REQUIRED_FIELDS:
        raise LabelAvailabilityAuditError("Label availability audit table header mismatch")

    allowed_label_types = dictionary["allowed_label_types"]
    assert isinstance(allowed_label_types, list)
    normalized_rows = validate_and_normalize_rows(rows, allowed_label_types)
    write_audit_table(table_path, normalized_rows)
    return table_path


def main() -> int:
    table_path = run_audit()
    print(f"Validated {table_path.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
