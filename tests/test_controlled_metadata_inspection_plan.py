import csv
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = REPO_ROOT / "docs" / "12_controlled_metadata_inspection_plan.md"
TARGETS_PATH = (
    REPO_ROOT / "reports" / "tables" / "controlled_metadata_inspection_targets.csv"
)
EVIDENCE_LOG_PATH = (
    REPO_ROOT / "reports" / "tables" / "metadata_inspection_evidence_log.csv"
)
INSPECTION_GATE_PATH = REPO_ROOT / "state" / "metadata_inspection_gate.yaml"
READINESS_GATE_PATH = REPO_ROOT / "state" / "modeling_readiness_gate.yaml"
STATE_PATH = REPO_ROOT / "state" / "project_state.yaml"
BACKLOG_PATH = REPO_ROOT / "state" / "backlog.yaml"

CELLXGENE_ID = (
    "CELLxGENE_HCA_436154da-bcf1-4130-9c8b-120ff9a888f2_"
    "218acb0f-9f2f-4f76-b90b-15a4b7c7f629"
)
TARGET_COLUMNS = [
    "target_id",
    "candidate_id",
    "source",
    "inspection_target",
    "allowed_action",
    "forbidden_action",
    "required_evidence",
    "expected_output",
    "risk_level",
    "status",
    "audit_status",
    "notes",
]
EVIDENCE_COLUMNS = [
    "evidence_id",
    "target_id",
    "candidate_id",
    "evidence_type",
    "evidence_value",
    "evidence_source",
    "supports_requirement",
    "verification_status",
    "verified_by",
    "notes",
    "audit_status",
]
EXPECTED_TARGETS = {
    "GSE137029 GEO metadata page",
    "GSE137029 supplementary file list",
    "GSE137029 SRA Run metadata page or metadata-only manifest",
    "GSE137029 linked publication metadata",
    "CELLxGENE collection metadata page",
    "CELLxGENE dataset metadata fields",
    "HCA project metadata page",
    "CELLxGENE/HCA donor/sample metadata field list",
    "GEO/CELLxGENE overlap reconciliation",
}


def read_table(path):
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames, list(reader)


def test_controlled_inspection_artifacts_exist():
    assert DOC_PATH.exists()
    assert TARGETS_PATH.exists()
    assert EVIDENCE_LOG_PATH.exists()
    assert INSPECTION_GATE_PATH.exists()


def test_inspection_targets_are_complete_and_metadata_reviewed():
    fieldnames, rows = read_table(TARGETS_PATH)

    assert fieldnames == TARGET_COLUMNS
    assert len(rows) == 9
    assert {row["inspection_target"] for row in rows} == EXPECTED_TARGETS
    assert all(row["status"] == "reviewed_metadata_only" for row in rows)
    assert all(row["audit_status"] == "metadata_inspection_reviewed" for row in rows)
    assert all(row["allowed_action"].strip() for row in rows)
    assert all(row["forbidden_action"].strip() for row in rows)
    assert all(row["required_evidence"].strip() for row in rows)
    assert all(row["expected_output"].strip() for row in rows)


def test_targets_cover_only_allowed_candidates_and_overlap_record():
    rows = read_table(TARGETS_PATH)[1]
    candidate_ids = {row["candidate_id"] for row in rows}

    assert "GSE137029" in candidate_ids
    assert CELLXGENE_ID in candidate_ids
    assert "GSE137029::CELLxGENE_HCA" in candidate_ids
    assert all("download" not in row["allowed_action"].lower() for row in rows)


def test_evidence_log_preserves_schema_and_contains_review_evidence():
    fieldnames, rows = read_table(EVIDENCE_LOG_PATH)

    assert fieldnames == EVIDENCE_COLUMNS
    assert len(rows) == 18
    assert {row["verification_status"] for row in rows} <= {
        "verified",
        "unclear",
        "blocked",
        "pending",
    }


def test_metadata_inspection_gate_is_restricted_and_pending():
    gate = json.loads(INSPECTION_GATE_PATH.read_text())

    assert gate["inspection_gate_status"] == "reviewed_with_blockers"
    assert gate["allow_metadata_only_inspection"] is True
    assert gate["allow_full_data_download"] is False
    assert gate["allow_preprocessing"] is False
    assert gate["allow_modeling"] is False
    assert gate["training_permission"] == "blocked"
    assert gate["phase_4_allowed"] is False
    assert set(gate["allowed_candidates"]) == {"GSE137029", CELLXGENE_ID}
    assert gate["required_outputs_before_training"] == [
        "verified_patient_or_donor_ids",
        "verified_label_provenance",
        "verified_split_manifest_feasibility",
        "verified_no_overlap_or_documented_overlap",
        "verified_qc_feasibility",
        "verified_feature_manifest_feasibility",
    ]


def test_modeling_readiness_gate_references_inspection_plan_and_stays_locked():
    gate = json.loads(READINESS_GATE_PATH.read_text())

    assert (
        gate["controlled_metadata_inspection_plan"]
        == "docs/12_controlled_metadata_inspection_plan.md"
    )
    assert gate["metadata_inspection_gate"] == "state/metadata_inspection_gate.yaml"
    assert (
        gate["metadata_inspection_targets"]
        == "reports/tables/controlled_metadata_inspection_targets.csv"
    )
    assert (
        gate["metadata_inspection_evidence_log"]
        == "reports/tables/metadata_inspection_evidence_log.csv"
    )
    assert gate["modeling_readiness"] == "not_ready"
    assert gate["training_permission"] == "blocked"
    assert gate["allow_modeling"] is False
    assert gate["training_allowed"] is False
    assert gate["phase_4_allowed"] is False


def test_project_state_remains_unassigned_and_phase4_not_started():
    state = STATE_PATH.read_text()
    backlog = BACKLOG_PATH.read_text()

    assert 'current_phase: "Phase 3"' in state
    assert "current_feature: P3-F017" in state
    assert "modeling_readiness: not_ready" in state
    assert "training_permission: blocked" in state
    assert "allow_modeling: false" in state
    assert "selected_datasets: []" in state
    assert "external_validation_cohort: TODO" in state
    assert 'current_phase: "Phase 4"' not in state
    assert "current_feature: P4-" not in state
    assert "phase_4_scaffold:" not in backlog
    assert "completed_through: P3-F017" in backlog
    assert "feature_id: P3-F014" in backlog


def test_later_phase3_features_remain_todo():
    backlog = BACKLOG_PATH.read_text()

    for feature_id in ("P3-F018", "P3-F019"):
        marker = f"feature_id: {feature_id}"
        assert marker in backlog
        section = backlog.split(marker, 1)[1].split("\n  - id:", 1)[0]
        assert "status: TODO" in section
