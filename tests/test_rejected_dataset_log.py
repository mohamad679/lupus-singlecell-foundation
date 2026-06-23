import csv
import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
REJECTED_LOG_PATH = REPO_ROOT / "reports" / "tables" / "rejected_dataset_log.csv"
SCRIPT_PATH = REPO_ROOT / "scripts" / "07_generate_dataset_feasibility_report.py"


def load_report_module():
    spec = importlib.util.spec_from_file_location(
        "generate_dataset_feasibility_report", SCRIPT_PATH
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_rejected_dataset_log_exists():
    assert REJECTED_LOG_PATH.exists()


def test_rejected_dataset_log_headers_match_schema():
    module = load_report_module()

    with REJECTED_LOG_PATH.open(newline="") as handle:
        header = next(csv.reader(handle))

    assert header == module.REJECTED_LOG_HEADERS


def test_rejected_dataset_log_has_no_rows():
    with REJECTED_LOG_PATH.open(newline="") as handle:
        rows = list(csv.DictReader(handle))

    assert rows == []
