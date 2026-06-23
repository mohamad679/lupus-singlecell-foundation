import csv
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = REPO_ROOT / "metadata" / "dataset_catalog.csv"

REQUIRED_COLUMNS = [
    "dataset_id",
    "source_name",
    "source_url",
    "accession",
    "organism",
    "disease_context",
    "case_definition",
    "control_definition",
    "tissue_or_sample_type",
    "assay_type",
    "platform",
    "donor_count",
    "sample_count",
    "cell_count",
    "raw_data_available",
    "processed_data_available",
    "clinical_metadata_available",
    "treatment_metadata_available",
    "disease_activity_metadata_available",
    "batch_metadata_available",
    "cell_type_annotations_available",
    "license_or_access_terms",
    "download_status",
    "feasibility_status",
    "feasibility_notes",
    "provenance_notes",
    "last_verified",
]


def test_dataset_catalog_exists():
    assert CATALOG_PATH.exists(), "metadata/dataset_catalog.csv is required"


def test_dataset_catalog_columns_match_schema():
    with CATALOG_PATH.open(newline="") as handle:
        reader = csv.reader(handle)
        header = next(reader)

    assert header == REQUIRED_COLUMNS


def test_catalog_does_not_claim_downloads_or_accessions_before_gate_1():
    with CATALOG_PATH.open(newline="") as handle:
        rows = list(csv.DictReader(handle))

    assert rows, "catalog should include at least one TODO placeholder row"

    for row in rows:
        assert row["download_status"] == "not_downloaded"
        assert row["accession"] == "TODO"
