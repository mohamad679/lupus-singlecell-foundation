"""Analyze released or corrected donor predictions without changing the release.

Input JSON has one object per arm (geneformer, pseudobulk, metadata_only_age),
each with donor_ids, y, and proba arrays. The output is explicitly labeled
historical when run on the released regenerated predictions.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from correction_stats import holm_adjust, paired_bootstrap_ci, paired_delong, probability_metrics

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "results/l2_sealed_predictions_regenerated.json"
DEFAULT_OUTPUT = ROOT / "results/correction_2026-09/historical_scores_analysis.json"
ARMS = ("geneformer", "pseudobulk", "metadata_only_age")


def analyze(predictions, *, input_provenance):
    base_ids = predictions["geneformer"]["donor_ids"]
    base_y = predictions["geneformer"]["y"]
    if len(base_ids) != len(set(base_ids)):
        raise ValueError("donor IDs must be unique")
    for arm in ARMS:
        row = predictions[arm]
        if row["donor_ids"] != base_ids or row["y"] != base_y:
            raise ValueError(f"{arm}: donor IDs or labels are not in the same order")
        if len(row["proba"]) != len(base_ids):
            raise ValueError(f"{arm}: probability count does not match donors")

    prevalence = 162 / 261
    metrics = {
        arm: probability_metrics(base_y, predictions[arm]["proba"],
                                 development_prevalence=prevalence)
        for arm in ARMS
    }
    comparisons = {}
    for name, comparator in (("geneformer_vs_age", "metadata_only_age"),
                             ("geneformer_vs_pseudobulk", "pseudobulk")):
        a = predictions["geneformer"]["proba"]
        b = predictions[comparator]["proba"]
        comparisons[name] = {
            **paired_delong(base_y, a, b),
            **paired_bootstrap_ci(base_y, a, b),
        }
    adjusted = holm_adjust({name: c["p_two_sided"] for name, c in comparisons.items()})
    for name, value in adjusted.items():
        comparisons[name]["holm_adjusted_p"] = value
        comparisons[name]["holm_significant_0_05"] = value <= 0.05
        comparisons[name]["positive_ci_condition"] = comparisons[name]["ci95"][0] > 0
        comparisons[name]["superiority_rule_met"] = (
            comparisons[name]["positive_ci_condition"] and value <= 0.05
        )
    historical = input_provenance in {
        str(DEFAULT_INPUT), str(DEFAULT_INPUT.relative_to(ROOT)),
    }
    return {
        "input_provenance": input_provenance,
        "status": "historical scores only" if historical else "corrected score analysis",
        "warning": (
            "These statistics do not validate Geneformer tokenization or replace a corrected embedding rerun."
            if historical else
            "This corrected reanalysis uses the previously examined external cohort."
        ),
        "n_donors": len(base_ids), "n_case": sum(base_y), "n_control": len(base_y) - sum(base_y),
        "metrics": metrics, "comparisons": comparisons,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--predictions", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    if args.output.resolve() == args.predictions.resolve():
        raise ValueError("output must not overwrite input predictions")
    with args.predictions.open() as file:
        predictions = json.load(file)
    source = args.predictions.resolve()
    provenance = (str(source.relative_to(ROOT)) if source.is_relative_to(ROOT)
                  else str(source))
    result = analyze(predictions, input_provenance=provenance)
    result["input_sha256"] = hashlib.sha256(args.predictions.read_bytes()).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w") as file:
        json.dump(result, file, indent=2, allow_nan=False)
    print(args.output)


if __name__ == "__main__":
    main()
