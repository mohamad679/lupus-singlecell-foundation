"""Compare an isolated CPU refit with the published corrected results.

The fitted logistic model is numerically sensitive to the platform BLAS/LBFGS
implementation. Reproduction therefore requires exact data/donor alignment,
exact selected regularization values, bounded probability drift, unchanged
ranking metrics and paired inference, rather than bit-for-bit coefficients.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

PROBABILITY_MAX_ABS_TOL = 0.02
BRIER_ABS_TOL = 0.001
EXACT_METRIC_TOL = 1e-12


def read(path: Path):
    return json.loads(path.read_text())


def compare(published: Path, rerun: Path):
    checks = {}
    drift = {}
    for mode in ("shared", "native"):
        prior_fit = read(published / f"corrected_v1_{mode}_fit_report.json")
        new_fit = read(rerun / f"corrected_v1_{mode}_fit_report.json")
        if prior_fit["development_selected_c_per_outer_fold"] != new_fit["development_selected_c_per_outer_fold"]:
            raise ValueError(f"{mode} selected C values differ")
        if prior_fit["final_c_median"] != new_fit["final_c_median"]:
            raise ValueError(f"{mode} final C differs")

        name = f"corrected_v1_{mode}_predictions.json"
        original, latest = read(published / name), read(rerun / name)
        drift[mode] = {}
        for arm in ("geneformer", "pseudobulk", "metadata_only_age"):
            a, b = original[arm], latest[arm]
            if a["donor_ids"] != b["donor_ids"] or a["y"] != b["y"]:
                raise ValueError(f"{mode}/{arm} donor or label alignment differs")
            delta = np.abs(np.asarray(a["proba"], dtype=float) - np.asarray(b["proba"], dtype=float))
            drift[mode][arm] = {
                "probability_max_abs": float(delta.max()),
                "probability_mean_abs": float(delta.mean()),
            }
            if float(delta.max()) > PROBABILITY_MAX_ABS_TOL:
                raise ValueError(
                    f"{mode}/{arm} probability drift exceeds tolerance: "
                    f"max_abs={delta.max():.17g}"
                )
            if arm == "geneformer":
                a_score = np.asarray(a["decision_score"], dtype=float)
                b_score = np.asarray(b["decision_score"], dtype=float)
                if not np.isfinite(b_score).all():
                    raise ValueError(f"{mode} rerun decision scores are nonfinite")
                if not np.array_equal(np.argsort(a_score), np.argsort(b_score)):
                    raise ValueError(f"{mode} Geneformer score ranking differs")
                score_delta = np.abs(a_score - b_score)
                drift[mode][arm]["decision_score_max_abs"] = float(score_delta.max())
                drift[mode][arm]["decision_score_mean_abs"] = float(score_delta.mean())

        prior_analysis = read(published / f"corrected_v1_{mode}_analysis.json")
        new_analysis = read(rerun / f"corrected_v1_{mode}_analysis.json")
        for arm in ("geneformer", "pseudobulk", "metadata_only_age"):
            for key in ("auroc", "average_precision"):
                d = abs(prior_analysis["metrics"][arm][key] - new_analysis["metrics"][arm][key])
                if d > EXACT_METRIC_TOL:
                    raise ValueError(f"{mode}/{arm} {key} differs by {d:.17g}")
            d = abs(prior_analysis["metrics"][arm]["brier_score"] -
                    new_analysis["metrics"][arm]["brier_score"])
            drift[mode][arm]["brier_abs"] = float(d)
            if d > BRIER_ABS_TOL:
                raise ValueError(f"{mode}/{arm} brier_score differs by {d:.17g}")

        for key in ("geneformer_vs_age", "geneformer_vs_pseudobulk"):
            for metric in ("difference", "p_two_sided", "holm_adjusted_p"):
                d = abs(prior_analysis["comparisons"][key][metric] -
                        new_analysis["comparisons"][key][metric])
                if d > EXACT_METRIC_TOL:
                    raise ValueError(f"{mode}/{key}/{metric} differs by {d:.17g}")
            if (prior_analysis["comparisons"][key]["superiority_rule_met"] !=
                    new_analysis["comparisons"][key]["superiority_rule_met"]):
                raise ValueError(f"{mode}/{key} superiority decision differs")

        checks[mode] = (
            "exact donor/label alignment and C selection; bounded cross-platform "
            "probability drift; unchanged ranking metrics, paired inference and decision"
        )

    for name in ("corrected_v1_gene_input_sensitivity.json", "corrected_v1_descriptive.json",
                 "corrected_v1_shared_cohort_probe.json"):
        if not (rerun / name).is_file():
            raise FileNotFoundError(rerun / name)

    report = {
        "status": "pass",
        "published": str(published),
        "rerun": str(rerun),
        "checks": checks,
        "numeric_policy": {
            "probability_max_abs_tolerance": PROBABILITY_MAX_ABS_TOL,
            "brier_abs_tolerance": BRIER_ABS_TOL,
            "ranking_and_paired_inference_tolerance": EXACT_METRIC_TOL,
            "reason": "cross-platform LBFGS/BLAS refits are not bit-for-bit deterministic",
        },
        "observed_drift": drift,
    }
    (rerun / "reproduction_comparison.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--published", type=Path, required=True)
    parser.add_argument("--rerun", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(compare(args.published, args.rerun), indent=2))
