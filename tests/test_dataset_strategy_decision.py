import csv
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DECISION_PATH = REPO_ROOT / "state" / "dataset_strategy_decision.yaml"
REPORT_PATH = (
    REPO_ROOT
    / "state"
    / "judge_reports"
    / "P3-F019_dataset_strategy_decision_report.md"
)
OPTIONS_PATH = REPO_ROOT / "reports" / "tables" / "dataset_strategy_options.csv"
BLOCKERS_PATH = (
    REPO_ROOT / "reports" / "tables" / "strategy_decision_blockers.csv"
)
STATE_PATH = REPO_ROOT / "state" / "project_state.yaml"
BACKLOG_PATH = REPO_ROOT / "state" / "backlog.yaml"

ALLOWED_DECISIONS = {
    "continue_GSE137029",
    "switch_primary_to_CELLxGENE_HCA",
    "search_new_dataset",
    "pivot_to_dataset_audit_paper",
    "pause_modeling",
}
OPTION_COLUMNS = [
    "strategy_option",
    "status",
    "scientific_rationale",
    "main_benefit",
    "main_risk",
    "required_next_action",
    "decision",
    "audit_status",
]
BLOCKER_COLUMNS = [
    "blocker_id",
    "blocker",
    "affected_strategy",
    "severity",
    "evidence_basis",
    "required_resolution",
    "audit_status",
]


def read_table(path):
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames, list(reader)


def test_strategy_artifacts_exist():
    assert DECISION_PATH.exists()
    assert REPORT_PATH.exists()
    assert OPTIONS_PATH.exists()
    assert BLOCKERS_PATH.exists()


def test_strategy_decision_is_allowed_and_restricted():
    decision = json.loads(DECISION_PATH.read_text())

    assert decision["decision"] in ALLOWED_DECISIONS
    assert decision["decision"] == "switch_primary_to_CELLxGENE_HCA"
    assert decision["decision_scope"] == "primary candidate validation only"
    assert decision["cellxgene_hca_role"] == "candidate_pending_primary_validation"
    assert decision["gse137029_role"] == "blocked_for_patient_level_modeling"
    assert decision["pivot_status"] == "not_activated"
    assert decision["modeling_readiness"] == "not_ready"
    assert decision["training_permission"] == "blocked"
    assert decision["allow_modeling"] is False
    assert decision["phase4_permission"] == "blocked"
    assert decision["selected_datasets"] == []
    assert decision["external_validation_cohort"] == "TODO"


def test_all_strategy_options_are_assessed_once():
    fieldnames, rows = read_table(OPTIONS_PATH)

    assert fieldnames == OPTION_COLUMNS
    assert len(rows) == 5
    assert {row["strategy_option"] for row in rows} == ALLOWED_DECISIONS
    assert sum(row["decision"] == "chosen" for row in rows) == 1
    assert next(row for row in rows if row["decision"] == "chosen")[
        "strategy_option"
    ] == "switch_primary_to_CELLxGENE_HCA"
    assert all(row["scientific_rationale"].strip() for row in rows)
    assert all(row["main_risk"].strip() for row in rows)
    assert all(row["required_next_action"].strip() for row in rows)
    assert all(row["audit_status"] == "strategy_option_reviewed" for row in rows)
    assert all("approved" not in row["status"].lower() for row in rows)


def test_strategy_blockers_remain_open_and_evidence_backed():
    fieldnames, rows = read_table(BLOCKERS_PATH)

    assert fieldnames == BLOCKER_COLUMNS
    assert len(rows) >= 1
    assert all(row["blocker_id"].strip() for row in rows)
    assert all(row["blocker"].strip() for row in rows)
    assert all(row["evidence_basis"].strip() for row in rows)
    assert all(row["required_resolution"].strip() for row in rows)
    assert all(row["severity"] in {"critical", "high", "moderate", "low"} for row in rows)
    assert all(row["audit_status"] == "strategy_blocker_open" for row in rows)


def test_project_permissions_and_assignments_remain_locked():
    state = STATE_PATH.read_text()

    assert "current_feature: STAGE3-PLANNING" in state
    assert "dataset_strategy_decision: reconcile_real_CELLxGENE_exploratory_run" in state
    assert "pivot_status: not_activated" in state
    assert "modeling_readiness: not_ready" in state
    assert "training_permission: blocked" in state
    assert "allow_modeling: false" in state
    assert "phase4_permission: blocked" in state
    assert "selected_datasets: []" in state
    assert "external_validation_cohort: TODO" in state


def test_phase4_and_model_artifacts_are_absent_and_p3_f020_is_todo():
    state = STATE_PATH.read_text()
    backlog = BACKLOG_PATH.read_text()
    forbidden_suffixes = {".pkl", ".pt", ".pth", ".onnx", ".joblib", ".ckpt"}
    artifacts = [
        path
        for path in REPO_ROOT.rglob("*")
        if path.is_file()
        and ".git" not in path.parts
        and ".venv" not in path.parts
        and "__pycache__" not in path.parts
        and "data" not in path.parts
        and not str(path.relative_to(REPO_ROOT)).startswith("results/phase1/")
        and path.suffix.lower() in forbidden_suffixes
    ]

    assert artifacts == []
    assert 'current_phase: "Phase 4"' not in state
    assert "current_feature: P4-" not in state
    assert "phase_4_scaffold:" not in backlog
    assert "completed_through: P3-F019" in backlog

    p3_f019 = backlog.split("feature_id: P3-F019", 1)[1].split(
        "feature_id: P3-F020", 1
    )[0]
    p3_f020 = backlog.split("feature_id: P3-F020", 1)[1]
    assert "status: done" in p3_f019
    assert "status: TODO" in p3_f020
