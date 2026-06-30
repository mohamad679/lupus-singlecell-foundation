import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DECISION_PATH = REPO_ROOT / "state" / "human_gate_2_decision.yaml"
STATE_PATH = REPO_ROOT / "state" / "project_state.yaml"
BACKLOG_PATH = REPO_ROOT / "state" / "backlog.yaml"
REPORT_PATH = (
    REPO_ROOT / "state" / "judge_reports" / "P2-F011_human_gate_2_decision_report.md"
)
CHECKLIST_PATH = REPO_ROOT / "state" / "human_gate_2_checklist.yaml"

PRIMARY_TASK = "SLE diagnosis / case-control prediction"
BLOCKED_TASKS = {
    "disease activity prediction",
    "flare prediction",
    "lupus nephritis prediction",
}
PHASE_3_FEATURES = {
    "P3-F001",
    "P3-F002",
    "P3-F003",
    "P3-F004",
    "P3-F005",
    "P3-F006",
    "P3-F007",
    "P3-F008",
}


def load_decision():
    return json.loads(DECISION_PATH.read_text())


def test_human_gate_2_decision_artifacts_exist():
    assert DECISION_PATH.exists()
    assert REPORT_PATH.exists()
    assert CHECKLIST_PATH.exists()


def test_gate_is_approved_with_restrictions_for_diagnosis_only():
    decision = load_decision()

    assert decision["human_gate_2_status"] == "approved_with_restrictions"
    assert decision["primary_task"] == PRIMARY_TASK
    assert decision["approved_only_for"] == [
        "Phase 3 baseline design for SLE diagnosis / case-control prediction"
    ]
    assert BLOCKED_TASKS <= set(decision["not_approved_for"])
    assert not BLOCKED_TASKS & set(decision["approved_only_for"])


def test_restricted_scopes_and_safety_controls_are_explicit():
    decision = load_decision()

    assert {
        "foundation models",
        "deep patient-level MIL",
        "uncertainty modeling",
        "dashboard",
    } <= set(decision["not_approved_for"])
    assert decision["allow_modeling"] is False
    assert decision["selected_datasets"] == []
    assert decision["external_validation_cohort"] == "TODO"
    assert decision["dataset_modeling_approval"] == "not_granted"
    assert len(decision["required_restrictions"]) == 6


def test_gate_checklist_records_restricted_decision_but_checks_remain_pending():
    checklist = json.loads(CHECKLIST_PATH.read_text())

    assert checklist["overall_status"] == "approved_with_restrictions"
    assert checklist["decision"] == "approved_with_restrictions"
    assert checklist["primary_task"] == PRIMARY_TASK
    assert all(
        check["status"] == "pending" for check in checklist["checks"].values()
    )


def test_project_state_records_restricted_gate_without_enabling_modeling():
    state = STATE_PATH.read_text()

    assert "current_phase: Stage 2" in state
    assert "current_feature: STAGE2-F004" in state
    assert "human_gate_2: approved_with_restrictions" in state
    assert "primary_task: Active SLE flare discrimination" in state
    assert "selected_datasets: []" in state
    assert "external_validation_cohort: TODO" in state
    assert "allow_modeling: false" in state
    assert "modeling_allowed: false" in state


def test_phase_2_is_complete_and_phase_3_backlog_only_exists():
    backlog = BACKLOG_PATH.read_text()

    assert "phase_2_scaffold:" in backlog
    assert "completed_through: P2-F011" in backlog
    assert "phase_3_scaffold:" in backlog
    assert "status: complete" in backlog
    assert "completed_through: P3-F019" in backlog
    for feature_id in PHASE_3_FEATURES:
        assert f"feature_id: {feature_id}" in backlog


def test_phase_3_models_package_contains_scaffold_only():
    models_dir = REPO_ROOT / "src" / "models"

    assert models_dir.exists()
    assert {path.name for path in models_dir.iterdir() if path.name != "__pycache__"} == {
        "__init__.py",
        "logistic_regression_baseline.py",
        "tree_baselines.py",
    }
