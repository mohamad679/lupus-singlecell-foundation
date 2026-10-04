"""Compare an isolated CPU rerun with immutable published corrected results."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


def read(path: Path):
    return json.loads(path.read_text())


def compare(published: Path, rerun: Path):
    checks = {}
    for mode in ("shared", "native"):
        name = f"corrected_v1_{mode}_predictions.json"
        original, latest = read(published / name), read(rerun / name)
        for arm in ("geneformer", "pseudobulk", "metadata_only_age"):
            a, b = original[arm], latest[arm]
            if a["donor_ids"] != b["donor_ids"] or a["y"] != b["y"]:
                raise ValueError(f"{mode}/{arm} donor or label alignment differs")
            if not np.allclose(a["proba"], b["proba"], rtol=0, atol=1e-12):
                delta = np.abs(np.asarray(a["proba"], dtype=float) - np.asarray(b["proba"], dtype=float))
                raise ValueError(
                    f"{mode}/{arm} probabilities differ: "
                    f"max_abs={delta.max():.17g}, mean_abs={delta.mean():.17g}"
                )
            if arm == "geneformer" and not np.allclose(a["decision_score"], b["decision_score"], rtol=0, atol=1e-12):
                delta = np.abs(np.asarray(a["decision_score"], dtype=float) - np.asarray(b["decision_score"], dtype=float))
                raise ValueError(
                    f"{mode} original decision scores differ: "
                    f"max_abs={delta.max():.17g}, mean_abs={delta.mean():.17g}"
                )
        prior_analysis, new_analysis = (read(published / f"corrected_v1_{mode}_analysis.json"),
                                        read(rerun / f"corrected_v1_{mode}_analysis.json"))
        for arm in ("geneformer", "pseudobulk", "metadata_only_age"):
            for key in ("auroc", "average_precision", "brier_score"):
                if abs(prior_analysis["metrics"][arm][key] - new_analysis["metrics"][arm][key]) > 1e-12:
                    raise ValueError(f"{mode}/{arm} {key} differs")
        for key in ("geneformer_vs_age", "geneformer_vs_pseudobulk"):
            for metric in ("difference", "p_two_sided", "holm_adjusted_p"):
                if abs(prior_analysis["comparisons"][key][metric] - new_analysis["comparisons"][key][metric]) > 1e-12:
                    raise ValueError(f"{mode}/{key}/{metric} differs")
        checks[mode] = "aligned probabilities, decision scores, discrimination and paired inference agree"
    for name in ("corrected_v1_gene_input_sensitivity.json", "corrected_v1_descriptive.json",
                 "corrected_v1_shared_cohort_probe.json"):
        if not (rerun / name).is_file():
            raise FileNotFoundError(rerun / name)
    report = {"status": "pass", "published": str(published), "rerun": str(rerun),
              "checks": checks, "comparison_tolerance": 1e-12}
    (rerun / "reproduction_comparison.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--published", type=Path, required=True)
    parser.add_argument("--rerun", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(compare(args.published, args.rerun), indent=2))
