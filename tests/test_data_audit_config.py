import csv
import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPO_ROOT / "configs" / "data_audit.yaml"
CATALOG_PATH = REPO_ROOT / "metadata" / "dataset_catalog.csv"
AUDIT_SCRIPT_PATH = REPO_ROOT / "scripts" / "00_audit_datasets.py"


def load_audit_module():
    spec = importlib.util.spec_from_file_location("audit_datasets", AUDIT_SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_data_audit_config_exists_and_has_required_sections():
    module = load_audit_module()
    config = module.load_config(CONFIG_PATH)

    for key in module.REQUIRED_CONFIG_KEYS:
        assert key in config
        assert config[key], f"{key} must not be empty"


def test_sources_to_audit_include_required_public_sources():
    module = load_audit_module()
    config = module.load_config(CONFIG_PATH)

    assert config["sources_to_audit"] == [
        "GEO / NCBI",
        "CELLxGENE Census",
        "Human Cell Atlas",
        "published AnnData / Seurat repositories",
    ]


def test_required_fields_match_dataset_catalog_header():
    module = load_audit_module()
    config = module.load_config(CONFIG_PATH)

    with CATALOG_PATH.open(newline="") as handle:
        header = next(csv.reader(handle))

    assert config["required_fields"] == header


def test_forbidden_actions_include_phase_1_safety_controls():
    module = load_audit_module()
    config = module.load_config(CONFIG_PATH)

    for action in module.REQUIRED_FORBIDDEN_ACTIONS:
        assert action in config["forbidden_actions"]
