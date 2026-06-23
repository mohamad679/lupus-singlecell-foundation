import csv
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
GEO_TABLE_PATH = REPO_ROOT / "reports" / "tables" / "geo_candidate_datasets.csv"
CELLXGENE_TABLE_PATH = REPO_ROOT / "reports" / "tables" / "cellxgene_candidate_datasets.csv"
SCORE_TABLE_PATH = REPO_ROOT / "reports" / "tables" / "dataset_eligibility_scores.csv"
STATE_PATH = REPO_ROOT / "state" / "project_state.yaml"


def read_rows(path: Path):
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def candidate_rows():
    return read_rows(GEO_TABLE_PATH) + read_rows(CELLXGENE_TABLE_PATH)


def test_all_candidate_rows_have_pending_audit_status():
    rows = candidate_rows()

    assert len(rows) == 4
    assert all(row["audit_status"] == "candidate_pending_audit" for row in rows)


def test_all_candidate_notes_contain_source_urls():
    for row in candidate_rows():
        notes = row["notes"]

        assert notes.startswith("Source: https://")
        assert "no full data downloaded" in notes


def test_no_candidate_row_marks_training_or_external_validation_approved():
    unsafe_values = {"approved", "yes", "eligible", "external_validation_ready"}
    guarded_fields = {
        "training_usability",
        "training_usable",
        "external_validation_usability",
        "external_validation_usable",
        "external_validation_suitability",
        "decision",
    }

    for row in candidate_rows():
        for field in guarded_fields.intersection(row):
            assert row[field].strip().lower() not in unsafe_values


def test_score_rows_are_pending_and_not_eligible():
    rows = read_rows(SCORE_TABLE_PATH)

    assert len(rows) == 4
    assert all(row["audit_status"] == "candidate_pending_audit" for row in rows)
    assert all(row["total_score"] == "TODO" for row in rows)
    assert all(row["eligibility_category"] == "TODO" for row in rows)
    assert all(row["training_usable"] == "TODO" for row in rows)
    assert all(row["external_validation_usable"] == "TODO" for row in rows)
    assert all(row["score_status"] == "not_scored_pending_manual_audit" for row in rows)


def test_state_keeps_human_gate_and_dataset_selection_closed():
    state = STATE_PATH.read_text()

    assert "current_feature: P2-F004" in state
    assert "selected_datasets: []" in state
    assert "external_validation_cohort: TODO" in state
    assert "label: \"Human Gate 1: Dataset Feasibility Approved\"" in state
    assert "status: approved_with_restrictions" in state
