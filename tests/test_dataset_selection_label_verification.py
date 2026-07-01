import csv
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = REPO_ROOT / "docs" / "10_dataset_selection_and_label_verification.md"
TABLE_DIR = REPO_ROOT / "reports" / "tables"
DATASET_PATH = TABLE_DIR / "dataset_selection_verification.csv"
LABEL_PATH = TABLE_DIR / "label_provenance_verification.csv"
PATIENT_PATH = TABLE_DIR / "patient_id_verification.csv"
STATE_PATH = REPO_ROOT / "state" / "project_state.yaml"
DECISION_PATH = REPO_ROOT / "state" / "training_permission_decision.yaml"
BACKLOG_PATH = REPO_ROOT / "state" / "backlog.yaml"

CELLXGENE_ID = (
    "CELLxGENE_HCA_436154da-bcf1-4130-9c8b-120ff9a888f2_"
    "218acb0f-9f2f-4f76-b90b-15a4b7c7f629"
)
CANDIDATES = {"GSE137029", CELLXGENE_ID}
REQUIRED_COLUMNS = [
    "candidate_id",
    "requirement",
    "evidence_status",
    "evidence_source",
    "risk_level",
    "blocker",
    "next_action",
    "audit_status",
]
ALLOWED_STATUSES = {"verified", "unclear", "blocked", "pending"}


def read_table(path):
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames, list(reader)


def test_verification_artifacts_exist():
    assert DOC_PATH.exists()
    assert DATASET_PATH.exists()
    assert LABEL_PATH.exists()
    assert PATIENT_PATH.exists()


def test_tables_have_required_schema_and_candidate_scope():
    for path in (DATASET_PATH, LABEL_PATH, PATIENT_PATH):
        fieldnames, rows = read_table(path)

        assert fieldnames == REQUIRED_COLUMNS
        assert rows
        assert {row["candidate_id"] for row in rows} == CANDIDATES
        assert {row["evidence_status"] for row in rows} <= ALLOWED_STATUSES
        assert all(row["evidence_source"].strip() for row in rows)
        assert all(row["next_action"].strip() for row in rows)
        assert all(row["audit_status"].strip() for row in rows)


def test_verified_facts_do_not_approve_a_dataset():
    dataset_rows = read_table(DATASET_PATH)[1]
    combined_rows = []
    for path in (DATASET_PATH, LABEL_PATH, PATIENT_PATH):
        combined_rows.extend(read_table(path)[1])

    assert any(row["evidence_status"] == "verified" for row in combined_rows)
    assert any(
        row["candidate_id"] == "GSE137029"
        and row["requirement"] == "primary training candidate suitability"
        and row["evidence_status"] == "blocked"
        and row["blocker"] == "true"
        for row in dataset_rows
    )
    assert all("approved" not in row["evidence_status"] for row in combined_rows)
    assert all("selected" not in row["audit_status"] for row in combined_rows)


def test_patient_level_labels_and_identifiers_are_not_overclaimed():
    label_rows = read_table(LABEL_PATH)[1]
    patient_rows = read_table(PATIENT_PATH)[1]

    assert any(
        row["candidate_id"] == "GSE137029"
        and row["requirement"] == "patient or donor linkage to diagnosis label"
        and row["evidence_status"] == "blocked"
        for row in label_rows
    )
    assert any(
        row["candidate_id"] == CELLXGENE_ID
        and row["requirement"] == "exact patient-level diagnosis label provenance"
        and row["evidence_status"] == "verified"
        for row in label_rows
    )
    assert any(
        row["candidate_id"] == "GSE137029"
        and row["requirement"] == "exact diagnosis label field and observed values"
        and row["evidence_status"] == "verified"
        for row in label_rows
    )
    assert any(
        row["candidate_id"] == "GSE137029"
        and row["requirement"] == "patient or donor identifier field availability"
        and row["evidence_status"] == "blocked"
        for row in patient_rows
    )
    assert any(
        row["candidate_id"] == CELLXGENE_ID
        and row["requirement"] == "cross-source donor overlap with GSE137029"
        and row["evidence_status"] == "blocked"
        for row in patient_rows
    )


def test_training_and_project_state_remain_locked():
    state = STATE_PATH.read_text()
    decision = json.loads(DECISION_PATH.read_text())

    assert "current_feature: STAGE3-F004" in state
    assert "modeling_readiness: not_ready" in state
    assert "training_permission: blocked" in state
    assert "allow_modeling: false" in state
    assert "selected_datasets: []" in state
    assert "external_validation_cohort: TODO" in state
    assert decision["training_permission"] == "blocked"
    assert decision["allow_modeling"] is False


def test_phase4_not_started_and_p3_f012_recorded():
    state = STATE_PATH.read_text()
    backlog = BACKLOG_PATH.read_text()

    assert 'current_phase: "Phase 4"' not in state
    assert "current_feature: P4-" not in state
    assert "phase_4_scaffold:" not in backlog
    assert "completed_through: P3-F019" in backlog
    assert "feature_id: P3-F012" in backlog
