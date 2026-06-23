import csv
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DECISION_TABLE_PATH = (
    REPO_ROOT / "reports" / "tables" / "final_dataset_feasibility_decision.csv"
)
DECISION_REPORT_PATH = (
    REPO_ROOT / "state" / "judge_reports" / "P1-F014_final_dataset_decision_report.md"
)
STATE_PATH = REPO_ROOT / "state" / "project_state.yaml"

EXPECTED_CANDIDATES = {
    "GSE162577",
    "GSE137029",
    "GSE174188",
    "436154da-bcf1-4130-9c8b-120ff9a888f2::218acb0f-9f2f-4f76-b90b-15a4b7c7f629",
}

VALID_READINESS = {
    "continue_audit",
    "limited_candidate",
    "needs_manual_verification",
    "reject",
}

REQUIRED_COLUMNS = [
    "candidate_id",
    "scientific_status",
    "bioinformatics_status",
    "patient_level_status",
    "label_status",
    "cell_type_annotation_status",
    "processed_object_status",
    "external_validation_status",
    "data_access_risk",
    "cohort_overlap_risk",
    "overall_readiness",
    "main_blockers",
    "recommended_role",
    "human_gate_required",
    "audit_status",
]


def read_rows(path: Path):
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def test_decision_table_exists_with_required_columns():
    assert DECISION_TABLE_PATH.exists()
    with DECISION_TABLE_PATH.open(newline="") as handle:
        header = next(csv.reader(handle))

    assert header == REQUIRED_COLUMNS


def test_decision_report_exists_and_states_no_modeling_approval():
    assert DECISION_REPORT_PATH.exists()
    report = DECISION_REPORT_PATH.read_text()

    assert "No dataset is approved for modeling." in report
    assert (
        "Human Gate 1 remains PENDING" in report
        or "Human Gate 1 is approved_with_restrictions" in report
    )


def test_all_candidates_have_one_decision_row():
    rows = read_rows(DECISION_TABLE_PATH)

    assert {row["candidate_id"] for row in rows} == EXPECTED_CANDIDATES
    assert len(rows) == len(EXPECTED_CANDIDATES)


def test_no_candidate_is_approved():
    unsafe_values = {
        "approved",
        "dataset_approved",
        "external_validation_ready",
        "training_ready",
        "selected",
    }

    for row in read_rows(DECISION_TABLE_PATH):
        assert row["audit_status"] == "candidate_pending_audit"
        assert row["human_gate_required"] == "true"
        for value in row.values():
            assert value.strip().lower() not in unsafe_values


def test_overall_readiness_values_are_valid():
    for row in read_rows(DECISION_TABLE_PATH):
        assert row["overall_readiness"] in VALID_READINESS


def test_project_state_remains_blocked_and_gate_pending():
    state = STATE_PATH.read_text()

    assert "current_feature: P2-F002" in state
    assert "blocked: false" in state
    assert "selected_datasets: []" in state
    assert "external_validation_cohort: TODO" in state
    assert "label: \"Human Gate 1: Dataset Feasibility Approved\"" in state
    assert "status: approved_with_restrictions" in state
