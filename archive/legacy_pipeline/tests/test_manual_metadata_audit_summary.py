import csv
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SUMMARY_PATH = REPO_ROOT / "reports" / "tables" / "manual_metadata_audit_summary.csv"

EXPECTED_CANDIDATES = {
    "GSE162577",
    "GSE137029",
    "GSE174188",
    "436154da-bcf1-4130-9c8b-120ff9a888f2::218acb0f-9f2f-4f76-b90b-15a4b7c7f629",
}

REQUIRED_COLUMNS = [
    "candidate_id",
    "source",
    "verified_single_cell",
    "verified_human",
    "verified_sle_or_lupus",
    "verified_tissue",
    "verified_patient_or_donor_count",
    "patient_id_status",
    "label_status",
    "activity_label_status",
    "processed_object_status",
    "access_risk",
    "training_risk",
    "external_validation_risk",
    "next_action",
    "audit_status",
]


def read_rows(path: Path):
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def test_manual_metadata_audit_summary_exists():
    assert SUMMARY_PATH.exists()


def test_manual_metadata_audit_summary_has_required_columns():
    with SUMMARY_PATH.open(newline="") as handle:
        reader = csv.reader(handle)
        header = next(reader)

    assert header == REQUIRED_COLUMNS


def test_manual_metadata_audit_summary_has_one_row_per_known_candidate():
    rows = read_rows(SUMMARY_PATH)

    assert {row["candidate_id"] for row in rows} == EXPECTED_CANDIDATES


def test_manual_metadata_audit_summary_rows_remain_pending():
    rows = read_rows(SUMMARY_PATH)

    assert rows
    assert all(row["audit_status"] == "candidate_pending_audit" for row in rows)


def test_manual_metadata_audit_summary_has_no_approval_language_in_status_fields():
    unsafe_values = {
        "approved",
        "eligible",
        "external_validation_ready",
        "training_ready",
    }
    status_fields = [
        "audit_status",
        "training_risk",
        "external_validation_risk",
        "next_action",
    ]

    for row in read_rows(SUMMARY_PATH):
        for field in status_fields:
            assert row[field].strip().lower() not in unsafe_values
