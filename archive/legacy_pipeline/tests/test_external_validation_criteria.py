import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CRITERIA_PATH = REPO_ROOT / "metadata" / "external_validation_criteria.yaml"
SCRIPT_PATH = REPO_ROOT / "scripts" / "06_external_validation_audit.py"


def load_external_module():
    spec = importlib.util.spec_from_file_location("external_validation_audit", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_external_validation_criteria_yaml_exists():
    assert CRITERIA_PATH.exists()


def test_all_external_validation_criteria_groups_exist():
    module = load_external_module()
    criteria = module.load_criteria(CRITERIA_PATH)

    for group in module.CRITERIA_GROUPS:
        assert group in criteria
        assert criteria[group]


def test_external_validation_hard_rejection_rules_exist():
    module = load_external_module()
    criteria = module.load_criteria(CRITERIA_PATH)

    for rule in module.REQUIRED_HARD_REJECTION_RULES:
        assert rule in criteria["hard_rejection_rules"]


def test_external_validation_scoring_decisions_exist():
    module = load_external_module()
    criteria = module.load_criteria(CRITERIA_PATH)

    for decision in module.SCORING_DECISIONS:
        assert decision in criteria["scoring"]
