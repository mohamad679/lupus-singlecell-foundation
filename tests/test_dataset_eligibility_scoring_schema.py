import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPO_ROOT / "metadata" / "dataset_eligibility_scoring.yaml"
SCRIPT_PATH = REPO_ROOT / "scripts" / "03_score_dataset_eligibility.py"


def load_scoring_module():
    spec = importlib.util.spec_from_file_location("score_dataset_eligibility", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_dataset_eligibility_scoring_yaml_exists():
    assert SCHEMA_PATH.exists()


def test_scoring_weights_sum_to_100():
    module = load_scoring_module()
    schema = module.load_scoring_schema(SCHEMA_PATH)

    total = sum(int(schema[key]) for key in module.DIMENSION_WEIGHT_KEYS)

    assert total == 100
    assert schema["total_points"] == 100


def test_eligibility_categories_exist():
    module = load_scoring_module()
    schema = module.load_scoring_schema(SCHEMA_PATH)

    for key in module.ELIGIBILITY_CATEGORY_KEYS:
        assert key in schema


def test_hard_rejection_rules_exist():
    module = load_scoring_module()
    schema = module.load_scoring_schema(SCHEMA_PATH)

    for rule in module.REQUIRED_HARD_REJECTION_RULES:
        assert rule in schema["hard_rejection_rules"]
