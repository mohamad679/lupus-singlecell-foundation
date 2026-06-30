import csv
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
TABLE_DIR = REPO_ROOT / "reports" / "tables"
EVIDENCE_PATH = TABLE_DIR / "metadata_inspection_evidence_log.csv"
DATASET_PATH = TABLE_DIR / "dataset_selection_verification.csv"
LABEL_PATH = TABLE_DIR / "label_provenance_verification.csv"
PATIENT_PATH = TABLE_DIR / "patient_id_verification.csv"
REPORT_PATH = (
    REPO_ROOT
    / "state"
    / "judge_reports"
    / "P3-F015_dataset_label_evidence_review.md"
)
GATE_PATH = REPO_ROOT / "state" / "metadata_inspection_gate.yaml"
STATE_PATH = REPO_ROOT / "state" / "project_state.yaml"
BACKLOG_PATH = REPO_ROOT / "state" / "backlog.yaml"

CELLXGENE_ID = (
    "CELLxGENE_HCA_436154da-bcf1-4130-9c8b-120ff9a888f2_"
    "218acb0f-9f2f-4f76-b90b-15a4b7c7f629"
)
ALLOWED_STATUSES = {"verified", "unclear", "blocked", "pending"}


def read_rows(path):
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def test_review_artifacts_and_evidence_exist():
    assert EVIDENCE_PATH.exists()
    assert REPORT_PATH.exists()

    rows = read_rows(EVIDENCE_PATH)
    assert len(rows) == 25
    assert {row["verification_status"] for row in rows} <= ALLOWED_STATUSES
    assert all(
        row["evidence_id"].startswith(("P3F015-E", "P3F018-E"))
        for row in rows
    )
    assert all(row["evidence_source"].strip() for row in rows)
    assert all(row["verified_by"].strip() for row in rows)
    assert {
        row["audit_status"] for row in rows
    } <= {"metadata_evidence_reviewed", "metadata_evidence_expanded"}


def test_verified_evidence_has_authoritative_url_and_no_guess_language():
    rows = read_rows(EVIDENCE_PATH)
    verified = [row for row in rows if row["verification_status"] == "verified"]

    assert verified
    assert all("https://" in row["evidence_source"] for row in verified)
    for row in rows:
        combined = " ".join(row.values()).lower()
        assert "guessed" not in combined
        assert "assumed patient" not in combined
        assert "assumed donor" not in combined


def test_training_critical_gse_linkage_and_cross_cohort_independence_remain_blocked():
    dataset_rows = read_rows(DATASET_PATH)
    label_rows = read_rows(LABEL_PATH)
    patient_rows = read_rows(PATIENT_PATH)

    assert any(
        row["candidate_id"] == "GSE137029"
        and row["requirement"] == "primary training candidate suitability"
        and row["evidence_status"] == "blocked"
        for row in dataset_rows
    )
    assert any(
        row["candidate_id"] == CELLXGENE_ID
        and row["requirement"] == "independent cohort status"
        and row["evidence_status"] == "blocked"
        for row in dataset_rows
    )
    assert any(
        row["candidate_id"] == "GSE137029"
        and row["requirement"] == "patient or donor linkage to diagnosis label"
        and row["evidence_status"] == "blocked"
        for row in label_rows
    )
    assert any(
        row["candidate_id"] == CELLXGENE_ID
        and row["requirement"] == "donor to sample and diagnosis linkage"
        and row["evidence_status"] == "verified"
        for row in patient_rows
    )
    assert any(
        row["candidate_id"] == CELLXGENE_ID
        and row["requirement"] == "cross-source donor overlap with GSE137029"
        and row["evidence_status"] == "blocked"
        for row in patient_rows
    )


def test_narrow_metadata_facts_are_separated_from_patient_readiness():
    evidence_rows = read_rows(EVIDENCE_PATH)
    label_rows = read_rows(LABEL_PATH)

    assert any(
        row["evidence_type"] == "sample_label_field"
        and row["verification_status"] == "verified"
        for row in evidence_rows
    )
    assert any(
        row["evidence_type"] == "donor_id_field"
        and row["verification_status"] == "verified"
        for row in evidence_rows
    )
    assert any(
        row["candidate_id"] == "GSE137029"
        and row["requirement"] == "exact diagnosis label field and observed values"
        and row["evidence_status"] == "verified"
        for row in label_rows
    )
    assert any(
        row["candidate_id"] == "GSE137029"
        and row["requirement"] == "patient or donor linkage to diagnosis label"
        and row["evidence_status"] == "blocked"
        for row in label_rows
    )


def test_gate_and_project_state_keep_training_blocked():
    gate = json.loads(GATE_PATH.read_text())
    state = STATE_PATH.read_text()

    assert gate["inspection_gate_status"] == "reviewed_with_blockers"
    assert gate["allow_full_data_download"] is False
    assert gate["allow_preprocessing"] is False
    assert gate["allow_modeling"] is False
    assert gate["training_permission"] == "blocked"
    assert "current_feature: STAGE3-F001" in state
    assert "modeling_readiness: not_ready" in state
    assert "training_permission: blocked" in state
    assert "allow_modeling: false" in state
    assert "selected_datasets: []" in state
    assert "external_validation_cohort: TODO" in state


def test_phase4_not_started_and_no_model_artifacts():
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

    assert 'current_phase: "Phase 4"' not in state
    assert "current_feature: P4-" not in state
    assert "phase_4_scaffold:" not in backlog
    assert "completed_through: P3-F019" in backlog
    assert artifacts == []
