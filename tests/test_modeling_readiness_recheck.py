import csv
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = (
    REPO_ROOT
    / "state"
    / "judge_reports"
    / "P3-F016_modeling_readiness_recheck_report.md"
)
RECHECK_PATH = (
    REPO_ROOT / "reports" / "tables" / "modeling_readiness_recheck.csv"
)
CHECKLIST_PATH = (
    REPO_ROOT / "reports" / "tables" / "modeling_readiness_checklist.csv"
)
GATE_PATH = REPO_ROOT / "state" / "modeling_readiness_gate.yaml"
TRAINING_DECISION_PATH = REPO_ROOT / "state" / "training_permission_decision.yaml"
STATE_PATH = REPO_ROOT / "state" / "project_state.yaml"
BACKLOG_PATH = REPO_ROOT / "state" / "backlog.yaml"

REQUIRED_COLUMNS = [
    "requirement",
    "previous_status",
    "current_status",
    "evidence_source",
    "blocking",
    "risk_level",
    "decision",
    "required_next_action",
    "audit_status",
]
REQUIRED_REQUIREMENTS = {
    "dataset_selection",
    "label_provenance",
    "patient_or_donor_id_availability",
    "split_manifest_readiness",
    "leakage_check_readiness",
    "training_cohort_suitability",
    "qc_approval",
    "feature_manifest_readiness",
    "external_validation_plan",
}
BLOCKING_REQUIREMENTS = REQUIRED_REQUIREMENTS - {"external_validation_plan"}


def read_table(path):
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames, list(reader)


def test_readiness_recheck_artifacts_exist():
    assert REPORT_PATH.exists()
    assert RECHECK_PATH.exists()


def test_recheck_table_has_required_rows_and_schema():
    fieldnames, rows = read_table(RECHECK_PATH)

    assert fieldnames == REQUIRED_COLUMNS
    assert len(rows) == 9
    assert {row["requirement"] for row in rows} == REQUIRED_REQUIREMENTS
    assert all(row["evidence_source"].strip() for row in rows)
    assert all(row["required_next_action"].strip() for row in rows)
    assert {
        row["audit_status"] for row in rows
    } <= {"readiness_rechecked", "readiness_expanded", "readiness_strategy_decided"}


def test_all_training_blockers_remain_pending():
    rows = read_table(RECHECK_PATH)[1]
    blockers = [row for row in rows if row["blocking"] == "true"]

    assert len(blockers) == 8
    assert {row["requirement"] for row in blockers} == BLOCKING_REQUIREMENTS
    assert all(row["previous_status"] == "pending" for row in blockers)
    assert all(row["current_status"] == "pending" for row in blockers)
    assert {
        row["decision"] for row in blockers
    } <= {
        "not_resolved",
        "candidate_specific_progress",
        "strategy_selected_validation_only",
        "candidate_validation_required",
    }


def test_external_validation_plan_stays_passed_without_cohort_assignment():
    rows = read_table(RECHECK_PATH)[1]
    external = next(
        row for row in rows if row["requirement"] == "external_validation_plan"
    )

    assert external["previous_status"] == "passed"
    assert external["current_status"] == "passed"
    assert external["blocking"] == "false"
    assert external["decision"] == "retain_passed_plan_only"


def test_readiness_checklist_did_not_pass_any_blocker():
    rows = read_table(CHECKLIST_PATH)[1]
    blockers = [row for row in rows if row["blocking"] == "true"]

    assert len(blockers) == 8
    assert all(row["status"] == "pending" for row in blockers)
    assert all(row["status"] != "passed" for row in blockers)
    assert {
        row["audit_status"] for row in rows
    } <= {"readiness_rechecked", "readiness_expanded", "readiness_strategy_decided"}


def test_gate_records_not_ready_decision_and_conditional_pivot():
    gate = json.loads(GATE_PATH.read_text())
    decision = gate["recheck_decision"]

    assert gate["modeling_readiness"] == "not_ready"
    assert gate["training_permission"] == "blocked"
    assert gate["allow_modeling"] is False
    assert gate["training_allowed"] is False
    assert gate["phase_4_allowed"] is False
    assert decision["decision"] == "not_ready"
    assert decision["recommendation"] == "more_metadata_inspection_required"
    assert decision["resolved_blocking_check_ids"] == []
    assert len(decision["remaining_blocking_check_ids"]) == 8
    assert "pivot" in decision["pivot_trigger"].lower()


def test_training_decision_and_project_state_remain_locked():
    training_decision = json.loads(TRAINING_DECISION_PATH.read_text())
    state = STATE_PATH.read_text()

    assert training_decision["training_permission"] == "blocked"
    assert training_decision["allow_modeling"] is False
    assert "current_feature: STAGE1-F003" in state
    assert "modeling_readiness: not_ready" in state
    assert "training_permission: blocked" in state
    assert "allow_modeling: false" in state
    assert "selected_datasets: []" in state
    assert "external_validation_cohort: TODO" in state


def test_no_model_artifacts_and_phase4_not_started():
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
    assert "feature_id: P3-F016" in backlog
    assert "feature_id: P3-F017" in backlog
