import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPO_ROOT / "configs" / "baseline_modeling.yaml"
SCRIPT_PATH = REPO_ROOT / "scripts" / "10_baseline_modeling_scaffold.py"
STATE_PATH = REPO_ROOT / "state" / "project_state.yaml"
SRC_PATH = REPO_ROOT / "src"


def load_module():
    spec = importlib.util.spec_from_file_location(
        "baseline_modeling_scaffold", SCRIPT_PATH
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_baseline_modeling_config_exists_and_is_restricted():
    assert CONFIG_PATH.exists()
    module = load_module()
    config = module.load_baseline_config()

    assert config["phase"] == 3
    assert config["approved_task"] == "SLE diagnosis / case-control prediction"
    assert config["allow_training"] is False
    assert config["allow_deep_learning"] is False
    assert config["allow_foundation_models"] is False
    assert config["allow_uncertainty_methods"] is False
    assert config["split_policy"] == "patient_or_cohort_only"
    assert config["forbid_cell_level_split"] is True


def test_all_baseline_families_are_disabled_for_training():
    module = load_module()
    config = module.load_baseline_config()

    assert all(
        family["enabled_for_training"] is False
        for family in config["baseline_families"].values()
    )
    assert config["baseline_families"]["deepsets"]["enabled_for_design"] is False


def test_baseline_package_markers_exist_without_implementations():
    features_dir = SRC_PATH / "features"
    assert features_dir.exists()
    assert {path.name for path in features_dir.iterdir() if path.name != "__pycache__"} == {
        "__init__.py",
        "cell_type_proportions.py",
        "pseudobulk_design.py",
    }

    models_dir = SRC_PATH / "models"
    assert models_dir.exists()
    assert {path.name for path in models_dir.iterdir() if path.name != "__pycache__"} == {
        "__init__.py",
        "logistic_regression_baseline.py",
        "tree_baselines.py",
    }

    evaluation_dir = SRC_PATH / "evaluation"
    assert evaluation_dir.exists()
    assert {path.name for path in evaluation_dir.iterdir() if path.name != "__pycache__"} == {
        "__init__.py",
        "calibration_protocol.py",
        "evaluation_protocol.py",
    }


def test_phase3_state_preserves_modeling_and_dataset_locks():
    state = STATE_PATH.read_text()

    assert "current_phase: Stage 3" in state
    assert "current_feature: STAGE3-F002" in state
    assert "primary_task: Active SLE flare discrimination" in state
    assert "human_gate_2: approved_with_restrictions" in state
    assert "allow_modeling: false" in state
    assert "modeling_allowed: false" in state
    assert "selected_datasets: []" in state
    assert "external_validation_cohort: TODO" in state
