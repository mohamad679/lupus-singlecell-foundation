import csv
import importlib.util
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
DICTIONARY_PATH = REPO_ROOT / "metadata" / "label_dictionary.yaml"
SCHEMA_PATH = REPO_ROOT / "metadata" / "label_availability_schema.yaml"
AUDIT_TABLE_PATH = REPO_ROOT / "metadata" / "table_schemas" / "label_availability_audit.csv"
SCRIPT_PATH = REPO_ROOT / "scripts" / "05_label_availability_audit.py"


def load_label_module():
    spec = importlib.util.spec_from_file_location("label_availability_audit", SCRIPT_PATH)
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
        "dataset_id": "TEST_DATASET_ONLY",
        "prediction_task": "diagnosis_case_control_prediction",
        "label_type": "diagnosis",
        "label_provenance": "TEST_METADATA_FIELD_ONLY",
        "cell_level_only": "false",
        "audit_status": "candidate_pending_audit",
    }


def test_label_availability_audit_csv_exists_with_correct_header():
    module = load_label_module()

    assert AUDIT_TABLE_PATH.exists()
    assert read_header(AUDIT_TABLE_PATH) == module.REQUIRED_FIELDS


def test_label_availability_audit_script_creates_headers(tmp_path):
    module = load_label_module()
    output_path = tmp_path / "label_availability_audit.csv"

    module.run_audit(DICTIONARY_PATH, SCHEMA_PATH, output_path)

    assert read_header(output_path) == module.REQUIRED_FIELDS
    assert read_rows(output_path) == []


def test_label_availability_audit_script_does_not_invent_rows(tmp_path):
    module = load_label_module()
    output_path = tmp_path / "label_availability_audit.csv"

    module.run_audit(DICTIONARY_PATH, SCHEMA_PATH, output_path)

    assert read_rows(output_path) == []


def test_audit_status_is_required_if_rows_exist(tmp_path):
    module = load_label_module()
    output_path = tmp_path / "label_availability_audit.csv"
    row = base_row()
    row["audit_status"] = ""
    write_rows(output_path, module.REQUIRED_FIELDS, [row])

    with pytest.raises(module.LabelAvailabilityAuditError, match="missing audit_status"):
        module.run_audit(DICTIONARY_PATH, SCHEMA_PATH, output_path)


def test_label_provenance_is_required_if_rows_exist(tmp_path):
    module = load_label_module()
    output_path = tmp_path / "label_availability_audit.csv"
    row = base_row()
    row["label_provenance"] = ""
    write_rows(output_path, module.REQUIRED_FIELDS, [row])

    with pytest.raises(module.LabelAvailabilityAuditError, match="missing label_provenance"):
        module.run_audit(DICTIONARY_PATH, SCHEMA_PATH, output_path)


def test_dataset_id_prediction_task_and_label_type_are_required(tmp_path):
    module = load_label_module()

    for field in ["dataset_id", "prediction_task", "label_type"]:
        output_path = tmp_path / f"{field}.csv"
        row = base_row()
        row[field] = ""
        write_rows(output_path, module.REQUIRED_FIELDS, [row])

        with pytest.raises(module.LabelAvailabilityAuditError, match=f"missing {field}"):
            module.run_audit(DICTIONARY_PATH, SCHEMA_PATH, output_path)


def test_cell_level_only_labels_are_rejected_for_patient_level_prediction(tmp_path):
    module = load_label_module()
    output_path = tmp_path / "label_availability_audit.csv"
    row = base_row()
    row["cell_level_only"] = "true"
    write_rows(output_path, module.REQUIRED_FIELDS, [row])

    with pytest.raises(module.LabelAvailabilityAuditError, match="cell_level_only"):
        module.run_audit(DICTIONARY_PATH, SCHEMA_PATH, output_path)


def test_unknown_values_are_normalized_to_todo(tmp_path):
    module = load_label_module()
    output_path = tmp_path / "label_availability_audit.csv"
    write_rows(output_path, module.REQUIRED_FIELDS, [base_row()])

    module.run_audit(DICTIONARY_PATH, SCHEMA_PATH, output_path)

    rows = read_rows(output_path)
    assert rows[0]["source"] == "TODO"
    assert rows[0]["activity_score_name"] == "TODO"


def test_label_availability_audit_script_has_no_network_or_process_clients():
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
