import csv
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
GATE_PATH = REPO_ROOT / "state" / "modeling_readiness_gate.yaml"
REPORT_PATH = (
    REPO_ROOT
    / "state"
    / "judge_reports"
    / "P3-F009_modeling_readiness_gate_report.md"
)
CHECKLIST_PATH = (
    REPO_ROOT / "reports" / "tables" / "modeling_readiness_checklist.csv"
)
STATE_PATH = REPO_ROOT / "state" / "project_state.yaml"
BACKLOG_PATH = REPO_ROOT / "state" / "backlog.yaml"

REQUIRED_REQUIREMENTS = {
    "dataset selected",
    "labels verified",
    "patient/donor IDs verified",
    "split manifest ready",
    "leakage checks ready",
    "prediction task approved",
    "training cohort selected",
    "external validation plan documented",
    "QC protocol approved",
    "feature manifest ready",
    "evaluation protocol ready",
}


def load_gate():
    return json.loads(GATE_PATH.read_text())


def read_checklist():
    with CHECKLIST_PATH.open(newline="") as handle:
        return list(csv.DictReader(handle))


def test_modeling_readiness_gate_artifacts_exist():
    assert GATE_PATH.exists()
    assert REPORT_PATH.exists()
    assert CHECKLIST_PATH.exists()


def test_gate_is_not_ready_and_cannot_enable_training():
    gate = load_gate()

    assert gate["modeling_readiness"] == "not_ready"
    assert gate["allow_modeling"] is False
    assert gate["training_allowed"] is False
    assert gate["phase_4_allowed"] is False


def test_checklist_has_all_requirements_and_unresolved_blockers():
    rows = read_checklist()

    assert len(rows) == len(REQUIRED_REQUIREMENTS)
    assert {row["requirement"] for row in rows} == REQUIRED_REQUIREMENTS
    assert all(row["status"] in {"pending", "passed"} for row in rows)
    assert all(row["required_evidence"] for row in rows)
    assert all(row["current_evidence"] for row in rows)
    assert all(row["next_action"] for row in rows)
    blockers = [
        row for row in rows if row["blocking"] == "true" and row["status"] == "pending"
    ]
    assert len(blockers) == 8
    assert all(row["status"] != "passed" for row in blockers)


def test_only_supported_scaffold_conditions_are_passed():
    rows = read_checklist()
    passed = {row["requirement"] for row in rows if row["status"] == "passed"}

    assert passed == {
        "prediction task approved",
        "external validation plan documented",
        "evaluation protocol ready",
    }


def test_project_state_remains_locked_and_unassigned():
    state = STATE_PATH.read_text()

    assert 'current_phase: "Phase 3"' in state
    assert "current_feature: P3-F013" in state
    assert "modeling_readiness: not_ready" in state
    assert "allow_modeling: false" in state
    assert "modeling_allowed: false" in state
    assert "training_allowed: false" in state
    assert "selected_datasets: []" in state
    assert "external_validation_cohort: TODO" in state


def test_phase4_is_not_started_and_next_phase3_items_exist():
    state = STATE_PATH.read_text()
    backlog = BACKLOG_PATH.read_text()

    assert 'current_phase: "Phase 4"' not in state
    assert "current_feature: P4-" not in state
    assert "phase_4_scaffold:" not in backlog
    for feature_id in ["P3-F009", "P3-F010", "P3-F011"]:
        assert f"feature_id: {feature_id}" in backlog
    assert "completed_through: P3-F013" in backlog


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
