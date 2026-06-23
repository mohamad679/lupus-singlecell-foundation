import csv
import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPO_ROOT / "metadata" / "cohort_manifest_schema.yaml"
MANIFEST_PATH = REPO_ROOT / "metadata" / "cohort_manifest.csv"
MODULE_PATH = REPO_ROOT / "src" / "data" / "cohort_manifest.py"

REQUIRED_FIELDS = [
    "manifest_id",
    "candidate_id",
    "source",
    "accession_or_collection_id",
    "dataset_id",
    "cohort_id",
    "sample_id",
    "patient_or_donor_id",
    "tissue",
    "assay_type",
    "disease_context",
    "disease_label_status",
    "activity_label_status",
    "batch_id_status",
    "treatment_metadata_status",
    "processed_object_status",
    "raw_data_status",
    "access_status",
    "intended_role",
    "approved_role",
    "risk_level",
    "provenance_url",
    "notes",
    "audit_status",
]


def load_module():
    spec = importlib.util.spec_from_file_location("cohort_manifest", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_cohort_manifest_schema_exists():
    assert SCHEMA_PATH.exists()


def test_cohort_manifest_schema_required_fields_and_specs():
    module = load_module()
    schema = module.load_cohort_manifest_schema(SCHEMA_PATH)

    module.validate_cohort_manifest_schema(schema)
    assert schema["required_fields"] == REQUIRED_FIELDS
    for field in REQUIRED_FIELDS:
        field_spec = schema["fields"][field]
        assert "description" in field_spec
        assert "required" in field_spec
        assert "allowed_values" in field_spec
        assert "allowed_missing" in field_spec
        assert "provenance_required" in field_spec


def test_cohort_manifest_csv_exists_with_required_headers_only():
    module = load_module()
    schema = module.load_cohort_manifest_schema(SCHEMA_PATH)

    assert MANIFEST_PATH.exists()
    with MANIFEST_PATH.open(newline="") as handle:
        rows = list(csv.reader(handle))

    assert rows == [REQUIRED_FIELDS]
    module.validate_cohort_manifest_headers(rows[0], schema)
