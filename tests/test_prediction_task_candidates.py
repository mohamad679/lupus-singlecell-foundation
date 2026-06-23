import csv
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = REPO_ROOT / "docs" / "07_prediction_task_plan.md"
SCHEMA_PATH = REPO_ROOT / "metadata" / "prediction_task_schema.yaml"
TABLE_PATH = REPO_ROOT / "reports" / "tables" / "prediction_task_candidates.csv"
CHECKLIST_PATH = REPO_ROOT / "state" / "human_gate_2_checklist.yaml"
STATE_PATH = REPO_ROOT / "state" / "project_state.yaml"

REQUIRED_FIELDS = [
    "task_id",
    "task_name",
    "target_label",
    "label_source",
    "patient_level_required",
    "cross_cohort_possible",
    "external_validation_possible",
    "uncertainty_required",
    "biological_interpretation_required",
    "main_blockers",
    "status",
]
EXPECTED_TASKS = {
    "SLE diagnosis",
    "Disease activity prediction",
    "Flare prediction",
    "Lupus nephritis prediction",
}
VALID_STATUSES = {"feasible", "partially_feasible", "blocked"}
REQUIRED_GATE_CHECKS = {
    "label_availability",
    "patient_identifiers",
    "cross_cohort_feasibility",
    "external_validation_feasibility",
    "biological_interpretation_feasibility",
    "uncertainty_feasibility",
}


def test_prediction_task_artifacts_exist():
    assert DOC_PATH.exists()
    assert SCHEMA_PATH.exists()
    assert TABLE_PATH.exists()
    assert CHECKLIST_PATH.exists()


def test_prediction_task_schema_has_required_fields_and_statuses():
    schema = json.loads(SCHEMA_PATH.read_text())

    assert schema["required_fields"] == REQUIRED_FIELDS
    assert set(schema["fields"]) == set(REQUIRED_FIELDS)
    assert set(schema["allowed_statuses"]) == VALID_STATUSES
    assert "approved" not in schema["allowed_statuses"]


def test_prediction_task_table_has_four_unapproved_candidates():
    with TABLE_PATH.open(newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)

    assert reader.fieldnames == REQUIRED_FIELDS
    assert len(rows) == 4
    assert {row["task_name"] for row in rows} == EXPECTED_TASKS
    assert {row["status"] for row in rows} <= VALID_STATUSES
    assert all(row["status"] != "approved" for row in rows)
    assert all(row["main_blockers"] for row in rows)
    assert all(row["label_source"] for row in rows)


def test_human_gate_2_checklist_preserves_pending_evidence_checks():
    checklist = json.loads(CHECKLIST_PATH.read_text())

    assert checklist["overall_status"] == "approved_with_restrictions"
    assert checklist["automatic_approval_allowed"] is False
    assert set(checklist["checks"]) == REQUIRED_GATE_CHECKS
    assert all(
        check["status"] == "pending" for check in checklist["checks"].values()
    )
    assert checklist["decision"] == "approved_with_restrictions"
    assert checklist["primary_task"] == "SLE diagnosis / case-control prediction"


def test_project_state_preserves_phase2_safety_locks():
    state = STATE_PATH.read_text()

    assert 'current_phase: "Phase 3"' in state
    assert "current_feature: P3-F002" in state
    assert 'primary_task: "SLE diagnosis / case-control prediction"' in state
    assert "selected_datasets: []" in state
    assert "external_validation_cohort: TODO" in state
    assert "allow_downloads: false" in state
    assert "allow_modeling: false" in state
    assert "human_gate_2: approved_with_restrictions" in state
