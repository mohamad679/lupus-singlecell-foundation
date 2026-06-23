import csv
import importlib.util
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
CRITERIA_PATH = REPO_ROOT / "metadata" / "external_validation_criteria.yaml"
TABLE_PATH = REPO_ROOT / "reports" / "tables" / "external_validation_candidates.csv"
SCRIPT_PATH = REPO_ROOT / "scripts" / "06_external_validation_audit.py"


def load_external_module():
    spec = importlib.util.spec_from_file_location("external_validation_audit", SCRIPT_PATH)
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


def base_row():
    return {
        "candidate_id": "TEST_CANDIDATE_ONLY",
        "source": "TEST_SOURCE_ONLY",
        "accession_or_collection_id": "TEST_SOURCE_ID_ONLY",
        "decision": "usable_with_caution",
        "audit_status": "candidate_pending_audit",
    }


def ready_row():
    row = base_row()
    row["decision"] = "external_validation_ready"
    for field in [
        "independent_study",
        "compatible_task",
        "compatible_tissue",
        "compatible_assay",
        "patient_id_available",
        "label_compatibility",
        "minimum_patient_count_met",
        "batch_metadata_available",
        "calibration_evaluation_possible",
        "uncertainty_shift_analysis_possible",
        "risk_level",
    ]:
        row[field] = "verified"
    return row


def test_external_validation_candidate_csv_exists_with_correct_headers():
    module = load_external_module()

    assert TABLE_PATH.exists()
    assert read_header(TABLE_PATH) == module.REQUIRED_HEADERS


def test_external_validation_audit_script_creates_headers(tmp_path):
    module = load_external_module()
    output_path = tmp_path / "external_validation_candidates.csv"

    module.run_audit(CRITERIA_PATH, output_path)

    assert read_header(output_path) == module.REQUIRED_HEADERS
    assert read_rows(output_path) == []


def test_external_validation_audit_script_does_not_invent_rows(tmp_path):
    module = load_external_module()
    output_path = tmp_path / "external_validation_candidates.csv"

    module.run_audit(CRITERIA_PATH, output_path)

    assert read_rows(output_path) == []


def test_required_headers_exist():
    module = load_external_module()
    header = read_header(TABLE_PATH)

    for field in module.REQUIRED_HEADERS:
        assert field in header


def test_audit_status_is_required_if_rows_exist(tmp_path):
    module = load_external_module()
    output_path = tmp_path / "external_validation_candidates.csv"
    row = base_row()
    row["audit_status"] = ""
    write_rows(output_path, module.REQUIRED_HEADERS, [row])

    with pytest.raises(module.ExternalValidationAuditError, match="missing audit_status"):
        module.run_audit(CRITERIA_PATH, output_path)


def test_critical_row_fields_are_required(tmp_path):
    module = load_external_module()

    for field in [
        "candidate_id",
        "source",
        "accession_or_collection_id",
        "decision",
    ]:
        output_path = tmp_path / f"{field}.csv"
        row = base_row()
        row[field] = ""
        write_rows(output_path, module.REQUIRED_HEADERS, [row])

        with pytest.raises(module.ExternalValidationAuditError, match=f"missing {field}"):
            module.run_audit(CRITERIA_PATH, output_path)


def test_external_validation_ready_cannot_have_todo_critical_fields(tmp_path):
    module = load_external_module()
    output_path = tmp_path / "external_validation_candidates.csv"
    row = ready_row()
    row["patient_id_available"] = "TODO"
    write_rows(output_path, module.REQUIRED_HEADERS, [row])

    with pytest.raises(module.ExternalValidationAuditError, match="external_validation_ready"):
        module.run_audit(CRITERIA_PATH, output_path)


def test_external_validation_ready_row_can_be_validated_when_resolved(tmp_path):
    module = load_external_module()
    output_path = tmp_path / "external_validation_candidates.csv"
    write_rows(output_path, module.REQUIRED_HEADERS, [ready_row()])

    module.run_audit(CRITERIA_PATH, output_path)

    rows = read_rows(output_path)
    assert rows[0]["decision"] == "external_validation_ready"


def test_external_validation_audit_script_has_no_network_or_process_clients():
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
