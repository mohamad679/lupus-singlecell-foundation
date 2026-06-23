import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPO_ROOT / "metadata" / "patient_metadata_schema.yaml"
SCRIPT_PATH = REPO_ROOT / "scripts" / "04_patient_metadata_audit.py"


def load_patient_module():
    spec = importlib.util.spec_from_file_location("patient_metadata_audit", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_patient_metadata_schema_exists():
    assert SCHEMA_PATH.exists()


def test_patient_metadata_schema_required_fields_exist():
    module = load_patient_module()
    fields = module.load_patient_schema(SCHEMA_PATH)

    assert list(fields) == module.REQUIRED_FIELDS


def test_patient_metadata_schema_field_attributes_exist():
    module = load_patient_module()
    fields = module.load_patient_schema(SCHEMA_PATH)

    for field in module.REQUIRED_FIELDS:
        for attribute in module.REQUIRED_FIELD_ATTRIBUTES:
            assert attribute in fields[field]
