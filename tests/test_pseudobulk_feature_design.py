import csv
import importlib.util
import json
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPO_ROOT / "configs" / "pseudobulk.yaml"
SCHEMA_PATH = REPO_ROOT / "metadata" / "pseudobulk_feature_schema.yaml"
MANIFEST_PATH = REPO_ROOT / "reports" / "tables" / "pseudobulk_feature_manifest.csv"
MODULE_PATH = REPO_ROOT / "src" / "features" / "pseudobulk_design.py"
STATE_PATH = REPO_ROOT / "state" / "project_state.yaml"

REQUIRED_FIELDS = [
    "feature_id",
    "dataset_id",
    "aggregation_unit",
    "aggregation_id",
    "cell_type",
    "gene_id",
    "gene_symbol",
    "aggregation_method",
    "value_type",
    "normalization_status",
    "split_group",
    "audit_status",
]
MANIFEST_HEADERS = REQUIRED_FIELDS + ["notes"]


def load_module():
    spec = importlib.util.spec_from_file_location("pseudobulk_design", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def valid_mock_row():
    return {
        "feature_id": "mock-feature-001",
        "dataset_id": "MOCK_DATASET",
        "aggregation_unit": "patient_id",
        "aggregation_id": "mock-patient-001",
        "cell_type": "TODO",
        "gene_id": "mock-gene-001",
        "gene_symbol": "TODO",
        "aggregation_method": "sum_counts",
        "value_type": "count",
        "normalization_status": "TODO",
        "split_group": "patient_level_train",
        "audit_status": "mock_only",
        "notes": "mock validation row; no real feature",
    }


def test_pseudobulk_config_exists_and_disables_execution():
    assert CONFIG_PATH.exists()
    module = load_module()
    config = module.load_pseudobulk_config(CONFIG_PATH)

    assert config["task"] == "SLE diagnosis / case-control prediction"
    assert config["allow_real_extraction"] is False
    assert config["allow_training"] is False
    assert config["forbidden_aggregation_units"] == ["cell_id", "barcode"]
    assert config["require_patient_level_split"] is True
    assert config["require_no_cell_level_leakage"] is True


def test_feature_schema_exists_with_required_field_specs():
    assert SCHEMA_PATH.exists()
    module = load_module()
    schema = json.loads(SCHEMA_PATH.read_text())

    module.validate_pseudobulk_feature_schema(schema)
    assert schema["required_fields"] == REQUIRED_FIELDS
    for field in REQUIRED_FIELDS:
        assert set(schema["fields"][field]) >= {
            "description",
            "required",
            "allowed_missing",
            "notes",
        }


def test_feature_manifest_is_headers_only():
    assert MANIFEST_PATH.exists()
    module = load_module()
    with MANIFEST_PATH.open(newline="") as handle:
        rows = list(csv.reader(handle))

    assert rows == [MANIFEST_HEADERS]
    module.validate_pseudobulk_manifest_headers(rows[0])


def test_valid_mock_pseudobulk_row_passes():
    module = load_module()

    module.validate_mock_pseudobulk_rows([valid_mock_row()])


@pytest.mark.parametrize("aggregation_unit", ["cell_id", "barcode"])
def test_cell_level_aggregation_fails(aggregation_unit):
    module = load_module()
    row = valid_mock_row()
    row["aggregation_unit"] = aggregation_unit

    with pytest.raises(module.PseudobulkDesignError, match="cell-level"):
        module.validate_mock_pseudobulk_rows([row])


def test_missing_audit_status_fails():
    module = load_module()
    row = valid_mock_row()
    row["audit_status"] = ""

    with pytest.raises(module.PseudobulkDesignError, match="audit_status"):
        module.validate_mock_pseudobulk_rows([row])


def test_unsupported_aggregation_unit_fails():
    module = load_module()
    row = valid_mock_row()
    row["aggregation_unit"] = "cohort_id"

    with pytest.raises(module.PseudobulkDesignError, match="aggregation_unit"):
        module.validate_mock_pseudobulk_rows([row])


def test_project_state_preserves_phase3_safety_locks():
    state = STATE_PATH.read_text()

    assert "current_phase: Stage 1" in state
    assert "current_feature: STAGE1-F003" in state
    assert "primary_task: Active SLE flare discrimination" in state
    assert "allow_modeling: false" in state
    assert "modeling_allowed: false" in state
    assert "selected_datasets: []" in state
    assert "external_validation_cohort: TODO" in state


def test_pseudobulk_utility_has_no_real_data_or_modeling_imports():
    source = MODULE_PATH.read_text().lower()
    forbidden_fragments = [
        "import scanpy",
        "from scanpy",
        "import anndata",
        "from anndata",
        "import pandas",
        "import numpy",
        "sklearn",
        "torch",
        "tensorflow",
        "xgboost",
        "requests",
        "urllib",
        ".fit(",
    ]

    for fragment in forbidden_fragments:
        assert fragment not in source
