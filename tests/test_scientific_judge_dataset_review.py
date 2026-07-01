import csv
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
JUDGE_REPORT_PATH = (
    REPO_ROOT / "state" / "judge_reports" / "P1-F011_scientific_judge_report.md"
)
REVIEW_TABLE_PATH = REPO_ROOT / "reports" / "tables" / "scientific_judge_dataset_review.csv"
STATE_PATH = REPO_ROOT / "state" / "project_state.yaml"

EXPECTED_CANDIDATES = {
    "GSE162577",
    "GSE137029",
    "GSE174188",
    "436154da-bcf1-4130-9c8b-120ff9a888f2::218acb0f-9f2f-4f76-b90b-15a4b7c7f629",
}

ALLOWED_STATUSES = {
    "continue_audit",
    "limited_candidate",
    "reject",
    "needs_manual_verification",
}

REQUIRED_COLUMNS = [
    "candidate_id",
    "source",
    "scientific_status",
    "patient_level_feasibility",
    "label_feasibility",
    "external_validation_feasibility",
    "activity_prediction_feasibility",
    "lupus_nephritis_feasibility",
    "data_access_risk",
    "leakage_risk",
    "main_blockers",
    "recommended_next_action",
    "audit_status",
]


def read_rows(path: Path):
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def test_scientific_judge_report_exists():
    assert JUDGE_REPORT_PATH.exists()
    assert JUDGE_REPORT_PATH.read_text().strip()


def test_scientific_review_csv_exists_with_required_columns():
    assert REVIEW_TABLE_PATH.exists()
    with REVIEW_TABLE_PATH.open(newline="") as handle:
        header = next(csv.reader(handle))

    assert header == REQUIRED_COLUMNS


def test_every_known_candidate_has_one_review_row():
    rows = read_rows(REVIEW_TABLE_PATH)

    assert {row["candidate_id"] for row in rows} == EXPECTED_CANDIDATES
    assert len(rows) == len(EXPECTED_CANDIDATES)


def test_no_candidate_is_marked_approved():
    unsafe_values = {
        "approved",
        "dataset_approved",
        "external_validation_ready",
        "training_ready",
    }

    for row in read_rows(REVIEW_TABLE_PATH):
        assert row["scientific_status"] in ALLOWED_STATUSES
        assert row["scientific_status"].lower() not in unsafe_values
        assert row["audit_status"] == "candidate_pending_audit"


def test_state_keeps_human_gate_and_selection_pending():
    state = STATE_PATH.read_text()

    assert "current_feature: STAGE3-F002" in state
    assert "selected_datasets: []" in state
    assert "external_validation_cohort: TODO" in state
    assert "Human Gate 1: Dataset Feasibility Approved" in state
    assert "status: approved_with_restrictions" in state


def test_every_row_has_next_action_and_blockers():
    for row in read_rows(REVIEW_TABLE_PATH):
        assert row["recommended_next_action"].strip()
        assert row["main_blockers"].strip()
