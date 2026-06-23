"""Safe external validation candidate audit scaffold.

This script validates local criteria and candidate table structure. It does not
approve external cohorts, download data, invent rows, or perform modeling.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, List, Sequence


REPO_ROOT = Path(__file__).resolve().parents[1]
CRITERIA_PATH = REPO_ROOT / "metadata" / "external_validation_criteria.yaml"
CANDIDATE_TABLE_PATH = REPO_ROOT / "reports" / "tables" / "external_validation_candidates.csv"

CRITERIA_GROUPS = [
    "cohort_independence",
    "task_compatibility",
    "biological_compatibility",
    "metadata_sufficiency",
    "evaluation_feasibility",
    "hard_rejection_rules",
    "scoring",
]

REQUIRED_HARD_REJECTION_RULES = [
    "cell-level split only",
    "no patient identifiers",
    "no disease labels",
    "non-human data",
    "bulk-only data",
    "same cohort as training without holdout design",
    "invented or unverifiable metadata",
    "incompatible prediction task",
]

SCORING_DECISIONS = [
    "external_validation_ready",
    "usable_with_caution",
    "internal_validation_only",
    "reject",
]

REQUIRED_HEADERS = [
    "candidate_id",
    "source",
    "accession_or_collection_id",
    "candidate_role",
    "independent_study",
    "compatible_task",
    "compatible_tissue",
    "compatible_assay",
    "patient_id_available",
    "label_compatibility",
    "minimum_patient_count_met",
    "batch_metadata_available",
    "calibration_evaluation_possible",
    "uncertainty_shift_analysis_possible",
    "risk_level",
    "decision",
    "notes",
    "audit_status",
]

CRITICAL_ROW_FIELDS = [
    "candidate_id",
    "source",
    "accession_or_collection_id",
    "decision",
    "audit_status",
]

EXTERNAL_READY_FIELDS = [
    "candidate_id",
    "source",
    "accession_or_collection_id",
    "independent_study",
    "compatible_task",
    "compatible_tissue",
    "compatible_assay",
    "patient_id_available",
    "label_compatibility",
    "minimum_patient_count_met",
    "batch_metadata_available",
    "calibration_evaluation_possible",
    "uncertainty_shift_analysis_possible",
    "risk_level",
    "audit_status",
]

TODO_VALUES = {"", "TODO", "todo", "UNKNOWN", "unknown", "unresolved", "UNRESOLVED"}


class ExternalValidationAuditError(ValueError):
    """Raised when external validation audit inputs are invalid."""


def _clean_scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def load_criteria(criteria_path: Path = CRITERIA_PATH) -> Dict[str, List[str]]:
    criteria: Dict[str, List[str]] = {}
    current_key: str | None = None

    for line_number, raw_line in enumerate(criteria_path.read_text().splitlines(), start=1):
        line = raw_line.split("#", 1)[0].rstrip()
        if not line.strip():
            continue

        if not raw_line.startswith(" ") and line.endswith(":"):
            current_key = line[:-1].strip()
            criteria[current_key] = []
            continue

        if line.startswith("  - "):
            if current_key is None:
                raise ExternalValidationAuditError(
                    f"List item without section at line {line_number}"
                )
            criteria[current_key].append(_clean_scalar(line[4:]))
            continue

        raise ExternalValidationAuditError(
            f"Unsupported criteria YAML shape at line {line_number}: {raw_line}"
        )

    missing_groups = [group for group in CRITERIA_GROUPS if group not in criteria]
    if missing_groups:
        raise ExternalValidationAuditError(
            f"Missing criteria groups: {', '.join(missing_groups)}"
        )

    for group in CRITERIA_GROUPS:
        if not criteria[group]:
            raise ExternalValidationAuditError(f"{group} must not be empty")

    missing_rules = [
        rule for rule in REQUIRED_HARD_REJECTION_RULES if rule not in criteria["hard_rejection_rules"]
    ]
    if missing_rules:
        raise ExternalValidationAuditError(
            f"Missing hard rejection rules: {', '.join(missing_rules)}"
        )

    missing_decisions = [
        decision for decision in SCORING_DECISIONS if decision not in criteria["scoring"]
    ]
    if missing_decisions:
        raise ExternalValidationAuditError(
            f"Missing scoring decisions: {', '.join(missing_decisions)}"
        )

    return criteria


def ensure_candidate_table(
    table_path: Path = CANDIDATE_TABLE_PATH,
    required_headers: Sequence[str] = REQUIRED_HEADERS,
) -> Path:
    table_path.parent.mkdir(parents=True, exist_ok=True)
    if not table_path.exists():
        with table_path.open("w", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(required_headers)
    return table_path


def read_candidate_table(table_path: Path) -> tuple[List[str], List[Dict[str, str]]]:
    with table_path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ExternalValidationAuditError("External validation table missing header")
        return list(reader.fieldnames), list(reader)


def _is_missing(value: str | None) -> bool:
    return value is None or value.strip() in TODO_VALUES


def _has_ready_value(value: str | None) -> bool:
    return not _is_missing(value)


def validate_rows(rows: Sequence[Dict[str, str]]) -> List[Dict[str, str]]:
    normalized_rows: List[Dict[str, str]] = []

    for index, row in enumerate(rows, start=2):
        for field in CRITICAL_ROW_FIELDS:
            if _is_missing(row.get(field)):
                raise ExternalValidationAuditError(f"Row {index} missing {field}")

        decision = row.get("decision", "").strip()
        if decision not in SCORING_DECISIONS:
            raise ExternalValidationAuditError(f"Row {index} has invalid decision")

        if decision == "external_validation_ready":
            unresolved = [
                field for field in EXTERNAL_READY_FIELDS if not _has_ready_value(row.get(field))
            ]
            if unresolved:
                raise ExternalValidationAuditError(
                    "external_validation_ready requires resolved critical fields: "
                    f"{', '.join(unresolved)}"
                )

        normalized_rows.append(
            {
                field: row.get(field, "").strip() if not _is_missing(row.get(field)) else "TODO"
                for field in REQUIRED_HEADERS
            }
        )

    return normalized_rows


def write_candidate_table(table_path: Path, rows: Sequence[Dict[str, str]]) -> None:
    with table_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=REQUIRED_HEADERS)
        writer.writeheader()
        writer.writerows(rows)


def run_audit(
    criteria_path: Path = CRITERIA_PATH,
    table_path: Path = CANDIDATE_TABLE_PATH,
) -> Path:
    load_criteria(criteria_path)
    ensure_candidate_table(table_path)
    header, rows = read_candidate_table(table_path)
    if header != REQUIRED_HEADERS:
        raise ExternalValidationAuditError("External validation candidate table header mismatch")

    normalized_rows = validate_rows(rows)
    write_candidate_table(table_path, normalized_rows)
    return table_path


def main() -> int:
    table_path = run_audit()
    print(f"Validated {table_path.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
