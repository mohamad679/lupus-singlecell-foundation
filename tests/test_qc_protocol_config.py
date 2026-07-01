import csv
import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPO_ROOT / "configs" / "qc.yaml"
SUMMARY_PATH = REPO_ROOT / "reports" / "tables" / "qc_summary.csv"
THRESHOLDS_PATH = REPO_ROOT / "reports" / "tables" / "qc_threshold_decisions.csv"
MODULE_PATH = REPO_ROOT / "src" / "qc" / "qc_policy.py"
STATE_PATH = REPO_ROOT / "state" / "project_state.yaml"


def load_module():
    spec = importlib.util.spec_from_file_location("qc_policy", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_qc_yaml_exists():
    assert CONFIG_PATH.exists()


def test_qc_config_restrictions():
    module = load_module()
    config = module.load_qc_config(CONFIG_PATH)

    module.validate_qc_config(config)
    policy = config["qc_policy"]
    assert policy["allow_real_filtering"] is False
    assert policy["forbid_threshold_guessing"] is True
    assert policy["threshold_source"] == "TODO"


def test_required_qc_outputs_are_listed():
    module = load_module()
    config = module.load_qc_config(CONFIG_PATH)

    assert "reports/tables/qc_summary.csv" in config["required_outputs"]
    assert "reports/tables/qc_threshold_decisions.csv" in config["required_outputs"]


def test_qc_summary_csv_exists_with_required_headers_only():
    module = load_module()

    assert SUMMARY_PATH.exists()
    with SUMMARY_PATH.open(newline="") as handle:
        rows = list(csv.reader(handle))

    assert rows == [module.QC_SUMMARY_HEADERS]


def test_qc_threshold_decisions_csv_exists_with_required_headers_only():
    module = load_module()

    assert THRESHOLDS_PATH.exists()
    with THRESHOLDS_PATH.open(newline="") as handle:
        rows = list(csv.reader(handle))

    assert rows == [module.QC_THRESHOLD_HEADERS]


def test_no_download_or_modeling_flags_changed():
    state = STATE_PATH.read_text()

    assert "current_feature: STAGE3-F002" in state
    assert "selected_datasets: []" in state
    assert "external_validation_cohort: TODO" in state
    assert "modeling_allowed: false" in state
    assert "allow_modeling: false" in state
    assert "dataset_download_allowed: false" in state
    assert "allow_downloads: false" in state
