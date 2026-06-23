import csv
import importlib.util
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPO_ROOT / "configs" / "data_audit.yaml"
SCHEMA_PATH = REPO_ROOT / "metadata" / "geo_candidate_schema.yaml"
TABLE_PATH = REPO_ROOT / "reports" / "tables" / "geo_candidate_datasets.csv"
SCRIPT_PATH = REPO_ROOT / "scripts" / "01_geo_metadata_search_plan.py"


def load_geo_module():
    spec = importlib.util.spec_from_file_location("geo_metadata_search_plan", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def read_rows(path: Path):
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def test_geo_config_has_metadata_only_ncbi_controls():
    module = load_geo_module()
    config = module.load_geo_config(CONFIG_PATH)

    assert config["search_terms"] == [
        "systemic lupus erythematosus single cell RNA sequencing",
        "SLE scRNA-seq",
        "lupus nephritis single cell RNA-seq",
        "autoimmune lupus single-cell transcriptomics",
        "PBMC lupus single cell",
        "kidney lupus nephritis single cell",
    ]
    assert config["metadata_only"] is True
    assert config["allow_full_download"] is False

    for field in module.REQUIRED_MANUAL_VERIFICATION:
        assert field in config["required_manual_verification"]


def test_geo_candidate_table_exists_with_correct_headers():
    module = load_geo_module()

    assert TABLE_PATH.exists()
    with TABLE_PATH.open(newline="") as handle:
        header = next(csv.reader(handle))

    assert header == module.REQUIRED_SCHEMA_FIELDS


def test_geo_plan_can_create_header_only_table(tmp_path):
    module = load_geo_module()
    output_path = tmp_path / "geo_candidate_datasets.csv"

    module.run_plan(CONFIG_PATH, SCHEMA_PATH, output_path)

    with output_path.open(newline="") as handle:
        reader = csv.reader(handle)
        header = next(reader)
        rows = list(reader)

    assert header == module.REQUIRED_SCHEMA_FIELDS
    assert rows == []


def test_geo_script_does_not_invent_rows():
    rows = read_rows(TABLE_PATH)

    assert rows == []


def test_audit_status_is_required_if_rows_exist(tmp_path):
    module = load_geo_module()
    output_path = tmp_path / "geo_candidate_datasets.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=module.REQUIRED_SCHEMA_FIELDS)
        writer.writeheader()
        writer.writerow({"accession": "TEST_ONLY_NOT_A_DATASET", "audit_status": ""})

    with pytest.raises(module.GeoPlanError, match="missing audit_status"):
        module.run_plan(CONFIG_PATH, SCHEMA_PATH, output_path)


def test_accession_is_required_if_rows_exist(tmp_path):
    module = load_geo_module()
    output_path = tmp_path / "geo_candidate_datasets.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=module.REQUIRED_SCHEMA_FIELDS)
        writer.writeheader()
        writer.writerow({"accession": "", "audit_status": "candidate_pending_audit"})

    with pytest.raises(module.GeoPlanError, match="missing explicit accession"):
        module.run_plan(CONFIG_PATH, SCHEMA_PATH, output_path)


def test_geo_script_has_no_network_or_process_clients():
    source = SCRIPT_PATH.read_text()

    forbidden_fragments = [
        "requests",
        "urllib",
        "http.client",
        "ftplib",
        "socket",
        "subprocess",
        "curl",
        "wget",
    ]

    for fragment in forbidden_fragments:
        assert fragment not in source
