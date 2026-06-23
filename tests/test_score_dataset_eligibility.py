import csv
import importlib.util
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPO_ROOT / "metadata" / "dataset_eligibility_scoring.yaml"
GEO_TABLE_PATH = REPO_ROOT / "reports" / "tables" / "geo_candidate_datasets.csv"
CELLXGENE_TABLE_PATH = REPO_ROOT / "reports" / "tables" / "cellxgene_candidate_datasets.csv"
SCORE_TABLE_PATH = REPO_ROOT / "reports" / "tables" / "dataset_eligibility_scores.csv"
SCRIPT_PATH = REPO_ROOT / "scripts" / "03_score_dataset_eligibility.py"


def load_scoring_module():
    spec = importlib.util.spec_from_file_location("score_dataset_eligibility", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def read_rows(path: Path):
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def read_header(path: Path):
    with path.open(newline="") as handle:
        return next(csv.reader(handle))


def write_table(path: Path, header, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=header)
        writer.writeheader()
        writer.writerows(rows)


def test_score_csv_exists_with_correct_headers():
    module = load_scoring_module()

    assert SCORE_TABLE_PATH.exists()
    assert read_header(SCORE_TABLE_PATH) == module.DEFAULT_OUTPUT_COLUMNS


def test_score_script_creates_header_only_output_for_empty_candidates(tmp_path):
    module = load_scoring_module()
    geo_path = tmp_path / "geo_candidate_datasets.csv"
    cellxgene_path = tmp_path / "cellxgene_candidate_datasets.csv"
    output_path = tmp_path / "dataset_eligibility_scores.csv"
    write_table(geo_path, read_header(GEO_TABLE_PATH), [])
    write_table(cellxgene_path, read_header(CELLXGENE_TABLE_PATH), [])

    module.run_scoring(
        SCHEMA_PATH,
        geo_path,
        cellxgene_path,
        output_path,
    )

    assert read_header(output_path) == module.DEFAULT_OUTPUT_COLUMNS
    assert read_rows(output_path) == []


def test_score_script_does_not_invent_rows(tmp_path):
    module = load_scoring_module()
    output_path = tmp_path / "dataset_eligibility_scores.csv"
    expected_count = len(read_rows(GEO_TABLE_PATH)) + len(read_rows(CELLXGENE_TABLE_PATH))

    module.run_scoring(
        SCHEMA_PATH,
        GEO_TABLE_PATH,
        CELLXGENE_TABLE_PATH,
        output_path,
    )

    rows = read_rows(output_path)
    assert len(rows) == expected_count
    assert all(row["score_status"] == "not_scored_pending_manual_audit" for row in rows)
    assert all(row["eligibility_category"] == "TODO" for row in rows)


def test_unaudited_candidates_are_not_scored_as_eligible(tmp_path):
    module = load_scoring_module()
    geo_path = tmp_path / "geo_candidate_datasets.csv"
    cellxgene_path = tmp_path / "cellxgene_candidate_datasets.csv"
    output_path = tmp_path / "dataset_eligibility_scores.csv"

    geo_header = read_header(GEO_TABLE_PATH)
    cellxgene_header = read_header(CELLXGENE_TABLE_PATH)
    write_table(
        geo_path,
        geo_header,
        [
            {
                "accession": "TEST_ONLY_NOT_A_DATASET",
                "audit_status": "candidate_pending_audit",
            }
        ],
    )
    write_table(cellxgene_path, cellxgene_header, [])

    module.run_scoring(SCHEMA_PATH, geo_path, cellxgene_path, output_path)

    rows = read_rows(output_path)
    assert len(rows) == 1
    assert rows[0]["total_score"] == "TODO"
    assert rows[0]["eligibility_category"] == "TODO"
    assert rows[0]["score_status"] == "not_scored_pending_manual_audit"
    assert rows[0]["training_usable"] == "TODO"


def test_manual_verified_row_requires_hard_rejection_fields(tmp_path):
    module = load_scoring_module()
    geo_path = tmp_path / "geo_candidate_datasets.csv"
    cellxgene_path = tmp_path / "cellxgene_candidate_datasets.csv"
    output_path = tmp_path / "dataset_eligibility_scores.csv"

    geo_header = read_header(GEO_TABLE_PATH)
    cellxgene_header = read_header(CELLXGENE_TABLE_PATH)
    write_table(
        geo_path,
        geo_header,
        [
            {
                "accession": "TEST_ONLY_NOT_A_DATASET",
                "audit_status": "manual_metadata_verified",
            }
        ],
    )
    write_table(cellxgene_path, cellxgene_header, [])

    with pytest.raises(module.EligibilityScoringError, match="missing hard-rejection"):
        module.run_scoring(SCHEMA_PATH, geo_path, cellxgene_path, output_path)


def test_score_script_has_no_network_or_process_clients():
    source = SCRIPT_PATH.read_text()

    forbidden_fragments = [
        "requests",
        "urllib",
        "http.client",
        "ftplib",
        "socket",
        "subprocess",
        "curl",
        "wget",
    ]

    for fragment in forbidden_fragments:
        assert fragment not in source
