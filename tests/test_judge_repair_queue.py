import csv
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
REPAIR_QUEUE_YAML = REPO_ROOT / "state" / "repair_queue.yaml"
REPAIR_QUEUE_CSV = REPO_ROOT / "reports" / "tables" / "judge_repair_queue.csv"
STATE_PATH = REPO_ROOT / "state" / "project_state.yaml"

REQUIRED_BLOCKER_TYPES = {
    "patient_id_availability",
    "label_provenance",
    "activity_label_availability",
    "treatment_metadata",
    "batch_metadata",
    "cell_type_annotation",
    "gene_identifier_feasibility",
    "processed_object_availability",
    "raw_count_availability",
    "data_access_restriction",
    "cohort_overlap_risk",
    "external_validation_uncertainty",
}

ALLOWED_STATUSES = {"unresolved", "pending_manual_review"}


def read_rows(path: Path):
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def test_repair_queue_yaml_exists():
    assert REPAIR_QUEUE_YAML.exists()
    text = REPAIR_QUEUE_YAML.read_text()
    assert "repair_queue:" in text
    assert "repair_id:" in text


def test_judge_repair_queue_csv_exists():
    assert REPAIR_QUEUE_CSV.exists()


def test_repair_rows_exist_and_cover_required_blocker_types():
    rows = read_rows(REPAIR_QUEUE_CSV)

    assert rows
    assert REQUIRED_BLOCKER_TYPES.issubset({row["blocker_type"] for row in rows})


def test_no_repair_is_marked_resolved():
    for row in read_rows(REPAIR_QUEUE_CSV):
        assert row["status"] in ALLOWED_STATUSES
        assert row["status"] != "resolved"


def test_every_repair_has_required_evidence_and_forbidden_actions():
    for row in read_rows(REPAIR_QUEUE_CSV):
        assert row["required_evidence"].strip()
        assert row["forbidden_resolution_actions"].strip()


def test_every_repair_requires_human_gate():
    for row in read_rows(REPAIR_QUEUE_CSV):
        assert row["human_gate_required"] == "true"


def test_project_state_remains_blocked_pending_human_gate():
    state = STATE_PATH.read_text()

    assert "current_feature: STAGE3-F005" in state
    assert "blocked: false" in state
    assert "blocked_reason: null" in state
    assert "selected_datasets: []" in state
    assert "external_validation_cohort: TODO" in state
    assert "Human Gate 1: Dataset Feasibility Approved" in state
    assert "status: approved_with_restrictions" in state
