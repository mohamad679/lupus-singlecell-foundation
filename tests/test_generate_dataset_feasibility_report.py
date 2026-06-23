import csv
import importlib.util
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "07_generate_dataset_feasibility_report.py"
STATE_PATH = REPO_ROOT / "state" / "project_state.yaml"
REPORT_PATH = REPO_ROOT / "reports" / "final_dataset_feasibility_report.md"


def load_report_module():
    spec = importlib.util.spec_from_file_location(
        "generate_dataset_feasibility_report", SCRIPT_PATH
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def read_rows(path: Path):
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def test_report_generator_script_exists():
    assert SCRIPT_PATH.exists()


def test_report_generator_writes_todo_report_without_inventing_rows(tmp_path):
    module = load_report_module()
    output_path = tmp_path / "final_dataset_feasibility_report.md"
    tracked_tables = [
        module.GEO_CANDIDATES_PATH,
        module.CELLXGENE_CANDIDATES_PATH,
        module.ELIGIBILITY_SCORES_PATH,
        module.LABEL_AUDIT_PATH,
        module.PATIENT_AUDIT_PATH,
        module.EXTERNAL_VALIDATION_PATH,
        module.REJECTED_DATASET_LOG_PATH,
    ]
    before_counts = {path: len(read_rows(path)) for path in tracked_tables}

    module.run_report(output_path, STATE_PATH)

    after_counts = {path: len(read_rows(path)) for path in tracked_tables}
    report = output_path.read_text()

    assert before_counts == after_counts
    assert "TODO" in report
    assert "Human Gate 1 remains PENDING" in report
    assert "None selected" in report


def test_report_generator_cannot_auto_approve_datasets():
    module = load_report_module()

    with pytest.raises(module.DatasetFeasibilityReportError, match="approve"):
        module.validate_no_approvals(
            [("test_table.csv", [{"decision": "approved", "dataset_id": "TEST_ONLY"}])]
        )


def test_human_gate_1_cannot_be_closed_automatically(tmp_path):
    module = load_report_module()
    state_path = tmp_path / "project_state.yaml"
    state_text = STATE_PATH.read_text().replace("status: PENDING", "status: APPROVED", 1)
    state_path.write_text(state_text)

    with pytest.raises(module.DatasetFeasibilityReportError, match="Human Gate 1"):
        module.validate_state_gate_pending(state_path)


def test_external_validation_cohort_must_remain_todo(tmp_path):
    module = load_report_module()
    state_path = tmp_path / "project_state.yaml"
    state_text = STATE_PATH.read_text().replace(
        "external_validation_cohort: TODO",
        "external_validation_cohort: TEST_ONLY",
    )
    state_path.write_text(state_text)

    with pytest.raises(
        module.DatasetFeasibilityReportError, match="external_validation_cohort"
    ):
        module.validate_state_gate_pending(state_path)


def test_report_generator_has_no_network_or_process_clients():
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


def test_existing_report_template_is_not_empty():
    assert REPORT_PATH.read_text().strip()
