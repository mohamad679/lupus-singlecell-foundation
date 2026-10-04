"""Regression tests for the corrected extraction and calibration boundaries."""

import copy
import hashlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from correction_protocol import (  # noqa: E402
    CHECKPOINT_SHA256_BY_FILE, EXPECTED_DICTIONARY_SHA256_BY_FILE,
    REVISION, SHARED_GENE_SHA256, validate_setup_provenance, validate_summary,
)
from correction_stats import calibration_fit  # noqa: E402


@pytest.mark.parametrize("field,bad", [
    ("emb_layer", 0), ("model_input_size", 4096),
    ("geneformer_revision", "arbitrary"),
    ("intersection_sha256", "wrong-shared-gene-set"),
    ("checkpoint_sha256_by_file", {"config.json": "wrong"}),
])
def test_wrong_but_matching_cohort_summaries_are_rejected(field, bad):
    folder = ROOT / "results/correction_2026-09/shared_features"
    names = ("l2_dev_geneformer_v1_shared_run_summary.json",
             "l2_sealed_geneformer_v1_shared_run_summary.json")
    for name in names:
        summary = json.loads((folder / name).read_text())
        validate_summary(summary, "shared")
        corrupted = copy.deepcopy(summary)
        corrupted[field] = bad
        with pytest.raises(ValueError, match="Geneformer protocol differs"):
            validate_summary(corrupted, "shared")


def test_original_scores_control_saturated_probability_calibration():
    predictions = json.loads((ROOT / "results/correction_2026-09/corrected_v1_shared_predictions.json").read_text())
    row = predictions["geneformer"]
    direct = calibration_fit(row["y"], row["proba"], decision_score=row["decision_score"])
    clipped = calibration_fit(row["y"], row["proba"])
    assert direct["status"] == clipped["status"] == "estimated"
    assert direct["slope"] == pytest.approx(0.148941996, abs=1e-7)
    assert clipped["slope"] == pytest.approx(0.1845047, abs=1e-7)
    assert clipped["n_probabilities_clipped"] == 8
    assert direct["n_probabilities_clipped"] == 0


def test_geo_age_conflict_retains_primary_and_reports_sensitivity():
    result = json.loads((ROOT / "results/correction_2026-09/external_age_source_sensitivity.json").read_text())
    assert result["source_labels_absent_from_public_geo_deposit"] == ["aHD2", "aSLE8"]
    assert result["age_conflict"]["geo_age_years"] == 50
    assert result["age_conflict"]["supplement_age_years_review_reported"] == 43
    assert result["primary_age_auroc"] == pytest.approx(0.578125)
    assert result["sensitivity_age_auroc"] == pytest.approx(0.5796875)
    assert result["shared_geneformer_minus_sensitivity_age"]["superiority_rule_met"] is False


def test_future_setup_record_requires_dictionary_and_batch_hashes():
    summary = json.loads((ROOT / "results/correction_2026-09/shared_features/l2_dev_geneformer_v1_shared_run_summary.json").read_text())
    record = {
        "geneformer_revision": REVISION,
        "dictionary_sha256_by_file": EXPECTED_DICTIONARY_SHA256_BY_FILE,
        "checkpoint_sha256_by_file": CHECKPOINT_SHA256_BY_FILE,
        "staged_source_sha256_by_file": {
            "corrected_run.py": "a" * 64,
            "v1_fixture.py": "b" * 64,
            "gene_space_intersection.txt": SHARED_GENE_SHA256,
        },
        "runtime_pip_freeze_sha256": hashlib.sha256("\n".join(summary["runtime_pip_freeze"]).encode()).hexdigest(),
        "batch_checkpoint_metadata_by_file": {
            f"batch_{b['batch_idx']:02d}.json": {
                "metadata": {
                    "parquet_sha256": b["checkpoint_sha256"],
                    "config": {"checkpoint_sha256_by_file": CHECKPOINT_SHA256_BY_FILE},
                }
            } for b in summary["batches"]
        },
    }
    validate_setup_provenance(record, summary)
    bad = copy.deepcopy(record)
    bad["dictionary_sha256_by_file"]["token_dictionary_gc30M.pkl"] = "0" * 64
    with pytest.raises(ValueError, match="dictionary hashes differ"):
        validate_setup_provenance(bad, summary)
