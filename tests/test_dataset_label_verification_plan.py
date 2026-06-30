import csv
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = REPO_ROOT / "docs" / "09_dataset_label_verification_plan.md"
SCHEMA_PATH = (
    REPO_ROOT / "metadata" / "dataset_label_verification_schema.yaml"
)
CHECKLIST_PATH = (
    REPO_ROOT / "reports" / "tables" / "dataset_label_verification_checklist.csv"
)
GATE_PATH = REPO_ROOT / "state" / "modeling_readiness_gate.yaml"
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
REQUIRED_FIELDS = [
    "verification_id",
    "candidate_id",
    "requirement_type",
    "requirement_description",
    "required_evidence",
    "evidence_source",
    "evidence_status",
    "blocking",
    "verified_by",
    "verification_date",
    "notes",
    "audit_status",
]


def read_rows():
    with CHECKLIST_PATH.open(newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
    return reader.fieldnames, rows


def test_verification_plan_artifacts_exist():
    assert DOC_PATH.exists()
    assert SCHEMA_PATH.exists()
    assert CHECKLIST_PATH.exists()


def test_verification_schema_contains_required_fields_and_blockers():
    schema = json.loads(SCHEMA_PATH.read_text())

    assert schema["required_fields"] == REQUIRED_FIELDS
    assert set(schema["allowed_requirement_types"]) == REQUIRED_BLOCKERS
    assert set(schema["allowed_evidence_statuses"]) == {"pending", "blocked"}
    assert set(schema["fields"]) == set(REQUIRED_FIELDS)


def test_checklist_has_one_unverified_row_per_blocker():
    fieldnames, rows = read_rows()

    assert fieldnames == REQUIRED_FIELDS
    assert len(rows) == len(REQUIRED_BLOCKERS)
    assert {row["requirement_type"] for row in rows} == REQUIRED_BLOCKERS
    assert {row["evidence_status"] for row in rows} <= {"pending", "blocked"}
    assert all(row["blocking"] == "true" for row in rows)
    assert all(row["verified_by"] == "TODO" for row in rows)
    assert all(row["verification_date"] == "TODO" for row in rows)
    assert all(row["evidence_status"] != "verified" for row in rows)


def test_modeling_gate_references_verification_artifacts_and_remains_locked():
    gate = json.loads(GATE_PATH.read_text())

    assert gate["verification_plan"] == "docs/09_dataset_label_verification_plan.md"
    assert (
        gate["verification_schema"]
        == "metadata/dataset_label_verification_schema.yaml"
    )
    assert (
        gate["verification_checklist"]
        == "reports/tables/dataset_label_verification_checklist.csv"
    )
    assert gate["modeling_readiness"] == "not_ready"
    assert gate["allow_modeling"] is False
    assert gate["training_allowed"] is False
    assert gate["phase_4_allowed"] is False


def test_project_state_remains_unassigned_and_training_blocked():
    state = STATE_PATH.read_text()

    assert "current_phase: Stage 2" in state
    assert "current_feature: STAGE2-F001" in state
    assert "modeling_readiness: not_ready" in state
    assert "allow_modeling: false" in state
    assert "training_allowed: false" in state
    assert "selected_datasets: []" in state
    assert "external_validation_cohort: TODO" in state


def test_phase4_is_not_started_and_p3_f011_remains_todo():
    state = STATE_PATH.read_text()
    backlog = BACKLOG_PATH.read_text()

    assert 'current_phase: "Phase 4"' not in state
    assert "current_feature: P4-" not in state
    assert "phase_4_scaffold:" not in backlog
    assert "completed_through: P3-F019" in backlog
    assert "feature_id: P3-F011" in backlog
