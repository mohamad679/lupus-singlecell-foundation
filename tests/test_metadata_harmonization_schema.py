import importlib.util
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPO_ROOT / "metadata" / "metadata_harmonization_schema.yaml"
MAPPING_PATH = REPO_ROOT / "metadata" / "source_field_mapping.yaml"
MODULE_PATH = REPO_ROOT / "src" / "data" / "metadata_harmonization.py"
STATE_PATH = REPO_ROOT / "state" / "project_state.yaml"

CANONICAL_FIELDS = [
    "patient_id",
    "donor_id",
    "sample_id",
    "cell_id",
    "cohort_id",
    "batch_id",
    "dataset_id",
    "source_dataset",
    "source_database",
    "organism",
    "tissue",
    "assay_type",
    "disease_label",
    "disease_activity",
    "cell_type",
    "treatment_status",
    "sex",
    "age",
    "timepoint",
    "split_group",
]


def load_module():
    spec = importlib.util.spec_from_file_location(
        "metadata_harmonization", MODULE_PATH
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def mock_metadata():
    return {
        "patient_id": "TODO",
        "donor_id": "TODO",
        "sample_id": "TODO",
        "cell_id": "TODO",
        "cohort_id": "TODO",
        "batch_id": "TODO",
        "dataset_id": "GSE137029",
        "source_dataset": "TODO",
        "source_database": "GEO",
        "organism": "Homo sapiens",
        "tissue": "TODO",
        "assay_type": "TODO",
        "disease_label": "SLE",
        "disease_activity": "TODO",
        "cell_type": "TODO",
        "treatment_status": "TODO",
        "sex": "TODO",
        "age": "TODO",
        "timepoint": "TODO",
        "split_group": "patient_level",
    }


def test_metadata_harmonization_schema_exists():
    assert SCHEMA_PATH.exists()


def test_canonical_fields_exist():
    module = load_module()
    schema = module.load_harmonization_schema(SCHEMA_PATH)

    for field in CANONICAL_FIELDS:
        assert field in schema["canonical_fields"]
        field_spec = schema["canonical_fields"][field]
        assert "description" in field_spec
        assert "required" in field_spec
        assert "allowed_missing" in field_spec
        assert "source_priority" in field_spec
        assert "harmonization_notes" in field_spec


def test_source_field_mapping_exists_and_sections_present():
    module = load_module()
    mapping = module.load_source_mapping(MAPPING_PATH)

    assert MAPPING_PATH.exists()
    for source in ["GEO", "CELLxGENE", "HCA"]:
        assert source in mapping
        assert mapping[source]
        for entry in mapping[source]:
            assert "original_field" in entry
            assert "canonical_field" in entry
            assert "transformation" in entry
            assert "notes" in entry


def test_validator_accepts_mock_metadata():
    module = load_module()
    schema = module.load_harmonization_schema(SCHEMA_PATH)

    module.validate_canonical_metadata(mock_metadata(), schema)


def test_validator_rejects_missing_disease_label():
    module = load_module()
    schema = module.load_harmonization_schema(SCHEMA_PATH)
    metadata = mock_metadata()
    metadata.pop("disease_label")

    with pytest.raises(module.MetadataHarmonizationError, match="disease_label"):
        module.validate_canonical_metadata(metadata, schema)


def test_validator_rejects_missing_dataset_id():
    module = load_module()
    schema = module.load_harmonization_schema(SCHEMA_PATH)
    metadata = mock_metadata()
    metadata.pop("dataset_id")

    with pytest.raises(module.MetadataHarmonizationError, match="dataset_id"):
        module.validate_canonical_metadata(metadata, schema)


def test_validator_rejects_unresolved_dataset_id():
    module = load_module()
    schema = module.load_harmonization_schema(SCHEMA_PATH)
    metadata = mock_metadata()
    metadata["dataset_id"] = "TODO"

    with pytest.raises(module.MetadataHarmonizationError, match="dataset_id"):
        module.validate_canonical_metadata(metadata, schema)


def test_no_download_or_modeling_flags_changed():
    state = STATE_PATH.read_text()

    assert "current_feature: STAGE1-F002" in state
    assert "selected_datasets: []" in state
    assert "external_validation_cohort: TODO" in state
    assert "modeling_allowed: false" in state
    assert "allow_modeling: false" in state
    assert "dataset_download_allowed: false" in state
    assert "allow_downloads: false" in state
