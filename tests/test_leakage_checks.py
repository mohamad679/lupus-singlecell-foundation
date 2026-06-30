import importlib.util
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / "src" / "data" / "leakage_checks.py"
STATE_PATH = REPO_ROOT / "state" / "project_state.yaml"


def load_module():
    spec = importlib.util.spec_from_file_location("leakage_checks", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def valid_mock_rows():
    return [
        {
            "entity_id": "patient-1",
            "entity_type": "patient_id",
            "patient_id": "patient-1",
            "donor_id": "donor-1",
            "sample_id": "sample-1",
            "cell_id": "cell-1",
            "cohort_id": "cohort-1",
            "batch_id": "batch-1",
            "split": "train",
            "disease_label": "SLE",
            "audit_status": "pending_manual_review",
        },
        {
            "entity_id": "patient-2",
            "entity_type": "patient_id",
            "patient_id": "patient-2",
            "donor_id": "donor-2",
            "sample_id": "sample-2",
            "cell_id": "cell-2",
            "cohort_id": "cohort-1",
            "batch_id": "batch-2",
            "split": "train",
            "disease_label": "control",
            "audit_status": "pending_manual_review",
        },
        {
            "entity_id": "patient-3",
            "entity_type": "patient_id",
            "patient_id": "patient-3",
            "donor_id": "donor-3",
            "sample_id": "sample-3",
            "cell_id": "cell-3",
            "cohort_id": "cohort-1",
            "batch_id": "batch-1",
            "split": "test",
            "disease_label": "SLE",
            "audit_status": "pending_manual_review",
        },
        {
            "entity_id": "patient-4",
            "entity_type": "patient_id",
            "patient_id": "patient-4",
            "donor_id": "donor-4",
            "sample_id": "sample-4",
            "cell_id": "cell-4",
            "cohort_id": "cohort-1",
            "batch_id": "batch-2",
            "split": "test",
            "disease_label": "control",
            "audit_status": "pending_manual_review",
        },
    ]


def test_valid_mock_patient_level_split_passes():
    module = load_module()
    rows = valid_mock_rows()

    module.check_no_cell_level_split(rows)
    module.check_no_patient_overlap(rows)
    module.check_no_donor_overlap(rows)
    module.check_no_sample_overlap(rows)
    module.check_no_duplicate_cell_ids(rows)
    module.check_no_batch_confounding(rows)
    module.check_no_label_leakage(rows)


def test_patient_overlap_fails():
    module = load_module()
    rows = valid_mock_rows()
    rows[2]["patient_id"] = "patient-1"

    with pytest.raises(module.LeakageCheckError, match="patient_id"):
        module.check_no_patient_overlap(rows)


def test_donor_overlap_fails():
    module = load_module()
    rows = valid_mock_rows()
    rows[2]["donor_id"] = "donor-1"

    with pytest.raises(module.LeakageCheckError, match="donor_id"):
        module.check_no_donor_overlap(rows)


def test_sample_overlap_fails():
    module = load_module()
    rows = valid_mock_rows()
    rows[2]["sample_id"] = "sample-1"

    with pytest.raises(module.LeakageCheckError, match="sample_id"):
        module.check_no_sample_overlap(rows)


def test_cell_level_split_fails():
    module = load_module()
    rows = valid_mock_rows()
    rows[0]["entity_type"] = "cell_id"

    with pytest.raises(module.LeakageCheckError, match="cell-level"):
        module.check_no_cell_level_split(rows)


def test_duplicate_cell_ids_fail():
    module = load_module()
    rows = valid_mock_rows()
    rows[2]["cell_id"] = "cell-1"

    with pytest.raises(module.LeakageCheckError, match="duplicated cell_id"):
        module.check_no_duplicate_cell_ids(rows)


def test_cohort_contamination_is_detected():
    module = load_module()
    rows = valid_mock_rows()
    rows[2]["split"] = "external_validation"

    with pytest.raises(module.LeakageCheckError, match="cohort contamination"):
        module.check_no_cohort_contamination(rows)


def test_missing_audit_status_fails():
    module = load_module()
    rows = valid_mock_rows()
    rows[0]["audit_status"] = ""

    result = module.run_all_leakage_checks(rows)

    assert result["status"] == "FAIL"
    assert any("audit_status" in error for error in result["errors"])


def test_batch_confounding_is_detected():
    module = load_module()
    rows = valid_mock_rows()
    rows[1]["batch_id"] = "batch-1"

    with pytest.raises(module.LeakageCheckError, match="batch confounding"):
        module.check_no_batch_confounding(rows)


def test_label_leakage_is_detected():
    module = load_module()
    rows = valid_mock_rows()
    rows[0]["disease_label"] = "SLE"
    rows[1]["disease_label"] = "SLE"
    rows[2]["disease_label"] = "control"
    rows[3]["disease_label"] = "control"

    with pytest.raises(module.LeakageCheckError, match="label leakage"):
        module.check_no_label_leakage(rows)


def test_check_no_overlap_detects_train_test_overlap():
    module = load_module()

    with pytest.raises(module.LeakageCheckError, match="patient"):
        module.check_no_overlap(["patient-1"], ["patient-1"], "patient")


def test_run_all_leakage_checks_returns_pass_for_valid_mock_rows():
    module = load_module()

    result = module.run_all_leakage_checks(valid_mock_rows())

    assert result == {"status": "PASS", "errors": [], "checked_rows": 4}


def test_run_all_leakage_checks_returns_fail_for_invalid_mock_rows():
    module = load_module()
    rows = valid_mock_rows()
    rows[2]["patient_id"] = "patient-1"

    result = module.run_all_leakage_checks(rows)

    assert result["status"] == "FAIL"
    assert any("patient_id" in error for error in result["errors"])


def test_state_remains_locked_for_phase2_scaffold():
    state = STATE_PATH.read_text()

    assert "current_feature: STAGE1-F006" in state
    assert "selected_datasets: []" in state
    assert "external_validation_cohort: TODO" in state
    assert "modeling_allowed: false" in state
    assert "allow_modeling: false" in state
    assert "dataset_download_allowed: false" in state
    assert "allow_downloads: false" in state


def test_leakage_utility_does_not_import_processing_or_modeling_libraries():
    source = MODULE_PATH.read_text().lower()
    forbidden_fragments = [
        "import scanpy",
        "import anndata",
        "from scanpy",
        "from anndata",
        "sklearn",
        "torch",
        "tensorflow",
        "xgboost",
        "lightgbm",
        "requests",
        "urllib",
        "socket",
    ]

    for fragment in forbidden_fragments:
        assert fragment not in source
