import csv
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
TABLE_DIR = REPO_ROOT / "reports" / "tables"
SUMMARY_PATH = TABLE_DIR / "metadata_evidence_expansion_summary.csv"
EVIDENCE_PATH = TABLE_DIR / "metadata_inspection_evidence_log.csv"
REPORT_PATH = (
    REPO_ROOT
    / "state"
    / "judge_reports"
    / "P3-F018_metadata_evidence_expansion_report.md"
)
GATE_PATH = REPO_ROOT / "state" / "modeling_readiness_gate.yaml"
STATE_PATH = REPO_ROOT / "state" / "project_state.yaml"
BACKLOG_PATH = REPO_ROOT / "state" / "backlog.yaml"

CELLXGENE_ID = (
    "CELLxGENE_HCA_436154da-bcf1-4130-9c8b-120ff9a888f2_"
    "218acb0f-9f2f-4f76-b90b-15a4b7c7f629"
)
SUMMARY_COLUMNS = [
    "candidate_id",
    "evidence_area",
    "previous_status",
    "expanded_status",
    "evidence_source",
    "decision",
    "remaining_blocker",
    "recommended_next_action",
    "audit_status",
]
EXPECTED_AREAS = {
    ("GSE137029", "patient/donor mapping"),
    ("GSE137029", "sample-label linkage"),
    ("GSE137029", "patient-level diagnosis labels"),
    (CELLXGENE_ID, "donor-label linkage"),
    (CELLXGENE_ID, "sample metadata"),
    ("GSE137029::CELLxGENE_HCA", "GEO/CELLxGENE overlap"),
    (CELLXGENE_ID, "external validation feasibility"),
}


def read_table(path):
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames, list(reader)


def test_expansion_artifacts_and_required_rows_exist():
    assert REPORT_PATH.exists()
    assert SUMMARY_PATH.exists()

    fieldnames, rows = read_table(SUMMARY_PATH)
    assert fieldnames == SUMMARY_COLUMNS
    assert len(rows) == 7
    assert {(row["candidate_id"], row["evidence_area"]) for row in rows} == (
        EXPECTED_AREAS
    )
    assert all(row["audit_status"] == "metadata_expansion_reviewed" for row in rows)


def test_expansion_separates_verified_metadata_from_readiness():
    rows = {
        (row["candidate_id"], row["evidence_area"]): row
        for row in read_table(SUMMARY_PATH)[1]
    }

    assert rows[("GSE137029", "patient/donor mapping")]["expanded_status"] == (
        "blocked"
    )
    assert rows[("GSE137029", "sample-label linkage")]["expanded_status"] == (
        "verified_sample_level_only"
    )
    assert rows[("GSE137029", "patient-level diagnosis labels")][
        "expanded_status"
    ] == "blocked"
    assert rows[(CELLXGENE_ID, "donor-label linkage")]["expanded_status"] == (
        "verified"
    )
    assert rows[(CELLXGENE_ID, "sample metadata")]["expanded_status"] == "verified"
    assert rows[("GSE137029::CELLxGENE_HCA", "GEO/CELLxGENE overlap")][
        "expanded_status"
    ] == "blocked"
    assert rows[(CELLXGENE_ID, "external validation feasibility")][
        "expanded_status"
    ] == "blocked"


def test_expanded_evidence_is_source_backed_and_not_guessed():
    _, rows = read_table(EVIDENCE_PATH)
    expanded = [row for row in rows if row["evidence_id"].startswith("P3F018-E")]

    assert len(expanded) == 7
    assert {row["evidence_id"] for row in expanded} == {
        f"P3F018-E{number:03d}" for number in range(19, 26)
    }
    assert all(row["evidence_source"].startswith("https://") for row in expanded)
    assert all(row["verification_status"] in {"verified", "blocked"} for row in expanded)
    assert all(row["audit_status"] == "metadata_evidence_expanded" for row in expanded)

    for row in expanded:
        combined = " ".join(row.values()).lower()
        assert "guessed" not in combined
        assert "assumed patient" not in combined
        assert "assumed donor" not in combined


def test_readiness_gate_stays_locked_and_pivot_is_not_activated():
    gate = json.loads(GATE_PATH.read_text())
    decision = gate["evidence_expansion_decision"]

    assert gate["modeling_readiness"] == "not_ready"
    assert gate["training_permission"] == "blocked"
    assert gate["allow_modeling"] is False
    assert gate["training_allowed"] is False
    assert gate["phase_4_allowed"] is False
    assert decision["gse137029_patient_mapping"] == "blocked"
    assert decision["cellxgene_hca_donor_label_mapping"] == "verified"
    assert decision["cross_repository_overlap"] == "blocked"
    assert decision["external_validation"] == "blocked"
    assert decision["prepare_pivot_gate"] is True
    assert decision["pivot_status"] == "not_activated"


def test_project_state_and_backlog_do_not_start_modeling_or_phase4():
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

    assert "current_feature: STAGE4-F001" in state
    assert "modeling_readiness: not_ready" in state
    assert "training_permission: blocked" in state
    assert "allow_modeling: false" in state
    assert "selected_datasets: []" in state
    assert "external_validation_cohort: TODO" in state
    assert "phase4_permission: real_artifact_validation_only" in state
    assert 'current_phase: "Phase 4"' not in state
    assert "current_feature: STAGE4-F001" in state
    assert "phase_4_scaffold:" not in backlog
    assert "completed_through: P3-F019" in backlog
    assert artifacts == []

    p3_f019 = backlog.split("feature_id: P3-F019", 1)[1].split(
        "feature_id: P3-F020", 1
    )[0]
    p3_f020 = backlog.split("feature_id: P3-F020", 1)[1]
    assert "status: done" in p3_f019
    assert "status: TODO" in p3_f020
