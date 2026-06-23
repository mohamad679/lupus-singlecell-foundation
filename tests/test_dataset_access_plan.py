import csv
import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PLAN_PATH = REPO_ROOT / "metadata" / "dataset_access_plan.yaml"
TABLE_PATH = REPO_ROOT / "reports" / "tables" / "dataset_access_plan.csv"
SCRIPT_PATH = REPO_ROOT / "scripts" / "09_validate_dataset_access_plan.py"
STATE_PATH = REPO_ROOT / "state" / "project_state.yaml"

EXPECTED_CANDIDATES = {
    "GSE137029",
    (
        "CELLxGENE_HCA_436154da-bcf1-4130-9c8b-120ff9a888f2_"
        "218acb0f-9f2f-4f76-b90b-15a4b7c7f629"
    ),
}


def load_module():
    spec = importlib.util.spec_from_file_location(
        "validate_dataset_access_plan", SCRIPT_PATH
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def read_rows():
    with TABLE_PATH.open(newline="") as handle:
        return list(csv.DictReader(handle))


def test_dataset_access_plan_yaml_exists():
    assert PLAN_PATH.exists()


def test_dataset_access_plan_csv_exists_and_has_two_candidate_rows():
    assert TABLE_PATH.exists()
    rows = read_rows()

    assert len(rows) == 2
    assert {row["candidate_id"] for row in rows} == EXPECTED_CANDIDATES


def test_access_plan_validator_accepts_scaffold_plan():
    module = load_module()

    assert module.run_validation() == {
        "candidate_count": 2,
        "approved_for_download": False,
        "approved_for_modeling": False,
        "audit_status": "pending_human_download_gate",
    }


def test_approved_for_download_is_false_for_all_rows():
    rows = read_rows()

    assert {row["approved_for_download"] for row in rows} == {"false"}


def test_approved_for_modeling_is_false_for_all_rows():
    rows = read_rows()

    assert {row["approved_for_modeling"] for row in rows} == {"false"}


def test_audit_status_is_pending_human_download_gate_for_all_rows():
    rows = read_rows()

    assert {row["audit_status"] for row in rows} == {"pending_human_download_gate"}


def test_selected_datasets_and_external_validation_remain_locked():
    state = STATE_PATH.read_text()

    assert "current_feature: P3-F005" in state
    assert "selected_datasets: []" in state
    assert "external_validation_cohort: TODO" in state
    assert "modeling_allowed: false" in state
    assert "allow_modeling: false" in state
    assert "dataset_download_allowed: false" in state
    assert "allow_downloads: false" in state


def test_no_executable_fetch_commands_appear_in_access_plan_script():
    source = SCRIPT_PATH.read_text().lower()
    forbidden_fragments = [
        "curl ",
        "wget ",
        "cellxgene ",
        "scanpy",
        "requests",
        "urllib",
        "socket",
        "subprocess",
    ]

    for fragment in forbidden_fragments:
        assert fragment not in source


def test_no_data_files_were_added_under_data_boundaries():
    for relative in ["data/raw", "data/interim", "data/processed"]:
        directory = REPO_ROOT / relative
        if not directory.exists():
            continue
        files = [path for path in directory.rglob("*") if path.is_file()]
        assert files == []
