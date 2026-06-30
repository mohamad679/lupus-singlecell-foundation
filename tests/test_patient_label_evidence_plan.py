import csv
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = (
    REPO_ROOT / "docs" / "11_patient_id_label_provenance_evidence_plan.md"
)
PATIENT_PLAN_PATH = (
    REPO_ROOT / "reports" / "tables" / "patient_donor_id_evidence_plan.csv"
)
LABEL_PLAN_PATH = (
    REPO_ROOT / "reports" / "tables" / "label_provenance_evidence_plan.csv"
)
GATE_PATH = REPO_ROOT / "state" / "modeling_readiness_gate.yaml"
STATE_PATH = REPO_ROOT / "state" / "project_state.yaml"
BACKLOG_PATH = REPO_ROOT / "state" / "backlog.yaml"

CELLXGENE_ID = (
    "CELLxGENE_HCA_436154da-bcf1-4130-9c8b-120ff9a888f2_"
    "218acb0f-9f2f-4f76-b90b-15a4b7c7f629"
)
EXPECTED_CANDIDATES = {"GSE137029", CELLXGENE_ID}
PATIENT_COLUMNS = [
    "candidate_id",
    "source",
    "evidence_item",
    "required_evidence",
    "evidence_source",
    "current_status",
    "blocking",
    "risk_level",
    "next_action",
    "audit_status",
]
LABEL_COLUMNS = [
    "candidate_id",
    "source",
    "prediction_task",
    "label_type",
    "required_label",
    "required_provenance",
    "current_status",
    "blocking",
    "risk_level",
    "next_action",
    "audit_status",
]


def read_table(path):
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames, list(reader)


def test_evidence_plan_artifacts_exist():
    assert DOC_PATH.exists()
    assert PATIENT_PLAN_PATH.exists()
    assert LABEL_PLAN_PATH.exists()


def test_patient_donor_plan_has_required_schema_and_items():
    fieldnames, rows = read_table(PATIENT_PLAN_PATH)

    assert fieldnames == PATIENT_COLUMNS
    assert rows
    assert EXPECTED_CANDIDATES <= {row["candidate_id"] for row in rows}
    required_items = {
        ("GSE137029", "patient/donor ID field"),
        ("GSE137029", "sample-to-patient mapping"),
        ("GSE137029", "case/control label linkage"),
        (CELLXGENE_ID, "donor ID field"),
        (CELLXGENE_ID, "sample ID field"),
        (CELLXGENE_ID, "disease label linkage"),
    }
    observed_items = {
        (row["candidate_id"], row["evidence_item"]) for row in rows
    }

    assert required_items <= observed_items
    assert any(row["evidence_item"] == "cohort overlap check" for row in rows)


def test_no_evidence_plan_row_is_prematurely_verified():
    patient_rows = read_table(PATIENT_PLAN_PATH)[1]
    label_rows = read_table(LABEL_PLAN_PATH)[1]
    rows = patient_rows + label_rows

    assert rows
    assert {row["current_status"] for row in rows} <= {"pending", "blocked"}
    assert all(row["current_status"] != "verified" for row in rows)
    assert all(row["blocking"] == "true" for row in rows)
    assert all(row["evidence_source"].strip() for row in patient_rows)
    assert all(row["required_provenance"].strip() for row in label_rows)
    assert all(row["next_action"].strip() for row in rows)


def test_label_plan_covers_both_candidates_and_required_tasks():
    fieldnames, rows = read_table(LABEL_PLAN_PATH)

    assert fieldnames == LABEL_COLUMNS
    assert {row["candidate_id"] for row in rows} == EXPECTED_CANDIDATES
    diagnosis_rows = [
        row
        for row in rows
        if row["prediction_task"] == "SLE diagnosis / case-control prediction"
    ]

    assert len(diagnosis_rows) == 4
    assert {row["label_type"] for row in diagnosis_rows} == {
        "diagnosis",
        "control_type",
    }
    assert all(
        row["current_status"] in {"pending", "blocked"}
        for row in diagnosis_rows
    )


def test_activity_and_lupus_nephritis_remain_blocked():
    rows = read_table(LABEL_PLAN_PATH)[1]
    blocked_tasks = {
        "disease activity prediction",
        "lupus nephritis prediction",
    }
    task_rows = [
        row for row in rows if row["prediction_task"] in blocked_tasks
    ]

    assert len(task_rows) == 4
    assert {row["prediction_task"] for row in task_rows} == blocked_tasks
    assert all(row["current_status"] == "blocked" for row in task_rows)
    assert all(row["blocking"] == "true" for row in task_rows)


def test_readiness_gate_references_plans_and_remains_locked():
    gate = json.loads(GATE_PATH.read_text())

    assert (
        gate["patient_donor_id_evidence_plan"]
        == "reports/tables/patient_donor_id_evidence_plan.csv"
    )
    assert (
        gate["label_provenance_evidence_plan"]
        == "reports/tables/label_provenance_evidence_plan.csv"
    )
    assert gate["modeling_readiness"] == "not_ready"
    assert gate["training_permission"] == "blocked"
    assert gate["allow_modeling"] is False
    assert gate["training_allowed"] is False
    assert gate["phase_4_allowed"] is False


def test_project_state_remains_unassigned_and_phase4_not_started():
    state = STATE_PATH.read_text()
    backlog = BACKLOG_PATH.read_text()

    assert "current_phase: Stage 1" in state
    assert "current_feature: STAGE1-F002" in state
    assert "modeling_readiness: not_ready" in state
    assert "training_permission: blocked" in state
    assert "allow_modeling: false" in state
    assert "selected_datasets: []" in state
    assert "external_validation_cohort: TODO" in state
    assert 'current_phase: "Phase 4"' not in state
    assert "current_feature: P4-" not in state
    assert "phase_4_scaffold:" not in backlog
    assert "completed_through: P3-F019" in backlog
    assert "feature_id: P3-F013" in backlog
