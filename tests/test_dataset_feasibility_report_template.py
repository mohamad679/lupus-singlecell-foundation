import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = REPO_ROOT / "reports" / "final_dataset_feasibility_report.md"
SCRIPT_PATH = REPO_ROOT / "scripts" / "07_generate_dataset_feasibility_report.py"


def load_report_module():
    spec = importlib.util.spec_from_file_location(
        "generate_dataset_feasibility_report", SCRIPT_PATH
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_dataset_feasibility_report_template_exists():
    assert REPORT_PATH.exists()


def test_dataset_feasibility_report_required_sections_exist():
    module = load_report_module()
    report = REPORT_PATH.read_text()

    for section in module.REPORT_SECTIONS:
        assert section in report


def test_dataset_feasibility_report_preserves_todo_sections():
    report = REPORT_PATH.read_text()

    assert "TODO" in report
    assert "Human Gate 1 remains PENDING" in report
    assert "None selected" in report
