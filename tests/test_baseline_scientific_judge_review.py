import csv
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = (
    REPO_ROOT
    / "state"
    / "judge_reports"
    / "P3-F008_baseline_scientific_judge_report.md"
)
REVIEW_PATH = (
    REPO_ROOT / "reports" / "tables" / "baseline_scientific_judge_review.csv"
)
STATE_PATH = REPO_ROOT / "state" / "project_state.yaml"
BACKLOG_PATH = REPO_ROOT / "state" / "backlog.yaml"

REQUIRED_REVIEW_ITEMS = {
    "pseudobulk design",
    "logistic regression scaffold",
    "tree-based scaffold",
    "cell-type proportion scaffold",
    "evaluation protocol",
    "calibration scaffold",
    "leakage prevention dependency",
    "label verification dependency",
    "external validation dependency",
    "modeling readiness",
}
RESULT_TABLES = [
    "pseudobulk_feature_manifest.csv",
    "logistic_regression_results.csv",
    "tree_baseline_results.csv",
    "cell_type_proportion_results.csv",
    "baseline_evaluation_results.csv",
    "calibration_results.csv",
]


def read_review_rows():
    with REVIEW_PATH.open(newline="") as handle:
        return list(csv.DictReader(handle))


def test_scientific_judge_artifacts_exist():
    assert REPORT_PATH.exists()
    assert REVIEW_PATH.exists()


def test_review_contains_all_required_items_and_actions():
    rows = read_review_rows()

    assert len(rows) == len(REQUIRED_REVIEW_ITEMS)
    assert {row["review_item"] for row in rows} == REQUIRED_REVIEW_ITEMS
    assert all(row["status"] for row in rows)
    assert all(row["risk_level"] for row in rows)
    assert all(row["main_concern"] for row in rows)
    assert all(row["required_action"] for row in rows)
    assert {row["audit_status"] for row in rows} == {
        "scientific_review_complete"
    }


def test_training_is_not_approved_by_report_or_review():
    report = REPORT_PATH.read_text()
    rows = read_review_rows()
    readiness = next(row for row in rows if row["review_item"] == "modeling readiness")

    assert "Training is allowed now: NO." in report
    assert readiness["status"] == "not_ready"
    assert all(row["status"] != "approved_for_training" for row in rows)


def test_project_state_remains_phase3_with_modeling_locked():
    state = STATE_PATH.read_text()

    assert 'current_phase: "Phase 3"' in state
    assert "current_feature: P3-F008" in state
    assert "allow_modeling: false" in state
    assert "modeling_allowed: false" in state
    assert "selected_datasets: []" in state
    assert "external_validation_cohort: TODO" in state
    assert "training_allowed: false" in state


def test_phase3_scaffold_complete_and_phase4_not_started():
    backlog = BACKLOG_PATH.read_text()
    state = STATE_PATH.read_text()

    assert "phase_3_scaffold:" in backlog
    assert "status: complete" in backlog
    assert "completed_through: P3-F008" in backlog
    assert 'current_phase: "Phase 4"' not in state
    assert "current_feature: P4-" not in state
    assert "phase_4_scaffold:" not in backlog


def test_no_model_artifacts_exist():
    forbidden_suffixes = {".pkl", ".pt", ".pth", ".onnx", ".joblib", ".ckpt"}
    artifacts = [
        path
        for path in REPO_ROOT.rglob("*")
        if path.is_file()
        and ".git" not in path.parts
        and path.suffix.lower() in forbidden_suffixes
    ]

    assert artifacts == []


def test_no_metric_or_feature_values_populated_in_result_tables():
    table_dir = REPO_ROOT / "reports" / "tables"
    for filename in RESULT_TABLES:
        with (table_dir / filename).open(newline="") as handle:
            rows = list(csv.reader(handle))
        assert len(rows) == 1, f"{filename} must remain headers only"
