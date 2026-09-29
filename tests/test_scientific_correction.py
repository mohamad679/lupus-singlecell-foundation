"""Checks for the active correction analysis and donor-pairing boundary."""

import importlib.util
import ast
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from correction_stats import calibration_fit, holm_adjust, paired_delong  # noqa: E402


def _analysis_module():
    spec = importlib.util.spec_from_file_location("correction_analysis", ROOT / "scripts/27_correction_analysis.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_delong_identical_predictions_have_zero_difference():
    y = np.array([0, 0, 0, 1, 1, 1])
    score = np.array([0.1, 0.6, 0.3, 0.2, 0.8, 0.9])
    result = paired_delong(y, score, score)
    assert result["difference"] == 0
    assert result["p_two_sided"] == 1


def test_historical_scores_reproduce_independent_paired_result():
    with (ROOT / "results/l2_sealed_predictions_regenerated.json").open() as file:
        predictions = json.load(file)
    y = predictions["geneformer"]["y"]
    gf = predictions["geneformer"]["proba"]
    age = predictions["metadata_only_age"]["proba"]
    pb = predictions["pseudobulk"]["proba"]
    a = paired_delong(y, gf, age)
    b = paired_delong(y, gf, pb)
    assert a["difference"] == pytest.approx(0.2375)
    assert a["p_two_sided"] == pytest.approx(0.09211444, abs=1e-7)
    assert b["difference"] == pytest.approx(-0.0828125)
    assert b["p_two_sided"] == pytest.approx(0.15899366, abs=1e-7)
    adjusted = holm_adjust({"a": a["p_two_sided"], "b": b["p_two_sided"]})
    assert adjusted == pytest.approx({"a": 0.18422888, "b": 0.18422888}, abs=1e-7)


def test_swapped_donors_with_equal_labels_are_rejected():
    with (ROOT / "results/l2_sealed_predictions_regenerated.json").open() as file:
        predictions = json.load(file)
    predictions["pseudobulk"]["donor_ids"][:2] = reversed(predictions["pseudobulk"]["donor_ids"][:2])
    with pytest.raises(ValueError, match="donor IDs"):
        _analysis_module().analyze(predictions, input_provenance="test")


def test_corrected_shared_calibration_is_stable_for_saturated_probabilities():
    path = ROOT / "results/correction_2026-09/corrected_v1_shared_predictions.json"
    with path.open() as file:
        predictions = json.load(file)
    for arm, row in predictions.items():
        first = calibration_fit(row["y"], row["proba"])
        assert first["status"] == "estimated", arm
        assert first == calibration_fit(row["y"], row["proba"])


class _TinyTokenizedDataset:
    def __init__(self, token_ids):
        self.columns = {"input_ids": token_ids, "cell_id": ["cell-1", "cell-2"]}

    def __len__(self):
        return len(self.columns["input_ids"])

    def __getitem__(self, key):
        return self.columns[key]


@pytest.mark.parametrize("kernel", [
    "kaggle_kernels/l2_geneformer_v1_corrected_dev/run.py",
    "kaggle_kernels/l2_geneformer_v1_corrected_external/run.py",
])
def test_corrected_kernel_rejects_invalid_v1_tokens_and_lost_cells(kernel):
    """Exercise the actual Kaggle validators without running their installers."""
    tree = ast.parse((ROOT / kernel).read_text())
    funcs = [node for node in tree.body if isinstance(node, ast.FunctionDef)
             and node.name in {"validate_tokenizer", "validate_batch"}]
    scope = {"np": np, "load_from_disk": lambda _: _TinyTokenizedDataset([[2, 8088], [3]])}
    exec(compile(ast.Module(body=funcs, type_ignores=[]), kernel, "exec"), scope)
    tokenizer = type("Tokenizer", (), {
        "model_version": "V1", "special_token": False, "model_input_size": 2048,
        "gene_token_dict": {"ENSG00000000003": 2, "ENSG00000000005": 3,
                            "ENSG00000141510": 8088, "ENSG00000139618": 7809},
    })()
    scope["validate_tokenizer"](tokenizer)
    embeddings = pd.DataFrame({"cell_id": ["cell-1", "cell-2"],
                               "donor_id": ["donor-a", "donor-b"],
                               "gf_dim_0": [0.1, 0.2]})
    audit = scope["validate_batch"]("unused", embeddings, {"donor-a": 1, "donor-b": 1}, 9000)
    assert audit["embedded"] == 2
    with pytest.raises(ValueError, match="cells were lost"):
        scope["validate_batch"]("unused", embeddings.iloc[:1], {"donor-a": 1, "donor-b": 1}, 9000)
    scope["load_from_disk"] = lambda _: _TinyTokenizedDataset([[2, 9000], [3]])
    with pytest.raises(ValueError, match="outside V1 vocabulary"):
        scope["validate_batch"]("unused", embeddings, {"donor-a": 1, "donor-b": 1}, 9000)


def test_main_process_tokenization_and_legacy_checkpoint_gate():
    dev_path = ROOT / "kaggle_kernels/l2_geneformer_v1_corrected_dev/run.py"
    external_path = ROOT / "kaggle_kernels/l2_geneformer_v1_corrected_external/run.py"
    for path in (dev_path, external_path):
        tree = ast.parse(path.read_text())
        constructors = [node for node in ast.walk(tree) if isinstance(node, ast.Call)
                        and isinstance(node.func, ast.Name)
                        and node.func.id in {"TranscriptomeTokenizer", "EmbExtractor"}]
        assert len(constructors) == 2
        nproc_by_constructor = {
            call.func.id: next(kw.value.value for kw in call.keywords if kw.arg == "nproc")
            for call in constructors
        }
        assert nproc_by_constructor == {"TranscriptomeTokenizer": None,
                                        "EmbExtractor": 1}

    tree = ast.parse(dev_path.read_text())
    legacy_assignment = next(node for node in tree.body if isinstance(node, ast.Assign)
                             and any(isinstance(target, ast.Name)
                                     and target.id == "LEGACY_MULTIPROCESS_SCRIPT_SHA256S"
                                     for target in node.targets))
    checker = next(node for node in tree.body if isinstance(node, ast.FunctionDef)
                   and node.name == "checkpoint_config_compatible")
    scope = {}
    exec(compile(ast.Module(body=[legacy_assignment, checker], type_ignores=[]),
                 str(dev_path), "exec"), scope)
    old = {"extraction_script_sha256": "591e91e36b95c808084407361570a50f472709ef526b2919ac328b37b2a79be0",
           "checkpoint_sha256_by_file": {"model.bin": "model-hash"},
           "gene_input_mode": "shared"}
    new = {**old, "extraction_script_sha256": "new-script-hash"}
    compatible = scope["checkpoint_config_compatible"]
    assert compatible(new, new)
    assert compatible(old, new)
    assert compatible({**old, "extraction_script_sha256":
                       "be18c4d09531f211b5729fbd1380d76165f12ab02fd243af3e861688d4be509c"}, new)
    assert compatible({**old, "extraction_script_sha256":
                       "90966854faa6e5e6d7902462cd429cc3f504a145053a5eea8a790420f122aed2"}, new)
    assert not compatible({**old, "checkpoint_sha256_by_file": {"model.bin": "changed"}}, new)
    assert not compatible({**old, "extraction_script_sha256": "unknown"}, new)
