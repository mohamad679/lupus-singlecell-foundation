import copy
import importlib.util
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPO_ROOT / "metadata" / "anndata_schema.yaml"
STATE_PATH = REPO_ROOT / "state" / "project_state.yaml"
MODULE_PATH = REPO_ROOT / "src" / "data" / "anndata_schema.py"

REQUIRED_OBS_FIELDS = [
    "cell_id",
    "patient_id",
    "donor_id",
    "sample_id",
    "cohort_id",
    "batch_id",
    "tissue",
    "assay_type",
    "disease_label",
    "cell_type",
    "source_dataset",
    "split_group",
]

REQUIRED_VAR_FIELDS = ["gene_id", "gene_symbol", "feature_type", "genome"]
REQUIRED_LAYERS = ["counts", "normalized", "log_normalized"]
REQUIRED_UNS_FIELDS = [
    "dataset_id",
    "source",
    "preprocessing_version",
    "schema_version",
    "audit_status",
    "patient_level_split_policy",
]


def load_module():
    spec = importlib.util.spec_from_file_location("anndata_schema", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def valid_mock_adata():
    obs_columns = {
        "cell_id": ["cell-1", "cell-2"],
        "patient_id": ["patient-1", "patient-2"],
        "donor_id": ["donor-1", "donor-2"],
        "sample_id": ["sample-1", "sample-2"],
        "cohort_id": ["cohort-1", "cohort-1"],
        "batch_id": ["batch-1", "batch-1"],
        "tissue": ["PBMC", "PBMC"],
        "assay_type": ["10x", "10x"],
        "disease_label": ["SLE", "healthy_control"],
        "cell_type": ["TODO", "TODO"],
        "source_dataset": ["GSE137029", "GSE137029"],
        "split_group": ["patient_level", "patient_level"],
    }
    var_columns = {
        "gene_id": ["ENSG000001", "ENSG000002"],
        "gene_symbol": ["GENE1", "GENE2"],
        "feature_type": ["Gene Expression", "Gene Expression"],
        "genome": ["GRCh38", "GRCh38"],
    }

    return {
        "obs": {"index": ["cell-1", "cell-2"], "columns": obs_columns},
        "var": {"index": ["gene-1", "gene-2"], "columns": var_columns},
        "X": {"shape": (2, 2)},
        "layers": {
            "counts": {"shape": (2, 2)},
            "normalized": {"shape": (2, 2)},
            "log_normalized": {"shape": (2, 2)},
        },
        "uns": {
            "dataset_id": "GSE137029",
            "source": "GEO / NCBI",
            "preprocessing_version": "TODO",
            "schema_version": "1.0",
            "audit_status": "candidate_pending_audit",
            "patient_level_split_policy": "patient_level",
        },
    }


def test_anndata_schema_yaml_exists():
    assert SCHEMA_PATH.exists()


def test_required_schema_sections_and_fields_exist():
    module = load_module()
    schema = module.load_anndata_schema(SCHEMA_PATH)

    module.validate_required_schema_sections(schema)
    for field in REQUIRED_OBS_FIELDS:
        assert field in schema["obs_required_fields"]
    for field in REQUIRED_VAR_FIELDS:
        assert field in schema["var_required_fields"]
    for layer in REQUIRED_LAYERS:
        assert layer in schema["layers_policy"]
    for field in REQUIRED_UNS_FIELDS:
        assert field in schema["uns_required_fields"]


def test_schema_validator_accepts_mock_valid_object():
    module = load_module()
    schema = module.load_anndata_schema(SCHEMA_PATH)

    module.validate_anndata_like_structure(valid_mock_adata(), schema)


def test_schema_validator_rejects_missing_patient_id():
    module = load_module()
    schema = module.load_anndata_schema(SCHEMA_PATH)
    adata = valid_mock_adata()
    adata["obs"]["columns"]["patient_id"] = ["patient-1", ""]

    with pytest.raises(module.AnnDataSchemaError, match="patient_id"):
        module.validate_anndata_like_structure(adata, schema)


def test_schema_validator_rejects_missing_disease_label():
    module = load_module()
    schema = module.load_anndata_schema(SCHEMA_PATH)
    adata = valid_mock_adata()
    adata["obs"]["columns"].pop("disease_label")

    with pytest.raises(module.AnnDataSchemaError, match="disease_label"):
        module.validate_anndata_like_structure(adata, schema)


def test_schema_validator_rejects_cell_level_split_policy():
    module = load_module()
    schema = module.load_anndata_schema(SCHEMA_PATH)
    adata = copy.deepcopy(valid_mock_adata())
    adata["obs"]["columns"]["split_group"] = ["cell_level", "cell_level"]

    with pytest.raises(module.AnnDataSchemaError, match="cell-level split"):
        module.validate_anndata_like_structure(adata, schema)


def test_schema_validator_rejects_ad_hoc_split_group_values():
    module = load_module()
    schema = module.load_anndata_schema(SCHEMA_PATH)
    adata = copy.deepcopy(valid_mock_adata())
    adata["obs"]["columns"]["split_group"] = ["train", "test"]

    with pytest.raises(module.AnnDataSchemaError, match="patient-level or cohort-level"):
        module.validate_anndata_like_structure(adata, schema)


def test_no_download_or_modeling_flags_changed():
    state = STATE_PATH.read_text()

    assert "current_feature: P2-F007" in state
    assert "selected_datasets: []" in state
    assert "external_validation_cohort: TODO" in state
    assert "modeling_allowed: false" in state
    assert "allow_modeling: false" in state
    assert "dataset_download_allowed: false" in state
    assert "allow_downloads: false" in state
