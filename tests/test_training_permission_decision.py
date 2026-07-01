import csv
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DECISION_PATH = REPO_ROOT / "state" / "training_permission_decision.yaml"
REPORT_PATH = (
    REPO_ROOT
    / "state"
    / "judge_reports"
    / "P3-F011_training_permission_decision_report.md"
)
VERIFICATION_PATH = (
    REPO_ROOT / "reports" / "tables" / "dataset_label_verification_checklist.csv"
)
READINESS_PATH = (
    REPO_ROOT / "reports" / "tables" / "modeling_readiness_checklist.csv"
)
STATE_PATH = REPO_ROOT / "state" / "project_state.yaml"
BACKLOG_PATH = REPO_ROOT / "state" / "backlog.yaml"

REQUIRED_BLOCKERS = {
    "dataset_selection",
    "label_provenance",
    "patient_or_donor_id_availability",
    "split_manifest_readiness",
    "leakage_check_readiness",
    "training_cohort_suitability",
    "qc_approval",
    "feature_manifest_readiness",
}


def load_decision():
    return json.loads(DECISION_PATH.read_text())


def read_csv(path):
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def test_training_permission_artifacts_exist():
    assert DECISION_PATH.exists()
    assert REPORT_PATH.exists()


def test_training_permission_is_formally_blocked():
    decision = load_decision()

    assert decision["training_permission"] == "blocked"
    assert decision["allow_modeling"] is False
    assert decision["training_allowed"] is False
    assert decision["modeling_readiness"] == "not_ready"
    assert decision["reason"] == "unresolved modeling readiness blockers"
    assert set(decision["blockers"]) == REQUIRED_BLOCKERS
    assert decision["phase_4_allowed"] is False


def test_unresolved_verification_blockers_remain_unverified():
    rows = read_csv(VERIFICATION_PATH)

    assert {row["requirement_type"] for row in rows} == REQUIRED_BLOCKERS
    assert all(row["evidence_status"] in {"pending", "blocked"} for row in rows)
    assert all(row["evidence_status"] != "verified" for row in rows)
    assert all(row["verified_by"] == "TODO" for row in rows)


def test_readiness_blockers_remain_pending_and_not_passed():
    rows = read_csv(READINESS_PATH)
    blockers = [row for row in rows if row["blocking"] == "true"]

    assert len(blockers) == 8
    assert all(row["status"] == "pending" for row in blockers)
    assert all(row["status"] != "passed" for row in blockers)


def test_project_state_records_denial_and_remains_unassigned():
    state = STATE_PATH.read_text()

    assert "current_phase: Stage 4" in state
    assert "current_feature: STAGE4-F001" in state
    assert "modeling_readiness: not_ready" in state
    assert "training_permission: blocked" in state
    assert "allow_modeling: false" in state
    assert "modeling_allowed: false" in state
    assert "training_allowed: false" in state
    assert "selected_datasets: []" in state
    assert "external_validation_cohort: TODO" in state


def test_phase3_is_complete_and_phase4_not_started():
    state = STATE_PATH.read_text()
    backlog = BACKLOG_PATH.read_text()

    assert "phase_3_scaffold:" in backlog
    assert "status: complete" in backlog
    assert "completed_through: P3-F019" in backlog
    assert 'current_phase: "Phase 4"' not in state
    assert "current_feature: STAGE4-F001" in state
    assert "phase_4_scaffold:" not in backlog


def test_no_model_artifacts_exist():
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
