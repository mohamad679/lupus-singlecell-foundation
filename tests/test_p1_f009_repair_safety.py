import csv
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
GEO_TABLE_PATH = REPO_ROOT / "reports" / "tables" / "geo_candidate_datasets.csv"
CELLXGENE_TABLE_PATH = REPO_ROOT / "reports" / "tables" / "cellxgene_candidate_datasets.csv"
STATE_PATH = REPO_ROOT / "state" / "project_state.yaml"
REPORT_PATH = REPO_ROOT / "reports" / "final_dataset_feasibility_report.md"


def read_rows(path: Path):
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def candidate_rows():
    return read_rows(GEO_TABLE_PATH) + read_rows(CELLXGENE_TABLE_PATH)


def test_all_candidate_rows_remain_pending_audit():
    rows = candidate_rows()

    assert rows
    assert all(row["audit_status"] == "candidate_pending_audit" for row in rows)


def test_all_candidate_rows_have_source_urls_in_notes():
    rows = candidate_rows()

    assert all(row["notes"].startswith("Source: https://") for row in rows)

    expected_sources = {
        "GSE162577": "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE162577",
        "GSE137029": "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE137029",
        "GSE174188": "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE174188",
        "436154da-bcf1-4130-9c8b-120ff9a888f2": (
            "https://cellxgene.cziscience.com/collections/"
            "436154da-bcf1-4130-9c8b-120ff9a888f2"
        ),
    }

    for row in rows:
        candidate_key = row.get("accession") or row.get("collection_id")
        assert expected_sources[candidate_key] in row["notes"]


def test_candidate_rows_do_not_mark_training_or_external_validation_approved():
    unsafe_values = {"yes", "approved", "external_validation_ready", "training_ready"}
    usability_fields = {
        "training_usability",
        "training_usable",
        "external_validation_usability",
        "external_validation_usable",
        "external_validation_suitability",
        "decision",
    }

    for row in candidate_rows():
        for field in usability_fields.intersection(row):
            assert row[field].strip().lower() not in unsafe_values


def test_project_state_has_no_selected_datasets_and_gate_remains_pending():
    state = STATE_PATH.read_text()

    assert "selected_datasets: []" in state
    assert "label: \"Human Gate 1: Dataset Feasibility Approved\"" in state
    assert "status: PENDING" in state


def test_report_has_candidate_provenance_caution_section():
    report = REPORT_PATH.read_text()

    assert "## Candidate Provenance and Caution Notes" in report
    assert "Patient-level usability is unresolved" in report or "patient-level" in report
    assert "not approved" in report.lower()
