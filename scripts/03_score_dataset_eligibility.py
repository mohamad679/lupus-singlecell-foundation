"""Safe dataset eligibility scoring scaffold.

This script validates scoring configuration and candidate tables. It creates a
score table, but it does not invent candidates, download data, or assign
eligibility to unaudited rows.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, List, Sequence


REPO_ROOT = Path(__file__).resolve().parents[1]
SCORING_SCHEMA_PATH = REPO_ROOT / "metadata" / "dataset_eligibility_scoring.yaml"
GEO_CANDIDATES_PATH = REPO_ROOT / "reports" / "tables" / "geo_candidate_datasets.csv"
CELLXGENE_CANDIDATES_PATH = (
    REPO_ROOT / "reports" / "tables" / "cellxgene_candidate_datasets.csv"
)
SCORE_OUTPUT_PATH = REPO_ROOT / "reports" / "tables" / "dataset_eligibility_scores.csv"

DIMENSION_WEIGHT_KEYS = [
    "core_dataset_validity_weight",
    "prediction_task_feasibility_weight",
    "patient_level_modeling_feasibility_weight",
    "cross_cohort_validation_suitability_weight",
    "bioinformatics_interpretability_weight",
    "reproducibility_and_accessibility_weight",
]

ELIGIBILITY_CATEGORY_KEYS = [
    "eligibility_category_excellent",
    "eligibility_category_usable_with_caution",
    "eligibility_category_limited",
    "eligibility_category_reject",
]

REQUIRED_HARD_REJECTION_RULES = [
    "not single-cell",
    "not human",
    "no patient/donor IDs",
    "no disease labels",
    "invented or unverifiable metadata",
    "bulk RNA-seq only",
    "ambiguous accession without source",
]

DEFAULT_OUTPUT_COLUMNS = [
    "source_table",
    "candidate_key",
    "audit_status",
    "total_score",
    "eligibility_category",
    "training_usable",
    "internal_validation_usable",
    "external_validation_usable",
    "disease_activity_prediction_usable",
    "biological_interpretation_usable",
    "hard_rejection_flags",
    "missing_information",
    "score_status",
    "notes",
]

MANUAL_VERIFIED_STATUS = "manual_metadata_verified"
TODO_VALUES = {"", "TODO", "UNKNOWN", "unknown", "todo"}


class EligibilityScoringError(ValueError):
    """Raised when scoring inputs are invalid or unsafe to score."""


def _clean_scalar(value: str) -> str | int:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        value = value[1:-1]
    if value.isdigit():
        return int(value)
    return value


def load_simple_yaml(path: Path) -> Dict[str, object]:
    """Load the top-level scalar/list YAML shape used by the scoring schema."""
    data: Dict[str, object] = {}
    current_key: str | None = None

    for line_number, raw_line in enumerate(path.read_text().splitlines(), start=1):
        line = raw_line.split("#", 1)[0].rstrip()
        if not line.strip():
            continue

        if not raw_line.startswith(" ") and ":" in line:
            key, value = line.split(":", 1)
            current_key = key.strip()
            value = value.strip()
            if value:
                data[current_key] = _clean_scalar(value)
            else:
                data[current_key] = []
            continue

        if line.startswith("  - "):
            if current_key is None:
                raise EligibilityScoringError(
                    f"List item without section at line {line_number}"
                )
            section = data.setdefault(current_key, [])
            if not isinstance(section, list):
                raise EligibilityScoringError(
                    f"List item under scalar section at line {line_number}"
                )
            section.append(_clean_scalar(line[4:]))
            continue

        raise EligibilityScoringError(
            f"Unsupported YAML shape at line {line_number}: {raw_line}"
        )

    return data


def load_scoring_schema(schema_path: Path = SCORING_SCHEMA_PATH) -> Dict[str, object]:
    schema = load_simple_yaml(schema_path)

    missing_weights = [key for key in DIMENSION_WEIGHT_KEYS if key not in schema]
    if missing_weights:
        raise EligibilityScoringError(
            f"Missing dimension weights: {', '.join(missing_weights)}"
        )

    total = sum(int(schema[key]) for key in DIMENSION_WEIGHT_KEYS)
    if total != int(schema.get("total_points", 0)):
        raise EligibilityScoringError("Dimension weights do not match total_points")
    if total != 100:
        raise EligibilityScoringError("Eligibility scoring total must be 100")

    missing_categories = [key for key in ELIGIBILITY_CATEGORY_KEYS if key not in schema]
    if missing_categories:
        raise EligibilityScoringError(
            f"Missing eligibility categories: {', '.join(missing_categories)}"
        )

    hard_rules = schema.get("hard_rejection_rules")
    if not isinstance(hard_rules, list):
        raise EligibilityScoringError("hard_rejection_rules must be a list")
    missing_rules = [rule for rule in REQUIRED_HARD_REJECTION_RULES if rule not in hard_rules]
    if missing_rules:
        raise EligibilityScoringError(
            f"Missing hard rejection rules: {', '.join(missing_rules)}"
        )

    output_columns = schema.get("score_output_columns")
    if not isinstance(output_columns, list) or output_columns != DEFAULT_OUTPUT_COLUMNS:
        raise EligibilityScoringError("score_output_columns must match expected output schema")

    for key in [
        "required_geo_hard_rejection_fields",
        "required_cellxgene_hard_rejection_fields",
    ]:
        if not isinstance(schema.get(key), list):
            raise EligibilityScoringError(f"{key} must be a list")

    return schema


def read_candidate_table(path: Path) -> tuple[List[str], List[Dict[str, str]]]:
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise EligibilityScoringError(f"{path} is missing a header")
        return list(reader.fieldnames), list(reader)


def validate_required_columns(
    source_name: str, header: Sequence[str], required_fields: Sequence[str]
) -> None:
    missing = [field for field in required_fields if field not in header]
    if missing:
        raise EligibilityScoringError(
            f"{source_name} candidate table missing required columns: {', '.join(missing)}"
        )


def _is_missing(value: str | None) -> bool:
    return value is None or value.strip() in TODO_VALUES


def _candidate_key(source_name: str, row: Dict[str, str]) -> str:
    if source_name == "geo":
        return row.get("accession", "").strip()
    return "::".join(
        [
            row.get("collection_id", "").strip(),
            row.get("dataset_id", "").strip(),
        ]
    )


def _missing_hard_fields(row: Dict[str, str], required_fields: Sequence[str]) -> List[str]:
    return [field for field in required_fields if _is_missing(row.get(field))]


def build_unscored_row(source_name: str, row: Dict[str, str]) -> Dict[str, str]:
    return {
        "source_table": source_name,
        "candidate_key": _candidate_key(source_name, row),
        "audit_status": row.get("audit_status", "").strip() or "TODO",
        "total_score": "TODO",
        "eligibility_category": "TODO",
        "training_usable": "TODO",
        "internal_validation_usable": "TODO",
        "external_validation_usable": "TODO",
        "disease_activity_prediction_usable": "TODO",
        "biological_interpretation_usable": "TODO",
        "hard_rejection_flags": "TODO",
        "missing_information": "TODO",
        "score_status": "not_scored_pending_manual_audit",
        "notes": "Unaudited candidate; scoring requires manual metadata verification.",
    }


def validate_candidate_rows_for_scoring(
    source_name: str,
    rows: Sequence[Dict[str, str]],
    required_hard_fields: Sequence[str],
) -> List[Dict[str, str]]:
    output_rows: List[Dict[str, str]] = []

    for index, row in enumerate(rows, start=2):
        audit_status = row.get("audit_status", "").strip()
        if _is_missing(audit_status):
            raise EligibilityScoringError(f"{source_name} row {index} missing audit_status")

        if source_name == "geo" and _is_missing(row.get("accession")):
            raise EligibilityScoringError(f"{source_name} row {index} missing accession")
        if source_name == "cellxgene":
            if _is_missing(row.get("collection_id")):
                raise EligibilityScoringError(
                    f"{source_name} row {index} missing collection_id"
                )
            if _is_missing(row.get("dataset_id")):
                raise EligibilityScoringError(f"{source_name} row {index} missing dataset_id")

        if audit_status != MANUAL_VERIFIED_STATUS:
            output_rows.append(build_unscored_row(source_name, row))
            continue

        missing_fields = _missing_hard_fields(row, required_hard_fields)
        if missing_fields:
            raise EligibilityScoringError(
                f"{source_name} row {index} missing hard-rejection fields: "
                f"{', '.join(missing_fields)}"
            )

        output_rows.append(
            {
                "source_table": source_name,
                "candidate_key": _candidate_key(source_name, row),
                "audit_status": audit_status,
                "total_score": "TODO",
                "eligibility_category": "TODO",
                "training_usable": "TODO",
                "internal_validation_usable": "TODO",
                "external_validation_usable": "TODO",
                "disease_activity_prediction_usable": "TODO",
                "biological_interpretation_usable": "TODO",
                "hard_rejection_flags": "TODO",
                "missing_information": "TODO",
                "score_status": "ready_for_manual_scoring",
                "notes": "Manual metadata verified; numerical scoring not implemented in this scaffold.",
            }
        )

    return output_rows


def write_score_table(output_path: Path, rows: Sequence[Dict[str, str]]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=DEFAULT_OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def run_scoring(
    schema_path: Path = SCORING_SCHEMA_PATH,
    geo_candidates_path: Path = GEO_CANDIDATES_PATH,
    cellxgene_candidates_path: Path = CELLXGENE_CANDIDATES_PATH,
    output_path: Path = SCORE_OUTPUT_PATH,
) -> Path:
    schema = load_scoring_schema(schema_path)

    geo_header, geo_rows = read_candidate_table(geo_candidates_path)
    cellxgene_header, cellxgene_rows = read_candidate_table(cellxgene_candidates_path)

    geo_required = schema["required_geo_hard_rejection_fields"]
    cellxgene_required = schema["required_cellxgene_hard_rejection_fields"]
    assert isinstance(geo_required, list)
    assert isinstance(cellxgene_required, list)

    validate_required_columns("geo", geo_header, geo_required)
    validate_required_columns("cellxgene", cellxgene_header, cellxgene_required)

    output_rows = []
    output_rows.extend(validate_candidate_rows_for_scoring("geo", geo_rows, geo_required))
    output_rows.extend(
        validate_candidate_rows_for_scoring(
            "cellxgene", cellxgene_rows, cellxgene_required
        )
    )

    write_score_table(output_path, output_rows)
    return output_path


def main() -> int:
    output_path = run_scoring()
    print(f"Wrote {output_path.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
