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


def read_rows(path: Path):
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def test_audit_script_writes_report_without_inventing_rows(tmp_path):
    module = load_audit_module()
    output_path = tmp_path / "dataset_feasibility_table.csv"

    module.run_audit(CONFIG_PATH, CATALOG_PATH, output_path)

    catalog_rows = read_rows(CATALOG_PATH)
    report_rows = read_rows(output_path)

    assert len(report_rows) == len(catalog_rows)
    assert [row["dataset_id"] for row in report_rows] == [
        row["dataset_id"] for row in catalog_rows
    ]
    assert [row["accession"] for row in report_rows] == [
        row["accession"] for row in catalog_rows
    ]
    assert all(row["download_status"] == "not_downloaded" for row in report_rows)
    assert all(row["audit_status"] == "pending_manual_source_audit" for row in report_rows)


def test_audit_script_has_no_network_or_process_clients():
    source = AUDIT_SCRIPT_PATH.read_text()

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
