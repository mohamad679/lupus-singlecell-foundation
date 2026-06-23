import csv
import importlib.util
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPO_ROOT / "metadata" / "patient_metadata_schema.yaml"
AUDIT_TABLE_PATH = REPO_ROOT / "reports" / "tables" / "patient_metadata_audit.csv"
SCRIPT_PATH = REPO_ROOT / "scripts" / "04_patient_metadata_audit.py"


def load_patient_module():
    spec = importlib.util.spec_from_file_location("patient_metadata_audit", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def read_header(path: Path):
    with path.open(newline="") as handle:
        return next(csv.reader(handle))


def read_rows(path: Path):
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def write_rows(path: Path, header, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=header)
        writer.writeheader()
        writer.writerows(rows)


def test_patient_metadata_audit_csv_exists_with_correct_header():
    module = load_patient_module()

    assert AUDIT_TABLE_PATH.exists()
    assert read_header(AUDIT_TABLE_PATH) == module.REQUIRED_FIELDS


def test_patient_metadata_audit_script_creates_headers(tmp_path):
    module = load_patient_module()
    output_path = tmp_path / "patient_metadata_audit.csv"

    module.run_audit(SCHEMA_PATH, output_path)

    assert read_header(output_path) == module.REQUIRED_FIELDS
    assert read_rows(output_path) == []


def test_patient_metadata_audit_script_does_not_invent_rows(tmp_path):
    module = load_patient_module()
    output_path = tmp_path / "patient_metadata_audit.csv"

    module.run_audit(SCHEMA_PATH, output_path)

    assert read_rows(output_path) == []


def test_missing_patient_id_is_rejected(tmp_path):
    module = load_patient_module()
    output_path = tmp_path / "patient_metadata_audit.csv"
    write_rows(
        output_path,
        module.REQUIRED_FIELDS,
        [{"patient_id": "", "audit_status": "candidate_pending_audit"}],
    )

    with pytest.raises(module.PatientMetadataAuditError, match="missing patient_id"):
        module.run_audit(SCHEMA_PATH, output_path)


def test_audit_status_is_required_if_rows_exist(tmp_path):
    module = load_patient_module()
    output_path = tmp_path / "patient_metadata_audit.csv"
    write_rows(
        output_path,
        module.REQUIRED_FIELDS,
        [{"patient_id": "TEST_PATIENT_ONLY", "audit_status": ""}],
    )

    with pytest.raises(module.PatientMetadataAuditError, match="missing audit_status"):
        module.run_audit(SCHEMA_PATH, output_path)


def test_unknown_values_are_normalized_to_todo(tmp_path):
    module = load_patient_module()
    output_path = tmp_path / "patient_metadata_audit.csv"
    write_rows(
        output_path,
        module.REQUIRED_FIELDS,
        [
            {
                "patient_id": "TEST_PATIENT_ONLY",
                "audit_status": "candidate_pending_audit",
            }
        ],
    )

    module.run_audit(SCHEMA_PATH, output_path)

    rows = read_rows(output_path)
    assert rows[0]["donor_id"] == "TODO"
    assert rows[0]["disease_label"] == "TODO"


def test_patient_metadata_audit_script_has_no_network_or_process_clients():
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
