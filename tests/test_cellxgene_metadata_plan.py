import csv
import importlib.util
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPO_ROOT / "configs" / "data_audit.yaml"
SCHEMA_PATH = REPO_ROOT / "metadata" / "cellxgene_candidate_schema.yaml"
TABLE_PATH = REPO_ROOT / "reports" / "tables" / "cellxgene_candidate_datasets.csv"
SCRIPT_PATH = REPO_ROOT / "scripts" / "02_cellxgene_metadata_plan.py"


def load_cellxgene_module():
    spec = importlib.util.spec_from_file_location("cellxgene_metadata_plan", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def read_rows(path: Path):
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def test_cellxgene_config_has_metadata_only_controls():
    module = load_cellxgene_module()
    config = module.load_cellxgene_config(CONFIG_PATH)

    assert config["query_terms"] == [
        "lupus",
        "systemic lupus erythematosus",
        "SLE",
        "lupus nephritis",
        "autoimmune",
        "PBMC",
        "kidney",
    ]
    assert config["metadata_only"] is True
    assert config["allow_full_download"] is False

    for field in module.REQUIRED_MANUAL_VERIFICATION:
        assert field in config["required_manual_verification"]


def test_cellxgene_candidate_table_exists_with_correct_headers():
    module = load_cellxgene_module()

    assert TABLE_PATH.exists()
    with TABLE_PATH.open(newline="") as handle:
        header = next(csv.reader(handle))

    assert header == module.REQUIRED_SCHEMA_FIELDS


def test_cellxgene_plan_can_create_header_only_table(tmp_path):
    module = load_cellxgene_module()
    output_path = tmp_path / "cellxgene_candidate_datasets.csv"

    module.run_plan(CONFIG_PATH, SCHEMA_PATH, output_path)

    with output_path.open(newline="") as handle:
        reader = csv.reader(handle)
        header = next(reader)
        rows = list(reader)

    assert header == module.REQUIRED_SCHEMA_FIELDS
    assert rows == []


def test_cellxgene_script_does_not_invent_rows():
    rows = read_rows(TABLE_PATH)

    assert rows == []


def test_audit_status_is_required_if_rows_exist(tmp_path):
    module = load_cellxgene_module()
    output_path = tmp_path / "cellxgene_candidate_datasets.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=module.REQUIRED_SCHEMA_FIELDS)
        writer.writeheader()
        writer.writerow(
            {
                "collection_id": "TEST_ONLY_COLLECTION",
                "dataset_id": "TEST_ONLY_DATASET",
                "audit_status": "",
            }
        )

    with pytest.raises(module.CellxgenePlanError, match="missing audit_status"):
        module.run_plan(CONFIG_PATH, SCHEMA_PATH, output_path)


def test_collection_id_is_required_if_rows_exist(tmp_path):
    module = load_cellxgene_module()
    output_path = tmp_path / "cellxgene_candidate_datasets.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=module.REQUIRED_SCHEMA_FIELDS)
        writer.writeheader()
        writer.writerow(
            {
                "collection_id": "",
                "dataset_id": "TEST_ONLY_DATASET",
                "audit_status": "candidate_pending_audit",
            }
        )

    with pytest.raises(module.CellxgenePlanError, match="missing collection_id"):
        module.run_plan(CONFIG_PATH, SCHEMA_PATH, output_path)


def test_dataset_id_is_required_if_rows_exist(tmp_path):
    module = load_cellxgene_module()
    output_path = tmp_path / "cellxgene_candidate_datasets.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=module.REQUIRED_SCHEMA_FIELDS)
        writer.writeheader()
        writer.writerow(
            {
                "collection_id": "TEST_ONLY_COLLECTION",
                "dataset_id": "",
                "audit_status": "candidate_pending_audit",
            }
        )

    with pytest.raises(module.CellxgenePlanError, match="missing dataset_id"):
        module.run_plan(CONFIG_PATH, SCHEMA_PATH, output_path)


def test_cellxgene_script_has_no_network_or_process_clients():
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
