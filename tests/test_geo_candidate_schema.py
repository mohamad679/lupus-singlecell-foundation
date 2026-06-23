import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPO_ROOT / "metadata" / "geo_candidate_schema.yaml"
SCRIPT_PATH = REPO_ROOT / "scripts" / "01_geo_metadata_search_plan.py"


def load_geo_module():
    spec = importlib.util.spec_from_file_location("geo_metadata_search_plan", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_geo_candidate_schema_exists():
    assert SCHEMA_PATH.exists()


def test_geo_candidate_schema_required_fields_are_present():
    module = load_geo_module()
    schema = module.load_candidate_schema(SCHEMA_PATH)

    assert schema["required_fields"] == module.REQUIRED_SCHEMA_FIELDS
    assert "candidate_pending_audit" in schema["allowed_audit_statuses"]
