"""Validate the candidate dataset access plan.

This scaffold reads local metadata tables only. It does not acquire files,
create AnnData objects, preprocess data, approve datasets, assign cohorts, or
perform modeling.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Dict, Mapping, Sequence


REPO_ROOT = Path(__file__).resolve().parents[1]
PLAN_PATH = REPO_ROOT / "metadata" / "dataset_access_plan.yaml"
TABLE_PATH = REPO_ROOT / "reports" / "tables" / "dataset_access_plan.csv"

REQUIRED_CANDIDATES = {
    "GSE137029",
    "CELLxGENE_HCA_436154da-bcf1-4130-9c8b-120ff9a888f2_218acb0f-9f2f-4f76-b90b-15a4b7c7f629",
}
REQUIRED_TABLE_COLUMNS = [
    "candidate_id",
    "source",
    "accession_or_dataset_id",
    "intended_phase2_role",
    "approved_for_download",
    "approved_for_modeling",
    "expected_access_route",
    "required_before_download",
    "storage_risk",
    "metadata_risk",
    "access_risk",
    "notes",
    "audit_status",
]
REQUIRED_AUDIT_STATUS = "pending_human_download_gate"


class DatasetAccessPlanError(ValueError):
    """Raised when the access plan violates Phase 2 restrictions."""


def load_dataset_access_plan(path: Path | str = PLAN_PATH) -> Dict[str, Any]:
    plan_path = Path(path)
    try:
        plan = json.loads(plan_path.read_text())
    except json.JSONDecodeError as exc:
        raise DatasetAccessPlanError(
            f"{plan_path} must use JSON-compatible YAML syntax"
        ) from exc
    if not isinstance(plan, dict):
        raise DatasetAccessPlanError("dataset access plan must be a mapping")
    return plan


def read_access_plan_table(path: Path | str = TABLE_PATH) -> list[Dict[str, str]]:
    table_path = Path(path)
    with table_path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != REQUIRED_TABLE_COLUMNS:
            raise DatasetAccessPlanError("dataset access plan CSV headers are invalid")
        return list(reader)


def _as_false(value: Any) -> bool:
    if isinstance(value, bool):
        return value is False
    return str(value).strip().lower() == "false"


def _non_empty_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(str(item).strip() for item in value)


def validate_plan_metadata(plan: Mapping[str, Any]) -> None:
    candidates = plan.get("candidates")
    if not isinstance(candidates, Mapping):
        raise DatasetAccessPlanError("plan must contain a candidates mapping")

    candidate_ids = {
        str(candidate.get("candidate_id", "")).strip()
        for candidate in candidates.values()
        if isinstance(candidate, Mapping)
    }
    if candidate_ids != REQUIRED_CANDIDATES:
        raise DatasetAccessPlanError("plan candidates do not match required Phase 2 scope")

    for candidate_key, candidate in candidates.items():
        if not isinstance(candidate, Mapping):
            raise DatasetAccessPlanError(f"{candidate_key} entry must be a mapping")
        if not _as_false(candidate.get("approved_for_download")):
            raise DatasetAccessPlanError(f"{candidate_key} approved_for_download must be false")
        if not _as_false(candidate.get("approved_for_modeling")):
            raise DatasetAccessPlanError(f"{candidate_key} approved_for_modeling must be false")
        if not _non_empty_list(candidate.get("required_before_download")):
            raise DatasetAccessPlanError(
                f"{candidate_key} required_before_download must be non-empty"
            )


def validate_plan_rows(rows: Sequence[Mapping[str, str]]) -> None:
    if len(rows) != 2:
        raise DatasetAccessPlanError("dataset access plan table must contain exactly two rows")

    candidate_ids = {row.get("candidate_id", "") for row in rows}
    if candidate_ids != REQUIRED_CANDIDATES:
        raise DatasetAccessPlanError("table candidates do not match required Phase 2 scope")

    for index, row in enumerate(rows, start=1):
        if not _as_false(row.get("approved_for_download")):
            raise DatasetAccessPlanError(f"row {index} approved_for_download must be false")
        if not _as_false(row.get("approved_for_modeling")):
            raise DatasetAccessPlanError(f"row {index} approved_for_modeling must be false")
        if not str(row.get("required_before_download", "")).strip():
            raise DatasetAccessPlanError(
                f"row {index} required_before_download must be non-empty"
            )
        if row.get("audit_status") != REQUIRED_AUDIT_STATUS:
            raise DatasetAccessPlanError(
                f"row {index} audit_status must be {REQUIRED_AUDIT_STATUS}"
            )


def run_validation(
    plan_path: Path | str = PLAN_PATH,
    table_path: Path | str = TABLE_PATH,
) -> Dict[str, object]:
    plan = load_dataset_access_plan(plan_path)
    rows = read_access_plan_table(table_path)
    validate_plan_metadata(plan)
    validate_plan_rows(rows)
    return {
        "candidate_count": len(rows),
        "approved_for_download": False,
        "approved_for_modeling": False,
        "audit_status": REQUIRED_AUDIT_STATUS,
    }


def main() -> int:
    summary = run_validation()
    print("Dataset access plan validation passed")
    for key, value in summary.items():
        print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
