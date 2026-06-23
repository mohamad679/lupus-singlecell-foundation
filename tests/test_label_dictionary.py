import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DICTIONARY_PATH = REPO_ROOT / "metadata" / "label_dictionary.yaml"
SCRIPT_PATH = REPO_ROOT / "scripts" / "05_label_availability_audit.py"


def load_label_module():
    spec = importlib.util.spec_from_file_location("label_availability_audit", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_label_dictionary_exists():
    assert DICTIONARY_PATH.exists()


def test_allowed_label_types_exist():
    module = load_label_module()
    dictionary = module.load_label_dictionary(DICTIONARY_PATH)

    assert dictionary["allowed_label_types"] == module.ALLOWED_LABEL_TYPES


def test_can_be_inferred_defaults_to_false_for_all_label_types():
    module = load_label_module()
    dictionary = module.load_label_dictionary(DICTIONARY_PATH)

    for label_type in module.ALLOWED_LABEL_TYPES:
        assert dictionary["label_types"][label_type]["can_be_inferred"] is False


def test_label_provenance_is_required_for_all_label_types():
    module = load_label_module()
    dictionary = module.load_label_dictionary(DICTIONARY_PATH)

    for label_type in module.ALLOWED_LABEL_TYPES:
        assert dictionary["label_types"][label_type]["provenance_required"] is True
