"""Safe dataset feasibility report generator scaffold.

This script reads local audit tables and writes a TODO-preserving report. It
does not approve datasets, close Human Gate 1, download data, invent rows, or
perform modeling.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, Iterable, List, Sequence


REPO_ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = REPO_ROOT / "state" / "project_state.yaml"
GEO_CANDIDATES_PATH = REPO_ROOT / "reports" / "tables" / "geo_candidate_datasets.csv"
CELLXGENE_CANDIDATES_PATH = (
    REPO_ROOT / "reports" / "tables" / "cellxgene_candidate_datasets.csv"
)
ELIGIBILITY_SCORES_PATH = REPO_ROOT / "reports" / "tables" / "dataset_eligibility_scores.csv"
LABEL_AUDIT_PATH = REPO_ROOT / "reports" / "tables" / "label_availability_audit.csv"
PATIENT_AUDIT_PATH = REPO_ROOT / "reports" / "tables" / "patient_metadata_audit.csv"
EXTERNAL_VALIDATION_PATH = (
    REPO_ROOT / "reports" / "tables" / "external_validation_candidates.csv"
)
REJECTED_DATASET_LOG_PATH = REPO_ROOT / "reports" / "tables" / "rejected_dataset_log.csv"
REPORT_PATH = REPO_ROOT / "reports" / "final_dataset_feasibility_report.md"

REJECTED_LOG_HEADERS = [
    "dataset_id",
    "source",
    "rejection_reason",
    "scientific_risk",
    "notes",
    "audit_status",
]

REPORT_SECTIONS = [
    "## 1. Executive Summary",
    "## 2. Scientific Goal",
    "## 3. Search Sources",
    "## 4. Candidate Dataset Table",
    "## 5. Rejected Datasets",
    "## 6. Selected Training Cohort(s)",
    "## 7. Selected External Validation Cohort(s)",
    "## 8. Label Availability Summary",
    "## 9. Patient Metadata Summary",
    "## 10. Cross-cohort Risks",
    "## 11. Known Limitations",
    "## 12. Human Gate 1 Recommendation",
    "## 13. TODOs",
]

APPROVAL_WORDS = {
    "approved",
    "approve",
    "selected",
    "accepted",
    "external_validation_ready",
}

ALLOWED_HUMAN_GATE_1_STATUSES = {"PENDING", "approved_with_restrictions"}


class DatasetFeasibilityReportError(ValueError):
    """Raised when report generation would violate Phase 1 scaffold controls."""


def read_csv(path: Path) -> tuple[List[str], List[Dict[str, str]]]:
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise DatasetFeasibilityReportError(f"{path} is missing a header")
        return list(reader.fieldnames), list(reader)


def ensure_rejected_log(
    path: Path = REJECTED_DATASET_LOG_PATH,
    headers: Sequence[str] = REJECTED_LOG_HEADERS,
) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        with path.open("w", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(headers)
    header, _ = read_csv(path)
    if header != list(headers):
        raise DatasetFeasibilityReportError("Rejected dataset log header mismatch")
    return path


def _state_value(lines: Sequence[str], key: str) -> str:
    prefix = f"  {key}:"
    for line in lines:
        if line.startswith(prefix):
            return line.split(":", 1)[1].strip()
    return "TODO"


def validate_state_gate_pending(state_path: Path = STATE_PATH) -> None:
    lines = state_path.read_text().splitlines()
    state_text = "\n".join(lines)
    if _state_value(lines, "external_validation_cohort") != "TODO":
        raise DatasetFeasibilityReportError("external_validation_cohort must remain TODO")

    required_locks = {
        "modeling_allowed: false",
        "allow_modeling: false",
        "training_allowed: false",
        "dataset_download_allowed: false",
        "allow_downloads: false",
    }
    missing_locks = sorted(lock for lock in required_locks if lock not in state_text)
    if missing_locks:
        raise DatasetFeasibilityReportError(
            "state must preserve modeling/training/download locks: "
            + ", ".join(missing_locks)
        )

    gate_seen = False
    allowed_status_seen = False
    for line in lines:
        if "Human Gate 1: Dataset Feasibility Approved" in line:
            gate_seen = True
        if gate_seen and line.strip().startswith("status:"):
            status = line.split(":", 1)[1].strip()
            allowed_status_seen = status in ALLOWED_HUMAN_GATE_1_STATUSES
            break
    if not allowed_status_seen:
        raise DatasetFeasibilityReportError(
            "Human Gate 1 must remain PENDING or approved_with_restrictions"
        )


def _contains_approval(row: Dict[str, str]) -> bool:
    for value in row.values():
        normalized = value.strip().lower()
        if normalized in APPROVAL_WORDS:
            return True
    return False


def validate_no_approvals(rows_by_table: Iterable[tuple[str, Sequence[Dict[str, str]]]]) -> None:
    for table_name, rows in rows_by_table:
        for index, row in enumerate(rows, start=2):
            if _contains_approval(row):
                raise DatasetFeasibilityReportError(
                    f"{table_name} row {index} appears to approve a dataset"
                )


def _todo_table(headers: Sequence[str]) -> str:
    header_line = "| " + " | ".join(headers) + " |"
    separator = "| " + " | ".join("---" for _ in headers) + " |"
    todo = "| " + " | ".join("TODO" for _ in headers) + " |"
    return "\n".join([header_line, separator, todo])


def _summary_line(label: str, rows: Sequence[Dict[str, str]]) -> str:
    if rows:
        return f"TODO: {label} has {len(rows)} row(s) requiring manual review."
    return f"TODO: {label} has no manually audited rows."


def build_report(
    geo_rows: Sequence[Dict[str, str]],
    cellxgene_rows: Sequence[Dict[str, str]],
    eligibility_rows: Sequence[Dict[str, str]],
    label_rows: Sequence[Dict[str, str]],
    patient_rows: Sequence[Dict[str, str]],
    external_rows: Sequence[Dict[str, str]],
    rejected_rows: Sequence[Dict[str, str]],
) -> str:
    candidate_headers = [
        "accession",
        "source",
        "tissue",
        "assay",
        "disease context",
        "number of patients",
        "labels available",
        "patient IDs available",
        "external validation suitability",
        "eligibility score",
        "decision",
    ]
    rejected_headers = ["dataset", "reason for rejection", "scientific risk"]

    lines = [
        "# Final Dataset Feasibility Report",
        "",
        "## 1. Executive Summary",
        "",
        "TODO: Human Gate 1 is approved_with_restrictions for scaffold work only. No dataset has been approved for modeling.",
        "",
        "## 2. Scientific Goal",
        "",
        "TODO: Define the final scientific goal after candidate datasets are manually audited.",
        "",
        "## 3. Search Sources",
        "",
        "- GEO: TODO.",
        "- CELLxGENE: TODO.",
        "- Human Cell Atlas: TODO.",
        "- Published AnnData/Seurat objects: TODO.",
        "",
        "## 4. Candidate Dataset Table",
        "",
        _todo_table(candidate_headers),
        "",
        _summary_line("GEO candidate table", geo_rows),
        "",
        _summary_line("CELLxGENE candidate table", cellxgene_rows),
        "",
        _summary_line("Eligibility score table", eligibility_rows),
        "",
        "## 5. Rejected Datasets",
        "",
        _todo_table(rejected_headers),
        "",
        _summary_line("Rejected dataset log", rejected_rows),
        "",
        "## 6. Selected Training Cohort(s)",
        "",
        "TODO: None selected. Human Gate 1 is approved_with_restrictions for scaffold work only.",
        "",
        "## 7. Selected External Validation Cohort(s)",
        "",
        "TODO: None selected. `external_validation_cohort` remains TODO.",
        "",
        "## 8. Label Availability Summary",
        "",
        _summary_line("Label availability audit", label_rows),
        "",
        "## 9. Patient Metadata Summary",
        "",
        _summary_line("Patient metadata audit", patient_rows),
        "",
        "## 10. Cross-cohort Risks",
        "",
        _summary_line("External validation candidate table", external_rows),
        "",
        "## 11. Known Limitations",
        "",
        "TODO: Candidate dataset limitations must be documented after manual audit.",
        "",
        "## 12. Human Gate 1 Recommendation",
        "",
        "TODO: Human Gate 1 is approved_with_restrictions for scaffold work only. Do not approve datasets, downloads, or modeling from this scaffold.",
        "",
        "## 13. TODOs",
        "",
        "- TODO: Manually audit candidate datasets.",
        "- TODO: Populate candidate evidence tables only with verified metadata.",
        "- TODO: Record rejected datasets with source-supported reasons.",
        "- TODO: Request Human Gate 1 review after feasibility evidence is complete.",
        "",
    ]
    return "\n".join(lines)


def run_report(
    report_path: Path = REPORT_PATH,
    state_path: Path = STATE_PATH,
) -> Path:
    validate_state_gate_pending(state_path)
    ensure_rejected_log()

    _, geo_rows = read_csv(GEO_CANDIDATES_PATH)
    _, cellxgene_rows = read_csv(CELLXGENE_CANDIDATES_PATH)
    _, eligibility_rows = read_csv(ELIGIBILITY_SCORES_PATH)
    _, label_rows = read_csv(LABEL_AUDIT_PATH)
    _, patient_rows = read_csv(PATIENT_AUDIT_PATH)
    _, external_rows = read_csv(EXTERNAL_VALIDATION_PATH)
    _, rejected_rows = read_csv(REJECTED_DATASET_LOG_PATH)

    validate_no_approvals(
        [
            ("geo_candidate_datasets.csv", geo_rows),
            ("cellxgene_candidate_datasets.csv", cellxgene_rows),
            ("dataset_eligibility_scores.csv", eligibility_rows),
            ("label_availability_audit.csv", label_rows),
            ("patient_metadata_audit.csv", patient_rows),
            ("external_validation_candidates.csv", external_rows),
            ("rejected_dataset_log.csv", rejected_rows),
        ]
    )

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        build_report(
            geo_rows,
            cellxgene_rows,
            eligibility_rows,
            label_rows,
            patient_rows,
            external_rows,
            rejected_rows,
        )
    )
    return report_path


def main() -> int:
    report_path = run_report()
    print(f"Wrote {report_path.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
