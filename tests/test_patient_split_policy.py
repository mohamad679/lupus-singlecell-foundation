import csv
import importlib.util
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPO_ROOT / "configs" / "splitting.yaml"
MANIFEST_PATH = REPO_ROOT / "reports" / "tables" / "split_manifest.csv"
MODULE_PATH = REPO_ROOT / "src" / "data" / "split_policy.py"
STATE_PATH = REPO_ROOT / "state" / "project_state.yaml"


def load_module():
    spec = importlib.util.spec_from_file_location("split_policy", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def valid_mock_rows():
    return [
        {
            "entity_id": "patient-1",
            "entity_type": "patient_id",
            "dataset_id": "GSE137029",
            "cohort_id": "cohort-1",
            "split": "train",
            "disease_label": "SLE",
            "n_cells": "TODO",
            "n_samples": "TODO",
            "audit_status": "pending_manual_review",
            "notes": "mock row only",
        },
        {
            "entity_id": "patient-2",
            "entity_type": "patient_id",
            "dataset_id": "GSE137029",
            "cohort_id": "cohort-1",
            "split": "test",
            "disease_label": "control",
            "n_cells": "TODO",
            "n_samples": "TODO",
            "audit_status": "pending_manual_review",
            "notes": "mock row only",
        },
    ]


def test_splitting_yaml_exists():
    assert CONFIG_PATH.exists()


def test_split_config_forbids_cell_level_splits():
    module = load_module()
    config = module.load_split_config(CONFIG_PATH)

    module.validate_split_config(config)
    split_policy = config["split_policy"]
    assert split_policy["allow_cell_level_split"] is False
    assert "cell_id" in split_policy["forbidden_split_units"]
    assert "barcode" in split_policy["forbidden_split_units"]


def test_split_manifest_csv_exists_with_required_headers_only():
    module = load_module()

    assert MANIFEST_PATH.exists()
    with MANIFEST_PATH.open(newline="") as handle:
        rows = list(csv.reader(handle))

    assert rows == [module.SPLIT_MANIFEST_HEADERS]


def test_reject_cell_level_split_rejects_cell_id():
    module = load_module()

    with pytest.raises(module.SplitPolicyError, match="cell_id"):
        module.reject_cell_level_split("cell_id")


def test_reject_cell_level_split_rejects_barcode():
    module = load_module()

    with pytest.raises(module.SplitPolicyError, match="barcode"):
        module.reject_cell_level_split("barcode")


def test_patient_overlap_between_train_and_test_is_detected():
    module = load_module()

    assert module.detect_patient_overlap(["patient-1", "patient-2"], ["patient-2"]) == [
        "patient-2"
    ]


def test_donor_overlap_between_train_and_test_is_detected():
    module = load_module()

    assert module.detect_donor_overlap(["donor-1"], ["donor-1", "donor-2"]) == [
        "donor-1"
    ]


def test_valid_mock_patient_level_split_passes():
    module = load_module()
    config = module.load_split_config(CONFIG_PATH)

    module.validate_mock_split_manifest(valid_mock_rows(), config)


def test_missing_audit_status_fails():
    module = load_module()
    config = module.load_split_config(CONFIG_PATH)
    rows = valid_mock_rows()
    rows[0]["audit_status"] = ""

    with pytest.raises(module.SplitPolicyError, match="audit_status"):
        module.validate_mock_split_manifest(rows, config)


def test_cell_id_entity_type_fails_in_mock_manifest():
    module = load_module()
    config = module.load_split_config(CONFIG_PATH)
    rows = valid_mock_rows()
    rows[0]["entity_type"] = "cell_id"

    with pytest.raises(module.SplitPolicyError, match="cell_id"):
        module.validate_mock_split_manifest(rows, config)


def test_train_test_entity_overlap_fails_in_mock_manifest():
    module = load_module()
    config = module.load_split_config(CONFIG_PATH)
    rows = valid_mock_rows()
    rows[1]["entity_id"] = "patient-1"

    with pytest.raises(module.SplitPolicyError, match="overlap"):
        module.validate_mock_split_manifest(rows, config)


def test_selected_datasets_and_external_validation_remain_locked():
    state = STATE_PATH.read_text()

    assert "current_feature: STAGE3-F003" in state
    assert "selected_datasets: []" in state
    assert "external_validation_cohort: TODO" in state
    assert "modeling_allowed: false" in state
    assert "allow_modeling: false" in state
    assert "dataset_download_allowed: false" in state
    assert "allow_downloads: false" in state


def test_split_policy_utility_does_not_import_processing_or_modeling_libraries():
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
