import csv
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DECISION_PATH = REPO_ROOT / "state" / "training_permission_reevaluation.yaml"
REPORT_PATH = (
    REPO_ROOT
    / "state"
    / "judge_reports"
    / "P3-F017_training_permission_reevaluation_report.md"
)
TABLE_PATH = (
    REPO_ROOT / "reports" / "tables" / "training_permission_reevaluation.csv"
)
STATE_PATH = REPO_ROOT / "state" / "project_state.yaml"
BACKLOG_PATH = REPO_ROOT / "state" / "backlog.yaml"

REQUIRED_COLUMNS = [
    "decision_item",
    "status",
    "blocking",
    "risk_level",
    "evidence_basis",
    "required_next_action",
    "audit_status",
]
REQUIRED_ITEMS = {
    "training_permission",
    "allow_modeling",
    "dataset_selection",
    "label_provenance",
    "patient_donor_mapping",
    "split_manifest",
    "leakage_checks",
    "qc_approval",
    "feature_manifest",
    "external_validation",
    "phase4_permission",
    "pivot_status",
}
REQUIRED_BLOCKING_REASONS = {
    "dataset selection unresolved",
    "label provenance unresolved",
    "patient/donor mapping unresolved",
    "split manifest unavailable",
    "leakage checks not executable on real data",
    "QC not approved on real data",
    "feature manifest unavailable",
    "external validation unresolved",
}


def load_decision():
    return json.loads(DECISION_PATH.read_text())


def read_table():
    with TABLE_PATH.open(newline="") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames, list(reader)


def test_reevaluation_artifacts_exist():
    assert DECISION_PATH.exists()
    assert REPORT_PATH.exists()
    assert TABLE_PATH.exists()


def test_reevaluation_decision_remains_blocked():
    decision = load_decision()

    assert decision["training_permission"] == "blocked"
    assert decision["allow_modeling"] is False
    assert decision["decision"] == "continue_metadata_inspection"
    assert decision["pivot_status"] == "not_activated"
    assert decision["phase4_permission"] == "blocked"
    assert decision["modeling_readiness"] == "not_ready"
    assert decision["selected_datasets"] == []
    assert decision["external_validation_cohort"] == "TODO"
    assert set(decision["blocking_reasons"]) == REQUIRED_BLOCKING_REASONS


def test_reevaluation_table_has_all_decision_items():
    fieldnames, rows = read_table()

    assert fieldnames == REQUIRED_COLUMNS
    assert len(rows) == 12
    assert {row["decision_item"] for row in rows} == REQUIRED_ITEMS
    assert all(row["evidence_basis"].strip() for row in rows)
    assert all(row["required_next_action"].strip() for row in rows)
    assert all(row["audit_status"] == "permission_reevaluated" for row in rows)


def test_critical_permissions_and_readiness_items_are_blocked():
    rows = {row["decision_item"]: row for row in read_table()[1]}

    assert rows["training_permission"]["status"] == "blocked"
    assert rows["allow_modeling"]["status"] == "false"
    assert rows["phase4_permission"]["status"] == "blocked"
    assert rows["dataset_selection"]["status"] == "unresolved"
    assert rows["label_provenance"]["status"] == "unresolved"
    assert rows["patient_donor_mapping"]["status"] == "unresolved"
    assert rows["split_manifest"]["status"] == "unavailable"
    assert rows["leakage_checks"]["status"] == "not_executable"
    assert rows["qc_approval"]["status"] == "not_approved"
    assert rows["feature_manifest"]["status"] == "unavailable"
    assert rows["external_validation"]["status"] == "unresolved"
    assert all(
        rows[item]["blocking"] == "true"
        for item in REQUIRED_ITEMS - {"pivot_status"}
    )


def test_pivot_is_documented_but_not_activated():
    decision = load_decision()
    rows = {row["decision_item"]: row for row in read_table()[1]}

    assert decision["pivot_status"] == "not_activated"
    assert decision["pivot_trigger_conditions"]
    assert rows["pivot_status"]["status"] == "not_activated"
    assert rows["pivot_status"]["blocking"] == "false"
    assert "separate" in rows["pivot_status"]["required_next_action"].lower()


def test_project_state_keeps_training_and_phase4_blocked():
    state = STATE_PATH.read_text()

    assert "current_phase: Stage 3" in state
    assert "current_feature: STAGE3-F005" in state
    assert "modeling_readiness: not_ready" in state
    assert "training_permission: blocked" in state
    assert "allow_modeling: false" in state
    assert "phase4_permission: blocked" in state
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
    assert "feature_id: P3-F017" in backlog


def test_optional_future_items_remain_todo():
    backlog = BACKLOG_PATH.read_text()

    for feature_id in ("P3-F020",):
        marker = f"feature_id: {feature_id}"
        assert marker in backlog
        section = backlog.split(marker, 1)[1].split("\n  - id:", 1)[0]
        assert "status: TODO" in section
