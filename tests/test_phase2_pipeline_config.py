import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPO_ROOT / "configs" / "data_pipeline.yaml"
STATE_PATH = REPO_ROOT / "state" / "project_state.yaml"
SCRIPT_PATH = REPO_ROOT / "scripts" / "08_phase2_pipeline_scaffold.py"


def load_phase2_module():
    spec = importlib.util.spec_from_file_location("phase2_pipeline_scaffold", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_data_pipeline_yaml_exists():
    assert CONFIG_PATH.exists()


def test_data_pipeline_config_restrictions():
    module = load_phase2_module()
    config = module.load_simple_yaml(CONFIG_PATH)

    assert config["phase"] == 2
    assert config["allow_downloads"] is False
    assert config["allow_modeling"] is False
    assert config["forbid_cell_level_split"] is True
    assert config["split_policy"] == "patient_or_cohort_only"


def test_data_pipeline_candidate_scope():
    module = load_phase2_module()
    config = module.load_simple_yaml(CONFIG_PATH)

    assert config["allowed_candidate_datasets"] == [
        "GSE137029",
        (
            "CELLxGENE_HCA_436154da-bcf1-4130-9c8b-120ff9a888f2_"
            "218acb0f-9f2f-4f76-b90b-15a4b7c7f629"
        ),
    ]
    assert config["restricted_candidate_datasets"] == ["GSE174188", "GSE162577"]


def test_required_future_metadata_fields_exist():
    module = load_phase2_module()
    config = module.load_simple_yaml(CONFIG_PATH)

    for field in module.REQUIRED_METADATA_FIELDS:
        assert field in config["required_future_metadata"]


def test_phase2_scaffold_validation_summary():
    module = load_phase2_module()
    summary = module.run_validation(CONFIG_PATH)

    assert summary["phase"] == 2
    assert summary["allow_downloads"] is False
    assert summary["allow_modeling"] is False
    assert summary["split_policy"] == "patient_or_cohort_only"
    assert summary["forbid_cell_level_split"] is True


def test_project_state_phase2_restricted_gate_controls():
    state = STATE_PATH.read_text()

    assert "current_phase: Stage 2" in state
    assert "current_feature: STAGE2-F004" in state
    assert "blocked: false" in state
    assert "blocked_reason: null" in state
    assert "status: approved_with_restrictions" in state
    assert "selected_datasets: []" in state
    assert "external_validation_cohort: TODO" in state
    assert "no_modeling: true" in state
    assert "no_downloads_without_explicit_feature: true" in state
    assert "no_cell_level_splits: true" in state
