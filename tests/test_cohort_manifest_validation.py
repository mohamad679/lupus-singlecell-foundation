import importlib.util
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPO_ROOT / "metadata" / "cohort_manifest_schema.yaml"
MODULE_PATH = REPO_ROOT / "src" / "data" / "cohort_manifest.py"
STATE_PATH = REPO_ROOT / "state" / "project_state.yaml"


def load_module():
    spec = importlib.util.spec_from_file_location("cohort_manifest", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def valid_candidate_row():
    return {
        "manifest_id": "manifest-001",
        "candidate_id": "GSE137029",
        "source": "GEO",
        "accession_or_collection_id": "GSE137029",
        "dataset_id": "GSE137029",
        "cohort_id": "TODO",
        "sample_id": "TODO",
        "patient_or_donor_id": "TODO",
        "tissue": "TODO",
        "assay_type": "TODO",
        "disease_context": "SLE",
        "disease_label_status": "candidate_pending_audit",
        "activity_label_status": "TODO",
        "batch_id_status": "TODO",
        "treatment_metadata_status": "TODO",
        "processed_object_status": "TODO",
        "raw_data_status": "TODO",
        "access_status": "candidate_pending_audit",
        "intended_role": "candidate_training",
        "approved_role": "TODO",
        "risk_level": "candidate_pending_audit",
        "provenance_url": "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE137029",
        "notes": "mock candidate row only; not approved",
        "audit_status": "candidate_pending_audit",
    }


def test_valid_mock_candidate_row_passes():
    module = load_module()
    schema = module.load_cohort_manifest_schema(SCHEMA_PATH)

    module.validate_cohort_manifest_rows([valid_candidate_row()], schema)


def test_approved_role_cannot_be_training_without_human_gate():
    module = load_module()
    schema = module.load_cohort_manifest_schema(SCHEMA_PATH)
    row = valid_candidate_row()
    row["approved_role"] = "training"

    with pytest.raises(module.CohortManifestError, match="human_gate_approved"):
        module.validate_cohort_manifest_rows([row], schema)


def test_approved_role_cannot_be_external_validation_without_human_gate():
    module = load_module()
    schema = module.load_cohort_manifest_schema(SCHEMA_PATH)
    row = valid_candidate_row()
    row["approved_role"] = "external_validation"

    with pytest.raises(module.CohortManifestError, match="human_gate_approved"):
        module.validate_cohort_manifest_rows([row], schema)


def test_provenance_url_is_required_for_rows():
    module = load_module()
    schema = module.load_cohort_manifest_schema(SCHEMA_PATH)
    row = valid_candidate_row()
    row["provenance_url"] = ""

    with pytest.raises(module.CohortManifestError, match="provenance_url"):
        module.validate_cohort_manifest_rows([row], schema)


def test_audit_status_is_required_for_rows():
    module = load_module()
    schema = module.load_cohort_manifest_schema(SCHEMA_PATH)
    row = valid_candidate_row()
    row["audit_status"] = ""

    with pytest.raises(module.CohortManifestError, match="audit_status"):
        module.validate_cohort_manifest_rows([row], schema)


def test_invalid_intended_role_is_rejected():
    module = load_module()
    schema = module.load_cohort_manifest_schema(SCHEMA_PATH)
    row = valid_candidate_row()
    row["intended_role"] = "official_training"

    with pytest.raises(module.CohortManifestError, match="intended_role"):
        module.validate_cohort_manifest_rows([row], schema)


def test_selected_dataset_assignment_is_rejected():
    module = load_module()
    schema = module.load_cohort_manifest_schema(SCHEMA_PATH)
    row = valid_candidate_row()
    row["selected_dataset"] = "true"

    with pytest.raises(module.CohortManifestError, match="selected dataset"):
        module.validate_cohort_manifest_rows([row], schema)


def test_selected_datasets_and_external_validation_remain_locked():
    state = STATE_PATH.read_text()

    assert "current_feature: STAGE3-F005" in state
    assert "selected_datasets: []" in state
    assert "external_validation_cohort: TODO" in state
    assert "modeling_allowed: false" in state
    assert "allow_modeling: false" in state
    assert "dataset_download_allowed: false" in state
    assert "allow_downloads: false" in state


def test_cohort_manifest_utility_does_not_import_processing_or_modeling_libraries():
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
