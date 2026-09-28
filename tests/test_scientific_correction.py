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
from correction_stats import holm_adjust, paired_delong  # noqa: E402


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
